#!/usr/bin/env python3
"""
Document Deduplication System
Detects and filters exact and near-duplicate documents
British English throughout - Lismore v Process Holdings

Location: src/utils/deduplication.py
"""

import hashlib
import re
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import math


class DocumentDeduplicator:
    """
    Detects duplicate and near-duplicate documents using:
    1. Content hashing for exact duplicates
    2. Fuzzy hashing for near-duplicates (first N pages)
    3. TF-IDF cosine similarity for semantic duplicates
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.85,
                 prefix_chars: int = 10000,
                 enable_semantic: bool = True):
        """
        Initialise deduplicator
        
        Args:
            similarity_threshold: 0.0-1.0, documents above this are considered duplicates
            prefix_chars: Number of chars from start to check (simulates "first few pages")
            enable_semantic: Use semantic similarity (slower but more accurate)
        """
        self.similarity_threshold = similarity_threshold
        self.prefix_chars = prefix_chars
        self.enable_semantic = enable_semantic
        
        # Track seen documents
        self.seen_hashes = set()  # Exact duplicates
        self.seen_fuzzy_hashes = set()  # Near-duplicates (prefix-based)
        self.document_vectors = {}  # For semantic similarity
        
        # Statistics
        self.stats = {
            'total_checked': 0,
            'exact_duplicates': 0,
            'fuzzy_duplicates': 0,
            'semantic_duplicates': 0,
            'unique_documents': 0
        }
    
    def is_duplicate(self, 
                     doc_content: str, 
                     doc_id: str,
                     filename: str = None) -> Tuple[bool, str]:
        """
        Check if document is a duplicate
        
        Args:
            doc_content: Full document text
            doc_id: Document identifier
            filename: Optional filename for better duplicate detection
            
        Returns:
            (is_duplicate: bool, reason: str)
        """
        self.stats['total_checked'] += 1
        
        if not doc_content or len(doc_content.strip()) < 100:
            # Too short to be meaningful
            return False, "too_short"
        
        # Clean content for hashing
        clean_content = self._clean_text(doc_content)
        
        # ================================================================
        # STAGE 1: EXACT DUPLICATE CHECK (Fast)
        # ================================================================
        content_hash = self._hash_content(clean_content)
        
        if content_hash in self.seen_hashes:
            self.stats['exact_duplicates'] += 1
            return True, "exact_duplicate"
        
        # ================================================================
        # STAGE 2: FUZZY DUPLICATE CHECK (First N chars - "First Few Pages")
        # ================================================================
        prefix = clean_content[:self.prefix_chars]
        fuzzy_hash = self._hash_content(prefix)
        
        if fuzzy_hash in self.seen_fuzzy_hashes:
            self.stats['fuzzy_duplicates'] += 1
            return True, "fuzzy_duplicate_prefix"
        
        # ================================================================
        # STAGE 3: SEMANTIC SIMILARITY CHECK (Slower but catches variants)
        # ================================================================
        if self.enable_semantic and len(self.document_vectors) > 0:
            # Check similarity against all previously seen documents
            is_similar, similar_to = self._check_semantic_similarity(
                clean_content, 
                doc_id
            )
            
            if is_similar:
                self.stats['semantic_duplicates'] += 1
                return True, f"semantic_duplicate_of_{similar_to}"
        
        # ================================================================
        # NOT A DUPLICATE - Register this document
        # ================================================================
        self.seen_hashes.add(content_hash)
        self.seen_fuzzy_hashes.add(fuzzy_hash)
        
        if self.enable_semantic:
            self.document_vectors[doc_id] = self._vectorise_document(clean_content)
        
        self.stats['unique_documents'] += 1
        return False, "unique"
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text for comparison
        Removes: whitespace variations, page numbers, headers/footers
        """
        # Lowercase
        text = text.lower()
        
        # Remove common document artefacts
        text = re.sub(r'page \d+( of \d+)?', '', text)
        text = re.sub(r'\[page \d+\]', '', text)
        text = re.sub(r'confidential', '', text, flags=re.IGNORECASE)
        text = re.sub(r'without prejudice', '', text, flags=re.IGNORECASE)
        
        # Normalise whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _hash_content(self, content: str) -> str:
        """Generate hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _check_semantic_similarity(self, 
                                   content: str, 
                                   doc_id: str) -> Tuple[bool, str]:
        """
        Check semantic similarity against all previously seen documents
        Uses TF-IDF + Cosine Similarity (no external dependencies)
        
        Returns:
            (is_similar: bool, similar_to_doc_id: str)
        """
        # Vectorise current document
        current_vector = self._vectorise_document(content)
        
        # Compare against all seen documents
        for seen_doc_id, seen_vector in self.document_vectors.items():
            similarity = self._cosine_similarity(current_vector, seen_vector)
            
            if similarity >= self.similarity_threshold:
                return True, seen_doc_id
        
        return False, None
    
    def _vectorise_document(self, content: str) -> Dict[str, float]:
        """
        Create TF-IDF vector for document
        Simple implementation without sklearn
        
        Returns:
            Dict mapping term -> TF-IDF score
        """
        # Tokenise
        words = re.findall(r'\b[a-z]{3,}\b', content.lower())
        
        # Remove stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'with', 
            'was', 'this', 'that', 'from', 'have', 'has', 'had', 'been',
            'will', 'would', 'could', 'should', 'may', 'might', 'must'
        }
        words = [w for w in words if w not in stop_words]
        
        # Calculate term frequency (TF)
        total_words = len(words)
        if total_words == 0:
            return {}
        
        tf = {}
        for word in words:
            tf[word] = tf.get(word, 0) + 1
        
        # Normalise by document length
        for word in tf:
            tf[word] = tf[word] / total_words
        
        # For simplicity, we skip IDF calculation (would need corpus statistics)
        # TF alone is sufficient for detecting near-duplicates
        
        return tf
    
    def _cosine_similarity(self, 
                          vec1: Dict[str, float], 
                          vec2: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between two TF-IDF vectors
        
        Returns:
            Similarity score 0.0-1.0
        """
        if not vec1 or not vec2:
            return 0.0
        
        # Get all terms
        all_terms = set(vec1.keys()) | set(vec2.keys())
        
        # Calculate dot product and magnitudes
        dot_product = 0.0
        mag1 = 0.0
        mag2 = 0.0
        
        for term in all_terms:
            v1 = vec1.get(term, 0.0)
            v2 = vec2.get(term, 0.0)
            
            dot_product += v1 * v2
            mag1 += v1 * v1
            mag2 += v2 * v2
        
        mag1 = math.sqrt(mag1)
        mag2 = math.sqrt(mag2)
        
        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def get_statistics(self) -> Dict:
        """Get deduplication statistics"""
        return {
            **self.stats,
            'deduplication_rate': (
                (self.stats['exact_duplicates'] + 
                 self.stats['fuzzy_duplicates'] + 
                 self.stats['semantic_duplicates']) / 
                max(1, self.stats['total_checked'])
            ),
            'unique_rate': self.stats['unique_documents'] / max(1, self.stats['total_checked'])
        }
    
    def reset(self):
        """Reset deduplicator (clear all seen documents)"""
        self.seen_hashes.clear()
        self.seen_fuzzy_hashes.clear()
        self.document_vectors.clear()
        self.stats = {
            'total_checked': 0,
            'exact_duplicates': 0,
            'fuzzy_duplicates': 0,
            'semantic_duplicates': 0,
            'unique_documents': 0
        }


# ================================================================
# INTEGRATION FUNCTIONS
# ================================================================

def deduplicate_document_list(documents: List[Dict], 
                              config=None) -> Tuple[List[Dict], Dict]:
    """
    Filter duplicate documents from a list
    
    Args:
        documents: List of document dicts with 'content' and 'doc_id'
        config: Optional config object with deduplication settings
        
    Returns:
        (unique_documents: List[Dict], stats: Dict)
    """
    # Get settings from config or use defaults
    if config and hasattr(config, 'deduplication_config'):
        settings = config.deduplication_config
    else:
        settings = {
            'enabled': True,
            'similarity_threshold': 0.85,
            'prefix_chars': 10000,
            'enable_semantic': True
        }
    
    if not settings['enabled']:
        return documents, {'deduplication': 'disabled'}
    
    deduplicator = DocumentDeduplicator(
        similarity_threshold=settings['similarity_threshold'],
        prefix_chars=settings['prefix_chars'],
        enable_semantic=settings['enable_semantic']
    )
    
    unique_documents = []
    duplicate_log = []
    
    for doc in documents:
        content = doc.get('content', '') or doc.get('preview', '')
        doc_id = doc.get('doc_id', '')
        filename = doc.get('filename', '')
        
        is_dup, reason = deduplicator.is_duplicate(content, doc_id, filename)
        
        if not is_dup:
            unique_documents.append(doc)
        else:
            duplicate_log.append({
                'doc_id': doc_id,
                'filename': filename,
                'duplicate_type': reason
            })
    
    stats = deduplicator.get_statistics()
    stats['duplicate_log'] = duplicate_log
    
    return unique_documents, stats