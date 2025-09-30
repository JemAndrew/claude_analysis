#!/usr/bin/env python3
"""
Phase Executor - Simplified for Maximum Claude Autonomy
Only 3 phase types: Legal Knowledge, Case Understanding, Free Investigation
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import re


class PhaseExecutor:
    """Executes phases with complete Claude autonomy"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        
        # Simple phase mapping - only 3 real phase types
        self.phase_strategies = {
            '0': self._execute_legal_knowledge,
            '1': self._execute_case_understanding,
            # Everything else uses free investigation
        }
    
    def execute(self, phase: str, context: Dict) -> Dict:
        """
        Execute phase with appropriate strategy
        Phase 0 = Legal knowledge only
        Phase 1 = Case understanding
        Phase 2+ = Free investigation iterations
        """
        
        print(f"\n{'='*60}")
        print(f"PHASE {phase}")
        print(f"{'='*60}")
        
        # Check if specific strategy exists
        if phase in self.phase_strategies:
            return self.phase_strategies[phase](context)
        
        # Everything else is free investigation
        iteration = int(phase) - 1
        return self._execute_investigation_iteration(iteration, context)
    
    def _execute_legal_knowledge(self, context: Dict) -> Dict:
        """
        Phase 0: Learn legal frameworks ONLY
        No case documents yet - just pure legal learning
        """
        
        print("  📚 Strategy: Legal Framework Mastery")
        print("  Loading legal knowledge documents...")
        
        # Load ONLY legal documents
        legal_docs = self._load_documents(self.config.legal_knowledge_dir)
        
        if not legal_docs:
            print("  ⚠️ No legal documents found - skipping legal knowledge phase")
            return {
                'phase': '0',
                'strategy': 'legal_framework_skipped',
                'documents_processed': 0,
                'synthesis': 'No legal documents provided',
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"  Found {len(legal_docs)} legal documents")
        
        # Build legal knowledge prompt using autonomous prompts
        prompt = self.orchestrator.autonomous_prompts.knowledge_synthesis_prompt(
            legal_knowledge=legal_docs,
            case_context=[],  # No case context in Phase 0
            existing_knowledge=""
        )
        
        # Execute with Sonnet 4.5 for maximum learning
        print("  🤖 Calling Claude Sonnet 4.5 for legal analysis...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],  # Force Sonnet 4.5
            task_type='knowledge_synthesis',
            phase='0'
        )
        
        # Store legal knowledge in knowledge graph
        self._store_legal_knowledge(response)
        
        print(f"  ✅ Legal knowledge synthesised")
        print(f"     Tokens: {metadata.get('input_tokens', 0):,} in / {metadata.get('output_tokens', 0):,} out")
        
        return {
            'phase': '0',
            'strategy': 'legal_framework_mastery',
            'documents_processed': len(legal_docs),
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_case_understanding(self, context: Dict) -> Dict:
        """
        Phase 1: Understand the case (first complete read)
        Claude reads ALL case documents and builds understanding
        Marks anything interesting for investigation
        """
        
        print("  📖 Strategy: Complete Case Understanding")
        print("  Loading ALL case documents for first read...")
        
        # FIXED: Use correct directory names
        # Try case_context first (case background), then disclosure (main documents)
        case_docs = self._load_documents(self.config.case_context_dir)
        
        if not case_docs:
            print("  ℹ️ No case context documents, trying disclosure directory...")
            case_docs = self._load_documents(self.config.disclosure_dir)
        
        if not case_docs:
            print("  ⚠️ No case documents found in either directory!")
            return {
                'phase': '1',
                'strategy': 'case_understanding_failed',
                'documents_processed': 0,
                'error': 'No case documents found',
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"  Found {len(case_docs)} case documents")
        
        # Get legal knowledge from phase 0
        legal_framework = context.get('legal_knowledge', 'Legal framework loaded')
        
        # Build case understanding prompt
        # FIXED: Check if method exists, use fallback if not
        try:
            prompt = self.orchestrator.autonomous_prompts.case_understanding_prompt(
                case_documents=case_docs,
                legal_framework=str(legal_framework)[:10000],
                doc_count=len(case_docs)
            )
        except AttributeError:
            # Fallback: Use investigation prompt
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=case_docs,
                context={'legal_knowledge': str(legal_framework)[:10000]},
                phase='1'
            )
        
        # Execute with Sonnet 4.5
        print("  🤖 Calling Claude Sonnet 4.5 for complete case analysis...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='case_understanding',
            phase='1'
        )
        
        # Extract all discovery markers
        discoveries = self._extract_all_markers(response)
        
        # Store discoveries in knowledge graph
        self._store_case_understanding(response, discoveries)
        
        print(f"  ✅ Case understanding complete")
        print(f"     Documents: {len(case_docs)}")
        print(f"     Discoveries: {len(discoveries)}")
        print(f"     Tokens: {metadata.get('input_tokens', 0):,} in / {metadata.get('output_tokens', 0):,} out")
        
        return {
            'phase': '1',
            'strategy': 'case_understanding',
            'documents_processed': len(case_docs),
            'discoveries': discoveries,
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_investigation_iteration(self, iteration: int, context: Dict) -> Dict:
        """
        Phase 2+: Free investigation iterations
        Claude decides what to investigate based on previous findings
        No predetermined focus - complete autonomy
        """
        
        print(f"  🔍 Strategy: Free Investigation (Iteration {iteration})")
        print("  Claude has complete freedom to investigate anything...")
        
        # Get all previous findings from knowledge graph
        previous_findings = self.orchestrator.knowledge_graph.get_context_for_phase(f"investigation_{iteration}")
        
        # FIXED: Use autonomous_prompts (simplified_prompts doesn't exist)
        prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
            documents=[],  # Load from context
            context={
                'iteration': iteration,
                'previous_findings': previous_findings,
                **context
            },
            phase=f'investigation_{iteration}'
        )
        
        # Execute with Sonnet 4.5
        print(f"  🤖 Calling Claude Sonnet 4.5 for investigation {iteration}...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='investigation',
            phase=f'investigation_{iteration}'
        )
        
        # Extract discoveries and new investigation threads
        discoveries = self._extract_all_markers(response)
        
        # Store investigation results
        self._store_investigation_results(iteration, response, discoveries)
        
        # Check for convergence (no new discoveries)
        converged = self._check_convergence(discoveries, iteration)
        
        print(f"  ✅ Investigation {iteration} complete")
        print(f"     New discoveries: {len(discoveries)}")
        print(f"     Converged: {'Yes' if converged else 'No'}")
        print(f"     Tokens: {metadata.get('input_tokens', 0):,} in / {metadata.get('output_tokens', 0):,} out")
        
        return {
            'phase': f'investigation_{iteration}',
            'iteration': iteration,
            'strategy': 'free_investigation',
            'discoveries': discoveries,
            'converged': converged,
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
    
    # ==================== HELPER METHODS ====================
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load all documents from directory (recursively handles subdirectories)"""
        
        if not directory.exists():
            print(f"  ⚠️ Directory does not exist: {directory}")
            return []
        
        # FIXED: Correct import path and pass config
        try:
            from utils.document_loader import DocumentLoader
            loader = DocumentLoader(self.config)  # Pass config
            return loader.load_directory(directory)
        except Exception as e:
            print(f"  ❌ Error loading documents: {e}")
            return []
    
    def _extract_all_markers(self, response: str) -> List[Dict]:
        """Extract all discovery markers from response"""
        
        discoveries = []
        
        # Extract NUCLEAR findings
        nuclear_pattern = r'\[NUCLEAR\](.*?)(?=\[|$)'
        for match in re.finditer(nuclear_pattern, response, re.DOTALL):
            discoveries.append({
                'type': 'NUCLEAR',
                'content': match.group(1).strip()[:500],
                'severity': 10,
                'timestamp': datetime.now().isoformat()
            })
        
        # Extract CRITICAL findings
        critical_pattern = r'\[CRITICAL\](.*?)(?=\[|$)'
        for match in re.finditer(critical_pattern, response, re.DOTALL):
            discoveries.append({
                'type': 'CRITICAL',
                'content': match.group(1).strip()[:500],
                'severity': 8,
                'timestamp': datetime.now().isoformat()
            })
        
        # Extract INVESTIGATE threads
        investigate_pattern = r'\[INVESTIGATE\](.*?)(?=\[|$)'
        for match in re.finditer(investigate_pattern, response, re.DOTALL):
            discoveries.append({
                'type': 'INVESTIGATE',
                'content': match.group(1).strip()[:500],
                'severity': 6,
                'timestamp': datetime.now().isoformat()
            })
        
        # Extract SUSPICIOUS findings
        suspicious_pattern = r'\[SUSPICIOUS\](.*?)(?=\[|$)'
        for match in re.finditer(suspicious_pattern, response, re.DOTALL):
            discoveries.append({
                'type': 'SUSPICIOUS',
                'content': match.group(1).strip()[:500],
                'severity': 5,
                'timestamp': datetime.now().isoformat()
            })
        
        return discoveries
    
    def _store_legal_knowledge(self, response: str):
        """Store legal knowledge in knowledge graph (with fallbacks)"""
        
        # Try multiple storage methods
        try:
            # Primary method
            self.orchestrator.knowledge_graph.store_legal_knowledge(response, '0')
            print("  ✅ Stored in knowledge graph")
        except AttributeError:
            try:
                # Alternative method
                self.orchestrator.knowledge_graph.add_analysis_result({
                    'phase': '0',
                    'type': 'legal_knowledge',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                print("  ✅ Stored as analysis result")
            except:
                # Fallback: Save to file
                output_dir = self.config.analysis_dir / "phase_0"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / "legal_knowledge.txt"
                output_file.write_text(response, encoding='utf-8')
                print(f"  ✅ Saved to {output_file}")
    
    def _store_case_understanding(self, response: str, discoveries: List[Dict]):
        """Store case understanding and discoveries (with fallbacks)"""
        
        # Always save discoveries to file (guaranteed to work)
        output_dir = self.config.analysis_dir / "phase_1"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full response
        response_file = output_dir / "case_understanding.txt"
        response_file.write_text(response, encoding='utf-8')
        
        # Save discoveries as JSON
        discoveries_file = output_dir / "discoveries.json"
        with open(discoveries_file, 'w', encoding='utf-8') as f:
            json.dump(discoveries, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved to {output_dir}/")
        
        # Try to store in knowledge graph and spawn investigations
        for discovery in discoveries:
            if discovery['type'] in ['NUCLEAR', 'CRITICAL']:
                try:
                    # Try to spawn investigation
                    investigation_id = self.orchestrator.spawn_investigation(
                        trigger_type='critical_discovery',
                        trigger_data=discovery,
                        priority=discovery['severity']
                    )
                    print(f"  ✅ Spawned investigation: {investigation_id}")
                except Exception as e:
                    # Log but don't crash
                    print(f"  ℹ️ Investigation spawning not available: {e}")
                    
                    # Save to investigations directory as fallback
                    inv_dir = self.config.investigations_dir / "phase_1_triggers"
                    inv_dir.mkdir(parents=True, exist_ok=True)
                    
                    inv_file = inv_dir / f"{discovery['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    inv_file.write_text(discovery['content'], encoding='utf-8')
    
    def _store_investigation_results(self, iteration: int, response: str, discoveries: List[Dict]):
        """Store investigation results (with fallbacks)"""
        
        # Always save to file
        output_dir = self.config.analysis_dir / f"investigation_{iteration}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full response
        response_file = output_dir / "investigation.txt"
        response_file.write_text(response, encoding='utf-8')
        
        # Save discoveries
        discoveries_file = output_dir / "discoveries.json"
        with open(discoveries_file, 'w', encoding='utf-8') as f:
            json.dump(discoveries, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved to {output_dir}/")
        
        # Try to spawn new investigations
        for discovery in discoveries:
            if discovery['severity'] >= 8:
                try:
                    investigation_id = self.orchestrator.spawn_investigation(
                        trigger_type='investigation_discovery',
                        trigger_data=discovery,
                        priority=discovery['severity']
                    )
                    print(f"  ✅ Spawned investigation: {investigation_id}")
                except Exception as e:
                    # Save as trigger file
                    inv_dir = self.config.investigations_dir / f"iteration_{iteration}_triggers"
                    inv_dir.mkdir(parents=True, exist_ok=True)
                    
                    inv_file = inv_dir / f"{discovery['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    inv_file.write_text(discovery['content'], encoding='utf-8')
    
    def _check_convergence(self, discoveries: List[Dict], iteration: int) -> bool:
        """Check if investigation has converged (no new significant discoveries)"""
        
        # Check if we have critical/nuclear discoveries
        critical_count = sum(1 for d in discoveries if d.get('severity', 0) >= 8)
        
        # If no critical discoveries and past iteration 3, consider converged
        if critical_count == 0 and iteration >= 3:
            print("  ℹ️ Convergence: No critical discoveries after iteration 3")
            return True
        
        # If we've done 10+ iterations, force convergence
        if iteration >= 10:
            print("  ℹ️ Convergence: Maximum iterations (10) reached")
            return True
        
        # If less than 2 total discoveries, converged
        if len(discoveries) < 2:
            print("  ℹ️ Convergence: Minimal discoveries found")
            return True
        
        return False