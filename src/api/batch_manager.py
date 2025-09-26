#!/usr/bin/env python3
"""
Intelligent Batch Manager for Document Processing
Semantic clustering and priority-based batching
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
from datetime import datetime
import numpy as np
from collections import defaultdict


class BatchManager:
    """Manages intelligent document batching for API calls"""
    
    def __init__(self, config):
        self.config = config
        self.batch_history = []
        
    def create_semantic_batches(self,
                               documents: List[Dict],
                               strategy: str = 'semantic_clustering') -> List[List[Dict]]:
        """
        Create document batches using specified strategy
        """
        
        if strategy == 'semantic_clustering':
            return self._semantic_clustering_batch(documents)
        elif strategy == 'chronological':
            return self._chronological_batch(documents)
        elif strategy == 'entity_focused':
            return self._entity_focused_batch(documents)
        elif strategy == 'priority_weighted':
            return self._priority_weighted_batch(documents)
        else:
            return self._simple_batch(documents)
    
    def _semantic_clustering_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Batch documents by semantic similarity
        Groups related documents together for better pattern recognition
        """
        
        # Create document fingerprints
        doc_fingerprints = []
        for doc in documents:
            fingerprint = self._create_semantic_fingerprint(doc)
            doc_fingerprints.append((fingerprint, doc))
        
        # Cluster similar documents
        clusters = defaultdict(list)
        
        for fingerprint, doc in doc_fingerprints:
            # Find best matching cluster
            best_cluster = None
            best_similarity = 0
            
            for cluster_id, cluster_docs in clusters.items():
                if cluster_docs:
                    cluster_fingerprint = cluster_docs[0][0]  # Use first doc as representative
                    similarity = self._calculate_similarity(fingerprint, cluster_fingerprint)
                    
                    if similarity > best_similarity and similarity > 0.3:  # Threshold
                        best_similarity = similarity
                        best_cluster = cluster_id
            
            if best_cluster is not None:
                clusters[best_cluster].append((fingerprint, doc))
            else:
                # Create new cluster
                new_cluster_id = len(clusters)
                clusters[new_cluster_id] = [(fingerprint, doc)]
        
        # Convert clusters to batches respecting size limits
        batches = []
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        for cluster_docs in clusters.values():
            current_batch = []
            current_tokens = 0
            
            for _, doc in cluster_docs:
                doc_tokens = len(doc.get('content', '')) // 4
                
                if current_tokens + doc_tokens <= max_batch_tokens:
                    current_batch.append(doc)
                    current_tokens += doc_tokens
                else:
                    if current_batch:
                        batches.append(current_batch)
                    current_batch = [doc]
                    current_tokens = doc_tokens
            
            if current_batch:
                batches.append(current_batch)
        
        self._record_batch_creation('semantic_clustering', batches)
        return batches
    
    def _chronological_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Batch documents chronologically for timeline analysis
        """
        
        # Extract dates and sort
        dated_docs = []
        undated_docs = []
        
        for doc in documents:
            date = self._extract_date(doc)
            if date:
                dated_docs.append((date, doc))
            else:
                undated_docs.append(doc)
        
        # Sort by date
        dated_docs.sort(key=lambda x: x[0])
        
        # Create batches maintaining chronological order
        batches = []
        current_batch = []
        current_tokens = 0
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        for date, doc in dated_docs:
            doc_tokens = len(doc.get('content', '')) // 4
            
            if current_tokens + doc_tokens <= max_batch_tokens:
                current_batch.append(doc)
                current_tokens += doc_tokens
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
        
        # Add undated documents to last batch or new batch
        for doc in undated_docs:
            doc_tokens = len(doc.get('content', '')) // 4
            
            if current_tokens + doc_tokens <= max_batch_tokens:
                current_batch.append(doc)
                current_tokens += doc_tokens
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        self._record_batch_creation('chronological', batches)
        return batches
    
    def _entity_focused_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Batch documents by entity presence for relationship analysis
        """
        
        # Extract entities from documents
        entity_docs = defaultdict(list)
        
        for doc in documents:
            entities = self._extract_entities(doc)
            
            if entities:
                # Add to most prominent entity's batch
                primary_entity = entities[0]
                entity_docs[primary_entity].append(doc)
            else:
                entity_docs['unknown'].append(doc)
        
        # Convert entity groups to batches
        batches = []
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        for entity, docs in entity_docs.items():
            current_batch = []
            current_tokens = 0
            
            for doc in docs:
                doc_tokens = len(doc.get('content', '')) // 4
                
                if current_tokens + doc_tokens <= max_batch_tokens:
                    current_batch.append(doc)
                    current_tokens += doc_tokens
                else:
                    if current_batch:
                        batches.append(current_batch)
                    current_batch = [doc]
                    current_tokens = doc_tokens
            
            if current_batch:
                batches.append(current_batch)
        
        self._record_batch_creation('entity_focused', batches)
        return batches
    
    def _priority_weighted_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Batch documents by priority scores
        High-priority documents get more context space
        """
        
        # Score documents
        scored_docs = []
        for doc in documents:
            score = self._calculate_priority_score(doc)
            scored_docs.append((score, doc))
        
        # Sort by priority
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Create batches with high-priority documents getting more space
        batches = []
        current_batch = []
        current_tokens = 0
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        for score, doc in scored_docs:
            doc_tokens = len(doc.get('content', '')) // 4
            
            # High-priority documents get their own batch if large
            if score > 0.8 and doc_tokens > max_batch_tokens * 0.5:
                if current_batch:
                    batches.append(current_batch)
                batches.append([doc])
                current_batch = []
                current_tokens = 0
            elif current_tokens + doc_tokens <= max_batch_tokens:
                current_batch.append(doc)
                current_tokens += doc_tokens
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        self._record_batch_creation('priority_weighted', batches)
        return batches
    
    def _simple_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Simple batching by size limits
        Fallback strategy
        """
        
        batches = []
        current_batch = []
        current_tokens = 0
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        for doc in documents:
            doc_tokens = len(doc.get('content', '')) // 4
            
            if current_tokens + doc_tokens <= max_batch_tokens:
                current_batch.append(doc)
                current_tokens += doc_tokens
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        self._record_batch_creation('simple', batches)
        return batches
    
    def _create_semantic_fingerprint(self, document: Dict) -> Dict:
        """
        Create semantic fingerprint for document clustering
        """
        
        content = document.get('content', '').lower()
        
        # Extract key features
        fingerprint = {
            'length': len(content),
            'entities': set(),
            'keywords': set(),
            'doc_type': document.get('metadata', {}).get('classification', 'unknown'),
            'has_numbers': bool(any(char.isdigit() for char in content)),
            'has_dates': bool(self._extract_date(document))
        }
        
        # Extract entities (simple approach)
        import re
        entities = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', document.get('content', ''))
        fingerprint['entities'] = set(entities[:10])
        
        # Extract keywords (simple approach)
        important_words = ['breach', 'contract', 'payment', 'agreement', 'liability',
                          'damages', 'conspiracy', 'fraud', 'misrepresentation']
        for word in important_words:
            if word in content:
                fingerprint['keywords'].add(word)
        
        return fingerprint
    
    def _calculate_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """
        Calculate similarity between two document fingerprints
        """
        
        similarity = 0.0
        
        # Entity overlap
        if fp1['entities'] and fp2['entities']:
            entity_overlap = len(fp1['entities'] & fp2['entities'])
            entity_union = len(fp1['entities'] | fp2['entities'])
            if entity_union > 0:
                similarity += 0.4 * (entity_overlap / entity_union)
        
        # Keyword overlap
        if fp1['keywords'] and fp2['keywords']:
            keyword_overlap = len(fp1['keywords'] & fp2['keywords'])
            keyword_union = len(fp1['keywords'] | fp2['keywords'])
            if keyword_union > 0:
                similarity += 0.3 * (keyword_overlap / keyword_union)
        
        # Document type match
        if fp1['doc_type'] == fp2['doc_type']:
            similarity += 0.2
        
        # Similar features
        if fp1['has_numbers'] == fp2['has_numbers']:
            similarity += 0.05
        if fp1['has_dates'] == fp2['has_dates']:
            similarity += 0.05
        
        return similarity
    
    def _extract_date(self, document: Dict) -> Optional[str]:
        """
        Extract primary date from document
        """
        
        # Check metadata first
        if document.get('metadata', {}).get('date'):
            return document['metadata']['date']
        
        # Simple date extraction from content
        import re
        content = document.get('content', '')
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        dates = re.findall(date_pattern, content)
        
        return dates[0] if dates else None
    
    def _extract_entities(self, document: Dict) -> List[str]:
        """
        Extract key entities from document
        """
        
        # Check metadata first
        if document.get('metadata', {}).get('entities'):
            return document['metadata']['entities'].get('people', [])[:5]
        
        # Simple entity extraction
        import re
        content = document.get('content', '')
        entities = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)
        
        # Count frequency
        entity_counts = defaultdict(int)
        for entity in entities:
            entity_counts[entity] += 1
        
        # Return most frequent entities
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        return [entity for entity, count in sorted_entities[:5]]
    
    def _calculate_priority_score(self, document: Dict) -> float:
        """
        Calculate document priority score
        """
        
        score = 0.0
        content_lower = document.get('content', '').lower()
        
        # Critical markers
        if 'nuclear' in content_lower or 'smoking gun' in content_lower:
            score += 1.0
        if 'critical' in content_lower:
            score += 0.8
        if 'suspicious' in content_lower or 'anomaly' in content_lower:
            score += 0.6
        
        # Document type priority
        doc_type = document.get('metadata', {}).get('classification', '')
        if doc_type in ['contract', 'agreement']:
            score += 0.5
        elif doc_type in ['email', 'correspondence']:
            score += 0.3
        
        # Entity presence
        entities = self._extract_entities(document)
        score += min(0.5, len(entities) * 0.1)
        
        return min(1.0, score)
    
    def _record_batch_creation(self, strategy: str, batches: List[List[Dict]]):
        """
        Record batch creation for analysis
        """
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'batch_count': len(batches),
            'document_count': sum(len(batch) for batch in batches),
            'avg_docs_per_batch': sum(len(batch) for batch in batches) / max(1, len(batches)),
            'batch_sizes': [len(batch) for batch in batches]
        }
        
        self.batch_history.append(record)
        
        # Keep only last 50 records
        if len(self.batch_history) > 50:
            self.batch_history = self.batch_history[-50:]
    
    def get_batch_statistics(self) -> Dict:
        """
        Get batching statistics
        """
        
        if not self.batch_history:
            return {'message': 'No batches created yet'}
        
        strategy_counts = defaultdict(int)
        total_docs = 0
        total_batches = 0
        
        for record in self.batch_history:
            strategy_counts[record['strategy']] += 1
            total_docs += record['document_count']
            total_batches += record['batch_count']
        
        return {
            'total_batch_operations': len(self.batch_history),
            'total_documents_processed': total_docs,
            'total_batches_created': total_batches,
            'avg_documents_per_batch': total_docs / max(1, total_batches),
            'strategies_used': dict(strategy_counts),
            'last_batch': self.batch_history[-1] if self.batch_history else None
        }