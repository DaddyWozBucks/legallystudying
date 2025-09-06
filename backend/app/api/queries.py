from fastapi import APIRouter, HTTPException, Request
from typing import Optional
import time

from app.dto.query_dto import QueryRequest, QueryResponse, SourceInfo
from domain.use_cases.query_documents import QueryDocumentsUseCase

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: Request,
    body: QueryRequest,
):
    """Execute a semantic query against the document corpus."""
    
    start_time = time.time()
    
    use_case = QueryDocumentsUseCase(
        vector_repo=request.app.state.vector_repo,
        embedding_service=request.app.state.embedding_service,
        llm_service=request.app.state.llm_service,
    )
    
    metadata_filter = body.metadata_filter or {}
    if body.document_ids:
        metadata_filter["document_id"] = {"$in": [str(id) for id in body.document_ids]}
    
    try:
        result = await use_case.execute(
            query=body.query,
            top_k=body.top_k,
            metadata_filter=metadata_filter if metadata_filter else None,
        )
        
        document_repo = request.app.state.document_repo
        sources = []
        for source in result.sources:
            doc = await document_repo.get_document(source["document_id"])
            if doc:
                sources.append(
                    SourceInfo(
                        document_id=doc.id,
                        document_name=doc.name,
                        page_number=source.get("page_number"),
                        relevance_score=source["relevance_score"],
                        excerpt=result.context_chunks[len(sources)][:200] if len(sources) < len(result.context_chunks) else None,
                    )
                )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return QueryResponse(
            answer=result.answer,
            sources=sources,
            query=result.query,
            processing_time_ms=processing_time_ms,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def semantic_search(
    request: Request,
    query: str,
    limit: int = 10,
    document_ids: Optional[list[str]] = None,
):
    """Perform semantic search without LLM generation."""
    
    embedding_service = request.app.state.embedding_service
    vector_repo = request.app.state.vector_repo
    
    try:
        query_embedding = await embedding_service.generate_embedding(query)
        
        metadata_filter = {}
        if document_ids:
            metadata_filter["document_id"] = {"$in": document_ids}
        
        results = await vector_repo.search_similar(
            query_embedding=query_embedding,
            top_k=limit,
            metadata_filter=metadata_filter if metadata_filter else None,
        )
        
        return {
            "query": query,
            "results": [
                {
                    "content": chunk.content,
                    "document_id": str(chunk.document_id),
                    "page_number": chunk.page_number,
                    "score": score,
                }
                for chunk, score in results
            ],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))