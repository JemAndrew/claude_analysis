from pathlib import Path
import json
from typing import Dict, List, Any
from datetime import datetime

class KnowledgeManager:
    """Manages knowledge base and investigation memory"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.evidence_map = {}
        
        # Initialise enhanced knowledge base
        self.knowledge_base = {
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
        
        # Investigation memory
        self.investigation_memory = {
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
        
        # Phase prompts
        self.phase_prompts = {
            'phase_1_additions': "",
            'phase_2_additions': "",
            'phase_3_additions': "",
            'phase_4_additions': "",
            'phase_5_additions': "",
            'phase_6_additions': ""
        }
        
        self.load_existing_knowledge()
    
    def load_existing_knowledge(self):
        """Load existing knowledge base from disk"""
        kb_file = self.project_root / "memory" / "opus_41_knowledge_base.json"
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                stored_kb = json.load(f)
                self.knowledge_base.update(stored_kb)
    
    def save_knowledge_base(self):
        """Save knowledge base to disk"""
        kb_file = self.project_root / "memory" / "opus_41_knowledge_base.json"
        kb_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def update_from_phase(self, phase: str, findings: str):
        """Update knowledge base with phase findings"""
        # Implementation of extraction logic
        # This would call specific extraction methods based on phase
        self.save_knowledge_base()
    
    def build_cumulative_context(self, phase: int) -> str:
        """Build context with Opus 4.1 enhancements"""
        context = "OPUS 4.1 ACCUMULATED INTELLIGENCE:\n\n"
        
        # Add legal training
        if self.knowledge_base.get('legal_training'):
            context += "Legal Framework Mastery:\n"
            context += f"{json.dumps(self.knowledge_base['legal_training'], indent=2)[:1500]}\n\n"
        
        # Add case context
        if self.knowledge_base.get('case_context'):
            context += "Case Intelligence:\n"
            context += f"{json.dumps(self.knowledge_base['case_context'], indent=2)[:1500]}\n\n"
        
        # Add phase-specific discoveries
        context += "Investigation Progress:\n"
        context += self.summarise_findings(1, phase)
        
        return context
    
    def summarise_findings(self, start_phase: int, end_phase: int) -> str:
        """Summarise findings with litigation focus"""
        summary = ""
        
        if end_phase >= 1:
            summary += f"\nKey Players Identified: {len(self.knowledge_base.get('players', {}))}"
            summary += f"\nDocuments Analysed: {len(self.evidence_map)}"
        
        if end_phase >= 2:
            patterns = self.knowledge_base.get('patterns', {})
            summary += f"\nControl Patterns: {len(patterns.get('control_patterns', []))}"
            summary += f"\nDeception Indicators: {len(patterns.get('deception_indicators', []))}"
        
        # ... continue for other phases
        
        return summary[:2000]
    
    def get_kill_shots(self) -> Dict:
        """Get kill shots summary"""
        kill_shots = self.knowledge_base.get('kill_shots', {})
        total = sum(len(v) for v in kill_shots.values() if isinstance(v, list))
        return {'total': total, 'details': kill_shots}
    
    def get_missing_docs(self) -> Dict:
        """Get missing documents"""
        return self.knowledge_base.get('missing_docs', {})
    
    def get_theories(self) -> Dict:
        """Get theories"""
        return self.knowledge_base.get('theories', {})
    
    def store_adverse_inference(self, report: List[Dict]):
        """Store adverse inference opportunities"""
        self.knowledge_base['missing_docs']['adverse_inference_opportunities'] = report
        self.save_knowledge_base()
    
    def update_legal_training(self, doc_count: int):
        """Update legal training status"""
        self.knowledge_base['legal_training']['documents_studied'] = doc_count
        self.knowledge_base['legal_training']['training_complete'] = True
        self.knowledge_base['legal_training']['opus_41_enhanced'] = True
        self.save_knowledge_base()
    
    def update_case_context(self, doc_count: int):
        """Update case context"""
        self.knowledge_base['case_context']['documents_studied'] = doc_count
        self.save_knowledge_base()