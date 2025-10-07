#!/usr/bin/env python3
"""
Automatic Bug Fixer for client.py
Finds and fixes the "keywords must be strings" error
British English throughout
"""

import re
from pathlib import Path
from typing import List, Tuple


def find_client_file() -> Path:
    """Find client.py file in project"""
    possible_paths = [
        Path('src/api/client.py'),
        Path('api/client.py'),
        Path('client.py'),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(
        "Cannot find client.py. Run this script from project root directory."
    )


def find_bugs(content: str) -> List[Tuple[int, str, str]]:
    """
    Find all occurrences of the bug
    
    Returns:
        List of (line_number, buggy_line, fixed_line)
    """
    bugs = []
    lines = content.split('\n')
    
    # Pattern to match: api_params[temperature] = 1.0
    # This captures using temperature variable as key instead of string
    bug_pattern = re.compile(r"(\s*)api_params\[temperature\]\s*=\s*1\.0")
    
    for i, line in enumerate(lines, start=1):
        match = bug_pattern.search(line)
        if match:
            indent = match.group(1)
            fixed_line = f"{indent}api_params['temperature'] = 1.0"
            bugs.append((i, line, fixed_line))
    
    return bugs


def fix_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Fix the bugs in client.py
    
    Args:
        file_path: Path to client.py
        dry_run: If True, show what would be fixed without making changes
        
    Returns:
        True if fixes were applied or would be applied
    """
    print(f"\n{'='*70}")
    print(f"Analysing: {file_path}")
    print(f"{'='*70}\n")
    
    # Read file
    content = file_path.read_text(encoding='utf-8')
    
    # Find bugs
    bugs = find_bugs(content)
    
    if not bugs:
        print("✅ No bugs found! File is already correct.")
        return False
    
    # Show bugs
    print(f"❌ Found {len(bugs)} bug(s):\n")
    for line_num, buggy_line, fixed_line in bugs:
        print(f"Line {line_num}:")
        print(f"  BEFORE: {buggy_line.strip()}")
        print(f"  AFTER:  {fixed_line.strip()}")
        print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes made")
        print("   Run without --dry-run to apply fixes")
        return True
    
    # Apply fixes
    print("Applying fixes...")
    fixed_content = content
    
    for _, buggy_line, fixed_line in bugs:
        fixed_content = fixed_content.replace(buggy_line, fixed_line)
    
    # Create backup
    backup_path = file_path.with_suffix('.py.backup')
    file_path.rename(backup_path)
    print(f"✅ Created backup: {backup_path}")
    
    # Write fixed file
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"✅ Fixed file saved: {file_path}")
    
    return True


def verify_fix(file_path: Path) -> bool:
    """Verify the fix was applied correctly"""
    print(f"\n{'='*70}")
    print("Verifying fix...")
    print(f"{'='*70}\n")
    
    content = file_path.read_text(encoding='utf-8')
    bugs = find_bugs(content)
    
    if bugs:
        print(f"❌ Verification failed: {len(bugs)} bug(s) still present")
        return False
    
    # Check for correct pattern
    correct_pattern = re.compile(r"api_params\['temperature'\]\s*=\s*1\.0")
    matches = correct_pattern.findall(content)
    
    if matches:
        print(f"✅ Verification passed!")
        print(f"   Found {len(matches)} correct usage(s) of api_params['temperature']")
        return True
    else:
        print("⚠️  No temperature assignments found")
        print("   This might be OK if extended thinking isn't used")
        return True


def main():
    """Main entry point"""
    import sys
    
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "AUTOMATIC CLIENT.PY BUG FIXER" + " "*24 + "║")
    print("║" + " "*10 + "Fixes: TypeError: keywords must be strings" + " "*15 + "║")
    print("╚" + "═"*68 + "╝")
    
    # Check for dry-run flag
    dry_run = '--dry-run' in sys.argv
    
    try:
        # Find client.py
        client_file = find_client_file()
        
        # Fix bugs
        changes_made = fix_file(client_file, dry_run=dry_run)
        
        if not changes_made:
            return 0
        
        if dry_run:
            print("\n" + "="*70)
            print("Next steps:")
            print("="*70)
            print("1. Review the changes above")
            print("2. Run: python auto_fix_client.py  (without --dry-run)")
            print("3. Run: python validate_api_call.py  (to test fixes)")
            return 0
        
        # Verify fix
        if verify_fix(client_file):
            print("\n" + "="*70)
            print("SUCCESS! Next steps:")
            print("="*70)
            print("1. Run: python validate_api_call.py")
            print("2. If tests pass, run your full caching process")
            print("3. Backup saved as: client.py.backup")
            return 0
        else:
            print("\n❌ Verification failed")
            return 1
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())