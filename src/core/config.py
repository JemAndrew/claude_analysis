#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Optimised for maximum Claude capability - Lismore v Process Holdings
British English throughout
COMPLETE VERSION - Memory tiers enabled
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# CRITICAL: Load environment variables from root .env
from dotenv import load_dotenv
load_dotenv(override=True)


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
        self._setup_memory_tiers()  # NEW
    
    def _setup_paths(self) -> None:
        """Define organised folder structure - UPDATED FOR LIS1.1"""
        
        # Root input directory
        self.input_dir = self.root / "data" 
        
        # ================================================================
        # ORGANISED FOLDER HIERARCHY (matches organisation script)
        # ================================================================
        
        # 1. Legal Knowledge - Foundation & Context
        self.legal_knowledge_dir = self.input_dir / "1_LEGAL_KNOWLEDGE"
        
        # 2. Case Pleadings - Parties' Legal Arguments  
        self.case_pleadings_dir = self.input_dir / "2_CASE_PLEADINGS"
        
        # 3. Witness Evidence - Witness Statements
        self.witness_evidence_dir = self.input_dir / "3_WITNESS_EVIDENCE"
        
        # 4. Disclosure - RAW EVIDENCE (HIGHEST PRIORITY)
        self.disclosure_dir = self.input_dir / "4_DISCLOSURE"
        
        # 5. Tribunal Orders - Procedural Rulings
        self.tribunal_orders_dir = self.input_dir / "5_TRIBUNAL_ORDERS"
        
        # 6. Correspondence - Emails & Letters
        self.correspondence_dir = self.input_dir / "6_CORRESPONDENCE"
        
        # 7. Disclosure Disputes - Shows What's Missing
        self.disclosure_disputes_dir = self.input_dir / "7_DISCLOSURE_DISPUTES"
        
        # 8. Procedural Low Priority - Admin Documents
        self.procedural_dir = self.input_dir / "8_PROCEDURAL_LOW_PRIORITY"
        
        # 9. Expert Instructions - Future Expert Evidence
        self.expert_instructions_dir = self.input_dir / "9_EXPERT_INSTRUCTIONS"
        
        # ================================================================
        # BACKWARD COMPATIBILITY ALIASES
        # ================================================================
        # (Keep old code working while we transition)
        
        self.case_context_dir = self.case_pleadings_dir  # Old name
        self.case_documents_dir = self.case_pleadings_dir  # Old name
        
        # ================================================================
        # PASS-SPECIFIC CONFIGURATIONS
        # ================================================================
        
        # Pass 0: Foundation building sources
        self.pass_0_sources = [
            self.legal_knowledge_dir,      # Legal context & rules
            self.case_pleadings_dir        # Parties' positions
        ]
        
        # Pass 1: Primary target (where smoking guns hide)
        self.pass_1_primary_target = self.disclosure_dir / "respondent_production"
        
        # Pass 1: Secondary targets (supporting evidence)
        self.pass_1_secondary_targets = [
            self.disclosure_dir / "claimant_production",  # Our disclosure
            self.witness_evidence_dir,                     # Witness statements
            self.correspondence_dir,                       # Email chains
            self.disclosure_disputes_dir                   # Shows what's missing!
        ]
        
        # Pass 1: Excluded folders (don't waste tokens)
        self.pass_1_exclude = [
            self.procedural_dir,           # Transcripts, bundles (low value)
            self.tribunal_orders_dir       # Reference only
        ]
        
        # ================================================================
        # KNOWLEDGE MANAGEMENT PATHS
        # ================================================================
        
        self.knowledge_dir = self.root / "data" / "knowledge"
        self.graph_db_path = self.knowledge_dir / "graph.db"
        self.backups_dir = self.knowledge_dir / "backups"
        self.investigations_db_path = self.knowledge_dir / "investigations.db"
        
        # ================================================================
        # OUTPUT PATHS
        # ================================================================
        
        self.output_dir = self.root / "data" / "output"
        self.analysis_dir = self.output_dir / "analysis"
        self.investigations_dir = self.output_dir / "investigations"
        self.reports_dir = self.output_dir / "reports"
        
        # ================================================================
        # CREATE ALL DIRECTORIES
        # ================================================================
        
        for dir_path in [
            # Input directories
            self.input_dir,
            self.legal_knowledge_dir,
            self.case_pleadings_dir,
            self.witness_evidence_dir,
            self.disclosure_dir,
            self.tribunal_orders_dir,
            self.correspondence_dir,
            self.disclosure_disputes_dir,
            self.procedural_dir,
            self.expert_instructions_dir,
            # Knowledge management
            self.knowledge_dir,
            self.backups_dir,
            # Output directories
            self.output_dir,
            self.analysis_dir,
            self.investigations_dir,
            self.reports_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


    def _setup_models(self) -> None:
        """Model selection for maximum reasoning"""
        self.models = {
            'primary': 'claude-sonnet-4-5-20250929',  # Latest Sonnet 4.5
            'secondary': 'claude-haiku-4-20250605',   # Haiku 4 for speed
            'opus': 'claude-opus-4-20250514'          # Opus 4 if needed
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
        
        # Prompt caching configuration
        self.caching_config = {
            'enabled': True,
            'min_tokens_to_cache': 1024,
            'ttl_seconds': 300
        }
        
        # Batching strategy
        self.batch_strategy = {
            'phase_0_batch_size': 20,
            'tier_1_batch_size': 25,
            'tier_2_batch_size': 100,
            'tier_3_batch_size': 15,
            'max_retries': 5,
            'retry_delay': 5,
            'auto_adjust': True
        }
        
        # Hallucination prevention
        self.hallucination_prevention = """
CRITICAL INSTRUCTIONS:
- Base all findings ONLY on documents provided
- Never fabricate document references
- Mark inferences clearly with [INFERENCE]
- Cite all factual claims with [DOC_ID: Location]
- If uncertain, state "Insufficient evidence to determine"
"""
    
    def _setup_investigation(self) -> None:
        """Investigation spawning configuration"""
        self.investigation_config = {
            'max_depth': 3,
            'priority_threshold': 7.0,
            'auto_spawn_enabled': True,
            'convergence_threshold': 0.95,
            'max_concurrent': 5,
            'discovery_types': [
                'NUCLEAR',      # Case-ending discovery
                'CRITICAL',     # Major strategic advantage
                'PATTERN',      # Significant pattern
                'CONTRADICTION', # Contradiction detected
                'TIMELINE',     # Timeline impossibility
                'MISSING'       # Evidence of withholding
            ]
        }
    
    def _setup_tiered_analysis(self) -> None:
        """Three-tier analysis configuration for Phase 1"""
        self.tier_config = {
            'tier_1': {
                'name': 'Deep Analysis',
                'doc_limit': 500,
                'batch_size': 25,
                'analysis_depth': 'deep',
                'model': 'primary',
                'priority_folders': [
                    'Document Production',
                    'Witness Statements',
                    'Expert Reports',
                    'Correspondence',
                    'Contracts'
                ]
            },
            'tier_2': {
                'name': 'Metadata Scan',
                'doc_limit': None,  # All remaining
                'batch_size': 100,
                'analysis_depth': 'shallow',
                'model': 'secondary',
                'flag_threshold': 7.0
            },
            'tier_3': {
                'name': 'Targeted Deep Dive',
                'batch_size': 15,
                'analysis_depth': 'deep',
                'model': 'primary'
            }
        }
    
    def _setup_api_config(self) -> None:
        """API configuration"""
        self.api_config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'rate_limit_delay': 3,
            'max_retries': 3,
            'timeout': 300,
            'default_model': self.models['primary']
        }
        
        # Validate API key
        if not self.api_config['api_key']:
            print("WARNING: ANTHROPIC_API_KEY not found in environment")
    
    def _setup_memory_tiers(self) -> None:
        """
        NEW: Memory tier configuration
        Enables hierarchical memory system
        """
        # Enable/disable memory tiers
        self.enable_vector_store = True   # Tier 2: Semantic search across all docs
        self.enable_cold_storage = True   # Tier 4: Encrypted vault for security
        self.enable_analysis_cache = True # Tier 5: Cache Claude responses
        
        # Vector store configuration (Tier 2)
        self.vector_config = {
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'collection_name': 'lismore_disclosure',
            'distance_metric': 'cosine'
        }
        
        # Cold storage configuration (Tier 4)
        self.cold_storage_config = {
            'encryption_enabled': True,
            'auto_encrypt_pdfs': True,
            'audit_trail': True
        }
        
        # Analysis cache configuration (Tier 5)
        self.cache_config = {
            'default_ttl_days': 30,
            'max_cache_size_mb': 1000,
            'auto_cleanup': True
        }
    
    def get_model_for_task(self, task_type: str) -> str:
        """Get appropriate model for task"""
        model_key = self.task_models.get(task_type, 'primary')
        return self.models[model_key]
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check API key
        if not self.api_config['api_key']:
            issues.append("ANTHROPIC_API_KEY not configured")
        
        # Check required directories
        if not self.legal_knowledge_dir.exists():
            issues.append(f"Legal knowledge directory missing: {self.legal_knowledge_dir}")
        
        if not self.case_context_dir.exists():
            issues.append(f"Case context directory missing: {self.case_context_dir}")
        
        if not self.disclosure_dir.exists():
            issues.append(f"Disclosure directory missing: {self.disclosure_dir}")
        
        return issues