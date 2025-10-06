#!/usr/bin/env python3
"""
Configuration for Lismore Litigation Intelligence System
Updated to use direct path access (no file copying needed)
British English throughout
"""

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Import folder mapping
from .folder_mapping import FolderMapping


class Config:
    """System configuration"""
    
    def __init__(self):
        """Initialise configuration"""
        
        # Load environment variables
        load_dotenv()
        
        # API Configuration
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Model Configuration
        self.haiku_model = "claude-3-5-haiku-20241022"
        self.sonnet_model = "claude-sonnet-4-20250514"
        
        # Cost Configuration (per million tokens)
        self.haiku_cost_input = 1.00    # £1 per 1M input tokens
        self.haiku_cost_output = 5.00   # £5 per 1M output tokens
        self.sonnet_cost_input = 3.00   # £3 per 1M input tokens
        self.sonnet_cost_output = 15.00 # £15 per 1M output tokens
        
        # Directory Configuration - DIRECT PATH ACCESS
        self._setup_paths()
        
        # Pass Configuration
        self._setup_pass_config()
        
        # Memory Configuration
        self._setup_memory_config()
        
        # Folder Mapping Reference
        self.folder_mapping = FolderMapping
    
    def _setup_paths(self):
        """Set up directory paths - points directly at LIS1.1"""
        
        # Root directory (claude_analysis-master)
        self.root_dir = Path(__file__).parent.parent.parent
        
        # SOURCE: LIS1.1 folder (where files actually are)
        self.source_root = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1")
        
        if not self.source_root.exists():
            raise FileNotFoundError(f"Source folder not found: {self.source_root}")
        
        # Output directories (for system-generated files)
        self.output_dir = self.root_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # System data directories (NOT source documents)
        self.data_dir = self.root_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Vector store and knowledge graph
        self.vector_store_dir = self.data_dir / "vector_store"
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_graph_db = self.data_dir / "knowledge_graph.db"
        
        # Cache directory
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Logs
        self.logs_dir = self.root_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_pass_config(self):
        """Configure pass-specific settings"""
        
        # Pass 1: Triage Configuration
        self.pass_1_config = {
            'model': self.haiku_model,
            'top_n_documents': 500,  # Select top 500 for deep analysis
            'preview_chars': 300,    # Characters to preview per document
            'batch_size': 100,       # Documents to process per batch
            'include_folders': FolderMapping.get_pass_1_folders(),  # Only folders marked for Pass 1
            'priority_boost': {
                10: 2.0,  # Disclosure gets +2.0 boost
                9: 1.5,   # Witness evidence gets +1.5
                8: 1.0,   # High priority gets +1.0
                7: 0.5,   # Medium-high gets +0.5
                6: 0.0,   # Medium gets no boost
                5: -0.3,  # Low gets penalty
                4: -0.5,  # Very low gets penalty
                3: -0.8,  # Skip tier gets penalty
                2: -1.0   # Really skip tier gets penalty
            }
        }
        
        # Pass 2: Deep Analysis Configuration
        self.pass_2_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'max_iterations': 25,
            'batch_size': 30,  # Documents per iteration
            'confidence_threshold': 0.95,
            'adaptive_loading': True,  # Load more docs if confidence low
            'adaptive_trigger_iteration': 15,  # Check confidence at iteration 15
            'adaptive_confidence_threshold': 0.90,  # If below this, load more
            'adaptive_additional_docs': 100,  # Load 100 more (docs 501-600)
        }
        
        # Pass 3: Autonomous Investigations Configuration
        self.pass_3_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'max_investigations': 10,
            'max_recursion_depth': 5,
            'min_investigation_priority': 7,  # Only investigate high-priority topics
        }
        
        # Pass 4: Deliverables Configuration
        self.pass_4_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': False,  # Faster for document generation
            'deliverables': [
                'scott_schedule',
                'opening_submissions',
                'witness_outlines',
                'cross_examination_outlines',
                'disclosure_requests',
                'skeleton_argument',
                'expert_instructions'
            ]
        }
    
    def _setup_memory_config(self):
        """Configure memory system"""
        
        self.memory_config = {
            # Vector Store Configuration
            'vector_store': {
                'collection_name': 'lismore_documents',
                'embedding_function': 'sentence-transformers',
                'chunk_size': 1000,
                'chunk_overlap': 200,
            },
            
            # Knowledge Graph Configuration
            'knowledge_graph': {
                'entity_types': [
                    'person', 'company', 'document', 'contract',
                    'transaction', 'meeting', 'email', 'financial_record'
                ],
                'relationship_types': [
                    'sent_email_to', 'attended_meeting', 'signed_contract',
                    'contradicts', 'supports', 'references', 'part_of'
                ]
            },
            
            # Cache Configuration
            'cache': {
                'ttl_seconds': 86400,  # 24 hours
                'max_size_mb': 1000,   # 1GB cache limit
            }
        }
    
    def get_folder_path(self, folder_name: str) -> Path:
        """
        Get full path to a source folder using fuzzy matching
        
        Args:
            folder_name: Name of LIS folder (e.g., "55. Document Production")
            
        Returns:
            Full path to folder
        """
        # Try exact match first
        folder_path = self.source_root / folder_name
        if folder_path.exists():
            return folder_path
        
        # Fuzzy match: try to find folder that starts with the same number/prefix
        # Extract number prefix (e.g., "29-" or "50.")
        import re
        match = re.match(r'^(\d+[-\.])\s*', folder_name)
        if match:
            prefix = match.group(1)
            # Find any folder starting with this prefix
            for folder in self.source_root.iterdir():
                if folder.is_dir() and folder.name.startswith(prefix):
                    return folder
        
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    def get_all_folders(self) -> List[Path]:
        """Get all LIS1.1 folders"""
        return [f for f in self.source_root.iterdir() if f.is_dir()]
    
    def get_pass_1_folders(self) -> List[Path]:
        """Get folders to include in Pass 1 triage"""
        folder_names = self.pass_1_config['include_folders']
        folders = []
        
        for name in folder_names:
            try:
                folders.append(self.get_folder_path(name))
            except FileNotFoundError:
                print(f"Warning: Pass 1 folder not found: {name}")
        
        return folders
    
    def get_disclosure_folders(self) -> List[Path]:
        """Get all disclosure folders (Priority 10)"""
        folder_names = FolderMapping.get_disclosure_folders()
        folders = []
        
        for name in folder_names:
            try:
                folders.append(self.get_folder_path(name))
            except FileNotFoundError:
                print(f"Warning: Disclosure folder not found: {name}")
        
        return folders
    
    def get_pleadings_folders(self) -> List[Path]:
        """Get all pleading folders"""
        folder_names = FolderMapping.get_pleadings_folders()
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
        return FolderMapping.get_priority(folder_name)
    
    def get_folder_category(self, folder_path: Path) -> str:
        """Get category for a folder"""
        folder_name = folder_path.name
        return FolderMapping.get_category(folder_name)
    
    def should_include_in_pass_1(self, folder_path: Path) -> bool:
        """Check if folder should be in Pass 1"""
        folder_name = folder_path.name
        return FolderMapping.should_include_in_pass_1(folder_name)
    
    def get_priority_boost(self, priority_tier: int) -> float:
        """Get priority boost for a tier"""
        return self.pass_1_config['priority_boost'].get(priority_tier, 0.0)
    
    def print_config(self):
        """Print configuration summary"""
        print("=" * 70)
        print("LISMORE LITIGATION INTELLIGENCE SYSTEM - CONFIGURATION")
        print("=" * 70)
        
        print(f"\nSource folder: {self.source_root}")
        print(f"Output folder: {self.output_dir}")
        print(f"Data folder: {self.data_dir}")
        
        print(f"\nModels:")
        print(f"  Haiku (Pass 1): {self.haiku_model}")
        print(f"  Sonnet (Pass 2-4): {self.sonnet_model}")
        
        print(f"\nPass 1 Configuration:")
        print(f"  Folders to triage: {len(self.pass_1_config['include_folders'])}")
        print(f"  Top documents to select: {self.pass_1_config['top_n_documents']}")
        
        print(f"\nPass 2 Configuration:")
        print(f"  Max iterations: {self.pass_2_config['max_iterations']}")
        print(f"  Batch size: {self.pass_2_config['batch_size']}")
        print(f"  Confidence threshold: {self.pass_2_config['confidence_threshold']}")
        print(f"  Adaptive loading: {self.pass_2_config['adaptive_loading']}")
        
        print(f"\nFolder Mapping:")
        print(f"  Total folders mapped: {len(FolderMapping.FOLDER_MAP)}")
        
        # Count available folders
        available = len([f for f in self.get_all_folders()])
        print(f"  Folders found in source: {available}")
        
        print("=" * 70)


if __name__ == "__main__":
    # Test configuration
    config = Config()
    config.print_config()
    
    print("\nPass 1 folders:")
    for folder in config.get_pass_1_folders():
        priority = config.get_folder_priority(folder)
        category = config.get_folder_category(folder)
        boost = config.get_priority_boost(priority)
        print(f"  [{priority}] {folder.name} ({category}, boost: {boost:+.1f})")