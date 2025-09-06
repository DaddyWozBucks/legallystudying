from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Prompt:
    """Entity representing a customizable prompt template."""
    id: UUID
    name: str  # e.g., "document_summary", "qa_response", "flashcard_generation"
    description: str
    template: str  # The actual prompt template with placeholders
    category: str  # e.g., "summary", "qa", "flashcards", "analysis"
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict = None

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        template: str,
        category: str,
        metadata: Optional[dict] = None,
    ) -> "Prompt":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            template=template,
            category=category,
            is_active=True,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )