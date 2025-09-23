# src/phases.py
"""
Guided Autonomous Phase Executor
Follows 6-phase structure but adds discoveries and self-learning
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

# Import guided autonomous prompts
import autonomous_prompts as prompts

logger = logging.getLogger(__name__)


class PhaseExecutor:
    """
    6-phase structured investigation with autonomous discovery additions
    """
    
    def __init__(self, investigator):
        self.investigator = investigator
        self.api_client = investigator.api_client
        self.knowledge_base = investigator.knowledge_base
        self.document_tracker = investigator.document_tracker
        self.project_root = investigator.project_root
        self.config = investigator.config
        
        # Phase findings - both required and discovered
        self.phase_findings = {}
        self.unexpected_discoveries = {}
        self.claude_additions = {}
        
        # Core mandate
        self.core_mandate = prompts.get_core_mandate()
    
    async def run_all_phases(self, documents: List[Dict]) -> Dict:
        """
        Execute 6-phase investigation with guided autonomy
        """
        print("\n" + "="*70)
        print(" Investigation Proceeding")
        print(" Structured Analysis + Claude's Additions")
        print("="*70)
        
        # PHASE 0: Legal Learning (Structured + Autonomous)
        print("\n" + "-"*50)
        print(" PHASE 0: Legal Expertise Building")
        await self.phase_0_legal_learning()
        
        # PHASE 1: Document Landscape (Required + Discoveries)
        print("\n" + "-"*50)
        print(" PHASE 1: Document Landscape Analysis")
        await self.phase_1_landscape(documents)
        
        # PHASE 2: Pattern Recognition (Structured + Discovered)
        print("\n" + "-"*50)
        print(" PHASE 2: Pattern Recognition")
        await self.phase_2_patterns(documents)
        
        # PHASE 3: Anomaly Detection (Required + Found)
        print("\n" + "-"*50)
        print(" PHASE 3: Anomaly Detection")
        await self.phase_3_anomalies(documents)
        
        # PHASE 4: Theory Building (Standard + Creative)
        print("\n" + "-"*50)
        print(" PHASE 4: Theory Construction")
        await self.phase_4_theories(documents)
        
        # PHASE 5: Evidence Analysis (Required + Unexpected)
        print("\n" + "-"*50)
        print(" PHASE 5: Evidence Preparation")
        await self.phase_5_evidence(documents)
        
        # PHASE 6: Kill Shots (Standard + Discovered)
        print("\n" + "-"*50)
        print(" PHASE 6: Kill Shot Identification")
        await self.phase_6_kill_shots(documents)
        
        # Final Synthesis
        await self.final_synthesis()
        
        return self.phase_findings
    
    async def phase_0_legal_learning(self):
        """Phase 0: Structured legal training with autonomous additions"""
        
        # Get framework prompt
        framework_prompt = prompts.get_phase_0_learning_framework()
        full_prompt = f"{self.core_mandate}\n\n{framework_prompt}"
        
        # Execute learning
        response = await self.api_client.make_api_call(
            full_prompt,
            phase='phase_0',
            temperature=0.4
        )
        
        # Store findings
        self.phase_findings['phase_0'] = response
        self.knowledge_base['legal_expertise'] = {
            'core_training': response,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check for unexpected discoveries
        await self._process_unexpected_discoveries(response, 0)
        
        print("✅ Legal expertise built (required + additional)")

    async def phase_0b_case_context(self):
        """
        Phase 0B: Analyse case context PDFs as Lismore's counsel
        """
        context_dir = self.project_root / "case_context"
        
        print("🎯 Analysing case context documents for Lismore...")
        
        # Process PDFs in case_context folder
        case_documents = []
        
        if context_dir.exists():
            # Use document_processor to handle PDFs
            from document_processor import DocumentProcessor
            
            processor = DocumentProcessor(self.project_root)
            
            # Find all PDFs in case_context
            for file in context_dir.glob("**/*.pdf"):
                try:
                    # Process the PDF
                    doc_id = processor._generate_doc_id(file)
                    processed_doc = processor._process_pdf(file, doc_id)
                    
                    case_documents.append({
                        'doc_id': doc_id,
                        'filename': file.name,
                        'text': processed_doc.text_content[:5000],  # First 5000 chars
                        'extraction_quality': processed_doc.extraction_quality
                    })
                    
                    print(f"  ✓ Processed: {file.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")
        
        print(f"📄 Processed {len(case_documents)} case context documents")
        
        # Get framework prompt with case documents
        framework = prompts.get_phase_0b_case_context_framework(
            len(case_documents)
        )
        
        # Format documents for analysis
        formatted_docs = "\n\n".join([
            f"[Document: {doc['filename']}]\n{doc['text']}"
            for doc in case_documents[:10]  # First 10 docs
        ])
        
        full_prompt = f"""
        {self.core_mandate}
        
        {framework}
        
        CASE DOCUMENTS TO ANALYSE:
        {formatted_docs}
        
        Extract:
        1. Key facts about the dispute
        2. Critical dates and timeline
        3. VR's vulnerabilities
        4. Lismore's advantages
        5. Evidence priorities
        """
        
        # Send to Claude for analysis
        response = await self.api_client.make_api_call(
            full_prompt,
            phase='phase_0b',
            temperature=0.3
        )
        
        # Store case understanding
        self.knowledge_base['case_context'] = {
            'documents_analysed': len(case_documents),
            'strategic_analysis': response,
            'key_documents': [doc['filename'] for doc in case_documents],
            'timestamp': datetime.now().isoformat()
        }
        
        self.phase_findings['phase_0b'] = response
        print("✅ Case context mastery achieved")
    
    async def phase_1_landscape(self, documents: List[Dict]):
        """Phase 1: Required landscape analysis + autonomous discoveries"""
        
        from utils import batch_documents, format_batch_with_metadata
        batches = batch_documents(documents, 40)
        
        all_findings = []
        
        for batch_num, batch in enumerate(batches):
            print(f"  Batch {batch_num + 1}/{len(batches)}...")
            
            # Get framework with accumulated knowledge
            framework = prompts.get_phase_1_framework(
                self._get_accumulated_knowledge()
            )
            
            full_prompt = f"""
            {self.core_mandate}
            
            {framework}
            
            Documents to analyse:
            {format_batch_with_metadata(batch)}
            
            Provide:
            1. Required analysis (all 5 categories)
            2. Your additional discoveries
            3. Unexpected patterns or findings
            """
            
            response = await self.api_client.make_api_call(
                full_prompt,
                phase='phase_1',
                temperature=0.3
            )
            
            all_findings.append(response)
            
            # Process for unexpected discoveries
            await self._process_unexpected_discoveries(response, 1)
            
            # Track withholding
            for doc in batch:
                self.document_tracker.analyse_for_withholding(
                    doc.get('text', ''),
                    doc.get('doc_id', 'unknown')
                )
        
        self.phase_findings['phase_1'] = '\n\n'.join(all_findings)
        
        # Check if we should adapt based on discoveries
        await self._check_adaptation_needed(1)
        
        print("✅ Phase 1 complete: Landscape mapped + discoveries noted")
    
    async def phase_2_patterns(self, documents: List[Dict]):
        """Phase 2: Required patterns + discovered patterns"""
        
        from utils import batch_documents, format_batch_with_metadata
        batches = batch_documents(documents, 40)
        
        all_findings = []
        
        for batch_num, batch in enumerate(batches):
            print(f"  Batch {batch_num + 1}/{len(batches)}...")
            
            # Get framework with Phase 1 findings
            framework = prompts.get_phase_2_framework(
                self.phase_findings.get('phase_1', '')
            )
            
            full_prompt = f"""
            {self.core_mandate}
            
            {framework}
            
            Documents to analyse:
            {format_batch_with_metadata(batch)}
            
            Identify:
            1. All 5 required pattern categories
            2. Any new patterns you discover
            3. Unexpected connections
            4. Patterns unique to this case
            """
            
            response = await self.api_client.make_api_call(
                full_prompt,
                phase='phase_2',
                temperature=0.4
            )
            
            all_findings.append(response)
            await self._process_unexpected_discoveries(response, 2)
        
        self.phase_findings['phase_2'] = '\n\n'.join(all_findings)
        await self._check_adaptation_needed(2)
        
        print("✅ Phase 2 complete: Patterns identified + new patterns found")
    
    async def phase_3_anomalies(self, documents: List[Dict]):
        """Phase 3: Required anomalies + discovered anomalies"""
        
        from utils import batch_documents, format_batch_with_metadata
        batches = batch_documents(documents, 40)
        
        all_findings = []
        
        for batch_num, batch in enumerate(batches):
            print(f"  Batch {batch_num + 1}/{len(batches)}...")
            
            framework = prompts.get_phase_3_framework(
                self._get_accumulated_findings()
            )
            
            full_prompt = f"""
            {self.core_mandate}
            
            {framework}
            
            Documents to analyse:
            {format_batch_with_metadata(batch)}
            
            Find:
            1. All 5 required anomaly categories
            2. Additional anomalies you discover
            3. Rate each (1-10) for impact
            4. Explain unexpected findings
            """
            
            response = await self.api_client.make_api_call(
                full_prompt,
                phase='phase_3',
                temperature=0.4
            )
            
            all_findings.append(response)
            await self._process_unexpected_discoveries(response, 3)
        
        self.phase_findings['phase_3'] = '\n\n'.join(all_findings)
        await self._check_adaptation_needed(3)
        
        print("✅ Phase 3 complete: Anomalies detected + surprises found")
    
    async def phase_4_theories(self, documents: List[Dict]):
        """Phase 4: Required theories + creative theories"""
        
        from utils import batch_documents, format_batch_with_metadata
        batches = batch_documents(documents, 40)
        
        all_findings = []
        
        for batch_num, batch in enumerate(batches):
            print(f"  Batch {batch_num + 1}/{len(batches)}...")
            
            framework = prompts.get_phase_4_framework(
                self._get_accumulated_analysis()
            )
            
            full_prompt = f"""
            {self.core_mandate}
            
            {framework}
            
            Documents to analyse:
            {format_batch_with_metadata(batch)}
            
            Develop:
            1. All 5 required theories
            2. Novel theories from discoveries
            3. Creative legal arguments
            4. Unexpected angles
            """
            
            response = await self.api_client.make_api_call(
                full_prompt,
                phase='phase_4',
                temperature=0.5
            )
            
            all_findings.append(response)
            await self._process_unexpected_discoveries(response, 4)
        
        self.phase_findings['phase_4'] = '\n\n'.join(all_findings)
        await self._check_adaptation_needed(4)
        
        print("✅ Phase 4 complete: Theories built + creative additions")
    
    async def phase_5_evidence(self, documents: List[Dict]):
        """Phase 5: Required evidence + unexpected evidence"""
        
        from utils import batch_documents, format_batch_with_metadata
        batches = batch_documents(documents, 40)
        
        all_findings = []
        
        for batch_num, batch in enumerate(batches):
            print(f"  Batch {batch_num + 1}/{len(batches)}...")
            
            framework = prompts.get_phase_5_framework(
                self._get_all_findings()
            )
            
            full_prompt = f"""
            {self.core_mandate}
            
            {framework}
            
            Documents to analyse:
            {format_batch_with_metadata(batch)}
            
            Package:
            1. All 5 required evidence categories
            2. Unexpected evidence found
            3. Creative presentations
            4. Surprising connections
            """
            
            response = await self.api_client.make_api_call(
                full_prompt,
                phase='phase_5',
                temperature=0.3
            )
            
            all_findings.append(response)
            await self._process_unexpected_discoveries(response, 5)
        
        self.phase_findings['phase_5'] = '\n\n'.join(all_findings)
        await self._check_adaptation_needed(5)
        
        print("✅ Phase 5 complete: Evidence prepared + surprises packaged")
    
    async def phase_6_kill_shots(self, documents: List[Dict]):
        """Phase 6: Required kill shots + discovered kill shots"""
        
        from utils import batch_documents, format_batch_with_metadata
        batches = batch_documents(documents, 40)
        
        all_findings = []
        
        for batch_num, batch in enumerate(batches):
            print(f"  Batch {batch_num + 1}/{len(batches)}...")
            
            framework = prompts.get_phase_6_framework(
                self._get_complete_investigation()
            )
            
            full_prompt = f"""
            {self.core_mandate}
            
            {framework}
            
            Documents to analyse:
            {format_batch_with_metadata(batch)}
            
            Identify:
            1. All 5 kill shot categories
            2. Unexpected kill shots
            3. Unique combinations
            4. Rank all by impact
            """
            
            response = await self.api_client.make_api_call(
                full_prompt,
                phase='phase_6',
                temperature=0.2
            )
            
            all_findings.append(response)
            await self._process_unexpected_discoveries(response, 6)
        
        self.phase_findings['phase_6'] = '\n\n'.join(all_findings)
        
        print("✅ Phase 6 complete: Kill shots identified + surprises found")
    
    async def final_synthesis(self):
        """Synthesise structured findings + autonomous discoveries"""
        
        print("\n" + "="*50)
        print("📊 FINAL SYNTHESIS")
        print("="*50)
        
        # Get synthesis framework
        synthesis_framework = prompts.get_synthesis_framework(
            json.dumps(self.phase_findings, indent=2)[:3000],
            json.dumps(self.unexpected_discoveries, indent=2)[:1500]
        )
        
        full_prompt = f"""
        {self.core_mandate}
        
        {synthesis_framework}
        
        Additional discoveries and insights:
        {json.dumps(self.claude_additions, indent=2)[:1000]}
        
        Withholding analysis:
        {self.document_tracker.generate_adverse_inference_report()[:1000]}
        
        Create comprehensive strategy showing:
        1. Required findings
        2. Unexpected discoveries
        3. How discoveries strengthen the case
        4. Novel advantages found
        """
        
        final_strategy = await self.api_client.make_api_call(
            full_prompt,
            phase='synthesis',
            temperature=0.2
        )
        
        # Save strategy
        output_file = self.project_root / "outputs" / "00_LISMORE_STRUCTURED_PLUS_DISCOVERIES.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# LISMORE vs VR - STRUCTURED INVESTIGATION WITH DISCOVERIES\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("## STRUCTURED FINDINGS\n")
            f.write("(Required 6-phase analysis)\n\n")
            f.write("## AUTONOMOUS DISCOVERIES\n")
            f.write("(Claude's additional findings)\n\n")
            f.write("="*80 + "\n\n")
            f.write(final_strategy)
        
        self.knowledge_base['final_strategy'] = final_strategy
        self.investigator._save_knowledge_base()
        
        print(f"✅ Strategy saved: {output_file}")
        print(f"📊 Unexpected discoveries: {len(self.unexpected_discoveries)}")
        print(f"💡 Claude additions: {len(self.claude_additions)}")
    
    async def _process_unexpected_discoveries(self, findings: str, phase_num: int):
        """Process and store unexpected discoveries"""
        
        discovery_prompt = prompts.get_discovery_prompt(phase_num, findings)
        
        analysis = await self.api_client.make_api_call(
            discovery_prompt,
            phase=f'discovery_analysis_{phase_num}',
            temperature=0.3
        )
        
        if f'phase_{phase_num}' not in self.unexpected_discoveries:
            self.unexpected_discoveries[f'phase_{phase_num}'] = []
        
        self.unexpected_discoveries[f'phase_{phase_num}'].append(analysis)
    
    async def _check_adaptation_needed(self, phase_num: int):
        """Check if investigation should adapt based on discoveries"""
        
        if f'phase_{phase_num}' in self.unexpected_discoveries:
            unexpected = '\n'.join(self.unexpected_discoveries[f'phase_{phase_num}'])
            
            adaptation_prompt = prompts.get_adaptation_prompt(phase_num, unexpected)
            
            adaptation = await self.api_client.make_api_call(
                adaptation_prompt,
                phase=f'adaptation_{phase_num}',
                temperature=0.4
            )
            
            self.claude_additions[f'phase_{phase_num}_adaptation'] = adaptation
    
    def _get_accumulated_knowledge(self) -> str:
        """Get accumulated knowledge for context"""
        knowledge = {
            'legal_expertise': self.knowledge_base.get('legal_expertise', {}),
            'phase_0': self.phase_findings.get('phase_0', '')[:500]
        }
        return json.dumps(knowledge, indent=2)
    
    def _get_accumulated_findings(self) -> str:
        """Get findings from phases 1-2"""
        findings = {
            'phase_1': self.phase_findings.get('phase_1', '')[:500],
            'phase_2': self.phase_findings.get('phase_2', '')[:500]
        }
        return json.dumps(findings, indent=2)
    
    def _get_accumulated_analysis(self) -> str:
        """Get analysis from phases 1-3"""
        analysis = {
            'phase_1': self.phase_findings.get('phase_1', '')[:400],
            'phase_2': self.phase_findings.get('phase_2', '')[:400],
            'phase_3': self.phase_findings.get('phase_3', '')[:400]
        }
        return json.dumps(analysis, indent=2)
    
    def _get_all_findings(self) -> str:
        """Get all findings from phases 1-4"""
        findings = {}
        for i in range(1, 5):
            phase_key = f'phase_{i}'
            if phase_key in self.phase_findings:
                findings[phase_key] = self.phase_findings[phase_key][:300]
        return json.dumps(findings, indent=2)
    
    def _get_complete_investigation(self) -> str:
        """Get complete investigation for phase 6"""
        complete = {}
        for i in range(1, 6):
            phase_key = f'phase_{i}'
            if phase_key in self.phase_findings:
                complete[phase_key] = self.phase_findings[phase_key][:250]
        return json.dumps(complete, indent=2)