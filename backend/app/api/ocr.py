from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
from app.services.ocr_pipeline import OCRPipeline

router = APIRouter()

# Initialize OCR pipeline
ocr_pipeline = OCRPipeline(storage_path="./ocr_output")

@router.post("/api/ocr/process")
async def process_document(
    file: UploadFile = File(...),
    analyze: bool = True
):
    """
    Process a document with OCR to extract text.
    
    Args:
        file: The uploaded file (PDF or image)
        analyze: Whether to perform text analysis (default: True)
    
    Returns:
        JSON response with extracted text and analysis
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Process the document
        result = ocr_pipeline.process_single_document(tmp_file_path, analyze=analyze)
        
        # Format response
        if result.get("extraction", {}).get("success"):
            response = {
                "success": True,
                "extracted_text": result["extraction"]["extracted_text"],
                "text_file_path": result["extraction"]["text_file_path"],
                "metadata": result["extraction"]["metadata"],
                "summary": result["extraction"]["summary"]
            }
            
            # Add analysis if performed
            if result.get("analysis"):
                response["analysis"] = result["analysis"]
            
            return JSONResponse(content=response)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

@router.post("/api/ocr/extract-text")
async def extract_text_only(file: UploadFile = File(...)):
    """
    Quick text extraction without analysis.
    
    Args:
        file: The uploaded file (PDF or image)
    
    Returns:
        JSON response with extracted text only
    """
    return await process_document(file, analyze=False)

@router.get("/api/ocr/status")
async def get_ocr_status():
    """
    Get OCR service status and statistics.
    """
    storage_path = Path(ocr_pipeline.storage_path)
    
    # Count processed files
    text_files = list((storage_path / "extracted_text").glob("*.txt")) if (storage_path / "extracted_text").exists() else []
    analysis_files = list((storage_path / "extracted_text").glob("*_analysis.json")) if (storage_path / "extracted_text").exists() else []
    
    return {
        "status": "operational",
        "storage_path": str(storage_path),
        "total_documents_processed": len(text_files),
        "total_analyses_performed": len(analysis_files),
        "available_storage": True
    }

@router.post("/api/ocr/batch")
async def process_batch(
    files: list[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Process multiple documents in batch.
    
    Args:
        files: List of uploaded files
    
    Returns:
        JSON response with batch processing results
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per batch"
        )
    
    results = []
    temp_files = []
    
    try:
        # Save all files temporarily
        for file in files:
            file_ext = Path(file.filename).suffix.lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)
        
        # Process all documents
        batch_results = ocr_pipeline.process_batch(temp_files, analyze=True)
        
        # Format results
        for i, result in enumerate(batch_results):
            if result.get("extraction", {}).get("success"):
                results.append({
                    "filename": files[i].filename,
                    "success": True,
                    "text_length": result["extraction"]["summary"]["character_count"],
                    "word_count": result["extraction"]["summary"]["word_count"]
                })
            else:
                results.append({
                    "filename": files[i].filename,
                    "success": False,
                    "error": result.get("error", "Processing failed")
                })
        
        return {
            "total_files": len(files),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }
        
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)