#!/usr/bin/env python3
"""
Synthesis and Narrative Building Prompts
Combines findings into powerful litigation strategy
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class SynthesisPrompts:
    """Prompts for synthesising findings into winning narratives"""
    
    def __init__(self, config):
        self.config = config
    
    def narrative_construction_prompt(self,
                                     findings: Dict,
                                     contradictions: List[Dict],
                                     patterns: Dict,
                                     timeline: Dict,
                                     entities: Dict) -> str:
        """
        Build compelling narrative from discovered evidence
        """
        
        prompt = f"""<narrative_mission>
Construct the devastating narrative that wins Lismore v Process Holdings.
Transform evidence into a story that compels victory.
</narrative_mission>

<available_evidence>
Critical Findings: {len(findings.get('critical', []))}
Contradictions: {len(contradictions)}
Established Patterns: {len(patterns)}
Timeline Events: {len(timeline)}
Key Entities: {len(entities)}
</available_evidence>

<narrative_requirements>
Your narrative must be:

LEGALLY DEVASTATING
- Every claim supported by documentary evidence
- Anticipate and destroy their defences
- Establish clear liability
- Quantify damages precisely

EMOTIONALLY COMPELLING
- Heroes: Lismore (betrayed partner)
- Villains: Process Holdings (deceitful operators)
- Theme: Breach of trust, conspiracy, greed
- Resolution: Justice demands compensation

STRUCTURALLY PERFECT
1. THE PROMISE (What Process Holdings agreed to)
2. THE CONSPIRACY (How they planned to breach)
3. THE BETRAYAL (How they executed their plan)
4. THE COVER-UP (How they tried to hide it)
5. THE DISCOVERY (How their deception unraveled)
6. THE RECKONING (Why they must pay)
</narrative_requirements>

<key_findings>
{json.dumps(findings, indent=2)[:5000]}
</key_findings>

<critical_contradictions>
{self._format_contradictions_for_narrative(contradictions[:10])}
</critical_contradictions>

<established_patterns>
{self._format_patterns_for_narrative(patterns)}
</established_patterns>

<timeline_events>
{self._format_timeline_for_narrative(timeline)}
</timeline_events>

<construction_instructions>
Build the narrative that destroys their position:

OPENING STATEMENT (The Promise):
- Set the scene of trust and agreement
- Establish Lismore's reasonable expectations
- Show Process Holdings' commitments

DEVELOPMENT (The Conspiracy & Betrayal):
- Present evidence chronologically
- Build tension with each revelation
- Deploy contradictions devastatingly
- Highlight pattern evidence

CLIMAX (The Smoking Gun):
- Present your most damaging evidence
- Show intentional deception
- Prove conspiracy/coordination
- Demonstrate damages

CLOSING (The Reckoning):
- Summarise the betrayal
- Quantify the harm
- Demand justice
- Make settlement/verdict inevitable

Use document references [DOC_XXXX] for every claim.
Make them feel the betrayal. Make the tribunal angry at their conduct.
Build inexorable momentum toward liability.
</construction_instructions>"""
        
        return prompt
    
    def strategic_synthesis_prompt(self,
                                 phase_analyses: Dict[str, str],
                                 investigations: List[Dict],
                                 knowledge_graph_export: Dict) -> str:
        """
        Synthesise all findings into strategic recommendations
        """
        
        prompt = f"""<strategic_synthesis_mission>
Synthesise all intelligence into actionable litigation strategy.
Transform analysis into victory.
</strategic_synthesis_mission>

<intelligence_summary>
Phases Completed: {len(phase_analyses)}
Investigations Conducted: {len(investigations)}
Entities Identified: {knowledge_graph_export.get('summary', {}).get('entities', 0)}
Contradictions Found: {knowledge_graph_export.get('summary', {}).get('contradictions', 0)}
Patterns Established: {knowledge_graph_export.get('summary', {}).get('patterns', 0)}
</intelligence_summary>

<phase_key_findings>
{self._summarise_phases(phase_analyses)}
</phase_key_findings>

<investigation_outcomes>
{self._summarise_investigations(investigations[:10])}
</investigation_outcomes>

<critical_discoveries>
{json.dumps(knowledge_graph_export.get('critical_findings', [])[:10], indent=2)[:3000]}
</critical_discoveries>

<strategic_synthesis_requirements>
Provide comprehensive strategic assessment:

1. WINNING ARGUMENTS (Rank by strength)
   - Primary claim with evidence
   - Alternative claims
   - Defensive positions
   - Counter-arguments to anticipate

2. CRITICAL EVIDENCE (By importance)
   - Documents that prove liability
   - Witnesses needed
   - Expert opinions required
   - Missing evidence to obtain

3. VULNERABILITIES ANALYSIS
   OUR VULNERABILITIES:
   - Weak points in our case
   - Evidence gaps
   - Mitigation strategies
   
   THEIR VULNERABILITIES:
   - Exposed contradictions
   - Indefensible positions
   - Pressure points

4. SETTLEMENT LEVERAGE
   - Nuclear options available
   - Negotiation ammunition
   - Walk-away alternatives
   - Optimal settlement range

5. TRIAL STRATEGY
   - Opening statement themes
   - Witness examination priorities
   - Document presentation order
   - Closing argument structure

6. IMMEDIATE ACTIONS (Next 48 hours)
   - Evidence to secure
   - Witnesses to interview
   - Experts to engage
   - Procedural moves

7. CONTINGENCY PLANNING
   - If they do X, we do Y scenarios
   - Surprise evidence responses
   - Alternative strategies
</strategic_synthesis_requirements>

<output_format>
Structure your synthesis for maximum clarity:

EXECUTIVE SUMMARY
- Bottom line assessment
- Probability of success (%)
- Recommended approach

DETAILED ANALYSIS
[Organised by sections above]

RISK MATRIX
- High/Medium/Low risks
- Mitigation strategies

DECISION POINTS
- Key strategic decisions needed
- Recommended choices
- Timeline for decisions
</output_format>

Synthesise with precision. Think strategically. Plan for victory.
"""
        
        return prompt
    
    def report_generation_prompt(self,
                               report_type: str,
                               content: Dict,
                               audience: str = "legal_team") -> str:
        """
        Generate polished reports from analysis
        """
        
        report_configs = {
            'executive': {
                'tone': 'decisive, confident',
                'length': 'concise',
                'focus': 'decisions and outcomes'
            },
            'legal_team': {
                'tone': 'thorough, technical',
                'length': 'comprehensive',
                'focus': 'evidence and strategy'
            },
            'expert': {
                'tone': 'analytical, objective',
                'length': 'detailed',
                'focus': 'methodology and findings'
            },
            'settlement': {
                'tone': 'firm, reasonable',
                'length': 'moderate',
                'focus': 'liability and damages'
            }
        }
        
        config = report_configs.get(audience, report_configs['legal_team'])
        
        prompt = f"""<report_generation>
Generate {report_type} report for {audience}.
Tone: {config['tone']}
Length: {config['length']}
Focus: {config['focus']}
</report_generation>

<content>
{json.dumps(content, indent=2)[:10000]}
</content>

<report_requirements>
Include:

EXECUTIVE SUMMARY
- Key findings in bullet points
- Strategic recommendations
- Critical actions required

DETAILED FINDINGS
- Organised by importance
- Evidence references
- Confidence levels

STRATEGIC ANALYSIS
- Strengths of position
- Risks and mitigation
- Recommended approach

EVIDENCE SUMMARY
- Critical documents
- Key contradictions
- Pattern analysis

NEXT STEPS
- Immediate actions
- Timeline
- Resource requirements

APPENDICES (if needed)
- Supporting documentation
- Detailed timelines
- Entity relationships
</report_requirements>

Write with authority. Be precise. Drive action.
"""
        
        return prompt
    
    def war_room_dashboard_prompt(self,
                                 current_status: Dict,
                                 critical_findings: List,
                                 active_investigations: List,
                                 strategic_options: Dict) -> str:
        """
        Generate executive war room dashboard
        """
        
        prompt = f"""<war_room_requirement>
Create executive war room dashboard for Lismore v Process Holdings.
This drives immediate strategic decisions.
</war_room_requirement>

<current_status>
{json.dumps(current_status, indent=2)[:2000]}
</current_status>

<dashboard_sections>

1. CASE STATUS SNAPSHOT
   □ Overall position strength (1-10)
   □ Settlement leverage (1-10)
   □ Trial readiness (%)
   □ Critical risks

2. TODAY'S CRITICAL FINDINGS
   {self._format_critical_findings(critical_findings[:5])}

3. ACTIVE OPERATIONS
   {self._format_active_investigations(active_investigations[:5])}

4. STRATEGIC OPTIONS
   NUCLEAR OPTIONS:
   - [Case-ending moves available]
   
   PRESSURE POINTS:
   - [Where to apply pressure now]
   
   DEFENSIVE REQUIREMENTS:
   - [What to protect against]

5. 48-HOUR PRIORITIES
   MUST DO:
   - [Non-negotiable actions]
   
   SHOULD DO:
   - [High-value actions]
   
   COULD DO:
   - [Opportunistic actions]

6. KEY METRICS
   Documents Analysed: {current_status.get('documents_analysed', 0)}
   Contradictions Found: {current_status.get('contradictions', 0)}
   Patterns Confirmed: {current_status.get('patterns', 0)}
   Investigation Threads: {len(active_investigations)}

7. DECISION REQUIREMENTS
   IMMEDIATE DECISIONS NEEDED:
   - [Decision 1: Options A/B/C]
   - [Decision 2: Options X/Y/Z]

8. WIN PROBABILITY
   Current Assessment: X%
   Trend: ↑/→/↓
   Key Factors:
   - [Factor affecting probability]

9. RECOMMENDED STRATEGY
   PRIMARY: [Aggressive litigation/Settlement/Hybrid]
   RATIONALE: [Why this strategy]
   TIMELINE: [Key milestones]

10. WILD CARDS
    GAME CHANGERS WE'RE PURSUING:
    - [High-risk/high-reward plays]
    
    WHAT KEEPS THEM AWAKE:
    - [Their biggest fears]
</dashboard_sections>

Create dashboard for immediate executive consumption.
Be direct. Be actionable. Drive decisions.
"""
        
        return prompt
    
    def _format_contradictions_for_narrative(self, contradictions: List[Dict]) -> str:
        """Format contradictions for narrative building"""
        formatted = []
        for cont in contradictions:
            formatted.append(
                f"CONTRADICTION (Severity {cont.get('severity', 0)}/10):\n"
                f"They claimed: {cont.get('statement_a', '')[:200]}\n"
                f"But also said: {cont.get('statement_b', '')[:200]}\n"
                f"Implication: {cont.get('implications', 'Deception')}\n"
            )
        return "\n".join(formatted)
    
    def _format_patterns_for_narrative(self, patterns: Dict) -> str:
        """Format patterns for narrative building"""
        formatted = []
        for pattern_id, pattern in list(patterns.items())[:10]:
            formatted.append(
                f"PATTERN: {pattern.get('description', pattern_id)}\n"
                f"Confidence: {pattern.get('confidence', 0):.1%}\n"
                f"Evidence: {len(pattern.get('supporting_evidence', []))} items\n"
            )
        return "\n".join(formatted)
    
    def _format_timeline_for_narrative(self, timeline: Dict) -> str:
        """Format timeline events for narrative"""
        formatted = []
        for date in sorted(timeline.keys())[:20]:
            events = timeline[date]
            for event in events[:2]:  # Max 2 events per date
                formatted.append(f"{date}: {event}")
        return "\n".join(formatted)
    
    def _summarise_phases(self, phase_analyses: Dict[str, str]) -> str:
        """Summarise key findings from each phase"""
        formatted = []
        for phase, analysis in phase_analyses.items():
            # Extract first 500 chars as summary
            summary = analysis[:500] if analysis else "No analysis"
            formatted.append(f"PHASE {phase}:\n{summary}...\n")
        return "\n".join(formatted)
    
    def _summarise_investigations(self, investigations: List[Dict]) -> str:
        """Summarise investigation outcomes"""
        formatted = []
        for inv in investigations:
            formatted.append(
                f"INVESTIGATION: {inv.get('type', 'Unknown')}\n"
                f"Priority: {inv.get('priority', 0)}\n"
                f"Key Finding: {str(inv.get('findings', {}))[:200]}\n"
            )
        return "\n".join(formatted)
    
    def _format_critical_findings(self, findings: List) -> str:
        """Format critical findings for dashboard"""
        formatted = []
        for i, finding in enumerate(findings, 1):
            formatted.append(
                f"{i}. {finding.get('content', '')[:150]}\n"
                f"   Importance: {finding.get('importance', 'HIGH')}"
            )
        return "\n".join(formatted)
    
    def _format_active_investigations(self, investigations: List) -> str:
        """Format active investigations for dashboard"""
        formatted = []
        for inv in investigations:
            formatted.append(
                f"• {inv.get('type', 'Unknown')} "
                f"(Priority: {inv.get('priority', 0):.1f})"
            )
        return "\n".join(formatted)