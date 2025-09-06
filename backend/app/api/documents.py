from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from typing import List, Optional
from uuid import UUID
from pathlib import Path
import aiofiles
import tempfile

from app.dto.document_dto import DocumentUploadRequest, DocumentResponse, DocumentListResponse, DocumentSummaryResponse, QuestionAnswerRequest, QuestionAnswerResponse
from domain.use_cases.process_document import ProcessDocumentUseCase
from domain.use_cases.summarize_document import SummarizeDocumentUseCase
from domain.use_cases.answer_question import AnswerQuestionUseCase
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    parser_plugin_id: Optional[str] = None,
    course_id: Optional[UUID] = None,
    week: Optional[int] = None,
):
    """Upload and process a document."""
    
    max_file_size = settings.max_file_size_mb * 1024 * 1024
    if file.size and file.size > max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    allowed_extensions = [
        '.pdf', '.docx', '.doc', '.txt', 
        '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif',
        '.epub', '.mobi', '.azw', '.azw3', '.fb2', '.lit', '.pdb'
    ]
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        use_case = ProcessDocumentUseCase(
            document_repo=request.app.state.document_repo,
            vector_repo=request.app.state.vector_repo,
            parser_service=request.app.state.parser_service,
            embedding_service=request.app.state.embedding_service,
            chunking_service=request.app.state.chunking_service,
        )
        
        document = await use_case.execute(
            tmp_path, 
            parser_plugin_id, 
            original_name=file.filename,
            course_id=course_id,
            week=week
        )
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'tmp_path' in locals():
            Path(tmp_path).unlink(missing_ok=True)


@router.post("/ingest", response_model=DocumentResponse)
async def ingest_document(
    request: Request,
    body: DocumentUploadRequest,
):
    """Process a document from a local file path."""
    
    use_case = ProcessDocumentUseCase(
        document_repo=request.app.state.document_repo,
        vector_repo=request.app.state.vector_repo,
        parser_service=request.app.state.parser_service,
        embedding_service=request.app.state.embedding_service,
        chunking_service=request.app.state.chunking_service,
    )
    
    try:
        document = await use_case.execute(body.file_path, body.parser_plugin_id)
        return DocumentResponse.from_orm(document)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    request: Request,
    course_id: Optional[UUID] = None,
    week: Optional[int] = None
):
    """List all documents, optionally filtered by course and/or week."""
    
    documents = await request.app.state.document_repo.get_all_documents()
    
    # Filter by course_id if provided
    if course_id:
        documents = [d for d in documents if d.course_id == course_id]
    
    # Filter by week if provided
    if week is not None:
        documents = [d for d in documents if d.week == week]
    
    return DocumentListResponse(
        documents=[DocumentResponse.from_orm(doc) for doc in documents],
        total=len(documents),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(request: Request, document_id: UUID):
    """Get a specific document by ID."""
    
    document = await request.app.state.document_repo.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse.from_orm(document)


@router.delete("/{document_id}")
async def delete_document(request: Request, document_id: UUID):
    """Delete a document and its associated data."""
    
    success = await request.app.state.document_repo.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await request.app.state.vector_repo.delete_by_document(document_id)
    
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/summarize", response_model=DocumentSummaryResponse)
async def summarize_document(request: Request, document_id: UUID):
    """Generate a summary for a specific document."""
    
    # Check if document exists
    document = await request.app.state.document_repo.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create and execute the summarize use case
    use_case = SummarizeDocumentUseCase(
        document_repo=request.app.state.document_repo,
        vector_repo=request.app.state.vector_repo,
        llm_service=request.app.state.llm_service,
        prompt_repo=request.app.state.prompt_repo,
        course_repo=request.app.state.course_repo,
        degree_repo=request.app.state.degree_repo,
    )
    
    try:
        summary = await use_case.execute(document_id)
        return DocumentSummaryResponse(
            document_id=str(document_id),
            summary=summary.content,
            key_points=summary.key_points,
            generated_at=summary.generated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/qa", response_model=QuestionAnswerResponse)
async def answer_question(
    request: Request, 
    document_id: UUID,
    body: QuestionAnswerRequest
):
    """Answer a question about a specific document."""
    
    # Check if document exists
    document = await request.app.state.document_repo.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create and execute the answer question use case
    use_case = AnswerQuestionUseCase(
        document_repo=request.app.state.document_repo,
        vector_repo=request.app.state.vector_repo,
        llm_service=request.app.state.llm_service,
        embedding_service=request.app.state.embedding_service,
        prompt_repo=request.app.state.prompt_repo,
        course_repo=request.app.state.course_repo,
        degree_repo=request.app.state.degree_repo,
    )
    
    try:
        answer = await use_case.execute(document_id, body.question)
        return QuestionAnswerResponse(
            question=body.question,
            answer=answer.content,
            sources=answer.sources if hasattr(answer, 'sources') else [],
            confidence=answer.confidence if hasattr(answer, 'confidence') else 0.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))