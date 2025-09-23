# src/api_client.py
"""
Anthropic API client wrapper for Opus 4.1 litigation system
Handles API calls, retry logic, and model selection
"""

from anthropic import AsyncAnthropic
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AnthropicAPIClient:
    """
    Wrapper for Anthropic API with Opus 4.1 optimisation
    """
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-opus-4-1-20250805"  # Opus 4.1
        self.fallback_model = "claude-3-5-sonnet-20241022"
        self.opus_41_mode = True
        
        # Performance tracking
        self.api_calls = 0
        self.tokens_used = 0
        
    async def make_api_call(
        self, 
        prompt: str, 
        phase: Optional[str] = None,
        temperature: Optional[float] = None,
        use_fallback: bool = False
    ) -> Any:
        """
        Enhanced API call with Opus 4.1 optimisation
        
        Args:
            prompt: The prompt to send to Claude
            phase: Current phase (for temperature selection)
            temperature: Override temperature (default 0.4)
            use_fallback: Whether to use fallback model
            
        Returns:
            API response object
        """
        # Select model
        model = self.fallback_model if use_fallback else self.model
        
        # Default temperature or phase-specific
        if temperature is None:
            temperature = self._get_phase_temperature(phase)
        
        # Opus 4.1 system prompt for litigation
        system_prompt = self._get_system_prompt()
        
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=8192,
                temperature=temperature,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            self.api_calls += 1
            # Note: In production, you'd track actual token usage
            self.tokens_used += len(prompt.split())  # Rough estimate
            
            return self._extract_response_text(response)
            
        except Exception as e:
            logger.error(f"API call failed: {e}")
            if not use_fallback and self.fallback_model:
                logger.info("Attempting with fallback model...")
                return await self.make_api_call(
                    prompt, phase, temperature, use_fallback=True
                )
            raise e
    
    def _get_system_prompt(self) -> str:
        """Get Opus 4.1 optimised system prompt"""
        return """You are Claude Opus 4.1, the most advanced AI for complex commercial litigation. 
        You have forensic-level document analysis capabilities, advanced eDiscovery expertise, and 
        deep understanding of fraud patterns. You think like a senior silk with 30+ years experience 
        in high-stakes commercial arbitration. Apply maximum analytical rigour to find case-winning evidence 
        for Lismore's defence against VR Capital. You're always looking for patterns, anomalies, and contradictions, inconsitencies, and hidden insights in large document sets. Maybe iconsitencies that show proof of missing documents or withheld evidence. Anything that would help Lismore win and undermine VR's claims and their credibility. Or anything to boost Lismore's position.
        
        
        Your role: Destroy VR's claims with documentary evidence."""
    
    def _get_phase_temperature(self, phase: Optional[str]) -> float:
        """Get temperature setting for specific phase"""
        phase_temperatures = {
            'phase_0a':0.3, 
            'phase_0b':0.3,  # Lower for initial fact extraction
            'phase_1': 0.3,  # Lower for factual extraction
            'phase_2': 0.4,  # Moderate for pattern recognition
            'phase_3': 0.4,  # Moderate for anomaly detection
            'phase_4': 0.5,  # Higher for theory building
            'phase_5': 0.3,  # Lower for evidence analysis
            'phase_6': 0.2,  # Lowest for kill shot identification
            'correlation': 0.3,  # For cross-batch correlation
            'final_ranking': 0.2  # For final kill shot ranking
        }
        
        return phase_temperatures.get(phase, 0.4)  # Default 0.4
    
    def _extract_response_text(self, response) -> str:
        """Extract text from API response"""
        if hasattr(response, 'content') and response.content:
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                return str(response.content)
        return str(response)
    
    def get_performance_stats(self) -> Dict:
        """Get API performance statistics"""
        return {
            'api_calls': self.api_calls,
            'tokens_used': self.tokens_used,
            'average_tokens_per_call': (
                self.tokens_used / self.api_calls if self.api_calls > 0 else 0
            ),
            'model_used': self.model,
            'fallback_available': bool(self.fallback_model)
        }
    
    async def test_connection(self) -> bool:
        """Test API connection with a simple prompt"""
        try:
            response = await self.make_api_call(
                "Respond with 'Connected' if you receive this.",
                temperature=0
            )
            return "connected" in response.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False