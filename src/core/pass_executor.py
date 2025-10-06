#!/usr/bin/env python3
"""
Pass Executor for 4-Pass Litigation Analysis
Handles execution of all four passes with autonomous investigation
British English throughout - Lismore v Process Holdings
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import re

from core.investigation_queue import InvestigationQueue, Investigation


class PassExecutor:
    """Executes 4-pass litigation analysis system"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        self.investigation_queue = InvestigationQueue()
    
    # ========================================================================
    # PASS 1: TRIAGE & PRIORITISATION
    # ========================================================================
    
    def execute_pass_1_triage(self) -> Dict:
        """
        Pass 1: Quick triage of ALL documents
        Uses Haiku for fast, cheap classification
        Returns: Top 500 priority documents
        """
        
        print("="*70)
        print("PASS 1: TRIAGE & PRIORITISATION")
        print("="*70)
        
        # Load ALL disclosure documents
        all_documents = self._load_all_documents()
        
        print(f"  Total documents to triage: {len(all_documents)}")
        
        # Create batches for triage (100 docs per batch for Haiku)
        batches = self._create_batches(all_documents, batch_size=100)
        
        print(f"  Processing in {len(batches)} batches")
        
        priority_scores = []
        
        for i, batch in enumerate(batches):
            if i % 10 == 0:
                print(f"    Triage progress: {i}/{len(batches)} batches")
            
            # Use triage prompt from autonomous prompts
            prompt = self.orchestrator.autonomous_prompts.triage_prompt(
                documents=batch
            )
            
            try:
                # Use Haiku (fast and cheap)
                response, metadata = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['secondary'],  # Haiku
                    task_type='triage',
                    phase='pass_1',
                    use_extended_thinking=False
                )
                
                # Extract priority scores from response
                scores = self._parse_triage_response(response, batch)
                priority_scores.extend(scores)
                
            except Exception as e:
                print(f"      ⚠️  Error in triage batch {i+1}: {str(e)[:100]}")
                continue
        
        # Sort by priority score (descending) and select top 500
        priority_scores.sort(key=lambda x: x['score'], reverse=True)
        priority_documents = priority_scores[:500]
        
        results = {
            'pass': '1',
            'strategy': 'triage',
            'total_documents': len(all_documents),
            'priority_documents': priority_documents,
            'priority_count': len(priority_documents),
            'completed_at': datetime.now().isoformat()
        }
        
        # Save priority list
        self._save_pass_output('1', results)
        
        print(f"  ✅ Triage complete: {len(priority_documents)} priority documents identified")
        print(f"     Average priority score: {sum(d['score'] for d in priority_documents) / len(priority_documents):.1f}/10")
        
        return results
    
    # ========================================================================
    # PASS 2: DEEP ANALYSIS WITH CONFIDENCE TRACKING
    # ========================================================================
    
    def execute_pass_2_deep_analysis(self, priority_documents: List[Dict]) -> Dict:
        """
        Pass 2: Deep comprehensive analysis of priority documents
        Uses Sonnet 4.5 with extended thinking
        Iterative with confidence tracking - stops when Claude reaches 95% confidence
        """
        
        print("\n" + "="*70)
        print("PASS 2: DEEP ANALYSIS (WITH CONFIDENCE TRACKING)")
        print("="*70)
        
        print(f"  Analysing {len(priority_documents)} priority documents")
        
        # Create batches of priority documents
        batches = self._create_batches(priority_documents, batch_size=25)
        
        confidence = 0.0
        iteration = 0
        max_iterations = 20
        
        results = {
            'pass': '2',
            'strategy': 'deep_analysis',
            'iterations': [],
            'final_confidence': 0.0
        }
        
        while confidence < 0.95 and iteration < max_iterations:
            print(f"\n  Iteration {iteration+1} (current confidence: {confidence:.2%})")
            
            if iteration >= len(batches):
                print("    All document batches processed")
                break
            
            batch = batches[iteration]
            
            # Get accumulated knowledge for context
            context = self.orchestrator.knowledge_graph.get_context_for_analysis()
            
            # Deep analysis prompt with confidence tracking
            prompt = self.orchestrator.autonomous_prompts.deep_analysis_prompt(
                documents=batch,
                iteration=iteration,
                accumulated_knowledge=context,
                confidence=confidence
            )
            
            try:
                # Use Sonnet with extended thinking
                response, metadata = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['primary'],  # Sonnet 4.5
                    task_type='deep_analysis',
                    phase='pass_2',
                    use_extended_thinking=True
                )
                
                # Parse analysis response
                iteration_result = self._parse_deep_analysis_response(response)
                
                # Update knowledge graph with findings
                self.orchestrator.knowledge_graph.integrate_analysis(iteration_result)
                
                # Queue investigations for critical findings
                critical_findings = iteration_result.get('critical_findings', [])
                for finding in critical_findings:
                    if finding.get('needs_investigation', False):
                        investigation = Investigation(
                            topic=finding['topic'],
                            priority=finding.get('priority', 5),
                            trigger_data=finding
                        )
                        self.investigation_queue.add(investigation)
                
                # Update confidence from Claude's self-assessment
                new_confidence = iteration_result.get('confidence', confidence)
                confidence = max(confidence, new_confidence)  # Only increase
                
                results['iterations'].append({
                    'iteration': iteration + 1,
                    'documents_analysed': len(batch),
                    'confidence': confidence,
                    'findings_count': len(iteration_result.get('findings', [])),
                    'critical_findings': len(critical_findings),
                    'investigations_spawned': sum(1 for f in critical_findings if f.get('needs_investigation'))
                })
                
                print(f"    Confidence after iteration: {confidence:.2%}")
                print(f"    Findings: {len(iteration_result.get('findings', []))}")
                print(f"    Critical findings requiring investigation: {sum(1 for f in critical_findings if f.get('needs_investigation'))}")
                
                iteration += 1
                
            except Exception as e:
                print(f"      ⚠️  Error in iteration {iteration+1}: {str(e)[:100]}")
                iteration += 1
                continue
        
        results['final_confidence'] = confidence
        results['total_iterations'] = iteration
        results['reason_stopped'] = 'confidence_reached' if confidence >= 0.95 else 'max_iterations'
        
        # Save results
        self._save_pass_output('2', results)
        
        print(f"\n  ✅ Deep analysis complete after {iteration} iterations")
        print(f"     Final confidence: {confidence:.2%}")
        print(f"     Investigations queued: {self.investigation_queue.queue.qsize()}")
        print(f"     Stopped because: {results['reason_stopped']}")
        
        return results
    
    # ========================================================================
    # PASS 3: AUTONOMOUS RECURSIVE INVESTIGATION
    # ========================================================================
    
    def execute_pass_3_investigations(self) -> Dict:
        """
        Pass 3: Run autonomous investigations recursively
        Claude decides what to investigate and spawns child investigations
        """
        
        print("\n" + "="*70)
        print("PASS 3: AUTONOMOUS INVESTIGATIONS")
        print("="*70)
        
        queue_status = self.investigation_queue.get_status()
        print(f"  Initial investigation queue: {queue_status['queued']} investigations")
        
        results = {
            'pass': '3',
            'strategy': 'autonomous_investigation',
            'investigations_run': [],
            'total_investigations': 0
        }
        
        investigation_count = 0
        max_investigations = 50  # Safety limit
        
        while not self.investigation_queue.is_empty() and investigation_count < max_investigations:
            investigation = self.investigation_queue.pop()
            investigation_count += 1
            
            print(f"\n  Investigation {investigation_count}: {investigation.topic}")
            print(f"    Priority: {investigation.priority}/10")
            if investigation.parent_id:
                print(f"    Parent: {investigation.parent_id}")
            
            # Get relevant documents for this investigation
            relevant_docs = self.orchestrator.knowledge_graph.get_documents_for_investigation(
                investigation.topic
            )
            
            # Get complete intelligence context
            complete_context = self.orchestrator.knowledge_graph.export_complete()
            
            # Recursive investigation prompt
            prompt = self.orchestrator.autonomous_prompts.investigation_recursive_prompt(
                investigation=investigation,
                relevant_documents=relevant_docs,
                complete_intelligence=complete_context
            )
            
            try:
                # Use Sonnet with extended thinking
                response, metadata = self.orchestrator.api_client.call_claude(
                    prompt=prompt,
                    model=self.config.models['primary'],
                    task_type='investigation',
                    phase='pass_3',
                    use_extended_thinking=True
                )
                
                # Parse investigation result
                investigation_result = self._parse_investigation_response(response)
                
                # Store result in knowledge graph
                self.orchestrator.knowledge_graph.add_investigation_result(
                    investigation=investigation,
                    result=investigation_result
                )
                
                # Mark investigation as complete
                self.investigation_queue.mark_complete(investigation)
                
                # Spawn child investigations if Claude requests them
                child_count = 0
                if investigation_result.get('spawn_children', False):
                    for child_data in investigation_result.get('child_investigations', []):
                        child = Investigation(
                            topic=child_data['topic'],
                            priority=child_data.get('priority', 5),
                            trigger_data=child_data,
                            parent_id=investigation.get_id()
                        )
                        self.investigation_queue.add(child)
                        child_count += 1
                        print(f"      → Spawned child: {child.topic} (priority: {child.priority}/10)")
                
                results['investigations_run'].append({
                    'id': investigation.get_id(),
                    'topic': investigation.topic,
                    'priority': investigation.priority,
                    'parent_id': investigation.parent_id,
                    'children_spawned': child_count,
                    'confidence': investigation_result.get('confidence', 0.0),
                    'conclusion': investigation_result.get('conclusion', '')[:200]
                })
                
                print(f"    Confidence: {investigation_result.get('confidence', 0.0):.2%}")
                print(f"    Children spawned: {child_count}")
                
            except Exception as e:
                print(f"      ⚠️  Error in investigation: {str(e)[:100]}")
                self.investigation_queue.mark_complete(investigation)
                continue
        
        results['total_investigations'] = investigation_count
        final_status = self.investigation_queue.get_status()
        results['final_queue_status'] = final_status
        
        # Save results
        self._save_pass_output('3', results)
        
        print(f"\n  ✅ Investigations complete")
        print(f"     Total investigations run: {investigation_count}")
        print(f"     Final queue: {final_status['queued']} queued, {final_status['completed']} completed")
        
        return results
    
    # ========================================================================
    # PASS 4: SYNTHESIS & DELIVERABLES
    # ========================================================================
    
    def execute_pass_4_synthesis(self) -> Dict:
        """
        Pass 4: Strategic synthesis and tribunal deliverables generation
        """
        
        print("\n" + "="*70)
        print("PASS 4: SYNTHESIS & DELIVERABLES")
        print("="*70)
        
        # Export complete intelligence from knowledge graph
        complete_intelligence = self.orchestrator.knowledge_graph.export_complete()
        
        results = {
            'pass': '4',
            'strategy': 'synthesis',
            'deliverables': {},
            'completed_at': datetime.now().isoformat()
        }
        
        # Part 1: Claim Construction
        print("\n  Building claims element-by-element...")
        claims = self._build_claims(complete_intelligence)
        results['deliverables']['claims'] = claims
        print(f"    ✓ {len(claims)} claims constructed")
        
        # Part 2: Strategic Recommendations
        print("  Generating strategic recommendations...")
        strategy = self._generate_strategy(complete_intelligence, claims)
        results['deliverables']['strategy'] = strategy
        print(f"    ✓ Strategic recommendations complete")
        
        # Part 3: Tribunal Deliverables
        print("  Generating tribunal documents...")
        
        deliverables_prompt = self.orchestrator.deliverables_prompts.generate_all_deliverables(
            intelligence=complete_intelligence,
            claims=claims,
            strategy=strategy
        )
        
        try:
            response, metadata = self.orchestrator.api_client.call_claude(
                prompt=deliverables_prompt,
                model=self.config.models['primary'],
                task_type='deliverables',
                phase='pass_4',
                use_extended_thinking=False  # Template generation, not deep reasoning
            )
            
            tribunal_docs = self._parse_deliverables_response(response)
            results['deliverables']['tribunal_documents'] = tribunal_docs
            
            print(f"    ✓ Tribunal documents generated:")
            for doc_type in tribunal_docs.keys():
                print(f"      - {doc_type}")
            
        except Exception as e:
            print(f"    ⚠️  Error generating deliverables: {str(e)[:100]}")
            results['deliverables']['tribunal_documents'] = {'error': str(e)}
        
        # Save results
        self._save_pass_output('4', results)
        
        print("\n  ✅ Synthesis complete")
        print(f"     Claims constructed: {len(claims)}")
        print(f"     Tribunal documents: {len(results['deliverables'].get('tribunal_documents', {}))}")
        
        return results
    
    # ========================================================================
    # HELPER METHODS: DOCUMENT LOADING
    # ========================================================================
    
    def _load_all_documents(self) -> List[Dict]:
        """Load all disclosure documents"""
        disclosure_path = self.config.disclosure_dir
        
        documents = self.orchestrator.document_loader.load_directory(
            disclosure_path,
            doc_types=['.pdf', '.txt', '.docx', '.doc', '.xlsx']
        )
        
        return documents
    
    def _create_batches(self, documents: List[Dict], batch_size: int) -> List[List[Dict]]:
        """Create document batches"""
        batches = []
        for i in range(0, len(documents), batch_size):
            batches.append(documents[i:i+batch_size])
        return batches
    
    # ========================================================================
    # HELPER METHODS: RESPONSE PARSING
    # ========================================================================
    
    def _parse_triage_response(self, response: str, batch: List[Dict]) -> List[Dict]:
        """
        Parse triage response and extract priority scores
        Expected format from Claude:
        [DOC_X]
        Priority Score: 8
        Reason: Key contract document
        Category: contract
        """
        
        scores = []
        
        # Extract document scores using regex
        doc_pattern = r'\[DOC_(\d+)\]\s*Priority Score:\s*(\d+)\s*Reason:\s*(.+?)\s*Category:\s*(\w+)'
        matches = re.finditer(doc_pattern, response, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            doc_idx = int(match.group(1))
            score = int(match.group(2))
            reason = match.group(3).strip()
            category = match.group(4).strip()
            
            if doc_idx < len(batch):
                scores.append({
                    'document': batch[doc_idx],
                    'score': score,
                    'reason': reason,
                    'category': category,
                    'doc_id': batch[doc_idx].get('metadata', {}).get('filename', f'doc_{doc_idx}')
                })
        
        return scores
    
    def _parse_deep_analysis_response(self, response: str) -> Dict:
        """
        Parse deep analysis response
        Extracts: findings, confidence, critical findings, investigations needed
        """
        
        result = {
            'findings': [],
            'critical_findings': [],
            'confidence': 0.0,
            'raw_response': response
        }
        
        # Extract confidence score
        confidence_pattern = r'Confidence.*?:\s*(0?\.\d+|1\.0)'
        confidence_match = re.search(confidence_pattern, response, re.IGNORECASE)
        if confidence_match:
            result['confidence'] = float(confidence_match.group(1))
        
        # Extract critical findings marked with [CRITICAL] or [NUCLEAR]
        critical_pattern = r'\[(CRITICAL|NUCLEAR)\](.*?)(?=\[|$)'
        critical_matches = re.finditer(critical_pattern, response, re.DOTALL)
        
        for match in critical_matches:
            severity = match.group(1)
            content = match.group(2).strip()[:500]
            
            # Determine if investigation needed
            needs_investigation = 'investigate' in content.lower() or severity == 'NUCLEAR'
            
            result['critical_findings'].append({
                'severity': severity,
                'content': content,
                'needs_investigation': needs_investigation,
                'topic': content.split('\n')[0][:100],  # First line as topic
                'priority': 9 if severity == 'NUCLEAR' else 7
            })
        
        return result
    
    def _parse_investigation_response(self, response: str) -> Dict:
        """
        Parse investigation response
        Extracts: conclusion, confidence, child investigations to spawn
        """
        
        result = {
            'conclusion': '',
            'confidence': 0.0,
            'spawn_children': False,
            'child_investigations': [],
            'raw_response': response
        }
        
        # Extract conclusion
        conclusion_pattern = r'(?:CONCLUSION|FINAL CONCLUSION):\s*(.+?)(?=\n\n|\Z)'
        conclusion_match = re.search(conclusion_pattern, response, re.DOTALL | re.IGNORECASE)
        if conclusion_match:
            result['conclusion'] = conclusion_match.group(1).strip()
        
        # Extract confidence
        confidence_pattern = r'Confidence.*?:\s*(0?\.\d+|1\.0)'
        confidence_match = re.search(confidence_pattern, response, re.IGNORECASE)
        if confidence_match:
            result['confidence'] = float(confidence_match.group(1))
        
        # Check if Claude wants to spawn child investigations
        if 'YES' in response and 'continue investigating' in response.lower():
            result['spawn_children'] = True
            
            # Extract child investigation topics
            child_pattern = r'Topic:\s*(.+?)\s*Priority:\s*(\d+)\s*Reason:\s*(.+?)(?=Topic:|$)'
            child_matches = re.finditer(child_pattern, response, re.DOTALL)
            
            for match in child_matches:
                result['child_investigations'].append({
                    'topic': match.group(1).strip(),
                    'priority': int(match.group(2)),
                    'reason': match.group(3).strip()[:200]
                })
        
        return result
    
    def _build_claims(self, intelligence: Dict) -> Dict:
        """
        Build legal claims element-by-element
        Maps evidence to claim elements
        """
        
        print("    Building claims from intelligence...")
        
        # Extract breaches from intelligence
        breaches = intelligence.get('breaches', [])
        
        claims = {}
        claim_types = ['breach_of_contract', 'misrepresentation', 'negligence']
        
        for claim_type in claim_types:
            # Filter relevant breaches
            relevant_breaches = [b for b in breaches if claim_type in b.get('type', '').lower()]
            
            if relevant_breaches:
                claims[claim_type] = {
                    'elements': self._map_breaches_to_elements(relevant_breaches, claim_type),
                    'evidence': [b.get('evidence', []) for b in relevant_breaches],
                    'strength': self._calculate_claim_strength(relevant_breaches)
                }
        
        return claims
    
    def _map_breaches_to_elements(self, breaches: List[Dict], claim_type: str) -> Dict:
        """Map breaches to legal claim elements"""
        
        if claim_type == 'breach_of_contract':
            return {
                'contract_exists': len(breaches) > 0,
                'obligations_identified': [b.get('obligation', '') for b in breaches],
                'breaches_proven': [b.get('breach', '') for b in breaches],
                'causation': [b.get('causation', '') for b in breaches],
                'damages': [b.get('damages', '') for b in breaches]
            }
        
        # Add other claim types as needed
        return {}
    
    def _calculate_claim_strength(self, breaches: List[Dict]) -> float:
        """Calculate overall claim strength from breaches"""
        if not breaches:
            return 0.0
        
        strengths = [b.get('confidence', 0.5) for b in breaches]
        return sum(strengths) / len(strengths)
    
    def _generate_strategy(self, intelligence: Dict, claims: Dict) -> Dict:
        """Generate strategic recommendations"""
        
        print("    Generating strategic recommendations...")
        
        strategy = {
            'strongest_claims': [],
            'weakest_areas': [],
            'evidence_needed': [],
            'settlement_position': {},
            'trial_strategy': {}
        }
        
        # Identify strongest claims
        for claim_type, claim_data in claims.items():
            strength = claim_data.get('strength', 0.0)
            if strength > 0.7:
                strategy['strongest_claims'].append({
                    'type': claim_type,
                    'strength': strength
                })
        
        return strategy
    
    def _parse_deliverables_response(self, response: str) -> Dict:
        """Parse tribunal deliverables from response"""
        
        deliverables = {}
        
        # Extract different document types
        doc_types = [
            'scott_schedule',
            'witness_statements',
            'skeleton_argument',
            'disclosure_requests',
            'opening_submissions',
            'expert_instructions'
        ]
        
        for doc_type in doc_types:
            pattern = f'(?:{doc_type.upper()}|{doc_type.replace("_", " ").title()}):\s*(.+?)(?=(?:{"".join([t.upper() for t in doc_types])})|$)'
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            
            if match:
                deliverables[doc_type] = match.group(1).strip()
        
        return deliverables
    
    # ========================================================================
    # HELPER METHODS: OUTPUT SAVING
    # ========================================================================
    
    def _save_pass_output(self, pass_num: str, results: Dict):
        """Save pass results to disk"""
        
        output_dir = self.config.analysis_dir / f"pass_{pass_num}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"pass_{pass_num}_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"    💾 Saved: {output_file}")