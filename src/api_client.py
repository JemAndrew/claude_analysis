# api_client.py (SIMPLIFIED & ENHANCED)
import os
import anthropic
from typing import Dict, List, Optional
import time
import json
from datetime import datetime

class ClaudeAPIClient:
    """Simplified API client for Claude interactions"""
    
    def __init__(self):
        """Initialise API client with key from .env"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("No API key found in .env file")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  # or claude-3-sonnet for cost savings
        self.max_tokens = 4096
        self.temperature = 0.3  # Lower for more consistent legal analysis
        
    def analyse_documents(
        self, 
        documents: List[str], 
        prompt: str, 
        context: Optional[Dict] = None,
        phase: Optional[str] = None
    ) -> str:
        """
        Send documents for analysis with prompt and context
        
        Args:
            documents: List of document texts
            prompt: The analysis prompt
            context: Previous phase knowledge
            phase: Current phase identifier
        """
        try:
            # Construct message
            system_prompt = self._build_system_prompt(phase)
            user_message = self._build_user_message(documents, prompt, context)
            
            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Log for debugging (optional)
            self._log_interaction(phase, prompt, response)
            
            return response.content[0].text
            
        except anthropic.RateLimitError:
            print("Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return self.analyse_documents(documents, prompt, context, phase)
            
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def _build_system_prompt(self, phase: str) -> str:
        """Build system prompt with Lismore focus"""
        return f"""You are a senior commercial litigation partner analysing documents 
        for Lismore in a complex commercial dispute. Phase: {phase if phase else 'General'}
        
        Always:
        - Prioritise findings that support Lismore's position
        - Identify weaknesses in opposing party arguments
        - Flag any documentary irregularities or inconsistencies
        - Use UK legal terminology and standards
        - Be forensically thorough
        """
    
    def _build_user_message(
        self, 
        documents: List[str], 
        prompt: str, 
        context: Optional[Dict]
    ) -> str:
        """Construct the user message with documents and context"""
        message_parts = []
        
        # Add context if available
        if context:
            message_parts.append("PREVIOUS PHASE KNOWLEDGE:")
            message_parts.append(json.dumps(context, indent=2))
            message_parts.append("\n---\n")
        
        # Add documents
        message_parts.append("DOCUMENTS TO ANALYSE:")
        for i, doc in enumerate(documents, 1):
            message_parts.append(f"\n[DOCUMENT {i}]")
            message_parts.append(doc[:50000])  # Truncate if needed
        
        # Add prompt
        message_parts.append("\n---\nANALYSIS REQUIRED:")
        message_parts.append(prompt)
        
        return "\n".join(message_parts)
    
    def _log_interaction(self, phase: str, prompt: str, response: any):
        """Optional logging for debugging"""
        if os.getenv('DEBUG_MODE') == 'true':
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'phase': phase,
                'prompt_preview': prompt[:200],
                'response_preview': response.content[0].text[:200]
            }
            
            # Append to log file
            with open('api_interactions.log', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def generate_autonomous_prompt(self, phase_knowledge: Dict) -> str:
        """Let Claude generate its own analytical prompt based on learnings"""
        prompt = """Based on the knowledge accumulated so far, generate a focused 
        analytical prompt that would uncover additional insights beneficial to 
        Lismore's case. Focus on gaps, inconsistencies, or unexplored angles."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.5,  # Slightly higher for creativity
            messages=[
                {
                    "role": "user", 
                    "content": f"Knowledge so far: {json.dumps(phase_knowledge)}\n\n{prompt}"
                }
            ]
        )
        
        return response.content[0].text