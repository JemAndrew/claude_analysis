#!/usr/bin/env python3
"""
Deliverables Generation Prompts
Generates tribunal-ready documents
British English throughout
"""

from typing import Dict
import json


class DeliverablesPrompts:
    """Prompts for generating tribunal deliverables"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_all_deliverables(self,
                                  intelligence: Dict,
                                  claims: Dict,
                                  strategy: Dict) -> str:
        """Generate all tribunal deliverables in one call"""
        
        prompt = f"""{self.config.hallucination_prevention}

<deliverables_mission>
Generate complete tribunal-ready deliverables for Lismore v Process Holdings.

You have completed your analysis. Now produce the work product that will be used at trial.
</deliverables_mission>

<complete_intelligence>
TIMELINE: {json.dumps(intelligence.get('timeline', []), indent=2)[:5000]}
BREACHES: {json.dumps(intelligence.get('breaches', []), indent=2)[:5000]}
EVIDENCE: {json.dumps(intelligence.get('evidence', []), indent=2)[:5000]}
PATTERNS: {json.dumps(intelligence.get('patterns', []), indent=2)[:3000]}
ENTITIES: {json.dumps(intelligence.get('entities', []), indent=2)[:3000]}
</complete_intelligence>

<claims>
{json.dumps(claims, indent=2)[:10000]}
</claims>

<strategy>
{json.dumps(strategy, indent=2)[:5000]}
</strategy>

<deliverables_required>

1. SCOTT SCHEDULE / CHRONOLOGY
   - Date | Event | Lismore's Position | PH's Position | Evidence
   - Chronological order
   - Focus on breach events

2. WITNESS STATEMENT OUTLINES
   For each witness:
   - Topics to cover
   - Key documents to reference
   - Questions to address

3. SKELETON ARGUMENT
   - Legal framework
   - Facts supporting each claim
   - Evidence references
   - Authorities

4. DISCLOSURE REQUESTS
   - Specific documents not yet disclosed
   - Justification for each request
   - Evidence they exist

5. OPENING SUBMISSIONS OUTLINE
   - Theme (one sentence)
   - Key 3-5 points
   - Evidence roadmap

6. EXPERT INSTRUCTION BRIEFS
   - Discipline required (financial, technical, etc.)
   - Questions for expert
   - Documents to review
</deliverables_required>

<quality_requirements>
- Every factual claim cited to specific document
- British English throughout
- Professional tribunal-ready formatting
- Concise but complete
- Focus on winning arguments
</quality_requirements>

Generate all deliverables now.
"""
        
        return prompt