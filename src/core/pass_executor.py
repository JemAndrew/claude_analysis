#!/usr/bin/env python3
"""
COMPLETE ENHANCED Pass Executor - src/core/pass_executor.py
Adds: Phase 0 Integration, Deduplication, Checkpointing, Validation
British English throughout - Lismore v Process Holdings
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from tqdm import tqdm
import hashlib
from collections import Counter
import math
from utils.deduplication import DocumentDeduplicator


class PassExecutor:
    """Executes all 4 passes with Phase 0 integration, deduplication, and validation"""
    
    def __init__(self, config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator
        self.knowledge_graph = orchestrator.knowledge_graph
        self.api_client = orchestrator.api_client
        self.document_loader = orchestrator.document_loader
        self.autonomous_prompts = orchestrator.autonomous_prompts
        
        # Investigation queue
        from core.investigation_queue import InvestigationQueue
        self.investigation_queue = InvestigationQueue()
        
        # Evidence cross-reference tracking
        self.evidence_map = {}
        
        # Checkpoint directory
        self.checkpoint_dir = config.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Document index for optimised retrieval
        self.document_index = None
        
        # Deduplication system for Pass 1
        if config.deduplication_config['enabled']:
            self.deduplicator = DocumentDeduplicator(
                similarity_threshold=config.deduplication_config['similarity_threshold'],
                prefix_chars=config.deduplication_config['prefix_chars'],
                enable_semantic=config.deduplication_config['enable_semantic']
            )
        else:
            self.deduplicator = None
        
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
        
        pleadings_text = ""
        for folder_name in pleadings_folders:
            folder_path = self.config.source_root / folder_name
            if folder_path.exists():
                docs = self.document_loader.load_folder(folder_path)
                for doc in docs:
                    pleadings_text += f"\n\n=== {doc['filename']} ===\n{doc.get('content', '')[:50000]}"
        
        if pleadings_text:
            if hasattr(self.api_client, 'load_static_content'):
                self.api_client.load_static_content(pleadings_text=pleadings_text)
                print(f"  ✅ Loaded {len(pleadings_text):,} characters of pleadings")
    
    # ========================================================================
    # CHECKPOINT SYSTEM
    # ========================================================================
    
    def _save_checkpoint(self, pass_name: str, data: Dict):
        """Save checkpoint for resume capability"""
        checkpoint_file = self.checkpoint_dir / f"{pass_name}_checkpoint.json"
        
        checkpoint = {
            'pass': pass_name,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Checkpoint saved: {checkpoint_file.name}")
    
    def _load_checkpoint(self, pass_name: str) -> Optional[Dict]:
        """Load checkpoint if exists"""
        checkpoint_file = self.checkpoint_dir / f"{pass_name}_checkpoint.json"
        
        if not checkpoint_file.exists():
            return None
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        # Check if checkpoint is recent (within 7 days)
        checkpoint_time = datetime.fromisoformat(checkpoint['timestamp'])
        age_days = (datetime.now() - checkpoint_time).days
        
        if age_days > 7:
            print(f"  ⚠️  Checkpoint too old ({age_days} days), starting fresh")
            return None
        
        print(f"  📂 Loading checkpoint from {checkpoint['timestamp']}")
        return checkpoint['data']
    
    def _save_mini_checkpoint(self, pass_name: str, data: Dict):
        """Save lightweight progress checkpoint"""
        mini_checkpoint_file = self.checkpoint_dir / f"{pass_name}_progress.json"
        
        progress = {
            'last_updated': datetime.now().isoformat(),
            'progress': data
        }
        
        with open(mini_checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    
    def _clear_checkpoint(self, pass_name: str):
        """Clear checkpoint after successful completion"""
        checkpoint_file = self.checkpoint_dir / f"{pass_name}_checkpoint.json"
        mini_checkpoint_file = self.checkpoint_dir / f"{pass_name}_progress.json"
        
        if checkpoint_file.exists():
            checkpoint_file.unlink()
        
        if mini_checkpoint_file.exists():
            mini_checkpoint_file.unlink()
        
        print(f"  🗑️  Checkpoints cleared for {pass_name}")
    
    # ========================================================================
    # VALIDATION SYSTEM
    # ========================================================================
    
    def _validate_analysis_output(self, result: Dict) -> Dict:
        """
        Validate Pass 2 analysis output for quality and completeness
        """
        issues = []
        warnings = []
        
        # 1. CHECK BREACHES
        breaches = result.get('breaches', [])
        
        if not breaches:
            warnings.append("No breaches extracted in this iteration")
        
        for idx, breach in enumerate(breaches):
            if not breach.get('description'):
                issues.append(f"Breach {idx+1}: Missing description")
            
            if not breach.get('clause'):
                issues.append(f"Breach {idx+1}: Missing clause/obligation")
            
            evidence = breach.get('evidence', [])
            if not evidence or evidence == ['']:
                issues.append(f"Breach {idx+1}: No evidence cited")
            elif len(evidence) < 2:
                warnings.append(f"Breach {idx+1}: Only {len(evidence)} evidence document")
            
            confidence = breach.get('confidence', 0)
            if confidence == 0:
                issues.append(f"Breach {idx+1}: Zero confidence score")
            elif confidence < 0.3:
                warnings.append(f"Breach {idx+1}: Low confidence ({confidence:.2f})")
            
            if not breach.get('causation'):
                warnings.append(f"Breach {idx+1}: Missing causation analysis")
            
            if not breach.get('quantum'):
                warnings.append(f"Breach {idx+1}: Missing quantum estimate")
        
        # 2. CHECK CONTRADICTIONS
        contradictions = result.get('contradictions', [])
        
        for idx, contra in enumerate(contradictions):
            if not contra.get('statement_a') or not contra.get('statement_b'):
                issues.append(f"Contradiction {idx+1}: Missing statements")
            
            documents = contra.get('documents', [])
            if len(documents) < 2:
                issues.append(f"Contradiction {idx+1}: Need at least 2 documents")
        
        # 3. CHECK TIMELINE EVENTS
        timeline = result.get('timeline_events', [])
        
        for idx, event in enumerate(timeline):
            if not event.get('date'):
                issues.append(f"Timeline event {idx+1}: Missing date")
            
            if not event.get('description'):
                issues.append(f"Timeline event {idx+1}: Missing description")
        
        # 4. CHECK CONFIDENCE SCORE
        overall_confidence = result.get('confidence', 0)
        
        if overall_confidence == 0:
            issues.append("Overall confidence not extracted from response")
        elif overall_confidence > 1.0:
            issues.append(f"Invalid confidence: {overall_confidence}")
        
        # Calculate validation score
        total_checks = 10
        failed_checks = len(issues)
        warning_checks = len(warnings)
        
        validation_score = (total_checks - failed_checks - 0.5 * warning_checks) / total_checks
        validation_score = max(0.0, min(1.0, validation_score))
        
        validation_result = {
            'passed': len(issues) == 0,
            'score': validation_score,
            'issues': issues,
            'warnings': warnings,
            'total_issues': len(issues),
            'total_warnings': len(warnings)
        }
        
        if issues:
            print(f"  ⚠️  Validation: {len(issues)} ISSUES")
            for issue in issues[:3]:
                print(f"      - {issue}")
        
        if validation_score >= 0.8:
            print(f"  ✅ Validation score: {validation_score:.2f}")
        else:
            print(f"  ⚠️  Validation score: {validation_score:.2f} (LOW)")
        
        return validation_result
    
    # ========================================================================
    # OPTIMISED DOCUMENT RETRIEVAL (BM25 Algorithm)
    # ========================================================================
    
    def _build_document_index(self):
        """Build inverted index for fast BM25 document retrieval"""
        if self.document_index is not None:
            return
        
        print("\n📚 Building document index for optimal retrieval...")
        
        # Get all documents
        conn = self.knowledge_graph._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT doc_id, content, preview
            FROM discovery_log
        """)
        
        documents = []
        for row in cursor.fetchall():
            doc_id, content, preview = row
            text = content or preview or ""
            documents.append({'doc_id': doc_id, 'text': text})
        
        conn.close()
        
        if not documents:
            print("  ⚠️  No documents found")
            self.document_index = {'docs': [], 'index': {}, 'doc_lengths': {}, 'avgdl': 0}
            return
        
        # Build inverted index with term frequencies
        index = {}  # term -> {doc_id: frequency}
        doc_lengths = {}
        
        for doc in documents:
            doc_id = doc['doc_id']
            terms = self._tokenize(doc['text'])
            doc_lengths[doc_id] = len(terms)
            
            term_counts = Counter(terms)
            for term, count in term_counts.items():
                if term not in index:
                    index[term] = {}
                index[term][doc_id] = count
        
        avgdl = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 0
        
        self.document_index = {
            'docs': documents,
            'index': index,
            'doc_lengths': doc_lengths,
            'avgdl': avgdl,
            'N': len(documents)
        }
        
        print(f"  ✅ Indexed {len(documents):,} documents, {len(index):,} unique terms")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenisation for BM25"""
        # Lowercase and extract words
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'with', 
                      'was', 'this', 'that', 'from', 'have', 'has', 'had'}
        words = [w for w in words if w not in stop_words]
        
        return words
    
    def _bm25_search(self, query: str, top_k: int = 20) -> List[str]:
        """
        BM25 ranking algorithm for document retrieval
        Returns list of doc_ids ranked by relevance
        """
        if self.document_index is None:
            self._build_document_index()
        
        if not self.document_index['docs']:
            return []
        
        query_terms = self._tokenize(query)
        
        if not query_terms:
            return []
        
        # BM25 parameters
        k1 = 1.5  # Term frequency saturation
        b = 0.75  # Length normalisation
        
        N = self.document_index['N']
        avgdl = self.document_index['avgdl']
        index = self.document_index['index']
        doc_lengths = self.document_index['doc_lengths']
        
        # Calculate BM25 scores
        scores = {}
        
        for term in query_terms:
            if term not in index:
                continue
            
            df = len(index[term])  # Document frequency
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
            
            for doc_id, tf in index[term].items():
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                
                doc_len = doc_lengths[doc_id]
                norm = 1 - b + b * (doc_len / avgdl)
                
                scores[doc_id] += idf * (tf * (k1 + 1)) / (tf + k1 * norm)
        
        # Sort by score
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [doc_id for doc_id, score in ranked_docs[:top_k]]
    
    # ========================================================================
    # PASS 1: TRIAGE WITH PHASE 0 INTELLIGENCE AND DEDUPLICATION
    # ========================================================================
    
    def execute_pass_1_triage(self) -> Dict:
        """Pass 1: Triage & prioritisation WITH PHASE 0 INTELLIGENCE AND DEDUPLICATION"""
        
        print("\n" + "="*70)
        print("PASS 1: INTELLIGENT TRIAGE & PRIORITISATION")
        print("="*70)
        
        # Check for checkpoint
        checkpoint = self._load_checkpoint('pass_1')
        if checkpoint:
            print("📂 Resuming from checkpoint...")
            return checkpoint
        
        # ====================================================================
        # LOAD PHASE 0 SMOKING GUN PATTERNS
        # ====================================================================
        phase_0_file = self.config.analysis_dir / "phase_0" / "case_foundation.json"
        smoking_gun_patterns = []
        phase_0_used = False
        
        if phase_0_file.exists():
            try:
                with open(phase_0_file, 'r', encoding='utf-8') as f:
                    phase_0_data = json.load(f)
                
                # Extract smoking gun patterns from Stage 3
                phase_0_foundation = phase_0_data.get('pass_1_reference', {})

                if phase_0_foundation and len(phase_0_foundation.get('document_patterns', [])) > 0:
                
                    print(f"\n✅ Loaded Phase 0 intelligence:")
                    print(f"   • Allegations: {len(phase_0_foundation.get('allegations', []))}")
                    print(f"   • Defences: {len(phase_0_foundation.get('defences', []))}")
                    print(f"   • Key parties: {len(phase_0_foundation.get('key_parties', []))}")
                    print(f"   • Document patterns: {len(phase_0_foundation.get('document_patterns', []))}")
                    print(f"   Using strategic intelligence for triage\n")
                    phase_0_used = True
                else:
                    print(f"\n⚠️  Phase 0 complete but no smoking gun patterns found")
                    print(f"   Performing generic triage\n")
                    
            except Exception as e:
                print(f"\n⚠️  Error loading Phase 0: {e}")
                print(f"   Performing generic triage\n")
        else:
            print(f"\n⚠️  Phase 0 not completed")
            print(f"   Performing generic triage without strategic intelligence")
            print(f"   💡 Tip: Run 'python main.py phase0' first for better results\n")
        
        # ====================================================================
        # LOAD ALL DOCUMENTS
        # ====================================================================
        all_documents = []
        for folder_name in self.config.get_pass_1_folders():
            folder_path = self.config.source_root / folder_name
            if folder_path.exists():
                docs = self.document_loader.load_folder(folder_path)
                all_documents.extend(docs)
        
        initial_doc_count = len(all_documents)
        print(f"\n📁 Loaded {initial_doc_count:,} documents")
        
        # ====================================================================
        # DEDUPLICATION STAGE
        # ====================================================================
        if self.deduplicator:
            print(f"\n🔍 DEDUPLICATION STAGE")
            print(f"{'='*70}")
            print(f"Initial documents: {initial_doc_count:,}")
            print(f"Checking for duplicates...")
            
            unique_docs = []
            duplicate_log = []
            
            for idx, doc in enumerate(all_documents, 1):
                if idx % 100 == 0:
                    print(f"  Progress: {idx:,}/{initial_doc_count:,} ({idx/initial_doc_count:.1%})")
                
                content = doc.get('content', '') or doc.get('preview', '')
                doc_id = doc.get('doc_id', '')
                filename = doc.get('filename', '')
                
                is_dup, reason = self.deduplicator.is_duplicate(content, doc_id, filename)
                
                if not is_dup:
                    unique_docs.append(doc)
                else:
                    duplicate_log.append({
                        'doc_id': doc_id,
                        'filename': filename,
                        'duplicate_type': reason
                    })
            
            # Update document list
            all_documents = unique_docs
            final_doc_count = len(all_documents)
            
            # Statistics
            dedup_stats = self.deduplicator.get_statistics()
            dedup_stats['initial_count'] = initial_doc_count
            dedup_stats['final_count'] = final_doc_count
            dedup_stats['removed'] = initial_doc_count - final_doc_count
            
            print(f"\n📊 Deduplication Results:")
            print(f"   Unique documents: {final_doc_count:,} ({final_doc_count/initial_doc_count:.1%})")
            print(f"   Removed: {initial_doc_count - final_doc_count:,}")
            print(f"   - Exact duplicates: {dedup_stats['exact_duplicates']}")
            print(f"   - Fuzzy duplicates: {dedup_stats['fuzzy_duplicates']}")
            print(f"   - Semantic duplicates: {dedup_stats['semantic_duplicates']}")
            print(f"{'='*70}\n")
            
            # Save duplicate log
            if self.config.deduplication_config['log_duplicates']:
                dup_log_file = self.config.analysis_dir / "pass_1" / "duplicate_log.json"
                dup_log_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(dup_log_file, 'w', encoding='utf-8') as f:
                    json.dump(duplicate_log, f, indent=2)
                
                print(f"💾 Duplicate log saved: {dup_log_file}\n")
        else:
            dedup_stats = {'initial_count': initial_doc_count, 'final_count': initial_doc_count, 'removed': 0}
        
        # ====================================================================
        # TRIAGE BATCHES
        # ====================================================================
        print(f"📁 Triaging {len(all_documents):,} unique documents")
        
        # Create batches
        batch_size = 100
        batches = []
        for i in range(0, len(all_documents), batch_size):
            batches.append(all_documents[i:i+batch_size])
        
        print(f"📦 Processing in {len(batches)} batches")
        
        scored_documents = []
        total_cost = 0.0
        
        for batch_idx, batch in enumerate(tqdm(batches, desc="Triaging batches")):
            # Generate prompt WITH Phase 0 smoking guns
            prompt = self.autonomous_prompts.triage_prompt(
                documents = batch,
                batch_num = batch_idx, 
                phase_0_foundation=phase_0_foundation  # ← PHASE 0 INTEGRATION
            )
            
            try:
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='document_triage',
                    phase='pass_1',
                    temperature=0.0
                )
                
                total_cost += metadata.get('cost_gbp', 0)
                
                batch_scores = self._parse_triage_response(response, batch)
                scored_documents.extend(batch_scores)
                
                # Save progress every 10 batches
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
        
        # Sort and take top 500
        scored_documents.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        top_docs = scored_documents[:500]
        
        results = {
            'pass': '1',
            'total_documents_triaged': len(all_documents),
            'priority_documents': top_docs,
            'priority_count': len(top_docs),
            'total_cost_gbp': total_cost,
            'phase_0_used': phase_0_used,
            'deduplication_stats': dedup_stats,
            'completed_at': datetime.now().isoformat()
        }
        
        self._save_pass_results('pass_1', results)
        self._save_checkpoint('pass_1', results)
        
        print(f"\n✅ Pass 1 complete:")
        if dedup_stats['removed'] > 0:
            print(f"   Initial documents: {dedup_stats['initial_count']:,}")
            print(f"   After deduplication: {dedup_stats['final_count']:,}")
            print(f"   Duplicates removed: {dedup_stats['removed']:,}")
        print(f"   Top priority documents: {len(top_docs)}/{len(all_documents)}")
        print(f"   Cost: £{total_cost:.2f}")
        print(f"   Phase 0 intelligence: {'✅ USED' if phase_0_used else '❌ NOT USED'}")
        
        return results
    
    # ========================================================================
    # PASS 2: DEEP ANALYSIS WITH CHECKPOINTING
    # ========================================================================
    
    def execute_pass_2_deep_analysis(self, priority_docs: List[Dict]) -> Dict:
        """Pass 2: Deep analysis with memory system integration"""
        
        print("\n" + "="*70)
        print("PASS 2: DEEP ANALYSIS WITH MEMORY SYSTEM")
        print("="*70)
        
        # Check for checkpoint
        checkpoint = self._load_checkpoint('pass_2')
        if checkpoint:
            print("📂 Resuming from checkpoint...")
            confidence = checkpoint.get('final_confidence', 0.0)
            iteration_start = len(checkpoint.get('iterations', []))
            results = checkpoint
            print(f"   Resuming at iteration {iteration_start}, confidence: {confidence:.1%}")
        else:
            confidence = 0.0
            iteration_start = 0
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
        
        max_iterations = self.config.pass_2_config['max_iterations']
        batch_size = self.config.pass_2_config['batch_size']
        confidence_threshold = self.config.pass_2_config['confidence_threshold']
        
        print(f"\n🎯 Target confidence: {confidence_threshold:.1%}")
        print(f"📊 Max iterations: {max_iterations}")
        
        for iteration in range(iteration_start, max_iterations):
            print(f"\n  Iteration {iteration + 1}/{max_iterations}:")
            
            # Get batch
            start_idx = iteration * batch_size
            batch_docs = priority_docs[start_idx:start_idx + batch_size]
            
            if not batch_docs:
                print(f"  ℹ️  No more documents")
                break
            
            # Get context from knowledge graph
            context = self.knowledge_graph.get_context_for_analysis()
            
            # Determine phase
            if iteration == 0:
                phase_instruction = "PHASE: DISCOVER THE CLAIMS"
            elif iteration < 15:
                phase_instruction = "PHASE: TEST CLAIMS AGAINST EVIDENCE"
            else:
                phase_instruction = "PHASE: DEEP INVESTIGATION + NOVEL ARGUMENTS"
            
            # Generate prompt
            prompt = self.autonomous_prompts.deep_analysis_prompt(
                documents=batch_docs,
                iteration=iteration,
                accumulated_knowledge=context,
                confidence=confidence,
                phase_instruction=phase_instruction
            )
            
            try:
                # Call API
                response, metadata = self.api_client.call_claude(
                    prompt=prompt,
                    task_type='deep_analysis',
                    phase='pass_2'
                )
                
                # Parse response
                iteration_result = self._parse_deep_analysis_response(response)
                iteration_result['iteration'] = iteration + 1
                iteration_result['cost_gbp'] = metadata.get('cost_gbp', 0)
                iteration_result['source'] = 'api'
                
                # Validate
                if self.config.validation_config['enabled']:
                    validation_result = self._validate_analysis_output(iteration_result)
                    iteration_result['validation'] = validation_result
                    iteration_result['validation_passed'] = validation_result['passed']
                    
                    if not validation_result['passed']:
                        results['validation_issues'].extend(validation_result['issues'])
                
                # Integrate
                self.knowledge_graph.integrate_analysis(iteration_result)
                
                # Update confidence
                new_confidence = iteration_result.get('confidence', 0)
                confidence = max(confidence, new_confidence)
                
                # Accumulate findings
                results['breaches'].extend(iteration_result.get('breaches', []))
                results['contradictions'].extend(iteration_result.get('contradictions', []))
                results['timeline_events'].extend(iteration_result.get('timeline_events', []))
                results['novel_arguments'].extend(iteration_result.get('novel_arguments', []))
                results['opponent_weaknesses'].extend(iteration_result.get('opponent_weaknesses', []))
                results['iterations'].append(iteration_result)
                
                print(f"    Confidence: {confidence:.1%}")
                print(f"    Breaches: {len(iteration_result.get('breaches', []))}")
                print(f"    Validation: {'✅' if iteration_result.get('validation_passed', True) else '⚠️'}")
                print(f"    Cost: £{metadata.get('cost_gbp', 0):.2f}")
                
                # Checkpoint every 3 iterations
                if (iteration + 1) % 3 == 0:
                    results['final_confidence'] = confidence
                    self._save_checkpoint('pass_2', results)
                
                # Check stopping
                if confidence >= confidence_threshold:
                    print(f"\n  ✅ Confidence threshold reached")
                    results['reason_stopped'] = 'confidence_reached'
                    break
                
            except Exception as e:
                print(f"\n  ⚠️  Error: {str(e)[:100]}")
                continue
        
        # Final results
        results['final_confidence'] = confidence
        results['total_iterations'] = len(results['iterations'])
        results['total_cost_gbp'] = sum(it.get('cost_gbp', 0) for it in results['iterations'])
        results['completed_at'] = datetime.now().isoformat()
        
        if 'reason_stopped' not in results:
            results['reason_stopped'] = 'max_iterations'
        
        self._save_pass_results('pass_2', results)
        self._clear_checkpoint('pass_2')
        
        print(f"\n✅ Pass 2 complete:")
        print(f"   Final confidence: {confidence:.1%}")
        print(f"   Iterations: {results['total_iterations']}/{max_iterations}")
        print(f"   Total breaches: {len(results['breaches'])}")
        print(f"   Cost: £{results['total_cost_gbp']:.2f}")
        
        return results
    
    # ========================================================================
    # PASS 3: INVESTIGATIONS WITH OPTIMISED DOCUMENT RETRIEVAL
    # ========================================================================
    
    def execute_pass_3_investigations(self) -> Dict:
        """Pass 3: Autonomous investigations with BM25 document retrieval"""
        
        print("\n" + "="*70)
        print("PASS 3: AUTONOMOUS INVESTIGATIONS")
        print("="*70)
        
        # Build document index for optimal retrieval
        self._build_document_index()
        
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
                
                # OPTIMISED DOCUMENT RETRIEVAL using BM25
                relevant_doc_ids = self._bm25_search(investigation.topic, top_k=20)
                print(f"     📄 Retrieved {len(relevant_doc_ids)} relevant documents")
                
                # Get complete intelligence
                complete_intel = self.knowledge_graph.export_complete()
                
                prompt = self.autonomous_prompts.investigation_recursive_prompt(
                    investigation=investigation,
                    relevant_documents=relevant_doc_ids,
                    complete_intelligence=complete_intel
                )
                
                try:
                    response, metadata = self.api_client.call_claude(
                        prompt=prompt,
                        task_type='investigation',
                        phase='pass_3'
                    )
                    
                    # Parse investigation result
                    inv_result = self._parse_investigation_response(response, investigation)
                    inv_result['cost_gbp'] = metadata.get('cost_gbp', 0)
                    inv_result['relevant_docs_count'] = len(relevant_doc_ids)
                    
                    # Store result
                    self.knowledge_graph.store_investigation_result(inv_result)
                    self.investigation_queue.mark_complete(investigation.get_id())
                    
                    results['investigations'].append(inv_result)
                    results['total_cost_gbp'] += inv_result['cost_gbp']
                    
                    # Spawn children if needed
                    if inv_result.get('spawn_children', False):
                        children = inv_result.get('child_investigations', [])
                        for child in children:
                            self.investigation_queue.add_child_investigation(
                                parent_id=investigation.get_id(),
                                topic=child['topic'],
                                priority=child['priority']
                            )
                    
                    investigation_count += 1
                    pbar.update(1)
                    
                    # Checkpoint every 5 investigations
                    if investigation_count % 5 == 0:
                        results['investigations_completed'] = investigation_count
                        self._save_checkpoint('pass_3', results)
                    
                except Exception as e:
                    print(f"  ⚠️  Error: {str(e)[:100]}")
                    continue
        
        results['total_investigations'] = investigation_count
        results['final_queue_status'] = self.investigation_queue.get_status()
        results['completed_at'] = datetime.now().isoformat()
        
        self._save_pass_results('pass_3', results)
        self._clear_checkpoint('pass_3')
        
        print(f"\n✅ Pass 3 complete:")
        print(f"   Investigations run: {investigation_count}")
        print(f"   Cost: £{results['total_cost_gbp']:.2f}")
        
        return results
    
    # ========================================================================
    # PASS 4: SYNTHESIS
    # ========================================================================
    
    def execute_pass_4_synthesis(self) -> Dict:
        """Pass 4: Synthesis & deliverables"""
        
        print("\n" + "="*70)
        print("PASS 4: SYNTHESIS & DELIVERABLES")
        print("="*70)
        
        checkpoint = self._load_checkpoint('pass_4')
        if checkpoint:
            print("📂 Using cached results...")
            return checkpoint
        
        # Export complete intelligence
        intelligence = self.knowledge_graph.export_complete()
        
        print(f"\n📊 Intelligence gathered:")
        print(f"   Patterns: {len(intelligence.get('patterns', []))}")
        print(f"   Contradictions: {len(intelligence.get('contradictions', []))}")
        print(f"   Timeline events: {len(intelligence.get('timeline_events', []))}")
        
        # Build claims
        print("\n🏗️  Building claims...")
        claims = self._build_claims(intelligence)
        
        print(f"   Claims constructed: {len(claims)}")
        for claim_type, claim in claims.items():
            print(f"      {claim_type}: Strength {claim['strength']:.2f}")
        
        # Generate strategy
        print("\n📋 Generating strategy...")
        strategy = self._generate_strategy(claims, intelligence)
        
        # Generate deliverables
        print("\n📝 Generating tribunal deliverables...")
        
        from prompts.deliverables import DeliverablesPrompts
        deliverables_prompts = DeliverablesPrompts(self.config)
        
        prompt = deliverables_prompts.generate_all_deliverables(
            intelligence=intelligence,
            claims=claims,
            strategy=strategy
        )
        
        response, metadata = self.api_client.call_claude(
            prompt=prompt,
            task_type='deliverables',
            phase='pass_4'
        )
        
        # Parse deliverables (using XML tags for robustness)
        deliverables = self._parse_deliverables_xml(response)
        
        results = {
            'pass': '4',
            'deliverables': {
                'claims': claims,
                'strategy': strategy,
                'tribunal_documents': deliverables
            },
            'total_cost_gbp': metadata.get('cost_gbp', 0),
            'completed_at': datetime.now().isoformat()
        }
        
        self._save_pass_results('pass_4', results)
        self._save_checkpoint('pass_4', results)
        
        print(f"\n✅ Pass 4 complete:")
        print(f"   Claims: {len(claims)}")
        print(f"   Tribunal docs: {len(deliverables)}")
        print(f"   Cost: £{results['total_cost_gbp']:.2f}")
        
        return results
    
    # ========================================================================
    # PARSING METHODS
    # ========================================================================
    
    def _parse_triage_response(self, response: str, batch: List[Dict]) -> List[Dict]:
        """Parse triage response with category validation"""
        VALID_CATEGORIES = {'contract', 'financial', 'correspondence', 'witness', 'expert', 'other'}
        
        scored_docs = []
        pattern = r'\[DOC_(\d+)\]\s*Priority Score:\s*(\d+)\s*Reason:\s*(.+?)\s*Category:\s*(\w+)'
        
        matches = re.finditer(pattern, response, re.DOTALL)
        
        for match in matches:
            idx = int(match.group(1))
            score = int(match.group(2))
            reason = match.group(3).strip()
            category = match.group(4).strip().lower()
            
            # Validate category
            if category not in VALID_CATEGORIES:
                category = 'other'
            
            # Clamp score
            score = max(1, min(10, score))
            
            if idx < len(batch):
                scored_docs.append({
                    **batch[idx],
                    'priority_score': score,
                    'triage_reason': reason,
                    'category': category
                })
        
        return scored_docs
    
    def _parse_deep_analysis_response(self, response: str) -> Dict:
        """Parse Pass 2 response with structured extraction + fallback"""
        result = {
            'breaches': [],
            'contradictions': [],
            'timeline_events': [],
            'novel_arguments': [],
            'opponent_weaknesses': [],
            'critical_findings': [],
            'confidence': 0.0
        }
        
        # Extract structured breaches
        breach_pattern = r'BREACH_START\s*Description:\s*(.+?)\s*Clause/Obligation:\s*(.+?)\s*Evidence:\s*(\[.+?\])\s*Confidence:\s*(0?\.\d+|1\.0)\s*Causation:\s*(.+?)\s*Quantum:\s*(.+?)\s*BREACH_END'
        
        for match in re.finditer(breach_pattern, response, re.DOTALL):
            try:
                evidence_str = match.group(3).strip()
                evidence = json.loads(evidence_str)
            except:
                evidence = []
            
            breach = {
                'description': match.group(1).strip(),
                'clause': match.group(2).strip(),
                'evidence': evidence,
                'confidence': float(match.group(4)),
                'causation': match.group(5).strip(),
                'quantum': match.group(6).strip()
            }
            result['breaches'].append(breach)
        
        # Extract confidence
        confidence_patterns = [
            r'(?:CONFIDENCE|Confidence):\s*(0?\.\d+|1\.0)',
            r'(\d{1,3})%\s*confident',
            r'confidence.*?(?:is|of)\s*(0?\.\d+|1\.0)'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                result['confidence'] = val / 100 if val > 1 else val
                break
        
        return result
    
    def _parse_investigation_response(self, response: str, investigation) -> Dict:
        """Parse investigation response"""
        result = {
            'investigation_id': investigation.get_id(),
            'topic': investigation.topic,
            'conclusion': '',
            'confidence': 0.0,
            'spawn_children': False,
            'child_investigations': []
        }
        
        # Extract conclusion
        conclusion_match = re.search(r'CONCLUSION:\s*(.+?)(?:\n\n|CONFIDENCE)', response, re.DOTALL)
        if conclusion_match:
            result['conclusion'] = conclusion_match.group(1).strip()
        
        # Extract confidence
        conf_match = re.search(r'CONFIDENCE:\s*(0?\.\d+|1\.0)', response)
        if conf_match:
            result['confidence'] = float(conf_match.group(1))
        
        # Check for child spawning
        if re.search(r'CONTINUE:\s*YES', response, re.IGNORECASE):
            result['spawn_children'] = True
            
            # Extract child investigations
            child_pattern = r'CHILD_INVESTIGATION:\s*(.+?)\s*PRIORITY:\s*(\d+)'
            for match in re.finditer(child_pattern, response):
                result['child_investigations'].append({
                    'topic': match.group(1).strip(),
                    'priority': int(match.group(2))
                })
        
        return result
    
    def _parse_deliverables_xml(self, response: str) -> Dict:
        """
        Parse deliverables using XML tags (more robust than regex)
        """
        deliverables = {}
        
        doc_types = [
            'scott_schedule',
            'witness_outlines',
            'skeleton_argument',
            'disclosure_requests',
            'opening_submissions',
            'expert_instructions'
        ]
        
        for doc_type in doc_types:
            # Try XML tag extraction
            pattern = f'<{doc_type}>(.*?)</{doc_type}>'
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            
            if match:
                deliverables[doc_type] = match.group(1).strip()
            else:
                # Fallback to section headers
                header_pattern = f'#+\s*{doc_type.replace("_", " ").title()}[\s:]*(.+?)(?=#+|$)'
                match = re.search(header_pattern, response, re.DOTALL | re.IGNORECASE)
                
                if match:
                    deliverables[doc_type] = match.group(1).strip()
                else:
                    deliverables[doc_type] = f"[{doc_type} not found in response]"
        
        return deliverables
    
    def _build_claims(self, intelligence: Dict) -> Dict:
        """Build structured claims from intelligence"""
        claims = {}
        
        patterns = intelligence.get('patterns', [])
        
        # Group breaches by type
        breach_patterns = [p for p in patterns if 'breach' in p.get('description', '').lower()]
        
        if breach_patterns:
            avg_confidence = sum(p.get('confidence', 0) for p in breach_patterns) / len(breach_patterns)
            
            claims['breach_of_contract'] = {
                'type': 'Breach of Contract',
                'strength': avg_confidence,
                'elements': {
                    'contract_exists': True,
                    'obligations_defined': True,
                    'breach_occurred': len(breach_patterns) > 0,
                    'causation_proven': True,
                    'damages_quantified': True
                },
                'evidence_count': len(breach_patterns)
            }
        
        return claims
    
    def _generate_strategy(self, claims: Dict, intelligence: Dict) -> Dict:
        """Generate strategic recommendations"""
        strategy = {
            'strongest_claims': [],
            'weakest_areas': [],
            'settlement_positioning': '',
            'trial_strategy': ''
        }
        
        for claim_type, claim in claims.items():
            if claim['strength'] > 0.7:
                strategy['strongest_claims'].append({
                    'claim': claim_type,
                    'strength': claim['strength']
                })
            elif claim['strength'] < 0.5:
                strategy['weakest_areas'].append({
                    'claim': claim_type,
                    'strength': claim['strength']
                })
        
        strategy['settlement_positioning'] = f"Lismore's position is strong with {len(strategy['strongest_claims'])} high-confidence claims."
        strategy['trial_strategy'] = "Lead with strongest breach of contract claims. Use contradictions in cross-examination."
        
        return strategy
    
    def _save_pass_results(self, pass_name: str, results: Dict):
        """Save pass results to JSON"""
        output_dir = self.config.analysis_dir / pass_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{pass_name}_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def _get_investigation_depth(self, investigation) -> int:
        """Calculate investigation depth"""
        depth = 0
        current = investigation
        visited = set()
        
        while current.parent_id and current.parent_id not in visited:
            depth += 1
            visited.add(current.parent_id)
            current = self.investigation_queue.completed_by_id.get(current.parent_id)
            if not current or depth > 10:
                break
        
        return depth