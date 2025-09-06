from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(5, description="Number of relevant chunks to retrieve", ge=1, le=50)
    document_ids: Optional[List[UUID]] = Field(None, description="Filter by specific documents")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Additional metadata filters")


class SourceInfo(BaseModel):
    document_id: UUID
    document_name: str
    page_number: Optional[int]
    relevance_score: float
    excerpt: Optional[str]


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    query: str
    processing_time_ms: float
    
    
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum results to return", ge=1, le=100)
    offset: int = Field(0, description="Pagination offset", ge=0)
    search_type: str = Field("semantic", description="Type of search: semantic, keyword, or hybrid")