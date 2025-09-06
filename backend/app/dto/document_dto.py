from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


class DocumentUploadRequest(BaseModel):
    file_path: str = Field(..., description="Path to the document file")
    parser_plugin_id: Optional[str] = Field(None, description="Specific parser plugin to use")
    course_id: Optional[UUID] = Field(None, description="Course this document belongs to")
    week: Optional[int] = Field(None, description="Week number for course reading")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    id: UUID
    name: str
    path: str
    content_hash: str
    file_type: str
    size_bytes: int
    processing_status: str
    parser_plugin_id: Optional[str]
    course_id: Optional[UUID]
    week: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    raw_text: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class DocumentProcessingStatus(BaseModel):
    document_id: UUID
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None


class DocumentSummaryResponse(BaseModel):
    document_id: str
    summary: str
    key_points: List[str]
    generated_at: datetime


class QuestionAnswerRequest(BaseModel):
    question: str = Field(..., description="Question to ask about the document")


class QuestionAnswerResponse(BaseModel):
    question: str
    answer: str
    sources: List[str] = Field(default_factory=list, description="Source references from the document")
    confidence: float = Field(default=0.0, description="Confidence score of the answer")