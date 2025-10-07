#!/usr/bin/env python3
"""
VERIFICATION: Check all fixes are applied correctly

RUN THIS THIRD: python verify_system.py
"""

from pathlib import Path
import json

def check_phase_0_exists():
    """Check if Phase 0 completed"""
    print("\n1️⃣  Checking Phase 0 completion...")
    
    phase_0_file = Path('data/output/analysis/phase_0/case_foundation.json')
    
    if not phase_0_file.exists():
        print("   ⚠️  Phase 0 NOT completed")
        print("   Run: python main.py phase0")
        return False
    
    with open(phase_0_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pass_1_ref = data.get('pass_1_reference', {})
    
    if not pass_1_ref:
        print("   ❌ Phase 0 missing pass_1_reference!")
        return False
    
    print("   ✅ Phase 0 completed")
    print(f"      • Allegations: {len(pass_1_ref.get('allegations', []))}")
    print(f"      • Defences: {len(pass_1_ref.get('defences', []))}")
    print(f"      • Patterns: {len(pass_1_ref.get('document_patterns', []))}")
    return True

def check_phase_0_integration():
    """Check Phase 0 integration fix"""
    print("\n2️⃣  Checking Phase 0 integration fix...")
    
    pass_executor = Path('src/core/pass_executor.py')
    with open(pass_executor, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'pass_1_reference' in content:
        print("   ✅ Phase 0 integration patched")
        return True
    else:
        print("   ❌ Phase 0 integration NOT patched")
        print("   Run: python fix_phase_0_integration.py")
        return False

def check_large_file_protection():
    """Check large file protection"""
    print("\n3️⃣  Checking large file protection...")
    
    doc_loader = Path('src/utils/document_loader.py')
    with open(doc_loader, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'MAX_FILE_SIZE_MB' in content and '_load_pdf_safe' in content:
        print("   ✅ Large file protection added")
        return True
    else:
        print("   ❌ Large file protection NOT added")
        print("   Run: python fix_large_files.py")
        return False

def check_api_key():
    """Check API key configured"""
    print("\n4️⃣  Checking API key...")
    
    import os
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if api_key and api_key.startswith('sk-ant-'):
        print(f"   ✅ API key configured: {api_key[:20]}...")
        return True
    else:
        print("   ❌ API key NOT configured")
        print("   Set: $env:ANTHROPIC_API_KEY='your-key-here'")
        return False

def check_folder_structure():
    """Check disclosure folders exist"""
    print("\n5️⃣  Checking folder structure...")
    
    disclosure_root = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1")
    
    if not disclosure_root.exists():
        print(f"   ❌ Disclosure folder not found: {disclosure_root}")
        return False
    
    # Count folders
    folders = [f for f in disclosure_root.iterdir() if f.is_dir()]
    print(f"   ✅ Found {len(folders)} folders")
    
    # Check for large files
    print("\n   Checking for large files...")
    pdfs = list(disclosure_root.rglob("*.pdf"))
    psts = list(disclosure_root.rglob("*.pst"))
    
    print(f"   ✅ PDFs: {len(pdfs)}")
    print(f"   ✅ PSTs: {len(psts)}")
    
    return True

if __name__ == '__main__':
    print("="*70)
    print("🔍 SYSTEM VERIFICATION")
    print("="*70)
    
    checks = [
        check_phase_0_exists(),
        check_phase_0_integration(),
        check_large_file_protection(),
        check_api_key(),
        check_folder_structure()
    ]
    
    print("\n" + "="*70)
    if all(checks):
        print("✅ ALL CHECKS PASSED - SYSTEM READY!")
        print("="*70)
        print("\n🚀 Ready to run:")
        print("   python main.py pass1")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("="*70)
        print("\nFix issues above, then run verification again.")