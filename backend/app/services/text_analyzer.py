import re
import json
from typing import Dict, List, Optional, Any
from collections import Counter
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self):
        self.analysis_results = []
        
    def load_text_from_file(self, text_file_path: str) -> str:
        """
        Load previously extracted text from file.
        """
        with open(text_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def analyze_text_structure(self, text: str) -> Dict:
        """
        Analyze the structure of the text.
        """
        lines = text.splitlines()
        paragraphs = text.split('\n\n')
        
        return {
            "total_characters": len(text),
            "total_words": len(text.split()),
            "total_lines": len(lines),
            "total_paragraphs": len(paragraphs),
            "avg_words_per_line": len(text.split()) / len(lines) if lines else 0,
            "avg_words_per_paragraph": len(text.split()) / len(paragraphs) if paragraphs else 0,
            "empty_lines": sum(1 for line in lines if not line.strip())
        }
    
    def extract_key_information(self, text: str) -> Dict:
        """
        Extract common key information from text.
        """
        info = {}
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        info['emails'] = list(set(re.findall(email_pattern, text)))
        
        # Extract phone numbers (US format)
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, text)
        info['phone_numbers'] = ['-'.join(phone) for phone in phones]
        
        # Extract dates (various formats)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
        ]
        info['dates'] = []
        for pattern in date_patterns:
            info['dates'].extend(re.findall(pattern, text, re.IGNORECASE))
        info['dates'] = list(set(info['dates']))
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        info['urls'] = list(set(re.findall(url_pattern, text)))
        
        # Extract potential document/case numbers
        doc_pattern = r'\b(?:Case|Document|File|Ref|No\.?|#)\s*:?\s*([A-Z0-9]+-?[A-Z0-9]+(?:-[A-Z0-9]+)*)\b'
        info['document_numbers'] = list(set(re.findall(doc_pattern, text, re.IGNORECASE)))
        
        # Extract money amounts
        money_pattern = r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?'
        info['monetary_amounts'] = list(set(re.findall(money_pattern, text)))
        
        return info
    
    def keyword_frequency_analysis(self, text: str, min_word_length: int = 3, top_n: int = 20) -> Dict:
        """
        Analyze keyword frequency in the text.
        """
        # Common stop words to exclude
        stop_words = set(['the', 'and', 'for', 'are', 'was', 'were', 'been', 'have', 'has', 
                         'had', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                         'can', 'this', 'that', 'these', 'those', 'with', 'from', 'into',
                         'through', 'during', 'before', 'after', 'above', 'below', 'between'])
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Filter words
        filtered_words = [word for word in words 
                         if len(word) >= min_word_length and word not in stop_words]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        return {
            "total_unique_words": len(set(filtered_words)),
            "top_keywords": dict(word_freq.most_common(top_n)),
            "word_frequency_distribution": {
                "1-5_occurrences": sum(1 for count in word_freq.values() if 1 <= count <= 5),
                "6-10_occurrences": sum(1 for count in word_freq.values() if 6 <= count <= 10),
                "11-20_occurrences": sum(1 for count in word_freq.values() if 11 <= count <= 20),
                "20+_occurrences": sum(1 for count in word_freq.values() if count > 20)
            }
        }
    
    def identify_sections(self, text: str) -> List[Dict]:
        """
        Identify potential sections or headers in the text.
        """
        sections = []
        lines = text.splitlines()
        
        # Patterns that might indicate section headers
        header_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^\d+\.?\s+[A-Z]',  # Numbered sections
            r'^[IVX]+\.?\s+',     # Roman numerals
            r'^(?:Section|Chapter|Part|Article)\s+\d+',  # Explicit section markers
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            for pattern in header_patterns:
                if re.match(pattern, line):
                    sections.append({
                        "line_number": i + 1,
                        "text": line,
                        "type": "potential_header"
                    })
                    break
        
        return sections
    
    def sentiment_indicators(self, text: str) -> Dict:
        """
        Simple sentiment indicators based on keyword presence.
        """
        positive_words = ['agree', 'approve', 'benefit', 'comply', 'confirm', 'grant', 
                         'success', 'valid', 'accept', 'allow', 'permit']
        negative_words = ['deny', 'reject', 'refuse', 'violate', 'breach', 'fail', 
                         'invalid', 'prohibit', 'dispute', 'object', 'oppose']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        return {
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "sentiment_ratio": positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
        }
    
    def comprehensive_analysis(self, text: str, source_info: Optional[Dict] = None) -> Dict:
        """
        Perform comprehensive text analysis.
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "source": source_info if source_info else {},
            "structure": self.analyze_text_structure(text),
            "key_information": self.extract_key_information(text),
            "keyword_analysis": self.keyword_frequency_analysis(text),
            "sections": self.identify_sections(text),
            "sentiment": self.sentiment_indicators(text)
        }
        
        # Add summary
        analysis["summary"] = {
            "is_structured": len(analysis["sections"]) > 3,
            "contains_personal_info": bool(analysis["key_information"]["emails"] or 
                                          analysis["key_information"]["phone_numbers"]),
            "contains_dates": bool(analysis["key_information"]["dates"]),
            "contains_financial_info": bool(analysis["key_information"]["monetary_amounts"]),
            "primary_language": "english",  # Could be enhanced with language detection
            "readability_score": self._calculate_readability(text)
        }
        
        return analysis
    
    def _calculate_readability(self, text: str) -> str:
        """
        Simple readability assessment based on average word and sentence length.
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        if not words or not sentences:
            return "unknown"
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        if avg_word_length < 4 and avg_sentence_length < 15:
            return "easy"
        elif avg_word_length < 5 and avg_sentence_length < 20:
            return "moderate"
        else:
            return "complex"
    
    def save_analysis(self, analysis: Dict, output_path: str) -> str:
        """
        Save analysis results to JSON file.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        logger.info(f"Analysis saved to {output_file}")
        return str(output_file)
    
    def analyze_from_file(self, text_file_path: str, save_results: bool = True) -> Dict:
        """
        Load text from file and perform analysis.
        """
        text = self.load_text_from_file(text_file_path)
        
        source_info = {
            "text_file": text_file_path,
            "file_size": Path(text_file_path).stat().st_size
        }
        
        analysis = self.comprehensive_analysis(text, source_info)
        
        if save_results:
            # Save analysis next to the text file
            text_path = Path(text_file_path)
            analysis_path = text_path.parent / f"{text_path.stem}_analysis.json"
            self.save_analysis(analysis, str(analysis_path))
            analysis["analysis_file"] = str(analysis_path)
        
        return analysis