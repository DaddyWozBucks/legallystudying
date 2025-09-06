from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.degree import Degree


class DegreeRepository(ABC):
    """Abstract repository for Degree entities."""
    
    @abstractmethod
    async def save_degree(self, degree: Degree) -> Degree:
        """Save a new degree."""
        pass
    
    @abstractmethod
    async def get_degree(self, degree_id: UUID) -> Optional[Degree]:
        """Get a degree by ID."""
        pass
    
    @abstractmethod
    async def get_all_degrees(self) -> List[Degree]:
        """Get all degrees."""
        pass
    
    @abstractmethod
    async def update_degree(self, degree: Degree) -> Degree:
        """Update an existing degree."""
        pass
    
    @abstractmethod
    async def delete_degree(self, degree_id: UUID) -> bool:
        """Delete a degree."""
        pass
    
    @abstractmethod
    async def get_active_degrees(self) -> List[Degree]:
        """Get all active degrees."""
        pass