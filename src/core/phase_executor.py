#!/usr/bin/env python3
"""
Phase Executor for Dynamic Phase Management
Handles individual phase execution with adaptive strategies
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
            '1': self._execute_discovery_phase,
            '2': self._execute_timeline_phase,
            '3': self._execute_contradiction_phase,
            '4': self._execute_pattern_phase,
            '5': self._execute_entity_phase,
            '6': self._execute_financial_phase,
            '7': self._execute_synthesis_phase
        }
        
    def execute(self, phase: str, context: Dict) -> Dict:
        """
        Execute phase with appropriate strategy
        """
        
        # Check if custom strategy exists
        if phase in self.phase_strategies:
            return self.phase_strategies[phase](context)
        
        # Default execution for unknown phases
        return self._execute_generic_phase(phase, context)
    
    def _execute_knowledge_phase(self, context: Dict) -> Dict:
        """
        Phase 0: Combined legal and case knowledge absorption
        """
        
        print("  Strategy: Unified knowledge synthesis")
        
        # Load documents
        legal_docs = self._load_phase_documents('legal_knowledge')
        case_docs = self._load_phase_documents('case_context')
        
        # Build knowledge synthesis prompt
        prompt = self.orchestrator.autonomous_prompts.knowledge_synthesis_prompt(
            legal_knowledge=legal_docs,
            case_context=case_docs,
            existing_knowledge=context
        )
        
        # Execute with Opus for maximum learning
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],  # Force Opus
            task_type='knowledge_synthesis',
            phase='0'
        )
        
        # Extract comprehensive knowledge
        self._process_knowledge_response(response, '0')
        
        return {
            'phase': '0',
            'strategy': 'unified_synthesis',
            'documents_processed': len(legal_docs) + len(case_docs),
            'synthesis': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_discovery_phase(self, context: Dict) -> Dict:
        """
        Phase 1: Initial discovery sweep
        """
        
        print("  Strategy: Broad discovery with pattern recognition")
        
        documents = self._load_phase_documents('disclosure')
        
        # Create semantic batches for better pattern recognition
        batches = self.orchestrator.batch_manager.create_semantic_batches(
            documents=documents,
            strategy='semantic_clustering'
        )
        
        results = {
            'phase': '1',
            'strategy': 'discovery_sweep',
            'batch_count': len(batches),
            'documents_processed': len(documents),
            'discoveries': []
        }
        
        # Process each batch with investigation focus
        for i, batch in enumerate(batches):
            print(f"    Processing batch {i+1}/{len(batches)}")
            
            # Build investigation prompt
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=batch,
                context=context,
                phase='1'
            )
            
            # Call Claude
            response, metadata = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                task_type='investigation',
                phase='1'
            )
            
            # Extract discoveries
            discoveries = self._extract_discoveries(response)
            results['discoveries'].extend(discoveries)
            
            # Update knowledge graph
            for discovery in discoveries:
                if discovery['type'] == 'CRITICAL':
                    self.orchestrator.spawn_investigation(
                        trigger_type='critical_discovery',
                        trigger_data=discovery,
                        priority=8.0
                    )
        
        results['synthesis'] = self._synthesise_discoveries(results['discoveries'])
        return results
    
    def _execute_timeline_phase(self, context: Dict) -> Dict:
        """
        Phase 2: Timeline reconstruction and impossibility detection
        """
        
        print("  Strategy: Temporal forensics")
        
        documents = self._load_phase_documents('disclosure')
        
        # Batch chronologically for timeline analysis
        batches = self.orchestrator.batch_manager.create_semantic_batches(
            documents=documents,
            strategy='chronological'
        )
        
        results = {
            'phase': '2',
            'strategy': 'timeline_reconstruction',
            'timeline_events': [],
            'impossibilities': []
        }
        
        for batch in batches:
            # Focus on temporal analysis
            prompt = self._build_timeline_prompt(batch, context)
            
            response, _ = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                task_type='timeline_analysis',
                phase='2'
            )
            
            # Extract timeline events
            events = self._extract_timeline_events(response)
            results['timeline_events'].extend(events)
            
            # Check for impossibilities
            for event in events:
                self.orchestrator.knowledge_graph.add_timeline_event(
                    date=event['date'],
                    description=event['description'],
                    entities=event.get('entities', []),
                    documents=event.get('documents', []),
                    is_critical=event.get('is_critical', False)
                )
        
        results['synthesis'] = self._synthesise_timeline(results['timeline_events'])
        return results
    
    def _execute_contradiction_phase(self, context: Dict) -> Dict:
        """
        Phase 3: Deep contradiction analysis
        """
        
        print("  Strategy: Contradiction hunting with severity scoring")
        
        documents = self._load_phase_documents('disclosure')
        
        # Use pattern detection prompt for contradictions
        prompt = self.orchestrator.autonomous_prompts.pattern_discovery_prompt(
            documents=documents[:100],  # Focus on key documents
            known_patterns=context.get('strong_patterns', {}),
            context=context
        )
        
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],  # Opus for logic
            task_type='contradiction_analysis',
            phase='3'
        )
        
        # Extract contradictions
        contradictions = self._extract_contradictions(response)
        
        results = {
            'phase': '3',
            'strategy': 'contradiction_analysis',
            'contradictions_found': len(contradictions),
            'critical_contradictions': [],
            'synthesis': response
        }
        
        # Add to knowledge graph and spawn investigations
        for contradiction in contradictions:
            self.orchestrator.knowledge_graph.add_contradiction(contradiction)
            
            if contradiction.severity >= 8:
                results['critical_contradictions'].append(contradiction)
                
                # Spawn deep investigation
                self.orchestrator.spawn_investigation(
                    trigger_type='critical_contradiction',
                    trigger_data={'contradiction': contradiction.__dict__},
                    priority=9.0
                )
        
        return results
    
    def _execute_pattern_phase(self, context: Dict) -> Dict:
        """
        Phase 4: Pattern recognition and validation
        """
        
        print("  Strategy: Cross-document pattern mining")
        
        documents = self._load_phase_documents('disclosure')
        
        # Build pattern discovery prompt
        prompt = self.orchestrator.autonomous_prompts.pattern_discovery_prompt(
            documents=documents[:150],
            known_patterns=self._get_known_patterns(),
            context=context
        )
        
        response, _ = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='pattern_recognition',
            phase='4'
        )
        
        # Extract and validate patterns
        patterns = self._extract_patterns(response)
        
        results = {
            'phase': '4',
            'strategy': 'pattern_mining',
            'patterns_discovered': len(patterns),
            'high_confidence_patterns': [],
            'synthesis': response
        }
        
        for pattern in patterns:
            self.orchestrator.knowledge_graph.add_pattern(pattern)
            
            if pattern.confidence > 0.8:
                results['high_confidence_patterns'].append(pattern)
        
        return results
    
    def _execute_entity_phase(self, context: Dict) -> Dict:
        """
        Phase 5: Entity relationship mapping
        """
        
        print("  Strategy: Entity extraction and relationship mapping")
        
        documents = self._load_phase_documents('disclosure')
        
        # Entity-focused batching
        batches = self.orchestrator.batch_manager.create_semantic_batches(
            documents=documents,
            strategy='entity_focused'
        )
        
        results = {
            'phase': '5',
            'strategy': 'entity_mapping',
            'entities_discovered': 0,
            'relationships_mapped': 0,
            'synthesis': ''
        }
        
        for batch in batches[:10]:  # Process key batches
            prompt = self.orchestrator.autonomous_prompts.entity_relationship_prompt(
                documents=batch,
                known_entities=self._get_known_entities(),
                context=context
            )
            
            response, _ = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                task_type='entity_mapping',
                phase='5'
            )
            
            # Extract entities and relationships
            entities, relationships = self._extract_entities_and_relationships(response)
            
            results['entities_discovered'] += len(entities)
            results['relationships_mapped'] += len(relationships)
            
            # Add to knowledge graph
            for entity in entities:
                self.orchestrator.knowledge_graph.add_entity(entity)
            
            for relationship in relationships:
                self.orchestrator.knowledge_graph.add_relationship(relationship)
        
        results['synthesis'] = f"Mapped {results['entities_discovered']} entities with {results['relationships_mapped']} relationships"
        return results
    
    def _execute_financial_phase(self, context: Dict) -> Dict:
        """
        Phase 6: Financial forensics
        """
        
        print("  Strategy: Financial pattern analysis and valuation scrutiny")
        
        documents = self._load_phase_documents('disclosure')
        
        # Filter for financial documents
        financial_docs = [
            doc for doc in documents 
            if any(term in doc['content'].lower() 
                  for term in ['payment', 'invoice', 'valuation', 'financial', '£', '$'])
        ]
        
        results = {
            'phase': '6',
            'strategy': 'financial_forensics',
            'documents_analysed': len(financial_docs),
            'anomalies': [],
            'synthesis': ''
        }
        
        if financial_docs:
            # Build financial analysis prompt
            prompt = self._build_financial_analysis_prompt(financial_docs[:50], context)
            
            response, _ = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                model=self.config.models['primary'],  # Opus for complex analysis
                task_type='financial_analysis',
                phase='6'
            )
            
            results['synthesis'] = response
            
            # Extract financial anomalies
            anomalies = self._extract_financial_anomalies(response)
            results['anomalies'] = anomalies
            
            # Spawn investigations for significant anomalies
            for anomaly in anomalies:
                if anomaly.get('severity', 0) > 7:
                    self.orchestrator.spawn_investigation(
                        trigger_type='financial_anomaly',
                        trigger_data=anomaly,
                        priority=8.0
                    )
        
        return results
    
    def _execute_synthesis_phase(self, context: Dict) -> Dict:
        """
        Phase 7: Strategic synthesis and narrative building
        """
        
        print("  Strategy: Narrative construction and strategic planning")
        
        # Get all discoveries from knowledge graph
        knowledge_export = self.orchestrator.knowledge_graph.export_for_report()
        
        # Build narrative construction prompt
        prompt = self.orchestrator.synthesis_prompts.narrative_construction_prompt(
            findings=knowledge_export.get('critical_findings', {}),
            contradictions=knowledge_export.get('key_contradictions', []),
            patterns=knowledge_export.get('strong_patterns', {}),
            timeline={},  # Would extract from knowledge graph
            entities={}   # Would extract from knowledge graph
        )
        
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            model=self.config.models['primary'],
            task_type='synthesis',
            phase='7'
        )
        
        results = {
            'phase': '7',
            'strategy': 'strategic_synthesis',
            'narrative': response,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save narrative
        self._save_narrative(response)
        
        return results
    
    def _execute_generic_phase(self, phase: str, context: Dict) -> Dict:
        """
        Generic phase execution for custom phases
        """
        
        print(f"  Strategy: Generic investigation for phase {phase}")
        
        documents = self._load_phase_documents('disclosure')
        
        # Use standard investigation approach
        batches = self.orchestrator.batch_manager.create_semantic_batches(
            documents=documents[:100],
            strategy='priority_weighted'
        )
        
        results = {
            'phase': phase,
            'strategy': 'generic',
            'batch_count': len(batches),
            'synthesis': ''
        }
        
        responses = []
        for batch in batches[:5]:  # Process top 5 batches
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=batch,
                context=context,
                phase=phase
            )
            
            response, _ = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                task_type='investigation',
                phase=phase
            )
            
            responses.append(response)
        
        # Combine responses
        results['synthesis'] = '\n\n'.join(responses)
        
        return results
    
    # Helper methods
    
    def _load_phase_documents(self, doc_type: str) -> List[Dict]:
        """Load documents for phase"""
        
        if doc_type == 'legal_knowledge':
            path = self.config.legal_knowledge_dir
        elif doc_type == 'case_context':
            path = self.config.case_context_dir
        elif doc_type == 'disclosure':
            path = self.config.disclosure_dir
        else:
            path = self.config.disclosure_dir
        
        return self.orchestrator._load_documents(path)
    
    def _process_knowledge_response(self, response: str, phase: str):
        """Process knowledge extraction from response"""
        
        # Extract various knowledge types
        # This would parse the response and update knowledge graph
        pass
    
    def _extract_discoveries(self, response: str) -> List[Dict]:
        """Extract discoveries from response"""
        
        discoveries = []
        
        # Parse response for discovery markers
        import re
        
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
    
    def _synthesise_discoveries(self, discoveries: List[Dict]) -> str:
        """Synthesise discoveries into summary"""
        
        if not discoveries:
            return "No significant discoveries in this phase"
        
        summary = f"Phase discovered {len(discoveries)} significant findings:\n\n"
        
        # Group by type
        by_type = {}
        for discovery in discoveries:
            disc_type = discovery['type']
            if disc_type not in by_type:
                by_type[disc_type] = []
            by_type[disc_type].append(discovery['content'][:200])
        
        for disc_type, contents in by_type.items():
            summary += f"{disc_type}: {len(contents)} findings\n"
            for content in contents[:3]:  # Top 3
                summary += f"  - {content}\n"
        
        return summary
    
    def _extract_timeline_events(self, response: str) -> List[Dict]:
        """Extract timeline events from response"""
        
        events = []
        
        # Simple extraction - would be more sophisticated
        import re
        date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})'
        dates = re.findall(date_pattern, response)
        
        for date in dates[:20]:  # Limit to 20 events
            events.append({
                'date': date,
                'description': f"Event on {date}",
                'entities': [],
                'documents': []
            })
        
        return events
    
    def _synthesise_timeline(self, events: List[Dict]) -> str:
        """Synthesise timeline into narrative"""
        
        if not events:
            return "No timeline events extracted"
        
        return f"Reconstructed timeline with {len(events)} events"
    
    def _build_timeline_prompt(self, documents: List[Dict], context: Dict) -> str:
        """Build timeline-focused prompt"""
        
        # This would build a specific prompt for timeline analysis
        return self.orchestrator.autonomous_prompts.investigation_prompt(
            documents=documents,
            context=context,
            phase='timeline'
        )
    
    def _build_financial_analysis_prompt(self, documents: List[Dict], context: Dict) -> str:
        """Build financial analysis prompt"""
        
        # This would build a specific prompt for financial analysis
        return self.orchestrator.autonomous_prompts.investigation_prompt(
            documents=documents,
            context=context,
            phase='financial'
        )
    
    def _extract_contradictions(self, response: str) -> List:
        """Extract contradictions from response"""
        
        # This would parse response for contradictions
        # Returns list of Contradiction objects
        return []
    
    def _extract_patterns(self, response: str) -> List:
        """Extract patterns from response"""
        
        # This would parse response for patterns
        # Returns list of Pattern objects
        return []
    
    def _extract_entities_and_relationships(self, response: str) -> tuple:
        """Extract entities and relationships from response"""
        
        # This would parse response for entities and relationships
        # Returns (entities_list, relationships_list)
        return [], []
    
    def _extract_financial_anomalies(self, response: str) -> List[Dict]:
        """Extract financial anomalies from response"""
        
        # This would parse response for financial anomalies
        return []
    
    def _get_known_patterns(self) -> Dict:
        """Get known patterns from knowledge graph"""
        
        # Query knowledge graph for existing patterns
        return {}
    
    def _get_known_entities(self) -> Dict:
        """Get known entities from knowledge graph"""
        
        # Query knowledge graph for existing entities
        return {}
    
    def _save_narrative(self, narrative: str):
        """Save narrative to file"""
        
        narrative_file = self.config.reports_dir / f"narrative_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(narrative_file, 'w', encoding='utf-8') as f:
            f.write("# Case Narrative - Lismore v Process Holdings\n\n")
            f.write(narrative)