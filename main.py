#!/usr/bin/env python3
"""
Main Entry Point for Litigation Intelligence System
Staged execution: Phase 0 → Phase 1 → Phase 2-N
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
        choices=['phase0', 'phase1', 'investigate', 'full'],
        help='Which stage to run: phase0 (legal knowledge), phase1 (case understanding), investigate (phase 2-N), or full (all phases)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum investigation iterations (default: 5)'
    )
    
    args = parser.parse_args()
    
    orchestrator = LitigationOrchestrator()
    
    if args.stage == 'phase0':
        run_phase_0(orchestrator)
    elif args.stage == 'phase1':
        run_phase_1(orchestrator)
    elif args.stage == 'investigate':
        run_investigations(orchestrator, args.max_iterations)
    elif args.stage == 'full':
        run_full_analysis(orchestrator, args.max_iterations)


def run_phase_0(orchestrator):
    """
    Phase 0: Legal Knowledge Mastery
    Loads legal documents and builds legal framework
    Cost: ~$0.10
    Time: ~5 minutes
    """
    
    print("\n" + "="*60)
    print("PHASE 0: LEGAL KNOWLEDGE MASTERY")
    print("="*60)
    print("\nThis phase will:")
    print("  - Load all legal documents")
    print("  - Synthesise legal framework with Claude Sonnet 4.5")
    print("  - Store legal knowledge for later phases")
    print("\nEstimated cost: $0.10")
    print("Estimated time: 5 minutes")
    
    response = input("\nProceed with Phase 0? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\nExecuting Phase 0...")
    results = orchestrator.execute_phase('0')
    
    print("\n" + "="*60)
    print("PHASE 0 COMPLETE")
    print("="*60)
    print(f"Documents processed: {results.get('documents_processed', 0)}")
    print(f"Tokens: {results['metadata']['input_tokens']:,} in / {results['metadata']['output_tokens']:,} out")
    
    cost = (results['metadata']['input_tokens'] / 1000 * 0.003) + \
           (results['metadata']['output_tokens'] / 1000 * 0.015)
    print(f"Cost: ${cost:.2f}")
    
    print("\nLegal framework stored. Ready for Phase 1.")
    print("\nNext step: python main.py phase1")


def run_phase_1(orchestrator):
    """
    Phase 1: Complete Case Understanding
    Loads all case documents, builds understanding, marks discoveries
    Cost: ~$5-10
    Time: ~15-30 minutes
    """
    
    print("\n" + "="*60)
    print("PHASE 1: COMPLETE CASE UNDERSTANDING")
    print("="*60)
    print("\nThis phase will:")
    print("  - Load ALL case documents (including subdirectories)")
    print("  - Send to Claude Sonnet 4.5 for complete understanding")
    print("  - Mark discoveries: [NUCLEAR], [CRITICAL], [INVESTIGATE]")
    print("  - Prepare for autonomous investigation")
    
    # Check if Phase 0 completed
    if '0' not in orchestrator.state.get('phases_completed', []):
        print("\n⚠️  Phase 0 not completed yet!")
        print("Run: python main.py phase0")
        return
    
    # Estimate documents
    import os
    case_dir = orchestrator.config.case_documents_dir
    doc_count = sum(1 for root, dirs, files in os.walk(case_dir) 
                    for file in files if file.endswith(('.pdf', '.docx', '.doc')))
    
    print(f"\nFound ~{doc_count} case documents")
    print(f"Estimated cost: ${doc_count * 0.05:.2f} - ${doc_count * 0.10:.2f}")
    print(f"Estimated time: 15-30 minutes")
    
    response = input("\nProceed with Phase 1? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\nExecuting Phase 1...")
    results = orchestrator.execute_phase('1')
    
    print("\n" + "="*60)
    print("PHASE 1 COMPLETE")
    print("="*60)
    print(f"Documents processed: {results.get('documents_processed', 0)}")
    print(f"Discoveries: {len(results.get('discoveries', []))}")
    print(f"Tokens: {results['metadata']['input_tokens']:,} in / {results['metadata']['output_tokens']:,} out")
    
    cost = (results['metadata']['input_tokens'] / 1000 * 0.003) + \
           (results['metadata']['output_tokens'] / 1000 * 0.015)
    print(f"Cost: ${cost:.2f}")
    
    # Show discoveries
    discoveries = results.get('discoveries', [])
    if discoveries:
        nuclear = [d for d in discoveries if d['type'] == 'NUCLEAR']
        critical = [d for d in discoveries if d['type'] == 'CRITICAL']
        investigate = [d for d in discoveries if d['type'] == 'INVESTIGATE']
        
        print(f"\nDiscoveries marked:")
        print(f"  NUCLEAR: {len(nuclear)}")
        print(f"  CRITICAL: {len(critical)}")
        print(f"  INVESTIGATE: {len(investigate)}")
    
    print("\nCase understanding complete. Ready for investigation.")
    print("\nNext step: python main.py investigate")


def run_investigations(orchestrator, max_iterations):
    """
    Phase 2-N: Autonomous Investigation
    Claude investigates freely until convergence
    Cost: ~$10-40
    Time: ~30-90 minutes
    """
    
    print("\n" + "="*60)
    print("PHASE 2-N: AUTONOMOUS INVESTIGATION")
    print("="*60)
    print("\nThis phase will:")
    print("  - Let Claude investigate ANYTHING it finds interesting")
    print("  - No predetermined focus (complete autonomy)")
    print(f"  - Run up to {max_iterations} investigation iterations")
    print("  - Stop when no new critical discoveries")
    print("  - Generate final strategic synthesis")
    
    # Check prerequisites
    if '0' not in orchestrator.state.get('phases_completed', []):
        print("\n⚠️  Phase 0 not completed! Run: python main.py phase0")
        return
    if '1' not in orchestrator.state.get('phases_completed', []):
        print("\n⚠️  Phase 1 not completed! Run: python main.py phase1")
        return
    
    print(f"\nEstimated cost: $10-$40")
    print(f"Estimated time: 30-90 minutes")
    
    response = input("\nProceed with autonomous investigation? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\nStarting autonomous investigation...")
    
    # Run investigation iterations
    converged = False
    iteration = 2
    
    while not converged and iteration < (2 + max_iterations):
        print(f"\n{'='*60}")
        print(f"INVESTIGATION ITERATION {iteration - 1}")
        print(f"{'='*60}")
        
        results = orchestrator.execute_phase(str(iteration))
        
        converged = results.get('converged', False)
        
        if converged:
            print("\n✅ INVESTIGATION CONVERGED")
            break
        
        iteration += 1
    
    # Final synthesis
    print("\n" + "="*60)
    print("FINAL SYNTHESIS")
    print("="*60)
    
    synthesis = orchestrator._execute_synthesis({'phases': {}})
    
    print("\n" + "="*60)
    print("INVESTIGATION COMPLETE")
    print("="*60)
    print(f"Iterations completed: {iteration - 2}")
    print(f"Reports saved: {orchestrator.config.reports_dir}")
    
    # Show usage
    api_stats = orchestrator.api_client.get_usage_statistics()
    print(f"\nTotal API Usage:")
    print(f"  Calls: {api_stats['summary']['total_calls']}")
    print(f"  Tokens: {api_stats['summary']['total_input_tokens']:,} in / {api_stats['summary']['total_output_tokens']:,} out")
    print(f"  Cost: ${api_stats['summary']['estimated_cost_usd']:.2f}")


def run_full_analysis(orchestrator, max_iterations):
    """
    Run complete analysis: Phase 0 → Phase 1 → Phase 2-N
    Cost: ~$20-50
    Time: ~1-2 hours
    """
    
    print("\n" + "="*60)
    print("FULL AUTONOMOUS ANALYSIS")
    print("="*60)
    print("\nThis will run ALL phases:")
    print("  Phase 0: Legal Knowledge Mastery")
    print("  Phase 1: Complete Case Understanding")
    print("  Phase 2-N: Autonomous Investigation")
    print("  Final: Strategic Synthesis")
    
    print(f"\nEstimated cost: $20-$50")
    print(f"Estimated time: 1-2 hours")
    
    response = input("\nProceed with FULL analysis? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    results = orchestrator.execute_full_analysis(
        start_phase='0',
        max_iterations=max_iterations
    )
    
    print("\n" + "="*60)
    print("COMPLETE ANALYSIS FINISHED")
    print("="*60)
    print(f"Check reports: {orchestrator.config.reports_dir}")


if __name__ == "__main__":
    main()