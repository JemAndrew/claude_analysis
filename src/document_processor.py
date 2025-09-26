#!/usr/bin/env python3
"""
Simplified Document Processor
Handles document loading and phase execution
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from api_client import ClaudeAPIClient
from prompts import Prompts
from knowledge_manager import KnowledgeManager


class DocumentProcessor:
    """Simple document processing and phase execution"""
    
    def __init__(self, api_client: ClaudeAPIClient):
        self.api_client = api_client
        self.prompts = Prompts()
        self.knowledge = KnowledgeManager()
        
        # Output directory
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def execute_phase(self, phase: str) -> Dict[str, Any]:
        """Execute a single phase"""
        
        phase_key = phase.replace("phase_", "")
        
        print(f"\n{'='*60}")
        print(f"PHASE {phase_key} EXECUTION")
        print(f"{'='*60}")
        
        # Load documents
        documents = self._load_phase_documents(phase_key)
        print(f"📁 Loaded {len(documents)} documents")
        
        # Build context from previous phases
        context = self._build_context(phase_key)
        
        # Execute analysis
        print(f"🔍 Analysing...")
        results = self.api_client.analyse_documents_batch(
            documents=documents,
            phase=f"phase_{phase_key}",
            context=context
        )
        
        # Save outputs
        phase_dir = self.output_dir / f"phase_{phase_key}"
        phase_dir.mkdir(exist_ok=True)
        
        # Save main analysis
        analysis_file = phase_dir / "analysis.md"
        with open(analysis_file, "w", encoding="utf-8") as f:
            f.write(f"# Phase {phase_key} Analysis\n\n")
            f.write(f"*Documents Analysed: {results.get('documents_analysed', 0)}*\n\n")
            f.write("---\n\n")
            f.write(results['synthesis'])
            
            if results.get('self_ask'):
                f.write(f"\n\n---\n\n")
                f.write(f"## Self-Investigation\n\n")
                f.write(results['self_ask'])
        
        print(f"✅ Analysis saved to {analysis_file}")
        
        # Store in knowledge manager for future phases
        self.knowledge.store_phase(phase_key, results)
        
        # Generate strategic report (except for Phase 0A which is pure knowledge building)
        if phase_key != "0A":
            self._generate_report(phase_key, results, phase_dir)
        
        # Print summary
        self._print_phase_summary(phase_key, results)
        
        return results
    
    def _load_phase_documents(self, phase: str) -> List[Dict]:
        """Load documents for phase"""
        
        documents = []
        
        # Determine path based on phase
        if phase == "0A":
            base_path = Path("legal_resources/processed/text")
            doc_prefix = "LEGAL"
        elif phase == "0B":
            base_path = Path("case_context/processed/text")
            doc_prefix = "CASE"
        else:
            base_path = Path("documents/processed/text")
            doc_prefix = "DOC"
        
        if not base_path.exists():
            print(f"⚠️ Directory {base_path} does not exist")
            return documents
        
        # Load all text files
        txt_files = sorted(base_path.glob("*.txt"))
        
        if not txt_files:
            print(f"⚠️ No .txt files found in {base_path}")
            return documents
        
        for i, txt_file in enumerate(txt_files, 1):
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                documents.append({
                    'id': f"{doc_prefix}_{i:04d}",
                    'filename': txt_file.name,
                    'content': content,
                    'type': phase
                })
            except Exception as e:
                print(f"⚠️ Error loading {txt_file.name}: {e}")
        
        return documents
    
    def _build_context(self, current_phase: str) -> Dict:
        """Build context from previous phases"""
        
        context = {}
        
        # Get all previous phase knowledge
        previous = self.knowledge.get_previous_phases(current_phase)
        
        if not previous:
            return context
        
        # Note that previous phases exist
        context['previous_phases'] = True
        
        # Special handling for different phases
        if current_phase == "0B":
            # Phase 0B gets the full Phase 0A legal arsenal
            if '0A' in previous:
                context['legal_arsenal'] = True
                # Include key tactical points from 0A
                synthesis_0a = previous['0A'].get('synthesis', '')
                if synthesis_0a:
                    # Extract first 2000 chars as context
                    context['legal_knowledge_summary'] = synthesis_0a[:2000]
        
        elif current_phase in ["1", "2", "3", "4", "5", "6", "7"]:
            # Later phases get cumulative knowledge
            context['legal_arsenal'] = '0A' in previous
            context['case_understanding'] = '0B' in previous
            
            # Get critical findings from immediate previous phase
            phase_order = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
            current_idx = phase_order.index(current_phase)
            
            if current_idx > 0:
                prev_phase = phase_order[current_idx - 1]
                if prev_phase in previous:
                    prev_synthesis = previous[prev_phase].get('synthesis', '')
                    
                    # Look for critical findings in previous phase
                    critical_findings = []
                    for line in prev_synthesis.split('\n'):
                        line_upper = line.upper()
                        if any(marker in line_upper for marker in ['CRITICAL:', 'NUCLEAR:', 'KEY:', 'IMPORTANT:']):
                            finding = line.strip()[:200]  # First 200 chars of finding
                            if finding:
                                critical_findings.append(finding)
                    
                    if critical_findings:
                        context['critical_findings'] = critical_findings[:5]  # Top 5 findings
        
        return context
    
    def _generate_report(self, phase: str, results: Dict, phase_dir: Path) -> None:
        """Generate strategic report from analysis"""
        
        print(f"📊 Generating strategic report...")
        
        # Build report prompt
        report_prompt = self.prompts.get_report_prompt(
            f"phase_{phase}",
            results
        )
        
        # Generate report using Claude
        report_response = self.api_client.analyse_documents_batch(
            documents=[],  # No documents needed for report generation
            phase=f"phase_{phase}_report",
            context={'prompt': report_prompt}
        )
        
        # Save report
        report_file = phase_dir / "report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"# Phase {phase} Strategic Report\n\n")
            f.write(f"*Generated from analysis of {results.get('documents_analysed', 0)} documents*\n\n")
            f.write("---\n\n")
            f.write(report_response.get('synthesis', 'No report generated'))
        
        print(f"✅ Report saved to {report_file}")
    
    def _print_phase_summary(self, phase: str, results: Dict) -> None:
        """Print summary of phase results"""
        
        print(f"\n📋 Phase {phase} Summary:")
        print(f"  • Documents analysed: {results.get('documents_analysed', 0)}")
        print(f"  • Analysis length: {len(results.get('synthesis', ''))} chars")
        print(f"  • Self-investigation: {'Yes' if results.get('self_ask') else 'No'}")
        
        # Count key findings
        synthesis = results.get('synthesis', '')
        contradictions = synthesis.upper().count('CONTRADICTION')
        admissions = synthesis.upper().count('ADMISSION')
        critical = synthesis.upper().count('CRITICAL')
        
        if contradictions or admissions or critical:
            print(f"  • Key findings:")
            if contradictions:
                print(f"    - Contradictions: {contradictions}")
            if admissions:
                print(f"    - Admissions: {admissions}")
            if critical:
                print(f"    - Critical points: {critical}")
    
    def generate_war_room_dashboard(self) -> None:
        """Generate final war room dashboard"""
        
        print("\n" + "="*60)
        print("GENERATING WAR ROOM DASHBOARD")
        print("="*60)
        
        # Gather all phase knowledge
        all_phases = {}
        for phase in ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]:
            knowledge = self.knowledge.get_phase(phase)
            if knowledge:
                all_phases[phase] = knowledge
        
        if not all_phases:
            print("⚠️ No phases completed yet")
            return
        
        print(f"📊 Synthesising {len(all_phases)} phases...")
        
        # Build dashboard prompt with key findings from each phase
        phase_summaries = []
        for phase, knowledge in all_phases.items():
            synthesis = knowledge.get('synthesis', '')[:500]  # First 500 chars
            phase_summaries.append(f"Phase {phase}: {synthesis}")
        
        dashboard_prompt = f"""Create an executive war room dashboard for Lismore v Process Holdings.

Phases completed: {', '.join(all_phases.keys())}

Key findings from each phase:
{'... '.join(phase_summaries[:3])}  # Include first 3 phases as context

Provide:
1. TOP 5 CASE-WINNING DISCOVERIES (with phase references)
2. IMMEDIATE ACTION ITEMS (next 48 hours)
3. SETTLEMENT LEVERAGE ASSESSMENT (score 1-10 with justification)
4. TRIAL READINESS SCORE (score 1-10 with gaps identified)
5. NUCLEAR OPTIONS AVAILABLE (case-ending moves)
6. RECOMMENDED STRATEGY (aggressive litigation vs settlement)

Be specific and reference findings from the phases."""
        
        # Generate dashboard
        dashboard_response = self.api_client.analyse_documents_batch(
            documents=[],
            phase="war_room_dashboard",
            context={'prompt': dashboard_prompt}
        )
        
        # Save dashboard
        dashboard_file = self.output_dir / "WAR_ROOM_DASHBOARD.md"
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write("# 🎯 WAR ROOM DASHBOARD\n")
            f.write("## Lismore Capital v Process Holdings\n\n")
            f.write(f"*Generated from {len(all_phases)} completed phases*\n\n")
            f.write("---\n\n")
            f.write(dashboard_response.get('synthesis', 'Dashboard generation failed'))
        
        print(f"✅ War Room Dashboard saved to {dashboard_file}")
        print(f"📁 All outputs in: {self.output_dir}")