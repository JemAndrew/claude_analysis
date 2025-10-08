"""
Fix MSG File Handling in Document Loader
Adds safe handling for .msg files to prevent crashes

RUN THIS NOW: python fix_msg_handling.py
"""

from pathlib import Path
import re


def fix_msg_handling():
    """Add .msg file handling to document loader"""
    
    file_path = Path('src/utils/document_loader.py')
    
    print("="*70)
    print("🔧 FIXING MSG FILE HANDLING")
    print("="*70)
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if '.msg' in content and 'Skip MSG files' in content:
        print("   ✅ Already fixed!")
        return True
    
    # Find the PST skip section and add MSG handling after it
    pst_skip_section = '''        # Skip PST files (email archives - handle separately)
        if file_path.suffix.lower() == '.pst':
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[EMAIL ARCHIVE: {file_size_mb:.1f} MB - Extract to .msg files first]',
                'preview': f'PST email archive ({file_size_mb:.1f} MB)',
                'metadata': {
                    'file_type': 'pst',
                    'size_mb': file_size_mb,
                    'skip_reason': 'Email archive - requires extraction'
                }
            }'''
    
    # New MSG skip section
    msg_skip_section = '''        # Skip PST files (email archives - handle separately)
        if file_path.suffix.lower() == '.pst':
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[EMAIL ARCHIVE: {file_size_mb:.1f} MB - Extract to .msg files first]',
                'preview': f'PST email archive ({file_size_mb:.1f} MB)',
                'metadata': {
                    'file_type': 'pst',
                    'size_mb': file_size_mb,
                    'skip_reason': 'Email archive - requires extraction'
                }
            }
        
        # Skip MSG files (individual emails - handle in Phase 5)
        if file_path.suffix.lower() == '.msg':
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[EMAIL MESSAGE: {file_size_mb:.1f} MB - Process in Phase 5]',
                'preview': f'Outlook email message ({file_size_mb:.1f} MB)',
                'metadata': {
                    'file_type': 'msg',
                    'size_mb': file_size_mb,
                    'skip_reason': 'Email message - process in Phase 5 email analysis'
                }
            }'''
    
    # Replace
    if pst_skip_section in content:
        content = content.replace(pst_skip_section, msg_skip_section)
        
        # Save
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Patched successfully!")
        print("\n📋 Changes made:")
        print("   • Added .msg file detection")
        print("   • MSG files now skipped safely (like PST files)")
        print("   • Returns placeholder with metadata")
        print("   • Phase 5 will handle email extraction")
        
        return True
    else:
        print("   ⚠️  Could not find PST skip section!")
        print("   Manual fix needed - see instructions below")
        return False


def print_manual_instructions():
    """Print manual fix instructions if automatic patch fails"""
    
    print("\n" + "="*70)
    print("📖 MANUAL FIX INSTRUCTIONS")
    print("="*70)
    
    print("""
Open: src/utils/document_loader.py

Find this section (around line 80):

    # Skip PST files (email archives - handle separately)
    if file_path.suffix.lower() == '.pst':
        return {
            ...
        }

Add this NEW section right after it:

    # Skip MSG files (individual emails - handle in Phase 5)
    if file_path.suffix.lower() == '.msg':
        return {
            'filename': file_path.name,
            'doc_id': self._generate_doc_id(file_path),
            'content': f'[EMAIL MESSAGE: {file_size_mb:.1f} MB - Process in Phase 5]',
            'preview': f'Outlook email message ({file_size_mb:.1f} MB)',
            'metadata': {
                'file_type': 'msg',
                'size_mb': file_size_mb,
                'skip_reason': 'Email message - process in Phase 5 email analysis'
            }
        }

Save the file and Pass 1 will safely skip MSG files!
""")


def main():
    """Run the fix"""
    
    print("\n🚨 URGENT: MSG FILE HANDLING FIX")
    print("   Your Pass 1 may crash or produce errors on .msg files")
    print("   This patch will make it skip them safely\n")
    
    success = fix_msg_handling()
    
    if success:
        print("\n" + "="*70)
        print("✅ FIX APPLIED SUCCESSFULLY!")
        print("="*70)
        print("\n💡 What happens now:")
        print("   • Pass 1 will skip .msg files (won't crash)")
        print("   • MSG files marked for Phase 5 processing")
        print("   • PST extraction (Phase 5) will handle all emails")
        print("   • Your current Pass 1 can continue safely")
        
        print("\n🎯 Next steps:")
        print("   1. Your Pass 1 is safe to continue")
        print("   2. Run PST extraction after Pass 1-4 complete")
        print("   3. Phase 5 will process all emails (PST + MSG)")
        
    else:
        print_manual_instructions()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()