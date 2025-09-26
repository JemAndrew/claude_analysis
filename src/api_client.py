#!/usr/bin/env python3
"""
Fixed Claude API Client
Handles all API calls with retry logic and rate limiting
"""

import time
import json
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from prompts import Prompts


class ClaudeAPIClient:
    """API client with proper retry logic and error handling"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompts = Prompts()
        
        # Model configuration by phase
        self.phase_models = {
            '0A': 'claude-3-haiku-20240307',  # Cheap for learning
            '0B': 'claude-3-5-sonnet-20241022',  # Using Sonnet for 0B-7
            '1':  'claude-3-5-sonnet-20241022',
            '2':  'claude-3-5-sonnet-20241022',
            '3':  'claude-3-5-sonnet-20241022',
            '4':  'claude-3-5-sonnet-20241022',
            '5':  'claude-3-5-sonnet-20241022',
            '6':  'claude-3-5-sonnet-20241022',
            '7':  'claude-3-5-sonnet-20241022',
        }
        
        # Batch configuration
        self.batch_config = {
            'max_docs_per_batch': 10,
            'max_tokens_per_batch': 20000,
            'inter_batch_delay': 8,  # Seconds between batches
            'synthesis_delay': 10,    # Before synthesis
        }
        
        # Track API usage
        self.total_api_calls = 0
        self.total_tokens_used = 0
    
    def analyse_documents_batch(self, 
                                documents: List[Dict], 
                                phase: str,
                                context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point for document analysis
        Always returns dict with 'synthesis', 'self_ask', 'batch_responses', 'documents_analysed'
        """
        
        phase_key = phase.replace("phase_", "").split("_")[0]
        
        # Handle special cases (no documents - used for report generation)
        if not documents:
            # This is a report generation or special prompt call
            prompt = context.get('prompt', '') if context else ''
            if not prompt:
                return {
                    'synthesis': 'No documents or prompt provided',
                    'self_ask': '',
                    'batch_responses': [],
                    'documents_analysed': 0
                }
            
            response = self._call_api_with_retry(
                prompt=prompt,
                phase=phase,
                system_prompt=self.prompts.get_system_prompt(phase)
            )
            
            return {
                'synthesis': response,
                'self_ask': '',
                'batch_responses': [response],
                'documents_analysed': 0
            }
        
        # Process documents in batches
        batches = self._split_into_batches(documents)
        batch_responses = []
        
        print(f"  Processing {len(documents)} documents in {len(batches)} batches")
        
        # Process each batch
        for i, batch in enumerate(batches):
            print(f"  Batch {i+1}/{len(batches)}: {len(batch)} documents", end="")
            
            # Build prompt for this batch
            prompt = self.prompts.get_analysis_prompt(
                phase=phase,
                batch_num=i+1,
                context=context
            )
            
            # Add document content
            doc_content = self._format_documents(batch)
            full_prompt = f"{prompt}\n\nDOCUMENTS:\n{doc_content}"
            
            # Call API with retry
            response = self._call_api_with_retry(
                prompt=full_prompt,
                phase=f"{phase}_batch_{i+1}",
                system_prompt=self.prompts.get_system_prompt(phase)
            )
            
            batch_responses.append(response)
            print(" ✓")
            
            # Update context with findings for next batch
            if context:
                self._update_context(context, response)
            
            # Delay between batches to avoid rate limits
            if i < len(batches) - 1:
                time.sleep(self.batch_config['inter_batch_delay'])
        
        # Synthesise if multiple batches
        synthesis = ""
        if len(batch_responses) > 1:
            print(f"  Synthesising {len(batch_responses)} batch results...")
            time.sleep(self.batch_config['synthesis_delay'])
            
            synthesis_prompt = self.prompts.get_synthesis_prompt(
                batch_responses=batch_responses,
                phase=phase
            )
            
            synthesis = self._call_api_with_retry(
                prompt=synthesis_prompt,
                phase=f"{phase}_synthesis",
                system_prompt=self.prompts.get_system_prompt(phase)
            )
        elif batch_responses:
            synthesis = batch_responses[0]
        
        # Self-ask for deeper analysis (phases 1-6 only)
        self_ask = ""
        if synthesis and phase_key in ["1", "2", "3", "4", "5", "6"]:
            print(f"  Performing self-questioning...")
            
            self_ask_prompt = self.prompts.get_self_ask_prompt(
                phase=phase,
                synthesis=synthesis
            )
            
            self_ask = self._call_api_with_retry(
                prompt=self_ask_prompt,
                phase=f"{phase}_self_ask",
                system_prompt=self.prompts.get_system_prompt(phase)
            )
        
        return {
            'synthesis': synthesis,
            'self_ask': self_ask,
            'batch_responses': batch_responses,
            'documents_analysed': len(documents)
        }
    
    def _call_api_with_retry(self, 
                             prompt: str, 
                             phase: str,
                             system_prompt: str,
                             max_retries: int = 5) -> str:
        """API call with exponential backoff for rate limits"""
        
        # Determine model based on phase
        phase_key = phase.split("_")[0].replace("phase", "")
        model = self.phase_models.get(phase_key, 'claude-3-5-sonnet-20241022')
        
        # Try API call with retries
        for attempt in range(max_retries):
            try:
                # Make the API call
                response = self.client.messages.create(
                    model=model,
                    max_tokens=4000,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Track usage
                self.total_api_calls += 1
                
                # Extract text from response
                if response.content:
                    return response.content[0].text
                else:
                    return "No response content"
                
            except Exception as e:
                error_str = str(e)
                
                # Handle rate limit errors
                if "rate_limit" in error_str or "429" in error_str:
                    wait_time = (2 ** attempt) * 5  # 5, 10, 20, 40, 80 seconds
                    print(f"\n  ⚠️ Rate limit hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                # Handle other API errors
                elif attempt < max_retries - 1:
                    print(f"\n  ⚠️ API error: {error_str[:100]}. Retrying...")
                    time.sleep(5)
                    continue
                else:
                    print(f"\n  ❌ API call failed after {max_retries} attempts")
                    raise e
        
        # If all retries exhausted
        raise Exception(f"Max retries ({max_retries}) exceeded for phase {phase}")
    
    def _split_into_batches(self, documents: List[Dict]) -> List[List[Dict]]:
        """Split documents into manageable batches based on token count"""
        
        if not documents:
            return []
        
        batches = []
        current_batch = []
        current_tokens = 0
        
        for doc in documents:
            # Estimate tokens (roughly 1 token per 4 characters)
            content = doc.get('content', '')
            doc_tokens = len(content) // 4
            
            # Check if adding this doc would exceed limits
            if current_tokens + doc_tokens > self.batch_config['max_tokens_per_batch']:
                # Save current batch if it has documents
                if current_batch:
                    batches.append(current_batch)
                # Start new batch with this document
                current_batch = [doc]
                current_tokens = doc_tokens
            else:
                # Add to current batch
                current_batch.append(doc)
                current_tokens += doc_tokens
            
            # Check batch size limit
            if len(current_batch) >= self.batch_config['max_docs_per_batch']:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
        
        # Add remaining documents
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format documents for prompt with clear separation"""
        
        if not documents:
            return "No documents provided"
        
        formatted = []
        for doc in documents:
            doc_id = doc.get('id', doc.get('doc_id', 'UNKNOWN'))
            content = doc.get('content', '')
            
            # Truncate very long documents
            if len(content) > 50000:
                content = content[:50000] + "\n[... truncated ...]"
            
            formatted.append(f"[{doc_id}]\n{content}\n{'='*40}")
        
        return "\n".join(formatted)
    
    def _update_context(self, context: Dict, response: str):
        """Update context with key findings from response"""
        
        if not context or not response:
            return
        
        # Extract critical findings
        if "CRITICAL:" in response or "NUCLEAR:" in response:
            if 'critical_findings' not in context:
                context['critical_findings'] = []
            
            # Extract lines with critical findings
            for line in response.split('\n'):
                if 'CRITICAL:' in line or 'NUCLEAR:' in line:
                    finding = line.strip()
                    if finding and finding not in context['critical_findings']:
                        context['critical_findings'].append(finding)
                    # Keep only top 5
                    context['critical_findings'] = context['critical_findings'][:5]
        
        # Extract follow-up questions from self-ask
        if "Q1:" in response or "Q2:" in response or "Q3:" in response:
            if 'follow_up_questions' not in context:
                context['follow_up_questions'] = []
            
            # Extract questions
            import re
            questions = re.findall(r'Q\d+:\s*(.+?)(?:\n|$)', response)
            for q in questions[:3]:  # Keep top 3
                if q.strip() and q.strip() not in context['follow_up_questions']:
                    context['follow_up_questions'].append(q.strip())
        
        # Track document references
        if 'referenced_docs' not in context:
            context['referenced_docs'] = set()
        
        # Find all DOC_XXXX references
        import re
        doc_refs = re.findall(r'DOC_\d{4}|LEGAL_\w+|CASE_\w+', response)
        context['referenced_docs'].update(doc_refs)
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'total_api_calls': self.total_api_calls,
            'estimated_cost': self.total_api_calls * 0.01  # Rough estimate
        }