from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import tempfile
from pathlib import Path
import uuid

from domain.use_cases.process_document import ProcessDocumentUseCase
from app.dto.document_dto import DocumentResponse

router = APIRouter()

AUTH_TOKEN = "legal-dify-extension-2024"

class PageContentRequest(BaseModel):
    url: str
    title: str
    content: str
    metadata: Optional[dict] = {}

@router.post("/ingest-page", response_model=DocumentResponse)
async def ingest_page_content(
    request: Request,
    body: PageContentRequest,
    authorization: Optional[str] = Header(None)
):
    """Receive and process text content from Chrome extension."""
    
    if not authorization or authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in body.title[:50])
        filename = f"webpage_{safe_title}_{timestamp}.txt"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(f"URL: {body.url}\n")
            tmp_file.write(f"Title: {body.title}\n")
            tmp_file.write(f"Captured: {datetime.now().isoformat()}\n")
            tmp_file.write("-" * 80 + "\n\n")
            tmp_file.write(body.content)
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
            parser_plugin_id=None,
            original_name=filename
        )
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'tmp_path' in locals():
            Path(tmp_path).unlink(missing_ok=True)

@router.get("/verify-auth")
async def verify_authentication(
    authorization: Optional[str] = Header(None)
):
    """Verify if the provided token is valid."""
    
    if not authorization or authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return {"status": "authenticated", "message": "Token is valid"}