# Add this method to your existing utils.py file

import PyPDF2
import docx
import chardet
import json
from pathlib import Path
from typing import Dict, List, Optional

def extract_text_from_file(filepath: str) -> Optional[str]:
    """
    Extract text from various file types
    
    Args:
        filepath: Path to the file
        
    Returns:
        Extracted text or None if extraction fails
    """
    file_path = Path(filepath)
    
    if not file_path.exists():
        print(f"❌ File not found: {filepath}")
        return None
    
    extension = file_path.suffix.lower()
    
    try:
        # PDF files
        if extension == '.pdf':
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text
        
        # Word documents
        elif extension in ['.docx', '.doc']:
            doc = docx.Document(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        
        # JSON files
        elif extension == '.json':
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return json.dumps(data, indent=2)
        
        # HTML/XML files
        elif extension in ['.html', '.xml']:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        
        # Text files or unknown - try to read as text
        else:
            # Detect encoding
            with open(filepath, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            # Read with detected encoding
            with open(filepath, 'r', encoding=encoding, errors='ignore') as file:
                return file.read()
                
    except Exception as e:
        print(f"⚠️ Error extracting from {filepath}: {e}")
        return None

def load_documents(document_paths: List[str]) -> List[Dict]:
    """
    Load documents from file paths or directories
    
    Args:
        document_paths: List of file paths or directory paths
        
    Returns:
        List of document dictionaries with content
    """
    documents = []
    
    for path_str in document_paths:
        path = Path(path_str)
        
        if path.is_file():
            # Single file
            content = extract_text_from_file(str(path))
            if content:
                documents.append({
                    'path': str(path),
                    'filename': path.name,
                    'content': content
                })
        
        elif path.is_dir():
            # Directory - load all files
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    content = extract_text_from_file(str(file_path))
                    if content:
                        documents.append({
                            'path': str(file_path),
                            'filename': file_path.name,
                            'content': content
                        })
    
    return documents

def validate_documents(documents: List[Dict]) -> List[Dict]:
    """
    Validate and clean documents
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        List of valid documents
    """
    valid_docs = []
    
    for doc in documents:
        if not doc.get('content'):
            print(f"⚠️ Skipping empty document: {doc.get('filename', 'unknown')}")
            continue
        
        # Check minimum content length
        if len(doc['content']) < 100:
            print(f"⚠️ Skipping too-short document: {doc.get('filename', 'unknown')}")
            continue
        
        valid_docs.append(doc)
    
    return valid_docs