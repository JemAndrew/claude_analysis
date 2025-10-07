#!/usr/bin/env python3
"""
Hierarchical Memory System - Main Coordinator
Manages 5-tier memory architecture for litigation intelligence
British English throughout

Location: src/memory/hierarchical_system.py
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class MemoryQuery:
    """Query structure for memory retrieval"""
    query_text: str
    max_tokens: int = 100000
    include_tiers: List[int] = None  # Which tiers to query [1,2,3,4,5]
    priority_entities: List[str] = None
    time_range: Tuple[str, str] = None
    document_types: List[str] = None


@dataclass
class MemoryResult:
    """Result from memory retrieval"""
    tier: int
    content: Any
    relevance_score: float
    token_cost: int
    source_docs: List[str]
    metadata: Dict[str, Any]


class HierarchicalMemory:
    """
    Main coordinator for 5-tier memory system
    
    TIER 1: Claude Projects (100 docs, permanent, £0/query)
    TIER 2: Vector Database (semantic search, millisecond retrieval)
    TIER 3: Knowledge Graph (relationships, patterns, contradictions)
    TIER 4: Cold Storage (encrypted originals, on-demand)
    TIER 5: Analysis Cache (processed outputs, fast retrieval)
    """
    
    def __init__(self, config, knowledge_graph=None):
        """
        Initialise hierarchical memory system
        
        Args:
            config: System configuration object
            knowledge_graph: Existing KnowledgeGraph instance (Tier 3)
        """
        self.config = config
        self.root = Path(config.project_root)
        
        # Set up logging
        self.logger = self._init_logging()
        
        # Create tier directory structure
        self.memory_root = self.root / "data" / "memory_tiers"
        self._init_tier_directories()
        
        # Initialise tier managers (lazy loading for performance)
        self._tier1 = None  # Claude Projects
        self._tier2 = None  # Vector Store
        self._tier3 = knowledge_graph  # Existing knowledge graph
        self._tier4 = None  # Cold Storage
        self._tier5 = None  # Analysis Cache
        
        # Track tier statistics
        self.stats = {
            'tier1_hits': 0,
            'tier2_hits': 0,
            'tier3_hits': 0,
            'tier4_hits': 0,
            'tier5_hits': 0,
            'total_queries': 0,
            'avg_response_time': 0,
            'cost_saved': 0.0
        }
        
        self.logger.info("Hierarchical Memory System initialised")
    
    def _init_logging(self) -> logging.Logger:
        """Initialise logging for memory system"""
        logger = logging.getLogger('HierarchicalMemory')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if needed
        log_dir = self.root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / "memory_system.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _init_tier_directories(self):
        """Create directory structure for all tiers"""
        self.tier_paths = {
            1: self.memory_root / "tier1_project_manifest",
            2: self.memory_root / "tier2_vector_store",
            3: self.memory_root / "tier3_knowledge_graph",
            4: self.memory_root / "tier4_cold_storage",
            5: self.memory_root / "tier5_analysis_cache"
        }
        
        for tier_path in self.tier_paths.values():
            tier_path.mkdir(parents=True, exist_ok=True)
    
    # ============= TIER MANAGERS (LAZY LOADING) =============
    
    @property
    def tier1(self):
        """Lazy load Tier 1: Claude Projects"""
        if self._tier1 is None:
            from memory.tier1_project import ProjectKnowledgeManager
            self._tier1 = ProjectKnowledgeManager(
                manifest_path=self.tier_paths[1],
                config=self.config
            )
            self.logger.info("Tier 1 (Claude Projects) loaded")
        return self._tier1
    
    @property
    def tier2(self):
        """Lazy load Tier 2: Vector Store"""
        if self._tier2 is None:
            try:
                from memory.tier2_vector import VectorStoreManager
                self._tier2 = VectorStoreManager(
                    store_path=self.tier_paths[2],
                    config=self.config
                )
                self.logger.info("Tier 2 (Vector Store) loaded")
            except ImportError as e:
                self.logger.warning(f"Tier 2 unavailable: {e}")
                self._tier2 = None
            except Exception as e:
                self.logger.error(f"Tier 2 initialisation failed: {e}")
                self._tier2 = None
        return self._tier2
    
    @property
    def tier3(self):
        """Tier 3: Knowledge Graph (already loaded)"""
        if self._tier3 is None:
            self.logger.warning("Tier 3 (Knowledge Graph) not provided!")
        return self._tier3
    
    @property
    def tier4(self):
        """Lazy load Tier 4: Cold Storage"""
        if self._tier4 is None:
            from memory.tier4_cold_storage import ColdStorageManager
            self._tier4 = ColdStorageManager(
                vault_path=self.tier_paths[4],
                config=self.config
            )
            self.logger.info("Tier 4 (Cold Storage) loaded")
        return self._tier4
    
    @property
    def tier5(self):
        """Lazy load Tier 5: Analysis Cache"""
        if self._tier5 is None:
            from memory.tier5_analysis_cache import AnalysisCacheManager
            self._tier5 = AnalysisCacheManager(
                cache_path=self.tier_paths[5],
                config=self.config
            )
            self.logger.info("Tier 5 (Analysis Cache) loaded")
        return self._tier5
    
    # ============= MAIN RETRIEVAL INTERFACE =============
    
    def retrieve_relevant_context(self, 
                                  query: MemoryQuery) -> Dict[str, Any]:
        """
        Intelligent multi-tier context retrieval
        
        This is the MAIN method your orchestrator calls
        
        Args:
            query: MemoryQuery object with search parameters
            
        Returns:
            Dict with combined context from all relevant tiers
        """
        start_time = datetime.now()
        self.stats['total_queries'] += 1
        
        self.logger.info(f"Memory query: {query.query_text[:100]}...")
        
        # Determine which tiers to query
        tiers_to_query = query.include_tiers or [1, 2, 3, 5]  # Skip Tier 4 by default
        
        results = {
            'query': query.query_text,
            'tier_results': {},
            'combined_context': '',
            'total_tokens': 0,
            'cost_estimate': 0.0,
            'retrieval_time_ms': 0
        }
        
        # TIER 1: Claude Projects (always free, always query if available)
        if 1 in tiers_to_query:
            tier1_result = self._query_tier1(query)
            if tier1_result:
                results['tier_results'][1] = tier1_result
                self.stats['tier1_hits'] += 1
                self.logger.info(f"Tier 1 provided {tier1_result.token_cost} tokens")
        
        # TIER 2: Vector Store (semantic search)
        if 2 in tiers_to_query:
            tier2_result = self._query_tier2(query)
            if tier2_result:
                results['tier_results'][2] = tier2_result
                self.stats['tier2_hits'] += 1
                self.logger.info(f"Tier 2 found {len(tier2_result.source_docs)} relevant docs")
        
        # TIER 3: Knowledge Graph (relationships & patterns)
        if 3 in tiers_to_query and self.tier3:
            tier3_result = self._query_tier3(query)
            if tier3_result:
                results['tier_results'][3] = tier3_result
                self.stats['tier3_hits'] += 1
                self.logger.info(f"Tier 3 provided graph context")
        
        # TIER 5: Analysis Cache (previous findings)
        if 5 in tiers_to_query:
            tier5_result = self._query_tier5(query)
            if tier5_result:
                results['tier_results'][5] = tier5_result
                self.stats['tier5_hits'] += 1
                self.logger.info(f"Tier 5 cache hit")
        
        # TIER 4: Cold Storage (only if specifically requested or other tiers insufficient)
        if 4 in tiers_to_query or self._should_query_cold_storage(results, query):
            tier4_result = self._query_tier4(query)
            if tier4_result:
                results['tier_results'][4] = tier4_result
                self.stats['tier4_hits'] += 1
                self.logger.info(f"Tier 4 cold storage accessed")
        
        # Combine results intelligently
        results['combined_context'] = self._combine_tier_results(
            results['tier_results'],
            query.max_tokens
        )
        
        # Calculate metrics
        results['total_tokens'] = self._estimate_tokens(results['combined_context'])
        results['cost_estimate'] = self._calculate_cost_savings(results['tier_results'])
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        results['retrieval_time_ms'] = elapsed
        
        self.stats['cost_saved'] += results['cost_estimate']
        
        self.logger.info(
            f"Retrieved {results['total_tokens']} tokens in {elapsed:.0f}ms, "
            f"saved ~£{results['cost_estimate']:.2f}"
        )
        
        return results
    
    # ============= TIER-SPECIFIC QUERY METHODS =============
    
    def _query_tier1(self, query: MemoryQuery) -> Optional[MemoryResult]:
        """Query Tier 1: Claude Projects"""
        try:
            # Claude Projects are automatically available in context
            # Just return manifest of what's available
            manifest = self.tier1.get_project_manifest()
            
            if not manifest:
                return None
            
            return MemoryResult(
                tier=1,
                content=manifest,
                relevance_score=1.0,  # Always relevant (permanent context)
                token_cost=0,  # Free!
                source_docs=manifest.get('document_list', []),
                metadata={'tier': 'project_knowledge', 'cost': 0}
            )
        except Exception as e:
            self.logger.error(f"Tier 1 query failed: {e}")
            return None
    
    def _query_tier2(self, query: MemoryQuery) -> Optional[MemoryResult]:
        """Query Tier 2: Vector Store (semantic search)"""
        try:
            # Semantic similarity search
            results = self.tier2.semantic_search(
                query_text=query.query_text,
                top_k=20,
                filters={
                    'time_range': query.time_range,
                    'document_types': query.document_types
                }
            )
            
            if not results:
                return None
            
            return MemoryResult(
                tier=2,
                content=results,
                relevance_score=results[0]['score'] if results else 0,
                token_cost=sum(r.get('tokens', 0) for r in results),
                source_docs=[r['doc_id'] for r in results],
                metadata={'search_type': 'semantic', 'results_count': len(results)}
            )
        except Exception as e:
            self.logger.error(f"Tier 2 query failed: {e}")
            return None
    
    def _query_tier3(self, query: MemoryQuery) -> Optional[MemoryResult]:
        """Query Tier 3: Knowledge Graph"""
        try:
            # Get context from existing knowledge graph
            graph_context = self.tier3.get_context_for_phase('query')
            
            if not graph_context:
                return None
            
            return MemoryResult(
                tier=3,
                content=graph_context,
                relevance_score=0.8,
                token_cost=self._estimate_tokens(str(graph_context)),
                source_docs=[],
                metadata={'source': 'knowledge_graph'}
            )
        except Exception as e:
            self.logger.error(f"Tier 3 query failed: {e}")
            return None
    
    def _query_tier4(self, query: MemoryQuery) -> Optional[MemoryResult]:
        """Query Tier 4: Cold Storage (encrypted vault)"""
        try:
            # Only retrieve if specific documents requested
            if not query.priority_entities:
                return None
            
            documents = self.tier4.retrieve_documents(
                doc_ids=query.priority_entities
            )
            
            if not documents:
                return None
            
            return MemoryResult(
                tier=4,
                content=documents,
                relevance_score=0.9,
                token_cost=sum(d.get('tokens', 0) for d in documents),
                source_docs=[d['doc_id'] for d in documents],
                metadata={'source': 'cold_storage', 'decrypted': True}
            )
        except Exception as e:
            self.logger.error(f"Tier 4 query failed: {e}")
            return None
    
    def _query_tier5(self, query: MemoryQuery) -> Optional[MemoryResult]:
        """Query Tier 5: Analysis Cache"""
        try:
            # Check if we've analysed this query before
            cached = self.tier5.get_cached_analysis(query.query_text)
            
            if not cached:
                return None
            
            return MemoryResult(
                tier=5,
                content=cached,
                relevance_score=1.0,  # Exact match
                token_cost=0,  # Already processed
                source_docs=[],
                metadata={'cache_hit': True, 'cached_date': cached.get('date')}
            )
        except Exception as e:
            self.logger.error(f"Tier 5 query failed: {e}")
            return None
    
    # ============= HELPER METHODS =============
    
    def _should_query_cold_storage(self, current_results: Dict, query: MemoryQuery) -> bool:
        """Determine if cold storage retrieval is needed"""
        # Check if we have enough relevant context already
        total_tokens = sum(
            r.token_cost for r in current_results.get('tier_results', {}).values()
        )
        
        # Only access cold storage if insufficient context
        return total_tokens < 10000  # Minimum context threshold
    
    def _combine_tier_results(self, 
                              tier_results: Dict[int, MemoryResult],
                              max_tokens: int) -> str:
        """Intelligently combine results from multiple tiers"""
        # Priority order: Tier 5 (cache) > Tier 1 (projects) > Tier 3 (graph) > Tier 2 (vector) > Tier 4 (cold)
        priority_order = [5, 1, 3, 2, 4]
        
        combined = []
        tokens_used = 0
        
        for tier_num in priority_order:
            if tier_num not in tier_results:
                continue
            
            result = tier_results[tier_num]
            
            # Check token budget
            if tokens_used + result.token_cost > max_tokens:
                # Truncate this result
                remaining = max_tokens - tokens_used
                content_str = str(result.content)[:remaining * 4]  # Approx 4 chars per token
                combined.append(f"\n=== TIER {tier_num} (TRUNCATED) ===\n{content_str}")
                break
            
            combined.append(f"\n=== TIER {tier_num} ===\n{str(result.content)}")
            tokens_used += result.token_cost
        
        return "\n".join(combined)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text) // 4
    
    def _calculate_cost_savings(self, tier_results: Dict[int, MemoryResult]) -> float:
        """Calculate cost savings from using tiered system"""
        # Tier 1 and Tier 5 are free
        free_tokens = 0
        for tier_num in [1, 5]:
            if tier_num in tier_results:
                free_tokens += tier_results[tier_num].token_cost
        
        # Opus pricing: £15 per 1M input tokens
        cost_saved = (free_tokens / 1_000_000) * 15
        return cost_saved
    
    # ============= DOCUMENT INGESTION =============
    
    def ingest_document(self, 
                       doc_path: Path,
                       doc_metadata: Dict[str, Any],
                       target_tiers: List[int] = None) -> Dict[str, bool]:
        """
        Ingest document into appropriate tiers
        
        Args:
            doc_path: Path to document file
            doc_metadata: Metadata (importance, type, etc.)
            target_tiers: Which tiers to add to (auto-determined if None)
            
        Returns:
            Dict of tier: success status
        """
        if target_tiers is None:
            target_tiers = self._determine_target_tiers(doc_metadata)
        
        results = {}
        
        # Tier 1: Only top 100 documents
        if 1 in target_tiers:
            results[1] = self.tier1.add_to_project_manifest(doc_path, doc_metadata)
        
        # Tier 2: All documents
        if 2 in target_tiers:
            results[2] = self.tier2.add_document(doc_path, doc_metadata)
        
        # Tier 3: Extract entities/relationships for knowledge graph
        if 3 in target_tiers and self.tier3:
            # This would be done through your existing analysis pipeline
            results[3] = True
        
        # Tier 4: Always store original
        if 4 in target_tiers:
            results[4] = self.tier4.encrypt_and_store(doc_path, doc_metadata)
        
        self.logger.info(f"Ingested {doc_path.name} into tiers: {list(results.keys())}")
        return results
    
    def _determine_target_tiers(self, doc_metadata: Dict[str, Any]) -> List[int]:
        """Automatically determine which tiers a document belongs in"""
        tiers = []
        
        importance = doc_metadata.get('importance', 5)
        
        # Tier 1: Top 100 most important documents
        if importance >= 9:
            tiers.append(1)
        
        # Tier 2: All documents
        tiers.append(2)
        
        # Tier 3: Documents with entities/relationships
        if doc_metadata.get('has_entities', True):
            tiers.append(3)
        
        # Tier 4: Always store originals
        tiers.append(4)
        
        return tiers
    
    # ============= SYSTEM MANAGEMENT =============
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            **self.stats,
            'tier_status': {
                1: self.tier1.get_status() if self._tier1 else 'Not loaded',
                2: self.tier2.get_status() if self._tier2 else 'Not loaded',
                3: 'Active' if self.tier3 else 'Not provided',
                4: self.tier4.get_status() if self._tier4 else 'Not loaded',
                5: self.tier5.get_status() if self._tier5 else 'Not loaded'
            },
            'memory_efficiency': self._calculate_efficiency()
        }
    
    def _calculate_efficiency(self) -> float:
        """Calculate memory system efficiency (0-1)"""
        if self.stats['total_queries'] == 0:
            return 0.0
        
        # Higher tier hits (1, 5) are more efficient
        weighted_hits = (
            self.stats['tier1_hits'] * 3 +
            self.stats['tier5_hits'] * 3 +
            self.stats['tier3_hits'] * 2 +
            self.stats['tier2_hits'] * 1 +
            self.stats['tier4_hits'] * 0.5
        )
        
        return min(weighted_hits / (self.stats['total_queries'] * 3), 1.0)
    
    def optimise_tiers(self):
        """Run optimisation across all tiers"""
        self.logger.info("Optimising memory tiers...")
        
        # Tier 2: Rebuild vector indices
        if self._tier2:
            self.tier2.optimise_indices()
        
        # Tier 3: Vacuum knowledge graph database
        if self.tier3:
            # Your existing knowledge_graph likely has this
            pass
        
        # Tier 5: Clear old cache entries
        if self._tier5:
            self.tier5.clear_old_cache(days=30)
        
        self.logger.info("Optimisation complete")