#!/usr/bin/env python3
"""
Optimised Claude API Client for Maximum Capability
Handles 150k+ token contexts with intelligent retry logic
"""

import time
import json
from typing import Dict, List, Optional, Any, Tuple
from anthropic import Anthropic
from datetime import datetime
import hashlib


class ClaudeClient:
    """API client optimised for maximum Claude utilisation"""
    
    def __init__(self, config):
        self.config = config
        self.client = Anthropic(api_key=config.api_config['api_key'])
        
        # Track usage for cost management
        self.usage_stats = {
            'total_calls': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'calls_by_model': {},
            'calls_by_phase': {},
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        # Rate limiting
        self.last_call_time = 0
        self.calls_in_window = []
        self.rate_limit_window = 60  # 1 minute window
        
    def call_claude(self,
                   prompt: str,
                   model: str = None,
                   temperature: float = None,
                   max_tokens: int = None,
                   phase: str = None,
                   task_type: str = None) -> Tuple[str, Dict]:
        """
        Main API call with intelligent retry and error handling
        Returns tuple of (response_text, metadata)
        """
        
        # Determine model based on task complexity
        if not model:
            complexity_score = self._calculate_complexity(prompt, task_type)
            model = self.config.get_model_for_task(task_type or 'general', complexity_score)
        
        # Determine temperature based on task type
        if temperature is None:
            temperature = self._get_temperature(task_type)
        
        # Set max tokens
        if max_tokens is None:
            max_tokens = self.config.token_config['max_output_tokens']
        
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Attempt API call with exponential backoff
        max_retries = self.config.api_config['max_retries']
        base_delay = self.config.api_config['retry_delay']
        
        for attempt in range(max_retries):
            try:
                # Make the API call
                start_time = time.time()
                
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Calculate tokens and timing
                elapsed_time = time.time() - start_time
                input_tokens = self._estimate_tokens(prompt)
                output_tokens = self._estimate_tokens(response.content[0].text)
                
                # Update statistics
                self._update_stats(
                    model=model,
                    phase=phase,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    elapsed_time=elapsed_time,
                    success=True
                )
                
                # Extract response text
                response_text = response.content[0].text if response.content else ""
                
                # Create metadata
                metadata = {
                    'model': model,
                    'temperature': temperature,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'elapsed_time': elapsed_time,
                    'attempt': attempt + 1,
                    'timestamp': datetime.now().isoformat()
                }
                
                return response_text, metadata
                
            except Exception as e:
                error_str = str(e)
                
                # Handle rate limiting
                if "rate_limit" in error_str.lower() or "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                # Handle overloaded errors
                elif "overloaded" in error_str.lower() or "503" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)
                        print(f"API overloaded. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                # Handle other errors
                else:
                    self.usage_stats['errors'].append({
                        'error': error_str[:500],
                        'timestamp': datetime.now().isoformat(),
                        'attempt': attempt + 1,
                        'phase': phase
                    })
                    
                    if attempt < max_retries - 1:
                        wait_time = base_delay
                        print(f"Error: {error_str[:100]}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API call failed after {max_retries} attempts: {error_str}")
        
        # Should never reach here
        raise Exception("Max retries exceeded")
    
    def call_with_context(self,
                         prompt: str,
                         context: Dict[str, Any],
                         task_type: str,
                         phase: str = None) -> Tuple[str, Dict]:
        """
        Call Claude with rich context from knowledge graph
        Optimises prompt with context injection
        """
        
        # Build context-aware prompt
        context_prompt = self._build_context_prompt(prompt, context)
        
        # Determine if complexity warrants Opus
        if self._should_use_opus(context, task_type):
            model = self.config.models['primary']  # Force Opus
        else:
            model = None  # Let call_claude decide
        
        return self.call_claude(
            prompt=context_prompt,
            model=model,
            task_type=task_type,
            phase=phase
        )
    
    def batch_call(self,
                  prompts: List[str],
                  task_type: str,
                  phase: str = None,
                  parallel: bool = False) -> List[Tuple[str, Dict]]:
        """
        Process multiple prompts efficiently
        Returns list of (response, metadata) tuples
        """
        
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"Processing prompt {i+1}/{len(prompts)}")
            
            try:
                response, metadata = self.call_claude(
                    prompt=prompt,
                    task_type=task_type,
                    phase=phase
                )
                results.append((response, metadata))
                
            except Exception as e:
                print(f"Failed on prompt {i+1}: {e}")
                results.append(("", {"error": str(e)}))
            
            # Delay between calls to avoid rate limiting
            if i < len(prompts) - 1:
                time.sleep(self.config.api_config['rate_limit_delay'])
        
        return results
    
    def _calculate_complexity(self, prompt: str, task_type: str = None) -> float:
        """
        Calculate prompt complexity to determine model selection
        Returns score 0.0-1.0
        """
        
        complexity = 0.0
        
        # Length complexity
        prompt_length = len(prompt)
        if prompt_length > 100000:
            complexity += 0.3
        elif prompt_length > 50000:
            complexity += 0.2
        elif prompt_length > 20000:
            complexity += 0.1
        
        # Task type complexity
        complex_tasks = [
            'deep_investigation', 'contradiction_analysis',
            'pattern_recognition', 'strategic_synthesis',
            'timeline_reconstruction', 'entity_mapping'
        ]
        if task_type in complex_tasks:
            complexity += 0.3
        
        # Content complexity markers
        complexity_markers = [
            'NUCLEAR', 'CRITICAL', 'INVESTIGATE',
            'recursive', 'hypothesis', 'strategic'
        ]
        marker_count = sum(1 for marker in complexity_markers if marker in prompt.upper())
        complexity += min(0.2, marker_count * 0.05)
        
        # Question depth (number of question marks)
        question_count = prompt.count('?')
        if question_count > 20:
            complexity += 0.2
        elif question_count > 10:
            complexity += 0.1
        
        return min(1.0, complexity)
    
    def _get_temperature(self, task_type: str = None) -> float:
        """Get temperature based on task type"""
        
        if not task_type:
            return 0.5
        
        # Check config for specific temperature
        temp_config = self.config.temperature_settings
        
        task_temp_map = {
            'investigation': temp_config.get('creative_investigation', 0.9),
            'hypothesis': temp_config.get('hypothesis_generation', 0.8),
            'pattern': temp_config.get('pattern_recognition', 0.6),
            'contradiction': temp_config.get('contradiction_analysis', 0.4),
            'synthesis': temp_config.get('synthesis', 0.3),
            'report': temp_config.get('final_report', 0.2)
        }
        
        # Find matching task type
        for key, temp in task_temp_map.items():
            if key in task_type.lower():
                return temp
        
        return 0.5  # Default
    
    def _should_use_opus(self, context: Dict, task_type: str) -> bool:
        """
        Determine if context/task complexity warrants Opus
        """
        
        triggers = self.config.complexity_triggers
        
        # Check for contradiction
        if context.get('critical_contradictions') and len(context['critical_contradictions']) > 0:
            if triggers.get('contradiction_found'):
                return True
        
        # Check pattern confidence
        patterns = context.get('strong_patterns', [])
        if patterns:
            max_confidence = max(p.get('confidence', 0) for p in patterns)
            if max_confidence > triggers.get('pattern_confidence_high', 0.8):
                return True
        
        # Check investigation depth
        investigations = context.get('active_investigations', [])
        if len(investigations) >= triggers.get('investigation_depth', 3):
            return True
        
        # Check timeline gaps
        if context.get('timeline_impossibilities'):
            if triggers.get('timeline_gaps'):
                return True
        
        # Check entity relationships
        entities = context.get('suspicious_entities', [])
        if len(entities) >= triggers.get('entity_relationships', 10):
            return True
        
        # Check for financial analysis
        if 'financial' in task_type.lower():
            if triggers.get('financial_analysis'):
                return True
        
        return False
    
    def _build_context_prompt(self, base_prompt: str, context: Dict) -> str:
        """
        Inject context into prompt intelligently
        """
        
        context_section = f"""<knowledge_graph_context>
Statistics: {json.dumps(context.get('statistics', {}), indent=2)}

Suspicious Entities: {len(context.get('suspicious_entities', []))} identified
Critical Contradictions: {len(context.get('critical_contradictions', []))} found
Strong Patterns: {len(context.get('strong_patterns', []))} confirmed
Timeline Issues: {len(context.get('timeline_impossibilities', []))} detected
Active Investigations: {len(context.get('active_investigations', []))} ongoing

Key Context:
{json.dumps(context, indent=2)[:5000]}
</knowledge_graph_context>

"""
        return context_section + base_prompt
    
    def _apply_rate_limit(self):
        """Apply rate limiting to avoid API throttling"""
        
        current_time = time.time()
        
        # Clean old calls from window
        self.calls_in_window = [
            call_time for call_time in self.calls_in_window
            if current_time - call_time < self.rate_limit_window
        ]
        
        # Check if we need to wait
        if len(self.calls_in_window) >= 10:  # Max 10 calls per minute
            sleep_time = self.rate_limit_window - (current_time - self.calls_in_window[0])
            if sleep_time > 0:
                print(f"Rate limiting: waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Record this call
        self.calls_in_window.append(current_time)
        self.last_call_time = current_time
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (roughly 1 token per 4 characters)"""
        return len(text) // 4
    
    def _update_stats(self, model: str, phase: str, input_tokens: int,
                     output_tokens: int, elapsed_time: float, success: bool):
        """Update usage statistics"""
        
        self.usage_stats['total_calls'] += 1
        self.usage_stats['total_input_tokens'] += input_tokens
        self.usage_stats['total_output_tokens'] += output_tokens
        
        # Track by model
        if model not in self.usage_stats['calls_by_model']:
            self.usage_stats['calls_by_model'][model] = 0
        self.usage_stats['calls_by_model'][model] += 1
        
        # Track by phase
        if phase:
            if phase not in self.usage_stats['calls_by_phase']:
                self.usage_stats['calls_by_phase'][phase] = 0
            self.usage_stats['calls_by_phase'][phase] += 1
    
    def get_usage_report(self) -> Dict:
        """Get detailed usage report with cost estimates"""
        
        # Rough cost estimates (adjust based on actual pricing)
        costs = {
            'claude-3-opus-latest': {'input': 0.015, 'output': 0.075},
            'claude-3-5-sonnet-latest': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku-latest': {'input': 0.00025, 'output': 0.00125}
        }
        
        total_cost = 0
        cost_by_model = {}
        
        for model, count in self.usage_stats['calls_by_model'].items():
            if model in costs:
                # Estimate tokens per call
                avg_input = self.usage_stats['total_input_tokens'] / max(1, self.usage_stats['total_calls'])
                avg_output = self.usage_stats['total_output_tokens'] / max(1, self.usage_stats['total_calls'])
                
                model_cost = (
                    (avg_input / 1000) * costs[model]['input'] * count +
                    (avg_output / 1000) * costs[model]['output'] * count
                )
                cost_by_model[model] = model_cost
                total_cost += model_cost
        
        return {
            'summary': {
                'total_calls': self.usage_stats['total_calls'],
                'total_input_tokens': self.usage_stats['total_input_tokens'],
                'total_output_tokens': self.usage_stats['total_output_tokens'],
                'estimated_cost_usd': round(total_cost, 2),
                'runtime_hours': (
                    (datetime.now() - datetime.fromisoformat(self.usage_stats['start_time'])).total_seconds() / 3600
                )
            },
            'by_model': self.usage_stats['calls_by_model'],
            'by_phase': self.usage_stats['calls_by_phase'],
            'cost_by_model': cost_by_model,
            'errors': self.usage_stats['errors'][-10:]  # Last 10 errors
        }