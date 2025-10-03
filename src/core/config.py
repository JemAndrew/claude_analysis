#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Optimised for maximum Claude capability - Lismore v Process Holdings
British English throughout
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
        self._setup_tiered_analysis()
        self._setup_api_config()
    
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
        """Model selection for maximum reasoning"""
        self.models = {
            'primary': 'claude-sonnet-4-20250514',
            'secondary': 'claude-haiku-4-20250605',
            'opus': 'claude-opus-4-20250514'
        }
        
        self.task_models = {
            'knowledge_synthesis': 'primary',
            'investigation': 'primary',
            'pattern_recognition': 'primary',
            'contradiction_analysis': 'primary',
            'metadata_extraction': 'secondary',
            'synthesis': 'primary',
            'timeline_analysis': 'primary',
            'financial_analysis': 'primary',
            'entity_mapping': 'primary'
        }
    
    def _setup_analysis(self) -> None:
        """Analysis configuration"""
        # Token management
        self.token_config = {
            'max_input_tokens': 200000,
            'max_output_tokens': 16000,
            'buffer_tokens': 10000,
            'optimal_batch_size': 140000
        }
        
        # Batching strategy
        self.batch_strategy = {
            'phase_0_batch_size': 20,
            'tier_1_batch_size': 25,
            'tier_2_batch_size': 100,
            'tier_3_batch_size': 15,
            'max_retries': 5,
            'retry_delay': 5,
            'auto_adjust': True,
            'method': 'semantic_clustering',
            'max_batch_size': 140000,
            'overlap_tokens': 5000,
            'prioritise_by': 'relevance',
            'min_batch_size': 50000
        }
        
        # Phase configuration
        self.phases = {
            '0': {
                'name': 'Knowledge Foundation',
                'strategy': 'batched_synthesis',
                'priority': 'CRITICAL'
            },
            '1': {
                'name': 'Disclosure Analysis',
                'strategy': 'tiered_analysis',
                'priority': 'HIGH'
            },
            '2': {
                'name': 'Timeline Reconstruction',
                'strategy': 'temporal_forensics',
                'priority': 'HIGH'
            },
            '3': {
                'name': 'Contradiction Mining',
                'strategy': 'logic_analysis',
                'priority': 'CRITICAL'
            },
            '4': {
                'name': 'Pattern Recognition',
                'strategy': 'cross_document_patterns',
                'priority': 'HIGH'
            },
            '5': {
                'name': 'Entity Relationship Mapping',
                'strategy': 'network_analysis',
                'priority': 'MEDIUM'
            },
            '6': {
                'name': 'Financial Forensics',
                'strategy': 'financial_analysis',
                'priority': 'HIGH'
            },
            '7': {
                'name': 'Strategic Synthesis',
                'strategy': 'narrative_construction',
                'priority': 'CRITICAL'
            }
        }
        
        # Convergence detection
        self.convergence_config = {
            'min_iterations': 3,
            'confidence_threshold': 0.85,
            'discovery_rate_threshold': 0.1,
            'max_iterations': 10
        }
        
        # Recursion configuration
        self.recursion_config = {
            'self_questioning_depth': 5,
            'min_questioning_depth': 3,
            'investigation_iterations': 10,
            'convergence_threshold': 0.95,
            'force_deep_dive_on': ['CRITICAL', 'NUCLEAR', 'CONTRADICTION']
        }
        
        # Temperature settings
        self.temperature_config = {
            'exploration': 0.9,
            'analysis': 0.7,
            'synthesis': 0.5,
            'final_report': 0.3,
            'knowledge_synthesis': 0.4,
            'investigation': 0.7,
            'creative_investigation': 0.9,
            'hypothesis_generation': 0.8,
            'pattern_recognition': 0.6,
            'contradiction_analysis': 0.4
        }
    
    def _setup_investigation(self) -> None:
        """Investigation spawning configuration"""
        # Investigation triggers
        self.investigation_triggers = {
            'critical_discovery': {'threshold': 8.0, 'auto_spawn': True},
            'contradiction': {'threshold': 7.5, 'auto_spawn': True},
            'pattern': {'threshold': 0.8, 'auto_spawn': True},
            'timeline_impossibility': {'threshold': 9.0, 'auto_spawn': True},
            'financial_anomaly': {'threshold': 7.0, 'auto_spawn': True},
            'missing_document': {'threshold': 6.5, 'auto_spawn': True},
            'contradiction_severity': 7,
            'pattern_confidence': 0.8,
            'missing_document_pattern': True,
            'entity_suspicion': 0.7,
            'keyword_triggers': [
                'CRITICAL', 'NUCLEAR', 'INVESTIGATE',
                'SUSPICIOUS', 'ANOMALY', 'IMPOSSIBLE'
            ]
        }
        
        # Investigation priority scoring
        self.priority_weights = {
            'financial_impact': 3.0,
            'timeline_critical': 2.5,
            'contradiction': 2.0,
            'pattern_strength': 1.5,
            'entity_centrality': 1.5,
            'document_absence': 2.0
        }
        
        # Investigation depth settings
        self.investigation_depth = {
            'initial_sweep': 1,
            'standard_investigation': 3,
            'deep_investigation': 5,
            'exhaustive_investigation': 10,
            'parallel_threads': 5,
            'deep': 5
        }
    
    def _setup_tiered_analysis(self) -> None:
        """Tiered analysis configuration for Phase 1"""
        
        self.tiered_analysis = {
            'tier_1_deep': {
                'name': 'Deep Forensic Analysis',
                'description': 'Full senior litigator analysis of priority documents',
                'batch_size': 25,
                'analysis_depth': 'comprehensive',
                'prompts': 'investigation',
                'spawn_investigations': True,
                'model': 'primary'
            },
            'tier_2_metadata': {
                'name': 'Metadata Scan',
                'description': 'Lightweight scanning to flag suspicious documents',
                'batch_size': 100,
                'analysis_depth': 'metadata',
                'prompts': 'metadata_extraction',
                'spawn_investigations': False,
                'model': 'secondary'
            },
            'tier_3_targeted': {
                'name': 'Targeted Deep Dive',
                'description': 'Deep analysis of documents flagged in Tier 2',
                'batch_size': 15,
                'analysis_depth': 'investigation',
                'prompts': 'focused_investigation',
                'spawn_investigations': True,
                'model': 'primary'
            }
        }
        
        # Priority folders for Tier 1 deep analysis
        self.tier_1_priority_folders = [
            '55. Document Production',
            '57. First Respondent\'s Responses',
            '61. Witness Statements',
            '12. Brendan Cahill\'s witness statements',
            '33. Correspondence',
            '45. Objections to Production',
            '46. PH Objections',
            '48. Objections',
            '36. Chronological Email Run',
            '40. Witness Statements Index'
        ]
    
    def _setup_api_config(self) -> None:
        """API and rate limiting configuration"""
        
        self.api_config = {
            'api_key': os. getenv('ANTHROPIC_API_KEY'),
            'rate_limit_delay': 2,
            'max_retries': 5,
            'retry_delay': 5,
            'timeout': 300
        }
    
    # Entity categories for knowledge graph
    @property
    def base_entities(self) -> Dict[str, List[str]]:
        """Base entity types for Lismore case"""
        return {
            'people': [
                'director', 'adviser', 'witness', 'expert',
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
                'breach', 'duty', 'obligation', 'representation',
                'warranty', 'indemnity', 'limitation', 'causation',
                'loss', 'quantum', 'liability'
            ]
        }
    
    # Hallucination prevention
    @property
    def hallucination_prevention(self) -> str:
        """Core instructions to prevent hallucination"""
        return """
<critical_accuracy_requirements>
- NEVER invent facts not in documents
- NEVER assume document content
- NEVER create fictional quotes
- ALWAYS cite specific document references
- ALWAYS distinguish between: (1) Facts from documents, (2) Logical inferences, (3) Strategic hypotheses
- Mark confidence levels: CERTAIN (in document), PROBABLE (strong inference), POSSIBLE (hypothesis)
- When uncertain: State "Not found in reviewed documents" rather than speculating
</critical_accuracy_requirements>

<lismore_advocacy_stance>
WE ARE ARGUING FOR LISMORE. All analysis must:
- Interpret ambiguous evidence favourably to Lismore
- Identify Process Holdings' vulnerabilities aggressively
- Frame legal principles to support Lismore's position
- Find weaknesses in PH's arguments
- Strengthen Lismore's case wherever possible
- Think like Lismore's senior litigation counsel
</lismore_advocacy_stance>
"""


# Global config instance
config = Config()