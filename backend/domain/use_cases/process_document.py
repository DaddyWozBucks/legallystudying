from typing import List, Optional
from uuid import UUID
import hashlib
from pathlib import Path

from domain.entities.document import Document, TextChunk
from domain.repositories.document_repository import DocumentRepository, VectorRepository


class ProcessDocumentUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,
        vector_repo: VectorRepository,
        parser_service,
        embedding_service,
        chunking_service,
    ):
        self.document_repo = document_repo
        self.vector_repo = vector_repo
        self.parser_service = parser_service
        self.embedding_service = embedding_service
        self.chunking_service = chunking_service

    async def execute(self, file_path: str, parser_plugin_id: Optional[str] = None, original_name: Optional[str] = None) -> Document:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_hash = self._calculate_file_hash(file_path)
        
        # Use original name if provided, otherwise use the file path name
        document_name = original_name or path.name
        
        document = Document.create(
            name=document_name,
            path=str(path.absolute()),
            content_hash=file_hash,
            file_type=path.suffix.lower(),
            size_bytes=path.stat().st_size,
        )
        
        saved_document = await self.document_repo.save_document(document)
        
        try:
            saved_document.processing_status = "processing"
            await self.document_repo.update_document(saved_document)
            
            text_content = await self.parser_service.parse(file_path, parser_plugin_id)
            
            # Save the raw text content to the document for quick access
            saved_document.raw_text = text_content[:500000] if text_content else None  # Limit to 500K chars for DB storage
            
            chunks = self.chunking_service.chunk_text(text_content, saved_document.id)
            
            embedded_chunks = []
            for chunk in chunks:
                embedding = await self.embedding_service.generate_embedding(chunk.content)
                chunk.embedding = embedding
                embedded_chunks.append(chunk)
            
            await self.vector_repo.save_chunks(embedded_chunks)
            
            saved_document.processing_status = "completed"
            saved_document.parser_plugin_id = parser_plugin_id
            await self.document_repo.update_document(saved_document)
            
            return saved_document
            
        except Exception as e:
            saved_document.processing_status = "failed"
            saved_document.error_message = str(e)
            await self.document_repo.update_document(saved_document)
            raise

    def _calculate_file_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()