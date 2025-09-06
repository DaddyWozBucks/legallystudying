from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from domain.entities.degree import Degree
from domain.repositories.degree_repository import DegreeRepository
from infrastructure.database.document_repository_impl import Base


class DegreeModel(Base):
    __tablename__ = "degrees"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    prompt_context = Column(Text, nullable=False)
    department = Column(String, nullable=False)
    duration_years = Column(Float, default=0.0)
    credit_hours = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    degree_metadata = Column('metadata', JSON, default={})


class SQLDegreeRepository(DegreeRepository):
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
    
    async def save_degree(self, degree: Degree) -> Degree:
        """Save a new degree."""
        with self.SessionLocal() as session:
            db_degree = DegreeModel(
                id=str(degree.id),
                name=degree.name,
                abbreviation=degree.abbreviation,
                description=degree.description,
                prompt_context=degree.prompt_context,
                department=degree.department,
                duration_years=degree.duration_years,
                credit_hours=degree.credit_hours,
                is_active=degree.is_active,
                created_at=degree.created_at,
                updated_at=degree.updated_at,
                degree_metadata=degree.metadata,
            )
            session.add(db_degree)
            session.commit()
            session.refresh(db_degree)
        
        return degree
    
    async def get_degree(self, degree_id: UUID) -> Optional[Degree]:
        """Get a degree by ID."""
        with self.SessionLocal() as session:
            db_degree = session.query(DegreeModel).filter(
                DegreeModel.id == str(degree_id)
            ).first()
            
            if not db_degree:
                return None
            
            return self._to_domain_model(db_degree)
    
    async def get_all_degrees(self) -> List[Degree]:
        """Get all degrees."""
        with self.SessionLocal() as session:
            db_degrees = session.query(DegreeModel).all()
            return [self._to_domain_model(d) for d in db_degrees]
    
    async def update_degree(self, degree: Degree) -> Degree:
        """Update an existing degree."""
        with self.SessionLocal() as session:
            db_degree = session.query(DegreeModel).filter(
                DegreeModel.id == str(degree.id)
            ).first()
            
            if not db_degree:
                raise ValueError(f"Degree not found: {degree.id}")
            
            db_degree.name = degree.name
            db_degree.abbreviation = degree.abbreviation
            db_degree.description = degree.description
            db_degree.prompt_context = degree.prompt_context
            db_degree.department = degree.department
            db_degree.duration_years = degree.duration_years
            db_degree.credit_hours = degree.credit_hours
            db_degree.is_active = degree.is_active
            db_degree.updated_at = datetime.utcnow()
            db_degree.degree_metadata = degree.metadata
            
            session.commit()
            session.refresh(db_degree)
        
        return degree
    
    async def delete_degree(self, degree_id: UUID) -> bool:
        """Delete a degree."""
        with self.SessionLocal() as session:
            db_degree = session.query(DegreeModel).filter(
                DegreeModel.id == str(degree_id)
            ).first()
            
            if not db_degree:
                return False
            
            session.delete(db_degree)
            session.commit()
            return True
    
    async def get_active_degrees(self) -> List[Degree]:
        """Get all active degrees."""
        with self.SessionLocal() as session:
            db_degrees = session.query(DegreeModel).filter(
                DegreeModel.is_active == True
            ).all()
            return [self._to_domain_model(d) for d in db_degrees]
    
    def _to_domain_model(self, db_model: DegreeModel) -> Degree:
        """Convert database model to domain model."""
        return Degree(
            id=UUID(db_model.id),
            name=db_model.name,
            abbreviation=db_model.abbreviation,
            description=db_model.description,
            prompt_context=db_model.prompt_context,
            department=db_model.department,
            duration_years=db_model.duration_years,
            credit_hours=db_model.credit_hours,
            is_active=db_model.is_active,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
            metadata=db_model.degree_metadata or {},
        )
    
    async def close(self):
        """Close database connection."""
        self.engine.dispose()