"""
Enhanced Output Generator for Litigation Intelligence System
Generates strategic reports for Phases 1-7 with full Claude integration
Phase 0A & 0B: Knowledge retention only (summary available)
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
from pathlib import Path

from knowledge_manage import KnowledgeManager
from api_client import ClaudeAPIClient


class OutputGenerator:
    """Generates strategic litigation reports from analysis results"""
    
    def __init__(self, knowledge_manage: KnowledgeManager):
        """
        Initialise output generator
        
        Args:
            knowledge_manage: KnowledgeManager instance with analysis results
        """
        self.knowledge_manage = knowledge_manage
        self.api_client = ClaudeAPIClient()
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
                'content': doc.get('content', '')
            }
    
    def _extract_page_count(self, content: str) -> int:
        """Extract approximate page count from content"""
        return max(1, len(content) // 3000)
    
    def _format_evidence_reference(self, doc_id: str, page: Optional[int] = None, 
                                  paragraph: Optional[int] = None) -> str:
        """Format evidence reference for legal citation"""
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
            prompt: Specific analysis prompt for Claude
            phase_data: Phase knowledge to analyse
            
        Returns:
            Claude's enhanced analysis
        """
        # Extract rich metadata from enhanced phase data
        patterns = phase_data.get('patterns', {})
        contradictions = phase_data.get('contradictions', {})
        strategy = phase_data.get('strategy', {})
        
        # Build context based on phase type
        enhanced_context = ""
        
        # Phase 0A - Legal Framework
        if 'legal_weapons' in phase_data:
            enhanced_context = f"""
            LEGAL INTELLIGENCE AVAILABLE:
            - Legal Weapons: {len(phase_data.get('offensive_weapons', '').split('\n')) if phase_data.get('offensive_weapons') else 0}
            - Procedural Advantages: {len(phase_data.get('procedural_traps', '').split('\n')) if phase_data.get('procedural_traps') else 0}
            - Criminal Crossovers: {len(phase_data.get('criminal_threats', '').split('\n')) if phase_data.get('criminal_threats') else 0}
            - Settlement Leverage: {len(phase_data.get('settlement_leverage', '').split('\n')) if phase_data.get('settlement_leverage') else 0}
            
            Synthesis: {phase_data.get('synthesis', '')[:1000]}
            """
        
        # Phase 0B - Case Context
        elif 'admissions_hunt' in phase_data:
            enhanced_context = f"""
            CASE INTELLIGENCE EXTRACTED:
            - Admissions Found: {phase_data.get('admissions_hunt', '').count('ADMISSION:') if phase_data.get('admissions_hunt') else 0}
            - Position Changes: {phase_data.get('position_evolution', '').count('Version') if phase_data.get('position_evolution') else 0}
            - Missing Evidence: {phase_data.get('missing_evidence', '').count('MISSING:') if phase_data.get('missing_evidence') else 0}
            - Credibility Gaps: {phase_data.get('credibility_gaps', '').count('PROBLEM:') if phase_data.get('credibility_gaps') else 0}
            - Timeline Conflicts: {phase_data.get('timeline_conflicts', '').count('IMPOSSIBILITY:') if phase_data.get('timeline_conflicts') else 0}
            """
        
        # Phases 1-7 - Main Analysis
        else:
            if patterns and 'findings' in patterns:
                enhanced_context += f"""
                PATTERNS DISCOVERED:
                {patterns.get('findings', '')[:1000]}
                """
            
            if contradictions and 'findings' in contradictions:
                enhanced_context += f"""
                
                CONTRADICTIONS IDENTIFIED:
                {contradictions.get('findings', '')[:1000]}
                """
            
            if strategy and 'findings' in strategy:
                enhanced_context += f"""
                
                STRATEGIC SYNTHESIS:
                {strategy.get('findings', '')[:1000]}
                """
            
            # Add special analysis if present
            if 'special_analysis' in phase_data:
                enhanced_context += f"""
                
                SPECIAL ANALYSIS:
                {str(phase_data['special_analysis'])[:1000]}
                """
        
        # Build full prompt
        full_prompt = f"""
        Based on the following enhanced phase analysis, {prompt}
        
        {enhanced_context}
        
        Phase Data Summary:
        Total findings extracted from this phase's analysis.
        
        Document Registry:
        {len(self.document_registry)} documents available for referencing
        Document IDs: {', '.join(list(self.document_registry.keys())[:20])}...
        
        CRITICAL REQUIREMENTS:
        1. Reference EVERY finding to specific documents using format [DOC_XXXX]
        2. Build on the patterns and contradictions already identified
        3. Be aggressive in identifying evidence that destroys Process Holdings
        4. Focus on what wins for Lismore
        5. Rank findings by strategic value (1-10)
        6. Provide exact quotes where available
        7. Suggest follow-up actions for each finding
        
        Remember: We are building a case to DESTROY Process Holdings.
        """
        
        try:
            response = self.api_client.analyse_documents(
                documents=[],
                prompt=full_prompt,
                phase="report_generation"
            )
            return response
        except Exception as e:
            print(f"⚠️  Claude enhancement failed: {e}")
            # Fallback to basic extraction from phase data
            return self._extract_basic_findings(phase_data)
    
    def _extract_basic_findings(self, phase_data: Dict) -> str:
        """Fallback extraction if Claude call fails"""
        findings = []
        
        for key, value in phase_data.items():
            if isinstance(value, dict) and 'findings' in value:
                findings.append(f"{key.upper()}:\n{value['findings']}\n")
            elif isinstance(value, str) and len(value) > 100:
                findings.append(f"{key.upper()}:\n{value[:1000]}\n")
        
        return "\n".join(findings) if findings else "Analysis findings require manual review."
    
    # ==================== PHASE 0 SUMMARY (Foundation Intelligence) ====================
    
    def generate_phase_0_summary(self, knowledge: Dict) -> str:
        """Generate strategic summary of Phase 0A and 0B findings"""
        
        phase_0a = knowledge.get('0A', {})
        phase_0b = knowledge.get('0B', {})
        
        if not phase_0a and not phase_0b:
            print("⚠️  No Phase 0 data available")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"{self.output_dir}/0_foundation_intelligence_{timestamp}.txt"
        
        summary_content = f"""
{'='*80}
FOUNDATION INTELLIGENCE SUMMARY
Phases 0A & 0B - Legal Framework & Case Context
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*80}

PHASE 0A - LEGAL ARSENAL:
{'-'*40}
"""
        
        if phase_0a:
            summary_content += f"""
Offensive Weapons Identified: {phase_0a.get('offensive_weapons', '').count('DOCTRINE:') if phase_0a.get('offensive_weapons') else 'Unknown'}
Defensive Shields Available: {phase_0a.get('defensive_shields', '').count('SHIELD:') if phase_0a.get('defensive_shields') else 'Unknown'}
Procedural Traps Found: {phase_0a.get('procedural_traps', '').count('TRAP:') if phase_0a.get('procedural_traps') else 'Unknown'}
Settlement Leverage Points: {phase_0a.get('settlement_leverage', '').count('PRESSURE:') if phase_0a.get('settlement_leverage') else 'Unknown'}
Criminal Threats Available: {phase_0a.get('criminal_threats', '').count('CRIME:') if phase_0a.get('criminal_threats') else 'Unknown'}

Legal Synthesis:
{phase_0a.get('synthesis', 'No synthesis available')[:2000]}
"""
        else:
            summary_content += "No Phase 0A data available\n"
        
        summary_content += f"""

PHASE 0B - CASE INTELLIGENCE:
{'-'*40}
"""
        
        if phase_0b:
            summary_content += f"""
Admissions Captured: {phase_0b.get('admissions_hunt', '').count('ADMISSION:') if phase_0b.get('admissions_hunt') else 'Unknown'}
Position Evolution Tracked: {phase_0b.get('position_evolution', '').count('Version') if phase_0b.get('position_evolution') else 'Unknown'}
Missing Evidence Items: {phase_0b.get('missing_evidence', '').count('MISSING:') if phase_0b.get('missing_evidence') else 'Unknown'}
Credibility Issues Found: {phase_0b.get('credibility_gaps', '').count('PROBLEM:') if phase_0b.get('credibility_gaps') else 'Unknown'}
Timeline Impossibilities: {phase_0b.get('timeline_conflicts', '').count('IMPOSSIBILITY:') if phase_0b.get('timeline_conflicts') else 'Unknown'}

Key Admissions Found:
{phase_0b.get('admissions_hunt', 'No admissions data')[:2000]}
"""
        else:
            summary_content += "No Phase 0B data available\n"
        
        summary_content += f"""

COMBINED STRATEGIC ADVANTAGE:
{'-'*40}
This foundation intelligence provides Lismore with:
1. Complete legal framework for attack and defence
2. Map of Process Holdings' vulnerabilities and admissions
3. Inventory of contradictions and timeline impossibilities
4. Blueprint for document requests and discovery demands
5. Cross-examination ammunition and witness impeachment material
6. Settlement leverage points and criminal referral options

DEPLOYMENT STRATEGY:
Phase 1-7 will now hunt for documentary evidence that:
- Proves the legal elements identified in Phase 0A
- Expands the admissions found in Phase 0B
- Exploits the contradictions and gaps discovered
- Supports criminal referrals and regulatory complaints
- Maximises settlement pressure and litigation advantage

{'='*80}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"✓ Generated Phase 0 Foundation Intelligence Summary")
        return summary_file
    
    # ==================== PHASE 1 REPORTS ====================
    
    def generate_phase_1_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 1: Initial Document Landscape reports
        Strategy: Map the battlefield, identify ammunition, spot weaknesses
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 1 reports with Claude enhancement...")
        
        # 1. Document Classification & Priority Matrix
        doc_matrix_prompt = """
        Create a comprehensive document classification matrix that:
        1. Categorises each document by type (contract, email, financial, board minutes, etc.)
        2. Assigns priority ratings (Critical/High/Medium/Low) based on litigation value
        3. Identifies which documents are "hot docs" that could damage Process Holdings
        4. Flags documents that appear altered, missing pages, or suspicious
        5. Maps document relationships and dependencies
        6. Identifies document chains and threads
        7. Spots gaps in document production
        
        Format as a strategic matrix for the legal team.
        Rank documents by their ability to destroy Process Holdings.
        """
        
        doc_matrix = self._get_claude_enhanced_analysis(doc_matrix_prompt, phase_data)
        
        doc_matrix_content = f"""
{'='*80}
DOCUMENT CLASSIFICATION & PRIORITY MATRIX
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Documents Analysed: {len(self.document_registry)}

{doc_matrix}

IMMEDIATE ACTIONS REQUIRED:
1. Forensic analysis of all "Critical" documents
2. Authentication challenges for suspicious documents
3. Depositions to explore document gaps
4. Requests for missing documents in chains
{'='*80}
"""
        
        matrix_file = f"{self.output_dir}/1_document_priority_matrix_{timestamp}.txt"
        with open(matrix_file, 'w', encoding='utf-8') as f:
            f.write(doc_matrix_content)
        reports['document_matrix'] = matrix_file
        
        # 2. Initial Red Flags & Irregularities Report
        red_flags_prompt = """
        Identify and analyse ALL irregularities and red flags found:
        1. Missing documents that should logically exist
        2. Chronological gaps or impossibilities
        3. Metadata anomalies or signs of tampering
        4. Unusual communication patterns or sudden changes
        5. Documents that contradict each other
        6. "Too perfect" documents that might be fabricated
        7. Suspicious timing of document creation
        8. Evidence of document destruction or spoliation
        
        For each red flag:
        - Describe the irregularity
        - Reference specific documents [DOC_XXXX]
        - Rate severity (1-10)
        - Suggest investigation steps
        - Identify legal implications
        """
        
        red_flags = self._get_claude_enhanced_analysis(red_flags_prompt, phase_data)
        
        red_flags_file = f"{self.output_dir}/1_red_flags_report_{timestamp}.txt"
        with open(red_flags_file, 'w', encoding='utf-8') as f:
            f.write(f"INITIAL RED FLAGS & IRREGULARITIES REPORT\n{'='*80}\n{red_flags}")
        reports['red_flags'] = red_flags_file
        
        # 3. Key Actor Network Analysis
        actors_prompt = """
        Conduct comprehensive actor network analysis:
        1. Identify ALL individuals mentioned with roles and affiliations
        2. Map communication patterns (who talks to whom, when, how often)
        3. Identify power dynamics and decision-making hierarchy
        4. Flag unusual exclusions/inclusions in communications
        5. Spot undisclosed relationships or conflicts of interest
        6. Identify who appears to be hiding information
        7. Track when lawyers first appear in communications
        8. Note tone changes when specific actors are involved
        
        Create an actor map showing:
        - Central players vs peripheral actors
        - Hidden influencers
        - Suspicious relationships
        - Potential witnesses to target
        """
        
        actors = self._get_claude_enhanced_analysis(actors_prompt, phase_data)
        
        actors_file = f"{self.output_dir}/1_actor_network_analysis_{timestamp}.txt"
        with open(actors_file, 'w', encoding='utf-8') as f:
            f.write(f"KEY ACTOR NETWORK & COMMUNICATION ANALYSIS\n{'='*80}\n{actors}")
        reports['actor_network'] = actors_file
        
        print(f"  ✓ Generated 3 Phase 1 reports")
        return reports
    
    # ==================== PHASE 2 REPORTS ====================
    
    def generate_phase_2_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 2: Chronological Deep Dive reports
        Strategy: Control the timeline narrative, find temporal impossibilities
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 2 reports with Claude enhancement...")
        
        # 1. Master Timeline with Conflict Analysis
        timeline_prompt = """
        Construct a forensic master timeline that:
        1. Lists EVERY dated event with document references [DOC_XXXX]
        2. Identifies timeline conflicts and impossibilities
        3. Highlights suspicious gaps or silence periods
        4. Shows where Process Holdings' story contradicts chronology
        5. Maps parallel tracks of activity revealing deception
        6. Identifies retroactive knowledge (knowing before possible)
        7. Spots document backdating or forward-dating
        8. Finds "smoking gun" moments
        
        Format chronologically with:
        Date | Event | Document | Conflict/Issue | Significance
        
        Flag every impossibility and inconsistency.
        """
        
        timeline = self._get_claude_enhanced_analysis(timeline_prompt, phase_data)
        
        timeline_file = f"{self.output_dir}/2_master_timeline_analysis_{timestamp}.txt"
        with open(timeline_file, 'w', encoding='utf-8') as f:
            f.write(f"MASTER TIMELINE WITH CONFLICT ANALYSIS\n{'='*80}\n{timeline}")
        reports['master_timeline'] = timeline_file
        
        # 2. Critical Period Analysis
        periods_prompt = """
        Identify and analyse critical periods:
        1. The relationship breakdown point - when and why
        2. Intense activity periods - what were they hiding?
        3. Suspicious silence periods - why no documents?
        4. Decision points where things went wrong
        5. Periods of obvious deception or cover-up
        6. When lawyers got involved and why
        7. Financial crisis or pressure points
        8. Regulatory scrutiny periods
        
        For each critical period:
        - Define exact date range
        - List all documents from period
        - Identify what's missing
        - Explain significance
        - Rate importance (1-10)
        """
        
        periods = self._get_claude_enhanced_analysis(periods_prompt, phase_data)
        
        periods_file = f"{self.output_dir}/2_critical_periods_analysis_{timestamp}.txt"
        with open(periods_file, 'w', encoding='utf-8') as f:
            f.write(f"CRITICAL PERIOD DEEP ANALYSIS\n{'='*80}\n{periods}")
        reports['critical_periods'] = periods_file
        
        # 3. Evolution of Deception Report
        evolution_prompt = """
        Track the evolution of Process Holdings' deception:
        1. How their story changed over time
        2. When cover-up activities began
        3. Evolution from cooperation to hostility
        4. Shift from informal to formal communications
        5. Introduction of lawyers and what triggered it
        6. Changes in document creation practices
        7. Evolution of financial claims/damages
        8. Shifting blame patterns
        
        Show the progression from truth to deception.
        Identify the "point of no return" where fraud began.
        """
        
        evolution = self._get_claude_enhanced_analysis(evolution_prompt, phase_data)
        
        evolution_file = f"{self.output_dir}/2_deception_evolution_{timestamp}.txt"
        with open(evolution_file, 'w', encoding='utf-8') as f:
            f.write(f"EVOLUTION OF DECEPTION ANALYSIS\n{'='*80}\n{evolution}")
        reports['deception_evolution'] = evolution_file
        
        print(f"  ✓ Generated 3 Phase 2 reports")
        return reports
    
    # ==================== PHASE 3 REPORTS ====================
    
    def generate_phase_3_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 3: Deep Contradiction & Pattern Analysis
        Strategy: Find every lie, contradiction, and impossibility
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 3 reports with Claude enhancement...")
        
        # 1. Contradiction Matrix Report
        contradiction_prompt = """
        Build a comprehensive contradiction matrix:
        1. DIRECT CONTRADICTIONS - A says X, B says Y
        2. TIMELINE IMPOSSIBILITIES - Can't have happened as claimed
        3. FINANCIAL DISCREPANCIES - Numbers don't match
        4. NARRATIVE EVOLUTION - Story changes over time
        5. MISSING DOCUMENTS - Referenced but not produced
        6. PARTICIPANT INCONSISTENCIES - Impossible attendance
        7. TECHNICAL IMPOSSIBILITIES - Violates physics/logic
        8. LEGAL CONTRADICTIONS - Conflicting legal positions
        
        Format as matrix:
        Doc1 | Doc2 | Type | Quote1 | Quote2 | Impact | How to Exploit
        
        Rank by case-killing potential.
        """
        
        contradictions = self._get_claude_enhanced_analysis(contradiction_prompt, phase_data)
        
        contradiction_file = f"{self.output_dir}/3_contradiction_matrix_{timestamp}.txt"
        with open(contradiction_file, 'w', encoding='utf-8') as f:
            f.write(f"COMPREHENSIVE CONTRADICTION MATRIX\n{'='*80}\n{contradictions}")
        reports['contradiction_matrix'] = contradiction_file
        
        # 2. Missing Documents & Gap Analysis
        gaps_prompt = """
        Identify every missing document and gap:
        1. Documents referenced but not produced
        2. Email chains with missing messages
        3. Board minutes for meetings mentioned
        4. Contracts/agreements referenced
        5. Financial records that should exist
        6. Communications during critical periods
        7. Draft versions mentioned but missing
        8. Attachments referenced but absent
        
        For each missing document:
        - What document is missing
        - Where it's referenced [DOC_XXXX]
        - Why it must exist
        - Likely content
        - Legal implications of absence
        - How to compel production
        """
        
        gaps = self._get_claude_enhanced_analysis(gaps_prompt, phase_data)
        
        gaps_file = f"{self.output_dir}/3_missing_documents_analysis_{timestamp}.txt"
        with open(gaps_file, 'w', encoding='utf-8') as f:
            f.write(f"MISSING DOCUMENTS & GAP ANALYSIS\n{'='*80}\n{gaps}")
        reports['missing_documents'] = gaps_file
        
        # 3. Communication Forensics
        comms_prompt = """
        Conduct forensic analysis of communications:
        1. Tone shifts indicating problems or guilt
        2. Sudden formality suggesting legal awareness
        3. Code words or euphemisms for illegal acts
        4. Off-the-record references
        5. Privileged communications improperly withheld
        6. Ghost-written or lawyer-edited messages
        7. Coordination patterns suggesting conspiracy
        8. Admissions hidden in routine messages
        
        Find the communications that prove wrongdoing.
        Identify the most damaging exchanges.
        """
        
        comms = self._get_claude_enhanced_analysis(comms_prompt, phase_data)
        
        comms_file = f"{self.output_dir}/3_communication_forensics_{timestamp}.txt"
        with open(comms_file, 'w', encoding='utf-8') as f:
            f.write(f"COMMUNICATION FORENSICS REPORT\n{'='*80}\n{comms}")
        reports['communication_forensics'] = comms_file
        
        print(f"  ✓ Generated 3 Phase 3 reports")
        return reports
    
    # ==================== PHASE 4 REPORTS ====================
    
    def generate_phase_4_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 4: Narrative Construction & Destruction
        Strategy: Build winning story, destroy theirs
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 4 reports with Claude enhancement...")
        
        # 1. Winning Narrative Construction
        winning_prompt = """
        Construct Lismore's winning narrative:
        1. Simple, compelling story of betrayal and wrongdoing
        2. Clear heroes (Lismore) and villains (Process Holdings)
        3. Emotional hooks for judge/jury
        4. Every claim supported by documents [DOC_XXXX]
        5. Addresses and destroys all defences
        6. Creates moral outrage at Process Holdings
        7. Makes verdict inevitable
        8. Supports maximum damages
        
        Structure as:
        - Opening hook
        - Act 1: The promise/agreement
        - Act 2: The betrayal
        - Act 3: The cover-up
        - Conclusion: Justice demanded
        """
        
        winning = self._get_claude_enhanced_analysis(winning_prompt, phase_data)
        
        winning_file = f"{self.output_dir}/4_winning_narrative_{timestamp}.txt"
        with open(winning_file, 'w', encoding='utf-8') as f:
            f.write(f"LISMORE'S WINNING NARRATIVE\n{'='*80}\n{winning}")
        reports['winning_narrative'] = winning_file
        
        # 2. Opposition Narrative Destruction
        destruction_prompt = """
        Systematically destroy Process Holdings' narrative:
        1. List every claim they make
        2. Disprove each with documentary evidence
        3. Show evolution of their lies
        4. Expose their bad faith
        5. Reveal their true motives (greed, fraud)
        6. Demonstrate consciousness of guilt
        7. Prove cover-up attempts
        8. Make their lawyers doubt them
        
        For each element of their story:
        - Their claim
        - Why it's false
        - Proof it's false [DOC_XXXX]
        - Real truth
        - How to expose in court
        """
        
        destruction = self._get_claude_enhanced_analysis(destruction_prompt, phase_data)
        
        destruction_file = f"{self.output_dir}/4_narrative_destruction_{timestamp}.txt"
        with open(destruction_file, 'w', encoding='utf-8') as f:
            f.write(f"PROCESS HOLDINGS NARRATIVE DESTRUCTION\n{'='*80}\n{destruction}")
        reports['narrative_destruction'] = destruction_file
        
        print(f"  ✓ Generated 2 Phase 4 reports")
        return reports
    
    # ==================== PHASE 5 REPORTS ====================
    
    def generate_phase_5_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 5: Legal Arsenal & Evidence Packages
        Strategy: Package evidence for maximum legal impact
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 5 reports with Claude enhancement...")
        
        # 1. Decisive Evidence Packages
        evidence_prompt = """
        Create decisive evidence packages:
        1. FRAUD PACKAGE - All evidence of deception
        2. DAMAGES PACKAGE - All financial harm evidence
        3. BAD FAITH PACKAGE - All evidence of malice
        4. COVER-UP PACKAGE - All obstruction evidence
        5. ADMISSION PACKAGE - All damaging admissions
        6. CONSPIRACY PACKAGE - All coordination evidence
        7. BREACH PACKAGE - All contract violations
        8. CREDIBILITY PACKAGE - All lies and contradictions
        
        For each package:
        - List documents in order of impact
        - Explain how they connect
        - Rate strength (1-10)
        - Suggest deployment strategy
        """
        
        evidence = self._get_claude_enhanced_analysis(evidence_prompt, phase_data)
        
        evidence_file = f"{self.output_dir}/5_evidence_packages_{timestamp}.txt"
        with open(evidence_file, 'w', encoding='utf-8') as f:
            f.write(f"DECISIVE EVIDENCE PACKAGES\n{'='*80}\n{evidence}")
        reports['evidence_packages'] = evidence_file
        
        # 2. Admission Compilation
        admissions_prompt = """
        Compile all admissions for maximum impact:
        1. Direct admissions of wrongdoing
        2. Admissions against interest
        3. Judicial admissions (binding)
        4. Admissions by conduct
        5. Admissions by silence
        6. Implicit admissions
        7. Qualified admissions we can expand
        8. Admissions in informal communications
        
        For each admission:
        - Quote exactly
        - Document reference [DOC_XXXX]
        - Legal effect
        - How to use in court
        - Questions to lock it down
        """
        
        admissions = self._get_claude_enhanced_analysis(admissions_prompt, phase_data)
        
        admissions_file = f"{self.output_dir}/5_admissions_compilation_{timestamp}.txt"
        with open(admissions_file, 'w', encoding='utf-8') as f:
            f.write(f"COMPREHENSIVE ADMISSIONS COMPILATION\n{'='*80}\n{admissions}")
        reports['admissions_compilation'] = admissions_file
        
        # 3. Criminal Referral Assessment
        criminal_prompt = """
        Assess criminal referral opportunities:
        1. FRAUD - Evidence of intentional deception
        2. CONSPIRACY - Evidence of coordinated wrongdoing
        3. MONEY LAUNDERING - Suspicious financial flows
        4. BRIBERY/CORRUPTION - Improper payments
        5. OBSTRUCTION - Document destruction/spoliation
        6. PERJURY - False statements under oath
        7. FORGERY - Altered or fake documents
        8. RACKETEERING - Pattern of criminal activity
        
        For each potential crime:
        - Elements proven
        - Evidence available
        - Prosecution likelihood
        - Settlement leverage created
        - How to threaten credibly
        """
        
        criminal = self._get_claude_enhanced_analysis(criminal_prompt, phase_data)
        
        criminal_file = f"{self.output_dir}/5_criminal_referral_assessment_{timestamp}.txt"
        with open(criminal_file, 'w', encoding='utf-8') as f:
            f.write(f"CRIMINAL REFERRAL ASSESSMENT\n{'='*80}\n{criminal}")
        reports['criminal_assessment'] = criminal_file
        
        print(f"  ✓ Generated 3 Phase 5 reports")
        return reports
    
    # ==================== PHASE 6 REPORTS ====================
    
    def generate_phase_6_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 6: Endgame Strategy
        Strategy: Orchestrate maximum pressure for victory
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 6 reports with Claude enhancement...")
        
        # 1. Cross-Examination Roadmap
        cross_exam_prompt = """
        Design devastating cross-examination strategy:
        1. Key witnesses to destroy
        2. Prior inconsistent statements to use
        3. Documents to ambush with
        4. Admissions to extract
        5. Credibility attacks
        6. Trap questions
        7. Visual aids to use
        8. Emotional moments to create
        
        For each witness:
        - Name and role
        - Vulnerabilities
        - Key documents to use
        - Questions in sequence
        - Expected admissions
        - Backup if they lie
        """
        
        cross_exam = self._get_claude_enhanced_analysis(cross_exam_prompt, phase_data)
        
        cross_exam_file = f"{self.output_dir}/6_cross_examination_roadmap_{timestamp}.txt"
        with open(cross_exam_file, 'w', encoding='utf-8') as f:
            f.write(f"CROSS-EXAMINATION ROADMAP\n{'='*80}\n{cross_exam}")
        reports['cross_examination'] = cross_exam_file
        
        # 2. Settlement Leverage Strategy
        settlement_prompt = """
        Create maximum settlement leverage:
        1. Rank evidence by settlement pressure
        2. Criminal referral threats
        3. Regulatory complaint threats
        4. Reputational destruction threats
        5. Personal liability threats
        6. Insurance coverage threats
        7. Third party claim threats
        8. Public disclosure threats
        
        Design escalation timeline:
        - Week 1: Deploy X
        - Week 2: Escalate to Y
        - Week 3: Nuclear option Z
        
        Price each threat removal.
        """
        
        settlement = self._get_claude_enhanced_analysis(settlement_prompt, phase_data)
        
        settlement_file = f"{self.output_dir}/6_settlement_leverage_strategy_{timestamp}.txt"
        with open(settlement_file, 'w', encoding='utf-8') as f:
            f.write(f"SETTLEMENT LEVERAGE MAXIMISATION\n{'='*80}\n{settlement}")
        reports['settlement_leverage'] = settlement_file
        
        # 3. Summary Judgment Roadmap
        summary_prompt = """
        Build summary judgment strategy:
        1. Claims with no genuine dispute
        2. Admissions eliminating fact issues
        3. Documents proving claims conclusively
        4. Legal arguments requiring no trial
        5. Defences that fail as matter of law
        6. Sanctions supporting judgment
        7. Procedural defaults
        8. Partial summary judgment options
        
        Show the court that trial is unnecessary.
        We've already won.
        """
        
        summary = self._get_claude_enhanced_analysis(summary_prompt, phase_data)
        
        summary_file = f"{self.output_dir}/6_summary_judgment_roadmap_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"SUMMARY JUDGMENT ROADMAP\n{'='*80}\n{summary}")
        reports['summary_judgment'] = summary_file
        
        print(f"  ✓ Generated 3 Phase 6 reports")
        return reports
    
    # ==================== PHASE 7 REPORTS ====================
    
    def generate_phase_7_reports(self, phase_data: Dict) -> Dict[str, str]:
        """
        Generate Phase 7: Autonomous Deep Intelligence
        Strategy: Unconstrained AI analysis for breakthrough insights
        """
        reports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("  Generating Phase 7 reports with unconstrained Claude analysis...")
        
        # 1. Pattern Recognition Beyond Human Capability
        patterns_prompt = """
        Use full AI pattern recognition to find:
        1. Linguistic fingerprints revealing deception
        2. Statistical anomalies in financial data
        3. Behavioural patterns indicating guilt
        4. Network analysis revealing hidden connections
        5. Temporal correlations humans would miss
        6. Document creation patterns showing fabrication
        7. Communication patterns revealing conspiracy
        8. Metadata patterns exposing tampering
        
        Find patterns no human would spot.
        Explain their significance.
        """
        
        patterns = self._get_claude_enhanced_analysis(patterns_prompt, phase_data)
        
        patterns_file = f"{self.output_dir}/7_ai_pattern_recognition_{timestamp}.txt"
        with open(patterns_file, 'w', encoding='utf-8') as f:
            f.write(f"AI PATTERN RECOGNITION ANALYSIS\n{'='*80}\n{patterns}")
        reports['ai_patterns'] = patterns_file
        
        # 2. Novel Legal Theory Development
        novel_prompt = """
        Develop creative legal theories:
        1. Untested but viable legal arguments
        2. Creative statutory interpretations
        3. Novel damages theories
        4. Innovative precedent combinations
        5. Policy arguments for new remedies
        6. Equitable doctrines to invoke
        7. International law applications
        8. Constitutional arguments
        
        Think outside conventional legal frameworks.
        Find arguments that could reshape the law.
        """
        
        novel = self._get_claude_enhanced_analysis(novel_prompt, phase_data)
        
        novel_file = f"{self.output_dir}/7_novel_legal_theories_{timestamp}.txt"
        with open(novel_file, 'w', encoding='utf-8') as f:
            f.write(f"NOVEL LEGAL THEORIES\n{'='*80}\n{novel}")
        reports['novel_theories'] = novel_file
        
        # 3. Hidden Connection Discovery
        hidden_prompt = """
        Discover hidden connections:
        1. Undisclosed relationships between parties
        2. Secret financial interests
        3. Hidden control structures
        4. Concealed conflicts of interest
        5. Covert coordination patterns
        6. Disguised common ownership
        7. Hidden beneficiaries
        8. Undisclosed side agreements
        
        Connect dots others wouldn't see.
        Reveal the hidden truth.
        """
        
        hidden = self._get_claude_enhanced_analysis(hidden_prompt, phase_data)
        
        hidden_file = f"{self.output_dir}/7_hidden_connections_{timestamp}.txt"
        with open(hidden_file, 'w', encoding='utf-8') as f:
            f.write(f"HIDDEN CONNECTION DISCOVERY\n{'='*80}\n{hidden}")
        reports['hidden_connections'] = hidden_file
        
        # 4. Nuclear Options & Game-Changers
        nuclear_prompt = """
        Identify nuclear options and game-changers:
        1. Evidence that ends the case immediately
        2. Revelations that trigger criminal prosecution
        3. Discoveries that void their insurance
        4. Findings that pierce corporate veils
        5. Evidence triggering treble damages
        6. Discoveries enabling asset freezing
        7. Revelations destroying all credibility
        8. Smoking guns we haven't recognised
        
        Find the game-changers.
        Identify the nuclear options.
        Show how to deploy for maximum impact.
        """
        
        nuclear = self._get_claude_enhanced_analysis(nuclear_prompt, phase_data)
        
        nuclear_file = f"{self.output_dir}/7_nuclear_options_{timestamp}.txt"
        with open(nuclear_file, 'w', encoding='utf-8') as f:
            f.write(f"NUCLEAR OPTIONS & GAME-CHANGERS\n{'='*80}\n{nuclear}")
        reports['nuclear_options'] = nuclear_file
        
        print(f"  ✓ Generated 4 Phase 7 reports")
        return reports
    
    # ==================== MASTER SUMMARY ====================
    
    def generate_master_war_room_summary(self, all_reports: Dict, knowledge: Dict):
        """Generate executive war room summary"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"{self.output_dir}/MASTER_WAR_ROOM_SUMMARY_{timestamp}.txt"
        
        # Count total reports
        total_reports = sum(len(reports) for reports in all_reports.values())
        
        # Build summary
        summary_content = f"""
{'='*80}
MASTER WAR ROOM SUMMARY - LISMORE v PROCESS HOLDINGS
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Reports Generated: {total_reports}
Phases Completed: {', '.join(knowledge.keys())}

EXECUTIVE SUMMARY:
{'-'*80}
This comprehensive litigation intelligence analysis has processed {len(self.document_registry)} documents
across {len(knowledge)} analytical phases, generating {total_reports} strategic reports.

KEY FINDINGS:
{'-'*80}
"""
        
        # Add phase summaries
        for phase in sorted(knowledge.keys()):
            phase_desc = {
                '0A': 'Legal Framework Weaponisation',
                '0B': 'Case Context Intelligence',
                '1': 'Document Landscape Mapping',
                '2': 'Chronological Analysis',
                '3': 'Contradiction & Gap Detection',
                '4': 'Narrative Construction',
                '5': 'Evidence Packaging',
                '6': 'Endgame Strategy',
                '7': 'AI Deep Intelligence'
            }.get(phase, f'Phase {phase}')
            
            summary_content += f"\nPHASE {phase} - {phase_desc}:\n"
            
            if phase in all_reports:
                for report_name in all_reports[phase].keys():
                    summary_content += f"  ✓ {report_name.replace('_', ' ').title()}\n"
            else:
                summary_content += f"  → Knowledge retained for analysis foundation\n"
        
        summary_content += f"""

STRATEGIC ADVANTAGES GAINED:
{'-'*80}
1. Complete documentary evidence mapped and prioritised
2. All contradictions and impossibilities identified
3. Comprehensive timeline with all conflicts exposed
4. Missing documents catalogued with production demands ready
5. Criminal referral options assessed and ready
6. Settlement leverage points identified and priced
7. Trial strategy complete with cross-examination roadmap
8. Novel legal theories developed for maximum impact

RECOMMENDED IMMEDIATE ACTIONS:
{'-'*80}
1. Deploy Phase 5 evidence packages in initial disclosures
2. File document production demands for missing items (Phase 3)
3. Prepare criminal referral threats for settlement leverage
4. Schedule depositions targeting Phase 1 key actors
5. Draft summary judgment motion using Phase 6 roadmap

LITIGATION READINESS: COMPLETE
{'-'*80}
All analytical phases complete. Lismore equipped with comprehensive
intelligence to destroy Process Holdings through litigation or force
maximum settlement.

War room ready for deployment.

{'='*80}
END MASTER SUMMARY
{'='*80}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"\n✓ Generated MASTER WAR ROOM SUMMARY")
        return summary_file