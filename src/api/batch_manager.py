#!/usr/bin/env python3
"""
Batch Manager with Safe Adaptive Batching
Prevents 413 errors with conservative document-count-based batching
British English throughout
"""

from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import hashlib


class BatchManager:
    """Manages safe batching to prevent API overload"""
    
    def __init__(self, config):
        self.config = config
        self.batch_history = []
        self.auto_adjust_enabled = config.batch_strategy.get('auto_adjust', True)
        self.current_batch_sizes = {
            'phase_0': config.batch_strategy['phase_0_batch_size'],
            'tier_1': config.batch_strategy['tier_1_batch_size'],
            'tier_2': config.batch_strategy['tier_2_batch_size'],
            'tier_3': config.batch_strategy['tier_3_batch_size']
        }
    
    def create_safe_batches(self, 
                           documents: List[Dict], 
                           batch_type: str = 'tier_1',
                           max_docs_per_batch: int = None) -> List[List[Dict]]:
        """
        Create document-count-based batches (safer than token estimation)
        
        Args:
            documents: List of document dictionaries
            batch_type: Type of batch ('phase_0', 'tier_1', 'tier_2', 'tier_3')
            max_docs_per_batch: Override default batch size
        
        Returns:
            List of document batches
        """
        
        # Get batch size (use override or default)
        if max_docs_per_batch is None:
            max_docs_per_batch = self.current_batch_sizes.get(batch_type, 25)
        
        print(f"    Creating {batch_type} batches: {max_docs_per_batch} docs per batch")
        
        batches = []
        current_batch = []
        
        for doc in documents:
            current_batch.append(doc)
            
            if len(current_batch) >= max_docs_per_batch:
                batches.append(current_batch)
                current_batch = []
        
        # Add final batch
        if current_batch:
            batches.append(current_batch)
        
        # Record batch creation
        self.batch_history.append({
            'timestamp': datetime.now().isoformat(),
            'batch_type': batch_type,
            'total_documents': len(documents),
            'batch_count': len(batches),
            'docs_per_batch': max_docs_per_batch
        })
        
        print(f"    Created {len(batches)} batches from {len(documents)} documents")
        
        return batches
    
    def handle_413_error(self, batch_type: str):
        """
        Auto-reduce batch size when 413 error occurs
        """
        
        if not self.auto_adjust_enabled:
            return
        
        current_size = self.current_batch_sizes.get(batch_type, 25)
        new_size = max(5, int(current_size * 0.7))  # Reduce by 30%, minimum 5
        
        self.current_batch_sizes[batch_type] = new_size
        
        print(f"    ⚠️  413 Error: Reducing {batch_type} batch size from {current_size} to {new_size}")
        print(f"    Please restart the phase to use new batch size")
    
    def create_semantic_batches(self, 
                               documents: List[Dict],
                               strategy: str = 'semantic_clustering') -> List[List[Dict]]:
        """
        Create semantically-grouped batches (for phases that benefit from context)
        Still uses safe document counts
        """
        
        if strategy == 'chronological':
            return self._create_chronological_batches(documents)
        elif strategy == 'by_folder':
            return self._create_folder_batches(documents)
        else:
            # Default: simple safe batching
            return self.create_safe_batches(documents, batch_type='tier_1')
    
    def _create_chronological_batches(self, documents: List[Dict]) -> List[List[Dict]]:
        """Batch documents chronologically for timeline analysis"""
        
        # Sort by date if available
        sorted_docs = sorted(
            documents,
            key=lambda d: d.get('metadata', {}).get('date', '9999-12-31')
        )
        
        return self.create_safe_batches(sorted_docs, batch_type='tier_1')
    
    def _create_folder_batches(self, documents: List[Dict]) -> List[List[Dict]]:
        """Batch documents by source folder (keeps context together)"""
        
        # Group by folder
        by_folder = {}
        for doc in documents:
            folder = doc.get('metadata', {}).get('source_folder', 'unknown')
            if folder not in by_folder:
                by_folder[folder] = []
            by_folder[folder].append(doc)
        
        # Create batches per folder
        all_batches = []
        for folder, folder_docs in by_folder.items():
            folder_batches = self.create_safe_batches(folder_docs, batch_type='tier_1')
            all_batches.extend(folder_batches)
        
        return all_batches
    
    def estimate_total_batches(self, 
                              phase_0_docs: int,
                              tier_1_docs: int,
                              tier_2_docs: int) -> Dict:
        """
        Estimate total batches and cost for analysis
        
        Args:
            phase_0_docs: Number of Phase 0 documents
            tier_1_docs: Number of Tier 1 priority documents
            tier_2_docs: Number of Tier 2 remaining documents
        
        Returns:
            Dictionary with batch counts and cost estimates
        """
        
        phase_0_batches = (phase_0_docs + self.current_batch_sizes['phase_0'] - 1) // self.current_batch_sizes['phase_0']
        tier_1_batches = (tier_1_docs + self.current_batch_sizes['tier_1'] - 1) // self.current_batch_sizes['tier_1']
        tier_2_batches = (tier_2_docs + self.current_batch_sizes['tier_2'] - 1) // self.current_batch_sizes['tier_2']
        
        # Estimate tier 3 (assume 5% of tier 2 docs get flagged)
        tier_3_docs = int(tier_2_docs * 0.05)
        tier_3_batches = (tier_3_docs + self.current_batch_sizes['tier_3'] - 1) // self.current_batch_sizes['tier_3']
        
        total_batches = phase_0_batches + tier_1_batches + tier_2_batches + tier_3_batches
        
        # Cost estimation (rough)
        # Phase 0: Sonnet 4 (~£0.20/batch)
        # Tier 1: Sonnet 4 (~£0.20/batch)
        # Tier 2: Haiku 4 (~£0.05/batch)
        # Tier 3: Sonnet 4 (~£0.20/batch)
        
        estimated_cost = (
            (phase_0_batches * 0.20) +
            (tier_1_batches * 0.20) +
            (tier_2_batches * 0.05) +
            (tier_3_batches * 0.20)
        )
        
        return {
            'phase_0': {
                'documents': phase_0_docs,
                'batches': phase_0_batches,
                'cost_gbp': round(phase_0_batches * 0.20, 2)
            },
            'tier_1': {
                'documents': tier_1_docs,
                'batches': tier_1_batches,
                'cost_gbp': round(tier_1_batches * 0.20, 2)
            },
            'tier_2': {
                'documents': tier_2_docs,
                'batches': tier_2_batches,
                'cost_gbp': round(tier_2_batches * 0.05, 2)
            },
            'tier_3': {
                'documents': tier_3_docs,
                'batches': tier_3_batches,
                'cost_gbp': round(tier_3_batches * 0.20, 2)
            },
            'total_batches': total_batches,
            'estimated_cost_gbp': round(estimated_cost, 2),
            'estimated_hours': round(total_batches * 0.1, 1)  # ~6 minutes per batch
        }
    
    def get_batch_size_recommendation(self, 
                                     document_count: int,
                                     analysis_type: str) -> int:
        """
        Get recommended batch size based on document count and analysis type
        
        Args:
            document_count: Total number of documents
            analysis_type: 'deep' or 'metadata'
        
        Returns:
            Recommended batch size
        """
        
        if analysis_type == 'deep':
            # Deep analysis: smaller batches
            if document_count < 100:
                return 15
            elif document_count < 500:
                return 20
            else:
                return 25
        else:
            # Metadata scan: larger batches
            if document_count < 1000:
                return 50
            elif document_count < 5000:
                return 75
            else:
                return 100
    
    def get_statistics(self) -> Dict:
        """Get batching statistics"""
        
        total_docs_processed = sum(
            batch['total_documents'] 
            for batch in self.batch_history
        )
        
        total_batches_created = sum(
            batch['batch_count']
            for batch in self.batch_history
        )
        
        return {
            'batches_created': total_batches_created,
            'documents_processed': total_docs_processed,
            'current_batch_sizes': self.current_batch_sizes,
            'auto_adjust_enabled': self.auto_adjust_enabled,
            'recent_batches': self.batch_history[-10:] if self.batch_history else []
        }
    
    def reset_batch_sizes(self):
        """Reset batch sizes to defaults (use if adjustments were too aggressive)"""
        
        self.current_batch_sizes = {
            'phase_0': self.config.batch_strategy['phase_0_batch_size'],
            'tier_1': self.config.batch_strategy['tier_1_batch_size'],
            'tier_2': self.config.batch_strategy['tier_2_batch_size'],
            'tier_3': self.config.batch_strategy['tier_3_batch_size']
        }
        
        print("    ✅ Batch sizes reset to defaults")