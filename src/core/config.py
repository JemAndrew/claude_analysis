#!/usr/bin/env python3
"""
Configuration Management for Litigation Intelligence System
COMPLETE REPLACEMENT for src/core/config.py

Sets up all system parameters for comprehensive litigation analysis
- Temperature = 0.0 for consistency
- Prompt caching enabled
- Citation enforcement
- Lismore-sided analysis focus
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json


class Config:
    """Central configuration for litigation intelligence system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialise configuration
        
        Args:
            config_path: Optional path to config file (defaults to project root)
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / 'config.json'
        
        # Load or create configuration
        if self.config_path.exists():
            self._load_config()
        else:
            self._setup_default_config()
            self._save_config()
    
    def _setup_default_config(self) -> None:
        """Set up default configuration values"""
        
        # API Configuration
        self._setup_api()
        
        # Directory Structure
        self._setup_directories()
        
        # Analysis Configuration
        self._setup_analysis()
        
        # Knowledge Graph Configuration
        self._setup_knowledge_graph()
        
        # Orchestration Configuration
        self._setup_orchestration()
        
        # Output Configuration
        self._setup_output()
    
    def _setup_api(self) -> None:
        """API configuration for Claude with prompt caching"""
        
        self.api_config = {
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 16000,  # Increased for comprehensive analysis
            
            # CRITICAL: Prompt caching enabled
            'enable_prompt_caching': True,
            'cache_control_breakpoints': ['legal_framework', 'knowledge_graph'],
            
            # Rate limiting
            'requests_per_minute': 50,
            'tokens_per_minute': 80000,
            
            # Retry configuration
            'max_retries': 3,
            'retry_delay': 2.0,
            'exponential_backoff': True,
        }
    
    def _setup_directories(self) -> None:
        """Directory structure for case files"""
        
        self.directories = {
            # Input directories
            'legal_knowledge': self.project_root / 'data' / 'legal_knowledge',
            'case_background': self.project_root / 'data' / 'case_background',
            'disclosure': self.project_root / 'data' / 'disclosure',
            'validation_tests': self.project_root / 'data' / 'validation_tests',
            
            # Output directories
            'output': self.project_root / 'data' / 'output',
            'analysis': self.project_root / 'data' / 'output' / 'analysis',
            'reports': self.project_root / 'data' / 'output' / 'reports',
            'knowledge_graph': self.project_root / 'data' / 'output' / 'knowledge_graph',
            'logs': self.project_root / 'data' / 'output' / 'logs',
            
            # Cache directories
            'cache': self.project_root / 'data' / 'cache',
            'processed_docs': self.project_root / 'data' / 'cache' / 'processed',
        }
        
        # Create all directories
        for directory in self.directories.values():
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_analysis(self) -> None:
        """Analysis configuration for comprehensive litigation intelligence"""
        
        # CRITICAL: All temperatures = 0.0 for consistency and deterministic output
        self.temperature_config = {
            'knowledge_synthesis': 0.0,      # Phase 0: Legal knowledge
            'investigation': 0.0,            # Document analysis
            'pattern_recognition': 0.0,      # Pattern detection
            'contradiction_analysis': 0.0,   # Finding contradictions
            'credibility_analysis': 0.0,     # Witness credibility
            'legal_argument': 0.0,           # Legal reasoning
            'damages_analysis': 0.0,         # Financial calculations
            'synthesis': 0.0,                # Final reports
            'recursive_questioning': 0.0,    # Deep investigation
            'hypothesis_generation': 0.0,    # Even creative tasks
        }
        
        # Analysis scope - COMPREHENSIVE for Lismore
        self.analysis_scope = {
            'contract_breach_analysis': True,
            'fraud_misrepresentation': True,
            'fiduciary_duty_breach': True,
            'credibility_attacks': True,
            'damages_quantification': True,
            'procedural_advantages': True,
            'novel_legal_arguments': True,
            'document_withholding': True,  # Still included but not primary focus
            'witness_inconsistencies': True,
            'timeline_reconstruction': True,
            'financial_analysis': True,
            'strategic_recommendations': True,
        }
        
        # Investigation triggers
        self.investigation_triggers = {
            'contradiction_severity': 7,           # 0-10 scale
            'pattern_confidence': 0.75,            # 0-1 scale
            'legal_argument_strength': 0.7,        # 0-1 scale
            'credibility_issue_severity': 7,       # 0-10 scale
            'damages_evidence_found': True,        # Boolean trigger
            'contractual_breach_identified': True, # Boolean trigger
            'fraud_indicators': 3,                 # Number of indicators
            'missing_document_references': 2,      # Count threshold
        }
        
        # Recursive investigation depth
        self.recursive_config = {
            'max_depth': 3,                    # How many layers of questioning
            'min_importance_score': 7,         # Only recurse on high-value findings
            'questions_per_finding': 5,        # Questions to ask per issue
            'follow_contradictions': True,     # Always dig into contradictions
            'follow_gaps': True,               # Investigate missing evidence
            'follow_patterns': True,           # Explore detected patterns
        }
        
        # Citation enforcement - MANDATORY
        self.citation_requirements = {
            'mandatory': True,
            'format': '[DOC_ID: Page X, Para Y]',
            'require_exact_quotes': True,
            'verify_citations': True,
            'reject_uncited_claims': True,
        }
    
    def _setup_knowledge_graph(self) -> None:
        """Knowledge graph configuration"""
        
        self.knowledge_graph_config = {
            # Entity extraction
            'extract_entities': True,
            'entity_types': [
                'person', 'organisation', 'contract', 'obligation',
                'payment', 'delivery', 'breach', 'representation',
                'warranty', 'document', 'meeting', 'communication'
            ],
            
            # Relationship tracking
            'track_relationships': True,
            'relationship_types': [
                'contradicts', 'supports', 'references', 'supersedes',
                'breaches', 'fulfils', 'owes', 'paid', 'delivered',
                'represented', 'witnessed', 'disclosed', 'withheld'
            ],
            
            # Temporal tracking
            'track_timeline': True,
            'date_extraction': True,
            'sequence_reconstruction': True,
            
            # Pattern detection
            'detect_patterns': True,
            'pattern_types': [
                'systematic_withholding',
                'late_disclosure_pattern',
                'contradictory_explanations',
                'inconsistent_testimony',
                'financial_discrepancies',
                'timeline_gaps',
                'document_trails'
            ],
            
            # Confidence scoring
            'use_confidence_scores': True,
            'min_confidence': 0.7,
        }
    
    def _setup_orchestration(self) -> None:
        """Orchestration configuration for multi-phase analysis"""
        
        self.orchestration_config = {
            # Phase configuration
            'phases': [
                {
                    'name': 'phase_0_knowledge_synthesis',
                    'description': 'Legal knowledge and case background synthesis',
                    'required': True,
                    'output_to_kg': True,
                },
                {
                    'name': 'phase_1_disclosure_analysis',
                    'description': 'Comprehensive disclosure analysis',
                    'iterations': 3,  # Multiple passes for depth
                    'batch_size': 50,  # Documents per batch
                    'required': True,
                },
                {
                    'name': 'phase_2_pattern_synthesis',
                    'description': 'Cross-document pattern detection',
                    'required': True,
                    'min_documents_analysed': 100,
                },
                {
                    'name': 'phase_3_strategic_synthesis',
                    'description': 'Final strategic report for Lismore',
                    'required': True,
                    'output_format': 'tribunal_ready',
                }
            ],
            
            # Batch processing
            'batch_config': {
                'default_batch_size': 50,
                'max_batch_size': 75,
                'min_batch_size': 10,
                'adaptive_batching': True,  # Adjust based on complexity
            },
            
            # Parallel processing
            'parallel_config': {
                'enable_parallel': False,  # Disabled for consistency
                'max_workers': 1,
                'preserve_order': True,
            },
            
            # Checkpoint configuration
            'checkpointing': {
                'enabled': True,
                'checkpoint_every_n_batches': 10,
                'save_intermediate_results': True,
                'resume_on_failure': True,
            }
        }
    
    def _setup_output(self) -> None:
        """Output configuration"""
        
        self.output_config = {
            # Report formats
            'formats': ['json', 'markdown', 'pdf'],
            'default_format': 'markdown',
            
            # Report sections
            'include_sections': [
                'executive_summary',
                'key_findings',
                'contract_breaches',
                'fraud_indicators',
                'credibility_issues',
                'damages_analysis',
                'legal_arguments',
                'strategic_recommendations',
                'document_withholding',  # One section among many
                'evidence_gaps',
                'procedural_opportunities',
                'annexes_and_citations'
            ],
            
            # Citation format
            'citation_style': 'litigation',  # [DOC_ID: Location]
            'include_citation_index': True,
            'verify_all_citations': True,
            
            # Logging
            'log_level': 'INFO',
            'log_to_file': True,
            'log_api_calls': True,
            'log_costs': True,
        }
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        with open(self.config_path, 'r') as f:
            saved_config = json.load(f)
            
        # Update config from saved values
        for key, value in saved_config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        config_dict = {
            'api_config': self.api_config,
            'directories': {k: str(v) for k, v in self.directories.items()},
            'temperature_config': self.temperature_config,
            'analysis_scope': self.analysis_scope,
            'investigation_triggers': self.investigation_triggers,
            'recursive_config': self.recursive_config,
            'citation_requirements': self.citation_requirements,
            'knowledge_graph_config': self.knowledge_graph_config,
            'orchestration_config': self.orchestration_config,
            'output_config': self.output_config,
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_temperature(self, task_type: str) -> float:
        """Get temperature for specific task type"""
        return self.temperature_config.get(task_type, 0.0)
    
    def get_directory(self, dir_type: str) -> Path:
        """Get path for specific directory type"""
        return self.directories.get(dir_type, self.project_root / 'data')
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration values"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._save_config()


# Global config instance
_config_instance = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance