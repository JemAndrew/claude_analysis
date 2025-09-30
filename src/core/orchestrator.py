#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
Simplified for maximum Claude autonomy - 3-phase system
British English throughout - Lismore v Process Holdings
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib

from core.config import config
from core.phase_executor import PhaseExecutor
from intelligence.knowledge_graph import KnowledgeGraph
from api.client import ClaudeClient
from api.context_manager import ContextManager
from api.batch_manager import BatchManager
from prompts.autonomous import AutonomousPrompts
from prompts.recursive import RecursivePrompts
from prompts.simplified import SimplifiedPrompts
from utils.document_loader import DocumentLoader


class LitigationOrchestrator:
    """Main system orchestrator for autonomous Claude investigation"""
    
    def __init__(self, config_override: Dict = None):
        """Initialise orchestrator with all components"""
        
        # Override config if needed
        if config_override:
            for key, value in config_override.items():
                setattr(config, key, value)
        
        self.config = config
        
        # Initialise core components
        self.knowledge_graph = KnowledgeGraph(config)
        self.api_client = ClaudeClient(config)
        self.context_manager = ContextManager(config)
        self.batch_manager = BatchManager(config)
        self.phase_executor = PhaseExecutor(config, self)
        
        # Initialise prompt systems
        self.autonomous_prompts = AutonomousPrompts(config)
        self.recursive_prompts = RecursivePrompts(config)
        self.simplified_prompts = SimplifiedPrompts(config)
        
        # Track system state
        self.state = {
            'current_phase': None,
            'phases_completed': [],
            'active_investigations': [],
            'iteration_count': 0,
            'start_time': datetime.now().isoformat(),
            'convergence_metrics': {}
        }
        
        # Load previous state if exists
        self._load_state()
    
    def execute_full_analysis(self, 
                             start_phase: str = '0',
                             max_iterations: int = 10) -> Dict:
        """
        Execute complete analysis with autonomous investigation
        Phase 0: Legal knowledge
        Phase 1: Case understanding
        Phase 2+: Free investigation until convergence
        """
        
        print("=" * 60)
        print("LITIGATION INTELLIGENCE SYSTEM - AUTONOMOUS MODE")
        print(f"Client: Lismore Capital v Process Holdings")
        print(f"Model: {self.config.models['primary']}")
        print(f"Starting at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = {
            'phases': {},
            'investigations': [],
            'synthesis': {},
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'model': self.config.models['primary']
            }
        }
        
        try:
            # Phase 0: Legal Knowledge
            print("\n" + "=" * 60)
            print("PHASE 0: LEGAL KNOWLEDGE MASTERY")
            print("=" * 60)
            
            phase_0_results = self.execute_phase('0')
            results['phases']['0'] = phase_0_results
            
            # Phase 1: Case Understanding
            print("\n" + "=" * 60)
            print("PHASE 1: COMPLETE CASE UNDERSTANDING")
            print("=" * 60)
            
            phase_1_results = self.execute_phase('1')
            results['phases']['1'] = phase_1_results
            
            # Phase 2+: Free Investigation Iterations
            converged = False
            iteration = 2
            
            while not converged and iteration < (2 + max_iterations):
                print("\n" + "=" * 60)
                print(f"PHASE {iteration}: FREE INVESTIGATION (Iteration {iteration - 1})")
                print("=" * 60)
                
                phase_results = self.execute_phase(str(iteration))
                results['phases'][str(iteration)] = phase_results
                
                # Check convergence
                converged = phase_results.get('converged', False)
                
                if converged:
                    print("\n✅ INVESTIGATION CONVERGED - No new critical discoveries")
                    break
                
                iteration += 1
            
            # Final synthesis
            print("\n" + "=" * 60)
            print("FINAL SYNTHESIS")
            print("=" * 60)
            
            synthesis = self._execute_synthesis(results)
            results['synthesis'] = synthesis
            
            # Save complete results
            self._save_results(results)
            
            # Print summary
            self._print_summary(results)
            
            return results
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Save partial results
            results['metadata']['error'] = str(e)
            results['metadata']['error_time'] = datetime.now().isoformat()
            self._save_results(results)
            
            raise
    
    def execute_phase(self, phase: str) -> Dict:
        """
        Execute single phase
        Delegates to phase_executor for actual work
        """
        
        self.state['current_phase'] = phase
        
        print(f"\n📍 Executing Phase {phase}")
        
        # Backup knowledge graph before phase
        self.knowledge_graph.backup_before_phase(phase)
        
        # Get context from knowledge graph
        context = self.knowledge_graph.get_context_for_phase(phase)
        
        # Execute phase via phase_executor
        results = self.phase_executor.execute(phase, context)
        
        # Update knowledge graph with findings (if phase_executor hasn't already)
        # phase_executor now handles this internally
        
        # Mark phase complete
        if phase not in self.state['phases_completed']:
            self.state['phases_completed'].append(phase)
        
        self._save_state()
        return results
    
    def spawn_investigation(self, 
                          trigger_type: str,
                          trigger_data: Dict,
                          priority: float = 5.0) -> str:
        """
        Spawn new investigation thread
        Returns investigation ID
        """
        
        investigation_id = self.knowledge_graph.spawn_investigation(
            trigger_type=trigger_type,
            trigger_data=trigger_data,
            priority=priority
        )
        
        self.state['active_investigations'].append(investigation_id)
        print(f"  → Spawned investigation {investigation_id} (Priority: {priority})")
        
        return investigation_id
    
    def _execute_synthesis(self, results: Dict) -> Dict:
        """
        Execute final strategic synthesis
        Pulls everything together into actionable report
        """
        
        print("  Synthesising all findings...")
        
        # Get all findings from knowledge graph
        all_findings = self.knowledge_graph.get_all_findings()
        
        # Count total investigations
        investigation_count = len(results['phases']) - 2  # Subtract Phase 0 and 1
        
        # Build synthesis prompt
        prompt = self.simplified_prompts.final_synthesis_prompt(
            all_findings=all_findings,
            investigation_count=investigation_count
        )
        
        # Call Claude for synthesis
        print("  🤖 Calling Claude for final synthesis...")
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='synthesis',
            phase='final'
        )
        
        synthesis_results = {
            'narrative': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat(),
            'findings_count': len(all_findings.get('critical_discoveries', []))
        }
        
        # Save synthesis
        self._save_synthesis(synthesis_results)
        
        print(f"  ✅ Synthesis complete")
        print(f"     Tokens: {metadata.get('input_tokens', 0):,} in / {metadata.get('output_tokens', 0):,} out")
        
        return synthesis_results
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory using document loader"""
        
        if not directory.exists():
            print(f"  ⚠️ Directory not found: {directory}")
            return []
        
        loader = DocumentLoader(self.config)
        return loader.load_directory(directory)
    
    def _load_state(self):
        """Load previous state if exists"""
        
        state_file = self.config.output_dir / 'orchestrator_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                    # Only load certain fields
                    self.state['phases_completed'] = saved_state.get('phases_completed', [])
                    print(f"  ℹ️ Loaded previous state: {len(self.state['phases_completed'])} phases completed")
            except Exception as e:
                print(f"  ⚠️ Could not load state: {e}")
    
    def _save_state(self):
        """Save current state"""
        
        state_file = self.config.output_dir / 'orchestrator_state.json'
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ⚠️ Could not save state: {e}")
    
    def _save_synthesis(self, synthesis: Dict):
        """Save synthesis results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        synthesis_file = self.config.reports_dir / f"synthesis_{timestamp}.md"
        
        try:
            with open(synthesis_file, 'w', encoding='utf-8') as f:
                f.write("# Strategic Synthesis - Lismore v Process Holdings\n\n")
                f.write(f"*Generated: {synthesis['timestamp']}*\n\n")
                f.write("---\n\n")
                f.write(synthesis['narrative'])
            
            print(f"  💾 Synthesis saved: {synthesis_file.name}")
        except Exception as e:
            print(f"  ⚠️ Could not save synthesis: {e}")
    
    def _save_results(self, results: Dict):
        """Save complete results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.config.output_dir / f"complete_results_{timestamp}.json"
        
        # Create serialisable version (remove large content)
        serialisable_results = {
            'phases': {},
            'investigations_count': len(results.get('investigations', [])),
            'metadata': results.get('metadata', {}),
            'synthesis_preview': results.get('synthesis', {}).get('narrative', '')[:1000]
        }
        
        # Add phase summaries
        for phase_key, phase_data in results.get('phases', {}).items():
            serialisable_results['phases'][phase_key] = {
                'documents_processed': phase_data.get('documents_processed', 0),
                'discoveries': len(phase_data.get('discoveries', [])),
                'converged': phase_data.get('converged', False),
                'timestamp': phase_data.get('timestamp', '')
            }
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serialisable_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved: {results_file.name}")
        except Exception as e:
            print(f"  ⚠️ Could not save results: {e}")
    
    def _print_summary(self, results: Dict):
        """Print analysis summary"""
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Count phases
        phases_executed = len(results['phases'])
        print(f"\n📊 Phases executed: {phases_executed}")
        
        # Count discoveries
        total_discoveries = 0
        for phase_data in results['phases'].values():
            total_discoveries += len(phase_data.get('discoveries', []))
        
        print(f"🔍 Total discoveries: {total_discoveries}")
        
        # Get statistics from knowledge graph
        stats = self.knowledge_graph.get_statistics()
        print(f"\n📈 Knowledge Graph Statistics:")
        print(f"   - Critical discoveries: {stats.get('critical_discoveries', 0)}")
        print(f"   - Patterns identified: {stats.get('patterns', 0)}")
        print(f"   - Contradictions found: {stats.get('contradictions', 0)}")
        print(f"   - Entities mapped: {stats.get('entities', 0)}")
        
        # API usage
        api_stats = self.api_client.get_usage_statistics()
        print(f"\n💰 API Usage:")
        print(f"   - Total calls: {api_stats['summary']['total_calls']}")
        print(f"   - Input tokens: {api_stats['summary']['total_input_tokens']:,}")
        print(f"   - Output tokens: {api_stats['summary']['total_output_tokens']:,}")
        print(f"   - Estimated cost: ${api_stats['summary']['estimated_cost_usd']:.2f}")
        
        # Timing
        start_time = datetime.fromisoformat(results['metadata']['start_time'])
        end_time = datetime.now()
        duration = end_time - start_time
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        print(f"\n⏱️ Duration: {hours}h {minutes}m")
        
        # Output locations
        print(f"\n📁 Outputs:")
        print(f"   - Reports: {self.config.reports_dir}")
        print(f"   - Knowledge: {self.config.knowledge_dir}")
        print(f"   - Full results: {self.config.output_dir}")
        
        print("\n" + "=" * 60)
        print("System ready for litigation deployment")
        print("=" * 60 + "\n")
    
    def get_status(self) -> Dict:
        """Get current system status"""
        
        return {
            'current_phase': self.state['current_phase'],
            'phases_completed': self.state['phases_completed'],
            'active_investigations': len(self.state['active_investigations']),
            'knowledge_graph_stats': self.knowledge_graph.get_statistics(),
            'api_usage': self.api_client.get_usage_statistics()
        }