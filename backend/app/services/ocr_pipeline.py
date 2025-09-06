import os
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime

from app.services.ocr_service import OCRService
from app.services.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)

class OCRPipeline:
    """
    Complete OCR pipeline that:
    1. Extracts text from PDFs/images
    2. Saves the extracted text
    3. Performs analysis on the text
    4. Returns both text and analysis results
    """
    
    def __init__(self, storage_path: str = "./ocr_output"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        self.ocr_service = OCRService(str(self.storage_path / "extracted_text"))
        self.text_analyzer = TextAnalyzer()
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for the pipeline."""
        log_path = self.storage_path / "logs"
        log_path.mkdir(exist_ok=True)
        
        log_file = log_path / f"ocr_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    def process_single_document(self, file_path: str, analyze: bool = True) -> Dict:
        """
        Process a single document through the complete pipeline.
        
        Args:
            file_path: Path to the document (PDF or image)
            analyze: Whether to perform text analysis after extraction
            
        Returns:
            Dictionary containing extraction and analysis results
        """
        logger.info(f"Starting OCR pipeline for: {file_path}")
        
        try:
            # Step 1: Extract text from document
            extraction_result = self.ocr_service.process_document(file_path)
            
            if not extraction_result["success"]:
                return extraction_result
            
            result = {
                "file": file_path,
                "extraction": extraction_result,
                "analysis": None
            }
            
            # Step 2: Perform text analysis if requested
            if analyze:
                logger.info("Performing text analysis...")
                text_file_path = extraction_result["text_file_path"]
                analysis_result = self.text_analyzer.analyze_from_file(text_file_path)
                result["analysis"] = analysis_result
                
                # Create summary report
                result["summary"] = self._create_summary_report(
                    extraction_result, 
                    analysis_result
                )
            
            logger.info(f"OCR pipeline completed successfully for: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error in OCR pipeline for {file_path}: {e}")
            return {
                "file": file_path,
                "success": False,
                "error": str(e)
            }
    
    def process_batch(self, file_paths: List[str], analyze: bool = True) -> List[Dict]:
        """
        Process multiple documents through the pipeline.
        
        Args:
            file_paths: List of paths to documents
            analyze: Whether to perform text analysis after extraction
            
        Returns:
            List of results for each document
        """
        results = []
        total = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Processing document {i}/{total}: {file_path}")
            result = self.process_single_document(file_path, analyze)
            results.append(result)
        
        # Generate batch summary
        self._generate_batch_summary(results)
        
        return results
    
    def process_folder(self, folder_path: str, 
                      extensions: List[str] = None,
                      analyze: bool = True) -> List[Dict]:
        """
        Process all supported documents in a folder.
        
        Args:
            folder_path: Path to the folder containing documents
            extensions: List of file extensions to process (default: PDF and images)
            analyze: Whether to perform text analysis
            
        Returns:
            List of results for each document
        """
        if extensions is None:
            extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        # Find all matching files
        file_paths = []
        for ext in extensions:
            file_paths.extend(folder.glob(f"*{ext}"))
            file_paths.extend(folder.glob(f"*{ext.upper()}"))
        
        # Remove duplicates and convert to strings
        file_paths = list(set(str(f) for f in file_paths))
        file_paths.sort()
        
        logger.info(f"Found {len(file_paths)} documents to process")
        
        return self.process_batch(file_paths, analyze)
    
    def _create_summary_report(self, extraction: Dict, analysis: Dict) -> Dict:
        """
        Create a summary report combining extraction and analysis results.
        """
        summary = {
            "extraction_method": extraction["metadata"]["extraction_method"],
            "text_length": len(extraction["extracted_text"]),
            "pages": extraction["metadata"].get("pages", 1),
            "key_findings": {
                "emails_found": len(analysis["key_information"]["emails"]),
                "phone_numbers_found": len(analysis["key_information"]["phone_numbers"]),
                "dates_found": len(analysis["key_information"]["dates"]),
                "monetary_amounts_found": len(analysis["key_information"]["monetary_amounts"]),
                "urls_found": len(analysis["key_information"]["urls"])
            },
            "text_characteristics": {
                "readability": analysis["summary"]["readability_score"],
                "is_structured": analysis["summary"]["is_structured"],
                "sentiment_ratio": analysis["sentiment"]["sentiment_ratio"]
            },
            "top_keywords": list(analysis["keyword_analysis"]["top_keywords"].keys())[:10]
        }
        
        return summary
    
    def _generate_batch_summary(self, results: List[Dict]) -> str:
        """
        Generate and save a summary report for batch processing.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = self.storage_path / f"batch_summary_{timestamp}.txt"
        
        successful = sum(1 for r in results if r.get("extraction", {}).get("success", False))
        failed = len(results) - successful
        
        with open(summary_path, 'w') as f:
            f.write("OCR BATCH PROCESSING SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total documents processed: {len(results)}\n")
            f.write(f"Successful: {successful}\n")
            f.write(f"Failed: {failed}\n\n")
            
            f.write("DOCUMENT DETAILS:\n")
            f.write("-" * 50 + "\n\n")
            
            for result in results:
                f.write(f"File: {result['file']}\n")
                
                if result.get("extraction", {}).get("success"):
                    extraction = result["extraction"]
                    f.write(f"  Status: SUCCESS\n")
                    f.write(f"  Text extracted: {extraction['summary']['character_count']} characters\n")
                    f.write(f"  Words: {extraction['summary']['word_count']}\n")
                    
                    if result.get("analysis"):
                        analysis = result["analysis"]
                        f.write(f"  Key information found:\n")
                        f.write(f"    - Emails: {len(analysis['key_information']['emails'])}\n")
                        f.write(f"    - Phone numbers: {len(analysis['key_information']['phone_numbers'])}\n")
                        f.write(f"    - Dates: {len(analysis['key_information']['dates'])}\n")
                        f.write(f"    - Monetary amounts: {len(analysis['key_information']['monetary_amounts'])}\n")
                else:
                    f.write(f"  Status: FAILED\n")
                    f.write(f"  Error: {result.get('error', 'Unknown error')}\n")
                
                f.write("\n")
        
        logger.info(f"Batch summary saved to: {summary_path}")
        return str(summary_path)
    
    def quick_extract(self, file_path: str) -> str:
        """
        Quick extraction method that just returns the extracted text.
        Useful when you just need the text without analysis.
        """
        result = self.ocr_service.process_document(file_path)
        if result["success"]:
            return result["extracted_text"]
        else:
            raise Exception(f"Failed to extract text: {result.get('error')}")
    
    def analyze_existing_text(self, text_file_path: str) -> Dict:
        """
        Analyze a previously extracted text file.
        """
        return self.text_analyzer.analyze_from_file(text_file_path)