from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.course import Course


class CourseRepository(ABC):
    """Abstract repository for Course entities."""
    
    @abstractmethod
    async def save_course(self, course: Course) -> Course:
        """Save a new course."""
        pass
    
    @abstractmethod
    async def get_course(self, course_id: UUID) -> Optional[Course]:
        """Get a course by ID."""
        pass
    
    @abstractmethod
    async def get_courses_by_degree(self, degree_id: UUID) -> List[Course]:
        """Get all courses for a specific degree."""
        pass
    
    @abstractmethod
    async def get_all_courses(self) -> List[Course]:
        """Get all courses."""
        pass
    
    @abstractmethod
    async def update_course(self, course: Course) -> Course:
        """Update an existing course."""
        pass
    
    @abstractmethod
    async def delete_course(self, course_id: UUID) -> bool:
        """Delete a course."""
        pass
    
    @abstractmethod
    async def get_active_courses(self) -> List[Course]:
        """Get all active courses."""
        pass
    
    @abstractmethod
    async def get_course_by_number(self, course_number: str) -> Optional[Course]:
        """Get a course by its course number."""
        pass