#!/usr/bin/env python3
"""
Memory Manager - Complete knowledge retention across phases
Ensures Claude has FULL context with complete details, not summaries
British English throughout - Lismore v Process Holdings
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class MemoryManager:
    """Manages complete memory persistence across all phases"""
    
    def __init__(self, config):
        """Initialise memory manager with full context retention"""
        self.config = config
        self.memory_dir = config.memory_bank_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all memory components - FULL DETAIL
        self.phase_memories = self.load_phase_memories()
        self.complete_case_knowledge = self.load_complete_case_knowledge()
        self.document_intelligence = self.load_document_intelligence()
        self.entity_intelligence = self.load_entity_intelligence()
        self.pattern_library = self.load_pattern_library()
        self.contradiction_database = self.load_contradiction_database()
        self.timeline_knowledge = self.load_timeline_knowledge()
        self.investigation_history = self.load_investigation_history()
        self.strategic_insights = self.load_strategic_insights()
        
        self.expertise_level = self.determine_expertise_level()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Memory Manager initialised - Expertise: {self.expertise_level}")
    
    # ==================== LOADING METHODS ====================
    
    def load_phase_memories(self) -> Dict:
        """Load complete memory from all completed phases"""
        memory_file = self.memory_dir / "phase_memories.json"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_complete_case_knowledge(self) -> Dict:
        """Load complete case knowledge (full details, not summaries)"""
        knowledge_file = self.memory_dir / "complete_case_knowledge.json"
        if knowledge_file.exists():
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'legal_framework': {},
            'case_overview': {},
            'parties': {},
            'key_events': [],
            'legal_issues': [],
            'factual_disputes': [],
            'evidence_map': {},
            'document_catalogue': {},
            'lismore_position': {},
            'process_holdings_position': {}
        }
    
    def load_document_intelligence(self) -> Dict:
        """Load complete document analysis results"""
        doc_file = self.memory_dir / "document_intelligence.json"
        if doc_file.exists():
            with open(doc_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_entity_intelligence(self) -> Dict:
        """Load complete entity profiles and relationships"""
        entity_file = self.memory_dir / "entity_intelligence.json"
        if entity_file.exists():
            with open(entity_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_pattern_library(self) -> List[Dict]:
        """Load all discovered patterns with full evidence"""
        pattern_file = self.memory_dir / "pattern_library.json"
        if pattern_file.exists():
            with open(pattern_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def load_contradiction_database(self) -> List[Dict]:
        """Load all contradictions with complete context"""
        contra_file = self.memory_dir / "contradiction_database.json"
        if contra_file.exists():
            with open(contra_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def load_timeline_knowledge(self) -> Dict:
        """Load complete timeline with all events"""
        timeline_file = self.memory_dir / "timeline_knowledge.json"
        if timeline_file.exists():
            with open(timeline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'events': [], 'gaps': [], 'impossibilities': []}
    
    def load_investigation_history(self) -> List[Dict]:
        """Load all investigation results"""
        invest_file = self.memory_dir / "investigation_history.json"
        if invest_file.exists():
            with open(invest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def load_strategic_insights(self) -> Dict:
        """Load strategic intelligence for Lismore"""
        strategy_file = self.memory_dir / "strategic_insights.json"
        if strategy_file.exists():
            with open(strategy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'lismore_strengths': [],
            'process_weaknesses': [],
            'attack_vectors': [],
            'defensive_positions': [],
            'settlement_leverage': [],
            'nuclear_evidence': []
        }
    
    # ==================== EXPERTISE TRACKING ====================
    
    def determine_expertise_level(self) -> str:
        """Determine current expertise level based on phases completed"""
        completed_phases = len(self.phase_memories)
        
        if completed_phases == 0:
            return "NOVICE"
        elif completed_phases == 1:
            return "BASIC"
        elif completed_phases == 2:
            return "DEVELOPING"
        elif completed_phases == 3:
            return "INTERMEDIATE"
        elif completed_phases == 4:
            return "ADVANCED"
        elif completed_phases == 5:
            return "EXPERT"
        else:
            return "MASTER"
    
    # ==================== UPDATE METHODS ====================
    
    def update_after_phase(self, phase_num: int, phase_results: Dict):
        """Update ALL memory components with complete phase results"""
        
        self.logger.info(f"Updating memory after Phase {phase_num}")
        
        # Store COMPLETE phase results (not summaries!)
        self.phase_memories[f"phase_{phase_num}"] = {
            "completion_date": datetime.now().isoformat(),
            "complete_results": phase_results,  # FULL RESULTS
            "insights_count": self.count_insights(phase_results),
            "discoveries": self.extract_discoveries(phase_results),
            "new_patterns": self.extract_patterns(phase_results),
            "new_contradictions": self.extract_contradictions(phase_results),
            "strategic_findings": self.extract_strategic_findings(phase_results),
            "phase_summary": phase_results.get('summary', 'No summary')
        }
        
        # Update complete case knowledge
        self.merge_case_knowledge(phase_results)
        
        # Update document intelligence
        self.merge_document_intelligence(phase_results)
        
        # Update entity intelligence
        self.merge_entity_intelligence(phase_results)
        
        # Update pattern library
        self.merge_patterns(phase_results)
        
        # Update contradiction database
        self.merge_contradictions(phase_results)
        
        # Update timeline
        self.merge_timeline(phase_results)
        
        # Update investigation history
        self.merge_investigations(phase_results)
        
        # Update strategic insights
        self.merge_strategic_insights(phase_results)
        
        # Update expertise level
        self.expertise_level = self.determine_expertise_level()
        
        # Save everything to disk
        self.save_all_memory()
        
        self.logger.info(f"Memory updated - Expertise: {self.expertise_level}, Total insights: {self.count_insights(phase_results)}")
    
    # ==================== CONTEXT BUILDING ====================
    
    def build_context_for_phase(self, phase_num: int) -> str:
        """Build COMPLETE context with FULL details for next phase"""
        
        if phase_num == 0:
            return self.build_phase_0_context()
        elif phase_num == 1:
            return self.build_phase_1_context()
        elif phase_num == 2:
            return self.build_phase_2_context()
        elif phase_num == 3:
            return self.build_phase_3_context()
        elif phase_num == 4:
            return self.build_phase_4_context()
        elif phase_num == 5:
            return self.build_phase_5_context()
        else:
            return self.build_phase_6_context()
    
    def build_phase_0_context(self) -> str:
        """Phase 0 context - Knowledge loading"""
        return """<initial_analysis>
PHASE 0: KNOWLEDGE FOUNDATION

You are beginning comprehensive analysis of Lismore v Process Holdings arbitration.
This is your first exposure to the case materials.

CASE OVERVIEW:
- Lismore Capital vs Process Holdings Ltd
- Arbitration dispute involving P&ID, Nigeria, VR Capital
- Complex commercial litigation with significant financial stakes
- Document withholding suspected

YOUR OBJECTIVE:
1. Absorb ALL legal knowledge (UK contract law, arbitration principles, litigation strategy)
2. Understand complete case context (parties, relationships, timeline, disputes)
3. Build strategic intelligence foundation

APPROACH:
- Read everything carefully with perfect recall
- Make connections between legal principles and case facts
- Identify strategic opportunities for Lismore
- Note what evidence would be most valuable
- Think like a top litigation barrister

REMEMBER: We represent Lismore. Every analysis should identify how to strengthen Lismore's position.

EXPERTISE LEVEL: NOVICE - Building foundation
</initial_analysis>"""
    
    def build_phase_1_context(self) -> str:
        """Phase 1 context with COMPLETE Phase 0 knowledge"""
        
        phase_0 = self.phase_memories.get('phase_0', {})
        
        context = f"""<accumulated_knowledge>
PHASE 1: DOCUMENT ORGANISATION & CATALOGUING

=== COMPLETE LEGAL FRAMEWORK (PHASE 0) ===
{json.dumps(self.complete_case_knowledge.get('legal_framework', {}), indent=2, ensure_ascii=False)[:20000]}

=== COMPLETE CASE OVERVIEW (PHASE 0) ===
{json.dumps(self.complete_case_knowledge.get('case_overview', {}), indent=2, ensure_ascii=False)[:15000]}

=== ALL PARTIES IDENTIFIED ===
{json.dumps(self.complete_case_knowledge.get('parties', {}), indent=2, ensure_ascii=False)[:12000]}

=== KEY LEGAL ISSUES ===
{json.dumps(self.complete_case_knowledge.get('legal_issues', []), indent=2, ensure_ascii=False)[:10000]}

=== FACTUAL DISPUTES ===
{json.dumps(self.complete_case_knowledge.get('factual_disputes', []), indent=2, ensure_ascii=False)[:10000]}

=== LISMORE'S POSITION ===
{json.dumps(self.complete_case_knowledge.get('lismore_position', {}), indent=2, ensure_ascii=False)[:8000]}

=== PROCESS HOLDINGS' POSITION ===
{json.dumps(self.complete_case_knowledge.get('process_holdings_position', {}), indent=2, ensure_ascii=False)[:8000]}

=== PHASE 0 STRATEGIC DISCOVERIES ===
{json.dumps(phase_0.get('discoveries', []), indent=2, ensure_ascii=False)[:8000]}

EXPERTISE LEVEL: {self.expertise_level}

YOUR TASK:
You now have complete legal and case knowledge.
Organise ALL case documents into strategic categories for deep analysis.
You have COMPLETE FREEDOM to create categories that make sense.
Think: What organisation would best reveal their deception?
</accumulated_knowledge>"""
        
        return context
    
    def build_phase_2_context(self) -> str:
        """Phase 2 context with COMPLETE Phase 0-1 knowledge"""
        
        phase_1 = self.phase_memories.get('phase_1', {})
        
        context = f"""<accumulated_knowledge>
PHASE 2: FOUNDATION INTELLIGENCE - DOCUMENT ANALYSIS

=== COMPLETE LEGAL FRAMEWORK ===
{json.dumps(self.complete_case_knowledge.get('legal_framework', {}), indent=2, ensure_ascii=False)[:18000]}

=== ALL DOCUMENTS CATALOGUED ===
Total Documents: {len(self.document_intelligence)}
Categories Created: {list(set([d.get('category', 'uncategorised') for d in self.document_intelligence.values()])) if self.document_intelligence else 'None yet'}

=== COMPLETE DOCUMENT INTELLIGENCE ===
{json.dumps(self.document_intelligence, indent=2, ensure_ascii=False)[:25000]}

=== ALL ENTITIES IDENTIFIED ===
Total Entities: {len(self.entity_intelligence)}
{json.dumps(self.entity_intelligence, indent=2, ensure_ascii=False)[:18000]}

=== COMPLETE TIMELINE ===
Total Events: {len(self.timeline_knowledge.get('events', []))}
{json.dumps(self.timeline_knowledge, indent=2, ensure_ascii=False)[:18000]}

=== PHASE 1 COMPLETE RESULTS ===
{json.dumps(phase_1.get('complete_results', {}), indent=2, ensure_ascii=False)[:15000]}

=== ALL PHASE 1 DISCOVERIES ===
{json.dumps(phase_1.get('discoveries', []), indent=2, ensure_ascii=False)[:12000]}

EXPERTISE LEVEL: {self.expertise_level}

YOUR TASK:
Build foundational intelligence from organised documents.
- Classify every document by type, strategic value, evidentiary strength
- Construct COMPLETE timeline with all events
- Profile ALL parties (behaviour, motivations, vulnerabilities)
- Map document relationships and cross-references

Extract EVERYTHING. Miss nothing.
</accumulated_knowledge>"""
        
        return context
    
    def build_phase_3_context(self) -> str:
        """Phase 3 context with COMPLETE accumulated knowledge"""
        
        phase_2 = self.phase_memories.get('phase_2', {})
        
        context = f"""<accumulated_knowledge>
PHASE 3: PATTERN RECOGNITION & DEEP ANALYSIS

=== COMPLETE CASE MASTERY ===
{json.dumps(self.complete_case_knowledge, indent=2, ensure_ascii=False)[:25000]}

=== ALL PATTERNS DISCOVERED ===
Total Patterns: {len(self.pattern_library)}
High-Confidence Patterns: {len([p for p in self.pattern_library if p.get('confidence', 0) > 0.8])}
{json.dumps(self.pattern_library, indent=2, ensure_ascii=False)[:20000]}

=== ALL CONTRADICTIONS FOUND ===
Total Contradictions: {len(self.contradiction_database)}
Critical Contradictions: {len([c for c in self.contradiction_database if c.get('severity', 0) > 7])}
{json.dumps(self.contradiction_database, indent=2, ensure_ascii=False)[:20000]}

=== COMPLETE ENTITY NETWORK ===
{json.dumps(self.entity_intelligence, indent=2, ensure_ascii=False)[:18000]}

=== COMPLETE TIMELINE WITH GAPS ===
Timeline Events: {len(self.timeline_knowledge.get('events', []))}
Timeline Gaps: {len(self.timeline_knowledge.get('gaps', []))}
Impossibilities: {len(self.timeline_knowledge.get('impossibilities', []))}
{json.dumps(self.timeline_knowledge, indent=2, ensure_ascii=False)[:18000]}

=== ALL PHASE 2 DISCOVERIES ===
{json.dumps(phase_2.get('discoveries', []), indent=2, ensure_ascii=False)[:12000]}

=== STRATEGIC INTELLIGENCE SO FAR ===
{json.dumps(self.strategic_insights, indent=2, ensure_ascii=False)[:15000]}

EXPERTISE LEVEL: {self.expertise_level}

YOUR TASK:
Deep pattern recognition, contradiction mining, gap detection.
You have complete foundation intelligence.
Now find the DEVASTATING evidence:
- Patterns revealing systematic deception
- Contradictions destroying their credibility  
- Missing documents proving withholding
- Timeline impossibilities exposing lies

This is where we find the smoking gun.
</accumulated_knowledge>"""
        
        return context
    
    def build_phase_4_context(self) -> str:
        """Phase 4 context - EXPERT LEVEL adversarial intelligence"""
        
        phase_3 = self.phase_memories.get('phase_3', {})
        
        context = f"""<accumulated_knowledge>
PHASE 4: ADVERSARIAL INTELLIGENCE

YOU ARE NOW AN EXPERT IN THIS CASE.

=== COMPLETE CASE MASTERY ===
{json.dumps(self.complete_case_knowledge, indent=2, ensure_ascii=False)[:28000]}

=== HIGH-CONFIDENCE PATTERNS ===
{json.dumps([p for p in self.pattern_library if p.get('confidence', 0) > 0.8], indent=2, ensure_ascii=False)[:18000]}

=== CRITICAL CONTRADICTIONS ===
{json.dumps([c for c in self.contradiction_database if c.get('severity', 0) > 7], indent=2, ensure_ascii=False)[:18000]}

=== COMPLETE INVESTIGATION RESULTS ===
Total Investigations: {len(self.investigation_history)}
{json.dumps(self.investigation_history, indent=2, ensure_ascii=False)[:18000]}

=== MISSING DOCUMENTS IDENTIFIED ===
{json.dumps(self.timeline_knowledge.get('gaps', []), indent=2, ensure_ascii=False)[:10000]}

=== LISMORE STRATEGIC ARSENAL ===
Strengths: {len(self.strategic_insights.get('lismore_strengths', []))}
{json.dumps(self.strategic_insights.get('lismore_strengths', []), indent=2, ensure_ascii=False)[:12000]}

Attack Vectors: {len(self.strategic_insights.get('attack_vectors', []))}
{json.dumps(self.strategic_insights.get('attack_vectors', []), indent=2, ensure_ascii=False)[:12000]}

=== PROCESS HOLDINGS VULNERABILITIES ===
Weaknesses: {len(self.strategic_insights.get('process_weaknesses', []))}
{json.dumps(self.strategic_insights.get('process_weaknesses', []), indent=2, ensure_ascii=False)[:12000]}

=== PHASE 3 COMPLETE FINDINGS ===
{json.dumps(phase_3.get('complete_results', {}), indent=2, ensure_ascii=False)[:15000]}

EXPERTISE LEVEL: {self.expertise_level}

YOUR TASK:
Adversarial analysis and strategic warfare.
- RED TEAM: Predict Process Holdings' best arguments. Destroy them pre-emptively.
- OFFENSIVE: Develop Lismore's attack strategy using all discovered evidence.
- DEFENSIVE: Anticipate their attacks on our position and prepare counters.
- LEVERAGE: Identify settlement pressure points.

Think like their barrister. Then crush their case.
</accumulated_knowledge>"""
        
        return context
    
    def build_phase_5_context(self) -> str:
        """Phase 5 context - MASTER LEVEL creative strategy"""
        
        phase_4 = self.phase_memories.get('phase_4', {})
        
        context = f"""<accumulated_knowledge>
PHASE 5: NOVEL THEORIES & CREATIVE STRATEGY

YOU ARE NOW A MASTER OF THIS CASE.

=== INTELLIGENCE SUMMARY ===
Documents Analysed: {len(self.document_intelligence)}
Entities Mapped: {len(self.entity_intelligence)}
Patterns Discovered: {len(self.pattern_library)}
Contradictions Found: {len(self.contradiction_database)}
Timeline Events: {len(self.timeline_knowledge.get('events', []))}
Investigations Completed: {len(self.investigation_history)}
Phases Completed: {len(self.phase_memories)}

=== NUCLEAR EVIDENCE ===
{self.get_nuclear_evidence_summary()}

=== COMPLETE STRATEGIC PLAYBOOK ===
{json.dumps(self.strategic_insights, indent=2, ensure_ascii=False)[:25000]}

=== PHASE 4 ADVERSARIAL INTELLIGENCE ===
{json.dumps(phase_4.get('complete_results', {}), indent=2, ensure_ascii=False)[:18000]}

=== ALL PREVIOUS DISCOVERIES ===
Phase 1: {len(self.phase_memories.get('phase_1', {}).get('discoveries', []))} discoveries
Phase 2: {len(self.phase_memories.get('phase_2', {}).get('discoveries', []))} discoveries
Phase 3: {len(self.phase_memories.get('phase_3', {}).get('discoveries', []))} discoveries
Phase 4: {len(self.phase_memories.get('phase_4', {}).get('discoveries', []))} discoveries

EXPERTISE LEVEL: {self.expertise_level}

YOUR TASK:
Generate novel legal theories. Create unprecedented strategies.
Think beyond conventional litigation.

- What legal arguments have NEVER been made in this context?
- What procedural innovations could we employ?
- What cross-jurisdictional precedents apply creatively?
- What settlement structures would maximise our leverage?
- What's the "unthinkable" move that actually wins?

Think like a legal genius. Find the winning innovation.
</accumulated_knowledge>"""
        
        return context
    
    def build_phase_6_context(self) -> str:
        """Phase 6 context - COMPLETE MASTERY synthesis"""
        
        phase_5 = self.phase_memories.get('phase_5', {})
        
        context = f"""<accumulated_knowledge>
PHASE 6: SYNTHESIS & WEAPONISATION

YOU HAVE COMPLETE MASTERY OF THIS CASE.

=== COMPLETE INTELLIGENCE DATABASE ===
{self.generate_complete_intelligence_summary()}

=== ALL EVIDENCE ORGANISED BY SEVERITY ===
Nuclear Evidence: {self.count_evidence_by_severity('nuclear')}
Critical Evidence: {self.count_evidence_by_severity('critical')}
Important Evidence: {self.count_evidence_by_severity('important')}

=== NUCLEAR EVIDENCE READY FOR DEPLOYMENT ===
{self.get_nuclear_evidence_summary()}

=== ALL ARGUMENTS DEVELOPED ===
{self.generate_complete_argument_list()}

=== COMPLETE STRATEGIC ARSENAL ===
{json.dumps(self.strategic_insights, indent=2, ensure_ascii=False)[:30000]}

=== PHASE 5 NOVEL THEORIES ===
{json.dumps(phase_5.get('complete_results', {}), indent=2, ensure_ascii=False)[:18000]}

=== EVERY PHASE SYNTHESISED ===
Phase 0: {self.phase_memories.get('phase_0', {}).get('phase_summary', 'No summary')}
Phase 1: {self.phase_memories.get('phase_1', {}).get('phase_summary', 'No summary')}
Phase 2: {self.phase_memories.get('phase_2', {}).get('phase_summary', 'No summary')}
Phase 3: {self.phase_memories.get('phase_3', {}).get('phase_summary', 'No summary')}
Phase 4: {self.phase_memories.get('phase_4', {}).get('phase_summary', 'No summary')}
Phase 5: {self.phase_memories.get('phase_5', {}).get('phase_summary', 'No summary')}

EXPERTISE LEVEL: {self.expertise_level} - COMPLETE MASTERY ACHIEVED

YOUR FINAL TASK:
Transform all intelligence into litigation weapons.

DELIVERABLES:
1. Prioritised argument hierarchy (what to lead with)
2. Evidence packages (organised for tribunal presentation)
3. Implementation strategy (step-by-step litigation plan)
4. Settlement strategy (maximum pressure points)
5. Trial strategy (if settlement fails)
6. Final war room briefing (ready for barristers)

Package everything for victory. This must win.
</accumulated_knowledge>"""
        
        return context
    
    # ==================== MERGING METHODS ====================
    
    def merge_case_knowledge(self, phase_results: Dict):
        """Merge new discoveries into complete case knowledge"""
        if 'case_knowledge' in phase_results:
            for key, value in phase_results['case_knowledge'].items():
                if key in self.complete_case_knowledge:
                    if isinstance(value, dict):
                        self.complete_case_knowledge[key].update(value)
                    elif isinstance(value, list):
                        self.complete_case_knowledge[key].extend(value)
                    else:
                        self.complete_case_knowledge[key] = value
                else:
                    self.complete_case_knowledge[key] = value
    
    def merge_document_intelligence(self, phase_results: Dict):
        """Merge document analysis results"""
        if 'document_analysis' in phase_results:
            for doc_id, analysis in phase_results['document_analysis'].items():
                self.document_intelligence[doc_id] = analysis
        
        if 'documents' in phase_results:
            for doc in phase_results['documents']:
                if 'id' in doc:
                    self.document_intelligence[doc['id']] = doc
    
    def merge_entity_intelligence(self, phase_results: Dict):
        """Merge entity profiles"""
        if 'entities' in phase_results:
            for entity_id, profile in phase_results['entities'].items():
                self.entity_intelligence[entity_id] = profile
    
    def merge_patterns(self, phase_results: Dict):
        """Add new patterns to library"""
        if 'patterns' in phase_results:
            self.pattern_library.extend(phase_results['patterns'])
        
        if 'strategic_patterns' in phase_results:
            self.pattern_library.extend(phase_results['strategic_patterns'])
    
    def merge_contradictions(self, phase_results: Dict):
        """Add new contradictions to database"""
        if 'contradictions' in phase_results:
            self.contradiction_database.extend(phase_results['contradictions'])
    
    def merge_timeline(self, phase_results: Dict):
        """Merge timeline events"""
        if 'timeline_events' in phase_results:
            self.timeline_knowledge['events'].extend(phase_results['timeline_events'])
        
        if 'timeline' in phase_results:
            if 'events' in phase_results['timeline']:
                self.timeline_knowledge['events'].extend(phase_results['timeline']['events'])
            if 'gaps' in phase_results['timeline']:
                self.timeline_knowledge['gaps'].extend(phase_results['timeline']['gaps'])
            if 'impossibilities' in phase_results['timeline']:
                self.timeline_knowledge['impossibilities'].extend(phase_results['timeline']['impossibilities'])
    
    def merge_investigations(self, phase_results: Dict):
        """Merge investigation results"""
        if 'investigations' in phase_results:
            self.investigation_history.extend(phase_results['investigations'])
    
    def merge_strategic_insights(self, phase_results: Dict):
        """Merge strategic intelligence"""
        if 'strategic_insights' in phase_results:
            for key, values in phase_results['strategic_insights'].items():
                if key in self.strategic_insights:
                    if isinstance(values, list):
                        self.strategic_insights[key].extend(values)
                    else:
                        self.strategic_insights[key] = values
                else:
                    self.strategic_insights[key] = values
    
    # ==================== EXTRACTION METHODS ====================
    
    def count_insights(self, phase_results: Dict) -> int:
        """Count total insights in phase results"""
        count = 0
        count += len(phase_results.get('discoveries', []))
        count += len(phase_results.get('patterns', []))
        count += len(phase_results.get('contradictions', []))
        count += len(phase_results.get('entities', {}))
        return count
    
    def extract_discoveries(self, phase_results: Dict) -> List[Dict]:
        """Extract all discoveries"""
        return phase_results.get('discoveries', [])
    
    def extract_patterns(self, phase_results: Dict) -> List[Dict]:
        """Extract all patterns"""
        patterns = phase_results.get('patterns', [])
        patterns.extend(phase_results.get('strategic_patterns', []))
        return patterns
    
    def extract_contradictions(self, phase_results: Dict) -> List[Dict]:
        """Extract all contradictions"""
        return phase_results.get('contradictions', [])
    
    def extract_strategic_findings(self, phase_results: Dict) -> Dict:
        """Extract strategic findings"""
        return phase_results.get('strategic_insights', {})
    
    # ==================== SUMMARY METHODS ====================
    
    def get_nuclear_evidence_summary(self) -> str:
        """Get summary of most damaging evidence"""
        nuclear = []
        
        # Nuclear patterns
        nuclear.extend([p for p in self.pattern_library if p.get('severity') == 'nuclear'])
        
        # Nuclear contradictions (severity >= 9)
        nuclear.extend([c for c in self.contradiction_database if c.get('severity', 0) >= 9])
        
        # Nuclear evidence from strategic insights
        nuclear.extend(self.strategic_insights.get('nuclear_evidence', []))
        
        return json.dumps(nuclear, indent=2, ensure_ascii=False)[:8000]
    
    def count_evidence_by_severity(self, severity: str) -> int:
        """Count evidence items by severity"""
        count = 0
        
        # Count patterns
        for pattern in self.pattern_library:
            if pattern.get('severity') == severity:
                count += 1
        
        # Count contradictions
        for contradiction in self.contradiction_database:
            if severity == 'nuclear' and contradiction.get('severity', 0) >= 9:
                count += 1
            elif severity == 'critical' and 7 <= contradiction.get('severity', 0) < 9:
                count += 1
            elif severity == 'important' and 5 <= contradiction.get('severity', 0) < 7:
                count += 1
        
        # Count from strategic insights
        count += len(self.strategic_insights.get(f'{severity}_evidence', []))
        
        return count
    
    def generate_complete_intelligence_summary(self) -> str:
        """Generate complete summary of all intelligence"""
        summary = {
            'total_documents': len(self.document_intelligence),
            'total_entities': len(self.entity_intelligence),
            'total_patterns': len(self.pattern_library),
            'high_confidence_patterns': len([p for p in self.pattern_library if p.get('confidence', 0) > 0.8]),
            'total_contradictions': len(self.contradiction_database),
            'critical_contradictions': len([c for c in self.contradiction_database if c.get('severity', 0) > 7]),
            'timeline_events': len(self.timeline_knowledge.get('events', [])),
            'timeline_gaps': len(self.timeline_knowledge.get('gaps', [])),
            'timeline_impossibilities': len(self.timeline_knowledge.get('impossibilities', [])),
            'investigations_completed': len(self.investigation_history),
            'phases_completed': len(self.phase_memories),
            'expertise_level': self.expertise_level,
            'lismore_strengths': len(self.strategic_insights.get('lismore_strengths', [])),
            'process_weaknesses': len(self.strategic_insights.get('process_weaknesses', [])),
            'attack_vectors': len(self.strategic_insights.get('attack_vectors', []))
        }
        return json.dumps(summary, indent=2, ensure_ascii=False)
    
    def generate_complete_argument_list(self) -> str:
        """Generate list of all arguments ready for litigation"""
        arguments = {
            'primary_arguments': [],
            'supporting_arguments': [],
            'defensive_arguments': [],
            'procedural_arguments': [],
            'novel_theories': []
        }
        
        # Extract from strategic insights
        arguments['primary_arguments'] = self.strategic_insights.get('attack_vectors', [])
        arguments['defensive_arguments'] = self.strategic_insights.get('defensive_positions', [])
        
        # Extract from phase 5 (novel theories)
        if 'phase_5' in self.phase_memories:
            phase_5_results = self.phase_memories['phase_5'].get('complete_results', {})
            arguments['novel_theories'] = phase_5_results.get('novel_legal_theories', [])
        
        return json.dumps(arguments, indent=2, ensure_ascii=False)[:15000]
    
    # ==================== SAVE METHODS ====================
    
    def save_all_memory(self):
        """Save all memory components to disk"""
        
        try:
            # Save phase memories
            with open(self.memory_dir / "phase_memories.json", 'w', encoding='utf-8') as f:
                json.dump(self.phase_memories, f, indent=2, ensure_ascii=False)
            
            # Save complete case knowledge
            with open(self.memory_dir / "complete_case_knowledge.json", 'w', encoding='utf-8') as f:
                json.dump(self.complete_case_knowledge, f, indent=2, ensure_ascii=False)
            
            # Save document intelligence
            with open(self.memory_dir / "document_intelligence.json", 'w', encoding='utf-8') as f:
                json.dump(self.document_intelligence, f, indent=2, ensure_ascii=False)
            
            # Save entity intelligence
            with open(self.memory_dir / "entity_intelligence.json", 'w', encoding='utf-8') as f:
                json.dump(self.entity_intelligence, f, indent=2, ensure_ascii=False)
            
            # Save pattern library
            with open(self.memory_dir / "pattern_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.pattern_library, f, indent=2, ensure_ascii=False)
            
            # Save contradiction database
            with open(self.memory_dir / "contradiction_database.json", 'w', encoding='utf-8') as f:
                json.dump(self.contradiction_database, f, indent=2, ensure_ascii=False)
            
            # Save timeline knowledge
            with open(self.memory_dir / "timeline_knowledge.json", 'w', encoding='utf-8') as f:
                json.dump(self.timeline_knowledge, f, indent=2, ensure_ascii=False)
            
            # Save investigation history
            with open(self.memory_dir / "investigation_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.investigation_history, f, indent=2, ensure_ascii=False)
            
            # Save strategic insights
            with open(self.memory_dir / "strategic_insights.json", 'w', encoding='utf-8') as f:
                json.dump(self.strategic_insights, f, indent=2, ensure_ascii=False)
            
            self.logger.info("All memory components saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving memory: {e}")
            raise