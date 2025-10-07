#!/usr/bin/env python3
"""
Phase 0 Prompts - Production-Ready with Robust Parsing
British English throughout - Acting for Lismore v Process Holdings

Location: src/prompts/phase_0_prompts.py

Philosophy:
- Understand → Analyse → Strategise
- Extract what EXISTS (no hallucinations)
- Simple output format for reliable parsing
- Knowledge retention for all subsequent passes
"""

import json
from typing import Dict


class Phase0Prompts:
    """Phase 0: Build comprehensive case understanding for AI memory"""
    
    def __init__(self, config):
        """
        Initialise Phase 0 prompts
        
        Args:
            config: Config object with system settings
        """
        self.config = config
    
    def build_stage_1_prompt(self, pleadings_text: str) -> str:
        """
        Stage 1: Deep case understanding from pleadings
        Returns: Case narrative, parties, disputes, obligations, timeline
        
        Args:
            pleadings_text: Combined text from all pleadings documents
            
        Returns:
            Formatted prompt string for Stage 1 analysis
        """
        
        return f"""You are strategic litigation counsel for Lismore in LCIA arbitration against Process Holdings (PH).

**YOUR MISSION: Build comprehensive case understanding from pleadings**

This understanding will power all subsequent analysis passes (1-4).

**ANTI-HALLUCINATION RULES:**
- Extract ONLY what is ACTUALLY PRESENT in the documents
- If 3 parties mentioned → list 3. If 50 mentioned → list 50
- DO NOT invent facts to meet quotas
- If uncertain → say "Not clearly established in pleadings"
- Quality over quantity: 3 accurate > 20 guessed

---

<pleadings>
{pleadings_text}
</pleadings>

---

**ANALYSE THE CASE ACROSS THESE DIMENSIONS:**

## 1. CASE SUMMARY (2-3 paragraphs)
Executive summary: What is this dispute about? What does each side want?

## 2. LISMORE'S NARRATIVE
Tell Lismore's story chronologically:
- What transaction/relationship is this?
- What did Lismore expect/receive?
- What went wrong?
- What harm resulted?

## 3. PH'S NARRATIVE
Tell PH's version:
- How does PH characterise the relationship?
- What does PH say Lismore got wrong?
- What justifications does PH offer?

## 4. KEY PARTIES & ENTITIES
List ONLY parties ACTUALLY MENTIONED and their roles:
- Name
- Role (e.g. "Claimant", "Target company", "Financial adviser")  
- Why they matter

## 5. FACTUAL DISPUTES
What specific facts are contested between the parties?
- Disputed fact
- Lismore's position
- PH's position
- Why this matters

## 6. AGREED FACTS
What facts are undisputed?

## 7. OBLIGATIONS & DUTIES
What obligations existed (list ONLY those discussed)?
- Obligation description
- Source (contract clause, statute, etc.)
- Whether disputed or accepted

## 8. LISMORE'S ALLEGATIONS
What specific wrongdoing does Lismore allege?
- Allegation description
- Which obligation allegedly breached
- Evidence cited (if any)

## 9. PH'S DEFENCES
How does PH respond?
- Defence type (denial, justification, legal defence)
- PH's argument
- Strength (strong/moderate/weak based on pleadings)

## 10. TIMELINE
Key events in chronological order (ONLY events mentioned):
- Date (YYYY-MM-DD or "Month YYYY")
- Event description
- Significance

## 11. FINANCIAL CLAIMS
- What amounts are claimed?
- How are they calculated?
- What does PH say about quantum?

---

**OUTPUT FORMAT:**

Provide your analysis in this EXACT structure for reliable parsing:

```
CASE_SUMMARY_START
[Your 2-3 paragraph executive summary]
CASE_SUMMARY_END

LISMORE_NARRATIVE_START
[Lismore's story - 3-5 paragraphs]
LISMORE_NARRATIVE_END

PH_NARRATIVE_START
[PH's story - 3-5 paragraphs]
PH_NARRATIVE_END

KEY_PARTIES_START
- Entity: [Name] | Role: [Role] | Significance: [Why they matter]
- Entity: [Name] | Role: [Role] | Significance: [Why they matter]
[Continue for all parties ACTUALLY mentioned]
KEY_PARTIES_END

FACTUAL_DISPUTES_START
- Dispute: [Description] | Lismore says: [Position] | PH says: [Position] | Significance: [Why it matters]
[Continue for all disputes identified]
FACTUAL_DISPUTES_END

AGREED_FACTS_START
- [Undisputed fact 1]
- [Undisputed fact 2]
[Continue]
AGREED_FACTS_END

OBLIGATIONS_START
- Obligation: [Description] | Source: [Contract clause/statute] | Status: [Disputed/Accepted]
[Continue for obligations ACTUALLY mentioned]
OBLIGATIONS_END

ALLEGATIONS_START
- Allegation: [What PH allegedly did wrong] | Obligation breached: [Which duty] | Evidence: [Documents cited if any]
[Continue for allegations identified]
ALLEGATIONS_END

DEFENCES_START
- Defence: [PH's response] | Type: [Denial/Justification/Legal] | Strength: [Strong/Moderate/Weak]
[Continue for defences identified]
DEFENCES_END

TIMELINE_START
- Date: [YYYY-MM-DD] | Event: [What happened] | Significance: [Why it matters]
[Continue chronologically]
TIMELINE_END

FINANCIAL_CLAIMS_START
- Claim: [Description] | Amount: [£X] | Calculation: [How derived] | PH response: [PH's position]
[Continue for all financial claims]
FINANCIAL_CLAIMS_END
```

**CRITICAL:** Use the exact delimiters (CASE_SUMMARY_START, etc.) for reliable parsing.

Begin your analysis now."""

    def build_stage_2_prompt(self, stage_1_summary: Dict, tribunal_text: str) -> str:
        """
        Stage 2: Legal framework and proof requirements
        Returns: Legal tests, proof elements, tribunal priorities, case strengths/weaknesses
        
        Args:
            stage_1_summary: Parsed results from Stage 1 analysis
            tribunal_text: Combined text from tribunal rulings
            
        Returns:
            Formatted prompt string for Stage 2 analysis
        """
        
        # Extract key context from Stage 1
        case_summary = stage_1_summary.get('case_summary', 'Unknown case')[:500]
        allegations = stage_1_summary.get('allegations', [])
        allegation_summary = f"Lismore alleges {len(allegations)} breaches" if allegations else "Allegations unclear"
        
        return f"""You are strategic litigation counsel for Lismore in LCIA arbitration against Process Holdings.

**YOUR MISSION: Analyse the legal framework and proof requirements**

You now understand the case narrative (Stage 1). Now determine:
- What legal tests apply?
- What must Lismore PROVE to succeed?
- What does the tribunal prioritise?
- Where is the case strong/weak?

---

**STAGE 1 CONTEXT:**

{case_summary}

Summary: {allegation_summary}

---

**TRIBUNAL RULINGS:**

{tribunal_text}

---

**ANALYSE ACROSS THESE DIMENSIONS:**

## 1. CLAIM TYPES & LEGAL TESTS
For EACH type of claim Lismore brings (e.g. breach of contract, misrepresentation, breach of warranty):

- Claim type
- Elements required to prove this claim
- Burden of proof
- Evidence categories typically needed for each element

## 2. PROOF MAP
For Lismore's key allegations, map what must be proven:

- Allegation
- Legal element it relates to
- What evidence would establish this
- Current strength (based on pleadings: Strong/Moderate/Weak/Uncertain)

## 3. PH'S DEFENCES - LEGAL ANALYSIS
For each defence PH raises:

- Defence type
- What PH must prove
- What would defeat this defence
- Strength assessment

## 4. TRIBUNAL PRIORITIES (from rulings)
What does the tribunal care about based on their orders?

- Issues emphasised
- Evidentiary standards mentioned
- Procedural signals (any party favoured?)
- Cost orders or conditions imposed

## 5. CASE STRENGTHS (for Lismore)
Where is Lismore's case strongest?

- Strong element
- Why it's strong
- Supporting factors

## 6. CASE WEAKNESSES (for Lismore)
Where is Lismore vulnerable?

- Weak element
- Why it's problematic
- How to mitigate

---

**OUTPUT FORMAT:**

Use this EXACT structure for reliable parsing:

```
LEGAL_TESTS_START
Claim: [Type] | Elements: [Element 1, Element 2, Element 3] | Burden: [Standard] | Evidence needed: [Categories]
[Continue for each claim type]
LEGAL_TESTS_END

PROOF_MAP_START
Allegation: [Description] | Legal element: [Which element] | Evidence required: [What would prove this] | Current strength: [Strong/Moderate/Weak]
[Continue for key allegations]
PROOF_MAP_END

PH_DEFENCES_LEGAL_START
Defence: [Type] | PH must prove: [Requirements] | Defeat by: [Counter-strategy] | Strength: [Assessment]
[Continue for each defence]
PH_DEFENCES_LEGAL_END

TRIBUNAL_PRIORITIES_START
Priority: [Issue] | Why: [Tribunal's stated concern] | Impact: [What this means for strategy]
[Continue for priorities identified]
TRIBUNAL_PRIORITIES_END

CASE_STRENGTHS_START
- Strength: [Element/issue] | Why: [Explanation] | Support: [Factors]
[Continue]
CASE_STRENGTHS_END

CASE_WEAKNESSES_START
- Weakness: [Element/issue] | Why: [Problem] | Mitigation: [How to address]
[Continue]
CASE_WEAKNESSES_END
```

**CRITICAL:** Use exact delimiters for reliable parsing.

Begin your legal framework analysis now."""

    def build_stage_3_prompt(self, stage_1_summary: Dict, stage_2_summary: Dict, admin_text: str) -> str:
        """
        Stage 3: Evidence strategy and document patterns
        Returns: Key entities, critical dates, document patterns, evidence priorities
        
        Args:
            stage_1_summary: Parsed results from Stage 1 analysis
            stage_2_summary: Parsed results from Stage 2 analysis
            admin_text: Combined text from chronology and dramatis personae
            
        Returns:
            Formatted prompt string for Stage 3 analysis
        """
        
        # Extract context
        case_summary = stage_1_summary.get('case_summary', 'Unknown')[:400]
        num_allegations = len(stage_1_summary.get('allegations', []))
        num_legal_tests = len(stage_2_summary.get('legal_tests', []))
        
        return f"""You are strategic litigation counsel for Lismore in LCIA arbitration against Process Holdings.

**YOUR MISSION: Build evidence strategy and document discovery intelligence**

You now have:
✓ Stage 1: Case understanding (narrative, parties, disputes)
✓ Stage 2: Legal framework ({num_legal_tests} legal tests, proof requirements)

Now create the EVIDENCE STRATEGY to guide document analysis in Passes 1-4.

---

**CASE FOUNDATION:**

{case_summary}

Lismore alleges: {num_allegations} breaches
Legal tests to satisfy: {num_legal_tests}

---

**CASE ADMINISTRATION (Chronology/Dramatis Personae):**

{admin_text}

---

**BUILD EVIDENCE STRATEGY:**

## 1. KEY ENTITIES & PEOPLE
From chronology/dramatis, who are the MOST IMPORTANT entities?

For each key entity:
- Name
- Role in the case
- Why they matter (what would their documents show?)
- Priority for document search (1-10)

## 2. CRITICAL TIMELINE
Key dates that evidence should cluster around:

- Date (YYYY-MM-DD)
- Event
- Why documents from this period matter
- Priority (1-10)

## 3. EVIDENCE CATEGORIES NEEDED
For major issues, what categories of evidence are required?

- Issue/allegation
- Evidence category needed (e.g. "board minutes", "financial statements", "correspondence with advisers")
- Time period relevant
- Likely creators/recipients
- What this would prove
- Priority (1-10)

## 4. DOCUMENT PATTERNS (for Pass 1 scoring)
Create document patterns that describe high-value evidence categories.

Each pattern should specify:
- Pattern name (memorable, e.g. "Grace Taiga corruption concerns")
- Why this matters (links to which allegation/defence/element)
- Document characteristics:
  * Likely keywords/topics
  * Likely authors/recipients
  * Likely time period
  * Likely document types
- What this would prove/disprove
- Priority score (1-10)

**GUIDANCE:** Create patterns that are:
- Specific enough to identify relevant documents
- Broad enough to catch variants
- Tied to specific legal elements or allegations
- Based on ACTUAL case issues (not generic)

## 5. EVIDENCE GAPS & RISKS
What evidence might be missing or problematic?

- Gap description
- Why this is problematic
- Alternative evidence that could fill this gap
- Risk level (High/Medium/Low)

---

**OUTPUT FORMAT:**

Use this EXACT structure:

```
KEY_ENTITIES_START
- Name: [Entity name] | Role: [Their role] | Significance: [Why their documents matter] | Priority: [1-10]
[Continue for all key entities identified]
KEY_ENTITIES_END

CRITICAL_TIMELINE_START
- Date: [YYYY-MM-DD] | Event: [What happened] | Why: [Why documents matter here] | Priority: [1-10]
[Continue chronologically]
CRITICAL_TIMELINE_END

EVIDENCE_CATEGORIES_START
- Issue: [Allegation/element] | Category: [Type of evidence] | Period: [Timeframe] | Creators: [Who made these] | Proves: [What it establishes] | Priority: [1-10]
[Continue]
EVIDENCE_CATEGORIES_END

DOCUMENT_PATTERNS_START
- Pattern: [Name] | Matters because: [Links to case element] | Keywords: [Topic words] | Likely authors: [People] | Time period: [Dates] | Doc types: [Types] | Would prove: [What] | Priority: [1-10]
[Continue for all patterns - create as many as are ACTUALLY relevant based on case issues]
DOCUMENT_PATTERNS_END

EVIDENCE_GAPS_START
- Gap: [Missing evidence] | Problematic because: [Why] | Alternatives: [Other evidence] | Risk: [High/Medium/Low]
[Continue]
EVIDENCE_GAPS_END
```

**CRITICAL:** Use exact delimiters. Create patterns based on ACTUAL case issues, not generic categories.

**NO HALLUCINATION:** If chronology is sparse, that's fine - extract what's there. Don't invent dates/events.

Begin your evidence strategy analysis now."""