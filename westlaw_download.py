#!/usr/bin/env python3
"""
Organise Westlaw downloads into proper directory structure
Run this from your project root where the .zip files are located
"""

import zipfile
import shutil
from pathlib import Path
import re

def organise_westlaw_downloads():
    """
    Unzip and organise Westlaw downloads into appropriate directories
    """
    
    # Mapping of Westlaw files to their target directories
    westlaw_mapping = {
        "Westlaw UK - 76 full text items for Redfern and Hu.zip": "legal_resources/sources/arbitration/Redfern_Hunter/",
        "Westlaw UK - 17 full text items for A Practical Gu.zip": "legal_resources/sources/arbitration/Practical_Guide/",
        "Westlaw UK - 256 full text items for Handbook of I.zip": "legal_resources/sources/arbitration/Handbook_Intl_Arb/",
        "Westlaw UK - 279 full text items for White Book 20.zip": "legal_resources/sources/civil_procedure/White_Book_2025/",
        "Westlaw UK - 487 full text items for Bullen And Le.zip": "legal_resources/sources/pleadings/Bullen_Leake/"
    }
    
    print("🔧 WESTLAW DOCUMENT ORGANISATION")
    print("=" * 60)
    
    for zip_file, target_dir in westlaw_mapping.items():
        zip_path = Path(zip_file)
        
        if not zip_path.exists():
            print(f"⚠️  Not found: {zip_file}")
            continue
            
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📦 Processing: {zip_file}")
        print(f"   Target: {target_dir}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to target directory
                zip_ref.extractall(target_path)
                
                # Count PDFs extracted
                pdf_count = len(list(target_path.glob("**/*.pdf")))
                print(f"   ✅ Extracted {pdf_count} PDFs")
                
                # Rename files for better organisation (optional)
                rename_pdfs_for_clarity(target_path)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Westlaw organisation complete!")
    print("\nNext steps:")
    print("1. Run text extraction on legal_resources/sources/")
    print("2. Create rule cards from extracted text")
    print("3. Run Phase 0A analysis")

def rename_pdfs_for_clarity(directory: Path):
    """
    Rename PDFs to remove Westlaw clutter and add structure
    Example: "Document_123456789.pdf" -> "Redfern_Ch5_Para123.pdf"
    """
    for pdf_file in directory.glob("**/*.pdf"):
        original_name = pdf_file.name
        
        # Skip if already renamed
        if "_WL" in original_name:
            continue
            
        # Extract Westlaw ID if present (usually at end)
        westlaw_id = ""
        id_match = re.search(r'_(\d{6,})\.pdf$', original_name)
        if id_match:
            westlaw_id = f"_WL{id_match.group(1)}"
        
        # Clean the filename
        clean_name = original_name
        clean_name = re.sub(r'_\d{6,}\.pdf$', '.pdf', clean_name)
        clean_name = clean_name.replace('_', ' ')
        
        # Reformat based on parent directory
        parent = pdf_file.parent.name
        if "Redfern" in parent:
            clean_name = f"Redfern_{clean_name}"
        elif "White" in parent:
            clean_name = f"WhiteBook_{clean_name}"
        elif "Bullen" in parent:
            clean_name = f"BullenLeake_{clean_name}"
        elif "Handbook" in parent:
            clean_name = f"HandbookArb_{clean_name}"
        elif "Practical" in parent:
            clean_name = f"PracticalGuide_{clean_name}"
        
        # Add Westlaw ID back
        clean_name = clean_name.replace('.pdf', f'{westlaw_id}.pdf')
        clean_name = clean_name.replace(' ', '_')
        
        # Rename
        new_path = pdf_file.parent / clean_name
        if new_path != pdf_file:
            pdf_file.rename(new_path)

def verify_structure():
    """
    Verify the complete directory structure is ready
    """
    print("\n📁 DIRECTORY VERIFICATION")
    print("=" * 60)
    
    required_dirs = [
        "legal_resources/sources/arbitration",
        "legal_resources/sources/civil_procedure",
        "legal_resources/sources/pleadings",
        "legal_resources/processed/text",
        "legal_resources/rule_cards",
        "case_context/raw",
        "documents/raw",
        "documents/processed/text"
    ]
    
    all_ready = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            # Count contents
            pdf_count = len(list(path.glob("*.pdf")))
            txt_count = len(list(path.glob("*.txt")))
            
            if pdf_count > 0:
                print(f"✅ {dir_path}: {pdf_count} PDFs")
            elif txt_count > 0:
                print(f"✅ {dir_path}: {txt_count} text files")
            else:
                print(f"📁 {dir_path}: Ready (empty)")
        else:
            print(f"❌ {dir_path}: Missing")
            all_ready = False
    
    print("=" * 60)
    return all_ready

if __name__ == "__main__":
    # Step 1: Organise Westlaw downloads
    organise_westlaw_downloads()
    
    # Step 2: Verify structure
    if verify_structure():
        print("✅ All directories ready for processing!")
    else:
        print("⚠️  Some directories missing - run setup script first")