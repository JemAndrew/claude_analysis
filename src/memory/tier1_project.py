#!/usr/bin/env python3
"""
Tier 1: Claude Projects Knowledge Manager
Manages manifest of permanent Claude Project documents
British English throughout

Location: src/memory/tier1_project.py

NOTE: Claude Projects are managed through Claude.ai UI
This manager tracks what should be in the project for £0/query access
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging


class ProjectKnowledgeManager:
    """
    Manages Tier 1: Claude Projects
    
    Purpose:
        - Track up to 100 most important documents
        - These documents are in Claude Project (free context)
        - £0 cost per query when using project knowledge
        - Permanent, always-available context
    
    Strategy:
        - Maintain manifest of documents in project
        - Categorise by type (case law, agreements, statements)
        - Track importance scoring
        - Provide guidance on what to add to project
    """
    
    def __init__(self, manifest_path: Path, config):
        """
        Initialise Project Knowledge Manager
        
        Args:
            manifest_path: Where to store project manifest
            config: System configuration
        """
        self.manifest_path = Path(manifest_path)
        self.config = config
        self.logger = logging.getLogger('ProjectKnowledge')
        
        # Create manifest directory
        self.manifest_path.mkdir(parents=True, exist_ok=True)
        
        # Manifest file
        self.manifest_file = self.manifest_path / "project_manifest.json"
        
        # Load or create manifest
        self.manifest = self._load_manifest()
        
        # Configuration
        self.max_capacity = 100  # Claude Project limit
        
        self.logger.info("Project Knowledge Manager initialised")
    
    def _load_manifest(self) -> Dict:
        """Load project knowledge manifest"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Create default manifest
        default_manifest = {
            'tier': 1,
            'name': 'Claude Projects (Permanent Context)',
            'capacity': 100,
            'cost_per_query': 0.0,
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'documents': [],
            'document_count': 0,
            'categories': {
                'case_law': {
                    'description': 'Legal precedents and statutes',
                    'documents': [],
                    'priority': 10
                },
                'agreements': {
                    'description': 'GSPA, P&ID contracts, key agreements',
                    'documents': [],
                    'priority': 10
                },
                'witness_statements': {
                    'description': 'Critical witness statements',
                    'documents': [],
                    'priority': 9
                },
                'expert_reports': {
                    'description': 'Expert analysis and valuations',
                    'documents': [],
                    'priority': 9
                },
                'key_correspondence': {
                    'description': 'Smoking gun emails and letters',
                    'documents': [],
                    'priority': 8
                },
                'tribunal_decisions': {
                    'description': 'Relevant arbitration awards',
                    'documents': [],
                    'priority': 10
                }
            },
            'recommendations': []
        }
        
        self._save_manifest(default_manifest)
        return default_manifest
    
    def _save_manifest(self, manifest: Dict = None):
        """Save manifest to file"""
        manifest = manifest or self.manifest
        manifest['last_updated'] = datetime.now().isoformat()
        manifest['document_count'] = len(manifest['documents'])
        
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def add_to_project_manifest(self, 
                                doc_path: Path, 
                                doc_metadata: Dict) -> bool:
        """
        Add document to project manifest (for tracking only)
        
        Args:
            doc_path: Path to document
            doc_metadata: Document metadata including importance
            
        Returns:
            True if added successfully
        """
        try:
            # Check capacity
            if len(self.manifest['documents']) >= self.max_capacity:
                self.logger.warning(f"Project at capacity ({self.max_capacity} docs)")
                return False
            
            # Build document entry
            doc_entry = {
                'filename': doc_path.name,
                'doc_id': doc_metadata.get('doc_id', doc_path.stem),
                'added_date': datetime.now().isoformat(),
                'importance': doc_metadata.get('importance', 5),
                'category': doc_metadata.get('category', 'general'),
                'classification': doc_metadata.get('classification', 'general'),
                'word_count': doc_metadata.get('word_count', 0)
            }
            
            # Add to appropriate category
            category = doc_entry['category']
            if category in self.manifest['categories']:
                self.manifest['categories'][category]['documents'].append(doc_entry)
            
            # Add to main document list
            self.manifest['documents'].append(doc_entry)
            
            self._save_manifest()
            
            self.logger.info(f"Added to manifest: {doc_path.name} (category: {category})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add to manifest: {e}")
            return False
    
    def recommend_for_project(self, 
                             all_documents: List[Dict],
                             max_recommendations: int = 100) -> List[Dict]:
        """
        Recommend which documents should be in Claude Project
        
        Args:
            all_documents: All available documents with metadata
            max_recommendations: Maximum documents to recommend
            
        Returns:
            List of recommended documents sorted by importance
        """
        recommendations = []
        
        for doc in all_documents:
            metadata = doc.get('metadata', {})
            
            # Calculate importance score
            importance = 0
            
            # Classification scoring
            classification = metadata.get('classification', 'general')
            if classification == 'contract':
                importance += 10
            elif classification == 'witness_statement':
                importance += 9
            elif classification == 'financial':
                importance += 7
            elif classification == 'correspondence':
                importance += 5
            
            # Entity scoring (documents with key entities)
            entities = metadata.get('entities', {})
            if entities.get('people') or entities.get('companies'):
                importance += 2
            
            # Date scoring (documents with dates important for timeline)
            if metadata.get('has_dates'):
                importance += 2
            
            # Amount scoring (financial docs)
            if metadata.get('has_amounts'):
                importance += 2
            
            # Add to recommendations
            if importance >= 5:  # Minimum threshold
                recommendations.append({
                    'filename': doc.get('filename'),
                    'doc_id': doc.get('id'),
                    'importance': importance,
                    'classification': classification,
                    'reason': self._generate_recommendation_reason(metadata, importance)
                })
        
        # Sort by importance
        recommendations.sort(key=lambda x: x['importance'], reverse=True)
        
        # Limit to max
        top_recommendations = recommendations[:max_recommendations]
        
        # Update manifest recommendations
        self.manifest['recommendations'] = top_recommendations
        self._save_manifest()
        
        return top_recommendations
    
    def _generate_recommendation_reason(self, 
                                       metadata: Dict, 
                                       importance: int) -> str:
        """Generate human-readable reason for recommendation"""
        classification = metadata.get('classification', 'general')
        
        reasons = []
        
        if classification == 'contract':
            reasons.append("Critical agreement document")
        elif classification == 'witness_statement':
            reasons.append("Key witness evidence")
        elif classification == 'financial':
            reasons.append("Financial evidence")
        
        if metadata.get('has_dates'):
            reasons.append("contains timeline evidence")
        
        if metadata.get('has_amounts'):
            reasons.append("contains financial amounts")
        
        entities = metadata.get('entities', {})
        if entities.get('people'):
            reasons.append(f"mentions key individuals")
        
        if not reasons:
            reasons.append("General importance")
        
        return "; ".join(reasons)
    
    def get_project_manifest(self) -> Dict:
        """Get current project manifest"""
        return self.manifest
    
    def export_for_upload(self, output_path: Path = None) -> Path:
        """
        Export list of documents that should be uploaded to Claude Project
        
        Args:
            output_path: Where to save the list
            
        Returns:
            Path to exported file
        """
        output_path = output_path or (self.manifest_path / "recommended_for_project.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("DOCUMENTS TO UPLOAD TO CLAUDE PROJECT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total recommendations: {len(self.manifest.get('recommendations', []))}\n")
            f.write(f"Project capacity: {self.max_capacity} documents\n\n")
            
            # Group by category
            for category, info in self.manifest['categories'].items():
                docs = info['documents']
                if docs:
                    f.write(f"\n{category.upper().replace('_', ' ')} ({len(docs)} documents)\n")
                    f.write("-" * 70 + "\n")
                    for doc in docs[:20]:  # Show first 20 per category
                        f.write(f"  • {doc['filename']} (importance: {doc['importance']})\n")
            
            # Add recommendations not yet in project
            if self.manifest.get('recommendations'):
                f.write("\n\nADDITIONAL RECOMMENDATIONS\n")
                f.write("-" * 70 + "\n")
                for rec in self.manifest['recommendations'][:50]:
                    if not any(d['filename'] == rec['filename'] for d in self.manifest['documents']):
                        f.write(f"  • {rec['filename']}\n")
                        f.write(f"    Importance: {rec['importance']}\n")
                        f.write(f"    Reason: {rec['reason']}\n\n")
        
        self.logger.info(f"Exported recommendations to {output_path}")
        return output_path
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """Get statistics by category"""
        stats = {}
        
        for category, info in self.manifest['categories'].items():
            docs = info['documents']
            stats[category] = {
                'count': len(docs),
                'priority': info['priority'],
                'description': info['description']
            }
        
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 1 status"""
        return {
            'tier': 1,
            'name': 'Claude Projects',
            'active': True,
            'documents': len(self.manifest['documents']),
            'capacity': self.max_capacity,
            'utilisation': f"{len(self.manifest['documents'])}/{self.max_capacity}",
            'cost_per_query': '£0.00',
            'categories': len([c for c, i in self.manifest['categories'].items() if i['documents']])
        }