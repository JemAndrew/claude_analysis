#!/usr/bin/env python3
"""
Litigation Orchestrator - Staged Execution Architecture
Phase 0 → Phase 1 → Phase 2-N with autonomous investigation
British English throughout - Lismore v Process Holdings
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

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
    """
    Staged execution orchestrator
    Phase 0: Legal knowledge
    Phase 1: Case understanding
    Phase 2-N: Autonomous investigation
    """
    
    def __init__(self):
        """Initialise orchestrator with all components"""
        
        self.config = config
        
        # Core components
        self.knowledge_graph = KnowledgeGraph(config)
        self.api_client = ClaudeClient(config)
        self.context_manager = ContextManager(config)
        self.batch_manager = BatchManager(config)
        self.phase_executor = PhaseExecutor(config, self)
        
        # Prompt systems
        self.autonomous_prompts = AutonomousPrompts(config)
        self.recursive_prompts = RecursivePrompts(config)
        self.synthesis_prompts = SynthesisPrompts(config)
        
        # State tracking
        self.state = {
            'phases_completed': [],
            'current_iteration': 0,
            'discoveries': [],
            'convergence_metrics': {}
        }
        
        self._load_state()
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE EXECUTION
    # ═══════════════════════════════════════════════════════════════
    
    def execute_phase(self, phase: str) -> Dict:
        """
        Execute specific phase
        Supports: '0', '1', '2', '3', etc.
        """
        
        if phase == '0':
            return self._execute_phase_0()
        elif phase == '1':
            return self._execute_phase_1()
        else:
            # Phase 2+ are investigation iterations
            iteration = int(phase)
            return self._execute_investigation_iteration(iteration)
    
    def execute_full_analysis(self, start_phase: str = '0', max_iterations: int = 5) -> Dict:
        """
        Execute complete analysis
        Phase 0 → Phase 1 → Phase 2-N
        """
        
        results = {
            'phases': {},
            'iterations': {},
            'final_synthesis': None
        }
        
        # Phase 0: Legal knowledge
        if '0' not in self.state['phases_completed']:
            print("\n[PHASE 0] Legal Knowledge Mastery")
            results['phases']['0'] = self._execute_phase_0()
        
        # Phase 1: Case understanding
        if '1' not in self.state['phases_completed']:
            print("\n[PHASE 1] Complete Case Understanding")
            results['phases']['1'] = self._execute_phase_1()
        
        # Phase 2-N: Autonomous investigation
        print("\n[PHASE 2-N] Autonomous Investigation")
        
        converged = False
        iteration = 2
        
        while not converged and iteration < (2 + max_iterations):
            print(f"\n  Iteration {iteration - 1}...")
            iter_results = self._execute_investigation_iteration(iteration)
            results['iterations'][iteration] = iter_results
            
            converged = iter_results.get('converged', False)
            iteration += 1
        
        # Final synthesis
        print("\n[SYNTHESIS] Building Strategic Narrative")
        results['final_synthesis'] = self._execute_synthesis(results)
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 0: LEGAL KNOWLEDGE MASTERY
    # ═══════════════════════════════════════════════════════════════
    
    def _execute_phase_0(self) -> Dict:
        """
        Phase 0: Load legal documents only and synthesise legal framework
        Cost: ~$0.10, Time: ~5 minutes
        """
        
        print("  Loading legal documents...")
        
        # Load legal documents
        loader = DocumentLoader(self.config)
        legal_docs = loader.load_directory(self.config.legal_knowledge_dir)
        
        print(f"  Loaded {len(legal_docs)} legal documents")
        
        # Build legal mastery prompt
        prompt = self._build_legal_knowledge_prompt(legal_docs)
        
        # Call Claude Sonnet 4.5
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model='claude-sonnet-4-20250514',  # Sonnet 4.5
            task_type='legal_knowledge',
            phase='0'
        )
        
        # Store legal knowledge
        self.knowledge_graph.log_discovery(
            discovery_type='LEGAL_FRAMEWORK',
            content=response[:2000],
            importance='HIGH',
            phase='0'
        )
        
        # Mark phase complete
        self.state['phases_completed'].append('0')
        self._save_state()
        
        # Save output
        results = {
            'phase': '0',
            'documents_processed': len(legal_docs),
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_phase_output('0', results)
        
        return results
    
    def _build_legal_knowledge_prompt(self, legal_docs: List[Dict]) -> str:
        """Build prompt for legal knowledge synthesis"""
        
        docs_formatted = self.autonomous_prompts._format_documents(legal_docs, "LEGAL")
        
        return f"""<mission>
You are building a complete legal framework for Lismore v Process Holdings litigation.
Absorb ALL legal knowledge. Create a mental model of available legal weapons.
</mission>

<approach>
As you read these legal documents:
1. Identify applicable laws, statutes, precedents
2. Note duties Process Holdings owed to Lismore
3. Identify potential causes of action
4. Spot defences they might raise
5. Build strategic legal framework
</approach>

<legal_documents>
{docs_formatted}
</legal_documents>

<output_requirements>
Synthesise complete legal framework covering:

APPLICABLE LAW:
- What laws govern this dispute?
- What duties exist?
- What standards apply?

CAUSES OF ACTION:
- What can we sue for?
- Elements we must prove for each
- Strength of each claim

DEFENCES TO ANTICIPATE:
- What will they argue?
- How do we counter?

STRATEGIC WEAPONS:
- Most powerful legal arguments
- Precedents in our favour
- Statutory provisions that help us

Provide comprehensive synthesis showing deep legal understanding.
Mark key strategic insights with [STRATEGIC].
</output_requirements>"""
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: COMPLETE CASE UNDERSTANDING
    # ═══════════════════════════════════════════════════════════════
    
    def _execute_phase_1(self) -> Dict:
        """
        Phase 1: Load ALL case documents and build complete understanding
        Marks discoveries for later investigation
        Cost: ~$5-10, Time: ~15-30 minutes
        """
        
        print("  Loading ALL case documents (including subdirectories)...")
        
        # Load case documents recursively
        loader = DocumentLoader(self.config)
        case_docs = loader.load_directory(self.config.case_documents_dir)
        
        print(f"  Loaded {len(case_docs)} case documents")
        
        # Get legal framework from Phase 0
        legal_context = self.knowledge_graph.export_for_report()
        
        # Build case understanding prompt
        prompt = self._build_case_understanding_prompt(case_docs, legal_context)
        
        # Call Claude Sonnet 4.5 with full case
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model='claude-sonnet-4-20250514',
            task_type='case_understanding',
            phase='1'
        )
        
        # Extract discoveries
        discoveries = self.phase_executor.extract_discoveries(response, '1')
        
        # Store in knowledge graph
        for discovery in discoveries:
            self.knowledge_graph.log_discovery(
                discovery_type=discovery['type'],
                content=discovery['content'],
                importance=self._discovery_importance(discovery['type']),
                phase='1'
            )
        
        # Mark phase complete
        self.state['phases_completed'].append('1')
        self.state['discoveries'].extend(discoveries)
        self._save_state()
        
        # Save output
        results = {
            'phase': '1',
            'documents_processed': len(case_docs),
            'discoveries': discoveries,
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_phase_output('1', results)
        
        return results
    
    def _build_case_understanding_prompt(self, case_docs: List[Dict], legal_context: Dict) -> str:
        """Build prompt for complete case understanding"""
        
        docs_formatted = self.autonomous_prompts._format_documents(case_docs, "CASE")
        
        return f"""<mission>
Build COMPLETE understanding of Lismore v Process Holdings case.
Read ALL documents. Understand the full story.
Mark anything worth investigating further.
</mission>

<legal_framework>
You've already mastered the legal framework. Key points:
{json.dumps(legal_context, indent=2)[:2000]}
</legal_framework>

<case_documents>
{docs_formatted}
</case_documents>

<understanding_requirements>
Build comprehensive case understanding covering:

THE STORY:
- What happened chronologically?
- Who are the key players?
- What did everyone do?
- What went wrong?

THE EVIDENCE:
- What documents prove what?
- What's the strongest evidence?
- What's missing?

THE CLAIMS:
- How do facts map to legal claims?
- What can we prove?
- What's our strongest case?

THEIR DEFENCE:
- What will they argue?
- What evidence supports them?
- Where are they vulnerable?

INVESTIGATION PRIORITIES:
- Mark anything NUCLEAR (case-ending)
- Mark anything CRITICAL (major advantage)
- Mark anything worth deeper investigation [INVESTIGATE]

Provide complete synthesis showing deep case understanding.
</understanding_requirements>

<discovery_markers>
Use these markers liberally:
[NUCLEAR] - This wins the case
[CRITICAL] - Major strategic advantage
[INVESTIGATE] - Needs deeper investigation
[SUSPICIOUS] - Something doesn't add up
[MISSING] - Evidence that should exist
</discovery_markers>"""
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 2-N: AUTONOMOUS INVESTIGATION
    # ═══════════════════════════════════════════════════════════════
    
    def _execute_investigation_iteration(self, iteration: int) -> Dict:
        """
        Execute one iteration of autonomous investigation
        Claude investigates whatever it finds interesting
        """
        
        # Get accumulated knowledge
        context = self.knowledge_graph.export_for_report()
        all_docs = self._load_all_documents()
        
        # Build autonomous investigation prompt
        prompt = self._build_investigation_prompt(context, all_docs, iteration)
        
        # Call Claude with full autonomy
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model='claude-sonnet-4-20250514',
            task_type='autonomous_investigation',
            phase=f'investigation_{iteration}'
        )
        
        # Extract new discoveries
        discoveries = self.phase_executor.extract_discoveries(response, f'iteration_{iteration}')
        
        # Check convergence
        converged = self._check_convergence(discoveries)
        
        # Store results
        results = {
            'iteration': iteration,
            'new_discoveries': len(discoveries),
            'discoveries': discoveries,
            'converged': converged,
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save output
        self._save_phase_output(f'iteration_{iteration}', results)
        
        return results
    
    def _build_investigation_prompt(self, context: Dict, all_docs: List[Dict], iteration: int) -> str:
        """Build autonomous investigation prompt"""
        
        return f"""<autonomous_investigation>
ITERATION {iteration - 1}

You have COMPLETE AUTONOMY to investigate ANYTHING interesting.
No predetermined focus. Follow your instincts.
</autonomous_investigation>

<what_you_know>
{json.dumps(context, indent=2)[:5000]}
</what_you_know>

<all_case_documents>
You have access to all case documents. Focus on whatever intrigues you.
{len(all_docs)} documents available for investigation.
</all_case_documents>

<investigation_freedom>
Investigate ANYTHING that:
- Seems suspicious
- Doesn't add up
- Could be important
- Might reveal something
- Interests you strategically

You decide what matters. You decide what to investigate.
Follow every interesting thread.
</investigation_freedom>

<discovery_markers>
Mark what you find:
[NUCLEAR] - Case-ending discovery
[CRITICAL] - Major advantage
[PATTERN] - Significant pattern
[CONTRADICTION] - Important contradiction
[INVESTIGATE] - Needs even deeper look
</discovery_markers>

<instruction>
What do YOU find interesting in this case?
What threads do YOU want to follow?
Investigate autonomously. Report everything you discover.
</instruction>"""
    
    def _check_convergence(self, discoveries: List[Dict]) -> bool:
        """Check if investigation has converged"""
        
        # Count critical discoveries
        critical_count = sum(1 for d in discoveries 
                           if d['type'] in ['NUCLEAR', 'CRITICAL'])
        
        # Track history
        if 'discovery_history' not in self.state['convergence_metrics']:
            self.state['convergence_metrics']['discovery_history'] = []
        
        self.state['convergence_metrics']['discovery_history'].append(critical_count)
        history = self.state['convergence_metrics']['discovery_history']
        
        # Convergence: no critical discoveries
        if critical_count == 0:
            return True
        
        # Convergence: declining trend
        if len(history) >= 3:
            if history[-1] < history[-2] < history[-3]:
                if history[-1] <= 1:
                    return True
        
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # FINAL SYNTHESIS
    # ═══════════════════════════════════════════════════════════════
    
    def _execute_synthesis(self, all_results: Dict) -> Dict:
        """Build final strategic narrative"""
        
        # Export all knowledge
        knowledge = self.knowledge_graph.export_for_report()
        
        # Build synthesis prompt
        prompt = self.synthesis_prompts.narrative_construction_prompt(
            findings=knowledge.get('critical_findings', {}),
            contradictions=knowledge.get('key_contradictions', []),
            patterns=knowledge.get('strong_patterns', {}),
            timeline=knowledge.get('timeline', {}),
            entities=knowledge.get('entities', {})
        )
        
        # Generate narrative
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model='claude-sonnet-4-20250514',
            task_type='synthesis',
            phase='final_synthesis'
        )
        
        # Save narrative
        self.phase_executor.synthesise_narrative(response)
        
        results = {
            'narrative': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_phase_output('final_synthesis', results)
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _load_all_documents(self) -> List[Dict]:
        """Load all case documents"""
        loader = DocumentLoader(self.config)
        return loader.load_directory(self.config.case_documents_dir)
    
    def _discovery_importance(self, discovery_type: str) -> str:
        """Map discovery type to importance level"""
        importance_map = {
            'NUCLEAR': 'NUCLEAR',
            'CRITICAL': 'CRITICAL',
            'INVESTIGATE': 'HIGH',
            'SUSPICIOUS': 'HIGH',
            'PATTERN': 'MEDIUM',
            'CONTRADICTION': 'CRITICAL',
            'MISSING': 'MEDIUM'
        }
        return importance_map.get(discovery_type, 'MEDIUM')
    
    def _save_phase_output(self, phase: str, results: Dict):
        """Save phase output to disk"""
        
        phase_dir = self.config.analysis_dir / f"phase_{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Save synthesis
        synthesis_file = phase_dir / "synthesis.md"
        with open(synthesis_file, 'w', encoding='utf-8') as f:
            f.write(f"# Phase {phase}\n\n")
            f.write(f"Timestamp: {results.get('timestamp', datetime.now().isoformat())}\n\n")
            f.write(results.get('synthesis', results.get('narrative', 'No output')))
        
        # Save JSON
        results_file = phase_dir / "results.json"
        save_results = results.copy()
        if 'synthesis' in save_results:
            save_results['synthesis'] = save_results['synthesis'][:5000] + "..."
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(save_results, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Load previous state"""
        state_file = self.config.output_dir / "system_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
            except Exception as e:
                print(f"  ⚠ Could not load state: {e}")
    
    def _save_state(self):
        """Save current state"""
        state_file = self.config.output_dir / "system_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)