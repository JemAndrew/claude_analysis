"""
Manages cumulative knowledge across all phases of analysis.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import os

class KnowledgeManager:
    """Manages and retrieves knowledge accumulated across phases"""
    
    def __init__(self, storage_path: str = "./knowledge_store"):
        """
        Initialise knowledge manager
        
        Args:
            storage_path: Directory to store knowledge files
        """
        self.storage_path = storage_path
        self.knowledge_store = {}
        self.phase_order = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
        # Load any existing knowledge
        self._load_existing_knowledge()
    
    def store_phase_knowledge(self, phase: str, knowledge: Dict) -> bool:
        """
        Store knowledge from a phase
        
        Args:
            phase: Phase identifier
            knowledge: Knowledge dictionary to store
            
        Returns:
            Success status
        """
        try:
            # Store in memory
            self.knowledge_store[phase] = knowledge
            
            # Persist to disk
            filename = f"{self.storage_path}/phase_{phase}_knowledge.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, indent=2, default=str)
            
            print(f"Knowledge for phase {phase} stored successfully")
            return True
            
        except Exception as e:
            print(f"Error storing knowledge: {e}")
            return False
    
    def get_phase_knowledge(self, phase: str) -> Optional[Dict]:
        """
        Retrieve knowledge for a specific phase
        
        Args:
            phase: Phase identifier
            
        Returns:
            Knowledge dictionary or None if not found
        """
        return self.knowledge_store.get(phase)
    
    def get_previous_knowledge(self, current_phase: str) -> Dict:
        """
        Get all knowledge from phases before the current one
        
        Args:
            current_phase: Current phase identifier
            
        Returns:
            Dictionary of previous phase knowledge
        """
        previous = {}
        
        try:
            current_index = self.phase_order.index(current_phase)
            
            for phase in self.phase_order[:current_index]:
                if phase in self.knowledge_store:
                    previous[phase] = self.knowledge_store[phase]
                    
        except ValueError:
            print(f"Warning: Unknown phase {current_phase}")
        
        return previous
    
    def get_all_knowledge(self) -> Dict:
        """
        Get all stored knowledge
        
        Returns:
            Complete knowledge store
        """
        return self.knowledge_store
    
    def get_completed_phases(self) -> List[str]:
        """
        Get list of completed phases
        
        Returns:
            List of phase identifiers that have been completed
        """
        return list(self.knowledge_store.keys())
    
    def _load_existing_knowledge(self):
        """Load any existing knowledge from disk"""
        try:
            for phase in self.phase_order:
                filename = f"{self.storage_path}/phase_{phase}_knowledge.json"
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        self.knowledge_store[phase] = json.load(f)
                    print(f"Loaded existing knowledge for phase {phase}")
                    
        except Exception as e:
            print(f"Error loading existing knowledge: {e}")
    
    def clear_knowledge(self, phase: Optional[str] = None):
        """
        Clear stored knowledge
        
        Args:
            phase: Specific phase to clear, or None to clear all
        """
        if phase:
            # Clear specific phase
            if phase in self.knowledge_store:
                del self.knowledge_store[phase]
                
            filename = f"{self.storage_path}/phase_{phase}_knowledge.json"
            if os.path.exists(filename):
                os.remove(filename)
                
            print(f"Cleared knowledge for phase {phase}")
        else:
            # Clear all knowledge
            self.knowledge_store = {}
            
            for file in os.listdir(self.storage_path):
                if file.endswith('_knowledge.json'):
                    os.remove(os.path.join(self.storage_path, file))
                    
            print("Cleared all knowledge")
    
    def generate_summary(self) -> Dict:
        """
        Generate a summary of all accumulated knowledge
        
        Returns:
            Summary dictionary
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'phases_completed': self.get_completed_phases(),
            'key_findings': {},
            'critical_evidence': [],
            'smoking_guns': [],
            'next_steps': []
        }
        
        # Extract key findings from each phase
        for phase in self.get_completed_phases():
            knowledge = self.knowledge_store[phase]
            
            if 'findings' in knowledge:
                findings = knowledge['findings']
                
                # Extract key points based on phase
                if phase == "6":  # Smoking guns phase
                    summary['smoking_guns'] = self._extract_smoking_guns(findings)
                elif phase == "7":  # Autonomous phase
                    summary['next_steps'] = self._extract_next_steps(findings)
                
                # General key findings
                summary['key_findings'][phase] = self._extract_key_points(findings)
        
        return summary
    
    def _extract_key_points(self, findings: any) -> List[str]:
        """Extract key points from findings"""
        key_points = []
        
        # Handle different finding structures
        if isinstance(findings, dict):
            if 'combined_insights' in findings:
                # Extract from combined insights
                text = findings['combined_insights']
            elif 'analysis' in findings:
                text = findings['analysis']
            else:
                text = str(findings)
        else:
            text = str(findings)
        
        # Simple extraction of key sentences (you could make this smarter)
        sentences = text.split('.')[:5]  # First 5 sentences as key points
        key_points = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        return key_points
    
    def _extract_smoking_guns(self, findings: any) -> List[str]:
        """Extract smoking guns from phase 6 findings"""
        # This would be more sophisticated in production
        # Looking for specific keywords and patterns
        guns = []
        
        text = str(findings)
        if "smoking gun" in text.lower():
            # Extract sentences containing smoking gun references
            sentences = text.split('.')
            for sentence in sentences:
                if "smoking gun" in sentence.lower() or "kill shot" in sentence.lower():
                    guns.append(sentence.strip())
        
        return guns[:5]  # Return top 5
    
    def _extract_next_steps(self, findings: any) -> List[str]:
        """Extract recommended next steps from autonomous phase"""
        steps = []
        
        text = str(findings)
        # Look for action-oriented language
        action_keywords = ['investigate', 'examine', 'pursue', 'follow', 'analyse']
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in action_keywords):
                steps.append(sentence.strip())
        
        return steps[:5]  # Return top 5
    
    def export_knowledge(self, export_path: str = "./exports") -> str:
        """
        Export all knowledge to a single file
        
        Args:
            export_path: Directory for export
            
        Returns:
            Path to exported file
        """
        os.makedirs(export_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{export_path}/lismore_analysis_{timestamp}.json"
        
        export_data = {
            'case': 'Lismore Capital vs Process Holdings Ltd',
            'export_timestamp': datetime.now().isoformat(),
            'phases': self.knowledge_store,
            'summary': self.generate_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Knowledge exported to {filename}")
        return filename