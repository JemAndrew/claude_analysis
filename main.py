#!/usr/bin/env python3
"""
Main Entry Point for Litigation Intelligence System
Staged execution: Phase 0 → Phase 1 → Disclosure Analysis
British English throughout - Lismore v Process Holdings
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv(override=True)

from core.orchestrator import LitigationOrchestrator
import argparse


def main():
    """Main entry point with staged execution"""
    
    parser = argparse.ArgumentParser(
        description='Litigation Intelligence System - Lismore v Process Holdings'
    )
    parser.add_argument(
        'stage',
        choices=['phase0', 'phase1', 'full'],
        help='Which stage to run: phase0 (knowledge absorption), phase1 (disclosure iteration), or full (complete analysis)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum disclosure iterations (default: 3)'
    )
    
    args = parser.parse_args()
    
    orchestrator = LitigationOrchestrator()
    
    if args.stage == 'phase0':
        run_phase_0(orchestrator)
    elif args.stage == 'phase1':
        run_phase_1(orchestrator)
    elif args.stage == 'full':
        run_full_analysis(orchestrator, args.max_iterations)


def run_phase_0(orchestrator):
    """
    Phase 0: Knowledge Absorption
    Loads legal_knowledge + case_context folders
    Cost: £8-12
    Time: 30-60 minutes
    """
    
    print("\n" + "="*60)
    print("PHASE 0: KNOWLEDGE ABSORPTION")
    print("="*60)
    print("\nThis phase will:")
    print("  - Load legal_knowledge folder (33 documents)")
    print("  - Load case_context folder (2,032 documents)")
    print("  - Total: 2,065 documents")
    print("  - Synthesise legal framework with Claude Sonnet 4.5")
    print("  - Build knowledge graph foundation")
    print("\nEstimated cost: £8-12 ($10-15)")
    print("Estimated time: 30-60 minutes")
    print("\nPrompt caching: Enabled (90% savings on repeated context)")
    
    response = input("\nProceed with Phase 0? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\nExecuting Phase 0...")
    print("This will take 30-60 minutes. Keep laptop plugged in.\n")
    
    try:
        results = orchestrator.execute_single_phase('0')
        
        print("\n" + "="*60)
        print("PHASE 0 COMPLETE")
        print("="*60)
        print(f"Documents processed: {results.get('documents_processed', 0)}")
        
        # Print usage summary
        orchestrator.api_client.print_usage_summary()
        
        print("\nKnowledge foundation built successfully.")
        print("Ready for disclosure analysis.")
        print("\nNext step: python main.py phase1")
        
    except Exception as e:
        print(f"\n❌ Error in Phase 0: {e}")
        raise


def run_phase_1(orchestrator):
    """
    Phase 1: Disclosure Analysis
    Analyses all 18,004 disclosure documents
    Cost: £100-150
    Time: Multiple hours
    """
    
    print("\n" + "="*60)
    print("PHASE 1: DISCLOSURE ANALYSIS")
    print("="*60)
    print("\nThis phase will:")
    print("  - Analyse disclosure folder (18,004 documents)")
    print("  - Run iterative analysis until convergence")
    print("  - Auto-spawn investigations on critical findings")
    print("  - Generate comprehensive case intelligence")
    
    # Check if Phase 0 completed
    if '0' not in orchestrator.state.get('phases_completed', []):
        print("\n⚠️  Phase 0 not completed yet!")
        print("Run: python main.py phase0")
        return
    
    print("\n⚠️  WARNING: This will process 18,004 documents")
    print("Estimated cost: £100-150 ($120-180)")
    print("Estimated time: 10-20 hours")
    print("\nRecommendation: Run on cloud VM or desktop (not laptop)")
    
    response = input("\nProceed with Phase 1? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\nExecuting Phase 1...")
    
    try:
        # Run disclosure iterations
        results = orchestrator.execute_full_analysis(
            start_phase='1',
            max_iterations=3
        )
        
        print("\n" + "="*60)
        print("PHASE 1 COMPLETE")
        print("="*60)
        
        orchestrator.api_client.print_usage_summary()
        
        print(f"\nReports saved: {orchestrator.config.reports_dir}")
        
    except Exception as e:
        print(f"\n❌ Error in Phase 1: {e}")
        raise


def run_full_analysis(orchestrator, max_iterations):
    """
    Run complete analysis: Phase 0 → Disclosure Analysis
    Cost: £120-180
    Time: 12-24 hours
    """
    
    print("\n" + "="*60)
    print("FULL ANALYSIS - ALL DOCUMENTS")
    print("="*60)
    print("\nThis will run:")
    print("  Phase 0: Knowledge Absorption (2,065 docs)")
    print("  Phase 1: Disclosure Analysis (18,004 docs)")
    print("  Investigations: Auto-spawned on critical findings")
    print("  Synthesis: Final strategic report")
    
    print("\n⚠️  TOTAL: 20,069 documents")
    print("Estimated cost: £120-180 ($150-220)")
    print("Estimated time: 12-24 hours")
    print("\nSTRONGLY RECOMMENDED: Run on cloud VM")
    
    response = input("\nProceed with FULL analysis? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    try:
        results = orchestrator.execute_full_analysis(
            start_phase='0',
            max_iterations=max_iterations
        )
        
        print("\n" + "="*60)
        print("COMPLETE ANALYSIS FINISHED")
        print("="*60)
        
        orchestrator.api_client.print_usage_summary()
        
        print(f"\nCheck reports: {orchestrator.config.reports_dir}")
        print(f"Check knowledge graph: {orchestrator.config.knowledge_dir}")
        
    except Exception as e:
        print(f"\n❌ Error in full analysis: {e}")
        raise


if __name__ == "__main__":
    main()