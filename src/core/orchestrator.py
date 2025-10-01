#!/usr/bin/env python3
"""
Litigation Intelligence Orchestrator
COMPLETE REPLACEMENT for src/core/orchestrator.py

Coordinates multi-phase comprehensive litigation analysis for Lismore:
- Phase 0: Legal knowledge synthesis
- Phase 1: Disclosure analysis (iterative with prompt caching)
- Phase 2: Pattern synthesis
- Phase 3: Strategic report generation

Implements prompt caching for cost efficiency
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import time

from ..api.client import ClaudeClient
from ..core.config import get_config
from ..knowledge.graph import KnowledgeGraph
from ..utils.logger import get_logger
from ..utils.document_processor import DocumentProcessor
from ..prompts.autonomous import AutonomousPrompts
from ..prompts.recursive import RecursivePrompts
from ..prompts.synthesis import SynthesisPrompts


class LitigationOrchestrator:
    """
    Orchestrates comprehensive litigation intelligence analysis
    
    Multi-phase approach:
    1. Knowledge synthesis (legal framework + case context)
    2. Iterative disclosure analysis (with caching)
    3. Cross-document pattern detection
    4. Strategic synthesis for Lismore
    """
    
    def __init__(self):
        """Initialise orchestrator"""
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Core components
        self.api_client = ClaudeClient()
        self.knowledge_graph = KnowledgeGraph()
        self.doc_processor = DocumentProcessor()
        
        # Prompt generators
        self.autonomous_prompts = AutonomousPrompts()
        self.recursive_prompts = RecursivePrompts()
        self.synthesis_prompts = SynthesisPrompts()
        
        # State tracking
        self.current_phase = None
        self.analysis_state = {
            'phase_0_complete': False,
            'legal_knowledge_synthesised': False,
            'disclosure_batches_processed': 0,
            'total_documents_analysed': 0,
            'high_value_findings': 0,
            'recursive_investigations_triggered': 0
        }
        
        # Cacheable context (built once, reused across batches)
        self.cacheable_context = None
        
        self.logger.info("Litigation orchestrator initialised")
    
    def run_full_analysis(
        self,
        legal_knowledge_dir: Optional[Path] = None,
        case_background_dir: Optional[Path] = None,
        disclosure_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Run complete multi-phase litigation analysis
        
        Args:
            legal_knowledge_dir: Directory with legal framework docs
            case_background_dir: Directory with case context
            disclosure_dir: Directory with disclosure documents
        
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        self.logger.info("=" * 60)
        self.logger.info("STARTING COMPREHENSIVE LITIGATION ANALYSIS")
        self.logger.info("Target: Process Holdings (PH)")
        self.logger.info("Client: Lismore Capital")
        self.logger.info("=" * 60)
        
        try:
            # Phase 0: Legal Knowledge Synthesis
            legal_knowledge = self._execute_phase_0(
                legal_knowledge_dir,
                case_background_dir
            )
            
            # Phase 1: Disclosure Analysis (Iterative with Caching)
            disclosure_results = self._execute_phase_1(disclosure_dir)
            
            # Phase 2: Pattern Synthesis
            patterns = self._execute_phase_2()
            
            # Phase 3: Strategic Report
            final_report = self._execute_phase_3(
                legal_knowledge,
                disclosure_results,
                patterns
            )
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Final statistics
            self.api_client.log_final_statistics()
            
            self.logger.info("=" * 60)
            self.logger.info(f"ANALYSIS COMPLETE in {total_time/60:.1f} minutes")
            self.logger.info(f"Documents analysed: {self.analysis_state['total_documents_analysed']}")
            self.logger.info(f"High-value findings: {self.analysis_state['high_value_findings']}")
            self.logger.info(f"Recursive investigations: {self.analysis_state['recursive_investigations_triggered']}")
            self.logger.info("=" * 60)
            
            return {
                'legal_knowledge': legal_knowledge,
                'disclosure_analysis': disclosure_results,
                'patterns': patterns,
                'final_report': final_report,
                'statistics': {
                    'total_time_seconds': total_time,
                    'documents_analysed': self.analysis_state['total_documents_analysed'],
                    'high_value_findings': self.analysis_state['high_value_findings'],
                    'api_usage': self.api_client.get_usage_summary()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise
    
    def _execute_phase_0(
        self,
        legal_knowledge_dir: Optional[Path],
        case_background_dir: Optional[Path]
    ) -> Dict[str, Any]:
        """
        Phase 0: Synthesise Legal Knowledge and Case Context
        
        This creates the foundational understanding that will be cached
        and reused across all subsequent analysis phases.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PHASE 0: LEGAL KNOWLEDGE SYNTHESIS")
        self.logger.info("=" * 60)
        
        self.current_phase = 'phase_0_knowledge_synthesis'
        
        # Load legal framework documents
        legal_docs = []
        if legal_knowledge_dir and legal_knowledge_dir.exists():
            legal_docs = self.doc_processor.load_directory(legal_knowledge_dir)
            self.logger.info(f"Loaded {len(legal_docs)} legal framework documents")
        
        # Load case background
        case_docs = []
        if case_background_dir and case_background_dir.exists():
            case_docs = self.doc_processor.load_directory(case_background_dir)
            self.logger.info(f"Loaded {len(case_docs)} case background documents")
        
        if not legal_docs and not case_docs:
            self.logger.warning("No legal knowledge or case background provided")
            return {'status': 'skipped', 'reason': 'no_input_documents'}
        
        # Generate knowledge synthesis prompt
        prompt = self.autonomous_prompts.knowledge_synthesis_prompt(
            legal_knowledge=legal_docs,
            case_context=case_docs,
            existing_knowledge={}
        )
        
        # Call Claude (no caching yet - this is first call)
        self.logger.info("Synthesising legal knowledge with Claude...")
        response, metadata = self.api_client.call_claude_with_cache(
            prompt=prompt,
            cacheable_context="",  # Nothing to cache yet
            task_type='knowledge_synthesis',
            phase='phase_0'
        )
        
        # Parse response
        legal_knowledge = self._parse_knowledge_synthesis(response)
        
        # Store in knowledge graph
        self.knowledge_graph.add_legal_framework(legal_knowledge)
        
        # Mark phase complete
        self.analysis_state['phase_0_complete'] = True
        self.analysis_state['legal_knowledge_synthesised'] = True
        
        self.logger.info(f"✓ Phase 0 complete. Synthesised {len(legal_knowledge.get('principles', []))} legal principles")
        
        return legal_knowledge
    
    def _execute_phase_1(self, disclosure_dir: Optional[Path]) -> Dict[str, Any]:
        """
        Phase 1: Comprehensive Disclosure Analysis
        
        Processes disclosure in batches with prompt caching for efficiency.
        Runs multiple iterations for depth.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PHASE 1: DISCLOSURE ANALYSIS")
        self.logger.info("=" * 60)
        
        self.current_phase = 'phase_1_disclosure_analysis'
        
        if not disclosure_dir or not disclosure_dir.exists():
            self.logger.error("No disclosure directory provided")
            return {'status': 'failed', 'reason': 'no_disclosure_directory'}
        
        # Load all disclosure documents
        all_docs = self.doc_processor.load_directory(disclosure_dir)
        self.logger.info(f"Loaded {len(all_docs)} disclosure documents")
        
        if not all_docs:
            return {'status': 'failed', 'reason': 'no_documents_found'}
        
        # Get iteration configuration
        iterations = self.config.orchestration_config['phases'][1].get('iterations', 3)
        batch_size = self.config.orchestration_config['phases'][1].get('batch_size', 50)
        
        # Run multiple iterations
        all_results = []
        for iteration in range(1, iterations + 1):
            self.logger.info(f"\n--- ITERATION {iteration}/{iterations} ---")
            
            iteration_results = self._execute_disclosure_iteration(
                iteration=iteration,
                documents=all_docs,
                batch_size=batch_size
            )
            
            all_results.append(iteration_results)
        
        # Consolidate results
        consolidated = self._consolidate_iteration_results(all_results)
        
        return consolidated
    
    def _execute_disclosure_iteration(
        self,
        iteration: int,
        documents: List[Dict],
        batch_size: int
    ) -> Dict[str, Any]:
        """
        Execute single iteration of disclosure analysis with prompt caching
        
        Key insight: The legal framework and knowledge graph context stays
        the same across ALL batches - perfect for caching.
        """
        self.logger.info(f"Processing {len(documents)} documents in batches of {batch_size}")
        
        # Build cacheable context ONCE per iteration
        cacheable_context = self._build_cacheable_context(iteration)
        
        # Split documents into batches
        batches = [
            documents[i:i + batch_size]
            for i in range(0, len(documents), batch_size)
        ]
        
        self.logger.info(f"Created {len(batches)} batches for iteration {iteration}")
        
        # Process each batch
        batch_results = []
        for batch_num, batch in enumerate(batches, 1):
            self.logger.info(f"\nProcessing batch {batch_num}/{len(batches)} ({len(batch)} documents)")
            
            # Build unique prompt for this batch
            unique_prompt = self.autonomous_prompts.investigation_prompt(
                documents=batch,
                context={},  # Context is in cacheable part
                phase=f'iteration_{iteration}'
            )
            
            # Call Claude with caching (cacheable_context is cached after first batch)
            response, metadata = self.api_client.call_claude_with_cache(
                prompt=unique_prompt,
                cacheable_context=cacheable_context,
                task_type='investigation',
                phase=f'iteration_{iteration}_batch_{batch_num}'
            )
            
            # Parse findings
            findings = self._parse_investigation_response(response)
            
            # Check for high-value findings that need recursive investigation
            high_value = self._identify_high_value_findings(findings)
            
            if high_value:
                self.logger.info(f"Found {len(high_value)} high-value findings - triggering recursive investigation")
                recursive_results = self._execute_recursive_investigation(
                    findings=high_value,
                    documents=batch,
                    cacheable_context=cacheable_context
                )
                findings['recursive_investigations'] = recursive_results
                self.analysis_state['recursive_investigations_triggered'] += len(high_value)
            
            # Update knowledge graph
            self.knowledge_graph.add_findings(findings, phase=f'iteration_{iteration}')
            
            # Track statistics
            self.analysis_state['disclosure_batches_processed'] += 1
            self.analysis_state['total_documents_analysed'] += len(batch)
            self.analysis_state['high_value_findings'] += len(findings.get('critical_findings', []))
            
            batch_results.append({
                'batch_number': batch_num,
                'documents_processed': len(batch),
                'findings': findings,
                'metadata': metadata
            })
        
        return {
            'iteration': iteration,
            'batches': batch_results,
            'total_findings': sum(len(b['findings'].get('critical_findings', [])) for b in batch_results)
        }
    
    def _build_cacheable_context(self, iteration: int) -> str:
        """
        Build the cacheable context that stays consistent across batches
        
        This includes:
        - Legal framework (from Phase 0)
        - Knowledge graph accumulated context
        - Analysis mission and instructions
        - Hallucination prevention rules
        """
        # Get legal knowledge from KG
        legal_framework = self.knowledge_graph.get_legal_framework()
        
        # Get accumulated context from previous iterations
        kg_context = self.knowledge_graph.get_context_for_phase(f'iteration_{iteration}')
        
        # Build comprehensive cacheable context
        context = f"""
<critical_accuracy_requirements>
MANDATORY CITATION RULES:
1. EVERY factual claim MUST cite: [DOC_ID: Page X, Para Y]
2. NEVER speculate without [INFERENCE] label
3. Quote marks only for EXACT quotes
4. If cannot cite location, DO NOT make the claim
</critical_accuracy_requirements>

<case_mission>
COMPREHENSIVE LITIGATION ANALYSIS FOR LISMORE CAPITAL v PROCESS HOLDINGS

Objective: Find EVERYTHING that helps Lismore win this arbitration.

Analysis must be:
- Adversarial for Lismore (not neutral)
- Comprehensive across all legal grounds
- Evidence-based with mandatory citations
- Strategically focused on winning

Key areas:
1. Contract breaches by PH
2. Fraud/misrepresentation indicators
3. Fiduciary duty breaches
4. Credibility attacks on PH witnesses
5. Damages quantification
6. Legal arguments (liability + quantum)
7. Procedural advantages
8. Document withholding patterns
9. Timeline reconstruction
10. Strategic recommendations
</case_mission>

<legal_framework>
{json.dumps(legal_framework, indent=2)}
</legal_framework>

<knowledge_graph_context>
{json.dumps(kg_context, indent=2)}
</knowledge_graph_context>

<lismore_strategy>
Every finding must address: "How does this help Lismore win?"

Prioritise:
- Evidence proving PH breach/fraud
- Ammunition for cross-examination
- Damages supporting evidence
- Procedural leverage
- Novel legal arguments
</lismore_strategy>
"""
        
        return context
    
    def _identify_high_value_findings(self, findings: Dict) -> List[Dict]:
        """
        Identify findings that warrant recursive investigation
        
        Triggers:
        - Severity >= 7
        - Contract breach identified
        - Fraud indicators
        - Major contradictions
        - Significant damages evidence
        """
        high_value = []
        
        for finding in findings.get('critical_findings', []):
            severity = finding.get('severity', 0)
            finding_type = finding.get('type', '')
            
            # Check triggers
            if severity >= self.config.investigation_triggers.get('contradiction_severity', 7):
                high_value.append(finding)
            elif finding_type in ['contract_breach', 'fraud', 'fiduciary_breach']:
                high_value.append(finding)
            elif 'contradiction' in finding.get('description', '').lower():
                high_value.append(finding)
        
        return high_value
    
    def _execute_recursive_investigation(
        self,
        findings: List[Dict],
        documents: List[Dict],
        cacheable_context: str
    ) -> List[Dict]:
        """
        Execute recursive self-questioning on high-value findings
        
        Uses RecursivePrompts to dig deeper
        """
        recursive_results = []
        
        for finding in findings:
            self.logger.info(f"Recursive investigation: {finding.get('description', 'Unknown')[:50]}...")
            
            # Generate deep questioning prompt
            prompt = self.recursive_prompts.deep_questioning_prompt(
                finding=finding,
                documents=documents,
                knowledge_context={}  # In cacheable part
            )
            
            # Call Claude (still benefits from cacheable context)
            response, metadata = self.api_client.call_claude_with_cache(
                prompt=prompt,
                cacheable_context=cacheable_context,
                task_type='recursive_questioning',
                phase='recursive_investigation'
            )
            
            # Parse recursive findings
            recursive_finding = self._parse_recursive_response(response, finding)
            recursive_results.append(recursive_finding)
        
        return recursive_results
    
    def _execute_phase_2(self) -> Dict[str, Any]:
        """
        Phase 2: Cross-Document Pattern Synthesis
        
        Analyses patterns across all findings accumulated in KG
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PHASE 2: PATTERN SYNTHESIS")
        self.logger.info("=" * 60)
        
        self.current_phase = 'phase_2_pattern_synthesis'
        
        # Get all findings from knowledge graph
        all_findings = self.knowledge_graph.get_all_findings()
        
        if not all_findings:
            self.logger.warning("No findings to analyse for patterns")
            return {'status': 'skipped', 'reason': 'no_findings'}
        
        self.logger.info(f"Analysing patterns across {len(all_findings)} findings")
        
        # Generate pattern detection prompt
        prompt = self.autonomous_prompts.pattern_discovery_prompt(
            documents=[],  # Not needed - working from findings
            known_patterns={},
            context={'all_findings': all_findings}
        )
        
        # Build cacheable context
        cacheable_context = self._build_cacheable_context(iteration=999)  # Use final context
        
        # Call Claude
        response, metadata = self.api_client.call_claude_with_cache(
            prompt=prompt,
            cacheable_context=cacheable_context,
            task_type='pattern_recognition',
            phase='phase_2'
        )
        
        # Parse patterns
        patterns = self._parse_pattern_response(response)
        
        # Store in knowledge graph
        self.knowledge_graph.add_patterns(patterns)
        
        self.logger.info(f"✓ Phase 2 complete. Identified {len(patterns.get('patterns', []))} patterns")
        
        return patterns
    
    def _execute_phase_3(
        self,
        legal_knowledge: Dict,
        disclosure_results: Dict,
        patterns: Dict
    ) -> Dict[str, Any]:
        """
        Phase 3: Strategic Synthesis - Final Report for Lismore
        
        Generates tribunal-ready strategic report
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PHASE 3: STRATEGIC SYNTHESIS")
        self.logger.info("=" * 60)
        
        self.current_phase = 'phase_3_strategic_synthesis'
        
        # Get complete knowledge graph
        complete_context = self.knowledge_graph.get_complete_context()
        
        # Generate final synthesis prompt
        prompt = self.synthesis_prompts.strategic_synthesis_prompt(
            legal_framework=legal_knowledge,
            all_findings=complete_context.get('findings', []),
            patterns=patterns,
            timeline=complete_context.get('timeline', {}),
            knowledge_graph=complete_context
        )
        
        # Build final cacheable context
        cacheable_context = self._build_cacheable_context(iteration=999)
        
        # Call Claude for final report
        self.logger.info("Generating final strategic report...")
        response, metadata = self.api_client.call_claude_with_cache(
            prompt=prompt,
            cacheable_context=cacheable_context,
            task_type='synthesis',
            phase='phase_3_final'
        )
        
        # Parse final report
        final_report = self._parse_final_report(response)
        
        # Save report
        self._save_final_report(final_report)
        
        self.logger.info("✓ Phase 3 complete. Final report generated")
        
        return final_report
    
    # Response parsing methods
    
    def _parse_knowledge_synthesis(self, response: str) -> Dict[str, Any]:
        """Parse Phase 0 knowledge synthesis response"""
        try:
            # Look for JSON in response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                # Fallback: return raw response
                return {'raw_synthesis': response}
        except Exception as e:
            self.logger.error(f"Failed to parse knowledge synthesis: {e}")
            return {'raw_synthesis': response}
    
    def _parse_investigation_response(self, response: str) -> Dict[str, Any]:
        """Parse investigation findings"""
        try:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return {'raw_response': response}
        except Exception as e:
            self.logger.error(f"Failed to parse investigation response: {e}")
            return {'raw_response': response}
    
    def _parse_recursive_response(self, response: str, original_finding: Dict) -> Dict[str, Any]:
        """Parse recursive investigation response"""
        return {
            'original_finding': original_finding,
            'recursive_analysis': response,
            'timestamp': datetime.now().isoformat()
        }
    
    def _parse_pattern_response(self, response: str) -> Dict[str, Any]:
        """Parse pattern detection response"""
        try:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return {'raw_patterns': response}
        except Exception as e:
            self.logger.error(f"Failed to parse patterns: {e}")
            return {'raw_patterns': response}
    
    def _parse_final_report(self, response: str) -> Dict[str, Any]:
        """Parse final strategic report"""
        return {
            'report': response,
            'generated_at': datetime.now().isoformat(),
            'statistics': self.analysis_state
        }
    
    def _consolidate_iteration_results(self, all_results: List[Dict]) -> Dict[str, Any]:
        """Consolidate results from multiple iterations"""
        consolidated = {
            'iterations': all_results,
            'total_batches': sum(len(r['batches']) for r in all_results),
            'total_findings': sum(r['total_findings'] for r in all_results),
            'statistics': self.analysis_state
        }
        return consolidated
    
    def _save_final_report(self, report: Dict) -> None:
        """Save final report to disk"""
        output_dir = self.config.get_directory('reports')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_path = output_dir / f'final_report_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save as Markdown
        md_path = output_dir / f'final_report_{timestamp}.md'
        with open(md_path, 'w') as f:
            f.write(report.get('report', 'No report content'))
        
        self.logger.info(f"Final report saved to: {md_path}")