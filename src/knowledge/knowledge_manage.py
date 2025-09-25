#!/usr/bin/env python3
"""
OPTIMISED Knowledge Manager for Maximum Claude Learning
Enhanced version with structured knowledge graphs and intelligent cross-phase learning
"""

import json
import hashlib
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class KnowledgeManager:
    """
    Enhanced knowledge management optimised for Claude's learning:
    - Structured knowledge graphs for better pattern recognition
    - Intelligent knowledge compression and extraction
    - Cross-phase relationship mapping
    - Contradiction tracking across all phases
    - Entity relationship evolution
    - Weaponised findings categorisation
    """
    
    def __init__(self, storage_path: str = "./knowledge_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Phase ordering
        self.phase_order = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        # Core knowledge structures optimised for Claude
        self.knowledge_graph = {
            # Legal Arsenal (Phase 0A)
            'legal_weapons': {
                'nuclear': [],      # Case-ending weapons
                'high_impact': [],  # Significant damage weapons
                'procedural': [],   # Process-based attacks
                'criminal': []      # Criminal crossovers
            },
            
            # Case Intelligence (Phase 0B) 
            'admissions': {
                'explicit': [],     # Direct admissions
                'implicit': [],     # Implied admissions
                'judicial': []      # Binding judicial admissions
            },
            
            # Contradiction Matrix (Phases 1-7)
            'contradictions': {
                'internal': [],     # Within same party's docs
                'timeline': [],     # Temporal impossibilities
                'financial': [],    # Number discrepancies
                'factual': []       # Factual inconsistencies
            },
            
            # Pattern Intelligence
            'patterns': {
                'fraud_indicators': [],
                'conspiracy_markers': [],
                'cover_up_behaviour': [],
                'missing_documents': []
            },
            
            # Entity Relationships
            'entities': defaultdict(lambda: {
                'mentions': [],
                'relationships': [],
                'suspicious_behaviour': [],
                'timeline': []
            }),
            
            # Timeline Intelligence
            'timeline': {
                'events': [],
                'impossibilities': [],
                'gaps': [],
                'critical_periods': []
            },
            
            # Strategic Intelligence
            'strategy': {
                'attack_vectors': [],
                'settlement_leverage': [],
                'cross_exam_traps': [],
                'document_requests': []
            }
        }
        
        # Phase-specific storage (backward compatible)
        self.knowledge_store = {}
        
        # Load existing knowledge
        self._load_existing_knowledge()
        self._migrate_to_optimised_format()
    
    def store_phase_knowledge(self, phase: str, knowledge: Dict) -> bool:
        """
        Enhanced storage that extracts and structures knowledge for optimal Claude learning
        """
        try:
            # Store raw knowledge (backward compatibility)
            self.knowledge_store[phase] = knowledge
            
            # Extract and structure for optimised learning
            self._extract_structured_knowledge(phase, knowledge)
            
            # Build cross-phase relationships
            self._build_relationships()
            
            # Compress and optimise for Claude
            optimised = self._optimise_for_claude(phase, knowledge)
            
            # Save both raw and optimised versions
            self._save_raw_knowledge(phase, knowledge)
            self._save_optimised_knowledge(phase, optimised)
            
            # Save the knowledge graph
            self._save_knowledge_graph()
            
            print(f"✅ Phase {phase} knowledge stored and optimised")
            return True
            
        except Exception as e:
            print(f"❌ Error storing knowledge: {e}")
            return False
    
    def _extract_structured_knowledge(self, phase: str, knowledge: Dict):
        """Extract structured intelligence from raw phase results"""
        
        if phase == "0A":
            self._extract_legal_weapons(knowledge)
        elif phase == "0B":
            self._extract_admissions(knowledge)
        elif phase in ["1", "2", "3", "4", "5", "6", "7"]:
            self._extract_patterns(knowledge)
            self._extract_contradictions(knowledge)
            self._extract_entities(knowledge)
            self._extract_timeline(knowledge)
    
    def _extract_legal_weapons(self, knowledge: Dict):
        """Extract legal weapons from Phase 0A"""
        if 'offensive_weapons' in knowledge:
            weapons = knowledge['offensive_weapons']
            # Parse and categorise weapons
            if isinstance(weapons, str):
                for line in weapons.split('\n'):
                    if 'NUCLEAR' in line:
                        self.knowledge_graph['legal_weapons']['nuclear'].append(line)
                    elif 'HIGH' in line:
                        self.knowledge_graph['legal_weapons']['high_impact'].append(line)
                    elif 'CRIMINAL' in line.upper():
                        self.knowledge_graph['legal_weapons']['criminal'].append(line)
    
    def _extract_admissions(self, knowledge: Dict):
        """Extract admissions from Phase 0B or other phases"""
        for key in ['admissions_hunt', 'admissions', 'admissions_bank']:
            if key in knowledge:
                admissions_data = knowledge[key]
                if isinstance(admissions_data, str):
                    # Parse admission types
                    for line in admissions_data.split('\n'):
                        if 'ADMISSION:' in line:
                            admission = line.split('ADMISSION:')[1].strip()
                            if 'explicit' in line.lower() or 'direct' in line.lower():
                                self.knowledge_graph['admissions']['explicit'].append(admission)
                            elif 'judicial' in line.lower():
                                self.knowledge_graph['admissions']['judicial'].append(admission)
                            else:
                                self.knowledge_graph['admissions']['implicit'].append(admission)
    
    def _extract_contradictions(self, knowledge: Dict):
        """Extract contradictions from any phase"""
        for key in ['contradictions', 'contradiction_matrix', 'inconsistencies']:
            if key in knowledge:
                data = knowledge[key]
                if isinstance(data, dict) and 'findings' in data:
                    findings = data['findings']
                    if isinstance(findings, list):
                        for finding in findings:
                            self._categorise_contradiction(finding)
                elif isinstance(data, str):
                    # Parse text for contradictions
                    for line in data.split('\n'):
                        if 'CONTRADICTION:' in line or 'INCONSISTENCY:' in line:
                            self._categorise_contradiction(line)
    
    def _categorise_contradiction(self, contradiction: Any):
        """Categorise a contradiction by type"""
        text = str(contradiction).lower()
        if 'timeline' in text or 'temporal' in text or 'date' in text:
            self.knowledge_graph['contradictions']['timeline'].append(contradiction)
        elif 'financial' in text or 'amount' in text or '$' in text or '£' in text:
            self.knowledge_graph['contradictions']['financial'].append(contradiction)
        elif 'internal' in text or 'same party' in text:
            self.knowledge_graph['contradictions']['internal'].append(contradiction)
        else:
            self.knowledge_graph['contradictions']['factual'].append(contradiction)
    
    def _extract_patterns(self, knowledge: Dict):
        """Extract patterns from phase results"""
        for key in ['patterns', 'pattern_recognition']:
            if key in knowledge:
                data = knowledge[key]
                if isinstance(data, dict) and 'findings' in data:
                    findings = data['findings']
                    self._categorise_patterns(findings)
    
    def _categorise_patterns(self, patterns: Any):
        """Categorise patterns by type"""
        text = str(patterns).lower()
        
        # Fraud indicators
        fraud_keywords = ['fraud', 'deceit', 'misrepresent', 'false', 'fabricat']
        if any(keyword in text for keyword in fraud_keywords):
            self.knowledge_graph['patterns']['fraud_indicators'].append(patterns)
        
        # Conspiracy markers
        conspiracy_keywords = ['conspiracy', 'collu', 'coordinat', 'agreement']
        if any(keyword in text for keyword in conspiracy_keywords):
            self.knowledge_graph['patterns']['conspiracy_markers'].append(patterns)
        
        # Cover-up behaviour
        coverup_keywords = ['destroy', 'delet', 'missing', 'withheld', 'concealed']
        if any(keyword in text for keyword in coverup_keywords):
            self.knowledge_graph['patterns']['cover_up_behaviour'].append(patterns)
    
    def _extract_entities(self, knowledge: Dict):
        """Extract and map entity relationships"""
        # Extract entity mentions from various fields
        text_fields = ['analysis', 'findings', 'synthesis']
        for field in text_fields:
            if field in knowledge:
                self._parse_entities_from_text(str(knowledge[field]))
    
    def _parse_entities_from_text(self, text: str):
        """Parse entities from text"""
        # Look for common entity patterns
        # Company names (capitalised words, Ltd, Inc, etc.)
        company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Ltd|Limited|Inc|Corporation|Corp|Holdings|Capital|Partners))?)\b'
        
        for match in re.finditer(company_pattern, text):
            entity = match.group(1)
            if len(entity) > 3:  # Filter out short matches
                self.knowledge_graph['entities'][entity]['mentions'].append({
                    'context': text[max(0, match.start()-50):match.end()+50],
                    'timestamp': datetime.now().isoformat()
                })
    
    def _extract_timeline(self, knowledge: Dict):
        """Extract timeline events"""
        # Look for dates and temporal references
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b'
        
        for field in ['analysis', 'findings']:
            if field in knowledge:
                text = str(knowledge[field])
                for match in re.finditer(date_pattern, text):
                    self.knowledge_graph['timeline']['events'].append({
                        'date': match.group(1),
                        'context': text[max(0, match.start()-100):match.end()+100]
                    })
    
    def _build_relationships(self):
        """Build cross-phase relationships between findings"""
        # Connect related contradictions
        for contradiction in self.knowledge_graph['contradictions']['timeline']:
            # Look for related entities
            entities = self._extract_entities_from_finding(contradiction)
            for entity in entities:
                self.knowledge_graph['entities'][entity]['suspicious_behaviour'].append({
                    'type': 'timeline_contradiction',
                    'detail': contradiction
                })
    
    def _extract_entities_from_finding(self, finding: Any) -> List[str]:
        """Extract entity names from a finding"""
        entities = []
        text = str(finding)
        for entity_name in self.knowledge_graph['entities'].keys():
            if entity_name in text:
                entities.append(entity_name)
        return entities
    
    def _optimise_for_claude(self, phase: str, knowledge: Dict) -> Dict:
        """
        Optimise knowledge format for Claude's maximum learning
        Creates structured, interconnected knowledge that Claude can build upon
        """
        optimised = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            
            # Structured findings for Claude to reference
            'key_findings': self._extract_key_findings(knowledge),
            
            # Actionable intelligence
            'actionable_intelligence': self._extract_actionable(knowledge),
            
            # Evidence references for Claude to track
            'evidence_map': self._build_evidence_map(knowledge),
            
            # Patterns for Claude to extend
            'pattern_evolution': self._track_pattern_evolution(phase),
            
            # Contradictions for Claude to exploit
            'contradiction_opportunities': self._identify_contradiction_opportunities(),
            
            # Strategic recommendations for next phases
            'strategic_guidance': self._generate_strategic_guidance(phase),
            
            # Knowledge gaps for Claude to fill
            'knowledge_gaps': self._identify_knowledge_gaps(knowledge),
            
            # Cross-references to previous phases
            'cross_phase_insights': self._build_cross_phase_insights(phase)
        }
        
        return optimised
    
    def _extract_key_findings(self, knowledge: Dict) -> List[Dict]:
        """Extract and structure key findings"""
        findings = []
        
        # Look for high-value findings
        for key in ['findings', 'analysis', 'synthesis', 'combined_insights']:
            if key in knowledge:
                content = str(knowledge[key])
                
                # Extract findings with impact ratings
                high_impact_patterns = [
                    r'(CRITICAL|NUCLEAR|HIGH.?IMPACT|SMOKING.?GUN)[:\s]+([^.]+)',
                    r'(ADMISSION|CONTRADICTION|IMPOSSIBILITY)[:\s]+([^.]+)',
                    r'(FRAUD|CONSPIRACY|CRIMINAL)[:\s]+([^.]+)'
                ]
                
                for pattern in high_impact_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        findings.append({
                            'type': match.group(1),
                            'finding': match.group(2).strip(),
                            'impact': 'CRITICAL' if 'NUCLEAR' in match.group(1).upper() else 'HIGH'
                        })
        
        return findings
    
    def _extract_actionable(self, knowledge: Dict) -> List[Dict]:
        """Extract actionable intelligence"""
        actionable = []
        
        # Categories of actionable items
        action_patterns = {
            'document_request': r'(?:request|demand|seek).{0,50}(?:document|disclosure)',
            'deposition_topic': r'(?:depose|examine|question).{0,50}(?:about|regarding)',
            'investigation_lead': r'(?:investigate|examine|pursue).{0,50}(?:further|lead)',
            'legal_action': r'(?:file|bring|pursue).{0,50}(?:motion|claim|action)'
        }
        
        for key, data in knowledge.items():
            if isinstance(data, str):
                for action_type, pattern in action_patterns.items():
                    for match in re.finditer(pattern, data, re.IGNORECASE):
                        actionable.append({
                            'type': action_type,
                            'action': match.group(0),
                            'source_phase': knowledge.get('phase', 'unknown')
                        })
        
        return actionable
    
    def _build_evidence_map(self, knowledge: Dict) -> Dict:
        """Build a map of evidence references"""
        evidence_map = {
            'documents': [],
            'witnesses': [],
            'exhibits': []
        }
        
        # Extract document references
        doc_pattern = r'(?:DOC|Document|Exhibit)\s*[#\s]?(\d+|[A-Z]+)'
        
        for key, value in knowledge.items():
            if isinstance(value, str):
                for match in re.finditer(doc_pattern, value):
                    evidence_map['documents'].append({
                        'reference': match.group(0),
                        'context': value[max(0, match.start()-50):match.end()+50]
                    })
        
        return evidence_map
    
    def _track_pattern_evolution(self, phase: str) -> Dict:
        """Track how patterns evolve across phases"""
        evolution = {
            'patterns_strengthened': [],
            'patterns_weakened': [],
            'new_patterns': [],
            'pattern_connections': []
        }
        
        # Compare current patterns with previous phases
        current_patterns = self.knowledge_graph['patterns']
        
        # Identify evolving patterns (simplified for demonstration)
        for pattern_type, patterns in current_patterns.items():
            if len(patterns) > 0:
                evolution['new_patterns'].append({
                    'type': pattern_type,
                    'count': len(patterns),
                    'phase_discovered': phase
                })
        
        return evolution
    
    def _identify_contradiction_opportunities(self) -> List[Dict]:
        """Identify opportunities to exploit contradictions"""
        opportunities = []
        
        # Analyse contradiction matrix
        for contradiction_type, contradictions in self.knowledge_graph['contradictions'].items():
            if contradictions:
                opportunities.append({
                    'type': contradiction_type,
                    'count': len(contradictions),
                    'exploitation_strategy': self._get_exploitation_strategy(contradiction_type),
                    'priority': 'HIGH' if contradiction_type in ['timeline', 'financial'] else 'MEDIUM'
                })
        
        return opportunities
    
    def _get_exploitation_strategy(self, contradiction_type: str) -> str:
        """Get exploitation strategy for contradiction type"""
        strategies = {
            'timeline': 'Use for adverse inference and credibility destruction in cross-examination',
            'financial': 'Basis for fraud claims and damages calculation challenges',
            'internal': 'Demonstrate pattern of deception and unreliability',
            'factual': 'Undermine entire narrative and witness credibility'
        }
        return strategies.get(contradiction_type, 'General credibility attack')
    
    def _generate_strategic_guidance(self, phase: str) -> Dict:
        """Generate strategic guidance for next phases"""
        guidance = {
            'next_phase_focus': [],
            'investigation_priorities': [],
            'document_requests': [],
            'deposition_strategy': []
        }
        
        # Phase-specific guidance
        if phase == "0A":
            guidance['next_phase_focus'] = [
                'Apply legal weapons to case documents',
                'Hunt for elements of fraud and conspiracy',
                'Identify adverse inference opportunities'
            ]
        elif phase == "0B":
            guidance['next_phase_focus'] = [
                'Expand admissions found',
                'Map contradiction evolution',
                'Identify missing evidence'
            ]
        elif phase in ["1", "2", "3"]:
            guidance['next_phase_focus'] = [
                'Deepen pattern analysis',
                'Connect contradictions across documents',
                'Build timeline impossibilities'
            ]
        
        return guidance
    
    def _identify_knowledge_gaps(self, knowledge: Dict) -> List[str]:
        """Identify gaps in current knowledge"""
        gaps = []
        
        # Check for missing evidence references
        if 'missing_evidence' in knowledge:
            gaps.append('Missing documents identified - need targeted discovery')
        
        # Check for unexplored patterns
        pattern_count = sum(len(p) for p in self.knowledge_graph['patterns'].values())
        if pattern_count < 10:
            gaps.append('Limited pattern detection - deeper analysis needed')
        
        # Check for entity relationships
        entity_count = len(self.knowledge_graph['entities'])
        if entity_count < 5:
            gaps.append('Insufficient entity mapping - need relationship analysis')
        
        return gaps
    
    def _build_cross_phase_insights(self, current_phase: str) -> Dict:
        """Build insights connecting to previous phases"""
        insights = {
            'reinforced_findings': [],
            'evolved_patterns': [],
            'connected_evidence': []
        }
        
        # Get previous phases
        try:
            current_index = self.phase_order.index(current_phase)
            previous_phases = self.phase_order[:current_index]
            
            for prev_phase in previous_phases:
                if prev_phase in self.knowledge_store:
                    # Connect findings
                    prev_knowledge = self.knowledge_store[prev_phase]
                    
                    # Identify reinforced findings
                    if 'key_findings' in prev_knowledge:
                        insights['reinforced_findings'].append({
                            'from_phase': prev_phase,
                            'finding_count': len(prev_knowledge.get('key_findings', []))
                        })
        except ValueError:
            pass
        
        return insights
    
    def get_previous_knowledge(self, current_phase: str) -> Dict:
        """
        Enhanced retrieval that provides structured knowledge for Claude
        """
        previous = {}
        
        try:
            current_index = self.phase_order.index(current_phase)
            
            for phase in self.phase_order[:current_index]:
                if phase in self.knowledge_store:
                    # Provide both raw and structured knowledge
                    previous[phase] = {
                        'raw': self.knowledge_store[phase],
                        'structured': self._get_structured_summary(phase)
                    }
        except ValueError:
            print(f"Warning: Unknown phase {current_phase}")
        
        # Add the knowledge graph summary
        previous['knowledge_graph'] = self._get_graph_summary()
        
        return previous
    
    def _get_structured_summary(self, phase: str) -> Dict:
        """Get structured summary of phase knowledge"""
        summary = {
            'phase': phase,
            'key_weapons': [],
            'critical_findings': [],
            'patterns': [],
            'contradictions': []
        }
        
        # Extract phase-specific highlights
        if phase == "0A":
            summary['key_weapons'] = self.knowledge_graph['legal_weapons']['nuclear'][:5]
        elif phase == "0B":
            summary['critical_findings'] = self.knowledge_graph['admissions']['judicial'][:5]
        
        return summary
    
    def _get_graph_summary(self) -> Dict:
        """Get summary of entire knowledge graph"""
        return {
            'total_weapons': sum(len(w) for w in self.knowledge_graph['legal_weapons'].values()),
            'total_admissions': sum(len(a) for a in self.knowledge_graph['admissions'].values()),
            'total_contradictions': sum(len(c) for c in self.knowledge_graph['contradictions'].values()),
            'total_patterns': sum(len(p) for p in self.knowledge_graph['patterns'].values()),
            'entities_mapped': len(self.knowledge_graph['entities']),
            'timeline_events': len(self.knowledge_graph['timeline']['events'])
        }
    
    def _save_raw_knowledge(self, phase: str, knowledge: Dict):
        """Save raw knowledge (backward compatible)"""
        filename = self.storage_path / f"phase_{phase}_knowledge.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, default=str, ensure_ascii=False)
    
    def _save_optimised_knowledge(self, phase: str, optimised: Dict):
        """Save optimised knowledge for Claude"""
        filename = self.storage_path / f"phase_{phase}_optimised.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(optimised, f, indent=2, default=str, ensure_ascii=False)
    
    def _save_knowledge_graph(self):
        """Save the knowledge graph"""
        filename = self.storage_path / "knowledge_graph.json"
        
        # Convert defaultdict to regular dict for JSON serialisation
        graph_to_save = {
            'legal_weapons': self.knowledge_graph['legal_weapons'],
            'admissions': self.knowledge_graph['admissions'],
            'contradictions': self.knowledge_graph['contradictions'],
            'patterns': self.knowledge_graph['patterns'],
            'entities': dict(self.knowledge_graph['entities']),
            'timeline': self.knowledge_graph['timeline'],
            'strategy': self.knowledge_graph['strategy']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(graph_to_save, f, indent=2, default=str, ensure_ascii=False)
    
    def _load_existing_knowledge(self):
        """Load existing knowledge from disk"""
        try:
            # Load raw knowledge (backward compatible)
            for phase in self.phase_order:
                filename = self.storage_path / f"phase_{phase}_knowledge.json"
                if filename.exists():
                    with open(filename, 'r', encoding='utf-8') as f:
                        self.knowledge_store[phase] = json.load(f)
                    print(f"Loaded existing knowledge for phase {phase}")
            
            # Load knowledge graph if exists
            graph_file = self.storage_path / "knowledge_graph.json"
            if graph_file.exists():
                with open(graph_file, 'r', encoding='utf-8') as f:
                    saved_graph = json.load(f)
                    # Restore the graph
                    for key in saved_graph:
                        if key == 'entities':
                            self.knowledge_graph['entities'] = defaultdict(
                                lambda: {'mentions': [], 'relationships': [], 'suspicious_behaviour': [], 'timeline': []},
                                saved_graph['entities']
                            )
                        else:
                            self.knowledge_graph[key] = saved_graph[key]
                print("Loaded existing knowledge graph")
                    
        except Exception as e:
            print(f"Error loading existing knowledge: {e}")
    
    def _migrate_to_optimised_format(self):
        """Migrate existing knowledge to optimised format if needed"""
        for phase, knowledge in self.knowledge_store.items():
            optimised_file = self.storage_path / f"phase_{phase}_optimised.json"
            if not optimised_file.exists() and knowledge:
                # Extract structured knowledge
                self._extract_structured_knowledge(phase, knowledge)
                print(f"Migrated phase {phase} to optimised format")
    
    # Backward compatible methods
    def store_phase_knowledge(self, phase: str, knowledge: Dict) -> bool:
        """Backward compatible method"""
        return self.store_phase_knowledge(phase, knowledge)
    
    def get_phase_knowledge(self, phase: str) -> Optional[Dict]:
        """Backward compatible method"""
        return self.knowledge_store.get(phase)
    
    def get_all_knowledge(self) -> Dict:
        """Backward compatible method"""
        return self.knowledge_store
    
    def get_completed_phases(self) -> List[str]:
        """Backward compatible method"""
        return list(self.knowledge_store.keys())
    
    def clear_knowledge(self, phase: Optional[str] = None):
        """Clear stored knowledge"""
        if phase:
            if phase in self.knowledge_store:
                del self.knowledge_store[phase]
            
            # Clear all phase files
            for pattern in [f"phase_{phase}_knowledge.json", f"phase_{phase}_optimised.json"]:
                file_path = self.storage_path / pattern
                if file_path.exists():
                    file_path.unlink()
            
            print(f"Cleared knowledge for phase {phase}")
        else:
            self.knowledge_store = {}
            self.knowledge_graph = self.__init__.__defaults__[0]  # Reset to default
            
            # Clear all files
            for file in self.storage_path.glob("*.json"):
                file.unlink()
            
            print("Cleared all knowledge")
    
    def generate_summary(self) -> Dict:
        """Enhanced summary generation"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'phases_completed': self.get_completed_phases(),
            'knowledge_graph_stats': self._get_graph_summary(),
            'nuclear_weapons': self.knowledge_graph['legal_weapons']['nuclear'][:5],
            'critical_admissions': self.knowledge_graph['admissions']['judicial'][:5],
            'timeline_impossibilities': self.knowledge_graph['contradictions']['timeline'][:5],
            'fraud_indicators': self.knowledge_graph['patterns']['fraud_indicators'][:5],
            'key_entities': list(self.knowledge_graph['entities'].keys())[:10],
            'strategic_priorities': self._generate_strategic_priorities()
        }
        
        return summary
    
    def _generate_strategic_priorities(self) -> List[str]:
        """Generate strategic priorities based on accumulated knowledge"""
        priorities = []
        
        # Priority 1: Nuclear weapons available
        if self.knowledge_graph['legal_weapons']['nuclear']:
            priorities.append("Deploy nuclear legal weapons for summary judgment")
        
        # Priority 2: Criminal crossovers
        if self.knowledge_graph['legal_weapons']['criminal']:
            priorities.append("Prepare criminal referrals for maximum leverage")
        
        # Priority 3: Timeline impossibilities
        if len(self.knowledge_graph['contradictions']['timeline']) > 3:
            priorities.append("Exploit timeline impossibilities for credibility destruction")
        
        # Priority 4: Fraud patterns
        if self.knowledge_graph['patterns']['fraud_indicators']:
            priorities.append("Build fraud case from identified patterns")
        
        # Priority 5: Missing documents
        if self.knowledge_graph['patterns']['missing_documents']:
            priorities.append("Pursue adverse inference for withheld documents")
        
        return priorities[:5]
    
    def export_knowledge(self, export_path: str = "./exports") -> str:
        """Enhanced export with full intelligence"""
        Path(export_path).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(export_path) / f"lismore_intelligence_{timestamp}.json"
        
        export_data = {
            'case': 'Lismore Capital vs Process Holdings Ltd',
            'export_timestamp': datetime.now().isoformat(),
            'phases_completed': self.get_completed_phases(),
            'raw_knowledge': self.knowledge_store,
            'knowledge_graph': {
                'legal_weapons': self.knowledge_graph['legal_weapons'],
                'admissions': self.knowledge_graph['admissions'],
                'contradictions': self.knowledge_graph['contradictions'],
                'patterns': self.knowledge_graph['patterns'],
                'entities': dict(self.knowledge_graph['entities']),
                'timeline': self.knowledge_graph['timeline'],
                'strategy': self.knowledge_graph['strategy']
            },
            'strategic_summary': self.generate_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"✅ Intelligence exported to {filename}")
        return str(filename)