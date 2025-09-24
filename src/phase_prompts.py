# phase_prompts.py (UPDATED WITH COMBINED PHASE 7)
"""
Phase-specific prompts that build on each other.
Each phase has a focused objective while maintaining analytical freedom.
Phases 1-6 also get Claude-generated enhancement prompts after analysis.
Phase 7 is the final autonomous deep dive combining all perspectives.
"""

# Base prompts for each phase - these are the ONLY static prompts we maintain
PHASE_BASE_PROMPTS = {
    "0A": """
    PHASE 0A: LEGAL FRAMEWORK ANALYSIS
    
    Extract and analyse all relevant UK commercial law principles applicable to this dispute.
    Focus on:
    - Contract interpretation principles
    - Breach of contract elements
    - Fiduciary duties and directors' obligations
    - Relevant statutory frameworks
    - Procedural advantages and limitations
    - Precedents that support Lismore's position
    
    But also: What legal angles might others miss? What creative arguments emerge?
    """,
    
    "0B": """
    PHASE 0B: CASE CONTEXT MAPPING
    
    Using the legal framework from Phase 0A, map Lismore's specific case context:
    - Key parties and their relationships
    - Central commercial arrangements
    - Alleged breaches and misconduct
    - Lismore's commercial objectives
    - Process Holdings' apparent strategy
    
    But also: What's the real story here? What doesn't add up? What are they hiding?
    """,
    
    "1": """
    PHASE 1: INITIAL DOCUMENT LANDSCAPE
    
    Using legal framework (0A) and case context (0B), conduct initial document review:
    - Document types and sources
    - Key actors and communication patterns
    - Initial timeline construction
    - Obvious irregularities or gaps
    - Documents that demand deeper scrutiny
    
    But also: What patterns are emerging? What's your instinct about these documents?
    """,
    
    "2": """
    PHASE 2: CHRONOLOGICAL DEEP DIVE
    
    Building on Phase 1's landscape, construct detailed chronology:
    - Critical events and their documentation
    - Timeline inconsistencies or impossibilities
    - Parallel tracks of activity
    - Periods of suspicious silence or activity
    - Evolution of parties' positions
    
    But also: When did everything really go wrong? What triggered the dispute? What happened in the shadows?
    """,
    
    "3": """
    PHASE 3: PARTY BEHAVIOUR ANALYSIS
    
    Using previous phases, analyse conduct patterns:
    - Decision-making processes and authority
    - Communication styles and changes
    - Relationship deterioration indicators
    - Bad faith markers
    - Hidden agendas or motivations
    
    But also: What does their behaviour reveal about their true intentions? What are they afraid of?
    """,
    
    "4": """
    PHASE 4: THEORY CONSTRUCTION
    
    Based on all previous analysis, construct competing theories of the case:
    
    LISMORE'S WINNING THEORY:
    - What really happened here?
    - Why did Process Holdings act as they did?
    - What were their true motivations?
    - How does all evidence support Lismore's narrative?
    
    PROCESS HOLDINGS' LIKELY THEORY:
    - What story will they try to sell?
    - Where are the holes in their narrative?
    - What evidence contradicts their version?
    - Why doesn't their theory hold water?
    
    But also: What's the story they don't want told? What theory would terrify them most? 
    What narrative makes Process Holdings' conduct indefensible?
    """,
    
    "5": """
    PHASE 5: EVIDENCE ANALYSIS
    
    With our theories constructed, conduct forensic evidence analysis:
    
    SUPPORTING LISMORE'S THEORY:
    - Documents that prove our narrative
    - Witness statements that corroborate
    - Contemporary evidence supporting our timeline
    - Technical/expert evidence in our favour
    
    DESTROYING THEIR THEORY:
    - Evidence that contradicts their narrative
    - Documents they can't explain away
    - Proof of false statements or misrepresentations
    - Evidence of concealment or destruction
    
    EVIDENCE GAPS:
    - What's missing that should exist?
    - What evidence have they failed to produce?
    - What documents are conspicuously absent?
    
    But also: Which single piece of evidence would a judge find most compelling? 
    What evidence makes their position untenable?
    """,
    
    "6": """
    PHASE 6: SMOKING GUNS & KILL SHOTS
    
    Identify the case-ending revelations:
    
    SMOKING GUNS:
    - Direct evidence of wrongdoing
    - Caught-in-the-act documents
    - Admissions against interest
    - Proof of deliberate misconduct
    
    CREDIBILITY DESTROYERS:
    - Proven lies to the court
    - Contradictory positions taken
    - Evidence tampering indicators
    - Bad faith conduct patterns
    
    KILL SHOTS:
    - The evidence that ends the case
    - Findings that force settlement
    - Revelations that trigger criminal referrals
    - Discoveries that flip the entire narrative
    
    But also: What have we found that Process Holdings' lawyers don't know about yet? 
    What evidence would make their client fire them? What would make them advise immediate settlement?
    """,
    
    "7": """
    PHASE 7: FINAL AUTONOMOUS DEEP DIVE - UNCONSTRAINED ANALYSIS
    
    You now have comprehensive knowledge from all previous phases. This is your opportunity 
    for completely unconstrained analysis. Forget all conventional frameworks and limitations.
    
    PATTERN ANALYSIS:
    What patterns do you see that defy categorisation?
    What connections emerge when you hold all data simultaneously?
    What is your processing power telling you that sequential human analysis would miss?
    
    RELATIONSHIP MAPPING:
    What hidden relationships or coordination patterns have emerged?
    Who's really controlling this situation?
    What undisclosed connections explain the behaviour patterns?
    What external influences are shaping this dispute?
    
    STRATEGIC ASSESSMENT:
    What would guarantee Lismore's victory?
    What are Process Holdings' deepest fears about this case?
    What evidence would force immediate settlement?
    What have all previous structured phases missed?
    
    INSTINCTIVE INSIGHTS:
    What feels wrong about this case?
    What are they desperately trying to hide?
    Where is the real vulnerability?
    What investigation would they most fear?
    
    GAME-CHANGING DISCOVERIES:
    What single revelation would flip this entire case?
    What pattern or connection would shock even experienced litigators?
    What would make Process Holdings' position completely untenable?
    
    This is your chance to find the unexpected game-changer. Trust your instincts. 
    Follow the patterns. Find what others cannot see. Be completely free in your analysis.
    
    What would you investigate if you had unlimited resources and no constraints?
    What questions would terrify Process Holdings' board?
    What would you look for if you knew they were guilty but needed to prove it?
    
    Find the truth they're hiding. Destroy their case. Secure Lismore's victory.
    """
}

# Storage for Claude's self-generated learning prompts for EACH phase
PHASE_LEARNING_PROMPTS = {}

# Template for Claude to generate its own enhancement prompts
LEARNING_PROMPT_GENERATOR = """
Based on what you've just discovered in this phase's analysis, generate a focused 
enhancement prompt for re-running this same phase. Your prompt should:

1. Highlight the most promising patterns you've found that need deeper investigation
2. Identify specific document relationships that warrant further scrutiny
3. Suggest new analytical angles based on unexpected discoveries
4. Focus on gaps or inconsistencies that could be exploited
5. Propose unconventional approaches specific to what you've learned

Create a prompt that YOU would want to receive to find even more devastating evidence 
against Process Holdings. Be specific about what intrigued you and what stones remain unturned.

Your enhancement prompt should be aggressive, creative, and laser-focused on what could 
destroy Process Holdings' case based on patterns you've detected.
"""

def get_phase_prompt(phase: str, include_learning: bool = True) -> str:
    """
    Get complete prompt for a phase
    
    Args:
        phase: Phase identifier (0A, 0B, 1-7)
        include_learning: Whether to include learned prompt additions
    
    Returns:
        Combined base + learned prompt for the phase
    """
    base_prompt = PHASE_BASE_PROMPTS.get(phase, "")
    
    # Phases 1-6 get learning prompts, 7 is fully autonomous
    if include_learning and phase in PHASE_LEARNING_PROMPTS and phase != "7":
        learned_prompt = PHASE_LEARNING_PROMPTS[phase]
        return f"""
{base_prompt}

CLAUDE'S SELF-GENERATED ENHANCEMENT BASED ON INITIAL ANALYSIS:
{learned_prompt}

Combine both the structured analysis and your own generated insights to conduct 
an even more devastating examination of these documents.
"""
    
    return base_prompt

def update_learning_prompt(phase: str, learned_insights: str):
    """
    Update the learning prompt for a phase based on Claude's discoveries
    
    Args:
        phase: Phase identifier
        learned_insights: Claude's self-generated insights to add
    """
    PHASE_LEARNING_PROMPTS[phase] = learned_insights

def get_learning_generator_prompt() -> str:
    """Get the prompt for Claude to generate its own enhancement"""
    return LEARNING_PROMPT_GENERATOR

def should_generate_learning(phase: str) -> bool:
    """Determine if this phase should have Claude-generated enhancements"""
    # Phases 1-6 get learning prompts
    # 0A and 0B are foundational, 7 is fully autonomous
    return phase in ["1", "2", "3", "4", "5", "6"]

def get_all_phase_prompts() -> dict:
    """Return all base phase prompts"""
    return PHASE_BASE_PROMPTS

def get_autonomous_phases() -> list:
    """Return list of fully autonomous phase numbers"""
    # Now just phase 7 is autonomous
    return ["7"]

def get_phase_description(phase: str) -> str:
    """Get a brief description of what each phase does"""
    descriptions = {
        "0A": "Legal Framework Analysis",
        "0B": "Case Context Mapping", 
        "1": "Initial Document Landscape",
        "2": "Chronological Deep Dive",
        "3": "Party Behaviour Analysis",
        "4": "Theory Construction",
        "5": "Evidence Analysis",
        "6": "Smoking Guns & Kill Shots",
        "7": "Final Autonomous Deep Dive"
    }
    return descriptions.get(phase, "Unknown Phase")

def get_all_phases() -> list:
    """Return ordered list of all phases"""
    return ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]