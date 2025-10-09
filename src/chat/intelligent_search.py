#!/usr/bin/env python3
"""
Intelligent Progressive Search with Full PDF Loading
Searches truncated text first, loads originals when needed
British English throughout
"""

from pathlib import Path
from typing import Dict, List, Tuple
import time


class IntelligentSearch:
    """
    Smart search that progressively loads deeper content
    
    Strategy:
    1. Fast search on truncated database text
    2. Detect high-value truncated documents
    3. Load full PDFs for critical matches
    4. Cache full text for future queries
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.kg = orchestrator.knowledge_graph
        self.document_loader = orchestrator.document_loader
        
        # Cache for loaded full documents
        self.full_doc_cache = {}  # {doc_id: full_text}
        
        # Stats
        self.stats = {
            'fast_searches': 0,
            'full_pdf_loads': 0,
            'cache_hits': 0,
            'time_saved_seconds': 0
        }
    
    def search(self, query: str, top_k: int = 20, 
               allow_deep_search: bool = True) -> List[Dict]:
        """
        Intelligent progressive search
        
        Args:
            query: Search query
            top_k: Number of results
            allow_deep_search: Whether to load full PDFs
            
        Returns:
            List of documents with content (may include full PDFs)
        """
        start_time = time.time()
        
        print(f"🔍 Searching: '{query}'")
        
        # ===============================================================
        # TIER 1: Fast Database Search
        # ===============================================================
        print("   ├─ Tier 1: Database search...", end='', flush=True)
        
        # BM25 search on truncated text
        bm25_results = self.orchestrator.retrieve_documents(query, top_k=top_k)
        
        # Vector search on truncated text
        vector_results = self.orchestrator.semantic_search(query, top_k=top_k)
        
        # Merge and rank
        merged = self._merge_and_rank(bm25_results, vector_results, query)
        
        tier1_time = time.time() - start_time
        print(f" ✅ {len(merged)} results ({tier1_time:.2f}s)")
        
        self.stats['fast_searches'] += 1
        
        if not allow_deep_search:
            return merged[:top_k]
        
        # ===============================================================
        # TIER 2: Smart Detection - Which docs need full load?
        # ===============================================================
        print("   ├─ Tier 2: Checking for truncated docs...", end='', flush=True)
        
        docs_to_load = []
        for i, doc in enumerate(merged[:top_k]):
            doc['rank'] = i + 1
            
            if self._should_load_full_pdf(doc, query):
                docs_to_load.append(doc)
        
        if not docs_to_load:
            print(" ✅ None need full load")
            return merged[:top_k]
        
        print(f" ⚠️  {len(docs_to_load)} docs truncated")
        
        # ===============================================================
        # TIER 3: Deep PDF Loading
        # ===============================================================
        print(f"   └─ Tier 3: Loading full PDFs...")
        
        for doc in docs_to_load:
            full_text = self._load_full_pdf_smart(doc)
            if full_text:
                doc['content'] = full_text
                doc['full_pdf_loaded'] = True
                print(f"      ✅ {doc['filename']}: {len(full_text):,} chars")
        
        total_time = time.time() - start_time
        print(f"\n   📊 Total time: {total_time:.2f}s")
        print(f"      Fast search: {tier1_time:.2f}s")
        print(f"      Full PDFs: {total_time - tier1_time:.2f}s")
        
        return merged[:top_k]
    
    def _should_load_full_pdf(self, doc: Dict, query: str) -> bool:
        """Decide if document needs full PDF loading"""
        
        # Already have full text?
        if not doc.get('metadata', {}).get('truncated'):
            return False
        
        # Check if in cache
        if doc['doc_id'] in self.full_doc_cache:
            return False  # Will use cache
        
        # Is it highly relevant?
        relevance_score = doc.get('score', 0)
        if relevance_score < 0.7:
            return False
        
        # Query indicators for depth
        deep_indicators = [
            'full', 'complete', 'all', 'everything',
            'comprehensive', 'detailed', 'entire',
            'show me', 'read', 'analyze', 'analyse'
        ]
        needs_depth = any(term in query.lower() for term in deep_indicators)
        
        # Top 5 AND (high score OR needs depth)
        if doc['rank'] <= 5 and (relevance_score > 0.8 or needs_depth):
            return True
        
        # Top 3 always load if truncated
        if doc['rank'] <= 3:
            return True
        
        return False
    
    def _load_full_pdf_smart(self, doc: Dict) -> str:
        """Load full PDF with caching"""
        
        doc_id = doc['doc_id']
        
        # Check cache first
        if doc_id in self.full_doc_cache:
            self.stats['cache_hits'] += 1
            return self.full_doc_cache[doc_id]
        
        # Find original file
        original_path = self._find_original_file(doc)
        
        if not original_path or not original_path.exists():
            print(f"      ⚠️  Original file not found: {doc['filename']}")
            return doc.get('content', '')
        
        # Load full PDF (NO LIMITS!)
        try:
            # Temporarily remove limits
            old_max_chars = self.document_loader.MAX_CHARS_EXTRACT
            old_max_pages = self.document_loader.MAX_PDF_PAGES
            
            self.document_loader.MAX_CHARS_EXTRACT = None  # No limit!
            self.document_loader.MAX_PDF_PAGES = None      # No limit!
            
            # Load full document
            full_doc = self.document_loader.load_document(
                original_path, 
                folder_metadata=doc.get('folder_metadata', {})
            )
            
            # Restore limits
            self.document_loader.MAX_CHARS_EXTRACT = old_max_chars
            self.document_loader.MAX_PDF_PAGES = old_max_pages
            
            full_text = full_doc['content']
            
            # Cache it
            self.full_doc_cache[doc_id] = full_text
            
            self.stats['full_pdf_loads'] += 1
            
            return full_text
            
        except Exception as e:
            print(f"      ❌ Error loading full PDF: {e}")
            return doc.get('content', '')
    
    def _find_original_file(self, doc: Dict) -> Path:
        """Find original PDF file from document metadata"""
        
        # Method 1: Check if filepath stored in metadata
        if 'filepath' in doc.get('metadata', {}):
            return Path(doc['metadata']['filepath'])
        
        # Method 2: Reconstruct from folder + filename
        folder = doc.get('folder', '')
        filename = doc.get('filename', '')
        
        if folder and filename:
            # Root folder from config
            root = self.orchestrator.config.source_root
            potential_path = root / folder / filename
            
            if potential_path.exists():
                return potential_path
        
        # Method 3: Search for it
        root = self.orchestrator.config.source_root
        for file in root.rglob(filename):
            return file
        
        return None
    
    def _merge_and_rank(self, bm25_results: List[Dict], 
                       vector_results: List[Dict], 
                       query: str) -> List[Dict]:
        """Merge BM25 and vector results with intelligent ranking"""
        
        # Create scoring dict
        scores = {}
        
        # BM25 scores (keyword relevance)
        for i, doc in enumerate(bm25_results):
            doc_id = doc['doc_id']
            bm25_score = (len(bm25_results) - i) / len(bm25_results)
            scores[doc_id] = {
                'bm25': bm25_score,
                'vector': 0,
                'doc': doc
            }
        
        # Vector scores (semantic relevance)
        for i, doc in enumerate(vector_results):
            doc_id = doc['doc_id']
            vector_score = (len(vector_results) - i) / len(vector_results)
            
            if doc_id in scores:
                scores[doc_id]['vector'] = vector_score
            else:
                scores[doc_id] = {
                    'bm25': 0,
                    'vector': vector_score,
                    'doc': doc
                }
        
        # Calculate combined score
        ranked = []
        for doc_id, data in scores.items():
            # Weighted combination (favor BM25 for litigation)
            combined = (data['bm25'] * 0.6) + (data['vector'] * 0.4)
            
            doc = data['doc']
            doc['score'] = combined
            doc['bm25_score'] = data['bm25']
            doc['vector_score'] = data['vector']
            
            ranked.append(doc)
        
        # Sort by combined score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        return ranked
    
    def get_stats(self) -> Dict:
        """Get search statistics"""
        return {
            **self.stats,
            'cache_size': len(self.full_doc_cache),
            'cached_docs': list(self.full_doc_cache.keys())
        }
    
    def clear_cache(self):
        """Clear full document cache"""
        self.full_doc_cache.clear()
        print("✅ Full PDF cache cleared")