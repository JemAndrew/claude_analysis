#!/usr/bin/env python3
"""
Enhanced KnowledgeManager with Optimal Phase 0A Storage
Maintains compatibility while maximising knowledge retention
Save as: src/knowledge/knowledge_manage.py
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class KnowledgeManager:
    """
    Enhanced KnowledgeManager - same interface, optimal storage
    Creates structured knowledge files for maximum retention
    """
    
    def __init__(self, storage_path: str = "./knowledge_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Phase ordering
        self.phase_order = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        # Core knowledge structures
        self.knowledge_graph = {
            'legal_weapons': {
                'nuclear': [],
                'high_impact': [],
                'procedural': [],
                'criminal': []
            },
            'admissions': {
                'explicit': [],
                'implicit': [],
                'judicial': []
            },
            'contradictions': {
                'internal': [],
                'timeline': [],
                'financial': [],
                'factual': []
            },
            'patterns': {
                'fraud_indicators': [],
                'conspiracy_markers': [],
                'cover_up_behaviour': [],
                'missing_documents': []
            },
            'entities': defaultdict(lambda: {
                'mentions': [],
                'relationships': [],
                'suspicious_behaviour': [],
                'timeline': []
            }),
            'timeline': {
                'events': [],
                'impossibilities': [],
                'gaps': [],
                'critical_periods': []
            },
            'strategy': {
                'attack_vectors': [],
                'settlement_leverage': [],
                'cross_exam_traps': [],
                'document_requests': []
            }
        }
        
        # Phase-specific storage
        self.knowledge_store = {}
        
        # Load existing knowledge
        self._load_existing_knowledge()
    
    def store_phase_knowledge(self, phase: str, knowledge: Dict) -> None:
        """
        Enhanced storage for Phase 0A with optimal structure
        Maintains compatibility while maximising retention
        """
        try:
            # Create output directory
            output_dir = Path(self.storage_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Store in memory
            self.knowledge_store[phase] = knowledge
            
            # Main results file (backward compatible)
            knowledge_to_store = {
                'phase': phase,
                'timestamp': datetime.now().isoformat(),
                'documents_analysed': knowledge.get('documents_analysed', 0),
                'synthesis': knowledge.get('synthesis', ''),
                'combined_analysis': knowledge.get('combined_analysis', []),
                'results': knowledge
            }
            
            # Save main results file
            output_file = output_dir / f'phase_{phase}_results.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_to_store, f, indent=2, default=str)
            
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"💾 Stored Phase {phase} knowledge to {output_file}")
            print(f"   File size: {file_size_mb:.2f} MB")
            
            # FOR PHASE 0A: Create optimal structured storage
            if phase == "0A":
                self._create_optimal_phase_0a_storage(knowledge)
            
            # Update knowledge graph
            self._update_knowledge_graph_from_phase(phase, knowledge)
            
            # Save enhanced knowledge graph
            kg_file = output_dir / 'knowledge_graph.json'
            with open(kg_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_graph, f, indent=2, default=str)
            
            print(f"✅ Knowledge stored with optimal structure")
            
        except Exception as e:
            print(f"⚠️ Error storing knowledge: {e}")
    
    def _create_optimal_phase_0a_storage(self, knowledge: Dict):
        """
        Create optimal structured storage for Phase 0A
        This maximises Claude's ability to recall and use the knowledge
        """
        print("\n🧠 Creating optimal Phase 0A knowledge structure...")
        
        # 1. Extract and store legal weapons
        weapons_file = self.storage_path / 'phase_0A_weapons.json'
        weapons = self._extract_weapons(knowledge)
        with open(weapons_file, 'w', encoding='utf-8') as f:
            json.dump(weapons, f, indent=2)
        print(f"   ✅ Extracted {sum(len(v) for v in weapons.values())} legal weapons")
        
        # 2. Extract and store doctrines
        doctrines_file = self.storage_path / 'phase_0A_doctrines.json'
        doctrines = self._extract_doctrines(knowledge)
        with open(doctrines_file, 'w', encoding='utf-8') as f:
            json.dump(doctrines, f, indent=2)
        print(f"   ✅ Extracted {len(doctrines)} legal doctrines")
        
        # 3. Extract and store precedents
        precedents_file = self.storage_path / 'phase_0A_precedents.json'
        precedents = self._extract_precedents(knowledge)
        with open(precedents_file, 'w', encoding='utf-8') as f:
            json.dump(precedents, f, indent=2)
        print(f"   ✅ Extracted {len(precedents)} case precedents")
        
        # 4. Create weapon combinations matrix
        combinations_file = self.storage_path / 'phase_0A_combinations.json'
        combinations = self._create_combinations_matrix(weapons, doctrines)
        with open(combinations_file, 'w', encoding='utf-8') as f:
            json.dump(combinations, f, indent=2)
        print(f"   ✅ Created {len(combinations)} weapon combinations")
        
        # 5. Create strategic playbook
        playbook_file = self.storage_path / 'phase_0A_playbook.json'
        playbook = self._create_strategic_playbook(weapons, doctrines, precedents)
        with open(playbook_file, 'w', encoding='utf-8') as f:
            json.dump(playbook, f, indent=2)
        print(f"   ✅ Created strategic playbook with {len(playbook)} strategies")
        
        # 6. Create quick reference index
        index_file = self.storage_path / 'phase_0A_index.json'
        index = self._create_quick_reference_index(knowledge)
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
        print(f"   ✅ Created quick reference index")
    
    def _extract_weapons(self, knowledge: Dict) -> Dict:
        """Extract and categorise legal weapons"""
        weapons = {
            'nuclear': [],
            'high_impact': [],
            'procedural': [],
            'criminal': [],
            'defensive': []
        }
        
        # Parse synthesis and combined analysis
        text_sources = [
            knowledge.get('synthesis', ''),
            *knowledge.get('combined_analysis', [])
        ]
        
        for text in text_sources:
            if not text:
                continue
            
            # Nuclear weapons
            nuclear_patterns = [
                r'(?:nuclear|case.?ending|instant.?victory|immediate.?win)[:\s]+([^.]+)',
                r'(?:void|invalid|nullif)[:\s]+([^.]+)',
                r'(?:fraud.?vitiate)[:\s]+([^.]+)'
            ]
            for pattern in nuclear_patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    weapons['nuclear'].append({
                        'weapon': match.group(1).strip(),
                        'context': text[max(0, match.start()-100):match.end()+100]
                    })
            
            # Criminal crossovers
            if any(word in text.lower() for word in ['criminal', 'fraud', 'bribe', 'corrupt']):
                criminal_matches = re.finditer(r'(?:criminal|fraud|brib|corrupt)[^.]+\.', text, re.IGNORECASE)
                for match in criminal_matches:
                    weapons['criminal'].append({
                        'weapon': match.group(0).strip(),
                        'statute': self._extract_statute(match.group(0))
                    })
        
        return weapons
    
    def _extract_doctrines(self, knowledge: Dict) -> List[Dict]:
        """Extract legal doctrines"""
        doctrines = []
        
        # Common doctrine patterns
        doctrine_keywords = [
            'doctrine', 'principle', 'rule', 'test', 'standard',
            'estoppel', 'waiver', 'laches', 'equity'
        ]
        
        text = knowledge.get('synthesis', '') + ' '.join(knowledge.get('combined_analysis', []))
        
        for keyword in doctrine_keywords:
            pattern = rf'\b{keyword}[^.]*\.'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                doctrines.append({
                    'doctrine': match.group(0).strip(),
                    'type': keyword,
                    'application': self._determine_application(match.group(0))
                })
        
        return doctrines
    
    def _extract_precedents(self, knowledge: Dict) -> List[Dict]:
        """Extract case precedents"""
        precedents = []
        
        # Case citation patterns
        case_patterns = [
            r'([A-Z][a-z]+\s+v\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\[(\d{4})\]\s+[A-Z]+\s+\d+',
            r'\(\d{4}\)\s+\d+\s+[A-Z]+\s+\d+'
        ]
        
        text = knowledge.get('synthesis', '') + ' '.join(knowledge.get('combined_analysis', []))
        
        for pattern in case_patterns:
            for match in re.finditer(pattern, text):
                precedents.append({
                    'case': match.group(0),
                    'context': text[max(0, match.start()-100):match.end()+100],
                    'principle': self._extract_principle(text[match.start():match.end()+200])
                })
        
        return precedents
    
    def _create_combinations_matrix(self, weapons: Dict, doctrines: List) -> List[Dict]:
        """Create matrix of weapon combinations for multiplier effects"""
        combinations = []
        
        # Powerful combinations
        if weapons['nuclear'] and weapons['criminal']:
            combinations.append({
                'primary': 'Fraud vitiates everything',
                'secondary': 'Criminal prosecution threat',
                'effect': 'Immediate settlement pressure',
                'multiplier': 10
            })
        
        if weapons['nuclear'] and doctrines:
            for nuclear in weapons['nuclear'][:3]:
                for doctrine in doctrines[:3]:
                    combinations.append({
                        'weapon': nuclear.get('weapon', ''),
                        'doctrine': doctrine.get('doctrine', ''),
                        'combined_effect': 'Enhanced legal position'
                    })
        
        return combinations
    
    def _create_strategic_playbook(self, weapons: Dict, doctrines: List, precedents: List) -> List[Dict]:
        """Create strategic playbook for deployment"""
        playbook = []
        
        # Opening gambits
        if weapons['nuclear']:
            playbook.append({
                'phase': 'Opening',
                'strategy': 'Nuclear Strike',
                'weapons': weapons['nuclear'][:3],
                'expected_outcome': 'Immediate capitulation or major concessions'
            })
        
        # Mid-game strategies
        if weapons['high_impact']:
            playbook.append({
                'phase': 'Mid-game',
                'strategy': 'Sustained Pressure',
                'weapons': weapons['high_impact'][:5],
                'expected_outcome': 'Erosion of opponent position'
            })
        
        # End game
        if weapons['criminal']:
            playbook.append({
                'phase': 'End-game',
                'strategy': 'Criminal Referral',
                'weapons': weapons['criminal'][:3],
                'expected_outcome': 'Total victory or maximum settlement'
            })
        
        return playbook
    
    def _create_quick_reference_index(self, knowledge: Dict) -> Dict:
        """Create index for quick lookups during later phases"""
        return {
            'total_documents': knowledge.get('documents_analysed', 0),
            'synthesis_length': len(knowledge.get('synthesis', '')),
            'batch_count': len(knowledge.get('combined_analysis', [])),
            'key_terms': self._extract_key_terms(knowledge),
            'document_references': self._extract_doc_references(knowledge),
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_key_terms(self, knowledge: Dict) -> List[str]:
        """Extract key legal terms for quick reference"""
        terms = []
        text = knowledge.get('synthesis', '')
        
        # Important legal terms
        important_terms = [
            'fraud', 'breach', 'void', 'estoppel', 'waiver',
            'jurisdiction', 'limitation', 'damages', 'conspiracy'
        ]
        
        for term in important_terms:
            if term in text.lower():
                terms.append(term)
        
        return terms
    
    def _extract_doc_references(self, knowledge: Dict) -> List[str]:
        """Extract document references"""
        refs = []
        text = knowledge.get('synthesis', '') + ' '.join(knowledge.get('combined_analysis', []))
        
        # Document reference patterns
        doc_pattern = r'(?:DOC_\d{4}|RULE_\d{4}|TEXT_\d{4})'
        
        for match in re.finditer(doc_pattern, text):
            if match.group(0) not in refs:
                refs.append(match.group(0))
        
        return refs
    
    def _extract_statute(self, text: str) -> str:
        """Extract statute references"""
        statute_pattern = r'(?:s\.|section)\s*\d+|Act\s+\d{4}'
        match = re.search(statute_pattern, text, re.IGNORECASE)
        return match.group(0) if match else ''
    
    def _determine_application(self, doctrine_text: str) -> str:
        """Determine how to apply a doctrine"""
        if 'fraud' in doctrine_text.lower():
            return 'Use to vitiate entire contract'
        elif 'estoppel' in doctrine_text.lower():
            return 'Prevent opponent from changing position'
        elif 'waiver' in doctrine_text.lower():
            return 'Show opponent gave up rights'
        else:
            return 'General application'
    
    def _extract_principle(self, text: str) -> str:
        """Extract legal principle from case text"""
        # Look for principle indicators
        if 'held that' in text.lower():
            return text.split('held that')[1][:100]
        elif 'principle' in text.lower():
            return text.split('principle')[1][:100]
        else:
            return text[:100]
    
    def _update_knowledge_graph_from_phase(self, phase: str, knowledge: Dict):
        """Update knowledge graph with phase results"""
        if phase == "0A" and 'synthesis' in knowledge:
            # Update legal weapons
            weapons = self._extract_weapons(knowledge)
            for category, items in weapons.items():
                if category in self.knowledge_graph['legal_weapons']:
                    self.knowledge_graph['legal_weapons'][category].extend(items)
    
    def get_previous_knowledge(self, current_phase: str) -> Dict:
        """Get knowledge from previous phases - enhanced for Phase 0A"""
        previous = {}
        
        try:
            current_index = self.phase_order.index(current_phase)
            
            for phase in self.phase_order[:current_index]:
                if phase == "0A":
                    # Load all Phase 0A structured files for maximum context
                    phase_0a_knowledge = {
                        'main': self._load_phase_file(phase),
                        'weapons': self._load_file('phase_0A_weapons.json'),
                        'doctrines': self._load_file('phase_0A_doctrines.json'),
                        'precedents': self._load_file('phase_0A_precedents.json'),
                        'combinations': self._load_file('phase_0A_combinations.json'),
                        'playbook': self._load_file('phase_0A_playbook.json'),
                        'index': self._load_file('phase_0A_index.json')
                    }
                    previous[phase] = phase_0a_knowledge
                else:
                    previous[phase] = self._load_phase_file(phase)
                    
        except ValueError:
            print(f"Warning: Unknown phase {current_phase}")
        
        return previous
    
    def _load_phase_file(self, phase: str) -> Optional[Dict]:
        """Load phase results file"""
        phase_file = self.storage_path / f'phase_{phase}_results.json'
        if phase_file.exists():
            with open(phase_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('results', data)
        return None
    
    def _load_file(self, filename: str) -> Optional[Dict]:
        """Load any file from knowledge store"""
        file_path = self.storage_path / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_completed_phases(self) -> List[str]:
        """Get list of completed phases"""
        completed = []
        
        if self.storage_path.exists():
            for phase_file in self.storage_path.glob('phase_*_results.json'):
                phase = phase_file.stem.replace('phase_', '').replace('_results', '')
                if phase in self.phase_order:
                    completed.append(phase)
        
        completed.sort(key=lambda x: self.phase_order.index(x) if x in self.phase_order else 999)
        return completed
    
    def _load_existing_knowledge(self):
        """Load existing knowledge from disk"""
        try:
            for phase in self.phase_order:
                phase_file = self.storage_path / f'phase_{phase}_results.json'
                if phase_file.exists():
                    with open(phase_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.knowledge_store[phase] = data.get('results', data)
            
            graph_file = self.storage_path / 'knowledge_graph.json'
            if graph_file.exists():
                with open(graph_file, 'r', encoding='utf-8') as f:
                    saved_graph = json.load(f)
                    for key, value in saved_graph.items():
                        if key in self.knowledge_graph and isinstance(self.knowledge_graph[key], dict):
                            self.knowledge_graph[key].update(value)
                        else:
                            self.knowledge_graph[key] = value
                    
        except Exception as e:
            pass  # Silent fail on load
    
    # Backward compatible methods
    def get_phase_knowledge(self, phase: str) -> Optional[Dict]:
        """Get knowledge for a specific phase"""
        if phase in self.knowledge_store:
            return self.knowledge_store[phase]
        return self._load_phase_file(phase)
    
    def get_all_knowledge(self) -> Dict:
        """Get all stored knowledge"""
        all_knowledge = {}
        for phase in self.phase_order:
            knowledge = self.get_phase_knowledge(phase)
            if knowledge:
                all_knowledge[phase] = knowledge
        return all_knowledge
    
    def clear_knowledge(self, phase: Optional[str] = None):
        """Clear stored knowledge"""
        if phase:
            if phase in self.knowledge_store:
                del self.knowledge_store[phase]
            
            # Delete all phase files
            for pattern in [f'phase_{phase}_*.json']:
                for file in self.storage_path.glob(pattern):
                    file.unlink()
        else:
            self.knowledge_store = {}
            if self.storage_path.exists():
                for file in self.storage_path.glob("*.json"):
                    file.unlink()
    
    def generate_summary(self) -> Dict:
        """Generate summary of all knowledge"""
        completed = self.get_completed_phases()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'phases_completed': completed,
            'total_phases': len(completed)
        }
        
        # Special summary for Phase 0A
        if '0A' in completed:
            weapons = self._load_file('phase_0A_weapons.json')
            if weapons:
                summary['phase_0A_weapons'] = {
                    'nuclear': len(weapons.get('nuclear', [])),
                    'criminal': len(weapons.get('criminal', [])),
                    'total': sum(len(v) for v in weapons.values())
                }
        
        return summary
    
    def export_knowledge(self, export_path: str = "./exports") -> str:
        """Export all knowledge"""
        Path(export_path).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(export_path) / f"knowledge_export_{timestamp}.json"
        
        export_data = {
            'case': 'Lismore vs Process Holdings',
            'export_timestamp': datetime.now().isoformat(),
            'phases_completed': self.get_completed_phases(),
            'knowledge': self.get_all_knowledge(),
            'summary': self.generate_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return str(filename)