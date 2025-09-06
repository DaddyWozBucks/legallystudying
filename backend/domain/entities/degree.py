from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Degree:
    """Represents an academic degree program."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""  # e.g., "Juris Doctor", "Master of Laws"
    abbreviation: str = ""  # e.g., "JD", "LLM"
    description: str = ""  # Full description of the degree program
    prompt_context: str = ""  # Summarized context for use in prompts
    department: str = ""  # e.g., "Law School", "Business School"
    duration_years: float = 0.0  # Expected duration in years
    credit_hours: int = 0  # Total credit hours required
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)