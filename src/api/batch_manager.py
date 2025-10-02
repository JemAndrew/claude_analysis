#!/usr/bin/env python3
"""
Intelligent Batch Manager for Document Processing
Semantic clustering and priority-based batching
Enhanced with metadata filtering and intelligent document selection
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
from datetime import datetime
import numpy as np
from collections import defaultdict
import re


class BatchManager:
    """Manages intelligent document batching for API calls with metadata awareness"""
    
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
        elif strategy == 'metadata_filtered':  # NEW strategy
            return self._metadata_filtered_batch(documents)
        else:
            return self._simple_batch(documents)
    
    def create_metadata_filtered_batches(self, 
                                        documents: List[Dict],
                                        filter_type: str,
                                        max_docs_per_batch: int = None) -> List[List[Dict]]:
        """
        NEW: Create batches filtered and prioritised by metadata characteristics
        """
        
        if max_docs_per_batch is None:
            max_docs_per_batch = self.config.filtering_thresholds.get(
                'maximum_documents_per_batch', 50
            )
        
        filtered_batches = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            
            # Calculate relevance score using config
            relevance_score = self.config.calculate_metadata_relevance(
                metadata, 
                filter_type
            )
            
            # Categorise by priority
            if relevance_score >= self.config.filtering_thresholds['priority_document_threshold']:
                priority = 'high_priority'
            elif relevance_score >= self.config.filtering_thresholds['minimum_relevance_score']:
                priority = 'medium_priority'
            else:
                priority = 'low_priority'
            
            filtered_batches[priority].append({
                'document': doc,
                'relevance_score': relevance_score
            })
        
        # Sort within each priority level
        for priority in filtered_batches:
            filtered_batches[priority].sort(
                key=lambda x: x['relevance_score'], 
                reverse=True
            )
        
        # Convert to batches with high priority first
        final_batches = []
        
        for priority in ['high_priority', 'medium_priority', 'low_priority']:
            if filtered_batches[priority]:
                # Extract just documents
                priority_docs = [item['document'] for item in filtered_batches[priority]]
                
                # Create batches respecting token limits
                priority_batches = self._create_token_limited_batches(
                    priority_docs, 
                    max_docs_per_batch
                )
                
                final_batches.extend(priority_batches)
        
        self._record_batch_creation(f'metadata_filtered_{filter_type}', final_batches)
        
        print(f"  Created {len(final_batches)} metadata-filtered batches")
        print(f"    High priority docs: {len(filtered_batches['high_priority'])}")
        print(f"    Medium priority docs: {len(filtered_batches['medium_priority'])}")
        print(f"    Low priority docs: {len(filtered_batches['low_priority'])}")
        
        return final_batches
    
    def create_investigation_batches(self, 
                                   documents: List[Dict],
                                   investigation_type: str,
                                   investigation_data: Dict) -> List[List[Dict]]:
        """
        NEW: Create batches optimised for specific investigation types
        """
        
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
        
        # Take top documents based on investigation type
        if investigation_type == 'contradiction':
            max_docs = 30  # Need context from multiple sources
        elif investigation_type == 'financial_anomaly':
            max_docs = 20  # Focus on financial documents
        elif investigation_type == 'timeline_impossibility':
            max_docs = 40  # Need broad temporal context
        else:
            max_docs = 25
        
        relevant_docs = [doc for score, doc in scored_docs[:max_docs] if score > 0]
        
        # Create batches
        batches = self._create_token_limited_batches(relevant_docs)
        
        self._record_batch_creation(f'investigation_{investigation_type}', batches)
        
        return batches
    
    def _metadata_filtered_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Batch documents based on metadata quality and relevance
        """
        
        # Score documents by metadata richness
        scored_docs = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            score = 0
            
            # Score based on metadata completeness
            if metadata.get('has_dates'):
                score += 1
            if metadata.get('has_amounts'):
                score += 1
            if metadata.get('entities', {}).get('people'):
                score += len(metadata['entities']['people']) * 0.1
            if metadata.get('entities', {}).get('companies'):
                score += len(metadata['entities']['companies']) * 0.1
            if metadata.get('classification') != 'general':
                score += 0.5
            
            scored_docs.append((score, doc))
        
        # Sort by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Create batches with high-quality documents first
        batches = []
        current_batch = []
        current_tokens = 0
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        for score, doc in scored_docs:
            doc_tokens = self._estimate_tokens(doc)
            
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
        
        return batches
    
    def _calculate_investigation_relevance(self, 
                                         document: Dict,
                                         investigation_type: str,
                                         investigation_data: Dict) -> float:
        """
        NEW: Calculate document relevance for specific investigation
        """
        
        score = 0.0
        content_lower = document.get('content', '').lower()
        metadata = document.get('metadata', {})
        
        if investigation_type == 'contradiction':
            # Check for statement fragments
            if 'statement_a' in investigation_data:
                if investigation_data['statement_a'].lower()[:100] in content_lower:
                    score += 5.0
            if 'statement_b' in investigation_data:
                if investigation_data['statement_b'].lower()[:100] in content_lower:
                    score += 5.0
            
            # Metadata relevance
            if metadata.get('has_dates'):
                score += 1.0
            if len(metadata.get('entities', {}).get('people', [])) > 2:
                score += 0.5
        
        elif investigation_type == 'financial_anomaly':
            # Financial documents are highly relevant
            if metadata.get('has_amounts'):
                score += 3.0
            if metadata.get('classification') == 'financial':
                score += 2.0
            
            # Check for specific amount mentioned
            if 'amount' in investigation_data:
                amount_str = str(investigation_data['amount'])
                if amount_str in content_lower:
                    score += 4.0
        
        elif investigation_type == 'timeline_impossibility':
            # Date-heavy documents are relevant
            if metadata.get('has_dates'):
                date_count = len(metadata.get('dates_found', []))
                score += min(5.0, date_count * 0.5)
            
            # Check for specific date
            if 'date' in investigation_data:
                if investigation_data['date'] in content_lower:
                    score += 3.0
        
        elif investigation_type == 'entity' or investigation_type == 'new_entity_type':
            # Check for entity presence
            entities_in_doc = metadata.get('entities', {})
            if 'entity' in investigation_data:
                entity_name = investigation_data['entity'].get('name', '')
                
                if entity_name in str(entities_in_doc):
                    score += 4.0
                if entity_name.lower() in content_lower:
                    score += 2.0
        
        # General relevance checks
        if 'trigger' in investigation_data:
            trigger_text = str(investigation_data.get('trigger', '')).lower()
            if trigger_text and trigger_text in content_lower:
                score += 1.5
        
        return score
    
    def _create_token_limited_batches(self, 
                                     documents: List[Dict],
                                     max_docs_per_batch: int = None) -> List[List[Dict]]:
        """
        NEW: Helper to create batches with token and document count limits
        """
        
        batches = []
        current_batch = []
        current_tokens = 0
        max_batch_tokens = self.config.batch_strategy['max_batch_size']
        
        if max_docs_per_batch is None:
            max_docs_per_batch = 100  # Default high limit
        
        for doc in documents:
            doc_tokens = self._estimate_tokens(doc)
            
            # Check both token and document count limits
            if (current_tokens + doc_tokens <= max_batch_tokens and 
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
        """
        NEW: Better token estimation including metadata
        """
        
        # Base content tokens
        content = document.get('content', '')
        content_tokens = len(content) // 4  # Rough estimate
        
        # Add tokens for metadata that will be sent
        metadata = document.get('metadata', {})
        metadata_tokens = 0
        
        if metadata.get('dates_found'):
            metadata_tokens += len(str(metadata['dates_found'])) // 4
        if metadata.get('amounts_found'):
            metadata_tokens += len(str(metadata['amounts_found'])) // 4
        if metadata.get('entities'):
            metadata_tokens += len(str(metadata['entities'])) // 4
        
        return content_tokens + metadata_tokens
    
    # ============================================================
    # EXISTING METHODS - Kept unchanged with minor enhancements
    # ============================================================
    
    def _semantic_clustering_batch(self, documents: List[Dict]) -> List[List[Dict]]:
        """
        Batch documents by semantic similarity
        Groups related documents together for better pattern recognition
        Enhanced with metadata awareness
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
                doc_tokens = self._estimate_tokens(doc)
                
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
        Enhanced to use metadata dates
        """
        
        # Extract dates and sort
        dated_docs = []
        undated_docs = []
        
        for doc in documents:
            # Try metadata first
            metadata_dates = doc.get('metadata', {}).get('dates_found', [])
            if metadata_dates:
                # Use first date found
                date = metadata_dates[0]
                dated_docs.append((date, doc))
            else:
                # Fall back to content extraction
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
            doc_tokens = self._estimate_tokens(doc)
            
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
            doc_tokens = self._estimate_tokens(doc)
            
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
        Enhanced to use metadata entities
        """
        
        # Extract entities from documents
        entity_docs = defaultdict(list)
        
        for doc in documents:
            # Prioritise metadata entities
            metadata_entities = doc.get('metadata', {}).get('entities', {})
            
            if metadata_entities:
                # Combine all entity types
                all_entities = (
                    metadata_entities.get('people', []) + 
                    metadata_entities.get('companies', [])
                )
                
                if all_entities:
                    # Add to most prominent entity's batch
                    primary_entity = all_entities[0]
                    entity_docs[primary_entity].append(doc)
                else:
                    entity_docs['unknown'].append(doc)
            else:
                # Fall back to extraction
                entities = self._extract_entities(doc)
                if entities:
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
                doc_tokens = self._estimate_tokens(doc)
                
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
        Enhanced with metadata scoring
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
            doc_tokens = self._estimate_tokens(doc)
            
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
            doc_tokens = self._estimate_tokens(doc)
            
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
        Enhanced with metadata features
        """
        
        content = document.get('content', '').lower()
        metadata = document.get('metadata', {})
        
        # Extract key features
        fingerprint = {
            'doc_type': metadata.get('classification', self._infer_doc_type(content)),
            'has_dates': metadata.get('has_dates', bool(re.search(r'\d{4}', content))),
            'has_numbers': metadata.get('has_amounts', bool(re.search(r'[\d,]+', content))),
            'length': len(content),
            'keywords': set()
        }
        
        # Extract keywords from metadata or content
        if metadata.get('entities'):
            # Use metadata entities as keywords
            entities = metadata['entities']
            fingerprint['keywords'].update(entities.get('people', [])[:5])
            fingerprint['keywords'].update(entities.get('companies', [])[:5])
        else:
            # Fall back to simple extraction
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
        if fp1['has_numbers'] == fp2['has_numbers']:
            similarity += 0.1
        
        return similarity
    
    def _extract_date(self, document: Dict) -> Optional[str]:
        """
        Extract primary date from document
        """
        
        # Check metadata first
        metadata_dates = document.get('metadata', {}).get('dates_found', [])
        if metadata_dates:
            return metadata_dates[0]
        
        # Simple date extraction from content
        content = document.get('content', '')
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        dates = re.findall(date_pattern, content)
        
        return dates[0] if dates else None
    
    def _extract_entities(self, document: Dict) -> List[str]:
        """
        Extract key entities from document
        """
        
        # Check metadata first
        metadata = document.get('metadata', {})
        if metadata.get('entities'):
            entities = metadata['entities']
            return (entities.get('people', [])[:5] + 
                   entities.get('companies', [])[:5])
        
        # Simple entity extraction
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
        Enhanced with metadata and critical terms
        """
        
        score = 0.0
        content_lower = document.get('content', '').lower()
        metadata = document.get('metadata', {})
        
        # Content-based scoring
        if 'nuclear' in content_lower or 'smoking gun' in content_lower:
            score += 1.0
        if 'critical' in content_lower:
            score += 0.8
        if 'suspicious' in content_lower or 'anomaly' in content_lower:
            score += 0.6
        
        # Check for critical terms from config
        if hasattr(self.config, 'metadata_patterns'):
            for term in self.config.metadata_patterns.get('critical_terms', []):
                if term in content_lower:
                    score += 0.3
        
        # Metadata-based scoring
        if metadata.get('classification') in ['contract', 'agreement']:
            score += 0.5
        elif metadata.get('classification') in ['email', 'correspondence']:
            score += 0.3
        elif metadata.get('classification') == 'financial':
            score += 0.4
        
        # Entity presence scoring
        entities = metadata.get('entities', {})
        total_entities = (
            len(entities.get('people', [])) + 
            len(entities.get('companies', []))
        )
        score += min(0.5, total_entities * 0.05)
        
        # Financial information
        if metadata.get('has_amounts'):
            score += 0.3
        
        # Temporal information
        if metadata.get('has_dates'):
            score += 0.2
        
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