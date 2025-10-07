#!/usr/bin/env python3
"""
Enhanced Claude API Client with FIXED Prompt Caching
- Caches static content only (pleadings, system prompt)
- Increased extended thinking budget (100K tokens)
- Proper cache separation
British English throughout
"""

# ============================================================================
# CRITICAL: Import os FIRST, then load .env
# ============================================================================
import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env file going up directories
current_dir = Path(__file__).resolve().parent
for _ in range(5):
    env_path = current_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ API Client loaded .env from: {env_path}")
        break
    current_dir = current_dir.parent

# Verify API key immediately (AFTER importing os!)
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError(
        "❌ ANTHROPIC_API_KEY not found in environment.\n"
        f"   Searched for .env starting from: {Path(__file__).resolve().parent}\n"
        "   Get your key from: https://console.anthropic.com/settings/keys\n"
        "   Add to .env file: ANTHROPIC_API_KEY=sk-ant-api03-your-key"
    )

# Now import everything else
import time
import json
import anthropic
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib


class ClaudeClient:
    """API client with optimised caching and extended thinking"""
    
    def __init__(self, config):
        """Initialise Claude API client"""
        self.config = config
        
        # Get API key from environment
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Static content for caching (loaded once)
        self.pleadings_text = None
        self.legal_framework_text = None
        
        # Track usage for cost management
        self.usage_stats = {
            'total_calls': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
            'thinking_tokens': 0,
            'calls_by_model': {},
            'calls_by_phase': {},
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_savings_gbp': 0.0,
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        # Rate limiting
        self.last_call_time = 0
        self.calls_in_window = []
        self.rate_limit_window = 60
    
    def load_static_content(self, pleadings_text: str = None, legal_framework_text: str = None):
        """
        Load static content for caching
        Call this once at system startup
        """
        if pleadings_text:
            self.pleadings_text = pleadings_text
            print(f"Loaded pleadings for caching: {len(pleadings_text):,} characters")
        
        if legal_framework_text:
            self.legal_framework_text = legal_framework_text
            print(f"Loaded legal framework for caching: {len(legal_framework_text):,} characters")
    
    def call_claude_with_cache(self,
                               prompt: str,
                               dynamic_context: str = None,
                               task_type: str = None,
                               phase: str = None,
                               temperature: float = None,
                               prefill: str = None) -> Tuple[str, Dict]:
        """
        Call Claude with FIXED prompt caching
        
        CACHES (static content that never changes):
        - System prompt
        - Pleadings text
        - Legal framework
        
        DOESN'T CACHE (dynamic content that changes):
        - Accumulated knowledge
        - Current documents
        - Iteration-specific context
        
        Args:
            prompt: The unique prompt for this call
            dynamic_context: Context that changes (accumulated knowledge, documents)
            task_type: Type of task
            phase: Analysis phase
            temperature: Temperature override
            prefill: Response prefill
        
        Returns:
            (response_text, metadata)
        """
        
        # Check if caching is enabled
        if not self.config.caching_config['enabled']:
            full_prompt = f"{dynamic_context}\n\n{prompt}" if dynamic_context else prompt
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
                
                # Build system array with STATIC content only
                system = [
                    {
                        "type": "text",
                        "text": self.config.system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
                
                # Add pleadings to cache if available (STATIC)
                if self.pleadings_text:
                    system.append({
                        "type": "text",
                        "text": f"<pleadings_context>\n{self.pleadings_text}\n</pleadings_context>",
                        "cache_control": {"type": "ephemeral"}
                    })
                
                # Add legal framework to cache if available (STATIC)
                if self.legal_framework_text:
                    system.append({
                        "type": "text",
                        "text": f"<legal_framework>\n{self.legal_framework_text}\n</legal_framework>",
                        "cache_control": {"type": "ephemeral"}
                    })
                
                # Build user message with DYNAMIC content (NOT cached)
                user_content = ""
                
                if dynamic_context:
                    user_content += f"{dynamic_context}\n\n"
                
                user_content += prompt
                
                # Build messages
                messages = []
                
                if prefill:
                    messages = [
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": prefill}
                    ]
                else:
                    messages = [
                        {"role": "user", "content": user_content}
                    ]
                
                # Build API parameters
                api_params = {
                    'model': model,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'system': system,
                    'messages': messages
                }
                
                # Add extended thinking if appropriate
                if self._should_use_extended_thinking(model, task_type):
                    api_params['thinking'] = {
                        'type': 'enabled',
                        'budget_tokens': self.config.token_config['extended_thinking_budget']
                    }
                    print(f"  🧠 Extended Thinking: ENABLED ({self.config.token_config['extended_thinking_budget']:,} tokens)")
                
                # Make API call with caching
                response = self.client.messages.create(**api_params)
                
                # Calculate timing and tokens
                elapsed_time = time.time() - start_time
                
                # Extract usage from response
                usage = response.usage
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens
                cache_creation_tokens = getattr(usage, 'cache_creation_input_tokens', 0)
                cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
                
                # Extract thinking tokens
                thinking_tokens = 0
                thinking_content = None
                if hasattr(response, 'content'):
                    for block in response.content:
                        if hasattr(block, 'type') and block.type == 'thinking':
                            thinking_text = getattr(block, 'thinking', '')
                            thinking_tokens = len(thinking_text.split()) * 1.3  # Rough estimate
                            thinking_content = thinking_text
                            if thinking_tokens > 0:
                                print(f"  💭 Thinking: {int(thinking_tokens):,} tokens used")
                
                # Track cache performance
                if cache_read_tokens > 0:
                    self.usage_stats['cache_hits'] += 1
                    # Cache reads are 90% cheaper
                    savings = (cache_read_tokens * 0.9 * 3.0) / 1_000_000  # £3 per 1M tokens
                    self.usage_stats['cache_savings_gbp'] += savings
                    print(f"  💰 Cache HIT: Saved {cache_read_tokens:,} tokens (£{savings:.2f})")
                else:
                    self.usage_stats['cache_misses'] += 1
                    if cache_creation_tokens > 0:
                        print(f"  📝 Cache CREATED: {cache_creation_tokens:,} tokens cached")
                
                # Update statistics
                self._update_stats(
                    model=model,
                    phase=phase,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cache_creation_tokens=cache_creation_tokens,
                    cache_read_tokens=cache_read_tokens,
                    thinking_tokens=thinking_tokens,
                    elapsed_time=elapsed_time
                )
                
                # Extract response text
                response_text = ""
                for block in response.content:
                    if hasattr(block, 'type') and block.type == 'text':
                        response_text += block.text
                
                # Build metadata
                metadata = {
                    'model': model,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'cache_creation_tokens': cache_creation_tokens,
                    'cache_read_tokens': cache_read_tokens,
                    'thinking_tokens': int(thinking_tokens),
                    'elapsed_time': elapsed_time,
                    'cost_gbp': self._calculate_cost(
                        model, input_tokens, output_tokens,
                        cache_creation_tokens, cache_read_tokens, thinking_tokens
                    ),
                    'cache_hit': cache_read_tokens > 0,
                    'thinking_used': thinking_tokens > 0
                }
                
                return response_text, metadata
                
            except Exception as e:
                error_str = str(e)
                self.usage_stats['errors'].append({
                    'attempt': attempt + 1,
                    'error': error_str,
                    'timestamp': datetime.now().isoformat()
                })
                
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"    ⚠️  API error (attempt {attempt + 1}/{max_retries}): {error_str[:100]}")
                    print(f"    Retrying in {wait_time}s...")
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
        """
        
        if not model:
            complexity_score = self._calculate_complexity(prompt, task_type)
            model = self.config.get_model_for_task(task_type or 'general', complexity_score)
        
        if temperature is None:
            temperature = self._get_temperature(task_type)
        
        if max_tokens is None:
            max_tokens = self.config.token_config['max_output_tokens']
        
        self._apply_rate_limit()
        
        max_retries = self.config.api_config['max_retries']
        base_delay = self.config.api_config['retry_delay']
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
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
                
                api_params = {
                    'model': model,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'system': self.config.system_prompt,
                    'messages': messages
                }
                
                if self._should_use_extended_thinking(model, task_type):
                    api_params['thinking'] = {
                        'type': 'enabled',
                        'budget_tokens': self.config.token_config['extended_thinking_budget']
                    }
                    print(f"  🧠 Extended Thinking: ENABLED ({self.config.token_config['extended_thinking_budget']:,} tokens)")
                
                response = self.client.messages.create(**api_params)
                
                elapsed_time = time.time() - start_time
                
                usage = response.usage
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens
                
                thinking_tokens = 0
                if hasattr(response, 'content'):
                    for block in response.content:
                        if hasattr(block, 'type') and block.type == 'thinking':
                            thinking_text = getattr(block, 'thinking', '')
                            thinking_tokens = len(thinking_text.split()) * 1.3
                            if thinking_tokens > 0:
                                print(f"  💭 Thinking: {int(thinking_tokens):,} tokens")
                
                self._update_stats(
                    model=model,
                    phase=phase,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cache_creation_tokens=0,
                    cache_read_tokens=0,
                    thinking_tokens=thinking_tokens,
                    elapsed_time=elapsed_time
                )
                
                response_text = ""
                for block in response.content:
                    if hasattr(block, 'type') and block.type == 'text':
                        response_text += block.text
                
                metadata = {
                    'model': model,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'thinking_tokens': int(thinking_tokens),
                    'elapsed_time': elapsed_time,
                    'cost_gbp': self._calculate_cost(
                        model, input_tokens, output_tokens,
                        0, 0, thinking_tokens
                    )
                }
                
                return response_text, metadata
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"    ⚠️  Error: {str(e)[:100]}")
                    print(f"    Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def _should_use_extended_thinking(self, model: str, task_type: str = None) -> bool:
        """Determine if extended thinking should be used"""
        if 'sonnet-4' not in model.lower():
            return False
        
        # Disable for basic tasks
        if task_type in ['metadata_scan', 'document_loading', 'prioritisation']:
            return False
        
        return True
    
    def _get_temperature(self, task_type: str = None) -> float:
        """Get temperature for task type"""
        temperature_map = {
            'document_triage': 0.0,
            'deep_analysis': 0.3,
            'investigation': 0.5,
            'synthesis': 0.3,
            'creative': 0.7
        }
        return temperature_map.get(task_type, 0.3)
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int,
                       cache_creation: int, cache_read: int, thinking_tokens: int) -> float:
        """Calculate cost in GBP"""
        
        # Pricing per 1M tokens (GBP)
        if 'haiku' in model.lower():
            input_price = 0.25
            output_price = 1.25
        elif 'sonnet' in model.lower():
            input_price = 3.0
            output_price = 15.0
        elif 'opus' in model.lower():
            input_price = 15.0
            output_price = 75.0
        else:
            input_price = 3.0
            output_price = 15.0
        
        # Cache pricing (90% discount on reads)
        cache_write_price = input_price * 1.25  # 25% more to write
        cache_read_price = input_price * 0.1    # 90% discount
        
        # Thinking tokens priced at input rate
        thinking_price = input_price
        
        cost = (
            (input_tokens * input_price / 1_000_000) +
            (output_tokens * output_price / 1_000_000) +
            (cache_creation * cache_write_price / 1_000_000) +
            (cache_read * cache_read_price / 1_000_000) +
            (thinking_tokens * thinking_price / 1_000_000)
        )
        
        return cost
    
    def _update_stats(self, model: str, phase: str, input_tokens: int,
                     output_tokens: int, cache_creation_tokens: int,
                     cache_read_tokens: int, thinking_tokens: int,
                     elapsed_time: float):
        """Update usage statistics"""
        
        self.usage_stats['total_calls'] += 1
        self.usage_stats['total_input_tokens'] += input_tokens
        self.usage_stats['total_output_tokens'] += output_tokens
        self.usage_stats['cache_creation_tokens'] += cache_creation_tokens
        self.usage_stats['cache_read_tokens'] += cache_read_tokens
        self.usage_stats['thinking_tokens'] += int(thinking_tokens)
        
        if model not in self.usage_stats['calls_by_model']:
            self.usage_stats['calls_by_model'][model] = 0
        self.usage_stats['calls_by_model'][model] += 1
        
        if phase:
            if phase not in self.usage_stats['calls_by_phase']:
                self.usage_stats['calls_by_phase'][phase] = 0
            self.usage_stats['calls_by_phase'][phase] += 1
    
    def _apply_rate_limit(self):
        """Apply rate limiting"""
        now = time.time()
        
        # Remove calls outside window
        self.calls_in_window = [
            t for t in self.calls_in_window 
            if now - t < self.rate_limit_window
        ]
        
        # If at limit, wait
        if len(self.calls_in_window) >= 50:  # 50 calls per minute
            wait_time = self.rate_limit_window - (now - self.calls_in_window[0])
            if wait_time > 0:
                time.sleep(wait_time)
        
        self.calls_in_window.append(now)
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation"""
        return len(text) // 4
    
    def _calculate_complexity(self, prompt: str, task_type: str = None) -> float:
        """Calculate prompt complexity"""
        complexity = 0.0
        
        prompt_length = len(prompt)
        if prompt_length > 100000:
            complexity += 0.3
        elif prompt_length > 50000:
            complexity += 0.2
        elif prompt_length > 20000:
            complexity += 0.1
        
        complex_tasks = [
            'deep_investigation', 'contradiction_analysis',
            'pattern_recognition', 'strategic_synthesis'
        ]
        if task_type in complex_tasks:
            complexity += 0.3
        
        return min(1.0, complexity)
    
    def print_usage_summary(self):
        """Print usage statistics"""
        print("\n" + "=" * 70)
        print("API USAGE SUMMARY")
        print("=" * 70)
        
        print(f"\nTotal calls: {self.usage_stats['total_calls']}")
        print(f"Total input tokens: {self.usage_stats['total_input_tokens']:,}")
        print(f"Total output tokens: {self.usage_stats['total_output_tokens']:,}")
        print(f"Total thinking tokens: {self.usage_stats['thinking_tokens']:,}")
        
        print(f"\nCache performance:")
        print(f"  Cache hits: {self.usage_stats['cache_hits']}")
        print(f"  Cache misses: {self.usage_stats['cache_misses']}")
        print(f"  Tokens cached: {self.usage_stats['cache_creation_tokens']:,}")
        print(f"  Tokens read from cache: {self.usage_stats['cache_read_tokens']:,}")
        print(f"  Cache savings: £{self.usage_stats['cache_savings_gbp']:.2f}")
        
        print("=" * 70)