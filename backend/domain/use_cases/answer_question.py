from typing import Optional
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

from domain.repositories.document_repository import DocumentRepository
from infrastructure.database.chroma_repository import ChromaVectorRepository
from domain.repositories.prompt_repository import PromptRepository
from domain.repositories.course_repository import CourseRepository
from domain.repositories.degree_repository import DegreeRepository
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService


@dataclass
class Answer:
    content: str
    sources: list[str]
    confidence: float
    generated_at: datetime


class AnswerQuestionUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,
        vector_repo: ChromaVectorRepository,
        llm_service: LLMService,
        embedding_service: EmbeddingService,
        prompt_repo: Optional[PromptRepository] = None,
        course_repo: Optional[CourseRepository] = None,
        degree_repo: Optional[DegreeRepository] = None,
    ):
        self.document_repo = document_repo
        self.vector_repo = vector_repo
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.prompt_repo = prompt_repo
        self.course_repo = course_repo
        self.degree_repo = degree_repo
    
    async def execute(self, document_id: UUID, question: str) -> Answer:
        """Answer a question about a specific document."""
        
        # Get document
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        # Generate embedding for the question
        question_embedding = await self.embedding_service.generate_embedding(question)
        
        # Search for relevant chunks
        metadata_filter = {"document_id": str(document_id)}
        chunk_results = await self.vector_repo.search_similar(
            query_embedding=question_embedding,
            top_k=5,
            metadata_filter=metadata_filter
        )
        
        # Combine chunks into context
        if chunk_results:
            context = "\n\n".join([chunk.content for chunk, score in chunk_results])
            sources = [f"Section {i+1} (score: {score:.2f})" for i, (chunk, score) in enumerate(chunk_results)]
        else:
            # Fallback to raw text if no chunks found
            context = document.raw_text if hasattr(document, 'raw_text') and document.raw_text else ""
            sources = ["Full document"]
        
        if not context:
            return Answer(
                content="Unable to find relevant information in the document to answer this question.",
                sources=[],
                confidence=0.0,
                generated_at=datetime.utcnow()
            )
        
        # Get course and degree context if document is linked to a course
        course_context = ""
        degree_context = ""
        
        if document.course_id and self.course_repo:
            course = await self.course_repo.get_course(document.course_id)
            if course:
                course_context = course.prompt_context or ""
                
                # Get degree context if course has a degree
                if course.degree_id and self.degree_repo:
                    degree = await self.degree_repo.get_degree(course.degree_id)
                    if degree:
                        degree_context = degree.prompt_context or ""
        
        # Get prompt template
        prompt_template = None
        if self.prompt_repo:
            # Try to get specialized Q&A prompt based on document type
            if document.file_type == '.pdf' and 'legal' in document.name.lower():
                prompt = await self.prompt_repo.get_active_prompt_by_name("legal_qa")
            elif document.file_type == '.pdf' and any(term in document.name.lower() for term in ['research', 'paper', 'journal']):
                prompt = await self.prompt_repo.get_active_prompt_by_name("research_qa")
            else:
                prompt = await self.prompt_repo.get_active_prompt_by_name("general_qa")
            
            if prompt:
                prompt_template = prompt.template
        
        # Use default prompt if no custom prompt found
        if not prompt_template:
            # Build educational context section if available
            educational_context = ""
            if degree_context or course_context:
                educational_context = "\n\nEducational Context:\n"
                if degree_context:
                    educational_context += f"Degree Program: {degree_context}\n"
                if course_context:
                    educational_context += f"Course: {course_context}\n"
            
            prompt_template = """Based on the following context from the document, please answer the question.{educational_context}

Document Context:
{context}

Question: {question}

Please provide a clear and concise answer based only on the information provided in the context. If the context doesn't contain enough information to answer the question, please state that clearly."""
        
        # Format prompt
        educational_context = ""
        if degree_context or course_context:
            educational_context = "\n\nEducational Context:\n"
            if degree_context:
                educational_context += f"Degree Program: {degree_context}\n"
            if course_context:
                educational_context += f"Course: {course_context}\n"
        
        formatted_prompt = prompt_template.format(
            context=context,
            question=question,
            educational_context=educational_context,
            degree_context=degree_context,
            course_context=course_context
        )
        
        # Generate answer
        answer_text = await self.llm_service.generate(formatted_prompt)
        
        # Calculate confidence based on chunk relevance (simplified)
        confidence = 0.8 if chunk_results else 0.5
        
        return Answer(
            content=answer_text,
            sources=sources,
            confidence=confidence,
            generated_at=datetime.utcnow()
        )