import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
import chromadb

from infrastructure.database.chroma_repository import ChromaVectorRepository
from domain.entities.document import TextChunk


class TestChromaVectorRepository:
    @pytest.fixture
    def mock_chroma_client(self):
        with patch('infrastructure.database.chroma_repository.chromadb.PersistentClient') as mock:
            yield mock
    
    def test_initialization(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository(
            persist_directory="/test/dir",
            collection_name="test_collection"
        )
        
        assert repo.collection == mock_collection
        mock_chroma_client.assert_called_once()
        mock_client_instance.get_collection.assert_called_once_with("test_collection")
    
    def test_initialization_creates_collection(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.side_effect = Exception("Collection not found")
        mock_client_instance.create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository(
            persist_directory="/test/dir",
            collection_name="test_collection"
        )
        
        assert repo.collection == mock_collection
        mock_client_instance.create_collection.assert_called_once_with(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
    
    @pytest.mark.asyncio
    async def test_save_chunks(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository("/test/dir")
        
        chunks = [
            TextChunk(
                id=uuid4(),
                document_id=uuid4(),
                content="Test content 1",
                sequence_number=0,
                page_number=1,
                embedding=[0.1, 0.2, 0.3],
                metadata={"test": "value"}
            ),
            TextChunk(
                id=uuid4(),
                document_id=uuid4(),
                content="Test content 2",
                sequence_number=1,
                page_number=2,
                embedding=[0.4, 0.5, 0.6],
                metadata={}
            ),
        ]
        
        await repo.save_chunks(chunks)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        
        assert len(call_args[1]["ids"]) == 2
        assert len(call_args[1]["embeddings"]) == 2
        assert len(call_args[1]["documents"]) == 2
        assert call_args[1]["documents"][0] == "Test content 1"
        assert call_args[1]["embeddings"][0] == [0.1, 0.2, 0.3]
    
    @pytest.mark.asyncio
    async def test_save_empty_chunks(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository("/test/dir")
        
        await repo.save_chunks([])
        
        mock_collection.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_search_similar(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository("/test/dir")
        
        mock_collection.query.return_value = {
            "ids": [[str(uuid4()), str(uuid4())]],
            "documents": [["Document 1", "Document 2"]],
            "metadatas": [[
                {"document_id": str(uuid4()), "sequence_number": 0, "page_number": 1},
                {"document_id": str(uuid4()), "sequence_number": 1, "page_number": 2},
            ]],
            "distances": [[0.1, 0.2]],
        }
        
        query_embedding = [0.1, 0.2, 0.3]
        results = await repo.search_similar(query_embedding, top_k=2)
        
        assert len(results) == 2
        assert results[0][0].content == "Document 1"
        assert results[0][1] == 0.9  # 1.0 - 0.1
        assert results[1][0].content == "Document 2"
        assert results[1][1] == 0.8  # 1.0 - 0.2
        
        mock_collection.query.assert_called_once_with(
            query_embeddings=[query_embedding],
            n_results=2,
            where=None,
            include=["documents", "metadatas", "distances"],
        )
    
    @pytest.mark.asyncio
    async def test_search_with_metadata_filter(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository("/test/dir")
        
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        
        metadata_filter = {"document_type": "legal", "year": {"$in": [2023, 2024]}}
        await repo.search_similar([0.1, 0.2], top_k=5, metadata_filter=metadata_filter)
        
        expected_where = {
            "document_type": "legal",
            "year": {"$in": [2023, 2024]}
        }
        
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert call_args[1]["where"] == expected_where
    
    @pytest.mark.asyncio
    async def test_delete_by_document(self, mock_chroma_client):
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository("/test/dir")
        
        doc_id = uuid4()
        await repo.delete_by_document(doc_id)
        
        mock_collection.delete.assert_called_once_with(
            where={"document_id": str(doc_id)}
        )
    
    @pytest.mark.asyncio
    async def test_get_collection_stats(self, mock_chroma_client):
        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_collection.metadata = {"hnsw:space": "cosine"}
        mock_client_instance = Mock()
        mock_client_instance.get_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance
        
        repo = ChromaVectorRepository("/test/dir")
        
        stats = await repo.get_collection_stats()
        
        assert stats["collection_name"] == "documents"
        assert stats["total_chunks"] == 42
        assert stats["metadata"] == {"hnsw:space": "cosine"}