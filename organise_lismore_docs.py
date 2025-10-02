#!/usr/bin/env python3
from pathlib import Path
import shutil

SOURCE = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1")
DEST = Path(r"C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\input\disclosure")

SUPPORTED = ['.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.html']
DEST.mkdir(parents=True, exist_ok=True)

folders = sorted([f for f in SOURCE.iterdir() if f.is_dir()])
total_copied = 0
total_skipped = 0
total_errors = 0

for i, folder in enumerate(folders, 1):
    print(f"[{i}/73] {folder.name}")
    folder_copied = 0
    folder_skipped = 0
    
    try:
        for file_path in folder.rglob('*'):
            try:
                if not file_path.is_file():
                    continue
                
                if file_path.suffix.lower() not in SUPPORTED:
                    continue
                
                dest = DEST / file_path.name
                
                # Skip if already exists
                if dest.exists():
                    folder_skipped += 1
                    total_skipped += 1
                    continue
                
                shutil.copy2(file_path, dest)
                folder_copied += 1
                total_copied += 1
                
                if folder_copied % 50 == 0:
                    print(f"  Copied: {folder_copied}...")
                    
            except (FileNotFoundError, OSError, PermissionError):
                total_errors += 1
                continue
                
    except (FileNotFoundError, OSError):
        print(f"  ERROR: Path issues, skipping folder")
        total_errors += 1
        continue
    
    if folder_copied > 0 or folder_skipped > 10:
        print(f"  New: {folder_copied}, Already had: {folder_skipped}")

print(f"\n=== COMPLETE ===")
print(f"New files copied: {total_copied}")
print(f"Already existed: {total_skipped}")
print(f"Errors: {total_errors}")