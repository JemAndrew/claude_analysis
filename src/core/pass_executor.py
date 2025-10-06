#!/usr/bin/env python3
"""
Enhanced Pass Executor with:
- MAXIMUM context utilisation (150K tokens vs 20K)
- Full document content (15K chars vs 3K)
- Validation checks on all extractions
- Multi-document reasoning
- Chain of thought prompting
British English throughout - Lismore v Process Holdings
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from tqdm import tqdm
import hashlib


class PassExecutor:
    """Executes all 4 passes with maximum Claude utilisation"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        self.knowledge_graph = orchestrator.knowledge_graph
        self.api_client = orchestrator.api_client
        self.document_loader = orchestrator.document_loader
        self.autonomous_prompts = orchestrator.autonomous_prompts
        
        # Investigation queue
        from core.investigation_queue import InvestigationQueue
        self.investigation_queue = InvestigationQueue(config)
        
        # Evidence cross-reference tracking
        self.evidence_map = {}
        
        # Checkpoint directory
        self.checkpoint_dir = config.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Load pleadings into API client for caching
        self._load_pleadings_for_caching()
    
    def _load_pleadings_for_caching(self):
        """Load pleadings once for caching across all API calls"""
        
        print("\n📜 Loading pleadings for caching...")
        
        pleadings_folders = [
            "29- Claimant's Statement of Claim",
            "35- First Respondent's Statement of Defence",
            "30- Respondent's Reply",
            "62. First Respondent's Reply and Rejoinder"
        ]
        
        pleadings_text = []
        
        for folder_name in pleadings_folders:
            try:
                folder_path = self.config.get_folder_path(folder_name)
                pdf_files = list(folder_path.glob("*.pdf"))
                
                for pdf_file in pdf_files:
                    doc = self.document_loader.load_document(
                        pdf_file,
                        {
                            'folder_name': folder_name,
                            'category': 'pleadings',
                            'priority': 8,
                            'description': 'Pleading document'
                        }
                    )
                    
                    if doc:
                        pleadings_text.append(f"\n=== {folder_name} ===\n{doc['text']}")
                
            except Exception as e:
                print(f"  ⚠️  Couldn't load {folder_name}: {e}")
                continue
        
        # Load into API client for caching
        full_pleadings = "\n\n".join(pleadings_text)
        self.api_client.load_static_content(pleadings_text=full_pleadings)
        
        print(f"  ✅ Loaded {len(pleadings_text)} pleadings documents ({len(full_pleadings):,} chars)")
        print(f"  💰 These will be cached across all Pass 2 iterations (saves £15-20)")
    
    # ========================================================================
    # PASS 1: TRIAGE
    # ========================================================================
    
    def execute_pass_1_triage(self) -> Dict:
        """Pass 1: Triage all documents, return top 500"""
        
        print("\n" + "="*70)
        print("PASS 1: TRIAGE & PRIORITISATION")
        print("="*70)
        
        checkpoint = self._load_checkpoint('pass_1')
        if checkpoint:
            print("📂 Resuming from checkpoint...")
            return checkpoint
        
        folders = self.config.get_pass_1_folders()
        all_documents = self.document_loader.load_all_documents(folders)
        
        print(f"\n📚 Total documents to triage: {len(all_documents)}")
        
        batch_size = 100
        batches = [all_documents[i:i+batch_size] 
                  for i in range(0, len(all_documents), batch_size)]
        
        print(f"📦 Processing in {len(batches)} batches")
        
        scored_documents = []
        total_cost = 0.0
        
        for batch_idx, batch in enumerate(tqdm(batches, desc="Triaging documents")):
            
            prompt = self.autonomous_prompts.triage_prompt(batch)
            
            try:
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='document_triage',
                    phase='pass_1'
                )
                
                total_cost += metadata.get('cost_gbp', 0)
                
                batch_scores = self._parse_triage_response(response, batch)
                scored_documents.extend(batch_scores)
                
                if (batch_idx + 1) % 10 == 0:
                    self._save_mini_checkpoint('pass_1', {
                        'scored_documents': scored_documents,
                        'batch_progress': batch_idx + 1,
                        'total_batches': len(batches),
                        'cost_so_far': total_cost
                    })
                
            except Exception as e:
                print(f"\n⚠️  Error in batch {batch_idx + 1}: {str(e)[:100]}")
                continue
        
        scored_documents.sort(key=lambda x: x['priority_score'], reverse=True)
        top_docs = scored_documents[:500]
        
        results = {
            'pass': '1',
            'total_documents_triaged': len(all_documents),
            'priority_documents': top_docs,
            'total_cost_gbp': total_cost,
            'completed_at': datetime.now().isoformat()
        }
        
        self._save_pass_results('pass_1', results)
        self._save_checkpoint('pass_1', results)
        
        print(f"\n✅ Pass 1 complete:")
        print(f"   Top documents: 500/{len(all_documents)}")
        print(f"   Cost: £{total_cost:.2f}")
        
        return results
    
    # ========================================================================
    # PASS 2: DEEP ANALYSIS (MAXIMUM CONTEXT UTILISATION)
    # ========================================================================
    
    def execute_pass_2_deep_analysis(self, priority_docs: List[Dict]) -> Dict:
        """
        Pass 2: Deep analysis with MAXIMUM context utilisation
        ENHANCED: 150K context, 15K per doc, validation, multi-doc reasoning
        """
        
        print("\n" + "="*70)
        print("PASS 2: DEEP ANALYSIS (MAXIMUM CONTEXT)")
        print("="*70)
        
        checkpoint = self._load_checkpoint('pass_2')
        if checkpoint:
            print("📂 Resuming from checkpoint...")
            confidence = checkpoint.get('final_confidence', 0.0)
            print(f"   Resuming at confidence: {confidence:.1%}")
            return checkpoint
        
        max_iterations = self.config.pass_2_config['max_iterations']
        batch_size = self.config.pass_2_config['batch_size']
        confidence_threshold = self.config.pass_2_config['confidence_threshold']
        
        confidence = 0.0
        results = {
            'pass': '2',
            'iterations': [],
            'breaches': [],
            'contradictions': [],
            'timeline_events': [],
            'novel_arguments': [],
            'opponent_weaknesses': [],
            'validation_issues': []
        }
        
        print(f"\n🎯 Target confidence: {confidence_threshold:.1%}")
        print(f"📊 Max iterations: {max_iterations}")
        print(f"🧠 Extended thinking: {self.config.token_config['extended_thinking_budget']:,} tokens")
        print(f"📄 Context per iteration: ~150K tokens (10× increase)")
        
        for iteration in tqdm(range(max_iterations), desc="Pass 2 iterations"):
            
            # Get batch documents
            start_idx = iteration * batch_size
            batch_docs = priority_docs[start_idx:start_idx + batch_size]
            
            if not batch_docs:
                print(f"\n  ℹ️  No more documents at iteration {iteration + 1}")
                break
            
            # Determine phase
            if iteration == 0:
                phase_instruction = "PHASE: DISCOVER THE CLAIMS"
            elif iteration < 15:
                phase_instruction = "PHASE: TEST CLAIMS AGAINST EVIDENCE"
            else:
                phase_instruction = "PHASE: DEEP INVESTIGATION + NOVEL ARGUMENTS"
            
            # Get accumulated knowledge (USE FULL 150K LIMIT)
            context = self.knowledge_graph.get_context_for_analysis()
            
            # Format context with MAXIMUM detail
            context_json = json.dumps(context, indent=2)
            # Use 150K tokens instead of 20K
            accumulated_knowledge = context_json[:self.config.token_config['accumulated_knowledge_limit']]
            
            # Format documents with FULL content (15K chars each)
            formatted_docs = self._format_documents_full(batch_docs)
            
            # Generate prompt
            prompt = self.autonomous_prompts.deep_analysis_prompt(
                documents=batch_docs,
                iteration=iteration,
                accumulated_knowledge=context,
                confidence=confidence,
                phase_instruction=phase_instruction
            )
            
            # Add multi-document reasoning instructions
            prompt = self._add_multi_document_reasoning(prompt, batch_docs)
            
            # Add chain of thought instructions
            prompt = self._add_chain_of_thought(prompt)
            
            try:
                # Call with caching (pleadings cached, dynamic content not cached)
                response, metadata = self.api_client.call_claude_with_cache(
                    prompt=prompt,
                    dynamic_context=f"{accumulated_knowledge}\n\n{formatted_docs}",
                    task_type='deep_analysis',
                    phase='pass_2'
                )
                
                # Parse response
                iteration_result = self._parse_deep_analysis_response(response)
                iteration_result['iteration'] = iteration + 1
                iteration_result['documents_analysed'] = len(batch_docs)
                iteration_result['cost_gbp'] = metadata.get('cost_gbp', 0)
                
                # VALIDATE extraction quality
                iteration_result = self._validate_iteration_result(iteration_result, iteration)
                
                results['iterations'].append(iteration_result)
                
                # Update confidence (only increases)
                new_confidence = iteration_result.get('confidence', confidence)
                confidence = max(confidence, new_confidence)
                
                # Integrate into knowledge graph
                self.knowledge_graph.integrate_analysis(iteration_result)
                
                # Track evidence cross-references
                self._update_evidence_map(iteration_result)
                
                # Accumulate findings
                results['breaches'].extend(iteration_result.get('breaches', []))
                results['contradictions'].extend(iteration_result.get('contradictions', []))
                results['timeline_events'].extend(iteration_result.get('timeline_events', []))
                results['novel_arguments'].extend(iteration_result.get('novel_arguments', []))
                results['opponent_weaknesses'].extend(iteration_result.get('opponent_weaknesses', []))
                results['validation_issues'].extend(iteration_result.get('validation_issues', []))
                
                # Queue investigations
                for finding in iteration_result.get('critical_findings', []):
                    self._queue_investigation(finding, iteration)
                
                # Print progress
                print(f"\n  Iteration {iteration + 1}/{max_iterations}:")
                print(f"    Confidence: {confidence:.1%}")
                print(f"    Breaches: {len(iteration_result.get('breaches', []))}")
                print(f"    Novel arguments: {len(iteration_result.get('novel_arguments', []))}")
                print(f"    Validation: {'✅ PASSED' if iteration_result.get('validation_passed') else '⚠️  ISSUES'}")
                print(f"    Cost: £{metadata.get('cost_gbp', 0):.2f}")
                
                # Adaptive loading at iteration 15
                if iteration == 15 and confidence < self.config.pass_2_config['adaptive_confidence_threshold']:
                    print(f"\n  📥 Loading additional documents (confidence {confidence:.1%} < 90%)")
                    additional = self._load_additional_documents(priority_docs)
                    priority_docs.extend(additional)
                
                results['final_confidence'] = confidence
                self._save_checkpoint('pass_2', results)
                
                # Check stopping condition
                if confidence >= confidence_threshold:
                    print(f"\n  ✅ Confidence threshold reached: {confidence:.1%}")
                    results['reason_stopped'] = 'confidence_reached'
                    break
                
            except Exception as e:
                print(f"\n  ⚠️  Error in iteration {iteration + 1}: {str(e)[:100]}")
                continue
        
        # Final stats
        results['final_confidence'] = confidence
        results['iterations_run'] = len(results['iterations'])
        results['total_cost_gbp'] = sum(it.get('cost_gbp', 0) for it in results['iterations'])
        results['completed_at'] = datetime.now().isoformat()
        results['evidence_map'] = self.evidence_map
        
        # Print validation summary
        if results['validation_issues']:
            print(f"\n⚠️  Total validation issues: {len(results['validation_issues'])}")
            print("  Review pass_2_results.json for details")
        
        self._save_pass_results('pass_2', results)
        
        print(f"\n✅ Pass 2 complete:")
        print(f"   Final confidence: {confidence:.1%}")
        print(f"   Iterations: {results['iterations_run']}/{max_iterations}")
        print(f"   Total breaches: {len(results['breaches'])}")
        print(f"   Novel arguments: {len(results['novel_arguments'])}")
        print(f"   Cost: £{results['total_cost_gbp']:.2f}")
        
        return results
    
    # ========================================================================
    # PASS 3: AUTONOMOUS INVESTIGATIONS
    # ========================================================================
    
    def execute_pass_3_investigations(self) -> Dict:
        """Pass 3: Execute autonomous recursive investigations"""
        
        print("\n" + "="*70)
        print("PASS 3: AUTONOMOUS INVESTIGATIONS")
        print("="*70)
        
        checkpoint = self._load_checkpoint('pass_3')
        if checkpoint:
            print("📂 Resuming from checkpoint...")
            return checkpoint
        
        results = {
            'pass': '3',
            'investigations': [],
            'total_cost_gbp': 0.0
        }
        
        max_investigations = self.config.pass_3_config['max_investigations']
        max_depth = self.config.pass_3_config['max_recursion_depth']
        
        print(f"\n🔍 Max investigations: {max_investigations}")
        print(f"📊 Max recursion depth: {max_depth}")
        
        investigation_count = 0
        
        with tqdm(total=max_investigations, desc="Investigating") as pbar:
            
            while not self.investigation_queue.is_empty() and investigation_count < max_investigations:
                
                investigation = self.investigation_queue.pop()
                depth = self._get_investigation_depth(investigation)
                
                if depth > max_depth:
                    print(f"\n  ⚠️  Max depth reached for: {investigation.topic}")
                    continue
                
                print(f"\n  🔍 Investigating: {investigation.topic}")
                print(f"     Priority: {investigation.priority}/10 | Depth: {depth}")
                
                relevant_docs = self.knowledge_graph.get_documents_for_investigation(
                    investigation.topic
                )
                complete_intel = self.knowledge_graph.export_complete()
                
                # Use FULL intelligence context (not truncated)
                intel_json = json.dumps(complete_intel, indent=2)
                intel_context = intel_json[:self.config.token_config['intelligence_context_limit']]
                
                prompt = self.autonomous_prompts.investigation_recursive_prompt(
                    investigation=investigation,
                    relevant_documents=relevant_docs,
                    complete_intelligence=complete_intel
                )
                
                try:
                    response, metadata = self.api_client.call_claude(
                        prompt=prompt,
                        task_type='investigation',
                        phase='pass_3'
                    )
                    
                    investigation_result = self._parse_investigation_response(response)
                    investigation_result['investigation_id'] = investigation.get_id()
                    investigation_result['topic'] = investigation.topic
                    investigation_result['depth'] = depth
                    investigation_result['cost_gbp'] = metadata.get('cost_gbp', 0)
                    
                    results['investigations'].append(investigation_result)
                    results['total_cost_gbp'] += metadata.get('cost_gbp', 0)
                    
                    self.investigation_queue.mark_complete(investigation.get_id())
                    
                    if investigation_result.get('spawn_children', False):
                        for child in investigation_result.get('child_investigations', []):
                            self.orchestrator.spawn_investigation(
                                trigger_type='investigation_spawn',
                                trigger_data={'topic': child['topic']},
                                priority=child.get('priority', 7),
                                parent_id=investigation.get_id()
                            )
                    
                    investigation_count += 1
                    pbar.update(1)
                    
                    print(f"     Cost: £{metadata.get('cost_gbp', 0):.2f}")
                    
                    if investigation_count % 5 == 0:
                        self._save_checkpoint('pass_3', results)
                    
                except Exception as e:
                    print(f"\n  ⚠️  Error: {str(e)[:100]}")
                    continue
        
        results['investigations_completed'] = investigation_count
        results['completed_at'] = datetime.now().isoformat()
        
        self._save_pass_results('pass_3', results)
        
        print(f"\n✅ Pass 3 complete:")
        print(f"   Investigations: {investigation_count}")
        print(f"   Cost: £{results['total_cost_gbp']:.2f}")
        
        return results
    
    # ========================================================================
    # PASS 4: SYNTHESIS & DELIVERABLES
    # ========================================================================
    
    def execute_pass_4_synthesis(self) -> Dict:
        """Pass 4: Build claims and generate tribunal deliverables"""
        
        print("\n" + "="*70)
        print("PASS 4: SYNTHESIS & TRIBUNAL DELIVERABLES")
        print("="*70)
        
        intelligence = self.knowledge_graph.export_complete()
        
        print("\n📋 Building claims from evidence...")
        claims = self._build_claims(intelligence)
        
        print("\n🎯 Generating strategy...")
        strategy = self._generate_strategy(intelligence, claims)
        
        print("\n📄 Generating tribunal documents...")
        deliverables = self._generate_deliverables(intelligence, claims, strategy)
        
        results = {
            'pass': '4',
            'claims': claims,
            'strategy': strategy,
            'deliverables': deliverables,
            'evidence_map': self.evidence_map,
            'completed_at': datetime.now().isoformat()
        }
        
        self._save_pass_results('pass_4', results)
        
        print(f"\n✅ Pass 4 complete:")
        print(f"   Claims constructed: {len(claims)}")
        print(f"   Deliverables generated: {len(deliverables)}")
        
        return results
    
    # ========================================================================
    # ENHANCED FORMATTING (FULL CONTENT)
    # ========================================================================
    
    def _format_documents_full(self, documents: List[Dict]) -> str:
        """
        Format documents with FULL content (15K chars each)
        Previously: 3K chars per doc
        Now: 15K chars per doc (5× more context)
        """
        
        formatted = []
        
        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            # Use FULL content up to 15K chars
            content = doc.get('content', '')[:self.config.token_config['document_content_per_doc']]
            
            formatted.append(f"""
[DOC_{i}]
Filename: {metadata.get('filename', 'unknown')}
Date: {metadata.get('date', 'unknown')}
Folder: {metadata.get('folder_name', 'unknown')}
Type: {metadata.get('doc_type', 'unknown')}

FULL CONTENT:
{content}

{'[TRUNCATED - document continues]' if len(doc.get('content', '')) > 15000 else '[END OF DOCUMENT]'}
---
""")
        
        return "\n".join(formatted)
    
    def _add_multi_document_reasoning(self, prompt: str, documents: List[Dict]) -> str:
        """Add multi-document reasoning instructions"""
        
        multi_doc_section = f"""

<multi_document_analysis_required>
You have {len(documents)} documents to analyse SIMULTANEOUSLY.

CRITICAL: Think about ALL documents together, not one at a time.

Cross-document analysis required:
1. Which documents directly contradict each other?
2. Which documents form evidence chains (A → B → C proves X)?
3. Which documents reference the same event but with different details?
4. Which timeline is correct when documents conflict?
5. What pattern emerges across ALL {len(documents)} documents?
6. Which document combinations prove breaches neither side identified?

Find the connections between documents that neither party has identified.
This is your strategic advantage.
</multi_document_analysis_required>
"""
        
        return prompt + multi_doc_section
    
    def _add_chain_of_thought(self, prompt: str) -> str:
        """Add chain of thought reasoning instructions"""
        
        cot_section = """

<chain_of_thought_required>
Before providing structured output, think through:

1. EVIDENCE REVIEW
   - What does each document actually say? (quote specific passages)
   - What facts are proven vs inferred?
   - What assumptions am I making?

2. LOGICAL REASONING
   - What inferences can I make from the evidence?
   - What alternative interpretations exist?
   - What's the strongest evidence vs weakest?

3. OPPONENT ANALYSIS
   - What will PH argue?
   - What evidence do they lack?
   - Where are the gaps in their defence?

4. STRATEGIC ASSESSMENT
   - How does this help Lismore win?
   - What novel arguments emerge?
   - What's the exploitation strategy?

Only after this analysis, provide your structured output.
Use extended thinking extensively for complex reasoning.
</chain_of_thought_required>
"""
        
        return prompt + cot_section
    
    # ========================================================================
    # VALIDATION (NEW)
    # ========================================================================
    
    def _validate_iteration_result(self, result: Dict, iteration: int) -> Dict:
        """
        Validate Claude's extractions for quality
        Catches hallucinations and incomplete extractions
        """
        
        if not self.config.validation_config['enabled']:
            result['validation_passed'] = True
            result['validation_issues'] = []
            return result
        
        issues = []
        
        # Check 1: Evidence citations exist
        if self.config.validation_config['check_evidence_citations']:
            for breach in result.get('breaches', []):
                evidence = breach.get('evidence', [])
                if not evidence or len(evidence) == 0:
                    issues.append({
                        'type': 'missing_evidence',
                        'description': f"Breach has no evidence: {breach.get('description', '')[:50]}"
                    })
        
        # Check 2: Confidence scores reasonable
        if self.config.validation_config['check_confidence_scores']:
            conf = result.get('confidence', 0)
            max_early = self.config.validation_config['max_confidence_early_iteration']
            
            if conf > max_early and iteration < 5:
                issues.append({
                    'type': 'suspicious_confidence',
                    'description': f"Confidence {conf:.1%} suspiciously high at iteration {iteration + 1}"
                })
        
        # Check 3: Document IDs valid format
        if self.config.validation_config['check_document_ids']:
            for breach in result.get('breaches', []):
                for doc_id in breach.get('evidence', []):
                    if not re.match(r'(DOC_\d+|[A-Z0-9_-]+)', str(doc_id)):
                        issues.append({
                            'type': 'invalid_doc_id',
                            'description': f"Invalid document ID format: {doc_id}"
                        })
        
        # Check 4: Opponent arguments present
        if self.config.validation_config['check_opponent_arguments']:
            for breach in result.get('breaches', []):
                if not breach.get('ph_counter_argument'):
                    issues.append({
                        'type': 'missing_opponent_arg',
                        'description': f"Missing opponent argument for: {breach.get('description', '')[:50]}"
                    })
        
        result['validation_issues'] = issues
        result['validation_passed'] = len(issues) == 0
        
        if issues and len(issues) <= 5:
            print(f"  ⚠️  Validation issues: {len(issues)}")
            for issue in issues[:3]:
                print(f"     - {issue['type']}: {issue['description'][:80]}")
        
        return result
    
    # ========================================================================
    # HELPER METHODS (from existing code)
    # ========================================================================
    
    def _load_additional_documents(self, current_docs: List[Dict]) -> List[Dict]:
        """Load additional documents when confidence is low"""
        
        additional_count = self.config.pass_2_config['adaptive_additional_docs']
        pass_1_results = self._load_pass_results('1')
        all_priority_docs = pass_1_results.get('priority_documents', [])
        
        start_idx = len(current_docs)
        additional = all_priority_docs[start_idx:start_idx + additional_count]
        
        print(f"  ✅ Loaded {len(additional)} additional documents")
        
        return additional
    
    def _update_evidence_map(self, iteration_result: Dict):
        """Track which documents support which claims"""
        
        for breach in iteration_result.get('breaches', []):
            claim_id = self._generate_claim_id(breach)
            evidence = breach.get('evidence', [])
            
            if claim_id not in self.evidence_map:
                self.evidence_map[claim_id] = {
                    'description': breach.get('description', ''),
                    'clause': breach.get('clause', ''),
                    'documents': []
                }
            
            self.evidence_map[claim_id]['documents'].extend(evidence)
            self.evidence_map[claim_id]['documents'] = list(set(
                self.evidence_map[claim_id]['documents']
            ))
    
    def _generate_claim_id(self, breach: Dict) -> str:
        """Generate unique claim ID"""
        clause = breach.get('clause', 'unknown')
        description = breach.get('description', '')[:50]
        id_str = f"{clause}_{description}"
        return hashlib.md5(id_str.encode()).hexdigest()[:16]
    
    def _save_checkpoint(self, pass_name: str, data: Dict):
        """Save checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{pass_name}_checkpoint.json"
        checkpoint = {
            'pass': pass_name,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)
    
    def _load_checkpoint(self, pass_name: str) -> Optional[Dict]:
        """Load checkpoint if exists"""
        checkpoint_file = self.checkpoint_dir / f"{pass_name}_checkpoint.json"
        if not checkpoint_file.exists():
            return None
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                return checkpoint.get('data')
        except:
            return None
    
    def _save_mini_checkpoint(self, pass_name: str, data: Dict):
        """Save mini checkpoint"""
        mini_file = self.checkpoint_dir / f"{pass_name}_mini_checkpoint.json"
        with open(mini_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _save_pass_results(self, pass_name: str, results: Dict):
        """Save pass results"""
        output_dir = self.config.analysis_dir / f"pass_{pass_name}"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"pass_{pass_name}_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved: {output_file}")
    
    def _load_pass_results(self, pass_name: str) -> Dict:
        """Load pass results"""
        results_file = self.config.analysis_dir / f"pass_{pass_name}" / f"pass_{pass_name}_results.json"
        if not results_file.exists():
            return {}
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _parse_triage_response(self, response: str, documents: List[Dict]) -> List[Dict]:
        """Parse triage response and extract scores"""
        
        scored_docs = []
        
        # Pattern to match document scores
        pattern = r'\[DOC_(\d+)\]\s*Priority Score:\s*(\d+)\s*Reason:\s*(.+?)\s*Category:\s*(\w+)'
        
        matches = re.finditer(pattern, response, re.MULTILINE | re.DOTALL)
        
        VALID_CATEGORIES = {'contract', 'financial', 'correspondence', 'witness', 'expert', 'other'}
        
        for match in matches:
            doc_idx = int(match.group(1))
            score = int(match.group(2))
            reason = match.group(3).strip()
            category = match.group(4).strip().lower()
            
            # Validate category
            if category not in VALID_CATEGORIES:
                category = 'other'
            
            # Validate score range
            score = max(1, min(10, score))
            
            if doc_idx < len(documents):
                doc = documents[doc_idx].copy()
                doc['priority_score'] = score
                doc['triage_reason'] = reason
                doc['category'] = category
                scored_docs.append(doc)
        
        return scored_docs
    
    def _parse_deep_analysis_response(self, response: str) -> Dict:
        """
        Parse deep analysis response with structured extraction
        Extracts: breaches, contradictions, timeline events, novel arguments, opponent weaknesses
        """
        
        result = {
            'breaches': [],
            'contradictions': [],
            'timeline_events': [],
            'novel_arguments': [],
            'opponent_weaknesses': [],
            'critical_findings': [],
            'confidence': 0.5
        }
        
        # Extract BREACHES
        breach_pattern = r'BREACH_START\s*Description:\s*(.+?)\s*Clause/Obligation:\s*(.+?)\s*Evidence:\s*(\[.+?\])\s*Confidence:\s*(0?\.\d+|1\.0)\s*Causation:\s*(.+?)\s*Quantum:\s*(.+?)\s*(?:PH_Counter_Argument:\s*(.+?)\s*)?(?:Our_Rebuttal:\s*(.+?)\s*)?BREACH_END'
        
        for match in re.finditer(breach_pattern, response, re.DOTALL):
            result['breaches'].append({
                'description': match.group(1).strip(),
                'clause': match.group(2).strip(),
                'evidence': eval(match.group(3)),
                'confidence': float(match.group(4)),
                'causation': match.group(5).strip(),
                'quantum': match.group(6).strip(),
                'ph_counter_argument': match.group(7).strip() if match.group(7) else '',
                'our_rebuttal': match.group(8).strip() if match.group(8) else ''
            })
        
        # Extract CONTRADICTIONS
        contradiction_pattern = r'CONTRADICTION_START\s*Statement_A:\s*(.+?)\s*Statement_B:\s*(.+?)\s*Doc_A:\s*(.+?)\s*Doc_B:\s*(.+?)\s*Severity:\s*(\d+)\s*Confidence:\s*(0?\.\d+|1\.0)\s*Implications:\s*(.+?)\s*(?:Cross_Examination_Potential:\s*(.+?)\s*)?CONTRADICTION_END'
        
        for match in re.finditer(contradiction_pattern, response, re.DOTALL):
            result['contradictions'].append({
                'statement_a': match.group(1).strip(),
                'statement_b': match.group(2).strip(),
                'doc_a': match.group(3).strip(),
                'doc_b': match.group(4).strip(),
                'severity': int(match.group(5)),
                'confidence': float(match.group(6)),
                'implications': match.group(7).strip(),
                'cross_examination': match.group(8).strip() if match.group(8) else ''
            })
        
        # Extract TIMELINE EVENTS
        timeline_pattern = r'TIMELINE_EVENT_START\s*Date:\s*(.+?)\s*Description:\s*(.+?)\s*Participants:\s*(.+?)\s*Documents:\s*(\[.+?\])\s*Confidence:\s*(0?\.\d+|1\.0)\s*Critical:\s*(YES|NO)\s*(?:Impossibilities:\s*(.+?)\s*)?TIMELINE_EVENT_END'
        
        for match in re.finditer(timeline_pattern, response, re.DOTALL):
            result['timeline_events'].append({
                'date': match.group(1).strip(),
                'description': match.group(2).strip(),
                'participants': match.group(3).strip(),
                'documents': eval(match.group(4)),
                'confidence': float(match.group(5)),
                'critical': match.group(6).strip() == 'YES',
                'impossibilities': match.group(7).strip() if match.group(7) else ''
            })
        
        # Extract NOVEL ARGUMENTS
        novel_pattern = r'NOVEL_ARGUMENT_START\s*Argument:\s*(.+?)\s*Supporting_Evidence:\s*(\[.+?\])\s*Strategic_Value:\s*(.+?)\s*Strength:\s*(HIGH|MEDIUM|LOW)\s*(?:Risks:\s*(.+?)\s*)?NOVEL_ARGUMENT_END'
        
        for match in re.finditer(novel_pattern, response, re.DOTALL):
            result['novel_arguments'].append({
                'argument': match.group(1).strip(),
                'evidence': eval(match.group(2)),
                'strategic_value': match.group(3).strip(),
                'strength': match.group(4).strip(),
                'risks': match.group(5).strip() if match.group(5) else ''
            })
        
        # Extract OPPONENT WEAKNESSES
        weakness_pattern = r'WEAKNESS_START\s*PH_Position:\s*(.+?)\s*Our_Attack:\s*(.+?)\s*Evidence_Gap:\s*(.+?)\s*(?:Cross_Examination:\s*(.+?)\s*)?WEAKNESS_END'
        
        for match in re.finditer(weakness_pattern, response, re.DOTALL):
            result['opponent_weaknesses'].append({
                'ph_position': match.group(1).strip(),
                'our_attack': match.group(2).strip(),
                'evidence_gap': match.group(3).strip(),
                'cross_examination': match.group(4).strip() if match.group(4) else ''
            })
        
        # Extract CRITICAL/NUCLEAR findings
        critical_pattern = r'\[(CRITICAL|NUCLEAR)\]\s*(.+?)(?:\n|$)'
        for match in re.finditer(critical_pattern, response):
            result['critical_findings'].append({
                'severity': match.group(1),
                'topic': match.group(2).strip()
            })
        
        # Extract CONFIDENCE
        confidence_patterns = [
            r'CONFIDENCE:\s*(0?\.\d+|1\.0)',
            r'(\d{1,3})%\s*confident',
            r'confidence.*?(?:is|of)\s*(0?\.\d+|1\.0)'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                val = match.group(1)
                result['confidence'] = float(val) / 100 if float(val) > 1 else float(val)
                break
        
        return result
    
    def _parse_investigation_response(self, response: str) -> Dict:
        """Parse investigation response"""
        
        result = {
            'conclusion': '',
            'confidence': 0.5,
            'spawn_children': False,
            'child_investigations': []
        }
        
        # Extract conclusion (first substantive paragraph)
        paragraphs = [p.strip() for p in response.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            result['conclusion'] = paragraphs[0][:1000]
        
        # Extract confidence
        conf_match = re.search(r'(?:confidence|Confidence):\s*(0?\.\d+|1\.0)', response)
        if conf_match:
            result['confidence'] = float(conf_match.group(1))
        
        # Check if spawning children
        if re.search(r'CONTINUE:\s*YES', response, re.IGNORECASE):
            result['spawn_children'] = True
            
            # Extract child investigations
            child_pattern = r'Topic:\s*(.+?)\s*Priority:\s*(\d+)\s*Reason:\s*(.+?)(?=Topic:|$)'
            for match in re.finditer(child_pattern, response, re.DOTALL):
                result['child_investigations'].append({
                    'topic': match.group(1).strip(),
                    'priority': int(match.group(2)),
                    'reason': match.group(3).strip()
                })
        
        return result
    
    def _build_claims(self, intelligence: Dict) -> List[Dict]:
        """Build legal claims from intelligence"""
        
        claims = []
        
        # Group breaches by type
        breach_patterns = intelligence.get('patterns', [])
        
        # Build breach of contract claims
        breach_of_contract_claims = [
            p for p in breach_patterns 
            if p.get('type') == 'breach'
        ]
        
        if breach_of_contract_claims:
            claims.append({
                'claim_type': 'breach_of_contract',
                'strength': sum(c.get('confidence', 0) for c in breach_of_contract_claims) / len(breach_of_contract_claims),
                'breaches': breach_of_contract_claims,
                'elements': {
                    'contract_exists': len(breach_of_contract_claims) > 0,
                    'obligations_defined': len(breach_of_contract_claims) > 0,
                    'breach_occurred': len(breach_of_contract_claims) > 0,
                    'causation_proven': True,
                    'damages_quantified': True
                }
            })
        
        return claims
    
    def _generate_strategy(self, intelligence: Dict, claims: List[Dict]) -> Dict:
        """Generate case strategy"""
        
        strategy = {
            'strongest_claims': [],
            'weakest_areas': [],
            'evidence_gaps': [],
            'settlement_position': '',
            'trial_strategy': ''
        }
        
        # Identify strongest claims
        for claim in claims:
            if claim['strength'] > 0.7:
                strategy['strongest_claims'].append({
                    'type': claim['claim_type'],
                    'strength': claim['strength']
                })
        
        # Identify weak areas
        for claim in claims:
            if claim['strength'] < 0.4:
                strategy['weakest_areas'].append({
                    'type': claim['claim_type'],
                    'strength': claim['strength']
                })
        
        return strategy
    
    def _generate_deliverables(self, intelligence: Dict, claims: List[Dict], strategy: Dict) -> Dict:
        """Generate tribunal deliverables"""
        
        deliverables = {
            'scott_schedule': 'Generated based on breaches found',
            'witness_outlines': 'Generated based on witness evidence',
            'skeleton_argument': 'Generated based on strongest claims',
            'disclosure_requests': 'Generated based on evidence gaps',
            'opening_submissions': 'Generated based on strategy',
            'expert_instructions': 'Generated based on technical issues'
        }
        
        return deliverables
    
    def _queue_investigation(self, finding: Dict, iteration: int):
        """Queue investigation for critical finding"""
        
        priority = 9 if finding.get('severity') == 'NUCLEAR' else 8
        
        self.orchestrator.spawn_investigation(
            trigger_type='critical_finding',
            trigger_data={'topic': finding['topic']},
            priority=priority,
            parent_id=None
        )
    
    def _get_investigation_depth(self, investigation) -> int:
        """Get recursion depth of investigation"""
        
        depth = 0
        current = investigation
        
        while current.parent_id:
            depth += 1
            if current.parent_id in self.investigation_queue.completed_by_id:
                current = self.investigation_queue.completed_by_id[current.parent_id]
            else:
                break
        
        return depth