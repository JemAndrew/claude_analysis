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
    
    def load_document(self, file_path: Path, folder_metadata: Dict) -> Optional[Dict]:
        """
        Load a single document
        
        Args:
            file_path: Path to document
            folder_metadata: Metadata extracted from folder
            
        Returns:
            Document dictionary or None if failed
        """
        # Extract text based on file type
        text = self._extract_text(file_path)
        
        if not text or len(text.strip()) < 10:
            return None  # Skip empty or near-empty files
        
        # Generate document ID
        doc_id = self._generate_doc_id(file_path)
        
        # Build document dictionary
        document = {
            'id': doc_id,
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_extension': file_path.suffix.lower(),
            'file_size_bytes': file_path.stat().st_size,
            'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'text': text,
            'text_length': len(text),
            'preview': text[:300],  # First 300 chars for triage
            
            # Folder metadata
            'folder_name': folder_metadata['folder_name'],
            'folder_category': folder_metadata['category'],
            'folder_priority': folder_metadata['priority'],
            'folder_description': folder_metadata['description'],
            
            # Processing metadata
            'loaded_at': datetime.now().isoformat(),
            'processing_status': 'loaded'
        }
        
        # Update format stats
        ext = file_path.suffix.lower()
        self.stats['by_format'][ext] = self.stats['by_format'].get(ext, 0) + 1
        
        # Update priority stats
        priority = folder_metadata['priority']
        self.stats['by_priority'][priority] = self.stats['by_priority'].get(priority, 0) + 1
        
        return document
    
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
            with open(file_path, 'rb') as f:
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