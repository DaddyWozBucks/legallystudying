import mobi
import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from bs4 import BeautifulSoup

from infrastructure.plugins.base_plugin import IDataSourcePlugin


class MOBIParser(IDataSourcePlugin):
    """Parser for MOBI/AZW e-book files."""
    
    @staticmethod
    def get_name() -> str:
        return "MOBI/AZW Parser"
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        return [".mobi", ".azw", ".azw3"]
    
    @staticmethod
    def get_description() -> str:
        return "Extracts text and metadata from MOBI/AZW e-books"
    
    async def parse(self, file_path: str) -> str:
        """Parse MOBI/AZW file and return formatted text."""
        try:
            # Create a temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract MOBI file
                tempdir, filepath = mobi.extract(file_path, temp_dir)
                
                # Find the extracted HTML file
                html_files = list(Path(tempdir).glob("*.html"))
                if not html_files:
                    # Try to find any text content
                    return self._extract_raw_text(file_path)
                
                # Parse the main HTML file
                main_html = html_files[0]
                
                # Read and parse HTML content
                with open(main_html, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                
                # Extract text from HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract metadata if available
                metadata = self._extract_metadata_from_html(soup)
                
                # Extract text content
                text_content = self._extract_text_from_html(soup)
                
                # Format output
                output = []
                
                if metadata:
                    output.append("=== BOOK METADATA ===")
                    for key, value in metadata.items():
                        if value:
                            output.append(f"{key}: {value}")
                    output.append("")
                
                output.append("=== CONTENT ===")
                output.append(text_content)
                
                return "\n".join(output)
                
        except Exception as e:
            # Fallback to basic text extraction
            return self._extract_raw_text(file_path)
    
    def _extract_metadata_from_html(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML if available."""
        metadata = {}
        
        # Try to find title
        title_tag = soup.find('title')
        if title_tag:
            metadata['Title'] = title_tag.text.strip()
        
        # Try to find meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'author':
                metadata['Author'] = content
            elif name == 'description':
                metadata['Description'] = content
            elif name == 'publisher':
                metadata['Publisher'] = content
        
        return metadata
    
    def _extract_text_from_html(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to identify chapters
        chapters = []
        chapter_markers = soup.find_all(['h1', 'h2', 'h3'])
        
        if chapter_markers:
            for i, marker in enumerate(chapter_markers):
                # Get chapter title
                chapter_title = marker.text.strip()
                
                # Get content until next chapter
                content = []
                for sibling in marker.find_next_siblings():
                    if sibling in chapter_markers:
                        break
                    text = sibling.get_text().strip()
                    if text:
                        content.append(text)
                
                if content:
                    chapters.append(f"\n[CHAPTER_START:{i+1}]\n# {chapter_title}\n" + 
                                  "\n".join(content) + f"\n[CHAPTER_END:{i+1}]\n")
        
        if chapters:
            return "\n".join(chapters)
        
        # Fallback to basic text extraction
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Fix common issues
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_raw_text(self, file_path: str) -> str:
        """Fallback method to extract raw text from MOBI file."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Try to decode as UTF-8, ignoring errors
            text = content.decode('utf-8', errors='ignore')
            
            # Clean up the text
            # Remove non-printable characters
            text = ''.join(char for char in text if char.isprintable() or char.isspace())
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()
            
        except Exception as e:
            return f"Error extracting text from MOBI file: {str(e)}"