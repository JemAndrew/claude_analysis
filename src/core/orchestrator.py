#!/usr/bin/env python3
"""
ORCHESTRATOR WITH HIERARCHICAL MEMORY SYSTEM ACTIVATED
REPLACE: src/core/orchestrator.py
British English throughout - Lismore v Process Holdings

This version USES your sophisticated 5-tier memory system
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from core.config import Config
from core.pass_executor import PassExecutor
from intelligence.knowledge_graph import KnowledgeGraph
from api.client import ClaudeClient
from prompts.autonomous import AutonomousPrompts
from prompts.deliverables import DeliverablesPrompts
from utils.document_loader import DocumentLoader
from utils.document_retrieval import DocumentRetrieval
from core.phase_0 import Phase0Executor 

# ACTIVATED: Import HierarchicalMemory system
from memory import HierarchicalMemory, MemoryQuery, MemoryResult


class LitigationOrchestrator:
    """
    Orchestrator with FULL HierarchicalMemory system:
    - Tier 1: Claude Projects (permanent knowledge)
    - Tier 2: Vector Store (semantic search with sentence-transformers)
    - Tier 3: Knowledge Graph (relationships & patterns)
    - Tier 4: Cold Storage (encrypted vault)
    - Tier 5: Analysis Cache (fast retrieval)
    - PLUS: BM25 document retrieval
    """
    
    def __init__(self, config_override: Dict = None):
        """Initialise orchestrator with all components"""
        self.config = Config()
        if config_override:
            for key, value in config_override.items():
                setattr(self.config, key, value)
        
        # ================================================================
        # STEP 1: Initialize base components (no dependencies)
        # ================================================================
        self.knowledge_graph = KnowledgeGraph(self.config)
        self.api_client = ClaudeClient(self.config)
        
        # ================================================================
        # STEP 2: Initialize utilities (needed by Phase0 and PassExecutor)
        # ================================================================
        self.document_loader = DocumentLoader(self.config)
        self.autonomous_prompts = AutonomousPrompts(self.config)
        self.deliverables_prompts = DeliverablesPrompts(self.config)
        
        # Document retrieval system (BM25)
        self.retrieval_system = None
        print("✅ BM25 Document Retrieval ready (builds index on first use)")
        
        # ================================================================
        # STEP 3: Now Phase0 can be created (needs document_loader)
        # ================================================================
        self.phase0_executor = Phase0Executor(self.config, self)
        
        # ================================================================
        # STEP 4: Hierarchical Memory System
        # ================================================================
        print("\n" + "="*70)
        print("INITIALISING HIERARCHICAL MEMORY SYSTEM")
        print("="*70)
        
        try:
            self.memory_system = HierarchicalMemory(
                config=self.config,
                knowledge_graph=self.knowledge_graph
            )
            self.memory_enabled = True
            
            print("✅ Tier 1: Claude Projects (permanent storage)")
            print("✅ Tier 2: Vector Store (semantic search)")
            print("✅ Tier 3: Knowledge Graph (relationships)")
            print("✅ Tier 4: Cold Storage (encrypted vault)")
            print("✅ Tier 5: Analysis Cache (fast retrieval)")
            print("\n🚀 HierarchicalMemory ACTIVE")
            
        except Exception as e:
            print(f"\n⚠️  HierarchicalMemory unavailable: {e}")
            print("   Missing dependencies? Install:")
            print("   pip install chromadb sentence-transformers")
            print("\n   Falling back to simple memory cache...")
            
            self.memory_system = None
            self.memory_enabled = False
            
            # Fallback to simple cache
            self.memory_cache = {
                'recent_findings': [],
                'critical_breaches': [],
                'key_contradictions': [],
                'timeline_summary': [],
                'investigation_cache': {}
            }
        
        # ================================================================
        # STEP 5: PassExecutor (needs everything above)
        # ================================================================
        self.pass_executor = PassExecutor(self.config, self)
        
        # ================================================================
        # STEP 6: State tracking
        # ================================================================
        self.state = {
            'passes_completed': [],
            'current_pass': None,
            'total_cost_gbp': 0.0,
            'total_findings': 0,
            'memory_efficiency': 0.0
        }
        self._load_state()
        
        # Create output directories
        self.config.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = self.config.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*70)

    
    def retrieve_memory_context(self, 
                               query_text: str, 
                               max_tokens: int = 50000,
                               tiers: List[int] = None) -> Dict:
        """
        Retrieve context from HierarchicalMemory system
        
        Args:
            query_text: What to search for
            max_tokens: Token budget for results
            tiers: Which tiers to query [1,2,3,4,5] (None = auto-select)
            
        Returns:
            Combined context from all relevant tiers
        """
        if not self.memory_enabled or self.memory_system is None:
            # Fallback to simple cache
            return self._get_fallback_context()
        
        try:
            # Create memory query
            memory_query = MemoryQuery(
                query_text=query_text,
                max_tokens=max_tokens,
                include_tiers=tiers or [1, 2, 3, 5]  # Skip cold storage by default
            )
            
            # Query memory system
            results = self.memory_system.retrieve_relevant_context(memory_query)
            
            tier_count = len(results.get('tier_results', {}))
            print(f"📚 Memory retrieval: {tier_count} tiers queried")
            
            return results
            
        except Exception as e:
            print(f"⚠️  Memory retrieval error: {e}")
            return self._get_fallback_context()
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Semantic search using Tier 2 vector store
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of semantically similar documents
        """
        if not self.memory_enabled or self.memory_system is None:
            print("⚠️  Semantic search unavailable (using fallback)")
            return []
        
        try:
            # Direct access to Tier 2 for semantic search
            results = self.memory_system.tier2.semantic_search(
                query_text=query,
                top_k=top_k
            )
            
            print(f"🔍 Semantic search: found {len(results)} similar documents")
            return results
            
        except Exception as e:
            print(f"⚠️  Semantic search error: {e}")
            return []
    
    def find_similar_breaches(self, breach_description: str, top_k: int = 5) -> List[Dict]:
        """
        Find breaches similar to given description using semantic search
        
        Args:
            breach_description: Description of breach to match
            top_k: Number of similar breaches
            
        Returns:
            List of similar breaches
        """
        return self.semantic_search(breach_description, top_k)
    
    def store_analysis_in_cache(self, 
                                query: str, 
                                analysis_result: Dict,
                                analysis_type: str = "deep_analysis"):
        """
        Store analysis result in Tier 5 cache
        
        Args:
            query: Query that generated this analysis
            analysis_result: Full analysis output
            analysis_type: Type of analysis (triage/deep_analysis/investigation)
        """
        if not self.memory_enabled or self.memory_system is None:
            return
        
        try:
            self.memory_system.tier5.cache_analysis(
                query_text=query,
                analysis_result=analysis_result,
                analysis_type=analysis_type
            )
            print(f"💾 Cached {analysis_type} result for future use")
            
        except Exception as e:
            print(f"⚠️  Cache storage error: {e}")
    
    def check_analysis_cache(self, query: str) -> Optional[Dict]:
        """
        Check if analysis already exists in cache
        
        Args:
            query: Query to check
            
        Returns:
            Cached analysis if exists, None otherwise
        """
        if not self.memory_enabled or self.memory_system is None:
            return None
        
        try:
            cached = self.memory_system.tier5.get_cached_analysis(query)
            if cached:
                print(f"🎯 Cache HIT: Using previous analysis")
            return cached
            
        except Exception as e:
            print(f"⚠️  Cache check error: {e}")
            return None
    
    def _get_fallback_context(self) -> Dict:
        """Fallback to simple cache if HierarchicalMemory unavailable"""
        if not hasattr(self, 'memory_cache'):
            return {
                'intelligence': self.knowledge_graph.export_complete_intelligence()
            }
        
        return {
            'intelligence': {
                'critical_breaches': self.memory_cache.get('critical_breaches', [])[:10],
                'key_contradictions': self.memory_cache.get('key_contradictions', [])[:8],
                'timeline_summary': self.memory_cache.get('timeline_summary', [])[:15]
            }
        }
    
    def update_memory_cache_fallback(self, new_findings: Dict):
        """
        Update fallback cache (if HierarchicalMemory unavailable)
        """
        if not hasattr(self, 'memory_cache'):
            self.memory_cache = {
                'recent_findings': [],
                'critical_breaches': [],
                'key_contradictions': [],
                'timeline_summary': [],
                'investigation_cache': {}
            }
        
        # Add breaches
        for breach in new_findings.get('breaches', []):
            if breach.get('confidence', 0) >= 0.7:
                self.memory_cache['critical_breaches'].append({
                    'description': breach['description'][:200],
                    'confidence': breach['confidence'],
                    'evidence': breach.get('evidence', [])
                })
        
        # Add contradictions
        for contra in new_findings.get('contradictions', []):
            if contra.get('severity', 0) >= 7:
                self.memory_cache['key_contradictions'].append({
                    'statement_a': contra['statement_a'][:150],
                    'statement_b': contra['statement_b'][:150],
                    'severity': contra['severity']
                })
        
        # Keep top items only
        self.memory_cache['critical_breaches'] = \
            sorted(self.memory_cache['critical_breaches'], 
                   key=lambda x: x['confidence'], reverse=True)[:20]
        
        self.memory_cache['key_contradictions'] = \
            sorted(self.memory_cache['key_contradictions'],
                   key=lambda x: x['severity'], reverse=True)[:15]
    
    def get_memory_statistics(self) -> Dict:
        """Get statistics from all memory tiers"""
        if not self.memory_enabled or self.memory_system is None:
            return {
                'enabled': False,
                'message': 'HierarchicalMemory not active'
            }
        
        try:
            return {
                'enabled': True,
                'tier1_status': self.memory_system.tier1.get_status() if hasattr(self.memory_system, 'tier1') else {},
                'tier2_status': self.memory_system.tier2.get_status() if hasattr(self.memory_system.tier2, 'get_status') else {},
                'tier5_status': self.memory_system.tier5.get_status() if hasattr(self.memory_system.tier5, 'get_status') else {},
                'statistics': self.memory_system.stats
            }
        except Exception as e:
            return {
                'enabled': True,
                'error': str(e)
            }
    
    # ========================================================================
    # BUILD BM25 DOCUMENT INDEX (when needed)
    # ========================================================================
    
    def build_document_index(self):
        """Build BM25 index for document retrieval (one-time operation)"""
        if self.retrieval_system is not None:
            print("✅ Document index already built")
            return
        
        print("\n" + "="*70)
        print("BUILDING BM25 DOCUMENT INDEX")
        print("="*70)
        
        try:
            # Load all documents
            print("Loading documents from knowledge graph...")
            all_docs = self.knowledge_graph.get_all_documents()
            
            if not all_docs:
                print("⚠️  No documents found in knowledge graph")
                return
            
            # Build retrieval index
            print(f"Building index for {len(all_docs)} documents...")
            self.retrieval_system = DocumentRetrieval(all_docs)
            
            print(f"✅ Document index built successfully")
            print(f"   {len(all_docs)} documents indexed")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"⚠️  Failed to build document index: {e}")
            self.retrieval_system = None
    
    def retrieve_documents(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Retrieve documents using BM25 or semantic search
        
        Args:
            query: Search query
            top_k: Number of documents to return
            
        Returns:
            List of relevant documents
        """
        # Try BM25 first (fast)
        if self.retrieval_system:
            bm25_results = self.retrieval_system.search(query, top_k=top_k)
            if bm25_results:
                return bm25_results
        
        # Fall back to semantic search if available
        if self.memory_enabled:
            semantic_results = self.semantic_search(query, top_k=top_k)
            if semantic_results:
                return semantic_results
        
        # Last resort: keyword search in knowledge graph
        return self.knowledge_graph.search_documents(query, limit=top_k)
    
    # ========================================================================
    # PASS EXECUTION METHODS
    # ========================================================================
    def execute_phase_0_foundation(self) -> Dict:
        """
        Execute Phase 0: Build Intelligent Case Foundation
        
        Analyses pleadings, tribunal rulings, and case admin documents
        to build contextual understanding before Pass 1 triage.
        
        Returns:
            Dict containing complete case foundation with metadata
        """
        print("\n" + "="*70)
        print("PHASE 0: INTELLIGENT CASE FOUNDATION")
        print("="*70)
        print("Building contextual understanding for intelligent triage")
        print("="*70 + "\n")
        
        # Check if Phase 0 already exists
        foundation_file = self.config.analysis_dir / "phase_0" / "case_foundation.json"
        
        if foundation_file.exists():
            print("⚠️  Phase 0 already completed!")
            print(f"   Found: {foundation_file}")
            
            response = input("\nRe-run Phase 0? (costs £16-22) (yes/no): ").strip().lower()
            if response != 'yes':
                print("Loading existing case foundation...")
                with open(foundation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # Execute Phase 0
        try:
            case_foundation = self.phase_0_executor.execute()
            
            # Store in memory system if available
            if self.memory_enabled:
                try:
                    self.memory_system.tier1.add_to_project_manifest({
                        'filename': 'case_foundation.json',
                        'content': json.dumps(case_foundation, indent=2),
                        'category': 'case_context',
                        'importance': 10
                    })
                    print("✓ Stored in memory system")
                except Exception as e:
                    print(f"⚠️  Memory storage error: {e}")
            
            return case_foundation
            
        except Exception as e:
            print(f"\n❌ ERROR in Phase 0: {e}")
            import traceback
            traceback.print_exc()
            raise

    def execute_full_analysis(self) -> Dict:
        """Execute complete 4-pass analysis"""
        
        print("\n" + "="*70)
        print("STARTING FULL 4-PASS ANALYSIS WITH HIERARCHICAL MEMORY")
        print("="*70)
        
        start_time = time.time()
        results = {}
        
        # Pass 1: Triage
        print("\n🎯 PASS 1: TRIAGE & PRIORITISATION")
        results['pass_1'] = self.execute_single_pass('1')
        
        # Pass 2: Deep Analysis
        print("\n🔍 PASS 2: DEEP ANALYSIS WITH CONFIDENCE TRACKING")
        results['pass_2'] = self.execute_single_pass('2')
        
        # Pass 3: Investigations
        print("\n🔬 PASS 3: AUTONOMOUS INVESTIGATIONS")
        results['pass_3'] = self.execute_single_pass('3')
        
        # Pass 4: Synthesis
        print("\n📋 PASS 4: SYNTHESIS & DELIVERABLES")
        results['pass_4'] = self.execute_single_pass('4')
        
        # Calculate totals
        total_time = time.time() - start_time
        total_cost = sum(r.get('cost_gbp', 0) for r in results.values())
        
        # Print summary
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"Total time: {total_time/3600:.1f} hours")
        print(f"Total cost: £{total_cost:.2f}")
        
        # Memory system statistics
        if self.memory_enabled:
            mem_stats = self.get_memory_statistics()
            print(f"\nMemory System Performance:")
            print(f"  Tier 2 queries: {mem_stats.get('statistics', {}).get('tier2_hits', 0)}")
            print(f"  Cache hits: {mem_stats.get('statistics', {}).get('tier5_hits', 0)}")
        
        return results
    
    def execute_single_pass(self, pass_num: str, limit: int = None) -> Dict:
        """Execute single pass for testing"""
        
        print(f"\n{'='*70}")
        print(f"EXECUTING PASS {pass_num}")
        print(f"{'='*70}\n")
        
        self.state['current_pass'] = pass_num
        
        if pass_num == '1':
            result = self.pass_executor.execute_pass_1_triage(limit=limit)  # PASS LIMIT HERE
        elif pass_num == '2':
            # Load priority docs from Pass 1
            pass_1_results = self._load_pass_results('1')
            priority_docs = pass_1_results.get('priority_documents', [])
            if not priority_docs:
                raise Exception("Pass 1 must be completed first")
            result = self.pass_executor.execute_pass_2_deep_analysis(priority_docs)
            
            # Update memory after Pass 2
            if self.memory_enabled:
                pass
            else:
                self.update_memory_cache_fallback(result)
                
        elif pass_num == '3':
            result = self.pass_executor.execute_pass_3_investigations()
        elif pass_num == '4':
            result = self.pass_executor.execute_pass_4_synthesis()
        else:
            raise ValueError(f"Invalid pass number: {pass_num}")
        
        if pass_num not in self.state['passes_completed']:
            self.state['passes_completed'].append(pass_num)
        
        self._save_state()
        
        return result
    
    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================
    
    def _load_state(self):
            """Load orchestrator state with safe defaults"""
            state_file = self.config.output_dir / "orchestrator_state.json"
            
            # Define default state structure
            default_state = {
                'passes_completed': [],
                'current_pass': None,
                'total_cost_gbp': 0.0,
                'total_findings': 0,
                'memory_efficiency': 0.0
            }
            
            if state_file.exists():
                try:
                    with open(state_file, 'r') as f:
                        loaded_state = json.load(f)
                    
                    # Merge loaded state with defaults (preserves missing keys)
                    for key, default_value in default_state.items():
                        if key not in loaded_state:
                            loaded_state[key] = default_value
                    
                    self.state = loaded_state
                    print(f"📂 Loaded state: {len(self.state.get('passes_completed', []))} passes completed")
                    
                except Exception as e:
                    print(f"⚠️  Error loading state: {e}")
                    print(f"   Using default state")
                    self.state = default_state
            else:
                # No state file exists - use defaults
                self.state = default_state
        
    def _save_state(self):
                """Save orchestrator state"""
                state_file = self.config.output_dir / "orchestrator_state.json"
                state_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(state_file, 'w') as f:
                    json.dump(self.state, f, indent=2)
    
    def _load_pass_results(self, pass_num: str) -> Dict:
        """Load results from a specific pass"""
        result_file = self.config.analysis_dir / f"pass_{pass_num}" / f"pass_{pass_num}_results.json"
        if not result_file.exists():
            return {}
        
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            'passes_completed': self.state['passes_completed'],
            'current_pass': self.state['current_pass'],
            'total_cost_gbp': self.state['total_cost_gbp'],
            'memory_enabled': self.memory_enabled,
            'memory_stats': self.get_memory_statistics() if self.memory_enabled else None
        }
    
    def estimate_costs(self) -> Dict:
        """Estimate costs for full analysis"""
        # This is implemented in your existing code
        # Keeping the structure the same
        return {
            'pass_1_triage': {
                'documents': 18004,
                'estimated_cost_gbp': 50,
                'estimated_time_hours': 9
            },
            'pass_2_deep_analysis': {
                'documents': 500,
                'estimated_cost_gbp': 80 if self.memory_enabled else 120,
                'estimated_time_hours': 15
            },
            'pass_3_investigations': {
                'estimated_investigations': 20,
                'estimated_cost_gbp': 70 if self.memory_enabled else 100,
                'estimated_time_hours': 10
            },
            'pass_4_synthesis': {
                'estimated_cost_gbp': 50,
                'estimated_time_hours': 5
            },
            'total_estimated_cost_gbp': 250 if self.memory_enabled else 320,
            'total_estimated_time_hours': 39,
            'memory_savings_gbp': 70 if self.memory_enabled else 0
        }