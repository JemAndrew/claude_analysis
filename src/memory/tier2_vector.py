#!/usr/bin/env python3
"""
Tier 2: Vector Store Manager
Semantic search across all 20,000+ documents using ChromaDB
British English throughout

Location: src/memory/tier2_vector.py
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("WARNING: chromadb not installed. Install with: pip install chromadb")


class VectorStoreManager:
    """
    Manages vector database for semantic search (Tier 2)
    
    Uses ChromaDB for:
        - Embedding all documents
        - Lightning-fast semantic similarity search
        - Automatic relevance ranking
        - Metadata filtering
    
    Benefits:
        - Find relevant docs in milliseconds
        - Semantic understanding (not just keyword matching)
        - Handles 20,000+ documents easily
        - Persistent storage
    """
    
    def __init__(self, store_path: Path, config):
        """
        Initialise Vector Store Manager
        
        Args:
            store_path: Where to store the vector database
            config: System configuration
        """
        self.store_path = Path(store_path)
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger('VectorStore')
        
        # Initialise ChromaDB
        self.client = None
        self.collection = None
        
        if CHROMADB_AVAILABLE:
            self._init_chromadb()
        else:
            self.logger.warning("ChromaDB not available - Tier 2 disabled")
    
    def _init_chromadb(self):
        """Initialise ChromaDB client and collection"""
        try:
            # Create persistent ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.store_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="lismore_documents",
                metadata={
                    "description": "Lismore v Process Holdings litigation documents",
                    "created": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"ChromaDB initialised: {self.collection.count()} documents indexed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialise ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_document(self, 
                    doc_path: Path, 
                    doc_metadata: Dict[str, Any],
                    text_content: str = None) -> bool:
        """
        Add document to vector store
        
        Args:
            doc_path: Path to document
            doc_metadata: Metadata (folder, importance, doc_type, etc.)
            text_content: Extracted text (will extract if None)
            
        Returns:
            True if added successfully
        """
        if not self.collection:
            return False
        
        try:
            # Generate unique ID
            doc_id = self._generate_doc_id(doc_path, doc_metadata)
            
            # Extract text if not provided
            if text_content is None:
                text_content = self._extract_text(doc_path)
            
            if not text_content or len(text_content) < 50:
                self.logger.warning(f"Insufficient text content for {doc_path.name}")
                return False
            
            # Prepare metadata for ChromaDB
            chroma_metadata = {
                'filename': doc_path.name,
                'folder': doc_metadata.get('folder', 'unknown'),
                'doc_type': doc_metadata.get('doc_type', 'unknown'),
                'importance': doc_metadata.get('importance', 5),
                'date_added': datetime.now().isoformat(),
                'size_bytes': doc_path.stat().st_size if doc_path.exists() else 0,
                'token_estimate': len(text_content) // 4
            }
            
            # Add to collection (ChromaDB handles embedding automatically)
            self.collection.add(
                documents=[text_content],
                metadatas=[chroma_metadata],
                ids=[doc_id]
            )
            
            self.logger.info(f"Added to vector store: {doc_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document {doc_path.name}: {e}")
            return False
    
    def add_documents_batch(self, 
                           documents: List[Tuple[Path, Dict, str]],
                           batch_size: int = 100) -> Dict[str, int]:
        """
        Add multiple documents in batches
        
        Args:
            documents: List of (doc_path, metadata, text_content) tuples
            batch_size: Number of docs to process at once
            
        Returns:
            Dict with success/failure counts
        """
        if not self.collection:
            return {'success': 0, 'failed': len(documents)}
        
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            doc_ids = []
            texts = []
            metadatas = []
            
            for doc_path, doc_metadata, text_content in batch:
                # Skip if insufficient content
                if not text_content or len(text_content) < 50:
                    results['skipped'] += 1
                    continue
                
                doc_id = self._generate_doc_id(doc_path, doc_metadata)
                
                chroma_metadata = {
                    'filename': doc_path.name,
                    'folder': doc_metadata.get('folder', 'unknown'),
                    'doc_type': doc_metadata.get('doc_type', 'unknown'),
                    'importance': doc_metadata.get('importance', 5),
                    'date_added': datetime.now().isoformat(),
                    'token_estimate': len(text_content) // 4
                }
                
                doc_ids.append(doc_id)
                texts.append(text_content)
                metadatas.append(chroma_metadata)
            
            try:
                if doc_ids:
                    self.collection.add(
                        documents=texts,
                        metadatas=metadatas,
                        ids=doc_ids
                    )
                    results['success'] += len(doc_ids)
                    self.logger.info(f"Batch added: {len(doc_ids)} documents")
            except Exception as e:
                self.logger.error(f"Batch failed: {e}")
                results['failed'] += len(batch)
        
        return results
    
    def semantic_search(self,
                       query_text: str,
                       top_k: int = 20,
                       filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search
        
        Args:
            query_text: The search query
            top_k: Number of results to return
            filters: Metadata filters (folder, doc_type, importance, etc.)
            
        Returns:
            List of matching documents with relevance scores
        """
        if not self.collection:
            return []
        
        try:
            # Build where clause for filters
            where_clause = self._build_where_clause(filters)
            
            # Perform query
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        'doc_id': doc_id,
                        'filename': results['metadatas'][0][i]['filename'],
                        'folder': results['metadatas'][0][i]['folder'],
                        'doc_type': results['metadatas'][0][i]['doc_type'],
                        'importance': results['metadatas'][0][i]['importance'],
                        'distance': results['distances'][0][i],
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'text_snippet': results['documents'][0][i][:500],  # First 500 chars
                        'tokens': results['metadatas'][0][i].get('token_estimate', 0)
                    })
            
            self.logger.info(f"Semantic search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []
    
    def find_similar_documents(self,
                              doc_id: str,
                              top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find documents similar to a specific document
        
        Args:
            doc_id: ID of the reference document
            top_k: Number of similar docs to return
            
        Returns:
            List of similar documents
        """
        if not self.collection:
            return []
        
        try:
            # Get the document
            doc = self.collection.get(ids=[doc_id])
            
            if not doc['documents']:
                return []
            
            # Search using the document's content
            return self.semantic_search(
                query_text=doc['documents'][0],
                top_k=top_k + 1  # +1 because it will include itself
            )[1:]  # Skip first result (itself)
            
        except Exception as e:
            self.logger.error(f"Similar document search failed: {e}")
            return []
    
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> Optional[Dict]:
        """Build ChromaDB where clause from filters"""
        if not filters:
            return None
        
        where = {}
        
        # Folder filter
        if filters.get('folder'):
            where['folder'] = filters['folder']
        
        # Document type filter
        if filters.get('document_types'):
            where['doc_type'] = {"$in": filters['document_types']}
        
        # Importance threshold
        if filters.get('min_importance'):
            where['importance'] = {"$gte": filters['min_importance']}
        
        # Time range (if dates are in metadata)
        if filters.get('time_range'):
            start_date, end_date = filters['time_range']
            where['date_added'] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        return where if where else None
    
    def _extract_text(self, doc_path: Path) -> str:
        """
        Extract text from document
        
        This is a placeholder - integrate with your existing text extraction
        """
        # TODO: Integrate with your existing PDF/DOCX extraction
        # For now, return placeholder
        return f"[Text extraction needed for {doc_path.name}]"
    
    def _generate_doc_id(self, doc_path: Path, doc_metadata: Dict) -> str:
        """Generate unique document ID"""
        # Combine path and folder for uniqueness
        unique_str = f"{doc_metadata.get('folder', '')}/{doc_path.name}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document by ID"""
        if not self.collection:
            return None
        
        try:
            result = self.collection.get(ids=[doc_id])
            
            if not result['ids']:
                return None
            
            return {
                'doc_id': result['ids'][0],
                'text': result['documents'][0],
                'metadata': result['metadatas'][0]
            }
        except Exception as e:
            self.logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not self.collection:
            return {'error': 'Collection not initialised'}
        
        try:
            count = self.collection.count()
            
            # Get sample to analyse
            sample = self.collection.get(limit=min(100, count))
            
            # Calculate statistics
            total_tokens = sum(
                m.get('token_estimate', 0) 
                for m in sample['metadatas']
            ) if sample['metadatas'] else 0
            
            avg_tokens = total_tokens / len(sample['metadatas']) if sample['metadatas'] else 0
            
            # Estimate total tokens
            estimated_total_tokens = int(avg_tokens * count)
            
            return {
                'total_documents': count,
                'estimated_total_tokens': estimated_total_tokens,
                'avg_tokens_per_doc': int(avg_tokens),
                'storage_path': str(self.store_path),
                'collection_name': self.collection.name
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {'error': str(e)}
    
    def optimise_indices(self):
        """Optimise vector indices for better performance"""
        if not self.collection:
            return
        
        # ChromaDB handles optimisation automatically
        # But we can trigger a peek to ensure indices are loaded
        try:
            self.collection.peek()
            self.logger.info("Vector store indices optimised")
        except Exception as e:
            self.logger.error(f"Optimisation failed: {e}")
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store"""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=[doc_id])
            self.logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete {doc_id}: {e}")
            return False
    
    def reset_collection(self, confirm: bool = False):
        """
        Reset the entire collection (DANGEROUS!)
        
        Args:
            confirm: Must be True to actually reset
        """
        if not confirm:
            raise ValueError("Must confirm=True to reset collection")
        
        if self.client:
            self.client.delete_collection(name="lismore_documents")
            self.collection = self.client.create_collection(
                name="lismore_documents",
                metadata={
                    "description": "Lismore v Process Holdings litigation documents",
                    "created": datetime.now().isoformat(),
                    "reset": True
                }
            )
            self.logger.warning("Collection reset!")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 2 status"""
        if not self.collection:
            return {
                'tier': 2,
                'name': 'Vector Store',
                'active': False,
                'error': 'ChromaDB not available'
            }
        
        stats = self.get_collection_stats()
        
        return {
            'tier': 2,
            'name': 'Vector Store (ChromaDB)',
            'active': True,
            'documents': stats.get('total_documents', 0),
            'estimated_tokens': stats.get('estimated_total_tokens', 0),
            'storage_path': str(self.store_path)
        }