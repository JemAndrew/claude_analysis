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
        Pass 1 Triage Prompt WITH PHASE 0 INTELLIGENCE
        Uses strategic patterns from Phase 0 to identify smoking gun documents
        British English throughout - Lismore-sided
        
        Args:
            documents: Batch of documents to triage
            batch_num: Current batch number
            phase_0_foundation: Intelligence from Phase 0 analysis
        
        Returns:
            Complete triage prompt with strategic intelligence
        """
        
        # ================================================================
        # BUILD PHASE 0 INTELLIGENCE SECTION
        # ================================================================
        intelligence_section = ""
        
        if phase_0_foundation and phase_0_foundation.get('document_patterns'):
            patterns = phase_0_foundation.get('document_patterns', [])
            allegations = phase_0_foundation.get('allegations', [])
            defences = phase_0_foundation.get('defences', [])
            key_parties = phase_0_foundation.get('key_parties', [])
            
            # Defensive: ensure lists and convert items to strings
            if not isinstance(patterns, list):
                patterns = []
            if not isinstance(allegations, list):
                allegations = []
            if not isinstance(defences, list):
                defences = []
            if not isinstance(key_parties, list):
                key_parties = []
            
            # Convert all items to strings (in case they're dicts or other types)
            allegations_str = [str(a) for a in allegations[:5] if a]
            defences_str = [str(d) for d in defences[:5] if d]
            key_parties_str = [str(k) for k in key_parties[:10] if k]
            
            intelligence_section = f"""
<phase_0_strategic_intelligence>
🎯 LISMORE'S CASE STRATEGY

You have strategic intelligence from Phase 0 deep case analysis.
Below are smoking gun patterns - specific documents we're hunting for.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY ALLEGATIONS (Lismore's Claims):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            if allegations_str:
                for idx, allegation in enumerate(allegations_str, 1):
                    intelligence_section += f"{idx}. {allegation}\n"
            else:
                intelligence_section += "⚠️ No allegations extracted from Phase 0\n"
            
            intelligence_section += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEIR DEFENCES (What Process Holdings Claims):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            if defences_str:
                for idx, defence in enumerate(defences_str, 1):
                    intelligence_section += f"{idx}. {defence}\n"
            else:
                intelligence_section += "⚠️ No defences extracted from Phase 0\n"
            
            intelligence_section += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY PEOPLE TO WATCH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{', '.join(key_parties_str) if key_parties_str else '⚠️ No key parties extracted'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SMOKING GUN DOCUMENT PATTERNS (Top Priority):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USE THIS INTELLIGENCE TO SCORE DOCUMENTS:
✓ If document matches a pattern below → Use the recommended score
✓ If document contains pattern keywords → Boost score by +2
✓ If document mentions key people → Boost score by +1
✓ If document contradicts their defence → Score 9-10 (smoking gun!)
✓ If routine/irrelevant → Score 1-3

"""
            
            # Filter patterns to only include dictionaries (defensive programming)
            dict_patterns = [p for p in patterns if isinstance(p, dict)]
            
            if not dict_patterns:
                # No valid patterns - create a simple message
                intelligence_section += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOCUMENT PATTERNS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ No structured patterns available from Phase 0.
Performing generic triage based on general relevance to case.

"""
            else:
                # Sort patterns by priority (defensive - use .get() with defaults)
                sorted_patterns = sorted(
                    dict_patterns, 
                    key=lambda p: (
                        p.get('score_if_found', 5) if isinstance(p.get('score_if_found'), (int, float)) else 5,
                        10 if p.get('priority_label') == 'CRITICAL' else 
                        8 if p.get('priority_label') == 'HIGH' else 5
                    ),
                    reverse=True
                )[:15]
                
                for idx, pattern in enumerate(sorted_patterns, 1):
                    # Defensive extraction with defaults
                    name = pattern.get('name', f'Pattern {idx}')
                    if not isinstance(name, str):
                        name = f'Pattern {idx}'
                    
                    description = pattern.get('description', 'No description')
                    if not isinstance(description, str):
                        description = 'No description'
                    
                    characteristics = pattern.get('characteristics', {})
                    if not isinstance(characteristics, dict):
                        characteristics = {}
                    
                    # Extract characteristics safely
                    keywords = characteristics.get('keywords', [])
                    if not isinstance(keywords, list):
                        keywords = []
                    
                    key_people_pattern = characteristics.get('key_people', [])
                    if not isinstance(key_people_pattern, list):
                        key_people_pattern = []
                    
                    doc_types = characteristics.get('doc_types', [])
                    if not isinstance(doc_types, list):
                        doc_types = []
                    
                    priority = pattern.get('priority_label', 'MEDIUM')
                    if not isinstance(priority, str):
                        priority = 'MEDIUM'
                    
                    score_if_found = pattern.get('score_if_found', 7)
                    if not isinstance(score_if_found, (int, float)):
                        score_if_found = 7
                    
                    strategic_value = pattern.get('strategic_value', 'Important evidence')
                    if not isinstance(strategic_value, str):
                        strategic_value = 'Important evidence'
                    
                    # Priority emoji
                    priority_emoji = "🔴" if priority == "CRITICAL" else "🟠" if priority == "HIGH" else "🟡"
                    
                    intelligence_section += f"""
{idx}. {priority_emoji} {name.upper()} [{priority} PRIORITY]
   What to look for: {description[:250]}
   Keywords: {', '.join(str(k) for k in keywords[:10]) if keywords else 'Any relevant terms'}
   Key people: {', '.join(str(k) for k in key_people_pattern[:5]) if key_people_pattern else 'Any'}
   Document types: {', '.join(str(d) for d in doc_types[:5]) if doc_types else 'Any'}
   
   ➜ If found → Score: {score_if_found}/10
   ➜ Strategic value: {strategic_value[:200]}

"""
            
            intelligence_section += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCORING STRATEGY:
• Documents matching 🔴 CRITICAL patterns → 9-10
• Documents matching 🟠 HIGH patterns → 7-8
• Documents with multiple pattern matches → +2 bonus
• Documents contradicting their defences → Automatic 9-10
• Documents supporting our allegations → 8-10
• Generic background material → 3-5
• Irrelevant documents → 1-2

</phase_0_strategic_intelligence>

"""
        else:
            # No Phase 0 intelligence available
            intelligence_section = """
<no_strategic_intelligence>
⚠️ Phase 0 analysis not available - performing generic triage.
💡 Run 'python main.py phase0' first for optimised triage using strategic patterns.
</no_strategic_intelligence>

"""
        
        # ================================================================
        # BUILD DOCUMENT PREVIEW SECTION
        # ================================================================
        doc_preview = "<documents_to_triage>\n"
        
        for idx, doc in enumerate(documents):
            filename = doc.get('filename', 'Unknown')
            folder = doc.get('folder_name', 'Unknown')
            preview = doc.get('preview', 'No preview available')[:400]
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
        # BUILD COMPLETE PROMPT
        # ================================================================
        prompt = f"""<triage_mission>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTELLIGENT DOCUMENT TRIAGE - Batch {batch_num + 1}
Lismore v Process Holdings LCIA Arbitration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ YOU ARE ACTING FOR LISMORE (THE CLAIMANT)

Your mission: Triage {len(documents)} documents to identify high-priority evidence.

🎯 WHAT LISMORE NEEDS TO WIN:
1. Evidence of Process Holdings' misrepresentations/breaches
2. Documents contradicting their defences
3. Evidence of undisclosed liabilities
4. Proof of causation (breach → damages)
5. Documents establishing quantum of loss
6. Timeline evidence showing when breaches occurred
7. Internal PH communications showing knowledge/intent
8. Expert/valuation documents supporting claims

</triage_mission>

{intelligence_section}

{doc_preview}

<scoring_rubric>
Score each document 1-10 based on evidential value to Lismore's case:

10 = SMOKING GUN - Directly proves breach/misrepresentation with specific evidence
9  = CRITICAL - Strong evidence supporting key claim elements
8  = HIGH VALUE - Important corroborating evidence
7  = RELEVANT - Useful supporting evidence
6  = MODERATELY USEFUL - Background context that may matter
5  = NEUTRAL - Generic business documents
4  = TANGENTIAL - Minimally relevant
3  = ADMINISTRATIVE - Routine business matter
2  = IRRELEVANT - No connection to case
1  = NOISE - Complete waste of time

CATEGORY TAGS (assign one):
- contract: SPAs, agreements, warranties, indemnities
- financial: Accounts, valuations, liabilities, management accounts
- correspondence: Emails, letters between parties
- witness: Documents authored by/mentioning key witnesses
- expert: Valuation reports, expert opinions
- other: Everything else
</scoring_rubric>

<output_format>
For each document, provide:

[DOC_0]
Priority Score: [1-10]
Reason: [2-3 sentences explaining score using specific details from preview]
Category: [contract/financial/correspondence/witness/expert/other]

[DOC_1]
Priority Score: [1-10]
Reason: [2-3 sentences explaining score using specific details from preview]
Category: [contract/financial/correspondence/witness/expert/other]

Continue for ALL {len(documents)} documents.
</output_format>

<quality_requirements>
1. Read EVERY document preview carefully
2. Use Phase 0 intelligence to identify smoking guns
3. Be consistent in scoring
4. Justify scores with specific evidence
5. Consider strategic value to Lismore's case
</quality_requirements>

Begin triage now. Be thorough. Win for Lismore.
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