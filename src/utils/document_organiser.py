#!/usr/bin/env python3
"""
Document Organiser - Helps Claude autonomously organise documents
British English throughout - Lismore v Process Holdings
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class DocumentOrganiser:
    """Manages Claude's autonomous document organisation"""
    
    def __init__(self, config):
        self.config = config
        self.organised_dir = config.organised_docs_dir
        self.organisation_structure = {}
    
    def create_organisation_structure(self, claude_response: str) -> Dict:
        """
        Parse Claude's organisation response into structure
        """
        
        structure = {
            'categories': [],
            'document_mappings': {},
            'created_at': datetime.now().isoformat()
        }
        
        # Parse Claude's response
        # This is a simplified parser - would need robust implementation
        categories = self._parse_categories(claude_response)
        
        for category in categories:
            structure['categories'].append(category)
            
            # Create directory for category
            category_dir = self.organised_docs_dir / self._sanitise_name(category['name'])
            category_dir.mkdir(parents=True, exist_ok=True)
        
        self.organisation_structure = structure
        return structure
    
    def organise_documents(self, documents: List[Dict], structure: Dict):
        """
        Physically organise documents based on structure
        """
        
        for category in structure['categories']:
            category_name = category['name']
            category_dir = self.organised_docs_dir / self._sanitise_name(category_name)
            
            # Get documents for this category
            doc_ids = category.get('documents', [])
            
            for doc_id in doc_ids:
                # Find document
                doc = self._find_document(documents, doc_id)
                if doc:
                    # Copy/link document to category folder
                    self._organise_document(doc, category_dir)
    
    def _parse_categories(self, response: str) -> List[Dict]:
        """
        Parse categories from Claude's response
        Simple implementation - would need enhancement
        """
        
        categories = []
        
        # Look for CATEGORY: markers
        import re
        category_blocks = re.findall(
            r'CATEGORY:\s*([^\n]+).*?DESCRIPTION:\s*([^\n]+).*?PRIORITY:\s*(\d+)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        for name, description, priority in category_blocks:
            categories.append({
                'name': name.strip(),
                'description': description.strip(),
                'priority': int(priority),
                'documents': []
            })
        
        return categories
    
    def _sanitise_name(self, name: str) -> str:
        """Sanitise category name for filesystem"""
        import re
        # Remove special characters
        sanitised = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with underscores
        sanitised = re.sub(r'[-\s]+', '_', sanitised)
        return sanitised.lower()
    
    def _find_document(self, documents: List[Dict], doc_id: str) -> Dict:
        """Find document by ID"""
        for doc in documents:
            if doc.get('id') == doc_id or doc.get('filename') == doc_id:
                return doc
        return None
    
    def _organise_document(self, doc: Dict, category_dir: Path):
        """Copy or link document to category directory"""
        
        source_path = doc.get('path')
        if not source_path or not Path(source_path).exists():
            return
        
        filename = Path(source_path).name
        dest_path = category_dir / filename
        
        # Create symlink if possible, otherwise copy
        try:
            if not dest_path.exists():
                dest_path.symlink_to(Path(source_path).absolute())
        except OSError:
            # Symlink failed, copy instead
            shutil.copy2(source_path, dest_path)
    
    def save_structure(self):
        """Save organisation structure to JSON"""
        structure_file = self.organised_docs_dir / "organisation_structure.json"
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(self.organisation_structure, f, indent=2, ensure_ascii=False)
    
    def load_structure(self) -> Dict:
        """Load organisation structure from JSON"""
        structure_file = self.organised_docs_dir / "organisation_structure.json"
        if structure_file.exists():
            with open(structure_file, 'r', encoding='utf-8') as f:
                self.organisation_structure = json.load(f)
                return self.organisation_structure
        return {}
    
    def get_documents_by_category(self, category_name: str) -> List[Path]:
        """Get all documents in a category"""
        category_dir = self.organised_docs_dir / self._sanitise_name(category_name)
        if not category_dir.exists():
            return []
        
        return list(category_dir.glob('*'))
    
    def get_category_summary(self) -> Dict:
        """Get summary of organisation"""
        summary = {
            'total_categories': len(self.organisation_structure.get('categories', [])),
            'categories': []
        }
        
        for category in self.organisation_structure.get('categories', []):
            category_dir = self.organised_docs_dir / self._sanitise_name(category['name'])
            doc_count = len(list(category_dir.glob('*'))) if category_dir.exists() else 0
            
            summary['categories'].append({
                'name': category['name'],
                'priority': category.get('priority', 0),
                'document_count': doc_count,
                'description': category.get('description', '')[:100]
            })
        
        # Sort by priority
        summary['categories'].sort(key=lambda x: x['priority'], reverse=True)
        
        return summary