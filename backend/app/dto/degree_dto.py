from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


class DegreeCreateRequest(BaseModel):
    name: str = Field(..., description="Degree name")
    abbreviation: str = Field(..., description="Degree abbreviation")
    description: str = Field(..., description="Full description of the degree")
    prompt_context: str = Field(..., description="Summarized context for prompts")
    department: str = Field(..., description="Department")
    duration_years: float = Field(default=0.0, description="Duration in years")
    credit_hours: int = Field(default=0, description="Total credit hours")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DegreeUpdateRequest(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    prompt_context: Optional[str] = None
    department: Optional[str] = None
    duration_years: Optional[float] = None
    credit_hours: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DegreeResponse(BaseModel):
    id: UUID
    name: str
    abbreviation: str
    description: str
    prompt_context: str
    department: str
    duration_years: float
    credit_hours: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class DegreeListResponse(BaseModel):
    degrees: List[DegreeResponse]
    total: int