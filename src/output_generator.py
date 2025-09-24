# output_generator.py (OPTIMISED VERSION)
"""
Generates formatted outputs and reports from analysis results.
Phases 0A & 0B: Knowledge retention only (no reports)
Phases 1-7: Multiple strategic reports per phase with full Claude integration
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
from knowledge_manage import KnowledgeManager
from api_client import ClaudeAPIClient

class OutputGenerator:
    """Generates various output formats from analysis results"""
    
    def __init__(self, knowledge_manage: KnowledgeManager):
        """
        Initialise output generator
        
        Args:
            knowledge_manage: KnowledgeManager instance with analysis results
        """
        self.knowledge_manage = knowledge_manage
        self.api_client = ClaudeAPIClient()  # For Claude-enhanced report generation
        self.output_dir = "./outputs"
        self.document_registry = {}
        os.makedirs(self.output_dir, exist_ok=True)
    
    def register_documents(self, documents: List[Dict]):
        """
        Register documents with unique IDs for referencing
        
        Args:
            documents: List of document dictionaries
        """
        for idx, doc in enumerate(documents, 1):
            doc_id = f"DOC_{idx:04d}"
            self.document_registry[doc_id] = {
                'filename': doc.get('filename', doc.get('path', 'Unknown').split('/')[-1]),
                'path': doc.get('path', 'Unknown'),
                'pages': self._extract_page_count(doc.get('content', '')),
                'content': doc.get('content', '')  # Store content for Claude analysis
            }
    
    def _extract_page_count(self, content: str) -> int:
        """Extract approximate page count from content"""
        return max(1, len(content) // 3000)
    
    def _format_evidence_reference(self, doc_id: str, page: Optional[int] = None, 
                                  paragraph: Optional[int] = None) -> str:
        """Format evidence reference"""
        doc_info = self.document_registry.get(doc_id, {})
        reference = f"[{doc_id}: {doc_info.get('filename', 'Unknown')}"
        
        if page:
            reference += f", p.{page}"
        if paragraph:
            reference += f", ¶{paragraph}"
        
        reference += "]"
        return reference
    
    def _get_claude_enhanced_analysis(self, prompt: str, phase_data: Dict) -> str:
        """
        Get Claude to enhance report content with deeper analysis
        
        Args:
            prompt: Specific prompt for Claude
            phase_data: Phase knowledge to analyse
            
        Returns:
            Claude's enhanced analysis
        """
        full_prompt = f"""
        Based on the following phase analysis, {prompt}
        
        Phase Data:
        {json.dumps(phase_data, indent=2)[:5000]}
        
        Document Registry:
        {json.dumps(list(self.document_registry.keys()), indent=2)}
        
        CRITICAL: Every finding must reference specific documents using format [DOC_XXXX].
        Be aggressive in identifying evidence that destroys Process Holdings' case.
        Focus on what wins for Lismore.
        """
        
        response = self.api_client.analyse_documents(
            documents=[],
            prompt=full_prompt,
            phase="report_generation"
        )
        
        return response
    
    # ==================== PHASE 1 REPORTS (3 Reports) ====================
    
    def generate_phase_1_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 1: Initial Document Landscape reports
        Strategy: Map the battlefield, identify ammunition, spot weaknesses
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 1 reports with Claude enhancement...")
        
        # 1. Document Classification & Priority Matrix
        doc_matrix_prompt = """
        Create a comprehensive document classification matrix that:
        1. Categorises each document by type (contract, email, financial, board minutes, etc.)
        2. Assigns priority ratings (Critical/High/Medium/Low) based on litigation value
        3. Identifies which documents are "hot docs" that could damage Process Holdings
        4. Flags documents that appear altered, missing pages, or suspicious
        5. Maps document relationships and dependencies
        
        Format as a strategic matrix for the legal team.
        """
        doc_matrix = self._get_claude_enhanced_analysis(doc_matrix_prompt, phase_data)
        
        doc_matrix_content = f"""
{'='*80}
DOCUMENT CLASSIFICATION & PRIORITY MATRIX
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Documents: {len(self.document_registry)}

CLAUDE'S STRATEGIC CLASSIFICATION:
{'-'*80}
{doc_matrix}

PRIORITY ACTIONS:
1. Immediate review of all "Critical" classified documents
2. Deep forensic analysis of suspected altered documents
3. Cross-reference related document chains
{'='*80}
"""
        
        matrix_file = f"{self.output_dir}/1_document_priority_matrix_{timestamp}.txt"
        with open(matrix_file, 'w', encoding='utf-8') as f:
            f.write(doc_matrix_content)
        reports['document_matrix'] = matrix_file
        
        # 2. Initial Irregularities & Red Flags Report
        red_flags_prompt = """
        Identify and analyse ALL irregularities and red flags found, including:
        1. Missing documents that should logically exist (with specific references to documents mentioning them)
        2. Chronological gaps or impossibilities
        3. Metadata anomalies or signs of tampering
        4. Unusual communication patterns or sudden changes
        5. Documents that contradict each other
        6. Any "too perfect" documents that might be fabricated
        
        Rank these by potential impact on the case. Be paranoid - assume Process Holdings is hiding something.
        """
        red_flags = self._get_claude_enhanced_analysis(red_flags_prompt, phase_data)
        
        red_flags_content = f"""
{'='*80}
INITIAL IRREGULARITIES & RED FLAGS ANALYSIS
{'='*80}
⚠️ CRITICAL FINDINGS REQUIRING IMMEDIATE INVESTIGATION ⚠️

{red_flags}

RECOMMENDED IMMEDIATE ACTIONS:
1. Forensic examination of flagged documents
2. Deposition questions focused on identified gaps
3. Discovery requests for missing referenced documents
{'='*80}
"""
        
        red_flags_file = f"{self.output_dir}/1_red_flags_analysis_{timestamp}.txt"
        with open(red_flags_file, 'w', encoding='utf-8') as f:
            f.write(red_flags_content)
        reports['red_flags'] = red_flags_file
        
        # 3. Key Actor Network Analysis
        actors_prompt = """
        Map the complete network of actors and their roles:
        1. Identify all individuals mentioned in documents with their roles
        2. Map communication patterns between actors (who talks to whom, frequency, tone)
        3. Identify power dynamics and decision-making hierarchy
        4. Flag unusual exclusions/inclusions in communications
        5. Spot any undisclosed relationships or conflicts
        6. Identify who appears to be hiding information or acting suspiciously
        
        Focus on exposing hidden relationships that could benefit Lismore.
        """
        actors = self._get_claude_enhanced_analysis(actors_prompt, phase_data)
        
        actors_content = f"""
{'='*80}
KEY ACTOR NETWORK & COMMUNICATION ANALYSIS
{'='*80}

{actors}

STRATEGIC IMPLICATIONS:
- Target depositions based on identified power players
- Exploit identified conflicts of interest
- Focus on actors showing suspicious behaviour patterns
{'='*80}
"""
        
        actors_file = f"{self.output_dir}/1_actor_network_analysis_{timestamp}.txt"
        with open(actors_file, 'w', encoding='utf-8') as f:
            f.write(actors_content)
        reports['actor_network'] = actors_file
        
        print(f"✓ Generated 3 Phase 1 reports")
        return reports
    
    # ==================== PHASE 2 REPORTS (3 Reports) ====================
    
    def generate_phase_2_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 2: Chronological Deep Dive reports
        Strategy: Control the timeline narrative, find temporal impossibilities
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 2 reports with Claude enhancement...")
        
        # 1. Master Timeline with Conflict Analysis
        timeline_prompt = """
        Construct a devastating master timeline that:
        1. Lists EVERY dated event with precise document references
        2. Identifies timeline conflicts and impossibilities
        3. Highlights periods of suspicious activity or silence
        4. Shows how Process Holdings' story doesn't fit the timeline
        5. Maps parallel tracks of activity that show deception
        6. Identifies "smoking gun" moments in the chronology
        
        Format with exact dates and document references. Flag every inconsistency.
        """
        timeline = self._get_claude_enhanced_analysis(timeline_prompt, phase_data)
        
        timeline_file = f"{self.output_dir}/2_master_timeline_analysis_{timestamp}.txt"
        with open(timeline_file, 'w', encoding='utf-8') as f:
            f.write(f"MASTER TIMELINE WITH CONFLICT ANALYSIS\n{'='*80}\n{timeline}")
        reports['master_timeline'] = timeline_file
        
        # 2. Critical Period Deep Analysis
        periods_prompt = """
        Identify and analyse critical periods in the dispute:
        1. The "point of no return" when the relationship broke down
        2. Periods of intense activity (what were they hiding?)
        3. Suspicious gaps or silences (what's missing?)
        4. Periods where Process Holdings' behaviour changed dramatically
        5. Time periods with the most documentary evidence of wrongdoing
        
        For each period, explain what Process Holdings was really doing and why it matters.
        """
        periods = self._get_claude_enhanced_analysis(periods_prompt, phase_data)
        
        periods_file = f"{self.output_dir}/2_critical_periods_analysis_{timestamp}.txt"
        with open(periods_file, 'w', encoding='utf-8') as f:
            f.write(f"CRITICAL PERIOD ANALYSIS\n{'='*80}\n{periods}")
        reports['critical_periods'] = periods_file
        
        # 3. Timeline Demolition Report
        demolition_prompt = """
        Demolish Process Holdings' likely chronological narrative by:
        1. Identifying where their timeline claims are impossible given the documents
        2. Finding documents that contradict their sequence of events
        3. Exposing attempts to backdate or alter chronology
        4. Showing where they've tried to hide critical events
        5. Proving their timeline is fabricated or misleading
        
        This should destroy their credibility on timing claims.
        """
        demolition = self._get_claude_enhanced_analysis(demolition_prompt, phase_data)
        
        demolition_file = f"{self.output_dir}/2_timeline_demolition_{timestamp}.txt"
        with open(demolition_file, 'w', encoding='utf-8') as f:
            f.write(f"PROCESS HOLDINGS TIMELINE DEMOLITION\n{'='*80}\n{demolition}")
        reports['timeline_demolition'] = demolition_file
        
        print(f"✓ Generated 3 Phase 2 reports")
        return reports
    
    # ==================== PHASE 3 REPORTS (3 Reports) ====================
    
    def generate_phase_3_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 3: Party Behaviour Analysis reports
        Strategy: Expose bad faith, prove malicious intent
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 3 reports with Claude enhancement...")
        
        # 1. Bad Faith Behaviour Dossier
        bad_faith_prompt = """
        Compile a comprehensive dossier of Process Holdings' bad faith behaviour:
        1. Deliberate delays and obstruction tactics
        2. Lies and misrepresentations (with proof)
        3. Attempts to mislead or deceive Lismore
        4. Breaches of duties to cooperate or act in good faith
        5. Evidence of malicious or vindictive conduct
        6. Patterns showing intentional harm to Lismore
        
        Each instance must have specific document evidence. This dossier should make them look terrible.
        """
        bad_faith = self._get_claude_enhanced_analysis(bad_faith_prompt, phase_data)
        
        bad_faith_file = f"{self.output_dir}/3_bad_faith_dossier_{timestamp}.txt"
        with open(bad_faith_file, 'w', encoding='utf-8') as f:
            f.write(f"BAD FAITH BEHAVIOUR DOSSIER\n{'='*80}\n{bad_faith}")
        reports['bad_faith_dossier'] = bad_faith_file
        
        # 2. Behavioural Psychology Analysis
        psychology_prompt = """
        Analyse the psychological patterns and motivations revealed:
        1. What emotional states do their communications reveal (panic, deception, aggression)?
        2. Identify manipulation tactics and gaslighting attempts
        3. Spot desperation moves and cover-up behaviours
        4. Analyse language changes that indicate deception
        5. Identify when they realised they were in trouble
        6. What are they most afraid of being discovered?
        
        Use this to predict their next moves and identify psychological pressure points.
        """
        psychology = self._get_claude_enhanced_analysis(psychology_prompt, phase_data)
        
        psychology_file = f"{self.output_dir}/3_behavioural_psychology_{timestamp}.txt"
        with open(psychology_file, 'w', encoding='utf-8') as f:
            f.write(f"BEHAVIOURAL PSYCHOLOGY ANALYSIS\n{'='*80}\n{psychology}")
        reports['behavioural_psychology'] = psychology_file
        
        # 3. Communication Forensics Report
        comms_prompt = """
        Conduct forensic analysis of all communications:
        1. Tone shifts that indicate problems or deception
        2. Missing communications that should exist
        3. Sudden formality indicating legal awareness
        4. Off-the-record communications referenced but not provided
        5. Language patterns suggesting different authors or legal editing
        6. Admissions or damaging statements in informal communications
        
        Find the communications that damn them.
        """
        comms = self._get_claude_enhanced_analysis(comms_prompt, phase_data)
        
        comms_file = f"{self.output_dir}/3_communication_forensics_{timestamp}.txt"
        with open(comms_file, 'w', encoding='utf-8') as f:
            f.write(f"COMMUNICATION FORENSICS REPORT\n{'='*80}\n{comms}")
        reports['communication_forensics'] = comms_file
        
        print(f"✓ Generated 3 Phase 3 reports")
        return reports
    
    # ==================== PHASE 4 REPORTS (2 Strategic Reports) ====================
    
    def generate_phase_4_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 4: Theory Construction reports
        Strategy: Build unassailable narrative, destroy theirs
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 4 reports with Claude enhancement...")
        
        # 1. Lismore's Winning Narrative Construction
        winning_prompt = """
        Construct Lismore's complete winning narrative that:
        1. Tells a compelling, coherent story of Process Holdings' wrongdoing
        2. Explains every major event and document in our favour
        3. Makes Process Holdings' conduct appear indefensible
        4. Addresses and refutes any potential defences
        5. Creates emotional impact (David vs Goliath, betrayal, injustice)
        6. Ties every element to specific documentary evidence
        
        This narrative should be so compelling that even Process Holdings' lawyers doubt their client.
        Include specific quotes and document references that prove each element.
        """
        winning = self._get_claude_enhanced_analysis(winning_prompt, phase_data)
        
        winning_content = f"""
{'='*80}
LISMORE'S WINNING NARRATIVE
{'='*80}
"The Story That Wins The Case"

{winning}

DEPLOYMENT STRATEGY:
1. Opening statement framework
2. Witness examination roadmap  
3. Closing argument structure
4. Settlement negotiation positioning
{'='*80}
"""
        
        winning_file = f"{self.output_dir}/4_winning_narrative_{timestamp}.txt"
        with open(winning_file, 'w', encoding='utf-8') as f:
            f.write(winning_content)
        reports['winning_narrative'] = winning_file
        
        # 2. Opposition Theory Destruction Playbook
        destruction_prompt = """
        Create a playbook to destroy every possible Process Holdings defence:
        1. Anticipate their likely theories and excuses
        2. Identify documents that contradict each defence
        3. Prepare cross-examination traps using their own documents
        4. Find the lies they've already told that box them in
        5. Identify which defences are mutually exclusive (they can't both be true)
        6. Show how their defences actually prove our case
        
        For each potential defence, provide the exact evidence that destroys it.
        """
        destruction = self._get_claude_enhanced_analysis(destruction_prompt, phase_data)
        
        destruction_file = f"{self.output_dir}/4_defence_destruction_playbook_{timestamp}.txt"
        with open(destruction_file, 'w', encoding='utf-8') as f:
            f.write(f"DEFENCE DESTRUCTION PLAYBOOK\n{'='*80}\n{destruction}")
        reports['defence_destruction'] = destruction_file
        
        print(f"✓ Generated 2 Phase 4 reports")
        return reports
    
    # ==================== PHASE 5 REPORTS (3 Reports) ====================
    
    def generate_phase_5_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 5: Evidence Analysis reports
        Strategy: Weaponise evidence, expose gaps
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 5 reports with Claude enhancement...")
        
        # 1. Evidence Power Ranking & Deployment Strategy
        evidence_ranking_prompt = """
        Create a strategic evidence ranking that:
        1. Ranks all evidence by destructive power (S-tier to F-tier)
        2. Identifies "combo attacks" where evidence works together
        3. Maps evidence to specific claims and counterclaims
        4. Identifies evidence Process Holdings can't explain away
        5. Highlights evidence that triggers cost sanctions or criminal referrals
        6. Creates optimal evidence deployment sequence for maximum impact
        
        Think like a chess grandmaster - how do we deploy evidence for checkmate?
        """
        ranking = self._get_claude_enhanced_analysis(evidence_ranking_prompt, phase_data)
        
        ranking_file = f"{self.output_dir}/5_evidence_power_ranking_{timestamp}.txt"
        with open(ranking_file, 'w', encoding='utf-8') as f:
            f.write(f"EVIDENCE POWER RANKING & DEPLOYMENT STRATEGY\n{'='*80}\n{ranking}")
        reports['evidence_ranking'] = ranking_file
        
        # 2. Missing Evidence & Adverse Inference Report
        missing_prompt = """
        Identify all missing evidence and build adverse inference arguments:
        1. Documents referenced but not produced (with specific references)
        2. Obvious gaps in document series (missing emails, board minutes, etc.)
        3. Documents Process Holdings must have but claims don't exist
        4. Metadata showing deleted/destroyed documents
        5. Legal obligations to maintain records they haven't produced
        6. Third party documents they failed to obtain
        
        For each gap, explain the adverse inference we should argue and why the missing evidence must be damaging.
        """
        missing = self._get_claude_enhanced_analysis(missing_prompt, phase_data)
        
        missing_file = f"{self.output_dir}/5_missing_evidence_adverse_inference_{timestamp}.txt"
        with open(missing_file, 'w', encoding='utf-8') as f:
            f.write(f"MISSING EVIDENCE & ADVERSE INFERENCE ARGUMENTS\n{'='*80}\n{missing}")
        reports['missing_evidence'] = missing_file
        
        # 3. Cross-Examination Trap Report
        cross_exam_prompt = """
        Design cross-examination traps using the evidence:
        1. Questions where any answer hurts Process Holdings
        2. Document combinations that prove lies
        3. Prior inconsistent statements to impeach witnesses
        4. "Gotcha" moments using their own evidence
        5. Questions that force admissions or obvious lies
        6. Setup questions that lead to devastating document reveals
        
        Provide exact question sequences with document references for maximum destruction.
        """
        cross_exam = self._get_claude_enhanced_analysis(cross_exam_prompt, phase_data)
        
        cross_exam_file = f"{self.output_dir}/5_cross_examination_traps_{timestamp}.txt"
        with open(cross_exam_file, 'w', encoding='utf-8') as f:
            f.write(f"CROSS-EXAMINATION TRAP PLAYBOOK\n{'='*80}\n{cross_exam}")
        reports['cross_examination'] = cross_exam_file
        
        print(f"✓ Generated 3 Phase 5 reports")
        return reports
    
    # ==================== PHASE 6 REPORTS (3 Critical Reports) ====================
    
    def generate_phase_6_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 6: Smoking Guns & Kill Shots reports
        Strategy: Identify case-ending evidence
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 6 reports with Claude enhancement...")
        
        # 1. Smoking Guns Dossier
        smoking_guns_prompt = """
        Identify and rank ALL smoking guns - the evidence that ends their case:
        1. Direct admissions of wrongdoing
        2. Proof of intentional misconduct or fraud
        3. Evidence of cover-ups or destruction
        4. Documents proving perjury or lies to the court
        5. Material that triggers criminal liability
        6. Evidence so damaging they must settle
        
        For each smoking gun:
        - Quote the exact damaging text
        - Explain why it's case-ending
        - Provide strategic deployment advice
        - Identify combination attacks with other evidence
        """
        smoking_guns = self._get_claude_enhanced_analysis(smoking_guns_prompt, phase_data)
        
        smoking_content = f"""
{'='*80}
🔫 SMOKING GUNS DOSSIER - CASE-ENDING EVIDENCE 🔫
{'='*80}
⚠️ HIGHEST CLASSIFICATION - LITIGATION PRIVILEGE ⚠️

{smoking_guns}

STRATEGIC DEPLOYMENT:
- Hold most devastating evidence for maximum impact
- Consider staged revelation for settlement leverage
- Prepare media strategy for public pressure
{'='*80}
"""
        
        smoking_file = f"{self.output_dir}/6_smoking_guns_dossier_{timestamp}.txt"
        with open(smoking_file, 'w', encoding='utf-8') as f:
            f.write(smoking_content)
        reports['smoking_guns'] = smoking_file
        
        # 2. Settlement Leverage Maximisation Report
        settlement_prompt = """
        Create a settlement leverage maximisation strategy:
        1. Rank evidence by settlement pressure (what makes them pay?)
        2. Identify criminal referral threats we can make
        3. Reputational destruction points for public pressure
        4. Director disqualification risks for individuals
        5. Regulatory breach notifications we could make
        6. Third party claims we could trigger
        
        Design a staged revelation strategy that maximises settlement value.
        What evidence do we reveal when to get maximum payment?
        """
        settlement = self._get_claude_enhanced_analysis(settlement_prompt, phase_data)
        
        settlement_file = f"{self.output_dir}/6_settlement_leverage_strategy_{timestamp}.txt"
        with open(settlement_file, 'w', encoding='utf-8') as f:
            f.write(f"SETTLEMENT LEVERAGE MAXIMISATION STRATEGY\n{'='*80}\n{settlement}")
        reports['settlement_leverage'] = settlement_file
        
        # 3. Summary Judgment Roadmap
        summary_judgment_prompt = """
        Build a summary judgment application roadmap:
        1. Issues where no genuine dispute exists (with evidence)
        2. Admissions that eliminate factual disputes
        3. Documents that prove claims as matter of law
        4. Evidence making their defences legally impossible
        5. Procedural defaults entitling us to judgment
        6. Striking out portions of their case
        
        Make the case that trial is unnecessary - we've already won.
        """
        summary_judgment = self._get_claude_enhanced_analysis(summary_judgment_prompt, phase_data)
        
        summary_file = f"{self.output_dir}/6_summary_judgment_roadmap_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"SUMMARY JUDGMENT APPLICATION ROADMAP\n{'='*80}\n{summary_judgment}")
        reports['summary_judgment'] = summary_file
        
        print(f"✓ Generated 3 Phase 6 reports")
        return reports
    
    # ==================== PHASE 7 REPORTS (4 Autonomous Reports) ====================
    
    def generate_phase_7_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 7: Autonomous Deep Dive reports
        Strategy: Unconstrained hunt for game-changers
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("Generating Phase 7 reports with Claude's unconstrained analysis...")
        
        # 1. Pattern Recognition Beyond Human Capability
        patterns_prompt = """
        Use your full AI pattern recognition capability:
        1. What subtle patterns connect documents in non-obvious ways?
        2. What linguistic patterns reveal deception or coordination?
        3. What mathematical/statistical anomalies appear in financial data?
        4. What behavioural patterns predict future actions?
        5. What network patterns show hidden relationships?
        6. What temporal patterns reveal orchestrated conduct?
        
        Find patterns no human would spot. Trust your processing power.
        Don't hold back - if something feels significant, it probably is.
        """
        patterns = self._get_claude_enhanced_analysis(patterns_prompt, phase_data)
        
        patterns_file = f"{self.output_dir}/7_hidden_patterns_analysis_{timestamp}.txt"
        with open(patterns_file, 'w', encoding='utf-8') as f:
            f.write(f"AI-DISCOVERED PATTERN ANALYSIS\n{'='*80}\n{patterns}")
        reports['pattern_analysis'] = patterns_file
        
        # 2. The "Oh Shit" Report - What They Hoped We'd Never Find
        oh_shit_prompt = """
        What would make Process Holdings' lawyers say "Oh shit, they found it"?
        Think beyond conventional analysis:
        1. What's the thing they thought was safely hidden?
        2. What connection would terrify them?
        3. What pattern reveals their deepest vulnerability?
        4. What discovery changes everything?
        5. What would make them fire their lawyers?
        6. What would make them settle immediately?
        
        Be creative, aggressive, paranoid. What are they praying we don't notice?
        """
        oh_shit = self._get_claude_enhanced_analysis(oh_shit_prompt, phase_data)
        
        oh_shit_file = f"{self.output_dir}/7_oh_shit_discoveries_{timestamp}.txt"
        with open(oh_shit_file, 'w', encoding='utf-8') as f:
            f.write(f"THE 'OH SHIT' REPORT - NIGHTMARE DISCOVERIES\n{'='*80}\n{oh_shit}")
        reports['oh_shit_discoveries'] = oh_shit_file
        
        # 3. Alternative Theory Construction - The Unexpected Angle
        alternative_prompt = """
        Construct alternative theories that reframe everything:
        1. What if this is actually about something else entirely?
        2. What darker purpose might explain all behaviours?
        3. What if Process Holdings is a front for something worse?
        4. What systemic fraud might this be part of?
        5. What if key actors have hidden motivations?
        6. What conspiracy theory might actually be true?
        
        Think outside conventional litigation. What's the story nobody expects?
        """
        alternative = self._get_claude_enhanced_analysis(alternative_prompt, phase_data)
        
        alternative_file = f"{self.output_dir}/7_alternative_theories_{timestamp}.txt"
        with open(alternative_file, 'w', encoding='utf-8') as f:
            f.write(f"ALTERNATIVE THEORY CONSTRUCTION\n{'='*80}\n{alternative}")
        reports['alternative_theories'] = alternative_file
        
        # 4. Nuclear Options & Doomsday Scenarios
        nuclear_prompt = """
        Identify nuclear options - the most aggressive possible moves:
        1. Criminal referrals we could make (fraud, forgery, perjury)
        2. Regulatory complaints that trigger investigations
        3. Public disclosure that destroys reputations
        4. Third party notifications that cascade problems
        5. Asset freezing or urgent injunctions we could seek
        6. Personal liability attacks on directors/individuals
        
        Also identify what Process Holdings might try (so we can pre-empt).
        What's the most aggressive strategy possible?
        """
        nuclear = self._get_claude_enhanced_analysis(nuclear_prompt, phase_data)
        
        nuclear_file = f"{self.output_dir}/7_nuclear_options_{timestamp}.txt"
        with open(nuclear_file, 'w', encoding='utf-8') as f:
            f.write(f"NUCLEAR OPTIONS & MAXIMUM AGGRESSION STRATEGIES\n{'='*80}\n{nuclear}")
        reports['nuclear_options'] = nuclear_file
        
        print(f"✓ Generated 4 Phase 7 reports")
        return reports
    
    # ==================== MASTER GENERATION FUNCTION ====================
    
    def generate_all_phase_reports(self, documents: List[Dict]) -> Dict[str, Dict]:
        """
        Generate all reports for phases 1-7 (skipping 0A & 0B)
        
        Args:
            documents: List of analysed documents
            
        Returns:
            Dictionary mapping phases to their generated reports
        """
        # Register documents first
        self.register_documents(documents)
        
        all_reports = {}
        knowledge = self.knowledge_manage.get_all_knowledge()
        
        print("\n" + "="*80)
        print("GENERATING STRATEGIC REPORTS FOR LISMORE CAPITAL")
        print("="*80)
        
        # Phase-specific report generators (excluding 0A and 0B)
        phase_report_generators = {
            '1': self.generate_phase_1_reports,  # 3 reports
            '2': self.generate_phase_2_reports,  # 3 reports
            '3': self.generate_phase_3_reports,  # 3 reports
            '4': self.generate_phase_4_reports,  # 2 reports
            '5': self.generate_phase_5_reports,  # 3 reports
            '6': self.generate_phase_6_reports,  # 3 reports
            '7': self.generate_phase_7_reports   # 4 reports
        }
        
        # Generate reports for each completed phase
        for phase, generator in phase_report_generators.items():
            if phase in knowledge:
                print(f"\n→ Processing Phase {phase}...")
                all_reports[phase] = generator(knowledge[phase])
        
        # Generate master summary
        self._generate_master_war_room_summary(all_reports, knowledge)
        
        print("\n" + "="*80)
        print("✓ ALL REPORTS GENERATED SUCCESSFULLY")
        print(f"✓ Total Reports: {sum(len(r) for r in all_reports.values())} strategic documents")
        print(f"✓ Output directory: {self.output_dir}")
        print("="*80)
        
        return all_reports
    
    def _generate_master_war_room_summary(self, all_reports: Dict, knowledge: Dict):
        """Generate master war room summary for senior partners"""
        
        # Use Claude to synthesise everything
        war_room_prompt = """
        Create an executive war room summary that:
        1. Lists the 5 most devastating pieces of evidence (with references)
        2. Identifies the 3 strongest legal arguments
        3. Recommends immediate actions (top 5 priorities)
        4. Estimates settlement value range based on evidence
        5. Identifies biggest risks to Lismore's case
        6. Provides a "confidence score" for victory
        
        This is for senior partners who need rapid decision-making intelligence.
        Be direct, aggressive, and focus on what wins.
        """
        
        # Combine all knowledge for summary
        combined_knowledge = {
            'phases_completed': list(knowledge.keys()),
            'total_documents': len(self.document_registry),
            'phase_6_findings': knowledge.get('6', {}).get('findings', {}),
            'phase_7_insights': knowledge.get('7', {}).get('findings', {})
        }
        
        war_room = self._get_claude_enhanced_analysis(war_room_prompt, combined_knowledge)
        
        content = f"""
{'='*80}
WAR ROOM EXECUTIVE SUMMARY - PARTNERS ONLY
{'='*80}
CASE: LISMORE CAPITAL VS PROCESS HOLDINGS LTD
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Classification: STRICTLY CONFIDENTIAL - LITIGATION PRIVILEGE

{war_room}

{'='*80}
RECOMMENDED IMMEDIATE ACTION:
Call emergency partner meeting to approve aggressive litigation strategy.
{'='*80}
"""
        
        filename = f"{self.output_dir}/MASTER_WAR_ROOM_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n⚔️ Master War Room Summary generated: {filename}")