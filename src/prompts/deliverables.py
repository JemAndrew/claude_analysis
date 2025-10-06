#!/usr/bin/env python3
"""
ENHANCED Deliverables Prompts - Replace src/prompts/deliverables.py
Uses XML tags for robust parsing instead of fragile regex
British English throughout - Lismore v Process Holdings
"""

import json
from typing import Dict, List


class DeliverablesPrompts:
    """Generate prompts for Pass 4 tribunal deliverables with XML structure"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_all_deliverables(self, 
                                 intelligence: Dict,
                                 claims: Dict,
                                 strategy: Dict) -> str:
        """
        Generate prompt for all 6 tribunal deliverables
        Uses XML tags for reliable parsing
        """
        
        # Format intelligence summary
        intel_summary = self._format_intelligence_summary(intelligence)
        claims_summary = self._format_claims_summary(claims)
        strategy_summary = self._format_strategy_summary(strategy)
        
        prompt = f"""You are senior litigation counsel for Lismore in their arbitration against Process Holdings.

You have completed comprehensive analysis of 18,000+ disclosure documents and identified strong grounds for claims.

Your task: Generate 6 tribunal-ready documents that will be used at hearing.

<intelligence_context>
{intel_summary}
</intelligence_context>

<claims_constructed>
{claims_summary}
</claims_constructed>

<strategic_recommendations>
{strategy_summary}
</strategic_recommendations>

<critical_instructions>
EXTREMELY IMPORTANT: You MUST wrap each deliverable in XML tags for parsing.

Use these EXACT tags:
<scott_schedule>...</scott_schedule>
<witness_outlines>...</witness_outlines>
<skeleton_argument>...</skeleton_argument>
<disclosure_requests>...</disclosure_requests>
<opening_submissions>...</opening_submissions>
<expert_instructions>...</expert_instructions>

DO NOT use any other tag names. DO NOT nest tags incorrectly.
Each deliverable must be complete and tribunal-ready.
</critical_instructions>

<quality_standards>
1. EVIDENCE-BASED
   ✓ Cite specific document IDs: [DOC_045] or (per DOC_045)
   ✓ Cite at least 2-3 documents per major assertion
   ✓ Reference evidence from the intelligence context

2. ADVERSARIAL BUT PROFESSIONAL
   ✓ Frame all facts favourably to Lismore
   ✓ Exploit Process Holdings' weaknesses aggressively
   ✓ Use contradictions to undermine credibility
   ✓ Maintain professional tribunal tone

3. STRATEGIC FOCUS
   ✓ Prioritise strongest claims (strength > 0.7)
   ✓ Minimise weakest claims (strength < 0.5)
   ✓ Use novel arguments for tactical advantage
   ✓ Exploit contradictions for cross-examination

4. PRECISION AND SPECIFICITY
   ✓ Exact dates (not "around" or "approximately")
   ✓ Specific amounts (not "substantial")
   ✓ Named individuals (not "management")
   ✓ Precise clause citations (not "various sections")
   ✓ Clear document references

5. TRIBUNAL-READY QUALITY
   ✓ British English throughout
   ✓ Professional legal language
   ✓ Proper formatting and structure
   ✓ Ready to submit without editing

6. WINNING MENTALITY
   ✓ Every deliverable serves goal of winning
   ✓ Aggressive exploitation of advantages
   ✓ Undermining of opponent credibility
   ✓ Clear path to victory
</quality_standards>

---

Generate all 6 deliverables now. Wrap each in the correct XML tags.

<scott_schedule>
# DELIVERABLE 1: SCOTT SCHEDULE / CHRONOLOGY

Create a detailed Scott Schedule showing:
- Key events in chronological order
- Lismore's position on each event
- Process Holdings' likely position
- Evidence references for each event
- Assessment of strength (Strong/Medium/Weak)

Format as a clear table or structured list with dates, events, positions, evidence.

Focus on events that support Lismore's strongest claims.
</scott_schedule>

<witness_outlines>
# DELIVERABLE 2: WITNESS STATEMENT OUTLINES

Identify key witnesses for Lismore and outline what each should address:

For each witness:
- Name and role
- Key topics they should cover
- Specific documents they should reference
- Timeline of events from their perspective
- Potential cross-examination vulnerabilities to prepare for

Include both fact witnesses and expert witnesses if needed.
</witness_outlines>

<skeleton_argument>
# DELIVERABLE 3: SKELETON ARGUMENT

Draft a comprehensive skeleton argument for Lismore containing:

1. INTRODUCTION
   - Parties and background
   - Summary of dispute

2. FACTUAL BACKGROUND
   - Key events (with dates and evidence)
   - Parties' conduct

3. LEGAL FRAMEWORK
   - Applicable law and principles
   - Relevant clauses from contracts

4. LISMORE'S CASE
   - Each head of claim with:
     * Legal basis
     * Factual foundation (with evidence)
     * Quantum of loss
   - Strongest claims first

5. PROCESS HOLDINGS' WEAKNESSES
   - Contradictions in their position
   - Missing or weak evidence
   - Implausible explanations

6. CONCLUSION
   - Relief sought
   - Summary of why Lismore should succeed

Cite evidence throughout: [DOC_ID] format.
</skeleton_argument>

<disclosure_requests>
# DELIVERABLE 4: DISCLOSURE REQUESTS

Identify specific categories of documents that Process Holdings must disclose:

For each category:
- Precise description of documents sought
- Why documents are relevant and necessary
- Specific time period
- Likely custodians
- How documents will support Lismore's case or undermine PH's case

Focus on gaps in current disclosure that Process Holdings is hiding.
</disclosure_requests>

<opening_submissions>
# DELIVERABLE 5: OPENING SUBMISSIONS OUTLINE

Draft outline for Lismore's opening submissions at hearing:

1. ROADMAP
   - What tribunal will hear
   - Key themes

2. UNCONTROVERSIAL FACTS
   - Facts PH cannot dispute
   - Establish favourable narrative early

3. KEY DISPUTED FACTS
   - Lismore's version (with evidence)
   - Why PH's version is implausible

4. LISMORE'S STRONGEST POINTS
   - 3-5 most compelling arguments
   - Evidence for each
   - Why each point is fatal to PH's case

5. PROCESS HOLDINGS' FATAL FLAWS
   - Contradictions
   - Implausibilities
   - Missing evidence

6. WHAT LISMORE WILL PROVE
   - Preview of evidence to come
   - Confidence in outcome

Make it persuasive and compelling. Set favourable tone from start.
</opening_submissions>

<expert_instructions>
# DELIVERABLE 6: EXPERT INSTRUCTION BRIEFS

Draft instructions for expert witnesses Lismore may need:

For each expert discipline (financial, technical, industry, etc.):
- Background and context
- Specific questions expert should address
- Documents expert should review
- Assumptions expert should make
- Format of report required
- Timeline for delivery

Include:
- Financial/accounting expert (if quantum disputed)
- Industry expert (if standards of practice disputed)
- Technical expert (if technical issues in dispute)

Focus experts on issues that strengthen Lismore's case or undermine PH's case.
</expert_instructions>

---

CRITICAL REMINDER: Each deliverable MUST be wrapped in its XML tags as shown above.
Generate complete, tribunal-ready documents now.
Use ALL the intelligence, claims, and strategy information provided.
This is Lismore's chance to WIN - make these documents compelling and comprehensive.
"""
        
        return prompt
    
    def _format_intelligence_summary(self, intelligence: Dict) -> str:
        """Format intelligence into concise summary"""
        summary = []
        
        # Patterns (breaches)
        patterns = intelligence.get('patterns', [])
        if patterns:
            summary.append(f"BREACHES IDENTIFIED: {len(patterns)}")
            summary.append("\nTop Breaches:")
            for i, pattern in enumerate(patterns[:10], 1):
                desc = pattern.get('description', '')[:150]
                conf = pattern.get('confidence', 0)
                summary.append(f"  {i}. {desc} (Confidence: {conf:.2f})")
        
        # Contradictions
        contradictions = intelligence.get('contradictions', [])
        if contradictions:
            summary.append(f"\n\nCONTRADICTIONS IDENTIFIED: {len(contradictions)}")
            summary.append("\nKey Contradictions:")
            for i, contra in enumerate(contradictions[:10], 1):
                stmt_a = contra.get('statement_a', '')[:100]
                stmt_b = contra.get('statement_b', '')[:100]
                severity = contra.get('severity', 0)
                summary.append(f"  {i}. Severity {severity}/10")
                summary.append(f"     Statement A: {stmt_a}")
                summary.append(f"     Statement B: {stmt_b}")
        
        # Timeline events
        timeline = intelligence.get('timeline_events', [])
        if timeline:
            summary.append(f"\n\nTIMELINE EVENTS: {len(timeline)}")
            summary.append("\nKey Events:")
            for i, event in enumerate(timeline[:15], 1):
                date = event.get('date', 'Unknown')
                desc = event.get('description', '')[:120]
                summary.append(f"  {i}. {date}: {desc}")
        
        # Investigations
        investigations = intelligence.get('investigations', [])
        if investigations:
            summary.append(f"\n\nINVESTIGATIONS COMPLETED: {len(investigations)}")
            summary.append("\nKey Findings:")
            for i, inv in enumerate(investigations[:5], 1):
                topic = inv.get('topic', '')
                conclusion = inv.get('conclusion', '')[:150]
                summary.append(f"  {i}. {topic}")
                summary.append(f"     Finding: {conclusion}")
        
        # Statistics
        stats = intelligence.get('statistics', {})
        summary.append(f"\n\nOVERALL STATISTICS:")
        summary.append(f"  Total Breaches: {stats.get('total_patterns', 0)}")
        summary.append(f"  Total Contradictions: {stats.get('total_contradictions', 0)}")
        summary.append(f"  Total Timeline Events: {stats.get('total_timeline_events', 0)}")
        summary.append(f"  Total Investigations: {stats.get('total_investigations', 0)}")
        
        return "\n".join(summary)
    
    def _format_claims_summary(self, claims: Dict) -> str:
        """Format constructed claims"""
        summary = []
        
        summary.append(f"CLAIMS CONSTRUCTED: {len(claims)}")
        
        for claim_type, claim in claims.items():
            summary.append(f"\n{claim_type.upper().replace('_', ' ')}")
            summary.append(f"  Strength: {claim.get('strength', 0):.2f}")
            summary.append(f"  Evidence Count: {claim.get('evidence_count', 0)}")
            
            elements = claim.get('elements', {})
            if elements:
                summary.append("  Elements Proven:")
                for element, proven in elements.items():
                    status = "✓" if proven else "✗"
                    summary.append(f"    {status} {element.replace('_', ' ').title()}")
        
        return "\n".join(summary)
    
    def _format_strategy_summary(self, strategy: Dict) -> str:
        """Format strategic recommendations"""
        summary = []
        
        # Strongest claims
        strongest = strategy.get('strongest_claims', [])
        if strongest:
            summary.append("STRONGEST CLAIMS (Lead with these):")
            for claim in strongest:
                summary.append(f"  - {claim.get('claim', '').replace('_', ' ').title()} (Strength: {claim.get('strength', 0):.2f})")
        
        # Weakest areas
        weakest = strategy.get('weakest_areas', [])
        if weakest:
            summary.append("\nWEAKEST AREAS (Minimise or strengthen):")
            for area in weakest:
                summary.append(f"  - {area.get('claim', '').replace('_', ' ').title()} (Strength: {area.get('strength', 0):.2f})")
        
        # Settlement positioning
        settlement = strategy.get('settlement_positioning', '')
        if settlement:
            summary.append(f"\nSETTLEMENT POSITIONING:")
            summary.append(f"  {settlement}")
        
        # Trial strategy
        trial = strategy.get('trial_strategy', '')
        if trial:
            summary.append(f"\nTRIAL STRATEGY:")
            summary.append(f"  {trial}")
        
        return "\n".join(summary)