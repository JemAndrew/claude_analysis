# src/utils.py
"""
Utility functions for document processing, batching, and analysis
Supports the Opus 4.1 litigation investigation system
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Any
import json
import logging

logger = logging.getLogger(__name__)

# In utils.py, update the load_documents function:
def load_documents(project_root: Path) -> List[Dict]:
    """
    Load documents with Opus 4.1 preprocessing
    Now includes metadata from document processor
    """
    documents = []
    text_dir = project_root / "documents" / "processed" / "text"
    metadata_dir = project_root / "documents" / "processed" / "metadata"
    
    if not text_dir.exists():
        logger.warning(f"No processed documents found at {text_dir}")
        return []
    
    for text_file in text_dir.glob("*.txt"):
        try:
            doc_id = text_file.stem
            
            # Load text content
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to load metadata
            doc_metadata = {}
            metadata_file = metadata_dir / f"{doc_id}.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    doc_metadata = json.load(f)
            
            documents.append({
                'doc_id': doc_id,
                'text': content,
                'date': extract_date_from_content(content),  # Still extract from content
                'type': identify_document_type(doc_metadata.get('filename', doc_id)),
                'length': len(content),
                'forensic_priority': assess_forensic_priority(content),
                'extraction_quality': doc_metadata.get('extraction_quality', 1.0),
                'original_filename': doc_metadata.get('filename', 'unknown'),
                'page_count': doc_metadata.get('page_count', 0),
                'extraction_method': doc_metadata.get('extraction_method', 'unknown')
            })
        except Exception as e:
            logger.error(f"Error loading document {text_file}: {e}")
    
    # Sort by forensic priority
    documents.sort(key=lambda x: x.get('forensic_priority', 0), reverse=True)
    
    logger.info(f"Loaded {len(documents)} documents from {text_dir}")
    return documents

def batch_documents(documents: List[Dict], batch_size: Optional[int] = None) -> List[List[Dict]]:
    """
    Optimised batching for Opus 4.1 processing
    
    Args:
        documents: List of document dictionaries
        batch_size: Maximum documents per batch (default 40)
        
    Returns:
        List of document batches
    """
    if batch_size is None:
        batch_size = 40  # Opus 4.1 optimal
    
    batches = []
    current_batch = []
    current_size = 0
    max_batch_chars = 150000  # Character limit per batch
    
    for doc in documents:
        doc_size = len(doc.get('text', ''))
        
        # Check if adding this doc would exceed limits
        if (current_size + doc_size > max_batch_chars or 
            len(current_batch) >= batch_size) and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_size = 0
        
        current_batch.append(doc)
        current_size += doc_size
    
    # Add remaining documents
    if current_batch:
        batches.append(current_batch)
    
    logger.info(f"Created {len(batches)} batches from {len(documents)} documents")
    return batches

def format_batch_with_metadata(batch: List[Dict]) -> str:
    """
    Format document batch with enhanced metadata for Opus 4.1
    
    Args:
        batch: List of document dictionaries
        
    Returns:
        Formatted string for API processing
    """
    formatted = []
    
    for doc in batch:
        # Truncate content to 3000 chars for processing efficiency
        content = doc.get('text', '')[:3000]
        
        doc_text = f"""
[DOCUMENT ID: {doc.get('doc_id', 'unknown')}]
[DATE: {doc.get('date', 'unknown')}]
[TYPE: {doc.get('type', 'unknown')}]
[FORENSIC PRIORITY: {doc.get('forensic_priority', 0)}]
[LENGTH: {doc.get('length', 0)} chars]
[FORENSIC NOTES: Check metadata for authenticity]
[CONTENT START]
{content}
[CONTENT END]
"""
        formatted.append(doc_text.strip())
    
    return "\n\n".join(formatted)

def extract_date_from_content(content: str) -> str:
    """
    Extract date from document content using pattern matching
    
    Args:
        content: Document text
        
    Returns:
        Date string or 'unknown'
    """
    # Multiple date patterns to try
    date_patterns = [
        r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',  # DD-MM-YYYY or similar
        r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b',  # DD Month YYYY
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})\b',  # Month DD, YYYY
        r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return "unknown"

def identify_document_type(filename: str) -> str:
    """
    Identify document type with litigation categories
    
    Args:
        filename: Name of the file
        
    Returns:
        Document type string
    """
    filename_lower = filename.lower()
    
    # Priority order matters - check most specific first
    type_patterns = {
        'board_minutes': ['minutes', 'board meeting'],
        'board_resolution': ['resolution', 'board resolution'],
        'email': ['email', 'e-mail', 'mail'],
        'contract': ['agreement', 'contract', 'deed', 'mou'],
        'report': ['report', 'analysis', 'assessment'],
        'correspondence': ['letter', 'memo', 'memorandum'],
        'legal_advice': ['legal', 'counsel', 'advice', 'opinion'],
        'financial': ['financial', 'accounts', 'audit', 'balance'],
        'due_diligence': ['due diligence', 'dd', 'diligence'],
        'presentation': ['presentation', 'slides', 'deck'],
    }
    
    for doc_type, patterns in type_patterns.items():
        if any(pattern in filename_lower for pattern in patterns):
            return doc_type
    
    return "general"

def assess_forensic_priority(content: str) -> int:
    """
    Assess forensic priority for Opus 4.1 analysis
    
    Args:
        content: Document text
        
    Returns:
        Priority score (0-100)
    """
    priority = 0
    content_lower = content.lower()
    
    # High priority indicators with weights
    priority_indicators = {
        # Critical legal/privilege indicators
        'privileged': 15,
        'confidential': 10,
        'without prejudice': 15,
        'litigation privilege': 20,
        'legal advice': 15,
        
        # Fraud and investigation indicators
        'fraud': 20,
        'investigation': 15,
        'suspicious': 12,
        'irregular': 10,
        'manipulat': 15,  # Catches manipulation, manipulated
        
        # Key parties
        'mcnaughton': 20,
        'vr capital': 15,
        'lismore': 15,
        'p&id': 15,
        'nigeria': 10,
        
        # Decision-making indicators
        'board resolution': 12,
        'board meeting': 10,
        'voting': 10,
        '51%': 15,
        'control': 10,
        'approval': 8,
        
        # Financial indicators
        'million': 5,
        'billion': 8,
        '$45': 10,  # VR's investment amount
        'payment': 7,
        
        # Timing indicators
        'october 2017': 15,  # VR investment date
        'january 2020': 15,  # McNaughton warning
        '2023': 10,  # Award set aside
        
        # Communication patterns
        'concern': 8,
        'warning': 10,
        'risk': 8,
        'issue': 5,
        'problem': 7,
    }
    
    for indicator, weight in priority_indicators.items():
        if indicator in content_lower:
            priority += weight
    
    # Cap at 100
    return min(priority, 100)

def extract_metadata_from_document(doc: Dict) -> Dict:
    """
    Extract additional metadata for forensic analysis
    
    Args:
        doc: Document dictionary
        
    Returns:
        Enhanced metadata dictionary
    """
    content = doc.get('text', '')
    
    metadata = {
        'doc_id': doc.get('doc_id'),
        'has_attachments': bool(re.search(r'attach|annex|append', content, re.IGNORECASE)),
        'references_meetings': bool(re.search(r'meeting|conference|discussion', content, re.IGNORECASE)),
        'references_board': bool(re.search(r'board|director', content, re.IGNORECASE)),
        'references_legal': bool(re.search(r'legal|lawyer|counsel|attorney', content, re.IGNORECASE)),
        'email_count': len(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)),
        'url_count': len(re.findall(r'https?://[^\s]+', content)),
        'monetary_references': len(re.findall(r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion))?', content, re.IGNORECASE)),
        'word_count': len(content.split()),
        'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
    }
    
    return metadata

def find_document_relationships(documents: List[Dict]) -> Dict[str, List[str]]:
    """
    Find relationships between documents based on references
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        Dictionary mapping document IDs to related document IDs
    """
    relationships = {}
    
    for doc in documents:
        doc_id = doc.get('doc_id', '')
        content = doc.get('text', '')
        related = []
        
        # Look for references to other documents
        for other_doc in documents:
            other_id = other_doc.get('doc_id', '')
            if doc_id != other_id and other_id in content:
                related.append(other_id)
        
        if related:
            relationships[doc_id] = related
    
    return relationships

def calculate_document_similarity(doc1: Dict, doc2: Dict) -> float:
    """
    Calculate similarity score between two documents
    
    Args:
        doc1: First document
        doc2: Second document
        
    Returns:
        Similarity score (0-1)
    """
    # Simple implementation - could be enhanced with proper NLP
    text1 = set(doc1.get('text', '').lower().split())
    text2 = set(doc2.get('text', '').lower().split())
    
    if not text1 or not text2:
        return 0.0
    
    intersection = text1 & text2
    union = text1 | text2
    
    return len(intersection) / len(union) if union else 0.0

def extract_key_phrases(content: str, top_n: int = 10) -> List[str]:
    """
    Extract key phrases from document content
    
    Args:
        content: Document text
        top_n: Number of top phrases to return
        
    Returns:
        List of key phrases
    """
    # Simple implementation - extracts capitalised phrases
    phrases = re.findall(r'[A-Z][A-Za-z\s]+(?:[A-Z][a-z]+)?', content)
    
    # Filter and count
    phrase_counts = {}
    for phrase in phrases:
        phrase = phrase.strip()
        if len(phrase) > 3 and len(phrase.split()) <= 5:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
    
    # Sort by frequency
    sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [phrase for phrase, count in sorted_phrases[:top_n]]

def save_json_output(data: Any, output_path: Path, indent: int = 2):
    """
    Save data as JSON with proper formatting
    
    Args:
        data: Data to save
        output_path: Path to save file
        indent: JSON indentation level
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.info(f"Saved output to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save output to {output_path}: {e}")

def load_json_file(file_path: Path) -> Optional[Dict]:
    """
    Load JSON file with error handling
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary or None if error
    """
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
    return None