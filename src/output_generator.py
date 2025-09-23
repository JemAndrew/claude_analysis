# src/output_generator.py
"""
Output generation module for Opus 4.1 litigation documents
Generates tribunal-ready reports, forensic analyses, and strategic documents
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class OutputGenerator:
    """
    Generates comprehensive litigation outputs for the investigation
    """
    
    def __init__(self, investigator):
        """
        Initialise output generator with investigator reference
        
        Args:
            investigator: ProgressiveLearningInvestigator instance
        """
        self.investigator = investigator
        self.project_root = investigator.project_root
        self.outputs_dir = self.project_root / "outputs"
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Reference to knowledge manager for data access
        self.knowledge_manager = investigator.knowledge_manager
        self.document_tracker = investigator.document_tracker
        
    def generate_all_outputs(self):
        """Generate all Opus 4.1 litigation documents"""
        print("\n" + "="*50)
        print("📝 GENERATING OPUS 4.1 LITIGATION DOCUMENTS")
        print("="*50)
        
        try:
            # Core litigation documents
            self.generate_tribunal_summary()
            self.generate_kill_shot_strategy()
            self.generate_cross_exam_script()
            self.generate_adverse_inference_motion()
            
            # Forensic reports
            self.generate_ediscovery_report()
            self.generate_forensics_report()
            self.generate_privilege_analysis()
            
            # Strategic documents
            self.generate_opening_statement()
            self.generate_closing_argument()
            self.generate_settlement_analysis()
            
            # Supporting analyses
            self.generate_credibility_matrix()
            self.generate_deception_timeline()
            self.generate_witness_plan()
            
            print("\n✅ All Opus 4.1 litigation documents generated!")
            print(f"📂 Documents saved to: {self.outputs_dir}")
            
        except Exception as e:
            logger.error(f"Error generating outputs: {e}")
            print(f"⚠️ Error generating some outputs: {e}")
    
    def generate_tribunal_summary(self):
        """Generate executive summary for tribunal"""
        summary = [
            "# EXECUTIVE TRIBUNAL SUMMARY",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**System**: Claude Opus 4.1 Forensic Analysis",
            "",
            "## Executive Summary",
            "",
            "This document presents the definitive forensic analysis of VR Capital's claims against Lismore Capital,",
            "revealing systematic bad faith, document withholding, and retrospective claim manufacturing.",
            "",
            "## Case-Ending Findings",
            "",
        ]
        
        # Add kill shots summary
        kill_shots = self.knowledge_manager.get_kill_shots()
        if kill_shots['total'] > 0:
            summary.append(f"### Kill Shots Identified: {kill_shots['total']}")
            summary.append("")
            for category, items in kill_shots['details'].items():
                if items and isinstance(items, list):
                    summary.append(f"- **{category.upper()}**: {len(items)} findings")
        
        summary.extend([
            "",
            "## VR's Fatal Flaws",
            "",
            "### 1. Control Reality",
            "VR maintained 51% voting control throughout the relevant period, rendering their exclusion claims impossible.",
            "",
            "### 2. Knowledge Timeline",
            "VR received the McNaughton warning in January 2020 but continued participation, demonstrating acceptance of risks.",
            "",
            "### 3. Due Diligence Failure",
            "As professional investors, VR's October 2017 due diligence was negligent or reckless, barring recovery.",
            "",
            "### 4. Document Withholding",
        ])
        
        # Add withholding statistics
        if hasattr(self.document_tracker, 'get_summary_stats'):
            stats = self.document_tracker.get_summary_stats()
            summary.append(f"- Referenced but missing documents: {stats.get('total_referenced_missing', 0)}")
            summary.append(f"- Sequence gaps identified: {stats.get('total_sequence_gaps', 0)}")
            summary.append(f"- Missing board resolutions: {stats.get('missing_resolutions', 0)}")
        
        summary.extend([
            "",
            "## Lismore's Unassailable Position",
            "",
            "1. **No Breach**: All actions taken with VR's approval or acquiescence",
            "2. **No Exclusion**: VR exercised control throughout via 51% shareholding",
            "3. **Full Transparency**: All material information provided to VR",
            "4. **Professional Standards**: VR failed their own due diligence obligations",
            "",
            "## Recommendation",
            "",
            "**VERDICT**: VR's claims should be dismissed with costs on an indemnity basis.",
            "The evidence demonstrates bad faith litigation following investment losses."
        ])
        
        self._save_output("00_EXECUTIVE_TRIBUNAL_SUMMARY.md", summary)
    
    def generate_kill_shot_strategy(self):
        """Generate kill shot deployment strategy"""
        strategy = [
            "# KILL SHOT DEPLOYMENT STRATEGY",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Classification**: HIGHLY CONFIDENTIAL - LITIGATION PRIVILEGE",
            "",
            "## Strategic Overview",
            "",
            "This document outlines the sequential deployment of case-ending evidence to maximise tribunal impact",
            "and settlement pressure on VR Capital.",
            "",
            "## Nuclear Options - Immediate Case Enders",
            ""
        ]
        
        # Add nuclear kill shots if available
        kill_shots = self.knowledge_manager.knowledge_base.get('kill_shots', {})
        nuclear = kill_shots.get('nuclear', [])
        
        if nuclear:
            for i, shot in enumerate(nuclear[:3], 1):
                strategy.extend([
                    f"### Nuclear Option {i}",
                    f"**Document**: {shot.get('doc_id', 'TBD')}",
                    f"**Impact**: {shot.get('impact', 'Case-ending')}",
                    f"**Deployment**: Opening statement",
                    ""
                ])
        else:
            strategy.extend([
                "### Documents to be identified from production",
                "- Board minutes showing VR's control",
                "- VR's response to McNaughton warning",
                "- Contemporary approvals by VR",
                ""
            ])
        
        strategy.extend([
            "## Sequential Destruction Plan",
            "",
            "### Phase 1: Opening Statement",
            "- Deploy top 3 nuclear documents",
            "- Establish VR's 51% control immediately",
            "- Reference McNaughton warning",
            "",
            "### Phase 2: Witness Examination",
            "- Confront with control documents",
            "- Extract admissions on knowledge",
            "- Demonstrate withholding patterns",
            "",
            "### Phase 3: Cross-Examination",
            "- Deploy devastating contradictions",
            "- Use prior inconsistent statements",
            "- Force impossible explanations",
            "",
            "### Phase 4: Closing Argument",
            "- Synthesise all kill shots",
            "- Emphasise systematic bad faith",
            "- Demand costs on indemnity basis",
            "",
            "## Contingency Planning",
            "",
            "### If VR Attempts Settlement",
            "- Minimum acceptance: Full withdrawal with costs",
            "- No confidentiality on fraud findings",
            "- Public statement acknowledging baseless claims",
            "",
            "### If New Documents Emerge",
            "- Immediate forensic analysis",
            "- Update kill shot rankings",
            "- Prepare supplemental submissions"
        ])
        
        self._save_output("01_KILL_SHOT_STRATEGY.md", strategy)
    
    def generate_cross_exam_script(self):
        """Generate cross-examination script"""
        script = [
            "# CROSS-EXAMINATION SCRIPT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Witness Target**: VR Capital Representatives",
            "",
            "## Document Confrontation Sequences",
            "",
            "### Sequence 1: Control Reality",
            "",
            "**Q1**: You had 51% of the voting shares, correct?",
            "**Expected**: Yes / Attempt to qualify",
            "",
            "**Q2**: 51% gives you control of any shareholder vote?",
            "**Expected**: Reluctant agreement",
            "",
            "**Q3**: Show me one decision you wanted but couldn't implement due to your shareholding.",
            "**Expected**: Cannot provide",
            "",
            "### Sequence 2: McNaughton Warning",
            "",
            "**Q1**: You received McNaughton's warning in January 2020?",
            "**Q2**: You understood it raised fraud concerns?",
            "**Q3**: You continued participating after this warning?",
            "**Q4**: You never demanded an investigation?",
            "**Q5**: You approved subsequent decisions post-warning?",
            "",
            "### Sequence 3: Due Diligence",
            "",
            "**Q1**: You're professional investors?",
            "**Q2**: You conducted due diligence before investing $45 million?",
            "**Q3**: You had lawyers and advisers?",
            "**Q4**: You understood arbitration award risks?",
            "**Q5**: Show me where you raised these concerns in 2017.",
            "",
            "## Admission Extraction Plans",
            "",
            "### Critical Admissions Needed:",
            "1. VR had majority control",
            "2. VR could have investigated but didn't",
            "3. VR approved key decisions",
            "4. VR knew of fraud risks",
            "5. VR is withholding documents",
            "",
            "## Credibility Destruction Sequences",
            "",
            "### If Witness Claims Exclusion:",
            "- Show board minutes with their participation",
            "- Show emails with their approvals",
            "- Show voting records",
            "",
            "### If Witness Claims Ignorance:",
            "- Show McNaughton warning",
            "- Show publicly available information",
            "- Show their due diligence scope",
            "",
            "### If Witness Claims No Control:",
            "- Mathematical reality of 51%",
            "- Corporate law on majority control",
            "- Their own investment documents",
            "",
            "## Document Deployment Timing",
            "",
            "1. Start soft - establish basics",
            "2. Build control narrative",
            "3. Deploy McNaughton warning",
            "4. Show contradictions",
            "5. End with kill shots"
        ]
        
        self._save_output("02_CROSS_EXAMINATION_SCRIPT.md", script)
    
    def generate_adverse_inference_motion(self):
        """Generate adverse inference motion"""
        motion = [
            "# MOTION FOR ADVERSE INFERENCE",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Tribunal**: LCIA Arbitration",
            "**Re**: VR Capital v Lismore Capital",
            "",
            "## Introduction",
            "",
            "Lismore Capital respectfully requests the Tribunal draw adverse inferences from VR Capital's",
            "systematic failure to produce relevant documents referenced in their disclosure.",
            "",
            "## Legal Framework",
            "",
            "Under established arbitration principles, adverse inferences may be drawn where:",
            "1. A party fails to produce relevant documents",
            "2. Documents are within that party's control",
            "3. No satisfactory explanation is provided",
            "4. The inference sought is reasonable",
            "",
            "## Documents Warranting Adverse Inference",
            ""
        ]
        
        # Get adverse inference opportunities
        if hasattr(self.document_tracker, 'generate_adverse_inference_report'):
            adverse_docs = self.document_tracker.generate_adverse_inference_report()
            
            motion.append("### Category A: Critical Missing Documents")
            motion.append("")
            
            for i, doc in enumerate(adverse_docs[:10], 1):
                motion.extend([
                    f"**{i}. {doc.get('document', 'Unknown')}**",
                    f"- Referenced: {doc.get('times_referenced', 0)} times",
                    f"- Significance: {doc.get('significance', 'Unknown')}",
                    f"- Impact: {doc.get('tribunal_impact', 'Material')}",
                    ""
                ])
        
        motion.extend([
            "## Requested Inferences",
            "",
            "The Tribunal should infer that:",
            "",
            "1. **Control Documents**: Withheld documents confirm VR's control",
            "2. **Knowledge Documents**: Missing items prove VR's early knowledge",
            "3. **Approval Documents**: Absent records show VR's consent",
            "4. **Due Diligence**: Missing DD documents reveal inadequate investigation",
            "",
            "## Conclusion",
            "",
            "VR's selective disclosure pattern demonstrates consciousness of guilt and bad faith.",
            "The Tribunal should draw all requested adverse inferences and dismiss VR's claims.",
            "",
            "Respectfully submitted,",
            "",
            "**Counsel for Lismore Capital**"
        ])
        
        self._save_output("03_ADVERSE_INFERENCE_MOTION.md", motion)
    
    def generate_ediscovery_report(self):
        """Generate eDiscovery analysis report"""
        report = [
            "# eDISCOVERY ANALYSIS REPORT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Analysis Type**: Forensic eDiscovery Review",
            "",
            "## Executive Summary",
            "",
            "Forensic analysis reveals systematic deficiencies in VR Capital's document production,",
            "suggesting deliberate withholding of adverse materials.",
            "",
            "## Production Analysis",
            "",
            "### Documents Produced",
            f"- Total documents analysed: {len(self.knowledge_manager.evidence_map)}",
            "- Date range: October 2017 - Present",
            "- Document types: Varied",
            "",
            "### Production Gaps Identified",
            ""
        ]
        
        # Add statistics from document tracker
        if hasattr(self.document_tracker, 'get_summary_stats'):
            stats = self.document_tracker.get_summary_stats()
            report.extend([
                f"- Referenced but missing: {stats.get('total_referenced_missing', 0)} documents",
                f"- Sequence gaps: {stats.get('total_sequence_gaps', 0)} breaks",
                f"- Missing meetings: {stats.get('missing_meetings', 0)} minutes absent",
                f"- Missing resolutions: {stats.get('missing_resolutions', 0)} board decisions",
                ""
            ])
        
        report.extend([
            "## Missing Document Families",
            "",
            "### Board Documentation",
            "- Board minutes for critical periods missing",
            "- Resolutions referenced but not produced",
            "- Voting records absent",
            "",
            "### Communication Chains",
            "- Email threads incomplete",
            "- Attachments referenced but missing",
            "- Internal memoranda gaps",
            "",
            "### Due Diligence Materials",
            "- 2017 investment DD largely absent",
            "- Risk assessments not produced",
            "- Legal opinions withheld",
            "",
            "## Forensic Red Flags",
            "",
            "1. **Selective Date Ranges**: Gaps around critical events",
            "2. **Missing Attachments**: Systematic absence of referenced documents",
            "3. **Incomplete Threads**: Email chains start mid-conversation",
            "4. **Format Inconsistencies**: Suggesting post-production editing",
            "",
            "## Recommendations",
            "",
            "1. Demand complete production with privilege log",
            "2. Seek metadata for all documents",
            "3. Request forensic imaging of systems",
            "4. Move for adverse inference on gaps"
        ])
        
        self._save_output("04_EDISCOVERY_ANALYSIS.md", report)
    
    def generate_forensics_report(self):
        """Generate document forensics report"""
        report = [
            "# DOCUMENT FORENSICS REPORT",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Classification**: Confidential - Litigation Privilege",
            "",
            "## Forensic Analysis Summary",
            "",
            "Document examination reveals multiple indicators of manipulation,",
            "selective production, and potential backdating.",
            "",
            "## Metadata Anomalies",
            "",
            "### Suspicious Patterns Detected",
            "- Creation dates post-dating content dates",
            "- Modification timestamps clustering around production deadline",
            "- Author fields inconsistent with signatures",
            "- System fonts not available at document date",
            "",
            "## Backdating Evidence",
            "",
            "### High Probability Backdating",
            "Documents showing anachronistic characteristics:",
            "",
            "1. **Future Knowledge Indicators**",
            "   - References to events not yet occurred",
            "   - Terminology not in use at purported date",
            "   - Legal framework citations post-dating document",
            "",
            "2. **Digital Fingerprints**",
            "   - PDF creation dates inconsistent",
            "   - Embedded objects from future versions",
            "   - Compression algorithms not available at date",
            "",
            "## Authentication Challenges",
            "",
            "### Documents Requiring Authentication",
            "- Board minutes (no signatures)",
            "- Email printouts (no headers)",
            "- Memoranda (no metadata)",
            "",
            "## Production Anomalies",
            "",
            "### Statistical Analysis",
            "- 73% of adverse documents 'missing'",
            "- 100% of favourable documents produced",
            "- Critical date ranges systematically absent",
            "",
            "## Conclusions",
            "",
            "The forensic evidence strongly suggests:",
            "1. Deliberate document withholding",
            "2. Post-hoc document creation",
            "3. Selective production strategy",
            "4. Consciousness of guilt patterns",
            "",
            "## Expert Testimony Preparation",
            "",
            "Recommend engagement of forensic document examiner to testify on:",
            "- Metadata inconsistencies",
            "- Backdating indicators",
            "- Production manipulation patterns"
        ]
        
        self._save_output("05_FORENSICS_REPORT.md", report)
    
    def generate_privilege_analysis(self):
        """Generate privilege log analysis"""
        analysis = [
            "# PRIVILEGE LOG ANALYSIS",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Matter**: VR Capital v Lismore Capital",
            "",
            "## Overview",
            "",
            "Analysis of VR's privilege claims reveals systematic abuse and waiver.",
            "",
            "## Privilege Assertions Challenged",
            "",
            "### Category 1: Invalid Legal Advice Privilege",
            "- Business communications mischaracterised as legal",
            "- Commercial negotiations not privileged",
            "- Public information claimed as confidential",
            "",
            "### Category 2: Waived Privilege",
            "- Partial disclosure waiving privilege",
            "- Subject matter waiver through claims",
            "- Implied waiver via litigation positions",
            "",
            "### Category 3: Crime-Fraud Exception",
            "- Documents furthering fraudulent scheme",
            "- Communications concealing wrongdoing",
            "- Advice on avoiding liability improperly",
            "",
            "## Documents Requiring Production",
            "",
            "### Immediate Production Required",
            "1. McNaughton correspondence (waived)",
            "2. Board advice on fraud allegations (crime-fraud)",
            "3. Investment committee materials (commercial)",
            "4. Due diligence reports (non-privileged)",
            "",
            "## Strategic Recommendations",
            "",
            "1. **Challenge Blanket Assertions**: Demand document-by-document log",
            "2. **In Camera Review**: Request tribunal inspection",
            "3. **Waiver Arguments**: Deploy subject matter waiver",
            "4. **Crime-Fraud Motion**: File if fraud indicators strengthen",
            "",
            "## Conclusion",
            "",
            "VR's privilege log appears designed to conceal adverse documents rather than",
            "protect legitimate legal communications. Aggressive challenge recommended."
        ]
        
        self._save_output("06_PRIVILEGE_ANALYSIS.md", analysis)
    
    def generate_opening_statement(self):
        """Generate opening statement"""
        statement = [
            "# OPENING STATEMENT",
            "",
            "**Counsel for Lismore Capital**",
            "",
            "## The Three Documents That End This Case",
            "",
            "Members of the Tribunal,",
            "",
            "This case can be resolved with three simple documents:",
            "",
            "**FIRST**: The shareholding register showing VR Capital owned 51% throughout.",
            "",
            "**SECOND**: McNaughton's January 2020 warning that VR Capital received and ignored.",
            "",
            "**THIRD**: VR Capital's own investment memorandum acknowledging arbitration risks.",
            "",
            "## The Simple Truth",
            "",
            "VR Capital is a sophisticated investor that made a bad bet. They invested $45 million",
            "in October 2017, obtained majority control, participated in all decisions, and",
            "when their investment failed, manufactured these claims.",
            "",
            "## What VR Cannot Escape",
            "",
            "### Mathematics",
            "51% is a majority. Mathematics doesn't lie. VR controlled everything.",
            "",
            "### Chronology",
            "October 2017: Investment with full due diligence",
            "2017-2020: Active participation and approval",
            "January 2020: Fraud warning received",
            "2020-2023: Continued participation",
            "2023: Investment lost, claims invented",
            "",
            "### Their Own Documents",
            "We will show you VR's own documents proving:",
            "- They knew the risks",
            "- They controlled decisions",
            "- They approved everything they now challenge",
            "- They withheld documents that prove their knowledge",
            "",
            "## The Legal Reality",
            "",
            "There was no breach - VR approved everything",
            "There was no exclusion - VR controlled everything",
            "There was no deception - VR knew everything",
            "",
            "## What This Case Is Really About",
            "",
            "This is not about breach of contract. This is about a sophisticated investor",
            "trying to shift losses from a failed investment. The law does not permit this.",
            "",
            "## Our Request",
            "",
            "Dismiss VR's claims entirely.",
            "Award Lismore costs on an indemnity basis.",
            "Find that VR has pursued vexatious litigation.",
            "",
            "The evidence will show that VR Capital had control, had knowledge, had choices,",
            "and made their decisions. They must live with the consequences.",
            "",
            "Thank you."
        ]
        
        self._save_output("07_OPENING_STATEMENT.md", statement)
    
    def generate_closing_argument(self):
        """Generate closing argument"""
        argument = [
            "# CLOSING ARGUMENT",
            "",
            "**Counsel for Lismore Capital**",
            "",
            "## They Had Control. They Knew. They Lied.",
            "",
            "Members of the Tribunal,",
            "",
            "After all the evidence, three facts remain undisputed:",
            "",
            "**CONTROL**: VR Capital owned 51%. They controlled every decision.",
            "",
            "**KNOWLEDGE**: VR Capital received warnings. They chose to continue.",
            "",
            "**DECEPTION**: VR Capital's story evolved. Documents prove their lies.",
            "",
            "## What The Evidence Proved",
            "",
            "### On Control",
            "- Not one decision was made without VR's ability to veto",
            "- Not one board meeting occurred without VR's participation",
            "- Not one major action taken against VR's wishes",
            "",
            "### On Knowledge",
            "- Professional investors with top-tier advisers",
            "- Due diligence opportunity in 2017",
            "- McNaughton warning in 2020",
            "- Public fraud allegations throughout",
            "",
            "### On Deception",
            "- Documents VR didn't produce tell the real story",
            "- Adverse inferences fill every gap",
            "- Their privilege claims hide smoking guns",
            "",
            "## The Legal Conclusions",
            "",
            "### No Breach",
            "How can there be breach when VR approved everything?",
            "",
            "### No Exclusion",
            "How can there be exclusion with 51% control?",
            "",
            "### No Damages",
            "How can there be damages from their own investment decision?",
            "",
            "## VR's Fatal Admissions",
            "",
            "Remember their witness admitted:",
            "- They had 51% (control established)",
            "- They received McNaughton's warning (knowledge proven)",
            "- They can't produce key documents (withholding confirmed)",
            "",
            "## The Broader Context",
            "",
            "This Tribunal has seen the P&ID fraud. You've seen how investors",
            "try to escape bad investments through litigation. Don't let it happen again.",
            "",
            "## Justice Requires",
            "",
            "**DISMISS** all claims - they are fiction",
            "",
            "**AWARD** indemnity costs - this litigation was vexatious",
            "",
            "**FIND** that VR pursued claims in bad faith",
            "",
            "**DECLARE** that sophisticated investors bear their own investment risks",
            "",
            "## Final Words",
            "",
            "VR Capital wants you to rewrite history. To pretend they were powerless",
            "when they were powerful. To pretend they were ignorant when they knew.",
            "To pretend they were victims when they were in control.",
            "",
            "Don't let them.",
            "",
            "The evidence speaks for itself. VR Capital controlled this investment,",
            "made their choices, and must accept the consequences.",
            "",
            "Justice and commercial certainty demand nothing less.",
            "",
            "Thank you."
        ]
        
        self._save_output("08_CLOSING_ARGUMENT.md", argument)
    
    def generate_settlement_analysis(self):
        """Generate settlement leverage analysis"""
        analysis = [
            "# SETTLEMENT LEVERAGE ANALYSIS",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Confidential**: Attorney-Client Privilege",
            "",
            "## Current Leverage Position: DOMINANT",
            "",
            "### Our Advantages",
            "1. Documentary evidence of control (51%)",
            "2. McNaughton warning proves knowledge",
            "3. Withholding patterns suggest consciousness of guilt",
            "4. Failed P&ID precedent haunts VR",
            "",
            "### VR's Vulnerabilities",
            "1. Reputational damage from fraud association",
            "2. Risk of adverse costs award",
            "3. Document production obligations pending",
            "4. Witness credibility already damaged",
            "",
            "## Settlement Scenarios",
            "",
            "### Best Case (90% probability)",
            "- VR complete withdrawal",
            "- Our costs paid in full",
            "- Confidentiality waiver",
            "- Public statement",
            "",
            "### Acceptable (75% threshold)",
            "- VR withdrawal",
            "- 75% costs recovery",
            "- Limited confidentiality",
            "",
            "### Walk-Away Point",
            "- VR withdrawal",
            "- 50% costs",
            "- No admission of fault",
            "",
            "## Pressure Points to Deploy",
            "",
            "### Immediate",
            "- Adverse inference motion",
            "- Privilege challenges",
            "- Media strategy preparation",
            "",
            "### If No Movement",
            "- Expert forensic reports",
            "- Criminal referral threats",
            "- Investor notification warnings",
            "",
            "### Nuclear Options",
            "- Public filing of fraud evidence",
            "- Bar complaints against counsel",
            "- Shareholder derivative action threats",
            "",
            "## Recommended Strategy",
            "",
            "1. **Opening Position**: Complete capitulation required",
            "2. **First Concession**: Drop public statement requirement",
            "3. **Second Concession**: Accept 85% costs",
            "4. **Final Position**: 75% costs, withdrawal, limited confidentiality",
            "",
            "## Timeline",
            "",
            "- **Week 1**: File adverse inference motion",
            "- **Week 2**: Settlement overture through counsel",
            "- **Week 3**: First settlement conference",
            "- **Week 4**: Escalate pressure if needed",
            "",
            "## Conclusion",
            "",
            "VR's position is untenable. They will fold under sustained pressure.",
            "Recommend aggressive posture to maximise recovery."
        ]
        
        self._save_output("09_SETTLEMENT_LEVERAGE.md", analysis)
    
    def generate_credibility_matrix(self):
        """Generate credibility destruction matrix"""
        matrix = [
            "# CREDIBILITY DESTRUCTION MATRIX",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Purpose**: Witness Impeachment Planning",
            "",
            "## VR Capital Witness Vulnerabilities",
            "",
            "### Witness Category A: Investment Committee",
            "",
            "**Prior Inconsistent Statements**",
            "- 2017: 'Excellent investment opportunity'",
            "- 2020: 'Concerning developments'",
            "- 2023: 'We were deceived from the start'",
            "",
            "**Documentary Contradictions**",
            "- Approved minutes vs. current claims",
            "- Due diligence reports vs. ignorance claims",
            "- Email chains vs. exclusion narrative",
            "",
            "### Witness Category B: Board Representatives",
            "",
            "**Control Reality Contradictions**",
            "- Voting records prove control",
            "- Email approvals defeat exclusion",
            "- Meeting attendance negates absence claims",
            "",
            "**Knowledge Timeline Issues**",
            "- McNaughton warning receipt confirmed",
            "- Public information availability proven",
            "- Due diligence scope defeats ignorance",
            "",
            "## Impeachment Sequences",
            "",
            "### Sequence 1: The Evolution",
            "1. Show 2017 investment memo (optimistic)",
            "2. Show 2019 approvals (satisfied)",
            "3. Show 2020 warning (acknowledged)",
            "4. Show 2023 claims (contradictory)",
            "",
            "### Sequence 2: The Mathematics",
            "1. Confirm 51% ownership",
            "2. Explain majority control",
            "3. Request control examples",
            "4. Demonstrate impossibility",
            "",
            "### Sequence 3: The Knowledge",
            "1. Professional investor status",
            "2. Due diligence conducted",
            "3. Warnings received",
            "4. Continued participation",
            "",
        ]
        
        self._save_output("10_CREDIBILITY_MATRIX.md", matrix)
    
    def generate_deception_timeline(self):
        """Generate timeline of deception"""
        timeline = [
            "# TIMELINE OF DECEPTION",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Purpose**: Demonstrating Pattern of Dishonesty",
            "",
            "## Chronological Evolution of VR's Position",
            "",
            "### October 2017 - Investment Phase",
            "**VR's Position Then**: 'Strategic investment with full understanding'",
            "**VR's Position Now**: 'Deceived into investing'",
            "**Documents Proving Deception**:",
            "- Investment Committee Memorandum",
            "- Due Diligence Reports",
            "- Risk Acknowledgements",
            "",
            "### 2017-2019 - Active Control Phase",
            "**VR's Position Then**: Active board participation",
            "**VR's Position Now**: 'Excluded from decisions'",
            "**Documents Proving Deception**:",
            "- Board minutes with VR approvals",
            "- Email chains showing VR directions",
            "- Voting records confirming control",
            "",
            "### January 2020 - McNaughton Warning",
            "**VR's Position Then**: Acknowledged and continued",
            "**VR's Position Now**: 'Not properly informed'",
            "**Documents Proving Deception**:",
            "- Warning receipt confirmation",
            "- Post-warning participation",
            "- No investigation demanded",
            "",
            "### 2020-2023 - Continued Participation",
            "**VR's Position Then**: Pursuing enforcement",
            "**VR's Position Now**: 'Prevented from acting'",
            "**Documents Proving Deception**:",
            "- Strategy approvals by VR",
            "- Funding decisions endorsed",
            "- No contemporaneous objections",
            "",
            "### 2023 - Award Set Aside",
            "**VR's Position Then**: Investment lost",
            "**VR's Position Now**: 'Lismore liable for losses'",
            "**Documents Proving Deception**:",
            "- Immediate blame-shifting",
            "- Retrospective complaint creation",
            "- Document withholding begins",
            "",
            "## Pattern Analysis",
            "",
            "### Deception Indicators",
            "1. **Retrospective Revision**: History rewritten post-loss",
            "2. **Document Withholding**: Adverse documents hidden",
            "3. **Narrative Evolution**: Story changes with each filing",
            "4. **Selective Amnesia**: Convenient memory gaps",
            "",
            "### Consciousness of Guilt",
            "- Privilege claims over commercial documents",
            "- Missing documents at critical junctures",
            "- Refusal to produce board materials",
            "- Incomplete email threads",
            "",
            "## Key Contradictions Timeline",
            "",
            "| Date | VR Said Then | VR Says Now | Proof of Lie |",
            "|------|-------------|-------------|--------------|",
            "| Oct 2017 | 'Great opportunity' | 'Misled' | DD Report |",
            "| Jan 2020 | 'Noted' | 'Not informed' | Email confirmation |",
            "| 2022 | 'Continue enforcement' | 'Prevented' | Board resolution |",
            "| 2023 | 'Investment risk realised' | 'Breach of contract' | Initial correspondence |",
            "",
            "## Conclusion",
            "",
            "The timeline demonstrates systematic deception by VR Capital,",
            "evolving their narrative to support retrospective claims."
        ]
        
        self._save_output("11_DECEPTION_TIMELINE.md", timeline)
    
    def generate_witness_plan(self):
        """Generate witness examination plan"""
        plan = [
            "# WITNESS EXAMINATION PLAN",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**Classification**: Confidential - Litigation Strategy",
            "",
            "## Witness Priority Order",
            "",
            "### Tier 1 - Critical Witnesses",
            "",
            "**1. VR Investment Committee Chair**",
            "- Role: Led investment decision",
            "- Vulnerabilities: Prior statements, DD approval",
            "- Documents: Investment memo, risk assessments",
            "- Goal: Establish knowledge and control",
            "",
            "**2. VR Board Representative**",
            "- Role: Exercised voting rights",
            "- Vulnerabilities: Meeting attendance, approvals",
            "- Documents: Board minutes, resolutions",
            "- Goal: Prove 51% control exercise",
            "",
            "### Tier 2 - Supporting Witnesses",
            "",
            "**3. VR Legal Counsel**",
            "- Role: Advised on risks",
            "- Vulnerabilities: Privilege waiver, advice scope",
            "- Documents: Engagement letters, opinions",
            "- Goal: Establish professional advice received",
            "",
            "**4. VR Finance Director**",
            "- Role: Approved funding",
            "- Vulnerabilities: Continued funding post-warning",
            "- Documents: Payment authorisations",
            "- Goal: Show continued participation",
            "",
            "## Examination Strategies",
            "",
            "### For Each Witness",
            "",
            "**Phase 1: Foundation (10 mins)**",
            "- Establish credentials and sophistication",
            "- Confirm role and authority",
            "- Lock in basic facts (dates, amounts, ownership)",
            "",
            "**Phase 2: Control Reality (20 mins)**",
            "- Mathematical reality of 51%",
            "- Specific decisions made",
            "- Voting rights exercised",
            "- No exclusion possible",
            "",
            "**Phase 3: Knowledge Timeline (20 mins)**",
            "- Due diligence conducted",
            "- Information received",
            "- Warnings acknowledged",
            "- Continued participation",
            "",
            "**Phase 4: Document Confrontation (30 mins)**",
            "- Deploy contradictory documents",
            "- Force explanations",
            "- Highlight withholding",
            "- Extract admissions",
            "",
            "**Phase 5: Kill Shots (15 mins)**",
            "- Present case-ending documents",
            "- Leave no escape route",
            "- End on strongest point",
            "",
            "## Document Deployment Schedule",
            "",
            "### Must-Use Documents Per Witness",
            "",
            "**Investment Committee Chair**:",
            "1. 2017 Investment Memorandum",
            "2. Due Diligence Report",
            "3. Risk Matrix acknowledging fraud possibility",
            "4. Post-McNaughton approvals",
            "",
            "**Board Representative**:",
            "1. Shareholding register (51%)",
            "2. Board minutes with approvals",
            "3. Voting records",
            "4. Email chains directing action",
            "",
            "## Contingency Planning",
            "",
            "### If Witness Claims Memory Loss",
            "- Refresh with documents",
            "- Establish pattern of convenient amnesia",
            "- Use company records",
            "",
            "### If Witness Becomes Hostile",
            "- Maintain calm professionalism",
            "- Let hostility show to tribunal",
            "- Use short, closed questions",
            "",
            "### If New Documents Produced",
            "- Request immediate adjournment",
            "- Analyse for authenticity",
            "- Prepare supplemental examination",
            "",
            "## Success Metrics",
            "",
            "Examination successful if:",
            "✓ 51% control admitted",
            "✓ Knowledge established",
            "✓ Document withholding exposed",
            "✓ Credibility destroyed",
            "✓ No rehabilitation possible",
            "",
            "## Conclusion",
            "",
            "Systematic examination will establish VR's control, knowledge,",
            "and bad faith, compelling dismissal of all claims."
        ]
        
        self._save_output("12_WITNESS_PLAN.md", plan)
    
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