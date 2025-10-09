#!/usr/bin/env python3
"""
Folder 69 Late Disclosure Deep Dive Launcher
Works with FIXED orchestrator __init__
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config_folder69 import config
from core.orchestrator import LitigationOrchestrator


def main():
    print("="*70)
    print("FOLDER 69 LATE DISCLOSURE - FORENSIC DEEP DIVE")
    print("="*70)
    print(f"\nTarget: {config.disclosure_dir}")
    print(f"Output: {config.analysis_dir}")
    print(f"\nUsing Phase 0 intelligence: {config.phase_0_dir}")
    
    # Check if Phase 0 exists
    phase_0_file = config.phase_0_dir / "case_foundation.json"
    if not phase_0_file.exists():
        print("\n⚠️  WARNING: Phase 0 not found!")
        print("   Run: python main.py phase0")
        response = input("\nContinue without Phase 0? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            return
    
    # Count documents
    try:
        doc_count = len(list(config.disclosure_dir.rglob('*.pdf'))) + \
                    len(list(config.disclosure_dir.rglob('*.docx'))) + \
                    len(list(config.disclosure_dir.rglob('*.doc')))
        print(f"\nDocuments in Folder 69: {doc_count}")
    except Exception as e:
        print(f"\n⚠️  Error counting documents: {e}")
    
    # Show settings
    print(f"\n{'='*70}")
    print("ANALYSIS SETTINGS")
    print(f"{'='*70}")
    print("🔥 Deduplication: DISABLED (analyses every document)")
    print("🧠 Pass 2: Up to 100 iterations, 20K thinking tokens")
    print("🔍 Cross-referencing: ENABLED (BM25 retrieval)")
    print("🎯 Confidence threshold: 99% (very thorough)")
    print("🔬 Pass 3: 50 investigations, depth 5")
    print("📊 Progress bars: ENABLED")
    
    print(f"\n{'='*70}")
    print("ESTIMATED")
    print(f"{'='*70}")
    print("Cost: £130-195")
    print("Time: 14-25 hours")
    print(f"{'='*70}")
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # ================================================================
    # SUPER SIMPLE: Just pass the config object!
    # The fixed __init__ handles it correctly
    # ================================================================
    print("\n" + "="*70)
    print("INITIALISING ORCHESTRATOR")
    print("="*70)
    
    orchestrator = LitigationOrchestrator(config_override=config)
    
    # ================================================================
    # RUN ANALYSIS
    # ================================================================
    
    print("\n" + "="*70)
    print("PASS 1: TRIAGE")
    print("="*70)
    try:
        pass1_results = orchestrator.execute_single_pass('1')
        priority_count = pass1_results.get('priority_count', 0)
        print(f"\n✅ {priority_count} priority documents identified")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print("PASS 2: ULTRA-DEEP ANALYSIS")
    print("="*70)
    print("⏱️  This will take 10-18 hours...")
    try:
        pass2_results = orchestrator.execute_single_pass('2')
        
        # Extract all findings from iterations
        all_breaches = []
        all_contradictions = []
        all_novel_arguments = []
        all_timeline_events = []
        
        for iteration in pass2_results.get('iterations', []):
            all_breaches.extend(iteration.get('breaches', []))
            all_contradictions.extend(iteration.get('contradictions', []))
            all_novel_arguments.extend(iteration.get('novel_arguments', []))
            all_timeline_events.extend(iteration.get('timeline_events', []))
        
        print(f"\n✅ Pass 2 complete:")
        print(f"   Iterations: {pass2_results.get('total_iterations', 0)}")
        print(f"   Confidence: {pass2_results.get('final_confidence', 0):.2%}")
        print(f"   Breaches: {len(all_breaches)}")
        print(f"   Contradictions: {len(all_contradictions)}")
        print(f"   Novel arguments: {len(all_novel_arguments)}")
        print(f"   Timeline events: {len(all_timeline_events)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print("PASS 3: INVESTIGATIONS")
    print("="*70)
    try:
        pass3_results = orchestrator.execute_single_pass('3')
        
        total_investigations = pass3_results.get('total_investigations', 0)
        print(f"\n✅ {total_investigations} investigations completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ================================================================
    # SUMMARY
    # ================================================================
    
    print("\n" + "="*70)
    print("FOLDER 69 ANALYSIS COMPLETE")
    print("="*70)
    
    print(f"\n📊 RESULTS:")
    print(f"  Priority documents: {priority_count}")
    print(f"  Breaches: {len(all_breaches)}")
    print(f"  Contradictions: {len(all_contradictions)}")
    print(f"  Novel arguments: {len(all_novel_arguments)}")
    print(f"  Timeline events: {len(all_timeline_events)}")
    print(f"  Investigations: {total_investigations}")
    
    # Total cost
    total_cost = (pass1_results.get('cost_gbp', 0) + 
                  pass2_results.get('total_cost_gbp', 0) + 
                  pass3_results.get('total_cost_gbp', 0))
    print(f"\n💰 TOTAL COST: £{total_cost:.2f}")
    
    print(f"\n📁 Results saved to: {config.analysis_dir}")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review smoking guns: folder_69_analysis/pass_2/")
    print("2. Review investigations: folder_69_analysis/pass_3/")
    print("3. Check novel arguments in pass_2_results.json")
    print("4. Use findings to build adverse inference case")
    
    # API usage
    if hasattr(orchestrator.api_client, 'print_usage_summary'):
        print("\n" + "="*70)
        print("API USAGE")
        print("="*70)
        orchestrator.api_client.print_usage_summary()


if __name__ == '__main__':
    main()