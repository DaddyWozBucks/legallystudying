import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path
import logging

from infrastructure.plugins.base_plugin import IDataSourcePlugin

logger = logging.getLogger(__name__)


class PDFPyMuPDFPlugin(IDataSourcePlugin):
    """High-speed PDF parser using PyMuPDF for general text extraction."""
    
    @staticmethod
    def get_name() -> str:
        return "pdf_pymupdf_parser"
    
    @staticmethod
    def get_supported_identifiers() -> List[str]:
        return [".pdf"]
    
    async def process(self, source_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF using PyMuPDF."""
        
        if not Path(source_path).exists():
            raise FileNotFoundError(f"File not found: {source_path}")
        
        chunks = []
        
        try:
            with fitz.open(source_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    text = page.get_text()
                    
                    if text.strip():
                        chunks.append({
                            "text_content": text,
                            "metadata": {
                                "page_number": page_num + 1,
                                "source_file": Path(source_path).name,
                                "parser": self.get_name(),
                            }
                        })
                
                logger.info(f"Extracted {len(chunks)} pages from {source_path}")
                
        except Exception as e:
            logger.error(f"Error processing PDF with PyMuPDF: {e}")
            raise
        
        return chunks