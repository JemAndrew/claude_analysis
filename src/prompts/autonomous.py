#!/usr/bin/env python3
"""
Autonomous Investigation Prompts for 4-Pass Litigation Analysis
Option 1: Structured output for precise claim construction
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class AutonomousPrompts:
    """Prompts that give Claude complete investigative freedom with structured output"""
    
    def __init__(self, config):
        self.config = config
    
    # ========================================================================
    # PASS 1: TRIAGE PROMPT
    # ========================================================================
    
    def triage_prompt(self, documents: List[Dict]) -> str:
        """
        Pass 1: Quick triage prompt for document prioritisation
        Uses Haiku for fast classification
        """
        
        doc_previews = []
        for i, doc in enumerate(documents):
            preview = doc.get('content', '')[:300]  # First 300 chars
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
    # PASS 2: DEEP ANALYSIS PROMPT (STRUCTURED OUTPUT - OPTION 1)
    # ========================================================================
    
    def deep_analysis_prompt(self, 
                            documents: List[Dict],
                            iteration: int,
                            accumulated_knowledge: Dict,
                            confidence: float) -> str:
        """
        Pass 2: Deep comprehensive analysis prompt with structured output
        Enhanced for Option 1: precise litigation claim construction
        """
        
        prompt = f"""<deep_analysis_mission>
ITERATION: {iteration + 1}
CURRENT CONFIDENCE: {confidence:.2%}
DOCUMENTS TO ANALYSE: {len(documents)}

You are conducting deep litigation analysis for Lismore v Process Holdings.

This is iteration {iteration + 1}. Your accumulated knowledge is below.
Analyse these {len(documents)} documents comprehensively and integrate with your existing understanding.

YOU HAVE COMPLETE AUTONOMY. Use extended thinking to:
- Reason through complex issues
- Challenge your own assumptions
- Make connections across documents
- Build legal arguments iteratively
- Self-assess completeness
</deep_analysis_mission>

<accumulated_knowledge>
{json.dumps(accumulated_knowledge, indent=2)[:20000]}

Timeline events: {len(accumulated_knowledge.get('timeline', []))}
Known breaches: {len(accumulated_knowledge.get('strong_patterns', []))}
Critical contradictions: {len(accumulated_knowledge.get('critical_contradictions', []))}
</accumulated_knowledge>

<analysis_framework>
For EACH document, simultaneously analyse:

LAYER 1: COMMERCIAL FUNDAMENTALS (60% focus)
- Obligations: What duties/promises exist?
- Performance: How did they perform vs obligations?
- Breach: Where did they fail?
- Causation: What losses resulted?
- Quantum: Financial impact?

LAYER 2: EVIDENCE ASSESSMENT (20% focus)
- Quality: Direct? Circumstantial? Hearsay?
- Strength: How compelling for tribunal?
- Gaps: What's missing?
- Links to claims: Which legal claims does this support?

LAYER 3: CROSS-DOCUMENT ANALYSIS (20% focus)
- Timeline: When did events occur? Contradictions with existing timeline?
- Patterns: Systematic behaviour or isolated incidents?
- Entities: Who's involved? Relationships?
- Contradictions: Conflicts with other evidence?

LAYER 4: CLAIM BUILDING (continuous)
As you find evidence, map to claim elements:
- Breach of contract: [evidence]
- Misrepresentation: [evidence]  
- Negligence: [evidence]
Rate each claim's strength (1-10).

LAYER 5: ADVERSARIAL THINKING
- What will they argue?
- Where are we vulnerable?
- What evidence destroys their defence?
</analysis_framework>

<documents_to_analyse>
{self._format_documents(documents)}
</documents_to_analyse>

<structured_output_requirements>
CRITICAL: Use this EXACT format for all findings to enable precise claim construction.

1. BREACHES FOUND (use this format for each breach):

BREACH_START
Description: [Detailed description of the breach]
Clause/Obligation: [Specific clause number or obligation breached]
Evidence: ["DOC_ID_1", "DOC_ID_2"]
Confidence: [0.0-1.0]
Causation: [What loss resulted]
Quantum: [Financial impact if known]
BREACH_END

2. CONTRADICTIONS FOUND (use this format for each contradiction):

CONTRADICTION_START
Statement_A: [First statement]
Statement_B: [Conflicting statement]
Doc_A: [Document ID for first statement]
Doc_B: [Document ID for second statement]
Severity: [1-10]
Confidence: [0.0-1.0]
Implications: [Why this matters for the case]
CONTRADICTION_END

3. TIMELINE EVENTS (use this format for each event):

TIMELINE_EVENT_START
Date: [YYYY-MM-DD or DD/MM/YYYY]
Description: [What happened]
Participants: [Who was involved]
Documents: ["DOC_ID_1", "DOC_ID_2"]
Confidence: [0.0-1.0]
Critical: [YES/NO]
TIMELINE_EVENT_END

4. GENERAL FINDINGS (natural language):
- [Finding 1]
- [Finding 2]
- [Finding 3]

5. CRITICAL FINDINGS REQUIRING INVESTIGATION:
Mark any finding that needs deeper investigation with [CRITICAL] or [NUCLEAR]:

[CRITICAL] Topic requiring investigation
[NUCLEAR] Smoking gun requiring immediate deep dive

6. SELF-ASSESSMENT (CRITICAL - DO NOT SKIP):

CONFIDENCE: [0.00 - 1.00]

Interpretation guide:
- 0.0-0.3: Just starting, need much more information
- 0.4-0.6: Getting clearer but significant gaps remain  
- 0.7-0.9: Strong understanding, minor gaps only
- 0.95-1.0: Complete understanding, confident I can advise

CONTINUE: [YES or NO]

Reasoning: [Why this confidence level? What am I still missing?]

IMPORTANT: You MUST provide a decimal confidence score.
Example: "CONFIDENCE: 0.73" or "CONFIDENCE: 0.42"
</structured_output_requirements>

<quality_requirements>
- Every breach must cite specific document IDs
- Every date must be in recognisable format
- Confidence scores must be decimal (0.0-1.0), not percentages
- Be honest about confidence - don't inflate scores
- If unsure about evidence, mark confidence lower
- Critical findings should be genuinely critical (smoking guns, major contradictions)
</quality_requirements>

Begin iteration {iteration + 1} analysis now.
Use extended thinking for complex reasoning.
Follow the structured output format EXACTLY.
"""
        
        return prompt
    
    # ========================================================================
    # PASS 3: RECURSIVE INVESTIGATION PROMPT
    # ========================================================================
    
    def investigation_recursive_prompt(self,
                                      investigation,
                                      relevant_documents: List[Dict],
                                      complete_intelligence: Dict) -> str:
        """
        Pass 3: Recursive investigation prompt
        Claude decides what to investigate and spawns children
        """
        
        prompt = f"""<investigation_mission>
INVESTIGATION: {investigation.topic}
PRIORITY: {investigation.priority}/10

You identified this as requiring deeper investigation.

TRIGGERING CONTEXT:
{json.dumps(investigation.trigger_data, indent=2)[:2000]}

YOUR COMPLETE INTELLIGENCE:
{json.dumps(complete_intelligence, indent=2)[:20000]}

RELEVANT DOCUMENTS:
{self._format_documents(relevant_documents[:20])}
</investigation_mission>

<investigation_framework>
Investigate thoroughly:

1. ANALYSIS
   - What's the truth here?
   - What additional evidence supports/refutes this?
   - What connections do you see?
   - What implications for the case?

2. AUTONOMOUS DECISION
   Do you need to investigate further?
   
   If YES:
   - What specific sub-investigations should you spawn?
   - For each child investigation:
     * Topic: [specific investigation topic]
     * Priority: [1-10]
     * Reason: [why this needs investigation]
   
   If NO:
   - What's your final conclusion?
   - Confidence level: [0.0-1.0]

3. STRATEGIC IMPACT
   - How does this help Lismore's case?
   - How does this damage Process Holdings' defence?
   - What evidence should be sought?
   - What actions should be taken?
</investigation_framework>

<output_requirements>
Provide:

1. INVESTIGATION FINDINGS
   - What you discovered
   - Evidence found
   - Conclusions reached
   - Confidence level

2. DECISION: Continue Investigating?
   - YES: List child investigations to spawn
   - NO: Provide final conclusion

3. STRATEGIC IMPACT
   - How this affects case strategy
   - What actions to take

You have complete autonomy to decide:
- Whether more investigation needed
- What specific sub-topics to investigate
- When this investigation thread is complete
</output_requirements>

Use extended thinking extensively.
Begin investigation now.
"""
        
        return prompt
    
    # ========================================================================
    # FORMATTING HELPER METHODS
    # ========================================================================
    
    def _format_documents(self, documents: List[Dict], doc_type: str = "DISCLOSURE") -> str:
        """Format documents for prompt inclusion"""
        
        formatted = []
        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            content = doc.get('content', '')[:3000]  # First 3000 chars
            
            formatted.append(f"""
[{doc_type}_DOC_{i}]
Filename: {metadata.get('filename', 'unknown')}
Date: {metadata.get('date', 'unknown')}
Source: {metadata.get('source_folder', 'unknown')}
Content:
{content}
{'...[TRUNCATED]' if len(doc.get('content', '')) > 3000 else ''}
---
""")
        
        return "\n".join(formatted)