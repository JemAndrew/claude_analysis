#!/usr/bin/env python3
"""
Batch Manager for Intelligent Document Batching
Handles semantic clustering and priority-based document grouping
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import re


class BatchManager:
    """Manages intelligent document batching for optimal API utilisation"""
    
    def __init__(self, config):
        self.config = config
        self.optimal_size = config.token_config.get('optimal_batch_size', 140000)
        self.max_size = config.token_config.get('max_input_tokens', 150000)
        self.batch_history = []
    
    def create_semantic_batches(self, 
                               documents: List[Dict], 
                               strategy: str = 'semantic_clustering') -> List[List[Dict]]:
        """
        Create document batches using specified strategy
        
        Args:
            documents: List of document dictionaries
            strategy: Batching strategy (semantic_clustering, chronological, 
                     priority_weighted, entity_focused)
        
        Returns:
            List of document batches
        """
        
        if not documents:
            return []
        
        if strategy == 'chronological':
            return self._batch_chronologically(documents)
        elif strategy == 'priority_weighted':
            return self._batch_by_priority(documents)
        elif strategy == 'entity_focused':
            return self._batch_by_entities(documents)
        else:  # Default: semantic_clustering
            return self._batch_semantically(documents)
    
    def create_investigation_batches(self,
                                   documents: List[Dict],
                                   investigation_type: str,
                                   investigation_data: Dict) -> List[List[Dict]]:
        """
        Create batches optimised for specific investigation
        
        Args:
            documents: List of documents
            investigation_type: Type of investigation
            investigation_data: Investigation trigger data
        
        Returns:
            List of relevant document batches
        """
        
        # Score documents by investigation relevance
        scored_docs = []
        for doc in documents:
            score = self._calculate_investigation_relevance(
                doc, 
                investigation_type, 
                investigation_data
            )
            scored_docs.append((score, doc))
        
        # Sort by relevance
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Determine document limit based on investigation type
        max_docs = {
            'contradiction': 30,
            'financial_anomaly': 20,
            'timeline_impossibility': 40,
            'entity': 25
        }.get(investigation_type, 25)
        
        # Take top relevant documents
        relevant_docs = [doc for score, doc in scored_docs[:max_docs] if score > 0]
        
        # Create token-limited batches
        batches = self._create_token_limited_batches(relevant_docs)
        
        self._record_batch_creation(f'investigation_{investigation_type}', batches)
        
        return batches
    
    # ============================================================
    # BATCHING STRATEGIES
    # ============================================================
    
    def _batch_semantically(self, documents: List[Dict]) -> List[List[Dict]]:
        """Batch documents by semantic similarity"""
        
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
                    cluster_fingerprint = cluster_docs[0][0]
                    similarity = self._calculate_similarity(fingerprint, cluster_fingerprint)
                    
                    if similarity > best_similarity and similarity > 0.3:
                        best_similarity = similarity
                        best_cluster = cluster_id
            
            if best_cluster is not None:
                clusters[best_cluster].append((fingerprint, doc))
            else:
                # Create new cluster
                new_cluster_id = len(clusters)
                clusters[new_cluster_id] = [(fingerprint, doc)]
        
        # Convert clusters to token-limited batches
        batches = []
        for cluster_docs in clusters.values():
            current_batch = []
            current_tokens = 0
            
            for _, doc in cluster_docs:
                doc_tokens = self._estimate_tokens(doc)
                
                if current_tokens + doc_tokens <= self.optimal_size:
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
    
    def _batch_chronologically(self, documents: List[Dict]) -> List[List[Dict]]:
        """Batch documents in chronological order"""
        
        # Extract dates and sort
        dated_docs = []
        undated_docs = []
        
        for doc in documents:
            dates = doc.get('metadata', {}).get('dates_found', [])
            if dates:
                dated_docs.append((dates[0], doc))
            else:
                undated_docs.append(doc)
        
        # Sort by date
        dated_docs.sort(key=lambda x: x[0])
        
        # Create batches maintaining chronological order
        batches = []
        current_batch = []
        current_tokens = 0
        
        for date, doc in dated_docs:
            doc_tokens = self._estimate_tokens(doc)
            
            if current_tokens + doc_tokens <= self.optimal_size:
                current_batch.append(doc)
                current_tokens += doc_tokens
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
        
        # Add undated documents
        for doc in undated_docs:
            doc_tokens = self._estimate_tokens(doc)
            
            if current_tokens + doc_tokens <= self.optimal_size:
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
    
    def _batch_by_priority(self, documents: List[Dict]) -> List[List[Dict]]:
        """Batch documents by priority scores"""
        
        # Score documents
        scored_docs = []
        for doc in documents:
            score = self._calculate_priority_score(doc)
            scored_docs.append((score, doc))
        
        # Sort by priority (highest first)
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Create batches with high-priority documents getting more space
        batches = []
        current_batch = []
        current_tokens = 0
        
        for score, doc in scored_docs:
            doc_tokens = self._estimate_tokens(doc)
            
            # High-priority documents get their own batch if large
            if score > 0.8 and doc_tokens > self.optimal_size * 0.5:
                if current_batch:
                    batches.append(current_batch)
                batches.append([doc])
                current_batch = []
                current_tokens = 0
            elif current_tokens + doc_tokens <= self.optimal_size:
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
    
    def _batch_by_entities(self, documents: List[Dict]) -> List[List[Dict]]:
        """Batch documents by entity presence"""
        
        # Extract entities from documents
        entity_docs = defaultdict(list)
        
        for doc in documents:
            entities = doc.get('metadata', {}).get('entities', {})
            
            if entities:
                all_entities = (
                    entities.get('people', []) + 
                    entities.get('companies', [])
                )
                
                if all_entities:
                    primary_entity = all_entities[0]
                    entity_docs[primary_entity].append(doc)
                else:
                    entity_docs['unknown'].append(doc)
            else:
                entity_docs['unknown'].append(doc)
        
        # Convert entity groups to batches
        batches = []
        
        for entity, docs in entity_docs.items():
            current_batch = []
            current_tokens = 0
            
            for doc in docs:
                doc_tokens = self._estimate_tokens(doc)
                
                if current_tokens + doc_tokens <= self.optimal_size:
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
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _create_token_limited_batches(self, 
                                     documents: List[Dict],
                                     max_docs_per_batch: int = 100) -> List[List[Dict]]:
        """Create batches with token and document count limits"""
        
        batches = []
        current_batch = []
        current_tokens = 0
        
        for doc in documents:
            doc_tokens = self._estimate_tokens(doc)
            
            if (current_tokens + doc_tokens <= self.optimal_size and 
                len(current_batch) < max_docs_per_batch):
                current_batch.append(doc)
                current_tokens += doc_tokens
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _estimate_tokens(self, document: Dict) -> int:
        """Estimate tokens in document (including metadata)"""
        
        content = document.get('content', '')
        content_tokens = len(content) // 4  # Rough estimate: 4 chars per token
        
        # Add metadata tokens
        metadata = document.get('metadata', {})
        metadata_tokens = len(str(metadata)) // 4
        
        return content_tokens + metadata_tokens
    
    def _create_semantic_fingerprint(self, document: Dict) -> Dict:
        """Create semantic fingerprint for document clustering"""
        
        content = document.get('content', '').lower()
        metadata = document.get('metadata', {})
        
        fingerprint = {
            'doc_type': metadata.get('classification', self._infer_doc_type(content)),
            'has_dates': metadata.get('has_dates', False),
            'has_amounts': metadata.get('has_amounts', False),
            'length': len(content),
            'keywords': set()
        }
        
        # Extract keywords
        if metadata.get('entities'):
            entities = metadata['entities']
            fingerprint['keywords'].update(entities.get('people', [])[:5])
            fingerprint['keywords'].update(entities.get('companies', [])[:5])
        else:
            # Simple keyword extraction
            keywords = re.findall(r'\b[A-Z][a-z]+\b', content)
            fingerprint['keywords'] = set(keywords[:20])
        
        return fingerprint
    
    def _infer_doc_type(self, content: str) -> str:
        """Infer document type from content"""
        
        content_lower = content.lower()
        
        if 'agreement' in content_lower or 'contract' in content_lower:
            return 'contract'
        elif 'email' in content_lower or 'from:' in content_lower:
            return 'email'
        elif 'invoice' in content_lower or 'payment' in content_lower:
            return 'financial'
        else:
            return 'general'
    
    def _calculate_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between two fingerprints"""
        
        similarity = 0.0
        
        # Type match
        if fp1['doc_type'] == fp2['doc_type']:
            similarity += 0.3
        
        # Keyword overlap
        if fp1['keywords'] and fp2['keywords']:
            keyword_overlap = len(fp1['keywords'] & fp2['keywords'])
            keyword_union = len(fp1['keywords'] | fp2['keywords'])
            if keyword_union > 0:
                similarity += 0.5 * (keyword_overlap / keyword_union)
        
        # Similar features
        if fp1['has_dates'] == fp2['has_dates']:
            similarity += 0.1
        if fp1['has_amounts'] == fp2['has_amounts']:
            similarity += 0.1
        
        return similarity
    
    def _calculate_investigation_relevance(self, 
                                          document: Dict,
                                          investigation_type: str,
                                          investigation_data: Dict) -> float:
        """Calculate document relevance for investigation"""
        
        score = 0.0
        content_lower = document.get('content', '').lower()
        metadata = document.get('metadata', {})
        
        if investigation_type == 'contradiction':
            if 'statement_a' in investigation_data:
                if investigation_data['statement_a'].lower()[:100] in content_lower:
                    score += 5.0
            if 'statement_b' in investigation_data:
                if investigation_data['statement_b'].lower()[:100] in content_lower:
                    score += 5.0
            if metadata.get('has_dates'):
                score += 1.0
        
        elif investigation_type == 'financial_anomaly':
            if metadata.get('has_amounts'):
                score += 3.0
            if metadata.get('classification') == 'financial':
                score += 2.0
        
        elif investigation_type == 'timeline_impossibility':
            if metadata.get('has_dates'):
                date_count = len(metadata.get('dates_found', []))
                score += min(5.0, date_count * 0.5)
        
        # General relevance
        if 'trigger' in investigation_data:
            trigger_text = str(investigation_data.get('trigger', '')).lower()
            if trigger_text and trigger_text in content_lower:
                score += 1.5
        
        return score
    
    def _calculate_priority_score(self, document: Dict) -> float:
        """Calculate document priority score"""
        
        score = 0.0
        content_lower = document.get('content', '').lower()
        metadata = document.get('metadata', {})
        
        # Critical content markers
        if 'nuclear' in content_lower or 'smoking gun' in content_lower:
            score += 1.0
        if 'critical' in content_lower:
            score += 0.8
        if 'suspicious' in content_lower or 'anomaly' in content_lower:
            score += 0.6
        
        # Document type scoring
        doc_type = metadata.get('classification', 'general')
        type_scores = {
            'contract': 0.5,
            'agreement': 0.5,
            'financial': 0.4,
            'email': 0.3
        }
        score += type_scores.get(doc_type, 0.1)
        
        # Entity presence
        entities = metadata.get('entities', {})
        total_entities = (
            len(entities.get('people', [])) + 
            len(entities.get('companies', []))
        )
        score += min(0.5, total_entities * 0.05)
        
        # Financial and temporal information
        if metadata.get('has_amounts'):
            score += 0.3
        if metadata.get('has_dates'):
            score += 0.2
        
        return min(1.0, score)
    
    def _record_batch_creation(self, strategy: str, batches: List[List[Dict]]):
        """Record batch creation for statistics"""
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'batch_count': len(batches),
            'document_count': sum(len(batch) for batch in batches),
            'avg_docs_per_batch': sum(len(batch) for batch in batches) / max(1, len(batches))
        }
        
        self.batch_history.append(record)
        
        # Keep only last 50 records
        if len(self.batch_history) > 50:
            self.batch_history = self.batch_history[-50:]
    
    def get_batch_statistics(self) -> Dict:
        """Get batching statistics"""
        
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
            'strategies_used': dict(strategy_counts)
        }