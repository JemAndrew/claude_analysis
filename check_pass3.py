#!/usr/bin/env python3
"""
Find all Pass 2 result files on your system
"""

from pathlib import Path
import json
from datetime import datetime

print("="*70)
print("SEARCHING FOR PASS 2 RESULTS")
print("="*70)

# Search locations
base_paths = [
    Path(r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master'),
    Path(r'C:\Users\JemAndrew\Velitor'),
    Path(r'.'),  # Current directory
]

found_files = []

for base in base_paths:
    if not base.exists():
        continue
    
    print(f"\nSearching in: {base}")
    
    # Look for any pass_2_results.json files
    for json_file in base.rglob('pass_2_results.json'):
        try:
            # Get file info
            size = json_file.stat().st_size
            modified = json_file.stat().st_mtime
            mod_time = datetime.fromtimestamp(modified)
            
            print(f"\n  📁 Found: {json_file.relative_to(base)}")
            print(f"     Full path: {json_file}")
            print(f"     Size: {size:,} bytes")
            print(f"     Modified: {mod_time}")
            
            # Try to load and check contents
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                iterations = data.get('total_iterations', 0)
                confidence = data.get('final_confidence', 0)
                
                print(f"     Iterations: {iterations}")
                print(f"     Confidence: {confidence:.2%}")
                
                # Count findings
                total_findings = 0
                for iteration in data.get('iterations', []):
                    total_findings += len(iteration.get('breaches', []))
                    total_findings += len(iteration.get('contradictions', []))
                    total_findings += len(iteration.get('novel_arguments', []))
                
                print(f"     Total findings: {total_findings}")
                
                found_files.append({
                    'path': json_file,
                    'size': size,
                    'modified': mod_time,
                    'iterations': iterations,
                    'confidence': confidence,
                    'findings': total_findings
                })
                
            except Exception as e:
                print(f"     ⚠️  Error reading file: {e}")
        
        except Exception as e:
            print(f"  ❌ Error accessing {json_file}: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if not found_files:
    print("\n❌ No pass_2_results.json files found!")
    print("\nPossible reasons:")
    print("  1. Pass 2 hasn't been run yet")
    print("  2. Pass 2 crashed before saving results")
    print("  3. Results saved to unexpected location")
    
    print("\n💡 Check if Pass 2 directory exists:")
    check_dirs = [
        Path(r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\output\analysis\pass_2'),
        Path(r'.\data\output\analysis\pass_2'),
    ]
    
    for d in check_dirs:
        if d.exists():
            print(f"\n  ✅ Directory exists: {d}")
            print(f"     Contents:")
            for item in d.iterdir():
                print(f"       - {item.name}")
        else:
            print(f"\n  ❌ Directory doesn't exist: {d}")
else:
    print(f"\n✅ Found {len(found_files)} Pass 2 result file(s)")
    
    # Show most recent
    if found_files:
        most_recent = max(found_files, key=lambda x: x['modified'])
        print(f"\n📊 Most recent Pass 2 results:")
        print(f"   Path: {most_recent['path']}")
        print(f"   Modified: {most_recent['modified']}")
        print(f"   Iterations: {most_recent['iterations']}")
        print(f"   Confidence: {most_recent['confidence']:.2%}")
        print(f"   Findings: {most_recent['findings']}")
        
        print(f"\n💡 To view this file:")
        print(f"   notepad \"{most_recent['path']}\"")

print("="*70)

# Also search for any JSON files in pass_2 directories
print("\n" + "="*70)
print("SEARCHING FOR ALL FILES IN pass_2 DIRECTORIES")
print("="*70)

for base in base_paths:
    if not base.exists():
        continue
    
    for pass2_dir in base.rglob('pass_2'):
        if pass2_dir.is_dir():
            print(f"\n📁 {pass2_dir}")
            
            files = list(pass2_dir.iterdir())
            if files:
                print(f"   Contents ({len(files)} files):")
                for f in sorted(files):
                    size = f.stat().st_size if f.is_file() else 0
                    print(f"     {'📄' if f.is_file() else '📁'} {f.name} ({size:,} bytes)")
            else:
                print(f"   ⚠️  Directory is empty!")

print("="*70)