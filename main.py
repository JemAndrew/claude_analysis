#!/usr/bin/env python3
"""
Main Entry Point for Litigation Intelligence System
UPDATED: Now includes document prioritisation command
Tiered execution: Prioritise → Phase 0 → Phase 1 (3-tier) → Additional Phases
British English throughout - Lismore v Process Holdings
"""

import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


from dotenv import load_dotenv
load_dotenv(override=True)

from core.orchestrator import LitigationOrchestrator
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
        choices=['prioritise', 'phase0', 'phase1', 'estimate', 'status', 'full'],
        help='Which stage to run'
    )
    
    args = parser.parse_args()
    
    orchestrator = LitigationOrchestrator()
    
    if args.stage == 'prioritise':
        run_prioritisation(orchestrator)
    elif args.stage == 'phase0':
        run_phase_0(orchestrator)
    elif args.stage == 'phase1':
        run_phase_1(orchestrator)
    elif args.stage == 'estimate':
        show_cost_estimate(orchestrator)
    elif args.stage == 'status':
        show_status(orchestrator)
    elif args.stage == 'full':
        run_full_analysis(orchestrator)


def run_prioritisation(orchestrator):
    """
    NEW COMMAND: python main.py prioritise
    
    Scores all documents using cheap Haiku, selects top N for analysis
    Solves the budget constraint problem (21k docs = £2,198, but budget = £200)
    """
    
    from utils.document_prioritiser import DocumentPrioritiser
    
    print("\n" + "="*70)
    print("DOCUMENT PRIORITISATION")
    print("="*70)
    
    # Count disclosure documents
    disclosure_count = count_documents(orchestrator.config.disclosure_dir)
    
    print(f"\nTotal disclosure documents: {disclosure_count}")
    
    if disclosure_count == 0:
        print("\n⚠️  No documents found in disclosure directory!")
        print(f"Expected location: {orchestrator.config.disclosure_dir}")
        return
    
    # Initialise prioritiser
    prioritiser = DocumentPrioritiser(orchestrator.config)
    
    # Estimate cost
    estimate = prioritiser.estimate_prioritisation_cost(disclosure_count)
    
    print(f"\nPrioritisation estimate:")
    print(f"  Documents to score: {estimate['document_count']}")
    print(f"  Estimated cost: £{estimate['cost_gbp']}")
    print(f"  Estimated time: {estimate['estimated_time_hours']} hours")
    print(f"    ({estimate['estimated_time_minutes']} minutes)")
    
    print(f"\nScoring strategy:")
    print(f"  Uses: Haiku 4 (£0.25/1M tokens)")
    print(f"  Method: Filename + first 2000 chars only")
    print(f"  Output: Priority scores 0-10 for each document")
    print(f"  Caching: Scores cached to avoid rescoring")
    
    # Get user parameters
    print(f"\nPrioritisation parameters:")
    
    top_n_input = input(f"  How many top documents to select? [default: 800]: ").strip()
    top_n = int(top_n_input) if top_n_input else 800
    
    min_score_input = input(f"  Minimum priority score (0-10)? [default: 7.0]: ").strip()
    min_score = float(min_score_input) if min_score_input else 7.0
    
    print(f"\nWill select:")
    print(f"  - Top {top_n} documents")
    print(f"  - With score >= {min_score}")
    print(f"  - (Whichever results in fewer documents)")
    
    response = input(f"\nProceed with prioritisation? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    try:
        # Run prioritisation
        print("\n" + "="*70)
        print("SCORING DOCUMENTS...")
        print("="*70)
        
        priority_docs, all_scored_docs = prioritiser.prioritise_folder(
            folder_path=orchestrator.config.disclosure_dir,
            top_n=top_n,
            min_score=min_score
        )
        
        # Save priority list
        priority_list_file = orchestrator.config.output_dir / "priority_documents.json"
        prioritiser.save_priority_list(priority_docs, priority_list_file)
        
        # Save full scores for reference
        scores_file = orchestrator.config.output_dir / "all_document_scores.json"
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump([
                {
                    'filename': doc.get('metadata', {}).get('filename', 'unknown'),
                    'score': doc.get('priority_score', 0.0),
                    'source_folder': doc.get('metadata', {}).get('source_folder', ''),
                    'doc_type': doc.get('metadata', {}).get('classification', 'general')
                }
                for doc in all_scored_docs
            ], f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print("PRIORITISATION COMPLETE")
        print(f"{'='*70}")
        print(f"\nFiles created:")
        print(f"  Priority list: {priority_list_file}")
        print(f"  All scores: {scores_file}")
        print(f"  Score cache: {prioritiser.scores_file}")
        
        print(f"\nNext steps:")
        print(f"  1. Review {priority_list_file.name}")
        print(f"  2. Run: python main.py estimate")
        print(f"  3. Run: python main.py phase0")
        print(f"  4. Run: python main.py phase1")
        
        # Show budget impact
        print(f"\n{'='*70}")
        print("BUDGET IMPACT")
        print(f"{'='*70}")
        print(f"Original cost (all {disclosure_count} docs): ~£2,198")
        print(f"New cost (top {len(priority_docs)} docs): ~£{int(len(priority_docs) * 2198 / disclosure_count)}")
        print(f"Savings: ~£{2198 - int(len(priority_docs) * 2198 / disclosure_count)}")
        
    except Exception as e:
        print(f"\n❌ Error during prioritisation: {e}")
        import traceback
        traceback.print_exc()
        raise


def show_cost_estimate(orchestrator):
    """Show detailed cost estimates"""
    
    print("\n" + "="*70)
    print("COST ESTIMATION")
    print("="*70)
    
    # Count documents
    legal_count = count_documents(orchestrator.config.legal_knowledge_dir)
    case_count = count_documents(orchestrator.config.case_context_dir)
    disclosure_count = count_documents(orchestrator.config.disclosure_dir)
    
    # Check if prioritisation has been done
    priority_file = orchestrator.config.output_dir / "priority_documents.json"
    if priority_file.exists():
        with open(priority_file, 'r', encoding='utf-8') as f:
            priority_data = json.load(f)
        priority_count = len(priority_data['documents'])
        print(f"\n✅ Prioritisation complete!")
        print(f"  Using {priority_count} priority documents (from {disclosure_count} total)")
        disclosure_count = priority_count  # Use priority count
    else:
        print(f"\n⚠️  Prioritisation not run yet!")
        print(f"  Estimates based on ALL {disclosure_count} disclosure documents")
        print(f"  Run 'python main.py prioritise' to reduce costs")
    
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
    
    print(f"\n  Tier 3 (Targeted Deep Dive - estimated 10% flagged):")
    print(f"    Documents: {estimates['tier_3']['documents']}")
    print(f"    Batches: {estimates['tier_3']['batches']}")
    print(f"    Cost: £{estimates['tier_3']['cost_gbp']}")
    
    total_cost = (estimates['phase_0']['cost_gbp'] + 
                  estimates['tier_1']['cost_gbp'] + 
                  estimates['tier_2']['cost_gbp'] + 
                  estimates['tier_3']['cost_gbp'])
    
    total_time = (estimates['phase_0']['batches'] + 
                  estimates['tier_1']['batches'] + 
                  estimates['tier_2']['batches'] + 
                  estimates['tier_3']['batches']) * 6
    
    print(f"\n{'='*70}")
    print("TOTAL ESTIMATES")
    print(f"{'='*70}")
    print(f"  Total Cost: £{total_cost}")
    print(f"  Total Time: {int(total_time / 60)} hours ({total_time} minutes)")
    print(f"  Budget Status: {'✅ WITHIN BUDGET' if total_cost <= 200 else '⚠️  OVER BUDGET'}")
    
    if total_cost > 200 and not priority_file.exists():
        print(f"\n⚠️  WARNING: Estimated cost exceeds £200 budget!")
        print(f"  Run 'python main.py prioritise' to reduce costs by 80-90%")


def show_status(orchestrator):
    """Show current system status"""
    
    print("\n" + "="*70)
    print("SYSTEM STATUS")
    print("="*70)
    
    # Check phases completed
    phases_completed = orchestrator.state.get('phases_completed', [])
    
    print(f"\nPhases completed: {len(phases_completed)}")
    for phase in phases_completed:
        print(f"  ✅ Phase {phase}")
    
    # Check if prioritisation done
    priority_file = orchestrator.config.output_dir / "priority_documents.json"
    if priority_file.exists():
        with open(priority_file, 'r', encoding='utf-8') as f:
            priority_data = json.load(f)
        print(f"\n✅ Prioritisation complete:")
        print(f"  Priority documents: {len(priority_data['documents'])}")
        print(f"  Timestamp: {priority_data['timestamp']}")
    else:
        print(f"\n⚠️  Prioritisation not yet run")
        print(f"  Run: python main.py prioritise")
    
    # Check knowledge graph stats
    try:
        stats = orchestrator.knowledge_graph.get_statistics()
        print(f"\nKnowledge Graph:")
        print(f"  Entities: {stats.get('entities', 0)}")
        print(f"  Contradictions: {stats.get('contradictions', 0)}")
        print(f"  Patterns: {stats.get('patterns', 0)}")
    except:
        print(f"\nKnowledge Graph: Not yet populated")
    
    # Check outputs
    if orchestrator.config.analysis_dir.exists():
        phase_dirs = list(orchestrator.config.analysis_dir.glob("phase_*"))
        print(f"\nOutput directories: {len(phase_dirs)}")
        for phase_dir in sorted(phase_dirs):
            print(f"  📁 {phase_dir.name}")


def run_phase_0(orchestrator):
    """
    Phase 0: Knowledge Foundation
    Absorbs legal knowledge + case context
    """
    
    print("\n" + "="*70)
    print("PHASE 0: KNOWLEDGE FOUNDATION")
    print("="*70)
    
    # Count documents
    legal_count = count_documents(orchestrator.config.legal_knowledge_dir)
    case_count = count_documents(orchestrator.config.case_context_dir)
    total_docs = legal_count + case_count
    
    print(f"\nThis phase builds the legal and case knowledge foundation:")
    print(f"  Legal knowledge: {legal_count} documents")
    print(f"  Case context: {case_count} documents")
    print(f"  Total: {total_docs} documents")
    
    # Estimate
    estimates = orchestrator.batch_manager.estimate_total_batches(
        phase_0_docs=total_docs,
        tier_1_docs=0,
        tier_2_docs=0
    )
    
    print(f"\nEstimated cost: £{estimates['phase_0']['cost_gbp']}")
    print(f"Estimated time: {int(estimates['phase_0']['batches'] * 6)} minutes")
    print(f"Batches: {estimates['phase_0']['batches']}")
    
    print(f"\nFeatures:")
    print(f"  ✅ Prompt caching (90% cost savings on repeat context)")
    print(f"  ✅ Safe batching (prevents 413 errors)")
    print(f"  ✅ Checkpoint/resume (continue after interruption)")
    print(f"  ✅ Knowledge graph building")
    
    response = input(f"\nProceed with Phase 0? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
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
    
    # Count disclosure documents (respects prioritisation)
    disclosure_count = count_documents(orchestrator.config.disclosure_dir)
    
    # Check if using priority documents
    priority_file = orchestrator.config.output_dir / "priority_documents.json"
    using_priority = priority_file.exists()
    
    if using_priority:
        with open(priority_file, 'r', encoding='utf-8') as f:
            priority_data = json.load(f)
        actual_count = len(priority_data['documents'])
        print(f"\n✅ Using prioritised documents:")
        print(f"  Priority documents: {actual_count}")
        print(f"  (Selected from {disclosure_count} total)")
    else:
        actual_count = disclosure_count
        print(f"\n⚠️  Processing ALL disclosure documents: {actual_count}")
        print(f"  Consider running 'python main.py prioritise' first")
    
    print(f"\nThis phase uses 3-tier intelligent analysis:")
    
    print(f"\n  TIER 1: Deep Analysis (~500 priority documents)")
    print(f"    - Uses full senior litigator prompts")
    print(f"    - Spawns investigations on critical findings")
    print(f"    - Priority folders: Document Production, Witness Statements, etc.")
    
    print(f"\n  TIER 2: Metadata Scan (remaining documents)")
    print(f"    - Fast lightweight scanning")
    print(f"    - Flags suspicious documents for Tier 3")
    print(f"    - Uses Haiku 4 for speed/cost efficiency")
    
    print(f"\n  TIER 3: Targeted Deep Dive (flagged documents)")
    print(f"    - Deep analysis of documents flagged in Tier 2")
    print(f"    - Full forensic investigation")
    
    # Estimate
    estimates = orchestrator.batch_manager.estimate_total_batches(
        phase_0_docs=0,
        tier_1_docs=min(500, actual_count),
        tier_2_docs=max(0, actual_count - 500)
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
    
    try:
        print("\n" + "="*70)
        print("Starting Phase 1...")
        print("="*70)
        results = orchestrator.execute_single_phase('1')
        
        print("\n" + "="*70)
        print("PHASE 1 COMPLETE")
        print("="*70)
        
        if hasattr(orchestrator.api_client, 'print_usage_summary'):
            orchestrator.api_client.print_usage_summary()
        
        print(f"\nOutputs saved to:")
        print(f"  Analysis: {orchestrator.config.analysis_dir}")
        print(f"  Reports: {orchestrator.config.reports_dir}")
        
    except Exception as e:
        print(f"\n❌ Error in Phase 1: {e}")
        import traceback
        traceback.print_exc()
        raise


def run_full_analysis(orchestrator):
    """
    Run complete analysis: Phase 0 + Phase 1
    """
    
    print("\n" + "="*70)
    print("FULL ANALYSIS: PHASE 0 + PHASE 1")
    print("="*70)
    
    # Check prioritisation
    priority_file = orchestrator.config.output_dir / "priority_documents.json"
    if not priority_file.exists():
        print("\n⚠️  WARNING: Prioritisation not run!")
        print("  This will process ALL documents and may exceed budget.")
        print("  Recommended: Run 'python main.py prioritise' first")
        
        response = input("\nContinue anyway? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled. Run: python main.py prioritise")
            return
    
    # Show estimates
    show_cost_estimate(orchestrator)
    
    print("\n" + "="*70)
    print("This will run:")
    print("  1. Phase 0: Knowledge Foundation")
    print("  2. Phase 1: 3-Tier Disclosure Analysis")
    print("="*70)
    
    response = input("\nProceed with full analysis? (yes/no): ").strip().lower()
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