import pytesseract
from PIL import Image
from typing import List, Dict, Any
from pathlib import Path
import logging

from infrastructure.plugins.base_plugin import IDataSourcePlugin

logger = logging.getLogger(__name__)


class ImageOCRPlugin(IDataSourcePlugin):
    """OCR parser for image files (PNG, JPG, JPEG, TIFF, BMP)."""
    
    @staticmethod
    def get_name() -> str:
        return "image_ocr_parser"
    
    @staticmethod
    def get_supported_identifiers() -> List[str]:
        return [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"]
    
    async def process(self, source_path: str) -> List[Dict[str, Any]]:
        """Extract text from image using OCR."""
        
        if not Path(source_path).exists():
            raise FileNotFoundError(f"File not found: {source_path}")
        
        chunks = []
        
        try:
            # Open the image
            image = Image.open(source_path)
            
            # Convert to RGB if necessary (for compatibility)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang='eng',
                config='--psm 3'  # Automatic page segmentation
            )
            
            if text.strip():
                chunks.append({
                    "text_content": text,
                    "metadata": {
                        "source_file": Path(source_path).name,
                        "parser": self.get_name(),
                        "image_format": image.format,
                        "image_size": f"{image.width}x{image.height}",
                        "extraction_method": "OCR"
                    }
                })
                logger.info(f"Successfully extracted text from image: {source_path}")
            else:
                logger.warning(f"No text found in image: {source_path}")
                # Still return metadata even if no text found
                chunks.append({
                    "text_content": "[No text detected in image]",
                    "metadata": {
                        "source_file": Path(source_path).name,
                        "parser": self.get_name(),
                        "image_format": image.format,
                        "image_size": f"{image.width}x{image.height}",
                        "extraction_method": "OCR",
                        "note": "No text detected - image may not contain text or OCR failed"
                    }
                })
                
        except Exception as e:
            logger.error(f"Error processing image with OCR: {e}")
            raise
        
        return chunks