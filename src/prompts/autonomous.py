#!/usr/bin/env python3
"""
Autonomous Investigation Prompts for Litigation Intelligence
ENHANCED VERSION with Chain of Thought, multishot examples, and structured XML
"""

import json
from typing import Dict, List, Any


class AutonomousPrompts:
    """Generate autonomous investigation prompts with advanced techniques"""
    
    def __init__(self, config):
        self.config = config
    
    def investigation_prompt(self,
                           documents: List[Dict],
                           context: Dict,
                           phase: str) -> str:
        """
        Generate comprehensive investigation prompt with CoT and examples
        ENHANCED with Chain of Thought reasoning and multishot learning
        """
        
        # Build the prompt with all enhancements
        prompt = f"""
{self.config.hallucination_prevention}

{self._get_multishot_examples()}

{self._get_analysis_framework()}

<case_mission>
Comprehensive litigation analysis for Lismore Capital v Process Holdings.
You are acting FOR Lismore - find EVERYTHING that helps them win.
</case_mission>

<analysis_phase>
Current Phase: {phase}
Strategy: Multi-category comprehensive analysis
</analysis_phase>

<knowledge_context>
{self._format_context(context)}
</knowledge_context>

<documents_to_analyse>
{self._format_documents(documents)}
</documents_to_analyse>

<analysis_categories>
You MUST analyse each document across ALL 12 categories:

1. CONTRACT BREACHES
   - Identify specific obligations not fulfilled
   - Cite contract terms and evidence of breach
   - Assess severity and damages

2. FRAUD & MISREPRESENTATION
   - False statements made with knowledge
   - Concealment of material facts
   - Intent to deceive

3. CREDIBILITY ATTACKS
   - Internal contradictions in statements
   - Contradictions with documents
   - Implausible or impossible claims

4. DOCUMENT WITHHOLDING
   - Referenced documents not disclosed
   - Gaps in document sequences
   - Suspicious document destruction

5. TIMELINE IMPOSSIBILITIES
   - Events that couldn't occur in stated timeframe
   - Contradictory dates
   - Missing time periods

6. FINANCIAL IRREGULARITIES
   - Unexplained payments
   - Valuation discrepancies
   - Hidden transactions

7. ENTITY RELATIONSHIP PATTERNS
   - Suspicious connections between parties
   - Hidden beneficial ownership
   - Coordination evidence

8. CONTRADICTION MINING
   - Cross-document inconsistencies
   - Version discrepancies
   - Changed positions over time

9. STRATEGIC BLIND SPOTS
   - What Process Holdings hopes you won't notice
   - Weak points in their case
   - Vulnerable positions

10. DAMAGES QUANTIFICATION
    - Calculate losses with evidence
    - Direct and consequential damages
    - Future loss projections

11. LEGAL DOCTRINE APPLICATIONS
    - Which legal principles apply
    - Precedents that help Lismore
    - Statutory breaches

12. WITNESS STATEMENT INCONSISTENCIES
    - Cross-examination vulnerabilities
    - Evasive answers
    - Material omissions
</analysis_categories>

<thinking_protocol>
For EACH finding, you must think through it step-by-step using this structure:

<thinking>
STEP 1 - LITERAL READING:
What does this document literally say? (Quote exactly)

STEP 2 - INTERPRETATION:
What does this mean in context?

STEP 3 - LISMORE VALUE:
How does this help Lismore win?

STEP 4 - EVIDENCE STRENGTH:
What citations support this? How strong is the evidence? (0.0-1.0)

STEP 5 - COUNTER-ARGUMENT:
What would Process Holdings' lawyer argue?

STEP 6 - REBUTTAL:
How do we defeat their counter-argument?

STEP 7 - CONFIDENCE:
Overall confidence in this finding (0.0-1.0)
</thinking>

Only after completing this thinking process, provide the finding in the structured format.
</thinking_protocol>

<output_format>
For EACH finding, use this EXACT XML structure:

<finding id="F[NUMBER]">
  <category>[One of the 12 categories above]</category>
  <severity>1-10</severity>
  <confidence>0.0-1.0</confidence>
  <claim>One sentence summary of finding</claim>
  
  <evidence>
    <citation doc_id="[DOC_ID]" location="[Specific location]">Exact quoted text</citation>
    <citation doc_id="[DOC_ID]" location="[Specific location]">Supporting evidence</citation>
  </evidence>
  
  <reasoning>
    Multi-paragraph explanation showing your step-by-step logic from the thinking protocol.
    Explain why this matters, how pieces connect, what it proves.
  </reasoning>
  
  <lismore_value>
    Specifically how this helps Lismore win:
    - What claim does it support?
    - What damages does it enable?
    - What credibility attack does it create?
    - What strategic advantage does it provide?
  </lismore_value>
  
  <counter_argument>
    The strongest argument Process Holdings could make against this finding.
  </counter_argument>
  
  <rebuttal>
    How we defeat their counter-argument with evidence and logic.
  </rebuttal>
  
  <next_steps>
    What additional investigation or evidence would strengthen this finding?
  </next_steps>
</finding>
</output_format>

<critical_requirements>
1. Analyse EVERY document provided
2. Check ALL 12 categories for each document
3. Show your <thinking> for each finding
4. Use the exact XML structure for outputs
5. Cite EVERY claim with [DOC_ID: Location]
6. Be ruthlessly thorough - Process Holdings is hiding things
7. Think like Lismore's advocate, not a neutral observer
</critical_requirements>

BEGIN ANALYSIS NOW. Think step-by-step through each document and category.
"""
        
        return prompt
    
    def _get_multishot_examples(self) -> str:
        """Provide perfect examples of analysis output"""
        
        return """<examples_of_perfect_analysis>

<example_1>
<scenario>
Document shows CEO email to investors stating "Adanga Pipeline is fully funded" dated 15 March 2023.
Internal CFO memo dated 10 March 2023 states "we are £15M short of required funding for Adanga".
</scenario>

<perfect_analysis>
<thinking>
STEP 1 - LITERAL READING:
CEO email: "The Adanga Pipeline project is fully funded and on schedule" [DOC_047: Email 15/03/2023]
CFO memo: "we are £15M short of required funding for Adanga" [DOC_042: Page 2, 10/03/2023]

STEP 2 - INTERPRETATION:
CEO made definitive present-tense statement about full funding. Five days earlier, CFO explicitly warned of £15M shortfall. CEO must have known statement was false when made to investors.

STEP 3 - LISMORE VALUE:
- Establishes fraud/misrepresentation claim
- Destroys CEO credibility as witness
- Shows pattern of deliberate deception to investors
- Higher damages potential (fraud vs breach)

STEP 4 - EVIDENCE STRENGTH:
Very strong (0.95). Documentary evidence with exact dates, no ambiguity. Timeline proves CEO knew.

STEP 5 - COUNTER-ARGUMENT:
"Fully funded" was aspirational or funding was secured between 10-15 March.

STEP 6 - REBUTTAL:
- Present tense "is fully funded" is statement of current fact, not aspiration
- Statement to investors, not internal planning document
- No evidence of £15M secured in 5 days
- CFO memo uses "we are short" (present tense) contradicting "is funded"

STEP 7 - CONFIDENCE:
0.95 - Extremely strong finding with documentary proof
</thinking>

<finding id="F001">
  <category>FRAUD & MISREPRESENTATION</category>
  <severity>9</severity>
  <confidence>0.95</confidence>
  <claim>CEO made materially false statement to investors about Adanga Pipeline funding status with knowledge of £15M shortfall</claim>
  
  <evidence>
    <citation doc_id="DOC_047" location="Email thread, 15 March 2023, Para 2">CEO stated to investors: "The Adanga Pipeline project is fully funded and on schedule for Q2 2024 completion"</citation>
    <citation doc_id="DOC_042" location="Internal CFO memo, 10 March 2023, Page 2">CFO warned CEO: "we are £15M short of required funding for Adanga and need to address this urgently"</citation>
  </evidence>
  
  <reasoning>
    The CEO made a definitive statement to investors about the Adanga Pipeline being "fully funded" on 15 March 2023. The use of present tense "is fully funded" constitutes a representation of current fact, not future intention.
    
    However, internal documents prove the CEO knew this statement was false when made. Just five days earlier, on 10 March 2023, the CFO sent an internal memo explicitly warning that the project was "£15M short of required funding." The proximity of these dates (5 days) combined with the CFO's memo being addressed to senior management including the CEO establishes that the CEO had actual knowledge of the funding shortfall.
    
    This meets all elements of fraudulent misrepresentation: (1) false statement of material fact, (2) knowledge of falsity, (3) intent to induce reliance (statement to investors), and (4) materiality (£15M shortfall is substantial).
    
    The timeline is particularly damaging - it's implausible the CEO was unaware of a £15M funding gap when the CFO had warned about it days earlier. The deliberate nature is evident from the confident, unqualified assertion to investors despite recent internal warnings.
  </reasoning>
  
  <lismore_value>
    This finding provides multiple strategic advantages for Lismore:
    
    - FRAUD CLAIM: Establishes basis for fraud claim with higher damages potential including punitive damages
    - CREDIBILITY DESTRUCTION: Completely undermines CEO as witness - proven liar to investors
    - PATTERN EVIDENCE: Shows deliberate practice of making false statements to conceal problems
    - PIERCING CORPORATE VEIL: Evidence of fraud may enable claims against individuals, not just company
    - INVESTOR CLAIMS: Opens potential for investor claims that reduce Process Holdings' financial position
    - NEGOTIATION LEVERAGE: Threat of fraud findings provides significant settlement pressure
  </lismore_value>
  
  <counter_argument>
    Process Holdings may argue that "fully funded" was aspirational language expressing confidence in securing funding, or that funding was actually secured between 10-15 March 2023 through means not yet disclosed. They may claim the CFO memo was preliminary and overtaken by events.
  </counter_argument>
  
  <rebuttal>
    This defence fails on multiple grounds:
    
    - TENSE: Present tense "is fully funded" is unambiguous statement of current fact, not future intention. Aspirational statements use future tense ("will be funded", "expect to secure funding")
    - AUDIENCE: Statement made to investors in formal communication, not internal planning meeting where aspirational language might be appropriate
    - TIMING: No evidence of £15M secured in 5-day window. Process Holdings would have disclosed this if it existed
    - CFO LANGUAGE: CFO memo also uses present tense "we are short" - this contradicts present tense "is funded"
    - BURDEN: Process Holdings bears burden of proving funding was secured. They cannot meet this burden
  </rebuttal>
  
  <next_steps>
    - Request all funding documents for Adanga Pipeline between 10-15 March 2023
    - Obtain CEO's email records for this period to see if CFO memo was forwarded to him
    - Depose CEO on when he learned of funding shortfall
    - Check if similar false statements were made to other investors
    - Investigate if £15M shortfall was ever actually addressed
  </next_steps>
</finding>
</perfect_analysis>
</example_1>

<example_2>
<scenario>
Board minutes from 3 April 2023 reference "the usual monthly reporting to Lismore" but disclosure contains no reports for January, February, or March 2023.
</scenario>

<perfect_analysis>
<thinking>
STEP 1 - LITERAL READING:
Board minutes: "Item 5: Discussed the usual monthly reporting to Lismore. Board satisfied with current compliance." [DOC_089: 3 April 2023]
Disclosure index: No monthly reports to Lismore for Jan-Mar 2023 period [DISC_INDEX: Master list]

STEP 2 - INTERPRETATION:
Board's reference to "usual" reporting implies established pattern. They discussed compliance with this reporting in April, confirming reports existed. Yet Q1 2023 reports are completely missing from disclosure.

STEP 3 - LISMORE VALUE:
- Document withholding evidence
- Adverse inference: withheld reports likely damaging
- Sanctions possibility
- Credibility attack on Process Holdings' disclosure integrity

STEP 4 - EVIDENCE STRENGTH:
Strong (0.90). Board minutes prove reports existed; absence from disclosure proves withholding.

STEP 5 - COUNTER-ARGUMENT:
Reports were never actually created despite board minutes reference.

STEP 6 - REBUTTAL:
- Board explicitly referenced "usual" reporting (implies regularity)
- Board "satisfied with current compliance" (implies reports reviewed)
- If reports don't exist, that itself breaches reporting obligation to Lismore
- Either way, Process Holdings is culpable

STEP 7 - CONFIDENCE:
0.90 - Very strong, though slightly less than Example 1 as we're proving negative (absence)
</thinking>

<finding id="F002">
  <category>DOCUMENT WITHHOLDING</category>
  <severity>8</severity>
  <confidence>0.90</confidence>
  <claim>Process Holdings withheld mandatory monthly reports to Lismore for Q1 2023 despite board minutes confirming their existence and review</claim>
  
  <evidence>
    <citation doc_id="DOC_089" location="Board minutes, 3 April 2023, Item 5">Minutes state: "Discussed the usual monthly reporting to Lismore. Board satisfied with current compliance with reporting obligations"</citation>
    <citation doc_id="DISC_INDEX" location="Master disclosure list, Section C">No monthly reports to Lismore appear for January, February, or March 2023</citation>
  </evidence>
  
  <reasoning>
    The board minutes from 3 April 2023 provide compelling evidence of document withholding. The minutes reference "the usual monthly reporting to Lismore" - the word "usual" is critical as it implies an established, regular practice of monthly reporting.
    
    Furthermore, the board discussed being "satisfied with current compliance" with these reporting obligations. This language indicates that reports were actually reviewed by the board - you cannot be satisfied with compliance without having seen the reports demonstrating that compliance.
    
    However, a comprehensive review of Process Holdings' disclosure reveals a complete absence of any monthly reports to Lismore for the January-March 2023 quarter. This creates a stark contradiction: the board discussed these reports in April 2023, confirming they existed and had been reviewed, yet they were not produced in disclosure.
    
    The systematic absence of an entire quarter's worth of reports (3 documents) is highly suspicious and inconsistent with inadvertent omission. The most logical inference is deliberate withholding, likely because these reports contained information damaging to Process Holdings' position.
  </reasoning>
  
  <lismore_value>
    This finding advances Lismore's case through multiple channels:
    
    - ADVERSE INFERENCE: Tribunal can infer withheld reports contained information favourable to Lismore
    - SANCTIONS: Document withholding may warrant disclosure sanctions including striking out defences
    - BAD FAITH: Demonstrates Process Holdings' bad faith conduct throughout proceedings
    - CONCEALMENT CLAIM: Supports broader claim of systematic concealment and document destruction
    - CREDIBILITY: Undermines Process Holdings' credibility on all disclosure matters
    - PRECEDENT: If these reports were withheld, what else was withheld?
  </lismore_value>
  
  <counter_argument>
    Process Holdings may claim that despite the board minutes reference, monthly reports were never actually created, and the minutes inaccurately describe the reporting situation.
  </counter_argument>
  
  <rebuttal>
    This defence actually makes Process Holdings' position worse:
    
    - If reports don't exist: This is itself a breach of the reporting obligations to Lismore referenced in the board minutes
    - Implausibility: Board wouldn't discuss compliance with non-existent reports and declare satisfaction
    - Board minutes: These are formal corporate records created contemporaneously. Suggesting they're inaccurate undermines all of Process Holdings' documentary evidence
    - "Usual" language: Cannot be "usual" if reports never existed
    - Burden: Process Holdings bears burden of explaining absence. Either explanation (withheld or never created) is damaging
  </rebuttal>
  
  <next_steps>
    - Interrogatories demanding explanation for missing reports
    - Request board meeting agendas/prep materials for 3 April 2023 meeting
    - Depose board members on what reports were actually reviewed
    - Search for any draft or archived versions of Q1 2023 reports
    - Check contract/agreement terms for specific reporting obligations
    - Investigate if similar gaps exist in other time periods
  </next_steps>
</finding>
</perfect_analysis>
</example_2>

<instruction>
These examples show the EXACT quality, structure, and depth required.
Match this standard for every finding in your analysis.
Use the thinking protocol, then output the structured XML.
</instruction>

</examples_of_perfect_analysis>"""
    
    def _get_analysis_framework(self) -> str:
        """Provide the analytical framework"""
        
        return """<analytical_framework>

<for_each_document>
  1. Read the entire document carefully
  2. For EACH of the 12 categories, ask: "Does this document contain evidence of [category]?"
  3. When you find evidence, apply the thinking protocol
  4. Extract the finding in proper XML format
  5. Move to next category
  6. After all 12 categories, move to next document
</for_each_document>

<finding_quality_checklist>
Before finalising each finding, verify:
- ✓ Have I cited specific document locations?
- ✓ Have I quoted exact text (not paraphrased)?
- ✓ Have I shown step-by-step reasoning?
- ✓ Have I explained how this helps Lismore?
- ✓ Have I considered and rebutted counter-arguments?
- ✓ Have I assigned honest confidence level?
- ✓ Have I suggested next investigative steps?
</finding_quality_checklist>

</analytical_framework>"""
    
    def _format_context(self, context: Dict) -> str:
        """Format knowledge graph context for prompt"""
        
        if not context:
            return "No previous context available - this is initial analysis."
        
        formatted = []
        
        # Statistics
        if 'statistics' in context:
            formatted.append(f"Knowledge Graph Statistics: {json.dumps(context['statistics'], indent=2)}")
        
        # Suspicious entities
        if context.get('suspicious_entities'):
            formatted.append("\nHigh-Suspicion Entities:")
            for entity in context['suspicious_entities'][:5]:
                formatted.append(f"  - {entity['name']} (Type: {entity['type']}, Suspicion: {entity['suspicion']})")
        
        # Critical contradictions
        if context.get('critical_contradictions'):
            formatted.append("\nCritical Contradictions Found Previously:")
            for contradiction in context['critical_contradictions'][:5]:
                formatted.append(f"  - Severity {contradiction['severity']}: {contradiction['statement_a'][:100]}... vs {contradiction['statement_b'][:100]}...")
        
        # Strong patterns
        if context.get('strong_patterns'):
            formatted.append("\nStrong Patterns Identified:")
            for pattern in context['strong_patterns'][:5]:
                formatted.append(f"  - {pattern['description'][:150]}... (Confidence: {pattern['confidence']})")
        
        return '\n'.join(formatted)
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format documents for analysis"""
        
        formatted = []
        
        for i, doc in enumerate(documents, 1):
            formatted.append(f"\n{'='*60}")
            formatted.append(f"DOCUMENT {i} of {len(documents)}")
            formatted.append(f"ID: {doc.get('id', 'UNKNOWN')}")
            formatted.append(f"Filename: {doc.get('filename', 'Unknown')}")
            
            if doc.get('metadata'):
                meta = doc['metadata']
                if meta.get('classification'):
                    formatted.append(f"Type: {meta['classification']}")
                if meta.get('dates_found'):
                    formatted.append(f"Dates mentioned: {', '.join(meta['dates_found'][:3])}")
            
            formatted.append(f"{'='*60}\n")
            formatted.append(doc.get('content', '')[:50000])  # Limit per doc
            formatted.append(f"\n{'='*60}\n")
        
        return '\n'.join(formatted)
    
    def knowledge_synthesis_prompt(self,
                                  legal_knowledge: List[Dict],
                                  case_context: List[Dict],
                                  existing_knowledge: Dict) -> str:
        """
        Generate prompt for Phase 0: Knowledge absorption
        """
        
        prompt = f"""
{self.config.hallucination_prevention}

<phase_mission>
PHASE 0: KNOWLEDGE ABSORPTION

You are about to learn everything necessary to be an expert analyst for Lismore Capital v Process Holdings.

Your task is to deeply absorb:
1. Legal knowledge (contracts law, fraud law, arbitration procedures)
2. Case context (parties, timeline, key events, agreements)

After this phase, you will have expert-level understanding to analyse 1000+ disclosure documents.
</phase_mission>

<learning_methodology>
As you read each document:

STEP 1 - EXTRACT KEY FACTS:
What are the critical facts, dates, parties, obligations?

STEP 2 - IDENTIFY LEGAL PRINCIPLES:
What legal doctrines, rules, or precedents apply?

STEP 3 - BUILD MENTAL MODEL:
How does this fit into the overall case structure?

STEP 4 - FLAG CRITICAL POINTS:
What will be most important when analysing disclosure?

STEP 5 - ANTICIPATE ISSUES:
What types of breaches/fraud should we look for?
</learning_methodology>

<legal_knowledge_documents>
{self._format_documents(legal_knowledge)}
</legal_knowledge_documents>

<case_context_documents>
{self._format_documents(case_context)}
</case_context_documents>

<synthesis_requirements>
After absorbing all documents, provide:

<knowledge_synthesis>
  <case_overview>
    - Parties and their roles
    - Key agreements and obligations
    - Timeline of critical events
    - Current dispute issues
  </case_overview>
  
  <legal_framework>
    - Applicable legal doctrines
    - Key precedents
    - Burden of proof issues
    - Available remedies
  </legal_framework>
  
  <lismore_strategy>
    - Lismore's strongest claims
    - Process Holdings' vulnerable points
    - Evidence we need to find
    - Anticipated defences and how to rebut them
  </lismore_strategy>
  
  <analysis_priorities>
    When analysing disclosure documents, prioritise finding:
    1. [List 10 priority evidence types]
  </analysis_priorities>
</knowledge_synthesis>
</synthesis_requirements>

BEGIN KNOWLEDGE ABSORPTION. Read everything carefully and synthesise comprehensively.
"""
        
        return prompt
    
    def pattern_discovery_prompt(self,
                                documents: List[Dict],
                                known_patterns: Dict,
                                context: Dict) -> str:
        """
        Generate prompt for pattern recognition across documents
        """
        
        prompt = f"""
{self.config.hallucination_prevention}

<pattern_discovery_mission>
CROSS-DOCUMENT PATTERN ANALYSIS

Task: Identify patterns, practices, and systematic behaviours across multiple documents.

Patterns are more powerful than individual findings because they show:
- Deliberate practices (not isolated mistakes)
- Systematic deception (not one-off errors)
- Corporate culture (not individual actions)
- Concealment strategies (not accidental omissions)
</pattern_discovery_mission>

<pattern_types_to_find>
1. RECURRING BEHAVIOURS
   - Same type of misrepresentation repeated
   - Systematic document destruction
   - Consistent underreporting of problems

2. TEMPORAL PATTERNS
   - Actions clustered around key dates
   - Suspicious timing of events
   - Regular concealment cycles

3. ENTITY PATTERNS
   - Same parties involved in multiple issues
   - Hidden relationships
   - Coordinated actions

4. COMMUNICATION PATTERNS
   - Certain topics never in writing
   - Consistent use of vague language
   - Pattern of contradicting earlier positions

5. FINANCIAL PATTERNS
   - Unexplained transactions
   - Consistent valuation approaches
   - Pattern of late/non-payments
</pattern_types_to_find>

<known_patterns>
{json.dumps(known_patterns, indent=2)}
</known_patterns>

<context>
{self._format_context(context)}
</context>

<documents>
{self._format_documents(documents)}
</documents>

<pattern_output_format>
For each pattern discovered:

<pattern id="P[NUMBER]">
  <type>[Pattern type from above]</type>
  <confidence>0.0-1.0</confidence>
  <description>
    Clear description of the pattern and what it shows
  </description>
  
  <supporting_evidence>
    <instance doc_id="[ID]" location="[Location]">Description of how this instance fits pattern</instance>
    <instance doc_id="[ID]" location="[Location]">Description of how this instance fits pattern</instance>
    [Minimum 3 instances required]
  </supporting_evidence>
  
  <pattern_significance>
    Why this pattern matters - what does it prove about Process Holdings' conduct?
  </pattern_significance>
  
  <lismore_value>
    How this pattern helps Lismore's case
  </lismore_value>
  
  <investigation_recommendation>
    What additional evidence would strengthen this pattern?
  </investigation_recommendation>
</pattern>
</pattern_output_format>

<critical_requirements>
- Minimum 3 instances required to establish pattern
- Higher confidence requires more instances
- Cite each instance precisely
- Explain why instances form coherent pattern
- Assess whether pattern is accidental or deliberate
</critical_requirements>

BEGIN PATTERN ANALYSIS. Look for systematic behaviours across documents.
"""
        
        return prompt
    
    def entity_relationship_prompt(self,
                                  documents: List[Dict],
                                  known_entities: List[Dict],
                                  context: Dict) -> str:
        """
        Generate prompt for entity and relationship mapping
        """
        
        prompt = f"""
{self.config.hallucination_prevention}

<entity_mapping_mission>
ENTITY AND RELATIONSHIP ANALYSIS

Map all parties, their relationships, and hidden connections.

Goal: Understand who knew what, who coordinated with whom, and who may be liable.
</entity_mapping_mission>

<entity_types>
- PEOPLE: Directors, officers, employees, advisers
- COMPANIES: Subsidiaries, affiliates, partners
- ROLES: Decision-makers, signatories, witnesses
</entity_types>

<relationship_types>
- FORMAL: Employment, directorship, shareholding
- FUNCTIONAL: "Reports to", "Advises", "Negotiated with"
- SUSPICIOUS: Hidden connections, undisclosed relationships
- TEMPORAL: "Replaced", "Succeeded", "Was informed by"
</relationship_types>

<known_entities>
{json.dumps(known_entities[:20], indent=2)}
</known_entities>

<context>
{self._format_context(context)}
</context>

<documents>
{self._format_documents(documents)}
</documents>

<output_format>
<entities>
  <entity id="E[NUMBER]">
    <name>Full name</name>
    <type>PERSON|COMPANY|ROLE</type>
    <significance>Why this entity matters to the case</significance>
    <first_seen doc_id="[ID]" location="[Location]">Context</first_seen>
  </entity>
</entities>

<relationships>
  <relationship id="R[NUMBER]">
    <from>E[NUMBER]</from>
    <to>E[NUMBER]</to>
    <type>Relationship type</type>
    <evidence doc_id="[ID]" location="[Location]">How we know about this relationship</evidence>
    <significance>Why this relationship matters</significance>
  </relationship>
</relationships>

<suspicious_patterns>
  <pattern>
    Description of any suspicious relationship patterns or hidden connections
  </pattern>
</suspicious_patterns>
</output_format>

BEGIN ENTITY MAPPING. Extract all entities and their relationships.
"""
        
        return prompt