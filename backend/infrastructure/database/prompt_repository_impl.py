from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON as PostgresJSON
from sqlalchemy import JSON
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from domain.entities.prompt import Prompt
from domain.repositories.prompt_repository import PromptRepository
from infrastructure.database.document_repository_impl import Base


class PromptModel(Base):
    __tablename__ = "prompts"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    template = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    prompt_metadata = Column('metadata', JSON, default={})


class SQLPromptRepository(PromptRepository):
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
    
    async def save_prompt(self, prompt: Prompt) -> Prompt:
        """Save a new prompt."""
        with self.SessionLocal() as session:
            db_prompt = PromptModel(
                id=str(prompt.id),
                name=prompt.name,
                description=prompt.description,
                template=prompt.template,
                category=prompt.category,
                is_active=prompt.is_active,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at,
                prompt_metadata=prompt.metadata,
            )
            session.add(db_prompt)
            session.commit()
            session.refresh(db_prompt)
        
        return prompt
    
    async def get_prompt(self, prompt_id: UUID) -> Optional[Prompt]:
        """Get a prompt by ID."""
        with self.SessionLocal() as session:
            db_prompt = session.query(PromptModel).filter(
                PromptModel.id == str(prompt_id)
            ).first()
            
            if not db_prompt:
                return None
            
            return self._to_domain_model(db_prompt)
    
    async def get_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get a prompt by its unique name."""
        with self.SessionLocal() as session:
            db_prompt = session.query(PromptModel).filter(
                PromptModel.name == name
            ).first()
            
            if not db_prompt:
                return None
            
            return self._to_domain_model(db_prompt)
    
    async def get_prompts_by_category(self, category: str) -> List[Prompt]:
        """Get all prompts in a category."""
        with self.SessionLocal() as session:
            db_prompts = session.query(PromptModel).filter(
                PromptModel.category == category
            ).all()
            
            return [self._to_domain_model(p) for p in db_prompts]
    
    async def get_all_prompts(self) -> List[Prompt]:
        """Get all prompts."""
        with self.SessionLocal() as session:
            db_prompts = session.query(PromptModel).all()
            return [self._to_domain_model(p) for p in db_prompts]
    
    async def update_prompt(self, prompt: Prompt) -> Prompt:
        """Update an existing prompt."""
        with self.SessionLocal() as session:
            db_prompt = session.query(PromptModel).filter(
                PromptModel.id == str(prompt.id)
            ).first()
            
            if not db_prompt:
                raise ValueError(f"Prompt not found: {prompt.id}")
            
            db_prompt.name = prompt.name
            db_prompt.description = prompt.description
            db_prompt.template = prompt.template
            db_prompt.category = prompt.category
            db_prompt.is_active = prompt.is_active
            db_prompt.updated_at = datetime.utcnow()
            db_prompt.prompt_metadata = prompt.metadata
            
            session.commit()
            session.refresh(db_prompt)
        
        return prompt
    
    async def delete_prompt(self, prompt_id: UUID) -> bool:
        """Delete a prompt."""
        with self.SessionLocal() as session:
            db_prompt = session.query(PromptModel).filter(
                PromptModel.id == str(prompt_id)
            ).first()
            
            if not db_prompt:
                return False
            
            session.delete(db_prompt)
            session.commit()
            return True
    
    async def get_active_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get the active prompt for a specific function."""
        with self.SessionLocal() as session:
            db_prompt = session.query(PromptModel).filter(
                PromptModel.name == name,
                PromptModel.is_active == True
            ).first()
            
            if not db_prompt:
                return None
            
            return self._to_domain_model(db_prompt)
    
    def _to_domain_model(self, db_model: PromptModel) -> Prompt:
        """Convert database model to domain model."""
        return Prompt(
            id=UUID(db_model.id),
            name=db_model.name,
            description=db_model.description,
            template=db_model.template,
            category=db_model.category,
            is_active=db_model.is_active,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
            metadata=db_model.prompt_metadata or {},
        )
    
    async def close(self):
        """Close database connection."""
        self.engine.dispose()