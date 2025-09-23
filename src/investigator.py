# src/investigator.py
"""
Core investigator class for the 6-Phase Progressive Learning System
This is the single source of truth for the ProgressiveLearningInvestigator class
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all modular components with correct names
from api_client import AnthropicAPIClient
from forensics import DocumentWithholdingTracker
from output_generator import OutputGenerator
import utils
import prompts

logger = logging.getLogger(__name__)


class ProgressiveLearningInvestigator:
    """
    6-Phase Progressive Learning System with Opus 4.1 Litigation Enhancement
    Specialised for complex commercial arbitration and fraud detection
    """
    
    def __init__(self, api_key: str, project_root: str):
        self.project_root = Path(project_root)
        
        # Initialise modular components
        self.api_client = AnthropicAPIClient(api_key)
        self.document_tracker = DocumentWithholdingTracker()
        self.output_generator = OutputGenerator(self)
        self.phase_findings = {}
        
        # Load configuration
        self.config = self._load_config()
        
        # Enhanced capabilities for Opus 4.1
        self.litigation_features = {
            'document_analysis': 'forensic',
            'ediscovery': True,
            'privilege_detection': True,
            'fraud_indicators': 'advanced',
            'cross_examination_prep': True,
            'adverse_inference': 'aggressive',
            'credibility_assessment': 'forensic',
            'pattern_recognition': 'maximum',
            'metadata_analysis': True
        }
        
        # Initialise knowledge base
        self.knowledge_base = self._initialise_knowledge_base()
        
        # Evolving prompts
        self.phase_prompts = {
            f'phase_{i}_additions': "" for i in range(1, 7)
        }
        
        # Investigation memory
        self.investigation_memory = self._initialise_investigation_memory()
        
        # Track document references
        self.evidence_map = {}
        
        # Performance tracking
        self.performance_metrics = {
            'api_calls': 0,
            'tokens_used': 0,
            'phases_completed': 0,
            'critical_findings': 0
        }
    
    def _initialise_knowledge_base(self) -> Dict:
        """Initialise the knowledge base structure"""
        return {
            'legal_training': {
                'procedures': {},
                'precedents': {},
                'analytical_methods': {},
                'professional_standards': {},
                'litigation_strategy': {},
                'ediscovery_patterns': {},
                'forensic_indicators': {}
            },
            'case_context': {
                'key_dates': {},
                'legal_principles': {},
                'successful_arguments': {},
                'failed_defences': {},
                'standards_applied': {},
                'tribunal_psychology': {},
                'precedent_strategies': {}
            },
            'terminology': {},
            'players': {},
            'document_map': {},
            'patterns': {
                'control_patterns': [],
                'knowledge_patterns': [],
                'financial_patterns': [],
                'withholding_patterns': [],
                'communication_patterns': [],
                'deception_indicators': [],
                'fraud_markers': []
            },
            'anomalies': {},
            'theories': {},
            'evidence': {},
            'contradictions': {},
            'missing_docs': {},
            'kill_shots': {
                'nuclear': [],
                'devastating': [],
                'severe': [],
                'tactical': [],
                'forensic': []
            }
        }
    
    def _initialise_investigation_memory(self) -> Dict:
        """Initialise the investigation memory structure"""
        return {
            'discoveries': [],
            'theories': [],
            'contradictions': [],
            'missing_documents': [],
            'timeline_anomalies': [],
            'behavioural_patterns': [],
            'linguistic_analysis': [],
            'money_trail': [],
            'power_dynamics': [],
            'smoking_guns': [],
            'kill_shots': [],
            'questions_for_human': [],
            'confidence_scores': {},
            'document_relationships': {},
            'key_players': {},
            'critical_dates': {},
            'vr_vulnerabilities': [],
            'lismore_advantages': [],
            'unexpected_findings': [],
            'claude_strategies': {},
            'forensic_findings': [],
            'ediscovery_insights': [],
            'litigation_strategies': [],
            'cross_examination_traps': {
                'control_admissions': [],
                'knowledge_admissions': [],
                'document_requests': [],
                'impossible_denials': [],
                'credibility_destroyers': []
            },
            'tribunal_impact_ranking': {
                'most_damaging_facts': [],
                'most_compelling_documents': [],
                'most_devastating_contradictions': [],
                'winning_narratives': []
            }
        }
    
    def _load_config(self) -> Dict:
        """Load configuration from config/settings.json"""
        config_path = self.project_root / 'config' / 'settings.json'
        if config_path.exists():
            return utils.load_json_file(config_path) or self._default_config()
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration if settings.json not found"""
        return {
            'model': {
                'temperature': {
                    'phase_1': 0.3,
                    'phase_2': 0.4,
                    'phase_3': 0.4,
                    'phase_4': 0.5,
                    'phase_5': 0.3,
                    'phase_6': 0.2
                }
            },
            'investigation': {
                'batch_size': 40,
                'max_tokens': 8192
            }
        }
    

    async def run_progressive_investigation(self):
        """Run 6-phase progressive investigation with Opus 4.1 enhancements"""
        
        print("\n" + "="*70)
        print("🧠 6-PHASE PROGRESSIVE LEARNING INVESTIGATION SYSTEM")
        print("⚡ Enhanced with Claude Opus 4.1 Litigation Capabilities")
        print("="*70)
        
        # Load documents
        documents = utils.load_documents(self.project_root)
        print(f"\n📄 Loaded {len(documents)} VR Capital documents")
        
        if not documents:
            print("⚠️ No documents found to analyse. Please add documents to documents/processed/text/")
            return
        
        # Create phase executor and run all phases
        from phases import PhaseExecutor
        self.phase_executor = PhaseExecutor(self)
        await self.phase_executor.run_all_phases(documents)
        
        # Generate outputs
        self.output_generator.generate_all_outputs()
        
        # Performance summary
        self._print_performance_summary()

    @property
    def phase_findings(self):
        """Access phase findings from PhaseExecutor"""
        if hasattr(self, 'phase_executor'):
            return self.phase_executor.phase_findings
        return {}
     
    def _build_cumulative_context(self, phase: int) -> str:
        """Build context with Opus 4.1 enhancements"""
        context = "OPUS 4.1 ACCUMULATED INTELLIGENCE:\n\n"
        
        if self.knowledge_base.get('legal_training'):
            context += "Legal Framework Mastery:\n"
            context += f"{json.dumps(self.knowledge_base['legal_training'], indent=2)[:1500]}\n\n"
        
        if self.knowledge_base.get('case_context'):
            context += "Case Intelligence:\n"
            context += f"{json.dumps(self.knowledge_base['case_context'], indent=2)[:1500]}\n\n"
        
        context += "Investigation Progress:\n"
        context += self._summarise_findings(1, phase)
        
        if phase >= 3:
            context += "\n\nForensic Findings:\n"
            forensic = self.investigation_memory.get('forensic_findings', [])[:5]
            context += f"{json.dumps(forensic, indent=2)[:1000]}"
        
        if phase >= 5:
            context += "\n\nLitigation Strategies Developed:\n"
            strategies = self.investigation_memory.get('litigation_strategies', [])[:3]
            context += f"{json.dumps(strategies, indent=2)[:1000]}"
        
        context += "\n\nApply Opus 4.1 maximum analytical capabilities."
        context += "\nThink like senior counsel in final trial preparation.\n"
        
        return context
    
    def _summarise_findings(self, start_phase: int, end_phase: int) -> str:
        """Summarise findings with litigation focus"""
        summary = ""
        
        if end_phase >= 1:
            summary += f"\nKey Players Identified: {len(self.knowledge_base.get('players', {}))}"
            summary += f"\nDocuments Analysed: {len(self.evidence_map)}"
        
        if end_phase >= 2:
            patterns = self.knowledge_base.get('patterns', {})
            summary += f"\nControl Patterns: {len(patterns.get('control_patterns', []))}"
            summary += f"\nDeception Indicators: {len(patterns.get('deception_indicators', []))}"
        
        if end_phase >= 3:
            summary += f"\nAnomalies Detected: {len(self.knowledge_base.get('anomalies', {}))}"
            summary += f"\nForensic Issues: {len(self.investigation_memory.get('forensic_findings', []))}"
        
        if end_phase >= 4:
            summary += f"\nTheories Built: {len(self.knowledge_base.get('theories', {}))}"
        
        if end_phase >= 5:
            summary += f"\nContradictions Found: {len(self.knowledge_base.get('contradictions', {}))}"
            summary += f"\nMissing Documents: {len(self.knowledge_base.get('missing_docs', {}))}"
        
        if end_phase >= 6:
            kill_shots = self.knowledge_base.get('kill_shots', {})
            summary += f"\nNuclear Kill Shots: {len(kill_shots.get('nuclear', []))}"
            summary += f"\nDevastating Evidence: {len(kill_shots.get('devastating', []))}"
        
        return summary[:2000]
    
    def _update_knowledge_base(self, phase: str, findings: str):
        """Update knowledge base with Opus 4.1 enhanced extraction"""
        
        # In production, would parse findings and extract specific information
        # For now, storing the raw findings
        if phase not in self.knowledge_base:
            self.knowledge_base[phase] = []
        
        self.knowledge_base[phase].append({
            'findings': findings[:1000],  # Store first 1000 chars as sample
            'timestamp': datetime.now().isoformat()
        })
        
        # Save to disk
        self._save_knowledge_base()
        
        # Update performance metrics
        self.performance_metrics['api_calls'] = self.api_client.api_calls
        self.performance_metrics['critical_findings'] += 1
    
    def _save_knowledge_base(self):
        """Save knowledge base with Opus 4.1 enhancements"""
        kb_file = self.project_root / "memory" / "opus_41_knowledge_base.json"
        kb_file.parent.mkdir(parents=True, exist_ok=True)
        
        utils.save_json_output(self.knowledge_base, kb_file)
    
    def get_kill_shots(self) -> Dict:
        """Get kill shots summary for output generator"""
        kill_shots = self.knowledge_base.get('kill_shots', {})
        total = sum(len(v) for v in kill_shots.values() if isinstance(v, list))
        return {'total': total, 'details': kill_shots}
    
    def _print_performance_summary(self):
        """Print Opus 4.1 performance summary"""
        print("\n" + "="*50)
        print("📊 OPUS 4.1 PERFORMANCE SUMMARY")
        print("="*50)
        print(f"API Calls Made: {self.api_client.api_calls}")
        print(f"Phases Completed: {self.performance_metrics['phases_completed']}/6")
        print(f"Documents Analysed: {len(self.evidence_map)}")
        
        kill_shots = self.get_kill_shots()
        print(f"Kill Shots Identified: {kill_shots['total']}")
        
        print(f"Missing Documents Found: {len(self.knowledge_base.get('missing_docs', {}))}")
        print(f"Theories Developed: {len(self.knowledge_base.get('theories', {}))}")
        print(f"Critical Findings: {self.performance_metrics['critical_findings']}")
        print("\n✅ Opus 4.1 Analysis Complete - Ready for Tribunal")