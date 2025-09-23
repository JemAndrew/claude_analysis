# src/forensics.py
"""
Forensic document analysis and withholding detection for Opus 4.1
Specialised for identifying missing documents and adverse inference opportunities
"""

import re
from typing import Dict, List

class DocumentWithholdingTracker:
    """
    Enhanced document withholding tracker for Opus 4.1
    Identifies references to documents not in disclosure for adverse inference
    """
    
    def __init__(self):
        self.referenced_but_missing = {}
        self.sequence_gaps = []
        self.attachment_references = {}
        self.meeting_minutes_gaps = []
        self.board_resolution_gaps = []
        
    def analyse_for_withholding(self, document_text: str, doc_id: str):
        """
        Identify references to documents not in disclosure - Opus 4.1 enhanced
        """
        # Enhanced patterns for forensic analysis
        patterns = {
            'attachments': r'(?:see|as per|per|refer to|attached|attachment|annex|appendix|exhibit)\s+([A-Z0-9\-\.]+)',
            'meetings': r'(?:minutes of|meeting on|board meeting of)\s+(\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4})',
            'resolutions': r'(?:resolution|board resolution|shareholder resolution)\s+(?:no\.?\s*)?([0-9\-\/]+)',
            'documents': r'(?:document|report|memo|letter|email)\s+(?:dated|of|from)\s+(\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4})',
            'previous_correspondence': r'(?:my|our|your)\s+(?:email|letter|memo)\s+(?:of|dated)\s+(\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4})',
            'agreements': r'(?:agreement|contract|deed|MOU)\s+(?:dated|of)\s+(\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4})',
            'reports': r'(?:report|assessment|analysis|review)\s+(?:on|regarding|about)\s+([A-Za-z\s]+?)(?:\.|,|\s+dated)',
            'legal_advice': r'(?:advice|opinion|counsel)\s+(?:from|by)\s+([A-Za-z\s&]+?)(?:\.|,|\s+dated)'
        }
        
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, document_text, re.IGNORECASE)
            for match in matches:
                key = f"{pattern_type}_{match}"
                if key not in self.referenced_but_missing:
                    self.referenced_but_missing[key] = {
                        'first_referenced_in': doc_id,
                        'reference_count': 0,
                        'referencing_documents': [],
                        'pattern_type': pattern_type,
                        'forensic_significance': self._assess_forensic_significance(pattern_type, match)
                    }
                self.referenced_but_missing[key]['reference_count'] += 1
                self.referenced_but_missing[key]['referencing_documents'].append(doc_id)
        
        # Check for sequence gaps
        self._identify_sequence_gaps(document_text, doc_id)
        
        # Check for meeting references without minutes
        self._track_meeting_references(document_text, doc_id)
        
        # Check for resolution references
        self._track_resolution_references(document_text, doc_id)
    
    def _identify_sequence_gaps(self, text: str, doc_id: str):
        """Identify gaps in document sequences"""
        # Look for document numbers
        number_pattern = r'(?:Doc|Document|Exhibit|Annex)\s*(?:No\.?\s*)?(\d+)'
        numbers = re.findall(number_pattern, text, re.IGNORECASE)
        
        for num_str in numbers:
            try:
                num = int(num_str)
                self.sequence_gaps.append({
                    'number': num,
                    'doc_id': doc_id,
                    'type': 'sequence_number'
                })
            except ValueError:
                pass
    
    def _track_meeting_references(self, text: str, doc_id: str):
        """Track references to meetings"""
        meeting_pattern = r'(?:meeting|conference|discussion)\s+(?:held\s+)?(?:on|dated)\s+(\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4})'
        meetings = re.findall(meeting_pattern, text, re.IGNORECASE)
        
        for meeting_date in meetings:
            key = f"meeting_{meeting_date}"
            if key not in self.meeting_minutes_gaps:
                self.meeting_minutes_gaps.append({
                    'meeting_date': meeting_date,
                    'referenced_in': doc_id,
                    'minutes_missing': True
                })
    
    def _track_resolution_references(self, text: str, doc_id: str):
        """Track board resolution references"""
        resolution_pattern = r'(?:board\s+)?resolution\s+(?:no\.?\s*)?(\d+[\-\/]?\d*)'
        resolutions = re.findall(resolution_pattern, text, re.IGNORECASE)
        
        for resolution_num in resolutions:
            key = f"resolution_{resolution_num}"
            if key not in self.board_resolution_gaps:
                self.board_resolution_gaps.append({
                    'resolution_number': resolution_num,
                    'referenced_in': doc_id,
                    'resolution_missing': True
                })
    
    def _assess_forensic_significance(self, pattern_type: str, reference: str) -> str:
        """Assess forensic significance for Opus 4.1"""
        if pattern_type in ['resolutions', 'agreements', 'legal_advice']:
            return "CRITICAL - Core decision documentation"
        elif pattern_type in ['meetings', 'reports']:
            return "HIGH - Process and analysis documentation"
        elif pattern_type in ['attachments', 'documents']:
            return "MEDIUM - Supporting documentation"
        else:
            return "STANDARD - General reference"
    
    def _assess_significance(self, reference: str) -> str:
        """Assess significance of missing document"""
        ref_lower = reference.lower()
        
        if any(term in ref_lower for term in ['board', 'resolution', 'shareholder', 'vote']):
            return "CRITICAL - Board/shareholder decision"
        elif any(term in ref_lower for term in ['meeting', 'minutes', 'discussion']):
            return "HIGH - Meeting documentation"
        elif any(term in ref_lower for term in ['report', 'assessment', 'analysis', 'due diligence']):
            return "HIGH - Analysis documentation"
        elif any(term in ref_lower for term in ['legal', 'advice', 'opinion', 'counsel']):
            return "CRITICAL - Legal advice"
        elif any(term in ref_lower for term in ['agreement', 'contract', 'deed']):
            return "CRITICAL - Contractual documentation"
        else:
            return "MEDIUM - General documentation"
    
    def generate_adverse_inference_report(self) -> List[Dict]:
        """
        Generate comprehensive adverse inference report for Opus 4.1
        Returns list of missing documents warranting adverse inference
        """
        critical_missing = []
        
        # Analyse referenced but missing documents
        for ref, details in self.referenced_but_missing.items():
            if details['reference_count'] >= 2:  # Referenced multiple times
                critical_missing.append({
                    'document': ref,
                    'times_referenced': details['reference_count'],
                    'documents_referencing': details['referencing_documents'],
                    'pattern_type': details.get('pattern_type', 'unknown'),
                    'forensic_significance': details.get('forensic_significance', 'unknown'),
                    'adverse_inference_available': True,
                    'significance': self._assess_significance(ref),
                    'spoliation_indicator': details['reference_count'] > 5,
                    'tribunal_impact': self._assess_tribunal_impact(details)
                })
        
        # Analyse sequence gaps
        if self.sequence_gaps:
            sequence_analysis = self._analyse_sequence_gaps()
            if sequence_analysis:
                critical_missing.extend(sequence_analysis)
        
        # Analyse missing meeting minutes
        for meeting in self.meeting_minutes_gaps:
            critical_missing.append({
                'document': f"Minutes of meeting on {meeting['meeting_date']}",
                'times_referenced': 1,
                'documents_referencing': [meeting['referenced_in']],
                'adverse_inference_available': True,
                'significance': 'HIGH - Meeting documentation',
                'meeting_specific': True
            })
        
        # Analyse missing board resolutions
        for resolution in self.board_resolution_gaps:
            critical_missing.append({
                'document': f"Board Resolution {resolution['resolution_number']}",
                'times_referenced': 1,
                'documents_referencing': [resolution['referenced_in']],
                'adverse_inference_available': True,
                'significance': 'CRITICAL - Board decision',
                'resolution_specific': True
            })
        
        # Sort by forensic priority
        return sorted(critical_missing, 
                     key=lambda x: (
                         x.get('significance', '').startswith('CRITICAL'),
                         x.get('spoliation_indicator', False),
                         x['times_referenced']
                     ), 
                     reverse=True)
    
    def _analyse_sequence_gaps(self) -> List[Dict]:
        """Analyse document sequence gaps for patterns"""
        gaps = []
        if not self.sequence_gaps:
            return gaps
        
        # Sort sequence numbers
        numbers = sorted(set(gap['number'] for gap in self.sequence_gaps))
        
        # Find gaps in sequences
        for i in range(len(numbers) - 1):
            if numbers[i+1] - numbers[i] > 1:
                for missing_num in range(numbers[i] + 1, numbers[i+1]):
                    gaps.append({
                        'document': f"Document {missing_num} (sequence gap)",
                        'times_referenced': 0,
                        'documents_referencing': [],
                        'adverse_inference_available': True,
                        'significance': 'HIGH - Sequence gap indicates withholding',
                        'sequence_gap': True,
                        'missing_number': missing_num
                    })
        
        return gaps
    
    def _assess_tribunal_impact(self, details: Dict) -> str:
        """Assess impact on tribunal for Opus 4.1"""
        ref_count = details['reference_count']
        pattern = details.get('pattern_type', '')
        
        if ref_count > 10 and pattern in ['resolutions', 'agreements']:
            return "DEVASTATING - Systematic withholding of critical documents"
        elif ref_count > 5:
            return "SEVERE - Pattern of selective disclosure"
        elif pattern in ['legal_advice', 'resolutions']:
            return "HIGH - Withholding of decision documentation"
        else:
            return "MODERATE - Supporting document withholding"
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for reporting"""
        return {
            'total_referenced_missing': len(self.referenced_but_missing),
            'total_sequence_gaps': len(self.sequence_gaps),
            'missing_meetings': len(self.meeting_minutes_gaps),
            'missing_resolutions': len(self.board_resolution_gaps),
            'high_frequency_missing': sum(1 for ref in self.referenced_but_missing.values() 
                                         if ref['reference_count'] > 5)
        }