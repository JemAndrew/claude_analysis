#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
Controls dynamic phase execution with prompt caching
Optimised for Lismore v Process Holdings (72 folders)
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
    """Main system orchestrator with prompt caching for cost efficiency"""
    
    def __init__(self, config_override: Dict = None):
        """Initialise orchestrator with all components"""
        
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
        
        self._load_state()
    
    def execute_full_analysis(self, 
                             start_phase: str = '0',
                             max_iterations: int = 10) -> Dict:
        """Execute complete analysis with prompt caching"""
        
        print("="*60)
        print("LITIGATION INTELLIGENCE SYSTEM")
        print("Case: Lismore Capital v Process Holdings")
        print(f"Starting: {datetime.now().isoformat()}")
        print("="*60)
        
        results = {
            'phases': {},
            'investigations': [],
            'convergence_data': {},
            'final_synthesis': None,
            'war_room_dashboard': None
        }
        
        try:
            # Phase 0: Knowledge Absorption
            if start_phase == '0':
                print("\nPHASE 0: KNOWLEDGE ABSORPTION")
                results['phases']['0'] = self.execute_single_phase('0')
            
            # Disclosure Iterations with caching
            print(f"\nDISCLOSURE ANALYSIS: {max_iterations} iterations")
            for iteration in range(1, max_iterations + 1):
                print(f"\n--- Iteration {iteration}/{max_iterations} ---")
                
                iteration_results = self._execute_disclosure_iteration(iteration)
                results['phases'][f'iteration_{iteration}'] = iteration_results
                
                if self._check_convergence(iteration_results):
                    print(f"  Convergence achieved at iteration {iteration}")
                    break
            
            # Process active investigations
            print("\nPROCESSING ACTIVE INVESTIGATIONS")
            results['investigations'] = self._process_all_investigations()
            
            # Final synthesis
            print("\nGENERATING STRATEGIC SYNTHESIS")
            results['final_synthesis'] = self._execute_synthesis(results)
            
            # War room dashboard
            print("\nGENERATING WAR ROOM DASHBOARD")
            results['war_room_dashboard'] = self._generate_war_room_dashboard(results)
            
            self._save_results(results)
            self.api_client.print_usage_summary()
            
            print("\n" + "="*60)
            print("ANALYSIS COMPLETE")
            print("="*60)
            
            return results
            
        except Exception as e:
            print(f"\nError in analysis: {e}")
            raise
    
    def execute_single_phase(self, phase: str) -> Dict:
        """Execute a single phase"""
        
        print(f"\nExecuting Phase {phase}")
        
        self.knowledge_graph.backup_before_phase(phase)
        context = self.knowledge_graph.get_context_for_phase(phase)
        
        if phase == '0':
            results = self.phase_executor.execute_phase_0(context)
        else:
            results = self.phase_executor.execute(phase, context)
        
        self._update_knowledge_from_results(results, phase)
        
        if phase not in self.state['phases_completed']:
            self.state['phases_completed'].append(phase)
        
        self._save_state()
        return results
    
    def _execute_disclosure_iteration(self, iteration: int) -> Dict:
        """
        Execute disclosure iteration WITH PROMPT CACHING
        60-90% cost savings through caching
        """
        
        disclosure_docs = self._load_documents(self.config.disclosure_dir)
        
        if not disclosure_docs:
            print("  No disclosure documents found")
            return {'error': 'no_documents'}
        
        batches = self.batch_manager.create_semantic_batches(
            documents=disclosure_docs,
            strategy='semantic_clustering'
        )
        
        print(f"  Processing {len(disclosure_docs)} documents in {len(batches)} batches")
        
        # BUILD CACHEABLE CONTEXT ONCE
        knowledge_context = self.knowledge_graph.get_context_for_phase(f'iteration_{iteration}')
        
        cacheable_context = f"""
{self.config.hallucination_prevention}

<case_mission>
COMPREHENSIVE LITIGATION ANALYSIS FOR LISMORE CAPITAL v PROCESS HOLDINGS

Objective: Find EVERYTHING that helps Lismore win this arbitration.
You are acting FOR Lismore (not neutral).
Analysis Phase: iteration_{iteration}

Key areas:
1. Contract breaches by Process Holdings
2. Fraud/misrepresentation indicators
3. Fiduciary duty breaches
4. Credibility attacks on Process Holdings witnesses
5. Damages quantification
6. Legal arguments (liability + quantum)
7. Procedural advantages
8. Document withholding patterns
9. Timeline reconstruction
10. Strategic recommendations
</case_mission>

<knowledge_graph_context>
{json.dumps(knowledge_context, indent=2)[:15000]}
</knowledge_graph_context>

<analysis_categories>
Analyse documents across ALL 12 categories:
1. CONTRACT BREACHES - Specific obligations and violations
2. FRAUD & MISREPRESENTATION - False statements to Lismore
3. CREDIBILITY ATTACKS - Contradictions, implausible claims
4. DOCUMENT WITHHOLDING - Referenced but not produced
5. TIMELINE IMPOSSIBILITIES - Events that couldn't have happened
6. FINANCIAL IRREGULARITIES - Payment discrepancies, valuations
7. ENTITY RELATIONSHIPS - Conflicts of interest, hidden relationships
8. CONTRADICTION MINING - Document vs document conflicts
9. STRATEGIC BLIND SPOTS - What they're hiding
10. DAMAGES QUANTIFICATION - Direct and consequential losses
11. LEGAL DOCTRINE APPLICATIONS - Applicable principles
12. WITNESS INCONSISTENCIES - Between witnesses and documents
</analysis_categories>
"""
        
        # PROCESS BATCHES WITH CACHING
        iteration_results = {
            'iteration': iteration,
            'batches_processed': len(batches),
            'documents_analysed': len(disclosure_docs),
            'batch_results': [],
            'new_discoveries': 0
        }
        
        for i, batch in enumerate(batches):
            print(f"    Batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            # Build unique prompt (changes per batch)
            prompt = self.autonomous_prompts.investigation_prompt(
                documents=batch,
                context={},  # Empty - context is in cacheable part
                phase=f'iteration_{iteration}'
            )
            
            # CALL WITH CACHING
            # First batch: Creates cache (pays 25% premium)
            # Subsequent batches: Use cache (90% discount)
            response, metadata = self.api_client.call_claude_with_cache(
                prompt=prompt,
                cacheable_context=cacheable_context,
                task_type='deep_investigation',
                phase=f'iteration_{iteration}'
            )
            
            # Extract discoveries
            discoveries = self._extract_discoveries_from_response(response, f'iteration_{iteration}')
            iteration_results['new_discoveries'] += len(discoveries)
            
            # Recursive investigation on high-value findings
            if discoveries:
                high_value = [d for d in discoveries if d.get('severity', 0) >= 7]
                
                if high_value:
                    print(f"      Found {len(high_value)} high-value findings - recursive analysis")
                    
                    recursive_prompt = self.recursive_prompts.deep_questioning_prompt(
                        initial_analysis=response,
                        depth=self.config.recursion_config['self_questioning_depth']
                    )
                    
                    # Recursive call also benefits from caching
                    recursive_response, _ = self.api_client.call_claude_with_cache(
                        prompt=recursive_prompt,
                        cacheable_context=cacheable_context,
                        task_type='recursive_analysis',
                        phase=f'iteration_{iteration}_recursive'
                    )
                    
                    self._extract_knowledge_from_response(recursive_response, f'iteration_{iteration}')
            
            iteration_results['batch_results'].append({
                'batch_num': i + 1,
                'documents': len(batch),
                'discoveries': len(discoveries),
                'response_length': len(response)
            })
            
            # Rate limiting delay
            if i < len(batches) - 1:
                time.sleep(self.config.api_config['rate_limit_delay'])
        
        return iteration_results
    
    def spawn_investigation(self, 
                          trigger_type: str,
                          trigger_data: Dict,
                          priority: float = 5.0) -> str:
        """Spawn new investigation thread"""
        
        investigation_id = self.knowledge_graph._spawn_investigation(
            trigger_type=trigger_type,
            trigger_data=trigger_data,
            priority=priority
        )
        
        self.state['active_investigations'].append(investigation_id)
        print(f"  Spawned investigation {investigation_id} (Priority: {priority})")
        
        return investigation_id
    
    def _process_all_investigations(self) -> List[Dict]:
        """Process all active investigations"""
        
        investigations = self.knowledge_graph.get_investigation_queue(limit=50)
        results = []
        
        for investigation in investigations:
            result = self._execute_investigation(investigation)
            results.append(result)
        
        return results
    
    def _execute_investigation(self, investigation: Dict) -> Dict:
        """Execute deep investigation thread"""
        
        print(f"  Investigation: {investigation['type']} (Priority: {investigation['priority']})")
        
        relevant_docs = self._get_investigation_documents(investigation)
        knowledge_context = self.knowledge_graph.get_context_for_phase('investigation')
        
        investigation_context = self.context_manager.build_investigation_context(
            investigation=investigation,
            relevant_docs=relevant_docs,
            knowledge_graph_context=knowledge_context
        )
        
        prompt = self.recursive_prompts.focused_investigation_prompt(
            investigation_thread=investigation,
            context=investigation_context,
            depth=self.config.investigation_depth.get('deep', 5)
        )
        
        # Build cacheable context for investigation
        cacheable_context = f"""
{self.config.hallucination_prevention}
{json.dumps(knowledge_context, indent=2)[:10000]}
"""
        
        response, metadata = self.api_client.call_claude_with_cache(
            prompt=prompt,
            cacheable_context=cacheable_context,
            task_type='deep_investigation',
            phase=f"investigation_{investigation['id']}"
        )
        
        findings = self._extract_investigation_findings(response, investigation)
        
        self.knowledge_graph.complete_investigation(
            investigation_id=investigation['id'],
            findings=findings
        )
        
        # Spawn child investigations if needed
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
        
        knowledge_export = self.knowledge_graph.export_for_report()
        
        phase_analyses = {}
        for phase_key, phase_data in results['phases'].items():
            if 'synthesis' in phase_data:
                phase_analyses[phase_key] = phase_data['synthesis'][:5000]
        
        prompt = self.synthesis_prompts.strategic_synthesis_prompt(
            phase_analyses=phase_analyses,
            investigations=results['investigations'][:20],
            knowledge_graph_export=knowledge_export
        )
        
        # Build final cacheable context
        cacheable_context = f"""
{self.config.hallucination_prevention}
{json.dumps(knowledge_export, indent=2)[:15000]}
"""
        
        response, metadata = self.api_client.call_claude_with_cache(
            prompt=prompt,
            cacheable_context=cacheable_context,
            task_type='synthesis',
            phase='final_synthesis'
        )
        
        synthesis_results = {
            'narrative': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_synthesis(synthesis_results)
        
        return synthesis_results
    
    def _generate_war_room_dashboard(self, results: Dict) -> Dict:
        """Generate executive war room dashboard"""
        
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
        knowledge_export = self.knowledge_graph.export_for_report()
        
        dashboard = {
            'current_status': current_status,
            'critical_findings': knowledge_export.get('critical_findings', [])[:20],
            'active_investigations': self.knowledge_graph.get_investigation_queue(limit=10),
            'strategic_options': {
                'nuclear_options': [],
                'pressure_points': [],
                'settlement_leverage': []
            },
            'next_steps': [],
            'api_usage': self.api_client.get_usage_report()
        }
        
        return dashboard
    
    def _check_convergence(self, iteration_results: Dict) -> bool:
        """Check if analysis has converged"""
        
        threshold = self.config.recursion_config['convergence_threshold']
        new_discoveries = iteration_results.get('new_discoveries', 0)
        
        if self.state['iteration_count'] > 0:
            prev_discoveries = self.state.get('prev_discoveries', 100)
            if prev_discoveries > 0:
                change_rate = new_discoveries / prev_discoveries
                if change_rate < (1 - threshold):
                    return True
        
        self.state['prev_discoveries'] = new_discoveries
        self.state['iteration_count'] += 1
        return False
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory"""
        
        loader = DocumentLoader(self.config)
        if directory and directory.exists():
            return loader.load_directory(directory)
        return []
    
    def _get_investigation_documents(self, investigation: Dict) -> List[Dict]:
        """Get relevant documents for investigation"""
        
        # Simple implementation - return subset of disclosure
        all_docs = self._load_documents(self.config.disclosure_dir)
        return all_docs[:20]  # Limit for focused investigation
    
    def _extract_discoveries_from_response(self, response: str, phase: str) -> List[Dict]:
        """Extract discoveries from response"""
        
        return self.phase_executor.extract_discoveries(response, phase)
    
    def _extract_investigation_findings(self, response: str, investigation: Dict) -> Dict:
        """Extract findings from investigation"""
        
        return {
            'raw_response': response[:5000],
            'investigation_id': investigation['id'],
            'spawn_children': []
        }
    
    def _extract_knowledge_from_response(self, response: str, phase: str):
        """Extract and store knowledge from response"""
        
        # Extract contradictions
        contradictions = self.phase_executor.extract_contradictions(response)
        for contradiction in contradictions:
            self.knowledge_graph.add_contradiction(contradiction)
        
        # Extract patterns
        patterns = self.phase_executor.extract_patterns(response)
        for pattern in patterns:
            self.knowledge_graph.add_pattern(pattern)
        
        # Extract entities and relationships
        entities, relationships = self.phase_executor.extract_entities_and_relationships(response)
        for entity in entities:
            self.knowledge_graph.add_entity(entity)
        for relationship in relationships:
            self.knowledge_graph.add_relationship(relationship)
    
    def _update_knowledge_from_results(self, results: Dict, phase: str):
        """Update knowledge graph from phase results"""
        
        if 'synthesis' in results:
            self._extract_knowledge_from_response(results['synthesis'], phase)
    
    def _save_phase_output(self, phase: str, results: Dict):
        """Save phase output to file"""
        
        phase_dir = self.config.analysis_dir / f"phase_{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        if 'synthesis' in results:
            synthesis_file = phase_dir / "synthesis.md"
            with open(synthesis_file, 'w', encoding='utf-8') as f:
                f.write(f"# Phase {phase} Analysis\n\n")
                f.write(f"*Documents Processed: {results.get('documents_processed', 0)}*\n\n")
                f.write("---\n\n")
                f.write(results['synthesis'])
        
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
        
        serialisable_results = {
            'phases': {k: {'summary': str(v)[:1000]} for k, v in results['phases'].items()},
            'investigations_count': len(results['investigations']),
            'synthesis_generated': results.get('final_synthesis') is not None,
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