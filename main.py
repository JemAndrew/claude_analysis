#!/usr/bin/env python3
"""
Main Entry Point for Litigation Intelligence System
Tiered execution: Phase 0 → Phase 1 (3-tier) → Additional Phases
British English throughout - Lismore v Process Holdings
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.core.orchestrator import LitigationOrchestrator
import argparse


def count_documents(directory):
    """Count documents in a directory"""
    if not directory.exists():
        return 0
    extensions = ['.pdf', '.txt', '.docx', '.doc', '.json', '.html', '.md']
    return sum(len(list(directory.glob(f"**/*{ext}"))) for ext in extensions)


def main():
    """Main entry point with staged execution"""
    
    parser = argparse.ArgumentParser(
        description='Litigation Intelligence System - Lismore v Process Holdings'
    )
    parser.add_argument(
        'stage',
        choices=['phase0', 'phase1', 'estimate', 'status', 'full'],
        help='Which stage to run'
    )
    
    args = parser.parse_args()
    
    orchestrator = LitigationOrchestrator()
    
    if args.stage == 'phase0':
        run_phase_0(orchestrator)
    elif args.stage == 'phase1':
        run_phase_1(orchestrator)
    elif args.stage == 'estimate':
        show_cost_estimate(orchestrator)
    elif args.stage == 'status':
        show_status(orchestrator)
    elif args.stage == 'full':
        run_full_analysis(orchestrator)


def show_cost_estimate(orchestrator):
    """Show detailed cost estimates"""
    
    print("\n" + "="*70)
    print("COST ESTIMATION")
    print("="*70)
    
    # Count documents
    legal_count = count_documents(orchestrator.config.legal_knowledge_dir)
    case_count = count_documents(orchestrator.config.case_context_dir)
    disclosure_count = count_documents(orchestrator.config.disclosure_dir)
    
    print(f"\nDocument Inventory:")
    print(f"  Legal Knowledge: {legal_count} documents")
    print(f"  Case Context: {case_count} documents")
    print(f"  Disclosure: {disclosure_count} documents")
    print(f"  Total: {legal_count + case_count + disclosure_count} documents")
    
    # Use batch manager's estimation
    estimates = orchestrator.batch_manager.estimate_total_batches(
        phase_0_docs=legal_count + case_count,
        tier_1_docs=min(500, disclosure_count),
        tier_2_docs=max(0, disclosure_count - 500)
    )
    
    print(f"\n{'='*70}")
    print("PHASE 0: KNOWLEDGE FOUNDATION")
    print(f"{'='*70}")
    print(f"  Documents: {estimates['phase_0']['documents']}")
    print(f"  Batches: {estimates['phase_0']['batches']}")
    print(f"  Estimated Cost: £{estimates['phase_0']['cost_gbp']}")
    print(f"  Estimated Time: {int(estimates['phase_0']['batches'] * 6)} minutes")
    
    print(f"\n{'='*70}")
    print("PHASE 1: TIERED DISCLOSURE ANALYSIS")
    print(f"{'='*70}")
    print(f"\n  Tier 1 (Deep Analysis of Priority Folders):")
    print(f"    Documents: {estimates['tier_1']['documents']}")
    print(f"    Batches: {estimates['tier_1']['batches']}")
    print(f"    Cost: £{estimates['tier_1']['cost_gbp']}")
    
    print(f"\n  Tier 2 (Metadata Scan of Remaining):")
    print(f"    Documents: {estimates['tier_2']['documents']}")
    print(f"    Batches: {estimates['tier_2']['batches']}")
    print(f"    Cost: £{estimates['tier_2']['cost_gbp']}")
    
    print(f"\n  Tier 3 (Targeted Deep Dive on Flagged):")
    print(f"    Estimated Flagged: {estimates['tier_3']['documents']}")
    print(f"    Batches: {estimates['tier_3']['batches']}")
    print(f"    Cost: £{estimates['tier_3']['cost_gbp']}")
    
    phase_1_total = (estimates['tier_1']['cost_gbp'] + 
                     estimates['tier_2']['cost_gbp'] + 
                     estimates['tier_3']['cost_gbp'])
    
    print(f"\n  Total Phase 1: £{phase_1_total:.2f}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL ESTIMATED COST: £{estimates['estimated_cost_gbp']}")
    print(f"TOTAL BATCHES: {estimates['total_batches']}")
    print(f"TOTAL ESTIMATED TIME: {estimates['estimated_hours']} hours")
    print(f"{'='*70}\n")


def show_status(orchestrator):
    """Show system status"""
    
    print("\n" + "="*70)
    print("SYSTEM STATUS")
    print("="*70)
    
    # Phase completion
    completed = orchestrator.state.get('phases_completed', [])
    print(f"\nPhases Completed: {', '.join(completed) if completed else 'None'}")
    
    # Knowledge graph stats
    stats = orchestrator.knowledge_graph.get_statistics()
    print(f"\nKnowledge Graph:")
    print(f"  Entities: {stats.get('entities', 0)}")
    print(f"  Relationships: {stats.get('relationships', 0)}")
    print(f"  Contradictions: {stats.get('contradictions', 0)}")
    print(f"  Patterns: {stats.get('patterns', 0)}")
    print(f"  Timeline Events: {stats.get('timeline_events', 0)}")
    
    # Batch manager stats
    batch_stats = orchestrator.batch_manager.get_statistics()
    print(f"\nBatch Processing:")
    print(f"  Batches Created: {batch_stats.get('batches_created', 0)}")
    print(f"  Documents Processed: {batch_stats.get('documents_processed', 0)}")
    
    if batch_stats.get('current_batch_sizes'):
        print(f"  Current Batch Sizes:")
        for batch_type, size in batch_stats['current_batch_sizes'].items():
            print(f"    {batch_type}: {size} docs/batch")
    
    print(f"\nActive Investigations: {len(orchestrator.state.get('active_investigations', []))}")
    print("")


def run_phase_0(orchestrator):
    """
    Phase 0: Knowledge Absorption
    Loads legal_knowledge + case_context folders
    """
    
    print("\n" + "="*70)
    print("PHASE 0: KNOWLEDGE ABSORPTION")
    print("="*70)
    
    # Count documents
    legal_count = count_documents(orchestrator.config.legal_knowledge_dir)
    case_count = count_documents(orchestrator.config.case_context_dir)
    total_docs = legal_count + case_count
    
    print(f"\nThis phase will:")
    print(f"  - Load legal_knowledge folder ({legal_count} documents)")
    print(f"  - Load case_context folder ({case_count} documents)")
    print(f"  - Total: {total_docs} documents")
    print(f"  - Synthesise legal framework with Claude Sonnet 4")
    print(f"  - Build knowledge graph foundation")
    
    # Estimate
    batch_size = orchestrator.config.batch_strategy['phase_0_batch_size']
    batches = (total_docs + batch_size - 1) // batch_size
    cost = batches * 0.20
    time_mins = batches * 6
    
    print(f"\nEstimated cost: £{cost:.2f}")
    print(f"Estimated time: {time_mins} minutes ({time_mins/60:.1f} hours)")
    print(f"Batch size: {batch_size} docs/batch")
    print(f"Total batches: {batches}")
    print("\nPrompt caching: Enabled (cost savings on repeated context)")
    
    response = input("\nProceed with Phase 0? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print(f"\nExecuting Phase 0...")
    print(f"This will take approximately {time_mins/60:.1f} hours. Keep system running.\n")
    
    try:
        results = orchestrator.execute_single_phase('0')
        
        print("\n" + "="*70)
        print("PHASE 0 COMPLETE")
        print("="*70)
        print(f"Documents processed: {results.get('documents_processed', 0)}")
        print(f"Batches completed: {results.get('batches', 0)}")
        
        # Print usage summary
        if hasattr(orchestrator.api_client, 'print_usage_summary'):
            orchestrator.api_client.print_usage_summary()
        
        print("\nKnowledge foundation built successfully.")
        print(f"Output saved to: {orchestrator.config.analysis_dir / 'phase_0'}")
        print("\nNext step: python main.py phase1")
        
    except Exception as e:
        print(f"\n❌ Error in Phase 0: {e}")
        import traceback
        traceback.print_exc()
        raise


def run_phase_1(orchestrator):
    """
    Phase 1: THREE-TIER Disclosure Analysis
    """
    
    print("\n" + "="*70)
    print("PHASE 1: TIERED DISCLOSURE ANALYSIS")
    print("="*70)
    
    # Check if Phase 0 completed
    if '0' not in orchestrator.state.get('phases_completed', []):
        print("\n⚠️  Phase 0 not completed yet!")
        print("Run: python main.py phase0")
        return
    
    # Count disclosure documents
    disclosure_count = count_documents(orchestrator.config.disclosure_dir)
    
    print(f"\nThis phase uses 3-tier intelligent analysis:")
    print(f"  Total disclosure documents: {disclosure_count}")
    
    print(f"\n  TIER 1: Deep Analysis (~500 priority documents)")
    print(f"    - Uses full senior litigator prompts")
    print(f"    - Spawns investigations on critical findings")
    print(f"    - Priority folders: Document Production, Witness Statements, etc.")
    
    print(f"\n  TIER 2: Metadata Scan (~{disclosure_count - 500} remaining documents)")
    print(f"    - Fast lightweight scanning")
    print(f"    - Flags suspicious documents for Tier 3")
    print(f"    - Uses Haiku 4 for speed/cost efficiency")
    
    print(f"\n  TIER 3: Targeted Deep Dive (flagged documents)")
    print(f"    - Deep analysis of documents flagged in Tier 2")
    print(f"    - Full forensic investigation")
    
    # Estimate
    estimates = orchestrator.batch_manager.estimate_total_batches(
        phase_0_docs=0,
        tier_1_docs=min(500, disclosure_count),
        tier_2_docs=max(0, disclosure_count - 500)
    )
    
    phase_1_cost = (estimates['tier_1']['cost_gbp'] + 
                    estimates['tier_2']['cost_gbp'] + 
                    estimates['tier_3']['cost_gbp'])
    
    print(f"\nEstimated cost: £{phase_1_cost:.2f}")
    print(f"Estimated time: {estimates['estimated_hours']:.1f} hours")
    
    response = input("\nProceed with Phase 1 (Tiered Analysis)? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print("\nExecuting Phase 1 (3-Tier Analysis)...")
    
    try:
        results = orchestrator.execute_single_phase('1')
        
        print("\n" + "="*70)
        print("PHASE 1 COMPLETE")
        print("="*70)
        
        # Print tier results
        if 'tiers' in results:
            if 'tier_1' in results['tiers']:
                t1 = results['tiers']['tier_1']
                print(f"\nTier 1 Results:")
                print(f"  Documents analysed: {t1.get('documents_analysed', 0)}")
                print(f"  Critical findings: {len(t1.get('critical_findings', []))}")
                print(f"  Contradictions: {len(t1.get('contradictions', []))}")
                print(f"  Investigations spawned: {t1.get('investigations_spawned', 0)}")
            
            if 'tier_2' in results['tiers']:
                t2 = results['tiers']['tier_2']
                print(f"\nTier 2 Results:")
                print(f"  Documents scanned: {t2.get('documents_scanned', 0)}")
                print(f"  Flagged for deep analysis: {len(t2.get('flagged_documents', []))}")
            
            if 'tier_3' in results['tiers']:
                t3 = results['tiers']['tier_3']
                print(f"\nTier 3 Results:")
                print(f"  Documents analysed: {t3.get('documents_analysed', 0)}")
                print(f"  Critical findings: {len(t3.get('critical_findings', []))}")
        
        if hasattr(orchestrator.api_client, 'print_usage_summary'):
            orchestrator.api_client.print_usage_summary()
        
        print(f"\nOutput saved to: {orchestrator.config.analysis_dir / 'phase_1'}")
        
    except Exception as e:
        print(f"\n❌ Error in Phase 1: {e}")
        import traceback
        traceback.print_exc()
        raise


def run_full_analysis(orchestrator):
    """
    Run complete analysis: Phase 0 → Phase 1 (3-tier)
    """
    
    print("\n" + "="*70)
    print("FULL ANALYSIS - PHASE 0 + PHASE 1")
    print("="*70)
    
    # Count all documents
    legal_count = count_documents(orchestrator.config.legal_knowledge_dir)
    case_count = count_documents(orchestrator.config.case_context_dir)
    disclosure_count = count_documents(orchestrator.config.disclosure_dir)
    total = legal_count + case_count + disclosure_count
    
    print(f"\nThis will run:")
    print(f"  Phase 0: Knowledge Absorption ({legal_count + case_count} docs)")
    print(f"  Phase 1: 3-Tier Disclosure Analysis ({disclosure_count} docs)")
    print(f"  Total: {total} documents")
    
    # Estimate
    estimates = orchestrator.batch_manager.estimate_total_batches(
        phase_0_docs=legal_count + case_count,
        tier_1_docs=min(500, disclosure_count),
        tier_2_docs=max(0, disclosure_count - 500)
    )
    
    print(f"\nEstimated cost: £{estimates['estimated_cost_gbp']}")
    print(f"Estimated time: {estimates['estimated_hours']} hours")
    
    response = input("\nProceed with FULL analysis? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    try:
        # Run Phase 0
        print("\n" + "="*70)
        print("Starting Phase 0...")
        print("="*70)
        results_0 = orchestrator.execute_single_phase('0')
        print(f"Phase 0 complete: {results_0.get('documents_processed', 0)} documents")
        
        # Run Phase 1
        print("\n" + "="*70)
        print("Starting Phase 1...")
        print("="*70)
        results_1 = orchestrator.execute_single_phase('1')
        
        print("\n" + "="*70)
        print("COMPLETE ANALYSIS FINISHED")
        print("="*70)
        
        if hasattr(orchestrator.api_client, 'print_usage_summary'):
            orchestrator.api_client.print_usage_summary()
        
        print(f"\nOutputs saved to:")
        print(f"  Analysis: {orchestrator.config.analysis_dir}")
        print(f"  Reports: {orchestrator.config.reports_dir}")
        print(f"  Knowledge Graph: {orchestrator.config.knowledge_dir}")
        
    except Exception as e:
        print(f"\n❌ Error in full analysis: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)