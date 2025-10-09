#!/usr/bin/env python3
"""
Dedicated Config for Folder 69 Late Disclosure Deep Dive
British English throughout
"""

from pathlib import Path
from datetime import datetime

class Folder69Config:
    """Configuration for targeted Folder 69 analysis"""
    
    def __init__(self):
        # Project root
        self.project_root = Path(__file__).parent.parent.parent
        
        # API
        self.anthropic_api_key = None  # Load from env
        
        # CRITICAL: Point ONLY at Folder 69
        self.source_root = Path(r'C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1')
        self.disclosure_dir = self.source_root / '69. PHL disclosure (15 September 2025)'
        
        # Separate output directory for Folder 69
        self.analysis_dir = self.project_root / 'data' / 'output' / 'folder_69_analysis'
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Use existing Phase 0 knowledge
        self.phase_0_dir = self.project_root / 'data' / 'output' / 'analysis' / 'phase_0'
        
        # Models
        self.haiku_model = 'claude-haiku-4-20250514'
        self.sonnet_model = 'claude-sonnet-4.5-20250514'
        
        # ULTRA-DEEP Pass 1 Config
        self.pass_1_config = {
            'model': self.haiku_model,
            'batch_size': 50,  # Smaller batches = more thorough
            'target_priority_docs': 200,  # Get top 200 from Folder 69
        }
        
        # ULTRA-DEEP Pass 2 Config
        self.pass_2_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'extended_thinking_budget': 20000,  # MAXIMUM
            'max_iterations': 50,  # GO VERY DEEP
            'batch_size': 15,  # SMALLER = MORE THOROUGH
            'confidence_threshold': 0.98,  # KEEP GOING LONGER
            
            # Late disclosure focus
            'focus_mode': 'late_disclosure_forensics',
        }
        
        # Pass 3 Config - Targeted investigations
        self.pass_3_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'extended_thinking_budget': 20000,
            'max_investigations': 25,  # Deep dive on findings
            'max_recursion_depth': 4,
        }
        
        # Token limits
        self.token_config = {
            'max_output_tokens': 16000,
            'extended_thinking_budget': 20000,
            'document_content_per_doc': 15000,
            'accumulated_knowledge_limit': 150000,
        }
        
        # System prompt
        self.system_prompt = """You are an expert forensic litigation analyst investigating PHL's LATE DISCLOSURE (Folder 69).

CRITICAL CONTEXT:
- These documents were WITHHELD initially by PHL
- Disclosed late (April 2025) under pressure
- You are investigating FOR LISMORE (the claimant)
- Your mission: Find smoking guns PHL tried to hide

Your role:
- Forensic document analysis
- Spoliation detection (missing documents)
- Contradiction mining (vs PHL's position)
- Timeline reconstruction
- Concealment pattern identification

CRITICAL: Every claim must cite specific DOC_IDs.
Think like a forensic investigator exposing cover-ups."""
        
        # Hallucination prevention
        self.hallucination_prevention = """CRITICAL RULES:
1. CITE SPECIFIC DOC_IDs for every factual claim
2. QUOTE ACCURATELY - verbatim only
3. NO SPECULATION - distinguish facts from inferences
4. ACKNOWLEDGE UNCERTAINTY - flag gaps
5. NO EXTERNAL KNOWLEDGE - only these documents"""

# Create instance
config = Folder69Config()