from pathlib import Path
import logging

from app.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import (
    OpenRouterLLMService, 
    AnthropicLLMService, 
    OpenAILLMService, 
    LocalLLMService, 
    MockLLMService
)
from app.services.chunking_service import ChunkingService
from app.services.parser_service import ParserService
from infrastructure.plugins.plugin_manager import PluginManager
from infrastructure.database.chroma_repository import ChromaVectorRepository
from infrastructure.database.document_repository_impl import SQLDocumentRepository
from infrastructure.database.prompt_repository_impl import SQLPromptRepository
from infrastructure.database.degree_repository_impl import SQLDegreeRepository
from infrastructure.database.course_repository_impl import SQLCourseRepository
from app.services.prompt_seeder import PromptSeeder

logger = logging.getLogger(__name__)


class StartupService:
    """Service responsible for initializing all components on startup."""
    
    def __init__(self):
        self.plugin_manager = None
        self.document_repo = None
        self.vector_repo = None
        self.prompt_repo = None
        self.degree_repo = None
        self.course_repo = None
        self.embedding_service = None
        self.llm_service = None
        self.parser_service = None
        self.chunking_service = None
    
    async def initialize(self):
        """Initialize all services and dependencies."""
        logger.info("Initializing services...")
        
        self._initialize_plugin_manager()
        
        await self._initialize_repositories()
        
        self._initialize_ai_services()
        
        self._initialize_processing_services()
        
        logger.info("All services initialized successfully")
    
    def _initialize_plugin_manager(self):
        """Initialize and load plugins."""
        plugins_dir = Path(settings.plugins_directory)
        plugins_dir.mkdir(parents=True, exist_ok=True)
        
        self.plugin_manager = PluginManager(plugins_dir)
        self.plugin_manager.discover_and_load_plugins()
        
        available_plugins = self.plugin_manager.list_available_plugins()
        logger.info(f"Loaded {len(available_plugins)} plugins")
    
    async def _initialize_repositories(self):
        """Initialize data repositories."""
        self.document_repo = SQLDocumentRepository(settings.database_url)
        await self.document_repo.initialize()
        
        self.prompt_repo = SQLPromptRepository(settings.database_url)
        await self.prompt_repo.initialize()
        
        self.degree_repo = SQLDegreeRepository(settings.database_url)
        await self.degree_repo.initialize()
        
        self.course_repo = SQLCourseRepository(settings.database_url)
        await self.course_repo.initialize()
        
        # Seed default prompts
        seeder = PromptSeeder(self.prompt_repo)
        await seeder.seed_default_prompts()
        
        chroma_dir = Path(settings.chroma_persist_directory)
        chroma_dir.mkdir(parents=True, exist_ok=True)
        
        self.vector_repo = ChromaVectorRepository(
            persist_directory=str(chroma_dir),
            collection_name=settings.chroma_collection_name,
        )
        
        logger.info("Data repositories initialized")
    
    def _initialize_ai_services(self):
        """Initialize AI/ML services."""
        self.embedding_service = EmbeddingService(
            model_name=settings.embedding_model
        )
        
        if settings.llm_provider == "openrouter" and settings.llm_api_key:
            self.llm_service = OpenRouterLLMService(
                api_key=settings.llm_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                site_url=settings.openrouter_site_url,
                app_name=settings.openrouter_app_name,
            )
        elif settings.llm_provider == "anthropic" and settings.llm_api_key:
            self.llm_service = AnthropicLLMService(
                api_key=settings.llm_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        elif settings.llm_provider == "openai" and settings.llm_api_key:
            self.llm_service = OpenAILLMService(
                api_key=settings.llm_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        elif settings.llm_provider == "local":
            self.llm_service = LocalLLMService(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
            )
        elif settings.llm_provider == "mock":
            logger.info("Using mock LLM service for testing")
            self.llm_service = MockLLMService()
        else:
            logger.warning("No LLM API key provided, using mock LLM service")
            self.llm_service = MockLLMService()
        
        logger.info(f"AI services initialized with {settings.llm_provider} provider")
    
    def _initialize_processing_services(self):
        """Initialize document processing services."""
        self.parser_service = ParserService(self.plugin_manager)
        
        self.chunking_service = ChunkingService(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        
        logger.info("Processing services initialized")
    
    async def shutdown(self):
        """Clean up resources on shutdown."""
        logger.info("Shutting down services...")
        
        if hasattr(self.document_repo, 'close'):
            await self.document_repo.close()
        
        logger.info("Services shut down successfully")