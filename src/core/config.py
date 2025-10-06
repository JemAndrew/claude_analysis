#!/usr/bin/env python3
"""
Enhanced Configuration with Increased Context Utilisation
British English throughout - Lismore v Process Holdings
"""

from pathlib import Path
from typing import Dict, List
from core.folder_mapping import FolderMapping


class Config:
    """System configuration with enhanced context limits"""
    
    def __init__(self):
        # Project paths
        self.project_root = Path(__file__).parent.parent
        self.source_root = self.project_root / "data" / "LIS1.1"
        self.output_dir = self.project_root / "data" / "output"
        self.analysis_dir = self.output_dir / "analysis"
        
        # API Configuration
        self.api_config = {
            'api_key': None,  # Set via environment variable
            'max_retries': 3,
            'retry_delay': 2,
            'rate_limit_delay': 1,
            'timeout': 300
        }
        
        # Model Configuration
        self.haiku_model = "claude-haiku-4-20250514"
        self.sonnet_model = "claude-sonnet-4.5-20250929"
        self.opus_model = "claude-opus-4-20250514"
        
        # Token Configuration - ENHANCED
        self.token_config = {
            'max_context_tokens': 200000,      # Claude's full capacity
            'max_output_tokens': 16000,        # Increased for detailed outputs
            'context_buffer': 10000,           # Safety margin
            'extended_thinking_budget': 100000, # INCREASED from 20K
            
            # Context utilisation per component - ENHANCED
            'accumulated_knowledge_limit': 150000,  # Up from 20K
            'document_content_per_doc': 15000,      # Up from 3K
            'pleadings_full_limit': 80000,          # Full pleadings
            'intelligence_context_limit': 100000     # Full intelligence
        }
        
        # Caching Configuration - ENHANCED
        self.caching_config = {
            'enabled': True,
            'min_tokens_to_cache': 1024,
            'cache_ttl_seconds': 300,
            
            # What to cache (static content only)
            'cache_static_only': True,
            'cache_pleadings': True,        # NEW
            'cache_legal_framework': True,  # NEW
            'cache_system_prompt': True
        }
        
        # Hallucination Prevention
        self.hallucination_prevention = """You are analysing real litigation documents for Lismore v Process Holdings arbitration.

CRITICAL INSTRUCTIONS:
- Only state facts that documents prove
- Cite specific document IDs for every claim
- If uncertain, say "needs investigation"
- Don't make assumptions beyond evidence
- Don't import theories from external sources"""
        
        # System Prompt - ENHANCED
        self.system_prompt = """You are an expert litigation analyst and strategic counsel for Lismore in their arbitration against Process Holdings.

Your role:
- Analyse disclosure documents with extreme rigour
- Build evidence-based legal arguments
- Identify opponent weaknesses
- Generate novel strategic arguments
- Produce tribunal-ready work product

You have access to extended thinking - use it extensively for:
- Complex legal reasoning
- Multi-document pattern analysis
- Strategic argument construction
- Evidence chain analysis

CRITICAL: Every factual claim must cite specific document IDs."""
        
        # Folder mapping
        self.folder_mapping = FolderMapping
        
        # Pass 1: Triage Configuration
        self.pass_1_config = {
            'model': self.haiku_model,
            'batch_size': 100,
            'use_batch_api': False,  # Set to True for 50% cost reduction
            'target_priority_docs': 500,
            'folders': self.folder_mapping.get_pass_1_folders(),
            'priority_boost': {
                10: 2.0,
                9: 1.5,
                8: 1.0,
                7: 0.5,
                6: 0.0,
                5: -0.3,
                4: -0.5,
                3: -0.8,
                2: -1.0
            }
        }
        
        # Pass 2: Deep Analysis Configuration - ENHANCED
        self.pass_2_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'extended_thinking_budget': 100000,  # INCREASED from 20K
            'max_iterations': 25,
            'batch_size': 30,
            'confidence_threshold': 0.95,
            'adaptive_loading': True,
            'adaptive_trigger_iteration': 15,
            'adaptive_confidence_threshold': 0.90,
            'adaptive_additional_docs': 100,
            
            # Enhanced context usage
            'use_full_documents': True,          # NEW
            'documents_per_iteration': 30,       # NEW
            'include_full_pleadings': True       # NEW
        }
        
        # Pass 3: Autonomous Investigations Configuration
        self.pass_3_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'extended_thinking_budget': 100000,  # INCREASED
            'max_investigations': 10,
            'max_recursion_depth': 5,
            'min_investigation_priority': 7
        }
        
        # Pass 4: Deliverables Configuration - ENHANCED
        self.pass_4_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': False,  # Templates don't need thinking
            'separate_deliverables': True,    # NEW - generate each separately
            'deliverables': [
                'scott_schedule',
                'witness_outlines',
                'skeleton_argument',
                'disclosure_requests',
                'opening_submissions',
                'expert_instructions'
            ]
        }
        
        # Quality Validation - NEW
        self.validation_config = {
            'enabled': True,
            'check_evidence_citations': True,
            'check_confidence_scores': True,
            'check_opponent_arguments': True,
            'check_document_ids': True,
            'min_evidence_per_breach': 1,
            'max_confidence_early_iteration': 0.80
        }
    
    def get_folder_path(self, folder_name: str) -> Path:
        """Get full path for a folder"""
        folder_path = self.source_root / folder_name
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        return folder_path
    
    def get_pass_1_folders(self) -> List[Path]:
        """Get all folders for Pass 1 triage"""
        folder_names = self.folder_mapping.get_pass_1_folders()
        folders = []
        
        for name in folder_names:
            try:
                folders.append(self.get_folder_path(name))
            except FileNotFoundError:
                print(f"Warning: Folder not found: {name}")
        
        return folders
    
    def get_pleadings_folders(self) -> List[Path]:
        """Get pleadings folders"""
        folder_names = self.folder_mapping.get_pleadings_folders()
        folders = []
        
        for name in folder_names:
            try:
                folders.append(self.get_folder_path(name))
            except FileNotFoundError:
                print(f"Warning: Pleadings folder not found: {name}")
        
        return folders
    
    def get_folder_priority(self, folder_path: Path) -> int:
        """Get priority tier for a folder (1-10)"""
        folder_name = folder_path.name
        return self.folder_mapping.get_priority(folder_name)
    
    def get_folder_category(self, folder_path: Path) -> str:
        """Get category for a folder"""
        folder_name = folder_path.name
        return self.folder_mapping.get_category(folder_name)
    
    def should_include_in_pass_1(self, folder_path: Path) -> bool:
        """Check if folder should be in Pass 1"""
        folder_name = folder_path.name
        return self.folder_mapping.should_include_in_pass_1(folder_name)
    
    def get_priority_boost(self, priority_tier: int) -> float:
        """Get priority boost for a tier"""
        return self.pass_1_config['priority_boost'].get(priority_tier, 0.0)
    
    def get_model_for_task(self, task_type: str, complexity: float) -> str:
        """Select appropriate model based on task and complexity"""
        
        if task_type in ['document_triage', 'metadata_scan']:
            return self.haiku_model
        
        if complexity > 0.7 or task_type in ['deep_analysis', 'investigation', 'synthesis']:
            return self.sonnet_model
        
        if complexity > 0.3:
            return self.sonnet_model
        
        return self.haiku_model
    
    def print_config(self):
        """Print configuration summary"""
        print("=" * 70)
        print("ENHANCED LITIGATION INTELLIGENCE SYSTEM - CONFIGURATION")
        print("=" * 70)
        
        print(f"\nSource folder: {self.source_root}")
        print(f"Output folder: {self.output_dir}")
        print(f"\nModels:")
        print(f"  Haiku: {self.haiku_model}")
        print(f"  Sonnet: {self.sonnet_model}")
        
        print(f"\nEnhanced Features:")
        print(f"  Context limit: {self.token_config['max_context_tokens']:,} tokens")
        print(f"  Extended thinking: {self.token_config['extended_thinking_budget']:,} tokens")
        print(f"  Document content per doc: {self.token_config['document_content_per_doc']:,} chars")
        print(f"  Accumulated knowledge limit: {self.token_config['accumulated_knowledge_limit']:,} tokens")
        
        print(f"\nPass Configuration:")
        print(f"  Pass 1 folders: {len(self.get_pass_1_folders())}")
        print(f"  Pass 2 max iterations: {self.pass_2_config['max_iterations']}")
        print(f"  Pass 3 max investigations: {self.pass_3_config['max_investigations']}")
        print(f"  Pass 4 separate deliverables: {self.pass_4_config['separate_deliverables']}")
        
        print(f"\nQuality Controls:")
        print(f"  Validation enabled: {self.validation_config['enabled']}")
        print(f"  Check evidence citations: {self.validation_config['check_evidence_citations']}")
        
        print("=" * 70)


if __name__ == "__main__":
    config = Config()
    config.print_config()