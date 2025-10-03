#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
Controls dynamic phase execution and investigation spawning
WITH INTEGRATED CHECKPOINT SYSTEM AND HIERARCHICAL MEMORY
British English throughout
"""

import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib

from core.config import config
from core.phase_executor import PhaseExecutor
from intelligence.knowledge_graph import KnowledgeGraph
from api.client import ClaudeClient
from api.context_manager import ContextManager
from api.batch_manager import BatchManager
from prompts.autonomous import AutonomousPrompts
from prompts.recursive import RecursivePrompts
from prompts.synthesis import SynthesisPrompts
from utils.document_loader import DocumentLoader


class LitigationOrchestrator:
    """Main system orchestrator for maximum Claude utilisation"""
    
    def __init__(self, config_override: Dict = None):
        """Initialise orchestrator with all components"""
        
        # Override config if needed
        if config_override:
            for key, value in config_override.items():
                setattr(config, key, value)
        
        self.config = config
        
        # Initialise core components
        self.knowledge_graph = KnowledgeGraph(config)
        self.api_client = ClaudeClient(config)
        self.context_manager = ContextManager(config)
        self.batch_manager = BatchManager(config)
        self.phase_executor = PhaseExecutor(config, self)
        
        # Initialise prompt systems
        self.autonomous_prompts = AutonomousPrompts(config)
        self.recursive_prompts = RecursivePrompts(config)
        self.synthesis_prompts = SynthesisPrompts(config)
        
        # NEW: Initialise hierarchical memory system
        try:
            from memory import HierarchicalMemory, MemoryQuery
            self.memory_system = HierarchicalMemory(
                config=self.config,
                knowledge_graph=self.knowledge_graph
            )
            self.memory_enabled = True
            print("Memory System: ACTIVE")
        except ImportError as e:
            print(f"Memory System: Not available ({e})")
            print("Install: pip install chromadb sentence-transformers cryptography")
            self.memory_system = None
            self.memory_enabled = False
        
        # Track system state
        self.state = {
            'current_phase': None,
            'phases_completed': [],
            'active_investigations': [],
            'iteration_count': 0,
            'start_time': datetime.now().isoformat(),
            'convergence_metrics': {},
            'memory_enabled': self.memory_enabled
        }
        
        # Load previous state if exists
        self._load_state()
        
        # Initialise checkpoint system
        self._init_checkpoints()
    
    # ============================================================================
    # CHECKPOINT METHODS
    # ============================================================================
    
    def _init_checkpoints(self):
        """Initialise checkpoint system"""
        
        self.checkpoint_dir = self.config.output_dir / ".checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_checkpoint_dir = self.checkpoint_dir / "batches"
        self.batch_checkpoint_dir.mkdir(exist_ok=True)
    
    def _save_batch_checkpoint(self, phase: str, batch_num: int, 
                              batch_results: Dict, doc_ids: List[str]):
        """Save checkpoint after batch completes"""
        
        checkpoint_data = {
            'phase': phase,
            'batch_number': batch_num,
            'timestamp': datetime.now().isoformat(),
            'batch_results': batch_results,
            'processed_document_ids': doc_ids,
            'status': 'completed'
        }
        
        checkpoint_file = self.batch_checkpoint_dir / f"phase_{phase}_batch_{batch_num}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"      Checkpoint saved (Batch {batch_num})")
    
    def _load_checkpoint(self, phase: str) -> Optional[Dict]:
        """Load latest checkpoint for phase"""
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        
        if latest_file.exists():
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def _get_processed_docs(self, phase: str) -> List[str]:
        """Get list of already-processed document IDs"""
        
        checkpoint = self._load_checkpoint(phase)
        
        if checkpoint:
            return checkpoint.get('processed_document_ids', [])
        
        return []
    
    def _should_resume_phase(self, phase: str) -> Tuple[bool, Optional[Dict]]:
        """Check if phase should resume from checkpoint"""
        
        checkpoint = self._load_checkpoint(phase)
        
        if checkpoint:
            print(f"\n  Found checkpoint for Phase {phase}")
            print(f"    Last batch: {checkpoint.get('batch_number', 0)}")
            print(f"    Documents processed: {len(checkpoint.get('processed_document_ids', []))}")
            print(f"    Timestamp: {checkpoint.get('timestamp', 'N/A')}")
            
            response = input("\n  Resume from checkpoint? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                return True, checkpoint
        
        return False, None
    
    def _clear_phase_checkpoints(self, phase: str):
        """Clear checkpoints after successful phase completion"""
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        if latest_file.exists():
            latest_file.unlink()
        
        archive_dir = self.checkpoint_dir / "archive" / phase
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for checkpoint_file in self.batch_checkpoint_dir.glob(f"phase_{phase}_batch_*.json"):
            shutil.move(str(checkpoint_file), str(archive_dir / checkpoint_file.name))
    
    def _create_backup(self, phase: str):
        """Create backup before starting phase"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.config.output_dir / f"backup_phase_{phase}_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config.graph_db_path.exists():
            shutil.copy2(
                self.config.graph_db_path,
                backup_dir / "graph.db"
            )
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        if state_file.exists():
            shutil.copy2(state_file, backup_dir / "orchestrator_state.json")
        
        print(f"  Backup created: {backup_dir.name}")
    
    # ============================================================================
    # NEW: MEMORY-AWARE METHODS
    # ============================================================================
    
    def get_context_with_memory(self, 
                                query_text: str,
                                phase: str = None,
                                max_tokens: int = 100000) -> Dict[str, Any]:
        """
        Get context using memory system if available, otherwise fallback
        """
        if self.memory_enabled and self.memory_system:
            from memory import MemoryQuery
            
            memory_query = MemoryQuery(
                query_text=query_text,
                max_tokens=max_tokens,
                include_tiers=[1, 2, 3, 5]
            )
            
            result = self.memory_system.retrieve_relevant_context(memory_query)
            
            print(f"      Memory: {result['total_tokens']} tokens, "
                  f"saved £{result['cost_estimate']:.3f}, "
                  f"{result['retrieval_time_ms']:.0f}ms")
            
            return {
                'context': result['combined_context'],
                'tokens_used': result['total_tokens'],
                'cost_saved': result['cost_estimate'],
                'source': 'hierarchical_memory'
            }
        else:
            context = self.knowledge_graph.get_context_for_phase(phase or 'query')
            
            return {
                'context': context,
                'tokens_used': len(str(context)) // 4,
                'cost_saved': 0,
                'source': 'knowledge_graph_only'
            }
    
    def _cache_analysis_if_enabled(self, 
                                   query_text: str,
                                   response: str,
                                   phase: str,
                                   doc_ids: List[str] = None):
        """Cache analysis result if memory system enabled"""
        
        if self.memory_enabled and self.memory_system:
            try:
                self.memory_system.tier5.cache_analysis(
                    query_text=query_text,
                    analysis_result={'response': response, 'phase': phase},
                    document_ids=doc_ids,
                    model_used='claude-sonnet-4',
                    analysis_type=phase
                )
            except Exception as e:
                print(f"      Cache warning: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if not self.memory_system:
            return {'available': False}
        
        return self.memory_system.get_system_stats()
    
    # ============================================================================
    # MAIN EXECUTION METHOD
    # ============================================================================
    
    def execute_single_phase(self, phase: str) -> Dict:
        """Execute a single phase with full context"""
        
        print(f"\n[PHASE {phase}] Execution Starting")
        
        if phase == '0':
            return self._execute_knowledge_phase()
        elif phase == '1':
            return self._execute_phase_1_tiered()
        else:
            print(f"Unknown phase: {phase}")
            return {}
    
    # ============================================================================
    # PHASE EXECUTION WITH CHECKPOINTS AND MEMORY
    # ============================================================================
    
    def _execute_knowledge_phase(self) -> Dict:
        """Execute Phase 0: Combined knowledge absorption"""
        
        phase = '0'
        
        should_resume, checkpoint = self._should_resume_phase(phase)
        
        if not should_resume:
            self._create_backup(phase)
        
        legal_docs = self._load_documents(self.config.legal_knowledge_dir)
        case_docs = self._load_documents(self.config.case_context_dir)
        
        all_docs = legal_docs + case_docs
        
        print(f"  Total documents: {len(all_docs)}")
        
        processed_doc_ids = self._get_processed_docs(phase) if should_resume else []
        
        if processed_doc_ids:
            all_docs = [
                doc for doc in all_docs 
                if doc.get('id', doc.get('filename')) not in processed_doc_ids
            ]
            print(f"  Remaining documents: {len(all_docs)}")
        
        batches = self.batch_manager.create_semantic_batches(
            documents=all_docs,
            strategy='semantic_clustering'
        )
        
        start_batch = checkpoint.get('batch_number', 0) + 1 if should_resume else 1
        
        print(f"  Processing {len(batches)} batches (starting from batch {start_batch})")
        
        results = {
            'phase': phase,
            'documents_processed': len(processed_doc_ids),
            'batches_processed': start_batch - 1,
            'synthesis': '',
            'metadata': {}
        }
        
        for i, batch in enumerate(batches[start_batch-1:], start_batch):
            print(f"    Batch {i}/{len(batches)}: {len(batch)} documents")
            
            try:
                context_result = self.get_context_with_memory(
                    query_text=f"Phase {phase} knowledge synthesis",
                    phase=phase,
                    max_tokens=80000
                )
                existing_knowledge = context_result['context']
                
                prompt = self.autonomous_prompts.knowledge_synthesis_prompt(
                    legal_knowledge=legal_docs if i <= len(legal_docs)//20 else [],
                    case_context=case_docs if i > len(legal_docs)//20 else [],
                    existing_knowledge=existing_knowledge
                )
                
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='knowledge_synthesis',
                    phase=phase
                )
                
                batch_doc_ids = [doc.get('id', doc.get('filename', f'doc_{j}')) 
                               for j, doc in enumerate(batch)]
                
                self._cache_analysis_if_enabled(
                    query_text=f"Phase {phase} batch {i}",
                    response=response,
                    phase=phase,
                    doc_ids=batch_doc_ids
                )
                
                self._extract_knowledge_from_response(response, phase)
                
                processed_doc_ids.extend(batch_doc_ids)
                
                results['documents_processed'] += len(batch)
                results['batches_processed'] = i
                results['synthesis'] += response[:500] + "\n\n"
                
                self._save_batch_checkpoint(
                    phase=phase,
                    batch_num=i,
                    batch_results={'response_length': len(response)},
                    doc_ids=processed_doc_ids
                )
                
                if i < len(batches):
                    time.sleep(self.config.api_config['rate_limit_delay'])
            
            except Exception as e:
                print(f"      Error in batch {i}: {e}")
                print(f"      Progress saved up to batch {i-1}")
                raise
        
        self._clear_phase_checkpoints(phase)
        self._save_phase_output(phase, results)
        
        if phase not in self.state['phases_completed']:
            self.state['phases_completed'].append(phase)
        self._save_state()
        
        return results
    
    def _execute_phase_1_tiered(self) -> Dict:
        """Execute Phase 1: Three-tier disclosure analysis"""
        
        phase = '1'
        
        print("\n  Executing 3-tier analysis...")
        
        results = {
            'phase': phase,
            'tiers': {}
        }
        
        # Tier 1: Priority documents
        print("\n  [TIER 1] Deep analysis of priority documents")
        tier1_results = self._execute_tier(
            tier_num=1,
            phase=phase,
            doc_limit=500,
            analysis_depth='deep'
        )
        results['tiers']['tier_1'] = tier1_results
        
        # Tier 2: Metadata scan
        print("\n  [TIER 2] Metadata scan of remaining documents")
        tier2_results = self._execute_tier(
            tier_num=2,
            phase=phase,
            doc_limit=None,
            analysis_depth='shallow'
        )
        results['tiers']['tier_2'] = tier2_results
        
        # Tier 3: Flagged documents
        flagged = tier2_results.get('flagged_documents', [])
        if flagged:
            print(f"\n  [TIER 3] Deep dive on {len(flagged)} flagged documents")
            tier3_results = self._execute_tier(
                tier_num=3,
                phase=phase,
                specific_docs=flagged,
                analysis_depth='deep'
            )
            results['tiers']['tier_3'] = tier3_results
        
        if phase not in self.state['phases_completed']:
            self.state['phases_completed'].append(phase)
        self._save_state()
        
        return results
    
    def _execute_tier(self, 
                     tier_num: int,
                     phase: str,
                     doc_limit: int = None,
                     specific_docs: List = None,
                     analysis_depth: str = 'deep') -> Dict:
        """Execute a single tier of analysis"""
        
        tier_phase = f"{phase}_tier_{tier_num}"
        
        should_resume, checkpoint = self._should_resume_phase(tier_phase)
        
        if not should_resume:
            self._create_backup(tier_phase)
        
        if specific_docs:
            docs = specific_docs
        else:
            all_docs = self._load_documents(self.config.disclosure_dir)
            if doc_limit:
                docs = all_docs[:doc_limit]
            else:
                docs = all_docs
        
        processed_doc_ids = self._get_processed_docs(tier_phase) if should_resume else []
        
        if processed_doc_ids:
            docs = [
                doc for doc in docs 
                if doc.get('id', doc.get('filename')) not in processed_doc_ids
            ]
        
        batches = self.batch_manager.create_semantic_batches(
            documents=docs,
            strategy='semantic_clustering'
        )
        
        start_batch = checkpoint.get('batch_number', 0) + 1 if should_resume else 1
        
        results = {
            'tier': tier_num,
            'documents_analysed': len(processed_doc_ids),
            'batches_processed': start_batch - 1,
            'critical_findings': [],
            'contradictions': [],
            'flagged_documents': []
        }
        
        for i, batch in enumerate(batches[start_batch-1:], start_batch):
            print(f"      Batch {i}/{len(batches)}: {len(batch)} documents")
            
            try:
                context_result = self.get_context_with_memory(
                    query_text=f"Tier {tier_num} analysis",
                    phase=tier_phase,
                    max_tokens=100000
                )
                context = context_result['context']
                
                prompt = self.autonomous_prompts.investigation_prompt(
                    documents=batch,
                    context=context,
                    phase=tier_phase
                )
                
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='tier_analysis',
                    phase=tier_phase
                )
                
                batch_doc_ids = [doc.get('id', doc.get('filename', f'doc_{j}')) 
                               for j, doc in enumerate(batch)]
                
                self._cache_analysis_if_enabled(
                    query_text=f"Tier {tier_num} batch {i}",
                    response=response,
                    phase=tier_phase,
                    doc_ids=batch_doc_ids
                )
                
                discoveries = self._extract_discoveries_from_response(response, tier_phase)
                results['critical_findings'].extend(discoveries)
                
                processed_doc_ids.extend(batch_doc_ids)
                results['documents_analysed'] += len(batch)
                results['batches_processed'] = i
                
                self._save_batch_checkpoint(
                    phase=tier_phase,
                    batch_num=i,
                    batch_results={'discoveries': len(discoveries)},
                    doc_ids=processed_doc_ids
                )
                
                if i < len(batches):
                    time.sleep(self.config.api_config['rate_limit_delay'])
            
            except Exception as e:
                print(f"      Error in batch {i}: {e}")
                print(f"      Progress saved up to batch {i-1}")
                raise
        
        self._clear_phase_checkpoints(tier_phase)
        
        return results
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory"""
        
        loader = DocumentLoader(self.config)
        
        documents = loader.load_directory(
            directory=directory,
            doc_types=['.pdf', '.txt', '.docx', '.doc', '.json', '.html', '.md']
        )
        
        if not documents:
            print(f"  Warning: No documents loaded from {directory}")
        else:
            print(f"  Loaded {len(documents)} documents from {directory}")
            
            by_type = {}
            for doc in documents:
                ext = doc['metadata'].get('extension', 'unknown')
                by_type[ext] = by_type.get(ext, 0) + 1
            
            for ext, count in by_type.items():
                print(f"    - {ext}: {count} documents")
        
        return documents
    
    def _extract_knowledge_from_response(self, response: str, phase: str):
        """Extract and store knowledge from response"""
        pass
    
    def _extract_discoveries_from_response(self, response: str, phase: str) -> List[Dict]:
        """Extract discoveries from response"""
        return []
    
    def _save_phase_output(self, phase: str, results: Dict):
        """Save phase output to file"""
        
        phase_dir = self.config.analysis_dir / f"phase_{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        if 'synthesis' in results:
            synthesis_file = phase_dir / "synthesis.md"
            with open(synthesis_file, 'w', encoding='utf-8') as f:
                f.write(f"# Phase {phase} Analysis\n\n")
                f.write(f"*Documents Processed: {results.get('documents_processed', 0)}*\n\n")
                f.write("---\n\n")
                f.write(results['synthesis'])
        
        metadata_file = phase_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(results.get('metadata', {}), f, indent=2)
    
    def _save_state(self):
        """Save orchestrator state"""
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def _load_state(self):
        """Load orchestrator state if exists"""
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                saved_state = json.load(f)
                self.state.update(saved_state)