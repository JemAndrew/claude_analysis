#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Optimised for autonomous analysis - Lismore v Process Holdings
British English throughout
"""

import os
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Central configuration for maximum Claude autonomy"""
    
    def __init__(self, root_path: str = None):
        """Initialise configuration with simplified structure"""
        self.root = Path(root_path) if root_path else Path.cwd()
        self._setup_paths()
        self._setup_models()
        self._setup_analysis()
        self._setup_investigation()
        self._setup_autonomous_organisation()
    
    def _setup_paths(self) -> None:
        """Define optimised folder structure for autonomous analysis"""
        # Input paths - SIMPLIFIED STRUCTURE
        self.input_dir = self.root / "data"
        self.legal_knowledge_dir = self.input_dir / "legal_knowledge"
        self.case_documents_dir = self.input_dir / "case_documents"  # COMBINED folder
        
        # Knowledge management
        self.knowledge_dir = self.root / "data" / "knowledge"
        self.graph_db_path = self.knowledge_dir / "graph.db"
        self.backups_dir = self.knowledge_dir / "backups"
        self.memory_bank_dir = self.knowledge_dir / "memory_bank"  # NEW
        
        # Claude's self-organised structure
        self.organised_docs_dir = self.knowledge_dir / "claude_organised"
        self.critical_docs_dir = self.organised_docs_dir / "critical"
        self.timeline_docs_dir = self.organised_docs_dir / "timeline"
        self.entity_docs_dir = self.organised_docs_dir / "by_entity"
        self.suspicious_docs_dir = self.organised_docs_dir / "suspicious"
        self.deep_dive_dir = self.organised_docs_dir / "deep_dive_required"
        
        # Output paths
        self.output_dir = self.root / "data" / "output"
        self.analysis_dir = self.output_dir / "analysis"
        self.investigations_dir = self.output_dir / "investigations"
        self.reports_dir = self.output_dir / "reports"
        
        # Create all directories
        for dir_path in [
            self.input_dir, self.legal_knowledge_dir, self.case_documents_dir,
            self.knowledge_dir, self.backups_dir, self.memory_bank_dir,
            self.organised_docs_dir, self.critical_docs_dir, self.timeline_docs_dir,
            self.entity_docs_dir, self.suspicious_docs_dir, self.deep_dive_dir,
            self.output_dir, self.analysis_dir, self.investigations_dir, self.reports_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_models(self) -> None:
        """Model selection - Opus 4.1 for all critical work"""
        
        # Model configuration with YOUR specified models
        self.models = {
            'primary': 'claude-opus-4-1-20250805',      # Maximum capability
            'quick': 'claude-3-haiku-20240307'          # Quick validation only
        }
        
        # Phase-specific model selection - Opus for everything important
        self.phase_models = {
            'knowledge_loading': 'claude-opus-4-1-20250805',
            'document_organisation': 'claude-opus-4-1-20250805',
            'initial_analysis': 'claude-opus-4-1-20250805',
            'deep_investigation': 'claude-opus-4-1-20250805',
            'contradiction_analysis': 'claude-opus-4-1-20250805',
            'pattern_recognition': 'claude-opus-4-1-20250805',
            'entity_analysis': 'claude-opus-4-1-20250805',
            'timeline_analysis': 'claude-opus-4-1-20250805',
            'recursive_questioning': 'claude-opus-4-1-20250805',
            'adversarial_analysis': 'claude-opus-4-1-20250805',
            'synthesis': 'claude-opus-4-1-20250805',
            'quick_validation': 'claude-3-haiku-20240307'
        }
        
        # Complexity triggers (always escalate to Opus when detected)
        self.complexity_triggers = {
            'contradiction_found': True,
            'pattern_confidence_high': 0.75,
            'investigation_depth': 2,
            'document_complexity': 0.6,
            'entity_relationships': 8,
            'timeline_gaps': True,
            'financial_analysis': True,
            'legal_reasoning_required': True,
            'strategic_importance': 0.7
        }
    
    def _setup_analysis(self) -> None:
        """Analysis configuration for deep autonomous work"""
        
        # Token management - maximise context
        self.token_config = {
            'max_input_tokens': 200000,      # Full Opus 4.1 window
            'max_output_tokens': 8096,       # Maximum response
            'buffer_tokens': 10000,
            'optimal_batch_size': 180000     # Near-maximum utilisation
        }
        
        # Temperature settings by task type
        self.temperature_settings = {
            'knowledge_synthesis': 0.4,          # Precise learning
            'document_organisation': 0.8,        # Creative organisation
            'pattern_recognition': 0.9,          # Maximum creativity
            'investigation': 1.0,                # Full autonomy
            'hypothesis_generation': 0.95,       # Wild theories encouraged
            'contradiction_analysis': 0.5,       # Precise logic
            'entity_analysis': 0.6,
            'timeline_forensics': 0.5,
            'recursive_questioning': 0.85,       # Creative self-challenge
            'adversarial_analysis': 0.7,
            'synthesis': 0.4,
            'final_report': 0.3
        }
        
        # Batching strategy
        self.batch_strategy = {
            'method': 'semantic_clustering',
            'max_batch_size': 180000,
            'overlap_tokens': 8000,
            'prioritise_by': 'strategic_value',
            'min_batch_size': 60000,
            'allow_dynamic_resizing': True
        }
        
        # Recursive analysis depth - MAXIMUM
        self.recursion_config = {
            'self_questioning_depth': 7,          # 7 levels deep
            'min_questioning_depth': 5,           # Never less than 5
            'investigation_iterations': 20,       # Up to 20 iterations per thread
            'convergence_threshold': 0.98,        # 98% confidence to stop
            'force_deep_dive_on': [
                'NUCLEAR', 'CRITICAL', 'CONTRADICTION', 
                'PATTERN', 'SUSPICIOUS', 'MISSING', 'IMPOSSIBLE'
            ],
            'spawn_child_investigations': True,
            'max_concurrent_investigations': 15
        }
    
    def _setup_investigation(self) -> None:
        """Investigation triggers for autonomous spawning"""
        
        # Auto-investigation triggers - AGGRESSIVE
        self.investigation_triggers = {
            'contradiction_severity': 6,          # Lower threshold (more sensitive)
            'pattern_confidence': 0.7,
            'missing_document_pattern': True,
            'timeline_impossibility': True,
            'financial_anomaly': 0.5,
            'entity_suspicion': 0.6,
            'strategic_importance': 0.7,
            'keyword_triggers': [
                'NUCLEAR', 'CRITICAL', 'INVESTIGATE', 'SUSPICIOUS',
                'ANOMALY', 'IMPOSSIBLE', 'MISSING', 'HIDDEN',
                'CONTRADICTS', 'INCONSISTENT', 'FALSE', 'FABRICATED',
                'WITHHELD', 'CONCEALED', 'COVER', 'DESTROY'
            ]
        }
        
        # Priority weights for investigation ranking
        self.priority_weights = {
            'financial_impact': 0.25,
            'timeline_critical': 0.20,
            'contradiction': 0.20,
            'pattern_strength': 0.15,
            'entity_centrality': 0.10,
            'document_absence': 0.10
        }
        
        # Investigation depth settings
        self.investigation_depth = {
            'quick_investigation': 3,
            'standard_investigation': 5,
            'deep_investigation': 7,
            'nuclear_investigation': 10
        }
    
    def _setup_autonomous_organisation(self) -> None:
        """Configuration for Claude's autonomous document organisation"""
        
        self.autonomous_organisation = {
            'enabled': True,
            'organisation_phase': 'phase_1',  # Document organisation in Phase 1
            
            # Organisation criteria
            'organisation_criteria': [
                'strategic_importance',
                'temporal_significance',
                'entity_centrality',
                'suspicious_indicators',
                'cross_reference_density',
                'evidentiary_value',
                'contradiction_potential',
                'pattern_relevance'
            ],
            
            # Categories Claude should consider creating
            'suggested_categories': [
                'nuclear_evidence',
                'critical_contradictions',
                'timeline_anchors',
                'entity_communications',
                'financial_transactions',
                'suspicious_behaviour',
                'missing_document_references',
                'procedural_documents',
                'background_context',
                'opposing_party_admissions',
                'withheld_evidence_indicators'
            ],
            
            # Organisational freedom
            'max_categories': 25,
            'allow_custom_categories': True,
            'allow_multi_category': True,
            'allow_nested_categories': True,
            'reorganise_after_discovery': True,
            'create_priority_rankings': True
        }
    
    # API configuration
    @property
    def api_config(self) -> Dict[str, Any]:
        """API configuration - NO EXTERNAL DATA SOURCES"""
        return {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'max_retries': 5,
            'retry_delay': 5,
            'exponential_backoff': True,
            'timeout': 180,
            'rate_limit_delay': 12,
            'parallel_calls': False,
            
            # SECURITY: No external data - EXPLICITLY DISABLED
            'web_search_enabled': False,
            'external_apis_enabled': False,
            'internet_access': False,
            'allow_web_requests': False
        }
    
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
    
    def get_model_for_task(self, task_type: str, complexity_score: float = 0.5) -> str:
        """Dynamically select model based on task and complexity"""
        
        # Quick validation only gets Haiku
        if task_type == 'quick_validation':
            return self.models['quick']
        
        # Everything else gets Opus 4.1
        if task_type in self.phase_models:
            return self.phase_models[task_type]
        
        # Check complexity triggers
        if complexity_score > 0.7:
            return self.models['primary']
        
        # Default to Opus for safety
        return self.models['primary']
    
    def should_investigate(self, discovery: Dict[str, Any]) -> bool:
        """Determine if a discovery warrants investigation"""
        
        # Check keyword triggers
        discovery_text = str(discovery).upper()
        if any(trigger in discovery_text for trigger in 
               self.investigation_triggers['keyword_triggers']):
            return True
        
        # Check metric triggers
        if discovery.get('contradiction_severity', 0) >= self.investigation_triggers['contradiction_severity']:
            return True
        
        if discovery.get('pattern_confidence', 0) >= self.investigation_triggers['pattern_confidence']:
            return True
        
        if discovery.get('timeline_impossibility'):
            return True
        
        if discovery.get('financial_anomaly', 0) >= self.investigation_triggers['financial_anomaly']:
            return True
        
        if discovery.get('strategic_importance', 0) >= self.investigation_triggers.get('strategic_importance', 0.7):
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