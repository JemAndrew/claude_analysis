# src/output_generator.py
"""
Enhanced output generation module for Opus 4.1 litigation documents
Generates tribunal-ready reports informed by all 6 phases of investigation
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class OutputGenerator:
    """
    Generates comprehensive litigation outputs informed by investigation findings
    """
    
    def __init__(self, investigator):
        """
        Initialise output generator with investigator reference
        
        Args:
            investigator: ProgressiveLearningInvestigator instance
        """
        self.investigator = investigator
        self.api_client = investigator.api_client  # Add API access
        self.project_root = investigator.project_root
        self.outputs_dir = self.project_root / "outputs"
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Reference to knowledge manager for data access
        self.knowledge_base = investigator.knowledge_base
        self.document_tracker = investigator.document_tracker
        
        # Storage for gathered findings
        self.all_findings = {}
        
    async def generate_all_outputs(self):
        """Generate all Opus 4.1 litigation documents with AI assistance"""
        print("\n" + "="*50)
        print("📝 GENERATING OPUS 4.1 LITIGATION DOCUMENTS")
        print("="*50)
        
        try:
            # First, gather all findings from the 6 phases
            print("📊 Gathering investigation findings...")
            self.all_findings = self._gather_all_phase_findings()
            
            # Core litigation documents
            print("📄 Generating tribunal summary...")
            await self.generate_tribunal_summary()
            
            print("🎯 Generating kill shot strategy...")
            await self.generate_kill_shot_strategy()
            
            print("❓ Generating cross-examination script...")
            await self.generate_cross_exam_script()
            
            print("⚖️ Generating adverse inference motion...")
            await self.generate_adverse_inference_motion()
            
            # Forensic reports
            print("🔍 Generating eDiscovery report...")
            await self.generate_ediscovery_report()
            
            print("🔬 Generating forensics report...")
            await self.generate_forensics_report()
            
            print("🔐 Generating privilege analysis...")
            await self.generate_privilege_analysis()
            
            # Strategic documents
            print("🎬 Generating opening statement...")
            await self.generate_opening_statement()
            
            print("🎭 Generating closing argument...")
            await self.generate_closing_argument()
            
            print("💰 Generating settlement analysis...")
            await self.generate_settlement_analysis()
            
            # Supporting analyses
            print("📊 Generating credibility matrix...")
            await self.generate_credibility_matrix()
            
            print("🕐 Generating deception timeline...")
            await self.generate_deception_timeline()
            
            print("👥 Generating witness plan...")
            await self.generate_witness_plan()
            
            print("\n✅ All Opus 4.1 litigation documents generated!")
            print(f"📂 Documents saved to: {self.outputs_dir}")
            
        except Exception as e:
            logger.error(f"Error generating outputs: {e}")
            print(f"⚠️ Error generating some outputs: {e}")
    
    def _gather_all_phase_findings(self) -> Dict:
        """Collect all findings from the 6 phases of investigation"""
        findings = {}
        
        # Get findings from knowledge base (through KnowledgeManager)
        for phase_num in range(1, 7):
            phase_key = f'phase_{phase_num}'
            phase_data = self.knowledge_base.get(phase_key, [])
            
            if phase_data:
                # Combine all findings for this phase
                if isinstance(phase_data, list):
                    findings[phase_key] = "\n".join([
                        item.get('findings', '') if isinstance(item, dict) else str(item)
                        for item in phase_data
                    ])
                else:
                    findings[phase_key] = str(phase_data)
        
        # Get phase findings from PhaseExecutor (this is where the actual findings are)
        if hasattr(self.investigator, 'phase_executor'):
            if hasattr(self.investigator.phase_executor, 'phase_findings'):
                for phase, content in self.investigator.phase_executor.phase_findings.items():
                    # Prioritise PhaseExecutor findings as they're the primary source
                    findings[phase] = content
        
        # Add specific findings categories from knowledge base
        findings['patterns'] = self.knowledge_base.get('patterns', {})
        findings['anomalies'] = self.knowledge_base.get('anomalies', {})
        findings['theories'] = self.knowledge_base.get('theories', {})
        findings['evidence'] = self.knowledge_base.get('evidence', {})
        findings['contradictions'] = self.knowledge_base.get('contradictions', {})
        findings['kill_shots'] = self.knowledge_base.get('kill_shots', {})
        findings['missing_docs'] = self.knowledge_base.get('missing_docs', {})
        
        return findings
    
    async def generate_tribunal_summary(self):
        """Generate executive summary informed by all 6 phases"""
        
        summary_prompt = f"""
        Based on the complete 6-phase forensic investigation of VR Capital's documents, 
        create an executive tribunal summary for the LCIA arbitration panel.
        
        PHASE 1 FINDINGS (Document Landscape & Forensics):
        {self.all_findings.get('phase_1', 'No findings')[:2000]}
        
        PHASE 2 FINDINGS (Pattern Recognition):
        {self.all_findings.get('phase_2', 'No findings')[:2000]}
        
        Control Patterns Found: {len(self.all_findings.get('patterns', {}).get('control_patterns', []))}
        Deception Indicators: {len(self.all_findings.get('patterns', {}).get('deception_indicators', []))}
        
        PHASE 3 FINDINGS (Anomalies):
        {self.all_findings.get('phase_3', 'No findings')[:2000]}
        
        PHASE 4 FINDINGS (Legal Theories):
        {self.all_findings.get('phase_4', 'No findings')[:2000]}
        
        PHASE 5 FINDINGS (Evidence Analysis):
        {self.all_findings.get('phase_5', 'No findings')[:2000]}
        
        PHASE 6 FINDINGS (Kill Shots):
        {self.all_findings.get('phase_6', 'No findings')[:2000]}
        
        Nuclear Kill Shots: {len(self.all_findings.get('kill_shots', {}).get('nuclear', []))}
        Devastating Evidence: {len(self.all_findings.get('kill_shots', {}).get('devastating', []))}
        
        CREATE AN EXECUTIVE TRIBUNAL SUMMARY THAT:
        1. Opens with the three most case-ending findings
        2. Lists specific document IDs that prove VR's 51% control
        3. Highlights patterns showing VR's consciousness of guilt
        4. Identifies timeline impossibilities and contradictions
        5. Summarises evidence of document withholding
        6. Provides clear recommendations for tribunal
        
        Structure as:
        - EXECUTIVE SUMMARY (2 paragraphs)
        - CASE-ENDING FINDINGS (top 3 with document IDs)
        - VR'S FATAL FLAWS (based on patterns found)
        - LISMORE'S UNASSAILABLE POSITION (from evidence analysis)
        - ADVERSE INFERENCE OPPORTUNITIES (missing documents)
        - RECOMMENDATION TO TRIBUNAL
        
        Be specific. Use actual document IDs. Reference real findings.
        This is for senior arbitrators - be precise and devastating.
        """
        
        response = await self.api_client.make_api_call(
            summary_prompt, 
            phase='output_summary',
            temperature=0.3  # Lower temperature for factual summary
        )
        
        # Format and save
        output = [
            "# EXECUTIVE TRIBUNAL SUMMARY",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**System**: Claude Opus 4.1 Forensic Analysis",
            "**Investigation**: 6-Phase Progressive Learning Complete",
            "",
            response
        ]
        
        self._save_output("00_EXECUTIVE_TRIBUNAL_SUMMARY.md", output)
    
    async def generate_kill_shot_strategy(self):
        """Generate strategy based on actual kill shots found"""
        
        kill_shots = self.all_findings.get('kill_shots', {})
        phase_6_findings = self.all_findings.get('phase_6', '')
        
        strategy_prompt = f"""
        Create a detailed deployment strategy for the kill shots identified in our investigation.
        
        ACTUAL KILL SHOTS FOUND:
        Nuclear (Case-Ending): {json.dumps(kill_shots.get('nuclear', []), indent=2)[:2000]}
        Devastating (Claim-Destroying): {json.dumps(kill_shots.get('devastating', []), indent=2)[:2000]}
        Severe (Credibility-Destroying): {json.dumps(kill_shots.get('severe', []), indent=2)[:2000]}
        
        PHASE 6 KILL SHOT ANALYSIS:
        {phase_6_findings[:3000]}
        
        CREATE A DEPLOYMENT STRATEGY THAT INCLUDES:
        
        1. OPENING STATEMENT DEPLOYMENT
           - Which 3 documents to lead with
           - Exact phrasing for maximum impact
           - Visual presentation approach
        
        2. WITNESS EXAMINATION SEQUENCE
           - Order of document presentation
           - Specific questions for each kill shot
           - Trap sequences using contradictions
        
        3. CROSS-EXAMINATION AMBUSHES
           - When to deploy each kill shot
           - How to prevent escape routes
           - Follow-up questions for denials
        
        4. CLOSING ARGUMENT CRESCENDO
           - How to sequence for maximum impact
           - Connecting kill shots to legal theories
           - Final devastating summary
        
        5. SETTLEMENT LEVERAGE
           - Which kill shots to preview in negotiations
           - How to demonstrate strength without revealing all
        
        Be specific about document IDs, timing, and sequences.
        This strategy must be actionable and devastating.
        """
        
        response = await self.api_client.make_api_call(
            strategy_prompt,
            phase='kill_shot_strategy',
            temperature=0.4
        )
        
        output = [
            "# KILL SHOT DEPLOYMENT STRATEGY",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Classification**: HIGHLY CONFIDENTIAL - LITIGATION PRIVILEGE",
            "",
            response
        ]
        
        self._save_output("01_KILL_SHOT_STRATEGY.md", output)
    
    async def generate_cross_exam_script(self):
        """Generate script based on patterns and contradictions found"""
        
        patterns = self.all_findings.get('patterns', {})
        contradictions = self.all_findings.get('contradictions', {})
        phase_2_findings = self.all_findings.get('phase_2', '')
        anomalies = self.all_findings.get('anomalies', {})
        
        cross_exam_prompt = f"""
        Create a detailed cross-examination script based on our investigation findings.
        
        PATTERNS DISCOVERED (Phase 2):
        Control Patterns: {json.dumps(patterns.get('control_patterns', []), indent=2)[:1500]}
        Deception Patterns: {json.dumps(patterns.get('deception_indicators', []), indent=2)[:1500]}
        
        CONTRADICTIONS FOUND (Phase 5):
        {json.dumps(contradictions, indent=2)[:1500]}
        
        ANOMALIES DETECTED (Phase 3):
        {json.dumps(anomalies, indent=2)[:1500]}
        
        Pattern Analysis:
        {phase_2_findings[:2000]}
        
        CREATE A CROSS-EXAMINATION SCRIPT WITH:
        
        1. CONTROL REALITY SEQUENCE
           - Questions proving VR's 51% control
           - Documents to present in order
           - Anticipated denials and follow-ups
        
        2. KNOWLEDGE TIMELINE SEQUENCE
           - Questions about McNaughton warning
           - When VR knew about fraud indicators
           - Documents proving knowledge
        
        3. CONTRADICTION CONFRONTATIONS
           - Prior inconsistent statements
           - Document vs testimony conflicts
           - Impossible explanations to force
        
        4. PATTERN DEMONSTRATIONS
           - Questions revealing deception patterns
           - Document sequences showing consciousness of guilt
           - Withholding pattern exposure
        
        5. CREDIBILITY DESTRUCTION
           - Final sequence of devastating questions
           - Documents that cannot be explained
           - Admissions to extract
        
        Format as actual Q&A sequences with specific document references.
        Include exact questions, expected answers, and follow-ups.
        Make it impossible for witnesses to escape.
        """
        
        response = await self.api_client.make_api_call(
            cross_exam_prompt,
            phase='cross_examination',
            temperature=0.3
        )
        
        output = [
            "# CROSS-EXAMINATION SCRIPT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Target Witnesses**: VR Capital Representatives",
            "",
            response
        ]
        
        self._save_output("02_CROSS_EXAMINATION_SCRIPT.md", output)
    
    async def generate_adverse_inference_motion(self):
        """Generate adverse inference motion based on withholding patterns"""
        
        # Get adverse inference opportunities from document tracker
        adverse_docs = []
        if hasattr(self.document_tracker, 'generate_adverse_inference_report'):
            adverse_docs = self.document_tracker.generate_adverse_inference_report()
        
        missing_docs = self.all_findings.get('missing_docs', {})
        phase_3_anomalies = self.all_findings.get('phase_3', '')
        
        motion_prompt = f"""
        Draft a formal motion for adverse inference based on VR Capital's document withholding.
        
        MISSING DOCUMENTS IDENTIFIED:
        {json.dumps(adverse_docs[:20], indent=2)[:3000]}
        
        WITHHOLDING PATTERNS FOUND:
        {json.dumps(missing_docs, indent=2)[:2000]}
        
        PRODUCTION ANOMALIES (Phase 3):
        {phase_3_anomalies[:2000]}
        
        CREATE A FORMAL MOTION THAT:
        
        1. INTRODUCTION
           - Establish legal basis for adverse inference
           - Cite relevant arbitration rules
        
        2. PATTERN OF WITHHOLDING
           - Systematic nature of missing documents
           - Statistical analysis of production gaps
           - Consciousness of guilt indicators
        
        3. SPECIFIC MISSING DOCUMENTS
           - List top 20 with times referenced
           - Explain significance of each
           - Impact on case if produced
        
        4. LEGAL ARGUMENT
           - Burden of production on VR
           - Failure to explain gaps
           - Inference requirements met
        
        5. REQUESTED INFERENCES
           - Specific inferences for each category
           - Impact on VR's claims
           - Support for Lismore's defences
        
        6. RELIEF SOUGHT
           - Adverse inferences
           - Cost consequences
           - Potential claim dismissal
        
        Draft in formal legal style for LCIA tribunal.
        Be precise about document references and legal standards.
        """
        
        response = await self.api_client.make_api_call(
            motion_prompt,
            phase='adverse_inference',
            temperature=0.2  # Very low for formal legal document
        )
        
        output = [
            "# MOTION FOR ADVERSE INFERENCE",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Tribunal**: LCIA Arbitration",
            "**Re**: VR Capital v Lismore Capital",
            "",
            response
        ]
        
        self._save_output("03_ADVERSE_INFERENCE_MOTION.md", output)
    
    async def generate_ediscovery_report(self):
        """Generate eDiscovery analysis based on production patterns"""
        
        stats = {}
        if hasattr(self.document_tracker, 'get_summary_stats'):
            stats = self.document_tracker.get_summary_stats()
        
        patterns = self.all_findings.get('patterns', {})
        phase_1_findings = self.all_findings.get('phase_1', '')
        
        report_prompt = f"""
        Create a comprehensive eDiscovery analysis report based on our document investigation.
        
        PRODUCTION STATISTICS:
        {json.dumps(stats, indent=2)}
        
        WITHHOLDING PATTERNS IDENTIFIED:
        {json.dumps(patterns.get('withholding_patterns', []), indent=2)[:2000]}
        
        DOCUMENT LANDSCAPE ANALYSIS (Phase 1):
        {phase_1_findings[:2000]}
        
        CREATE AN eDISCOVERY REPORT COVERING:
        
        1. EXECUTIVE SUMMARY
           - Key findings about VR's production
           - Systematic deficiencies identified
           - Impact on case
        
        2. PRODUCTION ANALYSIS
           - Documents produced vs referenced
           - Date range gaps
           - Document type analysis
           - Custodian coverage
        
        3. MISSING DOCUMENT FAMILIES
           - Board documentation gaps
           - Email chain incompleteness
           - Attachment analysis
           - Meeting minutes absence
        
        4. FORENSIC RED FLAGS
           - Metadata inconsistencies
           - Production timing anomalies
           - Selective disclosure patterns
           - Format irregularities
        
        5. PRIVILEGE LOG ANALYSIS
           - Questionable privilege claims
           - Waiver indicators
           - Crime-fraud possibilities
        
        6. RECOMMENDATIONS
           - Further production demands
           - Forensic examination needs
           - Deposition priorities
           - Motion practice
        
        Make this technical but accessible to arbitrators.
        Include specific examples and document IDs where available.
        """
        
        response = await self.api_client.make_api_call(
            report_prompt,
            phase='ediscovery_report',
            temperature=0.3
        )
        
        output = [
            "# eDISCOVERY ANALYSIS REPORT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Analysis Type**: Forensic eDiscovery Review",
            "",
            response
        ]
        
        self._save_output("04_EDISCOVERY_ANALYSIS.md", output)
    
    async def generate_forensics_report(self):
        """Generate document forensics report based on anomalies"""
        
        anomalies = self.all_findings.get('anomalies', {})
        phase_3_findings = self.all_findings.get('phase_3', '')
        patterns = self.all_findings.get('patterns', {})
        
        forensics_prompt = f"""
        Create a detailed document forensics report based on our anomaly detection.
        
        ANOMALIES DETECTED (Phase 3):
        {json.dumps(anomalies, indent=2)[:2500]}
        
        FORENSIC ANALYSIS:
        {phase_3_findings[:2000]}
        
        DECEPTION PATTERNS:
        {json.dumps(patterns.get('deception_indicators', []), indent=2)[:1500]}
        
        CREATE A FORENSICS REPORT INCLUDING:
        
        1. METADATA ANOMALIES
           - Creation date inconsistencies
           - Modification patterns
           - Author field irregularities
           - System timestamp conflicts
        
        2. BACKDATING EVIDENCE
           - Anachronistic references
           - Future knowledge indicators
           - Font/formatting issues
           - Digital fingerprint mismatches
        
        3. PRODUCTION MANIPULATION
           - Selective redaction patterns
           - Missing pages indicators
           - Resolution degradation
           - OCR vs native format issues
        
        4. AUTHENTICATION CHALLENGES
           - Documents lacking signatures
           - Email header absence
           - Chain of custody gaps
           - Version control issues
        
        5. BEHAVIOURAL FORENSICS
           - Consciousness of guilt language
           - Sudden formality shifts
           - Legal counsel involvement timing
           - Defensive communication patterns
        
        6. EXPERT TESTIMONY PREPARATION
           - Key findings for expert
           - Demonstrative exhibits needed
           - Cross-examination of opposing expert
           - Standards and methodology
        
        Write technically but clearly for tribunal understanding.
        Include specific document examples and forensic markers.
        """
        
        response = await self.api_client.make_api_call(
            forensics_prompt,
            phase='forensics_report',
            temperature=0.3
        )
        
        output = [
            "# DOCUMENT FORENSICS REPORT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Classification**: Confidential - Litigation Privilege",
            "",
            response
        ]
        
        self._save_output("05_FORENSICS_REPORT.md", output)
    
    async def generate_privilege_analysis(self):
        """Generate privilege log analysis"""
        
        phase_5_evidence = self.all_findings.get('phase_5', '')
        patterns = self.all_findings.get('patterns', {})
        
        privilege_prompt = f"""
        Analyse VR Capital's privilege claims based on our document review.
        
        EVIDENCE ANALYSIS (Phase 5):
        {phase_5_evidence[:2000]}
        
        WITHHOLDING PATTERNS:
        {json.dumps(patterns.get('withholding_patterns', []), indent=2)[:1500]}
        
        CREATE A PRIVILEGE ANALYSIS COVERING:
        
        1. OVERVIEW OF PRIVILEGE CLAIMS
           - Volume and categories
           - Temporal patterns
           - Custodian analysis
        
        2. INVALID PRIVILEGE ASSERTIONS
           - Business communications
           - Pre-existing documents
           - Third party communications
           - Published materials
        
        3. WAIVER ANALYSIS
           - Subject matter waiver
           - Partial disclosure
           - At-issue waiver
           - Implied waiver
        
        4. CRIME-FRAUD EXCEPTION
           - Fraudulent scheme evidence
           - Legal advice furthering fraud
           - Consciousness of guilt
           - Cover-up communications
        
        5. STRATEGIC RECOMMENDATIONS
           - Challenges to specific documents
           - In camera review requests
           - Waiver arguments
           - Motion practice
        
        Be precise about legal standards and specific documents.
        Focus on documents that would damage VR's case.
        """
        
        response = await self.api_client.make_api_call(
            privilege_prompt,
            phase='privilege_analysis',
            temperature=0.3
        )
        
        output = [
            "# PRIVILEGE LOG ANALYSIS",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Matter**: VR Capital v Lismore Capital",
            "",
            response
        ]
        
        self._save_output("06_PRIVILEGE_ANALYSIS.md", output)
    
    async def generate_opening_statement(self):
        """Generate opening statement based on strongest evidence"""
        
        kill_shots = self.all_findings.get('kill_shots', {})
        theories = self.all_findings.get('theories', {})
        phase_4_theories = self.all_findings.get('phase_4', '')
        
        opening_prompt = f"""
        Create a powerful opening statement based on our investigation findings.
        
        TOP KILL SHOTS:
        Nuclear: {json.dumps(kill_shots.get('nuclear', [])[:3], indent=2)[:1500]}
        
        LEGAL THEORIES DEVELOPED (Phase 4):
        {phase_4_theories[:1500]}
        
        CASE THEORIES:
        {json.dumps(theories, indent=2)[:1500]}
        
        CREATE AN OPENING STATEMENT THAT:
        
        1. OPENING HOOK
           - "Three documents end this case..."
           - Identify the specific documents
        
        2. THE SIMPLE TRUTH
           - VR had 51% control
           - VR knew of fraud concerns
           - VR now manufactures claims
        
        3. WHAT VR CANNOT ESCAPE
           - Mathematical reality of control
           - Documentary evidence
           - Their own communications
        
        4. THE LEGAL FRAMEWORK
           - Why each claim fails
           - Burden of proof
           - Standards to apply
        
        5. WHAT THE EVIDENCE WILL SHOW
           - Preview key documents
           - Witness admissions coming
           - Patterns of deception
        
        6. THE ONLY VERDICT
           - Dismiss all claims
           - Award costs to Lismore
           - Find bad faith
        
        Write persuasively for arbitrators.
        Use specific document references from our investigation.
        Make it impossible for VR to recover.
        """
        
        response = await self.api_client.make_api_call(
            opening_prompt,
            phase='opening_statement',
            temperature=0.4
        )
        
        output = [
            "# OPENING STATEMENT",
            "",
            "**Counsel for Lismore Capital**",
            "",
            response
        ]
        
        self._save_output("07_OPENING_STATEMENT.md", output)
    
    async def generate_closing_argument(self):
        """Generate closing argument synthesising all evidence"""
        
        all_phases_summary = {
            'phase_1': self.all_findings.get('phase_1', '')[:1000],
            'phase_2': self.all_findings.get('phase_2', '')[:1000],
            'phase_3': self.all_findings.get('phase_3', '')[:1000],
            'phase_4': self.all_findings.get('phase_4', '')[:1000],
            'phase_5': self.all_findings.get('phase_5', '')[:1000],
            'phase_6': self.all_findings.get('phase_6', '')[:1000]
        }
        
        closing_prompt = f"""
        Create a devastating closing argument using all six phases of our investigation.
        
        INVESTIGATION SUMMARY:
        Phase 1 (Documents): {all_phases_summary['phase_1']}
        Phase 2 (Patterns): {all_phases_summary['phase_2']}
        Phase 3 (Anomalies): {all_phases_summary['phase_3']}
        Phase 4 (Theories): {all_phases_summary['phase_4']}
        Phase 5 (Evidence): {all_phases_summary['phase_5']}
        Phase 6 (Kill Shots): {all_phases_summary['phase_6']}
        
        CREATE A CLOSING ARGUMENT WITH:
        
        1. THEY HAD CONTROL
           - Every document proving 51%
           - Every decision they made
           - Mathematical impossibility of exclusion
        
        2. THEY KNEW
           - McNaughton warning
           - Due diligence opportunity
           - Continued participation
        
        3. THEY LIED
           - Evolution of story
           - Document withholding
           - Consciousness of guilt
        
        4. THE LAW IS CLEAR
           - No breach possible
           - No exclusion possible
           - No damages possible
        
        5. JUSTICE DEMANDS
           - Complete dismissal
           - Indemnity costs
           - Bad faith finding
        
        Use specific findings from each phase.
        Reference actual documents by ID.
        Make this the closing that ends VR permanently.
        """
        
        response = await self.api_client.make_api_call(
            closing_prompt,
            phase='closing_argument',
            temperature=0.4
        )
        
        output = [
            "# CLOSING ARGUMENT",
            "",
            "**Counsel for Lismore Capital**",
            "",
            response
        ]
        
        self._save_output("08_CLOSING_ARGUMENT.md", output)
    
    async def generate_settlement_analysis(self):
        """Generate settlement leverage analysis"""
        
        kill_shots = self.all_findings.get('kill_shots', {})
        missing_docs = self.all_findings.get('missing_docs', {})
        theories = self.all_findings.get('theories', {})
        
        settlement_prompt = f"""
        Analyse our settlement leverage based on investigation findings.
        
        KILL SHOTS AVAILABLE:
        {json.dumps(kill_shots, indent=2)[:2000]}
        
        ADVERSE INFERENCE THREATS:
        {json.dumps(missing_docs, indent=2)[:1500]}
        
        THEORIES PROVEN:
        {json.dumps(theories, indent=2)[:1500]}
        
        CREATE A SETTLEMENT ANALYSIS INCLUDING:
        
        1. CURRENT LEVERAGE POSITION
           - Strength assessment (1-10)
           - VR's exposure analysis
           - Lismore's position
        
        2. PRESSURE POINTS
           - Reputational damage threats
           - Cost exposure
           - Criminal referral possibilities
           - Investor notifications
        
        3. NEGOTIATION STRATEGY
           - What to reveal in stages
           - What to hold back
           - Demonstration documents
           - Escalation timeline
        
        4. SETTLEMENT SCENARIOS
           - Best case (complete withdrawal)
           - Acceptable (80% costs)
           - Walk-away point
           - Non-negotiables
        
        5. TACTICAL DEPLOYMENT
           - When to show strength
           - How to force urgency
           - Using tribunal deadlines
           - Media strategy
        
        Be strategic and ruthless.
        We hold all the cards - show how to play them.
        """
        
        response = await self.api_client.make_api_call(
            settlement_prompt,
            phase='settlement_analysis',
            temperature=0.4
        )
        
        output = [
            "# SETTLEMENT LEVERAGE ANALYSIS",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Confidential**: Attorney-Client Privilege",
            "",
            response
        ]
        
        self._save_output("09_SETTLEMENT_LEVERAGE.md", output)
    
    async def generate_credibility_matrix(self):
        """Generate credibility destruction matrix"""
        
        contradictions = self.all_findings.get('contradictions', {})
        patterns = self.all_findings.get('patterns', {})
        phase_5_evidence = self.all_findings.get('phase_5', '')
        
        credibility_prompt = f"""
        Create a witness credibility destruction matrix based on our findings.
        
        CONTRADICTIONS FOUND:
        {json.dumps(contradictions, indent=2)[:2000]}
        
        DECEPTION PATTERNS:
        {json.dumps(patterns.get('deception_indicators', []), indent=2)[:1500]}
        
        EVIDENCE ANALYSIS (Phase 5):
        {phase_5_evidence[:1500]}
        
        CREATE A CREDIBILITY MATRIX COVERING:
        
        1. KEY WITNESS VULNERABILITIES
           - Prior inconsistent statements
           - Documentary contradictions
           - Evolution of testimony
           - Consciousness of guilt
        
        2. IMPEACHMENT SEQUENCES
           - Document confrontation order
           - Trap questions
           - Admission extractions
           - Credibility collapses
        
        3. CROSS-REFERENCE MATRIX
           - Witness vs witness conflicts
           - Witness vs document conflicts
           - Timeline impossibilities
           - Knowledge contradictions
        
        4. DESTRUCTION METHODOLOGY
           - Start soft, end hard
           - Build to crescendo
           - Leave no escape
           - Force admissions
        
        5. REHABILITATION PREVENTION
           - Anticipate explanations
           - Block escape routes
           - Counter-documents ready
           - Final devastation
        
        Map specific findings to specific witnesses.
        Make this actionable for cross-examination.
        """
        
        response = await self.api_client.make_api_call(
            credibility_prompt,
            phase='credibility_matrix',
            temperature=0.3
        )
        
        output = [
            "# CREDIBILITY DESTRUCTION MATRIX",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Purpose**: Witness Impeachment Planning",
            "",
            response
        ]
        
        self._save_output("10_CREDIBILITY_MATRIX.md", output)
    
    async def generate_deception_timeline(self):
        """Generate timeline of deception"""
        
        patterns = self.all_findings.get('patterns', {})
        anomalies = self.all_findings.get('anomalies', {})
        phase_2_patterns = self.all_findings.get('phase_2', '')
        
        timeline_prompt = f"""
        Create a detailed timeline of VR's deception based on pattern analysis.
        
        DECEPTION PATTERNS FOUND (Phase 2):
        {phase_2_patterns[:1500]}
        {json.dumps(patterns.get('deception_indicators', []), indent=2)[:1500]}
        
        TIMELINE ANOMALIES (Phase 3):
        {json.dumps(anomalies, indent=2)[:1500]}
        
        CREATE A DECEPTION TIMELINE SHOWING:
        
        1. OCTOBER 2017 - INVESTMENT
           - What VR claimed then
           - What documents show
           - What they claim now
        
        2. 2017-2019 - CONTROL PERIOD
           - Decisions VR made
           - Contemporary satisfaction
           - Current denials
        
        3. JANUARY 2020 - McNAUGHTON WARNING
           - What VR was told
           - How VR responded
           - What VR claims now
        
        4. 2020-2023 - CONTINUED PARTICIPATION
           - VR's actions
           - No complaints
           - Retrospective claims
        
        5. 2023-PRESENT - LITIGATION
           - Story evolution
           - Document withholding
           - Position changes
        
        For each period:
        - Quote specific documents
        - Show contradictions
        - Prove consciousness of guilt
        
        Make the pattern of deception undeniable.
        """
        
        response = await self.api_client.make_api_call(
            timeline_prompt,
            phase='deception_timeline',
            temperature=0.3
        )
        
        output = [
            "# TIMELINE OF DECEPTION",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Purpose**: Demonstrating Pattern of Dishonesty",
            "",
            response
        ]
        
        self._save_output("11_DECEPTION_TIMELINE.md", output)
    
    async def generate_witness_plan(self):
        """Generate witness examination plan"""
        
        evidence = self.all_findings.get('evidence', {})
        theories = self.all_findings.get('theories', {})
        kill_shots = self.all_findings.get('kill_shots', {})
        
        witness_prompt = f"""
        Create a comprehensive witness examination plan based on our evidence.
        
        EVIDENCE TO DEPLOY (Phase 5):
        {json.dumps(evidence, indent=2)[:2000]}
        
        THEORIES TO PROVE (Phase 4):
        {json.dumps(theories, indent=2)[:1500]}
        
        KILL SHOTS AVAILABLE:
        {json.dumps(kill_shots, indent=2)[:1500]}
        
        CREATE A WITNESS PLAN INCLUDING:
        
        1. WITNESS PRIORITY ORDER
           - Who to call first
           - Building momentum
           - Saving best for last
        
        2. VR INVESTMENT COMMITTEE
           - Documents to use
           - Admissions to get
           - Traps to set
           - Kill shots to deploy
        
        3. VR BOARD REPRESENTATIVES
           - Control evidence
           - Decision participation
           - Knowledge timeline
           - Contradiction exposure
        
        4. VR LEGAL COUNSEL
           - Privilege challenges
           - Advice timeline
           - Knowledge attribution
           - Waiver arguments
        
        5. EXAMINATION STRATEGY
           - Phase approach
           - Document deployment
           - Admission building
           - Credibility destruction
           - Kill shot timing
        
        For each witness:
        - Specific documents to use
        - Specific questions to ask
        - Specific admissions to extract
        - Specific kill shots to deploy
        
        Make this a blueprint for witness destruction.
        """
        
        response = await self.api_client.make_api_call(
            witness_prompt,
            phase='witness_plan',
            temperature=0.3
        )
        
        output = [
            "# WITNESS EXAMINATION PLAN",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Classification**: Confidential - Litigation Strategy",
            "",
            response
        ]
        
        self._save_output("12_WITNESS_PLAN.md", output)
    
    def _save_output(self, filename: str, content: List[str]):
        """
        Save output to file
        
        Args:
            filename: Name of output file
            content: List of strings to write
        """
        try:
            output_path = self.outputs_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            logger.info(f"Saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")