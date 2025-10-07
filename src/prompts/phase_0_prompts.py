#!/usr/bin/env python3
"""
Phase 0 Prompts: Deep Case Understanding with Extended Thinking
British English - Lismore v Process Holdings - Acting for Lismore
"""

from typing import Dict, List
import json 


class Phase0Prompts:
    """Prompts for intelligent case foundation with Extended Thinking"""
    
    def build_stage_1_prompt(self, pleadings_text: str) -> str:
        """
        Stage 1: Deep case understanding through autonomous analysis
        Uses Extended Thinking for complex reasoning
        """
        
        return f"""<phase_0_mission>
You are Lismore's strategic litigation counsel building the foundational case intelligence that will guide £320 of AI-driven document discovery.

CONTEXT:
- Case: Lismore v Process Holdings LCIA arbitration
- Acting for: LISMORE (Respondent)
- Current state: AI will analyse 4,000+ documents BLIND unless you provide context
- Your job: Build deep case understanding so AI can recognise smoking gun documents

CRITICAL: This isn't data extraction. This is litigation strategy.
Use Extended Thinking extensively to REASON through the case.
</phase_0_mission>

<pleadings>
{pleadings_text}
</pleadings>

<analysis_framework>
STAGE 1: UNDERSTAND THE BATTLEFIELD

Use Extended Thinking to deeply analyse these pleadings. Think step-by-step:

1. THE CORE DISPUTE (Deep Understanding)
   
   Don't just summarise. REASON through:
   - What is the fundamental disagreement?
   - What transaction went wrong?
   - What did each party expect vs what happened?
   - Why did this end up in arbitration?
   
   Think like a barrister explaining to a tribunal: What's this case REALLY about?

2. LISMORE'S POSITION (Our Case)
   
   For each allegation:
   - What exactly does Lismore claim PH did wrong?
   - What specific clauses/obligations were breached?
   - What damages/relief is Lismore seeking?
   - What EVIDENCE would prove this? (be specific - dates, doc types, people)
   
   CRITICAL: Think adversarially. For each claim, ask:
   - "What document would make this case unassailable?"
   - "What evidence would the tribunal find most compelling?"

3. PH'S DEFENCE (Opponent Analysis)
   
   For each defence:
   - What's PH's counter-narrative?
   - What facts do they dispute?
   - What legal arguments do they raise?
   - What WEAKNESSES exist in their defence? (missing evidence, contradictions, implausibilities)
   
   Think strategically: 
   - "What evidence are they hoping doesn't exist?"
   - "Where is their case most vulnerable?"

4. DISPUTED CLAUSES & LEGAL TESTS
   
   For each disputed clause:
   - What's the exact wording?
   - What does Lismore say it means?
   - What does PH say it means?
   - What evidence would resolve the dispute?
   - How central is this to the case? (1-10 scale)

5. CRITICAL TIMELINE
   
   Build the timeline that MATTERS:
   - What dates are make-or-break?
   - When did key events occur?
   - What sequence is disputed?
   - What evidence would establish the timeline?
   
   Think about causation chains and proving timing.

6. SMOKING GUN IDENTIFICATION
   
   THIS IS THE MOST IMPORTANT PART.
   
   For each disputed issue, identify documents that would WIN the case:
   
   Example thinking process:
   "If Lismore claims PH knew about X on date Y, the smoking gun would be:
    - Internal PH emails discussing X before date Y
    - Board minutes showing knowledge of X
    - Communications between PH and advisers mentioning X
    - Due diligence materials flagging X as a risk"
   
   Be SPECIFIC:
   - Who would have written the document? (names/roles)
   - When would it have been created? (date range)
   - What keywords/phrases would it contain?
   - What type of document? (email, minutes, memo, report)
   - Why would this document be devastating to PH?
   
   Generate 15-20 smoking gun patterns, prioritised by:
   - How likely the document exists
   - How damaging it would be to PH
   - How provable our case becomes with it

7. KEY ENTITIES (Deep Dive)
   
   Identify critical people/companies/amounts:
   - Who are the key actors? (with roles and importance 1-10)
   - What companies/entities matter?
   - What monetary amounts are in dispute?
   - What contracts/agreements are central?
   
   For each entity, note: Why do they matter? What documents would they appear in?
</analysis_framework>

<critical_instructions>
USE EXTENDED THINKING EXTENSIVELY:

Before answering each section, spend extended thinking reasoning through:
- What does the evidence show?
- What logical inferences can I draw?
- What patterns do I see?
- What would a skilled barrister focus on?
- What documents would change the case?

DO NOT:
- Simply extract text from pleadings
- Summarise without analysis
- Provide generic answers
- Skip the strategic reasoning

DO:
- Think deeply about evidence and proof
- Reason through legal tests and burdens
- Identify specific smoking gun characteristics
- Prioritise by strategic value
- Connect dots across pleadings

BE ADVERSARIAL:
- Every analysis should serve: "How does this help Lismore win?"
- Think like PH's counsel: "What evidence would terrify me?"
- Identify their weaknesses ruthlessly
</critical_instructions>

<output_format>
Respond in structured sections (use headers), but focus on QUALITY not format.

Each section should demonstrate deep thinking, not just extraction.
Use extended thinking heavily before each section.
Be specific with names, dates, amounts, clauses.
Prioritise by strategic importance.

Your output will guide AI to score 4,000+ documents.
Make it count.
</output_format>

Begin your deep analysis now. Use Extended Thinking extensively.
Think like Lismore's lead strategic counsel.
"""

    def build_stage_2_prompt(self, stage_1_summary: Dict, tribunal_text: str) -> str:
        """
        Stage 2: Tribunal signals and strategic priorities
        Uses Extended Thinking to read between the lines
        """
        
        # Extract core dispute for context
        core_dispute = json.dumps(stage_1_summary.get('core_dispute', ''), indent=2)[:500]
        lismore_allegations = json.dumps(stage_1_summary.get('lismore_allegations', []), indent=2)[:800]
        
        return f"""<stage_2_mission>
You've built deep understanding of the case from pleadings (Stage 1).

Now: Read the tribunal's rulings to understand what THEY care about.

CONTEXT:
You represent Lismore. The tribunal has issued rulings on procedural matters.
These rulings contain SIGNALS about what the tribunal thinks matters.

Your job: Read between the lines. What is the tribunal prioritising?
</stage_2_mission>

<stage_1_foundation>
CORE DISPUTE:
{core_dispute}

LISMORE'S KEY ALLEGATIONS:
{lismore_allegations}
</stage_1_foundation>

<tribunal_rulings>
{tribunal_text}
</tribunal_rulings>

<analysis_framework>
STAGE 2: DECODE TRIBUNAL PRIORITIES

Use Extended Thinking to read these rulings strategically:

1. TRIBUNAL SIGNALS (Deep Reading)
   
   Don't just list what they ruled. REASON through:
   - What issues did they spend time on?
   - What language did they use? (skeptical? sympathetic? neutral?)
   - What did they emphasise vs dismiss?
   - What evidence did they request vs deny?
   - What concerns did they express?
   
   For each signal:
   - Quote the specific paragraph
   - Explain what it reveals about tribunal thinking
   - Assess: Does this help Lismore or PH?
   - Strategic implication: How should this shape discovery?

2. EVIDENTIARY PRIORITIES
   
   What evidence has the tribunal indicated matters?
   - What did they order produced?
   - What did they refuse?
   - What materiality thresholds did they articulate?
   - What types of evidence did they find persuasive?
   
   Think: "Based on these rulings, what documents should we prioritise?"

3. PROCEDURAL PATTERNS
   
   Analyse the tribunal's procedural decisions:
   - Did they grant PH's applications or deny them?
   - Did they impose costs?
   - Did they express concern about conduct?
   - Did they fast-track or slow down anything?
   
   Pattern analysis: Is there a lean towards one party?

4. REFINED SMOKING GUN PATTERNS
   
   Based on tribunal signals, REFINE Stage 1 smoking gun patterns:
   - Which patterns now have HIGHER priority? (tribunal cares about this)
   - Which have LOWER priority? (tribunal dismissed this)
   - What NEW patterns emerge from tribunal concerns?
   
   Update the smoking gun list with tribunal priorities.

5. STRATEGIC OPPORTUNITIES
   
   Where has the tribunal opened doors for Lismore?
   - Did they question PH's evidence?
   - Did they express skepticism about PH's arguments?
   - Did they flag gaps in disclosure?
   - Did they impose obligations on PH?
   
   Think: "How can we exploit these signals in document discovery?"
</analysis_framework>

<critical_instructions>
USE EXTENDED THINKING TO:
- Read beyond the literal ruling text
- Identify patterns across multiple rulings
- Reason about tribunal's unspoken concerns
- Connect tribunal signals to smoking gun patterns
- Think strategically about exploitation

FOCUS ON:
- What tribunal emphasised (not what they said in passing)
- Differences in tone when discussing Lismore vs PH
- Evidence gaps the tribunal identified
- Materiality signals
- Procedural advantages/disadvantages

BE SPECIFIC:
- Quote exact paragraphs from rulings
- Cite specific case/document numbers
- Note dates and contexts
- Explain strategic implications
</critical_instructions>

<output_format>
Structure your analysis clearly:

1. TRIBUNAL SIGNALS (5-10 key signals with quotes)
2. EVIDENTIARY PRIORITIES (what tribunal wants to see)
3. PROCEDURAL PATTERNS (lean analysis)
4. UPDATED SMOKING GUN PATTERNS (refined from Stage 1)
5. STRATEGIC OPPORTUNITIES (how to exploit for Lismore)

Focus on INSIGHT not format.
Use extended thinking heavily.
</output_format>

Begin Stage 2 analysis now.
"""

    def build_stage_3_prompt(self, stage_1_summary: Dict, stage_2_summary: Dict, admin_text: str) -> str:
        """
        Stage 3: Final smoking gun synthesis with chronology/dramatis
        Uses Extended Thinking for pattern synthesis
        """
        
        # Get key context
        core = stage_1_summary.get('core_dispute', '')[:300]
        tribunal_signals = stage_2_summary.get('tribunal_signals', [])[:3]
        
        return f"""<stage_3_mission>
FINAL STAGE: Synthesise smoking gun patterns with complete case intelligence.

You've analysed:
✓ Stage 1: Pleadings (core dispute, allegations, defences)
✓ Stage 2: Tribunal rulings (what tribunal cares about)

Now: Integrate chronology + dramatis personae to create ACTIONABLE smoking gun patterns that will guide Pass 1 triage of 4,000+ documents.
</stage_3_mission>

<case_foundation>
CORE DISPUTE (from Stage 1):
{core}

KEY TRIBUNAL SIGNALS (from Stage 2):
{json.dumps(tribunal_signals, indent=2)[:500]}
</case_foundation>

<case_administration>
{admin_text}
</case_administration>

<analysis_framework>
STAGE 3: ACTIONABLE SMOKING GUN SYNTHESIS

Use Extended Thinking to create the final discovery intelligence:

1. KEY ENTITIES & AMOUNTS (Refined)
   
   From chronology + dramatis + pleadings:
   - Who are the 10-15 most critical people? (with roles, importance 1-10)
   - What companies/entities appear repeatedly?
   - What monetary amounts are in dispute? (be precise)
   - What contracts/agreements matter?
   
   For each entity: Why do they matter? What smoking guns would mention them?

2. CRITICAL TIMELINE (Refined)
   
   Build the definitive timeline:
   - Key dates (YYYY-MM-DD format)
   - What happened on each date?
   - Why is this date critical?
   - What evidence would establish/dispute this date?
   
   Identify timeline GAPS: dates where evidence is missing but needed.

3. SMOKING GUN PATTERNS (Final Synthesis)
   
   THIS IS THE DELIVERABLE THAT MATTERS MOST.
   
   Create 20-25 smoking gun patterns that Pass 1 will use to score documents.
   
   For EACH pattern:
   
   A. PATTERN NAME (short, memorable)
      Example: "PH Pre-Deal Knowledge of Taiga Payments"
   
   B. WHAT WE'RE LOOKING FOR
      Specific description of document type and content
      Example: "Internal PH emails/memos discussing Grace Taiga payments before October 2017"
   
   C. DOCUMENT CHARACTERISTICS
      - Date range: When would this document have been created?
      - Key people: Who would have written/received it? (specific names)
      - Keywords/phrases: What words would appear? (specific phrases)
      - Document types: Email, board minutes, memo, report, contract?
      - File types: .msg, .pdf, .docx?
      - Potential folders: Where might it live in disclosure?
   
   D. WHY CRITICAL (Strategic Value)
      - What does this prove/disprove?
      - How does this help Lismore win?
      - How does this destroy PH's defence?
      - What tribunal signal does this address?
   
   E. SCORING GUIDANCE
      - If found, what score (1-10)?
      - Priority level: NUCLEAR (10), CRITICAL (8-9), HIGH (7), MEDIUM (5-6), LOW (3-4)
   
   F. OPPONENT ANALYSIS
      - Would PH try to hide this document?
      - What will PH argue if we find it?
      - How do we pre-emptively rebut?
   
   Example Pattern:
PATTERN: "PH Due Diligence Risk Awareness"
WHAT: Due diligence reports/memos showing PH was warned about corruption risks in P&ID case before investing
CHARACTERISTICS:

Date: August-October 2017 (before Shareholders' Deed)
People: VR Capital analysts, Kobre & Kim lawyers, PH board members
Keywords: "corruption risk", "Taiga", "bribery concerns", "Nigeria investigation", "reputational risk", "enforcement risk"
Doc types: Due diligence reports, legal opinions, board presentations, investment committee memos
Folders: "2- Disclosure", "Due Diligence Materials", "Investment Committee"

WHY CRITICAL:

Destroys PH's "we didn't know" defence
Proves PH had actual knowledge of risks
Defeats Warranty 2.10 breach claim
Tribunal Signal: Tribunal questioned PH's "surprise" at fraud findings

SCORING: 10/10 - NUCLEAR
OPPONENT ANALYSIS:

PH will argue: "These were generic risks, not specific knowledge of Taiga"
Our rebuttal: Specific mentions of Taiga/corruption = actual knowledge, not constructive

   
   Create 20-25 patterns like this. Prioritise by:
   - Likelihood document exists
   - Damage to PH if found
   - Tribunal signals
   - Provability impact

4. DOCUMENT SCORING FRAMEWORK
   
   Create triage guidance for Pass 1:
   
   TIER 1 - NUCLEAR (Score 9-10):
   - Characteristics of documents that win/lose the case
   - Examples of smoking guns
   
   TIER 2 - CRITICAL (Score 7-8):
   - Important contextual documents
   - Strong supporting evidence
   
   TIER 3 - RELEVANT (Score 5-6):
   - Background information
   - Tangential documents
   
   TIER 4 - LOW (Score 1-4):
   - Routine correspondence
   - Minimal relevance
   
   Provide specific guidance for each tier with examples.
</analysis_framework>

<critical_instructions>
USE EXTENDED THINKING TO:
- Synthesise patterns across all 3 stages
- Reason through strategic priorities
- Connect entities to smoking guns
- Think adversarially about opponent weaknesses
- Prioritise patterns by tribunal signals

BE SPECIFIC:
- Exact date ranges
- Named individuals
- Specific keywords/phrases
- Precise monetary amounts
- Detailed document characteristics

FOCUS ON ACTIONABILITY:
- These patterns will guide AI to score 4,000+ documents
- Must be specific enough to recognise smoking guns
- Must be strategic enough to prioritise what matters
- Must be tribunal-aware to match what tribunal cares about

THIS IS THE FINAL DELIVERABLE:
- It must be comprehensive
- It must be actionable
- It must be strategically sound
- It will determine what gets deep analysis in Pass 2
</critical_instructions>

<output_format>
Structure clearly:

1. KEY ENTITIES & AMOUNTS (10-15 entities with details)
2. CRITICAL TIMELINE (15-20 dates with significance)
3. SMOKING GUN PATTERNS (20-25 detailed patterns with ALL fields)
4. DOCUMENT SCORING FRAMEWORK (tier guidance)

Focus on QUALITY and SPECIFICITY.
Use Extended Thinking extensively.
This is the intelligence that drives £320 of AI analysis.
Make it count.
</output_format>

Begin Stage 3 synthesis now.
"""