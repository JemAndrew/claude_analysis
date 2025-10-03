#!/usr/bin/env python3
"""
Phase Executor for Dynamic Phase Management
Handles individual phase execution with adaptive strategies
British English throughout - Lismore-sided analysis
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
import re
import hashlib


class PhaseExecutor:
    """Executes phases with dynamic adaptation based on findings"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        
        # Define phase strategies
        self.phase_strategies = {
            '0': self.execute_phase_0,
            '1': self.execute_tiered_phase_1,
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
    
    # ========================================================================
    # PHASE 0: KNOWLEDGE FOUNDATION WITH SAFE BATCHING
    # ========================================================================
    
    def execute_phase_0(self, context: Dict) -> Dict:
        """
        Phase 0: Knowledge absorption with SAFE batching
        Prevents 413 errors with conservative document-count-based batches
        """
        
        print("  Strategy: Batched knowledge synthesis (Lismore-focused)")
        
        # Load documents
        legal_docs = self._load_phase_documents('legal_knowledge')
        case_docs = self._load_phase_documents('case_context')
        
        all_docs = legal_docs + case_docs
        print(f"    Total documents: {len(all_docs)}")
        print(f"      Legal knowledge: {len(legal_docs)} documents")
        print(f"      Case context: {len(case_docs)} documents")
        
        # Create SAFE batches using batch manager
        batches = self.orchestrator.batch_manager.create_safe_batches(
            documents=all_docs,
            batch_type='phase_0'
        )
        
        print(f"    Processing in {len(batches)} batches")
        
        results = {
            'phase': '0',
            'strategy': 'batched_synthesis',
            'documents_processed': len(all_docs),
            'batches': len(batches),
            'batch_results': []
        }
        
        # Process each batch
        for i, batch in enumerate(batches):
            print(f"    Batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            # Build knowledge synthesis prompt (uses existing autonomous.py prompts)
            prompt = self.orchestrator.autonomous_prompts.knowledge_synthesis_prompt(
                legal_knowledge=batch[:10],  # First 10 as legal
                case_context=batch[10:],     # Rest as case
                existing_knowledge=context
            )
            
            # Cacheable context for cost efficiency
            cacheable_context = f"""
{self.config.hallucination_prevention}

<knowledge_absorption_mission>
Building comprehensive Lismore v Process Holdings litigation intelligence.
Batch {i+1}/{len(batches)} of knowledge foundation.
</knowledge_absorption_mission>
"""
            
            try:
                # Call with caching
                response, metadata = self.orchestrator.api_client.call_claude_with_cache(
                    prompt=prompt,
                    cacheable_context=cacheable_context,
                    task_type='knowledge_synthesis',
                    phase='0'
                )
                
                # Extract knowledge from this batch
                self._process_knowledge_response(response, '0')
                
                results['batch_results'].append({
                    'batch': i + 1,
                    'documents': len(batch),
                    'tokens_in': metadata.get('input_tokens', 0),
                    'tokens_out': metadata.get('output_tokens', 0)
                })
                
                # Update context for next batch
                context = self.orchestrator.knowledge_graph.get_context_for_phase('0')
                
            except Exception as e:
                error_str = str(e)
                print(f"      ⚠️  Error in batch {i+1}: {error_str[:100]}")
                
                # Handle 413 errors by reducing batch size
                if '413' in error_str:
                    self.orchestrator.batch_manager.handle_413_error('phase_0')
                    print(f"      Batch size reduced. Recommend restarting Phase 0.")
                
                continue
        
        # Save output
        self._save_phase_output('0', results)
        
        print(f"    ✅ Phase 0 complete - {len(all_docs)} documents processed")
        return results
    
    def _process_knowledge_response(self, response: str, phase: str):
        """Extract and store knowledge from batch response"""
        
        # Extract contradictions
        contradictions = self.extract_contradictions(response)
        for c in contradictions:
            self.orchestrator.knowledge_graph.add_contradiction(c)
        
        # Extract patterns
        patterns = self.extract_patterns(response)
        for p in patterns:
            self.orchestrator.knowledge_graph.add_pattern(p)
        
        # Extract entities and relationships
        entities, relationships = self.extract_entities_and_relationships(response)
        for e in entities:
            self.orchestrator.knowledge_graph.add_entity(e)
        for r in relationships:
            self.orchestrator.knowledge_graph.add_relationship(r)
    
    # ========================================================================
    # PHASE 1: TIERED DISCLOSURE ANALYSIS
    # ========================================================================
    
    def execute_tiered_phase_1(self, context: Dict) -> Dict:
        """
        Phase 1: THREE-TIER DISCLOSURE ANALYSIS
        - Tier 1: Deep analysis of ~500 critical documents
        - Tier 2: Metadata scan of remaining documents
        - Tier 3: Targeted deep dive on flagged documents
        """
        
        print("  Strategy: Three-tier intelligent disclosure analysis")
        
        results = {
            'phase': '1',
            'strategy': 'tiered_analysis',
            'tiers': {}
        }
        
        # ===== TIER 1: DEEP ANALYSIS OF PRIORITY DOCUMENTS =====
        print("\n  🎯 TIER 1: Deep Analysis of Priority Documents")
        tier_1_results = self._execute_tier_1_deep_analysis(context)
        results['tiers']['tier_1'] = tier_1_results
        
        # ===== TIER 2: METADATA SCAN OF REMAINING DOCUMENTS =====
        print("\n  📊 TIER 2: Metadata Scan of Remaining Documents")
        tier_2_results = self._execute_tier_2_metadata_scan(context)
        results['tiers']['tier_2'] = tier_2_results
        
        # ===== TIER 3: TARGETED DEEP DIVE ON FLAGGED DOCUMENTS =====
        if tier_2_results.get('flagged_documents', []):
            print(f"\n  🔍 TIER 3: Deep Dive on {len(tier_2_results['flagged_documents'])} Flagged Documents")
            tier_3_results = self._execute_tier_3_targeted_analysis(
                tier_2_results['flagged_documents'],
                context
            )
            results['tiers']['tier_3'] = tier_3_results
        else:
            print("\n  ℹ️  TIER 3: No documents flagged - skipping")
        
        # Save comprehensive results
        self._save_phase_output('1', results)
        
        return results
    
    def _execute_tier_1_deep_analysis(self, context: Dict) -> Dict:
        """
        Tier 1: Deep forensic analysis of ~500 priority documents
        Uses full autonomous investigation prompts
        """
        
        # Load only priority folders
        priority_docs = self._load_priority_folders()
        
        print(f"    Priority documents loaded: {len(priority_docs)}")
        
        # Create safe batches
        batches = self.orchestrator.batch_manager.create_safe_batches(
            documents=priority_docs,
            batch_type='tier_1'
        )
        
        tier_1_results = {
            'documents_analysed': len(priority_docs),
            'batches_processed': 0,
            'critical_findings': [],
            'contradictions': [],
            'patterns': [],
            'investigations_spawned': 0
        }
        
        for i, batch in enumerate(batches):
            print(f"      Batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            # Use FULL investigation prompt (your senior litigator prompts)
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=batch,
                context=context,
                phase='1-tier1-deep'
            )
            
            try:
                response, metadata = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['primary'],  # Sonnet 4 for deep thinking
                    task_type='investigation',
                    phase='1_tier1'
                )
                
                # Extract all discoveries
                discoveries = self._extract_discoveries(response)
                tier_1_results['critical_findings'].extend(discoveries)
                
                # Extract contradictions
                contradictions = self.extract_contradictions(response)
                tier_1_results['contradictions'].extend(contradictions)
                for c in contradictions:
                    self.orchestrator.knowledge_graph.add_contradiction(c)
                
                # Extract patterns
                patterns = self.extract_patterns(response)
                tier_1_results['patterns'].extend(patterns)
                for p in patterns:
                    self.orchestrator.knowledge_graph.add_pattern(p)
                
                # Spawn investigations for critical findings
                for discovery in discoveries:
                    if discovery.get('type') in ['NUCLEAR', 'CRITICAL']:
                        self.orchestrator.spawn_investigation(
                            trigger_type='critical_discovery',
                            trigger_data=discovery,
                            priority=9.0
                        )
                        tier_1_results['investigations_spawned'] += 1
                
                tier_1_results['batches_processed'] += 1
                
            except Exception as e:
                error_str = str(e)
                print(f"        ⚠️  Error in batch {i+1}: {error_str[:100]}")
                
                if '413' in error_str:
                    self.orchestrator.batch_manager.handle_413_error('tier_1')
                
                continue
        
        print(f"    ✅ Tier 1 complete: {tier_1_results['documents_analysed']} documents analysed")
        print(f"       Critical findings: {len(tier_1_results['critical_findings'])}")
        print(f"       Contradictions: {len(tier_1_results['contradictions'])}")
        print(f"       Patterns: {len(tier_1_results['patterns'])}")
        print(f"       Investigations spawned: {tier_1_results['investigations_spawned']}")
        
        return tier_1_results
    
    def _execute_tier_2_metadata_scan(self, context: Dict) -> Dict:
        """
        Tier 2: Fast metadata extraction from remaining documents
        Lightweight processing to flag suspicious documents for Tier 3
        """
        
        # Load ALL disclosure documents
        all_docs = self._load_phase_documents('disclosure')
        
        # Remove documents already processed in Tier 1
        priority_doc_ids = set(self._get_priority_doc_ids())
        remaining_docs = [doc for doc in all_docs if doc.get('id') not in priority_doc_ids]
        
        print(f"    Remaining documents for metadata scan: {len(remaining_docs)}")
        
        # Larger batches for metadata (uses Haiku for speed)
        batches = self.orchestrator.batch_manager.create_safe_batches(
            documents=remaining_docs,
            batch_type='tier_2'
        )
        
        tier_2_results = {
            'documents_scanned': len(remaining_docs),
            'batches_processed': 0,
            'flagged_documents': [],
            'metadata_extracted': []
        }
        
        for i, batch in enumerate(batches):
            if i % 10 == 0:  # Progress every 10 batches
                print(f"      Metadata scan progress: {i}/{len(batches)} batches")
            
            # Use NEW metadata_scan_prompt from autonomous.py
            prompt = self.orchestrator.autonomous_prompts.metadata_scan_prompt(
                documents=batch,
                context=context
            )
            
            try:
                response, metadata = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['secondary'],  # Haiku for speed
                    task_type='metadata_extraction',
                    phase='1_tier2'
                )
                
                # Extract flagged documents
                flagged = self._extract_flagged_documents(response, batch)
                tier_2_results['flagged_documents'].extend(flagged)
                
                tier_2_results['batches_processed'] += 1
                
            except Exception as e:
                print(f"        ⚠️  Error in metadata batch {i+1}: {str(e)[:100]}")
                continue
        
        print(f"    ✅ Tier 2 complete: {tier_2_results['documents_scanned']} documents scanned")
        print(f"       Flagged for deep analysis: {len(tier_2_results['flagged_documents'])}")
        
        return tier_2_results
    
    def _execute_tier_3_targeted_analysis(self, flagged_docs: List[Dict], context: Dict) -> Dict:
        """
        Tier 3: Deep investigation of documents flagged in Tier 2
        Full forensic analysis like Tier 1
        """
        
        print(f"    Flagged documents for deep analysis: {len(flagged_docs)}")
        
        # Small batches for deep analysis
        batches = self.orchestrator.batch_manager.create_safe_batches(
            documents=flagged_docs,
            batch_type='tier_3'
        )
        
        tier_3_results = {
            'documents_analysed': len(flagged_docs),
            'batches_processed': 0,
            'critical_findings': [],
            'investigations_spawned': 0
        }
        
        for i, batch in enumerate(batches):
            print(f"      Targeted batch {i+1}/{len(batches)}: {len(batch)} documents")
            
            # Use focused investigation prompt
            prompt = self.orchestrator.recursive_prompts.focused_investigation_prompt(
                investigation_thread={
                    'type': 'flagged_document_analysis',
                    'priority': 8.0,
                    'data': {'flagged_from_tier_2': True}
                },
                context=context,
                depth=3
            )
            
            try:
                response, metadata = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['primary'],
                    task_type='investigation',
                    phase='1_tier3'
                )
                
                # Extract discoveries
                discoveries = self._extract_discoveries(response)
                tier_3_results['critical_findings'].extend(discoveries)
                
                # Spawn investigations
                for discovery in discoveries:
                    if discovery.get('type') in ['NUCLEAR', 'CRITICAL']:
                        self.orchestrator.spawn_investigation(
                            trigger_type='tier3_discovery',
                            trigger_data=discovery,
                            priority=9.0
                        )
                        tier_3_results['investigations_spawned'] += 1
                
                tier_3_results['batches_processed'] += 1
                
            except Exception as e:
                print(f"        ⚠️  Error in targeted batch {i+1}: {str(e)[:100]}")
                continue
        
        print(f"    ✅ Tier 3 complete: {tier_3_results['documents_analysed']} documents analysed")
        print(f"       Critical findings: {len(tier_3_results['critical_findings'])}")
        print(f"       Investigations spawned: {tier_3_results['investigations_spawned']}")
        
        return tier_3_results
    
    # ========================================================================
    # HELPER METHODS FOR TIERED ANALYSIS
    # ========================================================================
    
    def _load_priority_folders(self) -> List[Dict]:
        """Load documents from priority folders only (Tier 1)"""
        
        priority_docs = []
        
        for folder_name in self.config.tier_1_priority_folders:
            folder_path = self.config.disclosure_dir / folder_name
            
            if folder_path.exists():
                docs = self._load_documents(folder_path)
                print(f"      Loaded {len(docs)} from '{folder_name}'")
                priority_docs.extend(docs)
            else:
                print(f"      ⚠️  Priority folder not found: '{folder_name}'")
        
        return priority_docs
    
    def _get_priority_doc_ids(self) -> List[str]:
        """Get document IDs from priority folders (to exclude from Tier 2)"""
        
        priority_docs = self._load_priority_folders()
        return [doc.get('id') for doc in priority_docs]
    
    def _extract_flagged_documents(self, response: str, batch_docs: List[Dict]) -> List[Dict]:
        """Extract flagged documents from Tier 2 metadata scan response"""
        
        flagged = []
        
        # Pattern: [FLAG_DOC_X]
        flag_pattern = r'\[FLAG_DOC_(\d+)\](.*?)(?=\[FLAG_DOC_|\Z)'
        matches = re.findall(flag_pattern, response, re.DOTALL)
        
        for doc_index_str, flag_details in matches:
            doc_index = int(doc_index_str)
            
            # Get the actual document
            if doc_index < len(batch_docs):
                flagged_doc = batch_docs[doc_index].copy()
                
                # Extract reason
                reason_match = re.search(r'Reason:\s*(.+?)(?=\n|$)', flag_details, re.IGNORECASE)
                reason = reason_match.group(1).strip() if reason_match else "Flagged for review"
                
                # Extract suspicion level
                suspicion_match = re.search(r'Suspicion Level:\s*(\d+)', flag_details, re.IGNORECASE)
                suspicion = int(suspicion_match.group(1)) if suspicion_match else 5
                
                # Extract priority
                priority_match = re.search(r'Priority:\s*(HIGH|MEDIUM|LOW)', flag_details, re.IGNORECASE)
                priority = priority_match.group(1).upper() if priority_match else 'MEDIUM'
                
                # Add flagging metadata
                flagged_doc['flag_metadata'] = {
                    'reason': reason,
                    'suspicion_level': suspicion,
                    'priority': priority,
                    'flagged_from': 'tier_2_metadata_scan',
                    'original_index': doc_index
                }
                
                flagged.append(flagged_doc)
        
        return flagged
    
    # ========================================================================
    # PHASE 2: TIMELINE RECONSTRUCTION
    # ========================================================================
    
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
        
        for i, batch in enumerate(batches[:20]):  # Process first 20 batches
            print(f"    Processing timeline batch {i+1}/{min(20, len(batches))}")
            
            # Use investigation prompt with timeline focus
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=batch,
                context=context,
                phase='2-timeline'
            )
            
            try:
                response, _ = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    task_type='timeline_analysis',
                    phase='2'
                )
                
                # Extract timeline events
                events = self._extract_timeline_events(response)
                results['timeline_events'].extend(events)
                
                # Add events to knowledge graph
                for event in events:
                    self.orchestrator.knowledge_graph.add_timeline_event(
                        date=event['date'],
                        description=event['description'],
                        entities=event.get('entities', []),
                        documents=event.get('documents', []),
                        is_critical=event.get('is_critical', False)
                    )
                
            except Exception as e:
                print(f"      ⚠️  Error in timeline batch {i+1}: {str(e)[:100]}")
                continue
        
        results['synthesis'] = self._synthesise_timeline(results['timeline_events'])
        self._save_phase_output('2', results)
        
        return results
    
    # ========================================================================
    # PHASE 3: CONTRADICTION MINING
    # ========================================================================
    
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
        
        try:
            response, metadata = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                model=self.config.models['primary'],
                task_type='contradiction_analysis',
                phase='3'
            )
            
            # Extract contradictions
            contradictions = self.extract_contradictions(response)
            
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
            
            self._save_phase_output('3', results)
            
        except Exception as e:
            print(f"    ⚠️  Error in contradiction phase: {str(e)[:100]}")
            results = {'phase': '3', 'error': str(e)}
        
        return results
    
    # ========================================================================
    # PHASE 4: PATTERN RECOGNITION
    # ========================================================================
    
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
        
        try:
            response, _ = self.orchestrator.api_client.call_claude(
                prompt=prompt,
                model=self.config.models['primary'],
                task_type='pattern_recognition',
                phase='4'
            )
            
            # Extract and validate patterns
            patterns = self.extract_patterns(response)
            
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
            
            self._save_phase_output('4', results)
            
        except Exception as e:
            print(f"    ⚠️  Error in pattern phase: {str(e)[:100]}")
            results = {'phase': '4', 'error': str(e)}
        
        return results
    
    # ========================================================================
    # PHASE 5: ENTITY RELATIONSHIP MAPPING
    # ========================================================================
    
    def _execute_entity_phase(self, context: Dict) -> Dict:
        """
        Phase 5: Entity extraction and relationship mapping
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
        
        for i, batch in enumerate(batches[:10]):  # Process key batches
            print(f"    Processing entity batch {i+1}/{min(10, len(batches))}")
            
            try:
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
                entities, relationships = self.extract_entities_and_relationships(response)
                
                results['entities_discovered'] += len(entities)
                results['relationships_mapped'] += len(relationships)
                
                # Add to knowledge graph
                for entity in entities:
                    self.orchestrator.knowledge_graph.add_entity(entity)
                
                for relationship in relationships:
                    self.orchestrator.knowledge_graph.add_relationship(relationship)
                
            except Exception as e:
                print(f"      ⚠️  Error in entity batch {i+1}: {str(e)[:100]}")
                continue
        
        results['synthesis'] = f"Mapped {results['entities_discovered']} entities with {results['relationships_mapped']} relationships"
        self._save_phase_output('5', results)
        
        return results
    
    # ========================================================================
    # PHASE 6: FINANCIAL FORENSICS
    # ========================================================================
    
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
            try:
                # Use investigation prompt with financial focus
                prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                    documents=financial_docs[:50],
                    context=context,
                    phase='6-financial'
                )
                
                response, _ = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['primary'],
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
                
            except Exception as e:
                print(f"    ⚠️  Error in financial phase: {str(e)[:100]}")
                results['error'] = str(e)
        
        self._save_phase_output('6', results)
        
        return results
    
    # ========================================================================
    # PHASE 7: STRATEGIC SYNTHESIS
    # ========================================================================
    
    def _execute_synthesis_phase(self, context: Dict) -> Dict:
        """
        Phase 7: Strategic synthesis and narrative building
        """
        
        print("  Strategy: Narrative construction and strategic planning")
        
        # Get all discoveries from knowledge graph
        knowledge_export = self.orchestrator.knowledge_graph.export_for_report()
        
        # Build narrative construction prompt (from synthesis.py)
        prompt = self.orchestrator.synthesis_prompts.narrative_construction_prompt(
            findings=knowledge_export.get('critical_findings', {}),
            contradictions=knowledge_export.get('key_contradictions', []),
            patterns=knowledge_export.get('strong_patterns', {}),
            timeline={},
            entities={}
        )
        
        try:
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
            self._save_phase_output('7', results)
            
        except Exception as e:
            print(f"    ⚠️  Error in synthesis phase: {str(e)[:100]}")
            results = {'phase': '7', 'error': str(e)}
        
        return results
    
    # ========================================================================
    # GENERIC PHASE EXECUTION
    # ========================================================================
    
    def _execute_generic_phase(self, phase: str, context: Dict) -> Dict:
        """
        Generic phase execution for custom phases
        """
        
        print(f"  Strategy: Generic investigation for phase {phase}")
        
        documents = self._load_phase_documents('disclosure')
        
        # Use standard investigation approach
        batches = self.orchestrator.batch_manager.create_safe_batches(
            documents=documents[:100],
            batch_type='tier_1'
        )
        
        results = {
            'phase': phase,
            'strategy': 'generic',
            'batch_count': len(batches),
            'synthesis': ''
        }
        
        responses = []
        for i, batch in enumerate(batches[:5]):
            print(f"    Processing batch {i+1}/5")
            
            prompt = self.orchestrator.autonomous_prompts.investigation_prompt(
                documents=batch,
                context=context,
                phase=phase
            )
            
            try:
                response, _ = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    task_type='investigation',
                    phase=phase
                )
                
                responses.append(response)
                
            except Exception as e:
                print(f"      ⚠️  Error: {str(e)[:100]}")
                continue
        
        results['synthesis'] = '\n\n'.join(responses)
        self._save_phase_output(phase, results)
        
        return results
    
    # ========================================================================
    # HELPER METHODS - DOCUMENT LOADING
    # ========================================================================
    
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
        
        return self._load_documents(path)
    
    def _load_documents(self, directory: Path) -> List[Dict]:
        """Load all documents from directory"""
        
        from utils.document_loader import DocumentLoader
        
        loader = DocumentLoader(self.config)
        documents = loader.load_directory(
            directory=directory,
            doc_types=['.pdf', '.txt', '.docx', '.doc', '.json', '.html', '.md']
        )
        
        return documents
    
    # ========================================================================
    # HELPER METHODS - EXTRACTION
    # ========================================================================
    
    def _extract_discoveries(self, response: str) -> List[Dict]:
        """Extract discoveries from response"""
        
        discoveries = []
        
        markers = {
            'NUCLEAR': r'\[NUCLEAR\]\s*([^\[]+)',
            'CRITICAL': r'\[CRITICAL\]\s*([^\[]+)',
            'PATTERN': r'\[PATTERN\]\s*([^\[]+)',
            'SUSPICIOUS': r'\[SUSPICIOUS\]\s*([^\[]+)',
            'MISSING': r'\[MISSING\]\s*([^\[]+)',
            'TIMELINE': r'\[TIMELINE\]\s*([^\[]+)',
            'FINANCIAL': r'\[FINANCIAL\]\s*([^\[]+)'
        }
        
        for discovery_type, pattern in markers.items():
            matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                discoveries.append({
                    'type': discovery_type,
                    'content': match.strip()[:500],
                    'timestamp': datetime.now().isoformat()
                })
        
        return discoveries
    
    def extract_contradictions(self, response: str) -> List:
        """Extract contradictions from response"""
        from intelligence.knowledge_graph import Contradiction
        
        contradictions = []
        
        patterns = [
            r'\[CONTRADICTION\](.*?)(?=\[|$)',
            r'contradicts?:?\s*(.*?)(?=\n|\[|$)',
            r'inconsistent:?\s*(.*?)(?=\n|\[|$)'
        ]
        
        for marker in patterns:
            matches = re.findall(marker, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                contradiction = Contradiction(
                    statement_a="Extracted from analysis",
                    statement_b=match[:500],
                    severity=7,
                    evidence=[],
                    context={}
                )
                contradictions.append(contradiction)
        
        return contradictions
    
    def extract_patterns(self, response: str) -> List:
        """Extract patterns from response"""
        from intelligence.knowledge_graph import Pattern
        
        patterns = []
        
        pattern_markers = [
            r'\[PATTERN-TEMPORAL\](.*?)(?=\[|$)',
            r'\[PATTERN-FINANCIAL\](.*?)(?=\[|$)',
            r'\[PATTERN-BEHAVIOURAL\](.*?)(?=\[|$)',
            r'\[PATTERN\](.*?)(?=\[|$)'
        ]
        
        for marker in pattern_markers:
            matches = re.findall(marker, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                pattern = Pattern(
                    description=match[:500],
                    confidence=0.7,
                    evidence=[],
                    pattern_type='discovered'
                )
                patterns.append(pattern)
        
        return patterns
    
    def extract_entities_and_relationships(self, response: str) -> tuple:
        """Extract entities and relationships from response"""
        
        entities = []
        relationships = []
        
        # Extract entities marked with [ENTITY-NEW]
        entity_pattern = r'\[ENTITY-NEW\](.*?)(?=\[|$)'
        entity_matches = re.findall(entity_pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in entity_matches:
            entities.append({
                'name': match[:100],
                'type': 'discovered',
                'suspicion': 0.5
            })
        
        # Extract relationships marked with [RELATIONSHIP-HIDDEN]
        rel_pattern = r'\[RELATIONSHIP-HIDDEN\](.*?)(?=\[|$)'
        rel_matches = re.findall(rel_pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in rel_matches:
            relationships.append({
                'description': match[:200],
                'type': 'hidden',
                'strength': 0.7
            })
        
        return entities, relationships
    
    def _extract_timeline_events(self, response: str) -> List[Dict]:
        """Extract timeline events from response"""
        
        events = []
        
        date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})'
        dates = re.findall(date_pattern, response)
        
        for date in dates[:20]:
            events.append({
                'date': date,
                'description': f"Event on {date}",
                'entities': [],
                'documents': [],
                'is_critical': False
            })
        
        return events
    
    def _extract_financial_anomalies(self, response: str) -> List[Dict]:
        """Extract financial anomalies from response"""
        
        anomalies = []
        
        markers = [
            r'\[FINANCIAL\](.*?)(?=\[|$)',
            r'anomaly:?\s*(.*?)(?=\n|\[|$)',
            r'suspicious.*?payment.*?:(.*?)(?=\n|\[|$)'
        ]
        
        for marker in markers:
            matches = re.findall(marker, response, re.IGNORECASE | re.DOTALL)
            for match in matches:
                anomaly = {
                    'type': 'financial_anomaly',
                    'description': match[:500],
                    'severity': 7,
                    'timestamp': datetime.now().isoformat()
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    # ========================================================================
    # HELPER METHODS - KNOWLEDGE GRAPH QUERIES
    # ========================================================================
    
    def _get_known_patterns(self) -> Dict:
        """Get known patterns from knowledge graph"""
        import sqlite3
        
        conn = sqlite3.connect(self.orchestrator.knowledge_graph.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, description, confidence 
            FROM patterns 
            WHERE confidence > 0.5
            LIMIT 20
        """)
        
        patterns = {}
        for row in cursor.fetchall():
            patterns[row[0]] = {
                'description': row[1],
                'confidence': row[2]
            }
        
        conn.close()
        return patterns
    
    def _get_known_entities(self) -> Dict:
        """Get known entities from knowledge graph"""
        import sqlite3
        
        conn = sqlite3.connect(self.orchestrator.knowledge_graph.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT entity_type, name 
            FROM entities 
            LIMIT 50
        """)
        
        entities = {}
        for row in cursor.fetchall():
            entity_type = row[0]
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append(row[1])
        
        conn.close()
        return entities
    
    # ========================================================================
    # HELPER METHODS - SYNTHESIS
    # ========================================================================
    
    def _synthesise_timeline(self, events: List[Dict]) -> str:
        """Synthesise timeline into narrative"""
        
        if not events:
            return "No timeline events extracted"
        
        return f"Reconstructed timeline with {len(events)} events spanning documented period"
    
    # ========================================================================
    # HELPER METHODS - SAVING
    # ========================================================================
    
    def _save_phase_output(self, phase: str, results: Dict):
        """Save phase output to file"""
        
        phase_dir = self.config.analysis_dir / f"phase_{phase}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Save synthesis
        if 'synthesis' in results:
            synthesis_file = phase_dir / "synthesis.md"
            with open(synthesis_file, 'w', encoding='utf-8') as f:
                f.write(f"# Phase {phase} Analysis\n\n")
                f.write(f"*Strategy: {results.get('strategy', 'unknown')}*\n\n")
                f.write(f"*Documents Processed: {results.get('documents_processed', 0)}*\n\n")
                f.write("---\n\n")
                f.write(results['synthesis'])
        
        # Save metadata
        metadata_file = phase_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            # Remove synthesis from metadata (too large)
            metadata_results = {k: v for k, v in results.items() if k != 'synthesis'}
            json.dump(metadata_results, f, indent=2)
        
        print(f"    📁 Saved to {phase_dir}")
    
    def _save_narrative(self, narrative: str):
        """Save narrative to file"""
        
        narrative_file = self.config.reports_dir / f"narrative_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(narrative_file, 'w', encoding='utf-8') as f:
            f.write("# Case Narrative - Lismore v Process Holdings\n\n")
            f.write(narrative)
        
        print(f"    📁 Narrative saved to {narrative_file}")