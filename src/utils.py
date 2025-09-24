# utils.py (COMPLETE FILE)
"""
Utility functions for document processing, file handling, and analysis support.
"""

import os
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import PyPDF2
import docx
import chardet

class DocumentUtils:
    """Utilities for document handling and processing"""
    
    @staticmethod
    def extract_text_from_file(filepath: str) -> Dict[str, Any]:
        """
        Extract text from various file formats
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with content and metadata
        """
        file_ext = os.path.splitext(filepath)[1].lower()
        filename = os.path.basename(filepath)
        
        try:
            if file_ext == '.pdf':
                content = DocumentUtils._extract_pdf_text(filepath)
            elif file_ext in ['.doc', '.docx']:
                content = DocumentUtils._extract_word_text(filepath)
            elif file_ext == '.txt':
                content = DocumentUtils._extract_txt_text(filepath)
            elif file_ext in ['.eml', '.msg']:
                content = DocumentUtils._extract_email_text(filepath)
            else:
                # Try as text file
                content = DocumentUtils._extract_txt_text(filepath)
            
            return {
                'filename': filename,
                'path': filepath,
                'content': content,
                'extension': file_ext,
                'size': os.path.getsize(filepath),
                'hash': DocumentUtils._generate_file_hash(filepath),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            return {
                'filename': filename,
                'path': filepath,
                'content': '',
                'error': str(e),
                'extension': file_ext
            }
    
    @staticmethod
    def _extract_pdf_text(filepath: str) -> str:
        """Extract text from PDF file"""
        text = []
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(f"[Page {page_num + 1}]\n{page.extract_text()}")
            return '\n'.join(text)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    @staticmethod
    def _extract_word_text(filepath: str) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(filepath)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            print(f"Word extraction error: {e}")
            return ""
    
    @staticmethod
    def _extract_txt_text(filepath: str) -> str:
        """Extract text from text file with encoding detection"""
        try:
            # Detect encoding
            with open(filepath, 'rb') as file:
                raw = file.read()
                result = chardet.detect(raw)
                encoding = result['encoding'] or 'utf-8'
            
            # Read with detected encoding
            with open(filepath, 'r', encoding=encoding, errors='ignore') as file:
                return file.read()
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
    
    @staticmethod
    def _extract_email_text(filepath: str) -> str:
        """Extract text from email file (basic implementation)"""
        # This would need proper email parsing library for production
        return DocumentUtils._extract_txt_text(filepath)
    
    @staticmethod
    def _generate_file_hash(filepath: str) -> str:
        """Generate SHA256 hash of file for integrity checking"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

class AnalysisUtils:
    """Utilities for analysis and data processing"""
    
    @staticmethod
    def extract_dates(text: str) -> List[Dict[str, Any]]:
        """
        Extract dates from text
        
        Args:
            text: Text to analyse
            
        Returns:
            List of date occurrences with context
        """
        dates = []
        
        # Common date patterns
        patterns = [
            (r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', 'DD/MM/YYYY or MM/DD/YYYY'),
            (r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}', 'DD Month YYYY'),
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}', 'Month DD, YYYY'),
            (r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', 'YYYY-MM-DD'),
        ]
        
        for pattern, format_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                dates.append({
                    'date_string': match.group(),
                    'format': format_type,
                    'position': match.start(),
                    'context': context
                })
        
        return dates
    
    @staticmethod
    def extract_money_references(text: str) -> List[Dict[str, Any]]:
        """
        Extract monetary references from text
        
        Args:
            text: Text to analyse
            
        Returns:
            List of money references with context
        """
        money_refs = []
        
        # Money patterns (GBP focused but includes others)
        patterns = [
            (r'£[\d,]+\.?\d*', 'GBP'),
            (r'GBP\s*[\d,]+\.?\d*', 'GBP'),
            (r'\$[\d,]+\.?\d*', 'USD'),
            (r'€[\d,]+\.?\d*', 'EUR'),
            (r'[\d,]+\.?\d*\s*(?:pounds?|sterling)', 'GBP'),
        ]
        
        for pattern, currency in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                money_refs.append({
                    'amount_string': match.group(),
                    'currency': currency,
                    'position': match.start(),
                    'context': context
                })
        
        return money_refs
    
    @staticmethod
    def extract_email_addresses(text: str) -> List[str]:
        """Extract email addresses from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(pattern, text)))
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract UK phone numbers from text"""
        patterns = [
            r'\+44\s?\d{2,4}\s?\d{3,4}\s?\d{3,4}',
            r'0\d{2,4}\s?\d{3,4}\s?\d{3,4}',
            r'\(\d{2,4}\)\s?\d{3,4}\s?\d{3,4}'
        ]
        
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        
        return list(set(numbers))
    
    @staticmethod
    def calculate_document_similarity(doc1: str, doc2: str) -> float:
        """
        Calculate similarity between two documents (simple implementation)
        
        Args:
            doc1: First document text
            doc2: Second document text
            
        Returns:
            Similarity score (0-1)
        """
        # Simple word-based similarity (could use more sophisticated methods)
        words1 = set(doc1.lower().split())
        words2 = set(doc2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

class ReportUtils:
    """Utilities for report formatting and generation"""
    
    @staticmethod
    def format_header(title: str, width: int = 80) -> str:
        """Format a report header"""
        return f"\n{'='*width}\n{title.center(width)}\n{'='*width}\n"
    
    @staticmethod
    def format_section(title: str, width: int = 80) -> str:
        """Format a section header"""
        return f"\n{title}\n{'-'*min(len(title), width)}\n"
    
    @staticmethod
    def format_evidence_list(evidence_items: List[Tuple[str, str]]) -> str:
        """
        Format a list of evidence items
        
        Args:
            evidence_items: List of (description, reference) tuples
            
        Returns:
            Formatted string
        """
        formatted = []
        for idx, (description, reference) in enumerate(evidence_items, 1):
            formatted.append(f"{idx}. {description}")
            formatted.append(f"   Evidence: {reference}")
        return '\n'.join(formatted)
    
    @staticmethod
    def format_timeline(events: List[Tuple[str, str, str]]) -> str:
        """
        Format timeline events
        
        Args:
            events: List of (date, event, reference) tuples
            
        Returns:
            Formatted timeline
        """
        formatted = []
        for date, event, reference in sorted(events):
            formatted.append(f"{date}: {event}")
            if reference:
                formatted.append(f"         Ref: {reference}")
        return '\n'.join(formatted)
    
    @staticmethod
    def generate_table_of_contents(reports: Dict[str, str]) -> str:
        """Generate table of contents for reports"""
        toc = ["TABLE OF CONTENTS", "="*40]
        
        for phase, phase_reports in reports.items():
            toc.append(f"\nPhase {phase}:")
            for report_name, filepath in phase_reports.items():
                filename = os.path.basename(filepath)
                toc.append(f"  - {report_name}: {filename}")
        
        return '\n'.join(toc)

class ValidationUtils:
    """Utilities for validation and error checking"""
    
    @staticmethod
    def validate_document_structure(doc: Dict) -> Tuple[bool, List[str]]:
        """
        Validate document structure
        
        Args:
            doc: Document dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ['content', 'filename']
        
        for field in required_fields:
            if field not in doc or not doc[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'content' in doc and len(doc['content']) < 10:
            errors.append("Content too short (< 10 characters)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_phase_sequence(completed_phases: List[str], 
                               target_phase: str) -> Tuple[bool, str]:
        """
        Validate if target phase can be run
        
        Args:
            completed_phases: List of completed phase IDs
            target_phase: Phase to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        phase_dependencies = {
            '0A': [],
            '0B': ['0A'],
            '1': ['0A', '0B'],
            '2': ['0A', '0B', '1'],
            '3': ['0A', '0B', '1', '2'],
            '4': ['0A', '0B', '1', '2', '3'],
            '5': ['0A', '0B', '1', '2', '3', '4'],
            '6': ['0A', '0B', '1', '2', '3', '4', '5'],
            '7': ['0A', '0B', '1', '2', '3', '4', '5', '6']
        }
        
        if target_phase not in phase_dependencies:
            return False, f"Unknown phase: {target_phase}"
        
        required = phase_dependencies[target_phase]
        missing = [p for p in required if p not in completed_phases]
        
        if missing:
            return False, f"Missing prerequisite phases: {', '.join(missing)}"
        
        return True, ""

class ConfigUtils:
    """Configuration and environment utilities"""
    
    @staticmethod
    def load_config(config_path: str = "./config.json") -> Dict:
        """Load configuration from file"""
        default_config = {
            'output_dir': './outputs',
            'knowledge_dir': './knowledge_store',
            'max_documents': 1000,
            'max_tokens': 4096,
            'temperature': 0.3,
            'model': 'claude-3-opus-20240229'
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    @staticmethod
    def check_environment() -> Dict[str, bool]:
        """Check environment setup"""
        checks = {
            'api_key': bool(os.getenv('ANTHROPIC_API_KEY')),
            'output_dir': os.path.exists('./outputs'),
            'knowledge_dir': os.path.exists('./knowledge_store')
        }
        
        # Create directories if missing
        os.makedirs('./outputs', exist_ok=True)
        os.makedirs('./knowledge_store', exist_ok=True)
        
        return checks