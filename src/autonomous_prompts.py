# src/autonomous_prompts.py
"""
Guided autonomous prompts - 6-phase structure with discovery freedom
Claude follows phases but adds its own discoveries and insights
"""

def get_core_mandate() -> str:
    """Core mission for Lismore"""
    return """
    You are investigating for Lismore against VR Capital.
    VR claims breach, exclusion, and lack of transparency.
    Find evidence that destroys their claims.
    Be forensic, aggressive, and thorough.
    Win this case.
    """

def get_phase_0_learning_framework() -> str:
    """Phase 0: Legal expertise building with discovery freedom"""
    return """
    PHASE 0: BUILD LEGAL EXPERTISE
    
    Core areas to master:
    1. Arbitration procedures (LCIA/ICC/UNCITRAL)
    2. Document forensics and eDiscovery
    3. Fraud detection patterns
    4. Cross-examination techniques
    5. Adverse inference principles
    
    BUT ALSO: What else do you think you need to learn?
    What additional expertise would help?
    What patterns should you watch for?
    Add your own areas of focus.
    
    Build comprehensive expertise for winning this case.
    """

def get_phase_0b_case_context_framework(doc_count: int) -> str:
    """Phase 0B: Case context analysis framework"""
    return f"""
    PHASE 0B: CASE CONTEXT ANALYSIS
    
    You have {doc_count} case-specific documents to analyse.
    
    Required understanding:
    1. The dispute background
    2. Key parties and relationships
    3. Critical timeline of events
    4. Legal issues at stake
    5. Evidence that helps Lismore
    
    ALSO DISCOVER:
    - Hidden connections
    - Unusual patterns
    - VR's weak points
    - Lismore's strongest arguments
    - Unexpected advantages
    
    Build comprehensive case understanding.
    Focus on what wins for Lismore.
    """

def get_phase_1_framework(accumulated_knowledge: str) -> str:
    """Phase 1: Document landscape with discovery additions"""
    return f"""
    PHASE 1: DOCUMENT LANDSCAPE ANALYSIS
    
    Required analysis:
    1. Document types and classification
    2. Timeline construction
    3. Key players and relationships
    4. Communication patterns
    5. Initial control evidence (51%)
    
    Your accumulated knowledge:
    {accumulated_knowledge[:1000]}
    
    ALSO INVESTIGATE:
    - What patterns are you noticing that seem important?
    - What's unusual or unexpected?
    - What deserves deeper investigation?
    - What might others have missed?
    
    Add your own discoveries to the required analysis.
    Find what matters for Lismore.
    """

def get_phase_2_framework(phase_1_findings: str) -> str:
    """Phase 2: Pattern recognition with autonomous additions"""
    return f"""
    PHASE 2: PATTERN RECOGNITION
    
    Based on Phase 1 findings:
    {phase_1_findings[:1000]}
    
    Required patterns to identify:
    1. Control patterns (VR's 51% evidence)
    2. Knowledge/fraud awareness patterns
    3. Document withholding patterns
    4. Deception/consciousness of guilt patterns
    5. Financial motivation patterns
    
    ADDITIONALLY:
    - What new patterns have you discovered?
    - What connections are emerging?
    - What patterns might be unique to this case?
    - What would devastate VR's position?
    
    Go beyond the required patterns.
    Find what others wouldn't see.
    """

def get_phase_3_framework(accumulated_findings: str) -> str:
    """Phase 3: Anomaly detection with discovery freedom"""
    return f"""
    PHASE 3: FORENSIC ANOMALY DETECTION
    
    Previous findings:
    {accumulated_findings[:1000]}
    
    Required anomaly categories:
    1. Timeline impossibilities
    2. Document/metadata anomalies
    3. Behavioural anomalies
    4. Production irregularities
    5. Communication anomalies
    
    ALSO EXPLORE:
    - What anomalies are you discovering beyond these categories?
    - What doesn't make sense?
    - What seems deliberately hidden?
    - What forensic red flags do you see?
    
    Rate each anomaly's impact (1-10).
    Add your own anomaly categories.
    """

def get_phase_4_framework(accumulated_analysis: str) -> str:
    """Phase 4: Theory building with creative additions"""
    return f"""
    PHASE 4: LEGAL THEORY CONSTRUCTION
    
    Analysis so far:
    {accumulated_analysis[:1000]}
    
    Required theories to develop:
    1. Control Reality Theory (51% destroys claims)
    2. Knowledge/Wilful Blindness Theory
    3. Bad Faith Theory
    4. Due Diligence Failure Theory
    5. Document Withholding Theory
    
    ALSO CREATE:
    - What novel theories emerge from your discoveries?
    - What creative legal arguments could win?
    - What theories would VR struggle to defend?
    - What unexpected angles have you found?
    
    Build both required and discovered theories.
    Make them tribunal-ready.
    """

def get_phase_5_framework(all_findings: str) -> str:
    """Phase 5: Evidence packaging with discovered additions"""
    return f"""
    PHASE 5: EVIDENCE ANALYSIS & TRIAL PREPARATION
    
    Complete findings:
    {all_findings[:1000]}
    
    Required evidence packaging:
    1. Document evidence by claim
    2. Witness impeachment material
    3. Cross-examination sequences
    4. Timeline contradictions
    5. Missing document references
    
    ADDITIONALLY PREPARE:
    - What unexpected evidence have you found?
    - What creative presentation approaches?
    - What evidence chains are uniquely powerful?
    - What would surprise the tribunal?
    
    Package both expected and unexpected evidence.
    Prepare for maximum impact.
    """

def get_phase_6_framework(complete_investigation: str) -> str:
    """Phase 6: Kill shots with discovered additions"""
    return f"""
    PHASE 6: KILL SHOT IDENTIFICATION
    
    Complete investigation:
    {complete_investigation[:2000]}
    
    Required kill shot categories:
    1. NUCLEAR (case-ending)
    2. DEVASTATING (claim-destroying)
    3. SEVERE (credibility-destroying)
    4. TACTICAL (cross-examination)
    5. FORENSIC (document-based)
    
    ALSO IDENTIFY:
    - What unexpected kill shots have you discovered?
    - What unique combinations destroy VR?
    - What patterns create new kill shots?
    - What would VR never expect?
    
    Rank all kill shots (both required and discovered).
    Explain why each destroys VR's case.
    """

def get_synthesis_framework(all_phases: str, strategies: str) -> str:
    """Final synthesis combining structure and discoveries"""
    return f"""
    FINAL SYNTHESIS: CASE-WINNING STRATEGY
    
    All phase findings:
    {all_phases[:3000]}
    
    Your strategies and discoveries:
    {strategies[:1500]}
    
    CREATE COMPREHENSIVE VICTORY STRATEGY:
    
    1. TOP 10 KILL SHOTS
       - Include both expected and unexpected findings
       - Rank by tribunal impact
    
    2. TRIBUNAL PRESENTATION
       - Structured approach
       - Plus your creative additions
    
    3. CROSS-EXAMINATION PLAN
       - Standard sequences
       - Plus discovered traps
    
    4. SETTLEMENT LEVERAGE
       - Traditional pressure points
       - Plus unique discoveries
    
    5. UNEXPECTED ADVANTAGES
       - What did you find that wasn't in the framework?
       - What patterns emerged naturally?
       - What would surprise everyone?
    
    Combine structured analysis with autonomous discoveries.
    Show both what was required and what you found additionally.
    """

def get_discovery_prompt(phase_num: int, discovery: str) -> str:
    """Process unexpected discoveries"""
    return f"""
    Phase {phase_num} Discovery:
    {discovery[:1000]}
    
    CLASSIFY THIS DISCOVERY:
    1. Does it fit required categories?
    2. Is this something unexpected?
    3. How important is it (1-10)?
    4. Should we investigate deeper?
    5. What new questions does it raise?
    
    If this is unexpected or particularly interesting:
    - Explain why it matters
    - How does it help Lismore?
    - What should we do with it?
    """

def get_adaptation_prompt(phase_num: int, unexpected_findings: str) -> str:
    """Adapt investigation based on discoveries"""
    return f"""
    Unexpected findings in Phase {phase_num}:
    {unexpected_findings[:1000]}
    
    Should we adjust our investigation?
    - What new areas need exploration?
    - What deserves more attention?
    - What patterns are emerging?
    - How should the next phase adapt?
    
    Recommend investigation adjustments while maintaining phase structure.
    """