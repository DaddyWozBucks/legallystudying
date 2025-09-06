import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
import json

from app.main import app
from domain.entities.document import Document


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_app_state():
    with patch.object(app, 'state') as mock_state:
        mock_state.plugin_manager = Mock()
        mock_state.document_repo = Mock()
        mock_state.vector_repo = Mock()
        mock_state.embedding_service = Mock()
        mock_state.llm_service = Mock()
        mock_state.parser_service = Mock()
        mock_state.chunking_service = Mock()
        mock_state.settings = Mock(
            max_file_size_mb=100,
            allowed_file_extensions=['.pdf', '.docx', '.txt']
        )
        yield mock_state


class TestHealthEndpoints:
    def test_health_check(self, client, mock_app_state):
        mock_app_state.vector_repo.get_collection_stats = AsyncMock(
            return_value={"total_chunks": 100}
        )
        
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["services"]["vector_database"]["total_chunks"] == 100
    
    def test_readiness_check(self, client, mock_app_state):
        mock_app_state.embedding_service.get_embedding_dimension = Mock(return_value=384)
        mock_app_state.plugin_manager.list_available_plugins = Mock(
            return_value=[{"name": "pdf_parser"}, {"name": "docx_parser"}]
        )
        
        response = client.get("/api/v1/health/readiness")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["embedding_dimension"] == 384
        assert data["plugins_loaded"] == 2


class TestDocumentEndpoints:
    def test_upload_document(self, client, mock_app_state):
        test_document = Document.create(
            name="test.pdf",
            path="/tmp/test.pdf",
            content_hash="hash123",
            file_type=".pdf",
            size_bytes=1000,
        )
        
        mock_app_state.document_repo.save_document = AsyncMock(return_value=test_document)
        mock_app_state.vector_repo.save_chunks = AsyncMock()
        mock_app_state.parser_service.parse = AsyncMock(return_value=[])
        mock_app_state.chunking_service.chunk_text = Mock(return_value=[])
        mock_app_state.embedding_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2])
        
        files = {"file": ("test.pdf", b"PDF content", "application/pdf")}
        response = client.post("/api/v1/documents/upload", files=files)
        
        # Note: This test requires more complex mocking of the ProcessDocumentUseCase
        # In a real implementation, you'd want to mock the use case directly
    
    def test_list_documents(self, client, mock_app_state):
        test_documents = [
            Document.create(
                name="doc1.pdf",
                path="/tmp/doc1.pdf",
                content_hash="hash1",
                file_type=".pdf",
                size_bytes=1000,
            ),
            Document.create(
                name="doc2.pdf",
                path="/tmp/doc2.pdf",
                content_hash="hash2",
                file_type=".pdf",
                size_bytes=2000,
            ),
        ]
        
        mock_app_state.document_repo.get_all_documents = AsyncMock(
            return_value=test_documents
        )
        
        response = client.get("/api/v1/documents/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["documents"]) == 2
        assert data["documents"][0]["name"] == "doc1.pdf"
    
    def test_get_document(self, client, mock_app_state):
        doc_id = uuid4()
        test_document = Document.create(
            name="test.pdf",
            path="/tmp/test.pdf",
            content_hash="hash123",
            file_type=".pdf",
            size_bytes=1000,
        )
        test_document.id = doc_id
        
        mock_app_state.document_repo.get_document = AsyncMock(
            return_value=test_document
        )
        
        response = client.get(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test.pdf"
        assert data["id"] == str(doc_id)
    
    def test_get_document_not_found(self, client, mock_app_state):
        doc_id = uuid4()
        mock_app_state.document_repo.get_document = AsyncMock(return_value=None)
        
        response = client.get(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_document(self, client, mock_app_state):
        doc_id = uuid4()
        mock_app_state.document_repo.delete_document = AsyncMock(return_value=True)
        mock_app_state.vector_repo.delete_by_document = AsyncMock()
        
        response = client.delete(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        mock_app_state.document_repo.delete_document.assert_called_once_with(doc_id)
        mock_app_state.vector_repo.delete_by_document.assert_called_once_with(doc_id)


class TestQueryEndpoints:
    def test_query_documents(self, client, mock_app_state):
        from domain.use_cases.query_documents import QueryResult
        
        query_result = QueryResult(
            answer="This is the answer",
            sources=[{
                "document_id": str(uuid4()),
                "page_number": 1,
                "relevance_score": 0.95,
                "metadata": {}
            }],
            query="test query",
            context_chunks=["chunk 1", "chunk 2"],
        )
        
        mock_app_state.vector_repo.search_similar = AsyncMock()
        mock_app_state.embedding_service.generate_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3]
        )
        mock_app_state.llm_service.generate_response = AsyncMock(
            return_value="This is the answer"
        )
        
        request_data = {
            "query": "test query",
            "top_k": 5
        }
        
        # This test would need proper mocking of the QueryDocumentsUseCase
        # response = client.post("/api/v1/queries/", json=request_data)
    
    def test_semantic_search(self, client, mock_app_state):
        test_chunks = [
            Mock(
                content="Test content",
                document_id=uuid4(),
                page_number=1,
            )
        ]
        
        mock_app_state.embedding_service.generate_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3]
        )
        mock_app_state.vector_repo.search_similar = AsyncMock(
            return_value=[(chunk, 0.95) for chunk in test_chunks]
        )
        
        response = client.post(
            "/api/v1/queries/search",
            params={"query": "test search", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test search"
        assert len(data["results"]) == 1


class TestPluginEndpoints:
    def test_list_plugins(self, client, mock_app_state):
        mock_plugins = [
            {"name": "pdf_parser", "supported_formats": [".pdf"], "loaded": True},
            {"name": "docx_parser", "supported_formats": [".docx"], "loaded": True},
        ]
        
        mock_app_state.plugin_manager.list_available_plugins = Mock(
            return_value=mock_plugins
        )
        mock_app_state.parser_service.get_supported_formats = Mock(
            return_value=[".pdf", ".docx"]
        )
        
        response = client.get("/api/v1/plugins/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["plugins"]) == 2
        assert ".pdf" in data["supported_formats"]
    
    def test_get_plugin_info(self, client, mock_app_state):
        mock_plugins = [
            {"name": "pdf_parser", "supported_formats": [".pdf"], "loaded": True},
        ]
        
        mock_app_state.plugin_manager.list_available_plugins = Mock(
            return_value=mock_plugins
        )
        
        response = client.get("/api/v1/plugins/pdf_parser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "pdf_parser"
        assert ".pdf" in data["supported_formats"]
    
    def test_get_plugin_not_found(self, client, mock_app_state):
        mock_app_state.plugin_manager.list_available_plugins = Mock(return_value=[])
        
        response = client.get("/api/v1/plugins/nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()