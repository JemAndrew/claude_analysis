#!/usr/bin/env python3
"""
Main Orchestration Engine for 4-Pass Litigation Intelligence
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


class LitigationOrchestrator:
    """Main system orchestrator for 4-pass litigation analysis"""
    
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
        
        # Hierarchical memory system (optional)
        self.memory_enabled = False
        self.memory_system = None
        try:
            from memory.hierarchical_system import HierarchicalMemory
            self.memory_system = HierarchicalMemory(self.config, self.knowledge_graph)
            self.memory_enabled = True
            print("✅ Hierarchical Memory System ACTIVE")
        except ImportError:
            print("ℹ️  Hierarchical Memory System not available (optional)")
        except Exception as e:
            print(f"⚠️  Memory system initialisation failed: {e}")
        
        # State tracking
        self.state = {
            'passes_completed': [],
            'current_pass': None,
            'total_cost_gbp': 0.0
        }
        self._load_state()
        
        # Create output directories
        self.config.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = self.config.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # MAIN EXECUTION METHOD
    # ========================================================================
    
    def execute_complete_analysis(self) -> Dict:
        """Execute complete 4-pass analysis"""
        
        print("\n" + "="*70)
        print("4-PASS LITIGATION INTELLIGENCE ANALYSIS")
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
        
        # Pass 2: Deep Analysis
        print("\n🎯 Starting Pass 2: Deep Analysis")
        priority_docs = results['passes']['pass_1']['priority_documents']
        results['passes']['pass_2'] = self.pass_executor.execute_pass_2_deep_analysis(priority_docs)
        self.state['passes_completed'].append('2')
        self._save_state()
        
        # Pass 3: Investigations
        print("\n🎯 Starting Pass 3: Autonomous Investigations")
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
        
        # Save final results
        self._save_final_results(results)
        
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
    # LEGACY SUPPORT (Phase 0 - foundation building)
    # ========================================================================
    
    def execute_phase_0_foundation(self) -> Dict:
        """
        Execute Phase 0: Knowledge foundation
        KEPT for backwards compatibility - builds legal/case knowledge
        """
        
        print("\n" + "="*70)
        print("PHASE 0: KNOWLEDGE FOUNDATION")
        print("="*70)
        
        # Load legal knowledge and case context
        legal_docs = self.document_loader.load_directory(
            self.config.legal_knowledge_dir,
            doc_types=['.pdf', '.txt', '.docx']
        )
        
        case_docs = self.document_loader.load_directory(
            self.config.case_context_dir,
            doc_types=['.pdf', '.txt', '.docx']
        )
        
        all_docs = legal_docs + case_docs
        
        print(f"  Legal knowledge: {len(legal_docs)} documents")
        print(f"  Case context: {len(case_docs)} documents")
        print(f"  Total: {len(all_docs)} documents")
        
        # Create batches
        batches = []
        batch_size = 30
        for i in range(0, len(all_docs), batch_size):
            batches.append(all_docs[i:i+batch_size])
        
        print(f"  Processing in {len(batches)} batches")
        
        results = {
            'phase': '0',
            'documents_processed': len(all_docs),
            'batches': len(batches)
        }
        
        # Process each batch
        context = {}
        for i, batch in enumerate(batches):
            print(f"\n  Batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            prompt = self.autonomous_prompts.knowledge_synthesis_prompt(
                legal_knowledge=batch[:15],
                case_context=batch[15:],
                existing_knowledge=context
            )
            
            cacheable_context = f"{self.config.hallucination_prevention}\n\nBatch {i+1}/{len(batches)} of knowledge foundation."
            
            try:
                response, metadata = self.api_client.call_claude_with_cache(
                    prompt=prompt,
                    cacheable_context=cacheable_context,
                    task_type='knowledge_synthesis',
                    phase='0'
                )
                
                # Update context for next batch
                context = self.knowledge_graph.get_context_for_analysis()
                
            except Exception as e:
                print(f"    ⚠️  Error in batch {i+1}: {str(e)[:100]}")
                continue
        
        # Save results
        output_dir = self.config.analysis_dir / "phase_0"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "phase_0_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print("\n  ✅ Phase 0 complete: Knowledge foundation built")
        
        return results
    
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
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_status(self) -> Dict:
        """Get current analysis status"""
        return {
            'passes_completed': self.state.get('passes_completed', []),
            'current_pass': self.state.get('current_pass'),
            'total_cost_gbp': self.api_client.get_total_cost_gbp(),
            'knowledge_graph_stats': self.knowledge_graph.get_statistics()
        }
    
    def estimate_costs(self) -> Dict:
        """Estimate costs for complete 4-pass analysis"""
        # Load document counts
        disclosure_count = len(list(self.config.disclosure_dir.glob("**/*.pdf")))
        
        return {
            'pass_1_triage': {
                'documents': disclosure_count,
                'estimated_cost_gbp': disclosure_count * 0.003,  # £0.003 per doc with Haiku
                'estimated_time_hours': disclosure_count / 1200  # 1200 docs/hour
            },
            'pass_2_deep_analysis': {
                'documents': 500,
                'estimated_cost_gbp': 120,
                'estimated_time_hours': 15
            },
            'pass_3_investigations': {
                'estimated_investigations': 30,
                'estimated_cost_gbp': 100,
                'estimated_time_hours': 10
            },
            'pass_4_synthesis': {
                'estimated_cost_gbp': 50,
                'estimated_time_hours': 5
            },
            'total_estimated_cost_gbp': 270 + (disclosure_count * 0.003),
            'total_estimated_time_hours': 30 + (disclosure_count / 1200)
        }