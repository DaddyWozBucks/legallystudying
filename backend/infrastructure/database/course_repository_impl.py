from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from domain.entities.course import Course
from domain.repositories.course_repository import CourseRepository
from infrastructure.database.document_repository_impl import Base


class CourseModel(Base):
    __tablename__ = "courses"
    
    id = Column(String, primary_key=True)
    course_number = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    prompt_context = Column(Text, nullable=False)
    degree_id = Column(String, nullable=True, index=True)
    credits = Column(Integer, default=0)
    semester = Column(String, nullable=False)
    professor = Column(String, nullable=False)
    attributes = Column(ARRAY(String), default=[])
    prerequisites = Column(ARRAY(String), default=[])
    learning_objectives = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    course_metadata = Column('metadata', JSON, default={})


class SQLCourseRepository(CourseRepository):
    def __init__(self, database_url: str):
        # Only use check_same_thread for SQLite
        if database_url.startswith("sqlite"):
            self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    async def initialize(self):
        """Create database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    async def save_course(self, course: Course) -> Course:
        """Save a new course."""
        with self.SessionLocal() as session:
            db_course = CourseModel(
                id=str(course.id),
                course_number=course.course_number,
                name=course.name,
                description=course.description,
                prompt_context=course.prompt_context,
                degree_id=str(course.degree_id) if course.degree_id else None,
                credits=course.credits,
                semester=course.semester,
                professor=course.professor,
                attributes=course.attributes,
                prerequisites=course.prerequisites,
                learning_objectives=course.learning_objectives,
                is_active=course.is_active,
                created_at=course.created_at,
                updated_at=course.updated_at,
                course_metadata=course.metadata,
            )
            session.add(db_course)
            session.commit()
            session.refresh(db_course)
        
        return course
    
    async def get_course(self, course_id: UUID) -> Optional[Course]:
        """Get a course by ID."""
        with self.SessionLocal() as session:
            db_course = session.query(CourseModel).filter(
                CourseModel.id == str(course_id)
            ).first()
            
            if not db_course:
                return None
            
            return self._to_domain_model(db_course)
    
    async def get_courses_by_degree(self, degree_id: UUID) -> List[Course]:
        """Get all courses for a specific degree."""
        with self.SessionLocal() as session:
            db_courses = session.query(CourseModel).filter(
                CourseModel.degree_id == str(degree_id)
            ).all()
            return [self._to_domain_model(c) for c in db_courses]
    
    async def get_all_courses(self) -> List[Course]:
        """Get all courses."""
        with self.SessionLocal() as session:
            db_courses = session.query(CourseModel).all()
            return [self._to_domain_model(c) for c in db_courses]
    
    async def update_course(self, course: Course) -> Course:
        """Update an existing course."""
        with self.SessionLocal() as session:
            db_course = session.query(CourseModel).filter(
                CourseModel.id == str(course.id)
            ).first()
            
            if not db_course:
                raise ValueError(f"Course not found: {course.id}")
            
            db_course.course_number = course.course_number
            db_course.name = course.name
            db_course.description = course.description
            db_course.prompt_context = course.prompt_context
            db_course.degree_id = str(course.degree_id) if course.degree_id else None
            db_course.credits = course.credits
            db_course.semester = course.semester
            db_course.professor = course.professor
            db_course.attributes = course.attributes
            db_course.prerequisites = course.prerequisites
            db_course.learning_objectives = course.learning_objectives
            db_course.is_active = course.is_active
            db_course.updated_at = datetime.utcnow()
            db_course.course_metadata = course.metadata
            
            session.commit()
            session.refresh(db_course)
        
        return course
    
    async def delete_course(self, course_id: UUID) -> bool:
        """Delete a course."""
        with self.SessionLocal() as session:
            db_course = session.query(CourseModel).filter(
                CourseModel.id == str(course_id)
            ).first()
            
            if not db_course:
                return False
            
            session.delete(db_course)
            session.commit()
            return True
    
    async def get_active_courses(self) -> List[Course]:
        """Get all active courses."""
        with self.SessionLocal() as session:
            db_courses = session.query(CourseModel).filter(
                CourseModel.is_active == True
            ).all()
            return [self._to_domain_model(c) for c in db_courses]
    
    async def get_course_by_number(self, course_number: str) -> Optional[Course]:
        """Get a course by its course number."""
        with self.SessionLocal() as session:
            db_course = session.query(CourseModel).filter(
                CourseModel.course_number == course_number
            ).first()
            
            if not db_course:
                return None
            
            return self._to_domain_model(db_course)
    
    def _to_domain_model(self, db_model: CourseModel) -> Course:
        """Convert database model to domain model."""
        return Course(
            id=UUID(db_model.id),
            course_number=db_model.course_number,
            name=db_model.name,
            description=db_model.description,
            prompt_context=db_model.prompt_context,
            degree_id=UUID(db_model.degree_id) if db_model.degree_id else None,
            credits=db_model.credits,
            semester=db_model.semester,
            professor=db_model.professor,
            attributes=db_model.attributes or [],
            prerequisites=db_model.prerequisites or [],
            learning_objectives=db_model.learning_objectives or [],
            is_active=db_model.is_active,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
            metadata=db_model.course_metadata or {},
        )
    
    async def close(self):
        """Close database connection."""
        self.engine.dispose()