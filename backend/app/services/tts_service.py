import logging
import httpx
from typing import Optional, AsyncGenerator
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)


class ElevenLabsTTSService:
    """Service for text-to-speech using ElevenLabs API."""
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = settings.elevenlabs_voice_id
        self.model_id = settings.elevenlabs_model_id
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            voice_id: Optional voice ID to use (defaults to config)
            model_id: Optional model ID to use (defaults to config)
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        voice_id = voice_id or self.voice_id
        model_id = model_id or self.model_id
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error generating speech: {str(e)}")
                raise
    
    async def text_to_speech_stream(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream text to speech using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            voice_id: Optional voice ID to use (defaults to config)
            model_id: Optional model ID to use (defaults to config)
            
        Yields:
            Audio data chunks (MP3 format)
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        voice_id = voice_id or self.voice_id
        model_id = model_id or self.model_id
        
        url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    url,
                    json=data,
                    headers=headers,
                    timeout=30.0
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs API error: {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Error streaming speech: {str(e)}")
                raise
    
    async def get_voices(self):
        """Get available voices from ElevenLabs."""
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        url = f"{self.base_url}/voices"
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching voices: {str(e)}")
                raise