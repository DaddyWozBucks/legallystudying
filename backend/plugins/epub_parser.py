import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

from infrastructure.plugins.base_plugin import IDataSourcePlugin


class EPUBParser(IDataSourcePlugin):
    """Parser for EPUB e-book files with chapter extraction support."""
    
    @staticmethod
    def get_name() -> str:
        return "EPUB Parser"
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        return [".epub"]
    
    @staticmethod
    def get_description() -> str:
        return "Extracts text, metadata, and chapter structure from EPUB e-books"
    
    async def parse(self, file_path: str) -> str:
        """Parse EPUB file and return formatted text with chapter markers."""
        book = epub.read_epub(file_path)
        
        # Extract metadata
        metadata = self._extract_metadata(book)
        
        # Extract chapters
        chapters = self._extract_chapters(book)
        
        # Format output with metadata and chapter markers
        output = []
        
        # Add metadata header
        output.append("=== BOOK METADATA ===")
        for key, value in metadata.items():
            if value:
                output.append(f"{key}: {value}")
        output.append("")
        
        # Add table of contents
        output.append("=== TABLE OF CONTENTS ===")
        for i, chapter in enumerate(chapters, 1):
            output.append(f"Chapter {i}: {chapter['title']}")
        output.append("")
        
        # Add chapter content with markers for chunking
        output.append("=== CONTENT ===")
        for i, chapter in enumerate(chapters, 1):
            output.append(f"\n[CHAPTER_START:{i}]")
            output.append(f"# {chapter['title']}")
            output.append(chapter['content'])
            output.append(f"[CHAPTER_END:{i}]\n")
        
        return "\n".join(output)
    
    def _extract_metadata(self, book: epub.EpubBook) -> Dict[str, Any]:
        """Extract metadata from EPUB book."""
        metadata = {}
        
        # Title
        title = book.get_metadata('DC', 'title')
        if title:
            metadata['Title'] = title[0][0] if title[0] else None
        
        # Author(s)
        creators = book.get_metadata('DC', 'creator')
        if creators:
            authors = [creator[0] for creator in creators if creator]
            metadata['Authors'] = ', '.join(authors)
        
        # Publisher
        publisher = book.get_metadata('DC', 'publisher')
        if publisher:
            metadata['Publisher'] = publisher[0][0] if publisher[0] else None
        
        # Language
        language = book.get_metadata('DC', 'language')
        if language:
            metadata['Language'] = language[0][0] if language[0] else None
        
        # ISBN
        identifiers = book.get_metadata('DC', 'identifier')
        for identifier in identifiers:
            if identifier and len(identifier) > 0:
                id_value = identifier[0]
                if 'isbn' in str(id_value).lower():
                    metadata['ISBN'] = id_value
                    break
        
        # Publication date
        date = book.get_metadata('DC', 'date')
        if date:
            metadata['Publication Date'] = date[0][0] if date[0] else None
        
        # Description
        description = book.get_metadata('DC', 'description')
        if description:
            metadata['Description'] = description[0][0] if description[0] else None
        
        return metadata
    
    def _extract_chapters(self, book: epub.EpubBook) -> List[Dict[str, str]]:
        """Extract chapters from EPUB book."""
        chapters = []
        
        # Get spine (reading order)
        spine = book.get_spine()
        
        for item_id, linear in spine:
            item = book.get_item_with_id(item_id)
            
            if item and isinstance(item, epub.EpubHtml):
                # Extract chapter title and content
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # Try to find chapter title
                title = self._find_chapter_title(soup, item)
                
                # Extract text content
                content = self._extract_text_from_html(soup)
                
                # Only add if there's substantial content
                if content and len(content.strip()) > 100:
                    chapters.append({
                        'title': title,
                        'content': content
                    })
        
        return chapters
    
    def _find_chapter_title(self, soup: BeautifulSoup, item: epub.EpubHtml) -> str:
        """Try to find the chapter title from HTML."""
        # Try common heading tags
        for tag in ['h1', 'h2', 'h3']:
            heading = soup.find(tag)
            if heading and heading.text.strip():
                return heading.text.strip()
        
        # Try to get from item title
        if hasattr(item, 'title') and item.title:
            return item.title
        
        # Fallback to generic title
        return "Untitled Section"
    
    def _extract_text_from_html(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Fix common issues
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    async def extract_chapters_separately(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract chapters as separate documents for individual processing."""
        book = epub.read_epub(file_path)
        
        metadata = self._extract_metadata(book)
        chapters = self._extract_chapters(book)
        
        # Format each chapter as a separate document
        chapter_documents = []
        for i, chapter in enumerate(chapters, 1):
            chapter_doc = {
                'chapter_number': i,
                'title': chapter['title'],
                'content': chapter['content'],
                'metadata': {
                    **metadata,
                    'chapter': i,
                    'chapter_title': chapter['title'],
                    'total_chapters': len(chapters)
                }
            }
            chapter_documents.append(chapter_doc)
        
        return chapter_documents