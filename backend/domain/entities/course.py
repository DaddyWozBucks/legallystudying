from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Course:
    """Represents an academic course."""
    id: UUID = field(default_factory=uuid4)
    course_number: str = ""  # e.g., "LAW 101", "CONTRACTS 201"
    name: str = ""  # e.g., "Constitutional Law", "Contract Law"
    description: str = ""  # Full course description
    prompt_context: str = ""  # Summarized context for use in prompts
    degree_id: Optional[UUID] = None  # Associated degree program
    credits: int = 0  # Credit hours
    semester: str = ""  # e.g., "Fall 2024", "Spring 2025"
    professor: str = ""  # Instructor name
    attributes: List[str] = field(default_factory=list)  # e.g., ["Required", "Writing Intensive", "Bar Exam Subject"]
    prerequisites: List[str] = field(default_factory=list)  # Course prerequisites
    learning_objectives: List[str] = field(default_factory=list)  # Course learning objectives
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if self.degree_id and isinstance(self.degree_id, str):
            self.degree_id = UUID(self.degree_id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)