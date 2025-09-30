#!/usr/bin/env python3
"""
SQLite-based Knowledge Graph for Litigation Intelligence
Maximises Claude's memory and analytical potential - Lismore v Process Holdings
Enhanced with comprehensive query methods for knowledge retrieval
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib
import re


@dataclass
class Entity:
    """Entity in the knowledge graph"""
    entity_id: str
    entity_type: str
    subtype: str
    name: str
    first_seen: str
    confidence: float
    properties: Dict[str, Any]
    discovery_phase: str


@dataclass
class Relationship:
    """Relationship between entities"""
    relationship_id: str
    source_entity: str
    target_entity: str
    relationship_type: str
    confidence: float
    evidence: List[str]
    discovered: str
    properties: Dict[str, Any]


@dataclass
class Contradiction:
    """Contradiction in evidence"""
    contradiction_id: str
    statement_a: str
    statement_b: str
    doc_a: str
    doc_b: str
    severity: int  # 1-10
    confidence: float
    implications: str
    investigation_priority: float
    discovered: str


@dataclass
class Pattern:
    """Identified pattern across documents"""
    pattern_id: str
    pattern_type: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    evolution_history: List[Dict[str, Any]]
    investigation_spawned: bool
    discovered: str


class KnowledgeGraph:
    """SQLite-based knowledge graph with versioning, auto-investigation, and enhanced querying"""
    
    def __init__(self, config):
        """Initialise knowledge graph with SQLite backend"""
        self.config = config
        self.db_path = config.graph_db_path
        self.backup_dir = config.backups_dir
        
        # Initialise database
        self._init_database()
        
        # Track active investigations
        self.active_investigations = []
        
        # Version tracking
        self.current_version = self._get_current_version()
    
    def _init_database(self) -> None:
        """Create SQLite database schema optimised for Claude's analysis"""
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        
        # Entities table - expandable entity types
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                subtype TEXT,
                name TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                properties TEXT,  -- JSON
                discovery_phase TEXT,
                suspicion_score REAL DEFAULT 0.0,
                investigation_count INTEGER DEFAULT 0
            )
        """)
        
        # Relationships table - connections between entities
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                source_entity TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                evidence TEXT,  -- JSON list
                discovered TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                properties TEXT,  -- JSON
                strength REAL DEFAULT 0.5,
                FOREIGN KEY (source_entity) REFERENCES entities(entity_id),
                FOREIGN KEY (target_entity) REFERENCES entities(entity_id)
            )
        """)
        
        # Contradictions table - track inconsistencies
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contradictions (
                contradiction_id TEXT PRIMARY KEY,
                statement_a TEXT NOT NULL,
                statement_b TEXT NOT NULL,
                doc_a TEXT NOT NULL,
                doc_b TEXT NOT NULL,
                severity INTEGER CHECK(severity >= 1 AND severity <= 10),
                confidence REAL DEFAULT 0.5,
                implications TEXT,
                investigation_priority REAL,
                investigation_status TEXT DEFAULT 'pending',
                discovered TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                resolution TEXT
            )
        """)
        
        # Patterns table - identified patterns with evolution tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                supporting_evidence TEXT,  -- JSON list
                contradicting_evidence TEXT,  -- JSON list
                evolution_history TEXT,  -- JSON list
                investigation_spawned BOOLEAN DEFAULT 0,
                discovered TEXT NOT NULL,
                last_confirmed TEXT,
                decay_rate REAL DEFAULT 0.0  -- How fast confidence decreases
            )
        """)
        
        # Timeline events table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                event_id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                entities_involved TEXT,  -- JSON list
                documents TEXT,  -- JSON list
                confidence REAL DEFAULT 0.5,
                is_critical BOOLEAN DEFAULT 0,
                discovered TEXT NOT NULL,
                impossibility_flag BOOLEAN DEFAULT 0
            )
        """)
        
        # Investigation threads table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                investigation_id TEXT PRIMARY KEY,
                trigger_type TEXT NOT NULL,
                trigger_data TEXT,  -- JSON
                priority REAL NOT NULL,
                status TEXT DEFAULT 'active',
                spawned_from TEXT,  -- Parent investigation
                depth INTEGER DEFAULT 0,
                created TEXT NOT NULL,
                completed TEXT,
                findings TEXT,  -- JSON
                child_investigations TEXT  -- JSON list
            )
        """)
        
        # Version history table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS version_history (
                version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                changes_summary TEXT,
                backup_path TEXT,
                entity_count INTEGER,
                relationship_count INTEGER,
                contradiction_count INTEGER,
                pattern_count INTEGER
            )
        """)
        
        # Discovery log table - tracks all significant findings
        conn.execute("""
            CREATE TABLE IF NOT EXISTS discovery_log (
                discovery_id TEXT PRIMARY KEY,
                discovery_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance TEXT CHECK(importance IN ('NUCLEAR', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
                phase TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                actionable BOOLEAN DEFAULT 1,
                actioned BOOLEAN DEFAULT 0
            )
        """)
        
        # Create indices for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_suspicion ON entities(suspicion_score)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)")  # NEW index
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(relationship_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_contradiction_severity ON contradictions(severity)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_confidence ON patterns(confidence)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_investigation_priority ON investigations(priority)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_date ON timeline_events(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_discovery_importance ON discovery_log(importance)")  # NEW index
        
        conn.commit()
        conn.close()
    
    # ============================================================
    # EXISTING METHODS - Kept unchanged
    # ============================================================
    
    def add_entity(self, entity: Entity) -> str:
        """Add or update entity with automatic investigation triggering"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if entity exists
        cursor.execute("SELECT entity_id, confidence FROM entities WHERE entity_id = ?", (entity.entity_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entity, potentially increasing confidence
            old_confidence = existing[1]
            new_confidence = min(1.0, old_confidence + 0.1)  # Increase confidence with each mention
            
            cursor.execute("""
                UPDATE entities 
                SET confidence = ?, last_updated = ?, properties = ?
                WHERE entity_id = ?
            """, (new_confidence, datetime.now().isoformat(), 
                  json.dumps(entity.properties), entity.entity_id))
        else:
            # Insert new entity
            cursor.execute("""
                INSERT INTO entities (
                    entity_id, entity_type, subtype, name, first_seen, 
                    last_updated, confidence, properties, discovery_phase
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.entity_id, entity.entity_type, entity.subtype,
                entity.name, entity.first_seen, datetime.now().isoformat(),
                entity.confidence, json.dumps(entity.properties),
                entity.discovery_phase
            ))
            
            # Check if new entity type should spawn investigation
            if entity.entity_type not in self.config.base_entities:
                self._spawn_investigation(
                    trigger_type="new_entity_type",
                    trigger_data={"entity": asdict(entity)},
                    priority=6.0
                )
        
        conn.commit()
        conn.close()
        return entity.entity_id
    
    def add_relationship(self, relationship: Relationship) -> str:
        """Add relationship between entities"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate relationship strength based on evidence
        strength = min(1.0, len(relationship.evidence) * 0.2)
        
        cursor.execute("""
            INSERT OR REPLACE INTO relationships (
                relationship_id, source_entity, target_entity, 
                relationship_type, confidence, evidence, discovered, 
                last_updated, properties, strength
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            relationship.relationship_id, relationship.source_entity,
            relationship.target_entity, relationship.relationship_type,
            relationship.confidence, json.dumps(relationship.evidence),
            relationship.discovered, datetime.now().isoformat(),
            json.dumps(relationship.properties), strength
        ))
        
        # Update entity suspicion scores if suspicious relationship
        suspicious_types = ['payment_to', 'controlled_by', 'conspired_with', 'hid_from']
        if relationship.relationship_type in suspicious_types:
            cursor.execute("""
                UPDATE entities 
                SET suspicion_score = MIN(1.0, suspicion_score + 0.2)
                WHERE entity_id IN (?, ?)
            """, (relationship.source_entity, relationship.target_entity))
        
        conn.commit()
        conn.close()
        return relationship.relationship_id
    
    def add_contradiction(self, contradiction: Contradiction) -> str:
        """Add contradiction with automatic investigation spawning"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate investigation priority
        priority = self.config.calculate_priority({
            'contradiction_severity': contradiction.severity,
            'financial_impact': 'financial' in contradiction.implications.lower(),
            'timeline_critical': 'date' in contradiction.statement_a.lower() or 'date' in contradiction.statement_b.lower()
        })
        
        contradiction.investigation_priority = priority
        
        cursor.execute("""
            INSERT INTO contradictions (
                contradiction_id, statement_a, statement_b, doc_a, doc_b,
                severity, confidence, implications, investigation_priority,
                discovered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contradiction.contradiction_id, contradiction.statement_a,
            contradiction.statement_b, contradiction.doc_a, contradiction.doc_b,
            contradiction.severity, contradiction.confidence,
            contradiction.implications, priority, contradiction.discovered
        ))
        
        conn.commit()
        
        # Spawn investigation if severity exceeds threshold
        if contradiction.severity > self.config.investigation_triggers['contradiction_severity']:
            self._spawn_investigation(
                trigger_type="contradiction",
                trigger_data=asdict(contradiction),
                priority=priority
            )
        
        # Log as discovery if critical
        if contradiction.severity >= 8:
            self.log_discovery(
                discovery_type="contradiction",
                content=f"{contradiction.statement_a} vs {contradiction.statement_b}",
                importance="CRITICAL" if contradiction.severity >= 9 else "HIGH",
                phase=contradiction.discovered.split('_')[0] if '_' in contradiction.discovered else "unknown"
            )
        
        conn.close()
        return contradiction.contradiction_id
    
    def add_pattern(self, pattern: Pattern) -> str:
        """Add pattern with confidence evolution tracking"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists and should evolve
        cursor.execute("SELECT pattern_id, confidence, evolution_history FROM patterns WHERE pattern_id = ?", 
                      (pattern.pattern_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update pattern confidence based on new evidence
            old_confidence = existing[1]
            history = json.loads(existing[2]) if existing[2] else []
            
            # Calculate new confidence
            supporting = len(pattern.supporting_evidence)
            contradicting = len(pattern.contradicting_evidence)
            
            if supporting + contradicting > 0:
                new_confidence = supporting / (supporting + contradicting)
            else:
                new_confidence = old_confidence
            
            # Add to evolution history
            history.append({
                'timestamp': datetime.now().isoformat(),
                'old_confidence': old_confidence,
                'new_confidence': new_confidence,
                'evidence_added': len(pattern.supporting_evidence)
            })
            
            cursor.execute("""
                UPDATE patterns 
                SET confidence = ?, supporting_evidence = ?, 
                    contradicting_evidence = ?, evolution_history = ?,
                    last_confirmed = ?
                WHERE pattern_id = ?
            """, (
                new_confidence, json.dumps(pattern.supporting_evidence),
                json.dumps(pattern.contradicting_evidence),
                json.dumps(history), datetime.now().isoformat(),
                pattern.pattern_id
            ))
            
            # Check if confidence change warrants investigation
            if abs(new_confidence - old_confidence) > 0.3:
                self._spawn_investigation(
                    trigger_type="pattern_evolution",
                    trigger_data={"pattern": asdict(pattern), "confidence_delta": new_confidence - old_confidence},
                    priority=7.0
                )
        else:
            # Insert new pattern
            cursor.execute("""
                INSERT INTO patterns (
                    pattern_id, pattern_type, description, confidence,
                    supporting_evidence, contradicting_evidence,
                    evolution_history, investigation_spawned, discovered
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id, pattern.pattern_type, pattern.description,
                pattern.confidence, json.dumps(pattern.supporting_evidence),
                json.dumps(pattern.contradicting_evidence),
                json.dumps([{'timestamp': datetime.now().isoformat(), 
                           'initial_confidence': pattern.confidence}]),
                False, pattern.discovered
            ))
            
            # Spawn investigation if confidence exceeds threshold
            if pattern.confidence > self.config.investigation_triggers['pattern_confidence']:
                self._spawn_investigation(
                    trigger_type="pattern",
                    trigger_data=asdict(pattern),
                    priority=pattern.confidence * 10
                )
                cursor.execute("UPDATE patterns SET investigation_spawned = 1 WHERE pattern_id = ?",
                             (pattern.pattern_id,))
        
        conn.commit()
        conn.close()
        return pattern.pattern_id
    
    def add_timeline_event(self, date: str, description: str, entities: List[str], 
                           documents: List[str], is_critical: bool = False) -> str:
        """Add timeline event with impossibility checking"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        event_id = hashlib.md5(f"{date}{description}".encode()).hexdigest()[:16]
        
        # Check for timeline impossibilities
        cursor.execute("""
            SELECT event_id, date, description FROM timeline_events 
            WHERE date = ? AND entities_involved LIKE ?
        """, (date, f'%{entities[0]}%' if entities else '%'))
        
        conflicts = cursor.fetchall()
        impossibility = len(conflicts) > 0 and any(
            'signed' in desc[2].lower() and 'signed' in description.lower()
            for desc in conflicts
        )
        
        cursor.execute("""
            INSERT INTO timeline_events (
                event_id, date, description, entities_involved,
                documents, confidence, is_critical, discovered,
                impossibility_flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id, date, description, json.dumps(entities),
            json.dumps(documents), 0.8, is_critical,
            datetime.now().isoformat(), impossibility
        ))
        
        if impossibility:
            # Timeline impossibility triggers immediate investigation
            self._spawn_investigation(
                trigger_type="timeline_impossibility",
                trigger_data={
                    'event': description,
                    'date': date,
                    'conflicts': conflicts
                },
                priority=9.0
            )
        
        conn.commit()
        conn.close()
        return event_id
    
    def _spawn_investigation(self, trigger_type: str, trigger_data: Dict, 
                           priority: float, parent_id: str = None) -> str:
        """Spawn new investigation thread"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        investigation_id = hashlib.md5(
            f"{trigger_type}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Determine depth
        depth = 0
        if parent_id:
            cursor.execute("SELECT depth FROM investigations WHERE investigation_id = ?", (parent_id,))
            parent_depth = cursor.fetchone()
            depth = (parent_depth[0] if parent_depth else 0) + 1
        
        cursor.execute("""
            INSERT INTO investigations (
                investigation_id, trigger_type, trigger_data, priority,
                status, spawned_from, depth, created
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            investigation_id, trigger_type, json.dumps(trigger_data),
            priority, 'active', parent_id, depth,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.active_investigations.append(investigation_id)
        return investigation_id
    
    def get_investigation_queue(self, limit: int = 5) -> List[Dict]:
        """Get highest priority investigations to pursue"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT investigation_id, trigger_type, trigger_data, priority
            FROM investigations
            WHERE status = 'active'
            ORDER BY priority DESC
            LIMIT ?
        """, (limit,))
        
        investigations = []
        for row in cursor.fetchall():
            investigations.append({
                'id': row[0],
                'type': row[1],
                'data': json.loads(row[2]) if row[2] else {},
                'priority': row[3]
            })
        
        conn.close()
        return investigations
    
    def complete_investigation(self, investigation_id: str, findings: Dict) -> None:
        """Mark investigation as complete with findings"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE investigations
            SET status = 'complete', completed = ?, findings = ?
            WHERE investigation_id = ?
        """, (datetime.now().isoformat(), json.dumps(findings), investigation_id))
        
        conn.commit()
        conn.close()
        
        if investigation_id in self.active_investigations:
            self.active_investigations.remove(investigation_id)
    
    def log_discovery(self, discovery_type: str, content: str, 
                     importance: str, phase: str) -> None:
        """Log significant discoveries"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        discovery_id = hashlib.md5(
            f"{discovery_type}{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        cursor.execute("""
            INSERT INTO discovery_log (
                discovery_id, discovery_type, content, importance,
                phase, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            discovery_id, discovery_type, content, importance,
            phase, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def backup_before_phase(self, phase: str) -> str:
        """Create versioned backup before phase execution"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"graph_backup_phase_{phase}_{timestamp}.db"
        
        # Copy database
        shutil.copy2(self.db_path, backup_path)
        
        # Record version
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current statistics
        stats = self.get_statistics()
        
        cursor.execute("""
            INSERT INTO version_history (
                phase, timestamp, changes_summary, backup_path,
                entity_count, relationship_count, contradiction_count,
                pattern_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            phase, datetime.now().isoformat(),
            f"Backup before phase {phase}", str(backup_path),
            stats['entities'], stats['relationships'],
            stats['contradictions'], stats['patterns']
        ))
        
        conn.commit()
        conn.close()
        
        return str(backup_path)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get current graph statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count entities
        cursor.execute("SELECT COUNT(*) FROM entities")
        stats['entities'] = cursor.fetchone()[0]
        
        # Count relationships
        cursor.execute("SELECT COUNT(*) FROM relationships")
        stats['relationships'] = cursor.fetchone()[0]
        
        # Count contradictions
        cursor.execute("SELECT COUNT(*) FROM contradictions")
        stats['contradictions'] = cursor.fetchone()[0]
        
        # Count patterns
        cursor.execute("SELECT COUNT(*) FROM patterns")
        stats['patterns'] = cursor.fetchone()[0]
        
        # Count timeline events
        cursor.execute("SELECT COUNT(*) FROM timeline_events")
        stats['timeline_events'] = cursor.fetchone()[0]
        
        # Count active investigations
        cursor.execute("SELECT COUNT(*) FROM investigations WHERE status = 'active'")
        stats['active_investigations'] = cursor.fetchone()[0]
        
        # Count discoveries
        cursor.execute("SELECT COUNT(*) FROM discovery_log")
        stats['discoveries'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def get_context_for_phase(self, phase: str) -> Dict[str, Any]:
        """Generate rich context for Claude from knowledge graph"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics()
        }
        
        # Get high-suspicion entities
        cursor.execute("""
            SELECT entity_id, name, entity_type, suspicion_score
            FROM entities
            WHERE suspicion_score > 0.5
            ORDER BY suspicion_score DESC
            LIMIT 10
        """)
        context['suspicious_entities'] = [
            {'id': row[0], 'name': row[1], 'type': row[2], 'suspicion': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Get critical contradictions
        cursor.execute("""
            SELECT contradiction_id, statement_a, statement_b, severity
            FROM contradictions
            WHERE severity >= 7 AND resolved = 0
            ORDER BY severity DESC
            LIMIT 10
        """)
        context['critical_contradictions'] = [
            {'id': row[0], 'statement_a': row[1][:100], 
             'statement_b': row[2][:100], 'severity': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Get high-confidence patterns
        cursor.execute("""
            SELECT pattern_id, description, confidence
            FROM patterns
            WHERE confidence > 0.7
            ORDER BY confidence DESC
            LIMIT 10
        """)
        context['strong_patterns'] = [
            {'id': row[0], 'description': row[1][:200], 'confidence': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Get timeline impossibilities
        cursor.execute("""
            SELECT event_id, date, description
            FROM timeline_events
            WHERE impossibility_flag = 1
            LIMIT 10
        """)
        context['timeline_impossibilities'] = [
            {'id': row[0], 'date': row[1], 'description': row[2][:100]}
            for row in cursor.fetchall()
        ]
        
        # Get active investigations
        cursor.execute("""
            SELECT investigation_id, trigger_type, priority
            FROM investigations
            WHERE status = 'active'
            ORDER BY priority DESC
            LIMIT 5
        """)
        context['active_investigations'] = [
            {'id': row[0], 'type': row[1], 'priority': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Get recent critical discoveries
        cursor.execute("""
            SELECT discovery_type, content, importance
            FROM discovery_log
            WHERE importance IN ('NUCLEAR', 'CRITICAL')
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        context['critical_discoveries'] = [
            {'type': row[0], 'content': row[1][:200], 'importance': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return context
    
    def _get_current_version(self) -> int:
        """Get current version number"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(version_id) FROM version_history")
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result[0] else 0
    
    def export_for_report(self) -> Dict[str, Any]:
        """Export key findings for report generation"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        export = {
            'summary': self.get_statistics(),
            'generated': datetime.now().isoformat()
        }
        
        # Export critical findings
        cursor.execute("""
            SELECT * FROM discovery_log
            WHERE importance IN ('NUCLEAR', 'CRITICAL')
            ORDER BY timestamp DESC
        """)
        export['critical_findings'] = [dict(row) for row in cursor.fetchall()]
        
        # Export key contradictions
        cursor.execute("""
            SELECT * FROM contradictions
            WHERE severity >= 8
            ORDER BY severity DESC
        """)
        export['key_contradictions'] = [dict(row) for row in cursor.fetchall()]
        
        # Export strong patterns
        cursor.execute("""
            SELECT * FROM patterns
            WHERE confidence > 0.8
            ORDER BY confidence DESC
        """)
        export['strong_patterns'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return export
    
    # ============================================================
    # NEW QUERY METHODS - Enhanced retrieval capabilities
    # ============================================================
    
    def search_by_entity(self, entity_name: str, limit: int = 50) -> Dict[str, Any]:
        """Search knowledge graph by entity name or ID"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = {
            'entity': None,
            'relationships': [],
            'timeline_events': [],
            'patterns': [],
            'contradictions': [],
            'discoveries': []
        }
        
        # Find entity (search by name or ID)
        cursor.execute("""
            SELECT * FROM entities 
            WHERE name LIKE ? OR entity_id = ?
            ORDER BY confidence DESC
            LIMIT 1
        """, (f'%{entity_name}%', entity_name))
        
        entity = cursor.fetchone()
        if entity:
            results['entity'] = dict(entity)
            entity_id = entity['entity_id']
            
            # Find relationships
            cursor.execute("""
                SELECT * FROM relationships 
                WHERE source_entity = ? OR target_entity = ?
                ORDER BY strength DESC
                LIMIT ?
            """, (entity_id, entity_id, limit))
            
            results['relationships'] = [dict(row) for row in cursor.fetchall()]
            
            # Find timeline events
            cursor.execute("""
                SELECT * FROM timeline_events 
                WHERE entities_involved LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, (f'%{entity_name}%', limit))
            
            results['timeline_events'] = [dict(row) for row in cursor.fetchall()]
            
            # Find patterns mentioning entity
            cursor.execute("""
                SELECT * FROM patterns 
                WHERE description LIKE ?
                ORDER BY confidence DESC
                LIMIT ?
            """, (f'%{entity_name}%', limit))
            
            results['patterns'] = [dict(row) for row in cursor.fetchall()]
            
            # Find contradictions involving entity
            cursor.execute("""
                SELECT * FROM contradictions 
                WHERE statement_a LIKE ? OR statement_b LIKE ?
                ORDER BY severity DESC
                LIMIT ?
            """, (f'%{entity_name}%', f'%{entity_name}%', limit))
            
            results['contradictions'] = [dict(row) for row in cursor.fetchall()]
            
            # Find discoveries mentioning entity
            cursor.execute("""
                SELECT * FROM discovery_log 
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f'%{entity_name}%', limit))
            
            results['discoveries'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def search_by_topic(self, topic: str, limit: int = 50) -> Dict[str, Any]:
        """Search knowledge graph by topic or keyword"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        topic_pattern = f'%{topic}%'
        
        results = {
            'patterns': [],
            'contradictions': [],
            'timeline_events': [],
            'discoveries': [],
            'entities': []
        }
        
        # Search patterns
        cursor.execute("""
            SELECT * FROM patterns 
            WHERE description LIKE ? OR pattern_type LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        """, (topic_pattern, topic_pattern, limit))
        
        results['patterns'] = [dict(row) for row in cursor.fetchall()]
        
        # Search contradictions
        cursor.execute("""
            SELECT * FROM contradictions 
            WHERE statement_a LIKE ? OR statement_b LIKE ? OR implications LIKE ?
            ORDER BY severity DESC
            LIMIT ?
        """, (topic_pattern, topic_pattern, topic_pattern, limit))
        
        results['contradictions'] = [dict(row) for row in cursor.fetchall()]
        
        # Search timeline events
        cursor.execute("""
            SELECT * FROM timeline_events 
            WHERE description LIKE ?
            ORDER BY date DESC
            LIMIT ?
        """, (topic_pattern, limit))
        
        results['timeline_events'] = [dict(row) for row in cursor.fetchall()]
        
        # Search discoveries
        cursor.execute("""
            SELECT * FROM discovery_log 
            WHERE content LIKE ? OR discovery_type LIKE ?
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        """, (topic_pattern, topic_pattern, limit))
        
        results['discoveries'] = [dict(row) for row in cursor.fetchall()]
        
        # Search entities
        cursor.execute("""
            SELECT * FROM entities 
            WHERE properties LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        """, (topic_pattern, limit))
        
        results['entities'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_contradictions_about(self, subject: str, limit: int = 20) -> List[Dict]:
        """Get contradictions related to a specific subject"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM contradictions 
            WHERE statement_a LIKE ? OR statement_b LIKE ? OR implications LIKE ?
            ORDER BY severity DESC, investigation_priority DESC
            LIMIT ?
        """, (f'%{subject}%', f'%{subject}%', f'%{subject}%', limit))
        
        contradictions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return contradictions
    
    def get_timeline_window(self, start_date: str, end_date: str) -> List[Dict]:
        """Get all events within a date range"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM timeline_events 
            WHERE date >= ? AND date <= ?
            ORDER BY date ASC
        """, (start_date, end_date))
        
        events = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return events
    
    def get_related_documents(self, doc_id: str, limit: int = 10) -> List[Dict]:
        """Get documents related to a specific document"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find all references to this document
        results = []
        
        # In contradictions
        cursor.execute("""
            SELECT 'contradiction' as source_type, * FROM contradictions 
            WHERE doc_a = ? OR doc_b = ?
            LIMIT ?
        """, (doc_id, doc_id, limit))
        
        for row in cursor.fetchall():
            results.append(dict(row))
        
        # In timeline events
        cursor.execute("""
            SELECT 'timeline' as source_type, * FROM timeline_events 
            WHERE documents LIKE ?
            LIMIT ?
        """, (f'%{doc_id}%', limit))
        
        for row in cursor.fetchall():
            results.append(dict(row))
        
        # In pattern evidence
        cursor.execute("""
            SELECT 'pattern' as source_type, * FROM patterns 
            WHERE supporting_evidence LIKE ? OR contradicting_evidence LIKE ?
            LIMIT ?
        """, (f'%{doc_id}%', f'%{doc_id}%', limit))
        
        for row in cursor.fetchall():
            results.append(dict(row))
        
        conn.close()
        return results[:limit]
    
    def get_entity_network(self, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get network of entities connected to a specific entity"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        network = {
            'center': None,
            'direct_connections': [],
            'secondary_connections': []
        }
        
        # Get center entity
        cursor.execute("SELECT * FROM entities WHERE entity_id = ?", (entity_id,))
        center = cursor.fetchone()
        
        if center:
            network['center'] = dict(center)
            
            # Get direct connections
            cursor.execute("""
                SELECT DISTINCT e.*, r.relationship_type, r.confidence as rel_confidence
                FROM relationships r
                JOIN entities e ON (
                    CASE 
                        WHEN r.source_entity = ? THEN r.target_entity = e.entity_id
                        WHEN r.target_entity = ? THEN r.source_entity = e.entity_id
                    END
                )
                WHERE r.source_entity = ? OR r.target_entity = ?
            """, (entity_id, entity_id, entity_id, entity_id))
            
            direct_entities = []
            for row in cursor.fetchall():
                entity_dict = dict(row)
                direct_entities.append(entity_dict)
                network['direct_connections'].append(entity_dict)
            
            # Get secondary connections if depth > 1
            if depth > 1:
                for entity in direct_entities:
                    cursor.execute("""
                        SELECT DISTINCT e.*
                        FROM relationships r
                        JOIN entities e ON (
                            CASE 
                                WHEN r.source_entity = ? THEN r.target_entity = e.entity_id
                                WHEN r.target_entity = ? THEN r.source_entity = e.entity_id
                            END
                        )
                        WHERE (r.source_entity = ? OR r.target_entity = ?)
                        AND e.entity_id != ?
                        LIMIT 10
                    """, (entity['entity_id'], entity['entity_id'], 
                         entity['entity_id'], entity['entity_id'], entity_id))
                    
                    for row in cursor.fetchall():
                        network['secondary_connections'].append(dict(row))
        
        conn.close()
        return network
    
    def get_critical_discoveries(self, importance_levels: List[str] = None, 
                                limit: int = 50) -> List[Dict]:
        """Get critical discoveries filtered by importance"""
        
        if importance_levels is None:
            importance_levels = ['NUCLEAR', 'CRITICAL', 'HIGH']
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(importance_levels))
        cursor.execute(f"""
            SELECT * FROM discovery_log 
            WHERE importance IN ({placeholders})
            ORDER BY 
                CASE importance 
                    WHEN 'NUCLEAR' THEN 1 
                    WHEN 'CRITICAL' THEN 2 
                    WHEN 'HIGH' THEN 3 
                    WHEN 'MEDIUM' THEN 4 
                    WHEN 'LOW' THEN 5 
                END,
                timestamp DESC
            LIMIT ?
        """, (*importance_levels, limit))
        
        discoveries = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return discoveries
    
    def get_pattern_evolution(self, pattern_id: str) -> Dict[str, Any]:
        """Get evolution history of a specific pattern"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patterns WHERE pattern_id = ?", (pattern_id,))
        pattern = cursor.fetchone()
        
        result = {}
        if pattern:
            result = dict(pattern)
            # Parse evolution history JSON
            if result.get('evolution_history'):
                result['evolution_history'] = json.loads(result['evolution_history'])
            if result.get('supporting_evidence'):
                result['supporting_evidence'] = json.loads(result['supporting_evidence'])
            if result.get('contradicting_evidence'):
                result['contradicting_evidence'] = json.loads(result['contradicting_evidence'])
        
        conn.close()
        return result
    
    def search_investigations(self, status: str = 'active', 
                            min_priority: float = 0.0) -> List[Dict]:
        """Search investigations by status and priority"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM investigations 
            WHERE status = ? AND priority >= ?
            ORDER BY priority DESC
        """, (status, min_priority))
        
        investigations = []
        for row in cursor.fetchall():
            inv = dict(row)
            # Parse JSON fields
            if inv.get('trigger_data'):
                inv['trigger_data'] = json.loads(inv['trigger_data'])
            if inv.get('findings'):
                inv['findings'] = json.loads(inv['findings'])
            investigations.append(inv)
        
        conn.close()
        return investigations