#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Optimised for maximum Claude capability - Lismore v Process Holdings
ENHANCED VERSION with Sonnet 4.5, system prompts, and prompt caching
"""

import os
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Central configuration for maximum Claude utilisation"""
    
    def __init__(self, root_path: str = None):
        """Initialise configuration with organised structure"""
        self.root = Path(root_path) if root_path else Path.cwd()
        self._setup_paths()
        self._setup_models()
        self._setup_analysis()
        self._setup_investigation()
        self._setup_prompting()
    
    def _setup_paths(self) -> None:
        """Define organised folder structure"""
        # Input paths
        self.input_dir = self.root / "data" / "input"
        self.legal_knowledge_dir = self.input_dir / "legal_knowledge"
        self.case_context_dir = self.input_dir / "case_context"
        self.disclosure_dir = self.input_dir / "disclosure"
        
        # Knowledge management
        self.knowledge_dir = self.root / "data" / "knowledge"
        self.graph_db_path = self.knowledge_dir / "graph.db"
        self.backups_dir = self.knowledge_dir / "backups"
        self.investigations_db_path = self.knowledge_dir / "investigations.db"
        
        # Output paths
        self.output_dir = self.root / "data" / "output"
        self.analysis_dir = self.output_dir / "analysis"
        self.investigations_dir = self.output_dir / "investigations"
        self.reports_dir = self.output_dir / "reports"
        
        # Create directories if they don't exist
        for dir_path in [
            self.input_dir, self.legal_knowledge_dir, self.case_context_dir,
            self.disclosure_dir, self.knowledge_dir, self.backups_dir,
            self.output_dir, self.analysis_dir, self.investigations_dir,
            self.reports_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_models(self) -> None:
        """Model selection for maximum reasoning capability"""
        
        # Primary model - Sonnet 4.5 for best performance and cost
        self.models = {
            'primary': 'claude-sonnet-4-5-20250929',    # Best for litigation analysis
            'secondary': 'claude-sonnet-4-5-20250929',  # Same - it's excellent
            'quick': 'claude-3-haiku-20240307'          # Quick validation only
        }
        
        # Phase-specific model selection
        self.phase_models = {
            'knowledge_loading': 'claude-sonnet-4-5-20250929',
            'initial_analysis': 'claude-sonnet-4-5-20250929',
            'deep_investigation': 'claude-sonnet-4-5-20250929',
            'contradiction_analysis': 'claude-sonnet-4-5-20250929',
            'synthesis': 'claude-sonnet-4-5-20250929',
            'quick_validation': 'claude-3-haiku-20240307'
        }
        
        # Complexity triggers for analysis depth
        self.complexity_triggers = {
            'contradiction_found': True,
            'pattern_confidence_high': 0.8,
            'investigation_depth': 3,
            'document_complexity': 0.7,
            'entity_relationships': 10,
            'timeline_gaps': True,
            'financial_analysis': True
        }
    
    def _setup_analysis(self) -> None:
        """Analysis configuration for maximum potential"""
        
        # Token management - maximise context
        self.token_config = {
            'max_input_tokens': 200000,     # Sonnet 4.5 supports 200k
            'max_output_tokens': 8192,      # Sonnet 4.5 supports 8k
            'buffer_tokens': 10000,         # Safety buffer
            'optimal_batch_size': 180000,   # Optimal for 200k window
            'cache_breakpoint': 1024        # Minimum tokens for caching
        }
        
        # Temperature settings by task type
        self.temperature_settings = {
            'creative_investigation': 0.9,
            'hypothesis_generation': 0.8,
            'pattern_recognition': 0.6,
            'contradiction_analysis': 0.4,
            'synthesis': 0.3,
            'final_report': 0.2
        }
        
        # Prompt caching configuration
        self.caching_config = {
            'enabled': True,
            'cache_legal_knowledge': True,
            'cache_case_context': True,
            'cache_knowledge_graph': True,
            'cache_duration': 300,              # 5 minutes (standard)
            'min_tokens_to_cache': 1024
        }
        
        # Batching strategy
        self.batch_strategy = {
            'method': 'semantic_clustering',
            'max_batch_size': 180000,
            'overlap_tokens': 5000,
            'prioritise_by': 'relevance',
            'min_batch_size': 50000
        }
        
        # Recursive analysis depth
        self.recursion_config = {
            'self_questioning_depth': 5,
            'min_questioning_depth': 3,
            'investigation_iterations': 10,
            'convergence_threshold': 0.95,
            'force_deep_dive_on': ['CRITICAL', 'NUCLEAR', 'CONTRADICTION']
        }
    
    def _setup_investigation(self) -> None:
        """Investigation triggers and thresholds"""
        
        # Auto-investigation triggers
        self.investigation_triggers = {
            'contradiction_severity': 7,
            'pattern_confidence': 0.8,
            'missing_document_pattern': True,
            'timeline_impossibility': True,
            'financial_anomaly': 0.6,
            'entity_suspicion': 0.7,
            'keyword_triggers': [
                'CRITICAL', 'NUCLEAR', 'INVESTIGATE',
                'SUSPICIOUS', 'ANOMALY', 'IMPOSSIBLE'
            ]
        }
        
        # Investigation depth by priority
        self.investigation_depth = {
            'nuclear': 7,
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2
        }
        
        # Priority weights for investigation scoring
        self.priority_weights = {
            'financial_impact': 0.3,
            'timeline_critical': 0.25,
            'contradiction': 0.2,
            'pattern_strength': 0.15,
            'entity_centrality': 0.05,
            'document_absence': 0.05
        }
        
        # Analysis categories with keywords
        self.analysis_categories = {
            'contract_breaches': [
                'breach', 'violation', 'default', 'non-compliance',
                'failed to', 'obligation', 'duty'
            ],
            'fraud': [
                'fraud', 'misrepresentation', 'false statement',
                'deception', 'concealment', 'dishonest'
            ],
            'credibility': [
                'inconsistent', 'contradicts', 'implausible',
                'impossible', 'conflicting'
            ],
            'document_withholding': [
                'missing', 'not provided', 'withheld',
                'absent', 'no record', 'cannot locate'
            ],
            'financial': [
                'payment', 'invoice', 'valuation', 'loss',
                'damages', 'cost', 'liability'
            ],
            'legal_doctrines': [
                'liability', 'damages', 'negligence',
                'fraud', 'misrepresentation', 'conspiracy'
            ]
        }
    
    def _setup_prompting(self) -> None:
        """Enhanced prompting configuration"""
        
        # System prompt for all litigation analysis
        self.system_prompt = self._get_litigation_system_prompt()
        
        # Prefill templates for consistent outputs
        self.prefill_templates = {
            'finding_xml': '<finding id="F001">\n  <category>',
            'executive_summary': 'EXECUTIVE SUMMARY FOR TRIBUNAL\n\nThe evidence demonstrates',
            'analysis_cot': 'ANALYSIS\n\n<thinking>\nStep 1: ',
            'json_output': '{"critical_findings": [',
            'citation_format': '[DOC_001: Para 15] The evidence shows'
        }
        
        # Hallucination prevention (used in all prompts)
        self.hallucination_prevention = """<critical_accuracy_requirements>
You MUST follow these rules without exception:

1. CITATIONS ARE MANDATORY
   - Every factual claim must cite [DOC_ID: Location]
   - Never reference a document not provided to you
   - Never fabricate document content
   - If uncertain, mark with [NEEDS_VERIFICATION]

2. DISTINGUISH FACTS FROM INFERENCES
   - Facts: "The contract states X" [DOC_001: Para 5]
   - Inferences: "This suggests Y" (clearly marked as inference)
   - Never present inferences as facts

3. ACKNOWLEDGE GAPS
   - If information is missing, say so explicitly
   - Don't fill gaps with assumptions
   - Flag what additional evidence would be needed

4. BE PRECISE
   - Use exact dates, amounts, party names
   - Never say "approximately" when exact figures are available
   - Quote key phrases exactly when critical

5. VERIFICATION
   - Before finalising any finding, mentally re-check citations
   - Ensure quoted text actually appears in referenced document
   - Flag anything you're less than 80% confident about
</critical_accuracy_requirements>"""
    
    def _get_litigation_system_prompt(self) -> str:
        """System prompt for all litigation analysis"""
        
        return """You are an expert litigation analyst working FOR Lismore Capital in their arbitration against Process Holdings. Your role is to:

CORE MISSION:
- Find EVERY piece of evidence that helps Lismore win
- Identify ALL weaknesses in Process Holdings' position  
- Build the strongest possible case for Lismore

ANALYSIS STANDARDS:
- Think step-by-step through complex legal reasoning
- Cite EVERY claim with [DOC_ID: Location] format
- Consider counter-arguments and pre-emptively rebut them
- Assess confidence levels honestly (0.0-1.0)
- Flag any assumptions you're making
- Use British English spelling throughout (analyse, realise, organisation, centre, behaviour)

FORBIDDEN BEHAVIOURS:
- Never fabricate facts or citations
- Never ignore contradicting evidence (analyse it critically instead)
- Never be vague - always be specific with dates, amounts, parties
- Never hedge excessively - be assertive when evidence supports it

TONE:
- Authoritative but measured
- Confident where evidence is strong
- Appropriately cautious where evidence is weak
- Always focused on winning for Lismore

You are NOT neutral - you are Lismore's analyst. Act accordingly."""
    
    # Database configuration
    @property
    def db_config(self) -> Dict[str, Any]:
        """SQLite configuration for knowledge persistence"""
        return {
            'path': str(self.graph_db_path),
            'backup_on_phase': True,
            'versioning': True,
            'compression': True,
            'wal_mode': True,
            'cache_size': -64000,
            'foreign_keys': True,
            'auto_vacuum': 'INCREMENTAL'
        }
    
    # API configuration
    @property
    def api_config(self) -> Dict[str, Any]:
        """API configuration for Claude"""
        return {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'max_retries': 5,
            'retry_delay': 5,
            'exponential_backoff': True,
            'timeout': 120,
            'rate_limit_delay': 10,
            'parallel_calls': False
        }
    
    def get_model_for_task(self, task_type: str, complexity_score: float = 0.5) -> str:
        """Get model for task - Sonnet 4.5 for all litigation work"""
        
        # Quick validation can use Haiku
        if task_type == 'quick_validation':
            return self.models['quick']
        
        # Everything else uses Sonnet 4.5
        return self.models['primary']
    
    def should_investigate(self, discovery: Dict[str, Any]) -> bool:
        """Determine if a discovery warrants investigation"""
        
        # Check keyword triggers
        if any(trigger in str(discovery).upper() for trigger in 
               self.investigation_triggers['keyword_triggers']):
            return True
        
        # Check metric triggers
        if discovery.get('contradiction_severity', 0) > self.investigation_triggers['contradiction_severity']:
            return True
        
        if discovery.get('pattern_confidence', 0) > self.investigation_triggers['pattern_confidence']:
            return True
        
        if discovery.get('timeline_impossibility'):
            return True
        
        if discovery.get('financial_anomaly', 0) > self.investigation_triggers['financial_anomaly']:
            return True
        
        return False
    
    def calculate_priority(self, discovery: Dict[str, Any]) -> float:
        """Calculate investigation priority score"""
        
        score = 0.0
        
        # Apply weighted scoring
        if 'financial_impact' in discovery:
            score += discovery['financial_impact'] * self.priority_weights['financial_impact']
        
        if discovery.get('timeline_critical'):
            score += self.priority_weights['timeline_critical']
        
        if discovery.get('contradiction_severity'):
            score += discovery['contradiction_severity'] * self.priority_weights['contradiction'] / 10
        
        if discovery.get('pattern_confidence'):
            score += discovery['pattern_confidence'] * self.priority_weights['pattern_strength']
        
        if discovery.get('entity_centrality'):
            score += discovery['entity_centrality'] * self.priority_weights['entity_centrality']
        
        if discovery.get('document_absence'):
            score += self.priority_weights['document_absence']
        
        return min(score, 10.0)


# Global config instance
config = Config()