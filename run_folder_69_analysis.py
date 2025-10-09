#!/usr/bin/env python3
"""
Folder 69 Late Disclosure Deep Dive Launcher
Runs targeted forensic analysis on PHL's late disclosure
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
    
    # Count documents
    doc_count = len(list(config.disclosure_dir.rglob('*.pdf'))) + \
                len(list(config.disclosure_dir.rglob('*.docx'))) + \
                len(list(config.disclosure_dir.rglob('*.doc')))
    
    print(f"\nDocuments in Folder 69: {doc_count}")
    
    # Estimate
    print(f"\nEstimated cost: £60-95")
    print(f"Estimated time: 10-14 hours")
    
    response = input("\nProceed with analysis? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Create orchestrator with Folder 69 config
    orchestrator = LitigationOrchestrator(config=config)
    
    # Run 3-stage analysis
    print("\n" + "="*70)
    print("STAGE 1: TRIAGE (Folder 69 only)")
    print("="*70)
    pass1_results = orchestrator.execute_single_pass('1')
    
    print("\n" + "="*70)
    print("STAGE 2: ULTRA-DEEP ANALYSIS")
    print("="*70)
    pass2_results = orchestrator.execute_single_pass('2')
    
    print("\n" + "="*70)
    print("STAGE 3: TARGETED INVESTIGATIONS")
    print("="*70)
    pass3_results = orchestrator.execute_single_pass('3')
    
    # Summary
    print("\n" + "="*70)
    print("FOLDER 69 ANALYSIS COMPLETE")
    print("="*70)
    
    print(f"\nStage 1: {pass1_results['priority_count']} priority documents identified")
    print(f"Stage 2: {len(pass2_results.get('breaches', []))} breaches found")
    print(f"         {len(pass2_results.get('contradictions', []))} contradictions found")
    print(f"         {len(pass2_results.get('novel_arguments', []))} novel arguments")
    print(f"Stage 3: {len(pass3_results.get('investigations', []))} investigations completed")
    
    print(f"\nResults saved to: {config.analysis_dir}")
    print("\nNext steps:")
    print("  1. Review findings in: folder_69_analysis/")
    print("  2. Check Pass 2 for smoking guns")
    print("  3. Review investigations for spoliation evidence")

if __name__ == '__main__':
    main()