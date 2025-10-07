#!/usr/bin/env python3
"""
ENHANCED Knowledge Graph - Replace src/intelligence/knowledge_graph.py
Adds: Better document retrieval support, memory integration, investigation storage
British English throughout - Lismore v Process Holdings
"""

import sqlite3
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


class KnowledgeGraph:
    """Enhanced knowledge graph with document retrieval and memory integration"""
    
    def __init__(self, config):
        """Initialise knowledge graph"""
        self.config = config
        self.db_path = config.output_dir / "knowledge_graph.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.root = Path(config.project_root)
        self.backup_dir = config.output_dir / "graph_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialise database
        self._init_database()
    
    def _init_database(self):
        """Initialise SQLite database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Discovery log (documents)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_log (
                doc_id TEXT PRIMARY KEY,
                filename TEXT,
                folder TEXT,
                content TEXT,
                preview TEXT,
                importance INTEGER DEFAULT 5,
                triage_score INTEGER,
                category TEXT,
                indexed_date TEXT,
                metadata_json TEXT
            )
        """)
        
        # Patterns (breaches, findings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                description TEXT,
                pattern_type TEXT,
                confidence REAL,
                supporting_docs TEXT,
                first_seen TEXT,
                last_updated TEXT,
                metadata_json TEXT
            )
        """)
        
        # Contradictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contradictions (
                contradiction_id TEXT PRIMARY KEY,
                statement_a TEXT,
                statement_b TEXT,
                doc_id_a TEXT,
                doc_id_b TEXT,
                severity INTEGER,
                explanation TEXT,
                identified_date TEXT,
                FOREIGN KEY (doc_id_a) REFERENCES discovery_log(doc_id),
                FOREIGN KEY (doc_id_b) REFERENCES discovery_log(doc_id)
            )
        """)
        
        # Timeline events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                event_id TEXT PRIMARY KEY,
                date TEXT,
                description TEXT,
                event_type TEXT,
                significance INTEGER,
                supporting_docs TEXT,
                metadata_json TEXT
            )
        """)
        
        # Entities (people, companies, amounts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_name TEXT,
                entity_type TEXT,
                first_mentioned TEXT,
                mention_count INTEGER DEFAULT 0,
                related_docs TEXT,
                metadata_json TEXT
            )
        """)
        
        # Relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                entity_a TEXT,
                entity_b TEXT,
                relationship_type TEXT,
                strength REAL,
                supporting_docs TEXT,
                FOREIGN KEY (entity_a) REFERENCES entities(entity_id),
                FOREIGN KEY (entity_b) REFERENCES entities(entity_id)
            )
        """)
        
        # Investigation results (NEW)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investigation_results (
                investigation_id TEXT PRIMARY KEY,
                topic TEXT,
                conclusion TEXT,
                confidence REAL,
                depth INTEGER,
                parent_id TEXT,
                completed_date TEXT,
                metadata_json TEXT
            )
        """)
        
        # Create indices for fast retrieval
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_date ON timeline_events(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contradictions_severity ON contradictions(severity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discovery_category ON discovery_log(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discovery_importance ON discovery_log(importance)")
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # ========================================================================
    # DOCUMENT MANAGEMENT
    # ========================================================================
    
    def add_document(self, doc: Dict):
        """Add document to discovery log"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO discovery_log
            (doc_id, filename, folder, content, preview, importance, 
             triage_score, category, indexed_date, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.get('doc_id'),
            doc.get('filename'),
            doc.get('folder'),
            doc.get('content'),
            doc.get('preview'),
            doc.get('importance', 5),
            doc.get('triage_score', 0),
            doc.get('category', 'other'),
            datetime.now().isoformat(),
            json.dumps(doc.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents for indexing"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT doc_id, filename, content, preview, category, importance
            FROM discovery_log
        """)
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'doc_id': row[0],
                'filename': row[1],
                'content': row[2],
                'preview': row[3],
                'category': row[4],
                'importance': row[5]
            })
        
        conn.close()
        return documents
    
    def get_documents_by_ids(self, doc_ids: List[str]) -> List[Dict]:
        """Get specific documents by their IDs"""
        if not doc_ids:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(doc_ids))
        cursor.execute(f"""
            SELECT doc_id, filename, content, preview, category
            FROM discovery_log
            WHERE doc_id IN ({placeholders})
        """, doc_ids)
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'doc_id': row[0],
                'filename': row[1],
                'content': row[2],
                'preview': row[3],
                'category': row[4]
            })
        
        conn.close()
        return documents
    
    def get_documents_for_investigation(self, topic: str) -> List[str]:
        """
        Get relevant document IDs for investigation topic
        NOTE: This now works with BM25 search in pass_executor
        Returns empty list - pass_executor will use BM25 instead
        """
        # This is intentionally simple - the BM25 algorithm in pass_executor
        # does the heavy lifting for document retrieval
        return []
    
    # ========================================================================
    # PATTERN MANAGEMENT
    # ========================================================================
    
    def add_pattern(self, pattern: Dict):
        """Add pattern (breach, finding) to knowledge graph"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        pattern_id = pattern.get('pattern_id') or self._generate_id('pattern')
        
        cursor.execute("""
            INSERT OR REPLACE INTO patterns
            (pattern_id, description, pattern_type, confidence, 
             supporting_docs, first_seen, last_updated, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            pattern.get('description'),
            pattern.get('pattern_type', 'breach'),
            pattern.get('confidence', 0.0),
            json.dumps(pattern.get('supporting_docs', [])),
            pattern.get('first_seen', datetime.now().isoformat()),
            datetime.now().isoformat(),
            json.dumps(pattern.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return pattern_id
    
    # ========================================================================
    # CONTRADICTION MANAGEMENT
    # ========================================================================
    
    def add_contradiction(self, contradiction: Dict):
        """Add contradiction to knowledge graph"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        contra_id = contradiction.get('contradiction_id') or self._generate_id('contradiction')
        
        cursor.execute("""
            INSERT OR REPLACE INTO contradictions
            (contradiction_id, statement_a, statement_b, doc_id_a, doc_id_b,
             severity, explanation, identified_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contra_id,
            contradiction.get('statement_a'),
            contradiction.get('statement_b'),
            contradiction.get('doc_id_a'),
            contradiction.get('doc_id_b'),
            contradiction.get('severity', 5),
            contradiction.get('explanation', ''),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return contra_id
    
    # ========================================================================
    # TIMELINE MANAGEMENT
    # ========================================================================
    
    def add_timeline_event(self, event: Dict):
        """Add timeline event to knowledge graph"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        event_id = event.get('event_id') or self._generate_id('event')
        
        cursor.execute("""
            INSERT OR REPLACE INTO timeline_events
            (event_id, date, description, event_type, significance,
             supporting_docs, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            event.get('date'),
            event.get('description'),
            event.get('event_type', 'general'),
            event.get('significance', 5),
            json.dumps(event.get('supporting_docs', [])),
            json.dumps(event.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return event_id
    
    # ========================================================================
    # INVESTIGATION RESULTS STORAGE (NEW)
    # ========================================================================
    
    def store_investigation_result(self, result: Dict):
        """Store investigation result"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO investigation_results
            (investigation_id, topic, conclusion, confidence, depth,
             parent_id, completed_date, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.get('investigation_id'),
            result.get('topic'),
            result.get('conclusion'),
            result.get('confidence', 0.0),
            result.get('depth', 0),
            result.get('parent_id'),
            datetime.now().isoformat(),
            json.dumps(result.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # CONTEXT RETRIEVAL FOR ANALYSIS
    # ========================================================================
    
    def get_context_for_analysis(self) -> Dict:
        """
        Get accumulated context for Pass 2 iterations
        Returns most relevant patterns, contradictions, timeline events
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        context = {
            'patterns': [],
            'contradictions': [],
            'timeline_events': [],
            'statistics': {}
        }
        
        # Get high-confidence patterns (breaches)
        cursor.execute("""
            SELECT pattern_id, description, confidence, supporting_docs
            FROM patterns
            WHERE confidence > 0.5
            ORDER BY confidence DESC
            LIMIT 50
        """)
        
        for row in cursor.fetchall():
            try:
                supporting_docs = json.loads(row[3])
            except:
                supporting_docs = []
            
            context['patterns'].append({
                'id': row[0],
                'description': row[1],
                'confidence': row[2],
                'supporting_docs': supporting_docs
            })
        
        # Get critical contradictions
        cursor.execute("""
            SELECT contradiction_id, statement_a, statement_b, severity
            FROM contradictions
            WHERE severity >= 7
            ORDER BY severity DESC
            LIMIT 20
        """)
        
        for row in cursor.fetchall():
            context['contradictions'].append({
                'id': row[0],
                'statement_a': row[1][:200],
                'statement_b': row[2][:200],
                'severity': row[3]
            })
        
        # Get timeline events
        cursor.execute("""
            SELECT event_id, date, description, significance
            FROM timeline_events
            ORDER BY date DESC
            LIMIT 30
        """)
        
        for row in cursor.fetchall():
            context['timeline_events'].append({
                'id': row[0],
                'date': row[1],
                'description': row[2],
                'significance': row[3]
            })
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM patterns")
        context['statistics']['total_patterns'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contradictions")
        context['statistics']['total_contradictions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM timeline_events")
        context['statistics']['total_timeline_events'] = cursor.fetchone()[0]
        
        conn.close()
        return context
    
    def get_context_for_phase(self, phase: str) -> Dict:
        """Alias for get_context_for_analysis for backwards compatibility"""
        return self.get_context_for_analysis()
    
    # ========================================================================
    # INTEGRATION METHOD (CRITICAL FOR PASS 2)
    # ========================================================================
    
    def integrate_analysis(self, iteration_result: Dict):
        """
        Integrate Pass 2 iteration results into knowledge graph
        This is called after each iteration to accumulate findings
        """
        # Store breaches as patterns
        for breach in iteration_result.get('breaches', []):
            pattern = {
                'description': breach.get('description'),
                'pattern_type': 'breach',
                'confidence': breach.get('confidence', 0.0),
                'supporting_docs': breach.get('evidence', []),
                'metadata': {
                    'clause': breach.get('clause'),
                    'causation': breach.get('causation'),
                    'quantum': breach.get('quantum')
                }
            }
            self.add_pattern(pattern)
        
        # Store contradictions
        for contra in iteration_result.get('contradictions', []):
            docs = contra.get('documents', [])
            contradiction = {
                'statement_a': contra.get('statement_a'),
                'statement_b': contra.get('statement_b'),
                'doc_id_a': docs[0] if len(docs) > 0 else None,
                'doc_id_b': docs[1] if len(docs) > 1 else None,
                'severity': contra.get('severity', 5),
                'explanation': contra.get('explanation', '')
            }
            self.add_contradiction(contradiction)
        
        # Store timeline events
        for event in iteration_result.get('timeline_events', []):
            timeline_event = {
                'date': event.get('date'),
                'description': event.get('description'),
                'event_type': event.get('type', 'general'),
                'significance': event.get('significance', 5),
                'supporting_docs': event.get('documents', [])
            }
            self.add_timeline_event(timeline_event)
        
        # Store novel arguments as patterns
        for argument in iteration_result.get('novel_arguments', []):
            pattern = {
                'description': argument.get('argument'),
                'pattern_type': 'novel_argument',
                'confidence': argument.get('strength', 0.7),
                'supporting_docs': argument.get('supporting_evidence', []),
                'metadata': {
                    'tactical_value': argument.get('tactical_value', 'medium')
                }
            }
            self.add_pattern(pattern)
    
    # ========================================================================
    # EXPORT METHODS
    # ========================================================================
    
    def export_complete(self) -> Dict:
        """
        Export complete intelligence for Pass 3 and Pass 4
        Returns all accumulated knowledge
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        intelligence = {
            'patterns': [],
            'contradictions': [],
            'timeline_events': [],
            'investigations': [],
            'statistics': {}
        }
        
        # Export all patterns
        cursor.execute("""
            SELECT pattern_id, description, pattern_type, confidence, 
                   supporting_docs, metadata_json
            FROM patterns
            ORDER BY confidence DESC
        """)
        
        for row in cursor.fetchall():
            try:
                supporting_docs = json.loads(row[4])
                metadata = json.loads(row[5])
            except:
                supporting_docs = []
                metadata = {}
            
            intelligence['patterns'].append({
                'id': row[0],
                'description': row[1],
                'type': row[2],
                'confidence': row[3],
                'supporting_docs': supporting_docs,
                'metadata': metadata
            })
        
        # Export all contradictions
        cursor.execute("""
            SELECT contradiction_id, statement_a, statement_b, 
                   doc_id_a, doc_id_b, severity, explanation
            FROM contradictions
            ORDER BY severity DESC
        """)
        
        for row in cursor.fetchall():
            intelligence['contradictions'].append({
                'id': row[0],
                'statement_a': row[1],
                'statement_b': row[2],
                'doc_id_a': row[3],
                'doc_id_b': row[4],
                'severity': row[5],
                'explanation': row[6]
            })
        
        # Export all timeline events
        cursor.execute("""
            SELECT event_id, date, description, event_type, 
                   significance, supporting_docs
            FROM timeline_events
            ORDER BY date
        """)
        
        for row in cursor.fetchall():
            try:
                supporting_docs = json.loads(row[5])
            except:
                supporting_docs = []
            
            intelligence['timeline_events'].append({
                'id': row[0],
                'date': row[1],
                'description': row[2],
                'type': row[3],
                'significance': row[4],
                'supporting_docs': supporting_docs
            })
        
        # Export investigation results
        cursor.execute("""
            SELECT investigation_id, topic, conclusion, confidence, depth
            FROM investigation_results
            ORDER BY confidence DESC
        """)
        
        for row in cursor.fetchall():
            intelligence['investigations'].append({
                'id': row[0],
                'topic': row[1],
                'conclusion': row[2],
                'confidence': row[3],
                'depth': row[4]
            })
        
        # Add statistics
        intelligence['statistics'] = {
            'total_patterns': len(intelligence['patterns']),
            'total_contradictions': len(intelligence['contradictions']),
            'total_timeline_events': len(intelligence['timeline_events']),
            'total_investigations': len(intelligence['investigations'])
        }
        
        conn.close()
        return intelligence
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Get knowledge graph statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM discovery_log")
        stats['documents'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patterns")
        stats['patterns'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contradictions")
        stats['contradictions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM timeline_events")
        stats['timeline_events'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        stats['entities'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        stats['relationships'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM investigation_results")
        stats['investigations'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def backup_before_phase(self, phase: str) -> str:
        """Create backup before major phase"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"graph_backup_{phase}_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        
        return str(backup_path)
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{prefix}_{timestamp}"
        hash_obj = hashlib.md5(hash_input.encode())
        return f"{prefix}_{hash_obj.hexdigest()[:8]}"
    
    def _get_context_from_memory(self, query: str, max_tokens: int = 50000) -> Dict:
        """
        Get context from HierarchicalMemory system
        Falls back to knowledge graph if memory unavailable
        """
        try:
            if hasattr(self.orchestrator, 'memory_enabled') and self.orchestrator.memory_enabled:
                print("   📚 Querying HierarchicalMemory system...")
                context = self.orchestrator.retrieve_memory_context(
                    query_text=query,
                    max_tokens=max_tokens,
                    tiers=[1, 2, 3, 5]
                )
                
                if 'intelligence' in context:
                    return context['intelligence']
                else:
                    return self.knowledge_graph.export_complete_intelligence()
            else:
                print("   📚 Using knowledge graph...")
                return self.knowledge_graph.export_complete_intelligence()
                
        except Exception as e:
            print(f"   ⚠️  Memory error: {e}, using fallback")
            return self.knowledge_graph.export_complete_intelligence()
    
    def _check_cache_before_analysis(self, query_key: str) -> Optional[Dict]:
        """Check if analysis already cached"""
        try:
            if hasattr(self.orchestrator, 'memory_enabled') and self.orchestrator.memory_enabled:
                cached = self.orchestrator.check_analysis_cache(query_key)
                if cached:
                    print(f"   🎯 CACHE HIT (£0 cost)")
                    return cached
                else:
                    print(f"   💰 Cache miss (£2-3 cost)")
            return None
        except Exception as e:
            print(f"   ⚠️  Cache error: {e}")
            return None
    
    def _store_in_cache(self, query_key: str, result: Dict, analysis_type: str):
        """Store analysis in cache"""
        try:
            if hasattr(self.orchestrator, 'memory_enabled') and self.orchestrator.memory_enabled:
                self.orchestrator.store_analysis_in_cache(
                    query=query_key,
                    analysis_result=result,
                    analysis_type=analysis_type
                )
                print(f"   💾 Cached for future use")
        except Exception as e:
            print(f"   ⚠️  Cache storage error: {e}")