"""
Fix Email Extraction Paths
Updates the correct folder paths for your disclosure location

RUN THIS: python fix_email_paths.py
"""

from pathlib import Path

def fix_paths():
    """Update paths in both email extraction scripts"""
    
    print("="*70)
    print("🔧 FIXING EMAIL EXTRACTION PATHS")
    print("="*70)
    
    # Correct paths based on your setup
    correct_pst_folder = r'C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1\36- Chronological Email Run'
    correct_root_folder = r'C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1'
    correct_output_folder = r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\emails'
    correct_output_folder_test = r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\emails\test'
    
    # Files to update
    files = [
        'extract_emails.py',
        'test_pst_extraction.py'
    ]
    
    for filename in files:
        filepath = Path(filename)
        
        if not filepath.exists():
            print(f"\n⚠️  {filename} not found - skipping")
            continue
        
        print(f"\n📝 Updating {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace PST folder path
        old_pst = r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\36- Chronological Email Run'
        if old_pst in content:
            content = content.replace(old_pst, correct_pst_folder)
            print(f"   ✅ Updated PST folder path")
        
        # Replace root folder path
        old_root = r'C:\Users\JemAndrew\OneDrive - Velitor\Claude'
        if old_root in content and old_pst not in content:  # Only replace if not part of PST path
            # Be more careful with replacement
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'ROOT_DISCLOSURE_FOLDER = Path' in line and old_root in line:
                    line = line.replace(old_root, correct_root_folder)
                new_lines.append(line)
            content = '\n'.join(new_lines)
            print(f"   ✅ Updated root folder path")
        
        # Replace output folder paths
        old_output = r'C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\emails'
        bad_output_pattern = r'C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1\claude_analysis-master\data\emails'
        
        # Fix any incorrect output paths
        if bad_output_pattern in content:
            content = content.replace(bad_output_pattern, correct_output_folder)
            print(f"   ✅ Fixed incorrect output folder path")
        
        # Ensure output folders are correct
        if filename == 'test_pst_extraction.py':
            # For test script, use test subfolder
            if 'OUTPUT_FOLDER = Path' in content:
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if 'OUTPUT_FOLDER = Path' in line:
                        line = f'    OUTPUT_FOLDER = Path(r"{correct_output_folder_test}")'
                    new_lines.append(line)
                content = '\n'.join(new_lines)
                print(f"   ✅ Set test output folder")
        else:
            # For main extraction script, use main folder
            if 'OUTPUT_FOLDER = Path' in content:
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if 'OUTPUT_FOLDER = Path' in line:
                        line = f'    OUTPUT_FOLDER = Path(r"{correct_output_folder}")'
                    new_lines.append(line)
                content = '\n'.join(new_lines)
                print(f"   ✅ Set main output folder")
        
        # Save updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("\n" + "="*70)
    print("✅ PATHS UPDATED SUCCESSFULLY!")
    print("="*70)
    print("\n📍 Correct paths:")
    print(f"   PST Folder:    {correct_pst_folder}")
    print(f"   Root Folder:   {correct_root_folder}")
    print(f"   Output Folder: {correct_output_folder}")
    print("\n🎯 Now run:")
    print("   python test_pst_extraction.py")
    print("="*70)


if __name__ == "__main__":
    fix_paths()