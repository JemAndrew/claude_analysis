#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
Controls dynamic phase execution and investigation spawning
WITH INTEGRATED CHECKPOINT SYSTEM FOR INTERNET RESILIENCE
"""

import json
import time
import shutil
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
        
        # ✅ NEW: Initialise checkpoint system
        self._init_checkpoints()
    
    # ============================================================================
    # ✅ NEW: CHECKPOINT METHODS
    # ============================================================================
    
    def _init_checkpoints(self):
        """Initialise checkpoint system"""
        
        self.checkpoint_dir = self.config.output_dir / ".checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_checkpoint_dir = self.checkpoint_dir / "batches"
        self.batch_checkpoint_dir.mkdir(exist_ok=True)
    
    def _save_batch_checkpoint(self, phase: str, batch_num: int, 
                              batch_results: Dict, doc_ids: List[str]):
        """Save checkpoint after batch completes"""
        
        checkpoint_data = {
            'phase': phase,
            'batch_number': batch_num,
            'timestamp': datetime.now().isoformat(),
            'batch_results': batch_results,
            'processed_document_ids': doc_ids,
            'status': 'completed'
        }
        
        # Save to batch-specific file
        checkpoint_file = self.batch_checkpoint_dir / f"phase_{phase}_batch_{batch_num}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # Also save as "latest" for easy recovery
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"      ✓ Checkpoint saved (Batch {batch_num})")
    
    def _load_checkpoint(self, phase: str) -> Optional[Dict]:
        """Load latest checkpoint for phase"""
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        
        if latest_file.exists():
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def _get_processed_docs(self, phase: str) -> List[str]:
        """Get list of already-processed document IDs"""
        
        checkpoint = self._load_checkpoint(phase)
        
        if checkpoint:
            return checkpoint.get('processed_document_ids', [])
        
        return []
    
    def _should_resume_phase(self, phase: str) -> Tuple[bool, Optional[Dict]]:
        """Check if phase should resume from checkpoint"""
        
        checkpoint = self._load_checkpoint(phase)
        
        if checkpoint:
            print(f"\n  🔄 Found checkpoint for Phase {phase}")
            print(f"    Last batch: {checkpoint.get('batch_number', 0)}")
            print(f"    Documents processed: {len(checkpoint.get('processed_document_ids', []))}")
            print(f"    Timestamp: {checkpoint.get('timestamp', 'N/A')}")
            
            response = input("\n  Resume from checkpoint? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                return True, checkpoint
        
        return False, None
    
    def _clear_phase_checkpoints(self, phase: str):
        """Clear checkpoints after successful phase completion"""
        
        # Remove latest checkpoint
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        if latest_file.exists():
            latest_file.unlink()
        
        # Archive batch checkpoints
        archive_dir = self.checkpoint_dir / "archive" / phase
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for checkpoint_file in self.batch_checkpoint_dir.glob(f"phase_{phase}_batch_*.json"):
            shutil.move(str(checkpoint_file), str(archive_dir / checkpoint_file.name))
    
    def _create_backup(self, phase: str):
        """Create backup before starting phase"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.config.output_dir / f"backup_phase_{phase}_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup knowledge graph
        if self.config.graph_db_path.exists():
            shutil.copy2(
                self.config.graph_db_path,
                backup_dir / "graph.db"
            )
        
        # Backup state
        state_file = self.config.output_dir / ".orchestrator_state.json"
        if state_file.exists():
            shutil.copy2(state_file, backup_dir / "orchestrator_state.json")
        
        print(f"  ✓ Backup created: {backup_dir.name}")
    
    # ============================================================================
    # MAIN EXECUTION METHODS
    # ============================================================================
    
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
    
    # ============================================================================
    # ✅ MODIFIED: PHASE EXECUTION WITH CHECKPOINTS
    # ============================================================================
    
    def _execute_knowledge_phase(self) -> Dict:
        """Execute Phase 0: Combined knowledge absorption WITH CHECKPOINTS"""
        
        phase = '0'
        
        # Check for checkpoint
        should_resume, checkpoint = self._should_resume_phase(phase)
        
        # Create backup before starting
        if not should_resume:
            self._create_backup(phase)
        
        # Load legal and case documents
        legal_docs = self._load_documents(self.config.legal_knowledge_dir)
        case_docs = self._load_documents(self.config.case_context_dir)
        
        all_docs = legal_docs + case_docs
        
        print(f"  Total documents: {len(all_docs)}")
        
        # Get already-processed documents if resuming
        processed_doc_ids = self._get_processed_docs(phase) if should_resume else []
        
        # Filter out already-processed documents
        if processed_doc_ids:
            all_docs = [
                doc for doc in all_docs 
                if doc.get('id', doc.get('filename')) not in processed_doc_ids
            ]
            print(f"  Remaining documents: {len(all_docs)}")
        
        # Create batches
        batches = self.batch_manager.create_semantic_batches(
            documents=all_docs,
            strategy='semantic_clustering'
        )
        
        start_batch = checkpoint.get('batch_number', 0) + 1 if should_resume else 1
        
        print(f"  Processing {len(batches)} batches (starting from batch {start_batch})")
        
        results = {
            'phase': phase,
            'documents_processed': len(processed_doc_ids),
            'batches_processed': start_batch - 1,
            'synthesis': '',
            'metadata': {}
        }
        
        # Process each batch with checkpoint
        for i, batch in enumerate(batches, start_batch):
            print(f"    Batch {i}/{len(batches) + start_batch - 1}: {len(batch)} documents")
            
            try:
                # Get current context
                existing_knowledge = self.knowledge_graph.get_context_for_phase(phase)
                
                # Build synthesis prompt
                prompt = self.autonomous_prompts.knowledge_synthesis_prompt(
                    legal_knowledge=legal_docs if i <= len(legal_docs)//20 else [],
                    case_context=case_docs if i > len(legal_docs)//20 else [],
                    existing_knowledge=existing_knowledge
                )
                
                # Call Claude
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='knowledge_synthesis',
                    phase=phase
                )
                
                # Extract knowledge
                self._extract_knowledge_from_response(response, phase)
                
                # Track processed documents
                batch_doc_ids = [doc.get('id', doc.get('filename', f'doc_{j}')) 
                               for j, doc in enumerate(batch)]
                processed_doc_ids.extend(batch_doc_ids)
                
                results['documents_processed'] += len(batch)
                results['batches_processed'] = i
                results['synthesis'] += response[:500] + "\n\n"
                
                # ✅ CRITICAL: Save checkpoint after batch
                self._save_batch_checkpoint(
                    phase=phase,
                    batch_num=i,
                    batch_results={'response_length': len(response)},
                    doc_ids=processed_doc_ids
                )
                
                # Rate limit delay
                if i < len(batches) + start_batch - 1:
                    time.sleep(self.config.api_config['rate_limit_delay'])
            
            except Exception as e:
                print(f"      ❌ Error in batch {i}: {e}")
                print(f"      ✓ Progress saved up to batch {i-1}")
                raise
        
        # Clear checkpoints after successful completion
        self._clear_phase_checkpoints(phase)
        
        # Save final phase output
        self._save_phase_output(phase, results)
        
        return results
    
    def _execute_disclosure_iteration(self, iteration: int) -> Dict:
        """Execute one iteration of disclosure analysis WITH CHECKPOINTS"""
        
        phase = f'iteration_{iteration}'
        
        # Check for checkpoint
        should_resume, checkpoint = self._should_resume_phase(phase)
        
        # Create backup if not resuming
        if not should_resume:
            self._create_backup(phase)
        
        # Load disclosure documents
        disclosure_docs = self._load_documents(self.config.disclosure_dir)
        
        # Get already-processed documents
        processed_doc_ids = self._get_processed_docs(phase) if should_resume else []
        
        # Filter out processed documents
        if processed_doc_ids:
            disclosure_docs = [
                doc for doc in disclosure_docs 
                if doc.get('id', doc.get('filename')) not in processed_doc_ids
            ]
        
        # Build batches
        batches = self.batch_manager.create_semantic_batches(
            documents=disclosure_docs,
            strategy='semantic_clustering'
        )
        
        start_batch = checkpoint.get('batch_number', 0) + 1 if should_resume else 1
        
        print(f"  Processing {len(disclosure_docs)} documents in {len(batches)} batches")
        print(f"  Starting from batch {start_batch}")
        
        iteration_results = {
            'iteration': iteration,
            'batches_processed': start_batch - 1,
            'documents_analysed': len(processed_doc_ids),
            'batch_results': [],
            'new_discoveries': 0
        }
        
        # Process each batch with checkpoint
        for i, batch in enumerate(batches, start_batch):
            print(f"    Batch {i}/{len(batches) + start_batch - 1}: {len(batch)} documents")
            
            try:
                # Get current context
                context = self.knowledge_graph.get_context_for_phase(phase)
                
                # Build investigation prompt
                prompt = self.autonomous_prompts.investigation_prompt(
                    documents=batch,
                    context=context,
                    phase=phase
                )
                
                # Call Claude
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='deep_investigation',
                    phase=phase
                )
                
                # Extract discoveries
                discoveries = self._extract_discoveries_from_response(response, phase)
                iteration_results['new_discoveries'] += len(discoveries)
                
                # Track processed documents
                batch_doc_ids = [doc.get('id', doc.get('filename', f'doc_{j}')) 
                               for j, doc in enumerate(batch)]
                processed_doc_ids.extend(batch_doc_ids)
                
                iteration_results['documents_analysed'] += len(batch)
                iteration_results['batches_processed'] = i
                
                iteration_results['batch_results'].append({
                    'batch_num': i,
                    'documents': len(batch),
                    'discoveries': len(discoveries)
                })
                
                # ✅ CRITICAL: Save checkpoint after batch
                self._save_batch_checkpoint(
                    phase=phase,
                    batch_num=i,
                    batch_results={'discoveries': len(discoveries)},
                    doc_ids=processed_doc_ids
                )
                
                # Delay between batches
                if i < len(batches) + start_batch - 1:
                    time.sleep(self.config.api_config['rate_limit_delay'])
            
            except Exception as e:
                print(f"      ❌ Error in batch {i}: {e}")
                print(f"      ✓ Progress saved up to batch {i-1}")
                raise
        
        # Clear checkpoints after successful completion
        self._clear_phase_checkpoints(phase)
        
        return iteration_results
    
    # ============================================================================
    # INVESTIGATION & SYNTHESIS (Unchanged)
    # ============================================================================
    
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
                    priority=child['priority']
                )
        
        return findings
    
    def _execute_synthesis(self, results: Dict) -> Dict:
        """Execute final synthesis"""
        
        # Get all knowledge from graph
        knowledge_export = self.knowledge_graph.export_for_report()
        
        # Build synthesis prompt
        prompt = self.synthesis_prompts.final_strategic_synthesis_prompt(
            all_findings=knowledge_export,
            phase_results=results['phases'],
            investigation_results=results['investigations']
        )
        
        # Call Claude
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='synthesis',
            phase='final_synthesis'
        )
        
        synthesis = {
            'narrative': response,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        # Save synthesis
        self._save_synthesis(synthesis)
        
        return synthesis
    
    def _generate_war_room_dashboard(self, results: Dict) -> Dict:
        """Generate executive dashboard"""
        
        # Prepare dashboard data
        stats = self.knowledge_graph.get_statistics()
        
        current_status = {
            'phases_completed': len(results['phases']),
            'investigations_conducted': len(results['investigations']),
            'entities': stats['entities'],
            'contradictions': stats['contradictions'],
            'patterns': stats['patterns']
        }
        
        critical_findings = self.knowledge_graph.get_critical_findings(limit=10)
        active_investigations = self.knowledge_graph.get_investigation_queue(limit=5)
        strategic_options = []
        
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
        """Check if analysis has converged"""
        
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
            if trend[-1] < trend[-2] < trend[-3]:
                if trend[-1] < 5:
                    return True
        
        return False
    
    # ============================================================================
    # HELPER METHODS (Unchanged)
    # ============================================================================
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory using DocumentLoader"""
        
        loader = DocumentLoader(self.config)
        
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
        
        all_docs = self._load_documents(self.config.disclosure_dir)
        relevant_docs = []
        
        investigation_data = investigation.get('data', {})
        
        for doc in all_docs:
            relevance_score = 0
            content_lower = doc['content'].lower()
            
            if 'contradiction' in investigation['type']:
                if 'statement_a' in investigation_data:
                    if investigation_data['statement_a'].lower()[:50] in content_lower:
                        relevance_score += 1.0
            
            if relevance_score > 0:
                relevant_docs.append(doc)
        
        return relevant_docs[:50]
    
    def _extract_knowledge_from_response(self, response: str, phase: str):
        """Extract and store knowledge from response"""
        # Simplified - implement parsing logic
        pass
    
    def _extract_discoveries_from_response(self, response: str, phase: str) -> List[Dict]:
        """Extract discoveries from response"""
        # Simplified - implement parsing logic
        return []
    
    def _extract_investigation_findings(self, response: str, investigation: Dict) -> Dict:
        """Extract investigation findings"""
        # Simplified - implement parsing logic
        return {}
    
    def _update_knowledge_from_results(self, results: Dict, phase: str):
        """Update knowledge graph from phase results"""
        pass
    
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
        
        stats = self.knowledge_graph.get_statistics()
        
        print(f"Phases Completed: {len(results['phases'])}")
        print(f"Investigations Conducted: {len(results['investigations'])}")
        print(f"Entities Identified: {stats['entities']}")
        print(f"Relationships Mapped: {stats['relationships']}")
        print(f"Contradictions Found: {stats['contradictions']}")
        print(f"Patterns Discovered: {stats['patterns']}")
        print(f"Timeline Events: {stats['timeline_events']}")
        
        usage = self.api_client.get_usage_report()
        print(f"\nAPI Usage:")
        print(f"  Total Calls: {usage['summary']['total_calls']}")
        print(f"  Estimated Cost: ${usage['summary']['estimated_cost_usd']}")
        
        print("\n" + "="*60)