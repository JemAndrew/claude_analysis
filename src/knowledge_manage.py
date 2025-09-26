#!/usr/bin/env python3
"""
Simple Knowledge Manager
Stores and retrieves phase knowledge without complexity
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class KnowledgeManager:
    """Simple storage and retrieval of phase knowledge"""
    
    def __init__(self, storage_path: str = "knowledge_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Phase order for reference
        self.phase_order = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
    
    def store_phase(self, phase: str, results: Dict[str, Any]) -> None:
        """
        Store phase results without truncation
        
        Args:
            phase: Phase identifier
            results: Complete results from document processor
        """
        
        # Create phase file path
        phase_file = self.storage_path / f"phase_{phase}.json"
        
        # Store complete results - NO TRUNCATION
        knowledge = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'synthesis': results.get('synthesis', ''),          # Full synthesis text
            'self_ask': results.get('self_ask', ''),           # Full self-ask text
            'documents_analysed': results.get('documents_analysed', 0),
            'batch_count': len(results.get('batch_responses', [])),
        }
        
        # Save to file
        try:
            with open(phase_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Stored Phase {phase} knowledge ({len(knowledge['synthesis'])} chars)")
            
        except Exception as e:
            print(f"⚠️ Error storing Phase {phase}: {e}")
    
    def get_phase(self, phase: str) -> Optional[Dict[str, Any]]:
        """
        Get knowledge for a specific phase
        
        Args:
            phase: Phase identifier
            
        Returns:
            Complete phase knowledge or None if not found
        """
        
        phase_file = self.storage_path / f"phase_{phase}.json"
        
        if not phase_file.exists():
            return None
        
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading Phase {phase}: {e}")
            return None
    
    def get_previous_phases(self, current_phase: str) -> Dict[str, Dict]:
        """
        Get all knowledge from phases before the current one
        
        Args:
            current_phase: Current phase identifier
            
        Returns:
            Dictionary of previous phase knowledge
        """
        
        previous = {}
        
        try:
            # Find current phase index
            current_idx = self.phase_order.index(current_phase)
            
            # Load all previous phases
            for phase in self.phase_order[:current_idx]:
                knowledge = self.get_phase(phase)
                if knowledge:
                    previous[phase] = knowledge
                    
        except ValueError:
            # Current phase not in order list
            print(f"⚠️ Unknown phase: {current_phase}")
        
        return previous
    
    def get_all_phases(self) -> Dict[str, Dict]:
        """
        Get all stored phase knowledge
        
        Returns:
            Dictionary of all phase knowledge
        """
        
        all_phases = {}
        
        for phase in self.phase_order:
            knowledge = self.get_phase(phase)
            if knowledge:
                all_phases[phase] = knowledge
        
        return all_phases
    
    def get_phase_summary(self, phase: str) -> Optional[str]:
        """
        Get a brief summary of a phase's findings
        
        Args:
            phase: Phase identifier
            
        Returns:
            Brief summary string or None
        """
        
        knowledge = self.get_phase(phase)
        
        if not knowledge:
            return None
        
        synthesis = knowledge.get('synthesis', '')
        
        # Return first 500 characters as summary
        if synthesis:
            return synthesis[:500] + "..." if len(synthesis) > 500 else synthesis
        
        return "No synthesis available"
    
    def clear(self, phase: Optional[str] = None) -> None:
        """
        Clear stored knowledge
        
        Args:
            phase: Specific phase to clear, or None to clear all
        """
        
        if phase:
            # Clear specific phase
            phase_file = self.storage_path / f"phase_{phase}.json"
            if phase_file.exists():
                try:
                    phase_file.unlink()
                    print(f"🗑️ Cleared Phase {phase}")
                except Exception as e:
                    print(f"⚠️ Error clearing Phase {phase}: {e}")
        else:
            # Clear all phases
            cleared = 0
            for phase in self.phase_order:
                phase_file = self.storage_path / f"phase_{phase}.json"
                if phase_file.exists():
                    try:
                        phase_file.unlink()
                        cleared += 1
                    except Exception as e:
                        print(f"⚠️ Error clearing Phase {phase}: {e}")
            
            if cleared > 0:
                print(f"🗑️ Cleared {cleared} phases")
            else:
                print("No phases to clear")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored knowledge
        
        Returns:
            Dictionary of statistics
        """
        
        stats = {
            'phases_completed': [],
            'total_synthesis_chars': 0,
            'total_documents_analysed': 0,
            'storage_size_bytes': 0
        }
        
        for phase in self.phase_order:
            phase_file = self.storage_path / f"phase_{phase}.json"
            
            if phase_file.exists():
                stats['phases_completed'].append(phase)
                
                knowledge = self.get_phase(phase)
                if knowledge:
                    stats['total_synthesis_chars'] += len(knowledge.get('synthesis', ''))
                    stats['total_documents_analysed'] += knowledge.get('documents_analysed', 0)
                
                # Add file size
                stats['storage_size_bytes'] += phase_file.stat().st_size
        
        # Convert bytes to human-readable
        size_bytes = stats['storage_size_bytes']
        if size_bytes < 1024:
            stats['storage_size'] = f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            stats['storage_size'] = f"{size_bytes / 1024:.1f} KB"
        else:
            stats['storage_size'] = f"{size_bytes / (1024 * 1024):.1f} MB"
        
        return stats