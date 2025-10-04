#!/usr/bin/env python3
"""
SQLite-based Knowledge Graph for Litigation Intelligence
Extended with litigation-specific tables for Lismore v Process Holdings
British English throughout
COMPLETE VERSION - All litigation tables included
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
    """SQLite-based knowledge graph with litigation intelligence extensions"""
    
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
        """Create SQLite database schema with litigation tables"""
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        
        cursor = conn.cursor()
        
        # =====================================================================
        # CORE TABLES (Original)
        # =====================================================================
        
        # Entities table
        cursor.execute("""
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
        cursor.execute("""
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
        
        # Contradictions table
        cursor.execute("""
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
        cursor.execute("""
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
        
        # Timeline events table (basic)
        cursor.execute("""
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
        cursor.execute("""
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
        cursor.execute("""
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
        cursor.execute("""
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
        
        # =====================================================================
        # LITIGATION-SPECIFIC TABLES (NEW for Lismore case)
        # =====================================================================
        
        # Detailed timeline events (for impossibility detection)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events_detailed (
                event_id TEXT PRIMARY KEY,
                event_date TEXT NOT NULL,
                event_time TEXT,
                event_description TEXT NOT NULL,
                location TEXT,
                participants TEXT,
                source_doc_ids TEXT,
                confidence REAL DEFAULT 0.5,
                event_type TEXT,
                discovered_phase TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Timeline impossibilities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_impossibilities (
                impossibility_id TEXT PRIMARY KEY,
                event_a_id TEXT,
                event_b_id TEXT,
                impossibility_type TEXT,
                description TEXT NOT NULL,
                severity INTEGER CHECK(severity >= 1 AND severity <= 10),
                evidence TEXT,
                lismore_value TEXT,
                discovered_at TEXT NOT NULL,
                FOREIGN KEY (event_a_id) REFERENCES timeline_events_detailed(event_id),
                FOREIGN KEY (event_b_id) REFERENCES timeline_events_detailed(event_id)
            )
        """)
        
        # Withheld documents (inferred from references)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS withheld_documents (
                inference_id TEXT PRIMARY KEY,
                referenced_in_doc TEXT NOT NULL,
                reference_text TEXT NOT NULL,
                inferred_date TEXT,
                inferred_subject TEXT,
                inferred_participants TEXT,
                missing_type TEXT,
                suspicion_score REAL DEFAULT 5.0,
                strategic_importance TEXT,
                lismore_impact TEXT,
                discovered_at TEXT NOT NULL
            )
        """)
        
        # Admissions against interest
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admissions_against_interest (
                admission_id TEXT PRIMARY KEY,
                admission_text TEXT NOT NULL,
                source_doc TEXT NOT NULL,
                date TEXT,
                speaker TEXT,
                admission_type TEXT,
                contradicts_ph_position TEXT,
                strength_score REAL DEFAULT 5.0,
                tribunal_weight TEXT,
                lismore_use TEXT,
                discovered_at TEXT NOT NULL
            )
        """)
        
        # Privilege claims analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS privilege_claims (
                claim_id TEXT PRIMARY KEY,
                document_description TEXT NOT NULL,
                date_range TEXT,
                privilege_type TEXT,
                claimed_by TEXT,
                suspicion_flags TEXT,
                legitimate_score REAL DEFAULT 5.0,
                discovered_at TEXT NOT NULL
            )
        """)
        
        # =====================================================================
        # INDICES for Performance
        # =====================================================================
        
        # Core table indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_suspicion ON entities(suspicion_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(relationship_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contradiction_severity ON contradictions(severity DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pattern_confidence ON patterns(confidence DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_investigation_priority ON investigations(priority DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_date ON timeline_events(date)")
        
        # Litigation table indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_detailed_date ON timeline_events_detailed(event_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_impossibility_severity ON timeline_impossibilities(severity DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_withheld_suspicion ON withheld_documents(suspicion_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_admission_strength ON admissions_against_interest(strength_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_privilege_legitimate ON privilege_claims(legitimate_score)")
        
        conn.commit()
        conn.close()
    
    # =========================================================================
    # CORE METHODS (Original - keeping all existing functionality)
    # =========================================================================
    
    def add_entity(self, entity: Entity) -> str:
        """Add or update entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT entity_id, confidence FROM entities WHERE entity_id = ?", 
                      (entity.entity_id,))
        existing = cursor.fetchone()
        
        if existing:
            old_confidence = existing[1]
            new_confidence = min(1.0, old_confidence + 0.1)
            
            cursor.execute("""
                UPDATE entities 
                SET confidence = ?, last_updated = ?, properties = ?
                WHERE entity_id = ?
            """, (new_confidence, datetime.now().isoformat(), 
                  json.dumps(entity.properties), entity.entity_id))
        else:
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
        """Add contradiction with automatic investigation spawning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        priority = contradiction.severity / 10.0 * 10
        contradiction.investigation_priority = priority
        
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
            'pending'
        ))
        
        conn.commit()
        
        if contradiction.severity >= 7:
            self._spawn_investigation(
                trigger_type="contradiction",
                trigger_data=asdict(contradiction),
                priority=priority
            )
        
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
        """Add basic timeline event"""
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
    
    # =========================================================================
    # NEW LITIGATION-SPECIFIC METHODS
    # =========================================================================
    
    def add_timeline_event_detailed(self, event: Dict) -> str:
        """
        Add detailed timeline event for forensic analysis
        
        Args:
            event: Dict with date, description, location, participants, etc.
        """
        event_id = hashlib.md5(
            f"{event['date']}_{event['description'][:50]}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO timeline_events_detailed
            (event_id, event_date, event_time, event_description, location,
             participants, source_doc_ids, confidence, event_type, discovered_phase, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            event['date'],
            event.get('time'),
            event['description'],
            event.get('location'),
            json.dumps(event.get('participants', [])),
            json.dumps(event.get('source_docs', [])),
            event.get('confidence', 0.5),
            event.get('event_type', 'unknown'),
            event.get('phase', 'unknown'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return event_id
    
    def add_timeline_impossibility(self, impossibility: Dict) -> str:
        """
        Track timeline impossibility
        
        Args:
            impossibility: Dict with event_a_id, event_b_id, type, description, severity
        """
        impossibility_id = hashlib.md5(
            f"{impossibility['event_a_id']}_{impossibility['event_b_id']}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO timeline_impossibilities
            (impossibility_id, event_a_id, event_b_id, impossibility_type,
             description, severity, evidence, lismore_value, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            impossibility_id,
            impossibility['event_a_id'],
            impossibility['event_b_id'],
            impossibility['type'],
            impossibility['description'],
            impossibility['severity'],
            json.dumps(impossibility.get('evidence', [])),
            impossibility.get('lismore_value', ''),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return impossibility_id
    
    def add_withheld_document_inference(self, withheld: Dict) -> str:
        """
        Track withheld/missing document inference
        
        Args:
            withheld: Dict with referenced_in_doc, reference_text, suspicion_score, etc.
        """
        inference_id = hashlib.md5(
            f"{withheld['referenced_in_doc']}_{withheld['reference_text'][:50]}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO withheld_documents
            (inference_id, referenced_in_doc, reference_text, inferred_date,
             inferred_subject, inferred_participants, missing_type, suspicion_score,
             strategic_importance, lismore_impact, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inference_id,
            withheld['referenced_in_doc'],
            withheld['reference_text'],
            withheld.get('inferred_date'),
            withheld.get('inferred_subject'),
            json.dumps(withheld.get('inferred_participants', [])),
            withheld.get('missing_type', 'unknown'),
            withheld.get('suspicion_score', 5.0),
            withheld.get('strategic_importance', ''),
            withheld.get('lismore_impact', ''),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return inference_id
    
    def add_admission_against_interest(self, admission: Dict) -> str:
        """
        Track admission against interest
        
        Args:
            admission: Dict with admission_text, source_doc, speaker, strength_score, etc.
        """
        admission_id = hashlib.md5(
            f"{admission['source_doc']}_{admission['admission_text'][:50]}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO admissions_against_interest
            (admission_id, admission_text, source_doc, date, speaker,
             admission_type, contradicts_ph_position, strength_score,
             tribunal_weight, lismore_use, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admission_id,
            admission['admission_text'],
            admission['source_doc'],
            admission.get('date'),
            admission.get('speaker'),
            admission.get('admission_type', 'unknown'),
            admission.get('contradicts_ph_position', ''),
            admission.get('strength_score', 5.0),
            admission.get('tribunal_weight', 'moderate'),
            admission.get('lismore_use', ''),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return admission_id
    
    def get_litigation_intelligence(self) -> Dict[str, Any]:
        """
        Get all litigation-specific intelligence for prompt context
        
        Returns comprehensive findings for Lismore case
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        intel = {}
        
        # Timeline impossibilities
        cursor.execute("""
            SELECT description, severity, lismore_value
            FROM timeline_impossibilities
            WHERE severity >= 7
            ORDER BY severity DESC
            LIMIT 10
        """)
        intel['timeline_impossibilities'] = [
            {'description': row[0], 'severity': row[1], 'value': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Withheld documents
        cursor.execute("""
            SELECT referenced_in_doc, reference_text, suspicion_score, lismore_impact
            FROM withheld_documents
            WHERE suspicion_score >= 7
            ORDER BY suspicion_score DESC
            LIMIT 10
        """)
        intel['withheld_documents'] = [
            {'referenced_in': row[0], 'reference': row[1][:100], 'suspicion': row[2], 'impact': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Admissions
        cursor.execute("""
            SELECT admission_text, speaker, strength_score, lismore_use
            FROM admissions_against_interest
            WHERE strength_score >= 7
            ORDER BY strength_score DESC
            LIMIT 10
        """)
        intel['admissions'] = [
            {'text': row[0][:200], 'speaker': row[1], 'strength': row[2], 'use': row[3]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return intel
    
    # =========================================================================
    # REMAINING ORIGINAL METHODS (Investigation, Discovery, Stats, etc.)
    # =========================================================================
    
    def _spawn_investigation(self, trigger_type: str, trigger_data: Dict, priority: float, parent_id: str = None) -> str:
        """Spawn new investigation thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        investigation_id = f"INV_{hashlib.md5(str(trigger_data).encode()).hexdigest()[:8].upper()}"
        
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
    
    def log_discovery(self, discovery_type: str, content: str, importance: str, phase: str) -> None:
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
        
        cursor.execute("SELECT COUNT(*) FROM timeline_events_detailed")
        stats['timeline_events_detailed'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM timeline_impossibilities")
        stats['timeline_impossibilities'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM withheld_documents")
        stats['withheld_documents'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM admissions_against_interest")
        stats['admissions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM investigations WHERE status = 'active'")
        stats['active_investigations'] = cursor.fetchone()[0]
        
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
        
        # High-suspicion entities
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
        
        # Critical contradictions
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
        
        # High-confidence patterns
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
        
        # Add litigation intelligence
        context['litigation_findings'] = self.get_litigation_intelligence()
        
        conn.close()
        return context
    
    def backup_before_phase(self, phase: str) -> str:
        """Create versioned backup before phase execution"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"graph_backup_phase_{phase}_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        
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
    
    def _get_current_version(self) -> int:
        """Get current version number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(version_id) FROM version_history")
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result[0] else 0