#!/usr/bin/env python3
"""
Context Manager for Litigation Intelligence
Builds rich context from knowledge graph and document metadata
Enhanced with metadata context and investigation-specific features
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import hashlib
from collections import defaultdict


class ContextManager:
    """Manages context building for Claude API calls with metadata awareness"""
    
    def __init__(self, config):
        self.config = config
        self.context_cache = {}
        self.context_history = []
    
    def build_phase_context(self, 
                           phase: str,
                           knowledge_graph_context: Dict,
                           documents: List[Dict] = None,
                           previous_phases: List[str] = None) -> Dict[str, Any]:
        """
        Build comprehensive context for a specific phase
        Enhanced with document metadata and phase-specific optimisations
        """
        
        context = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'knowledge_state': knowledge_graph_context,
            'document_metadata': None,
            'previous_insights': None,
            'strategic_focus': None
        }
        
        # Add document metadata context if documents provided
        if documents:
            context['document_metadata'] = self.build_metadata_context(documents)
        
        # Add insights from previous phases
        if previous_phases:
            context['previous_insights'] = self._gather_previous_insights(previous_phases)
        
        # Add phase-specific strategic focus
        context['strategic_focus'] = self._get_phase_strategic_focus(phase)
        
        # Cache the context
        self._cache_context(phase, context)
        
        return context
    
    def build_investigation_context(self,
                                  investigation: Dict,
                                  relevant_docs: List[Dict],
                                  knowledge_graph_context: Dict) -> Dict[str, Any]:
        """
        Build context for investigation thread
        Enhanced with investigation-specific metadata and parent context
        """
        
        context = {
            'investigation_id': investigation.get('id'),
            'investigation_type': investigation.get('type'),
            'priority': investigation.get('priority', 5.0),
            'trigger_data': investigation.get('data', {}),
            'knowledge_state': knowledge_graph_context,
            'document_context': None,
            'metadata_summary': None,
            'investigation_history': None,
            'related_entities': None,
            'related_patterns': None
        }
        
        # Add document context with metadata
        if relevant_docs:
            context['document_context'] = self._build_investigation_document_context(
                relevant_docs, 
                investigation
            )
            context['metadata_summary'] = self.build_metadata_context(relevant_docs)
        
        # Add investigation lineage if this is a child investigation
        if investigation.get('data', {}).get('parent_id'):
            context['investigation_history'] = self._get_investigation_lineage(
                investigation['data']['parent_id']
            )
        
        # Extract related entities and patterns from trigger data
        context['related_entities'] = self._extract_related_entities(investigation)
        context['related_patterns'] = self._extract_related_patterns(investigation)
        
        # Add investigation-specific strategic guidance
        context['strategic_guidance'] = self._get_investigation_strategy(investigation)
        
        return context
    
    def build_metadata_context(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        NEW: Build context from document metadata
        Provides high-level view of document collection characteristics
        """
        
        if not documents:
            return {}
        
        context = {
            'total_documents': len(documents),
            'date_range': self._extract_date_range(documents),
            'key_entities': self._extract_key_entities(documents),
            'financial_summary': self._extract_financial_summary(documents),
            'document_types': self._extract_document_types(documents),
            'metadata_quality': self._assess_metadata_quality(documents),
            'content_patterns': self._identify_content_patterns(documents)
        }
        
        return context
    
    def build_synthesis_context(self,
                               phase_results: Dict[str, Any],
                               investigations: List[Dict],
                               knowledge_graph_export: Dict) -> Dict[str, Any]:
        """
        NEW: Build context for final synthesis
        Aggregates all intelligence for strategic narrative construction
        """
        
        context = {
            'phases_completed': list(phase_results.keys()),
            'total_investigations': len(investigations),
            'knowledge_summary': knowledge_graph_export.get('summary', {}),
            'critical_findings': knowledge_graph_export.get('critical_findings', [])[:20],
            'key_contradictions': knowledge_graph_export.get('key_contradictions', [])[:15],
            'strong_patterns': knowledge_graph_export.get('strong_patterns', [])[:15],
            'timeline_summary': self._build_timeline_summary(knowledge_graph_export),
            'entity_network': self._build_entity_network_summary(knowledge_graph_export),
            'strategic_advantages': self._identify_strategic_advantages(
                phase_results, 
                knowledge_graph_export
            ),
            'case_theory': self._construct_case_theory(knowledge_graph_export)
        }
        
        return context
    
    def build_recursive_context(self,
                               initial_analysis: str,
                               depth_level: int,
                               previous_questions: List[Dict] = None) -> Dict[str, Any]:
        """
        NEW: Build context for recursive self-questioning
        Tracks questioning depth and evolution
        """
        
        context = {
            'current_depth': depth_level,
            'max_depth': self.config.recursion_config.get('self_questioning_depth', 5),
            'initial_analysis_length': len(initial_analysis),
            'previous_questions_count': len(previous_questions) if previous_questions else 0,
            'questioning_history': previous_questions or [],
            'focus_areas': self._determine_focus_areas(initial_analysis, depth_level),
            'confidence_threshold': self._calculate_confidence_threshold(depth_level)
        }
        
        return context
    
    # ============================================================
    # HELPER METHODS - Metadata extraction and analysis
    # ============================================================
    
    def _extract_date_range(self, documents: List[Dict]) -> Dict[str, Any]:
        """Extract date range from document metadata"""
        
        all_dates = []
        
        for doc in documents:
            dates = doc.get('metadata', {}).get('dates_found', [])
            all_dates.extend(dates)
        
        if all_dates:
            all_dates.sort()
            return {
                'earliest': all_dates[0],
                'latest': all_dates[-1],
                'total_dates': len(all_dates),
                'date_density': len(all_dates) / len(documents) if documents else 0
            }
        
        return {'message': 'No dates found in metadata'}
    
    def _extract_key_entities(self, documents: List[Dict]) -> Dict[str, Any]:
        """Extract and rank key entities from metadata"""
        
        entity_counts = {
            'people': defaultdict(int),
            'companies': defaultdict(int),
            'emails': defaultdict(int)
        }
        
        for doc in documents:
            entities = doc.get('metadata', {}).get('entities', {})
            
            for person in entities.get('people', []):
                entity_counts['people'][person] += 1
            
            for company in entities.get('companies', []):
                entity_counts['companies'][company] += 1
            
            for email in entities.get('emails', []):
                entity_counts['emails'][email] += 1
        
        # Sort and limit to top entities
        key_entities = {}
        
        for entity_type in entity_counts:
            sorted_entities = sorted(
                entity_counts[entity_type].items(),
                key=lambda x: x[1],
                reverse=True
            )
            key_entities[entity_type] = [
                {'name': name, 'count': count} 
                for name, count in sorted_entities[:10]
            ]
        
        # Add priority entities if configured
        if hasattr(self.config, 'metadata_patterns'):
            priority_entities = self.config.metadata_patterns.get('priority_entities', [])
            key_entities['priority_present'] = [
                entity for entity in priority_entities
                if any(entity in str(doc.get('metadata', {}).get('entities', {})) 
                      for doc in documents)
            ]
        
        return key_entities
    
    def _extract_financial_summary(self, documents: List[Dict]) -> Dict[str, Any]:
        """Extract financial information summary from metadata"""
        
        all_amounts = []
        currency_symbols = defaultdict(int)
        
        for doc in documents:
            amounts = doc.get('metadata', {}).get('amounts_found', [])
            all_amounts.extend(amounts)
            
            # Count currency types
            content = doc.get('content', '')
            if '£' in content:
                currency_symbols['GBP'] += 1
            if '$' in content:
                currency_symbols['USD'] += 1
            if '€' in content:
                currency_symbols['EUR'] += 1
        
        if all_amounts:
            # Parse amounts to numbers (simplified)
            numeric_amounts = []
            for amount in all_amounts:
                try:
                    # Remove currency symbols and convert
                    clean_amount = ''.join(c for c in amount if c.isdigit() or c == '.')
                    if clean_amount:
                        numeric_amounts.append(float(clean_amount))
                except:
                    continue
            
            if numeric_amounts:
                return {
                    'total_amounts_found': len(all_amounts),
                    'unique_amounts': len(set(all_amounts)),
                    'max_amount': max(numeric_amounts),
                    'min_amount': min(numeric_amounts),
                    'avg_amount': sum(numeric_amounts) / len(numeric_amounts),
                    'primary_currency': max(currency_symbols.items(), key=lambda x: x[1])[0] if currency_symbols else 'Unknown'
                }
        
        return {'message': 'No financial information found in metadata'}
    
    def _extract_document_types(self, documents: List[Dict]) -> Dict[str, int]:
        """Extract document type distribution"""
        
        type_counts = defaultdict(int)
        
        for doc in documents:
            doc_type = doc.get('metadata', {}).get('classification', 'unknown')
            type_counts[doc_type] += 1
        
        return dict(type_counts)
    
    def _assess_metadata_quality(self, documents: List[Dict]) -> Dict[str, Any]:
        """Assess the quality and completeness of metadata"""
        
        quality_scores = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            score = 0
            
            # Score based on metadata completeness
            if metadata.get('has_dates'):
                score += 1
            if metadata.get('has_amounts'):
                score += 1
            if metadata.get('entities', {}).get('people'):
                score += 1
            if metadata.get('entities', {}).get('companies'):
                score += 1
            if metadata.get('classification') != 'general':
                score += 1
            if metadata.get('dates_found'):
                score += len(metadata['dates_found']) * 0.1
            if metadata.get('amounts_found'):
                score += len(metadata['amounts_found']) * 0.1
            
            quality_scores.append(min(10, score))
        
        if quality_scores:
            return {
                'average_quality': sum(quality_scores) / len(quality_scores),
                'high_quality_docs': len([s for s in quality_scores if s > 5]),
                'low_quality_docs': len([s for s in quality_scores if s < 3]),
                'quality_distribution': {
                    'excellent': len([s for s in quality_scores if s >= 8]),
                    'good': len([s for s in quality_scores if 5 <= s < 8]),
                    'fair': len([s for s in quality_scores if 3 <= s < 5]),
                    'poor': len([s for s in quality_scores if s < 3])
                }
            }
        
        return {'message': 'No documents to assess'}
    
    def _identify_content_patterns(self, documents: List[Dict]) -> Dict[str, Any]:
        """Identify patterns in document content from metadata"""
        
        patterns = {
            'temporal_clusters': [],
            'entity_clusters': [],
            'document_relationships': []
        }
        
        # Temporal clustering
        date_counts = defaultdict(int)
        for doc in documents:
            for date in doc.get('metadata', {}).get('dates_found', [])[:5]:
                date_counts[date] += 1
        
        # Find dates mentioned multiple times
        patterns['temporal_clusters'] = [
            {'date': date, 'frequency': count}
            for date, count in sorted(date_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            if count > 1
        ]
        
        # Entity clustering
        entity_cooccurrence = defaultdict(int)
        for doc in documents:
            entities = doc.get('metadata', {}).get('entities', {})
            people = entities.get('people', [])
            
            # Count co-occurrences
            for i, person1 in enumerate(people):
                for person2 in people[i+1:]:
                    pair = tuple(sorted([person1, person2]))
                    entity_cooccurrence[pair] += 1
        
        # Find frequently co-occurring entities
        patterns['entity_clusters'] = [
            {'entities': list(pair), 'frequency': count}
            for pair, count in sorted(entity_cooccurrence.items(), key=lambda x: x[1], reverse=True)[:10]
            if count > 1
        ]
        
        return patterns
    
    # ============================================================
    # INVESTIGATION-SPECIFIC METHODS
    # ============================================================
    
    def _build_investigation_document_context(self, 
                                            documents: List[Dict],
                                            investigation: Dict) -> Dict[str, Any]:
        """Build document context specific to investigation"""
        
        investigation_type = investigation.get('type', '')
        
        context = {
            'document_count': len(documents),
            'relevance_distribution': self._calculate_relevance_distribution(
                documents, 
                investigation
            )
        }
        
        # Add investigation-specific document insights
        if 'contradiction' in investigation_type:
            context['contradiction_evidence'] = self._extract_contradiction_evidence(
                documents, 
                investigation
            )
        elif 'financial' in investigation_type:
            context['financial_evidence'] = self._extract_financial_evidence(
                documents, 
                investigation
            )
        elif 'timeline' in investigation_type:
            context['temporal_evidence'] = self._extract_temporal_evidence(
                documents, 
                investigation
            )
        
        return context
    
    def _calculate_relevance_distribution(self, 
                                         documents: List[Dict],
                                         investigation: Dict) -> Dict[str, int]:
        """Calculate relevance distribution of documents"""
        
        relevance_scores = {
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for doc in documents:
            # Use batch manager's relevance calculation if available
            if hasattr(self.config, 'batch_manager'):
                score = self.config.batch_manager._calculate_investigation_relevance(
                    doc, 
                    investigation['type'], 
                    investigation.get('data', {})
                )
            else:
                # Simple relevance scoring
                score = 1.0
            
            if score > 3.0:
                relevance_scores['high'] += 1
            elif score > 1.0:
                relevance_scores['medium'] += 1
            else:
                relevance_scores['low'] += 1
        
        return relevance_scores
    
    def _extract_contradiction_evidence(self, 
                                       documents: List[Dict],
                                       investigation: Dict) -> List[Dict]:
        """Extract evidence relevant to contradiction investigation"""
        
        evidence = []
        investigation_data = investigation.get('data', {})
        
        for doc in documents:
            doc_evidence = {
                'document_id': doc.get('id', 'unknown'),
                'relevant_dates': [],
                'relevant_entities': [],
                'relevant_statements': []
            }
            
            # Extract relevant dates
            doc_evidence['relevant_dates'] = doc.get('metadata', {}).get('dates_found', [])[:5]
            
            # Extract relevant entities
            entities = doc.get('metadata', {}).get('entities', {})
            doc_evidence['relevant_entities'] = (
                entities.get('people', [])[:3] + 
                entities.get('companies', [])[:2]
            )
            
            evidence.append(doc_evidence)
        
        return evidence[:10]  # Top 10 documents
    
    def _extract_financial_evidence(self, 
                                   documents: List[Dict],
                                   investigation: Dict) -> Dict[str, Any]:
        """Extract financial evidence for investigation"""
        
        all_amounts = []
        
        for doc in documents:
            amounts = doc.get('metadata', {}).get('amounts_found', [])
            all_amounts.extend(amounts)
        
        return {
            'total_financial_references': len(all_amounts),
            'unique_amounts': len(set(all_amounts)),
            'amounts': all_amounts[:20]  # Top 20 amounts
        }
    
    def _extract_temporal_evidence(self, 
                                  documents: List[Dict],
                                  investigation: Dict) -> Dict[str, Any]:
        """Extract temporal evidence for timeline investigation"""
        
        all_dates = []
        
        for doc in documents:
            dates = doc.get('metadata', {}).get('dates_found', [])
            all_dates.extend(dates)
        
        # Sort dates
        all_dates.sort()
        
        return {
            'date_range': {
                'earliest': all_dates[0] if all_dates else None,
                'latest': all_dates[-1] if all_dates else None
            },
            'total_dates': len(all_dates),
            'unique_dates': len(set(all_dates)),
            'date_list': list(set(all_dates))[:30]  # Top 30 unique dates
        }
    
    # ============================================================
    # STRATEGIC CONTEXT METHODS
    # ============================================================
    
    def _get_phase_strategic_focus(self, phase: str) -> Dict[str, Any]:
        """Get strategic focus for specific phase"""
        
        phase_strategies = {
            '0': {
                'focus': 'Knowledge absorption',
                'priorities': ['Legal framework', 'Case context', 'Key entities'],
                'output': 'Comprehensive legal and contextual understanding'
            },
            '1': {
                'focus': 'Discovery sweep',
                'priorities': ['Pattern identification', 'Entity mapping', 'Timeline construction'],
                'output': 'Initial evidence landscape'
            },
            '2': {
                'focus': 'Timeline analysis',
                'priorities': ['Temporal sequencing', 'Impossibility detection', 'Critical events'],
                'output': 'Chronological narrative'
            },
            '3': {
                'focus': 'Contradiction hunting',
                'priorities': ['Statement conflicts', 'Logical inconsistencies', 'Credibility issues'],
                'output': 'Contradiction matrix'
            },
            '4': {
                'focus': 'Pattern recognition',
                'priorities': ['Behavioural patterns', 'Financial patterns', 'Communication patterns'],
                'output': 'Pattern catalogue'
            },
            '5': {
                'focus': 'Entity relationship mapping',
                'priorities': ['Hidden connections', 'Control structures', 'Conflicts of interest'],
                'output': 'Entity network graph'
            },
            '6': {
                'focus': 'Financial forensics',
                'priorities': ['Valuation analysis', 'Payment flows', 'Hidden transactions'],
                'output': 'Financial evidence dossier'
            },
            '7': {
                'focus': 'Strategic synthesis',
                'priorities': ['Narrative construction', 'Evidence prioritisation', 'Case theory'],
                'output': 'Litigation strategy'
            }
        }
        
        return phase_strategies.get(phase, {
            'focus': 'General investigation',
            'priorities': ['Evidence gathering'],
            'output': 'Analysis results'
        })
    
    def _get_investigation_strategy(self, investigation: Dict) -> Dict[str, Any]:
        """Get strategic guidance for investigation"""
        
        investigation_type = investigation.get('type', '')
        priority = investigation.get('priority', 5.0)
        
        strategy = {
            'urgency': 'critical' if priority > 8 else 'high' if priority > 6 else 'normal',
            'depth': 'exhaustive' if priority > 8 else 'deep' if priority > 6 else 'standard',
            'focus_areas': [],
            'success_criteria': []
        }
        
        if 'contradiction' in investigation_type:
            strategy['focus_areas'] = [
                'Document authenticity',
                'Timeline validation',
                'Witness credibility'
            ]
            strategy['success_criteria'] = [
                'Resolve contradiction',
                'Identify deception',
                'Find supporting evidence'
            ]
        elif 'financial' in investigation_type:
            strategy['focus_areas'] = [
                'Transaction tracking',
                'Valuation analysis',
                'Hidden payments'
            ]
            strategy['success_criteria'] = [
                'Trace money flow',
                'Identify beneficiaries',
                'Quantify damages'
            ]
        
        return strategy
    
    def _extract_related_entities(self, investigation: Dict) -> List[str]:
        """Extract entities related to investigation"""
        
        entities = []
        investigation_data = investigation.get('data', {})
        
        # Extract from trigger data
        if 'entity' in investigation_data:
            entity_info = investigation_data['entity']
            if isinstance(entity_info, dict):
                entities.append(entity_info.get('name', ''))
        
        # Extract from other fields
        for key in ['entities', 'people', 'companies']:
            if key in investigation_data:
                value = investigation_data[key]
                if isinstance(value, list):
                    entities.extend(value)
                elif isinstance(value, str):
                    entities.append(value)
        
        return list(set(filter(None, entities)))[:10]
    
    def _extract_related_patterns(self, investigation: Dict) -> List[str]:
        """Extract patterns related to investigation"""
        
        patterns = []
        investigation_data = investigation.get('data', {})
        
        # Extract pattern information
        if 'pattern' in investigation_data:
            pattern_info = investigation_data['pattern']
            if isinstance(pattern_info, dict):
                patterns.append(pattern_info.get('description', ''))
        
        return list(filter(None, patterns))
    
    # ============================================================
    # SYNTHESIS AND SUMMARY METHODS
    # ============================================================
    
    def _build_timeline_summary(self, knowledge_graph_export: Dict) -> Dict[str, Any]:
        """Build timeline summary from knowledge graph export"""
        
        # This would parse timeline events from export
        return {
            'event_count': 0,
            'date_range': {},
            'critical_events': []
        }
    
    def _build_entity_network_summary(self, knowledge_graph_export: Dict) -> Dict[str, Any]:
        """Build entity network summary"""
        
        return {
            'total_entities': knowledge_graph_export.get('summary', {}).get('entities', 0),
            'total_relationships': knowledge_graph_export.get('summary', {}).get('relationships', 0),
            'key_players': []
        }
    
    def _identify_strategic_advantages(self, 
                                      phase_results: Dict,
                                      knowledge_graph_export: Dict) -> List[str]:
        """Identify strategic advantages from analysis"""
        
        advantages = []
        
        # Check for critical discoveries
        if knowledge_graph_export.get('critical_findings'):
            advantages.append('Multiple critical discoveries providing strong evidence')
        
        # Check for contradictions
        contradictions = knowledge_graph_export.get('key_contradictions', [])
        if len(contradictions) > 5:
            advantages.append(f'{len(contradictions)} major contradictions undermining their credibility')
        
        # Check for patterns
        patterns = knowledge_graph_export.get('strong_patterns', [])
        if patterns:
            advantages.append(f'{len(patterns)} established patterns demonstrating systematic behaviour')
        
        return advantages
    
    def _construct_case_theory(self, knowledge_graph_export: Dict) -> str:
        """Construct preliminary case theory from evidence"""
        
        # This would analyse the export to build a theory
        return "Case theory based on discovered evidence and patterns"
    
    def _determine_focus_areas(self, analysis: str, depth: int) -> List[str]:
        """Determine focus areas for recursive questioning"""
        
        base_areas = [
            'hidden assumptions',
            'alternative explanations',
            'missing evidence',
            'strategic implications'
        ]
        
        # Add depth-specific areas
        if depth > 3:
            base_areas.extend([
                'systemic patterns',
                'conspiracy indicators',
                'financial motivations'
            ])
        
        return base_areas
    
    def _calculate_confidence_threshold(self, depth: int) -> float:
        """Calculate confidence threshold for depth level"""
        
        # Higher depth requires higher confidence
        base_threshold = 0.6
        depth_adjustment = depth * 0.05
        
        return min(0.95, base_threshold + depth_adjustment)
    
    # ============================================================
    # CACHING AND HISTORY METHODS
    # ============================================================
    
    def _cache_context(self, identifier: str, context: Dict):
        """Cache context for reuse"""
        
        self.context_cache[identifier] = {
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        # Keep cache size limited
        if len(self.context_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(
                self.context_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            self.context_cache = dict(sorted_cache[-50:])
    
    def _gather_previous_insights(self, previous_phases: List[str]) -> Dict[str, Any]:
        """Gather insights from previous phases"""
        
        insights = {}
        
        for phase in previous_phases:
            if phase in self.context_cache:
                cached = self.context_cache[phase]
                insights[phase] = {
                    'timestamp': cached['timestamp'],
                    'key_findings': cached.get('context', {}).get('strategic_focus', {})
                }
        
        return insights
    
    def _get_investigation_lineage(self, parent_id: str) -> List[Dict]:
        """Get investigation lineage from parent"""
        
        # This would query the knowledge graph for parent investigations
        return [{'parent_id': parent_id, 'lineage': 'Available in knowledge graph'}]
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """Get statistics about context usage"""
        
        return {
            'cached_contexts': len(self.context_cache),
            'context_history_length': len(self.context_history),
            'cache_hit_rate': 0.0  # Would need to track this
        }