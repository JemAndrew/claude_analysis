# Handles PDFs, Word docs, OCR
"""
document_processor.py
Handles PDF/Word document extraction and OCR for Lismore investigation
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any 
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Document processing libraries
import PyPDF2
from PIL import Image
import pytesseract
import pdf2image
from docx import Document

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedDocument:
    """Represents a fully processed document ready for analysis"""
    doc_id: str
    original_path: str
    filename: str
    doc_type: str  # pdf, docx, scanned_pdf
    text_content: str
    page_count: int
    extraction_method: str  # direct_text, ocr, mixed
    extraction_quality: float  # 0.0 to 1.0
    metadata: Dict
    processing_date: str
    errors: List[str]
    
    def to_dict(self):
        return asdict(self)

class DocumentProcessor:
    """
    Processes all documents from hard drive for investigation.
    Handles PDFs (searchable and scanned) and Word documents.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.raw_dir = self.project_root / "documents" / "raw"
        self.processed_dir = self.project_root / "documents" / "processed"
        self.index_file = self.project_root / "documents" / "index" / "master_index.json"
        self.processed_documents = []
        self.failed_documents = []
        
        # Create directories if they don't exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        (self.processed_dir / "text").mkdir(exist_ok=True)
        (self.processed_dir / "ocr").mkdir(exist_ok=True)
        (self.processed_dir / "metadata").mkdir(exist_ok=True)
        (self.processed_dir / "failed_ocr").mkdir(exist_ok=True)
        
    def process_all_documents(self) -> Dict[str, Any]:
        """
        Main entry point - processes all documents in raw folder.
        Returns summary of processing results.
        """
        logger.info("Starting document processing...")
        
        # Find all documents
        all_files = self._find_all_documents()
        logger.info(f"Found {len(all_files)} documents to process")
        
        # Process each document
        for idx, file_path in enumerate(all_files, 1):
            logger.info(f"Processing {idx}/{len(all_files)}: {file_path.name}")
            
            try:
                processed_doc = self._process_single_document(file_path)
                self.processed_documents.append(processed_doc)
                self._save_processed_document(processed_doc)
                
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                self.failed_documents.append({
                    'path': str(file_path),
                    'error': str(e)
                })
        
        # Save index
        self._save_index()
        
        return {
            'total_files': len(all_files),
            'successfully_processed': len(self.processed_documents),
            'failed': len(self.failed_documents),
            'failed_files': self.failed_documents
        }
    
    def _find_all_documents(self) -> List[Path]:
        """Find all PDFs and Word docs in raw directory"""
        documents = []
        
        for batch_dir in self.raw_dir.glob("batch_*"):
            # Find PDFs
            documents.extend(batch_dir.glob("*.pdf"))
            documents.extend(batch_dir.glob("*.PDF"))
            
            # Find Word docs
            documents.extend(batch_dir.glob("*.docx"))
            documents.extend(batch_dir.glob("*.doc"))
            documents.extend(batch_dir.glob("*.DOCX"))
            documents.extend(batch_dir.glob("*.DOC"))
        
        return sorted(documents)
    
    def _process_single_document(self, file_path: Path) -> ProcessedDocument:
        """Process a single document file"""
        
        # Generate document ID
        doc_id = self._generate_doc_id(file_path)
        
        # Determine file type and process accordingly
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._process_pdf(file_path, doc_id)
        elif file_extension in ['.docx', '.doc']:
            return self._process_word(file_path, doc_id)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _process_pdf(self, file_path: Path, doc_id: str) -> ProcessedDocument:
        """Process PDF - try text extraction first, OCR if needed"""
        
        text_content = ""
        page_count = 0
        extraction_method = "unknown"
        extraction_quality = 0.0
        errors = []
        metadata = {}
        
        try:
            # Try direct text extraction first
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', ''))
                    }
                
                # Try to extract text
                extracted_text = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text.append(f"[Page {page_num + 1}]\n{page_text}")
                    except Exception as e:
                        errors.append(f"Page {page_num + 1}: {str(e)}")
                
                text_content = "\n\n".join(extracted_text)
                
                # Check if we got meaningful text
                if self._is_meaningful_text(text_content):
                    extraction_method = "direct_text"
                    extraction_quality = self._assess_text_quality(text_content)
                else:
                    # Need OCR
                    logger.info(f"PDF appears to be scanned, attempting OCR for {file_path.name}")
                    ocr_text = self._ocr_pdf(file_path)
                    
                    if ocr_text:
                        text_content = ocr_text
                        extraction_method = "ocr"
                        extraction_quality = self._assess_text_quality(ocr_text)
                    else:
                        extraction_method = "failed"
                        extraction_quality = 0.0
                        errors.append("OCR failed to extract meaningful text")
                        
        except Exception as e:
            errors.append(f"PDF processing error: {str(e)}")
            extraction_method = "failed"
            
        return ProcessedDocument(
            doc_id=doc_id,
            original_path=str(file_path),
            filename=file_path.name,
            doc_type="pdf",
            text_content=text_content,
            page_count=page_count,
            extraction_method=extraction_method,
            extraction_quality=extraction_quality,
            metadata=metadata,
            processing_date=datetime.now().isoformat(),
            errors=errors
        )
    
    def _process_word(self, file_path: Path, doc_id: str) -> ProcessedDocument:
        """Process Word document"""
        
        text_content = ""
        page_count = 1  # Word doesn't have clear pages
        errors = []
        metadata = {}
        
        try:
            doc = Document(file_path)
            
            # Extract text from paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            # Extract text from tables
            table_texts = []
            for table in doc.tables:
                table_text = self._extract_table_text(table)
                if table_text:
                    table_texts.append(table_text)
            
            # Combine all text
            text_content = "\n\n".join(paragraphs)
            if table_texts:
                text_content += "\n\n[Tables]\n" + "\n\n".join(table_texts)
            
            # Try to extract metadata
            try:
                core_props = doc.core_properties
                metadata = {
                    'title': core_props.title or '',
                    'author': core_props.author or '',
                    'created': str(core_props.created) if core_props.created else '',
                    'modified': str(core_props.modified) if core_props.modified else '',
                    'last_modified_by': core_props.last_modified_by or ''
                }
            except:
                pass
            
            extraction_quality = self._assess_text_quality(text_content)
            
        except Exception as e:
            errors.append(f"Word processing error: {str(e)}")
            extraction_quality = 0.0
            
        return ProcessedDocument(
            doc_id=doc_id,
            original_path=str(file_path),
            filename=file_path.name,
            doc_type="docx",
            text_content=text_content,
            page_count=page_count,
            extraction_method="direct_text",
            extraction_quality=extraction_quality,
            metadata=metadata,
            processing_date=datetime.now().isoformat(),
            errors=errors
        )
    
    def _ocr_pdf(self, file_path: Path) -> Optional[str]:
        """OCR a scanned PDF"""
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(file_path, dpi=300)
            
            # OCR each page
            ocr_texts = []
            for i, image in enumerate(images):
                logger.info(f"OCR processing page {i+1}/{len(images)} of {file_path.name}")
                
                # Perform OCR
                text = pytesseract.image_to_string(image, lang='eng')
                
                if text.strip():
                    ocr_texts.append(f"[Page {i+1}]\n{text}")
            
            return "\n\n".join(ocr_texts)
            
        except Exception as e:
            logger.error(f"OCR failed for {file_path.name}: {str(e)}")
            return None
    
    def _extract_table_text(self, table) -> str:
        """Extract text from Word table"""
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text.strip())
            table_data.append(" | ".join(row_data))
        return "\n".join(table_data)
    
    def _is_meaningful_text(self, text: str) -> bool:
        """Check if extracted text is meaningful or just garbage"""
        if not text or len(text.strip()) < 100:
            return False
        
        # Check for reasonable word count
        words = text.split()
        if len(words) < 20:
            return False
        
        # Check for too many special characters (sign of failed extraction)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            return False
        
        return True
    
    def _assess_text_quality(self, text: str) -> float:
        """Assess quality of extracted text (0.0 to 1.0)"""
        if not text:
            return 0.0
        
        score = 1.0
        
        # Penalise for too many special characters
        special_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        score -= special_ratio * 0.5
        
        # Penalise for very short text
        if len(text) < 500:
            score -= 0.3
        
        # Penalise for no proper words
        words = text.split()
        if len(words) < 50:
            score -= 0.3
        
        # Check for reasonable sentence structure
        if text.count('.') < 5:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _generate_doc_id(self, file_path: Path) -> str:
        """Generate unique document ID"""
        content = f"{file_path.name}_{file_path.stat().st_size}_{file_path.stat().st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _save_processed_document(self, doc: ProcessedDocument):
        """Save processed document to disk"""
        
        # Save text content
        text_file = self.processed_dir / "text" / f"{doc.doc_id}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(doc.text_content)
        
        # Save metadata
        metadata_file = self.processed_dir / "metadata" / f"{doc.doc_id}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved processed document: {doc.doc_id} ({doc.filename})")
    
    def _save_index(self):
        """Save master index of all processed documents"""
        
        index_data = {
            'total_documents': len(self.processed_documents) + len(self.failed_documents),
            'processed': len(self.processed_documents),
            'failed': len(self.failed_documents),
            'processing_date': datetime.now().isoformat(),
            'documents': [
                {
                    'doc_id': doc.doc_id,
                    'filename': doc.filename,
                    'doc_type': doc.doc_type,
                    'extraction_method': doc.extraction_method,
                    'extraction_quality': doc.extraction_quality,
                    'page_count': doc.page_count,
                    'has_errors': len(doc.errors) > 0
                }
                for doc in self.processed_documents
            ],
            'failed_documents': self.failed_documents
        }
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Index saved: {len(self.processed_documents)} processed, {len(self.failed_documents)} failed")

def main():
    """Run document processing""" 
    
    # Get project root from current file location
    project_root = Path(__file__).parent.parent
    
    processor = DocumentProcessor(project_root)
    results = processor.process_all_documents()
    
    print("\n" + "="*50)
    print("DOCUMENT PROCESSING COMPLETE")
    print("="*50)
    print(f"✅ Successfully processed: {results['successfully_processed']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['failed_files']:
        print("\nFailed files:")
        for failed in results['failed_files']:
            print(f"  - {failed['path']}: {failed['error']}")
    
    print(f"\n📁 Processed documents saved to: documents/processed/")
    print(f"📋 Index saved to: documents/index/master_index.json")

if __name__ == "__main__":
    main()