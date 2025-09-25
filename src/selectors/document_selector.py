#!/usr/bin/env python3
"""
Document Selector for Litigation Intelligence System
Intelligent document selection strategies for each phase
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict
import hashlib


class DocumentSelector:
    """
    Intelligent document selection for phase-specific analysis
    Optimises document selection to maximise Claude's effectiveness
    """
    
    def __init__(self, document_registry: Dict[str, Dict]):
        """
        Initialise document selector
        
        Args:
            document_registry: Dictionary of registered documents
        """
        self.document_registry = document_registry
        self.document_metadata = self._build_metadata_index()
    
    def _build_metadata_index(self) -> Dict:
        """Build metadata index for fast document retrieval"""
        metadata = {
            'by_date': defaultdict(list),
            'by_type': defaultdict(list),
            'by_entity': defaultdict(list),
            'by_amount': defaultdict(list),
            'by_keyword': defaultdict(list),
            'by_sender': defaultdict(list),
            'by_length': defaultdict(list)
        }
        
        for doc_id, doc in self.document_registry.items():
            content = doc.get('content', '')
            
            # Index by various attributes
            self._index_by_date(doc_id, content, metadata['by_date'])
            self._index_by_type(doc_id, content, metadata['by_type'])
            self._index_by_entity(doc_id, content, metadata['by_entity'])
            self._index_by_amount(doc_id, content, metadata['by_amount'])
            self._index_by_sender(doc_id, content, metadata['by_sender'])
            
            # Index by document length
            length_category = self._categorise_length(len(content))
            metadata['by_length'][length_category].append(doc_id)
        
        return metadata
    
    # ==================== PHASE-SPECIFIC SELECTION ====================
    
    def select_for_phase(self, phase: str, phase_data: Dict, max_docs: int = 50) -> List[Dict]:
        """
        Select optimal documents for a specific phase
        
        Args:
            phase: Phase identifier
            phase_data: Phase analysis data
            max_docs: Maximum number of documents to return
            
        Returns:
            List of selected documents
        """
        selectors = {
            "0A": self.select_legal_framework_docs,
            "0B": self.select_case_context_docs,
            "1": self.select_landscape_docs,
            "2": self.select_timeline_docs,
            "3": self.select_contradiction_docs,
            "4": self.select_narrative_docs,
            "5": self.select_evidence_docs,
            "6": self.select_endgame_docs,
            "7": self.select_deep_analysis_docs
        }
        
        selector = selectors.get(phase, self.select_all_docs)
        return selector(phase_data, max_docs)
    
    def select_legal_framework_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 0A: Legal Framework"""
        selected_ids = set()
        
        # Prioritise contracts and agreements
        selected_ids.update(self.document_metadata['by_type']['contract'][:10])
        selected_ids.update(self.document_metadata['by_type']['agreement'][:10])
        
        # Add documents with legal language
        legal_keywords = ['shall', 'whereas', 'liability', 'indemnify', 'breach', 
                         'damages', 'termination', 'warranty', 'representation']
        for keyword in legal_keywords:
            docs = self._find_by_keyword(keyword, limit=5)
            selected_ids.update(docs)
        
        # Add formal correspondence
        selected_ids.update(self.document_metadata['by_type']['letter'][:5])
        
        return self._get_documents_by_ids(list(selected_ids)[:max_docs])
    
    def select_case_context_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 0B: Case Context"""
        selected_ids = set()
        
        # Skeleton arguments and pleadings
        selected_ids.update(self.document_metadata['by_type']['pleading'][:15])
        selected_ids.update(self.document_metadata['by_type']['skeleton'][:15])
        
        # Witness statements
        selected_ids.update(self.document_metadata['by_type']['witness_statement'][:10])
        
        # Position papers and submissions
        position_keywords = ['position', 'submission', 'argument', 'contend', 'claim']
        for keyword in position_keywords:
            docs = self._find_by_keyword(keyword, limit=5)
            selected_ids.update(docs)
        
        return self._get_documents_by_ids(list(selected_ids)[:max_docs])
    
    def select_landscape_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 1: Document Landscape"""
        selected_ids = []
        
        # Get diverse sample across all types
        for doc_type, doc_ids in self.document_metadata['by_type'].items():
            # Take up to 5 from each type
            selected_ids.extend(doc_ids[:5])
        
        # Add high-value documents (long, detailed)
        selected_ids.extend(self.document_metadata['by_length']['long'][:10])
        
        # Add documents from key time periods
        critical_dates = self._identify_critical_dates()
        for date_range in critical_dates:
            selected_ids.extend(self.document_metadata['by_date'].get(date_range, [])[:3])
        
        # Deduplicate and limit
        seen = set()
        unique_ids = []
        for doc_id in selected_ids:
            if doc_id not in seen:
                seen.add(doc_id)
                unique_ids.append(doc_id)
        
        return self._get_documents_by_ids(unique_ids[:max_docs])
    
    def select_timeline_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 2: Timeline Analysis"""
        selected_ids = []
        
        # Get all dated documents
        dated_docs = []
        for date_key, doc_ids in self.document_metadata['by_date'].items():
            dated_docs.extend(doc_ids)
        
        # Sort by date (if dates extracted)
        dated_docs = self._sort_by_date(dated_docs)
        
        # Take even distribution across timeline
        if dated_docs:
            step = max(1, len(dated_docs) // max_docs)
            selected_ids = dated_docs[::step][:max_docs]
        
        # Add documents with timeline keywords
        timeline_keywords = ['before', 'after', 'during', 'when', 'then', 
                           'subsequently', 'prior', 'following']
        for keyword in timeline_keywords[:3]:
            docs = self._find_by_keyword(keyword, limit=3)
            selected_ids.extend(docs)
        
        return self._get_documents_by_ids(selected_ids[:max_docs])
    
    def select_contradiction_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 3: Contradiction Analysis"""
        selected_ids = set()
        
        # Get documents already identified with contradictions
        if 'contradictions' in phase_data:
            contradiction_docs = self._extract_docs_from_findings(
                phase_data.get('contradictions', {})
            )
            selected_ids.update(contradiction_docs[:20])
        
        # Add documents from same entities (likely to contradict)
        top_entities = self._get_top_entities(5)
        for entity in top_entities:
            entity_docs = self.document_metadata['by_entity'].get(entity, [])
            selected_ids.update(entity_docs[:5])
        
        # Add documents with contradiction indicators
        contradiction_keywords = ['however', 'contrary', 'despite', 'although', 
                                 'nevertheless', 'inconsistent', 'conflict']
        for keyword in contradiction_keywords[:3]:
            docs = self._find_by_keyword(keyword, limit=3)
            selected_ids.update(docs)
        
        return self._get_documents_by_ids(list(selected_ids)[:max_docs])
    
    def select_narrative_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 4: Narrative Construction"""
        selected_ids = []
        
        # Key narrative documents
        narrative_types = ['contract', 'agreement', 'letter', 'email', 'memo']
        for doc_type in narrative_types:
            selected_ids.extend(self.document_metadata['by_type'][doc_type][:5])
        
        # Documents that tell the story
        story_keywords = ['agreed', 'promised', 'failed', 'breach', 'refused',
                         'misrepresented', 'concealed', 'destroyed']
        for keyword in story_keywords[:4]:
            docs = self._find_by_keyword(keyword, limit=3)
            selected_ids.extend(docs)
        
        # High-impact documents
        if 'patterns' in phase_data:
            pattern_docs = self._extract_docs_from_findings(
                phase_data.get('patterns', {})
            )
            selected_ids.extend(pattern_docs[:10])
        
        return self._get_documents_by_ids(selected_ids[:max_docs])
    
    def select_evidence_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 5: Evidence Packaging"""
        selected_ids = set()
        
        # Financial evidence
        selected_ids.update(self.document_metadata['by_type']['financial'][:10])
        selected_ids.update(self.document_metadata['by_type']['invoice'][:5])
        
        # Contracts and agreements
        selected_ids.update(self.document_metadata['by_type']['contract'][:10])
        
        # Communications showing intent
        selected_ids.update(self.document_metadata['by_type']['email'][:10])
        
        # Documents with admissions
        admission_keywords = ['admit', 'acknowledge', 'confirm', 'accept', 'agree']
        for keyword in admission_keywords[:3]:
            docs = self._find_by_keyword(keyword, limit=5)
            selected_ids.update(docs)
        
        # Documents with monetary amounts
        for amount_range, doc_ids in self.document_metadata['by_amount'].items():
            selected_ids.update(doc_ids[:3])
        
        return self._get_documents_by_ids(list(selected_ids)[:max_docs])
    
    def select_endgame_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 6: Endgame Strategy"""
        selected_ids = []
        
        # Settlement-relevant documents
        settlement_keywords = ['settle', 'negotiate', 'offer', 'compromise', 'resolution']
        for keyword in settlement_keywords:
            docs = self._find_by_keyword(keyword, limit=3)
            selected_ids.extend(docs)
        
        # High-impact contradictions
        if 'contradictions' in phase_data:
            contradiction_docs = self._extract_docs_from_findings(
                phase_data.get('contradictions', {})
            )
            selected_ids.extend(contradiction_docs[:10])
        
        # Criminal evidence
        criminal_keywords = ['fraud', 'deceive', 'false', 'misrepresent', 'conceal']
        for keyword in criminal_keywords[:3]:
            docs = self._find_by_keyword(keyword, limit=3)
            selected_ids.extend(docs)
        
        # Key admissions
        selected_ids.extend(self._find_by_keyword('admit', limit=10))
        
        return self._get_documents_by_ids(selected_ids[:max_docs])
    
    def select_deep_analysis_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Select documents for Phase 7: AI Deep Analysis"""
        # For deep analysis, get the most diverse and comprehensive set
        selected_ids = []
        
        # Get everything if under limit
        all_doc_ids = list(self.document_registry.keys())
        if len(all_doc_ids) <= max_docs:
            return list(self.document_registry.values())
        
        # Otherwise, intelligent sampling
        # Take proportional sample from each category
        samples_per_type = max(1, max_docs // len(self.document_metadata['by_type']))
        
        for doc_type, doc_ids in self.document_metadata['by_type'].items():
            selected_ids.extend(doc_ids[:samples_per_type])
        
        # Fill remaining slots with high-value documents
        remaining = max_docs - len(selected_ids)
        if remaining > 0:
            # Add longest documents (likely most detailed)
            selected_ids.extend(self.document_metadata['by_length']['long'][:remaining])
        
        return self._get_documents_by_ids(selected_ids[:max_docs])
    
    def select_all_docs(self, phase_data: Dict, max_docs: int) -> List[Dict]:
        """Default: return all or sample of documents"""
        all_docs = list(self.document_registry.values())
        if len(all_docs) <= max_docs:
            return all_docs
        
        # Return evenly distributed sample
        step = len(all_docs) // max_docs
        return all_docs[::step][:max_docs]
    
    # ==================== SPECIALISED SELECTORS ====================
    
    def select_by_entity(self, entity_name: str, max_docs: int = 20) -> List[Dict]:
        """Select documents mentioning specific entity"""
        doc_ids = self.document_metadata['by_entity'].get(entity_name, [])
        return self._get_documents_by_ids(doc_ids[:max_docs])
    
    def select_by_date_range(self, start_date: str, end_date: str, max_docs: int = 30) -> List[Dict]:
        """Select documents within date range"""
        selected_ids = []
        
        # Simple date comparison (enhance with proper date parsing)
        for date_key, doc_ids in self.document_metadata['by_date'].items():
            if start_date <= date_key <= end_date:
                selected_ids.extend(doc_ids)
        
        return self._get_documents_by_ids(selected_ids[:max_docs])
    
    def select_hot_documents(self, max_docs: int = 20) -> List[Dict]:
        """Select 'hot' documents likely to be most damaging"""
        hot_keywords = [
            'fraud', 'lie', 'conceal', 'destroy', 'hide', 'falsify',
            'misrepresent', 'deceive', 'criminal', 'illegal', 'breach',
            'violate', 'conspiracy', 'collude', 'bribe', 'corrupt'
        ]
        
        selected_ids = set()
        for keyword in hot_keywords:
            docs = self._find_by_keyword(keyword, limit=3)
            selected_ids.update(docs)
        
        # Add documents with high monetary amounts
        high_value_docs = []
        for amount_range, doc_ids in self.document_metadata['by_amount'].items():
            if 'million' in amount_range.lower() or 'billion' in amount_range.lower():
                high_value_docs.extend(doc_ids)
        selected_ids.update(high_value_docs[:10])
        
        return self._get_documents_by_ids(list(selected_ids)[:max_docs])
    
    def select_missing_documents(self, phase_data: Dict, max_docs: int = 30) -> List[Dict]:
        """Select documents that reference missing documents"""
        missing_keywords = [
            'attachment', 'enclosed', 'see attached', 'as discussed',
            'per our conversation', 'following up', 'as agreed',
            'copy to', 'cc:', 'forwarded', 'draft'
        ]
        
        selected_ids = set()
        for keyword in missing_keywords:
            docs = self._find_by_keyword(keyword, limit=5)
            selected_ids.update(docs)
        
        return self._get_documents_by_ids(list(selected_ids)[:max_docs])
    
    # ==================== UTILITY METHODS ====================
    
    def _index_by_date(self, doc_id: str, content: str, index: Dict):
        """Index document by dates found"""
        date_patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for date_str in matches[:3]:  # Limit to first 3 dates
                index[date_str].append(doc_id)
    
    def _index_by_type(self, doc_id: str, content: str, index: Dict):
        """Index document by type"""
        content_lower = content[:2000].lower()  # Check first 2000 chars
        
        # Document type detection
        if 'agreement' in content_lower or 'contract' in content_lower:
            index['contract'].append(doc_id)
        elif '@' in content_lower and ('from:' in content_lower or 'to:' in content_lower):
            index['email'].append(doc_id)
        elif 'invoice' in content_lower or 'payment' in content_lower:
            index['financial'].append(doc_id)
        elif 'minutes' in content_lower and 'meeting' in content_lower:
            index['minutes'].append(doc_id)
        elif 'memorandum' in content_lower or 'memo' in content_lower:
            index['memo'].append(doc_id)
        elif 'dear' in content_lower or 'sincerely' in content_lower:
            index['letter'].append(doc_id)
        elif 'witness statement' in content_lower:
            index['witness_statement'].append(doc_id)
        elif 'skeleton' in content_lower and 'argument' in content_lower:
            index['skeleton'].append(doc_id)
        else:
            index['other'].append(doc_id)
    
    def _index_by_entity(self, doc_id: str, content: str, index: Dict):
        """Index document by entities mentioned"""
        # Look for company names and key individuals
        entity_patterns = [
            r'\b(Lismore\s+Capital)\b',
            r'\b(Process\s+Holdings(?:\s+Ltd)?)\b',
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  # Person names
            r'\b([A-Z][a-z]+\s+(?:Ltd|Limited|Inc|Corp|Corporation))\b'  # Companies
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, content[:5000], re.IGNORECASE)
            for entity in set(matches[:10]):  # Unique entities, max 10
                index[entity].append(doc_id)
    
    def _index_by_amount(self, doc_id: str, content: str, index: Dict):
        """Index document by monetary amounts mentioned"""
        amount_pattern = r'[£$]([\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B))?)'
        matches = re.findall(amount_pattern, content, re.IGNORECASE)
        
        for amount_str in set(matches[:5]):  # Unique amounts, max 5
            # Categorise amount
            if 'million' in amount_str.lower() or 'M' in amount_str:
                category = 'millions'
            elif 'billion' in amount_str.lower() or 'B' in amount_str:
                category = 'billions'
            else:
                # Parse numerical value
                try:
                    value = float(amount_str.replace(',', '').split()[0])
                    if value >= 1000000:
                        category = 'millions'
                    elif value >= 100000:
                        category = 'hundreds_thousands'
                    elif value >= 10000:
                        category = 'tens_thousands'
                    else:
                        category = 'thousands_or_less'
                except:
                    category = 'other'
            
            index[category].append(doc_id)
    
    def _index_by_sender(self, doc_id: str, content: str, index: Dict):
        """Index document by sender (for emails)"""
        sender_pattern = r'From:\s*([^\n]+)'
        match = re.search(sender_pattern, content[:1000], re.IGNORECASE)
        if match:
            sender = match.group(1).strip()
            index[sender].append(doc_id)
    
    def _categorise_length(self, length: int) -> str:
        """Categorise document by length"""
        if length > 10000:
            return 'long'
        elif length > 3000:
            return 'medium'
        else:
            return 'short'
    
    def _find_by_keyword(self, keyword: str, limit: int = 10) -> List[str]:
        """Find documents containing keyword"""
        found = []
        keyword_lower = keyword.lower()
        
        for doc_id, doc in self.document_registry.items():
            if keyword_lower in doc.get('content', '').lower():
                found.append(doc_id)
                if len(found) >= limit:
                    break
        
        return found
    
    def _get_top_entities(self, count: int = 10) -> List[str]:
        """Get most frequently mentioned entities"""
        entity_counts = {
            entity: len(doc_ids) 
            for entity, doc_ids in self.document_metadata['by_entity'].items()
        }
        
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        return [entity for entity, _ in sorted_entities[:count]]
    
    def _extract_docs_from_findings(self, findings: Dict) -> List[str]:
        """Extract document IDs from phase findings"""
        doc_ids = []
        findings_text = str(findings)
        
        # Extract DOC_XXXX references
        doc_pattern = re.compile(r'DOC_\d{4}')
        matches = doc_pattern.findall(findings_text)
        
        return list(set(matches))  # Unique document IDs
    
    def _identify_critical_dates(self) -> List[str]:
        """Identify critical date ranges"""
        # This would be enhanced with actual critical period detection
        return ['2021-01-01', '2021-06-30', '2021-12-31', '2022-06-30']
    
    def _sort_by_date(self, doc_ids: List[str]) -> List[str]:
        """Sort document IDs by date (simplified)"""
        # This would be enhanced with proper date parsing
        return doc_ids  # Return as-is for now
    
    def _get_documents_by_ids(self, doc_ids: List[str]) -> List[Dict]:
        """Get document objects by IDs"""
        documents = []
        seen = set()
        
        for doc_id in doc_ids:
            if doc_id not in seen and doc_id in self.document_registry:
                documents.append(self.document_registry[doc_id])
                seen.add(doc_id)
        
        return documents
    
    def get_selection_statistics(self) -> Dict:
        """Get statistics about document corpus"""
        stats = {
            'total_documents': len(self.document_registry),
            'document_types': {
                doc_type: len(doc_ids) 
                for doc_type, doc_ids in self.document_metadata['by_type'].items()
            },
            'entities_identified': len(self.document_metadata['by_entity']),
            'date_range': self._get_date_range(),
            'length_distribution': {
                length_cat: len(doc_ids)
                for length_cat, doc_ids in self.document_metadata['by_length'].items()
            }
        }
        
        return stats
    
    def _get_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """Get earliest and latest dates in corpus"""
        all_dates = list(self.document_metadata['by_date'].keys())
        if all_dates:
            return (min(all_dates), max(all_dates))
        return (None, None)