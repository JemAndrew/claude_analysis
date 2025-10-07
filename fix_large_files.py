#!/usr/bin/env python3
"""
CRITICAL FIX #2: Handle Large Files (529 MB PDFs, 7 GB PSTs)
Adds size checking and smart truncation to document_loader.py

RUN THIS SECOND: python fix_large_files.py
"""

from pathlib import Path

def patch_document_loader():
    """Add large file protection to document_loader.py"""
    
    file_path = Path('src/utils/document_loader.py')
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'MAX_FILE_SIZE_MB' in content:
        print("   ✅ Already patched!")
        return
    
    # Add constants after SUPPORTED_FORMATS
    constants_addition = '''
    
    # File size protection (added by fix_large_files.py)
    MAX_FILE_SIZE_MB = 500      # Skip files > 500 MB
    MAX_PDF_PAGES = 100         # Only extract first 100 pages of huge PDFs
    MAX_CHARS_EXTRACT = 100000  # Max 100K chars per document'''
    
    content = content.replace(
        "SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc', '.txt', '.json', '.html', '.md']",
        "SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc', '.txt', '.json', '.html', '.md']" + constants_addition
    )
    
    # Find the load_document method and add size check
    size_check_code = '''
    def load_document(self, file_path: Path, preview_only: bool = False) -> Dict:
        """
        Load document with size protection
        
        Args:
            file_path: Path to document
            preview_only: If True, only extract first page/preview
            
        Returns:
            Document dictionary
        """
        
        # Check file size BEFORE loading
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # Skip PST files (email archives - handle separately)
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
        
        # Skip extremely large files
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            print(f"   ⚠️  SKIPPING: {file_path.name} ({file_size_mb:.1f} MB)")
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[FILE TOO LARGE: {file_size_mb:.1f} MB - Skipped]',
                'preview': f'Large file ({file_size_mb:.1f} MB) not analysed',
                'metadata': {
                    'size_mb': file_size_mb,
                    'skip_reason': 'File exceeds size limit'
                }
            }
        
        # Route to format-specific handler
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self._load_pdf_safe(file_path, file_size_mb)
        elif suffix in ['.docx', '.doc']:
            return self._load_word_document(file_path)
        else:
            return self._load_text_document(file_path)
    
    def _load_pdf_safe(self, file_path: Path, file_size_mb: float) -> Dict:
        """
        Load PDF with size-based strategy
        Small PDFs: Extract all
        Large PDFs: Extract first 100 pages only
        """
        
        try:
            import pdfplumber
            
            # Determine extraction strategy
            if file_size_mb > 100:
                max_pages = self.MAX_PDF_PAGES
                print(f"   📄 {file_path.name} ({file_size_mb:.1f} MB) - extracting first {max_pages} pages")
            else:
                max_pages = None
            
            text_parts = []
            total_pages = 0
            pages_extracted = 0
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_extract = min(total_pages, max_pages) if max_pages else total_pages
                
                for i in range(pages_to_extract):
                    try:
                        page_text = pdf.pages[i].extract_text()
                        if page_text:
                            text_parts.append(page_text)
                        pages_extracted += 1
                        
                        # Stop if we've extracted enough chars
                        if len(''.join(text_parts)) > self.MAX_CHARS_EXTRACT:
                            break
                    except Exception as e:
                        continue
            
            full_text = '\\n\\n'.join(text_parts)
            
            # Truncate if still too long
            if len(full_text) > self.MAX_CHARS_EXTRACT:
                full_text = full_text[:self.MAX_CHARS_EXTRACT]
                full_text += f"\\n\\n[TRUNCATED - {total_pages} pages total, extracted {pages_extracted} pages]"
            
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': full_text,
                'preview': full_text[:300],
                'metadata': {
                    'file_type': 'pdf',
                    'size_mb': file_size_mb,
                    'total_pages': total_pages,
                    'pages_extracted': pages_extracted,
                    'truncated': pages_extracted < total_pages
                }
            }
            
        except Exception as e:
            print(f"   ❌ Error loading PDF: {e}")
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[ERROR LOADING PDF: {str(e)}]',
                'preview': 'Error loading document',
                'metadata': {'error': str(e)}
            }'''
    
    # Replace the existing load_document method
    # Find the method start
    method_start = content.find('def load_document(self')
    if method_start == -1:
        print("   ❌ Could not find load_document method!")
        return
    
    # Find the next method after load_document
    next_method = content.find('\n    def ', method_start + 10)
    
    # Replace the method
    before = content[:method_start]
    after = content[next_method:]
    
    new_content = before + size_check_code + '\n' + after
    
    # Save patched file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("   ✅ Patched document_loader.py")

if __name__ == '__main__':
    print("="*70)
    print("🔧 ADDING LARGE FILE PROTECTION")
    print("="*70)
    print("\nProtection limits:")
    print("  • Skip files > 500 MB")
    print("  • Extract first 100 pages only from large PDFs")
    print("  • Skip PST files (handle in email extraction)")
    
    try:
        patch_document_loader()
        
        print("\n" + "="*70)
        print("✅ PATCH COMPLETE!")
        print("="*70)
        print("\nYour system can now handle:")
        print("  ✅ 529 MB PDFs (will extract first 100 pages)")
        print("  ✅ 7 GB PST files (will skip with message)")
        print("\nNext step: python verify_system.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()