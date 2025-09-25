# main.py - THREE DIRECTORY STRUCTURE
"""
Main script for Lismore litigation analysis
Handles three-directory structure:
- legal_resources/ for Phase 0A (legal frameworks)
- case_context/ for Phase 0B (case background)  
- documents/ for Phases 1-7 (MAIN DISCLOSURE DOCUMENTS)
"""

import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from interface.document_processor import DocumentProcessor
from knowledge.knowledge_manage import OptimisedKnowledgeManager
from outputs.output_generator import OptimisedOutputGenerator

def verify_directories():
    """Verify all three document directories"""
    print("\n📁 DIRECTORY VERIFICATION")
    print("="*50)
    
    status = {}
    ready_for_analysis = True
    
    # Check legal_resources (Phase 0A)
    legal_dir = Path("legal_resources")
    if legal_dir.exists():
        pdf_count = len(list(legal_dir.glob("*.pdf")))
        status['legal_resources'] = pdf_count
        print(f"✅ legal_resources/: {pdf_count} PDFs")
        if pdf_count == 0:
            print("   ⚠️  No legal framework documents for Phase 0A")
    else:
        status['legal_resources'] = 0
        print("❌ legal_resources/ not found (needed for Phase 0A)")
        ready_for_analysis = False
    
    # Check case_context (Phase 0B)
    case_dir = Path("case_context")
    if case_dir.exists():
        pdf_count = len(list(case_dir.glob("*.pdf")))
        status['case_context'] = pdf_count
        print(f"✅ case_context/: {pdf_count} PDFs")
        if pdf_count == 0:
            print("   ⚠️  No case background documents for Phase 0B")
    else:
        status['case_context'] = 0
        print("❌ case_context/ not found (needed for Phase 0B)")
        ready_for_analysis = False
    
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
            if pdf_count >= 0:
                status['disclosure_raw'] = pdf_count
                print(f"✅ documents/raw/: {pdf_count} PDFs")
                disclosure_ready = True
    
    if not disclosure_ready:
        print("❌ No disclosure documents found (needed for Phases 1-7)")
        print("   Expected locations:")
        print("   - documents/processed/text/ (processed text files)")
        print("   - documents/raw/ (raw PDFs)")
        ready_for_analysis = False
    
    print("="*50)
    
    return status, ready_for_analysis

def estimate_cost(phases: list) -> float:
    """
    Estimate costs for the phases to run
    
    Args:
        phases: List of phases to run
        
    Returns:
        Estimated cost in GBP
    """
    processor = DocumentProcessor()
    dir_status = processor.verify_setup()
    
    BATCH_SIZES = {
        "0A": 3, "0B": 3, "1": 5, "2": 5, 
        "3": 5, "4": 7, "5": 7, "6": 10, "7": 10
    }
    
    total_cost = 0
    print("\n💰 COST BREAKDOWN BY PHASE:")
    print("="*50)
    
    for phase in phases:
        # Determine document count based on phase
        if phase == "0A":
            doc_count = dir_status['legal_resources']['count']
            source = "legal_resources"
        elif phase == "0B":
            doc_count = dir_status['case_context']['count']
            source = "case_context"
        else:  # Phases 1-7
            # Use processed if available, otherwise raw
            if dir_status['disclosure_processed']['count'] > 0:
                doc_count = dir_status['disclosure_processed']['count']
                source = "documents/processed/text"
            else:
                doc_count = dir_status['disclosure_raw']['count']
                source = "documents/raw"
        
        if doc_count == 0:
            print(f"  Phase {phase}: No documents in {source}/ - SKIPPED")
            continue
        
        batch_size = BATCH_SIZES.get(phase, 5)
        num_batches = (doc_count + batch_size - 1) // batch_size
        
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
    parser.add_argument('--phases', nargs='+', help='Specific phases to run (e.g., 0A 0B 1)')
    parser.add_argument('--resume', action='store_true', help='Resume from last completed phase')
    parser.add_argument('--estimate-only', action='store_true', help='Only show cost estimate')
    parser.add_argument('--verify', action='store_true', help='Verify directory setup')
    
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
    
    if not ready:
        print("\n❌ Cannot proceed - fix directory issues first")
        return 1
    
    # Initialise processor
    processor = DocumentProcessor()
    
    # Determine phases to run
    if args.phases:
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
        phases_to_run = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
    
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
    estimated_cost = estimate_cost(phases_to_run)
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
            # Process phase (documents loaded automatically per phase)
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
            cost_tracker = processor.api_client.cost_tracker
            print(f"💰 Total spent so far: £{cost_tracker.total_cost:.2f}")
            
            # Pause between phases
            if remaining > 0:
                print("⏱️  Pausing 5 seconds before next phase...")
                import time
                time.sleep(5)
        
        # Generate reports (only for phases 1-7)
        if any(phase not in ["0A", "0B"] for phase in phases_to_run):
            print(f"\n📄 Generating litigation reports...")
            
            output_gen = OutputGenerator(processor.knowledge_manage)
            
            # Register documents for referencing
            if processor.disclosure_cache:
                output_gen.register_documents(processor.disclosure_cache)
            
            # Generate phase-specific reports
            all_reports = {}
            for phase in phases_to_run:
                if phase not in ["0A", "0B"]:  # No reports for knowledge phases
                    phase_data = results.get(phase, {})
                    
                    if phase == "1":
                        reports = output_gen.generate_phase_1_reports(phase_data)
                    elif phase == "2":
                        reports = output_gen.generate_phase_2_reports(phase_data)
                    elif phase == "3":
                        reports = output_gen.generate_phase_3_reports(phase_data)
                    elif phase == "4":
                        reports = output_gen.generate_phase_4_reports(phase_data)
                    elif phase == "5":
                        reports = output_gen.generate_phase_5_reports(phase_data)
                    elif phase == "6":
                        reports = output_gen.generate_phase_6_reports(phase_data)
                    elif phase == "7":
                        reports = output_gen.generate_phase_7_reports(phase_data)
                    
                    all_reports[phase] = reports
            
            total_reports = sum(len(r) for r in all_reports.values())
            print(f"✅ Generated {total_reports} litigation reports")
        
        print(f"\n{'='*60}")
        print("🎯 ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        
        # Final summary
        print(f"\n📊 FINAL SUMMARY:")
        print(f"  Phases completed: {', '.join(results.keys())}")
        print(f"  Total cost: £{processor.api_client.cost_tracker.total_cost:.2f}")
        print(f"  Documents analysed:")
        
        for phase, result in results.items():
            doc_count = result.get('documents_analysed', 0)
            source = result.get('source_directory', 'unknown')
            print(f"    Phase {phase}: {doc_count} docs from {source}/")
        
        print(f"\n📁 Outputs saved to: ./outputs/")
        print(f"📚 Knowledge stored in: ./knowledge_store/")
        
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