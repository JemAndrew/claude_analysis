#!/usr/bin/env python3
"""
Recursive Self-Questioning Prompts for Deep Analysis
Forces Claude to challenge its own conclusions repeatedly
"""

from typing import Dict, List, Optional, Any
import json


class RecursivePrompts:
    """Multi-level self-questioning for maximum insight extraction"""
    
    def __init__(self, config):
        self.config = config
        self.max_depth = config.recursion_config['self_questioning_depth']
        self.min_depth = config.recursion_config['min_questioning_depth']
    
    def deep_questioning_prompt(self,
                               initial_analysis: str,
                               depth: int = None,
                               focus_areas: List[str] = None) -> str:
        """
        Generate recursive self-questioning prompt
        Each level challenges the previous level's assumptions
        """
        
        depth = depth or self.max_depth
        depth = max(self.min_depth, min(depth, self.max_depth))
        
        focus_areas = focus_areas or [
            'hidden assumptions',
            'alternative explanations',
            'missing evidence',
            'strategic implications',
            'opponent perspective'
        ]
        
        prompt = f"""<initial_analysis>
{initial_analysis[:8000]}
</initial_analysis>

<recursive_questioning_protocol>
You will now engage in {depth}-level deep recursive questioning about your analysis.
Each level must challenge and expand the previous level.

QUESTIONING FRAMEWORK:
- Every answer must be challenged by the next level
- Assumptions must be exposed and tested
- Alternative explanations must be considered
- Strategic value must be assessed at each level
- New investigation paths must be identified
</recursive_questioning_protocol>

<level_1_questions>
Generate 5 CRITICAL questions about your analysis focusing on:
{self._format_focus_areas(focus_areas)}

For each L1 question:
1. Provide detailed, thorough answer
2. Challenge your core assumptions
3. Identify what evidence would prove/disprove
4. Rate strategic importance (1-10)
5. Identify investigation paths
</level_1_questions>

<level_2_questions>
For EACH L1 answer, generate 3 follow-up questions that:
- Dig deeper into implications
- Challenge the L1 reasoning
- Explore alternative interpretations
- Find hidden connections
- Test logical soundness

For each L2 question:
1. Provide comprehensive answer
2. Identify new patterns/connections
3. Assess probability of being correct
4. Determine what we're missing
</level_2_questions>

<level_3_questions>
For EACH L2 answer, generate 2 critical challenges that:
- Test the fundamental logic
- Propose opposite interpretation
- Identify cognitive biases affecting analysis
- Determine strategic blind spots
- Find the "what if we're completely wrong"

For each L3 challenge:
1. Provide rigorous analysis
2. Calculate confidence adjustment
3. Identify pivotal evidence needed
4. Assess case impact
</level_3_questions>

{self._add_deeper_levels(depth)}

<synthesis_requirements>
After completing all levels, provide:

CRITICAL DISCOVERIES:
- Top 5 insights uncovered through questioning
- Confidence level for each (0.0-1.0)

NEW INVESTIGATION PRIORITIES:
- What must be investigated immediately
- Why it matters strategically

ASSUMPTION CORRECTIONS:
- What assumptions were wrong
- How this changes our approach

STRATEGIC ADJUSTMENTS:
- How our strategy should adapt
- What new attack vectors opened up

CONFIDENCE ASSESSMENT:
- Overall confidence in conclusions (0.0-1.0)
- Key uncertainties remaining
</synthesis_requirements>

<example_structure>
L1-Q1: Why did they structure the transaction this way?
L1-A1: [Detailed analysis of transaction structure]
  Strategic Importance: 8/10
  Evidence needed: Bank records, board minutes
  Investigation path: Follow money flow
  
  L2-Q1.1: What if the structure was designed to hide something else?
  L2-A1.1: [Analysis of potential concealment]
    Probability: 0.7
    New pattern: Similar structures in other deals
    
    L3-Q1.1.1: Could we be seeing conspiracy where there's incompetence?
    L3-A1.1.1: [Critical examination of conspiracy vs incompetence]
      Confidence adjustment: -0.2
      Pivotal evidence: Communications showing intent
      
    L3-Q1.1.2: What would their lawyer argue about this structure?
    L3-A1.1.2: [Adversarial perspective]
      Counter-argument: Legitimate tax planning
      Our response: Pattern shows intent beyond tax
</example_structure>

Begin {depth}-level recursive questioning. Be ruthlessly self-critical.
Question everything. Assume nothing. Find the truth.
"""
        
        return prompt
    
    def focused_investigation_prompt(self,
                                   investigation_thread: Dict,
                                   context: Dict,
                                   depth: int = 3) -> str:
        """
        Deep-dive prompt for specific investigation thread
        """
        
        prompt = f"""<investigation_thread>
Type: {investigation_thread.get('type')}
Priority: {investigation_thread.get('priority')}
Trigger: {json.dumps(investigation_thread.get('data', {}), indent=2)[:2000]}
</investigation_thread>

<investigation_context>
{json.dumps(context, indent=2)[:3000]}
</investigation_context>

<deep_investigation_protocol>
This requires {depth}-level deep investigation.

LEVEL 1: IMMEDIATE INVESTIGATION
- What does this discovery mean?
- What else must be true if this is true?
- What evidence would confirm/refute this?
- Who benefits from this?
- Who would know about this?

LEVEL 2: EXPANDED INVESTIGATION
For each L1 finding:
- What patterns connect to this?
- What timeline events relate?
- What documents should exist?
- What conversations happened?
- What money moved?

LEVEL 3: STRATEGIC INVESTIGATION  
For each L2 finding:
- How do we prove this in court?
- What's their best defence?
- How do we destroy that defence?
- What's the nuclear option here?
- What are we still missing?

{self._add_investigation_levels(depth)}
</deep_investigation_protocol>

<required_outputs>
1. FINDINGS SUMMARY
   - Key discoveries with confidence scores
   - Evidence located
   - Evidence still needed

2. CONTRADICTION ANALYSIS
   - New contradictions discovered
   - Severity assessment (1-10)
   - Strategic value

3. PATTERN EVOLUTION
   - How this changes known patterns
   - New patterns discovered
   - Confidence adjustments

4. ENTITY IMPLICATIONS
   - Who's implicated
   - New relationships uncovered
   - Suspicion score changes

5. NEXT STEPS
   - Child investigations to spawn
   - Priority actions
   - Evidence to secure

6. STRATEGIC ASSESSMENT
   - How this helps Lismore
   - How this damages Process Holdings
   - Settlement leverage impact
   - Trial strategy impact
</required_outputs>

Investigate with maximum thoroughness. Leave no stone unturned.
This could be the thread that unravels everything.
"""
        
        return prompt
    
    def hypothesis_testing_prompt(self,
                                hypothesis: str,
                                evidence_for: List[str],
                                evidence_against: List[str],
                                context: Dict) -> str:
        """
        Rigorous hypothesis testing through recursive questioning
        """
        
        prompt = f"""<hypothesis>
{hypothesis}
</hypothesis>

<current_evidence>
SUPPORTING EVIDENCE:
{self._format_evidence(evidence_for)}

CONTRADICTING EVIDENCE:
{self._format_evidence(evidence_against)}
</current_evidence>

<hypothesis_testing_protocol>
Test this hypothesis through 5-level recursive analysis:

LEVEL 1: BASIC VALIDITY
Q1: Is this hypothesis logically sound?
Q2: What assumptions underpin it?
Q3: What must be true for this to be true?
Q4: What cannot be true if this is true?
Q5: What's the simplest alternative explanation?

LEVEL 2: EVIDENCE ANALYSIS
For each L1 answer, examine:
- Quality of supporting evidence
- Weight of contradicting evidence  
- Missing evidence that should exist
- Reliability of sources
- Alternative interpretations

LEVEL 3: STRATEGIC TESTING
For each L2 finding, determine:
- Courtroom viability
- Burden of proof requirements
- Vulnerability to challenge
- Jury comprehension
- Documentary support needed

LEVEL 4: ADVERSARIAL TESTING
For each L3 conclusion:
- Best counter-argument
- Evidence they'd present
- Experts they'd call
- Narrative they'd construct
- Weaknesses they'd exploit

LEVEL 5: FINAL ASSESSMENT
For each L4 challenge:
- Our response strategy
- Additional evidence needed
- Confidence in prevailing
- Alternative approaches
- Risk assessment
</hypothesis_testing_protocol>

<output_requirements>
HYPOTHESIS VIABILITY:
- Probability of being correct (0.0-1.0)
- Confidence in evidence (0.0-1.0)
- Strategic value if proven (1-10)
- Risk if pursued and wrong (1-10)

CRITICAL EVIDENCE GAPS:
- What would prove this definitively
- Where that evidence likely exists
- How to obtain it
- Timeline for investigation

ALTERNATIVE HYPOTHESES:
- Other explanations that fit evidence
- Their relative probability
- Testing requirements

RECOMMENDATION:
- Pursue/modify/abandon hypothesis
- Resources required
- Expected outcomes
- Strategic implications
</output_requirements>

Test rigorously. Challenge mercilessly. Find truth.
"""
        
        return prompt
    
    def _format_focus_areas(self, areas: List[str]) -> str:
        """Format focus areas for questioning"""
        return "\n".join([f"- {area}" for area in areas])
    
    def _add_deeper_levels(self, depth: int) -> str:
        """Add additional levels beyond 3 if specified"""
        if depth <= 3:
            return ""
        
        additional = []
        for level in range(4, depth + 1):
            additional.append(f"""
<level_{level}_questions>
For EACH L{level-1} answer, generate 2 fundamental challenges that:
- Question the entire framework of analysis
- Propose paradigm-shifting interpretations
- Identify systemic biases
- Find critical vulnerabilities
- Test ultimate strategic value

Rate final confidence (0.0-1.0) and strategic importance (1-10)
</level_{level}_questions>""")
        
        return "\n".join(additional)
    
    def _add_investigation_levels(self, depth: int) -> str:
        """Add investigation levels beyond 3"""
        if depth <= 3:
            return ""
        
        additional = []
        for level in range(4, depth + 1):
            additional.append(f"""
LEVEL {level}: META-INVESTIGATION
- What are we not seeing?
- What would opposing counsel investigate?
- What would a forensic accountant find?
- What would a private investigator discover?
- What's the story behind the story?""")
        
        return "\n".join(additional)
    
    def _format_evidence(self, evidence: List[str]) -> str:
        """Format evidence list for prompt"""
        if not evidence:
            return "No evidence provided"
        
        formatted = []
        for i, item in enumerate(evidence[:20], 1):
            formatted.append(f"{i}. {item[:200]}")
        
        return "\n".join(formatted)