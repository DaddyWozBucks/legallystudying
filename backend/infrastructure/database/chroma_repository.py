import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
import os

from domain.entities.document import TextChunk
from domain.repositories.document_repository import VectorRepository

logger = logging.getLogger(__name__)


class ChromaVectorRepository(VectorRepository):
    def __init__(self, persist_directory: str = None, collection_name: str = "documents"):
        # Check if we should use HTTP client (for Docker deployment)
        chroma_host = os.getenv("CHROMA_HOST")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        
        if chroma_host:
            # Use HTTP client for external ChromaDB server
            logger.info(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}")
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=int(chroma_port),
            )
        else:
            # Use persistent client for local development
            if not persist_directory:
                persist_directory = "./chroma_db"
            logger.info(f"Using local ChromaDB at {persist_directory}")
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
        
        self.collection_name = collection_name
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists, create if not."""
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    async def save_chunks(self, chunks: List[TextChunk]) -> None:
        """Save text chunks with their embeddings to ChromaDB."""
        if not chunks:
            return
        
        ids = [str(chunk.id) for chunk in chunks]
        embeddings = [chunk.embedding for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        
        metadatas = []
        for chunk in chunks:
            metadata = {
                "document_id": str(chunk.document_id),
                "sequence_number": chunk.sequence_number,
            }
            if chunk.page_number is not None:
                metadata["page_number"] = chunk.page_number
            if chunk.metadata:
                metadata.update(chunk.metadata)
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        
        logger.info(f"Saved {len(chunks)} chunks to ChromaDB")
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[TextChunk, float]]:
        """Search for similar chunks using vector similarity."""
        
        where_clause = None
        if metadata_filter:
            where_clause = self._build_where_clause(metadata_filter)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )
        
        chunks_with_scores = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                chunk = TextChunk(
                    id=UUID(chunk_id),
                    document_id=UUID(results["metadatas"][0][i]["document_id"]),
                    content=results["documents"][0][i],
                    sequence_number=results["metadatas"][0][i]["sequence_number"],
                    page_number=results["metadatas"][0][i].get("page_number"),
                    metadata=results["metadatas"][0][i],
                )
                
                similarity_score = 1.0 - results["distances"][0][i]
                chunks_with_scores.append((chunk, similarity_score))
        
        return chunks_with_scores
    
    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete all chunks belonging to a specific document."""
        self.collection.delete(
            where={"document_id": str(document_id)}
        )
        logger.info(f"Deleted chunks for document: {document_id}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection."""
        count = self.collection.count()
        
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "metadata": self.collection.metadata,
        }
    
    def _build_where_clause(self, metadata_filter: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from metadata filter."""
        where_clause = {}
        
        for key, value in metadata_filter.items():
            if isinstance(value, dict) and "$in" in value:
                where_clause[key] = {"$in": value["$in"]}
            else:
                where_clause[key] = value
        
        return where_clause