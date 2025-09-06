import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, storage_path: str = "./extracted_text"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        Extract text from PDF using OCR when necessary.
        Returns tuple of (extracted_text, metadata)
        """
        text_parts = []
        metadata = {
            "source": pdf_path,
            "type": "pdf",
            "pages": 0,
            "extraction_method": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            pdf_document = fitz.open(pdf_path)
            metadata["pages"] = len(pdf_document)
            
            for page_num, page in enumerate(pdf_document):
                # First try to extract embedded text
                text = page.get_text()
                
                if text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
                    if "text_extraction" not in metadata["extraction_method"]:
                        metadata["extraction_method"].append("text_extraction")
                else:
                    # If no text, use OCR on the page image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    ocr_text = pytesseract.image_to_string(image, lang='eng')
                    text_parts.append(f"--- Page {page_num + 1} (OCR) ---\n{ocr_text}")
                    if "ocr" not in metadata["extraction_method"]:
                        metadata["extraction_method"].append("ocr")
            
            pdf_document.close()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        
        full_text = "\n\n".join(text_parts)
        return full_text, metadata
    
    def extract_text_from_image(self, image_path: str) -> Tuple[str, Dict]:
        """
        Extract text from image using OCR.
        Returns tuple of (extracted_text, metadata)
        """
        metadata = {
            "source": image_path,
            "type": "image",
            "extraction_method": ["ocr"],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            image = Image.open(image_path)
            metadata["dimensions"] = f"{image.width}x{image.height}"
            metadata["format"] = image.format
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            # Also get detailed OCR data for potential future use
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            metadata["word_count"] = len([word for word in ocr_data['text'] if word.strip()])
            metadata["confidence_scores"] = [
                conf for conf, text in zip(ocr_data['conf'], ocr_data['text']) 
                if text.strip() and conf > 0
            ]
            if metadata["confidence_scores"]:
                metadata["avg_confidence"] = sum(metadata["confidence_scores"]) / len(metadata["confidence_scores"])
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
        
        return text, metadata
    
    def save_extracted_text(self, text: str, metadata: Dict, filename_prefix: str) -> str:
        """
        Save extracted text and metadata to files.
        Returns the path to the saved text file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename_prefix}_{timestamp}"
        
        # Save text file
        text_path = self.storage_path / f"{base_filename}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Save metadata
        metadata_path = self.storage_path / f"{base_filename}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved extracted text to {text_path}")
        logger.info(f"Saved metadata to {metadata_path}")
        
        return str(text_path)
    
    def process_document(self, file_path: str) -> Dict:
        """
        Main method to process any document (PDF or image).
        Extracts text, saves it, and returns results.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type and extract text
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            text, metadata = self.extract_text_from_pdf(str(file_path))
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
            text, metadata = self.extract_text_from_image(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Save extracted text
        filename_prefix = file_path.stem
        saved_path = self.save_extracted_text(text, metadata, filename_prefix)
        
        return {
            "success": True,
            "extracted_text": text,
            "text_file_path": saved_path,
            "metadata": metadata,
            "summary": {
                "character_count": len(text),
                "word_count": len(text.split()),
                "line_count": len(text.splitlines())
            }
        }
    
    def batch_process(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple documents in batch.
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.process_document(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results.append({
                    "success": False,
                    "file": file_path,
                    "error": str(e)
                })
        
        return results