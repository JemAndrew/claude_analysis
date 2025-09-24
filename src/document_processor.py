
"""
Document processor with three-directory structure:
- legal_resources/ (legal framework documents)
- case_context/ (case background documents)
- documents/ (main disclosure documents, processed text preferred)
Handles intelligent batching, phase-specific processing, and cumulative knowledge management.

"""

import json
import time
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from api_client import ClaudeAPIClient
from knowledge_manage import KnowledgeManager
from phase_prompts import (
    get_phase_prompt,
    get_master_prompt,
    get_phase_description,
    get_all_phases,
    should_generate_learning,
    get_learning_generator_prompt,
    update_learning_prompt
)
from utils import load_documents, validate_documents

class DocumentProcessor:
    """
    Core document processing engine with three-directory structure
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise the document processor"""
        self.api_client = ClaudeAPIClient(api_key)
        self.knowledge_manage = KnowledgeManager()
        self.documents = []
        self.current_phase = None
        
        # THREE-DIRECTORY STRUCTURE
        self.PHASE_DIRECTORIES = {
            "0A": "legal_resources",           # Legal framework documents
            "0B": "case_context",              # Case background documents
            "1": "documents/processed/text",   # MAIN DISCLOSURE - processed text
            "2": "documents/processed/text",   # MAIN DISCLOSURE
            "3": "documents/processed/text",   # MAIN DISCLOSURE
            "4": "documents/processed/text",   # MAIN DISCLOSURE
            "5": "documents/processed/text",   # MAIN DISCLOSURE
            "6": "documents/processed/text",   # MAIN DISCLOSURE
            "7": "documents/processed/text"    # MAIN DISCLOSURE
        }
        
        # Alternative raw directory if processed not available
        self.RAW_DISCLOSURE_DIR = "documents/raw"
        
        # Cache for disclosure documents (the big set)
        self.disclosure_cache = None
        
        # CRITICAL: Batching configuration
        self.BATCH_SIZES = {
            "0A": 3,   # Legal framework - small batches for deep analysis
            "0B": 3,   # Case context - small batches
            "1": 5,    # Initial landscape - moderate batches
            "2": 5,    # Chronological - moderate batches
            "3": 5,    # Behaviour analysis - moderate batches
            "4": 7,    # Theory construction - larger batches
            "5": 7,    # Evidence analysis - larger batches
            "6": 10,   # Smoking guns - largest batches
            "7": 10    # Autonomous deep dive - largest batches
        }
        
        # Token limits per batch (conservative to avoid overflow)
        self.MAX_TOKENS_PER_BATCH = {
            "0A": 100000,  # ~25k words for legal analysis
            "0B": 100000,
            "1": 150000,   # ~37k words
            "2": 150000,
            "3": 150000,
            "4": 200000,   # ~50k words
            "5": 200000,
            "6": 250000,   # ~62k words
            "7": 250000
        }
    
    def load_documents_for_phase(self, phase_num: str) -> bool:
        """
        Load documents from the appropriate directory for the given phase
        
        Args:
            phase_num: Phase identifier (0A, 0B, 1-7)
            
        Returns:
            Success status
        """
        # Get the directory for this phase
        phase_dir = self.PHASE_DIRECTORIES.get(phase_num)
        
        if not phase_dir:
            print(f"❌ No directory configured for phase {phase_num}")
            return False
        
        # Check if we're loading disclosure documents (phases 1-7)
        is_disclosure_phase = phase_num not in ["0A", "0B"]
        
        # Use cached disclosure documents if available
        if is_disclosure_phase and self.disclosure_cache is not None:
            print(f"📌 Using cached disclosure documents ({len(self.disclosure_cache)} files)")
            self.documents = self.disclosure_cache
            return True
        
        # Check if directory exists
        phase_path = Path(phase_dir)
        
        # For disclosure phases, check both processed and raw directories
        if is_disclosure_phase and not phase_path.exists():
            print(f"⚠️  Processed text directory not found: {phase_dir}")
            print(f"   Checking raw directory: {self.RAW_DISCLOSURE_DIR}")
            phase_path = Path(self.RAW_DISCLOSURE_DIR)
            phase_dir = self.RAW_DISCLOSURE_DIR
        
        if not phase_path.exists():
            print(f"❌ Directory not found: {phase_dir}/")
            if is_disclosure_phase:
                print("   CRITICAL: Disclosure documents not found!")
                print("   Expected locations:")
                print("   - documents/processed/text/ (for processed text files)")
                print("   - documents/raw/ (for raw PDFs)")
            else:
                print(f"   Please create {phase_dir}/ and add relevant PDFs")
            return False
        
        # Load documents
        try:
            print(f"📂 Loading documents from {phase_dir}/ for Phase {phase_num}")
            
            # Determine file patterns based on directory
            if "processed/text" in phase_dir:
                # Load text files
                txt_files = list(phase_path.glob("*.txt"))
                print(f"   Found {len(txt_files)} text files")
                
                self.documents = []
                for txt_path in txt_files:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.documents.append({
                            'path': str(txt_path),
                            'filename': txt_path.name,
                            'content': content,
                            'source_type': 'processed_text'
                        })
            else:
                # Load PDFs (for legal_resources, case_context, or raw documents)
                self.documents = load_documents([str(phase_path)])
            
            if not self.documents:
                print(f"❌ No documents found in {phase_dir}/")
                return False
            
            # Validate documents
            valid_docs = validate_documents(self.documents)
            self.documents = valid_docs
            
            # Show what we loaded
            doc_type = "disclosure documents" if is_disclosure_phase else "documents"
            print(f"✅ Loaded {len(self.documents)} {doc_type} from {phase_dir}/")
            
            # Cache disclosure documents for reuse in phases 1-7
            if is_disclosure_phase:
                self.disclosure_cache = self.documents
                print(f"💾 Cached disclosure documents for phases 1-7")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading documents from {phase_dir}/: {e}")
            return False
    
    def process_phase(self, phase_num: str) -> Dict:
        """
        Process a single phase with automatic directory selection
        
        Args:
            phase_num: Phase to process (0A, 0B, 1-7)
            
        Returns:
            Phase results
        """
        self.current_phase = phase_num
        
        print(f"\n{'='*60}")
        print(f"PHASE {phase_num}: {get_phase_description(phase_num)}")
        print(f"{'='*60}")
        
        # Special message for disclosure phases
        if phase_num not in ["0A", "0B"]:
            print("🎯 ANALYSING MAIN DISCLOSURE DOCUMENTS")
        
        # Load documents for this specific phase
        if not self.load_documents_for_phase(phase_num):
            print(f"❌ Failed to load documents for phase {phase_num}")
            return {}
        
        print(f"📊 Documents to analyse: {len(self.documents)}")
        
        # Show which directory we're using
        phase_dir = self.PHASE_DIRECTORIES.get(phase_num, "unknown")
        if phase_num not in ["0A", "0B"] and self.disclosure_cache:
            if any('raw' in doc.get('path', '') for doc in self.documents[:1]):
                phase_dir = self.RAW_DISCLOSURE_DIR
        print(f"📁 Source directory: {phase_dir}/")
        
        # CRITICAL: Intelligent batching
        batches = self._create_intelligent_batches(self.documents, phase_num)
        print(f"📦 Created {len(batches)} batches for processing")
        
        # Estimate cost for this phase
        if phase_num in ["0A", "0B", "1"]:
            cost_per_batch = 0.15  # Haiku
            model = "Claude 3 Haiku"
        else:
            cost_per_batch = 2.50  # Opus 4.1
            model = "Claude Opus 4.1"
        
        phase_cost = len(batches) * cost_per_batch + 0.20  # Plus synthesis
        print(f"💰 Estimated cost for this phase: £{phase_cost:.2f} ({model})")
        
        # Process each batch
        all_batch_results = []
        batch_knowledge = {}
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n--- Processing Batch {batch_num}/{len(batches)} ---")
            print(f"   Documents in batch: {len(batch)}")
            
            # Calculate tokens in batch
            batch_tokens = sum(len(doc['content']) // 4 for doc in batch)
            print(f"   Estimated tokens: {batch_tokens:,}")
            
            # Process this batch
            batch_result = self._process_single_batch(
                phase_num, 
                batch, 
                batch_num, 
                len(batches),
                batch_knowledge
            )
            
            if batch_result:
                all_batch_results.append(batch_result)
                # Accumulate knowledge from this batch
                self._merge_batch_knowledge(batch_knowledge, batch_result)
            
            # Rate limit protection
            if batch_num < len(batches):
                print("⏱️  Waiting 3 seconds before next batch...")
                time.sleep(3)
        
        # Synthesise all batch results
        final_result = self._synthesise_batch_results(phase_num, all_batch_results)
        
        # Add metadata
        final_result['source_directory'] = phase_dir
        final_result['documents_analysed'] = len(self.documents)
        final_result['document_type'] = 'disclosure' if phase_num not in ["0A", "0B"] else phase_num
        
        # Store the complete phase knowledge
        self.knowledge_manage.store_phase_knowledge(phase_num, final_result)
        
        print(f"\n✅ Phase {phase_num} complete. Processed {len(batches)} batches.")
        
        return final_result
    
    def verify_setup(self) -> Dict:
        """Verify all directories are properly set up"""
        status = {
            'legal_resources': {'exists': False, 'count': 0},
            'case_context': {'exists': False, 'count': 0},
            'disclosure_processed': {'exists': False, 'count': 0},
            'disclosure_raw': {'exists': False, 'count': 0}
        }
        
        # Check legal_resources
        legal_path = Path("legal_resources")
        if legal_path.exists():
            status['legal_resources']['exists'] = True
            status['legal_resources']['count'] = len(list(legal_path.glob("*.pdf")))
        
        # Check case_context
        case_path = Path("case_context")
        if case_path.exists():
            status['case_context']['exists'] = True
            status['case_context']['count'] = len(list(case_path.glob("*.pdf")))
        
        # Check disclosure processed
        processed_path = Path("documents/processed/text")
        if processed_path.exists():
            status['disclosure_processed']['exists'] = True
            status['disclosure_processed']['count'] = len(list(processed_path.glob("*.txt")))
        
        # Check disclosure raw
        raw_path = Path("documents/raw")
        if raw_path.exists():
            status['disclosure_raw']['exists'] = True
            status['disclosure_raw']['count'] = len(list(raw_path.glob("*.pdf")))
        
        return status
    
    # [Keep all your existing methods below - they remain unchanged]
    def _create_intelligent_batches(self, documents: List[Dict], phase_num: str) -> List[List[Dict]]:
        """Create intelligent document batches based on phase and token limits"""
        batch_size = self.BATCH_SIZES.get(phase_num, 5)
        max_tokens = self.MAX_TOKENS_PER_BATCH.get(phase_num, 150000)
        
        batches = []
        current_batch = []
        current_tokens = 0
        
        for doc in documents:
            doc_tokens = len(doc.get('content', '')) // 4
            
            if current_batch and (
                len(current_batch) >= batch_size or 
                current_tokens + doc_tokens > max_tokens
            ):
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            
            current_batch.append(doc)
            current_tokens += doc_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _process_single_batch(self, phase_num: str, batch: List[Dict], 
                             batch_num: int, total_batches: int,
                             accumulated_knowledge: Dict) -> Dict:
        """Process a single batch of documents"""
        previous_knowledge = self.knowledge_manage.get_previous_knowledge(phase_num)
        
        if accumulated_knowledge:
            previous_knowledge['batch_knowledge'] = accumulated_knowledge
        
        master = get_master_prompt()
        phase_prompt = get_phase_prompt(phase_num)
        
        batch_context = f"""
        BATCH CONTEXT:
        This is batch {batch_num} of {total_batches} for Phase {phase_num}.
        Focus on extracting key patterns and findings that can be combined with other batches.
        """
        
        full_prompt = self._build_full_prompt(
            master, 
            phase_prompt + batch_context, 
            previous_knowledge
        )
        
        document_texts = []
        for doc in batch:
            text = doc['content']
            if len(text) > 40000:
                text = text[:35000] + "\n[...truncated...]\n" + text[-5000:]
            document_texts.append(text)
        
        api_phase = f"phase_{phase_num.lower()}"
        
        try:
            response = self.api_client.analyse_documents(
                documents=document_texts,
                prompt=full_prompt,
                phase=api_phase,
                context=previous_knowledge
            )
            
            return {
                'batch_num': batch_num,
                'documents_analysed': len(batch),
                'analysis': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error processing batch {batch_num}: {e}")
            return None
    
    def _merge_batch_knowledge(self, accumulated: Dict, new_batch: Dict):
        """Merge knowledge from new batch into accumulated knowledge"""
        if not new_batch:
            return
        
        batch_num = new_batch.get('batch_num', 0)
        analysis = new_batch.get('analysis', '')
        
        if 'batches' not in accumulated:
            accumulated['batches'] = {}
        
        accumulated['batches'][f'batch_{batch_num}'] = {
            'summary': analysis[:1000] if analysis else '',
            'doc_count': new_batch.get('documents_analysed', 0)
        }
    
    def _synthesise_batch_results(self, phase_num: str, batch_results: List[Dict]) -> Dict:
        """Synthesise results from all batches into coherent phase findings"""
        print(f"\n🔄 Synthesising {len(batch_results)} batch results...")
        
        combined_analyses = []
        total_docs = 0
        
        for batch in batch_results:
            if batch and batch.get('analysis'):
                combined_analyses.append(f"[Batch {batch['batch_num']}]:\n{batch['analysis']}")
                total_docs += batch.get('documents_analysed', 0)
        
        synthesis_prompt = f"""
        SYNTHESIS TASK FOR PHASE {phase_num}:
        
        You have analysed {total_docs} documents across {len(batch_results)} batches.
        Now synthesise all findings into a coherent, comprehensive analysis.
        
        BATCH ANALYSES TO SYNTHESISE:
        {chr(10).join(combined_analyses[:10000])}
        
        SYNTHESIS REQUIREMENTS:
        1. Identify the most critical patterns across ALL batches
        2. Highlight the strongest evidence against Process Holdings
        3. Note any contradictions or gaps discovered
        4. Provide actionable recommendations for Lismore
        5. Rank findings by legal/strategic importance
        
        Create a unified narrative that captures the essence of all batch findings.
        """
        
        api_phase = f"phase_{phase_num.lower()}_synthesis"
        
        try:
            synthesis = self.api_client.analyse_documents(
                documents=[],
                prompt=synthesis_prompt,
                phase=api_phase
            )
            
            return {
                'phase': phase_num,
                'description': get_phase_description(phase_num),
                'timestamp': datetime.now().isoformat(),
                'total_documents': total_docs,
                'total_batches': len(batch_results),
                'batch_results': batch_results,
                'synthesis': synthesis,
                'findings': {
                    'combined_analysis': synthesis,
                    'batch_count': len(batch_results),
                    'document_count': total_docs
                }
            }
            
        except Exception as e:
            print(f"❌ Error synthesising results: {e}")
            return {
                'phase': phase_num,
                'description': get_phase_description(phase_num),
                'timestamp': datetime.now().isoformat(),
                'total_documents': total_docs,
                'batch_results': batch_results,
                'findings': {
                    'combined_analysis': chr(10).join(combined_analyses),
                    'batch_count': len(batch_results),
                    'document_count': total_docs
                }
            }
    
    def _build_full_prompt(self, master: str, phase_prompt: str, previous_knowledge: Dict) -> str:
        """Build the complete prompt for analysis"""
        prompt_parts = [
            master,
            "\nCURRENT PHASE FOCUS:",
            phase_prompt
        ]
        
        if previous_knowledge:
            prompt_parts.extend([
                "\nPREVIOUS PHASE KNOWLEDGE:",
                "You have access to the following insights from previous phases:"
            ])
            
            knowledge_str = json.dumps(previous_knowledge, indent=2)
            if len(knowledge_str) > 5000:
                knowledge_str = knowledge_str[:4500] + "\n[...truncated...]"
            prompt_parts.append(knowledge_str)
        
        prompt_parts.append("\nBe ruthlessly forensic. Find what destroys Process Holdings.")
        
        return "\n".join(prompt_parts)
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        return {
            'current_phase': self.current_phase,
            'documents_loaded': len(self.documents),
            'phases_completed': self.knowledge_manage.get_completed_phases(),
            'total_phases': len(get_all_phases()),
            'batching_enabled': True,
            'batch_sizes': self.BATCH_SIZES,
            'phase_directories': self.PHASE_DIRECTORIES,
            'disclosure_cached': self.disclosure_cache is not None
        }