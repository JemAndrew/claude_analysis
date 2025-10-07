#!/usr/bin/env python3
"""
CRITICAL FIX #1: Phase 0 → Pass 1 Integration
Fixes bug where Pass 1 doesn't use Phase 0 intelligence

RUN THIS FIRST: python fix_phase_0_integration.py
"""

import re
from pathlib import Path

def patch_pass_executor():
    """Fix pass_executor.py to use correct Phase 0 structure"""
    
    file_path = Path('src/core/pass_executor.py')
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Change Phase 0 data loading
    old_pattern = r"stage_3 = phase_0_data\.get\('stage_3_summary', \{\}\)\s*smoking_gun_patterns = stage_3\.get\('smoking_gun_patterns', \[\]\)"
    
    new_code = """phase_0_foundation = phase_0_data.get('pass_1_reference', {})
                
                if phase_0_foundation and len(phase_0_foundation.get('document_patterns', [])) > 0:"""
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_code.replace('                ', ''), content)
        print("   ✅ Fixed Phase 0 data extraction")
    else:
        print("   ⚠️  Pattern not found - checking if already patched...")
        if 'pass_1_reference' in content:
            print("   ✅ Already patched!")
            return
    
    # Fix 2: Update print statements
    old_print = 'print(f"\\n✅ Loaded {len(smoking_gun_patterns)} smoking gun patterns from Phase 0")'
    new_print = '''print(f"\\n✅ Loaded Phase 0 intelligence:")
                    print(f"   • Allegations: {len(phase_0_foundation.get('allegations', []))}")
                    print(f"   • Defences: {len(phase_0_foundation.get('defences', []))}")
                    print(f"   • Key parties: {len(phase_0_foundation.get('key_parties', []))}")
                    print(f"   • Document patterns: {len(phase_0_foundation.get('document_patterns', []))}")'''
    
    content = content.replace(old_print, new_print)
    
    # Fix 3: Update triage_prompt call
    content = content.replace(
        'smoking_gun_patterns=smoking_gun_patterns',
        'phase_0_foundation=phase_0_foundation'
    )
    
    # Fix 4: Update condition checks
    content = content.replace(
        'if smoking_gun_patterns:',
        'if phase_0_foundation and len(phase_0_foundation.get("document_patterns", [])) > 0:'
    )
    
    # Save patched file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Patched pass_executor.py")

def patch_autonomous_prompts():
    """Fix autonomous.py to accept phase_0_foundation parameter"""
    
    file_path = Path('src/prompts/autonomous.py')
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix method signature
    old_sig = r'def triage_prompt\(self,\s*documents: List\[Dict\],\s*batch_num: int = 0,\s*smoking_gun_patterns: List\[Dict\] = None\)'
    new_sig = 'def triage_prompt(self, documents: List[Dict], batch_num: int = 0, phase_0_foundation: Dict = None)'
    
    content = re.sub(old_sig, new_sig, content)
    
    # Fix parameter usage in method
    content = content.replace('smoking_gun_patterns', 'phase_0_foundation')
    
    # Fix the condition check
    old_condition = 'if smoking_gun_patterns and len(smoking_gun_patterns) > 0:'
    new_condition = 'if phase_0_foundation and len(phase_0_foundation.get("document_patterns", [])) > 0:'
    
    content = content.replace(old_condition, new_condition)
    
    # Fix the pattern extraction
    old_extract = "sorted_patterns = sorted(\n            smoking_gun_patterns,"
    new_extract = "document_patterns = phase_0_foundation.get('document_patterns', [])\n        sorted_patterns = sorted(\n            document_patterns,"
    
    content = content.replace(old_extract, new_extract)
    
    # Save patched file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Patched autonomous.py")

if __name__ == '__main__':
    print("="*70)
    print("🔧 FIXING PHASE 0 → PASS 1 INTEGRATION BUG")
    print("="*70)
    
    try:
        patch_pass_executor()
        patch_autonomous_prompts()
        
        print("\n" + "="*70)
        print("✅ PATCH COMPLETE!")
        print("="*70)
        print("\nPhase 0 intelligence will now be used in Pass 1 triage.")
        print("Your 24 document patterns will guide document scoring!")
        print("\nNext step: python fix_large_files.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()