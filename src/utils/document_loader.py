#!/usr/bin/env python3
"""
Document Loader for Lismore Litigation Intelligence System
Loads documents directly from source folders (no copying needed)
Extracts folder metadata from FolderMapping
British English throughout
"""

import PyPDF2
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import hashlib


class DocumentLoader:
    """Loads and processes documents from source folders"""
    
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc', '.txt', '.json', '.html', '.md']
    
    # File size protection (added by fix_large_files.py)
    MAX_FILE_SIZE_MB = 500      # Skip files > 500 MB
    MAX_PDF_PAGES = 100         # Only extract first 100 pages of huge PDFs
    MAX_CHARS_EXTRACT = 100000  # Max 100K chars per document
    
    def __init__(self, config):
        """
        Initialise document loader
        
        Args:
            config: Config object with folder mapping
        """
        self.config = config
        self.folder_mapping = config.folder_mapping
        
        # Stats
        self.stats = {
            'total_loaded': 0,
            'successful': 0,
            'failed': 0,
            'by_format': {},
            'by_folder': {},
            'by_priority': {}
        }
    
    def load_all_documents(self, folders: Optional[List[Path]] = None) -> List[Dict]:
        """
        Load all documents from specified folders
        
        Args:
            folders: List of folder paths. If None, uses Pass 1 folders from config
            
        Returns:
            List of document dictionaries
        """
        if folders is None:
            folders = self.config.get_pass_1_folders()
        
        documents = []
        
        print(f"\n{'=' * 70}")
        print(f"LOADING DOCUMENTS")
        print(f"{'=' * 70}")
        print(f"Folders to load: {len(folders)}\n")
        
        for folder_path in folders:
            print(f"Loading: {folder_path.name}")
            folder_docs = self.load_folder(folder_path)
            documents.extend(folder_docs)
            print(f"  Loaded: {len(folder_docs)} documents\n")
        
        print(f"{'=' * 70}")
        print(f"Total documents loaded: {len(documents)}")
        print(f"{'=' * 70}\n")
        
        return documents
    
    def load_folder(self, folder_path: Path) -> List[Dict]:
        """
        Load all documents from a folder
        
        Args:
            folder_path: Path to folder
            
        Returns:
            List of document dictionaries
        """
        documents = []
        
        # Get folder metadata from mapping
        folder_name = folder_path.name
        folder_metadata = self._extract_folder_metadata(folder_name)
        
        # Find all supported files
        for file_path in folder_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                try:
                    doc = self.load_document(file_path, folder_metadata)
                    if doc:
                        documents.append(doc)
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                
                except Exception as e:
                    print(f"  ⚠️  Failed to load: {file_path.name} ({str(e)[:50]})")
                    self.stats['failed'] += 1
                
                self.stats['total_loaded'] += 1
        
        # Update stats
        self.stats['by_folder'][folder_name] = len(documents)
        
        return documents
    
    
    def load_document(self, file_path: Path, preview_only: bool = False) -> Dict:
        """
        Load document with size protection
        
        Args:
            file_path: Path to document
            preview_only: If True, only extract first page/preview
            
        Returns:
            Document dictionary
        """
        
        # Check file size BEFORE loading
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # Skip PST files (email archives - handle separately)
        if file_path.suffix.lower() == '.pst':
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[EMAIL ARCHIVE: {file_size_mb:.1f} MB - Extract to .msg files first]',
                'preview': f'PST email archive ({file_size_mb:.1f} MB)',
                'metadata': {
                    'file_type': 'pst',
                    'size_mb': file_size_mb,
                    'skip_reason': 'Email archive - requires extraction'
                }
            }
        
        # Skip MSG files (individual emails - handle in Phase 5)
        if file_path.suffix.lower() == '.msg':
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[EMAIL MESSAGE: {file_size_mb:.1f} MB - Process in Phase 5]',
                'preview': f'Outlook email message ({file_size_mb:.1f} MB)',
                'metadata': {
                    'file_type': 'msg',
                    'size_mb': file_size_mb,
                    'skip_reason': 'Email message - process in Phase 5 email analysis'
                }
            }
        
        # Skip extremely large files
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            print(f"   ⚠️  SKIPPING: {file_path.name} ({file_size_mb:.1f} MB)")
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[FILE TOO LARGE: {file_size_mb:.1f} MB - Skipped]',
                'preview': f'Large file ({file_size_mb:.1f} MB) not analysed',
                'metadata': {
                    'size_mb': file_size_mb,
                    'skip_reason': 'File exceeds size limit'
                }
            }
        
        # Route to format-specific handler
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self._load_pdf_safe(file_path, file_size_mb)
        elif suffix in ['.docx', '.doc']:
            return self._load_word_document(file_path)
        else:
            return self._load_text_document(file_path)
    
    def _load_pdf_safe(self, file_path: Path, file_size_mb: float) -> Dict:
        """
        Load PDF with comprehensive error handling and progress tracking
        Handles: corrupted PDFs, None errors, timeouts, large files
        
        Args:
            file_path: Path to PDF file
            file_size_mb: File size in megabytes
            
        Returns:
            Document dictionary with extracted content
        """
        
        import time
        start_time = time.time()
        
        print(f"   📄 PROGRESS: Loading {file_path.name} ({file_size_mb:.1f} MB)...", end='', flush=True)
        
        try:
            import pdfplumber
            
            # Determine extraction strategy
            if file_size_mb > 100:
                max_pages = self.MAX_PDF_PAGES
            else:
                max_pages = None
            
            text_parts = []
            total_pages = 0
            pages_extracted = 0
            
            # Open PDF with error handling
            try:
                pdf = pdfplumber.open(file_path)
            except Exception as open_error:
                print(f" ❌ FAILED (cannot open)")
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': f'[CANNOT OPEN PDF: {str(open_error)[:100]}]',
                    'preview': f'Failed to open PDF: {str(open_error)[:100]}',
                    'metadata': {
                        'file_type': 'pdf',
                        'size_mb': file_size_mb,
                        'error': f'Cannot open: {str(open_error)}'
                    }
                }
            
            try:
                # CRITICAL: Check if pages exist and is not None
                if not hasattr(pdf, 'pages') or pdf.pages is None:
                    pdf.close()
                    print(f" ❌ FAILED (no pages)")
                    return {
                        'filename': file_path.name,
                        'doc_id': self._generate_doc_id(file_path),
                        'content': '[CORRUPTED PDF: No pages found]',
                        'preview': 'PDF appears corrupted - no readable pages',
                        'metadata': {
                            'file_type': 'pdf',
                            'size_mb': file_size_mb,
                            'error': 'No pages attribute or pages is None'
                        }
                    }
                
                total_pages = len(pdf.pages)
                
                # CRITICAL: Handle None or 0 pages
                if total_pages is None or total_pages == 0:
                    pdf.close()
                    print(f" ❌ FAILED (0 pages)")
                    return {
                        'filename': file_path.name,
                        'doc_id': self._generate_doc_id(file_path),
                        'content': '[EMPTY PDF: 0 pages]',
                        'preview': 'PDF has no readable pages',
                        'metadata': {
                            'file_type': 'pdf',
                            'size_mb': file_size_mb,
                            'total_pages': 0,
                            'error': 'Empty PDF'
                        }
                    }
                
                # Calculate pages to extract
                if max_pages is not None:
                    pages_to_extract = min(total_pages, max_pages)
                else:
                    pages_to_extract = total_pages
                
                print(f" extracting {pages_to_extract}/{total_pages} pages...", end='', flush=True)
                
                # Extract text from pages with timeout protection
                for i in range(pages_to_extract):
                    # Check if taking too long (5 minutes per file max)
                    if time.time() - start_time > 300:
                        print(f" ⚠️ TIMEOUT after {pages_extracted} pages")
                        break
                    
                    try:
                        page_text = pdf.pages[i].extract_text()
                        if page_text:
                            text_parts.append(page_text)
                        pages_extracted += 1
                        
                        # Progress indicator for large files
                        if pages_extracted % 20 == 0 and file_size_mb > 50:
                            print(f" [{pages_extracted}/{pages_to_extract}]", end='', flush=True)
                        
                        # Stop if we've extracted enough chars
                        if len(''.join(text_parts)) > self.MAX_CHARS_EXTRACT:
                            break
                            
                    except Exception as page_error:
                        # Skip problematic pages but continue
                        continue
                
                pdf.close()
                
            except Exception as extract_error:
                if 'pdf' in locals():
                    try:
                        pdf.close()
                    except:
                        pass
                print(f" ❌ FAILED (extraction error)")
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': f'[PDF EXTRACTION ERROR: {str(extract_error)[:100]}]',
                    'preview': f'Error during extraction: {str(extract_error)[:100]}',
                    'metadata': {
                        'file_type': 'pdf',
                        'size_mb': file_size_mb,
                        'error': str(extract_error)[:200]
                    }
                }
            
            # Combine extracted text
            full_text = '\n\n'.join(text_parts)
            
            # Handle case where no text was extracted
            if not full_text or len(full_text.strip()) == 0:
                elapsed = time.time() - start_time
                print(f" ⚠️ NO TEXT ({elapsed:.1f}s)")
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': '[NO TEXT EXTRACTED: PDF may be scanned images]',
                    'preview': 'No text could be extracted from PDF',
                    'metadata': {
                        'file_type': 'pdf',
                        'size_mb': file_size_mb,
                        'total_pages': total_pages,
                        'pages_extracted': pages_extracted,
                        'warning': 'No text extracted - possibly scanned images'
                    }
                }
            
            # Truncate if still too long
            if len(full_text) > self.MAX_CHARS_EXTRACT:
                full_text = full_text[:self.MAX_CHARS_EXTRACT]
                full_text += f"\n\n[TRUNCATED - {total_pages} pages total, extracted {pages_extracted} pages]"
            
            elapsed = time.time() - start_time
            print(f" ✅ OK ({elapsed:.1f}s, {len(full_text):,} chars)")
            
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': full_text,
                'preview': full_text[:300],
                'metadata': {
                    'file_type': 'pdf',
                    'size_mb': file_size_mb,
                    'total_pages': total_pages,
                    'pages_extracted': pages_extracted,
                    'truncated': pages_extracted < total_pages,
                    'extraction_time_seconds': round(elapsed, 1)
                }
            }
            
        except Exception as e:
            print(f" ❌ FAILED ({str(e)[:50]})")
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[ERROR LOADING PDF: {str(e)[:200]}]',
                'preview': 'Error loading document',
                'metadata': {
                    'error': str(e)[:500],
                    'file_type': 'pdf',
                    'size_mb': file_size_mb
                }
            }

    
    def _load_word_document(self, file_path: Path) -> Dict:
        """
        Load Word document (.docx, .doc)
        
        Args:
            file_path: Path to Word document
            
        Returns:
            Document dictionary with extracted text
        """
        try:
            # Use the existing _extract_docx_text method
            text = self._extract_docx_text(file_path)
            
            if not text or len(text) < 10:
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': '[EMPTY DOCUMENT]',
                    'preview': 'Empty or unreadable Word document',
                    'metadata': {
                        'file_type': 'docx',
                        'error': 'No text extracted'
                    }
                }
            
            # Truncate if too long
            if len(text) > self.MAX_CHARS_EXTRACT:
                text = text[:self.MAX_CHARS_EXTRACT]
                text += "\n\n[TRUNCATED - document continues]"
            
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': text,
                'preview': text[:300],
                'metadata': {
                    'file_type': 'docx',
                    'text_length': len(text)
                }
            }
            
        except Exception as e:
            print(f"   ❌ Error loading Word doc: {file_path.name} - {str(e)}")
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[ERROR LOADING WORD DOC: {str(e)}]',
                'preview': 'Error loading document',
                'metadata': {'error': str(e)}
            }
    
    def _load_text_document(self, file_path: Path) -> Dict:
        """
        Load plain text document (.txt, .md, etc.)
        
        Args:
            file_path: Path to text file
            
        Returns:
            Document dictionary with text content
        """
        try:
            text = self._extract_text_file(file_path)
            
            if not text:
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': '[EMPTY FILE]',
                    'preview': 'Empty text file',
                    'metadata': {'file_type': 'text'}
                }
            
            # Truncate if too long
            if len(text) > self.MAX_CHARS_EXTRACT:
                text = text[:self.MAX_CHARS_EXTRACT]
                text += "\n\n[TRUNCATED - file continues]"
            
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': text,
                'preview': text[:300],
                'metadata': {
                    'file_type': 'text',
                    'text_length': len(text)
                }
            }
            
        except Exception as e:
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[ERROR LOADING TEXT: {str(e)}]',
                'preview': 'Error loading document',
                'metadata': {'error': str(e)}
            }
        
    def _extract_folder_metadata(self, folder_name: str) -> Dict:
        """
        Extract metadata for a folder from FolderMapping
        
        Args:
            folder_name: Name of folder (e.g., "55. Document Production")
            
        Returns:
            Dict with folder metadata
        """
        metadata = self.folder_mapping.get_folder_metadata(folder_name)
        
        if metadata:
            return {
                'folder_name': folder_name,
                'category': metadata['category'],
                'priority': metadata['priority'],
                'description': metadata['description'],
                'pass_1_include': metadata['pass_1_include']
            }
        else:
            # Folder not in mapping - use defaults
            return {
                'folder_name': folder_name,
                'category': 'unmapped',
                'priority': 5,  # Mid-priority default
                'description': 'Unmapped folder',
                'pass_1_include': True
            }
    
    def _extract_text(self, file_path: Path) -> str:
        """
        Extract text from file based on format
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
        """
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            return self._extract_pdf_text(file_path)
        elif ext in ['.docx', '.doc']:
            return self._extract_docx_text(file_path)
        elif ext in ['.txt', '.md']:
            return self._extract_text_file(file_path)
        elif ext == '.json':
            return self._extract_json_text(file_path)
        elif ext == '.html':
            return self._extract_html_text(file_path)
        else:
            return ""
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """
        Extract text from PDF using multiple methods
        Tries PyMuPDF first, falls back to pdfplumber, then PyPDF2
        """
        text = ""
        
        # Method 1: PyMuPDF (fitz) - fastest and most reliable
        try:
            with fitz.open(file_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
                
                if text.strip():
                    return text
        except Exception as e:
            pass
        
        # Method 2: pdfplumber - good for tables and complex layouts
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    return text
        except Exception as e:
            pass
        
        # Method 3: PyPDF2 - fallback
        try:
            with open(file_path, 'rb', encoding = 'utf-8') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
        except Exception as e:
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from Word document"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            return ""
    
    def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return ""
    
    def _extract_json_text(self, file_path: Path) -> str:
        """Extract text from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            return ""
    
    def _extract_html_text(self, file_path: Path) -> str:
        """Extract text from HTML file"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text()
        except Exception as e:
            # Fallback: just read as text
            return self._extract_text_file(file_path)
    
    def _generate_doc_id(self, file_path: Path) -> str:
        """
        Generate unique document ID from file path
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash of file path
        """
        path_str = str(file_path)
        return hashlib.sha256(path_str.encode()).hexdigest()[:16]
    
    def print_stats(self):
        """Print loading statistics"""
        print("\n" + "=" * 70)
        print("DOCUMENT LOADING STATISTICS")
        print("=" * 70)
        
        print(f"Total files processed: {self.stats['total_loaded']}")
        print(f"  Successful: {self.stats['successful']}")
        print(f"  Failed: {self.stats['failed']}")
        
        if self.stats['by_format']:
            print(f"\nBy format:")
            for fmt, count in sorted(self.stats['by_format'].items()):
                print(f"  {fmt}: {count} documents")
        
        if self.stats['by_priority']:
            print(f"\nBy priority tier:")
            for priority in sorted(self.stats['by_priority'].keys(), reverse=True):
                count = self.stats['by_priority'][priority]
                print(f"  Tier {priority}: {count} documents")
        
        if self.stats['by_folder']:
            print(f"\nBy folder (top 10):")
            sorted_folders = sorted(self.stats['by_folder'].items(), 
                                  key=lambda x: x[1], reverse=True)
            for folder, count in sorted_folders[:10]:
                print(f"  {folder}: {count} documents")
        
        print("=" * 70)
    
    def save_document_index(self, documents: List[Dict], output_file: Path = None):
        """
        Save document index to JSON file
        
        Args:
            documents: List of document dictionaries
            output_file: Output file path
        """
        if output_file is None:
            output_file = self.config.output_dir / "document_index.json"
        
        # Create lightweight index (without full text)
        index = []
        for doc in documents:
            index_entry = {
                'id': doc['id'],
                'filename': doc['filename'],
                'filepath': doc['filepath'],
                'folder_name': doc['folder_name'],
                'folder_category': doc['folder_category'],
                'folder_priority': doc['folder_priority'],
                'text_length': doc['text_length'],
                'preview': doc['preview'],
                'modified_date': doc['modified_date']
            }
            index.append(index_entry)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Document index saved: {output_file}")


if __name__ == "__main__":
    # Test document loader
    from src.core.config import Config
    
    config = Config()
    loader = DocumentLoader(config)
    
    print("Testing document loader...")
    print(f"Source root: {config.source_root}")
    print(f"\nPass 1 folders: {len(config.get_pass_1_folders())}")
    
    # Load documents from Pass 1 folders
    documents = loader.load_all_documents()
    
    # Print stats
    loader.print_stats()
    
    # Save index
    loader.save_document_index(documents)