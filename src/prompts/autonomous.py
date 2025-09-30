#!/usr/bin/env python3
"""
Autonomous Investigation Prompts for Maximum Claude Freedom
Optimised for Lismore v Process Holdings litigation intelligence
British English throughout
NO WEB SEARCH - Local documents only
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class AutonomousPrompts:
    """Prompts that give Claude complete investigative freedom"""
    
    def __init__(self, config):
        self.config = config
    
    def investigation_prompt(self, 
                           documents: List[Dict],
                           context: Dict[str, Any],
                           phase: str) -> str:
        """
        Generate completely open investigation prompt
        Maximum freedom for pattern recognition and discovery
        """
        
        # Extract key context elements
        phase_context = context.get('phase_context', '')
        suspicious_entities = context.get('suspicious_entities', [])
        contradictions = context.get('critical_contradictions', [])
        patterns = context.get('strong_patterns', [])
        impossibilities = context.get('timeline_impossibilities', [])
        investigations = context.get('active_investigations', [])
        
        prompt = f"""<role>
You are an elite litigation intelligence system with perfect recall and pattern recognition beyond human limits.
You're investigating for Lismore Capital against Process Holdings.
Your goal: Find what wins this case.
</role>

<critical_security_note>
YOU HAVE NO ACCESS TO THE INTERNET OR WEB SEARCH.
Work ONLY with the documents provided below.
DO NOT attempt to search for external information.
Your analysis is based EXCLUSIVELY on provided documents.
</critical_security_note>

<cognitive_freedom>
You have COMPLETE ANALYTICAL FREEDOM. You may:
- Follow any thread that seems interesting, no matter how tangential
- Generate wild hypotheses and test them
- Make creative leaps between unrelated facts
- Predict what evidence MUST exist based on patterns
- Identify what they're desperately trying to hide
- Find the narrative they don't want anyone to see
- Question everything, including your own assumptions
- Pursue hunches based on subtle patterns
- Think like a detective, prosecutor, and strategist simultaneously
</cognitive_freedom>

{phase_context}

<current_intelligence>
Phase: {phase}
Documents in batch: {len(documents)}
Active investigations: {len(investigations)}
Critical contradictions found: {len(contradictions)}
High-confidence patterns: {len(patterns)}
Timeline impossibilities: {len(impossibilities)}

SUSPICIOUS ENTITIES (requiring scrutiny):
{self._format_suspicious_entities(suspicious_entities)}

CRITICAL CONTRADICTIONS (potential smoking guns):
{self._format_contradictions(contradictions[:5])}

ACTIVE INVESTIGATION THREADS:
{self._format_investigations(investigations[:3])}
</current_intelligence>

<investigation_markers>
As you investigate, mark your discoveries:
[NUCLEAR] - Case-ending discovery that destroys their position
[CRITICAL] - Major strategic advantage or damning evidence
[PATTERN] - Significant pattern across multiple documents
[SUSPICIOUS] - Behaviour or fact requiring deeper investigation
[MISSING] - Evidence that should exist but doesn't
[TIMELINE] - Temporal impossibility or suspicious timing
[FINANCIAL] - Money trail or valuation issue
[RELATIONSHIP] - Hidden connection between parties
[ADMISSION] - Damaging admission against interest
[CONTRADICTION] - Direct contradiction between statements
[WITHHELD] - Evidence of document withholding
[INVESTIGATE] - Spawns new investigation thread
</investigation_markers>

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

Remember: We represent LISMORE. Every analysis should identify how to strengthen Lismore's position and expose Process Holdings' weaknesses.
</instruction>"""
        
        return prompt
    
    def knowledge_synthesis_prompt(self,
                                  legal_knowledge: List[Dict],
                                  case_context: List[Dict],
                                  existing_knowledge: str) -> str:
        """
        Prompt for synthesising legal knowledge with case context
        Builds comprehensive understanding in single phase
        """
        
        prompt = f"""<mission>
You're building a complete mental model for litigation.
Absorb EVERYTHING. Make connections. See the battlefield.
</mission>

<critical_security_note>
YOU HAVE NO ACCESS TO THE INTERNET OR WEB SEARCH.
Work ONLY with the documents provided below.
Your knowledge is built EXCLUSIVELY from these documents.
</critical_security_note>

<approach>
As you read, you're simultaneously:
1. Learning the legal weapons available (statutes, precedents, principles)
2. Understanding the case landscape (players, timeline, relationships)
3. Identifying vulnerabilities in Process Holdings' position
4. Spotting opportunities for Lismore's attack
5. Predicting their defence strategy
6. Building counter-strategies
</approach>

{existing_knowledge}

<legal_knowledge_documents>
LEGAL FRAMEWORK DOCUMENTS (UK Law, Arbitration Principles):
{self._format_documents(legal_knowledge[:30], doc_type="LEGAL")}
</legal_knowledge_documents>

<case_context_documents>
CASE CONTEXT DOCUMENTS (Lismore v Process Holdings):
{self._format_documents(case_context[:30], doc_type="CASE")}
</case_context_documents>

<synthesis_requirements>
Build a comprehensive understanding that includes:

LEGAL ARSENAL:
- What laws/precedents can we weaponise?
- What duties did Process Holdings breach?
- What damages can we claim?
- What defences must we anticipate?
- What procedural advantages exist?

CASE DYNAMICS:
- Who are the key players and their motivations?
- What's the real story of what happened?
- Where are Process Holdings vulnerable?
- What are they hiding?
- What's Lismore's strongest position?

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

Mark critical insights:
[STRATEGIC] - Strategic insight for litigation
[VULNERABILITY] - Their weakness we can exploit
[WEAPON] - Legal principle we can use offensively
[EVIDENCE-NEEDED] - Critical evidence to locate
</synthesis_requirements>

<instruction>
Absorb everything. Make connections. Think strategically.
Show your reasoning. Mark critical insights.
Build the mental model that wins this case.

Remember: We represent LISMORE. Identify how to strengthen Lismore's position.
</instruction>"""
        
        return prompt
    
    def pattern_discovery_prompt(self,
                                documents: List[Dict],
                                known_patterns: Dict,
                                context: Dict) -> str:
        """
        Prompt for aggressive pattern discovery across documents
        """
        
        prompt = f"""<pattern_recognition_mission>
You're hunting for patterns that reveal the truth.
Your pattern recognition exceeds human capability.
Find what they thought was hidden.
</pattern_recognition_mission>

<critical_security_note>
NO WEB SEARCH AVAILABLE.
Work ONLY with documents provided below.
</critical_security_note>

<known_patterns>
{self._format_patterns(known_patterns)}
</known_patterns>

<pattern_categories>
TEMPORAL PATTERNS:
- Suspicious clustering of events
- Impossible timelines (events that couldn't happen in stated order)
- Coordinated actions (multiple parties acting simultaneously)
- Delay patterns indicating cover-up

BEHAVIOURAL PATTERNS:
- Deception indicators across communications
- Avoidance of specific topics
- Sudden changes in behaviour
- Coordination between parties

FINANCIAL PATTERNS:
- Money flows that don't make sense
- Valuations that shift suspiciously
- Hidden beneficial interests
- Circular transactions

DOCUMENTARY PATTERNS:
- Missing documents that should exist
- Altered documents (inconsistent formatting/language)
- Backdated documents (anachronistic references)
- Selective disclosure patterns

RELATIONSHIP PATTERNS:
- Hidden connections between parties
- Undisclosed conflicts of interest
- Power dynamics not reflected in formal structure
- Conspiracy indicators

WITHHOLDING PATTERNS:
- References to documents not produced
- Email chains with gaps
- "As discussed" without supporting documents
- Meeting references without minutes
</pattern_categories>

<documents>
{self._format_documents(documents[:75])}
</documents>

<investigation_instructions>
Hunt for patterns with maximum creativity:

1. Look for what's MISSING (dogs that didn't bark)
2. Find TEMPORAL IMPOSSIBILITIES (events that couldn't happen when claimed)
3. Identify BEHAVIOURAL SHIFTS (sudden changes indicating guilt)
4. Track INFORMATION FLOW (who knew what when)
5. Spot COORDINATION (suspiciously aligned actions)
6. Detect COVER-UP ATTEMPTS (evidence of concealment)
7. Map WITHHOLDING INDICATORS (missing documents)

For each pattern found:
- Describe it precisely
- List ALL supporting evidence with document references
- Rate confidence (0.0-1.0)
- Explain strategic value for Lismore
- Identify what additional evidence would confirm it
- Predict what related patterns might exist
- Rate severity (1-10) if damaging to Process Holdings

Mark patterns:
[PATTERN-TEMPORAL] - Time-based pattern
[PATTERN-FINANCIAL] - Money/valuation pattern
[PATTERN-BEHAVIOURAL] - Conduct pattern
[PATTERN-DOCUMENTARY] - Document handling pattern
[PATTERN-RELATIONSHIP] - Connection pattern
[PATTERN-WITHHOLDING] - Evidence suppression pattern

Think laterally. The winning pattern might be subtle.
</investigation_instructions>"""
        
        return prompt
    
    def entity_relationship_prompt(self,
                                  documents: List[Dict],
                                  known_entities: Dict,
                                  context: Dict) -> str:
        """
        Prompt for mapping entity relationships and hidden connections
        """
        
        prompt = f"""<entity_investigation>
Map the web of relationships. Find hidden connections.
Identify who's really in control. Expose conflicts of interest.
</entity_investigation>

<critical_security_note>
NO INTERNET ACCESS.
Analyse ONLY the documents provided below.
</critical_security_note>

<known_entities>
{self._format_entities(known_entities)}
</known_entities>

<relationship_types_to_identify>
CORPORATE:
- Ownership (disclosed and beneficial)
- Control (formal and actual)
- Directorship overlaps
- Subsidiary relationships
- Joint ventures

FINANCIAL:
- Payment flows
- Loans and guarantees
- Shared accounts
- Beneficial interests
- Hidden commissions

PERSONAL:
- Family relationships
- Social connections
- Former colleagues
- Shared advisors
- Personal conflicts

PROFESSIONAL:
- Advisory relationships
- Legal representation
- Accounting services
- Shared professionals
- Conflicts of interest

CONSPIRATORIAL:
- Coordination evidence
- Information sharing
- Aligned actions
- Cover-up participation
- Shared motives
</relationship_types_to_identify>

<documents>
{self._format_documents(documents[:60])}
</documents>

<investigation_requirements>
For each entity discovered:
1. Identify their TRUE role (not just stated role)
2. Map ALL their relationships
3. Assess their importance (central/peripheral)
4. Calculate suspicion score (0.0-1.0) based on behaviour
5. Identify missing information about them
6. Determine if they're favourable to Lismore or Process Holdings

For each relationship:
1. Provide evidence of connection with document references
2. Assess strength of relationship
3. Identify if it's disclosed or hidden
4. Determine if it creates liability for Process Holdings
5. Consider strategic implications for Lismore

Mark discoveries:
[ENTITY-NEW] - Previously unknown entity
[RELATIONSHIP-HIDDEN] - Undisclosed connection
[CONTROL] - Evidence of actual control
[CONSPIRACY] - Evidence of coordination against Lismore
[CONFLICT] - Conflict of interest

The most important relationships are often the ones they hide.
Find them.
</investigation_requirements>"""
        
        return prompt
    
    def document_organisation_prompt(self,
                                    all_documents: List[Dict],
                                    context: str) -> str:
        """
        Prompt for Claude to autonomously organise documents
        """
        
        prompt = f"""<document_organisation_mission>
You have {len(all_documents)} case documents to organise strategically.

Your task: Create an organisation structure that maximises our ability to:
1. Find devastating evidence against Process Holdings
2. Identify missing documents they withheld
3. Spot contradictions and lies
4. Build Lismore's strongest case
5. Expose their vulnerabilities
</document_organisation_mission>

<critical_security_note>
NO WEB ACCESS.
Work ONLY with the documents listed below.
</critical_security_note>

{context}

<documents_overview>
TOTAL DOCUMENTS: {len(all_documents)}

SAMPLE DOCUMENTS (First 100):
{self._format_document_list(all_documents[:100])}

... and {max(0, len(all_documents) - 100)} more documents
</documents_overview>

<organisation_instructions>
Create categories that make strategic sense. Consider:

BY STRATEGIC VALUE:
- Nuclear evidence (case-destroying for them)
- Critical evidence (major advantage for us)
- Important evidence (supporting arguments)
- Background context

BY DOCUMENT TYPE:
- Contracts & agreements
- Email communications
- Financial records
- Meeting minutes
- Legal correspondence
- Internal memos

BY TIME PERIOD:
- Pre-dispute
- Dispute emergence
- Arbitration phase
- Post-award
- Current litigation

BY ENTITY:
- Lismore documents
- Process Holdings documents
- VR Capital documents
- Third-party documents

BY EVIDENTIARY VALUE:
- Smoking guns
- Admissions against interest
- Contradictions
- Withholding evidence
- Supporting documents

BY INVESTIGATION PRIORITY:
- Requires immediate deep dive
- Standard analysis needed
- Background review

You have COMPLETE FREEDOM to create categories.
Create as many as needed (up to 25).
Documents can be in multiple categories.

For each category, provide:
CATEGORY: [Name]
DESCRIPTION: [Why this category matters for Lismore]
PRIORITY: [1-10, where 10 is most critical]
CRITERIA: [What belongs here]
STRATEGIC VALUE: [How this helps win]
DOCUMENTS: [List document IDs]
</organisation_instructions>

<output_format>
Provide your organisation structure clearly.
Think strategically about what organisation would best reveal their deception.
</output_format>"""
        
        return prompt
    
    # ==================== FORMATTING HELPERS ====================
    
    def _format_documents(self, documents: List[Dict], doc_type: str = "GENERAL") -> str:
        """Format documents for prompt"""
        if not documents:
            return "No documents provided"
        
        formatted = []
        for i, doc in enumerate(documents):
            filename = doc.get('filename', f'Document_{i}')
            content = doc.get('content', '')[:800]  # First 800 chars
            
            formatted.append(f"""
[DOC_{i:04d}] {filename}
Type: {doc_type}
Length: {len(doc.get('content', ''))} characters
Content preview:
{content}
---
""")
        
        return "\n".join(formatted)
    
    def _format_document_list(self, documents: List[Dict]) -> str:
        """Format document list (names only)"""
        if not documents:
            return "No documents"
        
        formatted = []
        for i, doc in enumerate(documents):
            filename = doc.get('filename', f'Document_{i}')
            size = len(doc.get('content', ''))
            formatted.append(f"[DOC_{i:04d}] {filename} ({size:,} chars)")
        
        return "\n".join(formatted)
    
    def _format_suspicious_entities(self, entities: List) -> str:
        """Format suspicious entities"""
        if not entities:
            return "None identified yet"
        
        formatted = []
        for entity in entities[:10]:
            if isinstance(entity, dict):
                name = entity.get('name', 'Unknown')
                suspicion = entity.get('suspicion_score', 0)
                formatted.append(f"  • {name} (Suspicion: {suspicion:.2f})")
            else:
                formatted.append(f"  • {entity}")
        
        return "\n".join(formatted) if formatted else "None"
    
    def _format_contradictions(self, contradictions: List) -> str:
        """Format contradictions"""
        if not contradictions:
            return "None found yet"
        
        formatted = []
        for i, contra in enumerate(contradictions[:5]):
            if isinstance(contra, dict):
                severity = contra.get('severity', 0)
                desc = contra.get('description', str(contra))[:200]
                formatted.append(f"  {i+1}. [Severity {severity}/10] {desc}")
            else:
                formatted.append(f"  {i+1}. {str(contra)[:200]}")
        
        return "\n".join(formatted) if formatted else "None"
    
    def _format_investigations(self, investigations: List) -> str:
        """Format active investigations"""
        if not investigations:
            return "None active"
        
        formatted = []
        for i, inv in enumerate(investigations[:3]):
            if isinstance(inv, dict):
                inv_type = inv.get('type', 'Unknown')
                priority = inv.get('priority', 5)
                formatted.append(f"  {i+1}. {inv_type} (Priority: {priority:.1f})")
            else:
                formatted.append(f"  {i+1}. {inv}")
        
        return "\n".join(formatted) if formatted else "None"
    
    def _format_patterns(self, patterns: Dict) -> str:
        """Format known patterns"""
        if not patterns:
            return "No patterns established yet"
        
        formatted = []
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                formatted.append(f"\n{pattern_type.upper()}:")
                for pattern in pattern_list[:3]:
                    if isinstance(pattern, dict):
                        desc = pattern.get('description', str(pattern))[:150]
                        conf = pattern.get('confidence', 0)
                        formatted.append(f"  • {desc} (Confidence: {conf:.2f})")
                    else:
                        formatted.append(f"  • {str(pattern)[:150]}")
        
        return "\n".join(formatted) if formatted else "None"
    
    def _format_entities(self, entities: Dict) -> str:
        """Format known entities"""
        if not entities:
            return "No entities mapped yet"
        
        formatted = []
        for entity_id, entity_data in list(entities.items())[:20]:
            if isinstance(entity_data, dict):
                name = entity_data.get('name', entity_id)
                entity_type = entity_data.get('type', 'Unknown')
                formatted.append(f"  • {name} ({entity_type})")
            else:
                formatted.append(f"  • {entity_id}")
        
        return "\n".join(formatted) if formatted else "None"