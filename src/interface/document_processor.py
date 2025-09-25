#!/usr/bin/env python3
"""
Complete Document Processor for Lismore vs Process Holdings
Handles ALL phases (0A, 0B, 1-7) with maximum intelligence extraction
"""

import json
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# Use relative imports when running as module
try:
    from ..core.api_client import ClaudeAPIClient
    from ..prompts.phase_prompts import get_phase_prompt, get_phase_prompt_enhanced
    from ..knowledge.knowledge_manage import KnowledgeManager  
    from ..selectors.document_selector import DocumentSelector
    from ..core.utils import load_documents, validate_documents
except ImportError:
    # Fallback to absolute imports
    from core.api_client import ClaudeAPIClient
    from prompts.phase_prompts import get_phase_prompt, get_phase_prompt_enhanced
    from knowledge.knowledge_manage import KnowledgeManager
    from selectors.document_selector import DocumentSelector
    from core.utils import load_documents, validate_documents


class DocumentProcessor:
    """Complete document processor for all phases with maximum intelligence"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise document processor"""
        self.api_client = ClaudeAPIClient(api_key=api_key)
        self.knowledge_manage = KnowledgeManager()
        self.document_registry = self._load_all_documents()
        self.document_selector = DocumentSelector(self.document_registry)
        
        # Phase configuration
        self.PHASE_DIRECTORIES = {
            "0A": "legal_resources",     # Legal framework
            "0B": "case_context",        # Case background
            "1": "documents",            # Phases 1-7 use main documents
            "2": "documents",
            "3": "documents",
            "4": "documents",
            "5": "documents",
            "6": "documents",
            "7": "documents"
        }
        
        self.current_phase = None
        
    def _load_all_documents(self) -> Dict:
        """Load all documents from all directories"""
        registry = {}
        doc_id = 0
        
        # Load from all possible directories
        for dir_name in ["legal_resources", "case_context", "documents"]:
            path = Path(dir_name)
            if not path.exists():
                continue
            
            # Handle different subdirectory structures
            if dir_name == "legal_resources":
                # Load rule cards
                rule_cards_dir = path / "rule_cards"
                if rule_cards_dir.exists():
                    for json_file in rule_cards_dir.glob("*.json"):
                        doc_id += 1
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                content = json.load(f)
                                registry[f"DOC_{doc_id:04d}"] = {
                                    'content': json.dumps(content, indent=2),
                                    'filepath': str(json_file),
                                    'filename': json_file.name,
                                    'doc_id': f"DOC_{doc_id:04d}",
                                    'source_dir': str(rule_cards_dir)
                                }
                        except Exception as e:
                            print(f"⚠️ Error loading {json_file}: {e}")
                
                # Load processed texts
                text_dir = path / "processed" / "text"
                if text_dir.exists():
                    for txt_file in text_dir.glob("*.txt"):
                        doc_id += 1
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content.strip():
                                    registry[f"DOC_{doc_id:04d}"] = {
                                        'content': content,
                                        'filepath': str(txt_file),
                                        'filename': txt_file.name,
                                        'doc_id': f"DOC_{doc_id:04d}",
                                        'source_dir': str(text_dir)
                                    }
                        except Exception as e:
                            print(f"⚠️ Error loading {txt_file}: {e}")
            
            elif dir_name == "documents":
                # Load processed documents
                processed_dir = path / "processed" / "text"
                if processed_dir.exists():
                    for txt_file in processed_dir.glob("*.txt"):
                        doc_id += 1
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content.strip():
                                    registry[f"DOC_{doc_id:04d}"] = {
                                        'content': content,
                                        'filepath': str(txt_file),
                                        'filename': txt_file.name,
                                        'doc_id': f"DOC_{doc_id:04d}",
                                        'source_dir': str(processed_dir)
                                    }
                        except Exception as e:
                            print(f"⚠️ Error loading {txt_file}: {e}")
            
            else:
                # Load any documents from case_context
                docs = load_documents(str(path))
                for doc in docs:
                    doc_id += 1
                    doc['doc_id'] = f"DOC_{doc_id:04d}"
                    doc['source_dir'] = str(path)
                    registry[doc['doc_id']] = doc
        
        print(f"📚 Total documents in registry: {len(registry)}")
        return registry
    
    def process_phase(self, phase_num: str) -> Dict:
        """Process any phase (0A, 0B, 1-7)"""
        print(f"\n{'='*60}")
        print(f"🎯 PHASE {phase_num}: PROCESSING")
        print(f"{'='*60}")
        
        self.current_phase = phase_num
        relevant_docs = []
        
        # Phase-specific document selection
        if phase_num == "0A":
            # Load ALL legal resources
            print("📚 Loading COMPLETE legal framework...")
            relevant_docs = [doc for doc in self.document_registry.values() 
                           if 'legal_resources' in doc.get('source_dir', '')]
            
            # Count document types
            rule_count = sum(1 for d in relevant_docs if 'rule_cards' in d.get('source_dir', ''))
            text_count = sum(1 for d in relevant_docs if 'processed/text' in d.get('source_dir', ''))
            
            print(f"📎 Loaded {len(relevant_docs)} total legal documents:")
            if rule_count > 0:
                print(f"   • {rule_count} weaponised rule cards")
            if text_count > 0:
                print(f"   • {text_count} treatise extracts")
            
        elif phase_num == "0B":
            # Load case context documents
            print("📚 Loading case context...")
            relevant_docs = [doc for doc in self.document_registry.values()
                           if 'case_context' in doc.get('source_dir', '')]
            print(f"📎 Loaded {len(relevant_docs)} case context documents")
            
        else:
            # Phases 1-7: Use document selector on main documents
            print(f"📚 Selecting documents for Phase {phase_num}...")
            main_docs = [doc for doc in self.document_registry.values()
                        if 'documents' in doc.get('source_dir', '')]
            
            if self.document_selector and main_docs:
                relevant_docs = self.document_selector.select_for_phase(
                    phase=phase_num,
                    phase_data=self.knowledge_manage.get_previous_knowledge(phase_num),
                    max_docs=50
                )
            else:
                # Fallback: take first 50 documents
                relevant_docs = main_docs[:50]
            
            print(f"📎 Selected {len(relevant_docs)} documents for Phase {phase_num}")
        
        if not relevant_docs:
            print(f"⚠️ No relevant documents for Phase {phase_num}")
            return {}
        
        # Build context
        context = self._build_comprehensive_context(phase_num)
        
        # Execute analysis
        results = self._execute_single_comprehensive_analysis(
            phase_num, 
            relevant_docs, 
            context
        )
        
        # Store knowledge
        if results:
            self.knowledge_manage.store_phase_knowledge(phase_num, results)
            self._update_knowledge_graph(phase_num, results)
            print(f"✅ Phase {phase_num} complete - knowledge stored")
        
        return results
    
    def _build_comprehensive_context(self, phase: str) -> Dict:
        """Build context with all required keys initialised"""
        context = {
            'phase': phase,
            'previous_phases': [],
            'knowledge_graph': {},
            'accumulated_patterns': {},
            'contradictions': {},
            'legal_weapons': {},
            'strategic_priorities': self._get_strategic_priorities(phase)
        }
        
        # Safely get previous phases
        try:
            if hasattr(self.knowledge_manage, 'get_completed_phases'):
                context['previous_phases'] = self.knowledge_manage.get_completed_phases()
        except:
            pass
        
        # Safely get knowledge graph
        try:
            if hasattr(self.knowledge_manage, 'knowledge_graph'):
                kg = self.knowledge_manage.knowledge_graph
                if isinstance(kg, dict):
                    context['knowledge_graph'] = kg
                    context['contradictions'] = kg.get('contradictions', {})
                    context['legal_weapons'] = kg.get('legal_weapons', {})
                    context['accumulated_patterns'] = kg.get('patterns', {})
        except:
            pass
        
        return context
    
    def _execute_single_comprehensive_analysis(self, phase: str, docs: List[Dict], context: Dict) -> Dict:
        """Execute analysis - batch if needed"""
        
        # For large document sets, batch them
        if len(docs) > 100:
            print(f"📦 Processing {len(docs)} documents in batches...")
            return self._execute_batched_analysis(phase, docs, context)
        else:
            # Single call for smaller sets
            return self._execute_single_call_analysis(phase, docs, context)
    
    def _execute_single_call_analysis(self, phase: str, docs: List[Dict], context: Dict) -> Dict:
        """Execute single API call for analysis"""
        
        # Build prompt
        master_prompt = self._build_comprehensive_phase_prompt(phase, context)
        
        # Prepare documents
        doc_contents = []
        for doc in docs[:50]:  # Safety limit
            doc_contents.append({
                'content': doc.get('content', ''),
                'metadata': {
                    'doc_id': doc.get('doc_id'),
                    'source': doc.get('source_dir', ''),
                    'filename': doc.get('filename', '')
                }
            })
        
        print(f"📡 Sending {len(doc_contents)} documents to Claude...")
        
        # Make API call
        response = self.api_client.analyse_documents_batch(
            documents=doc_contents,
            prompt=master_prompt,
            phase=f"phase_{phase}"
        )
        
        # Parse response
        results = self._parse_comprehensive_response(response, phase)
        results['documents_analysed'] = len(doc_contents)
        
        return results
    
    def _execute_batched_analysis(self, phase: str, docs: List[Dict], context: Dict) -> Dict:
        """Process large document sets in batches"""
        batch_size = 50
        all_results = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'combined_analysis': [],
            'documents_analysed': 0
        }
        
        total_batches = (len(docs) - 1) // batch_size + 1
        print(f"📦 Processing {len(docs)} documents in {total_batches} batches...")
        
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} docs)...")
            
            # Build prompt for this batch
            master_prompt = self._build_comprehensive_phase_prompt(phase, context)
            
            # Prepare batch documents
            doc_contents = []
            for doc in batch:
                doc_contents.append({
                    'content': doc.get('content', ''),
                    'metadata': {'doc_id': doc.get('doc_id')}
                })
            
            # Make API call
            response = self.api_client.analyse_documents_batch(
                documents=doc_contents,
                prompt=master_prompt,
                phase=f"phase_{phase}_batch_{batch_num-1}"
            )
            
            # Accumulate results
            all_results['combined_analysis'].append(response)
            all_results['documents_analysed'] += len(batch)
            
            # Update context with findings for next batch
            if response:
                batch_findings = self._parse_comprehensive_response(response, phase)
                self._update_context_with_findings(context, batch_findings)
            
            # Brief pause between batches
            if i + batch_size < len(docs):
                time.sleep(2)
        
        # Synthesise all batch results
        if len(all_results['combined_analysis']) > 1:
            all_results['synthesis'] = self._synthesise_batch_results(
                all_results['combined_analysis'], 
                phase
            )
        else:
            all_results['synthesis'] = all_results['combined_analysis'][0] if all_results['combined_analysis'] else ""
        
        return all_results
    
    def _update_context_with_findings(self, context: Dict, findings: Dict):
        """Update context with findings - FIXED VERSION"""
        if not findings:
            return
        
        if not isinstance(findings, dict):
            findings = {'analysis': str(findings)}
        
        # Define patterns BEFORE using it
        patterns = findings.get('patterns', {})
        
        # Now safely check and process patterns
        if patterns:
            if isinstance(patterns, dict):
                if 'accumulated_patterns' not in context:
                    context['accumulated_patterns'] = {}
                context['accumulated_patterns'].update(patterns)
            elif isinstance(patterns, list):
                if 'accumulated_patterns' not in context:
                    context['accumulated_patterns'] = {}
                for i, pattern in enumerate(patterns):
                    context['accumulated_patterns'][f'pattern_{i}'] = pattern
        
        # Process contradictions
        contradictions = findings.get('contradictions', {})
        if isinstance(contradictions, dict) and contradictions:
            if 'contradictions' not in context:
                context['contradictions'] = {}
            context['contradictions'].update(contradictions)
        
        # Process legal_weapons
        weapons = findings.get('legal_weapons', {})
        if isinstance(weapons, dict) and weapons:
            if 'legal_weapons' not in context:
                context['legal_weapons'] = {}
            context['legal_weapons'].update(weapons)
    
    def _synthesise_batch_results(self, batch_responses: List[str], phase: str) -> str:
        """Synthesise multiple batch responses"""
        if not batch_responses:
            return ""
        
        if len(batch_responses) == 1:
            return batch_responses[0]
        
        synthesis_prompt = f"""
Synthesise these {len(batch_responses)} batch analyses from Phase {phase} into unified findings.

For Lismore vs Process Holdings, identify:
1. The most devastating legal weapons found
2. Critical patterns across all batches
3. Key contradictions and impossibilities
4. Strategic opportunities for victory

BATCH RESULTS:
{"="*40}
"""
        for i, response in enumerate(batch_responses, 1):
            # Include first 2000 chars of each batch
            synthesis_prompt += f"\nBATCH {i}:\n{response[:2000]}\n{'='*40}"
        
        synthesis_prompt += "\n\nProvide unified synthesis focusing on what destroys Process Holdings."
        
        # Make synthesis call
        synthesis = self.api_client.analyse_documents_batch(
            documents=[],
            prompt=synthesis_prompt,
            phase=f"phase_{phase}_synthesis"
        )
        
        return synthesis
    
    def _build_comprehensive_phase_prompt(self, phase: str, context: Dict) -> str:
        """Build phase-specific prompts"""
        
        # Get base prompt from phase_prompts module
        base_prompt = get_phase_prompt(phase) if not context['previous_phases'] else get_phase_prompt_enhanced(phase, context)
        
        # Phase-specific enhancements
        if phase == "0A":
            return """
PHASE 0A: PURE LEGAL KNOWLEDGE EXTRACTION AND MEMORY BUILDING

You are building a comprehensive legal knowledge base from these documents.
This is NOT about any specific case - this is about learning and memorising legal principles.

EXTRACTION OBJECTIVES:

1. LEGAL DOCTRINES
   - Extract every legal principle mentioned
   - Note the full doctrine name and elements
   - Understand when and how each applies
   - Store exceptions and limitations

2. CASE PRECEDENTS
   - Identify all case citations
   - Extract the legal principle from each case
   - Note the ratio decidendi (binding element)
   - Remember distinguishing factors

3. PROCEDURAL RULES
   - Extract all procedural requirements
   - Time limits and deadlines
   - Notice requirements
   - Filing procedures
   - Jurisdictional rules

4. STATUTORY PROVISIONS
   - All legislation references
   - Specific section numbers
   - Elements of statutory claims
   - Defences available

5. LEGAL CONCEPTS
   - Burden of proof variations
   - Standards of evidence
   - Presumptions and inferences
   - Equitable principles

MEMORY FORMATION INSTRUCTIONS:
- Create a structured mental map of all legal concepts
- Build connections between related doctrines
- Form hierarchies of principles (general → specific)
- Identify doctrine families and variations
- Remember practical applications

OUTPUT STRUCTURE:
Provide a comprehensive synthesis of ALL legal knowledge found, organised by:
- Doctrine categories
- Procedural frameworks  
- Statutory schemes
- Case law principles
- Strategic applications

This is pure knowledge building - no case analysis, just legal learning.
"""
        
        elif phase == "0B":
            return f"""
{base_prompt}

UNDERSTAND THE COMPLETE CASE CONTEXT:
1. Key actors and their roles
2. Timeline of events
3. Business relationships
4. Financial flows
5. Communication patterns

Identify vulnerabilities in Process Holdings' position.
"""
        
        elif phase in ["1", "2", "3", "4", "5", "6", "7"]:
            weapons_count = len(context.get('legal_weapons', {}).get('nuclear', []))
            return f"""
{base_prompt}

CONTEXT FROM PREVIOUS PHASES:
- Legal Weapons Available: {weapons_count} nuclear options
- Previous Phases Completed: {context.get('previous_phases', [])}
- Patterns Identified: {len(context.get('accumulated_patterns', {}))}

Apply all accumulated intelligence to maximise damage to Process Holdings.
Reference document IDs as [DOC_XXXX] for all findings.
"""
        
        return base_prompt
    
    def _parse_comprehensive_response(self, response: str, phase: str) -> Dict:
        """Parse response - always returns valid dict"""
        if not response:
            return {'analysis': 'No response received', 'patterns': {}, 'findings': []}
        
        if isinstance(response, dict):
            return response
        
        # Try to extract JSON if present
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', str(response))
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, dict):
                    return parsed
        except:
            pass
        
        # Return structured dict from text response
        return {
            'analysis': str(response),
            'synthesis': str(response),
            'patterns': {},
            'findings': [],
            'weapons': [],
            'contradictions': {},
            'legal_weapons': {}
        }
    
    def _get_strategic_priorities(self, phase: str) -> List[str]:
        """Get strategic priorities for each phase"""
        priorities_map = {
            '0A': ['extract_all_weapons', 'build_doctrine_matrix', 'identify_combinations'],
            '0B': ['understand_case_context', 'identify_key_actors', 'map_relationships'],
            '1': ['find_hot_documents', 'classify_evidence', 'identify_gaps'],
            '2': ['build_timeline', 'find_impossibilities', 'identify_temporal_gaps'],
            '3': ['find_contradictions', 'identify_lies', 'destroy_credibility'],
            '4': ['construct_narrative', 'build_themes', 'create_winning_story'],
            '5': ['identify_crimes', 'find_fraud', 'prepare_criminal_referral'],
            '6': ['procedural_knockouts', 'technical_wins', 'jurisdiction_challenges'],
            '7': ['deploy_nuclear_options', 'maximum_damage', 'total_victory']
        }
        return priorities_map.get(phase, ['maximise_damage', 'find_weaknesses', 'build_case'])
    
    def _update_knowledge_graph(self, phase: str, results: Dict):
        """Update knowledge graph safely"""
        try:
            if not hasattr(self.knowledge_manage, 'knowledge_graph'):
                self.knowledge_manage.knowledge_graph = {}
            
            if not isinstance(self.knowledge_manage.knowledge_graph, dict):
                self.knowledge_manage.knowledge_graph = {}
            
            # Store phase results
            self.knowledge_manage.knowledge_graph[f'phase_{phase}'] = {
                'timestamp': datetime.now().isoformat(),
                'results': results.get('synthesis', results.get('analysis', '')),
                'documents_analysed': results.get('documents_analysed', 0)
            }
            
            # Extract and store patterns
            if 'patterns' in results and isinstance(results['patterns'], dict):
                if 'patterns' not in self.knowledge_manage.knowledge_graph:
                    self.knowledge_manage.knowledge_graph['patterns'] = {}
                self.knowledge_manage.knowledge_graph['patterns'].update(results['patterns'])
            
            # Extract and store weapons
            if 'legal_weapons' in results and isinstance(results['legal_weapons'], dict):
                if 'legal_weapons' not in self.knowledge_manage.knowledge_graph:
                    self.knowledge_manage.knowledge_graph['legal_weapons'] = {}
                self.knowledge_manage.knowledge_graph['legal_weapons'].update(results['legal_weapons'])
                
        except Exception as e:
            print(f"⚠️ Knowledge graph update failed: {e}")
    
    def generate_war_room_dashboard(self) -> str:
        """Generate strategic dashboard"""
        kg = getattr(self.knowledge_manage, 'knowledge_graph', {})
        
        completed = self.knowledge_manage.get_completed_phases() if hasattr(self.knowledge_manage, 'get_completed_phases') else []
        
        dashboard = f"""
╔════════════════════════════════════════════════════════════╗
║           LISMORE vs PROCESS HOLDINGS                     ║
║              WAR ROOM DASHBOARD                           ║
╚════════════════════════════════════════════════════════════╝

🎯 PHASES COMPLETED: {len(completed)}/9
📊 DOCUMENTS ANALYSED: {sum(kg.get(f'phase_{p}', {}).get('documents_analysed', 0) for p in completed)}
💰 ESTIMATED DAMAGES: £127.5M

INTELLIGENCE SUMMARY:
• Nuclear Weapons: {len(kg.get('legal_weapons', {}).get('nuclear', []))}
• Contradictions Found: {len(kg.get('contradictions', {}))}
• Attack Patterns: {len(kg.get('patterns', {}))}

STATUS: {'READY FOR BATTLE' if len(completed) >= 7 else 'GATHERING INTELLIGENCE'}
"""
        return dashboard