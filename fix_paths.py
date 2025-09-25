#!/usr/bin/env python3
"""
Fix Phase 0A prompt to be pure knowledge extraction
No case context, just legal memory building
Save as: fix_phase_0a_prompt.py
"""

from pathlib import Path
import re

def fix_document_processor_prompt():
    """Fix the Phase 0A prompt in document_processor.py"""
    
    doc_proc = Path('src/interface/document_processor.py')
    if not doc_proc.exists():
        print("❌ document_processor.py not found")
        return False
    
    content = doc_proc.read_text(encoding='utf-8')
    
    # Find and replace the Phase 0A prompt section
    old_prompt_pattern = r'if phase == "0A":[^}]+?Focus on what will destroy Process Holdings[^"]*"'
    
    new_prompt = '''if phase == "0A":
            return """
PHASE 0A: PURE LEGAL KNOWLEDGE EXTRACTION AND MEMORY BUILDING

You are building a comprehensive legal knowledge base from these documents.
This is NOT about any specific case - this is about learning and memorising legal principles.

EXTRACTION OBJECTIVES:

1. LEGAL DOCTRINES
   - Extract every legal principle mentioned
   - Note the full doctrine name and elements
   - Understand when and how each applies
   - Store exceptions and limitations

2. CASE PRECEDENTS
   - Identify all case citations
   - Extract the legal principle from each case
   - Note the ratio decidendi (binding element)
   - Remember distinguishing factors

3. PROCEDURAL RULES
   - Extract all procedural requirements
   - Time limits and deadlines
   - Notice requirements
   - Filing procedures
   - Jurisdictional rules

4. STATUTORY PROVISIONS
   - All legislation references
   - Specific section numbers
   - Elements of statutory claims
   - Defences available

5. LEGAL CONCEPTS
   - Burden of proof variations
   - Standards of evidence
   - Presumptions and inferences
   - Equitable principles

MEMORY FORMATION INSTRUCTIONS:
- Create a structured mental map of all legal concepts
- Build connections between related doctrines
- Form hierarchies of principles (general → specific)
- Identify doctrine families and variations
- Remember practical applications

OUTPUT STRUCTURE:
Provide a comprehensive synthesis of ALL legal knowledge found, organised by:
- Doctrine categories
- Procedural frameworks  
- Statutory schemes
- Case law principles
- Strategic applications

This is pure knowledge building - no case analysis, just legal learning.
"""'''
    
    # Replace the prompt
    content = re.sub(
        r'if phase == "0A":.*?""".*?"""',
        new_prompt,
        content,
        flags=re.DOTALL
    )
    
    # Also fix any other mentions of Process Holdings in Phase 0A
    content = content.replace(
        'Extract and weaponise EVERYTHING:',
        'Extract and memorise EVERYTHING:'
    )
    content = content.replace(
        'Focus on what will destroy Process Holdings',
        'Focus on building comprehensive legal knowledge'
    )
    content = content.replace(
        'YOU ARE PROCESSING THE COMPLETE LEGAL FRAMEWORK FOR LISMORE vs PROCESS HOLDINGS',
        'YOU ARE BUILDING A COMPLETE LEGAL KNOWLEDGE BASE'
    )
    
    doc_proc.write_text(content, encoding='utf-8')
    print("✅ Fixed Phase 0A prompt to pure knowledge extraction")
    return True

def fix_phase_prompts_module():
    """Fix the phase_prompts.py module if it exists"""
    
    prompts_file = Path('src/prompts/phase_prompts.py')
    if not prompts_file.exists():
        print("⚠️  phase_prompts.py not found - may be using inline prompts")
        return False
    
    content = prompts_file.read_text(encoding='utf-8')
    
    # Check if there's a Phase 0A prompt
    if '"0A"' in content or "'0A'" in content:
        # Replace any case-specific content with pure knowledge extraction
        content = content.replace('Process Holdings', '[DEFENDANT]')
        content = content.replace('Lismore', '[PLAINTIFF]')
        content = content.replace('destroy', 'analyse')
        content = content.replace('weaponise', 'extract')
        
        prompts_file.write_text(content, encoding='utf-8')
        print("✅ Cleaned phase_prompts.py")
    
    return True

def verify_fix():
    """Verify the fix worked"""
    doc_proc = Path('src/interface/document_processor.py')
    content = doc_proc.read_text(encoding='utf-8')
    
    bad_phrases = [
        'destroy Process Holdings',
        'LISMORE vs PROCESS',
        'weaponise'
    ]
    
    issues = []
    for phrase in bad_phrases:
        if phrase in content:
            # Check if it's in Phase 0A section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if phrase in line:
                    # Look back to see if we're in Phase 0A
                    context = '\n'.join(lines[max(0, i-10):i+1])
                    if '0A' in context:
                        issues.append(f"Found '{phrase}' in Phase 0A context")
    
    if issues:
        print("\n⚠️  Some case-specific content still in Phase 0A:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Phase 0A is now pure knowledge extraction!")
    
    return len(issues) == 0

def main():
    print("="*60)
    print("🔧 FIXING PHASE 0A TO PURE KNOWLEDGE EXTRACTION")
    print("="*60)
    
    print("\nPhase 0A should be about building legal knowledge,")
    print("NOT about any specific case or parties.")
    
    print("\n1️⃣ Fixing document_processor.py...")
    fix_document_processor_prompt()
    
    print("\n2️⃣ Checking phase_prompts.py...")
    fix_phase_prompts_module()
    
    print("\n3️⃣ Verifying fixes...")
    success = verify_fix()
    
    print("\n" + "="*60)
    if success:
        print("✅ PHASE 0A FIXED!")
        print("="*60)
        print("\nPhase 0A will now:")
        print("• Extract pure legal knowledge")
        print("• Build comprehensive doctrine library")
        print("• Create procedural framework")
        print("• Memorise case precedents")
        print("• Form legal concept networks")
        print("\nNO case-specific analysis until Phase 0B!")
    else:
        print("⚠️  Some issues remain - check manually")
    
    print("\n🚀 Re-run Phase 0A for pure knowledge extraction:")
    print("   python -m src.main --phase 0A")

if __name__ == "__main__":
    main()