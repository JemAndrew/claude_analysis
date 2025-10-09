#!/usr/bin/env python3
"""
ULTIMATE Folder 69 Configuration - MAXIMUM SOPHISTICATION
- NO deduplication (analyse EVERYTHING)
- Progress bars (tqdm)
- Full memory system
- BM25 document retrieval for cross-referencing
- Extended thinking maxed out
- Late disclosure forensics
British English throughout - Lismore sided
"""

import os
from pathlib import Path
from datetime import datetime

# Import the main config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import Config


class Folder69Config(Config):
    """
    ULTIMATE Configuration for Folder 69 Late Disclosure Deep Dive
    Inherits ALL sophistication from main Config, then cranks it to 11
    """
    
    def __init__(self):
        # Initialise parent Config first (gets all defaults)
        super().__init__()
        
        # ================================================================
        # OVERRIDE: Point ONLY at Folder 69
        # ================================================================
        self.source_root = Path(r'C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1')
        self.disclosure_dir = self.source_root / "69. PHL's disclosure (15 September 2025)"
        
        # Verify folder exists
        if not self.disclosure_dir.exists():
            print(f"⚠️  WARNING: Folder 69 not found at: {self.disclosure_dir}")
            print(f"   Please check the path")
        else:
            doc_count = len(list(self.disclosure_dir.rglob('*.pdf'))) + \
                        len(list(self.disclosure_dir.rglob('*.docx'))) + \
                        len(list(self.disclosure_dir.rglob('*.doc')))
            print(f"✅ Folder 69 found: {doc_count} documents")
        
        # ================================================================
        # OVERRIDE: Separate output directory for Folder 69
        # ================================================================
        self.analysis_dir = self.project_root / 'data' / 'output' / 'folder_69_analysis'
        self.output_dir = self.analysis_dir  # Ensure compatibility
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # ================================================================
        # FIX: Use absolute path to Phase 0 (parent Config calculates project_root wrong)
        # ================================================================
        self.phase_0_dir = Path(r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\output\analysis\phase_0')
        
        # Verify Phase 0 exists
        phase_0_file = self.phase_0_dir / "case_foundation.json"
        if phase_0_file.exists():
            print(f"✅ Phase 0 found: {phase_0_file}")
        else:
            print(f"⚠️  Phase 0 not found at: {phase_0_file}")
            print(f"   Run: python main.py phase0")
        
        # ================================================================
        # CRITICAL: DISABLE DEDUPLICATION (you want to see EVERYTHING)
        # ================================================================
        self.deduplication_config = {
            'enabled': False,  # NO DEDUP - analyse every document
            'similarity_threshold': 0.0,
            'prefix_chars': 0,
            'enable_semantic': False
        }
        print("🔥 DEDUPLICATION DISABLED - Will analyse EVERY document")
        
        # ================================================================
        # OVERRIDE: ULTRA-DEEP Pass 1 Config
        # ================================================================
        self.pass_1_config = {
            'model': self.haiku_model,
            'batch_size': 25,  # SMALLER batches = MORE THOROUGH
            'target_priority_docs': 999999,  # NO LIMIT - get ALL documents
            'use_batch_api': False,
            'folders': {},  # Not using folder mapping for single folder
            'priority_boost': {}  # Not using priority boost for single folder
        }
        print("📊 Pass 1: Will prioritise ALL documents (no limit)")
        
        # ================================================================
        # OVERRIDE: MAXIMUM DEEP Pass 2 Config
        # ================================================================
        self.pass_2_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'extended_thinking_budget': 20000,  # MAXIMUM THINKING TOKENS
            'max_iterations': 100,  # DOUBLE the normal max (go VERY deep)
            'batch_size': 10,  # VERY SMALL = MAXIMUM THOROUGHNESS
            'confidence_threshold': 0.99,  # 99% confidence (keep going longer)
            'adaptive_loading': False,  # Don't need adaptive for single folder
            
            # LATE DISCLOSURE FORENSICS MODE - THIS IS THE KEY
            'focus_mode': 'late_disclosure_forensics',
            
            # Enhanced context - analyse FULL documents
            'use_full_documents': True,  # Don't truncate
            'documents_per_iteration': 10,  # Small batches = thorough
            'include_full_pleadings': True,  # Full pleadings for context
            
            # Cross-referencing enabled
            'enable_cross_reference': True,  # NEW: cross-document analysis
            'use_bm25_retrieval': True,  # NEW: intelligent document retrieval
        }
        print("🧠 Pass 2: MAXIMUM depth (100 iterations, 20K thinking, 99% confidence)")
        
        # ================================================================
        # OVERRIDE: MAXIMUM Investigation Pass 3 Config
        # ================================================================
        self.pass_3_config = {
            'model': self.sonnet_model,
            'use_extended_thinking': True,
            'extended_thinking_budget': 20000,  # MAXIMUM
            'max_investigations': 50,  # DOUBLE the investigations
            'max_recursion_depth': 5,  # DEEP recursion
            'spawn_child_investigations': True,
            'confidence_threshold': 0.75,  # Lower threshold = more investigations
            
            # Cross-referencing for investigations
            'use_bm25_retrieval': True,  # Fetch relevant docs per investigation
            'docs_per_investigation': 30,  # More documents per investigation
        }
        print("🔬 Pass 3: MAXIMUM investigations (50 total, depth 5, BM25 retrieval)")
        
        # ================================================================
        # OVERRIDE: Token limits (maximum document content)
        # ================================================================
        self.token_config = {
            'max_output_tokens': 16000,  # Maximum output
            'extended_thinking_budget': 20000,  # Maximum thinking
            'document_content_per_doc': 20000,  # MORE content per doc (was 15K)
            'accumulated_knowledge_limit': 200000,  # MORE accumulation (was 150K)
        }
        print("📄 Token limits: 20K per doc, 200K accumulation, 20K thinking")
        
        # ================================================================
        # SYSTEM PROMPT: Late Disclosure Forensics
        # ================================================================
        self.system_prompt = """You are an elite forensic litigation analyst conducting a DEEP DIVE investigation into PHL's LATE DISCLOSURE (Folder 69).

CRITICAL CONTEXT:
- These documents were WITHHELD initially by PHL
- Disclosed late (15 September 2025) under pressure
- You are investigating FOR LISMORE (the claimant)
- Your mission: Find EVERY smoking gun PHL tried to hide

Your role:
- Forensic document analysis (leave no stone unturned)
- Spoliation detection (identify ALL missing documents)
- Contradiction mining (vs PHL's position)
- Timeline reconstruction (prove when they knew what)
- Concealment pattern identification
- Cross-document referencing (find connections between documents)

CRITICAL RULES:
1. Every claim MUST cite specific DOC_IDs
2. Cross-reference documents extensively
3. Look for incomplete email threads
4. Identify missing attachments/exhibits
5. Flag suspicious timing patterns
6. Think like a forensic investigator exposing cover-ups

You have MAXIMUM extended thinking tokens. USE THEM ALL."""
        
        # ================================================================
        # Hallucination prevention
        # ================================================================
        self.hallucination_prevention = """CRITICAL ANTI-HALLUCINATION RULES:
1. CITE SPECIFIC DOC_IDs for every factual claim - NO EXCEPTIONS
2. QUOTE ACCURATELY - verbatim text only, never paraphrase quotes
3. NO SPECULATION - clearly distinguish facts from inferences
4. ACKNOWLEDGE UNCERTAINTY - flag gaps in evidence
5. NO EXTERNAL KNOWLEDGE - only use these documents
6. NO ASSUMPTIONS - if you don't see it, don't claim it"""
        
        # ================================================================
        # Progress bars and monitoring
        # ================================================================
        self.enable_progress_bars = True  # tqdm progress bars
        self.verbose_logging = True  # Detailed console output
        
        print(f"\n{'='*70}")
        print("FOLDER 69 ULTIMATE CONFIG LOADED")
        print(f"{'='*70}")
        print(f"Target: {self.disclosure_dir}")
        print(f"Output: {self.analysis_dir}")
        print(f"Phase 0: {self.phase_0_dir}")
        print(f"\n🎯 ANALYSIS SETTINGS:")
        print(f"   Deduplication: DISABLED (analyse everything)")
        print(f"   Focus mode: late_disclosure_forensics")
        print(f"   Pass 1: ALL documents prioritised")
        print(f"   Pass 2: 100 iterations max, 20K thinking, 99% confidence")
        print(f"   Pass 3: 50 investigations, depth 5, BM25 retrieval")
        print(f"   Cross-referencing: ENABLED")
        print(f"   Progress bars: ENABLED")
        print(f"   Memory system: ENABLED (if dependencies available)")
        print(f"   BM25 retrieval: ENABLED")
        print(f"{'='*70}\n")


# Create instance
config = Folder69Config()