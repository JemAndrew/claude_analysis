#!/usr/bin/env python3
"""
Maximum Quality Autonomous Prompts with:
- Few-shot examples (shows Claude exactly what you want)
- Multi-document reasoning
- Chain of thought instructions
- Enhanced adversarial framing
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class AutonomousPrompts:
    """Prompts optimised for maximum Claude performance"""
    
    def __init__(self, config):
        self.config = config
    
    # ========================================================================
    # PASS 1: TRIAGE PROMPT
    # ========================================================================
    
    def triage_prompt(self, documents: List[Dict]) -> str:
        """Pass 1: Quick triage with examples"""
        
        doc_previews = []
        for i, doc in enumerate(documents):
            preview = doc.get('content', '')[:300]
            metadata = doc.get('metadata', {})
            
            doc_previews.append(f"""
[DOC_{i}]
Filename: {metadata.get('filename', 'unknown')}
Date: {metadata.get('date', 'unknown')}
Type: {metadata.get('doc_type', 'unknown')}
Preview: {preview}
---
""")
        
        prompt = f"""<triage_mission>
You are triaging disclosure documents for commercial litigation analysis.

Goal: Quickly assess each document's priority for deep analysis.

WE ARE ARGUING FOR LISMORE. Prioritise documents that:
- Relate to contractual obligations and breaches
- Show evidence of wrongdoing or misrepresentation  
- Reference key parties, dates, or financial transactions
- Are high-quality evidence (contracts, board minutes, witness statements)
</triage_mission>

<documents>
{''.join(doc_previews)}
</documents>

<scoring>
For EACH document, provide:

[DOC_X]
Priority Score: [1-10]
Reason: [One sentence - why this priority?]
Category: [contract|financial|correspondence|witness|expert|other]

Scoring guide:
10: Smoking gun (direct breach evidence, admissions, critical contracts)
8-9: High value (key agreements, board minutes, expert reports, financial records)
6-7: Important (correspondence with key parties, meeting notes)
4-5: Relevant (background information, peripheral documents)
1-3: Low priority (administrative, duplicates, tangential)

Examples:
- "SPA_2021_Final.pdf" mentioning Lismore/PH → Score 9-10
- "Board_Minutes_Disclosure_Decision.pdf" → Score 10
- "Email_routine_admin.pdf" → Score 2
- "Valuation_Report_2021.pdf" → Score 8

Be decisive. Err on side of higher priority if uncertain.
</scoring>

Score all {len(documents)} documents now.
"""
        
        return prompt
    
    # ========================================================================
    # PASS 2: DEEP ANALYSIS PROMPT (MAXIMUM QUALITY)
    # ========================================================================
    
    def deep_analysis_prompt(self, 
                            documents: List[Dict],
                            iteration: int,
                            accumulated_knowledge: Dict,
                            confidence: float,
                            phase_instruction: str = None) -> str:
        """
        Pass 2: Maximum quality analysis prompt
        ENHANCED: Few-shot examples, chain of thought, multi-doc reasoning
        """
        
        # Determine phase
        if phase_instruction is None:
            if iteration == 0:
                phase_instruction = "PHASE: DISCOVER THE CLAIMS"
            elif iteration < 15:
                phase_instruction = "PHASE: TEST CLAIMS AGAINST EVIDENCE"
            else:
                phase_instruction = "PHASE: DEEP INVESTIGATION + NOVEL ARGUMENTS"
        
        # Phase-specific instructions
        if iteration == 0:
            critical_context = """
<critical_phase_1_instructions>
THIS IS ITERATION 1: DISCOVER THE CLAIMS

Your ONLY job this iteration is to understand what each party claims:

1. PH'S ALLEGATIONS AGAINST LISMORE:
   - What do they claim Lismore did wrong?
   - What obligations do they say were breached?
   - What damages are they claiming?
   - What is their factual narrative?

2. LISMORE'S DEFENCE:
   - How does Lismore respond to each allegation?
   - What is Lismore's factual narrative?
   - What affirmative defences does Lismore raise?

3. FACTUAL DISPUTES:
   - Where do they disagree on facts?
   - What facts do both sides agree on?

ZERO ASSUMPTIONS: Only extract what THE PARTIES actually say in the pleadings.
Don't import theories. Don't make inferences. Just map the dispute.

You're learning the battlefield before the battle.
</critical_phase_1_instructions>
"""
        elif iteration < 15:
            critical_context = """
<critical_phase_2_instructions>
TEST EVERY CLAIM AGAINST THIS EVIDENCE

You now know what each party claims (from iteration 1).
Test those claims against these contemporaneous documents.

For each PH allegation:
- What evidence supports it?
- What evidence contradicts it?
- Is their timeline consistent with documents?

For each Lismore defence:
- What evidence supports it?
- What evidence contradicts it?
- Is their narrative consistent with documents?

Look for:
- Contradictions (documents vs pleadings, documents vs witnesses)
- Timeline impossibilities
- Admissions (statements against interest)
- Gaps (what's missing that should exist)

EVIDENCE-BASED ASSESSMENT: Update your understanding based purely on what documents show, not what parties claim.
</critical_phase_2_instructions>
"""
        else:
            critical_context = """
<critical_phase_3_instructions>
GENERATE NOVEL ARGUMENTS NEITHER SIDE HAS MADE

You've learned what each party claims and tested against evidence.

NOW: Think as Lismore's strategic litigation counsel.

Generate NEW ARGUMENTS:

1. UNPLEADED DEFENCES:
   What defences do documents support that Lismore hasn't raised?

2. AFFIRMATIVE CASE:
   Can Lismore go on offence? Do documents support counterclaims?

3. EVIDENTIARY ATTACKS:
   Where is PH's evidence weakest? What contradictions can you exploit?

4. PROCEDURAL CHALLENGES:
   Has PH withheld documents? Failed disclosure obligations?

5. ALTERNATIVE THEORIES:
   What causation theories has neither side argued?

For each novel argument:
- State the argument
- Cite supporting evidence
- Explain why it's strategically valuable
- Assess strength (HIGH/MEDIUM/LOW)

Be creative. Generate arguments neither side has made.
</critical_phase_3_instructions>
"""
        
        prompt = f"""<deep_analysis_mission>
LITIGATION ANALYSIS FOR LISMORE v PROCESS HOLDINGS
ITERATION: {iteration + 1}/25
CURRENT CONFIDENCE: {confidence:.1%}
{phase_instruction}

WE ARE ARGUING FOR LISMORE. 
You are Lismore's strategic litigation counsel, not a neutral analyst.

Every analysis must serve ONE purpose:
→ Win this arbitration for Lismore.

YOU HAVE COMPLETE AUTONOMY. Use extended thinking extensively to:
- Reason through complex legal issues
- Challenge your own assumptions
- Make connections across documents
- Build evidence chains iteratively
- Self-assess completeness
- Generate creative arguments
</deep_analysis_mission>

{critical_context}

<core_principles>
1. ZERO ASSUMPTIONS
   - Only conclude what documents prove
   - Don't import theories from external sources
   - Don't make inferences beyond what evidence shows
   - If uncertain, mark as "needs investigation"
   - Quote specific passages from documents

2. LISMORE-SIDED ADVERSARIAL
   Every finding must answer:
   - How does this help Lismore's case?
   - How does this damage PH's defence?
   - What novel arguments can we construct?
   - What evidence destroys their case?
   - If you were PH's counsel, what would worry you most?

3. CREATIVE LITIGATION COUNSEL
   - Generate arguments neither side has made
   - Think beyond the pleadings
   - Identify procedural opportunities
   - Find evidentiary weaknesses in PH's case
   - Construct alternative causation theories

4. OPPONENT ARGUMENT PREDICTION
   For EVERY breach/argument you identify:
   - What will PH argue in response?
   - What evidence do they lack?
   - How do we pre-emptively destroy their counter-argument?

5. MULTI-DOCUMENT REASONING
   Think about ALL {len(documents)} documents together:
   - Which documents contradict each other?
   - Which documents form evidence chains?
   - What patterns emerge across documents?
   - What do document combinations prove?
</core_principles>

<accumulated_knowledge>
{json.dumps(accumulated_knowledge, indent=2)[:self.config.token_config['accumulated_knowledge_limit']]}

Timeline events: {len(accumulated_knowledge.get('timeline', []))}
Known breaches: {len(accumulated_knowledge.get('strong_patterns', []))}
Critical contradictions: {len(accumulated_knowledge.get('critical_contradictions', []))}
</accumulated_knowledge>

<documents_to_analyse>
{self._format_documents(documents)}
</documents_to_analyse>

<chain_of_thought_required>
Before providing structured output, use extended thinking to reason through:

STEP 1: EVIDENCE REVIEW
- What does each document actually say? (quote specific passages)
- What facts are proven vs inferred?
- What assumptions am I making? (identify them explicitly)

STEP 2: CROSS-DOCUMENT ANALYSIS
- How do these documents relate to each other?
- Which documents contradict which?
- What evidence chains exist (A → B → C proves X)?
- What patterns emerge across all documents?

STEP 3: LEGAL REASONING
- What legal elements does this evidence prove?
- What inferences can I make?
- What alternative interpretations exist?
- What's the strongest evidence vs weakest?

STEP 4: OPPONENT ANALYSIS
- What will PH argue about this evidence?
- What evidence do they lack to support their defence?
- Where are the gaps in their case?

STEP 5: STRATEGIC ASSESSMENT
- How does this help Lismore win?
- What novel arguments emerge?
- What's the exploitation strategy?
- What should we investigate further?

Only after completing this analysis, provide your structured output.
</chain_of_thought_required>

<few_shot_examples>
GOOD EXAMPLE - This is what we want:

BREACH_START
Description: Process Holdings failed to disclose £2.3M HMRC liability in pre-completion disclosure, violating express warranty in SPA clause 12.3(a) requiring "full and accurate disclosure of all material liabilities"
Clause/Obligation: SPA s.12.3(a) - Warranty of full disclosure of all material liabilities exceeding £100K
Evidence: ["DOC_0234_HMRC_Assessment_Notice", "DOC_0891_Board_Minutes_23_Feb_2021", "DOC_1247_Email_CFO_to_CEO"]
Confidence: 0.87
Causation: Lismore relied on warranties in SPA s.12.3 and overpaid by £2.3M for the shares, as purchase price was calculated on disclosed liabilities only. Had true liability position been known, purchase price would have been reduced by £2.3M per pricing formula in Schedule 4
Quantum: £2.3M direct loss (undisclosed liability) + £340K interest + £120K costs of HMRC negotiations = £2.76M total
PH_Counter_Argument: PH will claim the £2.3M liability was disclosed in the data room via document "DataRoom_Tax_Summary_Feb2021.xlsx" which showed "contingent tax exposures"
Our_Rebuttal: DataRoom document only disclosed £800K in "possible" tax issues, not the definite £2.3M liability. HMRC assessment notice (DOC_0234) dated 15 Feb 2021 made this a certain liability before completion on 1 March 2021. PH had actual knowledge per board minutes (DOC_0891) but failed to update data room. This is deliberate non-disclosure, not mere oversight.
BREACH_END

WHY THIS IS GOOD:
✓ Specific, detailed description with exact amounts
✓ Precise clause citation (s.12.3(a))
✓ Three supporting documents with clear IDs
✓ High confidence with specific reasoning
✓ Detailed causation with pricing mechanism explained
✓ Quantified damages with breakdown
✓ Predicts opponent's specific counter-argument
✓ Provides detailed rebuttal with evidence

---

BAD EXAMPLE - Do NOT do this:

BREACH_START
Description: There might be some disclosure issues
Clause/Obligation: Various clauses
Evidence: ["some documents"]
Confidence: 0.5
Causation: Possibly some losses
Quantum: Unknown
PH_Counter_Argument: They might say something
Our_Rebuttal: We disagree
BREACH_END

WHY THIS IS BAD:
✗ Vague, no specifics
✗ No precise clause citation
✗ Generic evidence references
✗ Low confidence without explanation
✗ Vague causation
✗ No quantum
✗ Generic opponent argument
✗ Weak rebuttal

---

ANOTHER GOOD EXAMPLE:

CONTRADICTION_START
Statement_A: PH's witness statement (para 23) claims "the HMRC assessment was first received on 15 March 2021, after completion"
Statement_B: Email chain (DOC_0891) shows CFO forwarded HMRC assessment to CEO on 17 February 2021 with subject line "Urgent - £2.3M tax issue before Lismore deal closes"
Doc_A: Witness_Statement_PH_CFO_para_23
Doc_B: DOC_0891_Email_17_Feb_2021
Severity: 9
Confidence: 0.95
Implications: This is a critical contradiction proving PH had actual knowledge of the liability before completion but deliberately misrepresented the timeline in litigation. The email is contemporaneous evidence that directly contradicts sworn testimony. This destroys PH's "we didn't know" defence.
Cross_Examination_Potential: Show witness the email with his own words "before Lismore deal closes" then ask: "Your witness statement says you received this after completion. That's false, isn't it?" Witness will be forced to admit the timeline was wrong, destroying credibility on the central issue.
CONTRADICTION_END

WHY THIS IS GOOD:
✓ Exact quotes from both documents
✓ Specific document references
✓ High severity with justification
✓ Explains why this matters strategically
✓ Provides specific cross-examination script
✓ Identifies how this undermines their defence

</few_shot_examples>

<structured_output_requirements>
CRITICAL: Use EXACT format shown in examples above.

1. BREACHES FOUND (use this format for each breach):

BREACH_START
Description: [Detailed description with specific amounts, dates, parties]
Clause/Obligation: [Exact clause citation e.g. "SPA s.12.3(a)"]
Evidence: ["DOC_ID_1", "DOC_ID_2", "DOC_ID_3"]
Confidence: [0.00-1.00]
Causation: [Detailed causation chain with specific mechanism]
Quantum: [Specific financial amounts with breakdown]
PH_Counter_Argument: [Specific argument PH will make - quote expected defence]
Our_Rebuttal: [Detailed rebuttal with evidence - show why their defence fails]
BREACH_END

2. CONTRADICTIONS FOUND:

CONTRADICTION_START
Statement_A: [Exact quote or detailed paraphrase]
Statement_B: [Exact quote or detailed paraphrase]
Doc_A: [Specific document ID]
Doc_B: [Specific document ID]
Severity: [1-10 with 10 being most severe]
Confidence: [0.0-1.0]
Implications: [Why this matters - what does it prove/disprove?]
Cross_Examination_Potential: [Specific questions to ask, predicted answers, follow-ups]
CONTRADICTION_END

3. TIMELINE EVENTS:

TIMELINE_EVENT_START
Date: [Exact date: YYYY-MM-DD or DD/MM/YYYY]
Description: [What happened, who was involved, what was said/done]
Participants: [Specific named individuals with roles]
Documents: ["DOC_ID_1", "DOC_ID_2"]
Confidence: [0.0-1.0]
Critical: [YES/NO]
Impossibilities: [Any timeline contradictions with other established events]
TIMELINE_EVENT_END

4. NOVEL ARGUMENTS (arguments neither side has made):

NOVEL_ARGUMENT_START
Argument: [Complete legal/factual argument with reasoning]
Supporting_Evidence: ["DOC_ID_1", "DOC_ID_2", "DOC_ID_3"]
Strategic_Value: [Why this helps Lismore win - be specific about impact]
Strength: [HIGH/MEDIUM/LOW with justification]
Risks: [Potential downsides, counter-arguments, weaknesses]
NOVEL_ARGUMENT_END

5. OPPONENT WEAKNESSES:

WEAKNESS_START
PH_Position: [What PH claims/argues]
Our_Attack: [How we exploit this weakness - specific strategy]
Evidence_Gap: [What evidence PH lacks and should have]
Cross_Examination: [Specific line of questioning to expose weakness]
WEAKNESS_END

6. GENERAL FINDINGS (natural language, bullet points):
- [Finding 1 with evidence citations]
- [Finding 2 with evidence citations]
- [Finding 3 with evidence citations]

7. CRITICAL FINDINGS REQUIRING INVESTIGATION:
Mark findings needing deeper investigation:

[CRITICAL] [Specific topic requiring investigation with initial evidence]
[NUCLEAR] [Smoking gun requiring immediate deep dive with doc references]

8. SELF-ASSESSMENT (MANDATORY):

CONFIDENCE: [0.00 - 1.00]

Interpretation guide:
- 0.0-0.3: Just starting, need much more information
- 0.4-0.6: Getting clearer but significant gaps remain  
- 0.7-0.9: Strong understanding, minor gaps only
- 0.95-1.0: Complete understanding, confident to advise

CONTINUE: [YES or NO]

Reasoning: [Detailed explanation - why this confidence? what am I missing? what would increase confidence?]

IMPORTANT: Provide decimal confidence score, not percentage.
</structured_output_requirements>

<quality_requirements>
EVERY finding must meet these standards:

1. EVIDENCE CITATIONS
   - Every factual claim cites specific document IDs
   - Document IDs must match format: DOC_XXXX or descriptive IDs
   - Cite at least 2-3 documents per breach
   - Quote specific passages where critical

2. PRECISION
   - Exact dates (not "around March")
   - Specific amounts (not "significant loss")
   - Named individuals (not "management")
   - Clause citations (not "various sections")

3. OPPONENT ANALYSIS
   - Predict PH's specific defence, not generic "they'll argue"
   - Provide detailed rebuttal with evidence
   - Identify what evidence PH lacks

4. STRATEGIC FOCUS
   - Explain how finding helps Lismore win
   - Identify exploitation opportunities
   - Prioritise strongest arguments

5. HONESTY
   - Don't inflate confidence scores
   - Acknowledge uncertainties
   - Mark weak evidence as weak
   - Identify gaps in our case

6. COMPREHENSIVENESS
   - Analyse ALL {len(documents)} documents
   - Cross-reference between documents
   - Build on previous findings
   - Identify patterns across documents
</quality_requirements>

Begin iteration {iteration + 1} analysis now.
Use extended thinking extensively for complex reasoning.
Follow the structured output format EXACTLY as shown in examples.
Be creative. Be adversarial. Win for Lismore.
"""
        
        return prompt
    
    # ========================================================================
    # PASS 3: RECURSIVE INVESTIGATION PROMPT
    # ========================================================================
    
    def investigation_recursive_prompt(self,
                                      investigation,
                                      relevant_documents: List[Dict],
                                      complete_intelligence: Dict) -> str:
        """Pass 3: Recursive investigation with examples"""
        
        prompt = f"""<investigation_mission>
INVESTIGATION: {investigation.topic}
PRIORITY: {investigation.priority}/10

You identified this as requiring deeper investigation.

TRIGGERING CONTEXT:
{json.dumps(investigation.trigger_data, indent=2)[:2000]}

YOUR COMPLETE INTELLIGENCE:
{json.dumps(complete_intelligence, indent=2)[:self.config.token_config['intelligence_context_limit']]}

RELEVANT DOCUMENTS:
{self._format_documents(relevant_documents[:20])}
</investigation_mission>

<adversarial_focus>
Remember: WE ARE ARGUING FOR LISMORE.

For this investigation, determine:
1. How does this help Lismore win?
2. How does this damage PH's case?
3. What novel arguments does this enable?
4. What weaknesses in PH's position does this expose?
</adversarial_focus>

<investigation_framework>
Investigate thoroughly using extended thinking:

1. EVIDENCE ANALYSIS
   - What's the truth here?
   - What additional evidence supports/refutes this?
   - What connections do you see across documents?
   - What patterns emerge?
   - What's the strongest evidence?

2. IMPLICATIONS
   - What does this prove/disprove?
   - How does this fit into the broader case?
   - What legal elements does this establish?
   - What strategic opportunities does this create?

3. OPPONENT ANALYSIS
   - What will PH argue about this?
   - What evidence do they lack?
   - How do we pre-emptively rebut their argument?
   - What weaknesses does this expose?

4. AUTONOMOUS DECISION
   Do you need to investigate further?
   
   If YES - spawn child investigations:
   - What specific sub-topics need investigation?
   - For each child:
     * Topic: [Specific investigation topic]
     * Priority: [1-10]
     * Reason: [Why this needs separate investigation]
   
   If NO - provide final conclusion:
   - Conclusion: [Complete findings]
   - Confidence: [0.0-1.0]
   - Strategic recommendations: [What actions to take]

5. STRATEGIC IMPACT FOR LISMORE
   - How does this strengthen our case?
   - What tribunal arguments does this enable?
   - What cross-examination opportunities?
   - What further evidence should be sought?
</investigation_framework>

<output_requirements>
Provide:

1. INVESTIGATION FINDINGS
   - What you discovered (detailed)
   - Evidence found (cite document IDs)
   - Conclusions reached (with reasoning)
   - Confidence level (0.0-1.0)

2. OPPONENT ANALYSIS
   - PH's likely counter-argument (specific)
   - Our rebuttal strategy (detailed with evidence)
   - Evidence gaps in their defence

3. DECISION: Continue Investigating?
   CONTINUE: [YES or NO]
   
   If YES:
   - List 2-5 child investigations to spawn
   - Each with: Topic, Priority (1-10), Reason
   
   If NO:
   - Final conclusion with all findings
   - Strategic recommendations

4. STRATEGIC IMPACT FOR LISMORE
   - How this affects case strategy
   - Tribunal presentation recommendations
   - Cross-examination opportunities
   - Evidence still needed

You have complete autonomy to decide:
- Whether more investigation needed
- What specific sub-topics to investigate
- When this investigation thread is complete
</output_requirements>

Use extended thinking extensively.
Be creative. Be adversarial. Win for Lismore.
Begin investigation now.
"""
        
        return prompt
    
    # ========================================================================
    # FORMATTING HELPER
    # ========================================================================
    
    def _format_documents(self, documents: List[Dict], doc_type: str = "DISCLOSURE") -> str:
        """Format documents with full content"""
        
        formatted = []
        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            # Use config's document content limit (15K chars)
            content = doc.get('content', '')[:self.config.token_config.get('document_content_per_doc', 15000)]
            
            formatted.append(f"""
[{doc_type}_DOC_{i}]
Filename: {metadata.get('filename', 'unknown')}
Date: {metadata.get('date', 'unknown')}
Source: {metadata.get('source_folder', 'unknown')}
Type: {metadata.get('doc_type', 'unknown')}

FULL CONTENT:
{content}

{'[TRUNCATED - document continues]' if len(doc.get('content', '')) > 15000 else '[END OF DOCUMENT]'}
---
""")
        
        return "\n".join(formatted)