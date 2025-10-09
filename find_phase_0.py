#!/usr/bin/env python3
"""
Find where Phase 0 case_foundation.json is located
"""

from pathlib import Path

print("="*70)
print("SEARCHING FOR PHASE 0")
print("="*70)

# Check possible locations
possible_locations = [
    Path(r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\output\analysis\phase_0'),
    Path(r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\output\phase_0'),
    Path(r'C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1\analysis\phase_0'),
    Path(r'.\data\output\analysis\phase_0'),
    Path(r'.\data\output\phase_0'),
]

found = []

for location in possible_locations:
    print(f"\nChecking: {location}")
    
    if not location.exists():
        print("  ❌ Directory doesn't exist")
        continue
    
    print("  ✅ Directory exists")
    
    # Check for case_foundation.json
    case_file = location / "case_foundation.json"
    if case_file.exists():
        print(f"  🎯 FOUND: case_foundation.json")
        
        # Get file size and modification time
        size = case_file.stat().st_size
        modified = case_file.stat().st_mtime
        from datetime import datetime
        mod_time = datetime.fromtimestamp(modified)
        
        print(f"     Size: {size:,} bytes")
        print(f"     Modified: {mod_time}")
        print(f"     Full path: {case_file.absolute()}")
        
        found.append(case_file.absolute())
    else:
        print("  ❌ case_foundation.json not found")

print("\n" + "="*70)
if found:
    print(f"✅ Found {len(found)} Phase 0 file(s)")
    print("\nUse this path in config_folder69.py:")
    print(f"self.phase_0_dir = Path(r'{found[0].parent}')")
else:
    print("❌ No Phase 0 files found")
    print("\nYou may need to run Phase 0 first:")
    print("python main.py phase0")
print("="*70)