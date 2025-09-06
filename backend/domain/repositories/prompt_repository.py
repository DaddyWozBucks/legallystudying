from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.prompt import Prompt


class PromptRepository(ABC):
    """Abstract repository for prompt management."""
    
    @abstractmethod
    async def save_prompt(self, prompt: Prompt) -> Prompt:
        """Save a new prompt."""
        pass
    
    @abstractmethod
    async def get_prompt(self, prompt_id: UUID) -> Optional[Prompt]:
        """Get a prompt by ID."""
        pass
    
    @abstractmethod
    async def get_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get a prompt by its unique name."""
        pass
    
    @abstractmethod
    async def get_prompts_by_category(self, category: str) -> List[Prompt]:
        """Get all prompts in a category."""
        pass
    
    @abstractmethod
    async def get_all_prompts(self) -> List[Prompt]:
        """Get all prompts."""
        pass
    
    @abstractmethod
    async def update_prompt(self, prompt: Prompt) -> Prompt:
        """Update an existing prompt."""
        pass
    
    @abstractmethod
    async def delete_prompt(self, prompt_id: UUID) -> bool:
        """Delete a prompt."""
        pass
    
    @abstractmethod
    async def get_active_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get the active prompt for a specific function."""
        pass