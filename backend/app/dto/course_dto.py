from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


class CourseCreateRequest(BaseModel):
    course_number: str = Field(..., description="Course number")
    name: str = Field(..., description="Course name")
    description: str = Field(..., description="Full course description")
    prompt_context: str = Field(..., description="Summarized context for prompts")
    degree_id: Optional[UUID] = Field(None, description="Associated degree ID")
    credits: int = Field(default=0, description="Credit hours")
    semester: str = Field(..., description="Semester")
    professor: str = Field(..., description="Professor/Instructor")
    attributes: List[str] = Field(default_factory=list, description="Course attributes")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CourseUpdateRequest(BaseModel):
    course_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_context: Optional[str] = None
    degree_id: Optional[UUID] = None
    credits: Optional[int] = None
    semester: Optional[str] = None
    professor: Optional[str] = None
    attributes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class CourseResponse(BaseModel):
    id: UUID
    course_number: str
    name: str
    description: str
    prompt_context: str
    degree_id: Optional[UUID]
    credits: int
    semester: str
    professor: str
    attributes: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    courses: List[CourseResponse]
    total: int