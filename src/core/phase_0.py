#!/usr/bin/env python3
"""
Phase 0: Deep Case Understanding & Knowledge Base Construction
Builds comprehensive case intelligence that powers all subsequent passes
British English throughout - Lismore v Process Holdings
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from src.prompts.phase_0_prompts import Phase0Prompts
from src.utils.document_loader import DocumentLoader


class Phase0Executor:
    """
    Executes Phase 0: Deep Case Understanding
    
    Creates comprehensive knowledge base across 3 stages:
    1. Case Understanding (narratives, parties, facts)
    2. Legal Framework (proof requirements, tribunal signals)
    3. Evidence Strategy (document patterns, priorities)
    """
    
    def __init__(self, config, api_client, memory_system=None, deduplicator=None):
        self.config = config
        self.api_client = api_client
        self.memory_system = memory_system
        self.deduplicator = deduplicator
        self.prompts = Phase0Prompts(config)
        self.doc_loader = DocumentLoader(config, deduplicator)
        
        # Output structure
        self.phase_0_dir = config.analysis_dir / "phase_0"
        self.knowledge_dir = self.phase_0_dir / "knowledge_base"
        self.phase_0_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
    
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
        print("📜 STAGE 1: Building Case Understanding")
        print("-"*70)
        
        start_time = datetime.now()
        total_cost = 0.0
        
        # Stage 1: Deep case understanding from pleadings
        stage_1 = self._execute_stage_1_understanding()
        total_cost += stage_1.get('cost_gbp', 0)
        
        # Save Stage 1 to knowledge base
        self._save_stage_knowledge(1, stage_1, "case_understanding")
        
        print("\n" + "="*70)
        print("⚖️  STAGE 2: Analysing Legal Framework & Proof Requirements")
        print("-"*70)
        
        # Stage 2: Legal framework and tribunal signals
        stage_2 = self._execute_stage_2_legal_framework(stage_1)
        total_cost += stage_2.get('cost_gbp', 0)
        
        # Save Stage 2 to knowledge base
        self._save_stage_knowledge(2, stage_2, "legal_framework")
        
        print("\n" + "="*70)
        print("🎯 STAGE 3: Building Evidence Strategy & Discovery Intelligence")
        print("-"*70)
        
        # Stage 3: Evidence strategy with chronology/dramatis
        stage_3 = self._execute_stage_3_evidence_strategy(stage_1, stage_2)
        total_cost += stage_3.get('cost_gbp', 0)
        
        # Save Stage 3 to knowledge base
        self._save_stage_knowledge(3, stage_3, "evidence_strategy")
        
        # Build comprehensive case foundation
        case_foundation = self._build_comprehensive_foundation(stage_1, stage_2, stage_3)
        
        # Add metadata
        execution_time = (datetime.now() - start_time).total_seconds()
        case_foundation['metadata'] = {
            'total_cost_gbp': total_cost,
            'execution_time_seconds': int(execution_time),
            'completed_at': datetime.now().isoformat(),
            'phase': 'phase_0',
            'version': '2.0_understanding_focused'
        }
        
        # Save complete foundation
        self._save_case_foundation(case_foundation)
        
        # Store in memory system
        self._store_in_memory(case_foundation)
        
        # Print summary
        self._print_summary(case_foundation)
        
        return case_foundation
    
    # ========================================================================
    # STAGE 1: CASE UNDERSTANDING
    # ========================================================================
    
    def _execute_stage_1_understanding(self) -> Dict:
        """
        Stage 1: Build deep understanding of case narratives and facts
        
        Returns:
            Dict with comprehensive case understanding
        """
        print("Loading pleadings from folders...")
        
        # Define pleading folders (your actual folder names)
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
        
        # Load documents with deduplication
        pleadings_text = self._load_documents_from_folders(pleadings_folders)
        
        if not pleadings_text:
            raise ValueError("No pleadings found. Check folder names.")
        
        print(f"✓ Loaded {len(pleadings_text):,} characters from pleadings")
        
        # Build prompt for deep understanding
        print("Analysing pleadings for deep case understanding...")
        print("  🧠 Extended Thinking: ENABLED (12,000 tokens)")
        
        prompt = self.prompts.build_stage_1_prompt(pleadings_text)
        
        # Call Claude API with extended thinking
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            model=self.config.sonnet_model,
            task_type='phase_0_stage_1_understanding',
            phase='phase_0'
        )
        
        # Print thinking tokens used
        thinking_tokens = metadata.get('thinking_tokens', 0)
        if thinking_tokens > 0:
            print(f"  💭 Thinking: {thinking_tokens:,} tokens")
        
        # Parse response
        result = self._parse_stage_1_response(response)
        result['cost_gbp'] = metadata.get('cost_gbp', 0)
        result['tokens_input'] = metadata.get('input_tokens', 0)
        result['tokens_output'] = metadata.get('output_tokens', 0)
        result['thinking_tokens'] = thinking_tokens
        
        # Print what was extracted
        print(f"✓ Stage 1 complete (£{result['cost_gbp']:.2f})")
        print(f"  • Case narrative understood: {len(result.get('case_summary', ''))//100} paragraphs")
        print(f"  • Key parties identified: {len(result.get('key_parties', []))}")
        print(f"  • Factual disputes mapped: {len(result.get('factual_disputes', []))}")
        print(f"  • Obligations catalogued: {len(result.get('obligations', []))}")
        print(f"  • Timeline events: {len(result.get('timeline', []))}")
        
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
            Dict with legal framework analysis
        """
        print("Loading tribunal rulings from folders...")
        
        # Define tribunal ruling folders (your actual folder names)
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
        
        # Load documents with deduplication
        tribunal_text = self._load_documents_from_folders(tribunal_folders)
        
        if not tribunal_text:
            print("⚠️  No tribunal rulings found. Continuing with pleadings only.")
            tribunal_text = "No tribunal rulings available."
        else:
            print(f"✓ Loaded {len(tribunal_text):,} characters from tribunal rulings")
        
        # Build prompt for legal framework
        print("Analysing legal framework and proof requirements...")
        print("  🧠 Extended Thinking: ENABLED (12,000 tokens)")
        
        prompt = self.prompts.build_stage_2_prompt(
            stage_1_summary=stage_1,
            tribunal_text=tribunal_text
        )
        
        # Call Claude API
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
        print(f"  • Proof elements mapped: {sum(len(test.get('elements_required', [])) for test in result.get('legal_tests', []))}")
        print(f"  • Case strengths identified: {len(result.get('case_strengths', []))}")
        print(f"  • Case weaknesses identified: {len(result.get('case_weaknesses', []))}")
        
        return result
    
    # ========================================================================
    # STAGE 3: EVIDENCE STRATEGY
    # ========================================================================
    
    def _execute_stage_3_evidence_strategy(self, stage_1: Dict, stage_2: Dict) -> Dict:
        """
        Stage 3: Build evidence strategy and discovery patterns
        
        Args:
            stage_1: Results from Stage 1
            stage_2: Results from Stage 2
            
        Returns:
            Dict with evidence strategy
        """
        print("Loading chronology and dramatis personae...")
        
        # Define case admin folders (your actual folder names)
        admin_folders = [
            "20- Dramatis Personae",
            "21- Chronology",
            "51. Hyperlinked Index",
            "52- Hyperlinked Consolidated Index of the Claimant",
            "3- Amended proposed timetable - LCIA Arbitration No. 215173",
            "36- Chronological Email Run",
        ]
        
        # Load documents with deduplication
        admin_text = self._load_documents_from_folders(admin_folders)
        
        if not admin_text:
            print("⚠️  No chronology/dramatis found. Using pleadings context only.")
            admin_text = ""
        else:
            print(f"✓ Loaded {len(admin_text):,} characters from case admin")
        
        # Build prompt for evidence strategy
        print("Building evidence strategy and discovery patterns...")
        print("  🧠 Extended Thinking: ENABLED (12,000 tokens)")
        
        prompt = self.prompts.build_stage_3_prompt(
            stage_1_summary=stage_1,
            stage_2_summary=stage_2,
            admin_text=admin_text
        )
        
        # Call Claude API
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
        print(f"  • Key entities refined: {len(result.get('key_entities', []))}")
        print(f"  • Evidence categories identified: {len(result.get('evidence_categories', []))}")
        print(f"  • Document patterns created: {len(result.get('document_patterns', []))}")
        print(f"  • Evidence gaps identified: {len(result.get('evidence_gaps', []))}")
        
        return result
    
    # ========================================================================
    # DOCUMENT LOADING WITH DEDUPLICATION
    # ========================================================================
    
    def _load_documents_from_folders(self, folder_patterns: List[str]) -> str:
        """
        Load and combine documents from multiple folders with deduplication
        
        Args:
            folder_patterns: List of folder names/patterns to load
            
        Returns:
            Combined text from all unique documents
        """
        combined_text = []
        unique_docs = 0
        loaded_count = 0
        
        print(f"\n  Deduplication: {'ENABLED ✅' if self.deduplicator else 'DISABLED'}")
        
        for folder_pattern in folder_patterns:
            try:
                # Load documents
                docs = self.doc_loader.load_from_folder(folder_pattern)
                
                if not docs:
                    print(f"  ⚠️  Not found: {folder_pattern}")
                    continue
                
                loaded_count += 1
                folder_unique = 0
                folder_dups = 0
                
                print(f"  📂 Loading: {folder_pattern}")
                
                # Process each document
                for doc in docs:
                    content = doc.get('content', '')
                    
                    if self.deduplicator:
                        # Check for duplicates
                        is_unique = self.deduplicator.is_unique(content, doc.get('metadata', {}))
                        
                        if is_unique:
                            combined_text.append(content)
                            folder_unique += 1
                            unique_docs += 1
                        else:
                            folder_dups += 1
                    else:
                        # No deduplication
                        combined_text.append(content)
                        folder_unique += 1
                        unique_docs += 1
                
                # Print folder results
                if self.deduplicator and folder_dups > 0:
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
        return "\n\n".join(combined_text)
    
    # ========================================================================
    # PARSING METHODS (Improved for new structure)
    # ========================================================================
    
    def _parse_stage_1_response(self, response: str) -> Dict:
        """Parse Stage 1 response with robust JSON extraction"""
        try:
            # Method 1: Extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Method 2: Find largest valid JSON object
            potential_jsons = list(re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL))
            for match in sorted(potential_jsons, key=lambda m: len(m.group()), reverse=True):
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
            
            # Method 3: Fallback extraction
            print("⚠️  JSON parsing failed, using fallback extraction")
            return {
                'case_summary': self._extract_section(response, 'case_summary') or 
                               self._extract_text_block(response, 300),
                'lismore_narrative': self._extract_object(response, 'lismore_narrative'),
                'ph_narrative': self._extract_object(response, 'ph_narrative'),
                'factual_disputes': self._extract_array(response, 'factual_disputes'),
                'agreed_facts': self._extract_simple_array(response, 'agreed_facts'),
                'key_parties': self._extract_array(response, 'key_parties'),
                'obligations': self._extract_array(response, 'obligations'),
                'lismore_allegations': self._extract_array(response, 'lismore_allegations'),
                'ph_defences': self._extract_array(response, 'ph_defences'),
                'timeline': self._extract_array(response, 'timeline'),
                'core_tensions': self._extract_array(response, 'core_tensions'),
                'raw_response': response[:3000]
            }
        except Exception as e:
            print(f"⚠️  Stage 1 parse error: {e}")
            return {'raw_response': response[:3000], 'parse_error': str(e)}
    
    def _parse_stage_2_response(self, response: str) -> Dict:
        """Parse Stage 2 response with robust JSON extraction"""
        try:
            # Try same methods as Stage 1
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            potential_jsons = list(re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL))
            for match in sorted(potential_jsons, key=lambda m: len(m.group()), reverse=True):
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
            
            # Fallback
            print("⚠️  JSON parsing failed, using fallback extraction")
            return {
                'legal_tests': self._extract_array(response, 'legal_tests'),
                'ph_defences_analysis': self._extract_array(response, 'ph_defences_analysis'),
                'tribunal_priorities': self._extract_object(response, 'tribunal_priorities'),
                'proof_map': self._extract_array(response, 'proof_map'),
                'case_strengths': self._extract_array(response, 'case_strengths'),
                'case_weaknesses': self._extract_array(response, 'case_weaknesses'),
                'strategic_insights': self._extract_simple_array(response, 'strategic_insights'),
                'raw_response': response[:3000]
            }
        except Exception as e:
            print(f"⚠️  Stage 2 parse error: {e}")
            return {'raw_response': response[:3000], 'parse_error': str(e)}
    
    def _parse_stage_3_response(self, response: str) -> Dict:
        """Parse Stage 3 response with robust JSON extraction"""
        try:
            # Try same methods
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            potential_jsons = list(re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL))
            for match in sorted(potential_jsons, key=lambda m: len(m.group()), reverse=True):
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
            
            # Fallback
            print("⚠️  JSON parsing failed, using fallback extraction")
            return {
                'key_entities': self._extract_array(response, 'key_entities'),
                'critical_timeline': self._extract_array(response, 'critical_timeline'),
                'evidence_categories': self._extract_array(response, 'evidence_categories'),
                'document_patterns': self._extract_array(response, 'document_patterns'),
                'evidence_gaps': self._extract_array(response, 'evidence_gaps'),
                'discovery_priorities': self._extract_object(response, 'discovery_priorities'),
                'scoring_guidance': self._extract_object(response, 'scoring_guidance'),
                'raw_response': response[:3000]
            }
        except Exception as e:
            print(f"⚠️  Stage 3 parse error: {e}")
            return {'raw_response': response[:3000], 'parse_error': str(e)}
    
    # ========================================================================
    # EXTRACTION HELPER METHODS
    # ========================================================================
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a text section"""
        patterns = [
            f'"{section_name}"\\s*:\\s*"([^"]*)"',
            f'"{section_name}"\\s*:\\s*`([^`]*)`',
            f'{section_name}[:\\s]+(.*?)(?=\\n\\n|\\n[A-Z]|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""
    
    def _extract_array(self, text: str, array_name: str) -> List[Dict]:
        """Extract array of objects"""
        # Look for JSON array
        pattern = f'"{array_name}"\\s*:\\s*\\[(.*?)\\]'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(f'[{match.group(1)}]')
            except:
                pass
        
        return []
    
    def _extract_simple_array(self, text: str, array_name: str) -> List[str]:
        """Extract array of strings"""
        pattern = f'"{array_name}"\\s*:\\s*\\[(.*?)\\]'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(f'[{match.group(1)}]')
            except:
                pass
        
        return []
    
    def _extract_object(self, text: str, object_name: str) -> Dict:
        """Extract nested object"""
        pattern = f'"{object_name}"\\s*:\\s*\\{{(.*?)\\}}'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(f'{{{match.group(1)}}}')
            except:
                pass
        
        return {}
    
    def _extract_text_block(self, text: str, max_length: int = 500) -> str:
        """Extract coherent text block (fallback)"""
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)
        return clean_text.strip()[:max_length]
    
    # ========================================================================
    # KNOWLEDGE BASE MANAGEMENT
    # ========================================================================
    
    def _build_comprehensive_foundation(self, stage_1: Dict, stage_2: Dict, stage_3: Dict) -> Dict:
        """
        Combine all stages into comprehensive, structured knowledge base
        
        This structure is optimised for:
        - Pass 1: Uses document_patterns and scoring_guidance
        - Pass 2: Uses legal_tests and proof_map
        - Pass 3: Uses evidence_gaps and investigation_priorities
        - Pass 4: Uses complete case_understanding for synthesis
        """
        
        return {
            # ============================================================
            # CASE UNDERSTANDING (Stage 1)
            # ============================================================
            'case_understanding': {
                'executive_summary': stage_1.get('case_summary', ''),
                
                'narratives': {
                    'lismore': stage_1.get('lismore_narrative', {}),
                    'ph': stage_1.get('ph_narrative', {})
                },
                
                'factual_landscape': {
                    'disputes': stage_1.get('factual_disputes', []),
                    'agreed_facts': stage_1.get('agreed_facts', []),
                    'core_tensions': stage_1.get('core_tensions', [])
                },
                
                'parties_and_context': {
                    'key_parties': stage_1.get('key_parties', []),
                    'transaction_context': stage_1.get('transaction_context', {}),
                    'financial_picture': stage_1.get('financial_picture', {})
                },
                
                'timeline': stage_1.get('timeline', []),
                
                'obligations': stage_1.get('obligations', []),
                
                'allegations_and_defences': {
                    'lismore_allegations': stage_1.get('lismore_allegations', []),
                    'ph_defences': stage_1.get('ph_defences', [])
                }
            },
            
            # ============================================================
            # LEGAL FRAMEWORK (Stage 2)
            # ============================================================
            'legal_framework': {
                'legal_tests': stage_2.get('legal_tests', []),
                'proof_map': stage_2.get('proof_map', []),
                
                'tribunal_intelligence': {
                    'priorities': stage_2.get('tribunal_priorities', {}),
                    'signals': stage_2.get('tribunal_priorities', {}).get('key_concerns', [])
                },
                
                'strategic_assessment': {
                    'strengths': stage_2.get('case_strengths', []),
                    'weaknesses': stage_2.get('case_weaknesses', []),
                    'ph_defences_analysis': stage_2.get('ph_defences_analysis', [])
                },
                
                'insights': stage_2.get('strategic_insights', [])
            },
            
            # ============================================================
            # EVIDENCE STRATEGY (Stage 3)
            # ============================================================
            'evidence_strategy': {
                'key_entities': stage_3.get('key_entities', []),
                'refined_timeline': stage_3.get('critical_timeline', []),
                
                'evidence_requirements': {
                    'categories': stage_3.get('evidence_categories', []),
                    'gaps': stage_3.get('evidence_gaps', [])
                },
                
                'document_patterns': stage_3.get('document_patterns', []),
                
                'discovery_priorities': stage_3.get('discovery_priorities', {}),
                
                'scoring_guidance': stage_3.get('scoring_guidance', {})
            },
            
            # ============================================================
            # RAW STAGE OUTPUTS (for debugging/reference)
            # ============================================================
            'raw_stages': {
                'stage_1': stage_1,
                'stage_2': stage_2,
                'stage_3': stage_3
            }
        }
    
    def _save_case_foundation(self, case_foundation: Dict):
        """Save complete case foundation to JSON"""
        output_file = self.phase_0_dir / "case_foundation.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(case_foundation, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Case foundation saved: {output_file}")
    
    def _save_stage_knowledge(self, stage_num: int, stage_data: Dict, knowledge_type: str):
        """
        Save individual stage knowledge to separate files for easy access
        
        Args:
            stage_num: Stage number (1, 2, or 3)
            stage_data: Stage results dictionary
            knowledge_type: Type of knowledge (case_understanding, legal_framework, evidence_strategy)
        """
        # Save to knowledge_base subdirectory
        stage_file = self.knowledge_dir / f"stage_{stage_num}_{knowledge_type}.json"
        
        with open(stage_file, 'w', encoding='utf-8') as f:
            json.dump(stage_data, f, indent=2, ensure_ascii=False)
        
        # Also save human-readable markdown summary
        md_file = self.knowledge_dir / f"stage_{stage_num}_{knowledge_type}.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Stage {stage_num}: {knowledge_type.replace('_', ' ').title()}\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("## Summary\n\n")
            f.write(self._generate_markdown_summary(stage_data, knowledge_type))
    
    def _generate_markdown_summary(self, stage_data: Dict, knowledge_type: str) -> str:
        """Generate human-readable markdown summary of stage"""
        lines = []
        
        if knowledge_type == 'case_understanding':
            lines.append(f"**Case Summary**: {stage_data.get('case_summary', 'N/A')[:500]}...\n\n")
            lines.append(f"**Key Parties**: {len(stage_data.get('key_parties', []))}\n")
            lines.append(f"**Factual Disputes**: {len(stage_data.get('factual_disputes', []))}\n")
            lines.append(f"**Obligations**: {len(stage_data.get('obligations', []))}\n")
            lines.append(f"**Timeline Events**: {len(stage_data.get('timeline', []))}\n\n")
            
        elif knowledge_type == 'legal_framework':
            lines.append(f"**Legal Tests**: {len(stage_data.get('legal_tests', []))}\n")
            lines.append(f"**Proof Elements**: {sum(len(t.get('elements_required', [])) for t in stage_data.get('legal_tests', []))}\n")
            lines.append(f"**Case Strengths**: {len(stage_data.get('case_strengths', []))}\n")
            lines.append(f"**Case Weaknesses**: {len(stage_data.get('case_weaknesses', []))}\n\n")
            
        elif knowledge_type == 'evidence_strategy':
            lines.append(f"**Document Patterns**: {len(stage_data.get('document_patterns', []))}\n")
            lines.append(f"**Key Entities**: {len(stage_data.get('key_entities', []))}\n")
            lines.append(f"**Evidence Categories**: {len(stage_data.get('evidence_categories', []))}\n")
            lines.append(f"**Evidence Gaps**: {len(stage_data.get('evidence_gaps', []))}\n\n")
        
        return ''.join(lines)
    
    def _store_in_memory(self, case_foundation: Dict):
        """Store case foundation in memory system for Tier 1 retrieval"""
        if not self.memory_system:
            return
        
        try:
            # Store executive summary
            self.memory_system.store({
                'type': 'case_summary',
                'content': case_foundation.get('case_understanding', {}).get('executive_summary', ''),
                'tier': 1,
                'phase': 'phase_0'
            })
            
            # Store document patterns for Pass 1
            for pattern in case_foundation.get('evidence_strategy', {}).get('document_patterns', []):
                self.memory_system.store({
                    'type': 'document_pattern',
                    'content': json.dumps(pattern),
                    'tier': 1,
                    'phase': 'phase_0'
                })
            
            # Store legal tests for Pass 2
            for test in case_foundation.get('legal_framework', {}).get('legal_tests', []):
                self.memory_system.store({
                    'type': 'legal_test',
                    'content': json.dumps(test),
                    'tier': 1,
                    'phase': 'phase_0'
                })
            
            print("✓ Stored in memory system (Tier 1)")
            
        except Exception as e:
            print(f"⚠️  Memory system storage error: {e}")
    
    def _print_summary(self, case_foundation: Dict):
        """Print comprehensive summary of Phase 0 results"""
        print("\n" + "="*70)
        print("✅ PHASE 0 COMPLETE: COMPREHENSIVE KNOWLEDGE BASE BUILT")
        print("="*70)
        
        metadata = case_foundation.get('metadata', {})
        
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"  • Total cost: £{metadata.get('total_cost_gbp', 0):.2f}")
        print(f"  • Execution time: {metadata.get('execution_time_seconds', 0)}s")
        
        # Stage 1 stats
        cu = case_foundation.get('case_understanding', {})
        print(f"\n📜 CASE UNDERSTANDING (Stage 1):")
        print(f"  • Executive summary: {len(cu.get('executive_summary', ''))//100} paragraphs")
        print(f"  • Key parties: {len(cu.get('parties_and_context', {}).get('key_parties', []))}")
        print(f"  • Factual disputes: {len(cu.get('factual_landscape', {}).get('disputes', []))}")
        print(f"  • Obligations: {len(cu.get('obligations', []))}")
        print(f"  • Timeline events: {len(cu.get('timeline', []))}")
        
        # Stage 2 stats
        lf = case_foundation.get('legal_framework', {})
        print(f"\n⚖️  LEGAL FRAMEWORK (Stage 2):")
        print(f"  • Legal tests: {len(lf.get('legal_tests', []))}")
        print(f"  • Proof elements: {sum(len(t.get('elements_required', [])) for t in lf.get('legal_tests', []))}")
        print(f"  • Case strengths: {len(lf.get('strategic_assessment', {}).get('strengths', []))}")
        print(f"  • Case weaknesses: {len(lf.get('strategic_assessment', {}).get('weaknesses', []))}")
        
        # Stage 3 stats
        es = case_foundation.get('evidence_strategy', {})
        print(f"\n🎯 EVIDENCE STRATEGY (Stage 3):")
        print(f"  • Document patterns: {len(es.get('document_patterns', []))}")
        print(f"  • Key entities: {len(es.get('key_entities', []))}")
        print(f"  • Evidence categories: {len(es.get('evidence_requirements', {}).get('categories', []))}")
        print(f"  • Evidence gaps: {len(es.get('evidence_requirements', {}).get('gaps', []))}")
        
        print(f"\n💾 OUTPUT:")
        print(f"  • Main file: {self.phase_0_dir / 'case_foundation.json'}")
        print(f"  • Knowledge base: {self.knowledge_dir}/")
        print(f"    - stage_1_case_understanding.json")
        print(f"    - stage_2_legal_framework.json")
        print(f"    - stage_3_evidence_strategy.json")
        print(f"    - (+ markdown summaries)")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"  • Phase 0 knowledge base is ready")
        print(f"  • Pass 1 will use document_patterns for intelligent triage")
        print(f"  • Pass 2 will use legal_tests and proof_map for deep analysis")
        print(f"  • Pass 3 will use evidence_gaps for targeted investigations")
        print(f"  • Pass 4 will use complete understanding for synthesis")
        print(f"  • Run: python main.py pass1")
        
        print("="*70 + "\n")