#!/usr/bin/env python3
"""
Main script for Lismore litigation analysis
Handles three-directory structure:
- legal_resources/ for Phase 0A (legal frameworks)
- case_context/ for Phase 0B (case background)  
- documents/ for Phases 1-7 (MAIN DISCLOSURE DOCUMENTS)
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple

# When running as module (python -m src.main)
if __name__ == "__main__" and __package__:
    from .interface.document_processor import DocumentProcessor
    from .knowledge.knowledge_manage import KnowledgeManager
    from .outputs.output_generator import OutputGenerator
else:
    # When running directly (python src/main.py)
    sys.path.insert(0, str(Path(__file__).parent))
    from interface.document_processor import DocumentProcessor
    from knowledge.knowledge_manage import KnowledgeManager
    from outputs.output_generator import OutputGenerator


def verify_directories() -> Tuple[Dict, bool]:
    """Verify all three document directories"""
    print("\n📁 DIRECTORY VERIFICATION")
    print("="*50)
    
    status = {}
    ready_for_analysis = True
    
    # Check legal_resources (Phase 0A)
    legal_dir = Path("legal_resources")
    if legal_dir.exists():
        # Check for rule cards
        rule_cards_dir = legal_dir / "rule_cards"
        if rule_cards_dir.exists():
            json_count = len(list(rule_cards_dir.glob("*.json")))
            status['legal_resources'] = json_count
            print(f"✅ legal_resources/rule_cards/: {json_count} rule cards")
        else:
            # Check for PDFs or text files
            pdf_count = len(list(legal_dir.glob("**/*.pdf")))
            txt_count = len(list((legal_dir / "processed/text").glob("*.txt"))) if (legal_dir / "processed/text").exists() else 0
            total = pdf_count + txt_count
            status['legal_resources'] = total
            print(f"✅ legal_resources/: {total} documents")
        
        if status['legal_resources'] == 0:
            print("   ⚠️  No legal framework documents for Phase 0A")
            ready_for_analysis = False
    else:
        status['legal_resources'] = 0
        print("❌ legal_resources/ not found (needed for Phase 0A)")
        ready_for_analysis = False
    
    # Check case_context (Phase 0B)
    case_dir = Path("case_context")
    if case_dir.exists():
        pdf_count = len(list(case_dir.glob("**/*.pdf")))
        status['case_context'] = pdf_count
        print(f"✅ case_context/: {pdf_count} PDFs")
        if pdf_count == 0:
            print("   ⚠️  No case background documents for Phase 0B")
    else:
        status['case_context'] = 0
        print("❌ case_context/ not found (needed for Phase 0B)")
        # Not critical if missing
    
    # Check disclosure documents (Phases 1-7)
    disclosure_ready = False
    
    # Check processed text first
    processed_dir = Path("documents/processed/text")
    if processed_dir.exists():
        txt_count = len(list(processed_dir.glob("*.txt")))
        if txt_count > 0:
            status['disclosure_processed'] = txt_count
            print(f"✅ documents/processed/text/: {txt_count} text files")
            disclosure_ready = True
    
    # Check raw if processed not available
    if not disclosure_ready:
        raw_dir = Path("documents/raw")
        if raw_dir.exists():
            pdf_count = len(list(raw_dir.glob("*.pdf")))
            if pdf_count > 0:
                status['disclosure_raw'] = pdf_count
                print(f"✅ documents/raw/: {pdf_count} PDFs")
                disclosure_ready = True
    
    if not disclosure_ready:
        status['disclosure_raw'] = 0
        status['disclosure_processed'] = 0
        print("ℹ️  No disclosure documents (needed for Phases 1-7)")
        print("   Expected locations:")
        print("   - documents/processed/text/ (processed text files)")
        print("   - documents/raw/ (raw PDFs)")
    
    print("="*50)
    
    return status, ready_for_analysis


def estimate_cost(phases: List[str], dir_status: Dict) -> float:
    """
    Estimate costs for the phases to run
    
    Args:
        phases: List of phases to run
        dir_status: Directory status from verification
        
    Returns:
        Estimated cost in GBP
    """
    BATCH_SIZES = {
        "0A": 10, "0B": 10, "1": 20, "2": 20, 
        "3": 20, "4": 25, "5": 25, "6": 30, "7": 30
    }
    
    total_cost = 0
    print("\n💰 COST BREAKDOWN BY PHASE:")
    print("="*50)
    
    for phase in phases:
        # Determine document count based on phase
        if phase == "0A":
            doc_count = dir_status.get('legal_resources', 0)
            source = "legal_resources"
        elif phase == "0B":
            doc_count = dir_status.get('case_context', 0)
            source = "case_context"
        else:  # Phases 1-7
            # Use processed if available, otherwise raw
            if dir_status.get('disclosure_processed', 0) > 0:
                doc_count = dir_status.get('disclosure_processed', 0)
                source = "documents/processed/text"
            else:
                doc_count = dir_status.get('disclosure_raw', 0)
                source = "documents/raw"
        
        if doc_count == 0:
            print(f"  Phase {phase}: No documents in {source}/ - SKIPPED")
            continue
        
        batch_size = BATCH_SIZES.get(phase, 20)
        num_batches = max(1, (doc_count + batch_size - 1) // batch_size)
        
        # Phases 0A, 0B, 1 use Haiku (cheaper)
        if phase in ["0A", "0B", "1"]:
            cost_per_batch = 0.15
            model = "Haiku"
        else:
            cost_per_batch = 2.50
            model = "Opus 4.1"
        
        # Add synthesis cost
        synthesis_cost = 0.20 if phase in ["0A", "0B", "1"] else 0.50
        phase_cost = (num_batches * cost_per_batch) + synthesis_cost
        total_cost += phase_cost
        
        print(f"  Phase {phase} ({source}, {model}):")
        print(f"    {doc_count} docs → {num_batches} batches")
        print(f"    Batches: {num_batches} × £{cost_per_batch:.2f} = £{num_batches * cost_per_batch:.2f}")
        print(f"    Synthesis: £{synthesis_cost:.2f}")
        print(f"    Phase total: £{phase_cost:.2f}")
    
    return total_cost


def main():
    parser = argparse.ArgumentParser(
        description='Lismore Capital Litigation Analysis System'
    )
    parser.add_argument('--phase', type=str, help='Single phase to run (e.g., 0A)')
    parser.add_argument('--phases', nargs='+', help='Multiple phases to run (e.g., 0A 0B 1)')
    parser.add_argument('--resume', action='store_true', help='Resume from last completed phase')
    parser.add_argument('--estimate-only', action='store_true', help='Only show cost estimate')
    parser.add_argument('--verify', action='store_true', help='Verify directory setup')
    parser.add_argument('--dashboard', action='store_true', help='Generate war room dashboard')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("LISMORE CAPITAL vs PROCESS HOLDINGS")
    print("DOCUMENT ANALYSIS SYSTEM")
    print(f"{'='*60}")
    
    # Verify directories
    dir_status, ready = verify_directories()
    
    if args.verify:
        if ready:
            print("\n✅ System ready for analysis!")
        else:
            print("\n⚠️  Fix directory issues before running analysis")
        return 0
    
    # Handle dashboard request
    if args.dashboard:
        print("\n📊 Generating War Room Dashboard...")
        processor = DocumentProcessor()
        dashboard = processor.generate_war_room_dashboard()
        print(dashboard)
        return 0
    
    # Check Phase 0A readiness
    if not ready and "0A" in (args.phases or [args.phase] or ["0A"]):
        print("\n❌ Cannot proceed - Phase 0A requires legal_resources/")
        return 1
    
    # Initialise processor
    print("\n🔧 Initialising document processor...")
    processor = DocumentProcessor()
    
    # Determine phases to run
    if args.phase:
        phases_to_run = [args.phase]
    elif args.phases:
        phases_to_run = args.phases
    elif args.resume:
        knowledge_manager = KnowledgeManager()
        completed = knowledge_manager.get_completed_phases()
        all_phases = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        phases_to_run = [p for p in all_phases if p not in completed]
        
        if not phases_to_run:
            print("\n✅ All phases already completed!")
            return 0
        
        print(f"\n📌 Resuming from phase {phases_to_run[0]}")
    else:
        # Default to Phase 0A if legal resources exist
        if dir_status.get('legal_resources', 0) > 0:
            phases_to_run = ["0A"]
        else:
            print("\n❓ No phase specified. Use --phase 0A to start")
            return 0
    
    print(f"\n📋 Phases to run: {', '.join(phases_to_run)}")
    
    # Check for disclosure documents if running phases 1-7
    if any(phase not in ["0A", "0B"] for phase in phases_to_run):
        has_disclosure = (dir_status.get('disclosure_processed', 0) > 0 or 
                         dir_status.get('disclosure_raw', 0) > 0)
        if not has_disclosure:
            print("\n⚠️  WARNING: No disclosure documents for phases 1-7!")
            print("   These are the main documents for analysis")
            response = input("   Continue anyway? [y/N]: ")
            if response.lower() != 'y':
                return 1
    
    # Estimate costs
    estimated_cost = estimate_cost(phases_to_run, dir_status)
    print(f"\n{'='*50}")
    print(f"💰 TOTAL ESTIMATED COST: £{estimated_cost:.2f}")
    print(f"{'='*50}")
    
    if args.estimate_only:
        return 0
    
    # Confirm before proceeding
    response = input(f"\n⚠️  Proceed with analysis? (estimated £{estimated_cost:.2f}) [y/N]: ")
    if response.lower() != 'y':
        print("Analysis cancelled.")
        return 0
    
    print(f"\n🚀 Starting multi-phase analysis...")
    
    try:
        results = {}
        
        for phase in phases_to_run:
            print(f"\n{'='*60}")
            print(f"📍 Starting Phase {phase}")
            print(f"{'='*60}")
            
            # Process phase
            result = processor.process_phase(phase)
            
            if not result:
                print(f"⚠️  Phase {phase} failed - stopping")
                break
            
            results[phase] = result
            
            # Show progress
            completed = phases_to_run.index(phase) + 1
            remaining = len(phases_to_run) - completed
            print(f"\n📊 Progress: {completed}/{len(phases_to_run)} phases complete")
            
            if remaining > 0:
                print(f"   Remaining: {', '.join(phases_to_run[completed:])}")
            
            # Cost tracking
            if hasattr(processor.api_client, 'cost_tracker'):
                cost_tracker = processor.api_client.cost_tracker
                print(f"💰 Total spent so far: £{cost_tracker.total_cost:.2f}")
            
            # Pause between phases
            if remaining > 0:
                print("⏱️  Pausing 5 seconds before next phase...")
                time.sleep(5)
        
        # Generate reports (only for phases 1-7)
        if any(phase not in ["0A", "0B"] for phase in phases_to_run):
            print(f"\n📄 Generating litigation reports...")
            
            # Import only when needed
            from outputs.output_generator import OutputGenerator
            output_gen = OutputGenerator(processor.knowledge_manage)
            
            # Register documents for referencing
            if hasattr(processor, 'document_registry') and processor.document_registry:
                output_gen.register_documents(list(processor.document_registry.values()))
            
            # Generate phase-specific reports
            all_reports = {}
            for phase in phases_to_run:
                if phase not in ["0A", "0B"]:  # No reports for knowledge phases
                    phase_data = results.get(phase, {})
                    reports = output_gen.generate_phase_reports(phase, phase_data)
                    all_reports[phase] = reports
            
            total_reports = sum(len(r) for r in all_reports.values())
            print(f"✅ Generated {total_reports} litigation reports")
        
        print(f"\n{'='*60}")
        print("🎯 ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        
        # Final summary
        print(f"\n📊 FINAL SUMMARY:")
        print(f"  Phases completed: {', '.join(results.keys())}")
        
        if hasattr(processor.api_client, 'cost_tracker'):
            print(f"  Total cost: £{processor.api_client.cost_tracker.total_cost:.2f}")
        
        print(f"  Documents analysed:")
        for phase, result in results.items():
            doc_count = result.get('documents_analysed', 0)
            print(f"    Phase {phase}: {doc_count} documents")
        
        print(f"\n📁 Outputs saved to: ./outputs/")
        print(f"📚 Knowledge stored in: ./knowledge_store/")
        
        # Generate war room dashboard if multiple phases completed
        if len(results) > 1:
            print(f"\n📊 Generating War Room Dashboard...")
            dashboard = processor.generate_war_room_dashboard()
            print(dashboard[:500] + "...")  # Show preview
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        print("Progress has been saved. Use --resume to continue.")
        return 1
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())