from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.dto.course_dto import CourseCreateRequest, CourseUpdateRequest, CourseResponse, CourseListResponse
from domain.entities.course import Course

router = APIRouter()


@router.post("/", response_model=CourseResponse)
async def create_course(request: Request, body: CourseCreateRequest):
    """Create a new course."""
    
    # Check if course number already exists
    existing = await request.app.state.course_repo.get_course_by_number(body.course_number)
    if existing:
        raise HTTPException(status_code=400, detail="Course number already exists")
    
    course = Course(
        id=uuid4(),
        course_number=body.course_number,
        name=body.name,
        description=body.description,
        prompt_context=body.prompt_context,
        degree_id=body.degree_id,
        credits=body.credits,
        semester=body.semester,
        professor=body.professor,
        attributes=body.attributes,
        prerequisites=body.prerequisites,
        learning_objectives=body.learning_objectives,
        metadata=body.metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )
    
    try:
        saved_course = await request.app.state.course_repo.save_course(course)
        return CourseResponse.from_orm(saved_course)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=CourseListResponse)
async def list_courses(
    request: Request,
    degree_id: Optional[UUID] = Query(None, description="Filter by degree ID")
):
    """List all courses, optionally filtered by degree."""
    
    if degree_id:
        courses = await request.app.state.course_repo.get_courses_by_degree(degree_id)
    else:
        courses = await request.app.state.course_repo.get_all_courses()
    
    return CourseListResponse(
        courses=[CourseResponse.from_orm(c) for c in courses],
        total=len(courses)
    )


@router.get("/active", response_model=CourseListResponse)
async def list_active_courses(request: Request):
    """List all active courses."""
    
    courses = await request.app.state.course_repo.get_active_courses()
    return CourseListResponse(
        courses=[CourseResponse.from_orm(c) for c in courses],
        total=len(courses)
    )


@router.get("/by-number/{course_number}", response_model=CourseResponse)
async def get_course_by_number(request: Request, course_number: str):
    """Get a course by its course number."""
    
    course = await request.app.state.course_repo.get_course_by_number(course_number)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return CourseResponse.from_orm(course)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(request: Request, course_id: UUID):
    """Get a specific course by ID."""
    
    course = await request.app.state.course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return CourseResponse.from_orm(course)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(request: Request, course_id: UUID, body: CourseUpdateRequest):
    """Update an existing course."""
    
    course = await request.app.state.course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if new course number already exists (if changing)
    if body.course_number and body.course_number != course.course_number:
        existing = await request.app.state.course_repo.get_course_by_number(body.course_number)
        if existing:
            raise HTTPException(status_code=400, detail="Course number already exists")
    
    # Update fields if provided
    if body.course_number is not None:
        course.course_number = body.course_number
    if body.name is not None:
        course.name = body.name
    if body.description is not None:
        course.description = body.description
    if body.prompt_context is not None:
        course.prompt_context = body.prompt_context
    if body.degree_id is not None:
        course.degree_id = body.degree_id
    if body.credits is not None:
        course.credits = body.credits
    if body.semester is not None:
        course.semester = body.semester
    if body.professor is not None:
        course.professor = body.professor
    if body.attributes is not None:
        course.attributes = body.attributes
    if body.prerequisites is not None:
        course.prerequisites = body.prerequisites
    if body.learning_objectives is not None:
        course.learning_objectives = body.learning_objectives
    if body.is_active is not None:
        course.is_active = body.is_active
    if body.metadata is not None:
        course.metadata = body.metadata
    
    course.updated_at = datetime.utcnow()
    
    try:
        updated_course = await request.app.state.course_repo.update_course(course)
        return CourseResponse.from_orm(updated_course)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{course_id}")
async def delete_course(request: Request, course_id: UUID):
    """Delete a course."""
    
    success = await request.app.state.course_repo.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {"message": "Course deleted successfully"}