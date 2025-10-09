#!/usr/bin/env python3
"""
COMPLETE Autonomous Prompts - Ready for Folder 69 Deep Dive
Includes: weaponised prompts + late disclosure forensics + triage
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class AutonomousPrompts:
    """Prompts optimised for autonomous discovery with extended thinking"""
    
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
        Pass 1 Triage - keep your existing version or use this basic one
        """
        
        # Build Phase 0 intelligence section
        intelligence_section = ""
        if phase_0_foundation:
            allegations = phase_0_foundation.get('allegations', [])[:5]
            defences = phase_0_foundation.get('defences', [])[:5]
            patterns = phase_0_foundation.get('document_patterns', [])[:10]
            
            intelligence_section = f"""
<phase_0_intelligence>
KEY ALLEGATIONS: {', '.join(str(a) for a in allegations)}
PHL DEFENCES: {', '.join(str(d) for d in defences)}
SMOKING GUN PATTERNS: {len(patterns)} patterns to look for
</phase_0_intelligence>
"""
        
        # Format documents
        doc_previews = []
        for i, doc in enumerate(documents):
            preview = doc.get('content', '')[:300]
            filename = doc.get('metadata', {}).get('filename', 'unknown')
            doc_previews.append(f"[DOC_{i}]\nFilename: {filename}\nPreview: {preview}...")
        
        docs_section = "\n\n".join(doc_previews)
        
        prompt = f"""
You are triaging documents for Lismore v Process Holdings arbitration.

{intelligence_section}

DOCUMENTS TO SCORE (1-10):
{docs_section}

For each document, provide:
[DOC_X]
Priority Score: [1-10]
Reason: [Why this score]
Category: [contract/financial/correspondence/witness/expert/other]

Score 9-10: Smoking guns, breaches, contradictions
Score 7-8: Important context, key parties
Score 4-6: Background information
Score 1-3: Irrelevant

Begin triage now.
"""
        return prompt
    
    # ========================================================================
    # PASS 2: WEAPONISED DEEP ANALYSIS (WITH LATE DISCLOSURE)
    # ========================================================================
    
    def deep_analysis_prompt(self,
                            documents: List[Dict],
                            iteration: int,
                            accumulated_knowledge: Dict,
                            confidence: float,
                            phase_instruction: str) -> str:
        """
        WEAPONISED Pass 2 with Late Disclosure Forensics
        """
        
        # Load Phase 0 context
        phase_0_context = self._load_phase_0_context()
        
        # Check if this is late disclosure mode
        late_disclosure_section = ""
        if hasattr(self.config, 'focus_mode') and self.config.focus_mode == 'late_disclosure_forensics':
            late_disclosure_section = """
<late_disclosure_forensics>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 LATE DISCLOSURE FORENSIC ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL CONTEXT: These documents are from PHL's LATE DISCLOSURE (April 2025).
PHL initially WITHHELD these documents. They disclosed under pressure.

YOUR FORENSIC MISSION:

1. WHY DID THEY HIDE THIS INITIALLY?
   - What does this document expose about their position?
   - What risk does this create for their defence?
   - What does the content reveal about their concealment strategy?

2. WHAT FORCED THEM TO DISCLOSE?
   - Tribunal order?
   - Specific document request from Lismore?
   - Fear of spoliation sanctions?
   - Adverse inference risk?

3. WHAT DOES THIS TIMING PROVE?
   - Document created: [date from metadata]
   - Withheld until: April 2025
   - Why the delay? What changed?

4. EVIDENCE OF KNOWLEDGE:
   - Timeline of when PHL actually knew X
   - Contradicts their claims of "we didn't know until..."
   - Shows earlier awareness than admitted

5. CONTRADICTIONS WITH THEIR POSITION:
   - What do these docs say vs what PHL claims in pleadings?
   - What do these docs say vs what witnesses swore to?
   - What timeline inconsistencies?

6. MISSING DOCUMENTS (SPOLIATION CASE):
   - What documents are referenced but not disclosed?
   - Incomplete email threads (missing replies/attachments)?
   - Suspicious gaps in paper trail?
   - Documents that MUST exist but aren't here?

7. FORENSIC INDICATORS TO EXAMINE:
   - Metadata: Creation date, modification date, author
   - Recipients: Who was included/excluded from distribution?
   - Subject matter: Topics they claim ignorance about
   - Redactions: What's blacked out and why?
   - Version control: Is this v1, v2, final? Where are earlier versions?

8. BUILD THE CONCEALMENT CASE:
   For each smoking gun, identify:
   - Document X was withheld because...
   - It proves Y (specific fact)
   - Which destroys PHL's defence that Z
   - Creating adverse inference: Court should infer...

ADVERSE INFERENCE FRAMEWORK:
"PHL withheld [DOC_ID] until April 2025 because it proves [X], 
which contradicts their defence that [Y]. The tribunal should infer 
that [Z] based on this late disclosure pattern."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIND THE SMOKING GUNS THEY TRIED TO HIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</late_disclosure_forensics>
"""
        
        # [REST OF YOUR EXISTING deep_analysis_prompt CODE]
        # Just insert late_disclosure_section after phase_0_context
        
        doc_section = self._format_documents(documents, "PRIORITY")
        knowledge_summary = f"""
<accumulated_intelligence>
Breaches Found: {len(accumulated_knowledge.get('patterns', []))}
Contradictions Found: {len(accumulated_knowledge.get('contradictions', []))}
Current Confidence: {confidence:.1%}

PREVIOUS FINDINGS: {json.dumps(accumulated_knowledge, indent=2)[:5000]}
</accumulated_intelligence>
"""
        
        # Iteration focus (keep your existing code)
        if iteration == 0:
            iteration_focus = """
<iteration_1_focus>
ITERATION 1: EVIDENCE MAPPING & SMOKING GUNS
Find specific documentary evidence for each allegation.
Discover contradictions. Identify document withholding patterns.
</iteration_1_focus>
"""
        elif iteration < 5:
            iteration_focus = """
<iterations_2_5_focus>
PHASE: CROSS-DOCUMENT PATTERN ANALYSIS
Build evidence chains across 3+ documents.
Timeline analysis. Witness credibility attacks.
</iterations_2_5_focus>
"""
        elif iteration < 10:
            iteration_focus = """
<iterations_6_10_focus>
PHASE: NOVEL ARGUMENT CONSTRUCTION
Discover novel legal arguments. Expose opponent weaknesses.
Settlement pressure points. Tribunal presentation strategy.
</iterations_6_10_focus>
"""
        else:
            iteration_focus = """
<iterations_11_plus_focus>
PHASE: DEEP INVESTIGATION & KILL SHOTS
Find nuclear evidence. Fraud indicators.
Tribunal win conditions. Spoliation case.
</iterations_11_plus_focus>
"""
        
        prompt = f"""<extended_thinking_mission>
PASS 2: DEEP ANALYSIS - Iteration {iteration + 1}
Lismore v Process Holdings LCIA Arbitration

⚖️ YOU ARE ACTING FOR LISMORE
You have 12,000 tokens of extended thinking. USE IT ALL.
Current Confidence: {confidence:.1%} | Target: 95%
</extended_thinking_mission>

{phase_0_context}

{late_disclosure_section}

{knowledge_summary}

{iteration_focus}

{doc_section}

<extended_thinking_instructions>
BEFORE writing your analysis, use thinking space to:
1. READ ALL DOCUMENTS THOROUGHLY
2. CROSS-REFERENCE DOCUMENTS
3. BUILD EVIDENCE CHAINS
4. IDENTIFY CONTRADICTIONS
5. ASSESS CONFIDENCE
6. GENERATE NOVEL ARGUMENTS
</extended_thinking_instructions>

<hallucination_prevention>
🚨 CRITICAL RULES:
1. CITE SPECIFIC DOC_IDs for every claim
2. QUOTE ACCURATELY - verbatim only
3. NO SPECULATION - distinguish facts from inferences
4. ACKNOWLEDGE UNCERTAINTY
5. NO EXTERNAL KNOWLEDGE
</hallucination_prevention>

<structured_output_requirements>
[YOUR EXISTING STRUCTURED OUTPUT FORMAT - KEEP IT ALL]

BREACH_START...BREACH_END
CONTRADICTION_START...CONTRADICTION_END
TIMELINE_EVENT_START...TIMELINE_EVENT_END
NOVEL_ARGUMENT_START...NOVEL_ARGUMENT_END
WEAKNESS_START...WEAKNESS_END
INVESTIGATION_START...INVESTIGATION_END
CONFIDENCE_START...CONFIDENCE_END
</structured_output_requirements>

Begin your extended thinking analysis now.
"""
        
        return prompt
    
    # ========================================================================
    # PASS 3: WEAPONISED INVESTIGATION (KEEP YOUR EXISTING VERSION)
    # ========================================================================
    
    def investigation_recursive_prompt(self,
                                      investigation,
                                      relevant_documents: List[Dict],
                                      complete_intelligence: Dict) -> str:
        """
        Keep your existing investigation prompt - it's already excellent
        """
        # [KEEP YOUR ENTIRE EXISTING INVESTIGATION PROMPT]
        pass
    
    # ========================================================================
    # HELPER METHODS (KEEP YOUR EXISTING VERSIONS)
    # ========================================================================
    
    def _load_phase_0_context(self) -> str:
        """Load Phase 0 allegations as context"""
        try:
            phase_0_file = self.config.analysis_dir / "phase_0" / "case_foundation.json"
            if not phase_0_file.exists():
                return "<no_phase_0>Phase 0 not available</no_phase_0>"
            
            with open(phase_0_file, 'r', encoding='utf-8') as f:
                phase_0 = json.load(f)
            
            allegations = phase_0.get('allegations', [])[:10]
            defences = phase_0.get('defences', [])[:10]
            
            context = """
<phase_0_strategic_context>
KNOWN ALLEGATIONS FROM PHASE 0:
"""
            for i, allegation in enumerate(allegations, 1):
                context += f"{i}. {allegation}\n"
            
            context += "\nPHL'S KNOWN DEFENCES:\n"
            for i, defence in enumerate(defences, 1):
                context += f"{i}. {defence}\n"
            
            context += """
DON'T RESTATE THESE - FIND THE SMOKING GUN EVIDENCE
</phase_0_strategic_context>
"""
            return context
        except Exception as e:
            return f"<phase_0_error>{e}</phase_0_error>"
    
    def _format_documents(self, documents: List[Dict], doc_type: str = "DISCLOSURE") -> str:
        """Format documents for analysis"""
        if not documents:
            return "<no_documents>No documents provided</no_documents>"
        
        formatted = []
        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            content_limit = self.config.token_config.get('document_content_per_doc', 15000)
            content = doc.get('content', '')[:content_limit]
            
            formatted.append(f"""
[{doc_type}_DOC_{i}]
Filename: {metadata.get('filename', 'unknown')}
Date: {metadata.get('date', 'unknown')}

FULL CONTENT:
{content}
{'[TRUNCATED]' if len(doc.get('content', '')) > content_limit else '[END]'}
""")
        
        return "\n".join(formatted)