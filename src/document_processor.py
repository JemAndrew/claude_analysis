"""
Enhanced Document Processor with Maximum Pattern Recognition
Integrated version of document_processor.py with advanced Claude utilisation
"""

import json
import time
import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from api_client import ClaudeAPIClient
from knowledge_manage import KnowledgeManager
from phase_prompts import (
    get_phase_prompt,
    get_master_prompt,
    get_phase_description,
    get_all_phases,
    should_generate_learning,
    get_learning_generator_prompt,
    update_learning_prompt
)
from utils import load_documents, validate_documents

class DocumentProcessor:
    """
    Enhanced document processing engine with maximum pattern recognition
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise the enhanced document processor"""
        self.api_client = ClaudeAPIClient(api_key=api_key)
        self.knowledge_manage = KnowledgeManager()
        self.documents = []
        self.current_phase = None
        
        # THREE-DIRECTORY STRUCTURE
        self.PHASE_DIRECTORIES = {
            "0A": "legal_resources",           
            "0B": "case_context",              
            "1": "documents/processed/text",   
            "2": "documents/processed/text",   
            "3": "documents/processed/text",   
            "4": "documents/processed/text",   
            "5": "documents/processed/text",   
            "6": "documents/processed/text",   
            "7": "documents/processed/text"    
        }
        
        self.RAW_DISCLOSURE_DIR = "documents/raw"
        
        # Enhanced tracking structures
        self.document_registry = {}
        self.pattern_cache = defaultdict(list)
        self.cross_references = defaultdict(set)
        self.entity_tracker = defaultdict(lambda: {
            'mentions': [],
            'contexts': [],
            'relationships': set(),
            'timeline': []
        })
        self.contradiction_matrix = []
        self.timeline_events = []
        self.financial_tracker = defaultdict(list)
        
        # Cache for disclosure documents
        self.disclosure_cache = None
        self.disclosure_metadata = None
        
    def process_phase(self, phase_num: str) -> Dict:
        """
        Enhanced phase processing with maximum pattern extraction
        """
        print(f"\n{'='*60}")
        print(f"PHASE {phase_num}: {get_phase_description(phase_num)}")
        print(f"{'='*60}")
        
        # Load documents for this phase
        documents = self.load_phase_documents(phase_num)
        
        if not documents:
            print(f"⚠️  No documents found for Phase {phase_num}")
            return None
        
        print(f"📄 Loaded {len(documents)} documents")
        
        # Prepare documents with rich metadata
        enriched_docs = self._prepare_documents_with_metadata(documents)
        
        # Get previous phase knowledge for context
        previous_knowledge = self.knowledge_manage.get_previous_knowledge(phase_num)
        
        # Build enhanced prompts based on phase
        if phase_num == "0A":
            results = self._process_legal_framework(enriched_docs)
        elif phase_num == "0B":
            results = self._process_case_context(enriched_docs, previous_knowledge)
        else:
            results = self._process_main_phase(phase_num, enriched_docs, previous_knowledge)
        
        # Store phase knowledge
        self.knowledge_manage.store_phase_knowledge(phase_num, results)
        
        return results
    
    def _prepare_documents_with_metadata(self, documents: List[Dict]) -> Dict:
        """
        Prepare documents with rich metadata for Claude analysis
        """
        print("🔍 Extracting document metadata and patterns...")
        
        for idx, doc in enumerate(documents, 1):
            doc_id = f"DOC_{idx:04d}"
            content = doc.get('content', '')
            
            # Extract comprehensive metadata
            metadata = {
                'length': len(content),
                'type': self._classify_document_type(content),
                'dates': self._extract_dates(content),
                'amounts': self._extract_amounts(content),
                'entities': self._extract_entities(content),
                'references': self._extract_references(content),
                'formality_level': self._assess_formality(content),
                'urgency_indicators': self._detect_urgency(content),
                'defensive_language': self._detect_defensive_language(content)
            }
            
            self.document_registry[doc_id] = {
                'id': doc_id,
                'filename': doc.get('filename', doc.get('path', 'unknown').split('/')[-1]),
                'content': content,
                'metadata': metadata
            }
            
            # Track entities across documents
            for person in metadata['entities'].get('people', []):
                self.entity_tracker[person]['mentions'].append(doc_id)
            
            # Track timeline events
            for date_info in metadata['dates']:
                self.timeline_events.append({
                    'date': date_info['date'],
                    'context': date_info['context'],
                    'document': doc_id
                })
            
            # Track financial amounts
            for amount_info in metadata['amounts']:
                self.financial_tracker[amount_info['amount']].append({
                    'context': amount_info['context'],
                    'document': doc_id
                })
        
        # Build cross-reference matrix
        self._build_cross_reference_matrix()
        
        # Create corpus overview for Claude
        corpus_overview = self._create_corpus_overview()
        
        return {
            'documents': self.document_registry,
            'overview': corpus_overview,
            'cross_references': dict(self.cross_references),
            'entity_map': dict(self.entity_tracker),
            'timeline': sorted(self.timeline_events, key=lambda x: x.get('date', '')),
            'financial_summary': dict(self.financial_tracker)
        }
    
    def _process_legal_framework(self, enriched_docs: Dict) -> Dict:
        """
        Enhanced Phase 0A processing - Legal framework weaponisation
        """
        print("\n⚖️ LEGAL FRAMEWORK WEAPONISATION")
        print("-" * 40)
        
        results = {
            'legal_weapons': [],
            'procedural_advantages': [],
            'criminal_crossovers': [],
            'settlement_leverage': []
        }
        
        # Multi-pass extraction
        passes = {
            "offensive_weapons": self._build_offensive_weapons_prompt(),
            "defensive_shields": self._build_defensive_shields_prompt(),
            "procedural_traps": self._build_procedural_traps_prompt(),
            "settlement_leverage": self._build_settlement_leverage_prompt(),
            "criminal_threats": self._build_criminal_threats_prompt()
        }
        
        for pass_name, prompt in passes.items():
            print(f"  🎯 Extracting {pass_name}...")
            
            # Build full prompt with document context
            full_prompt = self._build_contextualised_prompt(
                prompt,
                enriched_docs,
                focus=pass_name
            )
            
            # Call Claude with enhanced prompt
            response = self.api_client.analyse_documents(
                documents=[],  # Documents are in the prompt
                prompt=full_prompt,
                phase=f"0A_{pass_name}"
            )
            
            # Parse and store results
            results[pass_name] = response
        
        # Synthesise all legal weapons
        results['synthesis'] = self._synthesise_legal_arsenal(results)
        
        return results
    
    def _process_case_context(self, enriched_docs: Dict, previous_knowledge: Dict) -> Dict:
        """
        Enhanced Phase 0B processing - Case context weaponisation
        """
        print("\n📚 CASE CONTEXT WEAPONISATION")
        print("-" * 40)
        
        results = {
            'admissions_bank': [],
            'contradiction_matrix': [],
            'missing_evidence': [],
            'witness_credibility': [],
            'timeline_impossibilities': []
        }
        
        # Extract from skeleton arguments with prejudice
        skeleton_prompt = self._build_skeleton_destruction_prompt(previous_knowledge)
        
        # Multi-angle extraction
        extraction_angles = {
            "admissions_hunt": "Find EVERY admission, concession, or failure to deny",
            "position_evolution": "Track how Process Holdings' story has changed",
            "missing_evidence": "Identify evidence they claim but don't provide",
            "credibility_gaps": "Find witness credibility problems",
            "timeline_conflicts": "Identify chronological impossibilities"
        }
        
        for angle, focus in extraction_angles.items():
            print(f"  🔍 Analysing: {angle}...")
            
            full_prompt = f"""
            {skeleton_prompt}
            
            SPECIFIC FOCUS FOR THIS PASS: {focus}
            
            DOCUMENT CORPUS:
            {json.dumps(enriched_docs['overview'], indent=2)}
            
            ENTITY MAP:
            {json.dumps(list(enriched_docs['entity_map'].keys()), indent=2)}
            
            TIMELINE EVENTS:
            {json.dumps(enriched_docs['timeline'][:20], indent=2)}
            
            CRITICAL: Every finding must reference specific documents [DOC_XXXX].
            Provide exact quotes where possible.
            Rate damage potential 1-10 for Process Holdings.
            """
            
            response = self.api_client.analyse_documents(
                documents=[],
                prompt=full_prompt,
                phase=f"0B_{angle}"
            )
            
            results[angle] = response
        
        return results
    
    def _process_main_phase(self, phase_num: str, enriched_docs: Dict, previous_knowledge: Dict) -> Dict:
        """
        Enhanced processing for Phases 1-7 with maximum pattern extraction
        """
        print(f"\n🎯 ENHANCED PHASE {phase_num} PROCESSING")
        print("-" * 40)
        
        # Build phase-specific enhanced prompts
        phase_prompts = self._get_enhanced_phase_prompts(phase_num, previous_knowledge)
        
        # Multi-pass analysis for maximum extraction
        results = {}
        
        # Pass 1: Broad pattern recognition
        print("  Pass 1: Broad pattern recognition...")
        broad_patterns = self._execute_pattern_recognition_pass(
            enriched_docs, 
            phase_prompts['pattern_recognition'],
            phase_num
        )
        results['patterns'] = broad_patterns
        
        # Pass 2: Deep contradiction analysis
        print("  Pass 2: Deep contradiction analysis...")
        contradictions = self._execute_contradiction_analysis_pass(
            enriched_docs,
            phase_prompts['contradiction_hunting'],
            phase_num,
            broad_patterns
        )
        results['contradictions'] = contradictions
        
        # Pass 3: Strategic synthesis
        print("  Pass 3: Strategic synthesis...")
        strategy = self._execute_strategic_synthesis_pass(
            enriched_docs,
            phase_prompts['strategic_synthesis'],
            phase_num,
            broad_patterns,
            contradictions
        )
        results['strategy'] = strategy
        
        # Phase-specific special analysis
        if phase_num in ["3", "4", "5"]:
            print("  Pass 4: Phase-specific deep dive...")
            special_results = self._execute_phase_specific_analysis(
                phase_num,
                enriched_docs,
                results
            )
            results['special_analysis'] = special_results
        
        return results
    
    def _build_contextualised_prompt(self, base_prompt: str, enriched_docs: Dict, focus: str) -> str:
        """
        Build a fully contextualised prompt with document metadata
        """
        prompt_parts = [
            base_prompt,
            "\n\nDOCUMENT CORPUS OVERVIEW:",
            json.dumps(enriched_docs['overview'], indent=2)[:3000],
            "\n\nKEY ENTITIES IDENTIFIED:",
            json.dumps(list(enriched_docs.get('entity_map', {}).keys())[:50], indent=2),
            "\n\nTIMELINE SPAN:",
            f"Earliest: {enriched_docs.get('timeline', [{}])[0].get('date', 'Unknown')}",
            f"Latest: {enriched_docs.get('timeline', [{}])[-1].get('date', 'Unknown') if enriched_docs.get('timeline') else 'Unknown'}",
            f"\n\nFOCUS: {focus}",
            "\n\nCRITICAL REQUIREMENTS:",
            "1. Reference EVERY finding to specific documents [DOC_XXXX]",
            "2. Provide exact quotes where possible",
            "3. Rate strategic value 1-10",
            "4. Suggest follow-up actions",
            "5. Identify missing evidence needed"
        ]
        
        # Add sample documents for context
        sample_docs = list(enriched_docs.get('documents', {}).values())[:3]
        if sample_docs:
            prompt_parts.append("\n\nSAMPLE DOCUMENTS FOR CONTEXT:")
            for doc in sample_docs:
                prompt_parts.append(f"\n{doc['id']}: {doc.get('filename', 'Unknown')}")
                prompt_parts.append(f"Content preview: {doc.get('content', '')[:500]}...")
        
        return "\n".join(prompt_parts)
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract all named entities from content"""
        entities = {
            'people': [],
            'companies': [],
            'law_firms': [],
            'locations': []
        }
        
        # People detection
        people_patterns = [
            r'(?:Mr|Mrs|Ms|Dr|Prof|Sir|Lord|Lady)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
            r'[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?=\s+(?:said|wrote|stated|confirmed|denied))',
        ]
        for pattern in people_patterns:
            entities['people'].extend(re.findall(pattern, content))
        
        # Company detection
        company_patterns = [
            r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Ltd|Limited|PLC|Inc|Corp|Corporation|LLP|LLC|Group|Holdings))',
            r'Process\s+(?:&|and)\s+Industrial\s+Developments?',
            r'P&ID',
            r'VR\s+Capital(?:\s+Group)?',
            r'Lismore'
        ]
        for pattern in company_patterns:
            entities['companies'].extend(re.findall(pattern, content, re.IGNORECASE))
        
        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_dates(self, content: str) -> List[Dict]:
        """Extract dates with context"""
        dates = []
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})'
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                dates.append({
                    'date': match.group(1),
                    'context': context,
                    'position': match.start()
                })
        
        return dates
    
    def _extract_amounts(self, content: str) -> List[Dict]:
        """Extract financial amounts with context"""
        amounts = []
        amount_patterns = [
            r'[$£€][\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B))?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|GBP|EUR|dollars?|pounds?|euros?)'
        ]
        
        for pattern in amount_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                amounts.append({
                    'amount': match.group(0),
                    'context': context,
                    'position': match.start()
                })
        
        return amounts
    
    def _extract_references(self, content: str) -> List[str]:
        """Extract references to other documents"""
        references = []
        ref_patterns = [
            r'(?:see|refer to|as per|pursuant to|according to|per)\s+(?:the\s+)?([A-Z][^.!?]*(?:agreement|contract|letter|email|document|minutes|report))',
            r'(?:attached|enclosed|appended)\s+(?:is\s+)?(?:the\s+)?([^.!?]+)',
            r'(?:Exhibit|Appendix|Annex|Schedule)\s+[A-Z0-9]+',
        ]
        
        for pattern in ref_patterns:
            references.extend(re.findall(pattern, content, re.IGNORECASE))
        
        return list(set(references))
    
    def _classify_document_type(self, content: str) -> str:
        """Classify document type based on content"""
        content_lower = content.lower()
        
        if 'agreement' in content_lower or 'contract' in content_lower:
            return 'contract'
        elif 'email' in content_lower or 'from:' in content_lower or 'to:' in content_lower:
            return 'email'
        elif 'minutes' in content_lower or 'meeting' in content_lower:
            return 'minutes'
        elif 'invoice' in content_lower or 'payment' in content_lower:
            return 'financial'
        elif 'witness statement' in content_lower or 'i state' in content_lower:
            return 'witness_statement'
        elif 'expert' in content_lower and 'opinion' in content_lower:
            return 'expert_report'
        elif 'skeleton' in content_lower or 'submission' in content_lower:
            return 'legal_submission'
        else:
            return 'general'
    
    def _assess_formality(self, content: str) -> str:
        """Assess formality level of document"""
        formal_indicators = ['pursuant', 'whereas', 'heretofore', 'aforementioned', 'undersigned']
        informal_indicators = ['hi', 'thanks', 'cheers', 'best', 'fyi', "let's"]
        
        formal_count = sum(1 for word in formal_indicators if word in content.lower())
        informal_count = sum(1 for word in informal_indicators if word in content.lower())
        
        if formal_count > informal_count * 2:
            return 'highly_formal'
        elif formal_count > informal_count:
            return 'formal'
        elif informal_count > formal_count:
            return 'informal'
        else:
            return 'neutral'
    
    def _detect_urgency(self, content: str) -> List[str]:
        """Detect urgency indicators in document"""
        urgency_phrases = [
            'urgent', 'immediately', 'asap', 'time is of the essence',
            'deadline', 'by close of business', 'without delay',
            'critical', 'priority', 'expedite'
        ]
        
        found = []
        content_lower = content.lower()
        for phrase in urgency_phrases:
            if phrase in content_lower:
                found.append(phrase)
        
        return found
    
    def _detect_defensive_language(self, content: str) -> List[str]:
        """Detect defensive or evasive language"""
        defensive_phrases = [
            'without prejudice', 'subject to contract', 'we deny',
            'alleged', 'purported', 'so-called', 'unfounded',
            'baseless', 'no admission', 'strictly denied',
            'save as aforesaid', 'except as admitted'
        ]
        
        found = []
        content_lower = content.lower()
        for phrase in defensive_phrases:
            if phrase in content_lower:
                found.append(phrase)
        
        return found
    
    def _build_cross_reference_matrix(self):
        """Build matrix of document cross-references"""
        for doc_id, doc_data in self.document_registry.items():
            content = doc_data.get('content', '')
            
            # Look for references to other documents
            for other_id, other_data in self.document_registry.items():
                if doc_id != other_id:
                    other_filename = other_data.get('filename', '')
                    if other_filename and other_filename in content:
                        self.cross_references[doc_id].add(other_id)
    
    def _create_corpus_overview(self) -> Dict:
        """Create high-level corpus overview for Claude"""
        overview = {
            'total_documents': len(self.document_registry),
            'date_range': self._get_date_range(),
            'document_types': self._get_document_type_distribution(),
            'key_parties': self._get_key_parties(),
            'formality_distribution': self._get_formality_distribution(),
            'urgency_documents': self._count_urgent_documents(),
            'defensive_documents': self._count_defensive_documents(),
            'financial_mentions': len(self.financial_tracker),
            'total_entities': len(self.entity_tracker),
            'cross_reference_density': len(self.cross_references)
        }
        
        return overview
    
    def _get_date_range(self) -> Dict:
        """Get date range of corpus"""
        if not self.timeline_events:
            return {'earliest': 'Unknown', 'latest': 'Unknown'}
        
        sorted_events = sorted(self.timeline_events, key=lambda x: x.get('date', ''))
        return {
            'earliest': sorted_events[0].get('date', 'Unknown'),
            'latest': sorted_events[-1].get('date', 'Unknown')
        }
    
    def _get_document_type_distribution(self) -> Dict:
        """Get distribution of document types"""
        types = defaultdict(int)
        for doc_data in self.document_registry.values():
            doc_type = doc_data.get('metadata', {}).get('type', 'unknown')
            types[doc_type] += 1
        return dict(types)
    
    def _get_key_parties(self) -> List[str]:
        """Get most frequently mentioned parties"""
        party_mentions = Counter()
        for entity, data in self.entity_tracker.items():
            party_mentions[entity] = len(data['mentions'])
        
        return [party for party, _ in party_mentions.most_common(10)]
    
    def _get_formality_distribution(self) -> Dict:
        """Get distribution of formality levels"""
        formality = defaultdict(int)
        for doc_data in self.document_registry.values():
            level = doc_data.get('metadata', {}).get('formality_level', 'unknown')
            formality[level] += 1
        return dict(formality)
    
    def _count_urgent_documents(self) -> int:
        """Count documents with urgency indicators"""
        count = 0
        for doc_data in self.document_registry.values():
            if doc_data.get('metadata', {}).get('urgency_indicators'):
                count += 1
        return count
    
    def _count_defensive_documents(self) -> int:
        """Count documents with defensive language"""
        count = 0
        for doc_data in self.document_registry.values():
            if doc_data.get('metadata', {}).get('defensive_language'):
                count += 1
        return count
    
    # Enhanced prompt builders
    def _build_offensive_weapons_prompt(self) -> str:
        """Build prompt for offensive legal weapons extraction"""
        return """
        OBJECTIVE: Extract OFFENSIVE LEGAL WEAPONS from these legal documents.
        
        For each legal doctrine/principle found:
        1. NAME: Exact legal doctrine name and citation
        2. ELEMENTS: What must be proven (list each element)
        3. APPLICATION: How Process Holdings violates this
        4. EVIDENCE NEEDED: Specific documents/testimony required
        5. DAMAGE POTENTIAL: Financial impact possible (£)
        6. PRECEDENT: Similar cases we can cite
        7. DEPLOYMENT: When/how to use this weapon
        
        Focus on doctrines that:
        - Impose strict liability
        - Allow punitive damages
        - Create presumptions against Process Holdings
        - Enable immediate relief
        - Trigger criminal investigations
        
        Rank by devastation potential: NUCLEAR / HIGH / MEDIUM / LOW
        """
    
    def _build_defensive_shields_prompt(self) -> str:
        """Build prompt for defensive strategy extraction"""
        return """
        OBJECTIVE: Build DEFENSIVE SHIELDS to protect Lismore.
        
        Identify:
        1. Immunities we can claim
        2. Limitations periods that help us
        3. Burden shifts in our favour
        4. Presumptions we benefit from
        5. Estoppels we can invoke
        6. Privileges we can assert
        
        For each shield:
        - Legal basis
        - Requirements to invoke
        - Timing considerations
        - Counter-arguments to prepare for
        """
    
    def _build_procedural_traps_prompt(self) -> str:
        """Build prompt for procedural advantage extraction"""
        return """
        OBJECTIVE: Identify PROCEDURAL TRAPS Process Holdings has fallen into.
        
        Find:
        1. Disclosure failures (sanctions available)
        2. Pleading defects (striking out possible)
        3. Admission triggers (binding statements made)
        4. Waiver situations (rights lost)
        5. Default positions (they failed to act)
        6. Contempt possibilities (court order breaches)
        
        For each trap:
        - Procedural rule violated
        - Consequence available
        - Motion/application needed
        - Evidence required
        - Success probability
        """
    
    def _build_settlement_leverage_prompt(self) -> str:
        """Build prompt for settlement leverage extraction"""
        return """
        OBJECTIVE: Extract MAXIMUM SETTLEMENT LEVERAGE points.
        
        Identify everything that creates settlement pressure:
        1. Criminal liability exposure
        2. Director disqualification risks
        3. Regulatory breach consequences
        4. Reputational destruction potential
        5. Third party claim triggers
        6. Insurance coverage threats
        7. Punitive damage availability
        8. Cost sanction exposure
        
        For each pressure point:
        - Threat level (1-10)
        - Credibility of threat
        - Financial impact
        - Publicity impact
        - How to deploy threat
        - What payment removes threat
        """
    
    def _build_criminal_threats_prompt(self) -> str:
        """Build prompt for criminal crossover identification"""
        return """
        OBJECTIVE: Identify CRIMINAL LIABILITY EXPOSURE for leverage.
        
        Find where civil conduct becomes criminal:
        1. Fraud indicators
        2. Conspiracy elements
        3. Money laundering markers
        4. Bribery/corruption signs
        5. Document destruction evidence
        6. Perjury/false statement proof
        7. Obstruction of justice acts
        8. Market manipulation signs
        
        For each criminal exposure:
        - Criminal offence name
        - Statutory provision
        - Elements present
        - Evidence available
        - Prosecution likelihood
        - Sentence exposure
        - How to use as leverage
        """
    
    def _build_skeleton_destruction_prompt(self, previous_knowledge: Dict) -> str:
        """Build prompt for skeleton argument destruction"""
        legal_weapons = previous_knowledge.get('0A', {}).get('legal_weapons', [])
        
        return f"""
        SKELETON ARGUMENT DESTRUCTION PROTOCOL
        
        You have these legal weapons from Phase 0A:
        {json.dumps(legal_weapons[:5], indent=2) if legal_weapons else 'None yet'}
        
        FORENSIC EXTRACTION REQUIREMENTS:
        
        1. ADMISSIONS HUNT (even implicit ones)
        2. POSITION EVOLUTION (how story changed)
        3. MISSING EVIDENCE (what they claim but don't provide)
        4. CREDIBILITY GAPS (witness problems)
        5. TIMELINE CONFLICTS (impossibilities)
        6. LEGAL VULNERABILITIES (wrong law)
        7. FINANCIAL DISCREPANCIES (calculation errors)
        8. STRATEGIC INTELLIGENCE (what they fear)
        
        For EVERY finding:
        - Quote exactly
        - Document reference
        - Damage rating 1-10
        - How to exploit
        - Follow-up needed
        """
    
    def _get_enhanced_phase_prompts(self, phase_num: str, previous_knowledge: Dict) -> Dict:
        """Get enhanced prompts for main phases 1-7"""
        
        # Build cumulative context from all previous phases
        cumulative_context = self._build_cumulative_context(previous_knowledge)
        
        prompts = {}
        
        if phase_num == "1":
            prompts = {
                'pattern_recognition': self._build_phase1_pattern_prompt(cumulative_context),
                'contradiction_hunting': self._build_phase1_contradiction_prompt(cumulative_context),
                'strategic_synthesis': self._build_phase1_strategy_prompt(cumulative_context)
            }
        elif phase_num == "2":
            prompts = {
                'pattern_recognition': self._build_phase2_timeline_prompt(cumulative_context),
                'contradiction_hunting': self._build_phase2_temporal_prompt(cumulative_context),
                'strategic_synthesis': self._build_phase2_chronology_prompt(cumulative_context)
            }
        elif phase_num == "3":
            prompts = {
                'pattern_recognition': self._build_phase3_deep_pattern_prompt(cumulative_context),
                'contradiction_hunting': self._build_phase3_impossibility_prompt(cumulative_context),
                'strategic_synthesis': self._build_phase3_gap_prompt(cumulative_context)
            }
        # Continue for phases 4-7...
        else:
            # Default enhanced prompts
            prompts = {
                'pattern_recognition': self._build_default_pattern_prompt(phase_num, cumulative_context),
                'contradiction_hunting': self._build_default_contradiction_prompt(phase_num, cumulative_context),
                'strategic_synthesis': self._build_default_strategy_prompt(phase_num, cumulative_context)
            }
        
        return prompts
    
    def _build_cumulative_context(self, previous_knowledge: Dict) -> str:
        """Build cumulative context from all previous phases"""
        context_parts = []
        
        if '0A' in previous_knowledge:
            legal = previous_knowledge['0A']
            context_parts.append(f"""
            LEGAL ARSENAL AVAILABLE:
            - Doctrines: {len(legal.get('legal_weapons', []))}
            - Criminal threats: {len(legal.get('criminal_crossovers', []))}
            - Settlement leverage: {len(legal.get('settlement_leverage', []))}
            """)
        
        if '0B' in previous_knowledge:
            case = previous_knowledge['0B']
            context_parts.append(f"""
            CASE INTELLIGENCE KNOWN:
            - Admissions found: {len(case.get('admissions_bank', []))}
            - Contradictions mapped: {len(case.get('contradiction_matrix', []))}
            - Missing evidence: {len(case.get('missing_evidence', []))}
            """)
        
        # Add intelligence from other phases
        for phase in ['1', '2', '3', '4', '5', '6']:
            if phase in previous_knowledge:
                phase_data = previous_knowledge[phase]
                context_parts.append(f"""
                PHASE {phase} INTELLIGENCE:
                - Patterns found: {len(phase_data.get('patterns', {}).get('findings', []))}
                - Contradictions: {len(phase_data.get('contradictions', {}).get('findings', []))}
                """)
        
        return '\n'.join(context_parts)
    
    def _execute_pattern_recognition_pass(self, enriched_docs: Dict, prompt: str, phase_num: str) -> Dict:
        """Execute pattern recognition pass with enhanced context"""
        
        full_prompt = f"""
        {prompt}
        
        CORPUS INTELLIGENCE:
        {json.dumps(enriched_docs['overview'], indent=2)}
        
        ENTITY NETWORK:
        Top 20 entities by mention frequency:
        {json.dumps(self._get_top_entities(20), indent=2)}
        
        TIMELINE SPAN:
        {json.dumps(enriched_docs.get('timeline', [])[:10], indent=2)}
        
        FINANCIAL TRACKING:
        Unique amounts mentioned: {len(enriched_docs.get('financial_summary', {}))}
        
        PATTERN DETECTION REQUIREMENTS:
        1. LINGUISTIC PATTERNS (phrases, tone shifts, formality changes)
        2. TEMPORAL PATTERNS (frequency, gaps, bursts)
        3. BEHAVIOURAL PATTERNS (who talks to whom, when, why)
        4. FINANCIAL PATTERNS (amount evolution, discrepancies)
        5. DECEPTION PATTERNS (defensive language, evasion)
        
        For EACH pattern:
        - Description
        - Documents exhibiting pattern [DOC_XXXX]
        - Frequency/statistics
        - Strategic significance
        - How to exploit
        """
        
        response = self.api_client.analyse_documents(
            documents=[],
            prompt=full_prompt,
            phase=f"{phase_num}_patterns"
        )
        
        return {'findings': response, 'timestamp': datetime.now().isoformat()}
    
    def _execute_contradiction_analysis_pass(self, enriched_docs: Dict, prompt: str, 
                                            phase_num: str, patterns: Dict) -> Dict:
        """Execute contradiction analysis with pattern context"""
        
        full_prompt = f"""
        {prompt}
        
        PATTERNS ALREADY IDENTIFIED:
        {json.dumps(patterns.get('findings', '')[:2000], indent=2)}
        
        CROSS-REFERENCE MATRIX:
        Documents referencing each other:
        {json.dumps(dict(list(self.cross_references.items())[:20]), indent=2)}
        
        CONTRADICTION HUNTING PROTOCOL:
        1. DIRECT CONTRADICTIONS (A says X, B says Y)
        2. TIMELINE IMPOSSIBILITIES (can't have happened as claimed)
        3. MISSING DOCUMENTS (referenced but not produced)
        4. NARRATIVE EVOLUTION (story changes over time)
        5. FINANCIAL DISCREPANCIES (numbers don't match)
        6. PARTICIPANT INCONSISTENCIES (impossible attendance)
        
        CREATE CONTRADICTION MATRIX:
        Doc1 | Doc2 | Type | Severity | Quote1 | Quote2 | Impact
        
        Rank by case-killing potential.
        """
        
        response = self.api_client.analyse_documents(
            documents=[],
            prompt=full_prompt,
            phase=f"{phase_num}_contradictions"
        )
        
        # Store contradictions in matrix
        self._update_contradiction_matrix(response)
        
        return {'findings': response, 'timestamp': datetime.now().isoformat()}
    
    def _execute_strategic_synthesis_pass(self, enriched_docs: Dict, prompt: str,
                                         phase_num: str, patterns: Dict, contradictions: Dict) -> Dict:
        """Execute strategic synthesis with all findings"""
        
        full_prompt = f"""
        {prompt}
        
        PATTERNS FOUND:
        {json.dumps(patterns.get('findings', '')[:1500], indent=2)}
        
        CONTRADICTIONS IDENTIFIED:
        {json.dumps(contradictions.get('findings', '')[:1500], indent=2)}
        
        STRATEGIC SYNTHESIS REQUIREMENTS:
        1. TOP 10 CASE-WINNING FINDINGS
        2. DOCUMENT REQUEST LIST (what's missing)
        3. DEPOSITION STRATEGY (who to question on what)
        4. SETTLEMENT LEVERAGE POINTS
        5. SUMMARY JUDGMENT ARGUMENTS
        6. TRIAL THEMES
        
        Make Process Holdings' position untenable.
        Every recommendation must be specific and actionable.
        """
        
        response = self.api_client.analyse_documents(
            documents=[],
            prompt=full_prompt,
            phase=f"{phase_num}_strategy"
        )
        
        return {'findings': response, 'timestamp': datetime.now().isoformat()}
    
    def _execute_phase_specific_analysis(self, phase_num: str, enriched_docs: Dict, 
                                        current_results: Dict) -> Dict:
        """Execute phase-specific special analysis"""
        
        special_prompts = {
            "3": "Deep dive on missing documents and reference gaps",
            "4": "Construct winning narrative and destroy theirs",
            "5": "Develop novel legal theories and creative arguments"
        }
        
        prompt = special_prompts.get(phase_num, "Extract maximum strategic value")
        
        full_prompt = f"""
        PHASE {phase_num} SPECIAL ANALYSIS: {prompt}
        
        Current findings summary:
        - Patterns: {len(current_results.get('patterns', {}).get('findings', []))}
        - Contradictions: {len(current_results.get('contradictions', {}).get('findings', []))}
        
        {self._get_phase_specific_instructions(phase_num)}
        
        Deliver game-changing insights that weren't found in standard passes.
        """
        
        response = self.api_client.analyse_documents(
            documents=[],
            prompt=full_prompt,
            phase=f"{phase_num}_special"
        )
        
        return response
    
    def _get_phase_specific_instructions(self, phase_num: str) -> str:
        """Get phase-specific special instructions"""
        instructions = {
            "3": """
            MISSING DOCUMENT FORENSICS:
            - Identify every reference to non-produced documents
            - Infer content of missing documents
            - Build adverse inference arguments
            - Create document request list with legal compulsion basis
            """,
            "4": """
            NARRATIVE WARFARE:
            - Build emotional jury narrative
            - Identify villain/victim dynamics  
            - Create simple soundbites that destroy them
            - Design visual timeline showing their deception
            """,
            "5": """
            CREATIVE LEGAL THEORIES:
            - Develop untested but viable arguments
            - Find novel damages theories
            - Create policy arguments
            - Identify regulatory hooks
            """
        }
        
        return instructions.get(phase_num, "Extract maximum value from this phase")
    
    def _get_top_entities(self, n: int = 20) -> List[Tuple[str, int]]:
        """Get top N entities by mention frequency"""
        entity_counts = []
        for entity, data in self.entity_tracker.items():
            count = len(data['mentions'])
            entity_counts.append((entity, count))
        
        entity_counts.sort(key=lambda x: x[1], reverse=True)
        return entity_counts[:n]
    
    def _update_contradiction_matrix(self, findings: str):
        """Update the contradiction matrix with new findings"""
        # Parse findings and add to matrix
        # This would parse Claude's response and structure it
        pass
    
    def _synthesise_legal_arsenal(self, results: Dict) -> str:
        """Synthesise all legal weapons into actionable arsenal"""
        synthesis_prompt = f"""
        Synthesise all legal weapons found:
        
        Offensive weapons: {results.get('offensive_weapons', '')}
        Defensive shields: {results.get('defensive_shields', '')}
        Procedural traps: {results.get('procedural_traps', '')}
        Settlement leverage: {results.get('settlement_leverage', '')}
        Criminal threats: {results.get('criminal_threats', '')}
        
        Create prioritised action plan:
        1. Immediate weapons to deploy
        2. Evidence needed to activate weapons
        3. Timing sequence for maximum impact
        4. Settlement vs trial strategy
        """
        
        return self.api_client.analyse_documents(
            documents=[],
            prompt=synthesis_prompt,
            phase="0A_synthesis"
        )
    
    # Phase-specific prompt builders (samples - add more as needed)
    def _build_phase1_pattern_prompt(self, context: str) -> str:
        return f"""
        PHASE 1: FOUNDATION PATTERN RECOGNITION
        
        {context}
        
        Build comprehensive understanding of:
        1. All parties and their relationships
        2. Document types and purposes
        3. Communication patterns
        4. Financial structures
        5. Legal framework applicable
        
        You're not just reading - you're building a war map.
        """
    
    def _build_phase1_contradiction_prompt(self, context: str) -> str:
        return f"""
        PHASE 1: INITIAL CONTRADICTION DETECTION
        
        {context}
        
        Find the obvious lies first:
        1. Different versions of same events
        2. Timeline impossibilities  
        3. Missing documents referenced
        4. Suspicious gaps in production
        
        These are the low-hanging fruit. Grab them all.
        """
    
    def _build_phase1_strategy_prompt(self, context: str) -> str:
        return f"""
        PHASE 1: STRATEGIC FOUNDATION
        
        {context}
        
        Based on initial analysis:
        1. What's our strongest attack vector?
        2. What are they most vulnerable on?
        3. What evidence do we desperately need?
        4. What should we investigate further?
        
        Set the strategic direction for remaining phases.
        """
    
    # Add more phase-specific prompts...
    
    def _build_default_pattern_prompt(self, phase: str, context: str) -> str:
        return f"""
        PHASE {phase}: PATTERN RECOGNITION
        
        {context}
        
        Extract all patterns relevant to Phase {phase} objectives.
        Build on previous findings.
        Go deeper than before.
        """
    
    def _build_default_contradiction_prompt(self, phase: str, context: str) -> str:
        return f"""
        PHASE {phase}: CONTRADICTION HUNTING
        
        {context}
        
        Find contradictions specific to Phase {phase} focus.
        Use accumulated knowledge to spot subtle inconsistencies.
        """
    
    def _build_default_strategy_prompt(self, phase: str, context: str) -> str:
        return f"""
        PHASE {phase}: STRATEGIC SYNTHESIS
        
        {context}
        
        Synthesise Phase {phase} findings into actionable strategy.
        Every output must damage Process Holdings.
        """
    
    # Existing methods remain but are enhanced...
    def load_phase_documents(self, phase_num: str) -> List[Dict]:
        """Load documents for specific phase with intelligent handling"""
        
        # For phases 1-7, use cached disclosure documents if available
        if phase_num in ["1", "2", "3", "4", "5", "6", "7"]:
            if self.disclosure_cache is not None:
                print(f"  Using cached disclosure documents ({len(self.disclosure_cache)} docs)")
                return self.disclosure_cache
        
        # Get the directory for this phase
        phase_dir = Path(self.PHASE_DIRECTORIES.get(phase_num, "documents"))
        
        # Check if directory exists
        if not phase_dir.exists():
            # For main phases, try raw directory as fallback
            if phase_num in ["1", "2", "3", "4", "5", "6", "7"]:
                phase_dir = Path(self.RAW_DISCLOSURE_DIR)
                if not phase_dir.exists():
                    print(f"❌ Directory not found: {phase_dir}")
                    return []
        
        # Load documents
        documents = load_documents(str(phase_dir))
        
        # Cache disclosure documents
        if phase_num in ["1", "2", "3", "4", "5", "6", "7"] and documents:
            self.disclosure_cache = documents
            print(f"  Cached {len(documents)} disclosure documents for reuse")
        
        return documents