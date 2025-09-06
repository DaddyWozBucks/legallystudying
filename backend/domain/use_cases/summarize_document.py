from uuid import UUID
from datetime import datetime
from typing import List
from dataclasses import dataclass
import logging

from domain.repositories.document_repository import DocumentRepository, VectorRepository
from domain.repositories.prompt_repository import PromptRepository
from domain.repositories.course_repository import CourseRepository
from domain.repositories.degree_repository import DegreeRepository
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class DocumentSummary:
    content: str
    key_points: List[str]
    generated_at: datetime


class SummarizeDocumentUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,
        vector_repo: VectorRepository,
        llm_service: LLMService,
        prompt_repo: PromptRepository = None,
        course_repo: CourseRepository = None,
        degree_repo: DegreeRepository = None,
    ):
        self.document_repo = document_repo
        self.vector_repo = vector_repo
        self.llm_service = llm_service
        self.prompt_repo = prompt_repo
        self.course_repo = course_repo
        self.degree_repo = degree_repo
    
    async def execute(self, document_id: UUID) -> DocumentSummary:
        """Generate a summary for a document."""
        
        # Get the document
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        full_text = ""
        
        # First, try to use the raw_text field if available
        if document.raw_text:
            full_text = document.raw_text
            logger.info(f"Using stored raw text for document {document_id} (length: {len(full_text)} chars)")
        
        # If no raw_text, try to get from vector store chunks
        elif not full_text:
            try:
                # Get chunks from vector store by searching with document metadata
                from typing import List
                
                # Create a simple query embedding (we'll search for all chunks from this document)
                dummy_embedding = [0.0] * 384  # Standard embedding size for all-MiniLM-L6-v2
                
                # Search for chunks from this specific document
                chunks_with_scores = await self.vector_repo.search_similar(
                    query_embedding=dummy_embedding,
                    top_k=100,  # Get up to 100 chunks
                    metadata_filter={"document_id": str(document_id)}
                )
                
                if chunks_with_scores:
                    # Sort chunks by sequence number to maintain order
                    sorted_chunks = sorted(chunks_with_scores, key=lambda x: x[0].sequence_number)
                    text_parts = [chunk[0].content for chunk in sorted_chunks[:50]]  # Limit to first 50 chunks
                    full_text = "\n\n".join(text_parts)
                    logger.info(f"Retrieved {len(text_parts)} chunks from vector store for document {document_id}")
            except Exception as e:
                logger.error(f"Error retrieving chunks from vector store: {e}")
        
        # If no chunks found, try to read the file directly
        if not full_text:
            from pathlib import Path
            doc_path = Path(document.path)
            
            if doc_path.exists():
                try:
                    if document.file_type == '.pdf':
                        # Extract text from PDF using PyMuPDF
                        import fitz  # PyMuPDF
                        pdf_document = fitz.open(doc_path)
                        text_parts = []
                        for page_num in range(pdf_document.page_count):
                            page = pdf_document[page_num]
                            text_parts.append(page.get_text())
                        pdf_document.close()
                        full_text = "\n\n".join(text_parts)
                    else:
                        # For text files, read directly
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            full_text = f.read()
                except Exception as e:
                    logger.error(f"Error reading document file: {e}")
        
        # Limit text length for API
        if len(full_text) > 10000:
            full_text = full_text[:10000] + "\n\n[Document truncated for summary]"
        
        if not full_text or len(full_text) < 100:
            # If still no content, provide basic info
            full_text = f"Document: {document.name}\nType: {document.file_type}\nSize: {document.size_bytes} bytes\n\nContent not available for summarization."
        
        # Get course and degree context if document is linked to a course
        course_context = ""
        degree_context = ""
        
        if document.course_id and self.course_repo:
            course = await self.course_repo.get_course(document.course_id)
            if course:
                course_context = course.prompt_context or ""
                logger.info(f"Using course context for {course.name} ({course.course_number})")
                
                # Get degree context if course has a degree
                if course.degree_id and self.degree_repo:
                    degree = await self.degree_repo.get_degree(course.degree_id)
                    if degree:
                        degree_context = degree.prompt_context or ""
                        logger.info(f"Using degree context for {degree.name}")
        
        # Get prompt template from database or use default
        prompt_template = None
        if self.prompt_repo:
            # Try to get custom prompt for document type
            if document.file_type == '.pdf' and 'legal' in document.name.lower():
                prompt = await self.prompt_repo.get_active_prompt_by_name("legal_document_summary")
                if prompt:
                    prompt_template = prompt.template
            
            # Fall back to general document summary prompt
            if not prompt_template:
                prompt = await self.prompt_repo.get_active_prompt_by_name("document_summary")
                if prompt:
                    prompt_template = prompt.template
        
        # Use default if no custom prompt found
        if not prompt_template:
            # Build context section if we have course/degree context
            context_section = ""
            if degree_context or course_context:
                context_section = "\n\nCONTEXT:\n"
                if degree_context:
                    context_section += f"Degree Program: {degree_context}\n"
                if course_context:
                    context_section += f"Course: {course_context}\n"
            
            prompt_template = """Please provide a comprehensive summary of the following document:{context_section}

{full_text}

Please provide:
1. A concise summary (2-3 paragraphs)
2. 3-5 key points or takeaways

Format your response as:
SUMMARY:
[Your summary here]

KEY POINTS:
- [Point 1]
- [Point 2]
- [Point 3]
"""
        
        # Format the prompt with context and document text
        context_section = ""
        if degree_context or course_context:
            context_section = "\n\nCONTEXT:\n"
            if degree_context:
                context_section += f"Degree Program: {degree_context}\n"
            if course_context:
                context_section += f"Course: {course_context}\n"
        
        summary_prompt = prompt_template.format(
            full_text=full_text,
            context_section=context_section,
            degree_context=degree_context,
            course_context=course_context
        )
        
        response = await self.llm_service.generate(summary_prompt)
        
        # Parse the response
        summary_text = ""
        key_points = []
        
        if "SUMMARY:" in response and "KEY POINTS:" in response:
            parts = response.split("KEY POINTS:")
            summary_text = parts[0].replace("SUMMARY:", "").strip()
            
            key_points_text = parts[1].strip()
            key_points = [
                point.strip().lstrip("- ").lstrip("• ")
                for point in key_points_text.split("\n")
                if point.strip() and point.strip() not in ["", "-", "•"]
            ]
        else:
            # Fallback if format is not as expected
            summary_text = response
            key_points = ["Summary generated without structured format"]
        
        return DocumentSummary(
            content=summary_text,
            key_points=key_points,
            generated_at=datetime.utcnow()
        )