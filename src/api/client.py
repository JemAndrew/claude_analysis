#!/usr/bin/env python3
"""
Claude API Client with Prompt Caching Support
COMPLETE REPLACEMENT for src/api/client.py

Implements:
- Prompt caching for 90% cost reduction on repeated context
- Rate limiting and retry logic
- Token usage tracking
- Error handling
- Citation verification
"""

import os
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import anthropic
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from ..core.config import get_config
from ..utils.logger import get_logger


class ClaudeClient:
    """Client for interacting with Claude API with prompt caching"""
    
    def __init__(self):
        """Initialise Claude client"""
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Initialise Anthropic client
        api_key = self.config.api_config.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in config or environment")
        
        self.client = Anthropic(api_key=api_key)
        
        # Model configuration
        self.model = self.config.api_config.get('model', 'claude-sonnet-4-20250514')
        self.max_tokens = self.config.api_config.get('max_tokens', 16000)
        
        # Rate limiting
        self.requests_per_minute = self.config.api_config.get('requests_per_minute', 50)
        self.tokens_per_minute = self.config.api_config.get('tokens_per_minute', 80000)
        
        # Tracking
        self.request_times: List[float] = []
        self.token_usage = {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'cached_input_tokens': 0,
            'cache_creation_tokens': 0,
            'total_cost_gbp': 0.0
        }
        
        # Cache statistics
        self.cache_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_efficiency': 0.0
        }
        
        self.logger.info(f"Initialised Claude client with model: {self.model}")
        self.logger.info(f"Prompt caching enabled: {self.config.api_config.get('enable_prompt_caching', True)}")
    
    def call_claude_with_cache(
        self,
        prompt: str,
        cacheable_context: str,
        task_type: str = 'investigation',
        phase: str = 'disclosure_analysis',
        max_retries: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call Claude with prompt caching for cost savings
        
        Args:
            prompt: The unique prompt that changes per request
            cacheable_context: The large context that stays same (legal knowledge, KG context)
            task_type: Type of task for temperature selection
            phase: Current analysis phase
            max_retries: Max retry attempts
        
        Returns:
            Tuple of (response_text, metadata)
        """
        max_retries = max_retries or self.config.api_config.get('max_retries', 3)
        
        # Get temperature for this task type
        temperature = self.config.get_temperature(task_type)
        
        # Rate limiting
        self._enforce_rate_limits()
        
        # Build messages with cache control
        messages = self._build_cached_messages(prompt, cacheable_context)
        
        # Retry loop
        for attempt in range(max_retries):
            try:
                self.logger.info(f"API call attempt {attempt + 1}/{max_retries} for {task_type} in {phase}")
                
                # Make API call
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=temperature,
                    messages=messages
                )
                
                # Extract response text
                response_text = response.content[0].text
                
                # Track usage
                usage_metadata = self._track_usage(response, cacheable_context)
                
                # Verify citations if required
                if self.config.citation_requirements.get('verify_citations', True):
                    citation_check = self._verify_citations(response_text)
                    usage_metadata['citation_verification'] = citation_check
                
                self.logger.info(f"API call successful. Tokens: {usage_metadata['tokens_used']}")
                
                return response_text, usage_metadata
                
            except anthropic.RateLimitError as e:
                self.logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = self.config.api_config.get('retry_delay', 2.0) * (2 ** attempt)
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise
            
            except anthropic.APIError as e:
                self.logger.error(f"API error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = self.config.api_config.get('retry_delay', 2.0)
                    time.sleep(wait_time)
                else:
                    raise
            
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                raise
        
        raise Exception(f"Failed after {max_retries} attempts")
    
    def _build_cached_messages(self, prompt: str, cacheable_context: str) -> List[Dict]:
        """
        Build messages array with cache control markers
        
        The cacheable_context (legal knowledge, KG) gets cached after first use.
        The prompt (document batch) changes each time.
        """
        
        if not self.config.api_config.get('enable_prompt_caching', True):
            # No caching - simple message
            full_prompt = f"{cacheable_context}\n\n{prompt}"
            return [{"role": "user", "content": full_prompt}]
        
        # With caching - mark cacheable sections
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": cacheable_context,
                        "cache_control": {"type": "ephemeral"}  # This part gets cached
                    },
                    {
                        "type": "text",
                        "text": prompt  # This part is unique per request
                    }
                ]
            }
        ]
        
        return messages
    
    def _enforce_rate_limits(self) -> None:
        """Enforce rate limiting"""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [
            t for t in self.request_times 
            if current_time - t < 60
        ]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = min(self.request_times)
            wait_time = 60 - (current_time - oldest_request)
            
            if wait_time > 0:
                self.logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s")
                time.sleep(wait_time)
        
        # Record this request
        self.request_times.append(current_time)
    
    def _track_usage(self, response: Any, cacheable_context: str) -> Dict[str, Any]:
        """
        Track token usage and costs with cache statistics
        
        Args:
            response: API response object
            cacheable_context: The cached context (for size estimation)
        
        Returns:
            Metadata dictionary with usage stats
        """
        usage = response.usage
        
        # Extract token counts
        input_tokens = getattr(usage, 'input_tokens', 0)
        output_tokens = getattr(usage, 'output_tokens', 0)
        
        # Cache-specific tokens
        cache_creation_tokens = getattr(usage, 'cache_creation_input_tokens', 0)
        cache_read_tokens = getattr(usage, 'cache_read_input_tokens', 0)
        
        # Update totals
        self.token_usage['total_input_tokens'] += input_tokens
        self.token_usage['total_output_tokens'] += output_tokens
        self.token_usage['cache_creation_tokens'] += cache_creation_tokens
        self.token_usage['cached_input_tokens'] += cache_read_tokens
        
        # Update cache statistics
        if cache_read_tokens > 0:
            self.cache_stats['cache_hits'] += 1
        else:
            self.cache_stats['cache_misses'] += 1
        
        total_requests = self.cache_stats['cache_hits'] + self.cache_stats['cache_misses']
        if total_requests > 0:
            self.cache_stats['cache_efficiency'] = self.cache_stats['cache_hits'] / total_requests
        
        # Calculate costs (Claude Sonnet 4 pricing in GBP, approximate)
        # Input: ~£2.40 per million tokens
        # Output: ~£12.00 per million tokens
        # Cache writes: ~£3.00 per million tokens
        # Cache reads: ~£0.24 per million tokens (90% discount)
        
        input_cost = (input_tokens / 1_000_000) * 2.40
        output_cost = (output_tokens / 1_000_000) * 12.00
        cache_write_cost = (cache_creation_tokens / 1_000_000) * 3.00
        cache_read_cost = (cache_read_tokens / 1_000_000) * 0.24
        
        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        self.token_usage['total_cost_gbp'] += total_cost
        
        metadata = {
            'tokens_used': {
                'input': input_tokens,
                'output': output_tokens,
                'cache_creation': cache_creation_tokens,
                'cache_read': cache_read_tokens,
                'total': input_tokens + output_tokens
            },
            'cost_gbp': {
                'input': input_cost,
                'output': output_cost,
                'cache_write': cache_write_cost,
                'cache_read': cache_read_cost,
                'total': total_cost
            },
            'cache_stats': {
                'cache_hit': cache_read_tokens > 0,
                'cache_efficiency': self.cache_stats['cache_efficiency'],
                'total_cache_hits': self.cache_stats['cache_hits'],
                'total_cache_misses': self.cache_stats['cache_misses']
            }
        }
        
        # Log cache performance
        if cache_read_tokens > 0:
            savings = input_tokens * 0.9  # 90% savings on cached tokens
            self.logger.info(
                f"Cache HIT: Read {cache_read_tokens:,} tokens from cache. "
                f"Saved ~{savings:,.0f} tokens worth ~£{(savings/1_000_000)*2.40:.2f}"
            )
        
        return metadata
    
    def _verify_citations(self, response_text: str) -> Dict[str, Any]:
        """
        Verify that response contains proper citations
        
        Returns:
            Dictionary with citation verification results
        """
        import re
        
        # Look for citation pattern: [DOC_ID: Location]
        citation_pattern = r'\[([A-Z0-9_]+):\s*([^\]]+)\]'
        citations = re.findall(citation_pattern, response_text)
        
        # Count findings vs citations
        # Look for claim indicators
        claim_indicators = [
            'states', 'shows', 'indicates', 'demonstrates', 'proves',
            'confirms', 'reveals', 'evidences', 'establishes'
        ]
        
        claim_count = sum(response_text.lower().count(indicator) for indicator in claim_indicators)
        citation_count = len(citations)
        
        # Check if citation density is adequate
        adequate_citations = citation_count >= (claim_count * 0.5)  # At least 50% of claims cited
        
        verification = {
            'citation_count': citation_count,
            'estimated_claim_count': claim_count,
            'adequate_citations': adequate_citations,
            'citation_density': citation_count / max(claim_count, 1),
            'sample_citations': citations[:5]  # First 5 citations as examples
        }
        
        if not adequate_citations:
            self.logger.warning(
                f"Low citation density: {citation_count} citations for ~{claim_count} claims"
            )
        
        return verification
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of token usage and costs"""
        return {
            'token_usage': self.token_usage,
            'cache_stats': self.cache_stats,
            'average_cost_per_request': (
                self.token_usage['total_cost_gbp'] / 
                max(self.cache_stats['cache_hits'] + self.cache_stats['cache_misses'], 1)
            ),
            'cache_savings_gbp': self._calculate_cache_savings()
        }
    
    def _calculate_cache_savings(self) -> float:
        """Calculate approximate savings from caching"""
        # Cached tokens cost 90% less
        cached_tokens = self.token_usage['cached_input_tokens']
        savings = (cached_tokens / 1_000_000) * 2.40 * 0.9  # 90% of normal cost
        return savings
    
    def log_final_statistics(self) -> None:
        """Log final usage statistics"""
        summary = self.get_usage_summary()
        
        self.logger.info("=" * 60)
        self.logger.info("FINAL API USAGE STATISTICS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total input tokens: {summary['token_usage']['total_input_tokens']:,}")
        self.logger.info(f"Total output tokens: {summary['token_usage']['total_output_tokens']:,}")
        self.logger.info(f"Cached input tokens: {summary['token_usage']['cached_input_tokens']:,}")
        self.logger.info(f"Cache creation tokens: {summary['token_usage']['cache_creation_tokens']:,}")
        self.logger.info(f"Total cost: £{summary['token_usage']['total_cost_gbp']:.2f}")
        self.logger.info(f"Cache efficiency: {summary['cache_stats']['cache_efficiency']:.1%}")
        self.logger.info(f"Cache savings: £{summary['cache_savings_gbp']:.2f}")
        self.logger.info("=" * 60)