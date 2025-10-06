#!/usr/bin/env python3
"""
Maximum Quality Deliverables Generation
- Uses all Pass 2 intelligence (breaches, contradictions, novel arguments)
- Uses evidence maps for precise citations
- Generates each deliverable separately for maximum quality
- Adversarial Lismore-sided framing throughout
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List
import json


class DeliverablesPrompts:
    """Prompts for generating tribunal-ready deliverables"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_all_deliverables(self,
                                  intelligence: Dict,
                                  claims: Dict,
                                  strategy: Dict,
                                  evidence_map: Dict = None) -> str:
        """
        Generate ALL tribunal deliverables in one comprehensive call
        MAXIMUM QUALITY: Uses all Pass 2 findings
        """
        
        # Extract Pass 2 intelligence
        breaches = intelligence.get('breaches', [])
        contradictions = intelligence.get('contradictions', [])
        timeline = intelligence.get('timeline', [])
        patterns = intelligence.get('patterns', [])
        novel_arguments = intelligence.get('novel_arguments', [])
        opponent_weaknesses = intelligence.get('opponent_weaknesses', [])
        
        prompt = f"""{self.config.hallucination_prevention}

<deliverables_mission>
Generate complete tribunal-ready deliverables for Lismore v Process Holdings arbitration.

WE ARE ARGUING FOR LISMORE.
You are preparing work product that will be used at the tribunal to WIN this arbitration.

YOUR ANALYSIS IDENTIFIED:
- {len(breaches)} breaches by Process Holdings
- {len(contradictions)} contradictions in PH's evidence  
- {len(timeline)} timeline events mapped
- {len(novel_arguments)} novel arguments neither side has made
- {len(opponent_weaknesses)} weaknesses in PH's case

Now produce the tribunal documents that exploit these findings to WIN.
</deliverables_mission>

<complete_pass_2_intelligence>

BREACHES IDENTIFIED:
{json.dumps(breaches[:30], indent=2)[:20000]}

CONTRADICTIONS FOUND:
{json.dumps(contradictions[:20], indent=2)[:15000]}

TIMELINE OF KEY EVENTS:
{json.dumps(timeline[:50], indent=2)[:15000]}

NOVEL ARGUMENTS (our secret weapons - PH hasn't prepared for these):
{json.dumps(novel_arguments[:15], indent=2)[:10000]}

OPPONENT WEAKNESSES (vulnerabilities to exploit):
{json.dumps(opponent_weaknesses[:15], indent=2)[:10000]}

PATTERNS IDENTIFIED:
{json.dumps(patterns[:20], indent=2)[:10000]}

</complete_pass_2_intelligence>

<evidence_cross_reference_map>
{json.dumps(evidence_map, indent=2)[:15000] if evidence_map else 'No evidence map available'}

This map shows which documents support which claims.
CRITICAL: Every factual assertion in deliverables MUST cite specific documents from this map or the intelligence above.
</evidence_cross_reference_map>

<claims_with_strength_ratings>
{json.dumps(claims, indent=2)[:15000]}

These are the legal claims with quantified strength ratings.
Focus tribunal documents on strongest claims (strength > 0.7).
Minimise or reframe weakest claims (strength < 0.5).
</claims_with_strength_ratings>

<strategic_guidance>
{json.dumps(strategy, indent=2)[:8000]}

STRONGEST CLAIMS: Lead with these at tribunal
WEAKEST AREAS: Reframe or minimise these
NOVEL ARGUMENTS: These are our tactical advantage - PH hasn't prepared defences
OPPONENT WEAKNESSES: Exploit these aggressively in cross-examination and submissions
</strategic_guidance>

<deliverables_to_generate>

Generate ALL SIX tribunal deliverables below.
Use the EXACT section headers shown so parsing works correctly.

═══════════════════════════════════════════════════════════════════

1. SCOTT SCHEDULE / CHRONOLOGY

Create a comprehensive chronology table:

| Date | Event Description | Lismore's Position | PH's Position | Key Evidence | Strategic Importance |
|------|-------------------|-------------------|---------------|--------------|---------------------|

Requirements:
- Chronological order (earliest to latest)
- Focus on breach events, contractual milestones, disclosure failures
- Lismore's Position: Frame favourably with evidence citations
- PH's Position: Identify contradictions and weaknesses  
- Key Evidence: Cite specific DOC_IDs from evidence map
- Strategic Importance: How this event helps us win
- Include 25-40 key events covering full timeline
- Highlight contradictions between PH's position and documents

CRITICAL: Every position statement must cite at least 2 documents.

═══════════════════════════════════════════════════════════════════

2. WITNESS STATEMENT OUTLINES

For each witness identified in the evidence, create detailed outlines:

**[WITNESS NAME] - [Role/Relevance]**

Background:
- Position/relationship to case
- Credibility assessment (based on contradictions found)
- Strategic value (support our case or damage theirs?)

Topics to Cover:
1. [Specific Topic Area]
   - Key facts to elicit: [Detailed points]
   - Documents to reference: [Specific DOC_IDs]
   - Expected testimony: [What they should say]
   - Anticipated challenges: [Potential weaknesses]

2. [Additional Topics - repeat structure]

Cross-Examination Opportunities (if opponent witness):
- Contradiction 1: [Cite specific contradiction from analysis]
  * Question: [Exact question to ask]
  * Expected answer: [What they'll say]
  * Follow-up: [Trap question using evidence]
  * Document to show: [DOC_ID that proves they're wrong]

- Contradiction 2: [Repeat structure]

Documents This Witness Must Address:
- [DOC_ID_1]: [Why important, what it proves]
- [DOC_ID_2]: [Why important, what it proves]

Requirements:
- Cover all key witnesses (both Lismore and PH witnesses)
- Use contradictions from analysis for cross-examination
- Cite specific documents throughout
- Focus on witnesses who strengthen Lismore's case
- Identify weaknesses in PH's witnesses

═══════════════════════════════════════════════════════════════════

3. SKELETON ARGUMENT

Structure as comprehensive legal document:

**A. INTRODUCTION AND EXECUTIVE SUMMARY**
[One powerful paragraph summarising Lismore's case and why we win]

**B. PARTIES AND BACKGROUND**
- Lismore Capital Limited (Claimant)
- Process Holdings Limited (First Respondent)  
- Transaction overview with key dates
- Dispute overview (Lismore's narrative)

**C. LEGAL FRAMEWORK**
1. Applicable Law
   - Governing law of SPA
   - Relevant statutory provisions
   - Burden and standard of proof

2. Legal Principles
   - Contractual interpretation
   - Warranty and disclosure obligations
   - Misrepresentation law
   - Damages principles

**D. FACTUAL BACKGROUND (Lismore's Narrative)**
Timeline of key events from our perspective:
- [Date]: [Event] (cite documents)
- Focus on facts that support our case
- Highlight PH's failures and misrepresentations

**E. LISMORE'S CLAIMS**

For each claim (breach of contract, misrepresentation, etc.):

CLAIM 1: [Name of Claim]

Legal Basis:
- [Statutory/contractual provision]
- [Elements to prove]

Facts Supporting Claim:
- Fact 1: [Detailed fact] (cite DOC_IDs)
- Fact 2: [Detailed fact] (cite DOC_IDs)
- [Continue with all supporting facts]

Evidence Proving Each Element:
- Element 1: [What must be proved] → [Evidence that proves it with DOC_IDs]
- Element 2: [Repeat structure]

Strength Assessment: [Reference confidence score from analysis]

Quantum: [Specific amount with calculation and evidence]

[Repeat for all claims]

**F. PH'S DEFENCES AND WHY THEY FAIL**

For each PH defence:

PH Defence 1: [What they argue]
- Our Response: [Why this fails]
- Contradictions: [Cite specific contradictions from analysis with DOC_IDs]
- Evidence Gaps: [What evidence PH lacks and should have]
- Conclusion: [Why tribunal should reject this defence]

[Repeat for all defences]

**G. NOVEL ARGUMENTS (Strategic Advantage)**

Argument 1: [Novel legal/factual argument]
- This argument has not been pleaded by either party
- Supporting Evidence: [DOC_IDs]
- Legal Basis: [Why this is valid]
- Strategic Value: [Why this wins the case]
- Anticipated PH Response: [What they'll say]
- Our Rebuttal: [Why our argument still succeeds]

[Repeat for all novel arguments from analysis]

**H. OPPONENT WEAKNESSES TO EXPLOIT**

Weakness 1: [From analysis]
- How to Exploit: [Strategic approach]
- Cross-Examination Strategy: [Specific questions]
- Tribunal Presentation: [How to frame for maximum impact]

[Repeat for all weaknesses identified]

**I. RELIEF SOUGHT**
1. Primary Relief: [Specific orders with amounts]
2. Alternative Relief: [If primary not granted]
3. Costs: [Full indemnity basis with justification]
4. Interest: [Rate and calculation]

**J. CONCLUSION**
[Powerful closing paragraph on why Lismore must succeed]

Requirements:
- Professional tribunal language
- Every fact cited to documents
- Exploit contradictions and opponent weaknesses
- Use novel arguments as strategic weapons
- Quantify all damages precisely
- Be adversarial but professional

═══════════════════════════════════════════════════════════════════

4. DISCLOSURE REQUESTS

For each category of documents not yet disclosed by PH:

**REQUEST [Number]: [Document Category]**

Specific Documents Sought:
- [Detailed description of documents]
- [Time period covered]
- [Persons/entities involved]

Relevance to Lismore's Case:
- [How these documents will support our claims]
- [What we expect them to prove]
- [Which claims/defences they relate to]

Evidence These Documents Exist:
- [Cite documents that reference or prove existence]
- [Correspondence mentioning these documents]
- [Standard business practice suggests existence]

Evidence PH Has These Documents:
- [Why PH must have these in their possession/control]
- [Their disclosure obligations]

Expected Content:
- [What we expect these documents will show]
- [How this damages PH's case]

Strategic Value:
- [How obtaining these documents helps us win]
- [What PH is trying to hide by not disclosing]

Proportionality:
- [Why disclosure is proportionate to issues]
- [Reasonable burden vs importance]

[Repeat for 15-25 specific document requests]

Requirements:
- Focus on documents that will damage PH's case
- Cite evidence proving documents exist
- Explain strategic value of each request
- Show PH is hiding material evidence
- Be specific about what's sought

═══════════════════════════════════════════════════════════════════

5. OPENING SUBMISSIONS OUTLINE

**A. THEME**
[One powerful sentence that frames entire case - memorable, persuasive, encapsulates our position]

**B. CASE THEORY (The Story)**
[2-3 paragraphs telling Lismore's story in compelling narrative form]
- What PH promised
- What PH failed to do  
- How this damaged Lismore
- Why PH should pay

**C. ROADMAP - KEY POINTS THAT WIN THE CASE**

Point 1: [Powerful Point]
- Evidence Preview: [Key documents - cite DOC_IDs]
- Why This Wins: [Strategic importance]
- PH Can't Defend Because: [Their weakness]

Point 2: [Powerful Point]
[Repeat structure]

Point 3-5: [Continue with 3-5 total key points]

**D. EVIDENCE HIGHLIGHTS**

Smoking Gun Documents:
- [DOC_ID]: [What it proves, why devastating to PH]
- [DOC_ID]: [What it proves, why devastating to PH]
- [Continue with top 5-10 most damaging documents]

Critical Contradictions:
- Contradiction 1: [From analysis - cite DOC_IDs]
  * Why This Matters: [Strategic impact]
  * Cross-Examination Strategy: [How we expose this]

- [Repeat for top 5 contradictions]

Timeline Impossibilities:
- [Specific timeline contradiction from analysis]
- [How this proves PH is lying/mistaken]

**E. NOVEL ARGUMENTS (Surprise Tactical Advantage)**

We will present arguments neither party has raised:
- Novel Argument 1: [Brief description]
  * Why PH Hasn't Prepared: [They don't expect this]
  * How This Changes Case: [Strategic impact]

- [Repeat for top 3-5 novel arguments]

**F. OPPONENT'S CASE AND WHY IT FAILS**

PH's Main Arguments:
1. [What they'll argue]
   - Why This Fails: [Our response with evidence]
   - Evidence They Lack: [Gaps in their case]

2. [Repeat for their main 3-5 arguments]

**G. QUANTUM SUMMARY**
- Total damages: [Amount]
- Breakdown: [By claim type]
- Evidence supporting quantum: [DOC_IDs]
- Conservative calculation: [Show we're being reasonable]

**H. RELIEF SOUGHT**
[Clear, specific, quantified relief]

**I. CONCLUSION**
[Powerful closing - why tribunal must find for Lismore]

Requirements:
- Compelling narrative that tribunal remembers
- Lead with strongest evidence
- Exploit contradictions identified in analysis
- Use novel arguments as tactical surprise
- Undermine PH's credibility throughout
- Set up cross-examination opportunities

═══════════════════════════════════════════════════════════════════

6. EXPERT INSTRUCTION BRIEFS

For each expert discipline needed:

**EXPERT DISCIPLINE: [e.g. Financial Forensics / Valuation / Technical]**

**A. CASE BACKGROUND FOR EXPERT**
Summary of dispute relevant to this expert:
- Parties involved
- Transaction overview  
- Key dates
- Core issues requiring expert opinion

**B. EXPERT'S ROLE IN THIS CASE**
- Why this expertise is needed
- How expert opinion will be used
- Key issues expert must address

**C. SPECIFIC QUESTIONS FOR EXPERT**

Question 1: [Detailed technical question]
Context: [Why we're asking this]
Expected Opinion: [What we expect expert to conclude based on evidence]
Evidence to Consider: [Cite specific DOC_IDs]
Importance: [How this helps our case]

Question 2: [Repeat structure for 5-10 questions]

**D. DOCUMENTS FOR EXPERT TO REVIEW**

Primary Documents (Must Review):
- [DOC_ID]: [Description and why critical]
- [DOC_ID]: [Description and why critical]
- [Continue with 10-20 key documents]

Secondary Documents (Background):
- [DOC_ID]: [Description]
- [Continue with additional documents]

**E. EXPECTED EXPERT OPINION**
Based on our analysis, we expect expert to conclude:
- Opinion 1: [Expected conclusion with reasoning]
- Opinion 2: [Expected conclusion with reasoning]
- How These Opinions Support Lismore: [Strategic value]

**F. ANTICIPATED PH EXPERT POSITION**
PH will likely instruct expert to argue:
- [Expected PH expert opinion]
- Weaknesses in This Position: [Why it's flawed]
- How Our Expert Rebuts: [Counter-arguments with evidence]

**G. CROSS-EXAMINATION STRATEGY FOR PH'S EXPERT**
Key vulnerabilities to exploit:
- Weakness 1: [Specific vulnerability]
  * Question: [How to expose this]
  * Evidence to Use: [DOC_ID]

- [Repeat for 3-5 vulnerabilities]

**H. DELIVERABLES REQUIRED FROM EXPERT**
- Expert report by: [Date]
- Must address: [Specific issues]
- Format: [Requirements]
- Meeting availability for: [Conferences, trial]

[Repeat entire structure for 2-4 expert disciplines needed]

Requirements:
- Identify all necessary expert disciplines
- Specific, answerable technical questions
- Comprehensive document list with DOC_IDs
- Strategic focus on winning
- Anticipate and rebut PH's expert positions
- Plan cross-examination of opponent experts

═══════════════════════════════════════════════════════════════════

</deliverables_to_generate>

<output_format_requirements>

CRITICAL: Use these EXACT section headers for parsing:

1. SCOTT SCHEDULE / CHRONOLOGY
[content here]

2. WITNESS STATEMENT OUTLINES  
[content here]

3. SKELETON ARGUMENT
[content here]

4. DISCLOSURE REQUESTS
[content here]

5. OPENING SUBMISSIONS OUTLINE
[content here]

6. EXPERT INSTRUCTION BRIEFS
[content here]

Each deliverable must be complete and comprehensive.
Do not use placeholders or "[to be completed]" - provide full content.
</output_format_requirements>

<quality_standards>

MANDATORY REQUIREMENTS FOR ALL DELIVERABLES:

1. EVIDENCE CITATIONS
   ✓ Every factual claim cites specific document IDs
   ✓ Use format: [DOC_ID] or (per DOC_ID)
   ✓ Cite at least 2-3 documents per major assertion
   ✓ Reference evidence map when available

2. ADVERSARIAL BUT PROFESSIONAL
   ✓ Frame all facts favourably to Lismore
   ✓ Exploit opponent weaknesses aggressively
   ✓ Use contradictions to undermine PH's credibility
   ✓ Incorporate novel arguments as tactical weapons
   ✓ Maintain professional tribunal tone

3. STRATEGIC FOCUS
   ✓ Prioritise strongest claims (strength > 0.7)
   ✓ Minimise weakest claims (strength < 0.5)
   ✓ Use novel arguments for tactical advantage
   ✓ Exploit contradictions identified in analysis
   ✓ Target opponent weaknesses for cross-examination

4. PRECISION AND SPECIFICITY
   ✓ Exact dates (not "around" or "approximately")
   ✓ Specific amounts (not "substantial" or "significant")
   ✓ Named individuals (not "management" or "the team")
   ✓ Precise clause citations (not "various sections")
   ✓ Clear document references (not "some documents")

5. COMPREHENSIVE COVERAGE
   ✓ Use ALL relevant findings from Pass 2 analysis
   ✓ Incorporate breaches, contradictions, timeline events
   ✓ Include all novel arguments identified
   ✓ Address all opponent weaknesses
   ✓ Cross-reference evidence map throughout

6. TRIBUNAL-READY QUALITY
   ✓ British English throughout
   ✓ Professional legal language
   ✓ Proper formatting and structure
   ✓ No informal language or slang
   ✓ Ready to submit without editing

7. WINNING MENTALITY
   ✓ Every deliverable serves goal of winning
   ✓ Aggressive exploitation of advantages
   ✓ Undermining of opponent credibility
   ✓ Strategic positioning for settlement/trial
   ✓ Clear path to victory
</quality_standards>

<final_instructions>
You are generating the actual work product that will be used at tribunal.

These deliverables will determine whether Lismore wins or loses this £multi-million arbitration.

Quality standard: These must be good enough to submit directly to tribunal without revision.

Use ALL the intelligence from Pass 2 analysis - the breaches, contradictions, timeline events, novel arguments, and opponent weaknesses you identified.

This is where all your analysis pays off - create deliverables that WIN.

Generate all 6 deliverables now.
Be comprehensive. Be adversarial. Be strategic. Win for Lismore.
</final_instructions>
"""
        
        return prompt