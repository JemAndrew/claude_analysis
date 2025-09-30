#!/usr/bin/env python3
"""
Phase Executor for Dynamic Phase Management
Handles individual phase execution with adaptive strategies
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class PhaseExecutor:
    """Executes phases with dynamic adaptation based on findings"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        
        # Define phase strategies
        self.phase_strategies = {
            '0': self._execute_knowledge_phase,
            '1': self._execute_organisation_phase,
            '2': self._execute_foundation_phase,
            '3': self._execute_pattern_phase,
            '4': self._execute_adversarial_phase,
            '5': self._execute_creative_phase,
            '6': self._execute_synthesis_phase
        }
    
    def execute(self, phase: str, context: str) -> Dict:
        """
        Execute phase with appropriate strategy
        """
        
        # Check if custom strategy exists
        if phase in self.phase_strategies:
            return self.phase_strategies[phase](context)
        
        # Default execution for unknown phases
        return self._execute_generic_phase(phase, context)
    
    def _execute_knowledge_phase(self, context: str) -> Dict:
        """
        Phase 0: Combined legal and case knowledge absorption
        """
        
        print("  Strategy: Unified knowledge synthesis")
        
        # This is handled by orchestrator._execute_knowledge_phase()
        # Just return placeholder
        return {
            'phase': '0',
            'strategy': 'unified_synthesis',
            'note': 'Executed by orchestrator'
        }
    
    def _execute_organisation_phase(self, context: str) -> Dict:
        """
        Phase 1: Claude autonomously organises documents
        """
        
        print("  Strategy: Autonomous document organisation")
        
        # Load ALL case documents
        documents = self._load_phase_documents('case_documents')
        
        print(f"  • Total documents to organise: {len(documents)}")
        
        # Build organisation prompt with full context
        prompt = self._build_organisation_prompt(documents, context)
        
        # Call Claude to organise
        print("  • Claude organising documents autonomously...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='document_organisation',
            phase='1'
        )
        
        # Extract organisation structure from response
        organisation = self._extract_organisation_structure(response)
        
        # Save organised structure
        self._save_organisation_structure(organisation)
        
        # Perform initial document classification
        classifications = self._classify_documents(documents, response)
        
        results = {
            'phase': '1',
            'strategy': 'autonomous_organisation',
            'documents_processed': len(documents),
            'categories_created': len(organisation.get('categories', [])),
            'organisation_structure': organisation,
            'document_classifications': classifications,
            'synthesis': response[:3000],
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def _execute_foundation_phase(self, context: str) -> Dict:
        """
        Phase 2: Foundation intelligence - document analysis
        """
        
        print("  Strategy: Foundation intelligence extraction")
        
        # Load organised documents
        documents = self._load_phase_documents('case_documents')
        
        # Create semantic batches
        batches = self.orchestrator.batch_manager.create_semantic_batches(
            documents=documents,
            strategy='semantic_clustering'
        )
        
        print(f"  • Processing {len(documents)} documents in {len(batches)} batches")
        
        all_discoveries = []
        all_entities = {}
        all_timeline_events = []
        
        # Process each batch
        for i, batch in enumerate(batches):
            print(f"    • Batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            # Build investigation prompt with full context
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=batch,
                context={'phase_context': context},
                phase='2'
            )
            
            # Call Claude
            response, _ = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                task_type='initial_analysis',
                phase='2'
            )
            
            # Extract findings
            batch_discoveries = self._extract_discoveries(response)
            all_discoveries.extend(batch_discoveries)
            
            # Extract entities
            batch_entities = self._extract_entities(response)
            all_entities.update(batch_entities)
            
            # Extract timeline events
            batch_timeline = self._extract_timeline_events(response)
            all_timeline_events.extend(batch_timeline)
        
        # Build complete timeline
        complete_timeline = self._build_timeline(all_timeline_events)
        
        results = {
            'phase': '2',
            'strategy': 'foundation_intelligence',
            'documents_processed': len(documents),
            'batches_processed': len(batches),
            'discoveries': all_discoveries,
            'entities': all_entities,
            'timeline': complete_timeline,
            'document_analysis': self._analyse_documents(documents, all_discoveries),
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def _execute_pattern_phase(self, context: str) -> Dict:
        """
        Phase 3: Pattern recognition and deep analysis
        """
        
        print("  Strategy: Deep pattern recognition and contradiction mining")
        
        documents = self._load_phase_documents('case_documents')
        
        # Build pattern discovery prompt with full memory context
        prompt = self.orchestrator.autonomous_prompts.pattern_discovery_prompt(
            documents=documents[:100],  # Sample for pattern analysis
            known_patterns={},
            context={'phase_context': context}
        )
        
        # Call Claude with maximum creativity
        print("  • Discovering patterns with high creativity...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            temperature=0.9,  # High creativity
            task_type='pattern_recognition',
            phase='3'
        )
        
        # Extract patterns
        patterns = self._extract_patterns(response)
        
        # Mine contradictions
        print("  • Mining contradictions...")
        contradiction_prompt = self._build_contradiction_prompt(documents[:100], context)
        contradiction_response, _ = self.orchestrator.api_client.call_claude(
            prompt=contradiction_prompt,
            task_type='contradiction_analysis',
            phase='3'
        )
        
        contradictions = self._extract_contradictions(contradiction_response)
        
        # Detect gaps
        print("  • Detecting document gaps...")
        gap_detection_prompt = self._build_gap_detection_prompt(documents, context)
        gap_response, _ = self.orchestrator.api_client.call_claude(
            prompt=gap_detection_prompt,
            task_type='gap_detection',
            phase='3'
        )
        
        gaps = self._extract_gaps(gap_response)
        
        results = {
            'phase': '3',
            'strategy': 'pattern_recognition_deep_analysis',
            'patterns': patterns,
            'contradictions': contradictions,
            'gaps': gaps,
            'strategic_patterns': [p for p in patterns if p.get('strategic_value', 0) > 7],
            'synthesis': response[:3000],
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def _execute_adversarial_phase(self, context: str) -> Dict:
        """
        Phase 4: Adversarial intelligence - red team analysis
        """
        
        print("  Strategy: Adversarial red team analysis")
        
        # Build adversarial analysis prompt
        prompt = f"""{context}

<adversarial_analysis>
PHASE 4: ADVERSARIAL INTELLIGENCE

Your task is three-fold:

1. RED TEAM ANALYSIS - Process Holdings' Perspective
   - What are their BEST arguments?
   - What evidence do they have?
   - How will they attack our position?
   - What are their strategic options?
   
2. OFFENSIVE STRATEGY - Lismore's Attack
   - How do we destroy their arguments pre-emptively?
   - What's our strongest line of attack?
   - What evidence is devastating to them?
   - What's our nuclear option?
   
3. DEFENSIVE STRATEGY - Protecting Lismore
   - Where are we vulnerable?
   - How do we shore up weaknesses?
   - What counter-arguments do we prepare?
   - What's our fallback position?

Think like both sides. Then give Lismore the winning strategy.
</adversarial_analysis>"""
        
        # Call Claude for adversarial analysis
        print("  • Performing red team analysis...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            temperature=0.7,
            task_type='adversarial_analysis',
            phase='4'
        )
        
        # Extract adversarial intelligence
        adversarial_intel = self._extract_adversarial_intelligence(response)
        
        results = {
            'phase': '4',
            'strategy': 'adversarial_intelligence',
            'red_team_analysis': adversarial_intel.get('red_team', []),
            'offensive_strategy': adversarial_intel.get('offensive', []),
            'defensive_strategy': adversarial_intel.get('defensive', []),
            'strategic_insights': adversarial_intel.get('insights', {}),
            'synthesis': response[:3000],
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def _execute_creative_phase(self, context: str) -> Dict:
        """
        Phase 5: Novel theories and creative strategy
        """
        
        print("  Strategy: Creative legal theory development")
        
        # Build creative strategy prompt
        prompt = f"""{context}

<creative_strategy>
PHASE 5: NOVEL THEORIES & CREATIVE STRATEGY

You have MASTER-level knowledge of this case.

Your task: Generate unprecedented legal strategies.

1. NOVEL LEGAL THEORIES
   - What arguments have NEVER been made in this context?
   - What creative interpretations of law apply?
   - What precedents can we use innovatively?
   
2. PROCEDURAL INNOVATIONS
   - What procedural moves would surprise them?
   - What jurisdictional strategies apply?
   - What alternative dispute resolution leverage exists?
   
3. CREATIVE SETTLEMENT STRUCTURES
   - What settlement terms maximise our leverage?
   - What non-monetary remedies could we pursue?
   - What face-saving options exist for them?
   
4. THE UNTHINKABLE MOVE
   - What's the bold strategy that actually wins?
   - What would a legal genius do here?
   - What's the move they'll never see coming?

Think beyond convention. Find the winning innovation.
</creative_strategy>"""
        
        # Call Claude with maximum creativity
        print("  • Generating novel theories with maximum creativity...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            temperature=0.95,  # Maximum creativity
            task_type='hypothesis_generation',
            phase='5'
        )
        
        # Extract novel theories
        novel_theories = self._extract_novel_theories(response)
        
        results = {
            'phase': '5',
            'strategy': 'creative_innovation',
            'novel_legal_theories': novel_theories.get('legal_theories', []),
            'procedural_innovations': novel_theories.get('procedural', []),
            'creative_strategies': novel_theories.get('creative', []),
            'unthinkable_moves': novel_theories.get('unthinkable', []),
            'synthesis': response[:3000],
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def _execute_synthesis_phase(self, context: str) -> Dict:
        """
        Phase 6: Synthesis and weaponisation
        """
        
        print("  Strategy: Strategic synthesis and weaponisation")
        
        # Build synthesis prompt
        prompt = f"""{context}

<final_synthesis>
PHASE 6: SYNTHESIS & WEAPONISATION

You have COMPLETE MASTERY of this case.

Your final task: Package everything for victory.

DELIVERABLES:

1. PRIORITISED ARGUMENT HIERARCHY
   - What do we lead with?
   - What's our strongest evidence?
   - What's the knockout punch?
   
2. EVIDENCE PACKAGES
   - Organise evidence for tribunal presentation
   - Create exhibit bundles
   - Prepare witness examination guides
   
3. IMPLEMENTATION STRATEGY
   - Step-by-step litigation plan
   - Timeline for actions
   - Resource requirements
   
4. SETTLEMENT STRATEGY
   - Maximum pressure points
   - Optimal timing
   - Negotiation tactics
   
5. TRIAL STRATEGY (IF SETTLEMENT FAILS)
   - Opening statement outline
   - Evidence presentation order
   - Closing argument themes

6. WAR ROOM BRIEFING
   - Executive summary for barristers
   - Key facts at a glance
   - Strategic recommendations

Package everything. Make it tribunal-ready. This must win.
</final_synthesis>"""
        
        # Call Claude for final synthesis
        print("  • Generating final strategic synthesis...")
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            temperature=0.4,  # Precise synthesis
            task_type='synthesis',
            phase='6'
        )
        
        # Extract final deliverables
        final_deliverables = self._extract_final_deliverables(response)
        
        results = {
            'phase': '6',
            'strategy': 'synthesis_weaponisation',
            'argument_hierarchy': final_deliverables.get('arguments', []),
            'evidence_packages': final_deliverables.get('evidence', {}),
            'implementation_strategy': final_deliverables.get('implementation', {}),
            'settlement_strategy': final_deliverables.get('settlement', {}),
            'trial_strategy': final_deliverables.get('trial', {}),
            'war_room_briefing': final_deliverables.get('briefing', ''),
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save final synthesis as separate document
        self._save_final_synthesis(response)
        
        return results
    
    def _execute_generic_phase(self, phase: str, context: str) -> Dict:
        """
        Generic phase execution for custom phases
        """
        
        print(f"  Strategy: Generic investigation for phase {phase}")
        
        documents = self._load_phase_documents('case_documents')
        
        prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
            documents=documents[:50],
            context={'phase_context': context},
            phase=phase
        )
        
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            task_type='investigation',
            phase=phase
        )
        
        return {
            'phase': phase,
            'strategy': 'generic',
            'synthesis': response[:3000],
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
    
    # ==================== HELPER METHODS ====================
    
    def _load_phase_documents(self, doc_type: str) -> List[Dict]:
        """Load documents for phase"""
        
        if doc_type == 'legal_knowledge':
            path = self.config.legal_knowledge_dir
        elif doc_type == 'case_documents':
            path = self.config.case_documents_dir
        else:
            path = self.config.case_documents_dir
        
        return self.orchestrator._load_documents(path)
    
    def _build_organisation_prompt(self, documents: List[Dict], context: str) -> str:
        """Build prompt for document organisation"""
        
        # Format document list
        doc_list = []
        for i, doc in enumerate(documents[:200]):  # First 200 for overview
            doc_list.append(f"[DOC_{i:04d}] {doc.get('filename', 'Unknown')} - {len(doc.get('content', ''))} chars")
        
        prompt = f"""{context}

<document_organisation_task>
You have {len(documents)} case documents to organise.

DOCUMENTS TO ORGANISE:
{chr(10).join(doc_list[:100])}
... and {len(documents) - 100} more documents

YOUR TASK:
Organise these documents into strategic categories for deep analysis.

You have COMPLETE FREEDOM to create categories that make sense.

Consider organising by:
- Strategic importance (nuclear/critical/important/background)
- Document type (contracts/emails/financial/procedural)
- Time period (pre-arbitration/arbitration/post-award)
- Entity focus (by key players)
- Evidentiary value (smoking guns/supporting/neutral)
- Suspicious indicators (potential withholding/contradictions)

Create an organisation structure that would best reveal:
- Their deception
- Missing documents
- Contradictions
- Strategic weaknesses

Output your organisation structure as:
CATEGORY: [Name]
DESCRIPTION: [Why this category matters]
CRITERIA: [What belongs here]
PRIORITY: [1-10]
DOCUMENTS: [List document IDs]
</document_organisation_task>"""
        
        return prompt
    
    def _build_contradiction_prompt(self, documents: List[Dict], context: str) -> str:
        """Build prompt for contradiction mining"""
        
        prompt = f"""{context}

<contradiction_mining>
Hunt for contradictions ruthlessly.

Find where their statements conflict.
Find where documents contradict each other.
Find where actions contradict claims.

Rate each contradiction 1-10 for severity.
Severity 9-10 = Case-destroying contradictions
</contradiction_mining>

DOCUMENTS:
{self._format_documents_for_prompt(documents[:50])}

Find EVERY contradiction. Rate severity. Explain implications.
</contradiction_mining>"""
        
        return prompt
    
    def _build_gap_detection_prompt(self, documents: List[Dict], context: str) -> str:
        """Build prompt for gap detection"""
        
        prompt = f"""{context}

<gap_detection>
Find evidence of withheld documents.

Look for:
- "As discussed in previous email..." (where's that email?)
- "See attached..." (where's the attachment?)
- "Following up on..." (where's the original?)
- Email thread gaps (missing earlier messages)
- Meeting references without records
- Document version gaps (v2.1 and v2.3 exist, where's v2.2?)

For each gap, specify:
- What's missing
- How we know it existed
- Why it matters
- Who likely withheld it
</gap_detection>

DOCUMENTS:
{self._format_documents_for_prompt(documents[:100])}

Find EVERY missing document. Build the withholding case.
</gap_detection>"""
        
        return prompt
    
    def _format_documents_for_prompt(self, documents: List[Dict]) -> str:
        """Format documents for prompt"""
        formatted = []
        for i, doc in enumerate(documents):
            formatted.append(f"[DOC_{i:04d}] {doc.get('filename', 'Unknown')}\n{doc.get('content', '')[:500]}\n")
        return "\n".join(formatted)
    
    def _extract_organisation_structure(self, response: str) -> Dict:
        """Extract organisation structure from Claude's response"""
        # Parse organisation structure
        # This would parse Claude's structured output
        return {
            'categories': [],
            'document_mappings': {}
        }
    
    def _save_organisation_structure(self, organisation: Dict):
        """Save organisation structure to file"""
        output_file = self.config.organised_docs_dir / "organisation_structure.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(organisation, f, indent=2, ensure_ascii=False)
    
    def _classify_documents(self, documents: List[Dict], response: str) -> Dict:
        """Classify documents based on response"""
        classifications = {}
        for doc in documents:
            doc_id = doc.get('id', doc.get('filename'))
            classifications[doc_id] = {
                'category': 'uncategorised',
                'importance': 5,
                'strategic_value': 0
            }
        return classifications
    
    def _extract_discoveries(self, response: str) -> List[Dict]:
        """Extract discoveries from response"""
        import re
        discoveries = []
        
        markers = {
            'NUCLEAR': r'\[NUCLEAR\]\s*([^\n]+)',
            'CRITICAL': r'\[CRITICAL\]\s*([^\n]+)',
            'PATTERN': r'\[PATTERN\]\s*([^\n]+)',
            'SUSPICIOUS': r'\[SUSPICIOUS\]\s*([^\n]+)'
        }
        
        for discovery_type, pattern in markers.items():
            matches = re.findall(pattern, response)
            for match in matches:
                discoveries.append({
                    'type': discovery_type,
                    'content': match,
                    'timestamp': datetime.now().isoformat()
                })
        
        return discoveries
    
    def _extract_entities(self, response: str) -> Dict:
        """Extract entities from response"""
        # Simple entity extraction
        return {}
    
    def _extract_timeline_events(self, response: str) -> List[Dict]:
        """Extract timeline events from response"""
        return []
    
    def _build_timeline(self, events: List[Dict]) -> Dict:
        """Build complete timeline from events"""
        return {
            'events': events,
            'gaps': [],
            'impossibilities': []
        }
    
    def _analyse_documents(self, documents: List[Dict], discoveries: List[Dict]) -> Dict:
        """Analyse documents based on discoveries"""
        return {}
    
    def _extract_patterns(self, response: str) -> List[Dict]:
        """Extract patterns from response"""
        return []
    
    def _extract_contradictions(self, response: str) -> List[Dict]:
        """Extract contradictions from response"""
        return []
    
    def _extract_gaps(self, response: str) -> List[Dict]:
        """Extract document gaps from response"""
        return []
    
    def _extract_adversarial_intelligence(self, response: str) -> Dict:
        """Extract adversarial intelligence from response"""
        return {
            'red_team': [],
            'offensive': [],
            'defensive': [],
            'insights': {}
        }
    
    def _extract_novel_theories(self, response: str) -> Dict:
        """Extract novel theories from response"""
        return {
            'legal_theories': [],
            'procedural': [],
            'creative': [],
            'unthinkable': []
        }
    
    def _extract_final_deliverables(self, response: str) -> Dict:
        """Extract final deliverables from response"""
        return {
            'arguments': [],
            'evidence': {},
            'implementation': {},
            'settlement': {},
            'trial': {},
            'briefing': response[:2000]
        }
    
    def _save_final_synthesis(self, response: str):
        """Save final synthesis as separate document"""
        output_file = self.config.reports_dir / f"final_synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response)
        print(f"  • Final synthesis saved to: {output_file}")