from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class PromptCreateRequest(BaseModel):
    name: str = Field(..., description="Unique name for the prompt")
    description: str = Field(..., description="Description of what this prompt does")
    template: str = Field(..., description="The prompt template with placeholders")
    category: str = Field(..., description="Category: summary, qa, flashcards, analysis")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PromptUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Unique name for the prompt")
    description: Optional[str] = Field(None, description="Description of what this prompt does")
    template: Optional[str] = Field(None, description="The prompt template with placeholders")
    category: Optional[str] = Field(None, description="Category: summary, qa, flashcards, analysis")
    is_active: Optional[bool] = Field(None, description="Whether this prompt is active")
    metadata: Optional[Dict[str, Any]] = Field(None)


class PromptResponse(BaseModel):
    id: UUID
    name: str
    description: str
    template: str
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    prompts: list[PromptResponse]
    total: int