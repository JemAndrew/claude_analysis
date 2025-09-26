#!/usr/bin/env python3
"""
Simplified Output Generator
Keeps the valuable parts, removes complexity
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class OutputGenerator:
    """Simplified report generator focused on results"""
    
    # Phase priorities - what to focus on
    PHASE_PRIORITIES = {
        "0A": ["legal_weapons", "procedural_advantages", "criminal_crossovers"],
        "0B": ["admissions", "contradictions", "missing_evidence"],
        "1": ["hot_documents", "missing_chains", "actor_network"],
        "2": ["timeline_impossibilities", "critical_periods", "deception_evolution"],
        "3": ["contradiction_matrix", "missing_documents", "communication_forensics"],
        "4": ["winning_narrative", "narrative_destruction"],
        "5": ["evidence_packages", "criminal_referrals", "admissions_bank"],
        "6": ["settlement_leverage", "summary_judgment", "cross_examination"],
        "7": ["pattern_recognition", "nuclear_options", "hidden_connections"]
    }
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Document registry for tracking
        self.document_registry = {}
        
        # Simple metrics
        self.reports_generated = 0
    
    def register_documents(self, documents: List[Dict]):
        """Register documents with IDs"""
        for idx, doc in enumerate(documents, 1):
            doc_id = f"DOC_{idx:04d}"
            self.document_registry[doc_id] = {
                'filename': doc.get('filename', f'document_{idx}'),
                'content': doc.get('content', ''),
                'type': doc.get('type', 'unknown')
            }
    
    def generate_reports(self, phase: str, analysis_results: Dict) -> Dict[str, Path]:
        """
        Generate reports from analysis results
        
        Args:
            phase: Phase identifier
            analysis_results: Results from document processor
            
        Returns:
            Dictionary of report names to file paths
        """
        phase_dir = self.output_dir / f"phase_{phase}"
        reports_dir = phase_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        saved_reports = {}
        
        # Parse the synthesis into individual reports
        synthesis = analysis_results.get('synthesis', '')
        reports = self._parse_reports(synthesis)
        
        # Save each report
        for report_name, content in reports.items():
            # Format with header/footer
            formatted = self._format_report(phase, report_name, content)
            
            # Save to file
            clean_name = re.sub(r'[^\w\s-]', '', report_name.lower())
            clean_name = re.sub(r'[-\s]+', '_', clean_name)
            
            filename = f"{clean_name}.md"
            filepath = reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted)
            
            saved_reports[report_name] = filepath
            self.reports_generated += 1
        
        # Generate phase summary
        summary_path = self._generate_phase_summary(phase, analysis_results, phase_dir)
        saved_reports['summary'] = summary_path
        
        print(f"  ✅ Generated {len(saved_reports)} reports for Phase {phase}")
        return saved_reports
    
    def _parse_reports(self, synthesis: str) -> Dict[str, str]:
        """Parse synthesis into individual reports"""
        reports = {}
        
        # Look for report sections
        # Pattern: ==== REPORT NAME ====
        pattern = r'={4,}\s*([A-Z][A-Z\s\&\-:]+)\s*={4,}'
        matches = list(re.finditer(pattern, synthesis, re.MULTILINE))
        
        if matches:
            for i, match in enumerate(matches):
                report_name = match.group(1).strip()
                
                # Get content until next report or end
                start = match.end()
                end = matches[i+1].start() if i+1 < len(matches) else len(synthesis)
                
                content = synthesis[start:end].strip()
                
                if content and len(content) > 100:
                    reports[report_name] = content
        else:
            # No clear sections - save as single report
            reports["Analysis"] = synthesis
        
        return reports
    
    def _format_report(self, phase: str, report_name: str, content: str) -> str:
        """Format report with metadata"""
        
        # Extract statistics
        doc_refs = len(re.findall(r'DOC_\d{4}', content))
        contradictions = content.count('CONTRADICTION:') + content.count('INCONSISTENCY:')
        admissions = content.count('ADMISSION:')
        
        formatted = f"""# Phase {phase}: {report_name}
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Statistics
- Document References: {doc_refs}
- Contradictions: {contradictions}  
- Admissions: {admissions}
- Priority: {', '.join(self.PHASE_PRIORITIES.get(phase, []))}

---

## Analysis

{content}

---
*End of Report*
"""
        return formatted
    
    def _generate_phase_summary(self, phase: str, results: Dict, phase_dir: Path) -> Path:
        """Generate phase summary"""
        
        summary = f"""# Phase {phase} Summary
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Overview
- Documents Analysed: {results.get('documents_analysed', 0)}
- Reports Generated: {self.reports_generated}
- Self-Ask Performed: {'Yes' if results.get('self_ask') else 'No'}

## Key Focus Areas
{self._format_priorities(phase)}

## Synthesis Extract
{results.get('synthesis', 'No synthesis available')[:1000]}...

## Self-Ask Results
{results.get('self_ask', 'No self-questioning performed')[:500]}

## Next Steps
- Review generated reports
- Identify follow-up actions
- Prepare for next phase
"""
        
        summary_path = phase_dir / "summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary_path
    
    def _format_priorities(self, phase: str) -> str:
        """Format phase priorities as markdown list"""
        priorities = self.PHASE_PRIORITIES.get(phase, [])
        if not priorities:
            return "- Standard analysis"
        
        return '\n'.join([f"- {p.replace('_', ' ').title()}" for p in priorities])
    
    def generate_war_room_dashboard(self, all_phases: Dict[str, Dict]) -> Path:
        """Generate executive war room dashboard"""
        
        # Calculate metrics
        total_docs = sum(p.get('documents_analysed', 0) for p in all_phases.values())
        total_contradictions = sum(
            p.get('synthesis', '').count('CONTRADICTION:') 
            for p in all_phases.values()
        )
        total_admissions = sum(
            p.get('synthesis', '').count('ADMISSION:') 
            for p in all_phases.values()
        )
        
        # Extract top findings
        top_findings = self._extract_top_findings(all_phases)
        
        dashboard = f"""# WAR ROOM DASHBOARD
## Lismore v Process Holdings
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

---

## 🎯 KEY METRICS

| Metric | Value |
|--------|-------|
| Documents Analysed | {total_docs} |
| Contradictions Found | {total_contradictions} |
| Admissions Identified | {total_admissions} |
| Phases Completed | {len(all_phases)} |
| Reports Generated | {self.reports_generated} |

## 📊 TOP FINDINGS

{self._format_findings_list(top_findings)}

## ⚡ IMMEDIATE ACTIONS

- [ ] Deploy evidence packages for summary judgment
- [ ] Issue adverse inference demands
- [ ] Prepare criminal referral threats
- [ ] Schedule key witness depositions
- [ ] Draft settlement demand

## 📈 STRATEGIC ASSESSMENT

| Area | Score | Status |
|------|-------|--------|
| Settlement Leverage | {min(10, total_contradictions // 5)}/10 | {'HIGH' if total_contradictions > 20 else 'MEDIUM'} |
| Trial Readiness | {min(10, total_admissions // 3)}/10 | {'READY' if total_admissions > 15 else 'PREPARING'} |
| Summary Judgment | {min(10, total_admissions // 2)}/10 | {'VIABLE' if total_admissions > 10 else 'BUILDING'} |

## 📁 PHASE STATUS

{self._format_phase_status(all_phases)}

---

**RECOMMENDATION**: {self._get_recommendation(total_contradictions, total_admissions)}

---
*War Room Dashboard - Litigation Intelligence System*
"""
        
        dashboard_path = self.output_dir / f"WAR_ROOM_DASHBOARD.md"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        print(f"\n✅ War Room Dashboard generated: {dashboard_path}")
        return dashboard_path
    
    def _extract_top_findings(self, all_phases: Dict) -> List[str]:
        """Extract top findings from all phases"""
        findings = []
        
        for phase, results in all_phases.items():
            synthesis = results.get('synthesis', '')
            
            # Look for marked findings
            if 'NUCLEAR:' in synthesis:
                findings.append(f"[NUCLEAR - Phase {phase}] Evidence that ends the case")
            if 'CRITICAL:' in synthesis:
                findings.append(f"[CRITICAL - Phase {phase}] Major contradiction found")
            if 'ADMISSION:' in synthesis:
                findings.append(f"[ADMISSION - Phase {phase}] Binding admission extracted")
        
        return findings[:5]  # Top 5
    
    def _format_findings_list(self, findings: List[str]) -> str:
        """Format findings as numbered list"""
        if not findings:
            return "1. Analysis in progress..."
        
        return '\n'.join([f"{i+1}. {f}" for i, f in enumerate(findings)])
    
    def _format_phase_status(self, all_phases: Dict) -> str:
        """Format phase completion status"""
        phases = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        status_lines = []
        for phase in phases:
            if phase in all_phases:
                docs = all_phases[phase].get('documents_analysed', 0)
                status_lines.append(f"- Phase {phase}: ✅ Complete ({docs} documents)")
            else:
                status_lines.append(f"- Phase {phase}: ⏳ Pending")
        
        return '\n'.join(status_lines)
    
    def _get_recommendation(self, contradictions: int, admissions: int) -> str:
        """Get strategic recommendation based on findings"""
        
        if contradictions > 30 and admissions > 20:
            return "IMMEDIATE SUMMARY JUDGMENT - Overwhelming evidence"
        elif contradictions > 20 or admissions > 15:
            return "AGGRESSIVE SETTLEMENT - Strong position"
        elif contradictions > 10 or admissions > 8:
            return "CONTINUE BUILDING - Good progress"
        else:
            return "DEEPER ANALYSIS NEEDED - Gather more evidence"