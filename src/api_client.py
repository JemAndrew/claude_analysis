# api_client.py - FIXED VERSION with correct settings access
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
    
    def track_call(self, phase: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track an API call and return cost"""
        
        # Calculate cost
        pricing = self.model_pricing.get(model, self.model_pricing["claude-opus-4-1-20250805"])
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Update totals
        self.total_cost += total_cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        # Add to history
        self.call_history.append({
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_gbp': total_cost
        })
        
        # Display cost info
        model_name = "Haiku" if "haiku" in model else "Opus 4.1"
        print(f"   💰 Cost: £{total_cost:.4f} ({model_name}: {input_tokens:,} in, {output_tokens:,} out)")
        print(f"   📊 Total spend so far: £{self.total_cost:.4f}")
        
        # Save costs to disk
        self.save_costs()
        
        return total_cost
    
    def save_costs(self):
        """Save current costs to file"""
        with open(self.costs_file, 'w') as f:
            json.dump({
                'total_cost_gbp': self.total_cost,
                'total_input_tokens': self.total_input_tokens,
                'total_output_tokens': self.total_output_tokens,
                'calls': self.call_history
            }, f, indent=2)
    
    def get_phase_costs(self) -> Dict:
        """Get cost breakdown by phase"""
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
    
    def __init__(self, api_key: Optional[str] = None, settings_path: str = "./config/settings.json"):
        """Initialise the API client - FIXED to handle both api_key and settings_path"""
        
        # Load API key (use provided or get from environment)
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            # Try loading from .env
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
        settings_path = Path(settings_path)
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                self.settings = json.load(f)
        else:
            print(f"Warning: settings.json not found at {settings_path}, using defaults")
            self.settings = self._get_default_settings()
        
        # FIXED: Correct access to settings structure
        self.investigation = self.settings['investigation']
        self.model_config = self.settings['model']  # ✅ CORRECT - it's 'model' not 'model_config'
        self.litigation_strategy = self.settings.get('litigation_strategy', {})
        self.api_config = self.settings.get('api', {})
        
        # Model names
        self.opus_model = self.model_config['primary']['name']
        self.haiku_model = self.model_config['secondary']['name']
        
        # Initialise cost tracker
        self.cost_tracker = CostTracker()
        
        print(f"\n✅ API Client Ready")
        print(f"   Primary Model: {self.opus_model}")
        print(f"   Secondary Model: {self.haiku_model}")
        print(f"   Project: {self.investigation['project_name']}")
    
    def _get_default_settings(self):
        """Provide default settings if file is missing"""
        return {
            "model": {
                "primary": {
                    "name": "claude-opus-4-1-20250805",
                    "max_tokens": 4000
                },
                "secondary": {
                    "name": "claude-3-haiku-20240307",
                    "max_tokens": 2000
                },
                "temperature": {
                    "phase_0a": 0.3,
                    "phase_0b": 0.3,
                    "phase_1": 0.3,
                    "phase_2": 0.3,
                    "phase_3": 0.4,
                    "phase_4": 0.4,
                    "phase_5": 0.5,
                    "phase_6": 0.5,
                    "phase_7": 0.7,
                    "default": 0.3
                },
                "haiku_phases": ["phase_0a", "phase_0b", "phase_1"],
                "opus_phases": ["phase_2", "phase_3", "phase_4", "phase_5", "phase_6", "phase_7"]
            },
            "investigation": {
                "project_name": "Lismore Capital vs Process Holdings",
                "max_tokens": 4000,
                "haiku_max_tokens": 2000
            }
        }
    
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
        if phase in self.model_config.get('haiku_phases', ['phase_0a', 'phase_0b', 'phase_1']):
            # Use cheaper Haiku model for these phases
            model = self.haiku_model
            max_tokens = self.investigation.get('haiku_max_tokens', 2000)
            print(f"\n📊 Phase {phase}: Using Haiku (economy mode)")
        else:
            # Use Opus 4.1 for everything else
            model = self.opus_model
            max_tokens = self.investigation.get('max_tokens', 4000)
            print(f"\n🚀 Phase {phase}: Using Opus 4.1 (maximum power)")
        
        # Get temperature for this phase
        temperatures = self.model_config.get('temperature', {})
        temperature = temperatures.get(phase, temperatures.get('default', 0.3))
        
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
            
            # Extract text from response safely
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                print("⚠️ Empty response from API")
                return None
            
        except anthropic.RateLimitError:
            print("⏳ Rate limit hit - waiting 60 seconds...")
            time.sleep(60)
            return self.analyse_documents(documents, prompt, context, phase)
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def _build_system_prompt(self, phase: str) -> str:
        """Build adversarial system prompt"""
        base_prompt = f"""You are a senior commercial litigation partner at a magic circle firm.
You are conducting {phase if phase else 'analysis'} for LISMORE CAPITAL against Process Holdings.
Your mandate is to find evidence that destroys Process Holdings' position.
Be aggressive, thorough, and partisan for Lismore. Find every weakness."""
        
        # Add litigation strategy if available
        if self.litigation_strategy:
            objectives = self.litigation_strategy.get('primary_objectives', [])
            if objectives:
                base_prompt += f"\n\nPRIMARY OBJECTIVES:\n" + "\n".join(f"- {obj}" for obj in objectives)
        
        return base_prompt
    
    def _build_user_message(self, documents: List[str], prompt: str, context: Optional[Dict]) -> str:
        """Build user message with documents and context"""
        
        message_parts = []
        
        # Add context from previous phases if available
        if context:
            message_parts.append("PREVIOUS PHASE KNOWLEDGE:")
            # Truncate to avoid token limits
            context_str = json.dumps(context, indent=2)[:10000]
            message_parts.append(context_str)
            message_parts.append("\n" + "="*50 + "\n")
        
        # Add the main prompt
        message_parts.append("ANALYSIS TASK:")
        message_parts.append(prompt)
        message_parts.append("\n" + "="*50 + "\n")
        
        # Add documents
        message_parts.append("DOCUMENTS TO ANALYSE:")
        for i, doc in enumerate(documents, 1):
            # Truncate very long documents
            doc_text = doc[:50000] if len(doc) > 50000 else doc
            message_parts.append(f"\n--- Document {i} ---\n{doc_text}")
        
        return "\n".join(message_parts)