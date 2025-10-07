#!/usr/bin/env python3
"""
Phase 0 Prompts - Deep Understanding Philosophy
Builds comprehensive case knowledge before tactical evidence hunting
British English throughout - Lismore v Process Holdings
"""

import json
from typing import Dict


class Phase0Prompts:
    """Phase 0: Build comprehensive case understanding for AI memory"""
    
    def __init__(self, config):
        self.config = config
    
    def build_stage_1_prompt(self, pleadings_text: str) -> str:
        """
        Stage 1: DEEP CASE UNDERSTANDING
        Goal: Comprehend the factual narrative, parties' positions, and context
        """
        
        return f"""<stage_1_mission>
STAGE 1: COMPREHENSIVE CASE UNDERSTANDING

You are strategic litigation counsel for Lismore in arbitration against Process Holdings (PH).

Your task: Build a complete, nuanced understanding of this case that will inform ALL subsequent analysis phases.

DO NOT think about evidence or documents yet. Just understand:
- What is the story each side tells?
- What are the competing factual narratives?
- What are the key events and their sequence?
- Who are the important actors and what roles did they play?
- What obligations existed and what allegedly went wrong?

This understanding will be the foundation for 4 subsequent analysis passes.
</stage_1_mission>

<pleadings_text>
{pleadings_text}
</pleadings_text>

<analysis_framework>
Build comprehensive understanding across these dimensions:

1. THE STORY (Factual Narrative)
   
   Tell me the story from BOTH perspectives:
   
   A. LISMORE'S NARRATIVE
   - What does Lismore say happened? (chronological story)
   - What was Lismore expecting/entitled to?
   - What went wrong from Lismore's perspective?
   - What damages/harm resulted?
   
   B. PH'S NARRATIVE  
   - What does PH say happened? (their version)
   - How does PH justify its actions/position?
   - What does PH say Lismore got wrong?
   - What alternative explanation does PH offer?
   
   C. POINTS OF FACTUAL AGREEMENT
   - What facts do both sides agree on?
   - What is undisputed?
   
   D. POINTS OF FACTUAL DISPUTE
   - Where do their stories diverge?
   - What specific facts are contested?

2. THE TRANSACTION/RELATIONSHIP
   
   What is the commercial context?
   - What type of transaction/relationship is this?
   - What was the business purpose?
   - What did each party hope to achieve?
   - What was the timeline of the relationship?
   - What money/value was involved?

3. THE PARTIES & KEY ACTORS
   
   Who are the important people and entities?
   - Corporate entities involved and their relationships
   - Key individuals and their roles
   - Decision-makers on each side
   - Advisers, consultants, third parties
   - Why does each person/entity matter to the story?

4. THE OBLIGATIONS & EXPECTATIONS
   
   What obligations existed (legal and commercial)?
   - Contractual obligations (from SPAs, agreements, etc.)
   - Warranties and representations given
   - Covenants and undertakings
   - Implied obligations or duties
   - What did each party expect from the other?

5. THE ALLEGED PROBLEMS
   
   What does Lismore say went wrong?
   For each allegation:
   - What obligation/expectation was breached?
   - What specifically happened (or didn't happen)?
   - When did this occur?
   - Why does Lismore say this matters?
   - What harm/damage resulted?
   
   Rate each allegation's centrality (1-10)

6. THE DEFENCES & COUNTER-ARGUMENTS
   
   How does PH respond?
   For each defence:
   - What is PH's position?
   - What legal or factual basis do they cite?
   - What alternative interpretation do they offer?
   - How strong does this defence appear?
   
   Rate each defence's strength (1-10)

7. THE TIMELINE
   
   What is the chronology of key events?
   - Pre-transaction events
   - Transaction completion
   - Post-transaction events
   - When problems emerged
   - Key dates both sides reference
   
   For each: date, what happened, why it matters

8. THE FINANCIAL DIMENSION
   
   What are the economic stakes?
   - Transaction value/purchase price
   - Amounts in dispute
   - Categories of claimed damages
   - Financial relationships
   - Economic context

9. THE LEGAL LANDSCAPE
   
   What legal issues are in play?
   - Types of claims
   - Legal tests that will apply
   - Burdens of proof
   - Remedies sought
   - Governing law

10. THE CORE TENSIONS
    
    What are the fundamental disagreements?
    - Knowledge vs. ignorance (who knew what when?)
    - Interpretation disputes
    - Causation disputes
    - Valuation disputes
    - Conduct disputes
</analysis_framework>

<critical_instructions>
- Use Extended Thinking extensively - take time to truly understand
- Think like a barrister getting briefed on a new case
- Focus on UNDERSTANDING not ADVOCATING (yet)
- Be precise about what is alleged vs. what is proven
- Note ambiguities and gaps in pleadings
- Build a mental model of how this case works
- Think: "If I had to explain this case to a colleague in 10 minutes, what would I say?"
</critical_instructions>

<output_format>
**Output valid JSON with this structure:**

{{
  "case_summary": "2-3 paragraph executive summary of what this case is fundamentally about",
  
  "lismore_narrative": {{
    "story": "Lismore's version of what happened (500 words)",
    "key_contentions": ["contention 1", "contention 2"],
    "desired_outcome": "What Lismore wants"
  }},
  
  "ph_narrative": {{
    "story": "PH's version of what happened (500 words)",
    "key_contentions": ["contention 1", "contention 2"],
    "desired_outcome": "What PH wants"
  }},
  
  "factual_disputes": [
    {{
      "dispute": "What is disputed",
      "lismore_position": "What Lismore says",
      "ph_position": "What PH says",
      "importance": 8
    }}
  ],
  
  "agreed_facts": ["fact 1", "fact 2"],
  
  "transaction_context": {{
    "type": "Type of transaction",
    "purpose": "Commercial purpose",
    "value": "Financial value",
    "timeline": "When this occurred"
  }},
  
  "key_parties": [
    {{
      "name": "Entity/person name",
      "role": "Their role",
      "significance": "Why they matter",
      "importance": 9
    }}
  ],
  
  "obligations": [
    {{
      "obligation": "Description",
      "source": "Contract clause or legal duty",
      "owed_by": "Who owed this",
      "owed_to": "Who it was owed to",
      "importance": 8
    }}
  ],
  
  "lismore_allegations": [
    {{
      "allegation": "What Lismore alleges",
      "obligation_breached": "What obligation was breached",
      "facts_alleged": "Key facts supporting this",
      "harm_claimed": "Damage that resulted",
      "centrality": 9
    }}
  ],
  
  "ph_defences": [
    {{
      "defence": "PH's defence",
      "legal_basis": "Legal principle",
      "factual_basis": "Facts PH relies on",
      "strength_assessment": 7
    }}
  ],
  
  "timeline": [
    {{
      "date": "YYYY-MM-DD",
      "event": "What happened",
      "significance": "Why this matters"
    }}
  ],
  
  "financial_picture": {{
    "transaction_value": "Amount",
    "amounts_in_dispute": ["amount 1", "amount 2"],
    "damage_categories": ["category 1", "category 2"]
  }},
  
  "legal_framework": {{
    "claim_types": ["breach of contract", "misrepresentation"],
    "legal_tests": ["test 1", "test 2"],
    "remedies_sought": ["remedy 1", "remedy 2"],
    "governing_law": "Jurisdiction"
  }},
  
  "core_tensions": [
    {{
      "tension": "Description of fundamental disagreement",
      "why_it_matters": "Why this is central"
    }}
  ]
}}

**Output ONLY valid JSON. Do not include any text before or after the JSON object.**
</output_format>

Begin your deep analysis now. Use Extended Thinking extensively.
Take your time to truly understand this case before analysing it.
"""

    def build_stage_2_prompt(self, stage_1_summary: Dict, tribunal_text: str) -> str:
        """
        Stage 2: LEGAL FRAMEWORK & PROOF REQUIREMENTS
        Goal: Understand what must be proven and what legal tests apply
        """
        
        # Extract context safely
        case_summary = stage_1_summary.get('case_summary', 'Unknown')[:400]
        claim_types = stage_1_summary.get('legal_framework', {}).get('claim_types', [])
        
        return f"""<stage_2_mission>
STAGE 2: LEGAL FRAMEWORK & PROOF REQUIREMENTS

You now understand the case narrative (Stage 1). Now understand the legal framework.

Your task: Analyse what must be PROVEN to succeed, and what the tribunal cares about.

This is about understanding:
- What legal elements must Lismore establish?
- What burden of proof applies?
- What defences are available to PH?
- What does the tribunal prioritise based on their rulings?
</stage_2_mission>

<case_foundation>
CASE SUMMARY:
{case_summary}

CLAIM TYPES:
{json.dumps(claim_types, indent=2)}
</case_foundation>

<tribunal_rulings>
{tribunal_text}
</tribunal_rulings>

<analysis_framework>
Build understanding of the legal framework:

1. LEGAL TESTS & ELEMENTS
   
   For each type of claim Lismore brings:
   
   A. What are the ELEMENTS that must be proven?
      (e.g., for breach of contract: contract exists, obligation defined, breach occurred, causation, damages)
   
   B. What is the BURDEN OF PROOF?
      (balance of probabilities, clear evidence, etc.)
   
   C. What EVIDENCE would typically establish each element?
      (not specific documents yet - categories of evidence)
   
   D. Where is Lismore's case STRONGEST?
      (which elements are easy to prove?)
   
   E. Where is Lismore's case WEAKEST?
      (which elements might be challenged?)

2. PH'S DEFENCES - LEGAL ANALYSIS
   
   For each defence PH raises:
   
   A. What must PH prove to succeed with this defence?
   B. What is the legal test for this defence?
   C. What would defeat this defence?
   D. How strong is this defence legally? (1-10)

3. TRIBUNAL PRIORITIES (from rulings)
   
   Read the tribunal's rulings strategically:
   
   A. WHAT ISSUES did the tribunal emphasise?
   - What did they spend time analysing?
   - What did they gloss over?
   - What concerns did they express?
   
   B. EVIDENTIARY STANDARDS
   - What materiality thresholds did they articulate?
   - What types of evidence did they find persuasive?
   - What did they order produced vs. refuse?
   
   C. PROCEDURAL SIGNALS
   - Did they favour one party's applications?
   - Did they express scepticism about anyone's position?
   - Did they impose costs or conditions?
   
   D. WHAT THIS TELLS US
   - What does the tribunal seem to care about?
   - Are there signs of which way they're leaning?
   - What priorities should this create for us?

4. PROOF REQUIREMENTS ANALYSIS
   
   Create a "proof map" for Lismore's case:
   
   For each major allegation:
   - Element 1: [What must be proven] → [Strength: X/10] → [Evidence category needed]
   - Element 2: [What must be proven] → [Strength: X/10] → [Evidence category needed]
   - Element 3: [What must be proven] → [Strength: X/10] → [Evidence category needed]
   
   Identify:
   - "Slam dunk" elements (easy to prove)
   - "Battle ground" elements (contested but provable)
   - "Vulnerable" elements (hard to prove)

5. GAPS & WEAKNESSES
   
   Based on legal framework:
   - Where are gaps in Lismore's pleaded case?
   - Where might PH successfully defend?
   - What facts would Lismore struggle to prove?
   - What alternative legal characterisations exist?

6. STRATEGIC LEGAL INSIGHTS
   
   High-level strategic observations:
   - What is the strongest legal theory for Lismore?
   - What is the weakest part of Lismore's case legally?
   - Where is PH most vulnerable legally?
   - What legal pivots or alternative arguments exist?
</analysis_framework>

<critical_instructions>
- Think like a legal analyst, not an advocate
- Be honest about Lismore's weaknesses
- Understand the legal tests precisely
- Consider what tribunal's rulings reveal
- Think about proof and evidence in CATEGORIES not specific documents
- Use Extended Thinking to reason through legal requirements
</critical_instructions>

<output_format>
**Output valid JSON:**

{{
  "legal_tests": [
    {{
      "claim_type": "Breach of contract",
      "elements_required": [
        {{
          "element": "Contract exists",
          "proof_required": "What must be shown",
          "strength": 10,
          "evidence_category": "Type of evidence needed"
        }}
      ],
      "burden_of_proof": "Standard that applies",
      "overall_strength": 8
    }}
  ],
  
  "ph_defences_analysis": [
    {{
      "defence": "Defence name",
      "legal_test": "What PH must prove",
      "how_to_defeat": "What would defeat this",
      "strength": 6
    }}
  ],
  
  "tribunal_priorities": {{
    "key_concerns": ["concern 1", "concern 2"],
    "evidentiary_preferences": ["preference 1", "preference 2"],
    "procedural_signals": ["signal 1", "signal 2"],
    "apparent_lean": "Neutral/Towards Lismore/Towards PH"
  }},
  
  "proof_map": [
    {{
      "allegation": "Allegation description",
      "elements": [
        {{
          "element": "What must be proven",
          "current_strength": 8,
          "evidence_category": "Type of evidence needed",
          "difficulty": "Easy/Moderate/Hard"
        }}
      ]
    }}
  ],
  
  "case_strengths": [
    {{
      "strength": "Description",
      "why": "Why this is strong"
    }}
  ],
  
  "case_weaknesses": [
    {{
      "weakness": "Description",
      "why": "Why this is weak",
      "mitigation": "How to address this"
    }}
  ],
  
  "strategic_insights": [
    "Insight 1",
    "Insight 2"
  ]
}}

**Output ONLY valid JSON.**
</output_format>

Begin your legal analysis now. Use Extended Thinking extensively.
"""

    def build_stage_3_prompt(self, stage_1_summary: Dict, stage_2_summary: Dict, admin_text: str) -> str:
        """
        Stage 3: EVIDENCE STRATEGY & DISCOVERY PRIORITIES
        Goal: NOW think about what evidence is needed and how to find it
        """
        
        # Extract context
        case_summary = stage_1_summary.get('case_summary', '')[:300]
        proof_map = stage_2_summary.get('proof_map', [])[:3]
        
        return f"""<stage_3_mission>
STAGE 3: EVIDENCE STRATEGY & DISCOVERY INTELLIGENCE

You now have:
✓ Stage 1: Deep case understanding (narratives, parties, timeline)
✓ Stage 2: Legal framework (what must be proven, tribunal priorities)

Now build the EVIDENCE STRATEGY:
- What categories of evidence are needed?
- What discovery priorities should guide Pass 1-4?
- What patterns should we look for in documents?

This creates the "search intelligence" for subsequent analysis passes.
</stage_3_mission>

<case_foundation>
CASE SUMMARY:
{case_summary}

PROOF MAP (Sample):
{json.dumps(proof_map, indent=2)[:800]}
</case_foundation>

<case_administration>
{admin_text}
</case_administration>

<analysis_framework>
Build comprehensive evidence strategy:

1. KEY ENTITIES & ACTORS (Refined with Chronology/Dramatis)
   
   From chronology + dramatis personae:
   - Who are the 15-20 most critical people?
   - What companies/entities are involved?
   - What are their relationships?
   - Why does each entity matter?
   - What documents would they appear in?

2. CRITICAL TIMELINE (Refined)
   
   Build definitive timeline with chronology:
   - Key dates in YYYY-MM-DD format
   - What happened on each date
   - Why this date matters
   - What evidence relates to this date
   
   Identify gaps: dates where evidence might be missing but needed

3. EVIDENCE CATEGORIES NEEDED
   
   For each major issue in the case:
   
   A. What TYPES of evidence would address this?
   B. What TIME PERIOD is relevant?
   C. Who would have CREATED/RECEIVED these documents?
   D. What TOPICS/KEYWORDS would these documents discuss?
   E. How CRITICAL is this category? (1-10)

4. DOCUMENT PATTERNS TO LOOK FOR
   
   Based on case understanding + legal requirements:
   
   Create 20-30 "document patterns" that describe categories of useful evidence.
   
   Each pattern should specify:
   - Pattern name (memorable)
   - What this pattern covers
   - Why this category matters (links to allegations/defences/elements)
   - Document characteristics:
     * Likely time period
     * Likely authors/recipients
     * Likely keywords/topics
     * Likely document types
     * Likely file locations
   - What this would prove/disprove
   - Priority (1-10)

5. EVIDENCE GAPS & UNKNOWNS
   
   What evidence might be missing or hard to get?
   - What documents might not exist?
   - What might have been verbal?
   - What might PH withhold?
   - What alternative evidence could fill gaps?

6. DISCOVERY PRIORITIES
   
   Strategic guidance for Passes 1-4:
   
   A. TIER 1 PRIORITIES (Must find)
   B. TIER 2 PRIORITIES (Very important)
   C. TIER 3 PRIORITIES (Nice to have)

7. PATTERN MATCHING GUIDANCE
   
   How should Pass 1 (triage) score documents?
   - What combinations indicate high relevance?
   - What red flags indicate critical documents?
   - What should be prioritised vs. deprioritised?
</analysis_framework>

<critical_instructions>
- Now you can think tactically about evidence
- Keep it at the PATTERN level, not specific documents
- Think: "What TYPES of documents would matter?"
- Create intelligence that Pass 1-4 can use for smart triage
- Be specific about characteristics but broad about categories
- Use chronology/dramatis to identify actual names and dates
- Priority reflects: relevance + likely to exist + likely to help Lismore
</critical_instructions>

<output_format>
**Output valid JSON:**

{{
  "key_entities": [
    {{
      "name": "Entity name",
      "role": "Their role",
      "importance": 9,
      "why_matters": "Why critical",
      "document_types": ["email", "board_minutes"]
    }}
  ],
  
  "critical_timeline": [
    {{
      "date": "YYYY-MM-DD",
      "event": "What happened",
      "significance": "Why matters",
      "evidence_types": ["Type 1", "Type 2"]
    }}
  ],
  
  "evidence_categories": [
    {{
      "category": "Category name",
      "description": "What this covers",
      "relevance": "What issue this addresses",
      "time_period": "When created",
      "key_people": ["Person 1", "Person 2"],
      "priority": 9
    }}
  ],
  
  "document_patterns": [
    {{
      "pattern_name": "Memorable name",
      "description": "What we're looking for",
      "why_matters": "Link to case issues",
      "characteristics": {{
        "date_range": "Time period",
        "authors_recipients": ["Role 1", "Person 1"],
        "keywords": ["keyword 1", "keyword 2"],
        "document_types": ["email", "board_minutes"],
        "file_types": [".msg", ".pdf"],
        "likely_folders": ["Folder 1", "Folder 2"]
      }},
      "proves_disproves": "What this establishes",
      "priority": 8
    }}
  ],
  
  "evidence_gaps": [
    {{
      "gap": "What might be missing",
      "why_problematic": "Why this matters",
      "alternative_evidence": "What could fill the gap"
    }}
  ],
  
  "discovery_priorities": {{
    "tier_1": ["Critical pattern 1", "Critical pattern 2"],
    "tier_2": ["Important pattern 1", "Important pattern 2"],
    "tier_3": ["Useful pattern 1", "Useful pattern 2"]
  }},
  
  "scoring_guidance": {{
    "high_priority_indicators": ["indicator 1", "indicator 2"],
    "red_flags": ["red flag 1", "red flag 2"],
    "prioritise": ["factor 1", "factor 2"],
    "deprioritise": ["factor 1", "factor 2"]
  }}
}}

**Output ONLY valid JSON.**
</output_format>

Begin your evidence strategy analysis now. Use Extended Thinking extensively.
"""