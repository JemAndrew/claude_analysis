#!/usr/bin/env python3
"""
Tier 3: Enhanced Knowledge Graph Manager
Wrapper for existing knowledge_graph.py with additional memory features
British English throughout

Location: src/memory/tier3_graph_enhanced.py
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging


class EnhancedGraphManager:
    """
    Enhanced wrapper for existing KnowledgeGraph (Tier 3)
    
    Your existing knowledge_graph.py is already excellent!
    This wrapper adds:
        - Memory-aware context building
        - Cross-tier entity linking
        - Enhanced pattern retrieval
        - Optimised query interfaces
    
    Strategy:
        - Wrap existing knowledge_graph, don't replace it
        - Add memory system integration
        - Provide simplified interfaces for common queries
    """
    
    def __init__(self, knowledge_graph, config):
        """
        Initialise Enhanced Graph Manager
        
        Args:
            knowledge_graph: Existing KnowledgeGraph instance
            config: System configuration
        """
        self.kg = knowledge_graph  # Your existing knowledge graph
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger('EnhancedGraph')
        
        # Track frequently accessed entities
        self.entity_access_count = {}
        
        # Cache for common queries
        self.query_cache = {}
    
    def get_context_for_query(self, 
                             query_text: str,
                             max_tokens: int = 50000) -> Dict[str, Any]:
        """
        Get optimised context for a specific query
        
        This wraps your existing get_context_for_phase() with enhancements
        
        Args:
            query_text: The query being made
            max_tokens: Maximum tokens to return
            
        Returns:
            Optimised context dict
        """
        # Check cache first
        cache_key = self._get_cache_key(query_text)
        if cache_key in self.query_cache:
            self.logger.info("Cache hit for query context")
            return self.query_cache[cache_key]
        
        # Get base context from your existing knowledge graph
        base_context = self.kg.get_context_for_phase('query')
        
        # Enhance with query-specific information
        enhanced_context = {
            **base_context,
            'query_specific': self._get_query_specific_context(query_text),
            'hot_entities': self._get_frequently_accessed_entities(top_k=10),
            'recent_patterns': self._get_recent_patterns(days=7)
        }
        
        # Truncate to token limit if needed
        enhanced_context = self._truncate_context(enhanced_context, max_tokens)
        
        # Cache result
        self.query_cache[cache_key] = enhanced_context
        
        return enhanced_context
    
    def get_entity_context(self, entity_name: str) -> Dict[str, Any]:
        """
        Get complete context about a specific entity
        
        Args:
            entity_name: Name of entity (person, company, etc.)
            
        Returns:
            Dict with all information about the entity
        """
        # Track access
        self.entity_access_count[entity_name] = \
            self.entity_access_count.get(entity_name, 0) + 1
        
        # Query your existing knowledge graph
        # This would use your existing entity retrieval methods
        entity_context = {
            'entity_name': entity_name,
            'relationships': self._get_entity_relationships(entity_name),
            'mentions': self._get_entity_mentions(entity_name),
            'contradictions': self._get_entity_contradictions(entity_name),
            'timeline': self._get_entity_timeline(entity_name),
            'access_count': self.entity_access_count[entity_name]
        }
        
        return entity_context
    
    def get_contradiction_context(self, 
                                  contradiction_id: str = None) -> Dict[str, Any]:
        """
        Get context about contradictions
        
        Args:
            contradiction_id: Specific contradiction (or all if None)
            
        Returns:
            Dict with contradiction information
        """
        # Use your existing kg.get_contradictions() method
        if hasattr(self.kg, 'get_statistics'):
            stats = self.kg.get_statistics()
            
            return {
                'total_contradictions': stats.get('contradictions', 0),
                'critical_contradictions': self._get_critical_contradictions(),
                'contradiction_patterns': self._get_contradiction_patterns()
            }
        
        return {}
    
    def get_pattern_context(self) -> Dict[str, Any]:
        """Get context about identified patterns"""
        if hasattr(self.kg, 'get_statistics'):
            stats = self.kg.get_statistics()
            
            return {
                'total_patterns': stats.get('patterns', 0),
                'high_confidence_patterns': self._get_high_confidence_patterns(),
                'emerging_patterns': self._get_emerging_patterns()
            }
        
        return {}
    
    def link_to_vector_store(self, 
                            entity_id: str,
                            doc_ids: List[str]):
        """
        Link knowledge graph entity to vector store documents
        
        This creates cross-tier references for better context retrieval
        
        Args:
            entity_id: Entity in knowledge graph
            doc_ids: List of document IDs in vector store
        """
        # Store cross-reference
        if not hasattr(self, 'cross_tier_links'):
            self.cross_tier_links = {}
        
        if entity_id not in self.cross_tier_links:
            self.cross_tier_links[entity_id] = []
        
        self.cross_tier_links[entity_id].extend(doc_ids)
        
        self.logger.info(f"Linked entity {entity_id} to {len(doc_ids)} documents")
    
    def get_linked_documents(self, entity_id: str) -> List[str]:
        """Get document IDs linked to an entity"""
        if not hasattr(self, 'cross_tier_links'):
            return []
        
        return self.cross_tier_links.get(entity_id, [])
    
    # ============= HELPER METHODS =============
    
    def _get_query_specific_context(self, query_text: str) -> Dict[str, Any]:
        """Extract query-specific context"""
        # Extract key entities/concepts from query
        entities = self._extract_entities_from_query(query_text)
        
        context = {
            'query_entities': entities,
            'relevant_relationships': []
        }
        
        # Get relationships for each entity
        for entity in entities:
            relationships = self._get_entity_relationships(entity)
            context['relevant_relationships'].extend(relationships)
        
        return context
    
    def _extract_entities_from_query(self, query_text: str) -> List[str]:
        """Simple entity extraction from query text"""
        # This is basic - you could enhance with NER
        entities = []
        
        # Check for key names in your case
        key_names = [
            'Brendan Cahill', 'Isha Taiga', 'Lismore', 'Process Holdings',
            'VR Capital', 'P&ID', 'Nigeria', 'GSPA'
        ]
        
        query_lower = query_text.lower()
        for name in key_names:
            if name.lower() in query_lower:
                entities.append(name)
        
        return entities
    
    def _get_entity_relationships(self, entity_name: str) -> List[Dict]:
        """Get relationships for entity from knowledge graph"""
        # Placeholder - integrate with your kg methods
        return []
    
    def _get_entity_mentions(self, entity_name: str) -> List[Dict]:
        """Get mentions of entity across documents"""
        # Placeholder - integrate with your kg methods
        return []
    
    def _get_entity_contradictions(self, entity_name: str) -> List[Dict]:
        """Get contradictions involving entity"""
        # Placeholder - integrate with your kg methods
        return []
    
    def _get_entity_timeline(self, entity_name: str) -> List[Dict]:
        """Get timeline events involving entity"""
        # Placeholder - integrate with your kg methods
        return []
    
    def _get_frequently_accessed_entities(self, top_k: int = 10) -> List[Dict]:
        """Get most frequently accessed entities"""
        sorted_entities = sorted(
            self.entity_access_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'entity': name, 'access_count': count}
            for name, count in sorted_entities[:top_k]
        ]
    
    def _get_recent_patterns(self, days: int = 7) -> List[Dict]:
        """Get patterns identified in recent days"""
        # Placeholder - would query kg database with time filter
        return []
    
    def _get_critical_contradictions(self) -> List[Dict]:
        """Get critical contradictions (severity >= 7)"""
        # Placeholder - would query your kg database
        return []
    
    def _get_contradiction_patterns(self) -> List[Dict]:
        """Get patterns in contradictions"""
        # Placeholder - analyse contradiction types
        return []
    
    def _get_high_confidence_patterns(self) -> List[Dict]:
        """Get patterns with confidence >= 0.8"""
        # Placeholder - would query your kg database
        return []
    
    def _get_emerging_patterns(self) -> List[Dict]:
        """Get recently identified patterns"""
        # Placeholder - would query by discovery date
        return []
    
    def _truncate_context(self, 
                         context: Dict[str, Any],
                         max_tokens: int) -> Dict[str, Any]:
        """Truncate context to fit within token limit"""
        # Simple truncation - could be more sophisticated
        context_str = json.dumps(context)
        
        estimated_tokens = len(context_str) // 4
        
        if estimated_tokens <= max_tokens:
            return context
        
        # Truncate by priority
        truncated = {
            'statistics': context.get('statistics'),
            'suspicious_entities': context.get('suspicious_entities', [])[:5],
            'critical_contradictions': context.get('critical_contradictions', [])[:5],
            'strong_patterns': context.get('strong_patterns', [])[:5],
            'truncated': True
        }
        
        return truncated
    
    def _get_cache_key(self, query_text: str) -> str:
        """Generate cache key for query"""
        import hashlib
        return hashlib.md5(query_text.encode()).hexdigest()[:16]
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache = {}
        self.logger.info("Query cache cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 3 status"""
        stats = {}
        if hasattr(self.kg, 'get_statistics'):
            stats = self.kg.get_statistics()
        
        return {
            'tier': 3,
            'name': 'Knowledge Graph (Enhanced)',
            'active': self.kg is not None,
            'entities': stats.get('entities', 0),
            'relationships': stats.get('relationships', 0),
            'contradictions': stats.get('contradictions', 0),
            'patterns': stats.get('patterns', 0),
            'cached_queries': len(self.query_cache),
            'tracked_entities': len(self.entity_access_count)
        }
    
    def export_hot_entities(self) -> Path:
        """Export frequently accessed entities for review"""
        export_path = Path(self.config.root) / "data" / "memory_tiers" / "tier3_hot_entities.json"
        
        hot_entities = self._get_frequently_accessed_entities(top_k=50)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(hot_entities, f, indent=2, ensure_ascii=False)
        
        return export_path