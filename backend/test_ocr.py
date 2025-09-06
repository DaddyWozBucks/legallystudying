#!/usr/bin/env python3
"""
Test script for the OCR pipeline.
Demonstrates the complete workflow:
1. Extract text from PDFs/images
2. Save extracted text to files
3. Analyze the extracted text
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ocr_pipeline import OCRPipeline
import json
from pathlib import Path

def test_single_document():
    """Test processing a single document."""
    print("=" * 60)
    print("TESTING SINGLE DOCUMENT PROCESSING")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = OCRPipeline(storage_path="./test_ocr_output")
    
    # Create a test PDF with text (you'll need to provide an actual PDF)
    test_file = "test_document.pdf"  # Replace with actual file path
    
    if not Path(test_file).exists():
        print(f"Please provide a test file at: {test_file}")
        print("You can use any PDF or image file (png, jpg, etc.)")
        return
    
    # Process the document
    result = pipeline.process_single_document(test_file, analyze=True)
    
    # Display results
    if result.get("extraction", {}).get("success"):
        print("\n✓ Text Extraction Successful!")
        print(f"  - Extracted text saved to: {result['extraction']['text_file_path']}")
        print(f"  - Characters extracted: {result['extraction']['summary']['character_count']}")
        print(f"  - Words extracted: {result['extraction']['summary']['word_count']}")
        
        if result.get("analysis"):
            print("\n✓ Text Analysis Complete!")
            analysis = result["analysis"]
            
            print("\n  Key Information Found:")
            print(f"    - Emails: {len(analysis['key_information']['emails'])}")
            if analysis['key_information']['emails']:
                print(f"      Examples: {', '.join(analysis['key_information']['emails'][:3])}")
            
            print(f"    - Phone numbers: {len(analysis['key_information']['phone_numbers'])}")
            print(f"    - Dates: {len(analysis['key_information']['dates'])}")
            if analysis['key_information']['dates']:
                print(f"      Examples: {', '.join(analysis['key_information']['dates'][:3])}")
            
            print(f"    - URLs: {len(analysis['key_information']['urls'])}")
            print(f"    - Monetary amounts: {len(analysis['key_information']['monetary_amounts'])}")
            
            print("\n  Text Characteristics:")
            print(f"    - Readability: {analysis['summary']['readability_score']}")
            print(f"    - Is structured: {analysis['summary']['is_structured']}")
            print(f"    - Sentiment ratio: {analysis['sentiment']['sentiment_ratio']:.2f}")
            
            print("\n  Top Keywords:")
            top_keywords = list(analysis['keyword_analysis']['top_keywords'].items())[:10]
            for word, count in top_keywords:
                print(f"    - {word}: {count} occurrences")
    else:
        print(f"\n✗ Processing failed: {result.get('error')}")

def test_quick_extract():
    """Test quick text extraction without analysis."""
    print("\n" + "=" * 60)
    print("TESTING QUICK TEXT EXTRACTION")
    print("=" * 60)
    
    pipeline = OCRPipeline()
    
    test_file = "test_document.pdf"  # Replace with actual file path
    
    if not Path(test_file).exists():
        print(f"Please provide a test file at: {test_file}")
        return
    
    try:
        # Quick extract - just get the text
        text = pipeline.quick_extract(test_file)
        
        print("\n✓ Quick extraction successful!")
        print(f"  Extracted {len(text)} characters")
        print("\n  First 500 characters of extracted text:")
        print("-" * 40)
        print(text[:500])
        print("-" * 40)
        
    except Exception as e:
        print(f"\n✗ Quick extraction failed: {e}")

def test_batch_processing():
    """Test processing multiple documents."""
    print("\n" + "=" * 60)
    print("TESTING BATCH PROCESSING")
    print("=" * 60)
    
    pipeline = OCRPipeline(storage_path="./test_ocr_output")
    
    # List of test files (replace with actual file paths)
    test_files = [
        "test_document1.pdf",
        "test_image.png",
        "test_document2.pdf"
    ]
    
    # Filter to existing files
    existing_files = [f for f in test_files if Path(f).exists()]
    
    if not existing_files:
        print("No test files found. Please provide test files:")
        for f in test_files:
            print(f"  - {f}")
        return
    
    print(f"\nProcessing {len(existing_files)} documents...")
    results = pipeline.process_batch(existing_files, analyze=True)
    
    # Summary
    successful = sum(1 for r in results if r.get("extraction", {}).get("success", False))
    print(f"\n✓ Batch processing complete!")
    print(f"  - Total processed: {len(results)}")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {len(results) - successful}")

def demonstrate_workflow():
    """Demonstrate the complete OCR workflow."""
    print("\n" + "=" * 60)
    print("OCR PIPELINE DEMONSTRATION")
    print("=" * 60)
    print("\nThis pipeline provides a complete OCR workflow:")
    print("1. Extract text from PDFs and images using OCR")
    print("2. Save extracted text to organized files")
    print("3. Perform comprehensive text analysis")
    print("4. Generate reports with key findings")
    print("\nThe extracted text is saved separately, making it:")
    print("- Easy to read and review")
    print("- Searchable and indexable")
    print("- Ready for further processing")
    print("\nUsage example:")
    print("-" * 40)
    print("""
from services.ocr_pipeline import OCRPipeline

# Initialize pipeline
pipeline = OCRPipeline(storage_path="./ocr_output")

# Process a single document
result = pipeline.process_single_document("document.pdf")

# Access extracted text
text = result['extraction']['extracted_text']
text_file = result['extraction']['text_file_path']

# Access analysis results
analysis = result['analysis']
key_info = analysis['key_information']
keywords = analysis['keyword_analysis']

# Quick extraction (just text, no analysis)
text = pipeline.quick_extract("document.pdf")

# Process multiple documents
results = pipeline.process_batch(["doc1.pdf", "doc2.pdf"])

# Process entire folder
results = pipeline.process_folder("./documents/")
""")
    print("-" * 40)

if __name__ == "__main__":
    # Run demonstration
    demonstrate_workflow()
    
    # Run tests if test files are available
    print("\n" + "=" * 60)
    print("RUNNING TESTS (if test files are available)")
    print("=" * 60)
    
    # Uncomment to run tests with actual files:
    # test_single_document()
    # test_quick_extract()
    # test_batch_processing()
    
    print("\nTo run tests, uncomment the test functions at the bottom of test_ocr.py")
    print("and provide actual PDF or image files to test with.")