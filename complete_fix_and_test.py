#!/usr/bin/env python3
"""
COMPLETE FIX & TEST - All Pass 1 issues
Fixes: Progress tracking, PDF errors, timeouts, memory
British English throughout - Lismore-sided

RUN THIS BEFORE OVERNIGHT: python complete_fix_and_test.py
"""

from pathlib import Path
import re


def fix_document_loader_comprehensive():
    """Add progress, error handling, and timeout protection"""
    
    file_path = Path('src/utils/document_loader.py')
    
    print("="*70)
    print("🔧 COMPREHENSIVE DOCUMENT LOADER FIX")
    print("="*70)
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already comprehensively fixed
    if 'PROGRESS:' in content and 'total_pages is None' in content:
        print("   ✅ Already comprehensively fixed!")
        return True
    
    # Find and replace the _load_pdf_safe method entirely
    method_start = content.find('def _load_pdf_safe(self, file_path: Path, file_size_mb: float) -> Dict:')
    
    if method_start == -1:
        print("   ❌ Could not find _load_pdf_safe method!")
        return False
    
    # Find the end of this method (next method starts with "    def ")
    method_end = content.find('\n    def ', method_start + 10)
    
    if method_end == -1:
        # Last method in class
        method_end = len(content)
    
    # The new comprehensive method
    new_method = '''def _load_pdf_safe(self, file_path: Path, file_size_mb: float) -> Dict:
        """
        Load PDF with comprehensive error handling and progress tracking
        Handles: corrupted PDFs, None errors, timeouts, large files
        
        Args:
            file_path: Path to PDF file
            file_size_mb: File size in megabytes
            
        Returns:
            Document dictionary with extracted content
        """
        
        import time
        start_time = time.time()
        
        print(f"   📄 PROGRESS: Loading {file_path.name} ({file_size_mb:.1f} MB)...", end='', flush=True)
        
        try:
            import pdfplumber
            
            # Determine extraction strategy
            if file_size_mb > 100:
                max_pages = self.MAX_PDF_PAGES
            else:
                max_pages = None
            
            text_parts = []
            total_pages = 0
            pages_extracted = 0
            
            # Open PDF with error handling
            try:
                pdf = pdfplumber.open(file_path)
            except Exception as open_error:
                print(f" ❌ FAILED (cannot open)")
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': f'[CANNOT OPEN PDF: {str(open_error)[:100]}]',
                    'preview': f'Failed to open PDF: {str(open_error)[:100]}',
                    'metadata': {
                        'file_type': 'pdf',
                        'size_mb': file_size_mb,
                        'error': f'Cannot open: {str(open_error)}'
                    }
                }
            
            try:
                # CRITICAL: Check if pages exist and is not None
                if not hasattr(pdf, 'pages') or pdf.pages is None:
                    pdf.close()
                    print(f" ❌ FAILED (no pages)")
                    return {
                        'filename': file_path.name,
                        'doc_id': self._generate_doc_id(file_path),
                        'content': '[CORRUPTED PDF: No pages found]',
                        'preview': 'PDF appears corrupted - no readable pages',
                        'metadata': {
                            'file_type': 'pdf',
                            'size_mb': file_size_mb,
                            'error': 'No pages attribute or pages is None'
                        }
                    }
                
                total_pages = len(pdf.pages)
                
                # CRITICAL: Handle None or 0 pages
                if total_pages is None or total_pages == 0:
                    pdf.close()
                    print(f" ❌ FAILED (0 pages)")
                    return {
                        'filename': file_path.name,
                        'doc_id': self._generate_doc_id(file_path),
                        'content': '[EMPTY PDF: 0 pages]',
                        'preview': 'PDF has no readable pages',
                        'metadata': {
                            'file_type': 'pdf',
                            'size_mb': file_size_mb,
                            'total_pages': 0,
                            'error': 'Empty PDF'
                        }
                    }
                
                # Calculate pages to extract
                if max_pages is not None:
                    pages_to_extract = min(total_pages, max_pages)
                else:
                    pages_to_extract = total_pages
                
                print(f" extracting {pages_to_extract}/{total_pages} pages...", end='', flush=True)
                
                # Extract text from pages with timeout protection
                for i in range(pages_to_extract):
                    # Check if taking too long (5 minutes per file max)
                    if time.time() - start_time > 300:
                        print(f" ⚠️ TIMEOUT after {pages_extracted} pages")
                        break
                    
                    try:
                        page_text = pdf.pages[i].extract_text()
                        if page_text:
                            text_parts.append(page_text)
                        pages_extracted += 1
                        
                        # Progress indicator for large files
                        if pages_extracted % 20 == 0 and file_size_mb > 50:
                            print(f" [{pages_extracted}/{pages_to_extract}]", end='', flush=True)
                        
                        # Stop if we've extracted enough chars
                        if len(''.join(text_parts)) > self.MAX_CHARS_EXTRACT:
                            break
                            
                    except Exception as page_error:
                        # Skip problematic pages but continue
                        continue
                
                pdf.close()
                
            except Exception as extract_error:
                if 'pdf' in locals():
                    try:
                        pdf.close()
                    except:
                        pass
                print(f" ❌ FAILED (extraction error)")
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': f'[PDF EXTRACTION ERROR: {str(extract_error)[:100]}]',
                    'preview': f'Error during extraction: {str(extract_error)[:100]}',
                    'metadata': {
                        'file_type': 'pdf',
                        'size_mb': file_size_mb,
                        'error': str(extract_error)[:200]
                    }
                }
            
            # Combine extracted text
            full_text = '\\n\\n'.join(text_parts)
            
            # Handle case where no text was extracted
            if not full_text or len(full_text.strip()) == 0:
                elapsed = time.time() - start_time
                print(f" ⚠️ NO TEXT ({elapsed:.1f}s)")
                return {
                    'filename': file_path.name,
                    'doc_id': self._generate_doc_id(file_path),
                    'content': '[NO TEXT EXTRACTED: PDF may be scanned images]',
                    'preview': 'No text could be extracted from PDF',
                    'metadata': {
                        'file_type': 'pdf',
                        'size_mb': file_size_mb,
                        'total_pages': total_pages,
                        'pages_extracted': pages_extracted,
                        'warning': 'No text extracted - possibly scanned images'
                    }
                }
            
            # Truncate if still too long
            if len(full_text) > self.MAX_CHARS_EXTRACT:
                full_text = full_text[:self.MAX_CHARS_EXTRACT]
                full_text += f"\\n\\n[TRUNCATED - {total_pages} pages total, extracted {pages_extracted} pages]"
            
            elapsed = time.time() - start_time
            print(f" ✅ OK ({elapsed:.1f}s, {len(full_text):,} chars)")
            
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
                    'truncated': pages_extracted < total_pages,
                    'extraction_time_seconds': round(elapsed, 1)
                }
            }
            
        except Exception as e:
            print(f" ❌ FAILED ({str(e)[:50]})")
            return {
                'filename': file_path.name,
                'doc_id': self._generate_doc_id(file_path),
                'content': f'[ERROR LOADING PDF: {str(e)[:200]}]',
                'preview': 'Error loading document',
                'metadata': {
                    'error': str(e)[:500],
                    'file_type': 'pdf',
                    'size_mb': file_size_mb
                }
            }

    '''
    
    # Replace the method
    before = content[:method_start]
    after = content[method_end:]
    new_content = before + new_method + after
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("   ✅ Document loader comprehensively fixed!")
    print("      • Progress tracking added")
    print("      • NoneType errors fixed")
    print("      • Timeout protection (5 min per file)")
    print("      • Detailed error messages")
    
    return True


def add_pass_executor_progress():
    """Add progress to Pass 1 triage"""
    
    file_path = Path('src/core/pass_executor.py')
    
    print(f"\n📝 Patching {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has progress
    if re.search(r'print\(f"\s*\[{i\+1}/{len\(documents_to_triage\)}\]', content):
        print("   ✅ Already has progress tracking!")
        return True
    
    # Find the triage loop
    old_loop = r'(\s+)for i, doc in enumerate\(documents_to_triage\):'
    match = re.search(old_loop, content)
    
    if not match:
        print("   ⚠️  Triage loop not found")
        return False
    
    indent = match.group(1)
    
    new_loop = f'''{indent}print(f"\\n{'='*70}")
{indent}print(f"TRIAGING {{len(documents_to_triage)}} DOCUMENTS")
{indent}print(f"{'='*70}")
{indent}
{indent}for i, doc in enumerate(documents_to_triage):
{indent}    print(f"\\n[{{i+1}}/{{len(documents_to_triage)}}] {{doc.get('filename', 'unknown')[:60]}}")'''
    
    content = re.sub(old_loop, new_loop, content, count=1)
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Pass executor progress added!")
    
    return True


def create_test_script():
    """Create a test script for small-scale testing"""
    
    test_script = '''#!/usr/bin/env python3
"""
TEST SCRIPT - Verify fixes before overnight run
British English throughout - Lismore-sided
"""

print("="*70)
print("🧪 TESTING PASS 1 WITH FIXES")
print("="*70)

print("\\n1. Testing with 5 documents...")
print("   Command: python main.py pass1 --limit 5")
print("\\n2. Watch for:")
print("   • Progress indicators showing each file")
print("   • No hangs (each file should complete in <2 minutes)")
print("   • Clear error messages for problem files")
print("\\n3. If test succeeds, run full analysis:")
print("   Command: python main.py pass1")
print("\\n" + "="*70)
'''
    
    test_path = Path('test_pass1.py')
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"\n📝 Created {test_path}")
    
    return True


def run_verification():
    """Verify all fixes are in place"""
    
    print("\n" + "="*70)
    print("✅ VERIFICATION")
    print("="*70)
    
    checks = []
    
    # Check document_loader
    doc_loader = Path('src/utils/document_loader.py')
    with open(doc_loader, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'PROGRESS:' in content:
        print("   ✅ Progress tracking: Enabled")
        checks.append(True)
    else:
        print("   ❌ Progress tracking: Missing")
        checks.append(False)
    
    if 'total_pages is None' in content:
        print("   ✅ NoneType fix: Applied")
        checks.append(True)
    else:
        print("   ❌ NoneType fix: Missing")
        checks.append(False)
    
    if 'time.time() - start_time > 300' in content:
        print("   ✅ Timeout protection: 5 minutes per file")
        checks.append(True)
    else:
        print("   ❌ Timeout protection: Missing")
        checks.append(False)
    
    # Check pass_executor
    pass_exec = Path('src/core/pass_executor.py')
    with open(pass_exec, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'TRIAGING' in content:
        print("   ✅ Pass executor progress: Enabled")
        checks.append(True)
    else:
        print("   ❌ Pass executor progress: Missing")
        checks.append(False)
    
    return all(checks)


if __name__ == '__main__':
    try:
        print("COMPLETE FIX & TEST WORKFLOW\n")
        
        # Apply fixes
        success1 = fix_document_loader_comprehensive()
        success2 = add_pass_executor_progress()
        success3 = create_test_script()
        
        if not all([success1, success2, success3]):
            print("\n❌ Some fixes failed!")
            exit(1)
        
        # Verify
        if not run_verification():
            print("\n❌ Verification failed!")
            exit(1)
        
        print("\n" + "="*70)
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("="*70)
        
        print("\n📋 TESTING WORKFLOW:")
        print("-" * 70)
        print("1. Test with 5 documents first:")
        print("   python main.py pass1 --limit 5")
        print()
        print("2. Watch the output:")
        print("   📄 PROGRESS: Loading document.pdf (50.2 MB)... extracting 100/500 pages... ✅ OK (45.2s)")
        print("   [1/5] filename.pdf")
        print("   [2/5] another.pdf")
        print()
        print("3. If test succeeds (completes in <10 minutes):")
        print("   python main.py pass1")
        print()
        print("4. Let it run overnight with confidence! 🌙")
        print("-" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()