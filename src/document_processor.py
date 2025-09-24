# document_processor.py - FIXED VERSION WITH INTELLIGENT BATCHING
"""
Document processor with proper batching for Lismore arbitration analysis
Handles large document volumes without overloading API
"""

import json
import time
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .api_client import ClaudeAPIClient
from .knowledge_manage import KnowledgeManager
from .phase_prompts import (
    get_phase_prompt,
    get_master_prompt,
    get_phase_description,
    get_all_phases,
    should_generate_learning,
    get_learning_generator_prompt,
    update_learning_prompt
)
from .utils import load_documents, validate_documents

class DocumentProcessor:
    """
    Core document processing engine with intelligent batching
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise the document processor"""
        self.api_client = ClaudeAPIClient(api_key)
        self.knowledge_manage = KnowledgeManager()
        self.documents = []
        self.current_phase = None
        
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
        
    def load_documents(self, document_paths: List[str]) -> bool:
        """
        Load and validate documents with proper text extraction
        
        Args:
            document_paths: List of paths to documents
            
        Returns:
            Success status
        """
        try:
            self.documents = load_documents(document_paths)
            
            if not self.documents:
                print("❌ No documents loaded")
                return False
            
            # Validate documents
            valid_docs = validate_documents(self.documents)
            
            print(f"✅ Loaded {len(valid_docs)} valid documents")
            self.documents = valid_docs
            return True
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            return False
    
    def process_phase(self, phase_num: str, documents: Optional[List[Dict]] = None) -> Dict:
        """
        Process a single phase with INTELLIGENT BATCHING
        
        Args:
            phase_num: Phase to process (0A, 0B, 1-7)
            documents: Optional documents to process
            
        Returns:
            Phase results
        """
        self.current_phase = phase_num
        
        # Use provided documents or loaded ones
        docs_to_process = documents if documents is not None else self.documents
        
        if not docs_to_process:
            print(f"❌ No documents to process for phase {phase_num}")
            return {}
        
        print(f"\n{'='*60}")
        print(f"PHASE {phase_num}: {get_phase_description(phase_num)}")
        print(f"{'='*60}")
        print(f"📊 Documents to analyse: {len(docs_to_process)}")
        
        # CRITICAL: Intelligent batching
        batches = self._create_intelligent_batches(docs_to_process, phase_num)
        print(f"📦 Created {len(batches)} batches for processing")
        
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
        
        # Store the complete phase knowledge
        self.knowledge_manage.store_phase_knowledge(phase_num, final_result)
        
        print(f"\n✅ Phase {phase_num} complete. Processed {len(batches)} batches.")
        
        return final_result
    
    def _create_intelligent_batches(self, documents: List[Dict], phase_num: str) -> List[List[Dict]]:
        """
        Create intelligent document batches based on phase and token limits
        
        Args:
            documents: Documents to batch
            phase_num: Current phase
            
        Returns:
            List of document batches
        """
        batch_size = self.BATCH_SIZES.get(phase_num, 5)
        max_tokens = self.MAX_TOKENS_PER_BATCH.get(phase_num, 150000)
        
        batches = []
        current_batch = []
        current_tokens = 0
        
        for doc in documents:
            # Estimate tokens (1 token ≈ 4 characters)
            doc_tokens = len(doc.get('content', '')) // 4
            
            # Check if adding this document would exceed limits
            if current_batch and (
                len(current_batch) >= batch_size or 
                current_tokens + doc_tokens > max_tokens
            ):
                # Save current batch and start new one
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            
            # Add document to current batch
            current_batch.append(doc)
            current_tokens += doc_tokens
        
        # Don't forget the last batch
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _process_single_batch(
        self, 
        phase_num: str, 
        batch: List[Dict], 
        batch_num: int, 
        total_batches: int,
        accumulated_knowledge: Dict
    ) -> Dict:
        """
        Process a single batch of documents
        
        Args:
            phase_num: Current phase
            batch: Documents in this batch
            batch_num: Batch number
            total_batches: Total number of batches
            accumulated_knowledge: Knowledge from previous batches
            
        Returns:
            Batch analysis results
        """
        # Get previous phase knowledge
        previous_knowledge = self.knowledge_manage.get_previous_knowledge(phase_num)
        
        # Add accumulated knowledge from previous batches
        if accumulated_knowledge:
            previous_knowledge['batch_knowledge'] = accumulated_knowledge
        
        # Build prompts
        master = get_master_prompt()
        phase_prompt = get_phase_prompt(phase_num)
        
        # Add batch context
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
        
        # Prepare documents
        document_texts = []
        for doc in batch:
            text = doc['content']
            # Truncate if needed
            if len(text) > 40000:
                text = text[:35000] + "\n[...truncated...]\n" + text[-5000:]
            document_texts.append(text)
        
        # Send to Claude
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
        """
        Merge knowledge from new batch into accumulated knowledge
        
        Args:
            accumulated: Accumulated knowledge dict
            new_batch: New batch results
        """
        if not new_batch:
            return
        
        # Extract key findings from the new batch
        batch_num = new_batch.get('batch_num', 0)
        analysis = new_batch.get('analysis', '')
        
        # Store batch findings
        if 'batches' not in accumulated:
            accumulated['batches'] = {}
        
        accumulated['batches'][f'batch_{batch_num}'] = {
            'summary': analysis[:1000] if analysis else '',  # Keep summary only
            'doc_count': new_batch.get('documents_analysed', 0)
        }
    
    def _synthesise_batch_results(self, phase_num: str, batch_results: List[Dict]) -> Dict:
        """
        Synthesise results from all batches into coherent phase findings
        
        Args:
            phase_num: Current phase
            batch_results: All batch results
            
        Returns:
            Synthesised phase results
        """
        print(f"\n🔄 Synthesising {len(batch_results)} batch results...")
        
        # Combine all analyses
        combined_analyses = []
        total_docs = 0
        
        for batch in batch_results:
            if batch and batch.get('analysis'):
                combined_analyses.append(f"[Batch {batch['batch_num']}]:\n{batch['analysis']}")
                total_docs += batch.get('documents_analysed', 0)
        
        # Create synthesis prompt
        synthesis_prompt = f"""
        SYNTHESIS TASK FOR PHASE {phase_num}:
        
        You have analysed {total_docs} documents across {len(batch_results)} batches.
        Now synthesise all findings into a coherent, comprehensive analysis.
        
        BATCH ANALYSES TO SYNTHESISE:
        {chr(10).join(combined_analyses[:10000])}  # Limit to avoid token overflow
        
        SYNTHESIS REQUIREMENTS:
        1. Identify the most critical patterns across ALL batches
        2. Highlight the strongest evidence against Process Holdings
        3. Note any contradictions or gaps discovered
        4. Provide actionable recommendations for Lismore
        5. Rank findings by legal/strategic importance
        
        Create a unified narrative that captures the essence of all batch findings.
        """
        
        # Get synthesis from Claude
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
            # Return raw batch results if synthesis fails
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
        """
        Build the complete prompt for analysis
        
        Args:
            master: Master forensic prompt
            phase_prompt: Phase-specific prompt
            previous_knowledge: Knowledge from previous phases
            
        Returns:
            Combined prompt string
        """
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
            
            # Add knowledge but limit size
            knowledge_str = json.dumps(previous_knowledge, indent=2)
            if len(knowledge_str) > 5000:
                knowledge_str = knowledge_str[:4500] + "\n[...truncated...]"
            prompt_parts.append(knowledge_str)
        
        prompt_parts.append("\nBe ruthlessly forensic. Find what destroys Process Holdings.")
        
        return "\n".join(prompt_parts)
    
    def run_full_analysis(self) -> Dict:
        """
        Run all phases in sequence with proper batching
        
        Returns:
            Complete analysis results
        """
        print("\n" + "="*60)
        print("STARTING FULL ANALYSIS FOR LISMORE CAPITAL")
        print("WITH INTELLIGENT BATCHING")
        print("="*60)
        
        all_phases = get_all_phases()
        results = {}
        
        for phase in all_phases:
            phase_result = self.process_phase(phase)
            results[phase] = phase_result
            
            print(f"\n✅ Phase {phase} complete")
            
            # Cost check
            cost_summary = self.api_client.get_cost_summary()
            print(f"💰 Running total: £{cost_summary['total_cost']:.2f}")
            
            # Pause between phases
            if phase != all_phases[-1]:
                print("⏱️  Pausing 5 seconds before next phase...")
                time.sleep(5)
        
        print("\n" + "="*60)
        print("FULL ANALYSIS COMPLETE")
        print("="*60)
        
        # Generate summary
        summary = self.knowledge_manage.generate_summary()
        results['summary'] = summary
        
        # Final cost report
        self.api_client.get_cost_summary()
        
        return results
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        return {
            'current_phase': self.current_phase,
            'documents_loaded': len(self.documents),
            'phases_completed': self.knowledge_manage.get_completed_phases(),
            'total_phases': len(get_all_phases()),
            'batching_enabled': True,
            'batch_sizes': self.BATCH_SIZES
        }