from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


@dataclass
class Document:
    id: UUID
    name: str
    path: str
    content_hash: str
    file_type: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    parser_plugin_id: Optional[str] = None
    processing_status: str = "pending"
    course_id: Optional[UUID] = None  # Link to associated course
    week: Optional[int] = None  # Week number for grouping readings
    error_message: Optional[str] = None
    raw_text: Optional[str] = None  # Store extracted text for quick access

    @classmethod
    def create(
        cls,
        name: str,
        path: str,
        content_hash: str,
        file_type: str,
        size_bytes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Document":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            name=name,
            path=path,
            content_hash=content_hash,
            file_type=file_type,
            size_bytes=size_bytes,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            processing_status="pending",
        )


@dataclass
class TextChunk:
    id: UUID
    document_id: UUID
    content: str
    sequence_number: int
    page_number: Optional[int]
    embedding: Optional[list[float]] = None
    metadata: Dict[str, Any] = None

    @classmethod
    def create(
        cls,
        document_id: UUID,
        content: str,
        sequence_number: int,
        page_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "TextChunk":
        return cls(
            id=uuid4(),
            document_id=document_id,
            content=content,
            sequence_number=sequence_number,
            page_number=page_number,
            metadata=metadata or {},
        )