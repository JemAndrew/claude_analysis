# api_client.py - Simple version with cost tracking
"""
Simplified Claude API client with cost tracking for Opus 4.1.
Tracks spending continuously and makes it easy to monitor costs.
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path='./config/.env')

class CostTracker:
    """Simple cost tracker that shows spending in real-time"""
    
    def __init__(self):
        """Initialise cost tracking"""
        self.costs_file = Path("./costs/cost_tracking.json")
        self.costs_file.parent.mkdir(exist_ok=True)
        
        # Pricing for models (in GBP per 1K tokens)
        self.model_pricing = {
            "claude-opus-4-1-20250805": {
                "input": 0.012,   # £0.012 per 1K input tokens
                "output": 0.060   # £0.060 per 1K output tokens
            },
            "claude-3-haiku-20240307": {
                "input": 0.0002,  # £0.0002 per 1K input tokens
                "output": 0.001   # £0.001 per 1K output tokens
            }
        }
        
        # Load existing costs or start fresh
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_history = []
        
        self._load_existing_costs()
    
    def _load_existing_costs(self):
        """Load any existing cost data"""
        if self.costs_file.exists():
            try:
                with open(self.costs_file, 'r') as f:
                    data = json.load(f)
                    self.total_cost = data.get('total_cost_gbp', 0.0)
                    self.total_input_tokens = data.get('total_input_tokens', 0)
                    self.total_output_tokens = data.get('total_output_tokens', 0)
                    self.call_history = data.get('calls', [])
                    
                    print(f"═══════════════════════════════════════")
                    print(f"  RESUMED SESSION - Current spend: £{self.total_cost:.4f}")
                    print(f"═══════════════════════════════════════")
            except:
                pass  # Start fresh if can't load
    
    def track_call(self, phase: str, model: str, input_tokens: int, output_tokens: int) -> Dict:
        """Track an API call and return cost info"""
        
        # Get pricing for this model
        pricing = self.model_pricing.get(model, self.model_pricing["claude-opus-4-1-20250805"])
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        call_cost = input_cost + output_cost
        
        # Update totals
        self.total_cost += call_cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        # Record this call
        call_data = {
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_gbp': round(call_cost, 6)
        }
        self.call_history.append(call_data)
        
        # Save immediately
        self._save_costs()
        
        # Print cost update
        print(f"\n💷 Cost Update:")
        print(f"   This call: £{call_cost:.4f} ({input_tokens:,} in / {output_tokens:,} out)")
        print(f"   Total spent: £{self.total_cost:.4f}")
        print(f"   Total tokens: {self.total_input_tokens + self.total_output_tokens:,}")
        
        return call_data
    
    def _save_costs(self):
        """Save cost data to file"""
        data = {
            'total_cost_gbp': round(self.total_cost, 4),
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'calls': self.call_history,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.costs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_phase_costs(self) -> Dict:
        """Get breakdown by phase"""
        breakdown = {}
        for call in self.call_history:
            phase = call['phase']
            if phase not in breakdown:
                breakdown[phase] = {'cost': 0, 'calls': 0}
            breakdown[phase]['cost'] += call['cost_gbp']
            breakdown[phase]['calls'] += 1
        
        return breakdown
    
    def print_summary(self):
        """Print a nice summary of costs"""
        print("\n" + "="*50)
        print("💷 COST TRACKING SUMMARY")
        print("="*50)
        print(f"Total Spent: £{self.total_cost:.4f}")
        print(f"Input Tokens: {self.total_input_tokens:,}")
        print(f"Output Tokens: {self.total_output_tokens:,}")
        print(f"Total API Calls: {len(self.call_history)}")
        
        # Phase breakdown
        phase_costs = self.get_phase_costs()
        if phase_costs:
            print("\nBy Phase:")
            for phase, data in sorted(phase_costs.items()):
                print(f"  {phase}: £{data['cost']:.4f} ({data['calls']} calls)")
        
        print("="*50)


class ClaudeAPIClient:
    """Simple API client with your settings"""
    
    def __init__(self, settings_path: str = "./config/settings.json"):
        """Initialise the API client"""
        
        # Load API key (already loaded at module level, but check again)
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            # Try one more time with explicit path
            load_dotenv(dotenv_path='./config/.env', override=True)
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if not self.api_key:
                print(f"Current working directory: {os.getcwd()}")
                print(f"Looking for .env at: {Path('./config/.env').absolute()}")
                print(f"File exists: {Path('./config/.env').exists()}")
                raise ValueError("No ANTHROPIC_API_KEY found in .env file")
        
        # Initialise Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Load settings
        if not settings_path:
            settings_path = Path("config/settings.json")
        
        # Load settings with proper error handling
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                self.settings = json.load(f)
        else:
            print("Warning: settings.json not found, using defaults")
            self.settings = {
                "investigation": {
                    "max_tokens": 4000,
                    "haiku_max_tokens": 2000
                },
                "model_config": {
                    "temperature": {
                        "phase_0a": 0.3,
                        "phase_0b": 0.3,
                        "phase_1": 0.3,
                        "phase_2": 0.3,
                        "phase_3": 0.3,
                        "phase_4": 0.4,
                        "phase_5": 0.4,
                        "phase_6": 0.5,
                        "phase_7": 0.7
                    },
                    "haiku_phases": ["phase_0a", "phase_0b", "phase_1"],
                    "opus_phases": ["phase_2", "phase_3", "phase_4", "phase_5", "phase_6", "phase_7"]
                }
            }
        
        # Get configuration
        self.investigation = self.settings['investigation']
        self.model_config = self.settings['model']
        self.opus_optimisations = self.settings.get('opus_41_optimizations', {})
        
        # Default model (Opus 4.1)
        self.opus_model = self.model_config['primary']['name']
        self.haiku_model = "claude-3-haiku-20240307"
        
        # Initialise cost tracker
        self.cost_tracker = CostTracker()
        
        print(f"\n✅ API Client Ready")
        print(f"   Primary Model: {self.opus_model}")
        print(f"   Project: {self.investigation['project_name']}")
    
    def analyse_documents(
        self,
        documents: List[str],
        prompt: str,
        context: Optional[Dict] = None,
        phase: Optional[str] = None
    ) -> str:
        """
        Analyse documents and track costs
        
        Args:
            documents: List of document texts
            prompt: The analysis prompt
            context: Previous phase knowledge
            phase: Current phase (e.g., 'phase_0a', 'phase_1')
            
        Returns:
            Response text from Claude
        """
        
        # Determine which model to use based on phase
        if phase in ['phase_0a', 'phase_0b', 'phase_1']:
            # Use cheaper Haiku model for these phases
            model = self.haiku_model
            max_tokens = 4096
            print(f"\n📊 Phase {phase}: Using Haiku (economy mode)")
        else:
            # Use Opus 4.1 for everything else
            model = self.opus_model
            max_tokens = self.settings['investigation']['max_tokens']
            print(f"\n🚀 Phase {phase}: Using Opus 4.1 (maximum power)")
        
        # Get temperature for this phase
        temperatures = self.model_config.get('temperature', {})
        temperature = temperatures.get(phase, 0.3) if phase else 0.3
        
        # Build the prompts
        system_prompt = self._build_system_prompt(phase)
        user_message = self._build_user_message(documents, prompt, context)
        
        try:
            print(f"   Calling API...")
            
            # Make the API call
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Track the costs
            self.cost_tracker.track_call(
                phase=phase or 'general',
                model=model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )
            
            return response.content[0].text
            
        except anthropic.RateLimitError:
            print("⏳ Rate limit hit - waiting 60 seconds...")
            time.sleep(60)
            return self.analyse_documents(documents, prompt, context, phase)
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def _build_system_prompt(self, phase: str) -> str:
        """Build adversarial system prompt"""
        return f"""You are a senior commercial litigation partner at a magic circle firm.
    You are conducting {phase} for LISMORE CAPITAL against Process Holdings.

    CRITICAL INSTRUCTIONS:
    - You work exclusively FOR Lismore - be ruthlessly adversarial
    - Find every weakness in Process Holdings' position
    - Identify document gaps as evidence of deliberate withholding
    - Write like you're preparing to destroy them at trial
    - Use British English and UK legal terminology
    - Be forensically aggressive - you're hunting for the kill shot

    Current phase: {phase}"""
    
    def _build_user_message(
        self,
        documents: List[str],
        prompt: str,
        context: Optional[Dict]
    ) -> str:
        """Build the user message"""
        
        message_parts = []
        
        # Add context if available
        if context:
            message_parts.append("KNOWLEDGE FROM PREVIOUS PHASES:")
            # Limit context to avoid token overflow
            context_str = json.dumps(context, indent=2)
            if len(context_str) > 10000:
                context_str = context_str[:10000] + "\n[...truncated...]"
            message_parts.append(context_str)
            message_parts.append("\n" + "="*50 + "\n")
        
        # Add documents
        message_parts.append("DOCUMENTS TO ANALYSE:")
        for i, doc in enumerate(documents, 1):
            message_parts.append(f"\n[DOCUMENT {i}]")
            # Truncate very long documents
            if len(doc) > 50000:
                doc = doc[:45000] + "\n\n[...document truncated for length...]\n\n" + doc[-5000:]
            message_parts.append(doc)
        
        # Add the analysis prompt
        message_parts.append("\n" + "="*50)
        message_parts.append("\nANALYSIS REQUIRED:")
        message_parts.append(prompt)
        
        return "\n".join(message_parts)
    
    def get_cost_summary(self):
        """Get a summary of costs"""
        self.cost_tracker.print_summary()
        return {
            'total_cost': self.cost_tracker.total_cost,
            'total_tokens': self.cost_tracker.total_input_tokens + self.cost_tracker.total_output_tokens,
            'phase_breakdown': self.cost_tracker.get_phase_costs()
        }
    
    def estimate_cost(self, text: str, phase: str = "phase_4") -> Dict:
        """Estimate the cost before making a call"""
        
        # Rough estimation: 1 token ≈ 4 characters
        estimated_input_tokens = len(text) // 4
        estimated_output_tokens = 3000  # Assume typical response
        
        # Determine model
        if phase in ['phase_0a', 'phase_0b', 'phase_1']:
            model = "claude-3-haiku-20240307"
            pricing = self.cost_tracker.model_pricing[model]
        else:
            model = self.opus_model
            pricing = self.cost_tracker.model_pricing["claude-opus-4-1-20250805"]
        
        input_cost = (estimated_input_tokens / 1000) * pricing["input"]
        output_cost = (estimated_output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        print(f"\n💰 COST ESTIMATE for {phase}:")
        print(f"   Model: {model}")
        print(f"   Est. Input: {estimated_input_tokens:,} tokens (£{input_cost:.4f})")
        print(f"   Est. Output: {estimated_output_tokens:,} tokens (£{output_cost:.4f})")
        print(f"   Est. Total: £{total_cost:.4f}")
        
        return {
            'model': model,
            'estimated_cost_gbp': round(total_cost, 4),
            'estimated_tokens': estimated_input_tokens + estimated_output_tokens
        }