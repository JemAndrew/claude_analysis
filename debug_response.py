#!/usr/bin/env python3
"""
Debug script: See what Claude is actually returning in Pass 2
This won't affect your Folder 69 run
"""

import json
from pathlib import Path

print("="*70)
print("DEBUGGING PASS 2 RESPONSES")
print("="*70)

# Check if there are any iteration responses saved
pass2_dir = Path('data/output/analysis/pass_2')
results_file = pass2_dir / 'pass_2_results.json'

if not results_file.exists():
    print("\n❌ No Pass 2 results file found")
    print("   The run might not have saved anything yet")
    exit(1)

with open(results_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n📊 Pass 2 Status:")
print(f"   Total iterations: {data.get('total_iterations', 0)}")
print(f"   Confidence: {data.get('final_confidence', 0):.2%}")

iterations = data.get('iterations', [])
print(f"   Saved iterations: {len(iterations)}")

if not iterations:
    print("\n❌ No iteration data saved yet")
    exit(1)

# Look at the most recent iteration
latest = iterations[-1]

print(f"\n📄 Latest Iteration (#{len(iterations)}):")
print(f"   Documents analysed: {latest.get('documents_analysed', 'N/A')}")
print(f"   Breaches found: {len(latest.get('breaches', []))}")
print(f"   Contradictions found: {len(latest.get('contradictions', []))}")
print(f"   Confidence: {latest.get('confidence', 'N/A')}")

# Check if raw response is saved
if 'raw_response' in latest:
    raw = latest['raw_response']
    print(f"\n✅ Raw response captured ({len(raw)} characters)")
    
    print(f"\n{'='*70}")
    print("CLAUDE'S RAW RESPONSE (First 2000 chars)")
    print(f"{'='*70}")
    print(raw[:2000])
    
    if len(raw) > 2000:
        print(f"\n... [truncated, total length: {len(raw)} chars] ...")
        print(f"\n{'='*70}")
        print("LAST 1000 CHARS")
        print(f"{'='*70}")
        print(raw[-1000:])
    
    # Check for structured blocks
    print(f"\n{'='*70}")
    print("CHECKING FOR STRUCTURED BLOCKS")
    print(f"{'='*70}")
    
    blocks = {
        'BREACH_START': raw.count('BREACH_START'),
        'BREACH_END': raw.count('BREACH_END'),
        'CONTRADICTION_START': raw.count('CONTRADICTION_START'),
        'CONTRADICTION_END': raw.count('CONTRADICTION_END'),
        'CONFIDENCE_START': raw.count('CONFIDENCE_START'),
        'CONFIDENCE_END': raw.count('CONFIDENCE_END'),
        'CONFIDENCE:': raw.count('CONFIDENCE:'),
    }
    
    print(f"\nStructured block counts:")
    for block, count in blocks.items():
        emoji = "✅" if count > 0 else "❌"
        print(f"   {emoji} {block}: {count}")
    
    # Save full response to file
    debug_file = pass2_dir / 'debug_raw_response.txt'
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(raw)
    print(f"\n💾 Full response saved to: {debug_file}")
    
else:
    print(f"\n❌ No raw response saved in iteration data")
    print(f"   This means the system isn't saving Claude's responses")
    print(f"   Check if 'raw_response' storage is enabled in pass_executor.py")

# Check what the parser extracted
print(f"\n{'='*70}")
print("WHAT THE PARSER EXTRACTED")
print(f"{'='*70}")

print(f"\nBreaches: {len(latest.get('breaches', []))}")
if latest.get('breaches'):
    print(f"   Sample breach:")
    breach = latest['breaches'][0]
    print(f"   - Description: {breach.get('description', 'N/A')[:100]}")
    print(f"   - Evidence: {breach.get('evidence', [])}")
    print(f"   - Confidence: {breach.get('confidence', 'N/A')}")

print(f"\nContradictions: {len(latest.get('contradictions', []))}")
print(f"Timeline events: {len(latest.get('timeline_events', []))}")
print(f"Novel arguments: {len(latest.get('novel_arguments', []))}")

print(f"\n{'='*70}")
print("DIAGNOSIS")
print(f"{'='*70}")

if 'raw_response' not in latest:
    print("\n❌ PROBLEM: Raw responses not being saved")
    print("   Solution: Enable raw response storage in pass_executor.py")
elif blocks['BREACH_START'] == 0:
    print("\n❌ PROBLEM: Claude isn't using structured format")
    print("   Claude is responding in natural language, not structured blocks")
    print("\n   Possible causes:")
    print("   1. Prompt doesn't clearly require structured format")
    print("   2. Extended thinking might be interfering")
    print("   3. System prompt not emphasizing structure")
    
    print("\n   Solutions:")
    print("   1. Check autonomous.py deep_analysis_prompt()")
    print("   2. Make structured format requirements MORE explicit")
    print("   3. Add examples in the prompt")
elif blocks['BREACH_START'] != blocks['BREACH_END']:
    print("\n⚠️  PROBLEM: Mismatched block tags")
    print(f"   BREACH_START: {blocks['BREACH_START']}")
    print(f"   BREACH_END: {blocks['BREACH_END']}")
    print("   Claude started blocks but didn't finish them properly")
else:
    print(f"\n✅ Claude is using structured format")
    print(f"   Found {blocks['BREACH_START']} breach blocks")
    print("\n❌ But parser isn't extracting them!")
    print("   Problem is in _parse_deep_analysis_response() method")

print(f"\n{'='*70}")