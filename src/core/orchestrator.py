#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
UPDATED: Now supports priority document loading
PRODUCTION READY - All methods implemented
British English throughout - Lismore v Process Holdings
"""

import json
import time
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib

from core.config import Config
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
        self.config = Config()
        if config_override:
            for key, value in config_override.items():
                setattr(self.config, key, value)
        
        # Initialise core components
        self.knowledge_graph = KnowledgeGraph(self.config)
        self.api_client = ClaudeClient(self.config)
        self.context_manager = ContextManager(self.config)
        self.batch_manager = BatchManager(self.config)
        self.phase_executor = PhaseExecutor(self.config, self)
        
        # Initialise prompt systems
        self.autonomous_prompts = AutonomousPrompts(self.config)
        self.recursive_prompts = RecursivePrompts(self.config)
        self.synthesis_prompts = SynthesisPrompts(self.config)
        
        # Document loader
        self.document_loader = DocumentLoader(self.config)
        
        # Hierarchical memory system (optional)
        self.memory_enabled = False
        self.memory_system = None
        try:
            from memory.hierarchical_system import HierarchicalMemory
            self.memory_system = HierarchicalMemory(self.config, self.knowledge_graph)
            self.memory_enabled = True
            print("✅ Hierarchical Memory System ACTIVE")
        except ImportError:
            print("ℹ️  Hierarchical Memory System not available (optional)")
        except Exception as e:
            print(f"⚠️  Memory system initialisation failed: {e}")
        
        # State tracking
        self.state = {
            'phases_completed': [],
            'current_phase': None,
            'investigations': {},
            'total_cost_gbp': 0.0
        }
        self._load_state()
        
        # Checkpoint directories
        self.checkpoint_dir = self.config.output_dir / "checkpoints"
        self.batch_checkpoint_dir = self.checkpoint_dir / "batches"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.batch_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # ============================================================================
    # MAIN EXECUTION METHODS
    # ============================================================================
    
    def execute_single_phase(self, phase: str) -> Dict:
        """Execute single phase with context building"""
        
        print(f"\n{'='*70}")
        print(f"EXECUTING PHASE {phase}")
        print(f"{'='*70}\n")
        
        self.state['current_phase'] = phase
        
        # Build context from knowledge graph
        context = self.knowledge_graph.get_context_for_phase(phase)
        
        # Execute via phase executor
        results = self.phase_executor.execute(phase, context)
        
        # Update state
        if phase not in self.state['phases_completed']:
            self.state['phases_completed'].append(phase)
        
        self._save_state()
        
        return results
    
    # ============================================================================
    # CRITICAL METHOD: SPAWN INVESTIGATION
    # ============================================================================
    
    def spawn_investigation(self, 
                          trigger_type: str,
                          trigger_data: Dict,
                          priority: float,
                          parent_id: str = None) -> str:
        """
        Spawn new investigation thread
        
        Args:
            trigger_type: Type of trigger (contradiction, discovery, pattern, etc.)
            trigger_data: Data that triggered the investigation
            priority: Priority score (0.0-10.0)
            parent_id: Optional parent investigation ID
            
        Returns:
            Investigation ID
        """
        
        # Generate investigation ID
        inv_id = self._generate_investigation_id(trigger_type)
        
        investigation = {
            'id': inv_id,
            'type': trigger_type,
            'priority': priority,
            'data': trigger_data,
            'parent_id': parent_id,
            'status': 'active',
            'created': datetime.now().isoformat(),
            'findings': []
        }
        
        self.state['investigations'][inv_id] = investigation
        
        print(f"    🔍 Spawned investigation: {inv_id} (priority: {priority})")
        
        return inv_id
    
    def _generate_investigation_id(self, trigger_type: str) -> str:
        """Generate unique investigation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"INV_{trigger_type.upper()}_{timestamp}_{random_hash}"
    
    # ============================================================================
    # DOCUMENT LOADING (WITH PRIORITISATION SUPPORT)
    # ============================================================================
    
    def load_priority_documents_only(self, directory: Path) -> List[Dict]:
        """
        NEW: Load only priority documents based on prioritisation
        
        If priority_documents.json exists, loads only those documents.
        Otherwise falls back to loading all documents.
        
        Args:
            directory: Directory to load from
            
        Returns:
            List of document dicts
        """
        
        priority_file = self.config.output_dir / "priority_documents.json"
        
        if not priority_file.exists():
            print("  ℹ️  No priority list found - loading all documents")
            return self._load_documents(directory)
        
        # Load priority list
        with open(priority_file, 'r', encoding='utf-8') as f:
            priority_data = json.load(f)
        
        priority_filenames = set(
            doc['filename'] for doc in priority_data['documents']
        )
        
        print(f"  ✅ Priority list found: {len(priority_filenames)} documents")
        
        # Load only priority documents
        priority_docs = []
        
        for pattern in ['*.pdf', '*.txt', '*.docx', '*.doc']:
            for file_path in sorted(directory.glob(f"**/{pattern}")):
                if file_path.name in priority_filenames:
                    try:
                        doc = self.document_loader.load_document(file_path)
                        if doc:
                            priority_docs.append(doc)
                    except Exception as e:
                        print(f"  ⚠️  Failed to load {file_path.name}: {e}")
        
        print(f"  Loaded {len(priority_docs)} priority documents")
        
        return priority_docs
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load documents from directory (standard loading)"""
        
        documents = self.document_loader.load_directory(
            directory=directory,
            doc_types=['.pdf', '.txt', '.docx', '.doc', '.json', '.html', '.md']
        )
        
        if not documents:
            print(f"  Warning: No documents loaded from {directory}")
        else:
            print(f"  Loaded {len(documents)} documents from {directory}")
            
            # Show breakdown by type
            by_type = {}
            for doc in documents:
                ext = doc['metadata'].get('extension', 'unknown')
                by_type[ext] = by_type.get(ext, 0) + 1
            
            for ext, count in by_type.items():
                print(f"    - {ext}: {count} documents")
        
        return documents
    
    # ============================================================================
    # CHECKPOINT MANAGEMENT
    # ============================================================================
    
    def _save_batch_checkpoint(self, phase: str, batch_num: int, results: Dict) -> None:
        """Save checkpoint after batch completion"""
        
        checkpoint = {
            'phase': phase,
            'batch': batch_num,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'state': self.state
        }
        
        checkpoint_file = self.batch_checkpoint_dir / f"phase_{phase}_batch_{batch_num}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)
        
        # Also save as "latest" for easy resume
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)
    
    def _check_for_resume(self, phase: str) -> Tuple[bool, Optional[Dict]]:
        """Check if there's a checkpoint to resume from"""
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        
        if not latest_file.exists():
            return False, None
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        print(f"\n⚠️  Found checkpoint from {checkpoint['timestamp']}")
        print(f"  Last completed batch: {checkpoint['batch']}")
        
        # Ask user if they want to resume
        if sys.stdin.isatty():  # Only ask if interactive
            response = input(f"Resume from checkpoint? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                return True, checkpoint
        
        return False, None
    
    def _clear_phase_checkpoints(self, phase: str) -> None:
        """Clear checkpoints after successful phase completion"""
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        if latest_file.exists():
            latest_file.unlink()
        
        # Archive batch checkpoints
        archive_dir = self.checkpoint_dir / "archive" / phase
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for checkpoint_file in self.batch_checkpoint_dir.glob(f"phase_{phase}_batch_*.json"):
            shutil.move(str(checkpoint_file), str(archive_dir / checkpoint_file.name))
    
    def _create_backup(self, phase: str) -> None:
        """Create backup before starting phase"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.config.output_dir / f"backup_phase_{phase}_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup knowledge graph
        if self.config.graph_db_path.exists():
            shutil.copy2(
                self.config.graph_db_path,
                backup_dir / "graph.db"
            )
        
        # Backup state
        state_file = self.config.output_dir / ".orchestrator_state.json"
        if state_file.exists():
            shutil.copy2(state_file, backup_dir / "orchestrator_state.json")
        
        print(f"  Backup created: {backup_dir.name}")
    
    # ============================================================================
    # STATE MANAGEMENT
    # ============================================================================
    
    def _save_state(self) -> None:
        """Save orchestrator state"""
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def _load_state(self) -> None:
        """Load orchestrator state if exists"""
        
        state_file = self.config.output_dir / ".orchestrator_state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                saved_state = json.load(f)
                self.state.update(saved_state)
    
    # ============================================================================
    # MEMORY INTEGRATION (OPTIONAL)
    # ============================================================================
    
    def get_context_with_memory(self, 
                                query_text: str,
                                phase: str = None,
                                max_tokens: int = 100000) -> Dict[str, Any]:
        """Get context using memory system if available"""
        
        if self.memory_enabled and self.memory_system:
            from memory import MemoryQuery
            
            memory_query = MemoryQuery(
                query_text=query_text,
                max_tokens=max_tokens,
                include_tiers=[1, 2, 3, 5]  # Skip Tier 4 (cold storage) by default
            )
            
            result = self.memory_system.retrieve_relevant_context(memory_query)
            
            print(f"      Memory: {result['total_tokens']} tokens, "
                  f"saved ~£{result.get('cost_estimate', 0.0):.2f}")
            
            return result
        else:
            # Fallback to knowledge graph only
            return {
                'context': self.knowledge_graph.get_context_for_phase(phase or 'general'),
                'total_tokens': 0,
                'cost_estimate': 0.0
            }
    
    def _cache_analysis_if_enabled(self,
                                   query_text: str,
                                   response: str,
                                   phase: str,
                                   doc_ids: List[str]) -> None:
        """Cache analysis if memory system enabled"""
        
        if self.memory_enabled and self.memory_system:
            try:
                # Store in Tier 5 (Analysis Cache)
                self.memory_system.tier5.cache_analysis(
                    query=query_text,
                    response=response,
                    metadata={
                        'phase': phase,
                        'document_ids': doc_ids,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            except Exception as e:
                print(f"      ⚠️  Cache storage failed: {e}")