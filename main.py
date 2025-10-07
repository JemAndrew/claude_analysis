#!/usr/bin/env python3
"""
Lismore Litigation Intelligence System - Main Entry Point
4-Pass Iterative Deepening with Autonomous Investigation
British English throughout
"""

import sys
import argparse
from pathlib import Path
from typing import Dict

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from core.orchestrator import LitigationOrchestrator
from core.config import Config


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Lismore 4-Pass Litigation Intelligence System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  analyse       Run complete 4-pass analysis
  pass1         Run Pass 1: Triage only
  pass2         Run Pass 2: Deep analysis only
  pass3         Run Pass 3: Investigations only
  pass4         Run Pass 4: Synthesis & deliverables only
  phase0        Run Phase 0: Knowledge foundation (legacy)
  estimate      Show cost estimates
  status        Show current system status

Examples:
  python main.py analyse              # Run complete 4-pass analysis
  python main.py pass1                # Just triage documents
  python main.py estimate             # Check costs before running
  python main.py status               # Check what's been completed
        """
    )
    
    parser.add_argument(
        'command',
        choices=['analyse', 'pass1', 'pass2', 'pass3', 'pass4', 'phase0', 'estimate', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of documents (for testing)'
    )
    
    args = parser.parse_args()
    
    # Initialise orchestrator
    try:
        orchestrator = LitigationOrchestrator()
    except Exception as e:
        print(f"Failed to initialise orchestrator: {e}")
        sys.exit(1)
    
    # Route to appropriate command
    try:
        if args.command == 'analyse':
            run_complete_analysis(orchestrator)
        elif args.command == 'pass1':
            run_single_pass(orchestrator, '1', limit=args.limit)
        elif args.command == 'pass2':
            run_single_pass(orchestrator, '2')
        elif args.command == 'pass3':
            run_single_pass(orchestrator, '3')
        elif args.command == 'pass4':
            run_single_pass(orchestrator, '4')
        elif args.command == 'phase0':
            run_phase_0(orchestrator)
        elif args.command == 'estimate':
            show_cost_estimate(orchestrator)
        elif args.command == 'status':
            show_status(orchestrator)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress saved.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_complete_analysis(orchestrator):
    """Run complete 4-pass analysis"""
    
    print("\n" + "="*70)
    print("4-PASS LITIGATION INTELLIGENCE ANALYSIS")
    print("Lismore Capital v Process Holdings")
    print("="*70)
    
    # Show estimates
    print("\nCost Estimates:")
    estimates = orchestrator.estimate_costs()
    
    print(f"\n  Pass 1 (Triage):")
    print(f"    Documents: {estimates['pass_1_triage']['documents']}")
    print(f"    Estimated cost: £{estimates['pass_1_triage']['estimated_cost_gbp']:.2f}")
    print(f"    Estimated time: {estimates['pass_1_triage']['estimated_time_hours']:.1f} hours")
    
    print(f"\n  Pass 2 (Deep Analysis):")
    print(f"    Documents: {estimates['pass_2_deep_analysis']['documents']}")
    print(f"    Estimated cost: £{estimates['pass_2_deep_analysis']['estimated_cost_gbp']:.2f}")
    print(f"    Estimated time: {estimates['pass_2_deep_analysis']['estimated_time_hours']:.1f} hours")
    
    print(f"\n  Pass 3 (Investigations):")
    print(f"    Estimated investigations: {estimates['pass_3_investigations']['estimated_investigations']}")
    print(f"    Estimated cost: £{estimates['pass_3_investigations']['estimated_cost_gbp']:.2f}")
    print(f"    Estimated time: {estimates['pass_3_investigations']['estimated_time_hours']:.1f} hours")
    
    print(f"\n  Pass 4 (Synthesis):")
    print(f"    Estimated cost: £{estimates['pass_4_synthesis']['estimated_cost_gbp']:.2f}")
    print(f"    Estimated time: {estimates['pass_4_synthesis']['estimated_time_hours']:.1f} hours")
    
    print(f"\n  TOTAL:")
    print(f"    Estimated cost: £{estimates['total_estimated_cost_gbp']:.2f}")
    print(f"    Estimated time: {estimates['total_estimated_time_hours']:.1f} hours")
    
    # Confirm
    response = input("\nProceed with complete 4-pass analysis? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Run analysis
    print("\nStarting 4-pass analysis...")
    results = orchestrator.execute_complete_analysis()
    
    # Print summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    
    print(f"\nPass 1 (Triage):")
    print(f"  Priority documents identified: {results['passes']['pass_1']['priority_count']}")
    
    print(f"\nPass 2 (Deep Analysis):")
    print(f"  Iterations: {results['passes']['pass_2']['total_iterations']}")
    print(f"  Final confidence: {results['passes']['pass_2']['final_confidence']:.2%}")
    print(f"  Stopped because: {results['passes']['pass_2']['reason_stopped']}")
    
    print(f"\nPass 3 (Investigations):")
    print(f"  Investigations run: {results['passes']['pass_3']['total_investigations']}")
    
    print(f"\nPass 4 (Synthesis):")
    print(f"  Claims constructed: {len(results['passes']['pass_4']['deliverables'].get('claims', {}))}")
    print(f"  Tribunal documents: {len(results['passes']['pass_4']['deliverables'].get('tribunal_documents', {}))}")
    
    # Print API usage
    if hasattr(orchestrator.api_client, 'print_usage_summary'):
        print("\n" + "="*70)
        print("API USAGE SUMMARY")
        print("="*70)
        orchestrator.api_client.print_usage_summary()
    
    print(f"\nResults saved to: {orchestrator.config.analysis_dir}")
    print("\nNext steps:")
    print("  1. Review Pass 4 deliverables in: data/output/analysis/pass_4/")
    print("  2. Check tribunal documents and claims")
    print("  3. Review strategic recommendations")

def run_single_pass(orchestrator, pass_num: str, limit: int = None):
    """Run single pass for testing"""
    
    print("\n" + "="*70)
    print(f"EXECUTING PASS {pass_num}")
    print("="*70)
    
    # Check prerequisites
    if pass_num == '2':
        # Pass 2 needs Pass 1 results
        pass_1_file = orchestrator.config.analysis_dir / "pass_1" / "pass_1_results.json"
        if not pass_1_file.exists():
            print("\nError: Pass 1 must be completed first")
            print("Run: python main.py pass1")
            return
    
    if pass_num in ['3', '4']:
        # Pass 3 and 4 need Pass 2 results
        pass_2_file = orchestrator.config.analysis_dir / "pass_2" / "pass_2_results.json"
        if not pass_2_file.exists():
            print(f"\nError: Pass 2 must be completed before Pass {pass_num}")
            print("Run: python main.py pass2")
            return
    
    # Run the pass WITH LIMIT
    try:
        result = orchestrator.execute_single_pass(pass_num, limit=limit)
        
        print("\n" + "="*70)
        print(f"PASS {pass_num} COMPLETE")
        print("="*70)
        
        # Print pass-specific summary
        if pass_num == '1':
            print(f"\nPriority documents identified: {result['priority_count']}")
            print(f"Output saved to: {orchestrator.config.analysis_dir / 'pass_1'}")
            print("\nNext step: python main.py pass2")
        
        elif pass_num == '2':
            print(f"\nIterations completed: {result['total_iterations']}")
            print(f"Final confidence: {result['final_confidence']:.2%}")
            print(f"Investigations queued: {len(result.get('iterations', [])[-1].get('investigations_spawned', 0)) if result.get('iterations') else 0}")
            print(f"Output saved to: {orchestrator.config.analysis_dir / 'pass_2'}")
            print("\nNext step: python main.py pass3")
        
        elif pass_num == '3':
            print(f"\nInvestigations run: {result['total_investigations']}")
            print(f"Final queue status: {result['final_queue_status']}")
            print(f"Output saved to: {orchestrator.config.analysis_dir / 'pass_3'}")
            print("\nNext step: python main.py pass4")
        
        elif pass_num == '4':
            print(f"\nClaims constructed: {len(result['deliverables'].get('claims', {}))}")
            print(f"Tribunal documents generated: {len(result['deliverables'].get('tribunal_documents', {}))}")
            print(f"Output saved to: {orchestrator.config.analysis_dir / 'pass_4'}")
            print("\nAnalysis complete! Review deliverables in pass_4 folder.")
        
    except Exception as e:
        print(f"\n❌ Error executing Pass {pass_num}: {e}")
        import traceback
        traceback.print_exc()


def run_phase_0(orchestrator):
    """Run Phase 0: Intelligent Case Foundation"""
    
    print("\n" + "="*70)
    print("PHASE 0: INTELLIGENT CASE FOUNDATION")
    print("="*70)
    
    print("\nThis phase analyses pleadings, tribunal rulings, and case admin")
    print("to build comprehensive case understanding for intelligent document triage.")
    
    print("\nPhase 0 Stages:")
    print("  1. Analyse pleadings (core dispute understanding)")
    print("  2. Analyse tribunal rulings (legal framework & tribunal priorities)")
    print("  3. Map evidence landscape (entities, timelines, document patterns)")
    
    # Check if already completed
    phase_0_file = orchestrator.config.analysis_dir / "phase_0" / "case_foundation.json"
    
    if phase_0_file.exists():
        print(f"\n⚠️  Phase 0 already completed!")
        print(f"   Found: {phase_0_file}")
        
        response = input("\nRe-run Phase 0? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Using existing Phase 0 results.")
            return
    
    # Rough cost estimate
    estimated_cost = 5.0  # ~£5 for 3 API calls with extended thinking
    estimated_time = 0.25  # ~15 minutes
    
    print(f"\nEstimated cost: £{estimated_cost:.2f}")
    print(f"Estimated time: {estimated_time:.1f} hours (~15 minutes)")
    
    response = input("\nProceed with Phase 0? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Run Phase 0 via the Phase0Executor
    try:
        print("\nStarting Phase 0 analysis...")
        
        # Access the Phase0Executor through the orchestrator
        result = orchestrator.phase0_executor.execute()
        
        print("\n" + "="*70)
        print("PHASE 0 COMPLETE")
        print("="*70)
        
        # Print summary
        metadata = result.get('metadata', {})
        print(f"\nCost: £{metadata.get('total_cost_gbp', 0):.2f}")
        print(f"Time: {metadata.get('execution_time_seconds', 0):.0f} seconds")
        
        # ================================================================
        # FIXED: Read from correct nested structure
        # ================================================================
        print(f"\n📊 Case Foundation Built:")
        
        # Get the pass_1_reference (flat structure)
        pass_1_ref = result.get('pass_1_reference', {})
        
        if pass_1_ref:
            print(f"\n  PASS 1 REFERENCE (Flat structure for triage):")
            print(f"     • Lismore allegations: {len(pass_1_ref.get('allegations', []))}")
            print(f"     • PH defences: {len(pass_1_ref.get('defences', []))}")
            print(f"     • Key parties: {len(pass_1_ref.get('key_parties', []))}")
            print(f"     • Factual disputes: {len(pass_1_ref.get('factual_disputes', []))}")
            print(f"     • Legal tests: {len(pass_1_ref.get('legal_tests', []))}")
            print(f"     • Tribunal priorities: {len(pass_1_ref.get('tribunal_priorities', []))}")
            print(f"     • Document patterns: {len(pass_1_ref.get('document_patterns', []))}")
            print(f"     • Key entities: {len(pass_1_ref.get('key_entities', []))}")
            print(f"     • Critical dates: {len(pass_1_ref.get('critical_timeline', []))}")
        
        # Also show stage-by-stage breakdown
        stage_1 = result.get('stage_1_case_understanding', {})
        stage_2 = result.get('stage_2_legal_framework', {})
        stage_3 = result.get('stage_3_evidence_landscape', {})
        
        print(f"\n  DETAILED BREAKDOWN:")
        print(f"     Stage 1: {len(stage_1.get('allegations', []))} allegations, {len(stage_1.get('timeline', []))} timeline events")
        print(f"     Stage 2: {len(stage_2.get('case_strengths', []))} strengths, {len(stage_2.get('case_weaknesses', []))} weaknesses")
        print(f"     Stage 3: {len(stage_3.get('evidence_categories', []))} evidence categories, {len(stage_3.get('evidence_gaps', []))} gaps identified")
        
        print(f"\n💾 Output saved to: {orchestrator.config.analysis_dir / 'phase_0'}")
        print(f"   Main file: case_foundation.json")
        print(f"   Stage files: stage_1_case_understanding.json")
        print(f"                stage_2_legal_framework.json")
        print(f"                stage_3_evidence_landscape.json")
        
        print("\n🎯 Next Step:")
        print("   Case foundation with Pass 1 reference guide ready!")
        print("   Run: python main.py pass1")
        print("   Pass 1 will use these patterns for intelligent triage.")
        
    except Exception as e:
        print(f"\n❌ Error in Phase 0: {e}")
        import traceback
        traceback.print_exc()
        raise

def show_cost_estimate(orchestrator):
    """Show detailed cost estimates"""
    
    print("\n" + "="*70)
    print("COST ESTIMATES - 4-PASS SYSTEM")
    print("="*70)
    
    estimates = orchestrator.estimate_costs()
    
    print(f"\nPass 1: Triage & Prioritisation")
    print(f"  Documents to scan: {estimates['pass_1_triage']['documents']}")
    print(f"  Model: Haiku 4 (cheap)")
    print(f"  Cost: £{estimates['pass_1_triage']['estimated_cost_gbp']:.2f}")
    print(f"  Time: {estimates['pass_1_triage']['estimated_time_hours']:.1f} hours")
    
    print(f"\nPass 2: Deep Analysis")
    print(f"  Priority documents: {estimates['pass_2_deep_analysis']['documents']}")
    print(f"  Model: Sonnet 4.5 (with extended thinking)")
    print(f"  Cost: £{estimates['pass_2_deep_analysis']['estimated_cost_gbp']:.2f}")
    print(f"  Time: {estimates['pass_2_deep_analysis']['estimated_time_hours']:.1f} hours")
    
    print(f"\nPass 3: Autonomous Investigations")
    print(f"  Estimated investigations: {estimates['pass_3_investigations']['estimated_investigations']}")
    print(f"  Model: Sonnet 4.5 (recursive)")
    print(f"  Cost: £{estimates['pass_3_investigations']['estimated_cost_gbp']:.2f}")
    print(f"  Time: {estimates['pass_3_investigations']['estimated_time_hours']:.1f} hours")
    
    print(f"\nPass 4: Synthesis & Deliverables")
    print(f"  Model: Sonnet 4.5")
    print(f"  Cost: £{estimates['pass_4_synthesis']['estimated_cost_gbp']:.2f}")
    print(f"  Time: {estimates['pass_4_synthesis']['estimated_time_hours']:.1f} hours")
    
    print(f"\n{'='*70}")
    print(f"TOTAL ESTIMATED COST: £{estimates['total_estimated_cost_gbp']:.2f}")
    print(f"TOTAL ESTIMATED TIME: {estimates['total_estimated_time_hours']:.1f} hours ({estimates['total_estimated_time_hours']/24:.1f} days)")
    print(f"{'='*70}")
    
    print("\nNote: Actual costs may vary based on:")
    print("  - Document complexity")
    print("  - Number of investigations spawned")
    print("  - Confidence reaching 95% earlier/later")
    print("  - Extended thinking token usage")


def show_status(orchestrator):
    """Show current system status"""
    
    print("\n" + "="*70)
    print("SYSTEM STATUS")
    print("="*70)
    
    status = orchestrator.get_status()
    
    print(f"\nPasses completed: {', '.join(status['passes_completed']) if status['passes_completed'] else 'None'}")
    print(f"Current pass: {status['current_pass'] or 'None'}")
    
    # Check what files exist
    analysis_dir = orchestrator.config.analysis_dir
    
    print("\nCompleted passes:")
    for pass_num in ['1', '2', '3', '4']:
        pass_file = analysis_dir / f"pass_{pass_num}" / f"pass_{pass_num}_results.json"
        if pass_file.exists():
            print(f"  Pass {pass_num}: Complete")
        else:
            print(f"  Pass {pass_num}: Not started")
    
    # Check Phase 0 (legacy)
    phase_0_file = analysis_dir / "phase_0" / "phase_0_results.json"
    if phase_0_file.exists():
        print(f"  Phase 0 (foundation): Complete")
    
    # Knowledge graph stats
    kg_stats = status['knowledge_graph_stats']
    print(f"\nKnowledge Graph:")
    print(f"  Entities: {kg_stats.get('entities', 0)}")
    print(f"  Relationships: {kg_stats.get('relationships', 0)}")
    print(f"  Contradictions: {kg_stats.get('contradictions', 0)}")
    print(f"  Patterns: {kg_stats.get('patterns', 0)}")
    print(f"  Timeline events: {kg_stats.get('timeline_events', 0)}")
    
    # Total cost
    print(f"\nTotal cost so far: £{status['total_cost_gbp']:.2f}")
    
    print("\nNext steps:")
    if not status['passes_completed']:
        print("  Run: python main.py estimate    # Check costs")
        print("  Run: python main.py analyse     # Start analysis")
    elif '1' not in status['passes_completed']:
        print("  Run: python main.py pass1       # Start triage")
    elif '2' not in status['passes_completed']:
        print("  Run: python main.py pass2       # Deep analysis")
    elif '3' not in status['passes_completed']:
        print("  Run: python main.py pass3       # Run investigations")
    elif '4' not in status['passes_completed']:
        print("  Run: python main.py pass4       # Generate deliverables")
    else:
        print("  All passes complete!")
        print(f"  Check deliverables in: {analysis_dir / 'pass_4'}")


if __name__ == "__main__":
    main()