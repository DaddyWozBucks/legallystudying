from typing import Optional, Dict, Any
import logging
import httpx
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        pass
    
    async def generate(self, prompt: str) -> str:
        """Alias for generate_response for compatibility."""
        return await self.generate_response(prompt)


class OpenRouterLLMService(LLMService):
    """OpenRouter API implementation supporting multiple LLM providers."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3-haiku",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        site_url: Optional[str] = None,
        app_name: str = "LegalDify",
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = "https://openrouter.ai/api/v1"
        self.site_url = site_url
        self.app_name = app_name
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response using OpenRouter API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url or "http://localhost:8000",
            "X-Title": self.app_name,
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant analyzing documents."},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60.0,
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling OpenRouter API: {e}")
                raise
            except Exception as e:
                logger.error(f"Error calling OpenRouter API: {e}")
                raise


class AnthropicLLMService(LLMService):
    """Anthropic Claude API implementation of LLM service."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = "https://api.anthropic.com/v1"
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response using Anthropic API."""
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=30.0,
                )
                response.raise_for_status()
                
                result = response.json()
                return result["content"][0]["text"]
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling Anthropic API: {e}")
                raise
            except Exception as e:
                logger.error(f"Error calling Anthropic API: {e}")
                raise


class OpenAILLMService(LLMService):
    """OpenAI API implementation of LLM service."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response using OpenAI API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant analyzing documents."},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0,
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling OpenAI API: {e}")
                raise
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                raise


class LocalLLMService(LLMService):
    """Local LLM implementation (e.g., using Ollama or similar)."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        temperature: float = 0.7,
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response using local LLM."""
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False,
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=60.0,
                )
                response.raise_for_status()
                
                result = response.json()
                return result["response"]
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling local LLM: {e}")
                raise
            except Exception as e:
                logger.error(f"Error calling local LLM: {e}")
                raise


class MockLLMService(LLMService):
    """Mock LLM service for testing without API calls."""
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a mock response."""
        # Check if this is a summary request
        if "summary" in prompt.lower() and "key points" in prompt.lower():
            return """SUMMARY:
This document appears to be a legal agreement that outlines terms and conditions between parties. The document contains standard legal provisions including scope of services, payment terms, confidentiality clauses, and termination conditions. The agreement is structured in a formal legal format with numbered sections and subsections.

KEY POINTS:
- Legal services agreement with defined scope and terms
- Clear payment structure and billing procedures outlined
- Confidentiality and data protection provisions included
- Termination clauses with notice requirements specified
- Governing law and dispute resolution mechanisms defined"""
        
        # Default response for other queries
        return f"This is a mock response to your query. The system analyzed the provided context and generated this placeholder answer. In production, this would be replaced with actual LLM-generated content."