# document_processor.py (COMPLETE FILE)
"""
Core document processing engine that handles phase-by-phase analysis.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from api_client import ClaudeAPIClient
from master_prompt import get_master_prompt
from phase_prompts import (
    get_phase_prompt, 
    update_learning_prompt, 
    get_learning_generator_prompt,
    should_generate_learning,
    get_phase_description,
    get_all_phases
)
from knowledge_manage import KnowledgeManager

class DocumentProcessor:
    """Processes documents through all analysis phases"""
    
    def __init__(self):
        """Initialise the document processor"""
        self.api_client = ClaudeAPIClient()
        self.knowledge_manage = KnowledgeManager()
        self.current_phase = None
        self.documents = []
        
    def load_documents(self, document_paths: List[str]) -> bool:
        """
        Load documents from file paths
        
        Args:
            document_paths: List of paths to document files
            
        Returns:
            Success status
        """
        try:
            self.documents = []
            for path in document_paths:
                with open(path, 'r', encoding='utf-8') as f:
                    self.documents.append({
                        'path': path,
                        'content': f.read(),
                        'filename': path.split('/')[-1]
                    })
            print(f"Loaded {len(self.documents)} documents successfully")
            return True
        except Exception as e:
            print(f"Error loading documents: {e}")
            return False
    
    def process_phase(self, phase_num: str, documents: Optional[List[Dict]] = None) -> Dict:
        """
        Process documents for a specific phase
        
        Args:
            phase_num: Phase identifier (0A, 0B, 1-7)
            documents: Optional document list (uses self.documents if not provided)
            
        Returns:
            Analysis results dictionary
        """
        print(f"\n{'='*60}")
        print(f"PROCESSING PHASE {phase_num}: {get_phase_description(phase_num)}")
        print(f"{'='*60}")
        
        self.current_phase = phase_num
        docs_to_process = documents or self.documents
        
        # Get previous knowledge for context
        previous_knowledge = self.knowledge_manage.get_previous_knowledge(phase_num)
        
        # 1. Get the master forensic overlay (always applied)
        master = get_master_prompt()
        
        # 2. Get phase-specific prompt (includes any learned components if re-running)
        phase_prompt = get_phase_prompt(phase_num)
        
        # 3. Combine prompts with previous knowledge
        full_prompt = self._build_full_prompt(master, phase_prompt, previous_knowledge)
        
        # 4. Prepare documents for analysis
        document_texts = [doc['content'] for doc in docs_to_process]
        
        print(f"Sending {len(document_texts)} documents for analysis...")
        
        # 5. Send to Claude for initial analysis
        response = self.api_client.analyse_documents(
            documents=document_texts,
            prompt=full_prompt,
            phase=phase_num,
            context=previous_knowledge
        )
        
        if not response:
            print(f"Error: No response received for phase {phase_num}")
            return {}
        
        # 6. For phases 1-6, generate and apply Claude's learning enhancement
        if should_generate_learning(phase_num):
            print(f"Generating autonomous enhancement for phase {phase_num}...")
            enhanced_response = self._apply_learning_enhancement(
                phase_num, 
                response, 
                docs_to_process, 
                previous_knowledge
            )
            
            # Combine both analyses
            final_response = {
                'initial_analysis': response,
                'enhanced_analysis': enhanced_response,
                'combined_insights': f"{response}\n\nENHANCED ANALYSIS:\n{enhanced_response}"
            }
        else:
            final_response = {
                'analysis': response
            }
        
        # 7. Store the knowledge
        phase_result = {
            'phase': phase_num,
            'description': get_phase_description(phase_num),
            'timestamp': datetime.now().isoformat(),
            'documents_analysed': len(docs_to_process),
            'findings': final_response
        }
        
        self.knowledge_manage.store_phase_knowledge(phase_num, phase_result)
        
        print(f"Phase {phase_num} complete. Knowledge stored.")
        
        return phase_result
    
    def _build_full_prompt(self, master: str, phase_prompt: str, previous_knowledge: Dict) -> str:
        """
        Build the complete prompt for analysis
        
        Args:
            master: Master forensic prompt
            phase_prompt: Phase-specific prompt
            previous_knowledge: Knowledge from previous phases
            
        Returns:
            Combined prompt string
        """
        prompt_parts = [
            master,
            "\nCURRENT PHASE FOCUS:",
            phase_prompt
        ]
        
        if previous_knowledge:
            prompt_parts.extend([
                "\nPREVIOUS PHASE KNOWLEDGE:",
                "You have access to the following insights from previous phases:"
            ])
            
            for phase, knowledge in previous_knowledge.items():
                phase_desc = get_phase_description(phase)
                prompt_parts.append(f"\n[{phase} - {phase_desc}]:")
                
                # Summarise key findings to avoid token overflow
                if isinstance(knowledge, dict) and 'findings' in knowledge:
                    findings = knowledge['findings']
                    if isinstance(findings, dict):
                        # Handle combined insights from enhanced phases
                        if 'combined_insights' in findings:
                            prompt_parts.append(findings['combined_insights'][:3000])
                        elif 'analysis' in findings:
                            prompt_parts.append(findings['analysis'][:3000])
                    else:
                        prompt_parts.append(str(findings)[:3000])
        
        prompt_parts.append("\nAnalyse the provided documents through both the master forensic lens "
                          "and the specific phase focus. Find what others would miss. "
                          "Be aggressive in identifying anything that damages Process Holdings' case.")
        
        return "\n".join(prompt_parts)
    
    def _apply_learning_enhancement(
        self, 
        phase_num: str, 
        initial_response: str, 
        documents: List[Dict], 
        previous_knowledge: Dict
    ) -> str:
        """
        Generate and apply Claude's self-generated enhancement
        
        Args:
            phase_num: Current phase
            initial_response: Initial analysis response
            documents: Documents being analysed
            previous_knowledge: Previous phase knowledge
            
        Returns:
            Enhanced analysis response
        """
        # Ask Claude to generate enhancement based on initial findings
        enhancement_prompt = f"""
        You just completed Phase {phase_num} analysis with these findings:
        {initial_response[:3000]}
        
        {get_learning_generator_prompt()}
        
        Be specific about:
        - Document references that need deeper investigation
        - Patterns you've detected that could be significant
        - Connections to previous phase findings
        - Areas where Process Holdings seems vulnerable
        """
        
        # Get Claude's self-generated enhancement
        learning = self.api_client.analyse_documents(
            documents=[],  # No documents needed for prompt generation
            prompt=enhancement_prompt,
            phase=f"{phase_num}_learning"
        )
        
        # Store the learning for future use
        update_learning_prompt(phase_num, learning)
        
        # Re-run the phase with enhancement
        master = get_master_prompt()
        enhanced_phase_prompt = get_phase_prompt(phase_num, include_learning=True)
        
        enhanced_full_prompt = f"""
        {master}
        
        ENHANCED PHASE FOCUS:
        {enhanced_phase_prompt}
        
        PREVIOUS PHASE KNOWLEDGE:
        {json.dumps(previous_knowledge, indent=2)[:5000]}
        
        This is your SECOND PASS with your own insights. Go deeper. Be more aggressive.
        Find the evidence that destroys Process Holdings' case.
        """
        
        # Get document texts
        document_texts = [doc['content'] for doc in documents]
        
        # Second, enhanced analysis
        enhanced_response = self.api_client.analyse_documents(
            documents=document_texts,
            prompt=enhanced_full_prompt,
            phase=f"{phase_num}_enhanced",
            context=previous_knowledge
        )
        
        return enhanced_response
    
    def run_full_analysis(self) -> Dict:
        """
        Run all phases in sequence
        
        Returns:
            Complete analysis results
        """
        print("\n" + "="*60)
        print("STARTING FULL ANALYSIS FOR LISMORE CAPITAL")
        print("="*60)
        
        all_phases = get_all_phases()
        results = {}
        
        for phase in all_phases:
            phase_result = self.process_phase(phase)
            results[phase] = phase_result
            
            # Brief pause between phases (optional)
            print(f"\nPhase {phase} complete. Moving to next phase...")
        
        print("\n" + "="*60)
        print("FULL ANALYSIS COMPLETE")
        print("="*60)
        
        # Generate summary
        summary = self.knowledge_manage.generate_summary()
        results['summary'] = summary
        
        return results
    
    def run_single_phase(self, phase_num: str) -> Dict:
        """
        Run a single phase
        
        Args:
            phase_num: Phase to run
            
        Returns:
            Phase results
        """
        return self.process_phase(phase_num)
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        return {
            'current_phase': self.current_phase,
            'documents_loaded': len(self.documents),
            'phases_completed': self.knowledge_manage.get_completed_phases(),
            'total_phases': len(get_all_phases())
        }