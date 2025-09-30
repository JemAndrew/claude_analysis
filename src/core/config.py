#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Simplified for maximum Claude autonomy - Lismore v Process Holdings
British English throughout
"""

import os
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Central configuration for autonomous Claude analysis"""
    
    def __init__(self, root_path: str = None):
        """Initialise configuration with simplified structure"""
        self.root = Path(root_path) if root_path else Path.cwd()
        self._setup_paths()
        self._setup_models()
        self._setup_analysis()
        self._setup_investigation()
    
    def _setup_paths(self) -> None:
        """Define simplified folder structure - Claude organises content"""
        
        # Input paths - SIMPLIFIED (no pre-organised folders)
        self.input_dir = self.root / "data" / "input"
        self.legal_knowledge_dir = self.input_dir / "legal_knowledge"
        self.case_documents_dir = self.input_dir / "case_documents"
        
        # Knowledge management
        self.knowledge_dir = self.root / "data" / "knowledge"
        self.graph_db_path = self.knowledge_dir / "graph.db"
        self.backups_dir = self.knowledge_dir / "backups"
        self.investigations_db_path = self.knowledge_dir / "investigations.db"
        
        # Output paths
        self.output_dir = self.root / "data" / "output"
        self.reports_dir = self.output_dir / "reports"
        
        # Create directories if they don't exist
        for dir_path in [
            self.input_dir, self.legal_knowledge_dir, self.case_documents_dir,
            self.knowledge_dir, self.backups_dir,
            self.output_dir, self.reports_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_models(self) -> None:
        """Model selection - using working API model names"""
        
        # Primary models - CORRECTED MODEL NAMES
        self.models = {
            'primary': 'claude-3-5-sonnet-20241022',   # Sonnet 3.7 - Best balance
            'secondary': 'claude-3-haiku-20240307',    # Haiku 3 - Fallback
            'quick': 'claude-3-haiku-20240307'         # Haiku 3 - Quick tasks
        }
        
        # Phase-specific model selection
        self.phase_models = {
            'knowledge_synthesis': 'claude-3-5-sonnet-20241022',  # Critical learning
            'case_understanding': 'claude-3-5-sonnet-20241022',   # First read
            'investigation': 'claude-3-5-sonnet-20241022',        # Free investigation
            'synthesis': 'claude-3-5-sonnet-20241022',            # Final synthesis
            'quick_validation': 'claude-3-haiku-20240307'         # Simple checks
        }
        
        # Complexity triggers for automatic model selection
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
        """Analysis configuration for maximum capability"""
        
        # Token management - maximise context
        self.token_config = {
            'max_input_tokens': 150000,     # Maximum context window
            'max_output_tokens': 4096,      # Maximum response
            'buffer_tokens': 10000,         # Safety buffer
            'optimal_batch_size': 140000    # Optimal for processing
        }
        
        # Temperature settings by task type
        self.temperature_settings = {
            'creative_investigation': 0.9,   # High for hypothesis generation
            'hypothesis_generation': 0.8,    # Creative thinking
            'pattern_recognition': 0.6,      # Balanced
            'contradiction_analysis': 0.4,   # Logical precision
            'synthesis': 0.3,                # Structured thinking
            'final_report': 0.2              # Consistent output
        }
        
        # Batch processing strategy
        self.batch_strategy = {
            'max_batch_size': 150000,        # Maximum tokens per batch
            'min_batch_size': 20000,         # Minimum viable batch
            'overlap_tokens': 2000,          # Context overlap between batches
            'smart_splitting': True,         # Split on logical boundaries
            'semantic_clustering': True      # Group related documents
        }
        
        # Investigation spawning thresholds
        self.investigation_thresholds = {
            'contradiction_severity': 7,     # Severity > 7 spawns investigation
            'pattern_confidence': 0.8,       # Confidence > 0.8 spawns investigation
            'entity_suspicion': 0.7,         # Suspicion score > 0.7
            'timeline_gap_days': 30,         # Gaps > 30 days are suspicious
            'amount_threshold': 100000,      # Amounts > £100k warrant investigation
            'max_concurrent': 5              # Maximum parallel investigations
        }
    
    def _setup_investigation(self) -> None:
        """Investigation and discovery configuration"""
        
        # Discovery markers - what Claude should flag
        self.discovery_markers = {
            'nuclear': ['NUCLEAR', 'CASE-ENDING', 'SMOKING GUN'],
            'critical': ['CRITICAL', 'MAJOR', 'SIGNIFICANT'],
            'investigate': ['INVESTIGATE', 'SUSPICIOUS', 'ANOMALY'],
            'pattern': ['PATTERN', 'RECURRING', 'SYSTEMATIC'],
            'contradiction': ['CONTRADICTION', 'INCONSISTENT', 'CONFLICTS']
        }
        
        # Strategic focus - what matters for Lismore
        self.strategic_focus = {
            'our_client': 'Lismore Capital',
            'opponent': 'Process Holdings',
            'case_type': 'arbitration',
            'goal': 'destroy_their_case',
            'key_themes': [
                'breach of contract', 'fraud', 'misrepresentation',
                'liability', 'damages', 'negligence',
                'conspiracy', 'bad faith'
            ]
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
            'cache_size': -64000,          # 64MB cache
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
        """Dynamically select model based on task and complexity"""
        
        # Check if task has specific model assignment
        if task_type in self.phase_models:
            base_model = self.phase_models[task_type]
        else:
            base_model = self.models['primary']
        
        # High complexity always uses primary (Sonnet)
        if complexity_score > 0.7 and base_model != self.models['primary']:
            return self.models['primary']
        
        return base_model
    
    def should_spawn_investigation(self, 
                                   trigger_type: str,
                                   trigger_data: Dict) -> bool:
        """Determine if trigger warrants spawning investigation"""
        
        thresholds = self.investigation_thresholds
        
        if trigger_type == 'contradiction':
            return trigger_data.get('severity', 0) >= thresholds['contradiction_severity']
        
        elif trigger_type == 'pattern':
            return trigger_data.get('confidence', 0) >= thresholds['pattern_confidence']
        
        elif trigger_type == 'entity':
            return trigger_data.get('suspicion_score', 0) >= thresholds['entity_suspicion']
        
        elif trigger_type == 'timeline_gap':
            return trigger_data.get('gap_days', 0) >= thresholds['timeline_gap_days']
        
        elif trigger_type == 'financial':
            return trigger_data.get('amount', 0) >= thresholds['amount_threshold']
        
        # Default: spawn if marked critical
        return trigger_data.get('priority', 0) >= 8.0


# Global config instance
config = Config()