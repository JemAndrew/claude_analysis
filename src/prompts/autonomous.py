#!/usr/bin/env python3
"""
Autonomous Investigation Prompts for Maximum Claude Freedom
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
    
    def investigation_prompt(self, 
                           documents: List[Dict],
                           context: Dict[str, Any],
                           phase: str) -> str:
        """
        Generate completely open investigation prompt
        Maximum freedom for pattern recognition and discovery
        """
        
        # Extract key context elements
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

PROSECUTION MINDSET:
1. Assume opposition is HIDING something until proven otherwise
2. Every timeline gap is INTENTIONAL concealment
3. Every vague statement is deliberate EVASION
4. Every missing document is potential SPOLIATION
5. Every contradiction is potential PERJURY

DISCOVERY INTENSITY:
[SMOKING GUN] = Can win case alone
[NUCLEAR] = Game-changing evidence
[CRITICAL] = Major strategic advantage
[SUSPICIOUS] = Forensic investigation required
[PATTERN] = Systemic behaviour
[MISSING] = Document should exist but doesn't
[CONTRADICTION] = Witness/document conflict
[TIMELINE] = Impossible timing

ADVERSARIAL QUESTIONS (every document):
1. What are they NOT telling us?
2. What document SHOULD exist but doesn't?
3. Who BENEFITS from this omission?
4. What would THEIR LAWYER worry about?
5. How do we DESTROY their explanation?

Think like a PROSECUTOR building a criminal case.
</adversarial_litigation_mindset>
<role>
You are an elite litigation intelligence system with perfect recall and pattern recognition beyond human limits.
You're investigating for Lismore Capital against Process Holdings.
Your goal: Find what wins this case.
</role>

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

<current_intelligence>
Phase: {phase}
Documents in batch: {len(documents)}
Total entities tracked: {context.get('statistics', {}).get('entities', 0)}
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
</instruction>"""
        
        return prompt
    
    def knowledge_synthesis_prompt(self,
                                  legal_knowledge: List[Dict],
                                  case_context: List[Dict],
                                  existing_knowledge: Dict) -> str:
        """
        Prompt for synthesising legal knowledge with case context
        Builds comprehensive understanding in single phase
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
    
    def metadata_scan_prompt(self,
                            documents: List[Dict],
                            context: Dict) -> str:
        """
        NEW: Lightweight metadata scan prompt for Tier 2 analysis
        Flags suspicious documents for deep Tier 3 investigation
        """
        
        # Format documents for metadata scan (just preview, not full content)
        doc_list = []
        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            content_preview = doc.get('content', '')[:500]  # First 500 chars only
            
            doc_list.append(f"""
[DOC_{i}]
Filename: {metadata.get('filename', 'unknown')}
Date: {metadata.get('date', 'unknown')}
Source: {metadata.get('source_folder', 'unknown')}
Type: {metadata.get('doc_type', 'unknown')}
Preview: {content_preview}
---
""")
        
        docs_text = "\n".join(doc_list)
        
        # Extract key entities from context for reference
        known_entities = context.get('statistics', {}).get('entities', 0)
        known_contradictions = context.get('statistics', {}).get('contradictions', 0)
        
        prompt = f"""<metadata_scan_mission>
You are conducting a RAPID metadata scan of disclosure documents for Lismore v Process Holdings.

Current Intelligence: {known_entities} entities tracked, {known_contradictions} contradictions found

Your goal: FLAG suspicious documents requiring deep Tier 3 analysis.

WE ARE ARGUING FOR LISMORE. Flag documents that might:
- Contain evidence of Process Holdings' misconduct
- Reveal contradictions in PH's position
- Show hidden relationships or conspiracy
- Evidence financial irregularities
- Demonstrate timeline inconsistencies
- Reference withheld or destroyed documents
- Show coordination to deceive
- Contain smoking gun evidence
</metadata_scan_mission>

<flagging_criteria>
Flag documents with ANY of these indicators:

DECEPTION INDICATORS:
- References to "confidential", "destroy", "delete", "off the record"
- Phrases like "don't put in writing", "verbal only", "between us"
- References to legal privilege that seem questionable

TIMELINE SUSPICION:
- Unusual timing (events clustered suspiciously around key dates)
- Backdating indicators (anachronistic references)
- Communication gaps (suspicious lack of correspondence)

FINANCIAL ANOMALIES:
- Unexplained payments or valuations
- References to undisclosed accounts or entities
- Circular transactions or money flows

RELATIONSHIP INDICATORS:
- References to undisclosed parties or relationships
- Coordination evidence between supposedly independent parties
- Hidden beneficial interests

DOCUMENT GAPS:
- References to other documents not in disclosure
- Incomplete email chains (missing replies)
- Redactions or missing pages

ADMISSIONS/CONTRADICTIONS:
- Statements contradicting PH's known position
- Admissions against interest
- Internal doubts about their legal position
</flagging_criteria>

<documents_to_scan>
{docs_text}
</documents_to_scan>

<output_format>
For EACH document that should be flagged for Tier 3 deep analysis:

[FLAG_DOC_X]
Reason: [Brief specific reason for flagging - cite what you saw]
Suspicion Level: [1-10, where 10 is smoking gun]
Priority: [HIGH/MEDIUM/LOW]
Categories: [List applicable: DECEPTION/TIMELINE/FINANCIAL/RELATIONSHIP/GAPS/ADMISSION]

Example:
[FLAG_DOC_15]
Reason: Email references "off the record discussion" about valuation with undisclosed party
Suspicion Level: 8
Priority: HIGH
Categories: DECEPTION, RELATIONSHIP, FINANCIAL

If NO documents in this batch require flagging, state: NO_FLAGS
</output_format>

<critical_instructions>
- Be AGGRESSIVE in flagging - we don't want to miss potential smoking guns
- Even subtle suspicion warrants flagging (Tier 3 will investigate properly)
- Focus on WHAT YOU SEE in the preview, not speculation
- If a document references other documents or parties not in our knowledge base, FLAG IT
- Timeline proximity to critical dates is highly suspicious - FLAG IT
- Any coordination language between parties is CRITICAL - FLAG IT
</critical_instructions>

Scan rapidly. Flag aggressively. Protect Lismore's interests.
"""
        
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

<known_patterns>
{self._format_patterns(known_patterns)}
</known_patterns>

<pattern_categories>
TEMPORAL PATTERNS:
- Suspicious clustering of events
- Impossible timelines
- Coordinated actions
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

For each pattern found:
- Describe it precisely
- List ALL supporting evidence
- Rate confidence (0.0-1.0)
- Explain strategic value
- Identify what additional evidence would confirm it
- Predict what related patterns might exist

Mark patterns: [PATTERN-TEMPORAL], [PATTERN-FINANCIAL], [PATTERN-BEHAVIOURAL], [PATTERN-DOCUMENTARY], [PATTERN-RELATIONSHIP]

Be creative. Think laterally. The winning pattern might be subtle.
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
- Shared advisers
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
4. Calculate suspicion score (0.0-1.0)
5. Identify missing information about them

For each relationship:
1. Provide evidence of connection
2. Assess strength of relationship
3. Identify if it's disclosed or hidden
4. Determine if it creates liability
5. Consider strategic implications

Mark discoveries:
[ENTITY-NEW] - Previously unknown entity
[RELATIONSHIP-HIDDEN] - Undisclosed connection
[CONTROL] - Evidence of actual control
[CONSPIRACY] - Evidence of coordination
[CONFLICT] - Conflict of interest

The most important relationships are often the ones they hide.
Find them.
</investigation_requirements>"""
        
        return prompt
    
    # ========================================================================
    # FORMATTING HELPER METHODS
    # ========================================================================
    
    def _format_suspicious_entities(self, entities: List[Dict]) -> str:
        """Format suspicious entities for prompt"""
        if not entities:
            return "No suspicious entities identified yet"
        
        formatted = []
        for entity in entities[:10]:
            formatted.append(
                f"- {entity['name']} ({entity['type']}): "
                f"Suspicion {entity['suspicion']:.1f}/1.0"
            )
        return "\n".join(formatted)
    
    def _format_contradictions(self, contradictions: List[Dict]) -> str:
        """Format contradictions for prompt"""
        if not contradictions:
            return "No critical contradictions found yet"
        
        formatted = []
        for cont in contradictions:
            formatted.append(
                f"- Severity {cont['severity']}/10: "
                f"{cont['statement_a'][:100]} VS {cont['statement_b'][:100]}"
            )
        return "\n".join(formatted)
    
    def _format_investigations(self, investigations: List[Dict]) -> str:
        """Format active investigations for prompt"""
        if not investigations:
            return "No active investigation threads"
        
        formatted = []
        for inv in investigations:
            formatted.append(
                f"- {inv['type']} (Priority: {inv['priority']:.1f})"
            )
        return "\n".join(formatted)
    
    def _format_patterns(self, patterns: Dict) -> str:
        """Format known patterns for prompt"""
        if not patterns:
            return "No patterns identified yet - hunt freely"
        
        formatted = []
        for pattern_id, pattern_data in list(patterns.items())[:10]:
            formatted.append(
                f"- {pattern_data.get('description', pattern_id)[:100]} "
                f"(Confidence: {pattern_data.get('confidence', 0.5):.1f})"
            )
        return "\n".join(formatted) if formatted else "Starting fresh pattern recognition"
    
    def _format_entities(self, entities: Dict) -> str:
        """Format known entities for prompt"""
        if not entities:
            return "No entities mapped yet - identify all players"
        
        formatted = []
        for entity_type, entity_list in list(entities.items())[:5]:
            formatted.append(f"\n{entity_type.upper()}:")
            for entity in entity_list[:10]:
                formatted.append(f"  - {entity}")
        
        return "\n".join(formatted) if formatted else "Beginning entity mapping"
    
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