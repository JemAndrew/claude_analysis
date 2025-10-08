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
    


    def triage_prompt(self, 
                    documents: List[Dict], 
                    batch_num: int = 0,
                    phase_0_foundation: Dict = None) -> str:
        """
        ENHANCED Pass 1 Triage Prompt
        Extracts: Score, Category, Entities, Dates, Topics, Summary, Relevance, Red Flags
        
        Cost increase: ~3-4x output tokens (£50 → £170 for 20K docs)
        Search quality: 3/10 → 8/10
        """
        
        # ================================================================
        # BUILD PHASE 0 INTELLIGENCE SECTION (same as before)
        # ================================================================
        intelligence_section = ""
        
        if phase_0_foundation and phase_0_foundation.get('document_patterns'):
            patterns = phase_0_foundation.get('document_patterns', [])
            allegations = phase_0_foundation.get('allegations', [])
            defences = phase_0_foundation.get('defences', [])
            key_parties = phase_0_foundation.get('key_parties', [])
            
            # Defensive handling
            if not isinstance(patterns, list):
                patterns = []
            if not isinstance(allegations, list):
                allegations = []
            if not isinstance(defences, list):
                defences = []
            if not isinstance(key_parties, list):
                key_parties = []
            
            allegations_str = [str(a) for a in allegations[:5] if a]
            defences_str = [str(d) for d in defences[:5] if d]
            key_parties_str = [str(k) for k in key_parties[:10] if k]
            
            intelligence_section = f"""
    <phase_0_strategic_intelligence>
    🎯 LISMORE'S CASE STRATEGY

    KEY ALLEGATIONS (use these for Relevance field):
    {chr(10).join(f'{i+1}. {a}' for i, a in enumerate(allegations_str)) if allegations_str else 'None loaded'}

    PHL'S DEFENCES (flag documents contradicting these):
    {chr(10).join(f'{i+1}. {d}' for i, d in enumerate(defences_str)) if defences_str else 'None loaded'}

    KEY PARTIES (extract these in Key Entities):
    {', '.join(key_parties_str) if key_parties_str else 'None loaded'}

    SMOKING GUN PATTERNS (if found, score 9-10):
    """
            
            # Add smoking gun patterns (top 10)
            dict_patterns = [p for p in patterns if isinstance(p, dict)]
            if not dict_patterns:
                intelligence_section += """
    No smoking gun patterns loaded - performing generic triage.
    """
            else:
                sorted_patterns = sorted(
                    dict_patterns,
                    key=lambda p: (
                        p.get('score_if_found', 5),
                        10 if p.get('priority_label') == 'CRITICAL' else 5
                    ),
                    reverse=True
                )[:10]
                
                for idx, pattern in enumerate(sorted_patterns, 1):
                    name = pattern.get('name', f'Pattern {idx}')
                    description = pattern.get('description', '')
                    
                    intelligence_section += f"{idx}. {name}: {description[:100]}\n"
            
            intelligence_section += "\n</phase_0_strategic_intelligence>\n\n"
        else:
            intelligence_section = """
    <no_strategic_intelligence>
    ⚠️ Phase 0 not available - performing generic triage.
    </no_strategic_intelligence>

    """
        
        # ================================================================
        # BUILD DOCUMENT PREVIEW SECTION
        # ================================================================
        doc_preview = "<documents_to_triage>\n"
        
        for idx, doc in enumerate(documents):
            filename = doc.get('filename', 'Unknown')
            folder = doc.get('folder_name', 'Unknown')
            preview = doc.get('preview', 'No preview')[:400]
            file_type = doc.get('file_type', 'unknown')
            
            doc_preview += f"""
    [DOC_{idx}]
    Filename: {filename}
    Folder: {folder}
    File type: {file_type}
    Preview:
    {preview}
    ---

    """
        
        doc_preview += "</documents_to_triage>\n\n"
        
        # ================================================================
        # BUILD ENHANCED PROMPT WITH RICH METADATA EXTRACTION
        # ================================================================
        prompt = f"""<enhanced_triage_mission>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ENHANCED INTELLIGENT DOCUMENT TRIAGE - Batch {batch_num + 1}
    Lismore v Process Holdings LCIA Arbitration
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ⚖️ YOU ARE ACTING FOR LISMORE (THE CLAIMANT)

    Your mission: Triage {len(documents)} documents AND extract rich metadata for future search.

    🎯 EXTRACTION REQUIREMENTS:
    For EACH document, you must extract:
    1. Priority Score (1-10) - Evidential value
    2. Category - Document type
    3. Key Entities - People, companies, locations mentioned
    4. Key Dates - Dates mentioned in the document
    5. Key Topics - Main themes/subjects
    6. Summary - 50-100 word overview
    7. Relevance - Which allegations/defences it relates to
    8. Red Flags - Suspicious/concealment indicators (if any)
    9. Reason - Brief justification of score

    This enhanced metadata enables powerful search capabilities later.

    </enhanced_triage_mission>

    {intelligence_section}

    {doc_preview}

    <scoring_rubric>
    Score 1-10 based on evidential value to Lismore:

    10 = SMOKING GUN - Direct proof of breach with specific evidence
    9  = CRITICAL - Strong evidence supporting key claims
    8  = HIGH VALUE - Important corroborating evidence
    7  = RELEVANT - Useful supporting evidence
    6  = MODERATELY USEFUL - Background context
    5  = NEUTRAL - Generic business documents
    4  = TANGENTIAL - Minimally relevant
    3  = ADMINISTRATIVE - Routine business
    2  = IRRELEVANT - No case connection
    1  = NOISE - Waste of time
    </scoring_rubric>

    <category_tags>
    Assign ONE category:
    - contract: SPAs, agreements, warranties, indemnities
    - financial: Accounts, valuations, liabilities, management accounts
    - correspondence: Emails, letters between parties
    - witness: Documents authored by/mentioning key witnesses  
    - expert: Valuation reports, expert opinions
    - other: Everything else
    </category_tags>

    <extraction_guidelines>
    **Key Entities:** Extract ALL mentioned:
    • People: Full names (e.g., "Brendan Cahill", "Grace Taiga")
    • Companies: Full entity names (e.g., "Process Holdings Limited", "Lismore Capital")
    • Locations: Cities, offices (e.g., "Lagos Office", "London", "Nigeria")
    • Max 4-6 entities per document

    **Key Dates:** Extract ALL dates in format DD/MM/YYYY or Month YYYY:
    • Transaction dates
    • Meeting dates
    • Correspondence dates
    • Deadline dates
    • Max 3-5 dates per document

    **Key Topics:** Extract 2-4 main themes:
    • payment discrepancies, audit concerns, warranty breaches
    • disclosure obligations, shareholder reporting, regulatory compliance
    • valuation disputes, liability concealment, etc.

    **Summary:** 50-100 words covering:
    • What type of document (email, memo, report, etc.)
    • Who is involved
    • What it discusses
    • Why it matters to the case

    **Relevance:** Match to allegations/defences from Phase 0:
    • "Allegation #3 (failure to disclose)"
    • "Defence #4 (good faith dealing)"
    • "Contradiction to PHL's timeline"
    • "None" if not relevant

    **Red Flags:** Note if document shows:
    • Concealment language ("don't disclose", "keep internal", "off the record")
    • Contradictions to official statements
    • Knowledge of issues before claimed dates
    • Attempts to mislead
    • "None" if clean
    </extraction_guidelines>

    <enhanced_output_format>
    For EACH document, provide ALL fields in this exact format:

    [DOC_0]
    Priority Score: 8
    Category: correspondence
    Key Entities: Brendan Cahill, Grace Taiga, Lagos Office, PHL Board
    Key Dates: 15/03/2014, 22/03/2014
    Key Topics: payment discrepancies, audit concerns, disclosure obligations, regulatory reporting
    Summary: Email thread between Cahill (PHL CFO) and Taiga (Lagos Office Manager) discussing irregularities discovered in 2013 financial audit that were not disclosed in shareholder reports. Cahill acknowledges awareness of £1.8M liability omission and discusses strategies to avoid regulatory scrutiny. References prior discussions about "keeping this matter internal" until post-acquisition.
    Relevance: Allegation #3 (failure to disclose liabilities), Allegation #7 (misleading audit representation), Contradicts Defence #2 (claimed ignorance until 2015)
    Red Flags: Concealment language ("keep this internal", "don't include in shareholder report"), shows knowledge two years before PHL claims
    Reason: Strong evidence of deliberate non-disclosure with knowledge and intent, directly contradicts PHL's defence timeline

    [DOC_1]
    Priority Score: 5
    Category: financial
    Key Entities: KPMG, Process Holdings Limited
    Key Dates: 31/12/2012
    Key Topics: annual accounts, standard financial reporting
    Summary: Standard audited accounts for year ending 31 December 2012 prepared by KPMG. Contains routine financial statements with standard audit opinion. No obvious irregularities or disclosures relevant to disputed liabilities. Generic financial reporting document without contentious elements.
    Relevance: None - predates key events
    Red Flags: None
    Reason: Generic financial document from period before dispute arose, minimal evidential value

    [DOC_2]
    Priority Score: 10
    Category: witness
    Key Entities: Simon Odumosu, Grace Taiga, Lagos Project, Bribery allegations
    Key Dates: 08/2014, 03/2015
    Key Topics: bribery allegations, government payments, undisclosed liabilities, concealment
    Summary: Internal memo from Simon Odumosu (PHL Legal Counsel) to senior management explicitly discussing allegations of improper payments to Nigerian government officials in connection with Lagos Project. Memo states "these allegations were known to us by August 2014 but we decided not to disclose during acquisition negotiations as they were unsubstantiated". Confirms £3.2M in questionable payments and recommends settlement before disclosure.
    Relevance: Allegation #1 (undisclosed bribery liabilities), Allegation #3 (failure to disclose), Allegation #5 (misrepresentation of legal compliance), Contradicts Defence #1 (no knowledge of liabilities)
    Red Flags: SMOKING GUN - Explicit admission of knowledge and deliberate non-disclosure decision, shows intent to conceal material liabilities during acquisition
    Reason: Nuclear evidence - written admission from PHL's own legal counsel of knowing concealment of £3.2M liability during acquisition negotiations, destroys their primary defence

    Continue for ALL {len(documents)} documents.

    CRITICAL: You MUST extract ALL fields for EVERY document. Do not skip any fields.
    </enhanced_output_format>

    <quality_requirements>
    1. Read EVERY document preview thoroughly
    2. Extract entities, dates, and topics precisely from the text
    3. Write clear, detailed summaries (50-100 words)
    4. Match relevance to Phase 0 allegations/defences
    5. Flag suspicious language/concealment attempts
    6. Be consistent in scoring
    7. Justify high scores (8-10) with specific evidence
    </quality_requirements>

    Begin enhanced triage now. Extract ALL metadata fields for ALL documents.
    Win for Lismore.
    """
        
        return prompt
    
    # ========================================================================
    # PASS 2: DEEP ANALYSIS PROMPT
    # ========================================================================
    
    def deep_analysis_prompt(self,
                            documents: List[Dict],
                            iteration: int,
                            accumulated_knowledge: Dict,
                            confidence: float,
                            phase_instruction: str) -> str:
        """
        Pass 2: Deep analysis with structured output
        British English throughout - Lismore-sided
        """
        
        # Format documents
        doc_section = self._format_documents(documents, "PRIORITY")
        
        # Format accumulated knowledge
        knowledge_summary = f"""
<accumulated_intelligence>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KNOWLEDGE FROM PREVIOUS ITERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patterns Found: {len(accumulated_knowledge.get('patterns', []))}
Contradictions: {len(accumulated_knowledge.get('contradictions', []))}
Timeline Events: {len(accumulated_knowledge.get('timeline', []))}
Current Confidence: {confidence:.1%}

PREVIOUS FINDINGS SUMMARY:
{json.dumps(accumulated_knowledge, indent=2)[:5000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUILD ON THESE FINDINGS - DON'T REPEAT THEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</accumulated_intelligence>
"""
        
        prompt = f"""<deep_analysis_mission>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASS 2: DEEP ANALYSIS - Iteration {iteration + 1}
Lismore v Process Holdings LCIA Arbitration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ YOU ARE ACTING FOR LISMORE (THE CLAIMANT)

{phase_instruction}

Current Confidence: {confidence:.1%}
Target: 95% confidence to stop iterations

</deep_analysis_mission>

{knowledge_summary}

{doc_section}

<analysis_framework>
Use extended thinking to analyse deeply:

1. IDENTIFY BREACHES
   - What obligations were breached?
   - What's the evidence? (cite specific DOC_IDs)
   - What's the causation chain?
   - What's the quantum of loss?
   - What will PH argue? How do we rebut?

2. FIND CONTRADICTIONS
   - What conflicts exist between documents?
   - What undermines PH's defence?
   - What timeline impossibilities exist?
   - What cross-examination opportunities?

3. BUILD TIMELINE
   - What happened when?
   - Who knew what, when?
   - What's the sequence of events?
   - What timeline problems exist?

4. DEVELOP NOVEL ARGUMENTS
   - What connections haven't been made?
   - What creative legal arguments exist?
   - What strategic opportunities?

5. ATTACK OPPONENT'S WEAKNESSES
   - What evidence do they lack?
   - What inconsistencies in their position?
   - What questions they can't answer?
</analysis_framework>

<structured_output_requirements>
Use EXACT format below:

1. BREACHES FOUND:

BREACH_START
Description: [Detailed breach with specifics]
Clause/Obligation: [Exact citation]
Evidence: ["DOC_123", "DOC_456"]
Confidence: [0.00-1.00]
Causation: [How breach caused loss]
Quantum: [£X amount with breakdown]
PH_Counter_Argument: [What they'll say]
Our_Rebuttal: [Why they're wrong]
BREACH_END

2. CONTRADICTIONS FOUND:

CONTRADICTION_START
Statement_A: [Exact quote]
Statement_B: [Exact quote]
Doc_A: [DOC_ID]
Doc_B: [DOC_ID]
Severity: [1-10]
Confidence: [0.0-1.0]
Implications: [What this proves]
Cross_Examination_Potential: [Questions to ask]
CONTRADICTION_END

3. TIMELINE EVENTS:

TIMELINE_EVENT_START
Date: [YYYY-MM-DD]
Description: [What happened]
Participants: [Named individuals]
Documents: ["DOC_ID"]
Confidence: [0.0-1.0]
Critical: [YES/NO]
Impossibilities: [Timeline contradictions]
TIMELINE_EVENT_END

4. NOVEL ARGUMENTS:

NOVEL_ARGUMENT_START
Argument: [Complete argument]
Supporting_Evidence: ["DOC_ID"]
Strategic_Value: [Impact]
Strength: [HIGH/MEDIUM/LOW]
Risks: [Downsides]
NOVEL_ARGUMENT_END

5. OPPONENT WEAKNESSES:

WEAKNESS_START
PH_Position: [What they claim]
Our_Attack: [How we exploit]
Evidence_Gap: [What they lack]
Cross_Examination: [Questions]
WEAKNESS_END

6. CONFIDENCE ASSESSMENT:

CONFIDENCE_START
Current_Level: [0.00-1.00]
Reasoning: [Why this confidence]
Missing_Evidence: [What would increase confidence]
Ready_To_Stop: [YES/NO - stop if ≥0.95]
CONFIDENCE_END

7. INVESTIGATION SPAWNING:

If you identify topics needing deeper investigation:

INVESTIGATION_START
Topic: [Specific investigation topic]
Priority: [1-10]
Trigger: [What triggered this]
Expected_Findings: [What you expect to find]
INVESTIGATION_END

</structured_output_requirements>

<quality_requirements>
1. SPECIFICITY
   - Name amounts, dates, people, clauses
   - Cite specific DOC_IDs
   - Quote key passages
   - No vague statements

2. ADVERSARIAL THINKING
   - Always consider PH's counter
   - Pre-emptively rebut their defence
   - Identify evidence gaps in their position
   - Think like their barrister

3. STRATEGIC VALUE
   - How does this help Lismore win?
   - What tribunal arguments does this enable?
   - What's the cross-examination value?

4. CONFIDENCE CALIBRATION
   - Be honest about confidence
   - Identify what would increase it
   - Stop when ≥95% confident

5. COMPREHENSIVENESS
   - Analyse ALL documents
   - Cross-reference findings
   - Build on previous iterations

</quality_requirements>

Begin iteration {iteration + 1} analysis now.
Use extended thinking extensively.
Follow structured format EXACTLY.
Be creative. Be adversarial. Win for Lismore.
"""
        
        return prompt
    
    # ========================================================================
    # PASS 3: INVESTIGATION PROMPT
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