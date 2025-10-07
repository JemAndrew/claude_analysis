#!/usr/bin/env python3
"""
VERIFIED FIX for --limit parameter
Handles all variations of the function signature
British English throughout - Lismore-sided
"""

from pathlib import Path
import re


def fix_pass_executor_signature():
    """Fix the execute_pass_1_triage signature in multiple ways"""
    
    file_path = Path('src/core/pass_executor.py')
    
    print("="*70)
    print("🔧 FIXING execute_pass_1_triage SIGNATURE")
    print("="*70)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try multiple patterns to find the method
    patterns = [
        (r'def execute_pass_1_triage\(self\) -> Dict:', 
         'def execute_pass_1_triage(self, limit: int = None) -> Dict:'),
        
        (r'def execute_pass_1_triage\(self\):', 
         'def execute_pass_1_triage(self, limit: int = None):'),
         
        (r'def execute_pass_1_triage\(self, all_documents: List\[Dict\]\):', 
         'def execute_pass_1_triage(self, limit: int = None):'),
    ]
    
    fixed = False
    for old_pattern, new_signature in patterns:
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_signature, content)
            print(f"   ✅ Found and fixed signature!")
            fixed = True
            break
    
    if not fixed:
        print("   ⚠️  Could not find signature automatically")
        print("\n   Manual fix needed:")
        print("   Find this line in src/core/pass_executor.py:")
        print("   def execute_pass_1_triage(self) -> Dict:")
        print("\n   Change to:")
        print("   def execute_pass_1_triage(self, limit: int = None) -> Dict:")
        return False
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def verify_all_fixes():
    """Verify all three files are fixed"""
    
    print("\n" + "="*70)
    print("✅ VERIFICATION")
    print("="*70)
    
    errors = []
    
    # Check pass_executor.py
    pass_exec = Path('src/core/pass_executor.py')
    with open(pass_exec, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def execute_pass_1_triage(self, limit' not in content:
        errors.append("❌ pass_executor.py: Method signature missing 'limit' parameter")
        print("   ❌ pass_executor.py: Method signature not updated")
        print("\n   You need to manually change:")
        print("   def execute_pass_1_triage(self) -> Dict:")
        print("   to:")
        print("   def execute_pass_1_triage(self, limit: int = None) -> Dict:")
    else:
        print("   ✅ pass_executor.py: Signature has limit parameter")
    
    if 'TEST MODE: Limiting to' not in content:
        errors.append("❌ pass_executor.py: Limit check code missing")
        print("   ❌ pass_executor.py: Limit check not added")
    else:
        print("   ✅ pass_executor.py: Limit check present")
    
    # Check orchestrator.py
    orch = Path('src/core/orchestrator.py')
    with open(orch, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def execute_single_pass(self, pass_num: str, limit' not in content:
        errors.append("❌ orchestrator.py: Method signature missing 'limit'")
        print("   ❌ orchestrator.py: Missing limit parameter")
    else:
        print("   ✅ orchestrator.py: Has limit parameter")
    
    if 'execute_pass_1_triage(limit=' not in content:
        errors.append("❌ orchestrator.py: Not passing limit to pass_executor")
        print("   ❌ orchestrator.py: Not passing limit")
    else:
        print("   ✅ orchestrator.py: Passes limit correctly")
    
    # Check main.py
    main = Path('main.py')
    with open(main, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def run_single_pass(orchestrator, pass_num: str, limit' not in content:
        errors.append("❌ main.py: Function missing 'limit' parameter")
        print("   ❌ main.py: Missing limit parameter")
    else:
        print("   ✅ main.py: Has limit parameter")
    
    if "run_single_pass(orchestrator, '1', limit=" not in content:
        errors.append("❌ main.py: Not passing limit to run_single_pass")
        print("   ❌ main.py: Not passing args.limit")
    else:
        print("   ✅ main.py: Passes args.limit correctly")
    
    return len(errors) == 0, errors


if __name__ == '__main__':
    print("FIXING --limit PARAMETER ISSUE\n")
    
    # Try to fix
    success = fix_pass_executor_signature()
    
    # Verify
    all_good, errors = verify_all_fixes()
    
    if all_good:
        print("\n" + "="*70)
        print("✅ ALL FIXES VERIFIED!")
        print("="*70)
        print("\nRun: python main.py pass1 --limit 5")
        print("\nShould complete in ~30 seconds with only 5 documents!")
    else:
        print("\n" + "="*70)
        print("⚠️  MANUAL FIX NEEDED")
        print("="*70)
        print("\nErrors found:")
        for error in errors:
            print(f"  {error}")
        
        print("\n📝 QUICK MANUAL FIX:")
        print("-" * 70)
        print("Open: src/core/pass_executor.py")
        print("\nFind (around line 160-180):")
        print("  def execute_pass_1_triage(self) -> Dict:")
        print("\nChange to:")
        print("  def execute_pass_1_triage(self, limit: int = None) -> Dict:")
        print("\nSave and run: python main.py pass1 --limit 5")
        print("-" * 70)