#!/usr/bin/env python3
"""
Output Prompts for Litigation Intelligence System
Contains all phase-specific prompts for report generation
"""

from typing import Dict, Any


class OutputPrompts:
    """All prompts for litigation report generation"""
    
    @staticmethod
    def get_phase_1_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 1: Document Landscape - ALL reports in one prompt"""
        return f"""
PHASE 1: COMPREHENSIVE DOCUMENT LANDSCAPE ANALYSIS

You have access to {context['document_count']} documents from the Lismore vs Process Holdings litigation.

Previous legal weapons identified: {len(context.get('legal_weapons', {}).get('nuclear', []))} nuclear options

Generate THREE comprehensive reports:

====================
REPORT 1: DOCUMENT CLASSIFICATION & PRIORITY MATRIX
====================
Create a strategic document matrix that:
1. Categorises EVERY document by type (contract, email, financial, board minutes, etc.)
2. Assigns priority ratings (NUCLEAR/CRITICAL/HIGH/MEDIUM/LOW) based on case impact
3. Identifies "hot documents" that could destroy Process Holdings
4. Flags suspicious documents (altered, missing pages, backdated)
5. Maps document relationships and dependencies
6. Identifies gaps in document production
7. Ranks top 20 documents by litigation value

Format as structured matrix with document references [DOC_XXXX]

====================
REPORT 2: RED FLAGS & IRREGULARITIES ANALYSIS
====================
Identify ALL irregularities:
1. Missing documents that should exist (email chains, attachments, minutes)
2. Chronological impossibilities or gaps
3. Metadata anomalies suggesting tampering
4. Sudden communication pattern changes
5. Documents contradicting each other
6. "Too perfect" documents suggesting fabrication
7. Evidence of document destruction
8. Suspicious timing of creation/modification

For each red flag:
- Description of irregularity
- Document references [DOC_XXXX]
- Severity rating (1-10)
- Investigation steps needed
- Legal implications

====================
REPORT 3: ACTOR NETWORK & COMMUNICATION ANALYSIS
====================
Map the complete actor network:
1. ALL individuals mentioned with roles/affiliations
2. Communication patterns (who, when, frequency)
3. Power dynamics and decision hierarchy
4. Unusual exclusions/inclusions
5. Hidden relationships or conflicts
6. Who's hiding information
7. When lawyers first appear
8. Tone changes with specific actors

Create visual network showing:
- Central vs peripheral actors
- Hidden influencers
- Suspicious relationships
- Key witnesses to target

CRITICAL REQUIREMENTS:
- Reference EVERY finding to specific documents [DOC_XXXX]
- Rank findings by ability to destroy Process Holdings
- Identify follow-up actions for each discovery
- Focus on what wins the case for Lismore

Based on the document content and accumulated intelligence, provide all three reports.
"""
    
    @staticmethod
    def get_phase_2_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 2: Timeline Analysis - ALL reports in one prompt"""
        accumulated = context.get('accumulated_findings', {})
        
        return f"""
PHASE 2: COMPREHENSIVE TEMPORAL FORENSIC ANALYSIS

Documents span: {context.get('phase_specific', {}).get('timeline_span', 'Unknown')}
Contradictions found so far: {accumulated.get('total_contradictions', 0)}

Generate THREE timeline-focused reports:

====================
REPORT 1: MASTER TIMELINE WITH IMPOSSIBILITIES
====================
Construct forensic timeline showing:
1. EVERY dated event with document references [DOC_XXXX]
2. Timeline conflicts and impossibilities (highlight in CAPS)
3. Suspicious gaps or silence periods
4. Where Process Holdings' story breaks chronologically
5. Parallel activity tracks revealing deception
6. Retroactive knowledge (knowing before possible)
7. Document backdating/forward-dating evidence
8. "Smoking gun" temporal moments

Format: Date | Event | Document | Conflict | Significance (1-10)

====================
REPORT 2: CRITICAL PERIOD DEEP ANALYSIS
====================
Analyse these critical periods:
1. Relationship breakdown point - when and why
2. Intense activity bursts - what were they hiding?
3. Suspicious silence - why no documents?
4. Decision points where fraud began
5. Cover-up initiation period
6. Lawyer involvement trigger
7. Financial pressure points
8. Regulatory scrutiny periods

For each period:
- Exact date range
- All documents from period
- What's suspiciously missing
- Significance to case
- Impact rating (1-10)

====================
REPORT 3: DECEPTION EVOLUTION TRACKING
====================
Track Process Holdings' deception evolution:
1. How their story morphed over time
2. When cover-up activities began
3. Cooperation → hostility transition
4. Informal → formal communication shift
5. Lawyer introduction and trigger
6. Document creation practice changes
7. Damages claim evolution
8. Blame-shifting progression

Identify the "point of no return" where fraud became deliberate.
Show progression from truth → deception → cover-up.

Focus on timeline impossibilities that destroy their credibility.
"""
    
    @staticmethod
    def get_phase_3_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 3: Contradictions & Gaps - ALL reports in one prompt"""
        contradictions = context.get('contradictions', {})
        
        return f"""
PHASE 3: DEEP CONTRADICTION & PATTERN MINING

Contradictions identified across phases: {sum(len(v) for v in contradictions.values())}
Missing evidence patterns detected: {len(context.get('patterns', {}).get('missing_documents', []))}

Generate THREE comprehensive contradiction reports:

====================
REPORT 1: CONTRADICTION MATRIX
====================
Build exhaustive contradiction matrix:

1. DIRECT CONTRADICTIONS (Party A says X, Party B says Y)
2. TIMELINE IMPOSSIBILITIES (Can't have happened as claimed)
3. FINANCIAL DISCREPANCIES (Numbers don't match)
4. NARRATIVE EVOLUTION (Story changes)
5. MISSING DOCUMENTS (Referenced but not produced)
6. PARTICIPANT IMPOSSIBILITIES (Impossible attendance/knowledge)
7. TECHNICAL IMPOSSIBILITIES (Violates logic/physics)
8. LEGAL POSITION CONFLICTS

Format as matrix:
Source1 [DOC_XXXX] | Source2 [DOC_YYYY] | Type | Quote1 | Quote2 | Impact (1-10) | Exploitation Strategy

Rank by case-destroying potential.

====================
REPORT 2: MISSING DOCUMENTS & ADVERSE INFERENCE
====================
Catalogue EVERY missing document:

1. Documents referenced but not produced
2. Email chains with gaps
3. Board minutes for mentioned meetings
4. Referenced contracts/agreements
5. Financial records that must exist
6. Critical period communications
7. Draft versions mentioned
8. Missing attachments

For each missing item:
- What's missing
- Where referenced [DOC_XXXX]
- Why it MUST exist
- Likely damaging content
- Adverse inference argument
- Production demand language

Build the adverse inference case.

====================
REPORT 3: COMMUNICATION FORENSICS
====================
Forensic communication analysis:

1. Tone shifts indicating guilt/problems
2. Sudden formality (legal awareness)
3. Code words/euphemisms for wrongdoing
4. "Off the record" references
5. Improperly withheld privileged comms
6. Ghost-written/lawyer-edited messages
7. Conspiracy coordination patterns
8. Hidden admissions in routine messages

Find the communications that prove deliberate wrongdoing.
Identify consciousness of guilt markers.

Every contradiction is ammunition. Find them all.
"""
    
    @staticmethod
    def get_phase_4_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 4: Narrative Warfare - ALL reports in one prompt"""
        return f"""
PHASE 4: NARRATIVE CONSTRUCTION & DESTRUCTION

Admissions available: {context.get('accumulated_findings', {}).get('total_admissions', 0)}
Nuclear weapons ready: {len(context.get('legal_weapons', {}).get('nuclear', []))}

Generate TWO powerful narrative reports:

====================
REPORT 1: LISMORE'S WINNING NARRATIVE
====================
Construct the compelling story that wins:

THE STORY STRUCTURE:
- Opening Hook: The betrayal that shocks the conscience
- Act 1 - The Promise: What Process Holdings agreed to do
- Act 2 - The Breach: How they deliberately failed
- Act 3 - The Cover-up: How they tried to hide it
- Act 4 - The Discovery: How we exposed their fraud
- Conclusion: Justice demands victory for Lismore

Requirements:
1. Simple, emotionally compelling narrative
2. Every claim proven by documents [DOC_XXXX]
3. Heroes (Lismore) vs Villains (Process Holdings)
4. Creates moral outrage at defendant
5. Makes verdict inevitable
6. Supports maximum damages
7. Destroys all defences preemptively

Make the judge/jury WANT to punish Process Holdings.

====================
REPORT 2: PROCESS HOLDINGS NARRATIVE DESTRUCTION
====================
Systematically demolish their story:

For EVERY claim Process Holdings makes:
1. State their claim
2. Why it's demonstrably false
3. Documentary proof of falsehood [DOC_XXXX]
4. The real truth
5. Evidence of deliberate deception
6. How to expose in court

Show:
- Evolution of their lies
- Bad faith throughout
- True motives (greed/fraud)
- Consciousness of guilt
- Cover-up attempts
- Why their lawyers should settle

Make their narrative so untenable their own lawyers doubt them.

Transform the evidence into a story that wins.
"""
    
    @staticmethod
    def get_phase_5_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 5: Evidence Packaging - ALL reports in one prompt"""
        return f"""
PHASE 5: LEGAL ARSENAL DEPLOYMENT & EVIDENCE PACKAGING

Legal weapons available: {sum(len(v) for v in context.get('legal_weapons', {}).values())}
Criminal crossovers identified: {len(context.get('legal_weapons', {}).get('criminal', []))}

Generate THREE strategic evidence reports:

====================
REPORT 1: DECISIVE EVIDENCE PACKAGES
====================
Create themed evidence packages:

1. FRAUD PACKAGE
   - All deception evidence
   - False representations [DOC_XXXX]
   - Knowledge of falsity
   - Reliance and damages
   
2. DAMAGES PACKAGE
   - All financial harm
   - Lost profits evidence
   - Consequential damages
   - Punitive damages basis

3. BAD FAITH PACKAGE
   - Malicious intent evidence
   - Deliberate obstruction
   - Abuse of process

4. COVER-UP PACKAGE
   - Destruction evidence
   - Concealment attempts
   - Spoliation proof

5. CONSPIRACY PACKAGE
   - Coordination evidence
   - Common purpose
   - Unlawful acts

For each package:
- Documents in impact order
- How they connect
- Combined strength (1-10)
- Deployment strategy

====================
REPORT 2: COMPREHENSIVE ADMISSIONS BANK
====================
Compile ALL admissions for maximum impact:

1. JUDICIAL ADMISSIONS (binding)
2. DIRECT ADMISSIONS (explicit wrongdoing)
3. ADMISSIONS AGAINST INTEREST
4. ADMISSIONS BY CONDUCT
5. ADMISSIONS BY SILENCE
6. IMPLIED ADMISSIONS
7. ADOPTIVE ADMISSIONS

For each admission:
- Exact quote
- Document reference [DOC_XXXX]
- Legal effect
- How to lock down in deposition
- Cross-exam usage

Build the admission trap.

====================
REPORT 3: CRIMINAL REFERRAL ASSESSMENT
====================
Assess criminal prosecution threats:

1. FRAUD
   - Elements proven
   - Evidence available
   - Prosecution likelihood

2. CONSPIRACY
   - Participants identified
   - Agreement evidence
   - Overt acts

3. MONEY LAUNDERING
   - Suspicious transactions
   - Pattern evidence

4. OBSTRUCTION
   - Document destruction
   - Witness tampering

5. PERJURY
   - False statements
   - Materiality

For each crime:
- Strength of evidence (1-10)
- Settlement leverage created
- Referral threat credibility
- Personal exposure for executives

Package the evidence to maximise pressure.
"""
    
    @staticmethod
    def get_phase_6_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 6: Endgame Strategy - ALL reports in one prompt"""
        return f"""
PHASE 6: ENDGAME ORCHESTRATION

Total contradictions for cross-exam: {context.get('accumulated_findings', {}).get('total_contradictions', 0)}
Settlement leverage points: {len(context.get('legal_weapons', {}).get('nuclear', [])) + len(context.get('legal_weapons', {}).get('criminal', []))}

Generate THREE endgame reports:

====================
REPORT 1: CROSS-EXAMINATION DEMOLITION PLAN
====================
Design witness destruction strategy:

For KEY WITNESSES:
1. Name and vulnerability analysis
2. Prior inconsistent statements [DOC_XXXX]
3. Documents for ambush
4. Admissions to extract
5. Credibility destruction sequence
6. Trap questions that guarantee lies
7. Visual aids for dramatic moments
8. Backup plan if they evade

QUESTION SEQUENCES:
- Opening: Lock them into lies
- Development: Tighten the noose
- Confrontation: Deploy contradictions
- Climax: Destroy credibility
- Close: Extract admissions

Make them wish they'd settled.

====================
REPORT 2: SETTLEMENT LEVERAGE MAXIMISATION
====================
Create escalating pressure campaign:

LEVERAGE INVENTORY:
1. Criminal prosecution threats (specify crimes)
2. Regulatory complaints ready
3. Reputational destruction options
4. Personal liability exposure
5. Insurance coverage threats
6. Third party claims
7. Public disclosure threats

ESCALATION TIMELINE:
Week 1: Deploy initial evidence package
Week 2: Add criminal referral threat
Week 3: Threaten regulatory action
Week 4: Personal liability notices
Week 5: Nuclear option

Price each threat removal:
- Remove criminal referral: £X million
- Keep confidential: £Y million
- No regulatory report: £Z million

====================
REPORT 3: SUMMARY JUDGMENT ROADMAP
====================
Build the no-trial victory:

UNDISPUTED FACTS:
1. Admissions eliminating disputes
2. Documents proving claims conclusively
3. No genuine issues remaining

LEGAL ARGUMENTS:
1. Claims proven as matter of law
2. Defences that fail legally
3. Sanctions supporting judgment
4. Procedural defaults

PARTIAL JUDGMENT OPTIONS:
- Liability only
- Specific claims
- Striking defences

Show the court that trial is unnecessary - we've already won.

Orchestrate total victory or maximum settlement.
"""
    
    @staticmethod
    def get_phase_7_unified_prompt(context: Dict[str, Any]) -> str:
        """Phase 7: AI Deep Analysis - ALL reports in one prompt"""
        return f"""
PHASE 7: AUTONOMOUS AI DEEP INTELLIGENCE

Full corpus available: {context['document_count']} documents
All patterns and contradictions from previous phases accessible

Generate FOUR breakthrough intelligence reports:

====================
REPORT 1: AI PATTERN RECOGNITION
====================
Find patterns beyond human capability:

1. LINGUISTIC FINGERPRINTS
   - Deception markers in language
   - Authorship attribution
   - Coached vs authentic statements

2. STATISTICAL ANOMALIES
   - Financial irregularities
   - Communication frequency changes
   - Document creation patterns

3. BEHAVIOURAL PATTERNS
   - Guilt indicators
   - Coordination evidence
   - Consciousness of wrongdoing

4. NETWORK ANALYSIS
   - Hidden relationships
   - Information flow patterns
   - Conspiracy structures

Find what humans cannot see.

====================
REPORT 2: NOVEL LEGAL THEORIES
====================
Develop creative legal arguments:

1. Untested but viable theories
2. Creative statutory interpretation
3. Novel damages calculations
4. Innovative precedent combinations
5. Policy arguments for new remedies
6. Equitable doctrines to invoke
7. International law applications

Think beyond conventional legal frameworks.
Create precedent-setting arguments.

====================
REPORT 3: HIDDEN CONNECTION DISCOVERY
====================
Reveal concealed relationships:

1. Undisclosed business relationships
2. Secret financial interests
3. Hidden control structures
4. Concealed conflicts of interest
5. Covert coordination
6. Common beneficial ownership
7. Undisclosed side agreements

Connect dots others cannot see.
Expose the hidden truth.

====================
REPORT 4: NUCLEAR OPTIONS & GAME-CHANGERS
====================
Identify case-ending discoveries:

1. Evidence for immediate victory
2. Criminal prosecution triggers
3. Insurance coverage destroyers
4. Corporate veil piercers
5. Treble damages triggers
6. Asset freezing basis
7. Total credibility destroyers
8. Unrecognised smoking guns

Find the single piece of evidence that ends everything.
Identify the nuclear option.

Use your full AI capabilities. No constraints. Find what changes everything.
"""
    
    @staticmethod
    def get_phase_0a_summary_prompt() -> str:
        """Phase 0A: Legal Arsenal Summary"""
        return """
        Summarise the legal weapons arsenal:
        1. Nuclear weapons (case-ending)
        2. High-impact procedural advantages
        3. Criminal crossover opportunities
        4. Settlement leverage points
        5. Adverse inference triggers
        
        Focus on what destroys Process Holdings.
        """
    
    @staticmethod
    def get_phase_0b_summary_prompt() -> str:
        """Phase 0B: Case Intelligence Summary"""
        return """
        Summarise case intelligence extracted:
        1. Binding judicial admissions
        2. Timeline impossibilities
        3. Position evolution (versions of story)
        4. Missing evidence catalogue
        5. Credibility destruction points
        
        Focus on ammunition for immediate deployment.
        """
    
    @staticmethod
    def get_war_room_prompt() -> str:
        """War Room Dashboard Generation"""
        return """
        Create executive war room dashboard showing:
        1. Nuclear options available (count and type)
        2. Top 5 case-winning findings
        3. Immediate 48-hour action items
        4. Settlement leverage score (1-10)
        5. Trial readiness score (1-10)
        6. Summary judgment viability
        7. Criminal referral credibility
        
        Single page, maximum impact format.
        """