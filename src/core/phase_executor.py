#!/usr/bin/env python3
"""
Phase Executor for Dynamic Phase Management
Handles Phase 0 (knowledge) and dynamic iteration logic only
NO FIXED PHASES 1-7 - Pure Phase 0, 1, 2-N structure
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re
import hashlib
from pathlib import Path


class PhaseExecutor:
    """Executes Phase 0 and provides iteration support - British English"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        
    # ═══════════════════════════════════════════════════════════════
    # PHASE 0: KNOWLEDGE ABSORPTION (ONLY FIXED PHASE)
    # ═══════════════════════════════════════════════════════════════
    
    def execute_phase_0(self, context: Dict) -> Dict:
        """
        Phase 0: Combined legal and case knowledge absorption
        This is the ONLY fixed phase - everything else is dynamic iterations
        """
        
        print("  📚 Strategy: Unified knowledge synthesis (legal + case context)")
        
        # Load documents
        legal_docs = self._load_phase_documents('legal_knowledge')
        case_docs = self._load_phase_documents('case_context')
        
        print(f"    Legal documents: {len(legal_docs)}")
        print(f"    Case context documents: {len(case_docs)}")
        
        # Build knowledge synthesis prompt
        prompt = self.orchestrator.autonomous_prompts.knowledge_synthesis_prompt(
            legal_knowledge=legal_docs,
            case_context=case_docs,
            existing_knowledge=context
        )
        
        # Execute with primary model for maximum learning
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='knowledge_synthesis',
            phase='0'
        )
        
        # Store knowledge in graph
        self._process_knowledge_response(response, '0')
        
        return {
            'phase': '0',
            'strategy': 'unified_synthesis',
            'documents_processed': len(legal_docs) + len(case_docs),
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _load_phase_documents(self, doc_type: str) -> List[Dict]:
        """Load documents for phase"""
        from utils.document_loader import DocumentLoader
        
        if doc_type == 'legal_knowledge':
            path = self.config.legal_knowledge_dir
        elif doc_type == 'case_context':
            path = self.config.case_context_dir
        elif doc_type == 'disclosure':
            path = self.config.disclosure_dir
        else:
            path = self.config.disclosure_dir
        
        loader = DocumentLoader(self.config)
        return loader.load_directory(path)
    
    def _process_knowledge_response(self, response: str, phase: str):
        """
        Extract and store knowledge from Phase 0 response
        Looks for legal principles, case facts, strategic insights
        """
        
        # Log the knowledge acquisition
        self.orchestrator.knowledge_graph.log_discovery(
            discovery_type='KNOWLEDGE_SYNTHESIS',
            content=response[:1000],
            importance='HIGH',
            phase=phase
        )
        
        # Extract strategic insights
        insights = self._extract_strategic_insights(response)
        for insight in insights:
            self.orchestrator.knowledge_graph.log_discovery(
                discovery_type='STRATEGIC_INSIGHT',
                content=insight,
                importance='MEDIUM',
                phase=phase
            )
    
    def _extract_strategic_insights(self, response: str) -> List[str]:
        """Extract strategic insights from response"""
        insights = []
        
        # Look for marked strategic content
        markers = [
            r'\[STRATEGIC\](.*?)(?=\[|$)',
            r'\[VULNERABILITY\](.*?)(?=\[|$)',
            r'\[WEAPON\](.*?)(?=\[|$)'
        ]
        
        for marker in markers:
            matches = re.findall(marker, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                insights.append(match.strip()[:500])
        
        return insights
    
    # ═══════════════════════════════════════════════════════════════
    # DISCOVERY EXTRACTION (Used by orchestrator during iterations)
    # ═══════════════════════════════════════════════════════════════
    
    def extract_discoveries(self, response: str, phase: str) -> List[Dict]:
        """
        Extract discoveries from iteration response
        Called by orchestrator during dynamic iterations
        """
        discoveries = []
        
        # Parse response for discovery markers
        markers = {
            'NUCLEAR': r'\[NUCLEAR\]\s*([^\[]+)',
            'CRITICAL': r'\[CRITICAL\]\s*([^\[]+)',
            'PATTERN': r'\[PATTERN\]\s*([^\[]+)',
            'SUSPICIOUS': r'\[SUSPICIOUS\]\s*([^\[]+)',
            'MISSING': r'\[MISSING\]\s*([^\[]+)',
            'TIMELINE': r'\[TIMELINE\]\s*([^\[]+)',
            'FINANCIAL': r'\[FINANCIAL\]\s*([^\[]+)',
            'CONTRADICTION': r'\[CONTRADICTION\]\s*([^\[]+)'
        }
        
        for discovery_type, pattern in markers.items():
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                discoveries.append({
                    'type': discovery_type,
                    'content': match.strip()[:500],
                    'timestamp': datetime.now().isoformat(),
                    'phase': phase
                })
                
                # Log to knowledge graph
                importance_map = {
                    'NUCLEAR': 'NUCLEAR',
                    'CRITICAL': 'CRITICAL',
                    'SUSPICIOUS': 'HIGH',
                    'PATTERN': 'MEDIUM',
                    'MISSING': 'MEDIUM',
                    'TIMELINE': 'MEDIUM',
                    'FINANCIAL': 'HIGH',
                    'CONTRADICTION': 'CRITICAL'
                }
                
                self.orchestrator.knowledge_graph.log_discovery(
                    discovery_type=discovery_type,
                    content=match.strip()[:500],
                    importance=importance_map.get(discovery_type, 'MEDIUM'),
                    phase=phase
                )
        
        return discoveries
    
    def extract_contradictions(self, response: str) -> List:
        """Extract contradictions for investigation spawning"""
        from intelligence.knowledge_graph import Contradiction
        
        contradictions = []
        
        # Pattern matching for contradictions
        patterns = [
            r'\[CONTRADICTION\](.*?)(?=\[|$)',
            r'contradict(?:s|ion)?:?\s*(.*?)(?=\n|\[|$)',
            r'inconsistent:?\s*(.*?)(?=\n|\[|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Extract severity if mentioned
                severity_match = re.search(r'severity[:\s]+(\d+)', match, re.IGNORECASE)
                severity = int(severity_match.group(1)) if severity_match else 7
                
                contradiction = Contradiction(
                    contradiction_id=hashlib.md5(match.encode()).hexdigest()[:16],
                    statement_a=match[:200],
                    statement_b=match[200:400] if len(match) > 200 else "IMPLIED",
                    doc_a='EXTRACTED',
                    doc_b='EXTRACTED',
                    severity=severity,
                    confidence=0.8,
                    implications=match[:500],
                    investigation_priority=float(severity),
                    discovered=datetime.now().isoformat()
                )
                contradictions.append(contradiction)
        
        return contradictions
    
    def extract_patterns(self, response: str) -> List:
        """Extract patterns for knowledge graph"""
        from intelligence.knowledge_graph import Pattern
        
        patterns = []
        
        # Pattern markers
        markers = [
            r'\[PATTERN\](.*?)(?=\[|$)',
            r'\[PATTERN-TEMPORAL\](.*?)(?=\[|$)',
            r'\[PATTERN-FINANCIAL\](.*?)(?=\[|$)',
            r'\[PATTERN-BEHAVIOURAL\](.*?)(?=\[|$)',
            r'pattern:?\s*(.*?)(?=\n|\[|$)'
        ]
        
        for marker in markers:
            matches = re.findall(marker, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                pattern = Pattern(
                    pattern_id=hashlib.md5(match.encode()).hexdigest()[:16],
                    pattern_type='discovered',
                    description=match[:500],
                    confidence=0.7,
                    supporting_evidence=[],
                    contradicting_evidence=[],
                    evolution_history=[{'timestamp': datetime.now().isoformat()}],
                    investigation_spawned=False,
                    discovered=datetime.now().isoformat()
                )
                patterns.append(pattern)
        
        return patterns
    
    def extract_entities_and_relationships(self, response: str) -> tuple:
        """Extract entities and relationships from response"""
        from intelligence.knowledge_graph import Entity, Relationship
        
        entities = []
        relationships = []
        
        # Entity patterns
        entity_patterns = [
            r'\[ENTITY-NEW\](.*?)(?=\[|$)',
            r'entity:?\s*(.*?)(?=\n|\[|$)'
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                entity = Entity(
                    entity_id=hashlib.md5(match.encode()).hexdigest()[:16],
                    entity_type='DISCOVERED',
                    subtype='UNKNOWN',
                    name=match[:100],
                    first_seen=datetime.now().isoformat(),
                    confidence=0.7,
                    properties={},
                    discovery_phase='dynamic'
                )
                entities.append(entity)
        
        # Relationship patterns
        relationship_patterns = [
            r'\[RELATIONSHIP-HIDDEN\](.*?)(?=\[|$)',
            r'relationship:?\s*(.*?)(?=\n|\[|$)'
        ]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                relationship = Relationship(
                    relationship_id=hashlib.md5(match.encode()).hexdigest()[:16],
                    source_entity='UNKNOWN',
                    target_entity='UNKNOWN',
                    relationship_type='DISCOVERED',
                    confidence=0.7,
                    evidence=[match[:200]],
                    discovered=datetime.now().isoformat(),
                    properties={}
                )
                relationships.append(relationship)
        
        return entities, relationships
    
    def extract_financial_anomalies(self, response: str) -> List[Dict]:
        """Extract financial anomalies from response"""
        anomalies = []
        
        markers = [
            r'\[FINANCIAL\](.*?)(?=\[|$)',
            r'anomaly:?\s*(.*?)(?=\n|\[|$)',
            r'suspicious.*?(?:payment|valuation|transaction):?\s*(.*?)(?=\n|\[|$)'
        ]
        
        for marker in markers:
            matches = re.findall(marker, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Try to extract severity
                severity_match = re.search(r'severity[:\s]+(\d+)', match, re.IGNORECASE)
                severity = int(severity_match.group(1)) if severity_match else 7
                
                anomalies.append({
                    'description': match[:500],
                    'severity': severity,
                    'requires_investigation': severity > 6,
                    'discovered': datetime.now().isoformat()
                })
        
        return anomalies
    
    def synthesise_narrative(self, narrative: str):
        """Save final narrative synthesis"""
        narrative_file = self.config.reports_dir / "strategic_narrative.md"
        narrative_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(narrative_file, 'w', encoding='utf-8') as f:
            f.write(f"# LISMORE V PROCESS HOLDINGS - STRATEGIC NARRATIVE\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(narrative)
        
        print(f"  ✓ Narrative saved to {narrative_file}")
    
    # ═══════════════════════════════════════════════════════════════
    # KNOWLEDGE GRAPH HELPERS
    # ═══════════════════════════════════════════════════════════════
    
    def get_known_patterns(self) -> Dict:
        """Get known patterns from knowledge graph"""
        patterns = self.orchestrator.knowledge_graph.get_all_patterns()
        return {p.pattern_id: {
            'description': p.description,
            'confidence': p.confidence,
            'type': p.pattern_type
        } for p in patterns}
    
    def get_known_entities(self) -> Dict:
        """Get known entities from knowledge graph"""
        entities = self.orchestrator.knowledge_graph.get_all_entities()
        return {e.entity_id: {
            'name': e.name,
            'type': e.entity_type,
            'confidence': e.confidence
        } for e in entities}