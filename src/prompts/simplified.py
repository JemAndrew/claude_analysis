#!/usr/bin/env python3
"""
Simplified Prompts for Autonomous Claude Investigation
Only 3 prompt types: Legal Knowledge, Case Understanding, Free Investigation
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Any
from datetime import datetime


class SimplifiedPrompts:
    """Prompts for autonomous Claude investigation"""
    
    def __init__(self, config):
        self.config = config
    
    def legal_knowledge_prompt(self, 
                              legal_documents: str,
                              doc_count: int) -> str:
        """
        Phase 0: Legal knowledge absorption
        Claude learns ONLY the legal framework, no case analysis yet
        """
        
        prompt = f"""<legal_knowledge_mission>
You are learning the legal framework for Lismore Capital v Process Holdings.

Your ONLY job in this phase: Master the legal principles, doctrines, and precedents.
Do NOT analyse the case yet - just learn the law.

FOCUS ON:
- Applicable legal doctrines
- Burden of proof requirements
- Key precedents and their principles
- Elements of each cause of action
- Potential defences and how to defeat them
- Damages calculation frameworks
- Procedural considerations for arbitration
</legal_knowledge_mission>

<legal_documents count="{doc_count}">
{legal_documents}
</legal_documents>

<instruction>
Read these legal materials thoroughly.
Build a comprehensive understanding of the legal framework.
Identify which principles will be most useful for destroying Process Holdings' case.

Structure your response as a legal knowledge synthesis:
1. Key legal principles applicable to this case
2. Burden of proof requirements
3. Elements we must establish
4. Their potential defences and how to defeat them
5. Damages calculation approach

This becomes your foundation for analysing the case documents.
</instruction>"""
        
        return prompt
    
    def case_understanding_prompt(self,
                                 case_documents: str,
                                 legal_framework: str,
                                 doc_count: int) -> str:
        """
        Phase 1: Complete case understanding
        Claude reads ALL case documents for the first time
        Builds complete picture and marks everything interesting
        """
        
        prompt = f"""<legal_framework>
{legal_framework[:10000]}
</legal_framework>

<case_understanding_mission>
You are reading {doc_count} case documents for the FIRST time.

Your goal: Build COMPLETE understanding of this case.

WHAT TO UNDERSTAND:
- What happened? (full chronology)
- Who are the players? (all entities and their roles)
- What's the timeline? (key events and dates)
- Where are they vulnerable? (weaknesses in their case)
- What evidence exists? (documents, testimony, facts)
- What's missing? (gaps, inconsistencies, contradictions)
- What patterns emerge? (suspicious behaviour, systematic issues)

MARK EVERYTHING INTERESTING:
- [NUCLEAR] - Case-ending discoveries (e.g., smoking gun evidence, fatal contradictions)
- [CRITICAL] - Major strategic advantages (e.g., strong evidence of liability, damages proof)
- [INVESTIGATE] - Threads needing deep investigation (e.g., suspicious transactions, timeline gaps)
- [SUSPICIOUS] - Anomalies worth exploring (e.g., unusual patterns, odd behaviours)
- [PATTERN] - Recurring behaviours or themes (e.g., systematic concealment, consistent lies)
</case_understanding_mission>

<all_case_documents count="{doc_count}">
{case_documents}
</all_case_documents>

<instruction>
Read EVERYTHING thoroughly.
Think freely about what matters.
Mark ANYTHING worth investigating deeper.

Structure your understanding:
1. **CASE OVERVIEW**: What happened and why we'll win
2. **KEY PLAYERS**: Who they are and their roles
3. **TIMELINE**: Critical events in chronological order
4. **THEIR VULNERABILITIES**: Where their case is weak
5. **OUR STRENGTHS**: Evidence and arguments in our favour
6. **GAPS & CONTRADICTIONS**: Inconsistencies to exploit
7. **INVESTIGATION PRIORITIES**: What needs deeper analysis

This is your foundation for destroying Process Holdings.
Build the complete picture.
</instruction>"""
        
        return prompt
    
    def free_investigation_prompt(self,
                                 iteration: int,
                                 previous_findings: Dict,
                                 context: Dict) -> str:
        """
        Phase 2+: Free investigation iterations
        Claude has COMPLETE autonomy to investigate anything
        No predetermined focus or categories
        """
        
        # Format previous findings
        critical_findings = previous_findings.get('critical_discoveries', [])
        patterns = previous_findings.get('patterns', [])
        contradictions = previous_findings.get('contradictions', [])
        investigations = previous_findings.get('investigation_results', [])
        
        findings_text = self._format_findings_for_prompt(
            critical_findings, patterns, contradictions, investigations
        )
        
        prompt = f"""<iteration>{iteration}</iteration>

<previous_findings>
{findings_text}
</previous_findings>

<free_investigation_mission>
This is investigation iteration {iteration}.

You have COMPLETE FREEDOM. Investigate ANYTHING that seems important.

NO RESTRICTIONS:
- No predetermined "financial phase" or "timeline phase"
- No required categories or structure
- No limits on what you can explore
- Just find what wins this case for Lismore

FOLLOW ANY THREAD:
- Financial anomalies? Investigate deeply
- Timeline gaps? Explore thoroughly
- Suspicious entities? Map their connections
- Contradictions? Expose them fully
- New patterns? Validate and expand
- Unusual behaviour? Understand why
- Missing evidence? Identify what's hidden

USE DISCOVERY MARKERS:
- [NUCLEAR] - Case-ending discoveries
- [CRITICAL] - Major advantages
- [INVESTIGATE] - Needs deeper investigation
- [PATTERN] - Emerging patterns
- [CONTRADICTION] - Logical conflicts
- [SUSPICIOUS] - Anomalies found
</free_investigation_mission>

<investigation_approach>
For this iteration:

1. **REVIEW** your previous findings
2. **IDENTIFY** the most promising threads to follow
3. **INVESTIGATE** deeply and thoroughly
4. **QUESTION** everything you find
5. **CONNECT** dots across documents and findings
6. **MARK** significant discoveries

Be thorough. Be creative. Be relentless.
Find what destroys Process Holdings.
</investigation_approach>

<instruction>
Investigate freely based on your previous findings.
Follow whatever threads seem most important.
Question everything.
Make connections.
Find vulnerabilities.

Stop when you've found nothing significantly new.
Report your findings with appropriate markers.
</instruction>"""
        
        return prompt
    
    def _format_findings_for_prompt(self,
                                   critical_findings: List[Dict],
                                   patterns: List[Dict],
                                   contradictions: List[Dict],
                                   investigations: List[Dict]) -> str:
        """Format previous findings for investigation prompt"""
        
        sections = []
        
        # Critical discoveries
        if critical_findings:
            sections.append(f"CRITICAL DISCOVERIES: {len(critical_findings)} found")
            for i, finding in enumerate(critical_findings[:10], 1):
                sections.append(f"{i}. {finding.get('summary', finding.get('content', 'Unknown'))[:200]}")
        else:
            sections.append("CRITICAL DISCOVERIES: None yet")
        
        sections.append("")
        
        # Patterns
        if patterns:
            sections.append(f"PATTERNS IDENTIFIED: {len(patterns)} found")
            for i, pattern in enumerate(patterns[:5], 1):
                conf = pattern.get('confidence', 0)
                sections.append(f"{i}. {pattern.get('description', 'Unknown')} (confidence: {conf:.2f})")
        else:
            sections.append("PATTERNS IDENTIFIED: None yet")
        
        sections.append("")
        
        # Contradictions
        if contradictions:
            sections.append(f"CONTRADICTIONS: {len(contradictions)} found")
            for i, contra in enumerate(contradictions[:5], 1):
                sev = contra.get('severity', 0)
                sections.append(f"{i}. {contra.get('description', 'Unknown')} (severity: {sev}/10)")
        else:
            sections.append("CONTRADICTIONS: None yet")
        
        sections.append("")
        
        # Previous investigations
        if investigations:
            sections.append(f"PREVIOUS INVESTIGATIONS: {len(investigations)} completed")
            for i, inv in enumerate(investigations[:3], 1):
                sections.append(f"{i}. {inv.get('type', 'Unknown')}: {inv.get('summary', 'No summary')[:150]}")
        else:
            sections.append("PREVIOUS INVESTIGATIONS: None yet")
        
        return '\n'.join(sections)
    
    def final_synthesis_prompt(self,
                             all_findings: Dict,
                             investigation_count: int) -> str:
        """
        Final synthesis: Pull everything together into strategic report
        Used when investigations have converged
        """
        
        prompt = f"""<final_synthesis_mission>
You have completed {investigation_count} investigation iterations.

Now synthesise EVERYTHING into a devastating strategic report for Lismore Capital.
</final_synthesis_mission>

<all_findings>
{self._format_all_findings(all_findings)}
</all_findings>

<synthesis_requirements>
Create a comprehensive strategic report with:

1. **EXECUTIVE SUMMARY**
   - Bottom line: Will we win?
   - Key strengths and vulnerabilities
   - Recommended approach

2. **CASE-WINNING ARGUMENTS**
   - Strongest arguments (rank by strength)
   - Supporting evidence for each
   - How to present them

3. **CRITICAL EVIDENCE**
   - Documents that prove liability
   - Testimony needed
   - Expert opinions required

4. **THEIR VULNERABILITIES**
   - Fatal weaknesses in their case
   - Contradictions they can't explain
   - Evidence they're hiding

5. **OUR VULNERABILITIES**
   - Weak points in our case
   - How to mitigate them
   - Defensive strategies

6. **DAMAGE CALCULATIONS**
   - Quantified losses
   - Supporting documentation
   - Range of likely awards

7. **STRATEGIC RECOMMENDATIONS**
   - Immediate actions needed
   - Evidence to secure
   - Witnesses to interview
   - Settlement leverage points

8. **NUCLEAR OPTIONS**
   - Case-ending discoveries
   - Pressure points
   - Timing for maximum impact
</synthesis_requirements>

<instruction>
Synthesise everything into a clear, actionable strategic report.
Be brutal. Be precise. Be comprehensive.

This report should give Lismore everything needed to destroy Process Holdings.
</instruction>"""
        
        return prompt
    
    def _format_all_findings(self, all_findings: Dict) -> str:
        """Format all findings for final synthesis"""
        
        sections = []
        
        for category, findings in all_findings.items():
            if findings:
                sections.append(f"\n{category.upper()}: {len(findings)} items")
                for finding in findings[:20]:  # Limit to avoid token overflow
                    sections.append(f"- {str(finding)[:200]}")
        
        return '\n'.join(sections)