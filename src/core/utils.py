#!/usr/bin/env python3
"""
Enhanced utilities for sophisticated document processing
Handles large-scale document operations with metadata extraction
"""

import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

# Multiple PDF extraction methods for robustness
try:
    import fitz  # PyMuPDF - best for complex PDFs
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber  # Good for tables
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

import PyPDF2  # Fallback
import docx
import chardet


class DocumentExtractor:
    """Sophisticated document extraction with metadata"""
    
    @staticmethod
    def extract_from_pdf(filepath: Path) -> Tuple[Optional[str], Dict]:
        """
        Extract text and metadata from PDF using best available method
        
        Returns:
            Tuple of (text, metadata)
        """
        metadata = {
            'extraction_method': None,
            'page_count': 0,
            'extraction_quality': 'unknown',
            'tables_found': False,
            'images_found': False
        }
        
        # Try PyMuPDF first (best quality)
        if PYMUPDF_AVAILABLE:
            try:
                import fitz
                doc = fitz.open(str(filepath))
                text = ""
                
                for page_num, page in enumerate(doc):
                    page_text = page.get_text()
                    text += f"\n[PAGE {page_num + 1}]\n{page_text}"
                    
                    # Check for tables and images
                    if page.get_tables():
                        metadata['tables_found'] = True
                    if page.get_images():
                        metadata['images_found'] = True
                
                metadata['page_count'] = len(doc)
                metadata['extraction_method'] = 'PyMuPDF'
                metadata['extraction_quality'] = 'high'
                doc.close()
                
                if text.strip():
                    return text, metadata
                    
            except Exception as e:
                print(f"PyMuPDF failed: {e}")
        
        # Try pdfplumber (good for tables)
        if PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber
                with pdfplumber.open(filepath) as pdf:
                    text = ""
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        text += f"\n[PAGE {i + 1}]\n{page_text}"
                        
                        # Check for tables
                        if page.extract_tables():
                            metadata['tables_found'] = True
                    
                    metadata['page_count'] = len(pdf.pages)
                    metadata['extraction_method'] = 'pdfplumber'
                    metadata['extraction_quality'] = 'medium'
                    
                    if text.strip():
                        return text, metadata
                        
            except Exception as e:
                print(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += f"\n[PAGE {page_num + 1}]\n{page_text}"
                
                metadata['page_count'] = len(pdf_reader.pages)
                metadata['extraction_method'] = 'PyPDF2'
                metadata['extraction_quality'] = 'basic'
                
                return text, metadata
                
        except Exception as e:
            print(f"All PDF extraction methods failed for {filepath}: {e}")
            return None, metadata


class DocumentChunker:
    """Intelligent document chunking for API limits"""
    
    @staticmethod
    def chunk_by_tokens(text: str, max_tokens: int = 30000) -> List[str]:
        """
        Chunk text by approximate token count
        Maintains sentence boundaries
        """
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def chunk_by_pages(text: str, pages_per_chunk: int = 10) -> List[str]:
        """
        Chunk by page markers
        Useful for maintaining document structure
        """
        # Split by page markers
        pages = re.split(r'\[PAGE \d+\]', text)
        
        chunks = []
        for i in range(0, len(pages), pages_per_chunk):
            chunk_pages = pages[i:i + pages_per_chunk]
            chunk = "\n".join(chunk_pages)
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks


class DocumentMetadataExtractor:
    """Extract rich metadata from documents"""
    
    @staticmethod
    def extract_metadata(filepath: Path, content: str) -> Dict:
        """Extract comprehensive metadata"""
        
        metadata = {
            'filepath': str(filepath),
            'filename': filepath.name,
            'file_size_mb': filepath.stat().st_size / (1024 * 1024),
            'modified_date': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            'doc_id': f"DOC_{hashlib.md5(str(filepath).encode()).hexdigest()[:8].upper()}",
            'extension': filepath.suffix.lower()
        }
        
        # Content analysis
        metadata.update({
            'char_count': len(content),
            'word_count': len(content.split()),
            'line_count': content.count('\n'),
            'has_tables': bool(re.search(r'\t|\|', content)),
            'has_dates': bool(re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content)),
            'has_amounts': bool(re.findall(r'[£$€]\s*[\d,]+\.?\d*', content)),
            'has_emails': bool(re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', content))
        })
        
        # Extract key entities
        metadata['entities'] = DocumentMetadataExtractor._extract_entities(content)
        
        # Document classification
        metadata['classification'] = DocumentMetadataExtractor._classify_document(content, filepath.name)
        
        return metadata
    
    @staticmethod
    def _extract_entities(content: str) -> Dict:
        """Extract named entities from content"""
        entities = {
            'people': [],
            'companies': [],
            'dates': [],
            'amounts': [],
            'emails': []
        }
        
        # Extract people (simple pattern - could enhance with NLP)
        people_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        entities['people'] = list(set(re.findall(people_pattern, content)))[:10]
        
        # Extract company names
        company_patterns = [
            r'\b\w+\s+(?:Ltd|Limited|Inc|LLC|LLP|Plc|Corp|Corporation)\b',
            r'\b\w+\s+(?:Capital|Holdings|Partners|Group)\b'
        ]
        for pattern in company_patterns:
            entities['companies'].extend(re.findall(pattern, content, re.IGNORECASE))
        entities['companies'] = list(set(entities['companies']))[:10]
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities['dates'] = list(set(re.findall(date_pattern, content)))[:10]
        
        # Extract amounts
        amount_pattern = r'[£$€]\s*([\d,]+(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, content)
        entities['amounts'] = [amt.replace(',', '') for amt in amounts][:10]
        
        # Extract emails
        email_pattern = r'\b[\w.-]+@[\w.-]+\.\w+\b'
        entities['emails'] = list(set(re.findall(email_pattern, content)))[:10]
        
        return entities
    
    @staticmethod
    def _classify_document(content: str, filename: str) -> str:
        """Classify document type"""
        
        filename_lower = filename.lower()
        content_lower = content[:5000].lower()  # Check first 5000 chars
        
        # Check filename patterns
        if 'contract' in filename_lower or 'agreement' in filename_lower:
            return 'contract'
        elif 'email' in filename_lower or 'correspondence' in filename_lower:
            return 'correspondence'
        elif 'minutes' in filename_lower or 'meeting' in filename_lower:
            return 'minutes'
        elif 'invoice' in filename_lower or 'receipt' in filename_lower:
            return 'financial'
        elif 'statement' in filename_lower or 'witness' in filename_lower:
            return 'witness_statement'
        
        # Check content patterns
        if 'whereas' in content_lower and 'agreement' in content_lower:
            return 'contract'
        elif 'from:' in content_lower and 'to:' in content_lower and 'subject:' in content_lower:
            return 'email'
        elif 'minutes of' in content_lower or 'meeting held' in content_lower:
            return 'minutes'
        elif 'i state' in content_lower or 'witness statement' in content_lower:
            return 'witness_statement'
        
        return 'general'


def load_documents(path: str, max_docs: Optional[int] = None) -> List[Dict]:
    """
    Enhanced document loader with metadata and chunking
    
    Args:
        path: File or directory path
        max_docs: Maximum number of documents to load
        
    Returns:
        List of document dictionaries with content and metadata
    """
    documents = []
    extractor = DocumentExtractor()
    metadata_extractor = DocumentMetadataExtractor()
    
    path_obj = Path(path)
    
    # Get all files to process
    if path_obj.is_file():
        files = [path_obj]
    elif path_obj.is_dir():
        # Get all supported files
        patterns = ['*.pdf', '*.docx', '*.doc', '*.txt', '*.json', '*.html']
        files = []
        for pattern in patterns:
            files.extend(path_obj.glob(pattern))
            files.extend(path_obj.rglob(pattern))  # Recursive
        
        # Remove duplicates and sort
        files = sorted(set(files))
    else:
        print(f"Path does not exist: {path}")
        return []
    
    # Limit number of files if specified
    if max_docs:
        files = files[:max_docs]
    
    print(f"📂 Loading {len(files)} documents from {path}")
    
    for i, filepath in enumerate(files, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(files)} documents loaded...")
        
        try:
            # Extract content based on file type
            content = None
            pdf_metadata = {}
            
            if filepath.suffix.lower() == '.pdf':
                content, pdf_metadata = extractor.extract_from_pdf(filepath)
            elif filepath.suffix.lower() in ['.docx', '.doc']:
                doc = docx.Document(str(filepath))
                content = "\n".join([p.text for p in doc.paragraphs])
            elif filepath.suffix.lower() == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = json.dumps(data, indent=2)
            else:
                # Try as text file
                with open(filepath, 'rb') as f:
                    raw_data = f.read(10000)
                    result = chardet.detect(raw_data)
                    encoding = result['encoding'] or 'utf-8'
                
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
            
            if content:
                # Extract metadata
                metadata = metadata_extractor.extract_metadata(filepath, content)
                metadata.update(pdf_metadata)  # Add PDF-specific metadata
                
                # Create document entry
                doc_entry = {
                    'content': content,
                    'metadata': metadata,
                    'doc_id': metadata['doc_id'],
                    'filepath': str(filepath),
                    'filename': filepath.name
                }
                
                documents.append(doc_entry)
                
        except Exception as e:
            print(f"⚠️ Failed to load {filepath.name}: {e}")
    
    print(f"✅ Loaded {len(documents)} documents successfully")
    return documents


def validate_documents(documents: List[Dict], min_length: int = 100) -> List[Dict]:
    """
    Enhanced document validation
    
    Args:
        documents: List of document dictionaries
        min_length: Minimum content length required
        
    Returns:
        List of valid documents
    """
    valid_docs = []
    
    for doc in documents:
        # Check content exists and meets minimum length
        content = doc.get('content', '')
        if not content or len(content) < min_length:
            print(f"⚠️ Skipping invalid document: {doc.get('filename', 'unknown')}")
            continue
        
        # Check for corrupted extractions
        if content.count('�') > 10:  # Too many replacement characters
            print(f"⚠️ Skipping corrupted document: {doc.get('filename', 'unknown')}")
            continue
        
        valid_docs.append(doc)
    
    print(f"✅ Validated {len(valid_docs)}/{len(documents)} documents")
    return valid_docs


def batch_documents_for_api(documents: List[Dict], max_tokens: int = 30000) -> List[List[Dict]]:
    """
    Batch documents for API calls respecting token limits
    
    Args:
        documents: List of document dictionaries
        max_tokens: Maximum tokens per batch
        
    Returns:
        List of document batches
    """
    chunker = DocumentChunker()
    batches = []
    current_batch = []
    current_tokens = 0
    
    for doc in documents:
        # Estimate tokens (1 token ≈ 4 characters)
        doc_tokens = len(doc['content']) // 4
        
        if doc_tokens > max_tokens:
            # Document too large - chunk it
            chunks = chunker.chunk_by_tokens(doc['content'], max_tokens)
            for i, chunk in enumerate(chunks):
                chunk_doc = doc.copy()
                chunk_doc['content'] = chunk
                chunk_doc['chunk_index'] = i
                chunk_doc['total_chunks'] = len(chunks)
                batches.append([chunk_doc])
        elif current_tokens + doc_tokens <= max_tokens:
            # Add to current batch
            current_batch.append(doc)
            current_tokens += doc_tokens
        else:
            # Start new batch
            if current_batch:
                batches.append(current_batch)
            current_batch = [doc]
            current_tokens = doc_tokens
    
    if current_batch:
        batches.append(current_batch)
    
    print(f"📦 Created {len(batches)} batches from {len(documents)} documents")
    return batches