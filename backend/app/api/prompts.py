from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from uuid import UUID

from app.dto.prompt_dto import (
    PromptCreateRequest,
    PromptUpdateRequest,
    PromptResponse,
    PromptListResponse
)
from domain.entities.prompt import Prompt

router = APIRouter()


@router.post("/", response_model=PromptResponse)
async def create_prompt(request: Request, body: PromptCreateRequest):
    """Create a new prompt template."""
    
    # Check if prompt with same name exists
    existing = await request.app.state.prompt_repo.get_prompt_by_name(body.name)
    if existing:
        raise HTTPException(status_code=400, detail=f"Prompt with name '{body.name}' already exists")
    
    prompt = Prompt.create(
        name=body.name,
        description=body.description,
        template=body.template,
        category=body.category,
        metadata=body.metadata,
    )
    
    saved_prompt = await request.app.state.prompt_repo.save_prompt(prompt)
    return PromptResponse.from_orm(saved_prompt)


@router.get("/", response_model=PromptListResponse)
async def list_prompts(request: Request, category: Optional[str] = None):
    """List all prompts, optionally filtered by category."""
    
    if category:
        prompts = await request.app.state.prompt_repo.get_prompts_by_category(category)
    else:
        prompts = await request.app.state.prompt_repo.get_all_prompts()
    
    return PromptListResponse(
        prompts=[PromptResponse.from_orm(p) for p in prompts],
        total=len(prompts),
    )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(request: Request, prompt_id: UUID):
    """Get a specific prompt by ID."""
    
    prompt = await request.app.state.prompt_repo.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return PromptResponse.from_orm(prompt)


@router.get("/by-name/{name}", response_model=PromptResponse)
async def get_prompt_by_name(request: Request, name: str):
    """Get a prompt by its unique name."""
    
    prompt = await request.app.state.prompt_repo.get_prompt_by_name(name)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt with name '{name}' not found")
    
    return PromptResponse.from_orm(prompt)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(request: Request, prompt_id: UUID, body: PromptUpdateRequest):
    """Update an existing prompt."""
    
    prompt = await request.app.state.prompt_repo.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Update fields if provided
    if body.name is not None:
        # Check if new name already exists
        existing = await request.app.state.prompt_repo.get_prompt_by_name(body.name)
        if existing and existing.id != prompt.id:
            raise HTTPException(status_code=400, detail=f"Prompt with name '{body.name}' already exists")
        prompt.name = body.name
    
    if body.description is not None:
        prompt.description = body.description
    if body.template is not None:
        prompt.template = body.template
    if body.category is not None:
        prompt.category = body.category
    if body.is_active is not None:
        prompt.is_active = body.is_active
    if body.metadata is not None:
        prompt.metadata = body.metadata
    
    updated_prompt = await request.app.state.prompt_repo.update_prompt(prompt)
    return PromptResponse.from_orm(updated_prompt)


@router.delete("/{prompt_id}")
async def delete_prompt(request: Request, prompt_id: UUID):
    """Delete a prompt."""
    
    success = await request.app.state.prompt_repo.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return {"message": "Prompt deleted successfully"}