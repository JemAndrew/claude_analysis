#!/usr/bin/env python3
"""
SQLite-based Knowledge Graph for Litigation Intelligence
Extended with litigation-specific tables for Lismore v Process Holdings
British English throughout
UPDATED: Pass executor support methods added
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
    
    def _init_database(self):
        """Initialise SQLite database with full schema"""
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                subtype TEXT,
                name TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT,
                confidence REAL DEFAULT 0.5,
                suspicion_score REAL DEFAULT 0.0,
                properties TEXT,
                discovery_phase TEXT,
                notes TEXT
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
                properties TEXT,
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
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # ENTITY MANAGEMENT
    # ========================================================================
    
    def add_entity(self, entity: Dict) -> str:
        """Add entity to knowledge graph"""
        
        entity_id = entity.get('entity_id') or hashlib.md5(
            f"{entity['name']}_{entity['entity_type']}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO entities (
                entity_id, entity_type, subtype, name, first_seen,
                confidence, suspicion_score, properties, discovery_phase
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entity_id,
            entity['entity_type'],
            entity.get('subtype', ''),
            entity['name'],
            datetime.now().isoformat(),
            entity.get('confidence', 0.5),
            entity.get('suspicion_score', 0.0),
            json.dumps(entity.get('properties', {})),
            entity.get('discovery_phase', 'unknown')
        ))
        
        conn.commit()
        conn.close()
        
        return entity_id
    
    def add_relationship(self, relationship: Dict) -> str:
        """Add relationship between entities"""
        
        relationship_id = hashlib.md5(
            f"{relationship['source_entity']}_{relationship['target_entity']}_{relationship['relationship_type']}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO relationships (
                relationship_id, source_entity, target_entity, relationship_type,
                confidence, evidence, discovered, properties
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            relationship_id,
            relationship['source_entity'],
            relationship['target_entity'],
            relationship['relationship_type'],
            relationship.get('confidence', 0.5),
            json.dumps(relationship.get('evidence', [])),
            datetime.now().isoformat(),
            json.dumps(relationship.get('properties', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return relationship_id
    
    # ========================================================================
    # CONTRADICTION MANAGEMENT
    # ========================================================================
    
    def add_contradiction(self, contradiction: Dict) -> str:
        """Add contradiction to knowledge graph"""
        
        contradiction_id = hashlib.md5(
            f"{contradiction['doc_a']}_{contradiction['doc_b']}_{contradiction['statement_a'][:50]}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO contradictions (
                contradiction_id, statement_a, statement_b, doc_a, doc_b,
                severity, confidence, implications, investigation_priority, discovered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contradiction_id,
            contradiction['statement_a'],
            contradiction['statement_b'],
            contradiction['doc_a'],
            contradiction['doc_b'],
            contradiction.get('severity', 5),
            contradiction.get('confidence', 0.5),
            contradiction.get('implications', ''),
            contradiction.get('investigation_priority', 5.0),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return contradiction_id
    
    # ========================================================================
    # PATTERN MANAGEMENT
    # ========================================================================
    
    def add_pattern(self, pattern: Dict) -> str:
        """Add pattern to knowledge graph"""
        
        pattern_id = hashlib.md5(
            f"{pattern['pattern_type']}_{pattern['description'][:50]}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO patterns (
                pattern_id, pattern_type, description, confidence,
                supporting_evidence, contradicting_evidence, evolution_history,
                investigation_spawned, discovered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            pattern['pattern_type'],
            pattern['description'],
            pattern.get('confidence', 0.5),
            json.dumps(pattern.get('supporting_evidence', [])),
            json.dumps(pattern.get('contradicting_evidence', [])),
            json.dumps(pattern.get('evolution_history', [])),
            pattern.get('investigation_spawned', False),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return pattern_id
    
    # ========================================================================
    # DISCOVERY LOGGING
    # ========================================================================
    
    def add_discovery(self, discovery_type: str, content: str, 
                     importance: str, phase: str) -> str:
        """Add discovery to log"""
        
        discovery_id = hashlib.md5(
            f"{discovery_type}_{content[:50]}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO discovery_log (
                discovery_id, discovery_type, content, importance, phase, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            discovery_id, discovery_type, content, importance,
            phase, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return discovery_id
    
    # ========================================================================
    # STATISTICS & EXPORT
    # ========================================================================
    
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
    
    # ========================================================================
    # PASS EXECUTOR SUPPORT METHODS (for 4-pass system)
    # ========================================================================
    
    def get_context_for_analysis(self) -> Dict:
        """
        Get context for Pass 2 deep analysis
        Wrapper around get_context_for_phase for compatibility
        """
        return self.get_context_for_phase('analysis')
    
    def integrate_analysis(self, iteration_result: Dict):
        """
        Integrate Pass 2 iteration results into knowledge graph
        
        Args:
            iteration_result: Dict from Pass 2 with findings, breaches, evidence
        """
        # Add findings as discoveries
        for finding in iteration_result.get('findings', []):
            self.add_discovery(
                discovery_type='analysis_finding',
                content=str(finding),
                importance='MEDIUM',
                phase='pass_2'
            )
        
        # Add critical findings
        for critical in iteration_result.get('critical_findings', []):
            self.add_discovery(
                discovery_type='critical_finding',
                content=str(critical),
                importance='CRITICAL',
                phase='pass_2'
            )
    
    def get_documents_for_investigation(self, topic: str) -> List[Dict]:
        """
        Get relevant documents for Pass 3 investigation
        
        Args:
            topic: Investigation topic string
            
        Returns:
            List of relevant document dicts (empty list for now)
        """
        # TODO: Implement document retrieval based on topic
        # For now, return empty - Pass 3 will work with complete intelligence
        return []
    
    def add_investigation_result(self, investigation, result: Dict):
        """
        Store Pass 3 investigation result in knowledge graph
        
        Args:
            investigation: Investigation object
            result: Dict with findings, confidence, conclusion
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO investigations (
                investigation_id, trigger_type, trigger_data, priority,
                status, spawned_from, findings, created, completed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            investigation.get_id(),
            'autonomous',
            json.dumps(investigation.trigger_data),
            investigation.priority,
            'completed',
            investigation.parent_id,
            json.dumps(result),
            investigation.created_at.isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def export_complete(self) -> Dict:
        """
        Export complete knowledge graph for Pass 3 & 4
        
        Returns:
            Complete intelligence dict with all findings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        export = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'entities': [],
            'relationships': [],
            'contradictions': [],
            'patterns': [],
            'timeline': [],
            'breaches': [],
            'evidence': []
        }
        
        # Export entities (top 100)
        cursor.execute("""
            SELECT entity_id, name, entity_type, confidence, properties
            FROM entities
            ORDER BY confidence DESC
            LIMIT 100
        """)
        for row in cursor.fetchall():
            export['entities'].append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'confidence': row[3],
                'properties': json.loads(row[4]) if row[4] else {}
            })
        
        # Export relationships (top 100)
        cursor.execute("""
            SELECT source_entity, target_entity, relationship_type, confidence
            FROM relationships
            ORDER BY confidence DESC
            LIMIT 100
        """)
        for row in cursor.fetchall():
            export['relationships'].append({
                'source': row[0],
                'target': row[1],
                'type': row[2],
                'confidence': row[3]
            })
        
        # Export contradictions (all unresolved)
        cursor.execute("""
            SELECT statement_a, statement_b, severity, confidence, implications
            FROM contradictions
            WHERE resolved = 0
            ORDER BY severity DESC
        """)
        for row in cursor.fetchall():
            export['contradictions'].append({
                'statement_a': row[0],
                'statement_b': row[1],
                'severity': row[2],
                'confidence': row[3],
                'implications': row[4]
            })
        
        # Export patterns (high confidence)
        cursor.execute("""
            SELECT pattern_type, description, confidence, supporting_evidence
            FROM patterns
            WHERE confidence > 0.5
            ORDER BY confidence DESC
        """)
        for row in cursor.fetchall():
            export['patterns'].append({
                'type': row[0],
                'description': row[1],
                'confidence': row[2],
                'evidence': json.loads(row[3]) if row[3] else []
            })
        
        # Export timeline events
        cursor.execute("""
            SELECT date, description, confidence, is_critical
            FROM timeline_events
            ORDER BY date
        """)
        for row in cursor.fetchall():
            export['timeline'].append({
                'date': row[0],
                'description': row[1],
                'confidence': row[2],
                'critical': bool(row[3])
            })
        
        conn.close()
        return export