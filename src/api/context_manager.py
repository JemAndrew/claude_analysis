#!/usr/bin/env python3
"""
Context Manager for 150k+ Token Windows
Optimises document batching and context preservation
"""

from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime
import hashlib


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
                
                # Start new batch with context overlap
                overlap_context = self._create_overlap_context(current_batch)
                current_batch = {
                    'knowledge_context': overlap_context,
                    'documents': [doc],
                    'token_count': self._estimate_tokens(json.dumps(overlap_context)) + doc_tokens,
                    'overflow': False
                }
        
        # Add final batch
        if current_batch['documents']:
            batches.append(current_batch)
        
        # Record context usage
        self._record_context_usage(batches)
        
        return batches
    
    def build_investigation_context(self,
                                   investigation: Dict,
                                   relevant_docs: List[Dict],
                                   knowledge_graph_context: Dict) -> Dict:
        """
        Build focused context for investigation thread
        """
        
        # Priority context for investigation
        investigation_context = {
            'investigation_id': investigation.get('id'),
            'trigger': investigation.get('type'),
            'priority': investigation.get('priority'),
            'related_data': investigation.get('data', {})
        }
        
        # Filter knowledge graph context to relevant items
        filtered_knowledge = self._filter_knowledge_for_investigation(
            knowledge_graph_context, 
            investigation
        )
        
        # Calculate available space
        base_tokens = self._estimate_tokens(json.dumps(investigation_context))
        knowledge_tokens = self._estimate_tokens(json.dumps(filtered_knowledge))
        available = self.optimal_size - base_tokens - knowledge_tokens
        
        # Select most relevant documents
        selected_docs = []
        doc_tokens = 0
        
        for doc in relevant_docs:
            doc_size = self._estimate_tokens(doc.get('content', ''))
            if doc_tokens + doc_size <= available:
                selected_docs.append(doc)
                doc_tokens += doc_size
            else:
                # Truncate if valuable enough
                if self._should_truncate(doc, investigation):
                    truncated = self._truncate_document(doc, available - doc_tokens)
                    selected_docs.append(truncated)
                    break
        
        return {
            'investigation': investigation_context,
            'knowledge': filtered_knowledge,
            'documents': selected_docs,
            'token_count': base_tokens + knowledge_tokens + doc_tokens
        }
    
    def build_recursive_context(self,
                               current_analysis: str,
                               depth: int,
                               previous_levels: List[Dict]) -> Dict:
        """
        Build context for recursive self-questioning
        Preserves questioning chain while managing tokens
        """
        
        # Calculate how much space each level gets
        available_tokens = self.optimal_size - self.buffer
        tokens_per_level = available_tokens // (depth + 1)
        
        context = {
            'current_analysis': self._truncate_text(current_analysis, tokens_per_level * 2),
            'previous_levels': [],
            'depth': depth
        }
        
        # Add previous levels with intelligent truncation
        for level in previous_levels:
            level_summary = {
                'level': level.get('level'),
                'key_questions': level.get('questions', [])[:3],
                'key_findings': self._truncate_text(
                    level.get('findings', ''), 
                    tokens_per_level // 2
                ),
                'confidence': level.get('confidence')
            }
            context['previous_levels'].append(level_summary)
        
        return context
    
    def manage_overflow(self, content: str, context_id: str) -> Tuple[str, bool]:
        """
        Handle content that exceeds context window
        Returns (truncated_content, has_overflow)
        """
        
        content_tokens = self._estimate_tokens(content)
        
        if content_tokens <= self.optimal_size:
            return content, False
        
        # Store overflow in cache
        overflow_parts = []
        remaining = content
        part_num = 0
        
        while remaining:
            # Take optimal chunk
            chunk_size = self.optimal_size * 4  # Roughly 4 chars per token
            chunk = remaining[:chunk_size]
            remaining = remaining[chunk_size:]
            
            # Store in overflow cache
            overflow_key = f"{context_id}_part_{part_num}"
            self.overflow_cache[overflow_key] = chunk
            overflow_parts.append(overflow_key)
            part_num += 1
        
        # Return first part with overflow marker
        return self.overflow_cache[overflow_parts[0]] + "\n[OVERFLOW: Additional parts cached]", True
    
    def _score_documents(self, 
                        documents: List[Dict],
                        knowledge_context: Dict,
                        priority_metric: str) -> List[Tuple[float, Dict]]:
        """
        Score documents based on priority metric
        Returns sorted list of (score, document) tuples
        """
        
        scored = []
        
        # Extract priority signals from knowledge context
        critical_entities = set()
        for entity in knowledge_context.get('suspicious_entities', []):
            critical_entities.add(entity.get('name', '').lower())
        
        critical_patterns = []
        for pattern in knowledge_context.get('strong_patterns', []):
            critical_patterns.append(pattern.get('description', '').lower())
        
        for doc in documents:
            score = 0.0
            content_lower = doc.get('content', '').lower()
            
            # Score based on priority metric
            if priority_metric == 'relevance':
                # Check for critical entities
                for entity in critical_entities:
                    if entity in content_lower:
                        score += 2.0
                
                # Check for pattern matches
                for pattern in critical_patterns:
                    if any(word in content_lower for word in pattern.split()[:3]):
                        score += 1.5
                
                # Check for investigation markers
                markers = ['critical', 'suspicious', 'anomaly', 'impossible']
                for marker in markers:
                    if marker in content_lower:
                        score += 1.0
            
            elif priority_metric == 'chronology':
                # Score based on date
                if doc.get('metadata', {}).get('date'):
                    score = 1.0 / (1 + abs(hash(doc['metadata']['date'])) % 1000)
            
            elif priority_metric == 'entity':
                # Score based on entity presence
                entity_count = sum(1 for e in critical_entities if e in content_lower)
                score = entity_count
            
            # Add document length as tiebreaker (prefer complete docs)
            score += len(content_lower) / 1000000
            
            scored.append((score, doc))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored
    
    def _create_overlap_context(self, previous_batch: Dict) -> Dict:
        """
        Create overlap context for batch continuity
        """
        
        # Extract key findings from previous batch
        overlap = {
            'previous_batch_summary': {
                'document_count': len(previous_batch['documents']),
                'key_entities': [],
                'key_findings': []
            }
        }
        
        # Extract entities mentioned
        for doc in previous_batch['documents'][-3:]:  # Last 3 docs
            content = doc.get('content', '')[:500]
            # Simple entity extraction (could be enhanced)
            import re
            entities = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)
            overlap['previous_batch_summary']['key_entities'].extend(entities[:5])
        
        # Include critical knowledge context
        if 'knowledge_context' in previous_batch:
            overlap['critical_context'] = {
                'contradictions': previous_batch['knowledge_context'].get('critical_contradictions', [])[:3],
                'patterns': previous_batch['knowledge_context'].get('strong_patterns', [])[:3]
            }
        
        return overlap
    
    def _filter_knowledge_for_investigation(self,
                                           knowledge: Dict,
                                           investigation: Dict) -> Dict:
        """
        Filter knowledge graph context to investigation-relevant items
        """
        
        filtered = {}
        investigation_type = investigation.get('type', '').lower()
        
        # Always include statistics
        filtered['statistics'] = knowledge.get('statistics', {})
        
        # Filter based on investigation type
        if 'contradiction' in investigation_type:
            filtered['critical_contradictions'] = knowledge.get('critical_contradictions', [])
        
        if 'pattern' in investigation_type:
            filtered['strong_patterns'] = knowledge.get('strong_patterns', [])
        
        if 'timeline' in investigation_type:
            filtered['timeline_impossibilities'] = knowledge.get('timeline_impossibilities', [])
        
        if 'entity' in investigation_type or 'relationship' in investigation_type:
            filtered['suspicious_entities'] = knowledge.get('suspicious_entities', [])
        
        # Always include active investigations for cross-reference
        filtered['related_investigations'] = [
            inv for inv in knowledge.get('active_investigations', [])
            if inv.get('id') != investigation.get('id')
        ][:3]
        
        return filtered
    
    def _should_truncate(self, document: Dict, investigation: Dict) -> bool:
        """
        Determine if document is valuable enough to truncate
        """
        
        # Check if document contains investigation-relevant content
        investigation_data = str(investigation.get('data', {})).lower()
        doc_content = document.get('content', '').lower()
        
        # High-value indicators
        if any(term in doc_content for term in ['nuclear', 'critical', 'smoking gun']):
            return True
        
        # Check for investigation-specific terms
        key_terms = investigation_data.split()[:10]
        matches = sum(1 for term in key_terms if term in doc_content)
        
        return matches >= 3
    
    def _truncate_document(self, document: Dict, max_tokens: int) -> Dict:
        """
        Intelligently truncate document preserving key sections
        """
        
        truncated = document.copy()
        content = document.get('content', '')
        
        # Estimate character limit
        max_chars = max_tokens * 4
        
        if len(content) <= max_chars:
            return truncated
        
        # Try to preserve beginning and end
        start_chars = max_chars * 2 // 3
        end_chars = max_chars // 3
        
        truncated['content'] = (
            content[:start_chars] + 
            "\n[...TRUNCATED...]\n" + 
            content[-end_chars:]
        )
        truncated['truncated'] = True
        
        return truncated
    
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """Simple text truncation"""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "...[truncated]"
    
    def _estimate_tokens(self, text: str) -> int:
        # More accurate: ~1 token per 0.75 words
        word_count = len(text.split())
        return int(word_count * 1.3)
    
    def _record_context_usage(self, batches: List[Dict]):
        """Record context usage for optimisation"""
        
        usage = {
            'timestamp': datetime.now().isoformat(),
            'batch_count': len(batches),
            'total_tokens': sum(b['token_count'] for b in batches),
            'avg_tokens_per_batch': sum(b['token_count'] for b in batches) / max(1, len(batches)),
            'document_count': sum(len(b['documents']) for b in batches)
        }
        
        self.context_history.append(usage)
        
        # Keep only last 100 records
        if len(self.context_history) > 100:
            self.context_history = self.context_history[-100:]
    
    def get_usage_stats(self) -> Dict:
        """Get context usage statistics"""
        
        if not self.context_history:
            return {'message': 'No context usage recorded yet'}
        
        total_tokens = sum(h['total_tokens'] for h in self.context_history)
        total_batches = sum(h['batch_count'] for h in self.context_history)
        
        return {
            'total_contexts_built': len(self.context_history),
            'total_batches': total_batches,
            'total_tokens_processed': total_tokens,
            'avg_tokens_per_context': total_tokens / len(self.context_history),
            'avg_batches_per_context': total_batches / len(self.context_history),
            'overflow_cache_size': len(self.overflow_cache),
            'last_usage': self.context_history[-1] if self.context_history else None
        }