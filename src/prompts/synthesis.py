#!/usr/bin/env python3
"""
Synthesis Prompts for Final Strategic Reports
COMPLETE REPLACEMENT for src/prompts/synthesis.py
"""

from typing import Dict, List
import json


HALLUCINATION_PREVENTION = """
<critical_accuracy_requirements>
TRIBUNAL-READY REPORTS REQUIREMENTS:
1. EVERY claim must cite source: [DOC_ID: Location]
2. No unsupported assertions
3. No speculation without clear [INFERENCE] label
4. Quotes must be EXACT and verifiable
5. Legal arguments must cite authority

This report goes to tribunal. False claims destroy credibility.
</critical_accuracy_requirements>
"""


class SynthesisPrompts:
    """Generate synthesis prompts for final strategic reports"""
    
    def __init__(self, config):
        self.config = config
    
    def narrative_construction_prompt(self,
                                     findings: Dict,
                                     contradictions: List[Dict],
                                     patterns: Dict,
                                     timeline: Dict,
                                     entities: Dict) -> str:
        """
        Build compelling narrative from all analysis
        """
        
        return f"""{HALLUCINATION_PREVENTION}

<narrative_mission>
Construct tribunal-ready narrative that wins the arbitration for Lismore.

Transform analysis into compelling story:
- Clear, logical structure
- Devastating for PH
- Supported by evidence
- Legally sound
- Strategically optimal
</narrative_mission>

<available_intelligence>
FINDINGS: {json.dumps(findings, indent=2)[:10000]}
CONTRADICTIONS: {json.dumps(contradictions, indent=2)[:5000]}
PATTERNS: {json.dumps(patterns, indent=2)[:5000]}
TIMELINE: {json.dumps(timeline, indent=2)[:3000]}
ENTITIES: {json.dumps(entities, indent=2)[:3000]}
</available_intelligence>

<narrative_structure>

PART 1: THE FOUNDATION (Opening Statement Quality)
- Lismore's reasonable expectations
- The agreements and their terms
- What PH promised
- Why Lismore relied on PH

[2-3 paragraphs, cite key documents]

PART 2: THE BREACHES (Build Liability)
- Chronological account of PH's failures
- Each breach identified and proven
- Legal basis for each claim
- Evidence for each breach

[Detailed section with comprehensive citations]

PART 3: THE PATTERN (Show Systematic Misconduct)
- Not isolated failures but systematic
- Coordinated bad faith
- Evidence of deliberate strategy
- Pattern proves intent

[Show evolution with dated evidence]

PART 4: THE DAMAGES (Quantify Loss)
- Direct losses from breaches
- Consequential damages
- Lost opportunities
- Continuing losses
- Future losses

[Detailed calculations with evidence]

PART 5: THE SMOKING GUNS (Most Damaging Evidence)
- Top 5-10 most damaging findings
- Contradictions PH cannot explain
- Documents proving knowledge/intent
- Admissions in their own words

[Devastating presentation]

PART 6: PH'S DEFENCES (Preempt and Destroy)
- What PH will argue
- Why each defence fails
- Evidence contradicting their story
- Legal flaws in their arguments

[Thorough rebuttal]

PART 7: THE REMEDY (What Tribunal Should Award)
- Damages quantum
- Interest
- Costs
- Other relief

[Clear, justified demands]
</narrative_structure>

<quality_requirements>
1. Every factual claim cited: [DOC:LOC]
2. Every legal argument has authority
3. Chronology is clear and precise
4. Damages calculations shown
5. No speculation or guesswork
6. Anticipates PH's defences
7. Builds to inevitable conclusion: Lismore wins

TONE:
- Professional but forceful
- Confident but not arrogant
- Factual but compelling
- Detailed but readable
</quality_requirements>

<output_format>
# LISMORE CAPITAL V PROCESS HOLDINGS
## Strategic Case Analysis

### EXECUTIVE SUMMARY
[3-4 paragraphs: Core claims, key evidence, damages, why Lismore wins]

### PART 1: FOUNDATION
[As structured above]

### PART 2: LIABILITY
[Detailed breach-by-breach analysis]

### PART 3: SYSTEMATIC MISCONDUCT
[Pattern evidence]

### PART 4: DAMAGES
[Comprehensive damages analysis]

### PART 5: SMOKING GUN EVIDENCE
[Most damaging findings]

### PART 6: DEFENCE REBUTTAL
[Preemptive destruction of PH's arguments]

### PART 7: RELIEF SOUGHT
[What tribunal should award]

### CONCLUSION
[Why Lismore must prevail - 2-3 paragraphs]

### APPENDICES
A. Key Document Citations
B. Legal Authority
C. Damages Calculations
D. Chronology
E. Entity Map
</output_format>

Build the narrative that wins. Make it bulletproof. Cite everything.
"""
    
    def strategic_synthesis_prompt(self,
                                  phase_analyses: Dict[str, str],
                                  investigations: List[Dict],
                                  knowledge_graph_export: Dict) -> str:
        """
        Synthesise all intelligence into strategic recommendations
        """
        
        return f"""{HALLUCINATION_PREVENTION}

<synthesis_mission>
Transform all analysis into actionable litigation strategy for Lismore.

Deliverables:
1. Top strategic advantages
2. Priority actions
3. Evidence strategy
4. Witness strategy
5. Expert strategy
6. Settlement position
7. Trial strategy
8. Risk assessment
</synthesis_mission>

<intelligence_available>
PHASE ANALYSES: {json.dumps(phase_analyses, indent=2)[:5000]}
INVESTIGATIONS: {json.dumps(investigations, indent=2)[:5000]}
KNOWLEDGE GRAPH: {json.dumps(knowledge_graph_export, indent=2)[:10000]}
</intelligence_available>

<strategic_framework>

1. STRATEGIC ADVANTAGES (Top 10)
   Lismore's strongest positions:
   - [Advantage 1] [Evidence] [Legal basis] [How to exploit]
   - [Advantage 2] [Evidence] [Legal basis] [How to exploit]
   ...
   
   Priority: Which to lead with and why

2. CRITICAL WEAKNESSES IN PH'S CASE (Top 10)
   Attack these aggressively:
   - [Weakness 1] [How to expose] [Evidence to use]
   - [Weakness 2] [How to expose] [Evidence to use]
   ...
   
   Strategy: Order and method of attack

3. EVIDENCE STRATEGY
   Must-have documents:
   - [Document type] [Why critical] [How to obtain]
   
   Exhibit strategy:
   - Key exhibits for opening
   - Documentary evidence packages
   - Demonstrative exhibits
   
   Authentication issues:
   - [Document] [Authentication method]

4. WITNESS STRATEGY
   Lismore's witnesses:
   - [Witness] [Topics] [Preparation needs] [Strengths/Weaknesses]
   
   PH's witnesses to destroy:
   - [Witness] [Credibility issues] [Cross-examination strategy]
   
   Third-party witnesses:
   - [Witness] [What they prove] [How to secure]

5. EXPERT STRATEGY
   Experts needed:
   - [Expert type] [Issues to address] [Qualifications needed]
   
   Daubert/admissibility strategy:
   - How to get our experts in
   - How to exclude their experts

6. LEGAL ARGUMENT STRATEGY
   Primary theories:
   - [Theory 1] [Strength 1-10] [Legal authority]
   - [Theory 2] [Strength 1-10] [Legal authority]
   
   Alternative theories:
   - [Theory 3] [When to use] [Legal authority]
   
   Novel arguments:
   - [Argument] [Why it works] [Risk assessment]

7. DAMAGES STRATEGY
   Primary calculation:
   - [Method] [Amount] [Evidence] [Strength]
   
   Alternative calculations:
   - [Method] [Amount] [When to use]
   
   Expert evidence needed:
   - [Expert type] [Calculation to support]

8. SETTLEMENT POSITION
   Lismore's BATNA:
   - [Best outcome at trial] [Probability] [Amount]
   
   Settlement range:
   - Minimum acceptable: [Amount] [Justification]
   - Target: [Amount] [Justification]
   - Opening demand: [Amount] [Strategy]
   
   Leverage points:
   - [Finding] [How it pressures settlement]
   
   Timing: When to settle vs proceed

9. TRIAL STRATEGY
   Opening statement structure:
   - [Theme] [Key 3-5 points] [Visual aids]
   
   Case presentation order:
   - [Witness/Evidence order] [Rationale]
   
   Closing argument structure:
   - [Theme] [Key points] [Call to action]
   
   Demonstrative evidence:
   - [Timeline] [Entity charts] [Damages graphics]

10. RISK ASSESSMENT
    Risks to Lismore:
    - [Risk] [Likelihood] [Impact] [Mitigation]
    
    Contingency plans:
    - [If X happens] [Then do Y]
    
    Red lines:
    - [Issue] [If ruled against us] [Response]
</strategic_framework>

<output_format>
# STRATEGIC LITIGATION PLAN
## Lismore Capital v Process Holdings

### EXECUTIVE SUMMARY
[Lismore's position, path to victory, recommended strategy]

### I. STRATEGIC ADVANTAGES
[Detailed analysis with priorities]

### II. PH'S WEAKNESSES TO EXPLOIT
[Attack strategy]

### III. EVIDENCE STRATEGY
[Comprehensive plan]

### IV. WITNESS STRATEGY
[Detailed witness-by-witness plan]

### V. EXPERT STRATEGY
[Expert needs and deployment]

### VI. LEGAL ARGUMENTS
[Primary and alternative theories]

### VII. DAMAGES STRATEGY
[Calculation methods and expert support]

### VIII. SETTLEMENT ANALYSIS
[Position and leverage]

### IX. TRIAL STRATEGY
[Complete trial plan]

### X. RISK MANAGEMENT
[Risks and mitigation]

### PRIORITY ACTIONS
[Top 10 immediate actions ranked]

### TIMELINE TO HEARING
[Critical path with deadlines]
</output_format>

Synthesise everything. Give Lismore the roadmap to victory.
"""
    
    def final_report_prompt(self,
                           all_findings: Dict,
                           strategic_plan: Dict) -> str:
        """
        Generate final tribunal-ready report
        """
        
        return f"""{HALLUCINATION_PREVENTION}

<final_report_mission>
Create comprehensive tribunal-ready report.

This document will be:
- Read by tribunal members
- Used by Lismore's counsel
- Referenced in hearings
- Attached to submissions

MUST BE:
- Impeccably accurate
- Thoroughly cited
- Legally sound
- Strategically optimal
- Professionally formatted
</final_report_mission>

<content_to_synthesise>
FINDINGS: {json.dumps(all_findings, indent=2)[:15000]}
STRATEGY: {json.dumps(strategic_plan, indent=2)[:10000]}
</content_to_synthesise>

<report_structure>

COVER PAGE
- Title: Litigation Intelligence Report
- Case: Lismore Capital v Process Holdings  
- Date: [Current date]
- Confidential & Privileged

TABLE OF CONTENTS
[Auto-generate from sections]

EXECUTIVE SUMMARY (2-3 pages)
- Case overview
- Key findings (top 10)
- Strategic recommendations (top 5)
- Damages summary
- Recommended outcome

SECTION 1: CASE BACKGROUND (5-10 pages)
- Parties
- Agreements
- Relationship history
- Dispute genesis
- Procedural history

SECTION 2: LEGAL FRAMEWORK (10-15 pages)
- Applicable law
- Key legal principles
- Relevant precedents
- Elements to prove
- Burden of proof
[Every principle cited to authority]

SECTION 3: FACTUAL FINDINGS (30-50 pages)
Organised by category:
- Contract breaches (with evidence)
- Misrepresentations (with evidence)
- Fiduciary breaches (with evidence)
- Bad faith conduct (with evidence)
- Credibility issues (with evidence)
- Document withholding (with evidence)
[Every fact cited to document]

SECTION 4: PATTERN ANALYSIS (10-20 pages)
- Systematic misconduct patterns
- Evolution over time
- Coordinated actions
- Intent evidence
[Comprehensive pattern documentation]

SECTION 5: DAMAGES ANALYSIS (15-25 pages)
- Damages categories
- Calculations (detailed)
- Expert evidence needed
- Causation links
- Mitigation issues
[Every figure supported by evidence]

SECTION 6: STRATEGIC ANALYSIS (20-30 pages)
- Lismore's strengths
- PH's weaknesses
- Litigation strategy
- Evidence strategy
- Witness strategy
- Expert strategy

SECTION 7: LEGAL ARGUMENTS (15-25 pages)
- Primary theories (detailed)
- Alternative theories
- Novel arguments
- Anticipated defences
- Rebuttals
[Full legal analysis with authority]

SECTION 8: RECOMMENDATIONS (5-10 pages)
- Priority actions
- Settlement position
- Trial strategy
- Risk mitigation
- Timeline

APPENDICES
A. Chronology (detailed)
B. Entity relationship map
C. Key documents index
D. Legal authorities
E. Damages calculations (spreadsheets)
F. Witness list
G. Expert list
H. Document production gaps
</report_structure>

<quality_standards>
EVERY PAGE MUST:
- Be professionally formatted
- Cite all factual claims
- Cite all legal arguments
- Use clear headings
- Be internally consistent
- Support Lismore's case

NO PAGE MAY:
- Contain unsupported claims
- Include speculation as fact
- Misquote documents
- Misstate law
- Undermine Lismore's position
</quality_standards>

Generate complete report. Make it tribunal-ready. Cite everything.
"""