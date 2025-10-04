#!/usr/bin/env python3
"""
Main Orchestration Engine for Litigation Intelligence
PRODUCTION READY - All methods implemented
British English throughout
"""

import json
import time
import shutil
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
        
        # Hierarchical memory system (optional)
        self.memory_enabled = False
        self.memory_system = None
        try:
            from memory.hierarchical_system import HierarchicalMemory
            memory_path = self.config.root / "data" / "memory_tiers"
            self.memory_system = HierarchicalMemory(memory_path, self.config)
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
    # CRITICAL METHOD: SPAWN INVESTIGATION (NOW IMPLEMENTED)
    # ============================================================================
    
    def spawn_investigation(self, 
                          trigger_type: str,
                          trigger_data: Dict,
                          priority: float,
                          parent_id: str = None) -> str:
        """
        Spawn new investigation thread
        
        PRODUCTION READY IMPLEMENTATION
        
        Args:
            trigger_type: Type of trigger (contradiction, discovery, pattern, etc.)
            trigger_data: Data that triggered investigation
            priority: Investigation priority (0.0-10.0)
            parent_id: Parent investigation ID if this is a child
        
        Returns:
            Investigation ID
        """
        
        # Generate investigation ID
        trigger_hash = hashlib.md5(
            json.dumps(trigger_data, sort_keys=True).encode()
        ).hexdigest()[:8].upper()
        investigation_id = f"INV_{trigger_hash}"
        
        # Check if already exists
        if investigation_id in self.state['investigations']:
            print(f"    Investigation {investigation_id} already exists - skipping")
            return investigation_id
        
        # Determine depth
        depth = 0
        if parent_id and parent_id in self.state['investigations']:
            depth = self.state['investigations'][parent_id]['depth'] + 1
        
        # Create investigation record
        investigation = {
            'id': investigation_id,
            'type': trigger_type,
            'priority': priority,
            'status': 'active',
            'trigger_data': trigger_data,
            'parent_id': parent_id,
            'depth': depth,
            'created_at': datetime.now().isoformat(),
            'child_investigations': [],
            'findings': []
        }
        
        # Add to knowledge graph investigations table
        try:
            import sqlite3
            conn = sqlite3.connect(self.knowledge_graph.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO investigations (
                    investigation_id, trigger_type, trigger_data, priority,
                    status, spawned_from, depth, created
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                investigation_id,
                trigger_type,
                json.dumps(trigger_data),
                priority,
                'active',
                parent_id,
                depth,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"    ⚠️  Failed to add investigation to knowledge graph: {e}")
        
        # Store in state
        self.state['investigations'][investigation_id] = investigation
        
        # Update parent's children list
        if parent_id and parent_id in self.state['investigations']:
            self.state['investigations'][parent_id]['child_investigations'].append(
                investigation_id
            )
        
        self._save_state()
        
        print(f"    ✅ Investigation spawned: {investigation_id} (Priority: {priority}, Depth: {depth})")
        
        return investigation_id
    
    # ============================================================================
    # CRITICAL METHOD: EXTRACT KNOWLEDGE FROM RESPONSE (NOW IMPLEMENTED)
    # ============================================================================
    
    def _extract_knowledge_from_response(self, response: str, phase: str) -> None:
        """
        Extract and store knowledge from Claude response
        
        PRODUCTION READY IMPLEMENTATION
        
        Delegates to phase_executor for actual extraction,
        then ensures everything is stored in knowledge graph
        """
        
        try:
            # Use phase_executor's extraction methods
            if hasattr(self.phase_executor, '_process_knowledge_response'):
                self.phase_executor._process_knowledge_response(response, phase)
            else:
                # Fallback: manual extraction
                from intelligence.knowledge_graph import Entity, Relationship, Pattern, Contradiction
                
                # Extract contradictions
                contradictions = self.phase_executor.extract_contradictions(response)
                for contradiction in contradictions:
                    try:
                        self.knowledge_graph.add_contradiction(contradiction)
                    except Exception as e:
                        print(f"      ⚠️  Failed to add contradiction: {e}")
                
                # Extract patterns
                patterns = self.phase_executor.extract_patterns(response)
                for pattern in patterns:
                    try:
                        self.knowledge_graph.add_pattern(pattern)
                    except Exception as e:
                        print(f"      ⚠️  Failed to add pattern: {e}")
                
                # Extract entities and relationships
                entities, relationships = self.phase_executor.extract_entities_and_relationships(response)
                
                for entity_data in entities:
                    try:
                        # Convert dict to Entity object if needed
                        if isinstance(entity_data, dict):
                            entity = Entity(
                                entity_id=hashlib.md5(entity_data.get('name', 'unknown').encode()).hexdigest()[:16],
                                entity_type=entity_data.get('type', 'discovered'),
                                subtype='',
                                name=entity_data.get('name', 'Unknown'),
                                first_seen=datetime.now().isoformat(),
                                confidence=entity_data.get('suspicion', 0.5),
                                properties=entity_data,
                                discovery_phase=phase
                            )
                        else:
                            entity = entity_data
                        
                        self.knowledge_graph.add_entity(entity)
                    except Exception as e:
                        print(f"      ⚠️  Failed to add entity: {e}")
                
                for rel_data in relationships:
                    try:
                        # Convert dict to Relationship object if needed
                        if isinstance(rel_data, dict):
                            relationship = Relationship(
                                relationship_id=hashlib.md5(
                                    f"{rel_data.get('description', 'unknown')}".encode()
                                ).hexdigest()[:16],
                                source_entity='unknown',
                                target_entity='unknown',
                                relationship_type=rel_data.get('type', 'hidden'),
                                confidence=rel_data.get('strength', 0.7),
                                evidence=[rel_data.get('description', '')],
                                discovered=datetime.now().isoformat(),
                                properties=rel_data
                            )
                        else:
                            relationship = rel_data
                        
                        self.knowledge_graph.add_relationship(relationship)
                    except Exception as e:
                        print(f"      ⚠️  Failed to add relationship: {e}")
                
        except Exception as e:
            print(f"    ⚠️  Knowledge extraction error: {e}")
    
    # ============================================================================
    # CRITICAL METHOD: EXTRACT DISCOVERIES FROM RESPONSE (NOW IMPLEMENTED)
    # ============================================================================
    
    def _extract_discoveries_from_response(self, response: str, phase: str) -> List[Dict]:
        """
        Extract discovery markers from Claude response
        
        PRODUCTION READY IMPLEMENTATION
        
        Returns list of discoveries with type and content
        """
        
        discoveries = []
        
        # Discovery markers
        markers = {
            'NUCLEAR': r'\[NUCLEAR\]\s*([^\[]+)',
            'CRITICAL': r'\[CRITICAL\]\s*([^\[]+)',
            'PATTERN': r'\[PATTERN\]\s*([^\[]+)',
            'SUSPICIOUS': r'\[SUSPICIOUS\]\s*([^\[]+)',
            'MISSING': r'\[MISSING\]\s*([^\[]+)',
            'TIMELINE': r'\[TIMELINE\]\s*([^\[]+)',
            'FINANCIAL': r'\[FINANCIAL\]\s*([^\[]+)',
            'ADMISSION': r'\[ADMISSION\]\s*([^\[]+)',
            'RELATIONSHIP': r'\[RELATIONSHIP\]\s*([^\[]+)',
            'INVESTIGATE': r'\[INVESTIGATE\]\s*([^\[]+)'
        }
        
        import re
        
        for discovery_type, pattern in markers.items():
            matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                content = match.strip()[:1000]  # Limit to 1000 chars
                
                discovery = {
                    'type': discovery_type,
                    'content': content,
                    'phase': phase,
                    'timestamp': datetime.now().isoformat()
                }
                
                discoveries.append(discovery)
                
                # Log to knowledge graph discovery_log
                try:
                    importance_map = {
                        'NUCLEAR': 'NUCLEAR',
                        'CRITICAL': 'CRITICAL',
                        'PATTERN': 'HIGH',
                        'SUSPICIOUS': 'MEDIUM',
                        'MISSING': 'HIGH',
                        'TIMELINE': 'HIGH',
                        'FINANCIAL': 'HIGH',
                        'ADMISSION': 'CRITICAL',
                        'RELATIONSHIP': 'MEDIUM',
                        'INVESTIGATE': 'HIGH'
                    }
                    
                    importance = importance_map.get(discovery_type, 'MEDIUM')
                    
                    self.knowledge_graph.log_discovery(
                        discovery_type=discovery_type,
                        content=content,
                        importance=importance,
                        phase=phase
                    )
                except Exception as e:
                    print(f"      ⚠️  Failed to log discovery: {e}")
        
        return discoveries
    
    # ============================================================================
    # CHECKPOINT & STATE MANAGEMENT
    # ============================================================================
    
    def _save_batch_checkpoint(self, 
                               phase: str,
                               batch_num: int,
                               batch_results: Dict,
                               doc_ids: List[str]) -> None:
        """Save batch-level checkpoint"""
        
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
    
    def _clear_phase_checkpoints(self, phase: str) -> None:
        """Clear checkpoints after successful phase completion"""
        
        latest_file = self.batch_checkpoint_dir / f"phase_{phase}_latest.json"
        if latest_file.exists():
            latest_file.unlink()
        
        archive_dir = self.checkpoint_dir / "archive" / phase
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for checkpoint_file in self.batch_checkpoint_dir.glob(f"phase_{phase}_batch_*.json"):
            shutil.move(str(checkpoint_file), str(archive_dir / checkpoint_file.name))
    
    def _create_backup(self, phase: str) -> None:
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
    
    def _save_phase_output(self, phase: str, results: Dict) -> None:
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
                include_tiers=[1, 2, 3, 5]
            )
            
            result = self.memory_system.retrieve_relevant_context(memory_query)
            
            print(f"      Memory: {result['total_tokens']} tokens, "
                  f"saved £{result['cost_estimate_saved']:.2f}")
            
            return result
        else:
            # Fallback to knowledge graph only
            return {
                'context': self.knowledge_graph.get_context_for_phase(phase or 'general'),
                'total_tokens': 0,
                'cost_estimate_saved': 0.0
            }
    
    def _cache_analysis_if_enabled(self,
                                   query_text: str,
                                   response: str,
                                   phase: str,
                                   doc_ids: List[str]) -> None:
        """Cache analysis if memory system enabled"""
        
        if self.memory_enabled and self.memory_system:
            try:
                self.memory_system.store_analysis(
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