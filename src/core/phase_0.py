#!/usr/bin/env python3
"""
Phase 0: Deep Case Understanding & Knowledge Base Construction
ULTIMATE SMART FILTERING - Maximum efficiency, minimum noise
British English throughout - Acting for Lismore (Claimant)

Location: src/core/phase_0.py

🛡️ Multi-Layer Protection System:
1. Skip drafts/working copies/temp files
2. Prioritise master/final/signed versions (load best first)
3. Cap per folder (max 30 docs per folder)
4. Stricter deduplication (80% similarity - filters out MORE)
5. Size limits (max 500k chars total, 15k per doc)
6. Fuzzy folder name matching

Result: 2,199 docs → ~120 docs (4 folders × 30 docs)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from difflib import SequenceMatcher


class Phase0Executor:
    """
    Executes Phase 0: Deep Case Understanding
    
    Purpose: Learn and understand the case completely
    Builds comprehensive knowledge foundation for all future analysis.
    """
    
    # ========================================================================
    # SMART FILTERING RULES
    # ========================================================================
    
    # Skip documents with these patterns in filename (case-insensitive)
    SKIP_PATTERNS = [
        r'\bdraft\b',
        r'\bworking\b',
        r'\btemp\b',
        r'\bcopy\b',
        r'\(1\)',        # Windows duplicate markers
        r'\(2\)',
        r'\(3\)',
        r'\(4\)',
        r'\s+copy\b',
        r'version\s*\d+',
        r'\bv\d+\b',
        r'\bredline\b',
        r'track\s*change',
        r'\bcomment\b',
        r'\breview\b',
        r'\.tmp\b',
        r'~\$',          # Microsoft temp files
        r'^\.',          # Hidden files
        r'\bwip\b',      # Work in progress
    ]
    
    # Prioritise documents with these patterns (higher score = loaded first)
    PRIORITY_PATTERNS = [
        (r'\bmaster\b', 100),
        (r'\bfinal\b', 90),
        (r'\bsigned\b', 85),
        (r'\bconsolidated\b', 80),
        (r'\bexecution\b', 75),
        (r'\bamended\b', 70),
        (r'\bofficial\b', 65),
        (r'\bcertified\b', 60),
        (r'\bapproved\b', 55),
    ]
    
    # Limits to avoid 413 errors
    MAX_TOTAL_CHARS = 500_000        # 500k chars total (~125k tokens) - HARD STOP
    MAX_CHARS_PER_DOC = 15_000       # 15k chars per doc (~3.75k tokens)
    MAX_DOCS_PER_FOLDER = 30         # Max 30 docs per folder (prevents folder overload)
    DEDUP_THRESHOLD = 0.80           # 80% similarity (STRICTER - filters out MORE)
    
    def __init__(self, config, orchestrator):
        """
        Initialise Phase 0 Executor
        
        Args:
            config: System configuration object
            orchestrator: LitigationOrchestrator instance (provides dependencies)
        """
        self.config = config
        self.orchestrator = orchestrator
        
        # Get dependencies from orchestrator
        self.api_client = orchestrator.api_client
        self.memory_system = getattr(orchestrator, 'memory_system', None)
        self.deduplicator = getattr(orchestrator, 'deduplicator', None)
        
        # Import Phase0Prompts
        from prompts.phase_0_prompts import Phase0Prompts
        self.prompts = Phase0Prompts(config)
        
        # Import DocumentLoader - use orchestrator's loader
        self.doc_loader = orchestrator.document_loader
        
        # Output structure
        self.phase_0_dir = config.analysis_dir / "phase_0"
        self.knowledge_dir = self.phase_0_dir / "knowledge_base"
        self.phase_0_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache available folders for fuzzy matching
        self._available_folders = self._scan_available_folders()
        
        # Configure stricter deduplication if available
        if self.deduplicator:
            self.deduplicator.similarity_threshold = self.DEDUP_THRESHOLD
            print(f"  🔍 Deduplication threshold: {self.DEDUP_THRESHOLD:.0%} (stricter)")
    
    def _scan_available_folders(self) -> List[Path]:
        """
        Scan source root and cache all available folders
        
        Returns:
            List of folder paths
        """
        if not self.config.source_root.exists():
            print("⚠️  WARNING: source_root doesn't exist!")
            return []
        
        folders = [f for f in self.config.source_root.iterdir() if f.is_dir()]
        return sorted(folders)
    
    # ========================================================================
    # SMART DOCUMENT FILTERING
    # ========================================================================
    
    def _should_skip_document(self, filename: str) -> Tuple[bool, str]:
        """
        Check if document should be skipped based on filename
        
        Args:
            filename: Document filename
            
        Returns:
            (should_skip: bool, reason: str)
        """
        filename_lower = filename.lower()
        
        # Check skip patterns
        for pattern in self.SKIP_PATTERNS:
            if re.search(pattern, filename_lower):
                return True, f"matched_skip_pattern:{pattern}"
        
        return False, "ok"
    
    def _calculate_document_priority(self, filename: str) -> int:
        """
        Calculate priority score for document (higher = more important)
        
        Args:
            filename: Document filename
            
        Returns:
            Priority score (0-100)
        """
        filename_lower = filename.lower()
        priority = 0
        
        # Check priority patterns
        for pattern, score in self.PRIORITY_PATTERNS:
            if re.search(pattern, filename_lower):
                priority = max(priority, score)
        
        return priority
    
    def _prioritise_documents(self, docs: List[Dict]) -> List[Dict]:
        """
        Sort documents by priority (high priority first)
        
        Args:
            docs: List of document dictionaries
            
        Returns:
            Sorted list (high priority first)
        """
        for doc in docs:
            filename = doc.get('filename', '')
            doc['_priority'] = self._calculate_document_priority(filename)
        
        # Sort by priority (descending)
        return sorted(docs, key=lambda d: d.get('_priority', 0), reverse=True)
    
    # ========================================================================
    # FUZZY FOLDER MATCHING (Built-in)
    # ========================================================================
    
    def _find_folder_fuzzy(self, pattern: str, similarity_threshold: float = 0.75) -> Tuple[Optional[Path], float, str]:
        """
        Find folder matching pattern using fuzzy logic
        
        Handles: typos, case differences, punctuation, plurals
        
        Args:
            pattern: Folder name pattern to search for
            similarity_threshold: Minimum similarity (0.0-1.0) to consider a match
            
        Returns:
            (matched_folder_path, similarity_score, match_type)
        """
        if not self._available_folders:
            return None, 0.0, 'no_folders_available'
        
        # Stage 1: Try exact match first (fastest)
        for folder in self._available_folders:
            if folder.name == pattern:
                return folder, 1.0, 'exact'
        
        # Stage 2: Try case-insensitive exact match
        pattern_lower = pattern.lower()
        for folder in self._available_folders:
            if folder.name.lower() == pattern_lower:
                return folder, 0.99, 'case_insensitive'
        
        # Stage 3: Try normalised match (remove punctuation/numbers)
        pattern_normalised = self._normalise_folder_name(pattern)
        best_match = None
        best_score = 0.0
        
        for folder in self._available_folders:
            folder_normalised = self._normalise_folder_name(folder.name)
            
            # Check if normalised names match exactly
            if folder_normalised == pattern_normalised:
                return folder, 0.95, 'normalised'
            
            # Calculate fuzzy similarity
            similarity = SequenceMatcher(None, pattern_normalised, folder_normalised).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = folder
        
        # Stage 4: Return best fuzzy match if above threshold
        if best_match and best_score >= similarity_threshold:
            return best_match, best_score, 'fuzzy'
        
        # No good match found
        return None, 0.0, 'not_found'
    
    def _normalise_folder_name(self, name: str) -> str:
        """
        Normalise folder name for comparison
        
        Removes: numbers, punctuation, extra whitespace, possessives
        Handles: plurals (converts to singular)
        
        Examples:
        "29- Claimant's Statement of Claim" → "claimant statement claim"
        "First Respondent's Defence" → "first respondent defence"
        "5- Procedural Orders" → "procedural order"
        """
        # Convert to lowercase
        name = name.lower()
        
        # Remove leading numbers and separators (e.g., "29-", "5.", "42 -")
        name = re.sub(r'^\d+[\s\-\.]*', '', name)
        
        # Remove possessives ('s, s')
        name = re.sub(r"'s\b", '', name)
        name = re.sub(r"s'\b", '', name)
        
        # Remove all punctuation except spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Handle common plurals → singular
        name = re.sub(r'\borders\b', 'order', name)
        name = re.sub(r'\bstatements\b', 'statement', name)
        name = re.sub(r'\bdefences\b', 'defence', name)
        name = re.sub(r'\bclaims\b', 'claim', name)
        name = re.sub(r'\breplies\b', 'reply', name)
        name = re.sub(r'\bapplications\b', 'application', name)
        name = re.sub(r'\brulings\b', 'ruling', name)
        
        # Collapse multiple spaces
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    def execute(self) -> Dict:
        """
        Execute complete Phase 0 analysis
        
        Returns:
            Complete case foundation dictionary
        """
        print("\n" + "="*70)
        print("PHASE 0: BUILDING CASE FOUNDATION")
        print("Acting for: LISMORE (Claimant)")
        print("Purpose: Deep case understanding and knowledge retention")
        print("="*70)
        print(f"\n🛡️  Smart Filtering: ENABLED")
        print(f"   • Skip drafts/working copies")
        print(f"   • Prioritise master/final/signed")
        print(f"   • Max {self.MAX_DOCS_PER_FOLDER} docs per folder")
        print(f"   • Deduplication: {self.DEDUP_THRESHOLD:.0%} similarity (stricter)")
        print(f"   • Total limit: {self.MAX_TOTAL_CHARS:,} chars")
        
        start_time = datetime.now()
        total_cost = 0.0
        
        # ====================================================================
        # STAGE 1: CASE UNDERSTANDING
        # ====================================================================
        print("\n" + "="*70)
        print("📜 STAGE 1: Building Case Understanding")
        print("="*70)
        
        stage_1 = self._execute_stage_1_case_understanding()
        total_cost += stage_1.get('cost_gbp', 0)
        
        # Save Stage 1
        stage_1_file = self.knowledge_dir / "stage_1_case_understanding.json"
        with open(stage_1_file, 'w', encoding='utf-8') as f:
            json.dump(stage_1, f, indent=2, ensure_ascii=False)
        print(f"💾 Stage 1 saved: {stage_1_file.name}\n")
        
        # ====================================================================
        # STAGE 2: LEGAL FRAMEWORK
        # ====================================================================
        print("\n" + "="*70)
        print("⚖️  STAGE 2: Analysing Legal Framework")
        print("="*70)
        
        stage_2 = self._execute_stage_2_legal_framework(stage_1)
        total_cost += stage_2.get('cost_gbp', 0)
        
        # Save Stage 2
        stage_2_file = self.knowledge_dir / "stage_2_legal_framework.json"
        with open(stage_2_file, 'w', encoding='utf-8') as f:
            json.dump(stage_2, f, indent=2, ensure_ascii=False)
        print(f"💾 Stage 2 saved: {stage_2_file.name}\n")
        
        # ====================================================================
        # STAGE 3: EVIDENCE LANDSCAPE
        # ====================================================================
        print("\n" + "="*70)
        print("🗺️  STAGE 3: Mapping Evidence Landscape")
        print("="*70)
        
        stage_3 = self._execute_stage_3_evidence_landscape(stage_1, stage_2)
        total_cost += stage_3.get('cost_gbp', 0)
        
        # Save Stage 3
        stage_3_file = self.knowledge_dir / "stage_3_evidence_landscape.json"
        with open(stage_3_file, 'w', encoding='utf-8') as f:
            json.dump(stage_3, f, indent=2, ensure_ascii=False)
        print(f"💾 Stage 3 saved: {stage_3_file.name}\n")
        
        # ====================================================================
        # COMPILE COMPLETE FOUNDATION
        # ====================================================================
        execution_time = (datetime.now() - start_time).total_seconds()
        
        complete_foundation = {
            'phase': 'phase_0',
            'purpose': 'comprehensive_case_learning',
            'execution_time_seconds': execution_time,
            'total_cost_gbp': total_cost,
            'completed_at': datetime.now().isoformat(),
            
            'stage_1_case_understanding': stage_1,
            'stage_2_legal_framework': stage_2,
            'stage_3_evidence_landscape': stage_3,
            
            'metadata': {
                'model_used': self.config.sonnet_model,
                'extended_thinking': True,
                'fuzzy_folder_matching': True,
                'smart_filtering': True,
                'deduplication_threshold': self.DEDUP_THRESHOLD,
                'max_docs_per_folder': self.MAX_DOCS_PER_FOLDER,
                'max_total_chars': self.MAX_TOTAL_CHARS,
                'deduplication_enabled': self.deduplicator is not None,
                'memory_system_active': self.memory_system is not None,
                'approach': 'pure_learning_no_searching'
            }
        }
        
        # Save complete foundation
        foundation_file = self.phase_0_dir / "case_foundation.json"
        with open(foundation_file, 'w', encoding='utf-8') as f:
            json.dump(complete_foundation, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*70)
        print("✅ PHASE 0 COMPLETE - CASE FOUNDATION ESTABLISHED")
        print("="*70)
        print(f"Total cost: £{total_cost:.2f}")
        print(f"Execution time: {execution_time:.1f}s")
        print(f"\nFoundation saved: {foundation_file}")
        print("\n🧠 Comprehensive case knowledge ready for Pass 1-4 analysis")
        print("="*70 + "\n")
        
        return complete_foundation
    
    # ========================================================================
    # STAGE 1: CASE UNDERSTANDING
    # ========================================================================
    
    def _execute_stage_1_case_understanding(self) -> Dict:
        """
        Stage 1: Deep case understanding from pleadings
        
        Returns:
            Dict with case understanding results
        """
        print("Loading pleadings documents...")
        
        # Define pleadings folders
        pleadings_folders = [
            "29- Claimant's Statement of Claim",
            "35- First Respondent's Statement of Defence",
            "30- Respondent's Reply",
            "62. First Respondent's Reply and Rejoinder"
        ]
        
        # Load documents with SMART FILTERING
        pleadings_text = self._load_documents_from_folders(pleadings_folders)
        
        if not pleadings_text:
            raise RuntimeError("❌ Failed to load pleadings. Check folder paths!")
        
        print(f"✓ Loaded {len(pleadings_text):,} characters from pleadings")
        
        # Build prompt for case understanding
        print("Analysing case narratives and legal positions...")
        
        prompt = self.prompts.build_stage_1_prompt(pleadings_text)
        
        # Call Claude API (extended thinking auto-enabled by client)
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model=self.config.sonnet_model,
            task_type='phase_0_stage_1_understanding',
            phase='phase_0'
        )
        
        # Print thinking tokens
        thinking_tokens = metadata.get('thinking_tokens', 0)
        if thinking_tokens > 0:
            print(f"  💭 Thinking: {thinking_tokens:,} tokens")
        
        # Parse response
        result = self._parse_stage_1_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        result['thinking_tokens'] = thinking_tokens
        
        print(f"✓ Stage 1 complete (£{result['cost_gbp']:.2f})")
        print(f"  • Case summary: {len(result.get('case_summary', ''))//100} paragraphs")
        print(f"  • Parties identified: {len(result.get('key_parties', []))}")
        print(f"  • Allegations: {len(result.get('allegations', []))}")
        print(f"  • Defences analysed: {len(result.get('defences', []))}")
        
        return result
    
    # ========================================================================
    # STAGE 2: LEGAL FRAMEWORK
    # ========================================================================
    
    def _execute_stage_2_legal_framework(self, stage_1: Dict) -> Dict:
        """
        Stage 2: Analyse legal framework and proof requirements
        
        Args:
            stage_1: Results from Stage 1
            
        Returns:
            Dict with legal framework results
        """
        print("Loading tribunal rulings and procedural orders...")
        
        # Define tribunal folders
        tribunal_folders = [
            "5- Procedural Orders",
            "42- Tribunal's Ruling dated 31 July 2025",
            "68. Tribunal's Ruling (2 September 2025)",
            "1- Application to Stay Arbitral Proceedings",
            "27. Security for Costs Application"
        ]
        
        # Load documents with SMART FILTERING
        tribunal_text = self._load_documents_from_folders(tribunal_folders)
        
        if not tribunal_text:
            print("⚠️  No tribunal rulings found. Continuing with pleadings only.")
            tribunal_text = "No tribunal rulings available."
        else:
            print(f"✓ Loaded {len(tribunal_text):,} characters from tribunal rulings")
        
        # Build prompt for legal framework
        print("Analysing legal framework and proof requirements...")
        
        prompt = self.prompts.build_stage_2_prompt(
            stage_1_summary=stage_1,
            tribunal_text=tribunal_text
        )
        
        # Call Claude API (extended thinking auto-enabled by client)
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model=self.config.sonnet_model,
            task_type='phase_0_stage_2_legal',
            phase='phase_0'
        )
        
        # Print thinking tokens
        thinking_tokens = metadata.get('thinking_tokens', 0)
        if thinking_tokens > 0:
            print(f"  💭 Thinking: {thinking_tokens:,} tokens")
        
        # Parse response
        result = self._parse_stage_2_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        result['thinking_tokens'] = thinking_tokens
        
        print(f"✓ Stage 2 complete (£{result['cost_gbp']:.2f})")
        print(f"  • Legal tests analysed: {len(result.get('legal_tests', []))}")
        print(f"  • Proof elements: {sum(len(str(test).split('|')) for test in result.get('legal_tests', []))}")
        print(f"  • Case strengths: {len(result.get('case_strengths', []))}")
        print(f"  • Case weaknesses: {len(result.get('case_weaknesses', []))}")
        
        return result
    
    # ========================================================================
    # STAGE 3: EVIDENCE LANDSCAPE
    # ========================================================================
    
    def _execute_stage_3_evidence_landscape(self, stage_1: Dict, stage_2: Dict) -> Dict:
        """
        Stage 3: Map the evidence landscape
        
        Args:
            stage_1: Results from Stage 1
            stage_2: Results from Stage 2
            
        Returns:
            Dict with evidence landscape understanding
        """
        print("Loading chronology and dramatis personae...")
        
        # Define case admin folders
        admin_folders = [
            "20- Dramatis Personae",
            "21- Chronology",
            "51. Hyperlinked Index",
            "52- Hyperlinked Consolidated Index of the Claimant",
            "3- Amended proposed timetable - LCIA Arbitration No. 215173",
            "36- Chronological Email Run"
        ]
        
        # Load documents with SMART FILTERING
        admin_text = self._load_documents_from_folders(admin_folders)
        
        if not admin_text:
            print("⚠️  No chronology/dramatis found. Using pleadings context only.")
            admin_text = ""
        else:
            print(f"✓ Loaded {len(admin_text):,} characters from case admin")
        
        # Build prompt for evidence landscape
        print("Mapping evidence landscape and entity relationships...")
        
        prompt = self.prompts.build_stage_3_prompt(
            stage_1_summary=stage_1,
            stage_2_summary=stage_2,
            admin_text=admin_text
        )
        
        # Call Claude API (extended thinking auto-enabled by client)
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model=self.config.sonnet_model,
            task_type='phase_0_stage_3_evidence',
            phase='phase_0'
        )
        
        # Print thinking tokens
        thinking_tokens = metadata.get('thinking_tokens', 0)
        if thinking_tokens > 0:
            print(f"  💭 Thinking: {thinking_tokens:,} tokens")
        
        # Parse response
        result = self._parse_stage_3_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        result['thinking_tokens'] = thinking_tokens
        
        print(f"✓ Stage 3 complete (£{result['cost_gbp']:.2f})")
        print(f"  • Key entities: {len(result.get('key_entities', []))}")
        print(f"  • Evidence categories: {len(result.get('evidence_categories', []))}")
        print(f"  • Document types understood: {len(result.get('document_patterns', []))}")
        
        return result
    
    # ========================================================================
    # DOCUMENT LOADING WITH SMART FILTERING
    # ========================================================================
    
    def _load_documents_from_folders(self, folder_patterns: List[str]) -> str:
        """
        Load and combine documents from multiple folders
        
        Features:
        - Fuzzy folder name matching (handles typos, case, punctuation)
        - Smart filtering (skip drafts, prioritise master/final)
        - Per-folder cap (max 30 docs per folder)
        - Document content deduplication (80% similarity)
        - Total size limit (500k chars max)
        
        Args:
            folder_patterns: List of folder names/patterns to load
            
        Returns:
            Combined text from all unique documents
        """
        combined_text = []
        total_chars = 0
        unique_docs = 0
        total_docs_processed = 0
        folders_found = 0
        
        stats = {
            'skipped_drafts': 0,
            'skipped_duplicates': 0,
            'skipped_size_limit': 0,
            'loaded_priority': 0,
            'loaded_normal': 0
        }
        
        print(f"\n  📂 Fuzzy Folder Matching: ENABLED")
        print(f"  🔍 Deduplication: {'ENABLED (80% stricter)' if self.deduplicator else 'DISABLED'}")
        print(f"  🛡️  Per-folder cap: {self.MAX_DOCS_PER_FOLDER} documents")
        print(f"  📏 Total limit: {self.MAX_TOTAL_CHARS:,} chars\n")
        
        for pattern in folder_patterns:
            try:
                # Check if we've hit total size limit
                if total_chars >= self.MAX_TOTAL_CHARS:
                    print(f"  ⚠️  TOTAL SIZE LIMIT REACHED ({self.MAX_TOTAL_CHARS:,} chars)")
                    print(f"     Skipping remaining folders")
                    break
                
                # ✅ USE FUZZY MATCHING to find folder
                folder_path, similarity, match_type = self._find_folder_fuzzy(pattern)
                
                if not folder_path:
                    print(f"  ❌ NOT FOUND: '{pattern}'")
                    continue
                
                # Print match details
                if match_type == 'exact':
                    print(f"  ✅ EXACT: {folder_path.name}")
                elif match_type == 'case_insensitive':
                    print(f"  ✅ CASE: {folder_path.name}")
                elif match_type == 'normalised':
                    print(f"  ✅ NORM: {folder_path.name}")
                elif match_type == 'fuzzy':
                    print(f"  ✅ FUZZY ({similarity:.0%}): {folder_path.name}")
                
                folders_found += 1
                
                # Load documents using DocumentLoader
                docs = self.doc_loader.load_folder(folder_path)
                
                if not docs:
                    print(f"     ⚠️  Empty folder")
                    continue
                
                print(f"     Found: {len(docs)} documents")
                
                # ✅ PRIORITISE documents (master/final first)
                docs = self._prioritise_documents(docs)
                
                folder_loaded = 0
                folder_skipped_draft = 0
                folder_skipped_dup = 0
                
                # Process each document (up to MAX_DOCS_PER_FOLDER)
                for doc in docs:
                    total_docs_processed += 1
                    
                    # ✅ CHECK: Folder cap
                    if folder_loaded >= self.MAX_DOCS_PER_FOLDER:
                        break
                    
                    # ✅ CHECK: Total size limit
                    if total_chars >= self.MAX_TOTAL_CHARS:
                        stats['skipped_size_limit'] += 1
                        break
                    
                    filename = doc.get('filename', '')
                    
                    # ✅ CHECK: Should skip (draft/working copy)?
                    should_skip, skip_reason = self._should_skip_document(filename)
                    if should_skip:
                        folder_skipped_draft += 1
                        stats['skipped_drafts'] += 1
                        continue
                    
                    # Get content
                    content = doc.get('text', '') or doc.get('preview', '')
                    
                    if not content or len(content) < 100:
                        continue
                    
                    # ✅ CHECK: Deduplication
                    if self.deduplicator:
                        doc_id = doc.get('id', '')
                        is_dup, reason = self.deduplicator.is_duplicate(content, doc_id, filename)
                        
                        if is_dup:
                            folder_skipped_dup += 1
                            stats['skipped_duplicates'] += 1
                            continue
                    
                    # ✅ LOAD: Truncate to max chars per doc
                    content_truncated = content[:self.MAX_CHARS_PER_DOC]
                    
                    # Add to combined text
                    doc_header = f"\n\n=== {filename} ===\n"
                    combined_text.append(doc_header + content_truncated)
                    
                    # Update counters
                    total_chars += len(doc_header) + len(content_truncated)
                    folder_loaded += 1
                    unique_docs += 1
                    
                    # Track if priority doc
                    if doc.get('_priority', 0) > 0:
                        stats['loaded_priority'] += 1
                    else:
                        stats['loaded_normal'] += 1
                
                # Print folder results
                print(f"     Loaded: {folder_loaded} docs ({stats['loaded_priority']} priority)")
                if folder_skipped_draft > 0:
                    print(f"     Skipped: {folder_skipped_draft} drafts, {folder_skipped_dup} duplicates")
                
            except Exception as e:
                print(f"  ⚠️  Error with '{pattern}': {str(e)[:100]}")
                continue
        
        # Print summary
        print(f"\n  📊 FILTERING SUMMARY:")
        print(f"     Folders found: {folders_found}/{len(folder_patterns)}")
        print(f"     Documents processed: {total_docs_processed}")
        print(f"     Documents loaded: {unique_docs} ({stats['loaded_priority']} priority)")
        print(f"     Skipped drafts: {stats['skipped_drafts']}")
        print(f"     Skipped duplicates: {stats['skipped_duplicates']}")
        print(f"     Total characters: {total_chars:,} / {self.MAX_TOTAL_CHARS:,}")
        print(f"     Reduction: {100 - (total_chars/max(1, total_docs_processed*10000))*100:.1f}%")
        
        if not combined_text:
            print(f"  ⚠️  WARNING: No documents loaded after filtering")
            return ""
        
        return "".join(combined_text)
    
    # ========================================================================
    # RESPONSE PARSING - DELIMITER-BASED
    # ========================================================================
    
    def _parse_stage_1_response(self, response: str) -> Dict:
        """Parse Stage 1 response using SECTION_START/END delimiters"""
        result = {
            'case_summary': '',
            'lismore_narrative': '',
            'ph_narrative': '',
            'key_parties': [],
            'factual_disputes': [],
            'agreed_facts': [],
            'obligations': [],
            'allegations': [],
            'defences': [],
            'timeline': [],
            'financial_claims': []
        }
        
        # Extract text sections
        result['case_summary'] = self._extract_section(response, 'CASE_SUMMARY')
        result['lismore_narrative'] = self._extract_section(response, 'LISMORE_NARRATIVE')
        result['ph_narrative'] = self._extract_section(response, 'PH_NARRATIVE')
        
        # Extract structured list sections
        result['key_parties'] = self._extract_structured_list(response, 'KEY_PARTIES')
        result['factual_disputes'] = self._extract_structured_list(response, 'FACTUAL_DISPUTES')
        result['agreed_facts'] = self._extract_simple_list(response, 'AGREED_FACTS')
        result['obligations'] = self._extract_structured_list(response, 'OBLIGATIONS')
        result['allegations'] = self._extract_structured_list(response, 'ALLEGATIONS')
        result['defences'] = self._extract_structured_list(response, 'DEFENCES')
        result['timeline'] = self._extract_structured_list(response, 'TIMELINE')
        result['financial_claims'] = self._extract_structured_list(response, 'FINANCIAL_CLAIMS')
        
        return result
    
    def _parse_stage_2_response(self, response: str) -> Dict:
        """Parse Stage 2 response using SECTION_START/END delimiters"""
        result = {
            'legal_tests': [],
            'proof_map': [],
            'ph_defences_legal': [],
            'tribunal_priorities': [],
            'case_strengths': [],
            'case_weaknesses': []
        }
        
        result['legal_tests'] = self._extract_structured_list(response, 'LEGAL_TESTS')
        result['proof_map'] = self._extract_structured_list(response, 'PROOF_MAP')
        result['ph_defences_legal'] = self._extract_structured_list(response, 'PH_DEFENCES_LEGAL')
        result['tribunal_priorities'] = self._extract_structured_list(response, 'TRIBUNAL_PRIORITIES')
        result['case_strengths'] = self._extract_simple_list(response, 'CASE_STRENGTHS')
        result['case_weaknesses'] = self._extract_simple_list(response, 'CASE_WEAKNESSES')
        
        return result
    
    def _parse_stage_3_response(self, response: str) -> Dict:
        """Parse Stage 3 response - evidence landscape understanding"""
        result = {
            'key_entities': [],
            'critical_timeline': [],
            'evidence_categories': [],
            'document_patterns': [],
            'evidence_gaps': []
        }
        
        result['key_entities'] = self._extract_structured_list(response, 'KEY_ENTITIES')
        result['critical_timeline'] = self._extract_structured_list(response, 'CRITICAL_TIMELINE')
        result['evidence_categories'] = self._extract_structured_list(response, 'EVIDENCE_CATEGORIES')
        result['document_patterns'] = self._extract_structured_list(response, 'DOCUMENT_PATTERNS')
        result['evidence_gaps'] = self._extract_simple_list(response, 'EVIDENCE_GAPS')
        
        return result
    
    # ========================================================================
    # PARSING HELPER METHODS
    # ========================================================================
    
    def _extract_section(self, response: str, section_name: str) -> str:
        """Extract text between SECTION_NAME_START and SECTION_NAME_END"""
        pattern = f'{section_name}_START(.*?){section_name}_END'
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_simple_list(self, response: str, section_name: str) -> List[str]:
        """Extract simple bullet list from a section"""
        section_text = self._extract_section(response, section_name)
        if not section_text:
            return []
        
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if re.match(r'^[-•\*]\s+', line):
                item = re.sub(r'^[-•\*]\s+', '', line)
                if len(item) > 5:
                    items.append(item)
        
        return items
    
    def _extract_structured_list(self, response: str, section_name: str) -> List[str]:
        """Extract structured list with pipe-delimited fields"""
        section_text = self._extract_section(response, section_name)
        if not section_text:
            return []
        
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if re.match(r'^[-•\*]\s+', line) and '|' in line:
                item = re.sub(r'^[-•\*]\s+', '', line)
                if len(item) > 10:
                    items.append(item)
        
        return items


if __name__ == "__main__":
    """Test Phase 0 executor"""
    print("Phase 0 Executor - Ultimate Smart Filtering Version")
    print("This module requires full system initialisation")
    print("Run from main.py with: python main.py phase0")