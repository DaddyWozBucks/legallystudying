from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import JSON as PostgresJSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy import JSON
from typing import List, Optional
from uuid import UUID
import json
from datetime import datetime

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository

Base = declarative_base()


class DocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    processing_status = Column(String, default="pending")
    parser_plugin_id = Column(String, nullable=True)
    course_id = Column(String, nullable=True)  # Link to course
    week = Column(Integer, nullable=True)  # Week number for grouping
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    doc_metadata = Column('metadata', JSON, default={})
    raw_text = Column(Text, nullable=True)  # Store extracted text


class SQLDocumentRepository(DocumentRepository):
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
    
    async def save_document(self, document: Document) -> Document:
        """Save a new document."""
        with self.SessionLocal() as session:
            db_document = DocumentModel(
                id=str(document.id),
                name=document.name,
                path=document.path,
                content_hash=document.content_hash,
                file_type=document.file_type,
                size_bytes=document.size_bytes,
                processing_status=document.processing_status,
                parser_plugin_id=document.parser_plugin_id,
                course_id=str(document.course_id) if document.course_id else None,
                week=document.week,
                error_message=document.error_message,
                created_at=document.created_at,
                updated_at=document.updated_at,
                doc_metadata=document.metadata,
                raw_text=(json.dumps(document.raw_text) if isinstance(document.raw_text, (dict, list)) else document.raw_text or '').replace('\x00', ''),
            )
            session.add(db_document)
            session.commit()
            session.refresh(db_document)
        
        return document
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID."""
        with self.SessionLocal() as session:
            db_document = session.query(DocumentModel).filter(
                DocumentModel.id == str(document_id)
            ).first()
            
            if not db_document:
                return None
            
            return self._to_domain_model(db_document)
    
    async def get_all_documents(self) -> List[Document]:
        """Get all documents."""
        with self.SessionLocal() as session:
            db_documents = session.query(DocumentModel).all()
            return [self._to_domain_model(doc) for doc in db_documents]
    
    async def update_document(self, document: Document) -> Document:
        """Update an existing document."""
        with self.SessionLocal() as session:
            db_document = session.query(DocumentModel).filter(
                DocumentModel.id == str(document.id)
            ).first()
            
            if not db_document:
                raise ValueError(f"Document not found: {document.id}")
            
            db_document.name = document.name
            db_document.path = document.path
            db_document.processing_status = document.processing_status
            db_document.parser_plugin_id = document.parser_plugin_id
            db_document.course_id = str(document.course_id) if document.course_id else None
            db_document.week = document.week
            db_document.error_message = document.error_message
            db_document.updated_at = datetime.utcnow()
            db_document.doc_metadata = document.metadata
            # Ensure raw_text is a string, not a dict or list
            if isinstance(document.raw_text, (dict, list)):
                raw_text = json.dumps(document.raw_text)
            else:
                raw_text = document.raw_text
            
            # Clean null bytes that PostgreSQL cannot handle
            if raw_text:
                db_document.raw_text = raw_text.replace('\x00', '')
            else:
                db_document.raw_text = raw_text
            
            session.commit()
            session.refresh(db_document)
        
        return document
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document."""
        with self.SessionLocal() as session:
            db_document = session.query(DocumentModel).filter(
                DocumentModel.id == str(document_id)
            ).first()
            
            if not db_document:
                return False
            
            session.delete(db_document)
            session.commit()
            return True
    
    def _to_domain_model(self, db_model: DocumentModel) -> Document:
        """Convert database model to domain model."""
        return Document(
            id=UUID(db_model.id),
            name=db_model.name,
            path=db_model.path,
            content_hash=db_model.content_hash,
            file_type=db_model.file_type,
            size_bytes=db_model.size_bytes,
            processing_status=db_model.processing_status,
            parser_plugin_id=db_model.parser_plugin_id,
            course_id=UUID(db_model.course_id) if db_model.course_id else None,
            week=db_model.week if hasattr(db_model, 'week') else None,
            error_message=db_model.error_message,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
            metadata=db_model.doc_metadata or {},
            raw_text=db_model.raw_text if hasattr(db_model, 'raw_text') else None,
        )
    
    async def close(self):
        """Close database connection."""
        self.engine.dispose()