#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
Controls dynamic phase execution and investigation spawning
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
from prompts.synthesis import SynthesisPrompts
from utils.document_loader import DocumentLoader


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
        self.api_client = ClaudeClient(config)
        self.context_manager = ContextManager(config)
        self.batch_manager = BatchManager(config)
        self.phase_executor = PhaseExecutor(config, self)
        
        # Initialise prompt systems
        self.autonomous_prompts = AutonomousPrompts(config)
        self.recursive_prompts = RecursivePrompts(config)
        self.synthesis_prompts = SynthesisPrompts(config)
        
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
        Execute complete analysis with dynamic phase progression
        """
        
        print("="*60)
        print("LITIGATION INTELLIGENCE SYSTEM - FULL ANALYSIS")
        print(f"Starting at: {datetime.now().isoformat()}")
        print("="*60)
        
        results = {
            'phases': {},
            'investigations': [],
            'final_synthesis': None,
            'war_room_dashboard': None
        }
        
        # Phase 0: Combined knowledge absorption
        if '0' not in self.state['phases_completed']:
            print("\n[PHASE 0] Knowledge Absorption (Legal + Case Context)")
            phase_0_results = self._execute_knowledge_phase()
            results['phases']['0'] = phase_0_results
            self.state['phases_completed'].append('0')
            self._save_state()
        
        # Dynamic disclosure analysis with iteration
        iteration = 1
        converged = False
        
        while iteration <= max_iterations and not converged:
            print(f"\n[ITERATION {iteration}] Disclosure Analysis")
            
            # Execute disclosure analysis
            iteration_results = self._execute_disclosure_iteration(iteration)
            results['phases'][f'iteration_{iteration}'] = iteration_results
            
            # Check for investigation triggers
            investigations = self.knowledge_graph.get_investigation_queue(limit=5)
            
            if investigations:
                print(f"  Spawning {len(investigations)} investigation threads")
                for investigation in investigations:
                    inv_results = self._execute_investigation(investigation)
                    results['investigations'].append(inv_results)
            
            # Check convergence
            converged = self._check_convergence(iteration_results)
            
            if converged:
                print("  ✓ Analysis converged - no new significant discoveries")
            
            iteration += 1
            self.state['iteration_count'] = iteration
            self._save_state()
        
        # Final synthesis
        print("\n[SYNTHESIS] Building Strategic Narrative")
        synthesis_results = self._execute_synthesis(results)
        results['final_synthesis'] = synthesis_results
        
        # Generate war room dashboard
        print("\n[DASHBOARD] Generating Executive Dashboard")
        dashboard = self._generate_war_room_dashboard(results)
        results['war_room_dashboard'] = dashboard
        
        # Save final results
        self._save_results(results)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def execute_single_phase(self, phase: str) -> Dict:
        """Execute a single phase with full context"""
        
        print(f"\n[PHASE {phase}] Execution Starting")
        
        # Backup knowledge graph
        self.knowledge_graph.backup_before_phase(phase)
        
        # Get context from knowledge graph
        context = self.knowledge_graph.get_context_for_phase(phase)
        
        # Execute phase
        results = self.phase_executor.execute(phase, context)
        
        # Update knowledge graph with findings
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
        print(f"  → Spawned investigation {investigation_id} (Priority: {priority})")
        
        return investigation_id
    
    def _execute_knowledge_phase(self) -> Dict:
        """Execute Phase 0: Combined knowledge absorption"""
        
        # Load legal and case documents
        legal_docs = self._load_documents(self.config.legal_knowledge_dir)
        case_docs = self._load_documents(self.config.case_context_dir)
        
        print(f"  Loading {len(legal_docs)} legal documents")
        print(f"  Loading {len(case_docs)} case context documents")
        
        # Build synthesis prompt
        existing_knowledge = self.knowledge_graph.get_context_for_phase('0')
        
        prompt = self.autonomous_prompts.knowledge_synthesis_prompt(
            legal_knowledge=legal_docs,
            case_context=case_docs,
            existing_knowledge=existing_knowledge
        )
        
        # Call Claude with maximum context
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='knowledge_synthesis',
            phase='0'
        )
        
        # Extract and store knowledge
        self._extract_knowledge_from_response(response, '0')
        
        # Save results
        results = {
            'phase': '0',
            'documents_processed': len(legal_docs) + len(case_docs),
            'synthesis': response,
            'metadata': metadata
        }
        
        self._save_phase_output('0', results)
        
        return results
    
    def _execute_disclosure_iteration(self, iteration: int) -> Dict:
        """Execute one iteration of disclosure analysis"""
        
        # Load disclosure documents
        disclosure_docs = self._load_documents(self.config.disclosure_dir)
        
        # Build batches using semantic clustering
        batches = self.batch_manager.create_semantic_batches(
            documents=disclosure_docs,
            strategy='semantic_clustering'
        )
        
        print(f"  Processing {len(disclosure_docs)} documents in {len(batches)} batches")
        
        iteration_results = {
            'iteration': iteration,
            'batches_processed': len(batches),
            'documents_analysed': len(disclosure_docs),
            'batch_results': [],
            'new_discoveries': 0
        }
        
        # Process each batch
        for i, batch in enumerate(batches):
            print(f"    Batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            # Get current context
            context = self.knowledge_graph.get_context_for_phase(f'iteration_{iteration}')
            
            # Build investigation prompt
            prompt = self.autonomous_prompts.investigation_prompt(
                documents=batch,
                context=context,
                phase=f'iteration_{iteration}'
            )
            
            # Call Claude
            response, metadata = self.api_client.call_claude(
                prompt=prompt,
                task_type='deep_investigation',
                phase=f'iteration_{iteration}'
            )
            
            # Extract discoveries
            discoveries = self._extract_discoveries_from_response(response, f'iteration_{iteration}')
            iteration_results['new_discoveries'] += len(discoveries)
            
            # Perform recursive self-questioning on interesting findings
            if discoveries:
                recursive_prompt = self.recursive_prompts.deep_questioning_prompt(
                    initial_analysis=response,
                    depth=self.config.recursion_config['self_questioning_depth']
                )
                
                recursive_response, _ = self.api_client.call_claude(
                    prompt=recursive_prompt,
                    task_type='recursive_analysis',
                    phase=f'iteration_{iteration}_recursive'
                )
                
                # Extract additional insights from recursive analysis
                self._extract_knowledge_from_response(recursive_response, f'iteration_{iteration}')
            
            iteration_results['batch_results'].append({
                'batch_num': i + 1,
                'documents': len(batch),
                'discoveries': len(discoveries),
                'response_length': len(response)
            })
            
            # Delay between batches
            if i < len(batches) - 1:
                time.sleep(self.config.api_config['rate_limit_delay'])
        
        return iteration_results
    
    def _execute_investigation(self, investigation: Dict) -> Dict:
        """Execute deep investigation thread"""
        
        print(f"\n  [INVESTIGATION] {investigation['type']} (Priority: {investigation['priority']})")
        
        # Get relevant documents for investigation
        relevant_docs = self._get_investigation_documents(investigation)
        
        # Build investigation context
        knowledge_context = self.knowledge_graph.get_context_for_phase('investigation')
        
        investigation_context = self.context_manager.build_investigation_context(
            investigation=investigation,
            relevant_docs=relevant_docs,
            knowledge_graph_context=knowledge_context
        )
        
        # Generate investigation prompt
        prompt = self.recursive_prompts.focused_investigation_prompt(
            investigation_thread=investigation,
            context=investigation_context,
            depth=self.config.investigation_depth['deep_investigation']
        )
        
        # Call Claude with deep investigation
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='deep_investigation',
            phase=f"investigation_{investigation['id']}"
        )
        
        # Extract findings
        findings = self._extract_investigation_findings(response, investigation)
        
        # Update knowledge graph
        self.knowledge_graph.complete_investigation(
            investigation_id=investigation['id'],
            findings=findings
        )
        
        # Check if findings warrant child investigations
        if findings.get('spawn_children'):
            for child in findings['spawn_children']:
                self.spawn_investigation(
                    trigger_type=child['type'],
                    trigger_data=child['data'],
                    priority=child.get('priority', 5.0)
                )
        
        return {
            'investigation_id': investigation['id'],
            'type': investigation['type'],
            'findings': findings,
            'metadata': metadata
        }
    
    def _execute_synthesis(self, results: Dict) -> Dict:
        """Execute final strategic synthesis"""
        
        # Export knowledge graph
        knowledge_export = self.knowledge_graph.export_for_report()
        
        # Gather phase analyses
        phase_analyses = {}
        for phase_key, phase_data in results['phases'].items():
            if 'synthesis' in phase_data:
                phase_analyses[phase_key] = phase_data['synthesis'][:5000]
        
        # Generate synthesis prompt
        prompt = self.synthesis_prompts.strategic_synthesis_prompt(
            phase_analyses=phase_analyses,
            investigations=results['investigations'][:20],
            knowledge_graph_export=knowledge_export
        )
        
        # Call Claude for synthesis
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='synthesis',
            phase='final_synthesis'
        )
        
        synthesis_results = {
            'narrative': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save synthesis
        self._save_synthesis(synthesis_results)
        
        return synthesis_results
    
    def _generate_war_room_dashboard(self, results: Dict) -> Dict:
        """Generate executive war room dashboard"""
        
        # Get current status
        current_status = {
            'phases_completed': len(results['phases']),
            'investigations_conducted': len(results['investigations']),
            'documents_analysed': sum(
                p.get('documents_analysed', 0) 
                for p in results['phases'].values()
            ),
            **self.knowledge_graph.get_statistics()
        }
        
        # Get critical findings
        critical_findings = []
        conn = self.knowledge_graph.db_path
        # Direct database query for critical findings
        # (simplified for example)
        
        # Get active investigations
        active_investigations = self.knowledge_graph.get_investigation_queue(limit=10)
        
        # Strategic options (would be extracted from synthesis)
        strategic_options = {
            'nuclear_options': [],
            'pressure_points': [],
            'defensive_requirements': []
        }
        
        # Generate dashboard prompt
        prompt = self.synthesis_prompts.war_room_dashboard_prompt(
            current_status=current_status,
            critical_findings=critical_findings,
            active_investigations=active_investigations,
            strategic_options=strategic_options
        )
        
        # Call Claude
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='report',
            phase='war_room_dashboard'
        )
        
        dashboard = {
            'content': response,
            'generated': datetime.now().isoformat(),
            'status': current_status,
            'metadata': metadata
        }
        
        # Save dashboard
        dashboard_path = self.config.reports_dir / f"war_room_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard['content'])
        
        print(f"  ✓ Dashboard saved to {dashboard_path}")
        
        return dashboard
    
    def _check_convergence(self, iteration_results: Dict) -> bool:
        """
        Check if analysis has converged (no new significant discoveries)
        """
        
        new_discoveries = iteration_results.get('new_discoveries', 0)
        
        # Track discovery trend
        if 'discovery_trend' not in self.state['convergence_metrics']:
            self.state['convergence_metrics']['discovery_trend'] = []
        
        self.state['convergence_metrics']['discovery_trend'].append(new_discoveries)
        
        # Check convergence criteria
        if new_discoveries == 0:
            return True
        
        # Check if discovery rate is declining
        trend = self.state['convergence_metrics']['discovery_trend']
        if len(trend) >= 3:
            # If last 3 iterations show declining discoveries
            if trend[-1] < trend[-2] < trend[-3]:
                if trend[-1] < 5:  # And current is low
                    return True
        
        # Check confidence threshold
        if hasattr(self.config, 'convergence_threshold'):
            # Would check pattern confidence scores
            pass
        
        return False
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory using DocumentLoader"""
        
        loader = DocumentLoader(self.config)
        
        # Load all supported document types (PDFs, DOCX, TXT, etc.)
        documents = loader.load_directory(
            directory=directory,
            doc_types=['.pdf', '.txt', '.docx', '.doc', '.json', '.html', '.md']
        )
        
        if not documents:
            print(f"  Warning: No documents loaded from {directory}")
        else:
            print(f"  Loaded {len(documents)} documents from {directory}")
            
            # Show breakdown by type
            by_type = {}
            for doc in documents:
                ext = doc['metadata'].get('extension', 'unknown')
                by_type[ext] = by_type.get(ext, 0) + 1
            
            for ext, count in by_type.items():
                print(f"    - {ext}: {count} documents")
        
        return documents
    
    def _get_investigation_documents(self, investigation: Dict) -> List[Dict]:
        """Get relevant documents for investigation"""
        
        # Load all disclosure documents
        all_docs = self._load_documents(self.config.disclosure_dir)
        
        # Filter based on investigation type
        investigation_data = investigation.get('data', {})
        relevant_docs = []
        
        for doc in all_docs:
            relevance_score = 0
            content_lower = doc['content'].lower()
            
            # Check for relevant terms
            if 'contradiction' in investigation['type']:
                if 'statement_a' in investigation_data:
                    if investigation_data['statement_a'].lower()[:50] in content_lower:
                        relevance_score += 1.0
            
            # Add more relevance scoring logic here
            
            if relevance_score > 0:
                relevant_docs.append(doc)
        
        # Return top relevant documents
        return relevant_docs[:50]
    
    def _extract_knowledge_from_response(self, response: str, phase: str):
        """Extract and store knowledge from Claude's response"""
        
        # Extract entities
        import re
        
        # Look for entity markers
        entity_pattern = r'\[ENTITY-NEW\]\s*([^\n]+)'
        entities = re.findall(entity_pattern, response)
        
        for entity_text in entities:
            # Parse entity (simplified)
            entity_id = hashlib.md5(entity_text.encode()).hexdigest()[:8]
            self.knowledge_graph.add_entity({
                'entity_id': entity_id,
                'entity_type': 'person',  # Would parse from response
                'subtype': '',
                'name': entity_text[:50],
                'first_seen': phase,
                'confidence': 0.7,
                'properties': {},
                'discovery_phase': phase
            })
    
    def _extract_discoveries_from_response(self, response: str, phase: str) -> List[Dict]:
        """Extract discoveries from response"""
        
        discoveries = []
        
        # Look for discovery markers
        markers = ['[NUCLEAR]', '[CRITICAL]', '[SUSPICIOUS]', '[PATTERN]']
        
        for marker in markers:
            if marker in response:
                # Extract text after marker
                import re
                pattern = rf'{re.escape(marker)}\s*([^\n]+)'
                findings = re.findall(pattern, response)
                
                for finding in findings:
                    discoveries.append({
                        'type': marker.strip('[]'),
                        'content': finding,
                        'phase': phase
                    })
                    
                    # Log to knowledge graph
                    importance_map = {
                        'NUCLEAR': 'NUCLEAR',
                        'CRITICAL': 'CRITICAL',
                        'SUSPICIOUS': 'HIGH',
                        'PATTERN': 'MEDIUM'
                    }
                    
                    self.knowledge_graph.log_discovery(
                        discovery_type=marker.strip('[]'),
                        content=finding[:500],
                        importance=importance_map.get(marker.strip('[]'), 'MEDIUM'),
                        phase=phase
                    )
        
        return discoveries
    
    def _extract_investigation_findings(self, response: str, investigation: Dict) -> Dict:
        """Extract findings from investigation response"""
        
        findings = {
            'summary': '',
            'contradictions': [],
            'patterns': [],
            'entities': [],
            'spawn_children': [],
            'confidence': 0.7
        }
        
        # Extract summary (first paragraph)
        lines = response.split('\n')
        findings['summary'] = lines[0] if lines else ''
        
        # Look for child investigation triggers
        if '[INVESTIGATE]' in response:
            # Extract investigation triggers
            import re
            inv_pattern = r'\[INVESTIGATE\]\s*([^\n]+)'
            investigations = re.findall(inv_pattern, response)
            
            for inv_text in investigations[:3]:  # Max 3 children
                findings['spawn_children'].append({
                    'type': 'follow_up',
                    'data': {'trigger': inv_text[:200]},
                    'priority': 6.0
                })
        
        return findings
    
    def _update_knowledge_from_results(self, results: Dict, phase: str):
        """Update knowledge graph with phase results"""
        
        # This would parse results and update knowledge graph
        # Simplified for example
        pass
    
    def _save_phase_output(self, phase: str, results: Dict):
        """Save phase output to file"""
        
        phase_dir = self.config.analysis_dir / f"phase_{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Save synthesis
        if 'synthesis' in results:
            synthesis_file = phase_dir / "synthesis.md"
            with open(synthesis_file, 'w', encoding='utf-8') as f:
                f.write(f"# Phase {phase} Analysis\n\n")
                f.write(f"*Documents Processed: {results.get('documents_processed', 0)}*\n\n")
                f.write("---\n\n")
                f.write(results['synthesis'])
        
        # Save metadata
        metadata_file = phase_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(results.get('metadata', {}), f, indent=2)
    
    def _save_synthesis(self, synthesis: Dict):
        """Save synthesis results"""
        
        synthesis_file = self.config.reports_dir / f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(synthesis_file, 'w', encoding='utf-8') as f:
            f.write("# Strategic Synthesis - Lismore v Process Holdings\n\n")
            f.write(synthesis['narrative'])
    
    def _save_results(self, results: Dict):
        """Save complete results"""
        
        results_file = self.config.output_dir / f"complete_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to serialisable format
        serialisable_results = {
            'phases': {k: {'summary': v.get('synthesis', '')[:1000]} for k, v in results['phases'].items()},
            'investigations_count': len(results['investigations']),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serialisable_results, f, indent=2)
    
    def _save_state(self):
        """Save orchestrator state"""
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def _load_state(self):
        """Load orchestrator state if exists"""
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                saved_state = json.load(f)
                self.state.update(saved_state)
    
    def _print_summary(self, results: Dict):
        """Print execution summary"""
        
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        
        # Calculate statistics
        stats = self.knowledge_graph.get_statistics()
        
        print(f"Phases Completed: {len(results['phases'])}")
        print(f"Investigations Conducted: {len(results['investigations'])}")
        print(f"Entities Identified: {stats['entities']}")
        print(f"Relationships Mapped: {stats['relationships']}")
        print(f"Contradictions Found: {stats['contradictions']}")
        print(f"Patterns Discovered: {stats['patterns']}")
        print(f"Timeline Events: {stats['timeline_events']}")
        
        # API usage
        usage = self.api_client.get_usage_report()
        print(f"\nAPI Usage:")
        print(f"  Total Calls: {usage['summary']['total_calls']}")
        print(f"  Estimated Cost: ${usage['summary']['estimated_cost_usd']}")
        
        print("\n" + "="*60)