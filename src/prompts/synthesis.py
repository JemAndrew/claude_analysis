#!/usr/bin/env python3
"""
Synthesis Prompts for Final Strategic Reports
Complete file for Lismore v Process Holdings analysis
"""

from typing import Dict, List
import json


class SynthesisPrompts:
    """Generate synthesis prompts for final strategic reports"""
    
    def __init__(self, config):
        self.config = config
    
    def strategic_synthesis_prompt(self,
                                  phase_analyses: Dict[str, str],
                                  investigations: List[Dict],
                                  knowledge_graph_export: Dict) -> str:
        """
        Synthesise all intelligence into strategic recommendations
        """
        
        return f"""{self.config.hallucination_prevention}

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
   
   Priority: Which to lead with and why

2. CRITICAL WEAKNESSES IN PROCESS HOLDINGS' CASE (Top 10)
   Attack these aggressively:
   - [Weakness 1] [How to expose] [Evidence to use]
   - [Weakness 2] [How to expose] [Evidence to use]
   
   Strategy: Order and method of attack

3. EVIDENCE STRATEGY
   Must-have documents:
   - [Document type] [Why critical] [How to obtain]
   
   Exhibit strategy:
   - Key exhibits for opening
   - Documentary evidence packages
   - Demonstrative exhibits

4. WITNESS STRATEGY
   Lismore's witnesses:
   - [Witness] [Topics] [Preparation needs] [Strengths/Weaknesses]
   
   Process Holdings' witnesses to destroy:
   - [Witness] [Credibility issues] [Cross-examination strategy]

5. LEGAL ARGUMENT STRATEGY
   Primary theories:
   - [Theory 1] [Strength 1-10] [Legal authority]
   - [Theory 2] [Strength 1-10] [Legal authority]

6. DAMAGES STRATEGY
   Primary calculation:
   - [Method] [Amount] [Evidence] [Strength]

7. SETTLEMENT POSITION
   Lismore's BATNA:
   - [Best outcome at trial] [Probability] [Amount]
   
   Settlement range:
   - Minimum acceptable: [Amount] [Justification]
   - Target: [Amount] [Justification]

8. TRIAL STRATEGY
   Opening statement structure:
   - [Theme] [Key 3-5 points] [Visual aids]

9. RISK ASSESSMENT
   Risks to Lismore:
   - [Risk] [Likelihood] [Impact] [Mitigation]

10. PRIORITY ACTIONS
    [Top 10 immediate actions ranked]
</strategic_framework>

<output_format>
# STRATEGIC LITIGATION PLAN
## Lismore Capital v Process Holdings

### EXECUTIVE SUMMARY
[Lismore's position, path to victory, recommended strategy]

### I. STRATEGIC ADVANTAGES
[Detailed analysis with priorities]

### II. PROCESS HOLDINGS' WEAKNESSES TO EXPLOIT
[Attack strategy]

### III. EVIDENCE STRATEGY
[Comprehensive plan]

### IV. WITNESS STRATEGY
[Detailed witness-by-witness plan]

### V. LEGAL ARGUMENTS
[Primary and alternative theories]

### VI. DAMAGES STRATEGY
[Calculation methods and expert support]

### VII. SETTLEMENT ANALYSIS
[Position and leverage]

### VIII. TRIAL STRATEGY
[Complete trial plan]

### IX. RISK MANAGEMENT
[Risks and mitigation]

### X. PRIORITY ACTIONS
[Top 10 immediate actions ranked]

### TIMELINE TO HEARING
[Critical path with deadlines]
</output_format>

Use British English spelling. Synthesise everything. Give Lismore the roadmap to victory.
"""
    
    def narrative_construction_prompt(self,
                                     findings: Dict,
                                     contradictions: List[Dict],
                                     patterns: Dict,
                                     timeline: Dict,
                                     entities: Dict) -> str:
        """
        Build compelling narrative from all analysis
        """
        
        return f"""{self.config.hallucination_prevention}

<narrative_mission>
Construct tribunal-ready narrative that wins the arbitration for Lismore.

Transform analysis into compelling story:
- Clear, logical structure
- Devastating for Process Holdings
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

PART 1: THE FOUNDATION
- Lismore's reasonable expectations
- The agreements and their terms
- What Process Holdings promised
- Why Lismore relied on Process Holdings

PART 2: THE BREACHES
- Chronological account of Process Holdings' failures
- Each breach identified and proven
- Legal basis for each claim
- Evidence for each breach

PART 3: THE PATTERN
- Not isolated failures but systematic
- Coordinated bad faith
- Evidence of deliberate strategy
- Pattern proves intent

PART 4: THE DAMAGES
- Direct losses from breaches
- Consequential damages
- Lost opportunities

PART 5: THE SMOKING GUNS
- Top 5-10 most damaging findings
- Contradictions Process Holdings cannot explain
- Documents proving knowledge/intent

PART 6: PROCESS HOLDINGS' DEFENCES
- What Process Holdings will argue
- Why each defence fails
- Evidence contradicting their story

PART 7: THE REMEDY
- Damages quantum
- Interest
- Costs
- Other relief
</narrative_structure>

<quality_requirements>
1. Every factual claim cited: [DOC_ID: Location]
2. Every legal argument has authority
3. Chronology is clear and precise
4. No speculation without [INFERENCE] label
5. British English spelling throughout

TONE:
- Professional but forceful
- Confident but not arrogant
- Factual but compelling
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
[Pre-emptive destruction of Process Holdings' arguments]

### PART 7: RELIEF SOUGHT
[What tribunal should award]

### CONCLUSION
[Why Lismore must prevail]
</output_format>

Build the narrative that wins. Make it bulletproof. Cite everything.
"""