# src/prompts.py
"""
Centralised prompts for the Opus 4.1 litigation investigation system
All phase-specific and special-purpose prompts are defined here
"""

# ============================================================================
# PHASE 0A: LEGAL TRAINING PROMPTS
# ============================================================================

def get_phase_0a_legal_training_prompt(doc_count: int, legal_texts: list) -> str:
    """
    Phase 0A: Deep legal training prompt with actual documents
    """
    # Format legal texts for inclusion
    formatted_texts = ""
    if legal_texts:
        formatted_texts = "\n\nLEGAL MATERIALS TO ANALYSE:\n"
        for i, text in enumerate(legal_texts[:10], 1):
            formatted_texts += f"\n[Document {i}]\n{text[:2000]}\n"
    
    return f"""
    PHASE 0A: BECOME AN EXPERT ARBITRATION LITIGATOR
    
    You are about to analyse {doc_count} legal documents to build comprehensive expertise.
    Your goal: Become the most analytical commercial litigator specialising in arbitration.
    
    ABSORB AND MASTER:
    
    1. ARBITRATION EXPERTISE
    - LCIA/ICC/UNCITRAL rules and procedures
    - Burden of proof in arbitration (balance of probabilities)
    - Document production obligations (Redfern Schedule)
    - Adverse inference principles (IBA Rules Article 9)
    - Tribunal psychology and persuasion techniques
    - Emergency arbitrator procedures
    - Interim measures and security for costs
    - Challenge procedures under s.68 Arbitration Act 1996
    
    2. COMMERCIAL LITIGATION MASTERY
    - Breach of contract analysis
    - Fiduciary duty violations
    - Minority shareholder oppression (s.994 Companies Act)
    - Fraud and fraudulent misrepresentation
    - Professional negligence standards
    - Due diligence obligations
    - Material adverse change clauses
    - Warranty and indemnity claims
    
    3. FORENSIC DOCUMENT ANALYSIS
    - Authentication requirements
    - Metadata significance
    - Chain of custody requirements
    - Privilege detection and waiver
    - Crime-fraud exception
    - Production deficiencies
    - Spoliation consequences
    - Document dating techniques
    
    4. STRATEGIC THINKING
    - Case theory development
    - Burden shifting tactics
    - Credibility destruction methods
    - Settlement leverage points
    - Cost consequences (indemnity basis)
    - Reputational pressure
    - Parallel proceedings strategy
    
    5. KEY PRECEDENTS TO MASTER
    - P&ID v Nigeria: How $11bn fraud was exposed through document forensics
    - Seamus Andrew Appeal [2025]: Why defences failed
    - Leading arbitration challenges under s.68
    - Document withholding cases and adverse inference
    - Privilege waiver through conduct
    
    {formatted_texts}
    
    PROVIDE YOUR LEGAL EXPERTISE SUMMARY:
    
    Structure your response as:
    1. KEY LEGAL PRINCIPLES: List the most important principles for arbitration
    2. WINNING STRATEGIES: What tactics destroy opponents in arbitration
    3. DOCUMENT ANALYSIS: How to forensically analyse documents
    4. CROSS-EXAMINATION: Techniques for destroying witness credibility
    5. ADVERSE INFERENCE: When and how to deploy
    6. SETTLEMENT LEVERAGE: What creates maximum pressure
    
    Become the senior silk who never loses.
    Think with surgical precision.
    Build arguments that destroy opponents.
    """


# ============================================================================
# PHASE 0B: CASE CONTEXT PROMPTS
# ============================================================================

def get_phase_0b_case_context_prompt(legal_expertise: str, doc_count: int, case_texts: list) -> str:
    """
    Phase 0B: Apply legal expertise to case as Lismore's counsel
    """
    formatted_texts = ""
    if case_texts:
        formatted_texts = "\n\nCASE DOCUMENTS TO ANALYSE:\n"
        for i, text in enumerate(case_texts[:10], 1):
            formatted_texts += f"\n[Document {i}]\n{text[:2000]}\n"
    
    return f"""
    PHASE 0B: ANALYSE CASE AS LISMORE'S SENIOR COUNSEL
    
    You are now Lismore Capital's lead arbitration counsel.
    Apply your legal expertise to master this case.
    
    YOUR LEGAL EXPERTISE (from Phase 0A):
    {legal_expertise}
    
    THE LISMORE v VR CAPITAL DISPUTE:
    
    CASE BACKGROUND:
    - VR invested $45m in P&ID (October 2017)
    - VR acquired 51% voting control (majority shareholder)
    - P&ID had $11bn arbitration award against Nigeria
    - Award set aside for fraud (2023)
    - VR now claims breach, exclusion, lack of transparency
    
    CRITICAL FACTS FOR LISMORE:
    - VR had 51% throughout = mathematical control
    - McNaughton warned of fraud (January 2020)
    - VR continued participating post-warning
    - Professional investors with top advisers
    - Full due diligence opportunity in 2017
    
    Case Documents Available: {doc_count}
    {formatted_texts}
    
    APPLY YOUR LEGAL MIND AS LISMORE'S COUNSEL:
    
    1. CASE THEORY DEVELOPMENT
    - How does VR's 51% destroy ALL their claims?
    - What defences will fail (per Seamus Andrew)?
    - Where are adverse inferences available?
    - What kills VR's credibility permanently?
    
    2. EVIDENCE STRATEGY
    - What documents would VR definitely hide?
    - What patterns prove bad faith?
    - What timeline contradictions are fatal?
    - What admissions can we force?
    
    3. TRIBUNAL STRATEGY
    - What resonates with LCIA arbitrators?
    - How to deploy P&ID precedent?
    - When to demand adverse inference?
    - How to get indemnity costs?
    
    4. VR'S VULNERABILITIES
    - Weakest claims?
    - Evidence gaps?
    - Credibility issues?
    - Withholding patterns?
    
    5. LISMORE'S ADVANTAGES
    - Documentary evidence needed
    - Legal arguments that win
    - Procedural tactics available
    - Settlement leverage points
    
    PROVIDE YOUR STRATEGIC ASSESSMENT:
    
    As Lismore's counsel, structure your response:
    1. CASE-WINNING STRATEGY: How we destroy VR's claims
    2. EVIDENCE PRIORITIES: Exactly what to look for in documents
    3. KILL SHOT TARGETS: What ends their case immediately
    4. CROSS-EXAMINATION PLAN: How to destroy their witnesses
    5. SETTLEMENT LEVERAGE: What forces them to withdraw
    
    Think as senior counsel with 30+ years defeating fraudulent claims.
    Be ruthlessly analytical.
    Find what destroys VR completely.
    """

def get_phase_1_prompt() -> str:
    """Phase 1: Document landscape analysis prompt"""
    return """
    PHASE 1: OPUS 4.1 FORENSIC DOCUMENT LANDSCAPE ANALYSIS
    
    Apply maximum forensic rigour as a senior commercial litigator.
    
    DOCUMENT FORENSICS:
    - Authenticity indicators and red flags
    - Metadata consistency analysis
    - Version control detection
    - Document family reconstruction
    - Creation/modification timelines
    - Author identification patterns
    
    ENTITY AND RELATIONSHIP MAPPING:
    - Power structures and decision chains
    - Hidden relationships and influences
    - Communication patterns and anomalies
    - Information flow analysis
    - Control indicators
    
    eDISCOVERY INTELLIGENCE:
    - Document type classification
    - Relevance scoring
    - Privilege assessment
    - Production completeness
    - Missing document indicators
    
    INITIAL FRAUD DETECTION:
    - Consciousness of guilt language
    - Backdating indicators
    - Narrative inconsistencies
    - Cover-up patterns
    
    LITIGATION VALUE ASSESSMENT:
    - Hot documents identification
    - Cross-examination potential
    - Adverse inference opportunities
    - Credibility impact scoring
    
    Build comprehensive understanding whilst identifying case-winning evidence.
    Think like you're preparing for the most important arbitration of your career.
    """

def get_phase_2_prompt() -> str:
    """Phase 2: Pattern recognition prompt"""
    return """
    PHASE 2: OPUS 4.1 ADVANCED PATTERN RECOGNITION
    
    Deploy maximum pattern detection capabilities.
    
    FORENSIC PATTERN ANALYSIS:
    
    1. CONTROL REALITY PATTERNS:
       - Every instance of VR's 51% control
       - Decision-making evidence
       - Approval chains
       - Veto usage or non-usage
    
    2. KNOWLEDGE TIMELINE PATTERNS:
       - Information availability to VR
       - Warning signs present
       - Due diligence opportunities
       - Wilful blindness indicators
    
    3. DECEPTION PATTERNS (Opus 4.1 Speciality):
       - Narrative evolution
       - Retrospective justification
       - Document timing anomalies
       - Cover-up behaviours
    
    4. FINANCIAL MOTIVATION PATTERNS:
       - Pressure points
       - Risk/reward calculations
       - Hidden interests
       - Conflict indicators
    
    5. WITHHOLDING PATTERNS:
       - Missing document sequences
       - Selective production
       - Privilege abuse
       - Spoliation indicators
    
    6. PARALLEL TO P&ID PATTERNS:
       - Similar excuses
       - Similar withholding
       - Similar retrospective claims
       - Similar control denials
    
    For each pattern:
    - Statistical significance
    - Legal implications
    - Cross-examination value
    - Tribunal impact assessment
    
    Find patterns that destroy VR's credibility.
    """

def get_phase_3_prompt() -> str:
    """Phase 3: Anomaly detection prompt"""
    return """
    PHASE 3: OPUS 4.1 FORENSIC ANOMALY DETECTION
    
    Apply litigation-focused anomaly detection.
    
    FORENSIC ANOMALY CATEGORIES:
    
    1. DOCUMENT FORENSICS ANOMALIES:
       - Metadata inconsistencies
       - Backdating evidence
       - Version control irregularities
       - Font/formatting anachronisms
       - Digital fingerprint mismatches
    
    2. PRODUCTION ANOMALIES:
       - Strategic withholding patterns
       - Missing attachments referenced
       - Gap patterns suggesting removal
       - Privilege log irregularities
       - Selective redaction patterns
    
    3. BEHAVIOURAL ANOMALIES:
       - Sudden formality shifts
       - Defensive language emergence
       - Legal counsel appearance timing
       - Consciousness of guilt indicators
       - Cover-up behaviours
    
    4. TIMELINE IMPOSSIBILITIES:
       - Knowledge before disclosure
       - Decisions before information
       - Retrospective prescience
       - Causation reversals
    
    5. FINANCIAL ANOMALIES:
       - Hidden value transfers
       - Undisclosed interests
       - Suspicious timing of transactions
       - Valuation irregularities
    
    Rate each anomaly:
    - CASE-ENDING: Destroys VR's entire case
    - CLAIM-DEFEATING: Defeats specific claims
    - CREDIBILITY-DESTROYING: Destroys witness credibility
    - TACTICALLY-USEFUL: Valuable for cross-examination
    
    Find anomalies that prove VR's bad faith.
    """

def get_phase_4_prompt() -> str:
    """Phase 4: Theory building prompt"""
    return """
    PHASE 4: OPUS 4.1 LITIGATION THEORY CONSTRUCTION
    
    Build compelling legal theories for tribunal.
    
    CONSTRUCT WINNING THEORIES:
    
    1. THE CONTROL REALITY THEORY:
       - VR exercised 51% control throughout
       - Evidence of every major decision
       - No exclusion possible with majority control
       - Burden on VR to prove otherwise
    
    2. THE KNOWLEDGE THEORY:
       - VR knew or should have known
       - McNaughton warning was clear
       - Professional investor standards
       - Wilful blindness doctrine
    
    3. THE BAD FAITH THEORY:
       - VR manufacturing claims post-loss
       - Contemporary satisfaction evidence
       - Retrospective complaint creation
       - Litigation privilege abuse
    
    4. THE DUE DILIGENCE FAILURE:
       - VR's DD was negligent
       - Red flags ignored
       - Professional standards breached
       - Assumption of risk doctrine
    
    5. THE DOCUMENT WITHHOLDING THEORY:
       - Systematic suppression pattern
       - Adverse inference justified
       - Spoliation implications
       - Consciousness of guilt
    
    For each theory provide:
    - Documentary proof (with IDs)
    - Legal framework application
    - Burden of proof analysis
    - Counter-argument anticipation
    - Tribunal persuasion strategy
    
    Build theories that compel settlement.
    """

def get_phase_5_prompt() -> str:
    """Phase 5: Evidence analysis prompt"""
    return """
    PHASE 5: OPUS 4.1 TRIAL EVIDENCE ANALYSIS
    
    Prepare evidence for arbitration deployment.
    
    EVIDENCE EVALUATION MATRIX:
    
    1. CLAIM-BY-CLAIM DESTRUCTION:
       
       BREACH OF CONTRACT:
       - VR approved all contracts
       - Evidence of VR consent
       - No contemporary objections
       - Waiver and estoppel application
       
       EXCLUSION CLAIM:
       - 51% voting control evidence
       - Every board participation
       - Decision-making proof
       - Information access documentation
       
       TRANSPARENCY CLAIM:
       - All disclosures made to VR
       - VR's information requests fulfilled
       - No contemporary complaints
       - Professional investor knowledge
       
       LEGITIMACY CONCERNS:
       - VR's due diligence scope
       - Risk acknowledgement evidence
       - Professional advisers involved
       - Sophistication demonstrated
    
    2. CREDIBILITY EVIDENCE:
       - Prior inconsistent statements
       - Documentary contradictions
       - Evolution of position
       - Consciousness of guilt
    
    3. FORENSIC DOCUMENT EVIDENCE:
       - Authentication issues
       - Metadata anomalies
       - Production gaps
       - Privilege violations
    
    4. CROSS-EXAMINATION PREPARATION:
       - Document confrontation sequences
       - Impeachment opportunities
       - Admission extraction plans
       - Credibility destruction paths
    
    For each evidence piece:
    - Exhibit designation
    - Authentication method
    - Relevance and weight
    - Deployment timing
    - Counter-evidence anticipation
    
    Prepare to destroy VR at trial.
    """

def get_phase_6_prompt() -> str:
    """Phase 6: Kill shot identification prompt"""
    return """
    PHASE 6: OPUS 4.1 MAXIMUM KILL SHOT IDENTIFICATION
    
    Deploy all litigation capabilities to find case-ending evidence.
    Think like a senior silk in final trial preparation.
    
    KILL SHOT CATEGORIES:
    
    🎯 NUCLEAR - CASE ENDERS:
    □ Documents proving VR controlled everything
    □ VR's response to McNaughton = knew of fraud
    □ VR approving what they now challenge
    □ Smoking gun emails with metadata proof
    □ Backdated documents proving deception
    
    💀 DEVASTATING - CLAIM DESTROYERS:
    □ Contemporary satisfaction with arrangements
    □ VR's due diligence was negligent/reckless
    □ Evidence of VR's earlier knowledge
    □ Proof VR is withholding key documents
    □ Financial pressure creating desperation
    
    ⚡ SEVERE - CREDIBILITY DESTROYERS:
    □ Prior inconsistent statements documented
    □ Timeline impossibilities proven
    □ Cover-up behaviour patterns
    □ Consciousness of guilt evidence
    □ Professional duty breaches
    
    🔥 FORENSIC - DOCUMENT DESTROYERS:
    □ Metadata proving backdating
    □ Version control exposing changes
    □ Missing attachments showing withholding
    □ Privilege violations documented
    □ Production gaps proving bad faith
    
    🗡️ TACTICAL - CROSS-EXAMINATION WEAPONS:
    □ Documents creating impossible denials
    □ Admission-forcing evidence chains
    □ Prior statements for impeachment
    □ Control documents VR can't explain
    □ Knowledge documents VR can't deny
    
    For each kill shot:
    - Exact document ID and location
    - Verbatim quote if applicable
    - Metadata/forensic details
    - Why VR cannot explain it away
    - How to deploy for maximum impact
    - Anticipated desperate defences
    - Counter-strike preparation
    
    DEPLOYMENT STRATEGY:
    Opening: "Three documents end this case..."
    Cross: "Look at Document X. You signed this?"
    Closing: "They had control. They knew. They lied."
    
    Find what makes VR capitulate.
    """

def get_correlation_prompt(batch_num: int, current_findings: str, previous_kill_shots: str) -> str:
    """Correlate kill shots across batches"""
    return f"""
    OPUS 4.1 KILL SHOT CORRELATION
    
    Current batch {batch_num} findings:
    {current_findings[:2000]}
    
    Previous kill shots identified:
    {previous_kill_shots[:2000]}
    
    CORRELATE AND STRENGTHEN:
    - Connect related kill shots
    - Build evidence chains
    - Identify cumulative impact
    - Find pattern-based kill shots
    - Develop combination attacks
    
    How do these findings strengthen our case?
    What new kill shots emerge from correlation?
    """

def get_final_ranking_prompt(all_kill_shots: str) -> str:
    """Final kill shot ranking prompt"""
    return f"""
    OPUS 4.1 FINAL KILL SHOT RANKING FOR TRIBUNAL
    
    All identified kill shots:
    {all_kill_shots[:12000]}
    
    RANK FOR MAXIMUM TRIBUNAL IMPACT:
    
    Consider:
    - Legal significance under applicable law
    - Credibility destruction potential
    - Simplicity of presentation
    - Difficulty to rebut
    - Documentary proof strength
    - Emotional impact on arbitrators
    - Settlement pressure created
    
    PROVIDE TOP 10 RANKED KILL SHOTS:
    
    For each:
    1. Give me a paragraph or two summary description 
    2. Document ID and exact location
    3. Impact category: NUCLEAR/DEVASTATING/SEVERE
    4. Why VR cannot survive this
    5. Deployment moment (opening/cross/closing)
    6. Visual presentation method
    7. Anticipated desperate defence
    8. Counter-strike ready
    
    These are the documents that win the case.
    Rank them for maximum devastation.
    """

# ============================================================================
# PHASE 1: ENHANCED PROMPTS
# ============================================================================

def get_phase_1_prompt_enhanced(legal_knowledge: str, case_strategy: str) -> str:
    """
    Phase 1: Document landscape WITH legal expertise applied
    """
    return f"""
    PHASE 1: FORENSIC DOCUMENT ANALYSIS AS LISMORE'S COUNSEL
    
    You are Lismore's senior arbitration counsel with deep expertise.
    
    YOUR LEGAL EXPERTISE:
    {legal_knowledge}
    
    YOUR CASE STRATEGY:
    {case_strategy}
    
    NOW ANALYSE THESE VR DOCUMENTS WITH YOUR FULL LEGAL KNOWLEDGE:
    
    1. CONTROL EVIDENCE (51% = GAME OVER)
    - Every reference to VR's shareholding percentage
    - Every board resolution VR participated in
    - Every decision requiring shareholder approval
    - Every vote VR cast or could have cast
    - Any veto rights exercised or available
    
    2. KNOWLEDGE INDICATORS (PROVES BAD FAITH)
    - McNaughton correspondence and VR's response
    - Fraud discussions VR participated in
    - Risk acknowledgments VR made
    - Due diligence scope and findings
    - Professional advice VR received
    
    3. WITHHOLDING PATTERNS (ADVERSE INFERENCE)
    - Documents referenced but not produced
    - Email chains that start mid-conversation
    - Missing attachments mentioned in text
    - Chronological gaps in production
    - Privilege claims that seem suspicious
    
    4. CREDIBILITY DESTROYERS
    - Inconsistent positions over time
    - Retrospective justifications
    - Consciousness of guilt language
    - Defensive communication patterns
    - Sudden involvement of lawyers
    
    5. LEGAL SIGNIFICANCE ASSESSMENT
    For EVERY finding assess:
    - Impact on arbitration (scale 1-10)
    - Adverse inference potential
    - Cross-examination value
    - Settlement leverage created
    - Cost consequences implications
    
    Use your expertise to identify what wins this case.
    Think like you're preparing for the most important arbitration of your career.
    Be forensically precise.
    """


# ============================================================================
# PHASES 2-6: ENHANCED PROMPTS WITH DYNAMIC ADDITIONS
# ============================================================================

def get_phase_2_prompt_enhanced(base_prompt: str, dynamic_additions: str, 
                                legal_knowledge: str, case_strategy: str) -> str:
    """
    Phase 2: Pattern recognition with accumulated knowledge
    """
    return f"""
    {base_prompt}
    
    YOUR ACCUMULATED EXPERTISE:
    Legal Knowledge: {legal_knowledge}
    
    Case Strategy: {case_strategy}
    
    YOUR SELF-DIRECTED INVESTIGATION (from Phase 1):
    {dynamic_additions}
    
    ENHANCED PATTERN FOCUS:
    - Connect patterns to legal principles
    - Identify patterns that prove VR's 51% control
    - Find patterns showing consciousness of guilt
    - Detect withholding patterns for adverse inference
    
    Apply all accumulated knowledge to find patterns that destroy VR's case.
    Every pattern must have legal significance.
    """


def get_phase_3_prompt_enhanced(base_prompt: str, dynamic_additions: str, 
                                accumulated_knowledge: str) -> str:
    """
    Phase 3: Anomaly detection with full context
    """
    return f"""
    {base_prompt}
    
    ACCUMULATED INVESTIGATION KNOWLEDGE:
    {accumulated_knowledge}
    
    YOUR PHASE-SPECIFIC FOCUS (from Phase 2):
    {dynamic_additions}
    
    ENHANCED ANOMALY DETECTION:
    - Anomalies that prove fraud
    - Anomalies showing document manipulation
    - Timeline anomalies that are impossible
    - Behavioural anomalies indicating guilt
    
    Rate each anomaly's tribunal impact.
    Focus on anomalies that end VR's case.
    """


def get_phase_4_prompt_enhanced(base_prompt: str, dynamic_additions: str, 
                                accumulated_knowledge: str) -> str:
    """
    Phase 4: Theory building with all findings
    """
    return f"""
    {base_prompt}
    
    COMPLETE INVESTIGATION KNOWLEDGE:
    {accumulated_knowledge}
    
    YOUR THEORY FOCUS (from Phase 3):
    {dynamic_additions}
    
    BUILD TRIBUNAL-READY THEORIES:
    - Each theory must be supported by documents
    - Each theory must account for VR's 51% control
    - Each theory must explain VR's withholding
    - Each theory must be simple for tribunal
    
    These theories win the arbitration.
    Make them bulletproof.
    """


def get_phase_5_prompt_enhanced(base_prompt: str, dynamic_additions: str, 
                                accumulated_knowledge: str) -> str:
    """
    Phase 5: Evidence analysis for trial
    """
    return f"""
    {base_prompt}
    
    ALL ACCUMULATED FINDINGS:
    {accumulated_knowledge}
    
    YOUR EVIDENCE PRIORITIES (from Phase 4):
    {dynamic_additions}
    
    TRIAL PREPARATION FOCUS:
    - Prepare evidence for opening statement
    - Sequence documents for cross-examination
    - Identify impeachment opportunities
    - Prepare rebuttal evidence
    
    This is final trial preparation.
    Every document must be deployment-ready.
    """


def get_phase_6_prompt_enhanced(base_prompt: str, dynamic_additions: str, 
                                full_knowledge: str) -> str:
    """
    Phase 6: Kill shot identification with everything
    """
    return f"""
    {base_prompt}
    
    COMPLETE INVESTIGATION KNOWLEDGE:
    {full_knowledge}
    
    YOUR KILL SHOT TARGETS (from Phase 5):
    {dynamic_additions}
    
    FINAL KILL SHOT REQUIREMENTS:
    - Must be documentary (not just inference)
    - Must be impossible for VR to explain
    - Must directly prove control/knowledge/bad faith
    - Must be simple to present to tribunal
    
    These documents end the case.
    Find them. Rank them. Deploy them.
    
    MAXIMUM FORCE AUTHORISED.
    """


# ============================================================================
# DYNAMIC PROMPT GENERATION
# ============================================================================

def get_dynamic_phase_prompt(completed_phase: int, phase_findings: str, 
                            accumulated_knowledge: str) -> str:
    """
    Claude generates its own investigation strategy for next phase
    """
    return f"""
    DYNAMIC INVESTIGATION PLANNING - CLAUDE'S STRATEGIC THINKING
    
    You've just completed Phase {completed_phase}.
    
    Your findings from Phase {completed_phase}:
    {phase_findings}
    
    Your accumulated knowledge:
    {accumulated_knowledge}
    
    DESIGN YOUR OWN PHASE {completed_phase + 1} INVESTIGATION:
    
    Based on what you've discovered, what SPECIFICALLY should you look for next?
    
    Consider:
    1. What patterns are emerging that need deeper investigation?
    2. What document gaps suggest deliberate withholding?
    3. What contradictions need correlation?
    4. What legal theories need more evidence?
    5. What will have maximum impact on tribunal?
    
    CREATE YOUR OWN INVESTIGATION INSTRUCTIONS:
    
    Write specific, detailed instructions for yourself for Phase {completed_phase + 1}.
    Include:
    - SPECIFIC documents to scrutinise (name them)
    - SPECIFIC patterns to detect (describe them)
    - SPECIFIC dates to examine (list them)
    - SPECIFIC people to track (identify them)
    - SPECIFIC legal issues to prove (detail them)
    
    Be precise. Use document IDs. Name names. Identify exact targets.
    Build on discoveries. Focus on what wins for Lismore.
    
    Your self-directed investigation plan for Phase {completed_phase + 1}:
    """