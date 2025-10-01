#!/usr/bin/env python3
"""
SQLite-based Knowledge Graph for Litigation Intelligence
Maximises Claude's memory and analytical potential
COMPLETE FIXED VERSION - All SQL issues resolved
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib


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
    """SQLite-based knowledge graph with versioning and auto-investigation"""
    
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
        
        # Entities table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                subtype TEXT,
                name TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                properties TEXT,
                discovery_phase TEXT,
                suspicion_score REAL DEFAULT 0.0,
                investigation_count INTEGER DEFAULT 0
            )
        """)
        
        # Relationships table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                source_entity TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                evidence TEXT,
                discovered TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                properties TEXT,
                strength REAL DEFAULT 0.5,
                FOREIGN KEY (source_entity) REFERENCES entities(entity_id),
                FOREIGN KEY (target_entity) REFERENCES entities(entity_id)
            )
        """)
        
        # Contradictions table - FIXED with investigation_status
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
        
        # Patterns table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                supporting_evidence TEXT,
                contradicting_evidence TEXT,
                evolution_history TEXT,
                investigation_spawned BOOLEAN DEFAULT 0,
                discovered TEXT NOT NULL,
                last_confirmed TEXT,
                decay_rate REAL DEFAULT 0.0
            )
        """)
        
        # Timeline events table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                event_id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                entities_involved TEXT,
                documents TEXT,
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
                trigger_data TEXT,
                priority REAL NOT NULL,
                status TEXT DEFAULT 'active',
                spawned_from TEXT,
                depth INTEGER DEFAULT 0,
                created TEXT NOT NULL,
                completed TEXT,
                findings TEXT,
                child_investigations TEXT
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
        
        # Discovery log table
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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(relationship_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_contradiction_severity ON contradictions(severity)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_confidence ON patterns(confidence)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_investigation_priority ON investigations(priority)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_date ON timeline_events(date)")
        
        conn.commit()
        conn.close()
    
    def add_entity(self, entity: Entity) -> str:
        """Add or update entity with automatic investigation triggering"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if entity exists
        cursor.execute("SELECT entity_id, confidence FROM entities WHERE entity_id = ?", 
                      (entity.entity_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entity
            old_confidence = existing[1]
            new_confidence = min(1.0, old_confidence + 0.1)
            
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
        
        conn.commit()
        conn.close()
        return entity.entity_id
    
    def add_relationship(self, relationship: Relationship) -> str:
        """Add relationship between entities"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate relationship strength
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
        
        conn.commit()
        conn.close()
        return relationship.relationship_id
    
    def add_contradiction(self, contradiction: Contradiction) -> str:
        """
        Add contradiction with automatic investigation spawning
        FIXED VERSION - includes investigation_status field
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate investigation priority
        priority = contradiction.severity / 10.0 * 10  # Convert to 0-10 scale
        contradiction.investigation_priority = priority
        
        # FIXED: Added investigation_status field to INSERT
        cursor.execute("""
            INSERT INTO contradictions (
                contradiction_id, statement_a, statement_b, doc_a, doc_b,
                severity, confidence, implications, investigation_priority,
                discovered, investigation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contradiction.contradiction_id, contradiction.statement_a,
            contradiction.statement_b, contradiction.doc_a, contradiction.doc_b,
            contradiction.severity, contradiction.confidence,
            contradiction.implications, priority, contradiction.discovered,
            'pending'  # FIXED: Default status
        ))
        
        conn.commit()
        
        # Spawn investigation if severity exceeds threshold
        if contradiction.severity >= 7:
            self._spawn_investigation(
                trigger_type="contradiction",
                trigger_data=asdict(contradiction),
                priority=priority
            )
        
        # Log as discovery if critical
        if contradiction.severity >= 8:
            self.log_discovery(
                discovery_type="contradiction",
                content=f"{contradiction.statement_a[:100]} vs {contradiction.statement_b[:100]}",
                importance="CRITICAL" if contradiction.severity >= 9 else "HIGH",
                phase=contradiction.discovered.split('_')[0] if '_' in contradiction.discovered else "unknown"
            )
        
        conn.close()
        return contradiction.contradiction_id
    
    def add_pattern(self, pattern: Pattern) -> str:
        """Add pattern with confidence evolution tracking"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO patterns (
                pattern_id, pattern_type, description, confidence,
                supporting_evidence, contradicting_evidence, evolution_history,
                investigation_spawned, discovered, last_confirmed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern.pattern_id, pattern.pattern_type, pattern.description,
            pattern.confidence, json.dumps(pattern.supporting_evidence),
            json.dumps(pattern.contradicting_evidence), 
            json.dumps(pattern.evolution_history),
            pattern.investigation_spawned, pattern.discovered,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return pattern.pattern_id
    
    def add_timeline_event(self,
                          date: str,
                          description: str,
                          entities: List[str] = None,
                          documents: List[str] = None,
                          is_critical: bool = False) -> str:
        """Add timeline event"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        event_id = hashlib.md5(f"{date}{description}".encode()).hexdigest()[:16]
        
        cursor.execute("""
            INSERT OR REPLACE INTO timeline_events (
                event_id, date, description, entities_involved,
                documents, confidence, is_critical, discovered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id, date, description,
            json.dumps(entities or []),
            json.dumps(documents or []),
            0.7, is_critical, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return event_id
    
    def _spawn_investigation(self,
                           trigger_type: str,
                           trigger_data: Dict,
                           priority: float,
                           parent_id: str = None) -> str:
        """Spawn new investigation thread"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        investigation_id = f"INV_{hashlib.md5(str(trigger_data).encode()).hexdigest()[:8].upper()}"
        
        # Calculate depth
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
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        stats['entities'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        stats['relationships'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contradictions")
        stats['contradictions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patterns")
        stats['patterns'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM timeline_events")
        stats['timeline_events'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM investigations WHERE status = 'active'")
        stats['active_investigations'] = cursor.fetchone()[0]
        
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
        
        conn.close()
        return context
    
    def export_for_report(self) -> Dict[str, Any]:
        """Export knowledge graph for report generation"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        export = {
            'summary': self.get_statistics(),
            'critical_findings': [],
            'key_contradictions': [],
            'strong_patterns': []
        }
        
        # Export discoveries
        cursor.execute("""
            SELECT discovery_type, content, importance, phase
            FROM discovery_log
            WHERE importance IN ('NUCLEAR', 'CRITICAL')
            ORDER BY timestamp DESC
            LIMIT 20
        """)
        export['critical_findings'] = [
            {'type': row[0], 'content': row[1], 'importance': row[2], 'phase': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Export contradictions
        cursor.execute("""
            SELECT statement_a, statement_b, severity, implications
            FROM contradictions
            WHERE severity >= 7
            ORDER BY severity DESC
            LIMIT 15
        """)
        export['key_contradictions'] = [
            {'statement_a': row[0], 'statement_b': row[1], 'severity': row[2], 'implications': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Export patterns
        cursor.execute("""
            SELECT description, confidence, supporting_evidence
            FROM patterns
            WHERE confidence > 0.7
            ORDER BY confidence DESC
            LIMIT 15
        """)
        export['strong_patterns'] = [
            {'description': row[0], 'confidence': row[1], 'evidence': json.loads(row[2])}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return export
    
    def _get_current_version(self) -> int:
        """Get current version number"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(version_id) FROM version_history")
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result[0] else 0