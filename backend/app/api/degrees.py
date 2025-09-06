from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from app.dto.degree_dto import DegreeCreateRequest, DegreeUpdateRequest, DegreeResponse, DegreeListResponse
from domain.entities.degree import Degree

router = APIRouter()


@router.post("/", response_model=DegreeResponse)
async def create_degree(request: Request, body: DegreeCreateRequest):
    """Create a new degree."""
    
    degree = Degree(
        id=uuid4(),
        name=body.name,
        abbreviation=body.abbreviation,
        description=body.description,
        prompt_context=body.prompt_context,
        department=body.department,
        duration_years=body.duration_years,
        credit_hours=body.credit_hours,
        metadata=body.metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )
    
    try:
        saved_degree = await request.app.state.degree_repo.save_degree(degree)
        return DegreeResponse.from_orm(saved_degree)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DegreeListResponse)
async def list_degrees(request: Request):
    """List all degrees."""
    
    degrees = await request.app.state.degree_repo.get_all_degrees()
    return DegreeListResponse(
        degrees=[DegreeResponse.from_orm(d) for d in degrees],
        total=len(degrees)
    )


@router.get("/active", response_model=DegreeListResponse)
async def list_active_degrees(request: Request):
    """List all active degrees."""
    
    degrees = await request.app.state.degree_repo.get_active_degrees()
    return DegreeListResponse(
        degrees=[DegreeResponse.from_orm(d) for d in degrees],
        total=len(degrees)
    )


@router.get("/{degree_id}", response_model=DegreeResponse)
async def get_degree(request: Request, degree_id: UUID):
    """Get a specific degree by ID."""
    
    degree = await request.app.state.degree_repo.get_degree(degree_id)
    if not degree:
        raise HTTPException(status_code=404, detail="Degree not found")
    
    return DegreeResponse.from_orm(degree)


@router.put("/{degree_id}", response_model=DegreeResponse)
async def update_degree(request: Request, degree_id: UUID, body: DegreeUpdateRequest):
    """Update an existing degree."""
    
    degree = await request.app.state.degree_repo.get_degree(degree_id)
    if not degree:
        raise HTTPException(status_code=404, detail="Degree not found")
    
    # Update fields if provided
    if body.name is not None:
        degree.name = body.name
    if body.abbreviation is not None:
        degree.abbreviation = body.abbreviation
    if body.description is not None:
        degree.description = body.description
    if body.prompt_context is not None:
        degree.prompt_context = body.prompt_context
    if body.department is not None:
        degree.department = body.department
    if body.duration_years is not None:
        degree.duration_years = body.duration_years
    if body.credit_hours is not None:
        degree.credit_hours = body.credit_hours
    if body.is_active is not None:
        degree.is_active = body.is_active
    if body.metadata is not None:
        degree.metadata = body.metadata
    
    degree.updated_at = datetime.utcnow()
    
    try:
        updated_degree = await request.app.state.degree_repo.update_degree(degree)
        return DegreeResponse.from_orm(updated_degree)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{degree_id}")
async def delete_degree(request: Request, degree_id: UUID):
    """Delete a degree."""
    
    success = await request.app.state.degree_repo.delete_degree(degree_id)
    if not success:
        raise HTTPException(status_code=404, detail="Degree not found")
    
    return {"message": "Degree deleted successfully"}