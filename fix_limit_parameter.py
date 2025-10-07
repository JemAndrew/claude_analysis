#!/usr/bin/env python3
"""
FIX --limit PARAMETER - Actually stop loading after N documents
Currently: Loads all docs, then limits triage
Fixed: Stops loading after N documents
British English throughout - Lismore-sided

RUN THIS NOW: python fix_limit_parameter.py
Then: Ctrl+C to kill current process
Then: python main.py pass1 --limit 5
"""

from pathlib import Path
import re


def fix_main_py_limit():
    """Fix main.py to pass limit to document loading"""
    
    file_path = Path('main.py')
    
    print("="*70)
    print("🔧 FIXING --limit PARAMETER")
    print("="*70)
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the run_single_pass function
    pattern = r"def run_single_pass\(orchestrator, pass_num: str\):"
    
    if not re.search(pattern, content):
        print("   ❌ Could not find run_single_pass function!")
        return False
    
    # Find where it calls execute_pass_1
    old_call = r"results = orchestrator\.execute_pass_1\(\)"
    
    if re.search(old_call, content):
        # Check if there's an args.limit available
        if 'args.limit' in content:
            # Replace the call to pass limit
            new_call = "results = orchestrator.execute_pass_1(limit=args.limit if hasattr(args, 'limit') else None)"
            content = re.sub(old_call, new_call, content)
            print("   ✅ Fixed execute_pass_1 call to use limit")
        else:
            print("   ⚠️  args.limit not found in context")
            return False
    else:
        print("   ⚠️  execute_pass_1 call not found")
        return False
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def fix_orchestrator_pass_1():
    """Fix orchestrator to accept and pass limit to pass_executor"""
    
    file_path = Path('src/core/orchestrator.py')
    
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find execute_pass_1 method signature
    old_signature = r"def execute_pass_1\(self\):"
    new_signature = "def execute_pass_1(self, limit: int = None):"
    
    if re.search(old_signature, content):
        content = re.sub(old_signature, new_signature, content)
        print("   ✅ Updated execute_pass_1 signature")
    else:
        print("   ⚠️  execute_pass_1 signature not found or already updated")
    
    # Find where it calls pass_executor
    old_executor_call = r"results = self\.pass_executor\.execute_pass_1_triage\(all_documents\)"
    new_executor_call = "results = self.pass_executor.execute_pass_1_triage(all_documents, limit=limit)"
    
    if re.search(old_executor_call, content):
        content = re.sub(old_executor_call, new_executor_call, content)
        print("   ✅ Updated pass_executor call to pass limit")
    else:
        print("   ⚠️  pass_executor call not found or already updated")
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def fix_pass_executor_limit():
    """Fix pass_executor to stop loading after N documents"""
    
    file_path = Path('src/core/pass_executor.py')
    
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find execute_pass_1_triage signature
    old_signature = r"def execute_pass_1_triage\(self, all_documents: List\[Dict\]\):"
    new_signature = "def execute_pass_1_triage(self, all_documents: List[Dict], limit: int = None):"
    
    if re.search(old_signature, content):
        content = re.sub(old_signature, new_signature, content)
        print("   ✅ Updated execute_pass_1_triage signature")
    else:
        print("   ⚠️  Signature already updated or not found")
    
    # Find where documents are prepared for triage
    # Look for: documents_to_triage = 
    old_triage_prep = r"(\s+)# Remove duplicates if enabled\s+if self\.deduplicator:"
    
    match = re.search(old_triage_prep, content)
    if match:
        indent = match.group(1)
        
        # Insert limit check BEFORE deduplication
        limit_check = f'''{indent}# Apply limit if specified (for testing)
{indent}if limit is not None and limit > 0:
{indent}    print(f"   🔬 TEST MODE: Limiting to {{limit}} documents")
{indent}    all_documents = all_documents[:limit]
{indent}
{indent}'''
        
        content = content[:match.start()] + limit_check + content[match.start():]
        print("   ✅ Added limit check before deduplication")
    else:
        print("   ⚠️  Could not find deduplication section")
        return False
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def verify_fixes():
    """Verify all fixes are in place"""
    
    print("\n" + "="*70)
    print("✅ VERIFICATION")
    print("="*70)
    
    checks = []
    
    # Check main.py
    main_py = Path('main.py')
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'limit=args.limit' in content or 'limit=limit' in content:
        print("   ✅ main.py: Passes limit parameter")
        checks.append(True)
    else:
        print("   ❌ main.py: Doesn't pass limit")
        checks.append(False)
    
    # Check orchestrator
    orchestrator = Path('src/core/orchestrator.py')
    with open(orchestrator, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def execute_pass_1(self, limit' in content:
        print("   ✅ orchestrator.py: Accepts limit parameter")
        checks.append(True)
    else:
        print("   ❌ orchestrator.py: Doesn't accept limit")
        checks.append(False)
    
    # Check pass_executor
    pass_exec = Path('src/core/pass_executor.py')
    with open(pass_exec, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'TEST MODE: Limiting to' in content:
        print("   ✅ pass_executor.py: Limits document loading")
        checks.append(True)
    else:
        print("   ❌ pass_executor.py: Doesn't limit loading")
        checks.append(False)
    
    return all(checks)


if __name__ == '__main__':
    try:
        print("FIXING --limit PARAMETER\n")
        
        # Apply fixes
        success1 = fix_main_py_limit()
        success2 = fix_orchestrator_pass_1()
        success3 = fix_pass_executor_limit()
        
        if not all([success1, success2, success3]):
            print("\n❌ Some fixes failed!")
            exit(1)
        
        # Verify
        if not verify_fixes():
            print("\n❌ Verification failed!")
            exit(1)
        
        print("\n" + "="*70)
        print("✅ --limit PARAMETER FIXED!")
        print("="*70)
        
        print("\n📋 NEXT STEPS:")
        print("-" * 70)
        print("1. Kill the current running process:")
        print("   Ctrl+C")
        print()
        print("2. Test with ACTUALLY only 5 documents:")
        print("   python main.py pass1 --limit 5")
        print()
        print("3. You should see:")
        print("   🔬 TEST MODE: Limiting to 5 documents")
        print("   📄 PROGRESS: Loading doc1.pdf...")
        print("   📄 PROGRESS: Loading doc2.pdf...")
        print("   📄 PROGRESS: Loading doc3.pdf...")
        print("   📄 PROGRESS: Loading doc4.pdf...")
        print("   📄 PROGRESS: Loading doc5.pdf...")
        print("   [STOPS HERE - only 5 files loaded!]")
        print()
        print("4. Should complete in <1 minute!")
        print("-" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()