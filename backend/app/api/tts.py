from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel
import logging

from app.services.tts_service import ElevenLabsTTSService

logger = logging.getLogger(__name__)

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = None


@router.post("/generate")
async def generate_speech(
    request: Request,
    body: TTSRequest
):
    """Generate speech from text using ElevenLabs TTS."""
    
    try:
        tts_service = ElevenLabsTTSService()
        
        # Generate audio
        audio_data = await tts_service.text_to_speech(
            text=body.text,
            voice_id=body.voice_id,
            model_id=body.model_id
        )
        
        # Return audio as response
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate speech")


@router.post("/generate-stream")
async def generate_speech_stream(
    request: Request,
    body: TTSRequest
):
    """Stream generated speech from text using ElevenLabs TTS."""
    
    try:
        tts_service = ElevenLabsTTSService()
        
        # Create async generator for streaming
        async def audio_stream():
            async for chunk in tts_service.text_to_speech_stream(
                text=body.text,
                voice_id=body.voice_id,
                model_id=body.model_id
            ):
                yield chunk
        
        # Return streaming response
        return StreamingResponse(
            audio_stream(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "no-cache"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream speech")


@router.get("/voices")
async def get_available_voices(request: Request):
    """Get list of available voices from ElevenLabs."""
    
    try:
        tts_service = ElevenLabsTTSService()
        voices = await tts_service.get_voices()
        return voices
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch voices")


@router.post("/summary/{document_id}/speak")
async def speak_document_summary(
    request: Request,
    document_id: str,
    voice_id: Optional[str] = None
):
    """Generate speech for a document summary."""
    
    try:
        # Get the document summary
        from uuid import UUID
        doc_id = UUID(document_id)
        
        # Get document from repository
        document = await request.app.state.document_repo.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if summary exists
        if not hasattr(document, 'summary') or not document.summary:
            # Generate summary first
            from domain.use_cases.summarize_document import SummarizeDocumentUseCase
            
            use_case = SummarizeDocumentUseCase(
                document_repo=request.app.state.document_repo,
                vector_repo=request.app.state.vector_repo,
                llm_service=request.app.state.llm_service,
                prompt_repo=request.app.state.prompt_repo,
                course_repo=request.app.state.course_repo,
                degree_repo=request.app.state.degree_repo,
            )
            
            summary = await use_case.execute(doc_id)
            summary_text = summary.content
        else:
            summary_text = document.summary
        
        # Generate speech from summary
        tts_service = ElevenLabsTTSService()
        audio_data = await tts_service.text_to_speech(
            text=summary_text,
            voice_id=voice_id
        )
        
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=summary_{document_id}.mp3",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary speech: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate summary speech")