import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path
import logging
import pytesseract
from PIL import Image
import io
from pdf2image import convert_from_path
import tempfile

from infrastructure.plugins.base_plugin import IDataSourcePlugin

logger = logging.getLogger(__name__)


class PDFPyMuPDFPlugin(IDataSourcePlugin):
    """High-speed PDF parser using PyMuPDF with OCR support for scanned pages."""
    
    @staticmethod
    def get_name() -> str:
        return "pdf_pymupdf_parser"
    
    @staticmethod
    def get_supported_identifiers() -> List[str]:
        return [".pdf"]
    
    async def process(self, source_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF using PyMuPDF, with OCR fallback for image-based pages."""
        
        if not Path(source_path).exists():
            raise FileNotFoundError(f"File not found: {source_path}")
        
        chunks = []
        
        try:
            with fitz.open(source_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    
                    # First try to extract text normally
                    text = page.get_text()
                    
                    # If no text or very little text found, try OCR
                    if len(text.strip()) < 50:  # Threshold for determining if page is image-based
                        logger.info(f"Page {page_num + 1} appears to be image-based, attempting OCR...")
                        ocr_text = await self._ocr_page(source_path, page_num)
                        if ocr_text:
                            text = ocr_text
                    
                    if text.strip():
                        chunks.append({
                            "text_content": text,
                            "metadata": {
                                "page_number": page_num + 1,
                                "source_file": Path(source_path).name,
                                "parser": self.get_name(),
                                "extraction_method": "OCR" if len(page.get_text().strip()) < 50 else "text"
                            }
                        })
                
                logger.info(f"Extracted {len(chunks)} pages from {source_path}")
                
        except Exception as e:
            logger.error(f"Error processing PDF with PyMuPDF: {e}")
            raise
        
        return chunks
    
    async def _ocr_page(self, pdf_path: str, page_num: int) -> str:
        """Perform OCR on a specific page of the PDF."""
        try:
            # Convert PDF page to image
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(
                    pdf_path,
                    first_page=page_num + 1,
                    last_page=page_num + 1,
                    dpi=300,  # Higher DPI for better OCR accuracy
                    output_folder=temp_dir
                )
                
                if images:
                    # Perform OCR on the image
                    text = pytesseract.image_to_string(
                        images[0],
                        lang='eng',
                        config='--psm 3'  # Automatic page segmentation
                    )
                    return text
                    
        except Exception as e:
            logger.warning(f"OCR failed for page {page_num + 1}: {e}")
            
        return ""