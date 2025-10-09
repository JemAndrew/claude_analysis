#!/usr/bin/env python3
"""
Test Pass 2 with just 2 iterations and save raw responses
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.orchestrator import LitigationOrchestrator

print("="*70)
print("TESTING PASS 2 WITH RAW RESPONSE STORAGE")
print("="*70)

# Check Pass 1 exists
pass1_file = Path('data/output/analysis/pass_1/pass_1_results.json')
if not pass1_file.exists():
    print("\n❌ Pass 1 results not found!")
    print("   Run: python main.py pass1")
    exit(1)

print("\n✅ Pass 1 results found")

# Override config for testing
orch = LitigationOrchestrator()
orch.config.pass_2_config['max_iterations'] = 2  # Only 2 iterations
orch.config.pass_2_config['confidence_threshold'] = 0.99  # Won't stop early

print("\n🧪 Test Configuration:")
print("   Max iterations: 2")
print("   Confidence threshold: 99% (won't stop)")
print("\nRunning Pass 2 test...\n")

try:
    result = orch.execute_single_pass('2')
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    print(f"\n✅ Iterations completed: {result.get('total_iterations', 0)}")
    print(f"   Final confidence: {result.get('final_confidence', 0):.2%}")
    
    # Check if raw responses saved
    iterations = result.get('iterations', [])
    if iterations:
        has_raw = 'raw_response' in iterations[0]
        if has_raw:
            raw_len = len(iterations[0]['raw_response'])
            print(f"\n✅ Raw response saved: {raw_len:,} characters")
            print(f"\n💾 Now run: python debug_pass2_response.py")
        else:
            print(f"\n❌ Raw response NOT saved!")
            print(f"   The line might not be in the right place")
            print(f"   Check src/core/pass_executor.py around line 1245")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()