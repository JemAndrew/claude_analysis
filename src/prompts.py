#!/usr/bin/env python3
"""
Simplified Prompts for Maximum Claude Capability
Less structure, more intelligence
"""

from typing import Dict, Any, Optional


class Prompts:
    """Simple prompts that let Claude think freely"""
    
    @staticmethod
    def get_system_prompt(phase: str) -> str:
        """Minimal system prompts"""
        
        phase_key = phase.replace("phase_", "").split("_")[0]
        
        if phase_key == "0A":
            return """You are an expert legal strategist analysing legal resources 
to build tactical knowledge for commercial litigation."""
        
        return """You are an elite litigation strategist acting for Lismore Capital 
against Process Holdings. You have full legal knowledge plus specific resources 
from Phase 0A. Win by any legal means."""
    
    @staticmethod
    def get_analysis_prompt(phase: str, batch_num: int = 0, context: Optional[Dict] = None) -> str:
        """Simple, powerful prompts for each phase"""
        
        phase_key = phase.replace("phase_", "").split("_")[0]
        
        # Build context reminder if available
        context_note = ""
        if context and phase_key != "0A":
            if context.get('previous_phases'):
                context_note = "\nYou have knowledge from previous phases. Use it."
            if context.get('legal_arsenal'):
                context_note += "\nYour Phase 0A legal arsenal is available."
        
        prompts = {
            "0A": """Analyse these legal resources to build tactical knowledge.
Focus on:
- Procedural weapons and deadlines
- Powerful doctrine combinations  
- Practical litigation tactics
- Specific formulations worth remembering
- Anything that wins cases

Extract what matters for commercial litigation warfare.""",
            
            "0B": """The case: Lismore Capital v Process Holdings.
Understand everything:
- What really happened
- Who's involved and why
- What claims we have
- What they'll claim
- Early opportunities to attack

This is case intake. Miss nothing.{context}""",
            
            "1": """Document analysis. Find what matters.
- Documents that win the case
- Documents that hurt us
- What's missing that should exist
- Patterns revealing truth
- Priority attack targets{context}""",
            
            "2": """Build the timeline. Find impossibilities.
- When things happened
- When they couldn't have happened as claimed
- Suspicious gaps
- Time-based legal opportunities
- The moment they lost{context}""",
            
            "3": """Find contradictions that destroy them.
- Statements that conflict
- Positions that evolved
- Lies and their evolution
- Missing evidence that must exist
- How to weaponise each contradiction{context}""",
            
            "4": """Construct the winning narrative.
- The story that makes victory inevitable
- Evidence supporting each beat
- Destroying their counter-narrative
- Emotional and legal hooks
- Making the tribunal want us to win{context}""",
            
            "5": """Package evidence for maximum impact.
- Fraud package
- Damages package  
- Bad faith package
- Criminal referral threats
- Optimal deployment sequence{context}""",
            
            "6": """Design endgame strategy.
- How we win at trial
- Settlement pressure points
- Cross-examination devastation
- Summary judgment prospects
- Nuclear options{context}""",
            
            "7": """Find what everyone else missed.
- Hidden patterns
- Novel legal theories
- Overlooked connections
- Game-changing insights
- The thing that ends everything{context}"""
        }
        
        base_prompt = prompts.get(phase_key, "Analyse these documents.")
        
        # Add batch context for continuity
        if batch_num > 1:
            base_prompt = f"Continue Phase {phase_key} analysis (Batch {batch_num}).\n" + base_prompt
        
        # Add critical findings from context
        if context and context.get('critical_findings'):
            base_prompt += "\n\nPriority areas identified: "
            base_prompt += "; ".join(context['critical_findings'][:3])
        
        return base_prompt.format(context=context_note)
    
    @staticmethod
    def get_synthesis_prompt(batch_responses: list, phase: str) -> str:
        """Simple synthesis prompt"""
        
        phase_key = phase.replace("phase_", "").split("_")[0]
        
        # Combine batch excerpts
        combined = "\n---\n".join([r[:1500] for r in batch_responses[:5]])
        
        return f"""Synthesise Phase {phase_key} findings from {len(batch_responses)} batches.

{combined}

Create unified analysis that:
- Identifies the most important findings
- Preserves document references
- Highlights case-winning discoveries
- Notes what needs investigation

Write naturally, not in lists."""
    
    @staticmethod
    def get_self_ask_prompt(phase: str, synthesis: str) -> str:
        """Autonomous self-questioning"""
        
        phase_key = phase.replace("phase_", "").split("_")[0]
        
        return f"""Review your Phase {phase_key} analysis:

{synthesis[:2000]}

What deserves deeper investigation? 
What questions would change the case outcome?
Pursue what matters. Ask yourself what you need to know, then answer it.

No forced structure - follow your instincts."""
    
    @staticmethod
    def get_report_prompt(phase: str, phase_results: Dict[str, Any]) -> str:
        """Generate natural report from analysis"""
        
        phase_key = phase.replace("phase_", "").split("_")[0]
        
        return f"""Based on Phase {phase_key} analysis, write a strategic report.

Analysis completed:
{phase_results.get('synthesis', '')[:3000]}

Self-investigation:
{phase_results.get('self_ask', '')[:1000]}

Write a clear, flowing report that explains:
- What you found
- Why it matters
- How to use it
- What to do next

Write like a strategic memo to the legal team, not a database entry."""