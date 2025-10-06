#!/usr/bin/env python3
"""
Autonomous Investigation Prompts for 4-Pass Litigation Analysis
Optimised for Lismore v Process Holdings litigation intelligence
British English throughout
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class AutonomousPrompts:
    """Prompts that give Claude complete investigative freedom"""
    
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

Be decisive. Err on side of higher priority if uncertain.
</scoring>

Score all {len(documents)} documents now.
"""
        
        return prompt
    
    # ========================================================================
    # PASS 2: DEEP ANALYSIS PROMPT
    # ========================================================================
    
    def deep_analysis_prompt(self, 
                            documents: List[Dict],
                            iteration: int,
                            accumulated_knowledge: Dict,
                            confidence: float) -> str:
        """
        Pass 2: Deep comprehensive analysis prompt
        Uses Sonnet with extended thinking
        Includes confidence tracking and self-assessment
        """
        
        prompt = f"""<deep_analysis_mission>
ITERATION: {iteration + 1}
CURRENT CONFIDENCE: {confidence:.2%}
DOCUMENTS TO ANALYSE: {len(documents)}

You are conducting deep litigation analysis for a commercial dispute.

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
Breaches identified: {len(accumulated_knowledge.get('breaches', []))}
Evidence pieces: {len(accumulated_knowledge.get('evidence', []))}
Patterns detected: {len(accumulated_knowledge.get('patterns', []))}
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

<output_requirements>
Provide:

1. FINDINGS THIS ITERATION
   - New timeline events discovered
   - New breaches identified
   - New evidence found
   - Patterns detected
   - Mark critical findings: [CRITICAL] or [NUCLEAR]

2. CLAIM STATUS
   For each claim:
   - Elements proven vs needed
   - Evidence strength (1-10)
   - Gaps in proof

3. INVESTIGATION TRIGGERS
   If you found anything requiring deeper investigation:
   - Topic to investigate
   - Why critical
   - Priority (1-10)

4. SELF-ASSESSMENT (CRITICAL)
   - Confidence in completeness: 0.0-1.0
   - What am I still missing?
   - What's unclear?
   - Should analysis continue? YES/NO + reasoning
   
   Be HONEST. If only 60% confident, say so.
   Don't claim high confidence unless warranted.

5. STRATEGIC INSIGHTS
   - Strongest argument emerging
   - Their biggest vulnerability
   - Evidence still needed
</output_requirements>

Begin iteration {iteration + 1} analysis now.
Use extended thinking for complex reasoning.
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
    # PHASE 0: KNOWLEDGE SYNTHESIS (KEEP FROM OLD SYSTEM)
    # ========================================================================
    
    def knowledge_synthesis_prompt(self,
                                  legal_knowledge: List[Dict],
                                  case_context: List[Dict],
                                  existing_knowledge: Dict) -> str:
        """
        Prompt for synthesising legal knowledge with case context
        Builds comprehensive understanding in single phase
        KEPT FROM OLD SYSTEM - still useful for Phase 0 foundation
        """
        
        prompt = f"""<mission>
You're building a complete mental model for litigation.
Absorb EVERYTHING. Make connections. See the battlefield.
</mission>

<approach>
As you read, you're simultaneously:
1. Learning the legal weapons available (statutes, precedents, principles)
2. Understanding the case landscape (players, timeline, relationships)
3. Identifying vulnerabilities in Process Holdings' position
4. Spotting opportunities for Lismore's attack
5. Predicting their defence strategy
6. Building counter-strategies
</approach>

<existing_intelligence>
{json.dumps(existing_knowledge, indent=2)[:2000] if existing_knowledge else "First pass - no prior knowledge"}
</existing_intelligence>

<legal_knowledge_documents>
{self._format_documents(legal_knowledge[:30], doc_type="LEGAL")}
</legal_knowledge_documents>

<case_context_documents>
{self._format_documents(case_context[:30], doc_type="CASE")}
</case_context_documents>

<synthesis_requirements>
Build a comprehensive understanding that includes:

LEGAL ARSENAL:
- What laws/precedents can we weaponise?
- What duties did they breach?
- What damages can we claim?
- What defences must we anticipate?

CASE DYNAMICS:
- Who are the key players and their motivations?
- What's the real story of what happened?
- Where are they vulnerable?
- What are they hiding?

CONNECTIONS:
- How does the legal framework apply to these specific facts?
- What patterns emerge between law and conduct?
- Where does their behaviour violate legal principles?
- What evidence would be devastating given the law?

STRATEGIC SYNTHESIS:
- What's our strongest line of attack?
- What's their biggest weakness?
- What evidence should we hunt for?
- What questions destroy their case?
</synthesis_requirements>

<instruction>
Absorb everything. Make connections. Think strategically.
Show your reasoning. Mark critical insights with [STRATEGIC], [VULNERABILITY], [WEAPON].
Build the mental model that wins this case.
</instruction>"""
        
        return prompt
    
    # ========================================================================
    # LEGACY PROMPTS (KEEP FOR BACKWARDS COMPATIBILITY)
    # ========================================================================
    
    def investigation_prompt(self, 
                           documents: List[Dict],
                           context: Dict[str, Any],
                           phase: str) -> str:
        """
        Legacy investigation prompt from old system
        KEPT for backwards compatibility with Phase 0 if needed
        """
        
        suspicious_entities = context.get('suspicious_entities', [])
        contradictions = context.get('critical_contradictions', [])
        patterns = context.get('strong_patterns', [])
        impossibilities = context.get('timeline_impossibilities', [])
        investigations = context.get('active_investigations', [])
        
        prompt = f"""<adversarial_litigation_mindset>
YOU ARE A SENIOR LITIGATION PARTNER AT A MAGIC CIRCLE FIRM.

Client: Lismore Capital (£50M+ at stake)
Opposition: Process Holdings (document withholding suspected)
Mandate: FIND EVERYTHING that destroys their case

BALANCED COMMERCIAL FOCUS:
60% - Commercial fundamentals (obligations, breach, causation, quantum)
20% - Pattern recognition and evidence assessment
20% - Strategic positioning and adversarial thinking

DISCOVERY INTENSITY:
[SMOKING GUN] = Can win case alone
[NUCLEAR] = Game-changing evidence
[CRITICAL] = Major strategic advantage
[SUSPICIOUS] = Forensic investigation required
[PATTERN] = Systemic behaviour
[MISSING] = Document should exist but doesn't
[CONTRADICTION] = Witness/document conflict
[TIMELINE] = Impossible timing
</adversarial_litigation_mindset>

<current_intelligence>
Phase: {phase}
Documents in batch: {len(documents)}
Total entities tracked: {context.get('statistics', {}).get('entities', 0)}
Active investigations: {len(investigations)}
Critical contradictions found: {len(contradictions)}
High-confidence patterns: {len(patterns)}
Timeline impossibilities: {len(impossibilities)}

SUSPICIOUS ENTITIES:
{self._format_suspicious_entities(suspicious_entities)}

CRITICAL CONTRADICTIONS:
{self._format_contradictions(contradictions[:5])}
</current_intelligence>

<documents>
{self._format_documents(documents[:50])}  
</documents>

<instruction>
Begin your investigation. Think out loud. Show your reasoning in real-time.
Follow EVERY interesting thread to its conclusion. Be creative. Be thorough.
Connect dots others wouldn't see. Find patterns in chaos.
Question everything. Trust nothing at face value.

What wins this case might be hidden in a single sentence.
Find it.
</instruction>"""
        
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
    
    def _format_suspicious_entities(self, entities: List[Dict]) -> str:
        """Format suspicious entities for prompt"""
        if not entities:
            return "No suspicious entities identified yet"
        
        formatted = []
        for entity in entities[:10]:
            formatted.append(
                f"- {entity.get('name', 'Unknown')} ({entity.get('type', 'Unknown')}): "
                f"Suspicion {entity.get('suspicion', 0.0):.1f}/1.0"
            )
        return "\n".join(formatted)
    
    def _format_contradictions(self, contradictions: List[Dict]) -> str:
        """Format contradictions for prompt"""
        if not contradictions:
            return "No critical contradictions found yet"
        
        formatted = []
        for cont in contradictions:
            formatted.append(
                f"- Severity {cont.get('severity', 0)}/10: "
                f"{cont.get('statement_a', '')[:100]} VS {cont.get('statement_b', '')[:100]}"
            )
        return "\n".join(formatted)