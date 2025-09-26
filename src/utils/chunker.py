#!/usr/bin/env python3
"""
Intelligent Document Chunking for Large Context Windows
Optimised for 150k+ token contexts
"""

from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime


class DocumentChunker:
    """Intelligent chunking strategies for maximum context utilisation"""
    
    def __init__(self, config):
        self.config = config
        self.max_tokens = config.token_config['max_input_tokens']
        self.optimal_chunk_size = config.token_config['optimal_batch_size']
    
    def chunk_by_semantic_boundaries(self,
                                    text: str,
                                    max_chunk_tokens: int = None) -> List[Dict]:
        """
        Chunk text preserving semantic boundaries
        Returns list of chunk dictionaries with metadata
        """
        
        max_chunk_tokens = max_chunk_tokens or self.optimal_chunk_size
        max_chunk_chars = max_chunk_tokens * 4  # Approximate
        
        chunks = []
        
        # Split by major sections first
        sections = self._split_by_sections(text)
        
        current_chunk = {
            'content': '',
            'char_count': 0,
            'token_estimate': 0,
            'chunk_index': 0,
            'section_boundaries': []
        }
        
        for section_title, section_content in sections:
            section_chars = len(section_content)
            
            # If single section exceeds limit, split further
            if section_chars > max_chunk_chars:
                sub_chunks = self._split_large_section(
                    section_content,
                    max_chunk_chars,
                    section_title
                )
                
                for sub_chunk in sub_chunks:
                    chunks.append(sub_chunk)
            
            # If adding section exceeds limit, start new chunk
            elif current_chunk['char_count'] + section_chars > max_chunk_chars:
                if current_chunk['content']:
                    chunks.append(current_chunk)
                
                current_chunk = {
                    'content': section_content,
                    'char_count': section_chars,
                    'token_estimate': section_chars // 4,
                    'chunk_index': len(chunks),
                    'section_boundaries': [section_title] if section_title else []
                }
            
            # Add to current chunk
            else:
                current_chunk['content'] += '\n\n' + section_content
                current_chunk['char_count'] += section_chars
                current_chunk['token_estimate'] = current_chunk['char_count'] // 4
                if section_title:
                    current_chunk['section_boundaries'].append(section_title)
        
        # Add final chunk
        if current_chunk['content']:
            chunks.append(current_chunk)
        
        return chunks
    
    def chunk_for_investigation(self,
                              documents: List[Dict],
                              investigation_focus: str) -> List[Dict]:
        """
        Chunk documents optimised for specific investigation
        Prioritises relevant content
        """
        
        # Score documents by relevance
        scored_docs = []
        for doc in documents:
            score = self._score_relevance(doc, investigation_focus)
            scored_docs.append((score, doc))
        
        # Sort by relevance
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        chunks = []
        current_chunk = {
            'documents': [],
            'token_count': 0,
            'relevance_score': 0,
            'investigation_focus': investigation_focus
        }
        
        max_chunk_tokens = self.optimal_chunk_size
        
        for score, doc in scored_docs:
            doc_tokens = len(doc.get('content', '')) // 4
            
            # High-relevance documents get their own chunk if large
            if score > 0.8 and doc_tokens > max_chunk_tokens * 0.5:
                if current_chunk['documents']:
                    chunks.append(current_chunk)
                
                # Create dedicated chunk
                chunks.append({
                    'documents': [doc],
                    'token_count': doc_tokens,
                    'relevance_score': score,
                    'investigation_focus': investigation_focus,
                    'high_priority': True
                })
                
                # Reset current chunk
                current_chunk = {
                    'documents': [],
                    'token_count': 0,
                    'relevance_score': 0,
                    'investigation_focus': investigation_focus
                }
            
            # Add to current chunk if fits
            elif current_chunk['token_count'] + doc_tokens <= max_chunk_tokens:
                current_chunk['documents'].append(doc)
                current_chunk['token_count'] += doc_tokens
                current_chunk['relevance_score'] = max(
                    current_chunk['relevance_score'],
                    score
                )
            
            # Start new chunk
            else:
                if current_chunk['documents']:
                    chunks.append(current_chunk)
                
                current_chunk = {
                    'documents': [doc],
                    'token_count': doc_tokens,
                    'relevance_score': score,
                    'investigation_focus': investigation_focus
                }
        
        # Add final chunk
        if current_chunk['documents']:
            chunks.append(current_chunk)
        
        return chunks
    
    def chunk_chronologically(self,
                            documents: List[Dict],
                            overlap_days: int = 7) -> List[Dict]:
        """
        Chunk documents by time periods with overlap
        For timeline reconstruction
        """
        
        # Extract and sort by date
        dated_docs = []
        for doc in documents:
            dates = doc.get('metadata', {}).get('dates_found', [])
            if dates:
                # Use first date found
                dated_docs.append((dates[0], doc))
        
        # Sort chronologically
        dated_docs.sort(key=lambda x: x[0])
        
        chunks = []
        current_period_start = None
        current_chunk = {
            'documents': [],
            'period_start': None,
            'period_end': None,
            'token_count': 0
        }
        
        max_chunk_tokens = self.optimal_chunk_size
        
        for date, doc in dated_docs:
            doc_tokens = len(doc.get('content', '')) // 4
            
            # Check if new time period needed
            if current_chunk['token_count'] + doc_tokens > max_chunk_tokens:
                if current_chunk['documents']:
                    current_chunk['period_end'] = date
                    chunks.append(current_chunk)
                
                # Start new period with overlap
                current_chunk = {
                    'documents': self._get_overlap_docs(
                        chunks[-1]['documents'] if chunks else [],
                        overlap_days
                    ),
                    'period_start': date,
                    'period_end': None,
                    'token_count': sum(
                        len(d.get('content', '')) // 4
                        for d in current_chunk['documents']
                    )
                }
            
            current_chunk['documents'].append(doc)
            current_chunk['token_count'] += doc_tokens
            
            if not current_chunk['period_start']:
                current_chunk['period_start'] = date
        
        # Add final chunk
        if current_chunk['documents']:
            current_chunk['period_end'] = dated_docs[-1][0] if dated_docs else None
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[Tuple[str, str]]:
        """Split text into sections based on headers/structure"""
        
        sections = []
        
        # Look for section markers
        section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Z\s]+):?\s*$',  # ALL CAPS headers
            r'^\d+\.\s+(.+)$',  # Numbered sections
            r'^\[(.+)\]$',  # Bracketed sections
            r'^={3,}(.+?)={3,}$'  # Delimited sections
        ]
        
        lines = text.split('\n')
        current_section = []
        current_title = None
        
        for line in lines:
            # Check if line is section header
            is_header = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous section
                    if current_section:
                        sections.append((
                            current_title,
                            '\n'.join(current_section)
                        ))
                    
                    # Start new section
                    current_title = match.group(1) if match.lastindex else line
                    current_section = []
                    is_header = True
                    break
            
            if not is_header:
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append((current_title, '\n'.join(current_section)))
        
        # If no sections found, return whole text
        if not sections:
            sections = [(None, text)]
        
        return sections
    
    def _split_large_section(self,
                           text: str,
                           max_chars: int,
                           section_title: str = None) -> List[Dict]:
        """Split large section into smaller chunks"""
        
        chunks = []
        
        # Try to split by paragraphs
        paragraphs = text.split('\n\n')
        
        current_chunk = {
            'content': '',
            'char_count': 0,
            'token_estimate': 0,
            'chunk_index': len(chunks),
            'section_boundaries': [section_title] if section_title else [],
            'is_continuation': False
        }
        
        for para in paragraphs:
            para_chars = len(para)
            
            if current_chunk['char_count'] + para_chars > max_chars:
                if current_chunk['content']:
                    chunks.append(current_chunk)
                
                current_chunk = {
                    'content': para,
                    'char_count': para_chars,
                    'token_estimate': para_chars // 4,
                    'chunk_index': len(chunks),
                    'section_boundaries': [],
                    'is_continuation': True
                }
            else:
                if current_chunk['content']:
                    current_chunk['content'] += '\n\n' + para
                else:
                    current_chunk['content'] = para
                current_chunk['char_count'] += para_chars
                current_chunk['token_estimate'] = current_chunk['char_count'] // 4
        
        if current_chunk['content']:
            chunks.append(current_chunk)
        
        return chunks
    
    def _score_relevance(self, document: Dict, focus: str) -> float:
        """Score document relevance to investigation focus"""
        
        score = 0.0
        content_lower = document.get('content', '').lower()
        focus_lower = focus.lower()
        
        # Direct mention of focus
        if focus_lower in content_lower:
            score += 0.5
        
        # Related terms
        focus_terms = {
            'contradiction': ['inconsistent', 'conflict', 'dispute', 'disagree'],
            'timeline': ['date', 'when', 'chronology', 'sequence'],
            'financial': ['payment', 'amount', 'invoice', 'transaction'],
            'entity': ['company', 'person', 'director', 'shareholder'],
            'pattern': ['similar', 'repeated', 'consistent', 'trend']
        }
        
        if focus_lower in focus_terms:
            for term in focus_terms[focus_lower]:
                if term in content_lower:
                    score += 0.1
        
        # Critical markers
        if any(marker in content_lower for marker in ['critical', 'nuclear', 'smoking gun']):
            score += 0.3
        
        return min(1.0, score)
    
    def _get_overlap_docs(self, 
                         previous_docs: List[Dict],
                         overlap_days: int) -> List[Dict]:
        """Get documents from end of previous chunk for overlap"""
        
        # Simple implementation - take last 20% of documents
        overlap_count = max(1, len(previous_docs) // 5)
        return previous_docs[-overlap_count:]