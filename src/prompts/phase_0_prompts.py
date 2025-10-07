#!/usr/bin/env python3
"""
Phase 0 Prompts: Intelligent Case Foundation Building

CREATE AS: src/prompts/phase_0_prompts.py

British English - Lismore v Process Holdings - Acting for Lismore
"""

from typing import Dict, List


class Phase0Prompts:
    """Prompts for Phase 0 case foundation"""
    
    def build_stage_1_prompt(self, pleadings_text: str) -> str:
        """Stage 1: Understand the case from pleadings"""
        
        return f"""You are building case foundation for Lismore v Process Holdings arbitration.

CONTEXT:
Acting for LISMORE (Claimant). Your analysis guides £320 of AI document analysis.
Currently, AI scores documents BLINDLY. Your job: Give it context to recognise relevant documents.

PLEADINGS:
{pleadings_text}

EXTRACT FROM PLEADINGS:

1. CORE DISPUTE (200-300 words)
   What is this case about? What transaction? What breach? What remedy sought?

2. LISMORE'S ALLEGATIONS (5-10 points)
   Each allegation with specific clauses, amounts, dates

3. PH'S DEFENCES (5-10 points)
   Their counter-arguments

4. DISPUTED CLAUSES
   Clause number, Lismore's position, PH's position, centrality (1-10)

5. CRITICAL TIMELINE
   Key dates (YYYY-MM-DD), what happened, why it matters

6. KEY ENTITIES & AMOUNTS
   Companies, transactions, liabilities with actual amounts

7. SMOKING GUN CHARACTERISTICS
   What documents would prove Lismore's case?
   Example: "Emails from PH about [X] before [date]"

CRITICAL:
- Extract ONLY from pleadings - don't invent details
- Be specific with clause numbers, dates, amounts
- Think: what documents would prove/disprove allegations?

Respond in JSON format for easy parsing."""
    
    def build_stage_2_prompt(self, stage_1_summary: Dict, tribunal_text: str) -> str:
        """Stage 2: What does tribunal care about?"""
        
        core = stage_1_summary.get('core_dispute', 'N/A')[:300]
        
        return f"""Continuing Phase 0 for Lismore v Process Holdings.

STAGE 1 SUMMARY:
{core}

TRIBUNAL RULINGS:
{tribunal_text}

EXTRACT FROM RULINGS:

1. TRIBUNAL SIGNALS
   What issues does tribunal emphasise?
   Quote specific paragraphs
   How does this impact discovery strategy?

2. PROCEDURAL PRIORITIES
   What has tribunal focused on?
   What did they rule?
   Does this help Lismore or PH?

3. EVIDENTIARY STANDARDS
   Materiality thresholds?
   Burden of proof interpretations?

4. TRIBUNAL CONCERNS
   Has tribunal questioned PH's conduct?
   Expressed scepticism?

5. KEY DEADLINES
   Upcoming disclosure/evidence deadlines

CRITICAL:
- Extract from ACTUAL rulings
- Quote paragraphs
- Note patterns: does tribunal favour one party?

Respond in JSON format."""
    
    def build_stage_3_prompt(self, stage_1_summary: Dict, stage_2_summary: Dict, admin_text: str) -> str:
        """Stage 3: What documents to look for?"""
        
        core = stage_1_summary.get('core_dispute', 'N/A')[:200]
        
        return f"""Final Phase 0 stage for Lismore v Process Holdings.

CASE SUMMARY:
{core}

CHRONOLOGY & DRAMATIS PERSONAE:
{admin_text}

IDENTIFY SMOKING GUN PATTERNS:

1. SMOKING GUN PATTERNS (5-10)
   For each:
   - Document type
   - Why devastating?
   - Search terms
   - Date range
   - Key people involved
   - Red flags (subject lines, phrases)
   - Impact level (1-10)

2. KEY ENTITIES (5-10)
   - Name and aliases
   - Type (liability/transaction/company)
   - Amount
   - Why critical

3. CRITICAL DATES (10-15)
   - Date (YYYY-MM-DD)
   - Event
   - Search priority (1-10)
   - What documents from this period would prove?

4. KEY INDIVIDUALS (5-10)
   - Name (from dramatis personae)
   - Role
   - Why critical
   - What docs from/to them would show?

5. CONTRADICTION PATTERNS
   - Witness statement vs email
   - How to spot
   - Impact

6. PRIORITISATION RULES (5-10)
   - If doc mentions X and Y → Priority level
   - Rationale

CRITICAL:
- Be SPECIFIC: "emails from CFO about X in June 2023"
- Extract names from dramatis personae
- Use dates from chronology
- What are the KILLER documents?

Respond in JSON format."""
    
    def _format_list(self, items: List) -> str:
        """Helper to format lists"""
        if not items:
            return "(None)"
        if isinstance(items, list):
            return ", ".join(str(item)[:100] for item in items[:3])
        return str(items)[:200]