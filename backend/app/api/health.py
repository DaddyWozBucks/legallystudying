from fastapi import APIRouter, Request
from datetime import datetime
from typing import Optional

router = APIRouter()


@router.get("/")
async def health_check(request: Request):
    """Health check endpoint."""
    
    vector_stats = await request.app.state.vector_repo.get_collection_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "embedding_service": "active",
            "llm_service": "active",
            "parser_service": "active",
            "vector_database": {
                "status": "active",
                "total_chunks": vector_stats.get("total_chunks", 0),
            },
        },
    }


@router.get("/readiness")
async def readiness_check(request: Request):
    """Readiness check endpoint."""
    
    try:
        embedding_dimension = request.app.state.embedding_service.get_embedding_dimension()
        
        return {
            "ready": True,
            "embedding_model_loaded": True,
            "embedding_dimension": embedding_dimension,
            "plugins_loaded": len(request.app.state.plugin_manager.list_available_plugins()),
        }
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
        }