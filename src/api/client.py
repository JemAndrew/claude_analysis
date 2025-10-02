#!/usr/bin/env python3
"""
Optimised Claude API Client with Prompt Caching
Handles 200k token contexts with intelligent caching and retry logic
ENHANCED VERSION with system prompts, prefill support, and extended thinking
"""

import time
import json
from typing import Dict, List, Optional, Any, Tuple
from anthropic import Anthropic
from datetime import datetime
import hashlib


class ClaudeClient:
    """API client optimised for maximum Claude utilisation with caching"""
    
    def __init__(self, config):
        self.config = config
        self.client = Anthropic(api_key=config.api_config['api_key'])
        
        # Track usage for cost management
        self.usage_stats = {
            'total_calls': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
            'calls_by_model': {},
            'calls_by_phase': {},
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        # Rate limiting
        self.last_call_time = 0
        self.calls_in_window = []
        self.rate_limit_window = 60
    
    def call_claude_with_cache(self,
                               prompt: str,
                               cacheable_context: str,
                               task_type: str = None,
                               phase: str = None,
                               temperature: float = None,
                               prefill: str = None) -> Tuple[str, Dict]:
        """
        Call Claude with prompt caching for repeated contexts
        
        Args:
            prompt: The unique prompt for this call
            cacheable_context: Context that stays the same across calls (will be cached)
            task_type: Type of task for temperature selection
            phase: Analysis phase for tracking
            temperature: Override temperature
            prefill: Start of Claude's response (forces format/tone)
        
        Returns:
            (response_text, metadata)
        """
        
        # Check if caching is enabled
        if not self.config.caching_config['enabled']:
            # Fall back to standard call
            full_prompt = f"{cacheable_context}\n\n{prompt}"
            return self.call_claude(full_prompt, task_type=task_type, phase=phase, 
                                   temperature=temperature, prefill=prefill)
        
        # Check minimum cache size
        cache_tokens = self._estimate_tokens(cacheable_context)
        if cache_tokens < self.config.caching_config['min_tokens_to_cache']:
            # Too small to cache efficiently
            full_prompt = f"{cacheable_context}\n\n{prompt}"
            return self.call_claude(full_prompt, task_type=task_type, phase=phase,
                                   temperature=temperature, prefill=prefill)
        
        # Determine model and temperature
        model = self.config.get_model_for_task(task_type or 'general', 0.5)
        if temperature is None:
            temperature = self._get_temperature(task_type)
        
        max_tokens = self.config.token_config['max_output_tokens']
        
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Retry logic
        max_retries = self.config.api_config['max_retries']
        base_delay = self.config.api_config['retry_delay']
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Build messages with caching
                messages = []
                
                # If prefill provided, add user message then assistant prefill
                if prefill:
                    messages = [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": prefill}
                    ]
                else:
                    messages = [
                        {"role": "user", "content": prompt}
                    ]
                
                # Make API call with caching
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=[
                        {
                            "type": "text",
                            "text": self.config.system_prompt,
                            "cache_control": {"type": "ephemeral"}
                        },
                        {
                            "type": "text",
                            "text": cacheable_context,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    messages=messages
                )
                
                # Calculate timing and tokens
                elapsed_time = time.time() - start_time
                
                # Extract usage information
                usage = response.usage
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens
                cache_creation_tokens = getattr(usage, 'cache_creation_input_tokens', 0)
                cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
                
                # Track cache performance
                if cache_read_tokens > 0:
                    self.usage_stats['cache_hits'] += 1
                    print(f"  💰 Cache HIT: Saved {cache_read_tokens} tokens (90% cost reduction)")
                else:
                    self.usage_stats['cache_misses'] += 1
                    if cache_creation_tokens > 0:
                        print(f"  📝 Cache CREATED: {cache_creation_tokens} tokens cached")
                
                # Update statistics
                self._update_stats(
                    model=model,
                    phase=phase,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cache_creation_tokens=cache_creation_tokens,
                    cache_read_tokens=cache_read_tokens,
                    elapsed_time=elapsed_time,
                    success=True
                )
                
                # Extract response text
                response_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
                
                # If prefill was used, prepend it to response
                if prefill:
                    response_text = prefill + response_text
                
                # Create metadata
                metadata = {
                    'model': model,
                    'temperature': temperature,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'cache_creation_tokens': cache_creation_tokens,
                    'cache_read_tokens': cache_read_tokens,
                    'cache_hit': cache_read_tokens > 0,
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
                        wait_time = base_delay * (2 ** attempt)
                        print(f"  ⏳ Rate limit hit. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                # Handle overloaded errors
                elif "overloaded" in error_str.lower() or "503" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)
                        print(f"  ⏳ API overloaded. Waiting {wait_time}s...")
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
                        print(f"  ⚠️  Error: {error_str[:100]}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API call failed after {max_retries} attempts: {error_str}")
        
        raise Exception("Max retries exceeded")
    
    def call_claude(self,
                   prompt: str,
                   model: str = None,
                   temperature: float = None,
                   max_tokens: int = None,
                   phase: str = None,
                   task_type: str = None,
                   prefill: str = None) -> Tuple[str, Dict]:
        """
        Standard API call without caching
        
        Args:
            prompt: Full prompt text
            model: Model to use (defaults to config selection)
            temperature: Temperature setting
            max_tokens: Maximum output tokens
            phase: Analysis phase for tracking
            task_type: Type of task
            prefill: Start of Claude's response
        
        Returns:
            (response_text, metadata)
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
        
        # Retry logic
        max_retries = self.config.api_config['max_retries']
        base_delay = self.config.api_config['retry_delay']
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Build messages
                messages = []
                if prefill:
                    messages = [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": prefill}
                    ]
                else:
                    messages = [
                        {"role": "user", "content": prompt}
                    ]
                
                # Make the API call
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=self.config.system_prompt,
                    messages=messages
                )
                
                # Calculate tokens and timing
                elapsed_time = time.time() - start_time
                input_tokens = self._estimate_tokens(prompt)
                output_tokens = self._estimate_tokens(response.content[0].text if response.content else "")
                
                # Update statistics
                self._update_stats(
                    model=model,
                    phase=phase,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cache_creation_tokens=0,
                    cache_read_tokens=0,
                    elapsed_time=elapsed_time,
                    success=True
                )
                
                # Extract response text
                response_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
                
                # If prefill was used, prepend it
                if prefill:
                    response_text = prefill + response_text
                
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
                        wait_time = base_delay * (2 ** attempt)
                        print(f"  ⏳ Rate limit hit. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                # Handle overloaded errors
                elif "overloaded" in error_str.lower() or "503" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)
                        print(f"  ⏳ API overloaded. Waiting {wait_time}s...")
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
                        print(f"  ⚠️  Error: {error_str[:100]}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API call failed after {max_retries} attempts: {error_str}")
        
        raise Exception("Max retries exceeded")
    
    def call_with_context(self,
                         prompt: str,
                         context: Dict[str, Any],
                         task_type: str,
                         phase: str = None) -> Tuple[str, Dict]:
        """
        Call Claude with rich context from knowledge graph
        Uses caching if context is large enough
        """
        
        # Build context string
        context_str = json.dumps(context, indent=2)
        
        # If context is large, use caching
        if self._estimate_tokens(context_str) >= self.config.caching_config['min_tokens_to_cache']:
            return self.call_claude_with_cache(
                prompt=prompt,
                cacheable_context=context_str,
                task_type=task_type,
                phase=phase
            )
        else:
            # Small context - standard call
            full_prompt = f"<context>\n{context_str}\n</context>\n\n{prompt}"
            return self.call_claude(
                prompt=full_prompt,
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
            print(f"  Processing prompt {i+1}/{len(prompts)}")
            
            try:
                response, metadata = self.call_claude(
                    prompt=prompt,
                    task_type=task_type,
                    phase=phase
                )
                results.append((response, metadata))
                
            except Exception as e:
                print(f"  ❌ Failed on prompt {i+1}: {e}")
                results.append(("", {"error": str(e)}))
            
            # Delay between calls to avoid rate limiting
            if i < len(prompts) - 1:
                time.sleep(self.config.api_config['rate_limit_delay'])
        
        return results
    
    def _calculate_complexity(self, prompt: str, task_type: str = None) -> float:
        """Calculate prompt complexity to determine model selection"""
        
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
        
        # Question depth
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
        
        return 0.5
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting to avoid API throttling"""
        
        current_time = time.time()
        
        # Remove old calls outside window
        self.calls_in_window = [
            t for t in self.calls_in_window 
            if current_time - t < self.rate_limit_window
        ]
        
        # Check if we need to wait
        if len(self.calls_in_window) >= 50:  # Conservative limit
            oldest_call = min(self.calls_in_window)
            wait_time = self.rate_limit_window - (current_time - oldest_call)
            if wait_time > 0:
                print(f"  ⏳ Rate limit approached. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        # Record this call
        self.calls_in_window.append(current_time)
        self.last_call_time = current_time
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 0.75 words)"""
        word_count = len(text.split())
        return int(word_count * 1.3)
    
    def _update_stats(self,
                     model: str,
                     phase: str,
                     input_tokens: int,
                     output_tokens: int,
                     cache_creation_tokens: int,
                     cache_read_tokens: int,
                     elapsed_time: float,
                     success: bool) -> None:
        """Update usage statistics"""
        
        self.usage_stats['total_calls'] += 1
        self.usage_stats['total_input_tokens'] += input_tokens
        self.usage_stats['total_output_tokens'] += output_tokens
        self.usage_stats['cache_creation_tokens'] += cache_creation_tokens
        self.usage_stats['cache_read_tokens'] += cache_read_tokens
        
        # By model
        if model not in self.usage_stats['calls_by_model']:
            self.usage_stats['calls_by_model'][model] = {
                'count': 0,
                'input_tokens': 0,
                'output_tokens': 0
            }
        self.usage_stats['calls_by_model'][model]['count'] += 1
        self.usage_stats['calls_by_model'][model]['input_tokens'] += input_tokens
        self.usage_stats['calls_by_model'][model]['output_tokens'] += output_tokens
        
        # By phase
        if phase:
            if phase not in self.usage_stats['calls_by_phase']:
                self.usage_stats['calls_by_phase'][phase] = {
                    'count': 0,
                    'input_tokens': 0,
                    'output_tokens': 0
                }
            self.usage_stats['calls_by_phase'][phase]['count'] += 1
            self.usage_stats['calls_by_phase'][phase]['input_tokens'] += input_tokens
            self.usage_stats['calls_by_phase'][phase]['output_tokens'] += output_tokens
    
    def get_usage_report(self) -> Dict:
        """Generate comprehensive usage report with cost estimates"""
        
        # Sonnet 4.5 pricing (per million tokens)
        input_price = 3.0  # £3 per million input tokens
        output_price = 15.0  # £15 per million output tokens
        cache_write_price = 3.75  # £3.75 per million (25% more than input)
        cache_read_price = 0.30  # £0.30 per million (90% discount)
        
        # Calculate costs
        input_cost = (self.usage_stats['total_input_tokens'] / 1_000_000) * input_price
        output_cost = (self.usage_stats['total_output_tokens'] / 1_000_000) * output_price
        cache_write_cost = (self.usage_stats['cache_creation_tokens'] / 1_000_000) * cache_write_price
        cache_read_cost = (self.usage_stats['cache_read_tokens'] / 1_000_000) * cache_read_price
        
        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        
        # Calculate savings from caching
        cache_savings = 0
        if self.usage_stats['cache_read_tokens'] > 0:
            # What it would have cost without caching
            would_have_cost = (self.usage_stats['cache_read_tokens'] / 1_000_000) * input_price
            cache_savings = would_have_cost - cache_read_cost
        
        return {
            'summary': {
                'total_calls': self.usage_stats['total_calls'],
                'total_input_tokens': self.usage_stats['total_input_tokens'],
                'total_output_tokens': self.usage_stats['total_output_tokens'],
                'cache_creation_tokens': self.usage_stats['cache_creation_tokens'],
                'cache_read_tokens': self.usage_stats['cache_read_tokens'],
                'cache_hits': self.usage_stats['cache_hits'],
                'cache_misses': self.usage_stats['cache_misses'],
                'cache_hit_rate': (
                    self.usage_stats['cache_hits'] / 
                    max(1, self.usage_stats['cache_hits'] + self.usage_stats['cache_misses'])
                ),
                'estimated_cost_gbp': round(total_cost, 2),
                'cache_savings_gbp': round(cache_savings, 2),
                'error_count': len(self.usage_stats['errors'])
            },
            'by_model': self.usage_stats['calls_by_model'],
            'by_phase': self.usage_stats['calls_by_phase'],
            'recent_errors': self.usage_stats['errors'][-5:] if self.usage_stats['errors'] else []
        }
    
    def print_usage_summary(self) -> None:
        """Print formatted usage summary"""
        
        report = self.get_usage_report()
        summary = report['summary']
        
        print("\n" + "="*60)
        print("API USAGE SUMMARY")
        print("="*60)
        print(f"Total API Calls: {summary['total_calls']}")
        print(f"Total Input Tokens: {summary['total_input_tokens']:,}")
        print(f"Total Output Tokens: {summary['total_output_tokens']:,}")
        print(f"\nCache Performance:")
        print(f"  Cache Hits: {summary['cache_hits']}")
        print(f"  Cache Misses: {summary['cache_misses']}")
        print(f"  Hit Rate: {summary['cache_hit_rate']:.1%}")
        print(f"  Cache Read Tokens: {summary['cache_read_tokens']:,}")
        print(f"  Cache Savings: £{summary['cache_savings_gbp']:.2f}")
        print(f"\nEstimated Total Cost: £{summary['estimated_cost_gbp']:.2f}")
        print(f"Errors: {summary['error_count']}")
        print("="*60 + "\n")