#!/usr/bin/env python3
"""
Recursive Self-Questioning Prompts for Deep Analysis
COMPLETE REPLACEMENT for src/prompts/recursive.py
"""

from typing import Dict, List
import json


HALLUCINATION_PREVENTION = """
<critical_accuracy_requirements>
MANDATORY CITATION RULES:
1. EVERY factual claim MUST cite: [DOC_ID: Location]
2. No speculation without [INFERENCE] label
3. Quotes must be EXACT - word-for-word from documents
4. If uncertain, clearly mark as [UNCERTAIN] with reasoning

✓ "PH stated 'X' [DOC_123: p4, para 2]"
✗ "PH probably stated X" - REJECTED: No citation
</critical_accuracy_requirements>
"""


class RecursivePrompts:
    """Generate recursive self-questioning prompts for deep litigation analysis"""
    
    def __init__(self, config):
        self.config = config
    
    def deep_questioning_prompt(self,
                                initial_analysis: str,
                                depth: int = 5,
                                context: Dict = None) -> str:
        """
        Recursive self-questioning to deepen analysis quality
        Claude questions its own conclusions to find gaps and strengthen arguments
        """
        
        return f"""{HALLUCINATION_PREVENTION}

<recursive_analysis_mission>
You just completed initial analysis. Now CHALLENGE YOUR OWN CONCLUSIONS.

Goal: Strengthen Lismore's case by:
- Identifying gaps in your analysis
- Finding alternative explanations you missed
- Stress-testing your arguments
- Anticipating PH's counter-arguments
- Deepening legal analysis
- Finding additional evidence
</recursive_analysis_mission>

<initial_analysis>
{initial_analysis[:20000]}
</initial_analysis>

<context>
{json.dumps(context, indent=2)[:3000] if context else "No additional context"}
</context>

<recursive_questioning_framework>

LEVEL 1: QUESTION YOUR FINDINGS
For each finding in your initial analysis, ask:
- What evidence did I rely on? Is it the strongest available?
- What alternative explanations exist?
- What would PH argue against this?
- What additional evidence would make this stronger?
- Did I miss any relevant legal principles?
- Is my legal analysis complete?

LEVEL 2: CHALLENGE YOUR REASONING
- Am I making logical leaps?
- Are my inferences justified by the evidence?
- What assumptions am I making?
- Could I be wrong about this?
- What would make me change my conclusion?
- How would an expert critique this analysis?

LEVEL 3: STRATEGIC DEPTH
- How does this help Lismore WIN?
- Is this the best use of this evidence?
- Are there stronger arguments available?
- What's the most compelling way to present this?
- How does this fit into overall case strategy?
- What's the risk if PH has a good counter?

LEVEL 4: ADVERSARIAL TESTING
- How would PH's lawyer attack this finding?
- What documents might undermine this?
- What witness testimony could contradict this?
- What legal arguments defeat this?
- How do I counter those attacks?
- Does this survive aggressive cross-examination?

LEVEL 5: SYNTHESIS & REFINEMENT
- What are the 3 strongest arguments for Lismore?
- What evidence must we find to win?
- What are Lismore's biggest risks?
- What novel legal arguments exist?
- How do all findings connect?
- What's the winning narrative?
</recursive_questioning_framework>

<output_format>
For each level of questioning:

LEVEL X: [Level name]

QUESTIONS:
Q1: [Specific question about initial analysis]
A1: [Answer with evidence and reasoning]
   CONFIDENCE: [0.0-1.0]
   NEW INSIGHTS: [What this reveals]
   
Q2: [Next question]
A2: [Answer]
   ...

KEY DISCOVERIES:
- [New finding or insight from questioning]
- [Gap identified in initial analysis]
- [Stronger argument developed]
- [Risk identified and mitigated]

REFINEMENTS TO INITIAL ANALYSIS:
- [Change #1: Why and how it strengthens case]
- [Change #2: Additional evidence needed]
- [Change #3: Legal argument refined]
</output_format>

<critical_instructions>
1. Be RUTHLESS in questioning yourself
2. Find flaws before PH's lawyers do
3. Strengthen arguments through self-critique
4. Identify evidence gaps explicitly
5. Every refined conclusion must cite evidence
6. If you find your initial analysis was wrong, say so
7. Prioritise quality over quantity
8. Focus on what wins the case
</critical_instructions>

<self_verification>
After recursive analysis:
□ Every new/refined finding has citation
□ Identified weaknesses in initial analysis
□ Anticipated PH's counter-arguments
□ Suggested stronger alternative arguments
□ Identified evidence gaps
□ Assessed strategic value realistically
□ No speculation without [INFERENCE] label
</self_verification>

Question yourself deeply. Find the truth. Strengthen Lismore's case.
"""
    
    def focused_investigation_prompt(self,
                                   investigation_thread: Dict,
                                   context: Dict,
                                   depth: int = 3) -> str:
        """
        Deep-dive investigation on specific finding
        """
        
        return f"""{HALLUCINATION_PREVENTION}

<investigation_mission>
Deep investigation of specific finding that requires thorough analysis.

INVESTIGATION TYPE: {investigation_thread.get('type')}
PRIORITY: {investigation_thread.get('priority'):.1f}/10
TRIGGER: {json.dumps(investigation_thread.get('data', {}), indent=2)[:1000]}
</investigation_mission>

<context>
{json.dumps(context, indent=2)[:5000]}
</context>

<deep_investigation_protocol>

PHASE 1: EVIDENCE GATHERING
- What documents are most relevant?
- What specific passages contain evidence?
- What's missing from the evidence?
- What witnesses would know about this?
- What experts might help?

Cite every piece of evidence: [DOC:LOC]

PHASE 2: LEGAL ANALYSIS
- What legal principles apply?
- What precedents are relevant?
- What elements must Lismore prove?
- What burdens of proof apply?
- What defences might PH raise?

Provide legal basis for each argument.

PHASE 3: FACTUAL ANALYSIS
- What exactly happened?
- Who knew what, when?
- What was said/written?
- What actions were taken?
- What's the timeline?

Build chronology with citations.

PHASE 4: CAUSATION & DAMAGES
- How did this cause Lismore's losses?
- What damages flow from this?
- How do we quantify the loss?
- What mitigation issues exist?
- What's the maximum recovery?

Link damages to breach with evidence.

PHASE 5: STRATEGIC ASSESSMENT
- How strong is this finding? [1-10]
- What's the best use in arbitration?
- Opening statement? Expert report? Cross-examination?
- What additional evidence would make it bulletproof?
- What are the risks if we pursue this?

Provide realistic strategic assessment.

PHASE 6: COUNTER-ANALYSIS
- What will PH argue?
- What's their best defence?
- What evidence might undermine this?
- How do we counter their arguments?
- What's our fallback position?

Anticipate and prepare for defence.
</deep_investigation_protocol>

<output_format>
INVESTIGATION SUMMARY:
[2-3 sentences on what this investigation found]

KEY FINDINGS:
1. [Finding with citation and legal basis]
2. [Finding with citation and legal basis]
3. [Finding with citation and legal basis]

EVIDENCE MAP:
- Primary: [DOC:LOC] [What it shows]
- Supporting: [DOC:LOC] [What it shows]
- Corroborating: [DOC:LOC] [What it shows]

LEGAL FRAMEWORK:
- Applicable law: [Citation]
- Elements to prove: [List with evidence for each]
- Burden of proof: [Who bears it, strength of case]

DAMAGES:
- Type: [Consequential/Direct/etc]
- Calculation: [How computed]
- Amount: [Range or specific amount]
- Evidence: [Citations]

STRATEGIC RECOMMENDATION:
[How to use this in arbitration]

RISKS & MITIGATION:
- Risk: [What could go wrong]
- Mitigation: [How to address it]

ADDITIONAL INVESTIGATION NEEDED:
- [Specific evidence to seek]
- [Witnesses to interview]
- [Experts to instruct]
</output_format>

Investigate thoroughly. Leave no stone unturned. Build bulletproof case.
"""
    
    def contradiction_deep_dive(self,
                               contradiction: Dict,
                               documents: List[Dict],
                               context: Dict) -> str:
        """
        Deep analysis of specific contradiction
        """
        
        return f"""{HALLUCINATION_PREVENTION}

<contradiction_investigation>
Investigate this contradiction in depth to determine its significance for Lismore's case.

CONTRADICTION IDENTIFIED:
{json.dumps(contradiction, indent=2)[:2000]}
</contradiction_investigation>

<relevant_documents>
{self._format_documents(documents[:20])}
</relevant_documents>

<context>
{json.dumps(context, indent=2)[:2000]}
</context>

<contradiction_analysis_framework>

1. VERIFY THE CONTRADICTION
   - Confirm Statement A is accurately quoted [cite exact location]
   - Confirm Statement B is accurately quoted [cite exact location]
   - Verify they actually conflict (not just different emphasis)
   - Check for any qualifications or conditions
   
   VERIFIED: Yes/No
   If No, explain why it's not actually a contradiction

2. ASSESS MATERIALITY
   - Is this contradiction material to key issues?
   - Does it affect liability or damages?
   - Would outcome differ if resolved in PH's favour?
   
   MATERIALITY: [High/Medium/Low] with reasoning

3. DETERMINE CAUSE
   Why does this contradiction exist?
   - Deliberate falsehood?
   - Changed circumstances?
   - Different knowledge at different times?
   - Witness coordination failure?
   - Cover-up attempt?
   
   MOST LIKELY CAUSE: [with evidence]

4. LEGAL IMPLICATIONS
   - Does this prove misrepresentation?
   - Does it show fraudulent inducement?
   - Does it establish breach?
   - Does it affect credibility?
   - Can we draw adverse inferences?
   
   LEGAL SIGNIFICANCE: [detailed analysis]

5. STRATEGIC USE
   - Opening statement impact?
   - Cross-examination potential?
   - Expert evidence support?
   - Adverse inference argument?
   - Settlement leverage?
   
   BEST USE: [specific recommendation]

6. ANTICIPATE DEFENCE
   - How will PH explain this?
   - What's their best argument?
   - What evidence might support them?
   - How do we rebut?
   
   COUNTER-STRATEGY: [detailed plan]
</contradiction_analysis_framework>

<output_format>
CONTRADICTION VERIFIED: [Yes/No]

STATEMENT A: [exact quote] [DOC:LOC] [date]
STATEMENT B: [exact quote] [DOC:LOC] [date]

CONFLICT: [Precisely how they contradict]

MATERIALITY: [High/Medium/Low]
REASONING: [Why material or not]

CAUSE: [Most likely explanation with evidence]

LEGAL BASIS:
- [Principle 1] [How contradiction proves it]
- [Principle 2] [How contradiction proves it]

STRATEGIC VALUE: [1-10]
RECOMMENDED USE: [Specific deployment strategy]

PH'S LIKELY DEFENCE: [What they'll argue]
OUR COUNTER: [How we defeat their defence]

EVIDENCE NEEDED: [What would make this bulletproof]
</output_format>

Analyse this contradiction exhaustively. Make it a weapon for Lismore.
"""
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format documents for prompts"""
        if not documents:
            return "No documents provided"
        
        formatted = []
        for doc in documents:
            formatted.append(f"""
<document id="{doc.get('id', 'unknown')}">
<filename>{doc.get('filename', 'unknown')}</filename>
<content>
{doc.get('content', '')[:10000]}
</content>
</document>
""")
        
        return '\n'.join(formatted)