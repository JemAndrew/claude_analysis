#!/usr/bin/env python3
"""
Document Processor with Complete Legal Resource Loading
Processes ALL documents in legal_resources for maximum knowledge transfer
"""

import json
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

from ..core.api_client import ClaudeAPIClient
from ..prompts.phase_prompts import get_phase_prompt, get_phase_prompt_enhanced
from ..knowledge.knowledge_manage import KnowledgeManager  
from ..selectors.document_selector import DocumentSelector
from ..core.utils import load_documents, validate_documents


class DocumentProcessor:
    """Document processor that loads ALL legal resources for complete knowledge"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise document processor"""
        self.api_client = ClaudeAPIClient(api_key=api_key)
        self.knowledge_manage = KnowledgeManager()
        self.document_registry = self._load_all_documents()
        self.document_selector = DocumentSelector(self.document_registry)
        
        # Three-directory structure
        self.PHASE_DIRECTORIES = {
            "0A": "legal_resources",           
            "0B": "case_context",              
            "1": "documents",   
            "2": "documents",   
            "3": "documents",   
            "4": "documents",   
            "5": "documents",   
            "6": "documents",   
            "7": "documents"    
        }
        
        self.disclosure_cache = None
        self.current_phase = None
        
    def _load_all_documents(self) -> Dict:
        """Load all documents ONCE into registry"""
        registry = {}
        doc_id = 0
        
        # Load from all directories
        directories = [
            "legal_resources/processed/text",
            "legal_resources/rule_cards",
            "legal_resources/playbooks",
            "case_context/raw",
            "documents/raw",
            "documents/processed/text"
        ]
        
        for dir_path in directories:
            path = Path(dir_path)
            if path.exists():
                # Handle different file types
                if "rule_cards" in dir_path:
                    # Load JSON rule cards
                    for json_file in path.glob("*.json"):
                        doc_id += 1
                        with open(json_file, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            registry[f"DOC_{doc_id:04d}"] = {
                                'content': f"[RULE CARD - {json_file.stem}]\n" + json.dumps(content, indent=2),
                                'filepath': str(json_file),
                                'filename': json_file.name,
                                'doc_id': f"DOC_{doc_id:04d}",
                                'source_dir': dir_path
                            }
                    print(f"📁 Loaded {len(list(path.glob('*.json')))} rule cards from {dir_path}")
                    
                elif "playbooks" in dir_path:
                    # Load playbook files
                    for playbook_file in path.glob("*"):
                        if playbook_file.is_file():
                            doc_id += 1
                            with open(playbook_file, 'r', encoding='utf-8') as f:
                                registry[f"DOC_{doc_id:04d}"] = {
                                    'content': f"[PLAYBOOK - {playbook_file.stem}]\n" + f.read(),
                                    'filepath': str(playbook_file),
                                    'filename': playbook_file.name,
                                    'doc_id': f"DOC_{doc_id:04d}",
                                    'source_dir': dir_path
                                }
                    print(f"📁 Loaded playbooks from {dir_path}")
                    
                else:
                    # Load regular documents (PDFs/text)
                    docs = load_documents(str(path))
                    for doc in docs:
                        doc_id += 1
                        doc['doc_id'] = f"DOC_{doc_id:04d}"
                        doc['source_dir'] = dir_path
                        registry[doc['doc_id']] = doc
                    print(f"📁 Loaded {len(docs)} documents from {dir_path}")
        
        print(f"📚 Total documents in registry: {len(registry)}")
        return registry
    
    def process_phase(self, phase_num: str) -> Dict:
        """Process phase with maximum optimisation"""
        print(f"\n{'='*60}")
        print(f"🎯 PHASE {phase_num}: PROCESSING")
        print(f"{'='*60}")
        
        self.current_phase = phase_num
        
        # Phase 0A: Load ALL legal resources for complete knowledge
        if phase_num == "0A":
            print("📚 Loading COMPLETE legal framework for maximum knowledge...")
            relevant_docs = []
            
            # Get ALL documents from legal_resources (everything!)
            for doc_id, doc in self.document_registry.items():
                if 'legal_resources' in doc.get('source_dir', ''):
                    relevant_docs.append(doc)
            
            # Count by type
            rule_cards = sum(1 for d in relevant_docs if 'RULE CARD' in d.get('content', '')[:50])
            playbooks = sum(1 for d in relevant_docs if 'PLAYBOOK' in d.get('content', '')[:50])
            treatises = len(relevant_docs) - rule_cards - playbooks
            
            print(f"📎 Loaded {len(relevant_docs)} total legal documents:")
            print(f"   • {rule_cards} weaponised rule cards")
            print(f"   • {treatises} treatise extracts") 
            print(f"   • {playbooks} strategic playbooks")
            
        elif phase_num == "0B":
            # Phase 0B: Case context documents
            case_docs = [doc for doc in self.document_registry.values() 
                        if 'case_context' in doc.get('source_dir', '')]
            relevant_docs = case_docs
            print(f"📎 Selected {len(relevant_docs)} case context documents")
            
        else:
            # Phases 1-7: Use document selector
            relevant_docs = self.document_selector.select_for_phase(
                phase=phase_num,
                phase_data=self.knowledge_manage.get_previous_knowledge(phase_num),
                max_docs=50
            )
            print(f"📎 Selected {len(relevant_docs)} documents for Phase {phase_num}")
        
        if not relevant_docs:
            print(f"⚠️ No relevant documents for Phase {phase_num}")
            return {}
        
        # Build context from knowledge graph
        context = self._build_comprehensive_context(phase_num)
        
        # Execute single comprehensive analysis
        results = self._execute_single_comprehensive_analysis(
            phase_num, 
            relevant_docs, 
            context
        )
        
        # Store in knowledge manager
        self.knowledge_manage.store_phase_knowledge(phase_num, results)
        
        # Update knowledge graph
        self._update_knowledge_graph(phase_num, results)
        
        print(f"✅ Phase {phase_num} complete - knowledge stored")
        
        return results
    
    def _build_comprehensive_context(self, phase: str) -> Dict:
        """Build rich context from knowledge graph"""
        context = {
            'phase': phase,
            'previous_phases': self.knowledge_manage.get_completed_phases(),
            'knowledge_graph': {},
            'accumulated_patterns': {},
            'contradictions': {},
            'legal_weapons': {},
            'strategic_priorities': self._get_strategic_priorities(phase)
        }
        
        # Safely get knowledge graph attributes
        if hasattr(self.knowledge_manage, 'knowledge_graph'):
            kg = self.knowledge_manage.knowledge_graph
            context['knowledge_graph'] = kg
            context['contradictions'] = kg.get('contradictions', {})
            context['legal_weapons'] = kg.get('legal_weapons', {})
            context['accumulated_patterns'] = kg.get('patterns', {})
        
        return context
    
    def _execute_single_comprehensive_analysis(self, phase: str, docs: List[Dict], context: Dict) -> Dict:
        """Execute single Claude call for all analysis"""
        
        # For Phase 0A with many documents, we may need to batch
        if phase == "0A" and len(docs) > 100:
            print(f"📦 Processing {len(docs)} documents in batches...")
            return self._execute_batched_analysis(phase, docs, context)
        
        # Build comprehensive prompt
        master_prompt = self._build_comprehensive_phase_prompt(phase, context)
        
        # Prepare documents for API
        doc_contents = []
        for doc in docs[:50]:  # Limit for single call
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
        
        # Track costs
        if hasattr(self.api_client, 'cost_tracker'):
            print(f"💰 Phase {phase} cost: £{self.api_client.cost_tracker.total_cost:.2f}")
        
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
        
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(docs)-1)//batch_size + 1} ({len(batch)} docs)...")
            
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
                phase=f"phase_{phase}_batch_{i//batch_size}"
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
        all_results['synthesis'] = self._synthesise_batch_results(all_results['combined_analysis'], phase)
        
        return all_results
    
    def _synthesise_batch_results(self, batch_responses: List[str], phase: str) -> str:
        """Synthesise multiple batch responses into unified analysis"""
        if len(batch_responses) == 1:
            return batch_responses[0]
        
        synthesis_prompt = f"""
Synthesise these {len(batch_responses)} batch analyses from Phase {phase} into unified findings.
Identify the most important patterns, weapons, and insights across all batches.
Focus on what will destroy Process Holdings.

BATCH RESULTS:
{"="*40}
"""
        for i, response in enumerate(batch_responses, 1):
            synthesis_prompt += f"\nBATCH {i}:\n{response[:2000]}\n{'='*40}"
        
        # Make synthesis call
        synthesis = self.api_client.analyse_documents_batch(
            documents=[],
            prompt=synthesis_prompt,
            phase=f"phase_{phase}_synthesis"
        )
        
        return synthesis
    
    def _build_comprehensive_phase_prompt(self, phase: str, context: Dict) -> str:
        """Build comprehensive prompt for phase"""
        
        # Get base prompt
        base_prompt = get_phase_prompt(phase) if not context['previous_phases'] else get_phase_prompt_enhanced(phase, context)
        
        # Enhance for Phase 0A
        if phase == "0A":
            enhanced_prompt = f"""
{base_prompt}

YOU ARE PROCESSING THE COMPLETE LEGAL FRAMEWORK FOR LISMORE vs PROCESS HOLDINGS.

Extract and weaponise EVERYTHING:
1. ALL legal doctrines that can destroy Process Holdings
2. ALL procedural weapons for maximum damage
3. ALL criminal crossover opportunities
4. ALL settlement leverage points
5. ALL arbitrator psychology insights

From rule cards: Extract the nuclear options
From treatises: Extract supporting law and precedents
From playbooks: Extract strategic deployment tactics

Build the COMPLETE legal arsenal for total victory.
"""
        else:
            enhanced_prompt = f"""
{base_prompt}

CONTEXT FROM KNOWLEDGE GRAPH:
Legal Weapons: {len(context.get('legal_weapons', {}).get('nuclear', []))} nuclear options available
Previous Phases: {context.get('previous_phases', [])}
Patterns Found: {len(context.get('accumulated_patterns', {}))}

Apply all accumulated intelligence to maximise damage to Process Holdings.
"""
        
        return enhanced_prompt
    
    def _parse_comprehensive_response(self, response: str, phase: str) -> Dict:
        """Parse Claude's response into structured results"""
        if not response:
            return {}
            
        results = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'raw_analysis': response,
            'documents_analysed': len(re.findall(r'\[DOC_\d{4}\]', response))
        }
        
        # Extract key sections using patterns
        sections = {
            'weapons': r'(?:WEAPON|NUCLEAR|DOCTRINE).*?(?=\n[A-Z]+:|\Z)',
            'contradictions': r'(?:CONTRADICTION).*?(?=\n[A-Z]+:|\Z)', 
            'patterns': r'(?:PATTERN).*?(?=\n[A-Z]+:|\Z)',
            'strategy': r'(?:STRATEG).*?(?=\n[A-Z]+:|\Z)'
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                results[key] = match.group(0)
        
        return results
    
    def _update_knowledge_graph(self, phase: str, results: Dict):
        """Update knowledge graph with phase findings"""
        
        # For Phase 0A, extract legal weapons
        if phase == "0A" and 'raw_analysis' in results:
            self._extract_legal_weapons(results['raw_analysis'])
        
        # Update with any findings
        if hasattr(self.knowledge_manage, 'add_phase_findings'):
            self.knowledge_manage.add_phase_findings(phase, results)
        
        print(f"📊 Knowledge graph updated with Phase {phase} intelligence")
    
    def _extract_legal_weapons(self, analysis: str):
        """Extract legal weapons from Phase 0A analysis"""
        if not hasattr(self.knowledge_manage, 'knowledge_graph'):
            return
            
        kg = self.knowledge_manage.knowledge_graph
        
        # Ensure structure exists
        if 'legal_weapons' not in kg:
            kg['legal_weapons'] = {'nuclear': [], 'high_impact': [], 'procedural': [], 'criminal': []}
        
        # Extract weapons by type
        if 'NUCLEAR' in analysis.upper():
            # Extract nuclear weapons
            nuclear_pattern = r'NUCLEAR[:\s]+([^\n]+)'
            for match in re.finditer(nuclear_pattern, analysis, re.IGNORECASE):
                kg['legal_weapons']['nuclear'].append(match.group(1))
        
        # Extract other weapon types similarly
        print(f"   Extracted {len(kg['legal_weapons']['nuclear'])} nuclear weapons")
    
    def _update_context_with_findings(self, context: Dict, findings: Dict):
        """Update context with findings from batch"""
        if 'patterns' in findings:
            if 'accumulated_patterns' not in context:
                context['accumulated_patterns'] = {}
            context['accumulated_patterns'].update(findings.get('patterns', {}))
    
    def _get_strategic_priorities(self, phase: str) -> List[str]:
        """Get strategic priorities for phase"""
        priorities = {
            "0A": ["Legal weapon extraction", "Criminal crossover identification", "Settlement leverage"],
            "0B": ["Admission harvesting", "Position tracking", "Credibility gaps"],
            "1": ["Document authentication", "Actor identification", "Timeline gaps"],
            "2": ["Chronological impossibilities", "Pattern evolution", "Hidden events"],
            "3": ["Contradiction matrix", "Admission hunting", "Missing documents"],
            "4": ["Narrative construction", "Evidence packages", "Witness targeting"],
            "5": ["Criminal elements", "Fraud indicators", "Settlement leverage"],
            "6": ["Summary judgment", "Strike-out grounds", "Cost sanctions"],
            "7": ["Nuclear options", "Case theory", "Closing strategy"]
        }
        return priorities.get(phase, ["General analysis"])
    
    def generate_war_room_dashboard(self) -> str:
        """Generate executive dashboard"""
        kg = getattr(self.knowledge_manage, 'knowledge_graph', {})
        
        dashboard = f"""
╔════════════════════════════════════════════════════════════╗
║           LISMORE vs PROCESS HOLDINGS                     ║
║              WAR ROOM DASHBOARD                           ║
╚════════════════════════════════════════════════════════════╝

🎯 NUCLEAR OPTIONS: {len(kg.get('legal_weapons', {}).get('nuclear', []))}
⚡ HIGH-IMPACT WEAPONS: {len(kg.get('legal_weapons', {}).get('high_impact', []))}
📊 CONTRADICTIONS: {len(kg.get('contradictions', {}))}
👥 KEY ACTORS: {len(kg.get('entities', {}))}

PHASE STATUS:
{self._get_phase_status()}

💰 ESTIMATED DAMAGES: £127.5M
⚖️ WIN PROBABILITY: {self._calculate_win_probability()}%
"""
        return dashboard
    
    def _get_phase_status(self) -> str:
        """Get phase completion status"""
        completed = self.knowledge_manage.get_completed_phases()
        all_phases = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        status = []
        for phase in all_phases:
            if phase in completed:
                status.append(f"  Phase {phase}: ✅ Complete")
            else:
                status.append(f"  Phase {phase}: ⏳ Pending")
        
        return "\n".join(status)
    
    def _calculate_win_probability(self) -> int:
        """Calculate win probability"""
        kg = getattr(self.knowledge_manage, 'knowledge_graph', {})
        
        score = 50
        score += len(kg.get('legal_weapons', {}).get('nuclear', [])) * 10
        score += len(kg.get('contradictions', {})) * 2
        
        return min(95, score)