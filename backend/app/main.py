from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import documents, queries, plugins, health, extension, prompts, degrees, courses, tts
from app.services.startup_service import StartupService
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LegalDify Backend Service...")
    
    startup_service = StartupService()
    await startup_service.initialize()
    
    app.state.plugin_manager = startup_service.plugin_manager
    app.state.document_repo = startup_service.document_repo
    app.state.vector_repo = startup_service.vector_repo
    app.state.prompt_repo = startup_service.prompt_repo
    app.state.degree_repo = startup_service.degree_repo
    app.state.course_repo = startup_service.course_repo
    app.state.embedding_service = startup_service.embedding_service
    app.state.llm_service = startup_service.llm_service
    app.state.parser_service = startup_service.parser_service
    app.state.chunking_service = startup_service.chunking_service
    
    logger.info("LegalDify Backend Service started successfully")
    
    yield
    
    logger.info("Shutting down LegalDify Backend Service...")
    await startup_service.shutdown()


app = FastAPI(
    title="LegalDify Backend API",
    description="AI-powered document intelligence platform for macOS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost",
        "http://127.0.0.1",
        "*"  # Allow all origins in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(queries.router, prefix="/api/v1/queries", tags=["queries"])
app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])
app.include_router(extension.router, prefix="/api/v1/extension", tags=["extension"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(degrees.router, prefix="/api/v1/degrees", tags=["degrees"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["tts"])


@app.get("/")
async def root():
    return {
        "service": "LegalDify Backend",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }