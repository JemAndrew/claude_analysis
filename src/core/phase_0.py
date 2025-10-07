#!/usr/bin/env python3
"""
Phase 0 Executor: Intelligent Case Foundation Building
Analyses pleadings, tribunal rulings, and case administration documents
to build contextual understanding before document triage.

British English throughout - Lismore v Process Holdings
Acting for Lismore - arguments are Lismore-sided
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from utils.deduplication import DocumentDeduplicator


class Phase0Executor:
    """
    Builds intelligent case foundation in 3 stages:
    Stage 1: Pleadings analysis (core dispute understanding)
    Stage 2: Tribunal signals (what tribunal cares about)
    Stage 3: Smoking gun patterns (what evidence to look for)
    """
    
    def __init__(self, config, orchestrator):
        """
        Initialise Phase 0 Executor
        
        Args:
            config: System configuration
            orchestrator: Main orchestrator instance
        """
        self.config = config
        self.orchestrator = orchestrator
        self.api_client = orchestrator.api_client
        self.document_loader = orchestrator.document_loader
        self.knowledge_graph = orchestrator.knowledge_graph
        
        # Output directory
        self.phase_0_dir = config.analysis_dir / "phase_0"
        self.phase_0_dir.mkdir(parents=True, exist_ok=True)
        
        # Import prompts
        from prompts.phase_0_prompts import Phase0Prompts
        self.prompts = Phase0Prompts()
        
        # Deduplication system
        if config.deduplication_config['enabled']:
            self.deduplicator = DocumentDeduplicator(
                similarity_threshold=config.deduplication_config['similarity_threshold'],
                prefix_chars=config.deduplication_config['prefix_chars'],
                enable_semantic=config.deduplication_config['enable_semantic']
            )
        else:
            self.deduplicator = None
        
        # Track costs
        self.total_cost = 0.0
    
    def execute(self) -> Dict:
        """
        Execute complete Phase 0 analysis
        
        Returns:
            Dict containing case foundation and metadata
        """
        print("\n" + "="*70)
        print("PHASE 0: INTELLIGENT CASE FOUNDATION")
        print("="*70)
        print("Building contextual understanding of Lismore v Process Holdings")
        print("to enable intelligent document triage in Pass 1.")
        print("="*70 + "\n")
        
        start_time = datetime.now()
        
        try:
            # Stage 1: Analyse pleadings
            print("📜 STAGE 1: Analysing Pleadings")
            print("-" * 70)
            stage_1_result = self._execute_stage_1_pleadings()
            self.total_cost += stage_1_result.get('cost_gbp', 0)
            
            # Stage 2: Analyse tribunal rulings
            print("\n⚖️  STAGE 2: Analysing Tribunal Rulings")
            print("-" * 70)
            stage_2_result = self._execute_stage_2_tribunal(stage_1_result)
            self.total_cost += stage_2_result.get('cost_gbp', 0)
            
            # Stage 3: Identify smoking gun patterns
            print("\n🎯 STAGE 3: Identifying Smoking Gun Patterns")
            print("-" * 70)
            stage_3_result = self._execute_stage_3_patterns(
                stage_1_result, 
                stage_2_result
            )
            self.total_cost += stage_3_result.get('cost_gbp', 0)
            
            # Build comprehensive case foundation
            case_foundation = self._build_case_foundation(
                stage_1_result,
                stage_2_result,
                stage_3_result
            )
            
            # Add metadata
            case_foundation['metadata'] = {
                'created_at': datetime.now().isoformat(),
                'total_cost_gbp': self.total_cost,
                'execution_time_seconds': (datetime.now() - start_time).total_seconds(),
                'stages_completed': 3
            }
            
            # Save outputs
            self._save_case_foundation(case_foundation)
            self._save_stage_outputs(stage_1_result, stage_2_result, stage_3_result)
            
            # Store in knowledge systems
            self._store_in_knowledge_graph(case_foundation)
            self._store_in_memory_system(case_foundation)
            
            # Print summary
            self._print_summary(case_foundation)
            
            return case_foundation
            
        except Exception as e:
            print(f"\n❌ ERROR in Phase 0: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # ========================================================================
    # STAGE 1: PLEADINGS ANALYSIS
    # ========================================================================
    
    def _execute_stage_1_pleadings(self) -> Dict:
        """
        Stage 1: Analyse pleadings to understand core dispute
        
        Returns:
            Dict with core allegations, defences, disputed clauses
        """
        print("Loading pleadings from folders...")
        
        # Define pleadings folders (YOUR ACTUAL FOLDER NAMES)
        pleadings_folders = [
            "5- Request for Arbitration",
            "29- Claimant's Statement of Claim",
            "72. Lismore's Submission (6 October 2025)",
            "10- Claimant's Response to the First Respondent's Stay Application",
            "13- Claimant's Response to Stay Application",
            "28- Claimant's Response to the First Respondent's application for security for costs",
            "35- First Respondent's Statement of Defence",
            "43. Statement of Defence Shared with Counsel",
            "30- Respondent's Reply",
            "62. First Respondent's Reply and Rejoinder",
            "63. PHL's Rejoinder to Lismore's Reply of 30 May 2025",
        ]
        
        # Load documents WITH DEDUPLICATION
        pleadings_text = self._load_documents_from_folders(pleadings_folders)
        
        if not pleadings_text:
            raise ValueError("No pleadings found. Check folder names.")
        
        print(f"✓ Loaded {len(pleadings_text):,} characters from pleadings")
        
        # Build prompt
        print("Analysing pleadings with Sonnet + Extended Thinking...")
        prompt = self.prompts.build_stage_1_prompt(pleadings_text)
        
        # Call Claude API
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='phase_0_stage_1_pleadings',
            phase='phase_0',
            extended_thinking=True
        )
        
        # Parse response
        result = self._parse_stage_1_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        
        print(f"✓ Stage 1 complete (£{result['cost_gbp']:.2f})")
        print(f"  • {len(result.get('lismore_allegations', []))} Lismore allegations identified")
        print(f"  • {len(result.get('ph_defences', []))} PH defences identified")
        print(f"  • {len(result.get('disputed_clauses', []))} disputed clauses mapped")
        
        return result
    
    # ========================================================================
    # STAGE 2: TRIBUNAL SIGNALS
    # ========================================================================
    
    def _execute_stage_2_tribunal(self, stage_1: Dict) -> Dict:
        """
        Stage 2: Analyse tribunal rulings to understand tribunal priorities
        
        Args:
            stage_1: Results from Stage 1
            
        Returns:
            Dict with tribunal signals and priorities
        """
        print("Loading tribunal rulings from folders...")
        
        # Define tribunal ruling folders (YOUR ACTUAL FOLDER NAMES)
        tribunal_folders = [
            "4- PO1",
            "8- PO2",
            "39- Procedural Order No. 2",
            "42. Procedural Order No. 3",
            "22- Tribunal's Ruling on the Stay Application",
            "31- Tribunal's Ruling on Application for Security for Costs",
            "53- Tribunal's Decisions on Stern Schedules",
            "65. Tribunal's Ruling dated 31 July 2025",
            "68. Tribunal's Ruling (2 September 2025)",
            "1- Application to Stay Arbitral Proceedings",
            "27. Security for Costs Application",
        ]
        
        # Load documents WITH DEDUPLICATION
        tribunal_text = self._load_documents_from_folders(tribunal_folders)
        
        if not tribunal_text:
            print("⚠️  No tribunal rulings found. Skipping Stage 2.")
            return {'tribunal_signals': [], 'cost_gbp': 0}
        
        print(f"✓ Loaded {len(tribunal_text):,} characters from tribunal rulings")
        
        # Build prompt with Stage 1 context
        print("Analysing tribunal rulings with Sonnet + Extended Thinking...")
        prompt = self.prompts.build_stage_2_prompt(
            stage_1_summary=stage_1,
            tribunal_text=tribunal_text
        )
        
        # Call Claude API
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='phase_0_stage_2_tribunal',
            phase='phase_0',
            extended_thinking=True
        )
        
        # Parse response
        result = self._parse_stage_2_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        
        print(f"✓ Stage 2 complete (£{result['cost_gbp']:.2f})")
        print(f"  • {len(result.get('tribunal_signals', []))} tribunal signals identified")
        print(f"  • {len(result.get('procedural_priorities', []))} procedural priorities")
        
        return result
    
    # ========================================================================
    # STAGE 3: SMOKING GUN PATTERNS
    # ========================================================================
    
    def _execute_stage_3_patterns(self, stage_1: Dict, stage_2: Dict) -> Dict:
        """
        Stage 3: Identify smoking gun patterns based on case understanding
        
        Args:
            stage_1: Results from Stage 1
            stage_2: Results from Stage 2
            
        Returns:
            Dict with smoking gun patterns and search criteria
        """
        print("Loading chronology and dramatis personae...")
        
        # Define case admin folders (YOUR ACTUAL FOLDER NAMES)
        admin_folders = [
            "20- Dramatis Personae",
            "21- Chronology",
            "51. Hyperlinked Index",
            "52- Hyperlinked Consolidated Index of the Claimant",
            "3- Amended proposed timetable - LCIA Arbitration No. 215173",
            "36- Chronological Email Run",
        ]
        
        # Load documents WITH DEDUPLICATION
        admin_text = self._load_documents_from_folders(admin_folders)
        
        if not admin_text:
            print("⚠️  No chronology/dramatis found. Using stages 1+2 only.")
            admin_text = ""
        else:
            print(f"✓ Loaded {len(admin_text):,} characters from case admin")
        
        # Build prompt with all context
        print("Identifying smoking gun patterns with Sonnet + Extended Thinking...")
        prompt = self.prompts.build_stage_3_prompt(
            stage_1_summary=stage_1,
            stage_2_summary=stage_2,
            admin_text=admin_text
        )
        
        # Call Claude API
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='phase_0_stage_3_patterns',
            phase='phase_0',
            extended_thinking=True
        )
        
        # Parse response
        result = self._parse_stage_3_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        
        print(f"✓ Stage 3 complete (£{result['cost_gbp']:.2f})")
        print(f"  • {len(result.get('smoking_gun_patterns', []))} smoking gun patterns")
        print(f"  • {len(result.get('key_entities', []))} key entities/amounts")
        print(f"  • {len(result.get('critical_timeline', []))} critical dates")
        
        return result
    
    # ========================================================================
    # DOCUMENT LOADING WITH DEDUPLICATION
    # ========================================================================
    
    def _load_documents_from_folders(self, folder_names: List[str]) -> str:
        """
        Load all documents from specified folders WITH DEDUPLICATION
        
        Args:
            folder_names: List of folder name patterns
            
        Returns:
            Combined text from all unique documents
        """
        combined_text = ""
        loaded_count = 0
        total_docs = 0
        unique_docs = 0
        
        print(f"\n  Deduplication: {'ENABLED ✅' if self.deduplicator else 'DISABLED'}")
        
        for folder_pattern in folder_names:
            # Find matching folder - exact match first
            folder_path = None
            
            # Try exact match
            exact_path = self.config.source_root / folder_pattern
            if exact_path.exists() and exact_path.is_dir():
                folder_path = exact_path
            else:
                # Fallback: case-insensitive partial match
                for candidate in self.config.source_root.iterdir():
                    if candidate.is_dir() and folder_pattern.lower() in candidate.name.lower():
                        folder_path = candidate
                        break
            
            if not folder_path:
                print(f"  ⚠️  Not found: {folder_pattern}")
                continue
            
            # Load documents from folder
            try:
                print(f"  📂 Loading: {folder_path.name}")
                docs = self.document_loader.load_folder(folder_path)
                
                if not docs:
                    print(f"     (Empty folder)")
                    continue
                
                total_docs += len(docs)
                folder_unique = 0
                folder_dups = 0
                
                for doc in docs:
                    # Check for duplicates
                    if self.deduplicator:
                        content = doc.get('content', '') or doc.get('preview', '')
                        doc_id = doc.get('doc_id', '')
                        filename = doc.get('filename', '')
                        
                        is_dup, reason = self.deduplicator.is_duplicate(
                            content, doc_id, filename
                        )
                        
                        if is_dup:
                            folder_dups += 1
                            continue
                    
                    # Not a duplicate - include it
                    unique_docs += 1
                    folder_unique += 1
                    
                    combined_text += f"\n\n{'='*70}\n"
                    combined_text += f"DOCUMENT: {doc['filename']}\n"
                    combined_text += f"FOLDER: {doc['folder_name']}\n"
                    combined_text += f"{'='*70}\n\n"
                    
                    content = doc.get('content', '') or doc.get('preview', '')
                    combined_text += content[:100000]  # Max 100K chars per doc
                
                loaded_count += 1
                if folder_dups > 0:
                    print(f"     ✅ Loaded {folder_unique}/{len(docs)} unique ({folder_dups} duplicates skipped)")
                else:
                    print(f"     ✅ Loaded {folder_unique} documents")
                
            except Exception as e:
                print(f"  ⚠️  Error loading {folder_pattern}: {e}")
                continue
        
        # Print deduplication summary
        if self.deduplicator:
            stats = self.deduplicator.get_statistics()
            print(f"\n  📊 Deduplication Summary:")
            print(f"     Total checked: {stats['total_checked']}")
            print(f"     Unique: {stats['unique_documents']} ({stats['unique_rate']:.1%})")
            print(f"     Exact duplicates: {stats['exact_duplicates']}")
            print(f"     Fuzzy duplicates: {stats['fuzzy_duplicates']}")
            print(f"     Semantic duplicates: {stats['semantic_duplicates']}")
        
        if not combined_text:
            print(f"  ⚠️  WARNING: No unique documents loaded")
            return ""
        
        print(f"\n  ✅ Summary: {unique_docs} unique documents from {loaded_count} folders")
        return combined_text
    
    # ========================================================================
    # PARSING METHODS
    # ========================================================================
    
    def _parse_stage_1_response(self, response: str) -> Dict:
        """Parse Stage 1 response into structured format"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback: manual parsing
            return {
                'core_dispute': self._extract_section(response, 'core_dispute'),
                'lismore_allegations': self._extract_list(response, 'lismore_allegations'),
                'ph_defences': self._extract_list(response, 'ph_defences'),
                'disputed_clauses': self._extract_list(response, 'disputed_clauses'),
                'raw_response': response
            }
        except Exception as e:
            print(f"⚠️  Parse error: {e}")
            return {'raw_response': response}
    
    def _parse_stage_2_response(self, response: str) -> Dict:
        """Parse Stage 2 response into structured format"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                'tribunal_signals': self._extract_list(response, 'tribunal_signals'),
                'procedural_priorities': self._extract_list(response, 'procedural_priorities'),
                'raw_response': response
            }
        except Exception as e:
            print(f"⚠️  Parse error: {e}")
            return {'raw_response': response}
    
    def _parse_stage_3_response(self, response: str) -> Dict:
        """Parse Stage 3 response into structured format"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                'smoking_gun_patterns': self._extract_list(response, 'smoking_gun_patterns'),
                'key_entities': self._extract_list(response, 'key_entities'),
                'critical_timeline': self._extract_list(response, 'critical_timeline'),
                'raw_response': response
            }
        except Exception as e:
            print(f"⚠️  Parse error: {e}")
            return {'raw_response': response}
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a named section from text"""
        pattern = f"{section_name}[:\\s]+(.*?)(?:\\n\\n|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, text: str, list_name: str) -> List:
        """Extract a list from text"""
        pattern = f"{list_name}[:\\s]+\\[(.*?)\\]"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                return json.loads(f"[{match.group(1)}]")
            except:
                pass
        return []
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _build_case_foundation(self, 
                               stage_1: Dict, 
                               stage_2: Dict, 
                               stage_3: Dict) -> Dict:
        """
        Combine all stages into comprehensive case foundation
        
        Args:
            stage_1: Pleadings analysis
            stage_2: Tribunal signals
            stage_3: Smoking gun patterns
            
        Returns:
            Complete case foundation dictionary
        """
        return {
            'stage_1_summary': stage_1,
            'stage_2_summary': stage_2,
            'stage_3_summary': stage_3,
            'core_dispute': stage_1.get('core_dispute', ''),
            'lismore_allegations': stage_1.get('lismore_allegations', []),
            'ph_defences': stage_1.get('ph_defences', []),
            'disputed_clauses': stage_1.get('disputed_clauses', []),
            'tribunal_signals': stage_2.get('tribunal_signals', []),
            'procedural_priorities': stage_2.get('procedural_priorities', []),
            'smoking_gun_patterns': stage_3.get('smoking_gun_patterns', []),
            'key_entities': stage_3.get('key_entities', []),
            'critical_timeline': stage_3.get('critical_timeline', [])
        }
    
    def _save_case_foundation(self, case_foundation: Dict):
        """Save case foundation to JSON file"""
        output_file = self.phase_0_dir / "case_foundation.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(case_foundation, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Case foundation saved: {output_file}")
    
    def _save_stage_outputs(self, stage_1: Dict, stage_2: Dict, stage_3: Dict):
        """Save individual stage outputs for debugging"""
        stages = {
            'stage_1_pleadings.json': stage_1,
            'stage_2_tribunal.json': stage_2,
            'stage_3_patterns.json': stage_3
        }
        
        for filename, data in stages.items():
            output_file = self.phase_0_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _store_in_knowledge_graph(self, case_foundation: Dict):
        """Store case foundation in knowledge graph"""
        try:
            # Check if method exists
            if hasattr(self.knowledge_graph, 'store_case_foundation'):
                self.knowledge_graph.store_case_foundation(case_foundation)
                print("✓ Stored in knowledge graph")
        except Exception as e:
            print(f"⚠️  Knowledge graph storage error: {e}")
    
    def _store_in_memory_system(self, case_foundation: Dict):
        """Store case foundation in hierarchical memory system"""
        try:
            if hasattr(self.orchestrator, 'memory_enabled') and self.orchestrator.memory_enabled:
                # Store in Tier 1 (Claude Projects - permanent)
                if hasattr(self.orchestrator.memory_system, 'tier1'):
                    self.orchestrator.memory_system.tier1.add_to_project_manifest({
                        'filename': 'case_foundation.json',
                        'content': json.dumps(case_foundation, indent=2),
                        'category': 'case_context',
                        'importance': 10
                    })
                    print("✓ Stored in memory system (Tier 1)")
        except Exception as e:
            print(f"⚠️  Memory system storage error: {e}")
    
    def _print_summary(self, case_foundation: Dict):
        """Print Phase 0 summary"""
        print("\n" + "="*70)
        print("✅ PHASE 0 COMPLETE: INTELLIGENT CASE FOUNDATION BUILT")
        print("="*70)
        
        print(f"\n📊 SUMMARY:")
        print(f"  • Total cost: £{case_foundation['metadata']['total_cost_gbp']:.2f}")
        print(f"  • Execution time: {case_foundation['metadata']['execution_time_seconds']:.0f}s")
        
        print(f"\n📜 CASE UNDERSTANDING:")
        print(f"  • Lismore allegations: {len(case_foundation.get('lismore_allegations', []))}")
        print(f"  • PH defences: {len(case_foundation.get('ph_defences', []))}")
        print(f"  • Disputed clauses: {len(case_foundation.get('disputed_clauses', []))}")
        
        print(f"\n⚖️  TRIBUNAL INSIGHTS:")
        print(f"  • Tribunal signals: {len(case_foundation.get('tribunal_signals', []))}")
        print(f"  • Procedural priorities: {len(case_foundation.get('procedural_priorities', []))}")
        
        print(f"\n🎯 DISCOVERY GUIDANCE:")
        print(f"  • Smoking gun patterns: {len(case_foundation.get('smoking_gun_patterns', []))}")
        print(f"  • Key entities: {len(case_foundation.get('key_entities', []))}")
        print(f"  • Critical dates: {len(case_foundation.get('critical_timeline', []))}")
        
        print(f"\n💾 OUTPUT:")
        print(f"  • Location: {self.phase_0_dir}")
        print(f"  • Main file: case_foundation.json")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"  • Phase 0 foundation is ready")
        print(f"  • Pass 1 will use this context for intelligent triage")
        print(f"  • Run: python main.py pass1")
        
        print("="*70 + "\n")