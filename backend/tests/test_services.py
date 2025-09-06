import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from pathlib import Path

from app.services.embedding_service import EmbeddingService
from app.services.chunking_service import ChunkingService
from app.services.parser_service import ParserService
from app.services.llm_service import MockLLMService, OpenRouterLLMService
from infrastructure.plugins.plugin_manager import PluginManager


class TestEmbeddingService:
    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        with patch('app.services.embedding_service.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
            mock_st.return_value = mock_model
            
            service = EmbeddingService(model_name="test-model")
            
            embedding = await service.generate_embedding("test text")
            
            assert isinstance(embedding, list)
            assert len(embedding) == 3
            assert embedding == [0.1, 0.2, 0.3]
            mock_model.encode.assert_called_once_with("test text", convert_to_tensor=False)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self):
        with patch('app.services.embedding_service.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
            mock_st.return_value = mock_model
            
            service = EmbeddingService(model_name="test-model")
            
            embeddings = await service.generate_embeddings(["text1", "text2"])
            
            assert isinstance(embeddings, list)
            assert len(embeddings) == 2
            assert embeddings[0] == [0.1, 0.2]
            assert embeddings[1] == [0.3, 0.4]
    
    def test_get_embedding_dimension(self):
        with patch('app.services.embedding_service.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            
            service = EmbeddingService(model_name="test-model")
            
            dimension = service.get_embedding_dimension()
            
            assert dimension == 384


class TestChunkingService:
    def test_chunk_text_simple(self):
        from uuid import uuid4
        
        service = ChunkingService(chunk_size=50, chunk_overlap=10)
        
        text = "This is a test text. " * 10  # Create text longer than chunk_size
        doc_id = uuid4()
        
        chunks = service.chunk_text(text, doc_id)
        
        assert len(chunks) > 1
        assert all(chunk.document_id == doc_id for chunk in chunks)
        assert all(len(chunk.content) <= 50 for chunk in chunks)
        assert chunks[0].sequence_number == 0
        assert chunks[1].sequence_number == 1
    
    def test_chunk_pages(self):
        from uuid import uuid4
        
        service = ChunkingService(chunk_size=100, chunk_overlap=20)
        
        pages = [
            {"text_content": "Page 1 content", "metadata": {"page_number": 1}},
            {"text_content": "Page 2 content", "metadata": {"page_number": 2}},
        ]
        doc_id = uuid4()
        
        chunks = service.chunk_text(pages, doc_id)
        
        assert len(chunks) == 2
        assert chunks[0].page_number == 1
        assert chunks[1].page_number == 2
        assert chunks[0].content == "Page 1 content"
        assert chunks[1].content == "Page 2 content"
    
    def test_chunk_with_overlap(self):
        from uuid import uuid4
        
        service = ChunkingService(chunk_size=20, chunk_overlap=5)
        
        text = "A" * 50  # Create a long string
        doc_id = uuid4()
        
        chunks = service.chunk_text(text, doc_id)
        
        assert len(chunks) > 2
        # Check that chunks have the expected overlap
        for i in range(len(chunks) - 1):
            assert len(chunks[i].content) <= 20


class TestParserService:
    @pytest.mark.asyncio
    async def test_parse_with_specific_plugin(self):
        mock_plugin_manager = Mock(spec=PluginManager)
        mock_plugin = Mock()
        mock_plugin.get_name.return_value = "test_parser"
        mock_plugin.process = AsyncMock(return_value=[{"text_content": "parsed text"}])
        
        mock_plugin_manager.get_plugin_instance.return_value = mock_plugin
        
        service = ParserService(mock_plugin_manager)
        
        result = await service.parse("/test/file.pdf", "test_parser")
        
        assert result == [{"text_content": "parsed text"}]
        mock_plugin_manager.get_plugin_instance.assert_called_once_with("test_parser")
        mock_plugin.process.assert_called_once_with("/test/file.pdf")
    
    @pytest.mark.asyncio
    async def test_parse_auto_select_plugin(self):
        mock_plugin_manager = Mock(spec=PluginManager)
        mock_plugin = Mock()
        mock_plugin.get_name.return_value = "pdf_parser"
        mock_plugin.process = AsyncMock(return_value=[{"text_content": "pdf content"}])
        
        mock_plugin_manager.find_plugin_for_file.return_value = mock_plugin
        
        service = ParserService(mock_plugin_manager)
        
        result = await service.parse("/test/file.pdf")
        
        assert result == [{"text_content": "pdf content"}]
        mock_plugin_manager.find_plugin_for_file.assert_called_once_with("/test/file.pdf")
    
    @pytest.mark.asyncio
    async def test_parse_no_plugin_found(self):
        mock_plugin_manager = Mock(spec=PluginManager)
        mock_plugin_manager.find_plugin_for_file.return_value = None
        
        service = ParserService(mock_plugin_manager)
        
        with pytest.raises(ValueError, match="No parser plugin found"):
            await service.parse("/test/file.unknown")
    
    def test_get_supported_formats(self):
        mock_plugin_manager = Mock(spec=PluginManager)
        mock_plugin_manager.list_available_plugins.return_value = [
            {"name": "pdf_parser", "supported_formats": [".pdf"], "loaded": True},
            {"name": "docx_parser", "supported_formats": [".docx", ".doc"], "loaded": True},
        ]
        
        service = ParserService(mock_plugin_manager)
        
        formats = service.get_supported_formats()
        
        assert sorted(formats) == [".doc", ".docx", ".pdf"]


class TestLLMServices:
    @pytest.mark.asyncio
    async def test_mock_llm_service(self):
        service = MockLLMService()
        
        response = await service.generate_response("Test prompt")
        
        assert "mock response" in response
        assert "Test prompt" in response
    
    @pytest.mark.asyncio
    async def test_openrouter_service_init(self):
        service = OpenRouterLLMService(
            api_key="test_key",
            model="anthropic/claude-3-haiku",
            temperature=0.5,
            max_tokens=1000,
        )
        
        assert service.api_key == "test_key"
        assert service.model == "anthropic/claude-3-haiku"
        assert service.temperature == 0.5
        assert service.max_tokens == 1000
        assert service.base_url == "https://openrouter.ai/api/v1"
    
    @pytest.mark.asyncio
    async def test_openrouter_generate_response(self):
        service = OpenRouterLLMService(api_key="test_key")
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = mock_client_class.return_value.__aenter__.return_value
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "AI response"}}]
            }
            mock_response.raise_for_status = Mock()
            mock_client.post = AsyncMock(return_value=mock_response)
            
            response = await service.generate_response("Test prompt")
            
            assert response == "AI response"
            mock_client.post.assert_called_once()
            
            # Verify the request was made with correct parameters
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://openrouter.ai/api/v1/chat/completions"
            assert "Authorization" in call_args[1]["headers"]
            assert call_args[1]["json"]["model"] == "anthropic/claude-3-haiku"