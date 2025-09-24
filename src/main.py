# Add these improvements to your main.py

import argparse
import sys
from pathlib import Path
from src.document_processor import DocumentProcessor
from src.knowledge_manage import KnowledgeManager
from src.output_generator import OutputGenerator

def estimate_cost(document_count: int, phases: list) -> float:
    """
    Estimate API costs before processing
    
    Args:
        document_count: Number of documents
        phases: List of phases to run
        
    Returns:
        Estimated cost in GBP
    """
    BATCH_SIZES = {
        "0A": 3, "0B": 3, "1": 5, "2": 5, 
        "3": 5, "4": 7, "5": 7, "6": 10, "7": 10
    }
    
    total_cost = 0
    
    for phase in phases:
        batch_size = BATCH_SIZES.get(phase, 5)
        num_batches = (document_count + batch_size - 1) // batch_size
        
        # Phases 0A, 0B, 1 use Haiku (cheaper)
        if phase in ["0A", "0B", "1"]:
            cost_per_batch = 0.15  # £0.15 per batch
        else:
            cost_per_batch = 2.50  # £2.50 per batch for Opus
        
        phase_cost = num_batches * cost_per_batch
        total_cost += phase_cost
        
        print(f"  Phase {phase}: {num_batches} batches × £{cost_per_batch:.2f} = £{phase_cost:.2f}")
    
    return total_cost

def main():
    parser = argparse.ArgumentParser(description='Lismore Document Analysis System')
    parser.add_argument('documents', help='Path to documents directory or file')
    parser.add_argument('--phases', nargs='+', help='Specific phases to run (e.g., 0A 0B 1)')
    parser.add_argument('--resume', action='store_true', help='Resume from last completed phase')
    parser.add_argument('--estimate-only', action='store_true', help='Only show cost estimate')
    parser.add_argument('--test-batch', type=int, help='Test with N documents only')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Load documents
    print(f"\n{'='*60}")
    print("LISMORE CAPITAL DOCUMENT ANALYSIS SYSTEM")
    print(f"{'='*60}")
    
    print(f"\n📂 Loading documents from: {args.documents}")
    
    # Handle test batch
    if args.test_batch:
        print(f"⚠️  TEST MODE: Loading only {args.test_batch} documents")
    
    success = processor.load_documents([args.documents])
    
    if not success:
        print("❌ Failed to load documents")
        return 1
    
    # Apply test batch limit if specified
    if args.test_batch:
        processor.documents = processor.documents[:args.test_batch]
    
    document_count = len(processor.documents)
    print(f"✅ Loaded {document_count} documents")
    
    # Determine phases to run
    if args.phases:
        phases_to_run = args.phases
    elif args.resume:
        knowledge_manager = KnowledgeManager()
        completed = knowledge_manager.get_completed_phases()
        all_phases = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        phases_to_run = [p for p in all_phases if p not in completed]
        
        if not phases_to_run:
            print("✅ All phases already completed!")
            return 0
        
        print(f"📌 Resuming from phase {phases_to_run[0]}")
    else:
        phases_to_run = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
    
    print(f"\n📋 Phases to run: {', '.join(phases_to_run)}")
    
    # Estimate costs
    print(f"\n💰 COST ESTIMATE:")
    estimated_cost = estimate_cost(document_count, phases_to_run)
    print(f"{'='*40}")
    print(f"TOTAL ESTIMATED COST: £{estimated_cost:.2f}")
    print(f"{'='*40}")
    
    if args.estimate_only:
        return 0
    
    # Confirm before proceeding
    response = input(f"\n⚠️  Proceed with analysis? (estimated £{estimated_cost:.2f}) [y/N]: ")
    if response.lower() != 'y':
        print("Analysis cancelled.")
        return 0
    
    # Run analysis
    print(f"\n🚀 Starting analysis...")
    
    try:
        if len(phases_to_run) == 1:
            # Single phase
            result = processor.process_phase(phases_to_run[0])
        else:
            # Multiple phases
            results = {}
            for phase in phases_to_run:
                result = processor.process_phase(phase)
                results[phase] = result
                
                # Show progress
                completed = phases_to_run.index(phase) + 1
                remaining = len(phases_to_run) - completed
                print(f"\n📊 Progress: {completed}/{len(phases_to_run)} phases complete")
                
                if remaining > 0:
                    print(f"   Remaining phases: {', '.join(phases_to_run[completed:])}")
        
        # Generate reports
        print(f"\n📄 Generating reports...")
        output_gen = OutputGenerator()
        reports = output_gen.generate_all_reports()
        
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"📁 Reports saved to: {output_gen.output_dir}")
        
        # Show actual costs
        cost_summary = processor.api_client.get_cost_summary()
        print(f"\n💰 ACTUAL COST: £{cost_summary['total_cost']:.2f}")
        print(f"   (Estimated was: £{estimated_cost:.2f})")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Analysis interrupted by user")
        print(f"✅ Progress saved - use --resume to continue")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())