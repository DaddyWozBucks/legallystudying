from typing import List, Dict, Any
from uuid import UUID
import logging

from domain.entities.document import TextChunk

logger = logging.getLogger(__name__)


class ChunkingService:
    """Service for splitting text into chunks for embedding."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def chunk_text(self, text: str, document_id: UUID) -> List[TextChunk]:
        """Split text into overlapping chunks."""
        
        if isinstance(text, list):
            chunks_data = self._chunk_pages(text, document_id)
        else:
            chunks_data = self._recursive_chunk(text, document_id)
        
        return chunks_data
    
    def _chunk_pages(self, pages: List[Dict], document_id: UUID) -> List[TextChunk]:
        """Chunk text that's already split by pages."""
        chunks = []
        sequence_number = 0
        
        for page_data in pages:
            if isinstance(page_data, dict):
                page_text = page_data.get("text_content", "")
                page_number = page_data.get("metadata", {}).get("page_number")
            else:
                page_text = page_data
                page_number = None
            
            page_chunks = self._split_text_into_chunks(page_text)
            
            for chunk_text in page_chunks:
                chunk = TextChunk.create(
                    document_id=document_id,
                    content=chunk_text,
                    sequence_number=sequence_number,
                    page_number=page_number,
                )
                chunks.append(chunk)
                sequence_number += 1
        
        return chunks
    
    def _recursive_chunk(self, text: str, document_id: UUID) -> List[TextChunk]:
        """Recursively split text into chunks."""
        chunks = []
        sequence_number = 0
        
        text_chunks = self._split_text_into_chunks(text)
        
        for chunk_text in text_chunks:
            chunk = TextChunk.create(
                document_id=document_id,
                content=chunk_text,
                sequence_number=sequence_number,
            )
            chunks.append(chunk)
            sequence_number += 1
        
        logger.info(f"Created {len(chunks)} chunks for document {document_id}")
        return chunks
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if not text:
            return []
        
        separators = ["\n\n", "\n", ". ", " ", ""]
        
        chunks = []
        current_chunk = ""
        
        for separator in separators:
            if separator:
                parts = text.split(separator)
            else:
                parts = list(text)
            
            for part in parts:
                if len(current_chunk) + len(part) + len(separator) <= self.chunk_size:
                    if current_chunk:
                        current_chunk += separator + part
                    else:
                        current_chunk = part
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    if len(part) > self.chunk_size:
                        sub_chunks = [part[i:i+self.chunk_size] 
                                    for i in range(0, len(part), self.chunk_size - self.chunk_overlap)]
                        chunks.extend(sub_chunks[:-1])
                        current_chunk = sub_chunks[-1] if sub_chunks else ""
                    else:
                        if chunks and self.chunk_overlap > 0:
                            overlap_text = chunks[-1][-self.chunk_overlap:]
                            current_chunk = overlap_text + separator + part
                        else:
                            current_chunk = part
            
            if separator:
                break
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks