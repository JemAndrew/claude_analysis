#!/usr/bin/env python3
"""
Tier 1: Claude Projects Knowledge Manager
Manages the 100 most critical documents in Claude Projects
British English throughout

Location: src/memory/tier1_project.py
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ProjectDocument:
    """Document in Claude Projects"""
    doc_id: str
    filename: str
    folder: str
    importance: int  # 1-10
    doc_type: str
    size_bytes: int
    hash: str
    upload_date: str
    last_referenced: str
    reference_count: int
    description: str


class ProjectKnowledgeManager:
    MAX_DOCS = 100
    """
    Manages Claude Projects integration (Tier 1)
    
    Claude Projects allow up to 100 documents to be permanently available
    in Claude's context WITHOUT token costs. This is MASSIVE for your case.
    
    Strategy:
        - Upload top 100 most critical documents
        - Maintain manifest of what's in Projects
        - Track usage to optimise document selection
        - Automatic rotation of less-used documents
    """
    
    def __init__(self, manifest_path: Path, config):
        """
        Initialise Project Knowledge Manager
        
        Args:
            manifest_path: Where to store the project manifest
            config: System configuration
        """
        self.manifest_path = Path(manifest_path)
        self.config = config
        
        # Manifest file
        self.manifest_file = self.manifest_path / "project_manifest.json"
        
        # Recommended documents list
        self.recommended_file = self.manifest_path / "recommended_100.json"
        
        # Load existing manifest
        self.manifest = self._load_manifest()
        
        # Maximum documents in Projects
        self.MAX_DOCS = 100
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load existing project manifest"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'documents': [],
            'total_docs': 0,
            'total_size_mb': 0,
            'slots_remaining': self.MAX_DOCS,
            'usage_stats': {}
        }
    
    def _save_manifest(self):
        """Save manifest to disk"""
        self.manifest['last_updated'] = datetime.now().isoformat()
        self.manifest['total_docs'] = len(self.manifest['documents'])
        self.manifest['slots_remaining'] = self.MAX_DOCS - self.manifest['total_docs']
        
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
    
    def add_to_project_manifest(self, 
                                doc_path: Path, 
                                doc_metadata: Dict[str, Any]) -> bool:
        """
        Add document to project manifest
        
        NOTE: This doesn't actually upload to Claude Projects (that's manual via UI)
        This tracks WHAT SHOULD BE in Projects for optimal performance
        
        Args:
            doc_path: Path to document
            doc_metadata: Document metadata (importance, type, etc.)
            
        Returns:
            True if added successfully
        """
        # Check if we have space
        if self.manifest['total_docs'] >= self.MAX_DOCS:
            # Need to rotate - remove least important/used document
            self._rotate_least_valuable()
        
        # Create document record
        doc_id = self._generate_doc_id(doc_path)
        
        doc_record = ProjectDocument(
            doc_id=doc_id,
            filename=doc_path.name,
            folder=doc_metadata.get('folder', 'unknown'),
            importance=doc_metadata.get('importance', 5),
            doc_type=doc_metadata.get('doc_type', 'unknown'),
            size_bytes=doc_path.stat().st_size if doc_path.exists() else 0,
            hash=self._calculate_hash(doc_path),
            upload_date=datetime.now().isoformat(),
            last_referenced=datetime.now().isoformat(),
            reference_count=0,
            description=doc_metadata.get('description', '')
        )
        
        # Add to manifest
        self.manifest['documents'].append(asdict(doc_record))
        self._save_manifest()
        
        return True
    
    def _rotate_least_valuable(self):
        """Remove least valuable document to make room"""
        if not self.manifest['documents']:
            return
        
        # Score each document by value
        scored_docs = []
        for doc in self.manifest['documents']:
            # Value = importance * log(reference_count + 1)
            import math
            value = doc['importance'] * math.log(doc['reference_count'] + 1)
            scored_docs.append((value, doc))
        
        # Sort by value (ascending)
        scored_docs.sort(key=lambda x: x[0])
        
        # Remove lowest value document
        removed_doc = scored_docs[0][1]
        self.manifest['documents'].remove(removed_doc)
        
        print(f"  [TIER 1] Rotated out: {removed_doc['filename']} (value: {scored_docs[0][0]:.2f})")
    
    def get_project_manifest(self) -> Dict[str, Any]:
        """
        Get current project manifest
        
        This tells the system what documents are available in Claude Projects
        """
        return {
            'total_docs': self.manifest['total_docs'],
            'slots_used': self.manifest['total_docs'],
            'slots_remaining': self.manifest['slots_remaining'],
            'document_list': [doc['filename'] for doc in self.manifest['documents']],
            'document_details': self.manifest['documents'],
            'total_size_mb': sum(doc['size_bytes'] for doc in self.manifest['documents']) / 1_000_000
        }
    
    def record_document_usage(self, doc_id: str):
        """Record that a document was referenced in a query"""
        for doc in self.manifest['documents']:
            if doc['doc_id'] == doc_id:
                doc['reference_count'] += 1
                doc['last_referenced'] = datetime.now().isoformat()
                break
        
        self._save_manifest()
    
    def get_recommended_100(self) -> List[Dict[str, Any]]:
        """
        Generate recommended top 100 documents for Claude Projects
        
        This analyses your entire document set and recommends which 100
        documents should be in Claude Projects for maximum benefit
        
        Returns:
            List of recommended documents with reasons
        """
        # This would analyse all documents and return top 100
        # For now, return the manifest as a guide
        
        recommendations = []
        
        # Sort by importance
        sorted_docs = sorted(
            self.manifest['documents'],
            key=lambda x: (x['importance'], x['reference_count']),
            reverse=True
        )
        
        for rank, doc in enumerate(sorted_docs[:self.MAX_DOCS], 1):
            recommendations.append({
                'rank': rank,
                'filename': doc['filename'],
                'folder': doc['folder'],
                'importance': doc['importance'],
                'reason': self._get_recommendation_reason(doc),
                'doc_type': doc['doc_type']
            })
        
        # Save recommendations
        with open(self.recommended_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        
        return recommendations
    
    def _get_recommendation_reason(self, doc: Dict) -> str:
        """Generate reason for recommending document"""
        reasons = []
        
        if doc['importance'] >= 9:
            reasons.append("Critical importance (9-10)")
        elif doc['importance'] >= 7:
            reasons.append("High importance (7-8)")
        
        if doc['reference_count'] > 10:
            reasons.append(f"Frequently referenced ({doc['reference_count']} times)")
        
        doc_type = doc['doc_type'].lower()
        if 'witness' in doc_type or 'statement' in doc_type:
            reasons.append("Key witness evidence")
        elif 'ruling' in doc_type or 'order' in doc_type:
            reasons.append("Tribunal ruling/order")
        elif 'claim' in doc_type or 'defence' in doc_type:
            reasons.append("Core pleading")
        
        return "; ".join(reasons) if reasons else "Strategic document"
    
    def generate_upload_instructions(self) -> str:
        """
        Generate instructions for uploading to Claude Projects
        
        Returns markdown instructions for manual upload
        """
        instructions = f"""
# Claude Projects Upload Instructions

## Documents to Upload ({self.manifest['total_docs']}/{self.MAX_DOCS} slots)

### How to Upload:
1. Go to Claude.ai
2. Open your "Lismore v Process Holdings" project
3. Click "Add Content" → "Upload Files"
4. Upload the following {self.manifest['total_docs']} documents:

### Priority 1: Critical Documents (Importance 9-10)
"""
        
        # Group by importance
        priority_1 = [d for d in self.manifest['documents'] if d['importance'] >= 9]
        priority_2 = [d for d in self.manifest['documents'] if 7 <= d['importance'] < 9]
        priority_3 = [d for d in self.manifest['documents'] if d['importance'] < 7]
        
        for doc in priority_1:
            instructions += f"- `{doc['folder']}/{doc['filename']}`\n"
        
        instructions += "\n### Priority 2: High Importance (7-8)\n"
        for doc in priority_2:
            instructions += f"- `{doc['folder']}/{doc['filename']}`\n"
        
        if priority_3:
            instructions += "\n### Priority 3: Supporting Documents\n"
            for doc in priority_3:
                instructions += f"- `{doc['folder']}/{doc['filename']}`\n"
        
        instructions += f"""

## Benefits:
- These {self.manifest['total_docs']} documents will be **permanently available** in all chats
- **Zero token cost** for these documents
- **Estimated savings: £{self._estimate_savings():.2f}** over the project lifecycle

## After Upload:
Run: `memory.tier1.verify_project_sync()` to confirm all documents are accessible
"""
        
        return instructions
    
    def _estimate_savings(self) -> float:
        """Estimate cost savings from Project documents"""
        # Assume each document averages 5000 tokens
        # Assume queried 50 times during project
        # Opus pricing: £15 per 1M input tokens
        
        avg_tokens_per_doc = 5000
        queries_per_project = 50
        
        total_tokens_saved = (
            len(self.manifest['documents']) * 
            avg_tokens_per_doc * 
            queries_per_project
        )
        
        cost_saved = (total_tokens_saved / 1_000_000) * 15
        return cost_saved
    
    def _generate_doc_id(self, doc_path: Path) -> str:
        """Generate unique document ID"""
        return hashlib.md5(str(doc_path).encode()).hexdigest()[:16]
    
    def _calculate_hash(self, doc_path: Path) -> str:
        """Calculate document hash for integrity checking"""
        if not doc_path.exists():
            return "FILE_NOT_FOUND"
        
        hasher = hashlib.sha256()
        with open(doc_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()[:16]
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 1 status"""
        return {
            'tier': 1,
            'name': 'Claude Projects',
            'active': True,
            'documents': self.manifest['total_docs'],
            'capacity': f"{self.manifest['total_docs']}/{self.MAX_DOCS}",
            'slots_remaining': self.manifest['slots_remaining'],
            'total_size_mb': round(
                sum(d['size_bytes'] for d in self.manifest['documents']) / 1_000_000, 
                2
            ),
            'estimated_savings': f"£{self._estimate_savings():.2f}"
        }
    
    def export_manifest_for_review(self) -> Path:
        """
        Export manifest in human-readable format for review
        
        Returns:
            Path to exported file
        """
        export_file = self.manifest_path / "project_manifest_review.md"
        
        content = "# Claude Projects Manifest\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        content += f"**Documents:** {self.manifest['total_docs']}/{self.MAX_DOCS}\n\n"
        
        content += "## Documents by Folder\n\n"
        
        # Group by folder
        by_folder = {}
        for doc in self.manifest['documents']:
            folder = doc['folder']
            if folder not in by_folder:
                by_folder[folder] = []
            by_folder[folder].append(doc)
        
        for folder in sorted(by_folder.keys()):
            content += f"### {folder}\n\n"
            for doc in sorted(by_folder[folder], key=lambda x: x['importance'], reverse=True):
                content += f"- **{doc['filename']}** (Importance: {doc['importance']}/10)\n"
                if doc['description']:
                    content += f"  - {doc['description']}\n"
            content += "\n"
        
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return export_file