from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from domain.repositories.document_repository import VectorRepository


@dataclass
class QueryResult:
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    context_chunks: List[str]


class QueryDocumentsUseCase:
    def __init__(
        self,
        vector_repo: VectorRepository,
        embedding_service,
        llm_service,
    ):
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service
        self.llm_service = llm_service

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> QueryResult:
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        similar_chunks = await self.vector_repo.search_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )
        
        context_chunks = [chunk.content for chunk, _ in similar_chunks]
        context = "\n\n".join(context_chunks)
        
        prompt = self._build_prompt(query, context)
        
        answer = await self.llm_service.generate_response(prompt)
        
        sources = self._extract_sources(similar_chunks)
        
        return QueryResult(
            answer=answer,
            sources=sources,
            query=query,
            context_chunks=context_chunks,
        )

    def _build_prompt(self, query: str, context: str) -> str:
        return f"""You are a helpful assistant analyzing documents. 
Based on the following context, please answer the user's question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based solely on the information provided in the context."""

    def _extract_sources(self, similar_chunks) -> List[Dict[str, Any]]:
        sources = []
        seen_documents = set()
        
        for chunk, score in similar_chunks:
            if chunk.document_id not in seen_documents:
                sources.append({
                    "document_id": str(chunk.document_id),
                    "page_number": chunk.page_number,
                    "relevance_score": score,
                    "metadata": chunk.metadata,
                })
                seen_documents.add(chunk.document_id)
        
        return sources