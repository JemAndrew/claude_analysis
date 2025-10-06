#!/usr/bin/env python3
"""
Pass Executor for 4-Pass Litigation Analysis
Handles execution of all four passes with autonomous investigation
British English throughout - Lismore v Process Holdings
PRODUCTION READY - Option 1 Structured Extraction
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
        
        if not all_documents:
            raise Exception("No documents found in disclosure directory. Check config.disclosure_dir path.")
        
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
        avg_score = sum(d['score'] for d in priority_documents) / len(priority_documents) if priority_documents else 0
        print(f"     Average priority score: {avg_score:.1f}/10")
        
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
                critical_findings = iteration_result.get('investigations_needed', [])
                for finding in critical_findings:
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
                    'breaches_found': len(iteration_result.get('breaches', [])),
                    'contradictions_found': len(iteration_result.get('contradictions', [])),
                    'timeline_events': len(iteration_result.get('timeline_events', [])),
                    'investigations_spawned': len(critical_findings)
                })
                
                print(f"    Confidence after iteration: {confidence:.2%}")
                print(f"    Breaches found: {len(iteration_result.get('breaches', []))}")
                print(f"    Contradictions: {len(iteration_result.get('contradictions', []))}")
                print(f"    Timeline events: {len(iteration_result.get('timeline_events', []))}")
                print(f"    Investigations spawned: {len(critical_findings)}")
                
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
        max_depth = 5  # Prevent infinite recursion
        
        while not self.investigation_queue.is_empty() and investigation_count < max_investigations:
            investigation = self.investigation_queue.pop()
            
            # Check depth to prevent infinite recursion
            depth = self._get_investigation_depth(investigation)
            if depth >= max_depth:
                print(f"    ⚠️ Max depth {max_depth} reached, skipping: {investigation.topic}")
                self.investigation_queue.mark_complete(investigation)
                continue
            
            investigation_count += 1
            
            print(f"\n  Investigation {investigation_count}: {investigation.topic}")
            print(f"    Priority: {investigation.priority}/10")
            print(f"    Depth: {depth}/{max_depth}")
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
                    'depth': depth,
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
    
    def _get_investigation_depth(self, investigation: Investigation) -> int:
        """Calculate depth of investigation in the tree (prevent infinite recursion)"""
        depth = 0
        current = investigation
        visited = set()  # Prevent circular references
        
        while current.parent_id and current.parent_id not in visited:
            depth += 1
            visited.add(current.parent_id)
            
            # Use dictionary lookup (O(1)) instead of list scan (O(n))
            current = self.investigation_queue.completed_by_id.get(current.parent_id)
            
            if not current or depth > 10:  # Safety limit
                break
        
        return depth
    
    # ========================================================================
    # HELPER METHODS: RESPONSE PARSING (OPTION 1 - STRUCTURED EXTRACTION)
    # ========================================================================
    
    def _parse_triage_response(self, response: str, batch: List[Dict]) -> List[Dict]:
        """
        Parse triage response and extract priority scores
        Expected format:
        [DOC_X]
        Priority Score: 8
        Reason: Key contract document
        Category: contract
        """
        
        VALID_CATEGORIES = {'contract', 'financial', 'correspondence', 'witness', 'expert', 'other'}
        scores = []
        
        # Extract document scores using regex
        doc_pattern = r'\[DOC_(\d+)\]\s*Priority Score:\s*(\d+)\s*Reason:\s*(.+?)\s*Category:\s*(\w+)'
        matches = re.finditer(doc_pattern, response, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            try:
                doc_idx = int(match.group(1))
                score = int(match.group(2))
                reason = match.group(3).strip()[:200]  # Limit reason length
                category = match.group(4).strip().lower()
                
                # Validate category
                if category not in VALID_CATEGORIES:
                    category = 'other'
                
                if doc_idx < len(batch):
                    scores.append({
                        'document': batch[doc_idx],
                        'score': min(10, max(1, score)),  # Clamp to 1-10
                        'reason': reason,
                        'category': category,
                        'doc_id': batch[doc_idx].get('metadata', {}).get('filename', f'doc_{doc_idx}')
                    })
            except (ValueError, IndexError) as e:
                print(f"      Warning: Failed to parse document score: {e}")
                continue
        
        # If no scores parsed, log warning
        if not scores and batch:
            print(f"      ⚠️ Warning: No scores parsed from response")
            print(f"         Response sample: {response[:300]}...")
        
        return scores
    
    def _parse_deep_analysis_response(self, response: str) -> Dict:
        """
        Parse deep analysis response with structured extraction (Option 1)
        Primary: Extract structured BREACH/CONTRADICTION/TIMELINE blocks
        Fallback: Natural language extraction if structured blocks missing
        """
        
        result = {
            'findings': [],
            'critical_findings': [],
            'investigations_needed': [],
            'breaches': [],           # Structured breach data
            'contradictions': [],     # Structured contradiction data
            'timeline_events': [],    # Structured timeline data
            'confidence': 0.0,
            'should_continue': True,
            'raw_response': response[:1000]
        }
        
        # ====================================================================
        # EXTRACT BREACHES (Structured format)
        # ====================================================================
        
        breach_pattern = r'BREACH_START\s*Description:\s*(.+?)\s*Clause/Obligation:\s*(.+?)\s*Evidence:\s*(\[.+?\])\s*Confidence:\s*(0?\.\d+|1\.0)\s*Causation:\s*(.+?)\s*Quantum:\s*(.+?)\s*BREACH_END'
        breach_matches = re.finditer(breach_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in breach_matches:
            try:
                evidence_str = match.group(3).strip()
                # Parse JSON array of evidence
                try:
                    evidence = json.loads(evidence_str)
                except json.JSONDecodeError:
                    # Fallback: extract document IDs manually
                    evidence = re.findall(r'DOC_[\w\d]+', evidence_str)
                
                result['breaches'].append({
                    'description': match.group(1).strip()[:500],
                    'clause': match.group(2).strip()[:200],
                    'evidence': evidence if isinstance(evidence, list) else [evidence_str],
                    'confidence': float(match.group(4)),
                    'causation': match.group(5).strip()[:500],
                    'quantum': match.group(6).strip()[:200]
                })
            except (ValueError, IndexError) as e:
                print(f"      Warning: Failed to parse structured breach: {e}")
                continue
        
        # Fallback: If no structured breaches, extract from natural language
        if not result['breaches']:
            fallback_breach_pattern = r'(?:breach|violation|failed to comply).*?(?:clause|article|section|obligation)\s*[\d\.]+.*?(?:\n|$)'
            fallback_matches = re.finditer(fallback_breach_pattern, response, re.IGNORECASE | re.MULTILINE)
            
            for match in fallback_matches:
                breach_text = match.group(0).strip()
                # Extract doc IDs mentioned nearby
                doc_ids = re.findall(r'DOC_[\w\d]+', breach_text)
                
                result['breaches'].append({
                    'description': breach_text[:500],
                    'clause': 'unknown',
                    'evidence': doc_ids if doc_ids else [],
                    'confidence': 0.6,  # Lower confidence for unstructured
                    'causation': '',
                    'quantum': ''
                })
        
        # ====================================================================
        # EXTRACT CONTRADICTIONS (Structured format)
        # ====================================================================
        
        contradiction_pattern = r'CONTRADICTION_START\s*Statement_A:\s*(.+?)\s*Statement_B:\s*(.+?)\s*Doc_A:\s*(.+?)\s*Doc_B:\s*(.+?)\s*Severity:\s*(\d+)\s*Confidence:\s*(0?\.\d+|1\.0)\s*Implications:\s*(.+?)\s*CONTRADICTION_END'
        contra_matches = re.finditer(contradiction_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in contra_matches:
            try:
                result['contradictions'].append({
                    'statement_a': match.group(1).strip()[:1000],
                    'statement_b': match.group(2).strip()[:1000],
                    'doc_a': match.group(3).strip(),
                    'doc_b': match.group(4).strip(),
                    'severity': min(10, max(1, int(match.group(5)))),
                    'confidence': float(match.group(6)),
                    'implications': match.group(7).strip()[:1000]
                })
            except (ValueError, IndexError) as e:
                print(f"      Warning: Failed to parse structured contradiction: {e}")
                continue
        
        # Fallback: Natural language contradiction extraction
        if not result['contradictions']:
            fallback_contra_pattern = r'(?:contradiction|inconsistent|conflicts? with).*?(?:\n|$)'
            fallback_matches = re.finditer(fallback_contra_pattern, response, re.IGNORECASE | re.MULTILINE)
            
            for match in fallback_matches:
                contra_text = match.group(0).strip()
                result['contradictions'].append({
                    'statement_a': contra_text[:500],
                    'statement_b': 'See document context',
                    'doc_a': 'unknown',
                    'doc_b': 'unknown',
                    'severity': 7,
                    'confidence': 0.6
                })
        
        # ====================================================================
        # EXTRACT TIMELINE EVENTS (Structured format)
        # ====================================================================
        
        timeline_pattern = r'TIMELINE_EVENT_START\s*Date:\s*(.+?)\s*Description:\s*(.+?)\s*Participants:\s*(.+?)\s*Documents:\s*(\[.+?\])\s*Confidence:\s*(0?\.\d+|1\.0)\s*Critical:\s*(YES|NO)\s*TIMELINE_EVENT_END'
        timeline_matches = re.finditer(timeline_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in timeline_matches:
            try:
                docs_str = match.group(4).strip()
                try:
                    documents = json.loads(docs_str)
                except json.JSONDecodeError:
                    documents = re.findall(r'DOC_[\w\d]+', docs_str)
                
                result['timeline_events'].append({
                    'date': match.group(1).strip(),
                    'description': match.group(2).strip()[:500],
                    'participants': match.group(3).strip()[:200],
                    'documents': documents if isinstance(documents, list) else [docs_str],
                    'confidence': float(match.group(5)),
                    'is_critical': match.group(6).upper() == 'YES'
                })
            except (ValueError, IndexError) as e:
                print(f"      Warning: Failed to parse structured timeline event: {e}")
                continue
        
        # Fallback: Extract dates from natural language
        if not result['timeline_events']:
            fallback_date_pattern = r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}-\d{2}-\d{2})\s*[:\-]?\s*(.{20,200}?)(?:\n|$)'
            date_matches = re.finditer(fallback_date_pattern, response, re.MULTILINE)
            
            for match in date_matches:
                result['timeline_events'].append({
                    'date': match.group(1),
                    'description': match.group(2).strip()[:500],
                    'participants': '',
                    'documents': [],
                    'confidence': 0.5,
                    'is_critical': False
                })
        
        # ====================================================================
        # EXTRACT CONFIDENCE SCORE (Multiple patterns)
        # ====================================================================
        
        confidence_patterns = [
            r'(?:CONFIDENCE|Confidence):\s*(0?\.\d+|1\.0)',  # "CONFIDENCE: 0.85"
            r'(\d{1,3})%\s*confident',                        # "85% confident"
            r'confidence.*?(?:is|of)\s*(0?\.\d+|1\.0)',      # "confidence is 0.85"
            r'(?:current|overall)\s+confidence:\s*(0?\.\d+|1\.0)'  # "current confidence: 0.73"
        ]
        
        for pattern in confidence_patterns:
            conf_match = re.search(pattern, response, re.IGNORECASE)
            if conf_match:
                val = conf_match.group(1)
                # Convert percentage to decimal if needed
                result['confidence'] = float(val) / 100 if float(val) > 1 else float(val)
                break
        
        # Log warning if confidence not found
        if result['confidence'] == 0.0 and 'confidence' in response.lower():
            print(f"      ⚠️ Confidence mentioned but not parsed. Sample:")
            print(f"         {response[:300]}...")
        
        # ====================================================================
        # EXTRACT CONTINUE DECISION
        # ====================================================================
        
        continue_patterns = [
            r'(?:CONTINUE|Continue):\s*(YES|NO)',
            r'(?:Should|should)\s+(?:analysis\s+)?continue\??\s*:?\s*(YES|NO)',
            r'analysis\s+(?:should\s+)?continue:\s*(YES|NO)'
        ]
        
        for pattern in continue_patterns:
            continue_match = re.search(pattern, response, re.IGNORECASE)
            if continue_match:
                result['should_continue'] = continue_match.group(1).upper() == 'YES'
                break
        
        # ====================================================================
        # EXTRACT CRITICAL FINDINGS (Investigation triggers)
        # ====================================================================
        
        critical_pattern = r'\[(?:CRITICAL|NUCLEAR)\]\s*(.+?)(?=\[(?:CRITICAL|NUCLEAR)\]|\n\n|$)'
        critical_matches = re.finditer(critical_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in critical_matches:
            investigation_text = match.group(1).strip()
            severity = 'NUCLEAR' if '[NUCLEAR]' in match.group(0).upper() else 'CRITICAL'
            
            # Extract topic (first sentence or up to 100 chars)
            topic = investigation_text.split('.')[0][:100] if '.' in investigation_text else investigation_text[:100]
            
            result['investigations_needed'].append({
                'topic': topic,
                'priority': 9 if severity == 'NUCLEAR' else 7,
                'trigger_text': investigation_text[:500]
            })
            
            result['critical_findings'].append({
                'severity': severity,
                'content': investigation_text[:500],
                'needs_investigation': True
            })
        
        # ====================================================================
        # EXTRACT GENERAL FINDINGS
        # ====================================================================
        
        finding_patterns = [
            r'(?:^|\n)\s*[\d\-\•]+\s*(.{20,300}(?:breach|evidence|misrepresentation|contract|violation).*?)(?=\n[\d\-\•]|\n\n|$)',
            r'(?:Finding|FINDING)\s*\d+:\s*(.+?)(?=Finding|FINDING|\n\n|$)'
        ]
        
        for pattern in finding_patterns:
            finding_matches = re.finditer(pattern, response, re.IGNORECASE | re.MULTILINE)
            for match in finding_matches:
                finding_text = match.group(1).strip()
                if len(finding_text) > 20:
                    result['findings'].append(finding_text)
        
        return result
    
    def _parse_investigation_response(self, response: str) -> Dict:
        """
        Parse investigation response
        Extract: conclusion, confidence, whether to spawn children, child topics
        """
        
        result = {
            'conclusion': '',
            'confidence': 0.0,
            'spawn_children': False,
            'child_investigations': []
        }
        
        # Extract final conclusion
        conclusion_patterns = [
            r'(?:CONCLUSION|Final Conclusion|Investigation Conclusion):\s*(.+?)(?=\n\n|DECISION|CONFIDENCE|$)',
            r'(?:^|\n)Conclusion:\s*(.+?)(?=\n\n|$)'
        ]
        
        for pattern in conclusion_patterns:
            conclusion_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if conclusion_match:
                result['conclusion'] = conclusion_match.group(1).strip()[:1000]
                break
        
        # Extract confidence
        confidence_patterns = [
            r'(?:CONFIDENCE|Confidence).*?:\s*(0?\.\d+|1\.0)',
            r'(\d{1,3})%\s*confident',
            r'confidence.*?(?:is|of)\s*(0?\.\d+|1\.0)'
        ]
        
        for pattern in confidence_patterns:
            conf_match = re.search(pattern, response, re.IGNORECASE)
            if conf_match:
                val = conf_match.group(1)
                result['confidence'] = float(val) / 100 if float(val) > 1 else float(val)
                break
        
        # Check if Claude says YES to spawning children
        decision_patterns = [
            r'(?:DECISION|Continue Investigating\?).*?:\s*(YES|NO)',
            r'(?:Should\s+)?(?:continue|investigate)\s+(?:further|investigating)\??\s*:?\s*(YES|NO)',
            r'(?:Spawn|spawn)\s+(?:child\s+)?investigations\??\s*:?\s*(YES|NO)'
        ]
        
        for pattern in decision_patterns:
            decision_match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if decision_match:
                result['spawn_children'] = decision_match.group(1).upper() == 'YES'
                break
        
        # If YES, extract child investigation topics
        if result['spawn_children']:
            # Look for structured "Topic:" patterns
            child_pattern = r'Topic:\s*(.+?)\s*Priority:\s*(\d+)\s*Reason:\s*(.+?)(?=Topic:|STRATEGIC|$)'
            child_matches = re.finditer(child_pattern, response, re.DOTALL | re.IGNORECASE)
            
            for match in child_matches:
                topic = match.group(1).strip()[:100]
                try:
                    priority = int(match.group(2))
                except ValueError:
                    priority = 5
                reason = match.group(3).strip()[:200]
                
                result['child_investigations'].append({
                    'topic': topic,
                    'priority': min(10, max(1, priority)),
                    'reason': reason
                })
        
        return result
    
    def _build_claims(self, intelligence: Dict) -> Dict:
        """
        Build legal claims element-by-element
        Maps evidence to claim elements
        """
        
        claims = {}
        
        # Extract data from intelligence
        breaches = intelligence.get('breaches', [])
        evidence = intelligence.get('evidence', [])
        contradictions = intelligence.get('contradictions', [])
        
        # Breach of Contract Claim
        contract_breaches = [
            b for b in breaches 
            if b.get('type') == 'contract' or 'contract' in str(b).lower()
        ]
        
        if contract_breaches or 'contract' in str(intelligence).lower():
            claims['breach_of_contract'] = {
                'elements': {
                    'contract_exists': len(contract_breaches) > 0,
                    'obligations_defined': True,  # Assume true if breaches identified
                    'breach_occurred': len(contract_breaches) > 0,
                    'causation_proven': any(b.get('causation') for b in contract_breaches),
                    'damages_quantified': any(b.get('damages') for b in contract_breaches)
                },
                'evidence': [b.get('evidence', []) for b in contract_breaches],
                'breaches': contract_breaches,
                'strength': self._calculate_claim_strength(contract_breaches)
            }
        
        # Misrepresentation Claim
        misrep_indicators = [
            b for b in breaches 
            if 'misrepresent' in str(b).lower() or 'false' in str(b).lower()
        ]
        
        if misrep_indicators or any('misrepresent' in str(c).lower() for c in contradictions):
            claims['misrepresentation'] = {
                'elements': {
                    'false_statement': True,
                    'materiality': len(misrep_indicators) > 0,
                    'reliance': any(b.get('reliance') for b in misrep_indicators),
                    'damages': any(b.get('damages') for b in misrep_indicators)
                },
                'evidence': [b.get('evidence', []) for b in misrep_indicators],
                'breaches': misrep_indicators,
                'strength': self._calculate_claim_strength(misrep_indicators)
            }
        
        # Negligence Claim
        negligence_indicators = [
            b for b in breaches 
            if 'negligent' in str(b).lower() or 'duty' in str(b).lower()
        ]
        
        if negligence_indicators:
            claims['negligence'] = {
                'elements': {
                    'duty_of_care': True,
                    'breach_of_duty': len(negligence_indicators) > 0,
                    'causation': any(b.get('causation') for b in negligence_indicators),
                    'damages': any(b.get('damages') for b in negligence_indicators)
                },
                'evidence': [b.get('evidence', []) for b in negligence_indicators],
                'breaches': negligence_indicators,
                'strength': self._calculate_claim_strength(negligence_indicators)
            }
        
        return claims
    
    def _calculate_claim_strength(self, breaches: List[Dict]) -> float:
        """Calculate claim strength 0.0-1.0 based on breach confidence"""
        if not breaches:
            return 0.0
        
        strengths = []
        for breach in breaches:
            if isinstance(breach, dict):
                # Default 0.6 if breach exists but no confidence specified
                conf = breach.get('confidence', 0.6)
                strengths.append(conf)
        
        if not strengths:
            # Breaches exist but all malformed - low confidence
            return 0.3
        
        return sum(strengths) / len(strengths)
    
    def _generate_strategy(self, intelligence: Dict, claims: Dict) -> Dict:
        """Generate strategic recommendations"""
        
        strategy = {
            'strongest_claims': [],
            'weakest_areas': [],
            'evidence_gaps': [],
            'settlement_position': {
                'minimum_acceptable': 'To be determined based on quantum',
                'target': 'Full damages plus costs',
                'justification': 'Strong evidence base'
            },
            'trial_strategy': {
                'opening_theme': 'Breach of fundamental contractual obligations',
                'key_witnesses': [],
                'critical_documents': []
            }
        }
        
        # Identify strongest claims (strength > 0.7)
        for claim_type, claim_data in claims.items():
            strength = claim_data.get('strength', 0.0)
            evidence_count = len(claim_data.get('evidence', []))
            
            if strength > 0.7:
                strategy['strongest_claims'].append({
                    'claim': claim_type,
                    'strength': round(strength, 2),
                    'evidence_count': evidence_count,
                    'recommendation': 'Lead with this claim'
                })
            elif strength < 0.4:
                strategy['weakest_areas'].append({
                    'claim': claim_type,
                    'strength': round(strength, 2),
                    'reason': 'Insufficient evidence or weak causation link',
                    'recommendation': 'Seek additional evidence or consider dropping'
                })
        
        # Identify evidence gaps from breaches
        all_breaches = intelligence.get('breaches', [])
        for breach in all_breaches:
            if isinstance(breach, dict) and not breach.get('evidence'):
                strategy['evidence_gaps'].append({
                    'area': breach.get('description', str(breach))[:100],
                    'needed': 'Documentary evidence required',
                    'priority': 'High' if breach.get('severity', 0) > 7 else 'Medium'
                })
        
        # Extract critical documents from intelligence
        evidence_items = intelligence.get('evidence', [])
        if evidence_items:
            strategy['trial_strategy']['critical_documents'] = evidence_items[:10]
        
        return strategy
    
    def _parse_deliverables_response(self, response: str) -> Dict:
        """
        Parse tribunal deliverables from response
        Extracts: scott_schedule, witness_statements, skeleton_argument, etc.
        """
        
        deliverables = {}
        
        # Define document types and their pattern variations
        doc_types = {
            'scott_schedule': [
                r'(?:SCOTT SCHEDULE|Scott Schedule|Chronology):?\s*(.+?)(?=\n\n(?:WITNESS|SKELETON|DISCLOSURE|OPENING|EXPERT)|$)',
                r'1\.\s*SCOTT SCHEDULE.*?:?\s*(.+?)(?=\n\n2\.|$)'
            ],
            'witness_statements': [
                r'(?:WITNESS STATEMENT|Witness Statement|Witness Outlines):?\s*(.+?)(?=\n\n(?:SKELETON|DISCLOSURE|OPENING|EXPERT)|$)',
                r'2\.\s*WITNESS STATEMENT.*?:?\s*(.+?)(?=\n\n3\.|$)'
            ],
            'skeleton_argument': [
                r'(?:SKELETON ARGUMENT|Skeleton Argument):?\s*(.+?)(?=\n\n(?:DISCLOSURE|OPENING|EXPERT)|$)',
                r'3\.\s*SKELETON ARGUMENT.*?:?\s*(.+?)(?=\n\n4\.|$)'
            ],
            'disclosure_requests': [
                r'(?:DISCLOSURE REQUEST|Disclosure Requests):?\s*(.+?)(?=\n\n(?:OPENING|EXPERT)|$)',
                r'4\.\s*DISCLOSURE REQUEST.*?:?\s*(.+?)(?=\n\n5\.|$)'
            ],
            'opening_submissions': [
                r'(?:OPENING SUBMISSION|Opening Submissions):?\s*(.+?)(?=\n\n(?:EXPERT)|$)',
                r'5\.\s*OPENING SUBMISSION.*?:?\s*(.+?)(?=\n\n6\.|$)'
            ],
            'expert_instructions': [
                r'(?:EXPERT INSTRUCTION|Expert Instructions):?\s*(.+?)$',
                r'6\.\s*EXPERT INSTRUCTION.*?:?\s*(.+?)$'
            ]
        }
        
        # Try to extract each deliverable type
        for doc_type, patterns in doc_types.items():
            found = False
            for pattern in patterns:
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    deliverables[doc_type] = match.group(1).strip()
                    found = True
                    break
            
            if not found:
                # Log warning but don't fail
                print(f"        ⚠️ Could not extract {doc_type}")
                deliverables[doc_type] = f"[{doc_type.replace('_', ' ').title()} not found in response]"
        
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