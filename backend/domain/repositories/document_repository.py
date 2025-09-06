from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from domain.entities.document import Document, TextChunk


class DocumentRepository(ABC):
    @abstractmethod
    async def save_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_all_documents(self) -> List[Document]:
        pass

    @abstractmethod
    async def update_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def delete_document(self, document_id: UUID) -> bool:
        pass


class VectorRepository(ABC):
    @abstractmethod
    async def save_chunks(self, chunks: List[TextChunk]) -> None:
        pass

    @abstractmethod
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[TextChunk, float]]:
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_collection_stats(self) -> Dict[str, Any]:
        pass