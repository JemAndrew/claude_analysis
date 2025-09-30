#!/usr/bin/env python3
"""
Configuration for Litigation Intelligence System
Simplified for maximum Claude autonomy
"""

import os
from pathlib import Path
from typing import Dict, List


class Config:
    """Central configuration"""
    
    def __init__(self, root_path: str = None):
        self.root = Path(root_path) if root_path else Path.cwd()
        self._setup_paths()
        self._setup_models()
        self._setup_analysis()
    
    def _setup_paths(self) -> None:
        """Simple folder structure"""
        # Input
        self.input_dir = self.root / "data" / "input"
        self.legal_knowledge_dir = self.input_dir / "legal_knowledge"
        self.case_documents_dir = self.input_dir / "case_documents"
        
        # Knowledge
        self.knowledge_dir = self.root / "data" / "knowledge"
        self.graph_db_path = self.knowledge_dir / "graph.db"
        self.backups_dir = self.knowledge_dir / "backups"
        
        # Output
        self.output_dir = self.root / "data" / "output"
        self.reports_dir = self.output_dir / "reports"
        
        # Create all
        for dir_path in [
            self.input_dir, self.legal_knowledge_dir, self.case_documents_dir,
            self.knowledge_dir, self.backups_dir, self.output_dir, self.reports_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_models(self) -> None:
        """Model configuration"""
        self.models = {
            'primary': 'claude-3-opus-latest',
            'secondary': 'claude-3-5-sonnet-latest',
            'quick': 'claude-3-haiku-latest'
        }
    
    def _setup_analysis(self) -> None:
        """Analysis configuration"""
        self.token_config = {
            'max_input_tokens': 150000,
            'max_output_tokens': 4096,
            'buffer_tokens': 10000,
            'optimal_batch_size': 140000
        }
        
        self.api_config = {
            'max_requests_per_minute': 20,
            'rate_limit_delay': 3,
            'retry_attempts': 3,
            'retry_delay': 5
        }
        
        self.recursion_config = {
            'self_questioning_depth': 5,
            'max_investigation_depth': 10
        }

# Global config
config = Config()