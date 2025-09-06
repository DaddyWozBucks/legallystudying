import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import UUID, uuid4
from pathlib import Path

from domain.entities.document import Document, TextChunk
from domain.use_cases.process_document import ProcessDocumentUseCase
from domain.use_cases.query_documents import QueryDocumentsUseCase


@pytest.fixture
def mock_repositories():
    return {
        "document_repo": Mock(),
        "vector_repo": Mock(),
    }


@pytest.fixture
def mock_services():
    return {
        "parser_service": Mock(),
        "embedding_service": Mock(),
        "chunking_service": Mock(),
        "llm_service": Mock(),
    }


class TestProcessDocumentUseCase:
    @pytest.mark.asyncio
    async def test_process_document_success(self, mock_repositories, mock_services):
        # Arrange
        use_case = ProcessDocumentUseCase(
            document_repo=mock_repositories["document_repo"],
            vector_repo=mock_repositories["vector_repo"],
            parser_service=mock_services["parser_service"],
            embedding_service=mock_services["embedding_service"],
            chunking_service=mock_services["chunking_service"],
        )
        
        test_file = "/test/document.pdf"
        test_document = Document.create(
            name="document.pdf",
            path=test_file,
            content_hash="hash123",
            file_type=".pdf",
            size_bytes=1000,
        )
        
        mock_repositories["document_repo"].save_document = AsyncMock(return_value=test_document)
        mock_repositories["document_repo"].update_document = AsyncMock(return_value=test_document)
        
        mock_services["parser_service"].parse = AsyncMock(return_value=[
            {"text_content": "Test content", "metadata": {"page_number": 1}}
        ])
        
        test_chunks = [
            TextChunk.create(
                document_id=test_document.id,
                content="Test chunk",
                sequence_number=0,
            )
        ]
        mock_services["chunking_service"].chunk_text = Mock(return_value=test_chunks)
        
        mock_services["embedding_service"].generate_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3]
        )
        
        mock_repositories["vector_repo"].save_chunks = AsyncMock()
        
        # Mock file operations
        with pytest.mock.patch("pathlib.Path.exists", return_value=True):
            with pytest.mock.patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 1000
                with pytest.mock.patch("builtins.open", pytest.mock.mock_open(read_data=b"test")):
                    # Act
                    result = await use_case.execute(test_file)
        
        # Assert
        assert result.processing_status == "completed"
        mock_repositories["document_repo"].save_document.assert_called_once()
        mock_services["parser_service"].parse.assert_called_once_with(test_file, None)
        mock_repositories["vector_repo"].save_chunks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_document_file_not_found(self, mock_repositories, mock_services):
        # Arrange
        use_case = ProcessDocumentUseCase(
            document_repo=mock_repositories["document_repo"],
            vector_repo=mock_repositories["vector_repo"],
            parser_service=mock_services["parser_service"],
            embedding_service=mock_services["embedding_service"],
            chunking_service=mock_services["chunking_service"],
        )
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            await use_case.execute("/nonexistent/file.pdf")
    
    @pytest.mark.asyncio
    async def test_process_document_parsing_error(self, mock_repositories, mock_services):
        # Arrange
        use_case = ProcessDocumentUseCase(
            document_repo=mock_repositories["document_repo"],
            vector_repo=mock_repositories["vector_repo"],
            parser_service=mock_services["parser_service"],
            embedding_service=mock_services["embedding_service"],
            chunking_service=mock_services["chunking_service"],
        )
        
        test_file = "/test/document.pdf"
        test_document = Document.create(
            name="document.pdf",
            path=test_file,
            content_hash="hash123",
            file_type=".pdf",
            size_bytes=1000,
        )
        
        mock_repositories["document_repo"].save_document = AsyncMock(return_value=test_document)
        mock_repositories["document_repo"].update_document = AsyncMock(return_value=test_document)
        
        mock_services["parser_service"].parse = AsyncMock(
            side_effect=Exception("Parsing error")
        )
        
        # Mock file operations
        with pytest.mock.patch("pathlib.Path.exists", return_value=True):
            with pytest.mock.patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 1000
                with pytest.mock.patch("builtins.open", pytest.mock.mock_open(read_data=b"test")):
                    # Act & Assert
                    with pytest.raises(Exception, match="Parsing error"):
                        await use_case.execute(test_file)
        
        # Verify document status was updated to failed
        calls = mock_repositories["document_repo"].update_document.call_args_list
        last_call = calls[-1][0][0]
        assert last_call.processing_status == "failed"
        assert "Parsing error" in last_call.error_message


class TestQueryDocumentsUseCase:
    @pytest.mark.asyncio
    async def test_query_documents_success(self, mock_repositories, mock_services):
        # Arrange
        use_case = QueryDocumentsUseCase(
            vector_repo=mock_repositories["vector_repo"],
            embedding_service=mock_services["embedding_service"],
            llm_service=mock_services["llm_service"],
        )
        
        query = "What is the main topic?"
        query_embedding = [0.1, 0.2, 0.3]
        
        mock_services["embedding_service"].generate_embedding = AsyncMock(
            return_value=query_embedding
        )
        
        test_chunks = [
            (TextChunk(
                id=uuid4(),
                document_id=uuid4(),
                content="This is about AI",
                sequence_number=0,
                page_number=1,
                metadata={}
            ), 0.95),
            (TextChunk(
                id=uuid4(),
                document_id=uuid4(),
                content="Machine learning concepts",
                sequence_number=1,
                page_number=2,
                metadata={}
            ), 0.90),
        ]
        
        mock_repositories["vector_repo"].search_similar = AsyncMock(
            return_value=test_chunks
        )
        
        mock_services["llm_service"].generate_response = AsyncMock(
            return_value="The main topic is artificial intelligence and machine learning."
        )
        
        # Act
        result = await use_case.execute(query, top_k=2)
        
        # Assert
        assert result.query == query
        assert result.answer == "The main topic is artificial intelligence and machine learning."
        assert len(result.sources) == 2
        assert len(result.context_chunks) == 2
        
        mock_services["embedding_service"].generate_embedding.assert_called_once_with(query)
        mock_repositories["vector_repo"].search_similar.assert_called_once()
        mock_services["llm_service"].generate_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_with_metadata_filter(self, mock_repositories, mock_services):
        # Arrange
        use_case = QueryDocumentsUseCase(
            vector_repo=mock_repositories["vector_repo"],
            embedding_service=mock_services["embedding_service"],
            llm_service=mock_services["llm_service"],
        )
        
        query = "Find information"
        metadata_filter = {"document_type": "legal"}
        
        mock_services["embedding_service"].generate_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3]
        )
        
        mock_repositories["vector_repo"].search_similar = AsyncMock(return_value=[])
        mock_services["llm_service"].generate_response = AsyncMock(return_value="No relevant information found.")
        
        # Act
        result = await use_case.execute(query, top_k=5, metadata_filter=metadata_filter)
        
        # Assert
        mock_repositories["vector_repo"].search_similar.assert_called_once()
        call_args = mock_repositories["vector_repo"].search_similar.call_args
        assert call_args[1]["metadata_filter"] == metadata_filter