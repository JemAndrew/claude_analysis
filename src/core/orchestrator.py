#!/usr/bin/env python3
"""
ENHANCED Orchestrator with Integrated Memory & Document Retrieval
Replace: src/core/orchestrator.py
British English throughout - Lismore v Process Holdings
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

# NEW: Import document retrieval
from utils.document_retrieval import DocumentRetrieval


class LitigationOrchestrator:
    """
    Enhanced orchestrator with:
    - Integrated document retrieval (BM25)
    - Practical memory system (context management)
    - Better knowledge retention
    """
    
    def __init__(self, config_override: Dict = None):
        """Initialise orchestrator with all components"""
        self.config = Config()
        if config_override:
            for key, value in config_override.items():
                setattr(self.config, key, value)
        
        # Initialise core components
        self.knowledge_graph = KnowledgeGraph(self.config)
        self.api_client = ClaudeClient(self.config)
        self.pass_executor = PassExecutor(self.config, self)
        
        # Initialise prompt systems
        self.autonomous_prompts = AutonomousPrompts(self.config)
        self.deliverables_prompts = DeliverablesPrompts(self.config)
        
        # Document loader
        self.document_loader = DocumentLoader(self.config)
        
        # ====================================================================
        # NEW: INTEGRATED DOCUMENT RETRIEVAL
        # ====================================================================
        self.retrieval_system = None
        try:
            # Initialise after documents are loaded
            # Will be built in first pass that needs it
            print("✅ Document Retrieval System ready (will build index on first use)")
        except Exception as e:
            print(f"⚠️  Document Retrieval unavailable: {e}")
        
        # ====================================================================
        # ENHANCED: PRACTICAL MEMORY SYSTEM
        # ====================================================================
        # Instead of complex 5-tier system that's never used,
        # we use a simple but effective context management system
        
        self.memory_cache = {
            'recent_findings': [],      # Last 50 findings for quick access
            'critical_breaches': [],    # High-confidence breaches
            'key_contradictions': [],   # Severe contradictions
            'timeline_summary': [],     # Chronological events
            'investigation_cache': {}   # Investigation results by topic
        }
        
        # Context window management
        self.context_budget = {
            'max_tokens': 150000,           # Claude's context limit
            'allocated_pleadings': 80000,   # Static pleadings (cached)
            'allocated_findings': 50000,    # Accumulated findings
            'allocated_documents': 20000    # Current batch documents
        }
        
        print("✅ Enhanced Memory System ACTIVE")
        print(f"   Context budget: {self.context_budget['max_tokens']:,} tokens")
        print(f"   Pleadings (cached): {self.context_budget['allocated_pleadings']:,} tokens")
        print(f"   Dynamic findings: {self.context_budget['allocated_findings']:,} tokens")
        
        # State tracking
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
    
    # ========================================================================
    # ENHANCED: MEMORY MANAGEMENT
    # ========================================================================
    
    def update_memory_cache(self, new_findings: Dict):
        """
        Update in-memory cache with new findings
        This is what ACTUALLY gets used for context in next iteration
        
        Args:
            new_findings: Results from Pass 2 iteration or Pass 3 investigation
        """
        # Add breaches to cache
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
        
        # Add timeline events
        for event in new_findings.get('timeline_events', []):
            self.memory_cache['timeline_summary'].append({
                'date': event.get('date'),
                'description': event['description'][:150]
            })
        
        # Keep only most recent/relevant
        self.memory_cache['critical_breaches'] = \
            sorted(self.memory_cache['critical_breaches'], 
                   key=lambda x: x['confidence'], reverse=True)[:20]
        
        self.memory_cache['key_contradictions'] = \
            sorted(self.memory_cache['key_contradictions'],
                   key=lambda x: x['severity'], reverse=True)[:15]
        
        self.memory_cache['timeline_summary'] = \
            sorted(self.memory_cache['timeline_summary'],
                   key=lambda x: x.get('date', ''), reverse=True)[:30]
        
        # Update state
        self.state['total_findings'] = (
            len(self.memory_cache['critical_breaches']) +
            len(self.memory_cache['key_contradictions']) +
            len(self.memory_cache['timeline_summary'])
        )
        
        # Calculate memory efficiency (0-1)
        # Higher = more high-quality findings with less redundancy
        total_items = self.state['total_findings']
        avg_confidence = sum(b['confidence'] for b in self.memory_cache['critical_breaches']) / max(len(self.memory_cache['critical_breaches']), 1)
        self.state['memory_efficiency'] = min(1.0, (total_items / 100) * avg_confidence)
    
    def get_optimised_context(self, iteration: int = 0) -> Dict:
        """
        Get optimised context within token budget
        This replaces the unused HierarchicalMemory system
        
        Returns:
            Structured context ready for Claude API
        """
        context = {
            'iteration': iteration,
            'critical_breaches': self.memory_cache['critical_breaches'][:10],
            'key_contradictions': self.memory_cache['key_contradictions'][:8],
            'timeline_summary': self.memory_cache['timeline_summary'][:15],
            'statistics': {
                'total_findings': self.state['total_findings'],
                'memory_efficiency': self.state['memory_efficiency'],
                'breaches_identified': len(self.memory_cache['critical_breaches']),
                'contradictions_found': len(self.memory_cache['key_contradictions']),
                'timeline_events': len(self.memory_cache['timeline_summary'])
            }
        }
        
        return context
    
    def cache_investigation_result(self, topic: str, result: Dict):
        """Cache investigation result for quick retrieval"""
        self.memory_cache['investigation_cache'][topic] = {
            'conclusion': result.get('conclusion', '')[:300],
            'confidence': result.get('confidence', 0.0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Keep only recent 20 investigations
        if len(self.memory_cache['investigation_cache']) > 20:
            # Remove oldest
            sorted_investigations = sorted(
                self.memory_cache['investigation_cache'].items(),
                key=lambda x: x[1]['timestamp']
            )
            self.memory_cache['investigation_cache'] = dict(sorted_investigations[-20:])
    
    # ========================================================================
    # DOCUMENT RETRIEVAL INTEGRATION
    # ========================================================================
    
    def get_retrieval_system(self) -> DocumentRetrieval:
        """
        Get document retrieval system (lazy initialisation)
        Builds BM25 index on first call
        """
        if self.retrieval_system is None:
            print("\n📚 Building document retrieval index...")
            self.retrieval_system = DocumentRetrieval(self.knowledge_graph, self.config)
        
        return self.retrieval_system
    
    def search_documents(self, query: str, top_k: int = 20) -> List[str]:
        """
        Search for relevant documents using BM25
        
        Args:
            query: Search query
            top_k: Number of documents to return
            
        Returns:
            List of document IDs
        """
        retrieval = self.get_retrieval_system()
        return retrieval.get_doc_ids_only(query, top_k)
    
    # ========================================================================
    # MAIN EXECUTION METHOD
    # ========================================================================
    
    def execute_complete_analysis(self) -> Dict:
        """Execute complete 4-pass analysis with enhanced memory"""
        
        print("\n" + "="*70)
        print("4-PASS LITIGATION INTELLIGENCE ANALYSIS")
        print("Enhanced with Integrated Memory & Retrieval")
        print("Lismore v Process Holdings")
        print("="*70)
        
        results = {
            'analysis_started': datetime.now().isoformat(),
            'passes': {}
        }
        
        # Pass 1: Triage
        print("\n🎯 Starting Pass 1: Triage & Prioritisation")
        results['passes']['pass_1'] = self.pass_executor.execute_pass_1_triage()
        self.state['passes_completed'].append('1')
        self._save_state()
        
        # Pass 2: Deep Analysis (with memory updates)
        print("\n🎯 Starting Pass 2: Deep Analysis with Memory")
        priority_docs = results['passes']['pass_1']['priority_documents']
        results['passes']['pass_2'] = self.pass_executor.execute_pass_2_deep_analysis(priority_docs)
        
        # Update memory after Pass 2
        print("\n💾 Updating memory cache with Pass 2 findings...")
        self.update_memory_cache(results['passes']['pass_2'])
        
        self.state['passes_completed'].append('2')
        self._save_state()
        
        # Pass 3: Investigations (with document retrieval)
        print("\n🎯 Starting Pass 3: Autonomous Investigations")
        print("   Using BM25 retrieval for optimal document selection")
        results['passes']['pass_3'] = self.pass_executor.execute_pass_3_investigations()
        self.state['passes_completed'].append('3')
        self._save_state()
        
        # Pass 4: Synthesis & Deliverables
        print("\n🎯 Starting Pass 4: Synthesis & Deliverables")
        results['passes']['pass_4'] = self.pass_executor.execute_pass_4_synthesis()
        self.state['passes_completed'].append('4')
        self._save_state()
        
        results['analysis_completed'] = datetime.now().isoformat()
        results['total_passes_completed'] = len(self.state['passes_completed'])
        
        # Add memory statistics
        results['memory_statistics'] = {
            'total_findings': self.state['total_findings'],
            'memory_efficiency': self.state['memory_efficiency'],
            'critical_breaches': len(self.memory_cache['critical_breaches']),
            'key_contradictions': len(self.memory_cache['key_contradictions']),
            'timeline_events': len(self.memory_cache['timeline_summary']),
            'cached_investigations': len(self.memory_cache['investigation_cache'])
        }
        
        # Save final results
        self._save_final_results(results)
        
        # Print memory summary
        print("\n" + "="*70)
        print("MEMORY SYSTEM SUMMARY")
        print("="*70)
        print(f"Total findings retained: {self.state['total_findings']}")
        print(f"Memory efficiency: {self.state['memory_efficiency']:.2%}")
        print(f"Critical breaches: {len(self.memory_cache['critical_breaches'])}")
        print(f"Key contradictions: {len(self.memory_cache['key_contradictions'])}")
        print(f"Timeline events: {len(self.memory_cache['timeline_summary'])}")
        
        return results
    
    # ========================================================================
    # INDIVIDUAL PASS EXECUTION (for testing/debugging)
    # ========================================================================
    
    def execute_single_pass(self, pass_num: str) -> Dict:
        """Execute single pass for testing"""
        
        print(f"\n{'='*70}")
        print(f"EXECUTING PASS {pass_num}")
        print(f"{'='*70}\n")
        
        self.state['current_pass'] = pass_num
        
        if pass_num == '1':
            result = self.pass_executor.execute_pass_1_triage()
        elif pass_num == '2':
            # Load priority docs from Pass 1
            pass_1_results = self._load_pass_results('1')
            priority_docs = pass_1_results.get('priority_documents', [])
            if not priority_docs:
                raise Exception("Pass 1 must be completed first")
            result = self.pass_executor.execute_pass_2_deep_analysis(priority_docs)
            
            # Update memory after Pass 2
            self.update_memory_cache(result)
            
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
    # INVESTIGATION SPAWNING (used by Pass 2 & 3)
    # ========================================================================
    
    def spawn_investigation(self, 
                          trigger_type: str,
                          trigger_data: Dict,
                          priority: float,
                          parent_id: str = None) -> str:
        """
        Spawn new investigation thread
        Used by pass_executor when critical findings discovered
        """
        
        from core.investigation_queue import Investigation
        
        investigation = Investigation(
            topic=trigger_data.get('topic', 'Investigation'),
            priority=int(priority),
            trigger_data=trigger_data,
            parent_id=parent_id
        )
        
        self.pass_executor.investigation_queue.add(investigation)
        
        return investigation.get_id()
    
    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================
    
    def _load_state(self):
        """Load orchestrator state from disk"""
        state_file = self.config.output_dir / "orchestrator_state.json"
        
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
    
    def _save_state(self):
        """Save orchestrator state to disk"""
        state_file = self.config.output_dir / "orchestrator_state.json"
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def _load_pass_results(self, pass_num: str) -> Dict:
        """Load results from a previous pass"""
        results_file = self.config.analysis_dir / f"pass_{pass_num}" / f"pass_{pass_num}_results.json"
        
        if not results_file.exists():
            return {}
        
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_final_results(self, results: Dict):
        """Save final complete analysis results"""
        output_file = self.config.analysis_dir / "complete_analysis_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Final results saved: {output_file}")
    
    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            'passes_completed': self.state['passes_completed'],
            'current_pass': self.state.get('current_pass'),
            'total_cost_gbp': self.state.get('total_cost_gbp', 0.0),
            'total_findings': self.state.get('total_findings', 0),
            'memory_efficiency': self.state.get('memory_efficiency', 0.0),
            'knowledge_graph_stats': self.knowledge_graph.get_statistics()
        }