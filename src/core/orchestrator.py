#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
Controls dynamic phase execution and investigation spawning
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
from intelligence.memory_manager import MemoryManager
from api.client import ClaudeClient
from api.context_manager import ContextManager
from api.batch_manager import BatchManager
from prompts.autonomous import AutonomousPrompts
from prompts.recursive import RecursivePrompts
from prompts.synthesis import SynthesisPrompts
from utils.document_processor import DocumentLoader


class LitigationOrchestrator:
    """Main system orchestrator for maximum Claude utilisation"""
    
    def __init__(self, config_override: Dict = None):
        """Initialise orchestrator with all components"""
        
        # Override config if needed
        if config_override:
            for key, value in config_override.items():
                setattr(config, key, value)
        
        self.config = config
        
        # Initialise core components
        self.knowledge_graph = KnowledgeGraph(config)
        self.memory_manager = MemoryManager(config)  # NEW
        self.api_client = ClaudeClient(config)
        self.context_manager = ContextManager(config)
        self.batch_manager = BatchManager(config)
        self.phase_executor = PhaseExecutor(config, self)
        
        # Initialise prompt systems
        self.autonomous_prompts = AutonomousPrompts(config)
        self.recursive_prompts = RecursivePrompts(config)
        self.synthesis_prompts = SynthesisPrompts(config)
        
        # Document loader
        self.document_loader = DocumentLoader()
        
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
        
        print("✅ Litigation Intelligence System initialised")
        print(f"   Memory Manager: {self.memory_manager.expertise_level}")
        print(f"   Previous phases completed: {len(self.state['phases_completed'])}")
    
    def execute_full_analysis(self, 
                             start_phase: int = 0,
                             max_iterations: int = 10) -> Dict:
        """
        Execute complete analysis with dynamic phase progression
        """
        
        print("="*60)
        print("LITIGATION INTELLIGENCE SYSTEM - FULL ANALYSIS")
        print(f"Case: Lismore Capital v Process Holdings")
        print(f"Model: {self.config.models['primary']}")
        print(f"Starting at: {datetime.now().isoformat()}")
        print("="*60)
        
        results = {
            'phases': {},
            'investigations': [],
            'convergence': {},
            'final_synthesis': {}
        }
        
        # Execute Phase 0: Knowledge Foundation (if starting from beginning)
        if start_phase == 0:
            print("\n" + "="*60)
            print("PHASE 0: KNOWLEDGE FOUNDATION")
            print("="*60)
            results['phases']['0'] = self._execute_knowledge_phase()
            self.state['phases_completed'].append('0')
            self._save_state()
        
        # Execute Phases 1-6
        for phase_num in range(max(1, start_phase), 7):
            print("\n" + "="*60)
            print(f"PHASE {phase_num}: {self._get_phase_name(phase_num)}")
            print("="*60)
            
            # Execute phase
            phase_results = self.execute_phase(str(phase_num))
            results['phases'][str(phase_num)] = phase_results
            
            # Update memory with complete results
            self.memory_manager.update_after_phase(phase_num, phase_results)
            
            # Check if we should spawn investigations
            self._check_and_spawn_investigations(phase_results)
            
            print(f"\n✅ Phase {phase_num} complete")
            print(f"   Expertise level: {self.memory_manager.expertise_level}")
            print(f"   New insights: {self.memory_manager.count_insights(phase_results)}")
        
        # Generate final synthesis
        print("\n" + "="*60)
        print("GENERATING FINAL SYNTHESIS")
        print("="*60)
        results['final_synthesis'] = self._generate_final_synthesis()
        
        # Save final results
        self._save_final_results(results)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total phases: {len(results['phases'])}")
        print(f"Total investigations: {len(results['investigations'])}")
        print(f"Final expertise: {self.memory_manager.expertise_level}")
        
        return results
    
    def execute_phase(self, phase: str) -> Dict:
        """
        Execute a single phase with memory context
        """
        
        self.state['current_phase'] = phase
        
        print(f"\n🔍 Preparing Phase {phase}...")
        
        # Backup knowledge graph before phase
        print("  • Creating backup...")
        self.knowledge_graph.backup_before_phase(phase)
        
        # Get complete context from memory manager
        print("  • Loading complete context from memory...")
        context = self.memory_manager.build_context_for_phase(int(phase))
        
        # Execute phase with full context
        print(f"  • Executing phase with {self.memory_manager.expertise_level} expertise...")
        results = self.phase_executor.execute(phase, context)
        
        # Update knowledge graph with findings
        print("  • Updating knowledge graph...")
        self._update_knowledge_from_results(results, phase)
        
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
        
        investigation_id = self.knowledge_graph._spawn_investigation(
            trigger_type=trigger_type,
            trigger_data=trigger_data,
            priority=priority
        )
        
        self.state['active_investigations'].append(investigation_id)
        print(f"  → Spawned investigation {investigation_id[:8]} (Priority: {priority:.1f})")
        
        return investigation_id
    
    def _execute_knowledge_phase(self) -> Dict:
        """Execute Phase 0: Combined knowledge absorption"""
        
        # Load legal and case documents
        print("  • Loading legal knowledge documents...")
        legal_docs = self._load_documents(self.config.legal_knowledge_dir)
        
        print("  • Loading case documents...")
        case_docs = self._load_documents(self.config.case_documents_dir)
        
        print(f"  • Total documents: {len(legal_docs)} legal + {len(case_docs)} case")
        
        # Get context from memory manager
        context = self.memory_manager.build_context_for_phase(0)
        
        # Build synthesis prompt
        prompt = self.autonomous_prompts.knowledge_synthesis_prompt(
            legal_knowledge=legal_docs,
            case_context=case_docs,
            existing_knowledge=context
        )
        
        # Call Claude with maximum context
        print("  • Analysing with Claude Opus 4.1...")
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='knowledge_synthesis',
            phase='0'
        )
        
        # Extract and store knowledge
        knowledge_extracted = self._extract_knowledge_from_response(response, '0')
        
        # Save results
        results = {
            'phase': '0',
            'documents_processed': len(legal_docs) + len(case_docs),
            'legal_documents': len(legal_docs),
            'case_documents': len(case_docs),
            'knowledge_extracted': knowledge_extracted,
            'synthesis': response[:5000],  # First 5000 chars
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_phase_output('0', results)
        
        return results
    
    def _check_and_spawn_investigations(self, phase_results: Dict):
        """Check phase results for investigation triggers"""
        
        discoveries = phase_results.get('discoveries', [])
        
        for discovery in discoveries:
            if self.config.should_investigate(discovery):
                priority = self.config.calculate_priority(discovery)
                
                if priority >= 7.0:  # Only spawn high-priority investigations
                    self.spawn_investigation(
                        trigger_type=discovery.get('type', 'general'),
                        trigger_data=discovery,
                        priority=priority
                    )
    
    def _update_knowledge_from_results(self, results: Dict, phase: str):
        """Update knowledge graph with phase results"""
        
        # Add entities
        if 'entities' in results:
            for entity_data in results['entities']:
                # Create Entity object and add to knowledge graph
                pass  # Implementation depends on Entity structure
        
        # Add contradictions
        if 'contradictions' in results:
            for contradiction in results['contradictions']:
                # Add to knowledge graph
                pass
        
        # Add patterns
        if 'patterns' in results:
            for pattern in results['patterns']:
                # Add to knowledge graph
                pass
        
        # Log discoveries
        if 'discoveries' in results:
            for discovery in results['discoveries']:
                self.knowledge_graph.log_discovery(
                    discovery_type=discovery.get('type', 'general'),
                    content=str(discovery),
                    importance=discovery.get('importance', 'MEDIUM'),
                    phase=phase
                )
    
    def _generate_final_synthesis(self) -> Dict:
        """Generate final synthesis of all intelligence"""
        
        # Get all phase results from memory
        all_phase_analyses = {}
        for phase_id, phase_memory in self.memory_manager.phase_memories.items():
            all_phase_analyses[phase_id] = phase_memory.get('complete_results', {})
        
        # Get investigation results
        investigations = self.memory_manager.investigation_history
        
        # Get knowledge graph export
        knowledge_export = self.knowledge_graph.export_for_report()
        
        # Build synthesis prompt
        prompt = self.synthesis_prompts.strategic_synthesis_prompt(
            phase_analyses=all_phase_analyses,
            investigations=investigations,
            knowledge_graph_export=knowledge_export
        )
        
        # Call Claude for final synthesis
        print("  • Generating strategic synthesis with Opus 4.1...")
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='synthesis',
            phase='final'
        )
        
        synthesis = {
            'summary': response[:2000],
            'full_synthesis': response,
            'metadata': metadata,
            'intelligence_stats': self.memory_manager.generate_complete_intelligence_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        return synthesis
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory"""
        
        documents = []
        
        if not directory.exists():
            print(f"  ⚠️  Directory not found: {directory}")
            return documents
        
        # Load all PDF, TXT, DOCX files
        for file_path in directory.glob('**/*'):
            if file_path.suffix.lower() in ['.pdf', '.txt', '.docx', '.doc']:
                try:
                    doc = self.document_loader.load_document(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    print(f"  ⚠️  Failed to load {file_path.name}: {e}")
        
        return documents
    
    def _extract_knowledge_from_response(self, response: str, phase: str) -> Dict:
        """Extract structured knowledge from Claude's response"""
        
        # Simple extraction - looks for marked sections
        knowledge = {
            'legal_principles': [],
            'case_facts': [],
            'strategic_insights': [],
            'entities_identified': [],
            'key_documents': []
        }
        
        # Extract [STRATEGIC] markers
        import re
        strategic = re.findall(r'\[STRATEGIC\](.*?)(?=\[|\n\n|$)', response, re.DOTALL)
        knowledge['strategic_insights'] = [s.strip() for s in strategic]
        
        # Extract [VULNERABILITY] markers
        vulnerabilities = re.findall(r'\[VULNERABILITY\](.*?)(?=\[|\n\n|$)', response, re.DOTALL)
        knowledge['vulnerabilities'] = [v.strip() for v in vulnerabilities]
        
        # Extract [WEAPON] markers
        weapons = re.findall(r'\[WEAPON\](.*?)(?=\[|\n\n|$)', response, re.DOTALL)
        knowledge['legal_weapons'] = [w.strip() for w in weapons]
        
        return knowledge
    
    def _get_phase_name(self, phase_num: int) -> str:
        """Get human-readable phase name"""
        phase_names = {
            0: "KNOWLEDGE FOUNDATION",
            1: "DOCUMENT ORGANISATION",
            2: "FOUNDATION INTELLIGENCE",
            3: "PATTERN RECOGNITION & DEEP ANALYSIS",
            4: "ADVERSARIAL INTELLIGENCE",
            5: "NOVEL THEORIES & CREATIVE STRATEGY",
            6: "SYNTHESIS & WEAPONISATION"
        }
        return phase_names.get(phase_num, f"PHASE {phase_num}")
    
    def _load_state(self):
        """Load previous state if exists"""
        state_file = self.config.knowledge_dir / "orchestrator_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
    
    def _save_state(self):
        """Save current state"""
        state_file = self.config.knowledge_dir / "orchestrator_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _save_phase_output(self, phase: str, results: Dict):
        """Save phase output to file"""
        output_file = self.config.analysis_dir / f"phase_{phase}_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"  • Results saved to: {output_file}")
    
    def _save_final_results(self, results: Dict):
        """Save final analysis results"""
        output_file = self.config.output_dir / f"final_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Final results saved to: {output_file}")
    
    def get_status_report(self) -> Dict:
        """Get current system status"""
        return {
            'current_phase': self.state['current_phase'],
            'phases_completed': self.state['phases_completed'],
            'expertise_level': self.memory_manager.expertise_level,
            'active_investigations': len(self.state['active_investigations']),
            'knowledge_graph_stats': self.knowledge_graph.get_statistics(),
            'memory_stats': {
                'documents_analysed': len(self.memory_manager.document_intelligence),
                'entities_tracked': len(self.memory_manager.entity_intelligence),
                'patterns_found': len(self.memory_manager.pattern_library),
                'contradictions_found': len(self.memory_manager.contradiction_database)
            }
        }