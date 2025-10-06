#!/usr/bin/env python3
"""
Document Retrieval with BM25 Algorithm
Optimised search for litigation documents
British English throughout - Lismore v Process Holdings

Location: src/utils/document_retrieval.py
"""

import re
import math
from typing import List, Dict, Tuple
from collections import Counter
import logging


class DocumentRetrieval:
    """
    BM25-based document retrieval system
    
    BM25 is the industry standard for document ranking, used by:
    - Elasticsearch
    - Apache Lucene
    - Microsoft Bing
    
    Advantages over simple keyword matching:
    - Term frequency saturation (diminishing returns for repeated terms)
    - Document length normalisation (fair comparison of short/long docs)
    - IDF weighting (rare terms are more valuable)
    """
    
    def __init__(self, knowledge_graph, config=None):
        """
        Initialise document retrieval system
        
        Args:
            knowledge_graph: KnowledgeGraph instance with documents
            config: Optional configuration object
        """
        self.knowledge_graph = knowledge_graph
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger('DocumentRetrieval')
        self.logger.setLevel(logging.INFO)
        
        # BM25 parameters (tuned for legal documents)
        self.k1 = 1.5  # Term frequency saturation (1.2-2.0 typical)
        self.b = 0.75  # Length normalisation (0.75 is standard)
        
        # Index structures
        self.index = None
        self.doc_lengths = None
        self.avgdl = 0
        self.N = 0
        self.documents = []
        
        # Build index on initialisation
        self._build_index()
    
    def _build_index(self):
        """
        Build inverted index for fast BM25 search
        
        Index structure:
        {
            'term': {
                'doc_id_1': frequency,
                'doc_id_2': frequency,
                ...
            }
        }
        """
        self.logger.info("Building document index for BM25 retrieval...")
        
        # Get all documents from knowledge graph
        self.documents = self.knowledge_graph.get_all_documents()
        
        if not self.documents:
            self.logger.warning("No documents found in knowledge graph")
            self.index = {}
            self.doc_lengths = {}
            self.avgdl = 0
            self.N = 0
            return
        
        self.N = len(self.documents)
        self.index = {}
        self.doc_lengths = {}
        
        # Build inverted index
        for doc in self.documents:
            doc_id = doc['doc_id']
            
            # Get document text
            text = doc.get('content', '') or doc.get('preview', '')
            
            # Tokenise
            terms = self._tokenize(text)
            self.doc_lengths[doc_id] = len(terms)
            
            # Count term frequencies in this document
            term_counts = Counter(terms)
            
            # Add to inverted index
            for term, count in term_counts.items():
                if term not in self.index:
                    self.index[term] = {}
                self.index[term][doc_id] = count
        
        # Calculate average document length
        if self.doc_lengths:
            self.avgdl = sum(self.doc_lengths.values()) / len(self.doc_lengths)
        
        self.logger.info(f"✅ Indexed {self.N:,} documents, {len(self.index):,} unique terms")
        self.logger.info(f"   Average document length: {self.avgdl:.0f} terms")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenise text into terms for BM25
        
        Rules:
        - Lowercase
        - Extract words 3+ characters
        - Remove stop words
        - Remove punctuation
        """
        # Lowercase
        text = text.lower()
        
        # Extract words (alphanumeric, 3+ chars)
        words = re.findall(r'\b[a-z0-9]{3,}\b', text)
        
        # Remove common stop words (expanded for legal documents)
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'with', 'was',
            'this', 'that', 'from', 'have', 'has', 'had', 'been', 'were',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'shall', 'his', 'her', 'their', 'our', 'your', 'its',
            'who', 'what', 'where', 'when', 'why', 'how', 'which', 'whom',
            'said', 'did', 'does', 'done', 'being', 'able', 'about', 'above',
            'after', 'all', 'also', 'any', 'because', 'before', 'between',
            'both', 'during', 'each', 'few', 'into', 'more', 'most', 'other',
            'out', 'over', 'same', 'some', 'such', 'than', 'then', 'there',
            'these', 'those', 'through', 'under', 'until', 'very', 'while'
        }
        
        words = [w for w in words if w not in stop_words]
        
        return words
    
    def search(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Search for documents using BM25 ranking
        
        Args:
            query: Search query (natural language)
            top_k: Number of documents to return (default 20)
            
        Returns:
            List of documents with scores, sorted by relevance
            [
                {
                    'doc_id': 'DOC_001',
                    'filename': 'document.pdf',
                    'score': 15.23,
                    'preview': 'Document preview...'
                },
                ...
            ]
        """
        if not self.index:
            self.logger.warning("Index not built, returning empty results")
            return []
        
        # Tokenise query
        query_terms = self._tokenize(query)
        
        if not query_terms:
            self.logger.warning(f"No valid terms in query: {query}")
            return []
        
        self.logger.info(f"Searching for: {query_terms}")
        
        # Calculate BM25 scores
        scores = self._calculate_bm25_scores(query_terms)
        
        # Sort by score (descending)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Take top K
        top_results = ranked[:top_k]
        
        # Build result objects
        results = []
        doc_lookup = {doc['doc_id']: doc for doc in self.documents}
        
        for doc_id, score in top_results:
            if doc_id in doc_lookup:
                doc = doc_lookup[doc_id]
                results.append({
                    'doc_id': doc_id,
                    'filename': doc.get('filename', 'Unknown'),
                    'category': doc.get('category', 'other'),
                    'score': round(score, 2),
                    'preview': (doc.get('preview', '') or doc.get('content', ''))[:200]
                })
        
        self.logger.info(f"Found {len(results)} relevant documents")
        
        return results
    
    def _calculate_bm25_scores(self, query_terms: List[str]) -> Dict[str, float]:
        """
        Calculate BM25 scores for all documents
        
        BM25 formula:
        score(D,Q) = Σ IDF(qi) · (f(qi,D) · (k1 + 1)) / (f(qi,D) + k1 · (1 - b + b · |D|/avgdl))
        
        Where:
        - D = document
        - Q = query
        - qi = query term i
        - f(qi,D) = frequency of qi in document D
        - |D| = length of document D
        - avgdl = average document length
        - k1, b = tuning parameters
        """
        scores = {}
        
        for term in query_terms:
            if term not in self.index:
                continue  # Term not in any document
            
            # Document frequency (how many docs contain this term)
            df = len(self.index[term])
            
            # Inverse document frequency (IDF)
            # Higher for rare terms, lower for common terms
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)
            
            # For each document containing this term
            for doc_id, tf in self.index[term].items():
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                
                # Document length normalisation
                doc_len = self.doc_lengths[doc_id]
                norm = 1 - self.b + self.b * (doc_len / self.avgdl)
                
                # BM25 score contribution from this term
                score_contribution = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * norm)
                
                scores[doc_id] += score_contribution
        
        return scores
    
    def get_doc_ids_only(self, query: str, top_k: int = 20) -> List[str]:
        """
        Convenience method: return just document IDs
        
        Args:
            query: Search query
            top_k: Number of documents to return
            
        Returns:
            List of document IDs: ['DOC_001', 'DOC_002', ...]
        """
        results = self.search(query, top_k)
        return [r['doc_id'] for r in results]
    
    def multi_term_search(self, terms: List[str], top_k: int = 20) -> List[Dict]:
        """
        Search using multiple specific terms (OR query)
        
        Args:
            terms: List of search terms
            top_k: Number of documents to return
            
        Returns:
            Ranked documents
        """
        # Combine terms into single query
        query = ' '.join(terms)
        return self.search(query, top_k)
    
    def get_statistics(self) -> Dict:
        """
        Get retrieval system statistics
        
        Returns:
            {
                'total_documents': int,
                'total_terms': int,
                'average_doc_length': float,
                'index_size_mb': float
            }
        """
        import sys
        
        # Estimate index size in memory
        index_size_bytes = sys.getsizeof(self.index)
        for term_dict in self.index.values():
            index_size_bytes += sys.getsizeof(term_dict)
        
        return {
            'total_documents': self.N,
            'total_terms': len(self.index),
            'average_doc_length': round(self.avgdl, 1),
            'index_size_mb': round(index_size_bytes / (1024 * 1024), 2)
        }
    
    def rebuild_index(self):
        """
        Rebuild index (call if documents are added to knowledge graph)
        """
        self.logger.info("Rebuilding document index...")
        self._build_index()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
Example usage in pass_executor.py:

from utils.document_retrieval import DocumentRetrieval

# In __init__:
self.retrieval_system = DocumentRetrieval(self.knowledge_graph, self.config)

# In Pass 3 investigations:
relevant_docs = self.retrieval_system.search(
    query="disclosure liabilities balance sheet",
    top_k=20
)

# Or just get doc IDs:
doc_ids = self.retrieval_system.get_doc_ids_only(
    query=investigation.topic,
    top_k=20
)

# Statistics:
stats = self.retrieval_system.get_statistics()
print(f"Index contains {stats['total_documents']} documents, {stats['total_terms']} terms")
"""