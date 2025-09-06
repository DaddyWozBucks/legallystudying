#!/usr/bin/env python3
"""
Test the OCR pipeline with the Clapham.pdf file
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ocr_pipeline import OCRPipeline
import json
from pathlib import Path

def test_clapham_pdf():
    """Test OCR processing on Clapham.pdf"""
    print("=" * 60)
    print("TESTING OCR PIPELINE WITH CLAPHAM.PDF")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = OCRPipeline(storage_path="./ocr_output")
    
    # Use the provided PDF file
    test_file = "/Users/woz/Downloads/Clapham.pdf"
    
    if not Path(test_file).exists():
        print(f"Error: File not found at {test_file}")
        return
    
    print(f"\nProcessing: {test_file}")
    print("-" * 40)
    
    # Process the document
    result = pipeline.process_single_document(test_file, analyze=True)
    
    # Display results
    if result.get("extraction", {}).get("success"):
        print("\n✓ TEXT EXTRACTION SUCCESSFUL!")
        print("=" * 40)
        
        extraction = result["extraction"]
        print(f"\nFile Information:")
        print(f"  - Source: {extraction['metadata']['source']}")
        print(f"  - Type: {extraction['metadata']['type']}")
        print(f"  - Pages: {extraction['metadata'].get('pages', 'N/A')}")
        print(f"  - Extraction Method: {', '.join(extraction['metadata']['extraction_method'])}")
        
        print(f"\nExtracted Text Statistics:")
        print(f"  - Characters: {extraction['summary']['character_count']:,}")
        print(f"  - Words: {extraction['summary']['word_count']:,}")
        print(f"  - Lines: {extraction['summary']['line_count']:,}")
        
        print(f"\nText File Saved To:")
        print(f"  {extraction['text_file_path']}")
        
        # Show first 1000 characters of extracted text
        print("\n" + "=" * 40)
        print("FIRST 1000 CHARACTERS OF EXTRACTED TEXT:")
        print("-" * 40)
        print(extraction['extracted_text'][:1000])
        print("\n... (truncated)")
        
        if result.get("analysis"):
            print("\n" + "=" * 40)
            print("TEXT ANALYSIS RESULTS:")
            print("-" * 40)
            
            analysis = result["analysis"]
            
            # Key Information
            print("\nKey Information Found:")
            key_info = analysis["key_information"]
            
            if key_info["emails"]:
                print(f"  Emails ({len(key_info['emails'])}):")
                for email in key_info["emails"][:5]:
                    print(f"    - {email}")
                if len(key_info["emails"]) > 5:
                    print(f"    ... and {len(key_info['emails']) - 5} more")
            
            if key_info["phone_numbers"]:
                print(f"  Phone Numbers ({len(key_info['phone_numbers'])}):")
                for phone in key_info["phone_numbers"][:5]:
                    print(f"    - {phone}")
            
            if key_info["dates"]:
                print(f"  Dates ({len(key_info['dates'])}):")
                for date in key_info["dates"][:5]:
                    print(f"    - {date}")
                if len(key_info["dates"]) > 5:
                    print(f"    ... and {len(key_info['dates']) - 5} more")
            
            if key_info["monetary_amounts"]:
                print(f"  Monetary Amounts ({len(key_info['monetary_amounts'])}):")
                for amount in key_info["monetary_amounts"][:5]:
                    print(f"    - {amount}")
                if len(key_info["monetary_amounts"]) > 5:
                    print(f"    ... and {len(key_info['monetary_amounts']) - 5} more")
            
            if key_info["document_numbers"]:
                print(f"  Document/Reference Numbers ({len(key_info['document_numbers'])}):")
                for doc_num in key_info["document_numbers"][:5]:
                    print(f"    - {doc_num}")
            
            if key_info["urls"]:
                print(f"  URLs ({len(key_info['urls'])}):")
                for url in key_info["urls"][:3]:
                    print(f"    - {url}")
            
            # Top Keywords
            print("\nTop 15 Keywords:")
            top_keywords = list(analysis["keyword_analysis"]["top_keywords"].items())[:15]
            for i, (word, count) in enumerate(top_keywords, 1):
                print(f"  {i:2}. {word}: {count} occurrences")
            
            # Document Characteristics
            print("\nDocument Characteristics:")
            print(f"  - Readability: {analysis['summary']['readability_score']}")
            print(f"  - Structured: {'Yes' if analysis['summary']['is_structured'] else 'No'}")
            print(f"  - Sentiment Ratio: {analysis['sentiment']['sentiment_ratio']:.2%} positive")
            print(f"  - Positive Indicators: {analysis['sentiment']['positive_indicators']}")
            print(f"  - Negative Indicators: {analysis['sentiment']['negative_indicators']}")
            
            # Sections identified
            if analysis.get("sections"):
                print(f"\nSections/Headers Identified ({len(analysis['sections'])}):")
                for section in analysis["sections"][:10]:
                    print(f"  Line {section['line_number']}: {section['text'][:50]}...")
                if len(analysis["sections"]) > 10:
                    print(f"  ... and {len(analysis['sections']) - 10} more sections")
            
            # Analysis file location
            if analysis.get("analysis_file"):
                print(f"\nAnalysis JSON Saved To:")
                print(f"  {analysis['analysis_file']}")
        
        print("\n" + "=" * 40)
        print("OCR PROCESSING COMPLETE!")
        print("=" * 40)
        
    else:
        print(f"\n✗ Processing failed: {result.get('error', 'Unknown error')}")
        
    return result

if __name__ == "__main__":
    try:
        result = test_clapham_pdf()
        print("\n✓ Test completed successfully!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()