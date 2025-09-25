#!/usr/bin/env python3
"""
Final verification before running Phase 0A
Ensures everything is perfectly configured
"""

import json
from pathlib import Path
from datetime import datetime

def verify_phase_0a_ready():
    """Complete verification for Phase 0A readiness"""
    
    print("\n" + "="*70)
    print("🎯 LISMORE LITIGATION SYSTEM - PHASE 0A READINESS CHECK")
    print("="*70)
    
    ready = True
    issues = []
    
    # 1. Check Westlaw PDFs
    print("\n📚 WESTLAW LIBRARY STATUS:")
    pdf_count = len(list(Path("legal_resources/sources").rglob("*.pdf")))
    print(f"  Source PDFs: {pdf_count}")
    
    # 2. Check extracted text
    text_count = len(list(Path("legal_resources/processed/text").glob("*.txt")))
    print(f"  Extracted texts: {text_count}")
    
    if text_count == 0:
        ready = False
        issues.append("No text files extracted")
    
    # 3. Check rule cards
    print("\n⚔️ RULE CARDS STATUS:")
    rule_dir = Path("legal_resources/rule_cards")
    total_weapons = 0
    nuclear_weapons = 0
    
    for rule_file in rule_dir.glob("*.json"):
        with open(rule_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
            total_weapons += len(cards)
            
            # Count nuclear weapons
            for card in cards:
                if card.get('devastation_rating') == 'NUCLEAR':
                    nuclear_weapons += 1
            
            print(f"  {rule_file.stem}: {len(cards)} weapons")
    
    if total_weapons == 0:
        ready = False
        issues.append("No rule cards generated")
    
    print(f"\n  TOTAL WEAPONS: {total_weapons}")
    print(f"  NUCLEAR WEAPONS: {nuclear_weapons}")
    
    # 4. Check playbook
    playbook_path = Path("legal_resources/playbooks/phase_0a_arsenal.md")
    if playbook_path.exists():
        size_kb = playbook_path.stat().st_size / 1024
        print(f"\n📋 PLAYBOOK: ✅ Generated ({size_kb:.1f} KB)")
    else:
        ready = False
        issues.append("Playbook not generated")
    
    # 5. Check main.py exists
    main_py = Path("main.py")
    if main_py.exists():
        print(f"\n🐍 MAIN SCRIPT: ✅ Found")
    else:
        ready = False
        issues.append("main.py not found")
    
    # 6. Check required directories
    print("\n📁 DIRECTORY STRUCTURE:")
    required_dirs = [
        "legal_resources/sources",
        "legal_resources/processed/text",
        "legal_resources/rule_cards",
        "legal_resources/playbooks",
        "outputs",
        "knowledge_base"
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path}")
            ready = False
            issues.append(f"Missing directory: {dir_path}")
    
    # 7. Display sample weapons
    print("\n💀 SAMPLE NUCLEAR WEAPONS:")
    sample_count = 0
    for rule_file in rule_dir.glob("*.json"):
        with open(rule_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
            for card in cards:
                if card.get('devastation_rating') == 'NUCLEAR' and sample_count < 3:
                    print(f"  • {card.get('doctrine', 'Unknown')}")
                    if card.get('criminal_crossover'):
                        print(f"    ⚠️ Criminal referral possible")
                    sample_count += 1
    
    # Final verdict
    print("\n" + "="*70)
    if ready:
        print("✅ SYSTEM READY FOR PHASE 0A!")
        print("\n🚀 LAUNCH COMMAND:")
        print("   python main.py --phase 0A")
        print("\n📊 EXPECTED OUTCOMES:")
        print("  • Legal framework weaponisation")
        print("  • Offensive doctrine catalogue")
        print("  • Procedural attack strategies")
        print("  • Criminal crossover identification")
        print("  • Settlement leverage points")
        print("  • Arbitrator psychology insights")
        
        print("\n⚠️ COST ESTIMATE:")
        print("  Phase 0A typically uses ~3-5 Claude API calls")
        print("  Estimated cost: £0.50 - £1.00")
        
        print("\n📝 AFTER PHASE 0A:")
        print("  1. Review outputs/phase_reports/0A_*.txt")
        print("  2. Add skeleton arguments to case_context/ for Phase 0B")
        print("  3. Add Process Holdings docs to documents/ for Phases 1-7")
    else:
        print("❌ SYSTEM NOT READY")
        print("\nISSUES TO FIX:")
        for issue in issues:
            print(f"  • {issue}")
    
    print("="*70)
    
    return ready

def show_next_steps():
    """Display next steps after Phase 0A"""
    print("\n📍 COMPLETE PIPELINE OVERVIEW:")
    print("="*70)
    
    phases = [
        ("0A", "Legal Framework Weaponisation", "✅ READY", "legal_resources/"),
        ("0B", "Case Context Intelligence", "⏳ Awaiting skeleton arguments", "case_context/"),
        ("1", "Document Landscape Mapping", "⏳ Awaiting disclosure", "documents/"),
        ("2", "Temporal Forensic Analysis", "⏳ Awaiting disclosure", "documents/"),
        ("3", "Contradiction Mining", "⏳ Awaiting disclosure", "documents/"),
        ("4", "Narrative Warfare", "⏳ Awaiting disclosure", "documents/"),
        ("5", "Legal Arsenal Deployment", "⏳ Awaiting disclosure", "documents/"),
        ("6", "Endgame Orchestration", "⏳ Awaiting disclosure", "documents/"),
        ("7", "AI Breakthrough Analysis", "⏳ Awaiting disclosure", "documents/")
    ]
    
    for phase, description, status, directory in phases:
        print(f"  Phase {phase}: {description}")
        print(f"    Status: {status}")
        print(f"    Source: {directory}")
        print()
    
    print("="*70)

if __name__ == "__main__":
    # Run verification
    ready = verify_phase_0a_ready()
    
    if ready:
        show_next_steps()
        
        print("\n🎯 IMMEDIATE ACTION:")
        print("  python main.py --phase 0A")
        print("\nThis will:")
        print("  1. Load your 48 rule cards")
        print("  2. Process with Claude's Phase 0A prompts")
        print("  3. Generate weaponised legal strategies")
        print("  4. Output comprehensive attack framework")
        print("  5. Save to outputs/phase_reports/")
    else:
        print("\n⚠️ Fix issues above before running Phase 0A")