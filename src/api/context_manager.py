#!/usr/bin/env python3
"""
Context Manager for 150k+ Token Windows
Optimises document batching and context preservation
COMPLETE FIXED VERSION
"""

from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime


class ContextManager:
    """Manages large context windows for maximum Claude utilisation"""
    
    def __init__(self, config):
        self.config = config
        self.max_context = config.token_config['max_input_tokens']  # 150k
        self.buffer = config.token_config['buffer_tokens']  # 10k safety
        self.optimal_size = config.token_config['optimal_batch_size']  # 140k
        
        # Track context usage
        self.context_history = []
        self.overflow_cache = {}
    
    def build_optimal_context(self,
                             documents: List[Dict],
                             knowledge_context: Dict,
                             priority_metric: str = 'relevance') -> List[Dict]:
        """
        Build optimal context batches for 150k token window
        Returns list of context batches
        """
        
        # Calculate knowledge context size
        knowledge_tokens = self._estimate_tokens(json.dumps(knowledge_context))
        available_tokens = self.optimal_size - knowledge_tokens
        
        print(f"  Knowledge context: {knowledge_tokens:,} tokens")
        print(f"  Available for documents: {available_tokens:,} tokens")
        
        # Score and sort documents
        scored_documents = self._score_documents(documents, knowledge_context, priority_metric)
        
        # Create batches optimised for context window
        batches = []
        current_batch = {
            'knowledge_context': knowledge_context,
            'documents': [],
            'token_count': knowledge_tokens,
            'overflow': False
        }
        
        for score, doc in scored_documents:
            doc_tokens = self._estimate_tokens(doc.get('content', ''))
            
            # Check if document fits in current batch
            if current_batch['token_count'] + doc_tokens <= self.optimal_size:
                current_batch['documents'].append(doc)
                current_batch['token_count'] += doc_tokens
            else:
                # Save current batch and start new one
                if current_batch['documents']:
                    batches.append(current_batch)
                
                # Start new batch with knowledge context
                current_batch = {
                    'knowledge_context': knowledge_context,
                    'documents': [doc],
                    'token_count': knowledge_tokens + doc_tokens,
                    'overflow': False
                }
        
        # Add final batch
        if current_batch['documents']:
            batches.append(current_batch)
        
        print(f"  Created {len(batches)} context batches")
        
        return batches
    
    def build_investigation_context(self,
                                   investigation: Dict,
                                   relevant_docs: List[Dict],
                                   knowledge_graph_context: Dict) -> Dict:
        """
        Build context for investigation thread
        """
        
        return {
            'investigation': investigation,
            'documents': relevant_docs[:20],  # Top 20 relevant docs
            'knowledge': knowledge_graph_context,
            'focus': investigation.get('type', 'general'),
            'priority': investigation.get('priority', 5.0)
        }
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _score_documents(self, 
                        documents: List[Dict], 
                        knowledge_context: Dict,
                        priority_metric: str) -> List[Tuple[float, Dict]]:
        """Score and sort documents by priority"""
        
        scored = []
        
        for doc in documents:
            score = 0.5  # Default score
            
            if priority_metric == 'relevance':
                score = self._calculate_relevance(doc, knowledge_context)
            elif priority_metric == 'chronological':
                score = self._calculate_chronological_score(doc)
            elif priority_metric == 'suspicion':
                score = self._calculate_suspicion(doc)
            
            scored.append((score, doc))
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored
    
    def _calculate_relevance(self, doc: Dict, context: Dict) -> float:
        """Calculate document relevance to current analysis"""
        
        content_lower = doc.get('content', '').lower()
        score = 0.5
        
        # Check for key terms
        key_terms = ['lismore', 'process holdings', 'valuation', 'breach', 'contract', 'agreement']
        for term in key_terms:
            if term in content_lower:
                score += 0.1
        
        # Check for critical markers
        if 'nuclear' in content_lower or 'smoking gun' in content_lower:
            score += 0.5
        if 'critical' in content_lower or 'important' in content_lower:
            score += 0.3
        
        # Check for entities mentioned in context
        if context.get('suspicious_entities'):
            for entity in context.get('suspicious_entities', []):
                entity_name = entity.get('name', '').lower()
                if entity_name and entity_name in content_lower:
                    score += 0.2
        
        return min(1.0, score)
    
    def _calculate_chronological_score(self, doc: Dict) -> float:
        """Calculate score based on date (more recent = higher)"""
        
        dates = doc.get('metadata', {}).get('dates_found', [])
        if dates:
            return 0.7
        return 0.3
    
    def _calculate_suspicion(self, doc: Dict) -> float:
        """Calculate suspicion score"""
        
        content_lower = doc.get('content', '').lower()
        score = 0.3
        
        # Suspicious indicators
        suspicious_terms = [
            'private', 'confidential', 'without prejudice', 
            'delete', 'destroy', 'off the record',
            'between us', 'keep this quiet', 'not for distribution'
        ]
        
        for term in suspicious_terms:
            if term in content_lower:
                score += 0.15
        
        return min(1.0, score)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens in text"""
        if isinstance(text, str):
            return len(text) // 4
        elif isinstance(text, dict) or isinstance(text, list):
            return len(str(text)) // 4
        return 0