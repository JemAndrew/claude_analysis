#!/usr/bin/env python3
"""
Enhanced Document Loader with Metadata Extraction
Handles all document types for litigation intelligence
COMPLETE VERSION - Memory tiers integrated
British English throughout
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib
import json
import re

# PDF libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

import PyPDF2
import docx
import chardet


class DocumentLoader:
    """Advanced document loading with metadata extraction and memory tier integration"""
    
    def __init__(self, config):
        self.config = config
        self.load_stats = {
            'total_loaded': 0,
            'failed_loads': 0,
            'by_type': {}
        }
        
        # NEW: Memory tier integration
        self.vector_store = None
        self.cold_storage = None
        
        # Initialise Tier 2: Vector Store (if enabled)
        if hasattr(config, 'enable_vector_store') and config.enable_vector_store:
            try:
                from memory.tier2_vector import VectorStoreManager
                vector_path = config.root / "data" / "memory_tiers" / "tier2_vector_store"
                self.vector_store = VectorStoreManager(vector_path, config)
                print("✅ Tier 2 Vector Store ACTIVE (semantic search enabled)")
            except ImportError as e:
                print(f"⚠️  Tier 2 Vector Store unavailable: {e}")
                print("    Install: pip install chromadb sentence-transformers")
            except Exception as e:
                print(f"⚠️  Tier 2 Vector Store error: {e}")
        
        # Initialise Tier 4: Cold Storage (if enabled)
        if hasattr(config, 'enable_cold_storage') and config.enable_cold_storage:
            try:
                from memory.tier4_cold_storage import ColdStorageManager
                vault_path = config.root / "data" / "memory_tiers" / "tier4_cold_storage"
                self.cold_storage = ColdStorageManager(vault_path, config)
                print("✅ Tier 4 Cold Storage ACTIVE (document encryption enabled)")
            except ImportError as e:
                print(f"⚠️  Tier 4 Cold Storage unavailable: {e}")
                print("    Install: pip install cryptography")
            except Exception as e:
                print(f"⚠️  Tier 4 Cold Storage error: {e}")
    
    def load_directory(self, 
                      directory: Path,
                      max_docs: Optional[int] = None,
                      doc_types: List[str] = None) -> List[Dict]:
        """
        Load all documents from directory
        
        Args:
            directory: Path to document directory
            max_docs: Maximum documents to load
            doc_types: List of extensions to load
        
        Returns:
            List of document dictionaries with content and metadata
        """
        
        if not directory.exists():
            print(f"Warning: Directory {directory} does not exist")
            return []
        
        # Default document types
        if doc_types is None:
            doc_types = ['.pdf', '.docx', '.doc', '.txt', '.json', '.html', '.md']
        
        documents = []
        files_processed = 0
        
        # Get all matching files
        all_files = []
        for doc_type in doc_types:
            all_files.extend(directory.glob(f"**/*{doc_type}"))
        
        # Sort for consistent ordering
        all_files.sort()
        
        # Limit if specified
        if max_docs:
            all_files = all_files[:max_docs]
        
        print(f"Loading {len(all_files)} documents from {directory}")
        
        for file_path in all_files:
            files_processed += 1
            
            if files_processed % 10 == 0:
                print(f"  Progress: {files_processed}/{len(all_files)}")
            
            try:
                document = self.load_document(file_path)
                if document:
                    documents.append(document)
                    self.load_stats['total_loaded'] += 1
            except Exception as e:
                print(f"  Failed to load {file_path.name}: {e}")
                self.load_stats['failed_loads'] += 1
        
        print(f"✅ Loaded {len(documents)} documents successfully")
        
        # Report memory tier statistics
        if self.vector_store:
            stats = self.vector_store.get_collection_stats()
            print(f"   Tier 2: {stats.get('total_documents', 0)} docs indexed")
        
        return documents
    
    def load_document(self, file_path: Path) -> Optional[Dict]:
        """
        Load single document with metadata extraction
        
        Returns:
            Document dictionary with content and metadata
        """
        
        if not file_path.exists():
            return None
        
        # Generate document ID
        doc_id = self._generate_doc_id(file_path)
        
        # Load based on file type
        extension = file_path.suffix.lower()
        
        content = None
        extraction_metadata = {}
        
        if extension == '.pdf':
            content, extraction_metadata = self._load_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            content = self._load_docx(file_path)
        elif extension == '.json':
            content = self._load_json(file_path)
        elif extension in ['.txt', '.md', '.html']:
            content = self._load_text(file_path)
        else:
            content = self._load_text(file_path)  # Try as text
        
        if not content:
            return None
        
        # Extract comprehensive metadata
        metadata = self._extract_metadata(file_path, content, extraction_metadata)
        
        # Update stats
        ext = extension
        self.load_stats['by_type'][ext] = self.load_stats['by_type'].get(ext, 0) + 1
        
        # Build document object
        document = {
            'id': doc_id,
            'filename': file_path.name,
            'filepath': str(file_path),
            'content': content,
            'metadata': metadata
        }
        
        # NEW: Add to memory tiers if enabled
        self._add_to_memory_tiers(file_path, document, extension)
        
        return document
    
    def _add_to_memory_tiers(self, file_path: Path, document: Dict, extension: str):
        """Add document to memory tiers (Tier 2 & 4)"""
        
        doc_id = document['id']
        content = document['content']
        metadata = document['metadata']
        
        # TIER 2: Add to vector store (for semantic search)
        if self.vector_store and content:
            try:
                self.vector_store.add_document(
                    doc_path=file_path,
                    doc_metadata={
                        'doc_id': doc_id,
                        'content': content,
                        'filename': file_path.name,
                        'folder': str(file_path.parent.name),
                        'classification': metadata.get('classification', 'general'),
                        'has_dates': metadata.get('has_dates', False),
                        'has_amounts': metadata.get('has_amounts', False),
                        'word_count': metadata.get('word_count', 0),
                        **metadata
                    }
                )
            except Exception as e:
                # Don't fail entire load if vector indexing fails
                print(f"    ⚠️  Vector indexing failed for {file_path.name}: {e}")
        
        # TIER 4: Encrypt to cold storage (PDFs only for security)
        if self.cold_storage and extension == '.pdf':
            try:
                # Determine importance for prioritisation
                importance = 5  # Default
                classification = metadata.get('classification', 'general')
                
                if classification in ['witness_statement', 'contract']:
                    importance = 10  # High importance
                elif classification in ['correspondence', 'minutes']:
                    importance = 7
                
                self.cold_storage.encrypt_and_store(
                    file_path=file_path,
                    doc_metadata={
                        'doc_id': doc_id,
                        'filename': file_path.name,
                        'classification': classification,
                        'importance': importance,
                        'file_size': metadata.get('file_size_mb', 0),
                        **metadata
                    }
                )
            except Exception as e:
                print(f"    ⚠️  Cold storage encryption failed for {file_path.name}: {e}")
    
    def _load_pdf(self, file_path: Path) -> Tuple[Optional[str], Dict]:
        """Load PDF file with metadata"""
        
        extraction_metadata = {}
        content = None
        
        # Try PyMuPDF first (best quality)
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(file_path)
                text_parts = []
                
                for page_num, page in enumerate(doc):
                    text_parts.append(page.get_text())
                
                content = '\n\n'.join(text_parts)
                extraction_metadata['page_count'] = len(doc)
                extraction_metadata['method'] = 'pymupdf'
                doc.close()
                
                if content and len(content.strip()) > 50:
                    return content, extraction_metadata
            except Exception as e:
                pass  # Try next method
        
        # Try pdfplumber
        if PDFPLUMBER_AVAILABLE and not content:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    
                    content = '\n\n'.join(text_parts)
                    extraction_metadata['page_count'] = len(pdf.pages)
                    extraction_metadata['method'] = 'pdfplumber'
                
                if content and len(content.strip()) > 50:
                    return content, extraction_metadata
            except Exception as e:
                pass  # Try next method
        
        # Fallback to PyPDF2
        if not content:
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text_parts = []
                    
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    
                    content = '\n\n'.join(text_parts)
                    extraction_metadata['page_count'] = len(reader.pages)
                    extraction_metadata['method'] = 'pypdf2'
            except Exception as e:
                return None, {}
        
        return content, extraction_metadata
    
    def _load_docx(self, file_path: Path) -> Optional[str]:
        """Load DOCX file"""
        
        try:
            doc = docx.Document(file_path)
            
            # Extract paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = '\t'.join(cell.text for cell in row.cells)
                    if row_text.strip():
                        paragraphs.append(row_text)
            
            return '\n'.join(paragraphs)
            
        except Exception as e:
            return None
    
    def _load_json(self, file_path: Path) -> Optional[str]:
        """Load JSON file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            return None
    
    def _load_text(self, file_path: Path) -> Optional[str]:
        """Load text file with encoding detection"""
        
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            # Load with detected encoding
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
                
        except Exception as e:
            return None
    
    def _generate_doc_id(self, file_path: Path) -> str:
        """Generate unique document ID"""
        
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8].upper()
        
        # Prefix based on location
        if 'legal' in str(file_path).lower():
            prefix = 'LEGAL'
        elif 'case' in str(file_path).lower():
            prefix = 'CASE'
        elif 'disclosure' in str(file_path).lower():
            prefix = 'DISC'
        else:
            prefix = 'DOC'
        
        return f"{prefix}_{path_hash}"
    
    def _extract_metadata(self, 
                         file_path: Path,
                         content: str,
                         extraction_metadata: Dict) -> Dict:
        """Extract comprehensive metadata from document"""
        
        metadata = {
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'extension': file_path.suffix.lower(),
            'source_folder': file_path.parent.name,
            'char_count': len(content),
            'word_count': len(content.split()),
            'line_count': content.count('\n')
        }
        
        # Add extraction metadata
        metadata.update(extraction_metadata)
        
        # Extract dates
        dates = self._extract_dates(content)
        metadata['dates_found'] = dates[:10]
        metadata['has_dates'] = len(dates) > 0
        
        # Extract amounts
        amounts = self._extract_amounts(content)
        metadata['amounts_found'] = amounts[:10]
        metadata['has_amounts'] = len(amounts) > 0
        
        # Extract entities
        entities = self._extract_entities(content)
        metadata['entities'] = entities
        metadata['has_entities'] = bool(entities['people'] or entities['companies'])
        
        # Document classification
        metadata['classification'] = self._classify_document(file_path.name, content)
        
        # Content flags
        metadata['has_tables'] = bool(re.search(r'\t|\|', content))
        metadata['has_emails'] = bool(re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', content))
        
        return metadata
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        
        dates = []
        
        # Multiple date patterns
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_dates = []
        for date in dates:
            if date not in seen:
                seen.add(date)
                unique_dates.append(date)
        
        return unique_dates
    
    def _extract_amounts(self, content: str) -> List[str]:
        """Extract monetary amounts from content"""
        
        amounts = []
        
        # Amount patterns - British English focused
        patterns = [
            r'£\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|k|m|bn))?',
            r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|k|m|bn))?',
            r'€\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|k|m|bn))?',
            r'[\d,]+(?:\.\d{2})?\s*(?:GBP|USD|EUR|pounds?|dollars?)',
            r'\b\d{1,3}(?:,\d{3})+(?:\.\d{2})?\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            amounts.extend(matches)
        
        # Remove duplicates
        seen = set()
        unique_amounts = []
        for amount in amounts:
            clean_amount = amount.strip()
            if clean_amount not in seen:
                seen.add(clean_amount)
                unique_amounts.append(clean_amount)
        
        return unique_amounts
    
    def _extract_entities(self, content: str) -> Dict:
        """Extract entities from content"""
        
        entities = {
            'people': [],
            'companies': [],
            'emails': []
        }
        
        # Extract people (capitalised names)
        people_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        people = re.findall(people_pattern, content)
        entities['people'] = list(set(people))[:20]
        
        # Extract companies
        company_patterns = [
            r'\b\w+\s+(?:Ltd|Limited|Inc|LLC|LLP|Plc|Corp|Corporation)\b',
            r'\b\w+\s+(?:Capital|Holdings|Partners|Group|Ventures)\b'
        ]
        
        companies = []
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            companies.extend(matches)
        entities['companies'] = list(set(companies))[:20]
        
        # Extract emails
        email_pattern = r'\b[\w.-]+@[\w.-]+\.\w+\b'
        emails = re.findall(email_pattern, content)
        entities['emails'] = list(set(emails))[:10]
        
        return entities
    
    def _classify_document(self, filename: str, content: str) -> str:
        """Classify document type based on content and filename"""
        
        filename_lower = filename.lower()
        content_lower = content[:5000].lower()
        
        # Check filename patterns
        if 'contract' in filename_lower or 'agreement' in filename_lower:
            return 'contract'
        elif 'email' in filename_lower or 'correspondence' in filename_lower:
            return 'correspondence'
        elif 'invoice' in filename_lower or 'receipt' in filename_lower:
            return 'financial'
        elif 'statement' in filename_lower or 'witness' in filename_lower:
            return 'witness_statement'
        elif 'minutes' in filename_lower or 'meeting' in filename_lower:
            return 'minutes'
        
        # Check content patterns
        if 'whereas' in content_lower and 'agreement' in content_lower:
            return 'contract'
        elif 'from:' in content_lower and 'to:' in content_lower:
            return 'email'
        elif 'invoice' in content_lower or 'payment' in content_lower:
            return 'financial'
        elif 'i state' in content_lower or 'witness statement' in content_lower:
            return 'witness_statement'
        elif 'minutes of' in content_lower:
            return 'minutes'
        
        return 'general'
    
    def get_statistics(self) -> Dict:
        """Get loading statistics"""
        
        stats = {
            'total_loaded': self.load_stats['total_loaded'],
            'failed_loads': self.load_stats['failed_loads'],
            'by_type': self.load_stats['by_type'],
            'success_rate': (
                self.load_stats['total_loaded'] / 
                max(1, self.load_stats['total_loaded'] + self.load_stats['failed_loads'])
            )
        }
        
        # Add memory tier stats if available
        if self.vector_store:
            vector_stats = self.vector_store.get_collection_stats()
            stats['vector_store'] = {
                'documents': vector_stats.get('total_documents', 0),
                'tokens': vector_stats.get('estimated_total_tokens', 0)
            }
        
        if self.cold_storage:
            storage_stats = self.cold_storage.get_vault_statistics()
            stats['cold_storage'] = {
                'documents': storage_stats.get('total_documents', 0),
                'encrypted_size_mb': storage_stats.get('total_size_mb', 0)
            }
        
        return stats