#!/usr/bin/env python3
"""
Robust PDF text extractor with multiple fallback methods
Works with Westlaw PDFs which can be tricky
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Try multiple PDF libraries
libraries_available = []

try:
    import PyPDF2
    libraries_available.append('PyPDF2')
except ImportError:
    print("⚠️ PyPDF2 not installed")

try:
    import pdfplumber
    libraries_available.append('pdfplumber')
except ImportError:
    print("⚠️ pdfplumber not installed")

try:
    import fitz  # PyMuPDF
    libraries_available.append('PyMuPDF')
except ImportError:
    print("⚠️ PyMuPDF not installed")

class RobustPDFExtractor:
    def __init__(self):
        self.source_dir = Path("legal_resources/sources")
        self.output_dir = Path("legal_resources/processed/text")
        self.metadata_dir = Path("legal_resources/processed/metadata")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'methods': {}
        }
        
        print(f"📚 PDF EXTRACTION SYSTEM")
        print(f"Available libraries: {', '.join(libraries_available)}")
        print("=" * 60)
    
    def extract_all(self):
        """Extract text from all PDFs"""
        pdf_files = list(self.source_dir.rglob("*.pdf"))
        self.stats['total'] = len(pdf_files)
        
        print(f"Found {len(pdf_files)} PDFs to process")
        print("=" * 60)
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            # Progress indicator
            if idx % 10 == 0:
                print(f"Progress: {idx}/{len(pdf_files)} ({idx*100//len(pdf_files)}%)")
            
            self.process_pdf(pdf_path)
        
        self.print_summary()
    
    def process_pdf(self, pdf_path: Path) -> bool:
        """Process a single PDF with multiple fallback methods"""
        # Generate output filename
        rel_path = pdf_path.relative_to(self.source_dir)
        output_name = str(rel_path).replace(os.sep, '_').replace('.pdf', '')
        text_file = self.output_dir / f"{output_name}.txt"
        
        # Skip if already processed
        if text_file.exists():
            file_size = text_file.stat().st_size
            if file_size > 100:  # Has meaningful content
                print(f"✓ Already processed: {pdf_path.name}")
                self.stats['success'] += 1
                return True
        
        print(f"Processing: {pdf_path.name}")
        
        # Try extraction methods in order
        text = ""
        method_used = None
        
        # Method 1: PyMuPDF (most reliable for complex PDFs)
        if 'PyMuPDF' in libraries_available and not text:
            try:
                text = self.extract_with_pymupdf(pdf_path)
                if text and len(text) > 100:
                    method_used = 'PyMuPDF'
            except Exception as e:
                print(f"  PyMuPDF failed: {str(e)[:50]}")
        
        # Method 2: pdfplumber (good for tables)
        if 'pdfplumber' in libraries_available and not text:
            try:
                text = self.extract_with_pdfplumber(pdf_path)
                if text and len(text) > 100:
                    method_used = 'pdfplumber'
            except Exception as e:
                print(f"  pdfplumber failed: {str(e)[:50]}")
        
        # Method 3: PyPDF2 (fallback)
        if 'PyPDF2' in libraries_available and not text:
            try:
                text = self.extract_with_pypdf2(pdf_path)
                if text and len(text) > 100:
                    method_used = 'PyPDF2'
            except Exception as e:
                print(f"  PyPDF2 failed: {str(e)[:50]}")
        
        # Method 4: Command line pdftotext (if available)
        if not text:
            try:
                text = self.extract_with_pdftotext(pdf_path)
                if text and len(text) > 100:
                    method_used = 'pdftotext'
            except Exception:
                pass
        
        # Save if we got text
        if text and len(text) > 100:
            # Save text
            with open(text_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(text)
            
            # Save metadata
            metadata = {
                'source_pdf': pdf_path.name,
                'source_path': str(pdf_path),
                'extraction_date': datetime.now().isoformat(),
                'extraction_method': method_used,
                'text_length': len(text),
                'category': self.get_category(pdf_path),
                'treatise': self.get_treatise(pdf_path)
            }
            
            metadata_file = self.metadata_dir / f"{output_name}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"  ✅ Success ({method_used}): {len(text)} chars")
            self.stats['success'] += 1
            self.stats['methods'][method_used] = self.stats['methods'].get(method_used, 0) + 1
            return True
        else:
            print(f"  ❌ Failed: No text extracted")
            self.stats['failed'] += 1
            
            # Save failure record
            failure_file = self.output_dir / f"{output_name}.failed"
            with open(failure_file, 'w') as f:
                f.write(f"Failed to extract: {pdf_path}\n")
            
            return False
    
    def extract_with_pymupdf(self, pdf_path: Path) -> str:
        """Extract using PyMuPDF"""
        import fitz
        doc = fitz.open(str(pdf_path))
        text = []
        for page in doc:
            text.append(page.get_text())
        doc.close()
        return '\n'.join(text)
    
    def extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract using pdfplumber"""
        import pdfplumber
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)
    
    def extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract using PyPDF2"""
        import PyPDF2
        text = []
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)
    
    def extract_with_pdftotext(self, pdf_path: Path) -> str:
        """Extract using command line pdftotext"""
        try:
            result = subprocess.run(
                ['pdftotext', str(pdf_path), '-'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        return ""
    
    def get_category(self, pdf_path: Path) -> str:
        """Get category from path"""
        parts = pdf_path.parts
        if 'arbitration' in str(pdf_path).lower():
            return 'arbitration'
        elif 'civil_procedure' in str(pdf_path).lower():
            return 'civil_procedure'
        elif 'pleadings' in str(pdf_path).lower():
            return 'pleadings'
        return 'unknown'
    
    def get_treatise(self, pdf_path: Path) -> str:
        """Get treatise name from path"""
        parts = pdf_path.parts
        for part in parts:
            if 'Redfern' in part:
                return 'Redfern_Hunter'
            elif 'White' in part:
                return 'White_Book'
            elif 'Bullen' in part:
                return 'Bullen_Leake'
            elif 'Handbook' in part:
                return 'Handbook_Intl_Arb'
            elif 'Practical' in part:
                return 'Practical_Guide'
        return 'unknown'
    
    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print(f"Total PDFs: {self.stats['total']}")
        print(f"Successfully extracted: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success rate: {self.stats['success']*100//max(1,self.stats['total'])}%")
        
        if self.stats['methods']:
            print("\nMethods used:")
            for method, count in self.stats['methods'].items():
                print(f"  {method}: {count} files")
        
        print("=" * 60)

def install_libraries():
    """Offer to install missing libraries"""
    print("\n📦 LIBRARY INSTALLATION")
    print("=" * 60)
    
    if not libraries_available:
        print("No PDF libraries installed. Installing required libraries...")
        print("\nRun these commands:")
        print("pip install PyPDF2")
        print("pip install pdfplumber")
        print("pip install PyMuPDF")
        print("\nOr all at once:")
        print("pip install PyPDF2 pdfplumber PyMuPDF")
        
        response = input("\nInstall now? (y/n): ")
        if response.lower() == 'y':
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyPDF2', 'pdfplumber', 'PyMuPDF'])
            print("\n✅ Libraries installed! Please restart the script.")
            sys.exit(0)
    elif len(libraries_available) < 3:
        print(f"Some libraries missing. For best results, install all three.")
        print("pip install PyPDF2 pdfplumber PyMuPDF")

if __name__ == "__main__":
    # Check libraries
    if not libraries_available:
        install_libraries()
        sys.exit(1)
    
    # Run extraction
    extractor = RobustPDFExtractor()
    extractor.extract_all()
    
    # Check if successful
    text_files = list(Path("legal_resources/processed/text").glob("*.txt"))
    if text_files:
        print(f"\n✅ Extraction complete! {len(text_files)} text files created")
        print("Next step: python rule_card.py")
    else:
        print("\n⚠️ No text files created. Check error messages above.")
        install_libraries()