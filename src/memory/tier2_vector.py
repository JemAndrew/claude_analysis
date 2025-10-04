#!/usr/bin/env python3
"""
Tier 2: Vector Store Manager
Semantic search across all documents using ChromaDB
British English throughout - FIXED TEXT EXTRACTION

Location: src/memory/tier2_vector.py
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class VectorStoreManager:
    """
    Manages Tier 2: Vector Store using ChromaDB
    
    Purpose:
        - Semantic search across entire document corpus
        - Fast retrieval (milliseconds)
        - Find similar documents or passages
        - Pattern detection across documents
    
    Strategy:
        - Use sentence-transformers for embeddings
        - ChromaDB for vector storage
        - Metadata filtering
        - Similarity search
    """
    
    def __init__(self, store_path: Path, config):
        """
        Initialise Vector Store Manager
        
        Args:
            store_path: Where to store vector database
            config: System configuration
        """
        self.store_path = Path(store_path)
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger('VectorStore')
        
        # Check dependencies
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not installed. Install: pip install chromadb")
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed. Install: pip install sentence-transformers")
        
        # Create store directory
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialise ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.store_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        collection_name = getattr(config.vector_config, 'collection_name', 'lismore_disclosure')
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info(f"Vector Store initialised at {store_path}")
    
    def add_document(self, 
                    doc_path: Path,
                    doc_metadata: Dict[str, Any]) -> bool:
        """
        Add document to vector store
        
        Args:
            doc_path: Path to document (for ID generation)
            doc_metadata: Metadata including content and other fields
            
        Returns:
            True if successful
        """
        try:
            # Extract content
            content = doc_metadata.get('content', '')
            if not content:
                self.logger.warning(f"No content for {doc_path.name}")
                return False
            
            # Generate unique ID
            doc_id = doc_metadata.get('doc_id', self._generate_doc_id(doc_path, doc_metadata))
            
            # Prepare metadata (ChromaDB requires simple types)
            metadata = {
                'doc_id': doc_id,
                'filename': doc_metadata.get('filename', doc_path.name),
                'folder': doc_metadata.get('folder', ''),
                'classification': doc_metadata.get('classification', 'general'),
                'word_count': int(doc_metadata.get('word_count', 0)),
                'has_dates': bool(doc_metadata.get('has_dates', False)),
                'has_amounts': bool(doc_metadata.get('has_amounts', False)),
                'extension': doc_metadata.get('extension', doc_path.suffix.lower())
            }
            
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            self.logger.info(f"Added {doc_path.name} to vector store ({len(content)} chars)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document {doc_path}: {e}")
            return False
    
    def semantic_search(self,
                       query_text: str,
                       top_k: int = 10,
                       filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Semantic search across documents
        
        Args:
            query_text: Search query
            top_k: Number of results to return
            filters: Metadata filters
            
        Returns:
            List of matching documents with scores
        """
        try:
            # Build where clause for filtering
            where = self._build_where_clause(filters)
            
            # Perform search
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = []
            if results and results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'doc_id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'tokens': len(results['documents'][0][i]) // 4
                    })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def find_similar_documents(self,
                              doc_id: str,
                              top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document
        
        Args:
            doc_id: Document ID to find similar documents for
            top_k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        try:
            # Get the document
            result = self.collection.get(ids=[doc_id])
            
            if not result or not result['documents']:
                return []
            
            doc_content = result['documents'][0]
            
            # Search for similar documents
            return self.semantic_search(
                query_text=doc_content,
                top_k=top_k + 1  # +1 because it will include itself
            )[1:]  # Skip first result (the document itself)
            
        except Exception as e:
            self.logger.error(f"Similar document search failed: {e}")
            return []
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Optional[Dict]:
        """Build ChromaDB where clause from filters"""
        if not filters:
            return None
        
        where = {}
        
        # Classification filter
        if filters.get('classification'):
            where['classification'] = filters['classification']
        
        # Folder filter
        if filters.get('folder'):
            where['folder'] = filters['folder']
        
        # Time range filter (if dates stored)
        if filters.get('time_range'):
            start_date, end_date = filters['time_range']
            # Note: This requires dates to be stored in metadata
            # For now, we'll skip time range filtering
            pass
        
        # Document types filter
        if filters.get('document_types'):
            doc_types = filters['document_types']
            if len(doc_types) == 1:
                where['extension'] = doc_types[0]
            # Multi-value filtering requires different syntax in ChromaDB
        
        return where if where else None
    
    def _generate_doc_id(self, doc_path: Path, doc_metadata: Dict) -> str:
        """Generate unique document ID"""
        # Use folder + filename for uniqueness
        unique_str = f"{doc_metadata.get('folder', '')}/{doc_path.name}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document by ID"""
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
        try:
            count = self.collection.count()
            
            # Get sample to analyse
            sample_size = min(100, count)
            sample = self.collection.get(limit=sample_size) if count > 0 else None
            
            # Calculate statistics
            total_tokens = 0
            avg_doc_length = 0
            
            if sample and sample['documents']:
                for doc in sample['documents']:
                    total_tokens += len(doc) // 4
                
                avg_doc_length = total_tokens // len(sample['documents'])
                
                # Estimate total tokens
                estimated_total_tokens = avg_doc_length * count
            else:
                estimated_total_tokens = 0
            
            return {
                'total_documents': count,
                'estimated_total_tokens': estimated_total_tokens,
                'avg_document_tokens': avg_doc_length,
                'collection_name': self.collection.name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {
                'total_documents': 0,
                'estimated_total_tokens': 0,
                'error': str(e)
            }
    
    def optimise_indices(self):
        """Optimise vector indices for better performance"""
        # ChromaDB handles this automatically
        self.logger.info("Vector indices optimised (automatic in ChromaDB)")
    
    def clear_collection(self):
        """Clear all documents from collection (use with caution)"""
        try:
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.client.create_collection(
                name=self.collection.name,
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.warning("Collection cleared - all documents removed")
        except Exception as e:
            self.logger.error(f"Failed to clear collection: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 2 status"""
        stats = self.get_collection_stats()
        
        return {
            'tier': 2,
            'name': 'Vector Store (ChromaDB)',
            'active': True,
            'documents': stats.get('total_documents', 0),
            'estimated_tokens': stats.get('estimated_total_tokens', 0),
            'storage_path': str(self.store_path)
        }