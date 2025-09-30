#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Optimised for maximum Claude capability - Lismore v Process Holdings
Enhanced with valid model names and metadata filtering settings
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
        self._setup_metadata_filtering()  # NEW: Metadata filtering configuration
    
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
        """Model selection with VALID API model names"""
        
        # UPDATED: Using valid model identifiers that work with the API
        self.models = {
            'primary': 'claude-3-opus-20240229',      # Valid Opus model
            'secondary': 'claude-3-5-sonnet-20241022', # Valid Sonnet model
            'quick': 'claude-3-haiku-20240307'        # Valid Haiku model
        }
        
        # Phase-specific model selection with valid names
        self.phase_models = {
            'knowledge_loading': 'claude-3-opus-20240229',     # Critical learning
            'initial_analysis': 'claude-3-opus-20240229',      # Pattern recognition
            'deep_investigation': 'claude-3-opus-20240229',    # Complex reasoning
            'contradiction_analysis': 'claude-3-opus-20240229', # Logic required
            'synthesis': 'claude-3-opus-20240229',             # Strategic thinking
            'quick_validation': 'claude-3-haiku-20240307'      # Simple checks only
        }
        
        # Complexity triggers for automatic Opus upgrade
        self.complexity_triggers = {
            'contradiction_found': True,
            'pattern_confidence_high': 0.8,  # Confidence > 0.8
            'investigation_depth': 3,         # Recursive depth > 3
            'document_complexity': 0.7,       # Complexity score > 0.7
            'entity_relationships': 10,       # More than 10 relationships
            'timeline_gaps': True,           # Timeline inconsistencies
            'financial_analysis': True       # Any financial forensics
        }
    
    def _setup_analysis(self) -> None:
        """Analysis configuration for maximum potential"""
        
        # Token management - maximise context
        self.token_config = {
            'max_input_tokens': 150000,     # Maximum context window
            'max_output_tokens': 4096,      # Maximum response
            'buffer_tokens': 10000,          # Safety buffer
            'optimal_batch_size': 140000    # Optimal for processing
        }
        
        # Temperature settings by task type
        self.temperature_settings = {
            'creative_investigation': 0.9,   # Maximum creativity
            'hypothesis_generation': 0.8,    # High creativity
            'pattern_recognition': 0.6,      # Balanced
            'contradiction_analysis': 0.4,   # More focused
            'synthesis': 0.3,                # Precise
            'final_report': 0.2              # Very precise
        }
        
        # Batching strategy
        self.batch_strategy = {
            'method': 'semantic_clustering',  # Group related documents
            'max_batch_size': 140000,        # Token limit per batch
            'overlap_tokens': 5000,          # Context overlap between batches
            'prioritise_by': 'relevance',    # relevance/chronology/entity
            'min_batch_size': 50000          # Don't waste API calls
        }
        
        # Recursive analysis depth
        self.recursion_config = {
            'self_questioning_depth': 5,      # 5 levels deep
            'min_questioning_depth': 3,       # Never less than 3
            'investigation_iterations': 10,   # Max iterations per thread
            'convergence_threshold': 0.95,    # Stop when confidence > 95%
            'force_deep_dive_on': ['CRITICAL', 'NUCLEAR', 'CONTRADICTION']
        }
    
    def _setup_investigation(self) -> None:
        """Investigation triggers and thresholds"""
        
        # Auto-investigation triggers
        self.investigation_triggers = {
            'contradiction_severity': 7,      # Severity > 7/10
            'pattern_confidence': 0.8,       # Confidence > 0.8
            'missing_document_pattern': True, # Always investigate
            'timeline_impossibility': True,   # Always investigate
            'financial_anomaly': 0.6,        # Anomaly score > 0.6
            'entity_suspicion': 0.7,         # Suspicion score > 0.7
            'keyword_triggers': [
                'CRITICAL', 'NUCLEAR', 'INVESTIGATE',
                'SUSPICIOUS', 'ANOMALY', 'IMPOSSIBLE'
            ]
        }
        
        # Investigation priority scoring
        self.priority_weights = {
            'financial_impact': 3.0,          # Triple weight for money
            'timeline_critical': 2.5,         # Key for causation
            'contradiction': 2.0,             # Direct evidence
            'pattern_strength': 1.5,          # Circumstantial
            'entity_centrality': 1.5,         # Key player involvement
            'document_absence': 2.0           # Missing evidence
        }
        
        # Investigation depth settings
        self.investigation_depth = {
            'initial_sweep': 1,               # First pass
            'standard_investigation': 3,      # Normal depth
            'deep_investigation': 5,          # Triggered by high priority
            'exhaustive_investigation': 10,   # Manual trigger only
            'parallel_threads': 5             # Max concurrent investigations
        }
    
    def _setup_metadata_filtering(self) -> None:
        """NEW: Metadata filtering configuration"""
        
        # Metadata relevance scoring for different phases
        self.metadata_relevance = {
            'financial_analysis': {
                'has_amounts': 3.0,
                'amount_count': 0.5,  # Per amount
                'classification_financial': 2.0,
                'has_tables': 1.0
            },
            'timeline_analysis': {
                'has_dates': 3.0,
                'date_count': 0.5,  # Per date
                'classification_contract': 1.5,
                'classification_correspondence': 1.0
            },
            'entity_analysis': {
                'person_count': 0.5,  # Per person
                'company_count': 0.5,  # Per company
                'has_emails': 1.0,
                'classification_correspondence': 1.5
            },
            'contradiction_analysis': {
                'has_dates': 2.0,
                'entity_count': 0.3,  # Per entity
                'classification_contract': 1.5,
                'classification_witness_statement': 2.0
            }
        }
        
        # Document filtering thresholds
        self.filtering_thresholds = {
            'minimum_relevance_score': 1.0,  # Min score to include document
            'maximum_documents_per_batch': 50,  # Max docs per API call
            'priority_document_threshold': 5.0,  # Score for priority processing
        }
        
        # Metadata extraction patterns
        self.metadata_patterns = {
            'critical_terms': [
                'breach', 'fraud', 'misrepresentation', 'conspiracy',
                'default', 'termination', 'damages', 'liability'
            ],
            'priority_entities': [
                'Lismore', 'Process Holdings', 'VR Capital'
            ],
            'suspicious_patterns': [
                'confidential', 'privileged', 'without prejudice',
                'off the record', 'destroy after reading'
            ]
        }
    
    # Entity categories for knowledge graph
    @property
    def base_entities(self) -> Dict[str, List[str]]:
        """Base entity types for Lismore case"""
        return {
            'people': [
                'director', 'advisor', 'witness', 'expert',
                'shareholder', 'employee', 'legal_representative'
            ],
            'companies': [
                'defendant', 'plaintiff', 'subsidiary', 'parent',
                'related_party', 'third_party', 'joint_venture'
            ],
            'financial': [
                'payment', 'valuation', 'loss', 'profit', 'investment',
                'debt', 'asset', 'liability', 'transaction'
            ],
            'dates': [
                'contract_date', 'breach_date', 'payment_date',
                'meeting_date', 'filing_date', 'deadline', 'event'
            ],
            'documents': [
                'contract', 'email', 'report', 'minutes', 'invoice',
                'statement', 'filing', 'correspondence', 'evidence'
            ],
            'legal_concepts': [
                'breach', 'duty', 'liability', 'damages', 'negligence',
                'fraud', 'misrepresentation', 'conspiracy'
            ]
        }
    
    # Database configuration
    @property
    def db_config(self) -> Dict[str, Any]:
        """SQLite configuration for knowledge persistence"""
        return {
            'path': str(self.graph_db_path),
            'backup_on_phase': True,          # Backup before each phase
            'versioning': True,                # Track version history
            'compression': True,               # Compress backups
            'wal_mode': True,                  # Write-ahead logging for performance
            'cache_size': -64000,              # 64MB cache
            'foreign_keys': True,              # Enforce relationships
            'auto_vacuum': 'INCREMENTAL'       # Gradual space reclamation
        }
    
    # API configuration
    @property
    def api_config(self) -> Dict[str, Any]:
        """API configuration for Claude"""
        return {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'max_retries': 5,
            'retry_delay': 5,                 # Base delay in seconds
            'exponential_backoff': True,
            'timeout': 120,                   # 2 minutes timeout
            'rate_limit_delay': 10,           # Delay between calls
            'parallel_calls': False           # Sequential for consistency
        }
    
    def get_model_for_task(self, task_type: str, complexity_score: float = 0.5) -> str:
        """Dynamically select model based on task and complexity"""
        
        # Always use Opus for critical phases
        if task_type in self.phase_models:
            base_model = self.phase_models[task_type]
        else:
            base_model = self.models['primary']
        
        # Check if complexity triggers upgrade to Opus
        if complexity_score > 0.7 and base_model != self.models['primary']:
            return self.models['primary']
        
        return base_model
    
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
        
        return min(score, 10.0)  # Cap at 10
    
    def calculate_metadata_relevance(self, metadata: Dict, analysis_type: str) -> float:
        """NEW: Calculate relevance score based on metadata"""
        
        score = 0.0
        relevance_config = self.metadata_relevance.get(analysis_type, {})
        
        # Check boolean flags
        for flag in ['has_amounts', 'has_dates', 'has_tables', 'has_emails']:
            if metadata.get(flag) and flag in relevance_config:
                score += relevance_config[flag]
        
        # Check counts
        if 'amount_count' in relevance_config:
            score += len(metadata.get('amounts_found', [])) * relevance_config['amount_count']
        
        if 'date_count' in relevance_config:
            score += len(metadata.get('dates_found', [])) * relevance_config['date_count']
        
        if 'person_count' in relevance_config:
            score += len(metadata.get('entities', {}).get('people', [])) * relevance_config['person_count']
        
        if 'company_count' in relevance_config:
            score += len(metadata.get('entities', {}).get('companies', [])) * relevance_config['company_count']
        
        if 'entity_count' in relevance_config:
            total_entities = (
                len(metadata.get('entities', {}).get('people', [])) +
                len(metadata.get('entities', {}).get('companies', []))
            )
            score += total_entities * relevance_config['entity_count']
        
        # Check classification
        doc_class = metadata.get('classification', '')
        class_key = f'classification_{doc_class}'
        if class_key in relevance_config:
            score += relevance_config[class_key]
        
        # Check for critical terms in content
        content = metadata.get('content_preview', '')
        for term in self.metadata_patterns['critical_terms']:
            if term in content.lower():
                score += 0.5
        
        # Check for priority entities
        entities = metadata.get('entities', {})
        for priority_entity in self.metadata_patterns['priority_entities']:
            if priority_entity in str(entities):
                score += 1.0
        
        return score

# Global config instance
config = Config()