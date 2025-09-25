#!/usr/bin/env python3
"""
Enhanced Claude API client with sophisticated batching and document handling
Optimised for maximum efficiency and cost control
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path='./config/.env')


class CostTracker:
    """Enhanced cost tracking with phase analytics"""
    
    def __init__(self):
        self.costs_file = Path("./costs/cost_tracking.json")
        self.costs_file.parent.mkdir(exist_ok=True)
        
        # Enhanced pricing with all models
        self.model_pricing = {
            "claude-opus-4-1-20250805": {
                "input": 0.012,
                "output": 0.060,
                "name": "Opus 4.1"
            },
            "claude-3-haiku-20240307": {
                "input": 0.0002,
                "output": 0.001,
                "name": "Haiku"
            },
            "claude-3-sonnet-20240229": {
                "input": 0.003,
                "output": 0.015,
                "name": "Sonnet"
            }
        }
        
        # Enhanced tracking
        self.total_cost = 0.0
        self.phase_costs = {}
        self.model_usage = {}
        self.call_history = []
        self.batch_stats = {
            'total_batches': 0,
            'avg_batch_size': 0,
            'max_batch_size': 0
        }
        
        self._load_existing_costs()
    
    def _load_existing_costs(self):
        """Load existing cost data with migration support"""
        if self.costs_file.exists():
            try:
                with open(self.costs_file, 'r') as f:
                    data = json.load(f)
                    self.total_cost = data.get('total_cost_gbp', 0.0)
                    self.phase_costs = data.get('phase_costs', {})
                    self.model_usage = data.get('model_usage', {})
                    self.call_history = data.get('calls', [])
                    self.batch_stats = data.get('batch_stats', self.batch_stats)
                    
                    print(f"╔════════════════════════════════════════╗")
                    print(f"║  COST TRACKER LOADED                   ║")
                    print(f"║  Current spend: £{self.total_cost:.4f}        ║")
                    print(f"║  Total calls: {len(self.call_history):4d}             ║")
                    print(f"╚════════════════════════════════════════╝")
            except Exception as e:
                print(f"Starting fresh cost tracking: {e}")
    
    def track_call(self, phase: str, model: str, input_tokens: int, 
                   output_tokens: int, batch_size: int = 1) -> float:
        """Track API call with batch statistics"""
        
        # Get pricing
        pricing = self.model_pricing.get(model, self.model_pricing["claude-opus-4-1-20250805"])
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        call_cost = input_cost + output_cost
        
        # Update totals
        self.total_cost += call_cost
        
        # Update phase costs
        if phase not in self.phase_costs:
            self.phase_costs[phase] = {'cost': 0, 'calls': 0, 'tokens': 0}
        self.phase_costs[phase]['cost'] += call_cost
        self.phase_costs[phase]['calls'] += 1
        self.phase_costs[phase]['tokens'] += input_tokens + output_tokens
        
        # Update model usage
        model_name = pricing['name']
        if model_name not in self.model_usage:
            self.model_usage[model_name] = {'calls': 0, 'tokens': 0, 'cost': 0}
        self.model_usage[model_name]['calls'] += 1
        self.model_usage[model_name]['tokens'] += input_tokens + output_tokens
        self.model_usage[model_name]['cost'] += call_cost
        
        # Update batch stats
        self.batch_stats['total_batches'] += 1
        self.batch_stats['max_batch_size'] = max(self.batch_stats['max_batch_size'], batch_size)
        
        # Add to history
        self.call_history.append({
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'model': model,
            'model_name': model_name,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_gbp': call_cost,
            'batch_size': batch_size
        })
        
        # Display
        print(f"   💰 Cost: £{call_cost:.4f} ({model_name}: {input_tokens:,} in, {output_tokens:,} out)")
        print(f"   📊 Phase {phase} total: £{self.phase_costs[phase]['cost']:.4f}")
        print(f"   💸 Running total: £{self.total_cost:.4f}")
        
        self.save_costs()
        return call_cost
    
    def save_costs(self):
        """Save enhanced cost data"""
        with open(self.costs_file, 'w') as f:
            json.dump({
                'total_cost_gbp': self.total_cost,
                'phase_costs': self.phase_costs,
                'model_usage': self.model_usage,
                'batch_stats': self.batch_stats,
                'calls': self.call_history[-100:]  # Keep last 100 for history
            }, f, indent=2)
    
    def generate_cost_report(self) -> str:
        """Generate detailed cost report"""
        report = []
        report.append("\n" + "="*60)
        report.append("💷 DETAILED COST ANALYSIS REPORT")
        report.append("="*60)
        
        # Overall
        report.append(f"\n📊 OVERALL STATISTICS:")
        report.append(f"  Total Cost: £{self.total_cost:.4f}")
        report.append(f"  Total API Calls: {len(self.call_history)}")
        report.append(f"  Average Cost per Call: £{self.total_cost/max(len(self.call_history), 1):.4f}")
        
        # By Phase
        report.append(f"\n📈 COST BY PHASE:")
        for phase in sorted(self.phase_costs.keys()):
            data = self.phase_costs[phase]
            report.append(f"  {phase}:")
            report.append(f"    Cost: £{data['cost']:.4f}")
            report.append(f"    Calls: {data['calls']}")
            report.append(f"    Tokens: {data['tokens']:,}")
        
        # By Model
        report.append(f"\n🤖 MODEL USAGE:")
        for model, data in self.model_usage.items():
            report.append(f"  {model}:")
            report.append(f"    Calls: {data['calls']}")
            report.append(f"    Tokens: {data['tokens']:,}")
            report.append(f"    Cost: £{data['cost']:.4f}")
        
        # Batch Statistics
        report.append(f"\n📦 BATCH EFFICIENCY:")
        report.append(f"  Total Batches: {self.batch_stats['total_batches']}")
        report.append(f"  Max Batch Size: {self.batch_stats['max_batch_size']} docs")
        
        report.append("="*60)
        return "\n".join(report)


class ClaudeAPIClient:
    """Sophisticated API client with intelligent batching and error handling"""
    
    def __init__(self, api_key: Optional[str] = None, settings_path: str = "./config/settings.json"):
        """Initialise enhanced API client"""
        
        # API setup
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            load_dotenv(dotenv_path='./config/.env', override=True)
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("No ANTHROPIC_API_KEY found")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Load settings with defaults
        self.settings = self._load_settings(settings_path)
        
        # Enhanced configuration
        self.models = {
            'opus': self.settings['models']['opus'],
            'haiku': self.settings['models']['haiku'],
            'sonnet': self.settings['models'].get('sonnet', 'claude-3-sonnet-20240229')
        }
        
        self.phase_config = self.settings.get('phase_config', self._get_default_phase_config())
        
        # Enhanced tracking
        self.cost_tracker = CostTracker()
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 60,
            'backoff_factor': 2
        }
        
        # Document batching configuration
        self.batch_config = {
            'max_tokens_per_batch': 30000,
            'max_docs_per_batch': 20,
            'intelligent_batching': True
        }
        
        print(f"\n✅ Enhanced API Client Ready")
        print(f"   Models: Opus 4.1, Haiku, Sonnet")
        print(f"   Intelligent Batching: Enabled")
        print(f"   Cost Tracking: Enhanced")
    
    def _load_settings(self, settings_path: str) -> Dict:
        """Load settings with migration support"""
        path = Path(settings_path)
        if path.exists():
            with open(path, 'r') as f:
                settings = json.load(f)
                
                # Migrate old settings format
                if 'model' in settings:
                    settings['models'] = {
                        'opus': settings['model'].get('primary', {}).get('name', 'claude-opus-4-1-20250805'),
                        'haiku': settings['model'].get('secondary', {}).get('name', 'claude-3-haiku-20240307'),
                        'sonnet': 'claude-3-sonnet-20240229'
                    }
                
                return settings
        else:
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict:
        """Enhanced default settings"""
        return {
            'models': {
                'opus': 'claude-opus-4-1-20250805',
                'haiku': 'claude-3-haiku-20240307',
                'sonnet': 'claude-3-sonnet-20240229'
            },
            'investigation': {
                'project_name': 'Lismore Capital vs Process Holdings',
                'max_tokens': 4000
            }
        }
    
    def _get_default_phase_config(self) -> Dict:
        """Phase-specific configuration"""
        return {
            '0A': {'model': 'haiku', 'max_tokens': 2000, 'temperature': 0.3},
            '0B': {'model': 'haiku', 'max_tokens': 2000, 'temperature': 0.3},
            '1': {'model': 'haiku', 'max_tokens': 3000, 'temperature': 0.3},
            '2': {'model': 'opus', 'max_tokens': 4000, 'temperature': 0.4},
            '3': {'model': 'opus', 'max_tokens': 4000, 'temperature': 0.4},
            '4': {'model': 'opus', 'max_tokens': 4000, 'temperature': 0.5},
            '5': {'model': 'opus', 'max_tokens': 4000, 'temperature': 0.5},
            '6': {'model': 'opus', 'max_tokens': 4000, 'temperature': 0.6},
            '7': {'model': 'opus', 'max_tokens': 4000, 'temperature': 0.7}
        }
    
    def analyse_documents_batch(
        self,
        documents: List[Dict],
        prompt: str,
        context: Optional[Dict] = None,
        phase: Optional[str] = None
    ) -> str:
        """
        Analyse documents with intelligent batching
        
        Args:
            documents: List of document dictionaries
            prompt: Analysis prompt
            context: Previous phase knowledge
            phase: Current phase identifier
            
        Returns:
            Combined analysis from all batches
        """
        
        if not documents:
            return self._call_api([], prompt, context, phase)
        
        # Intelligent batching
        from core.utils import batch_documents_for_api
        batches = batch_documents_for_api(documents, self.batch_config['max_tokens_per_batch'])
        
        print(f"\n📦 Processing {len(documents)} documents in {len(batches)} batches")
        
        # Process batches
        batch_results = []
        for i, batch in enumerate(batches, 1):
            print(f"\n  Batch {i}/{len(batches)}: {len(batch)} documents")
            
            # Build batch-specific prompt
            batch_prompt = self._build_batch_prompt(prompt, i, len(batches))
            
            # Process batch
            result = self._call_api_with_retry(
                documents=batch,
                prompt=batch_prompt,
                context=context,
                phase=phase,
                batch_info={'current': i, 'total': len(batches), 'size': len(batch)}
            )
            
            if result:
                batch_results.append(result)
            
            # Brief pause between batches
            if i < len(batches):
                time.sleep(2)
        
        # Synthesise results if multiple batches
        if len(batch_results) > 1:
            print(f"\n🔄 Synthesising {len(batch_results)} batch results...")
            return self._synthesise_batch_results(batch_results, phase)
        elif batch_results:
            return batch_results[0]
        else:
            return "No results obtained from document analysis"
    
    def _build_batch_prompt(self, base_prompt: str, batch_num: int, total_batches: int) -> str:
        """Build prompt for specific batch"""
        if total_batches == 1:
            return base_prompt
        
        return f"""
BATCH {batch_num} of {total_batches}

{base_prompt}

NOTE: This is a partial document set. Focus on extracting maximum intelligence from these specific documents.
Other batches will cover remaining documents.
"""
    
    def _call_api_with_retry(
        self,
        documents: List[Dict],
        prompt: str,
        context: Optional[Dict],
        phase: Optional[str],
        batch_info: Optional[Dict] = None
    ) -> Optional[str]:
        """API call with intelligent retry logic"""
        
        retries = 0
        delay = self.retry_config['retry_delay']
        
        while retries < self.retry_config['max_retries']:
            try:
                return self._call_api(documents, prompt, context, phase, batch_info)
                
            except anthropic.RateLimitError as e:
                retries += 1
                print(f"⏳ Rate limit hit - waiting {delay} seconds (retry {retries}/{self.retry_config['max_retries']})")
                time.sleep(delay)
                delay *= self.retry_config['backoff_factor']
                
            except anthropic.APIError as e:
                retries += 1
                print(f"⚠️ API error: {e} (retry {retries}/{self.retry_config['max_retries']})")
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return None
        
        print(f"❌ Max retries exceeded for phase {phase}")
        return None
    
    def _call_api(
        self,
        documents: List[Dict],
        prompt: str,
        context: Optional[Dict],
        phase: Optional[str],
        batch_info: Optional[Dict] = None
    ) -> str:
        """Core API call with enhanced configuration"""
        
        # Get phase configuration
        phase_key = phase.replace('phase_', '') if phase else 'default'
        config = self.phase_config.get(phase_key, self.phase_config.get('1'))
        
        # Select model
        model_key = config.get('model', 'opus')
        model = self.models[model_key]
        max_tokens = config.get('max_tokens', 4000)
        temperature = config.get('temperature', 0.4)
        
        # Build messages
        system_prompt = self._build_enhanced_system_prompt(phase)
        user_message = self._build_enhanced_user_message(documents, prompt, context)
        
        # Make API call
        print(f"   🤖 Calling {model_key.upper()} model...")
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        # Track costs
        batch_size = batch_info['size'] if batch_info else len(documents)
        self.cost_tracker.track_call(
            phase=phase or 'general',
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            batch_size=batch_size
        )
        
        # Extract response
        if response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            return "Empty response from API"
    
    def _build_enhanced_system_prompt(self, phase: Optional[str]) -> str:
        """Build sophisticated system prompt"""
        
        base = """You are a senior litigation partner at a magic circle law firm with 30 years' experience in complex commercial disputes.
        
You are acting for LISMORE CAPITAL against Process Holdings in a high-stakes arbitration.

Your approach is:
- ADVERSARIAL: Find every weakness in Process Holdings' position
- FORENSIC: Extract maximum intelligence from every document
- STRATEGIC: Connect findings to winning legal strategies
- PARTISAN: Everything you find must benefit Lismore

You have expertise in:
- Document forensics and pattern recognition
- Contradiction hunting and timeline analysis
- Financial fraud detection
- Witness credibility assessment
- Procedural warfare tactics"""
        
        # Add phase-specific expertise
        if phase:
            phase_key = phase.replace('phase_', '')
            phase_expertise = {
                '0A': "\n\nFor Phase 0A: Focus on weaponising legal doctrines into nuclear options.",
                '0B': "\n\nFor Phase 0B: Identify vulnerabilities in their skeleton arguments.",
                '1': "\n\nFor Phase 1: Map the document landscape and find hot documents.",
                '2': "\n\nFor Phase 2: Build timeline and find impossibilities.",
                '3': "\n\nFor Phase 3: Hunt contradictions relentlessly.",
                '4': "\n\nFor Phase 4: Construct winning narrative.",
                '5': "\n\nFor Phase 5: Identify criminal conduct.",
                '6': "\n\nFor Phase 6: Find procedural knock-outs.",
                '7': "\n\nFor Phase 7: Deploy nuclear options."
            }
            base += phase_expertise.get(phase_key, "")
        
        return base
    
    def _build_enhanced_user_message(
        self,
        documents: List[Dict],
        prompt: str,
        context: Optional[Dict]
    ) -> str:
        """Build sophisticated user message"""
        
        parts = []
        
        # Add context if available
        if context:
            parts.append("="*60)
            parts.append("ACCUMULATED INTELLIGENCE FROM PREVIOUS PHASES:")
            
            # Intelligently summarise context
            if 'knowledge_graph' in context:
                kg = context['knowledge_graph']
                parts.append(f"Nuclear Weapons Available: {len(kg.get('nuclear', []))}")
                parts.append(f"Contradictions Found: {len(kg.get('contradictions', []))}")
                parts.append(f"Key Actors Identified: {len(kg.get('entities', []))}")
            
            if 'strategic_priorities' in context:
                parts.append(f"Strategic Focus: {', '.join(context['strategic_priorities'][:3])}")
            
            parts.append("="*60 + "\n")
        
        # Add main prompt
        parts.append("ANALYSIS REQUIREMENTS:")
        parts.append(prompt)
        parts.append("\n" + "="*60)
        
        # Add documents with metadata
        if documents:
            parts.append(f"\nDOCUMENTS FOR ANALYSIS ({len(documents)} documents):")
            
            for i, doc in enumerate(documents, 1):
                # Add document header with metadata
                metadata = doc.get('metadata', {})
                doc_id = metadata.get('doc_id', f'DOC_{i:04d}')
                
                parts.append(f"\n{'='*40}")
                parts.append(f"[{doc_id}] {doc.get('filename', 'Unknown')}")
                
                if metadata:
                    parts.append(f"Classification: {metadata.get('classification', 'unknown')}")
                    if metadata.get('entities', {}).get('people'):
                        parts.append(f"Key People: {', '.join(metadata['entities']['people'][:3])}")
                    if metadata.get('entities', {}).get('amounts'):
                        parts.append(f"Amounts: {', '.join(metadata['entities']['amounts'][:3])}")
                
                parts.append(f"{'='*40}")
                
                # Add content (intelligently truncated)
                content = doc.get('content', '')
                if len(content) > 50000:
                    # Smart truncation - keep beginning and end
                    parts.append(content[:25000])
                    parts.append("\n[... middle section truncated for length ...]\n")
                    parts.append(content[-20000:])
                else:
                    parts.append(content)
        else:
            parts.append("\n[No documents provided for this analysis]")
        
        return "\n".join(parts)
    
    def _synthesise_batch_results(self, batch_results: List[str], phase: str) -> str:
        """Synthesise multiple batch results into coherent analysis"""
        
        synthesis_prompt = f"""
Synthesise these {len(batch_results)} batch analyses into a single comprehensive analysis.

Combine all findings, eliminate duplicates, and present a unified analysis that:
1. Preserves ALL unique findings from each batch
2. Resolves any contradictions between batches
3. Highlights the most important discoveries
4. Maintains document references [DOC_XXXX]

BATCH RESULTS TO SYNTHESISE:
{'='*60}
"""
        
        for i, result in enumerate(batch_results, 1):
            synthesis_prompt += f"\nBATCH {i}:\n{result[:5000]}\n{'='*40}"
        
        # Use Opus for synthesis (highest quality)
        return self._call_api(
            documents=[],
            prompt=synthesis_prompt,
            context=None,
            phase=f"{phase}_synthesis" if phase else "synthesis"
        )
    
    def generate_cost_report(self) -> str:
        """Generate comprehensive cost report"""
        return self.cost_tracker.generate_cost_report()