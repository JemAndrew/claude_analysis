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
    
    def knowledge_synthesis_prompt(self,
                                  legal_knowledge: List[Dict],
                                  case_context: List[Dict],
                                  existing_knowledge: str) -> str:
        """
        Phase 0: Synthesise legal knowledge ONLY
        Build comprehensive understanding of legal framework
        NO case analysis yet - pure legal learning
        """
        
        prompt = f"""<mission>
You're building complete legal knowledge for Lismore v Process Holdings arbitration.
Master the legal weapons. Understand the battlefield. Prepare for war.
</mission>

<critical_security_note>
YOU HAVE NO ACCESS TO THE INTERNET OR WEB SEARCH.
Work ONLY with the documents provided below.
Your knowledge is built EXCLUSIVELY from these documents.
</critical_security_note>

<approach>
As you read legal documents, you're:
1. Learning the legal weapons available (statutes, precedents, principles)
2. Understanding applicable legal frameworks
3. Identifying how to establish liability
4. Mapping out damages frameworks
5. Predicting their defence strategy
6. Building counter-strategies
</approach>

{existing_knowledge}

<legal_knowledge_documents>
LEGAL FRAMEWORK DOCUMENTS (UK Law, Arbitration Principles):
{self._format_documents(legal_knowledge[:30], doc_type="LEGAL")}
</legal_knowledge_documents>

<synthesis_requirements>
Build comprehensive legal understanding that includes:

LEGAL ARSENAL:
- What laws/precedents can we weaponise?
- What duties did Process Holdings breach?
- What damages can we claim?
- What defences must we anticipate?
- What procedural advantages exist?

BURDEN OF PROOF:
- What must we establish?
- What standard applies?
- What evidence types are needed?
- What presumptions help us?

STRATEGIC LEGAL FRAMEWORK:
- What's our strongest legal angle?
- What are their weakest legal positions?
- What legal principles favour Lismore?
- What case law destroys their arguments?

Mark critical insights:
[STRATEGIC] - Strategic insight for litigation
[WEAPON] - Legal principle we can use offensively
[DEFENCE-KILLER] - Principle that destroys their defences
[EVIDENCE-NEEDED] - Critical evidence type required
</synthesis_requirements>

<instruction>
Absorb everything. Make connections. Think strategically.
Show your reasoning. Mark critical insights.
Build the legal framework that wins this case.

Remember: We represent LISMORE. Master the law to strengthen our position.
</instruction>"""
        
        return prompt
    
    def case_understanding_prompt(self,
                                 case_documents: List[Dict],
                                 legal_framework: str,
                                 doc_count: int) -> str:
        """
        Phase 1: Complete case understanding (NEW - added for simplified system)
        Claude reads ALL case documents for first time
        Builds complete picture, marks everything interesting
        """
        
        prompt = f"""<legal_framework>
{legal_framework[:10000]}
</legal_framework>

<case_understanding_mission>
You are reading {doc_count} case documents for the FIRST time.

Your goal: Build COMPLETE understanding of Lismore v Process Holdings.

WHAT TO UNDERSTAND:
- What happened? (full chronology)
- Who are the players? (all entities and their roles)
- What's the timeline? (key events and dates)
- Where are they vulnerable? (weaknesses in their case)
- What evidence exists? (documents, testimony, facts)
- What's missing? (gaps, inconsistencies, contradictions)
- What patterns emerge? (suspicious behaviour, systematic issues)

MARK EVERYTHING INTERESTING:
- [NUCLEAR] - Case-ending discoveries (smoking gun evidence, fatal contradictions)
- [CRITICAL] - Major strategic advantages (strong liability evidence, damages proof)
- [INVESTIGATE] - Threads needing deep investigation (suspicious transactions, timeline gaps)
- [SUSPICIOUS] - Anomalies worth exploring (unusual patterns, odd behaviours)
- [PATTERN] - Recurring behaviours or themes (systematic concealment, consistent lies)
- [CONTRADICTION] - Direct contradictions between statements
- [MISSING] - Evidence that should exist but doesn't
- [FINANCIAL] - Money trails or valuation issues
</case_understanding_mission>

<critical_security_note>
NO WEB SEARCH AVAILABLE.
Work ONLY with documents provided below.
</critical_security_note>

<all_case_documents count="{doc_count}">
{self._format_documents(case_documents[:50])}
</all_case_documents>

<instruction>
Read EVERYTHING thoroughly.
Think freely about what matters.
Mark ANYTHING worth investigating deeper.

Structure your understanding:
1. **CASE OVERVIEW**: What happened and why we'll win
2. **KEY PLAYERS**: Who they are and their roles
3. **TIMELINE**: Critical events in chronological order
4. **THEIR VULNERABILITIES**: Where their case is weak
5. **OUR STRENGTHS**: Evidence and arguments in our favour
6. **GAPS & CONTRADICTIONS**: Inconsistencies to exploit
7. **INVESTIGATION PRIORITIES**: What needs deeper analysis

This is your foundation for destroying Process Holdings.
Build the complete picture.

Remember: We represent LISMORE. Every analysis strengthens our position.
</instruction>"""
        
        return prompt
    
    def investigation_prompt(self, 
                           documents: List[Dict],
                           context: Dict[str, Any],
                           phase: str) -> str:
        """
        Phase 2+: Completely open investigation prompt
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
    
    def pattern_discovery_prompt(self,
                                documents: List[Dict],
                                known_patterns: Dict,
                                context: Dict) -> str:
        """
        Aggressive pattern discovery across documents
        Can be called autonomously during investigations
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
        Map entity relationships and hidden connections
        Can be called autonomously during investigations
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


    def _format_documents(self, documents: List[Dict], doc_type: str = "DISCLOSURE") -> str:
        """Format documents for prompt inclusion - British English"""
        
        if not documents:
            return f"No {doc_type.lower()} documents provided"
        
        formatted = []
        for i, doc in enumerate(documents[:50], 1):  # Limit to 50 for context window
            # Extract key fields
            title = doc.get('title', doc.get('filename', 'Unknown'))
            source = doc.get('source', doc.get('path', 'Unknown'))
            date = doc.get('date', doc.get('created', 'Unknown'))
            content = doc.get('content', '')[:2000]  # First 2000 chars
            
            formatted.append(f"""
    [DOC_{i:04d}] ({doc_type})
    Title: {title}
    Source: {source}
    Date: {date}
    Content Preview:
    {content}
    {'...' if len(doc.get('content', '')) > 2000 else ''}
    ---
    """)
        
        summary = f"\n{len(documents)} {doc_type} documents available"
        if len(documents) > 50:
            summary += f" (showing first 50, {len(documents) - 50} more available)"
        
        return summary + "\n\n" + "\n".join(formatted)


    def _format_evidence(self, evidence: List[str]) -> str:
        """Format evidence list for prompts"""
        
        if not evidence:
            return "No evidence provided"
        
        formatted = []
        for i, ev in enumerate(evidence[:20], 1):  # Limit to 20
            # Truncate long evidence
            evidence_text = ev[:500]
            if len(ev) > 500:
                evidence_text += "..."
            
            formatted.append(f"{i}. {evidence_text}")
        
        if len(evidence) > 20:
            formatted.append(f"\n[...and {len(evidence) - 20} more pieces of evidence]")
        
        return "\n".join(formatted)


    def _format_entities(self, entities: Dict) -> str:
        """Format known entities for prompt"""
        
        if not entities:
            return "No entities mapped yet - identify all players"
        
        formatted = []
        
        # Group by entity type
        by_type = {}
        for entity_id, entity_data in entities.items():
            entity_type = entity_data.get('type', 'UNKNOWN')
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity_data)
        
        # Format each type
        for entity_type, entity_list in list(by_type.items())[:5]:  # Limit to 5 types
            formatted.append(f"\n{entity_type}:")
            for entity in entity_list[:10]:  # Limit to 10 per type
                name = entity.get('name', 'Unknown')
                confidence = entity.get('confidence', 0.0)
                formatted.append(f"  - {name} (confidence: {confidence:.2f})")
            
            if len(entity_list) > 10:
                formatted.append(f"  [...and {len(entity_list) - 10} more {entity_type}]")
        
        if len(by_type) > 5:
            formatted.append(f"\n[...and {len(by_type) - 5} more entity types]")
        
        return "\n".join(formatted) if formatted else "Starting entity mapping"


    def _format_timeline(self, timeline: Dict) -> str:
        """Format timeline events for prompt"""
        
        if not timeline or not timeline.get('events'):
            return "No timeline events recorded yet"
        
        events = timeline.get('events', [])
        
        formatted = []
        formatted.append(f"Timeline: {len(events)} events recorded\n")
        
        # Sort by date if available
        try:
            sorted_events = sorted(events, key=lambda x: x.get('date', ''))
        except:
            sorted_events = events
        
        # Show first 20 events
        for event in sorted_events[:20]:
            date = event.get('date', 'Unknown date')
            description = event.get('description', 'No description')[:200]
            critical = " [CRITICAL]" if event.get('is_critical') else ""
            
            formatted.append(f"  • {date}: {description}{critical}")
        
        if len(events) > 20:
            formatted.append(f"\n  [...and {len(events) - 20} more events]")
        
        return "\n".join(formatted)


    def _format_relationships(self, relationships: List[Dict]) -> str:
        """Format relationships for prompt"""
        
        if not relationships:
            return "No relationships mapped yet"
        
        formatted = []
        formatted.append(f"Relationships: {len(relationships)} identified\n")
        
        for rel in relationships[:15]:  # Limit to 15
            source = rel.get('source', 'Unknown')
            target = rel.get('target', 'Unknown')
            rel_type = rel.get('type', 'UNKNOWN')
            confidence = rel.get('confidence', 0.0)
            
            formatted.append(
                f"  • {source} --[{rel_type}]--> {target} "
                f"(confidence: {confidence:.2f})"
            )
        
        if len(relationships) > 15:
            formatted.append(f"\n  [...and {len(relationships) - 15} more relationships]")
        
        return "\n".join(formatted)


    def _format_context_summary(self, context: Dict) -> str:
        """Format full context summary for prompt"""
        
        summary = []
        
        # Statistics
        stats = context.get('statistics', {})
        if stats:
            summary.append("CURRENT INTELLIGENCE STATE:")
            summary.append(f"  Entities tracked: {stats.get('entities', 0)}")
            summary.append(f"  Relationships mapped: {stats.get('relationships', 0)}")
            summary.append(f"  Contradictions found: {stats.get('contradictions', 0)}")
            summary.append(f"  Patterns identified: {stats.get('patterns', 0)}")
            summary.append(f"  Timeline events: {stats.get('timeline_events', 0)}")
            summary.append(f"  Discoveries logged: {stats.get('discoveries', 0)}")
            summary.append("")
        
        # Critical findings
        critical_findings = context.get('critical_findings', [])
        if critical_findings:
            summary.append("CRITICAL FINDINGS SO FAR:")
            for i, finding in enumerate(critical_findings[:5], 1):
                finding_text = finding if isinstance(finding, str) else finding.get('content', 'Unknown')
                summary.append(f"  {i}. {finding_text[:200]}")
            
            if len(critical_findings) > 5:
                summary.append(f"  [...and {len(critical_findings) - 5} more critical findings]")
            summary.append("")
        
        # Active investigations
        investigations = context.get('active_investigations', [])
        if investigations:
            summary.append("ACTIVE INVESTIGATIONS:")
            for inv in investigations[:5]:
                inv_type = inv if isinstance(inv, str) else inv.get('type', 'Unknown')
                priority = inv.get('priority', 0.0) if isinstance(inv, dict) else 0.0
                summary.append(f"  • {inv_type} (priority: {priority:.1f})")
            
            if len(investigations) > 5:
                summary.append(f"  [...and {len(investigations) - 5} more investigations]")
            summary.append("")
        
        return "\n".join(summary) if summary else "No context available yet - beginning fresh analysis"


    def _format_investigation_triggers(self, triggers: List[Dict]) -> str:
        """Format investigation triggers for prompt"""
        
        if not triggers:
            return "No investigation triggers"
        
        formatted = []
        formatted.append("INVESTIGATION TRIGGERS:\n")
        
        for trigger in triggers[:10]:
            trigger_type = trigger.get('type', 'Unknown')
            priority = trigger.get('priority', 0.0)
            data = trigger.get('data', {})
            
            # Extract key info from trigger data
            if 'contradiction' in data:
                desc = data['contradiction'].get('implications', 'Contradiction detected')[:100]
            elif 'pattern' in data:
                desc = data['pattern'].get('description', 'Pattern detected')[:100]
            else:
                desc = str(data)[:100]
            
            formatted.append(f"  [{priority:.1f}] {trigger_type}: {desc}")
        
        if len(triggers) > 10:
            formatted.append(f"\n  [...and {len(triggers) - 10} more triggers]")
        
        return "\n".join(formatted)