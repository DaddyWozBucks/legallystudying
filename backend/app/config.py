from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    app_name: str = "LegalDify Backend"
    debug: bool = False
    
    host: str = "127.0.0.1"
    port: int = 8000
    
    database_url: str = "sqlite:///./legal_dify.db"
    
    chroma_persist_directory: Path = Path("./chroma_db")
    chroma_collection_name: str = "legal_documents"
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    llm_provider: str = "openrouter"
    llm_model: str = "anthropic/claude-3-haiku"
    llm_api_key: Optional[str] = None
    openrouter_site_url: Optional[str] = None
    openrouter_app_name: str = "LegalDify"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    # ElevenLabs TTS Configuration
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default)
    elevenlabs_model_id: str = "eleven_monolingual_v1"
    
    plugins_directory: Path = Path("./plugins")
    
    max_file_size_mb: int = 100
    allowed_file_extensions: list[str] = [".pdf", ".docx", ".txt", ".md"]
    
    log_level: str = "INFO"
    

settings = Settings()