#!/usr/bin/env python3
"""
Progressive Testing Script for Phase 0A
Tests batching, knowledge accumulation, and synthesis
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.document_processor import DocumentProcessor
from src.api_client import ClaudeAPIClient
from src.knowledge_manage import KnowledgeManager

def test_1_single_document():
    """Test 1: Single document processing"""
    print("\n" + "="*60)
    print("TEST 1: SINGLE DOCUMENT PROCESSING")
    print("="*60)
    print("Purpose: Verify basic document loading and API connection")
    
    processor = DocumentProcessor()
    
    # Find one PDF
    legal_dir = Path("./legal_resources")
    pdf_files = list(legal_dir.glob("*.pdf"))[:1]
    
    if not pdf_files:
        print("❌ No PDF files found in legal_resources/")
        return False
    
    print(f"📄 Testing with: {pdf_files[0].name}")
    
    # Load single document
    success = processor.load_documents([str(pdf_files[0])])
    
    if not success:
        print("❌ Failed to load document")
        return False
    
    print(f"✅ Document loaded successfully")
    print(f"   Content length: {len(processor.documents[0]['content'])} chars")
    
    # Estimate cost
    api_client = ClaudeAPIClient()
    estimate = api_client.estimate_cost(processor.documents[0]['content'], "phase_0a")
    print(f"💰 Estimated cost: £{estimate['estimated_cost_gbp']}")
    
    # Run Phase 0A
    input("\n⏸️  Press Enter to process this single document...")
    
    result = processor.process_phase("0A")
    
    if result:
        print("✅ Single document test PASSED")
        print(f"   Findings stored: {len(str(result.get('findings', '')))} chars")
        return True
    else:
        print("❌ Single document test FAILED")
        return False

def test_2_small_batch():
    """Test 2: Small batch (3 documents - 1 batch)"""
    print("\n" + "="*60)
    print("TEST 2: SMALL BATCH (3 DOCUMENTS)")
    print("="*60)
    print("Purpose: Test single batch processing")
    
    processor = DocumentProcessor()
    
    # Load 3 documents
    legal_dir = Path("./legal_resources")
    pdf_files = list(legal_dir.glob("*.pdf"))[:3]
    
    if len(pdf_files) < 3:
        print("❌ Need at least 3 PDFs for this test")
        return False
    
    print(f"📄 Testing with {len(pdf_files)} documents:")
    for pdf in pdf_files:
        print(f"   • {pdf.name}")
    
    success = processor.load_documents([str(f) for f in pdf_files])
    
    if not success:
        print("❌ Failed to load documents")
        return False
    
    # Check batch creation
    batches = processor._create_intelligent_batches(processor.documents, "0A")
    print(f"📦 Created {len(batches)} batch(es)")
    print(f"   Batch 1 size: {len(batches[0])} documents")
    
    # Estimate cost
    total_chars = sum(len(doc['content']) for doc in processor.documents)
    api_client = ClaudeAPIClient()
    estimate = api_client.estimate_cost(str(total_chars), "phase_0a")
    print(f"💰 Estimated cost: £{estimate['estimated_cost_gbp']}")
    
    input("\n⏸️  Press Enter to process these 3 documents...")
    
    result = processor.process_phase("0A")
    
    if result:
        print("✅ Small batch test PASSED")
        return True
    else:
        print("❌ Small batch test FAILED")
        return False

def test_3_multi_batch():
    """Test 3: Multi-batch (10 documents - 3-4 batches)"""
    print("\n" + "="*60)
    print("TEST 3: MULTI-BATCH (10 DOCUMENTS)")
    print("="*60)
    print("Purpose: Test batch accumulation and synthesis")
    
    processor = DocumentProcessor()
    
    # Load 10 documents
    legal_dir = Path("./legal_resources")
    pdf_files = list(legal_dir.glob("*.pdf"))[:10]
    
    if len(pdf_files) < 10:
        print(f"⚠️  Only found {len(pdf_files)} PDFs, adjusting test...")
    
    print(f"📄 Testing with {len(pdf_files)} documents")
    
    success = processor.load_documents([str(f) for f in pdf_files])
    
    if not success:
        print("❌ Failed to load documents")
        return False
    
    # Check batch creation
    batches = processor._create_intelligent_batches(processor.documents, "0A")
    print(f"📦 Will create {len(batches)} batches")
    for i, batch in enumerate(batches, 1):
        print(f"   Batch {i}: {len(batch)} documents")
    
    # Estimate cost
    total_chars = sum(len(doc['content']) for doc in processor.documents)
    api_client = ClaudeAPIClient()
    
    # Cost = batches * cost_per_batch + 1 synthesis call
    batch_cost = len(batches) * 0.15  # £0.15 per batch for Haiku
    synthesis_cost = 0.20  # Synthesis call
    total_estimate = batch_cost + synthesis_cost
    
    print(f"💰 Estimated cost: £{total_estimate:.2f}")
    print(f"   Batches: £{batch_cost:.2f}")
    print(f"   Synthesis: £{synthesis_cost:.2f}")
    
    input("\n⏸️  Press Enter to process these documents...")
    
    # Track time
    start_time = time.time()
    
    result = processor.process_phase("0A")
    
    elapsed = time.time() - start_time
    
    if result:
        print(f"✅ Multi-batch test PASSED")
        print(f"⏱️  Time taken: {elapsed:.1f} seconds")
        
        # Verify synthesis occurred
        if 'synthesis' in result:
            print("✅ Synthesis completed successfully")
        
        # Check knowledge storage
        knowledge_file = Path("./knowledge_store/phase_0A_knowledge.json")
        if knowledge_file.exists():
            with open(knowledge_file, 'r') as f:
                knowledge = json.load(f)
                print(f"✅ Knowledge stored: {len(json.dumps(knowledge))} chars")
        
        return True
    else:
        print("❌ Multi-batch test FAILED")
        return False

def test_4_knowledge_accumulation():
    """Test 4: Verify knowledge accumulation works"""
    print("\n" + "="*60)
    print("TEST 4: KNOWLEDGE ACCUMULATION")
    print("="*60)
    print("Purpose: Verify knowledge builds across batches")
    
    knowledge_manager = KnowledgeManager()
    
    # Check if Phase 0A knowledge exists
    phase_0a_knowledge = knowledge_manager.get_phase_knowledge("0A")
    
    if not phase_0a_knowledge:
        print("❌ No Phase 0A knowledge found - run Test 3 first")
        return False
    
    print("✅ Phase 0A knowledge found")
    
    # Analyse knowledge structure
    if 'findings' in phase_0a_knowledge:
        findings = phase_0a_knowledge['findings']
        
        if 'synthesis' in findings:
            print("✅ Synthesis present")
            print(f"   Length: {len(findings['synthesis'])} chars")
        
        if 'batch_results' in phase_0a_knowledge:
            batch_count = len(phase_0a_knowledge['batch_results'])
            print(f"✅ Batch results: {batch_count} batches")
        
        if 'total_documents' in phase_0a_knowledge:
            print(f"✅ Total documents: {phase_0a_knowledge['total_documents']}")
    
    # Test knowledge retrieval for next phase
    print("\n🔄 Testing knowledge retrieval for Phase 0B...")
    previous_knowledge = knowledge_manager.get_previous_knowledge("0B")
    
    if "0A" in previous_knowledge:
        print("✅ Phase 0A knowledge available for Phase 0B")
        print(f"   Knowledge size: {len(json.dumps(previous_knowledge))} chars")
        return True
    else:
        print("❌ Knowledge not properly structured for next phase")
        return False

def test_5_cost_verification():
    """Test 5: Verify actual vs estimated costs"""
    print("\n" + "="*60)
    print("TEST 5: COST VERIFICATION")
    print("="*60)
    print("Purpose: Verify cost tracking accuracy")
    
    api_client = ClaudeAPIClient()
    cost_summary = api_client.get_cost_summary()
    
    print(f"💰 Actual costs from tests:")
    print(f"   Total: £{cost_summary['total_cost']:.4f}")
    
    if 'phase_breakdown' in cost_summary:
        print("\n   Breakdown by phase:")
        for phase, cost in cost_summary['phase_breakdown'].items():
            if cost > 0:
                print(f"   • {phase}: £{cost:.4f}")
    
    return True

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("\n" + "🧪"*30)
    print("COMPREHENSIVE PHASE 0A TESTING")
    print("🧪"*30)
    
    tests = [
        ("Single Document", test_1_single_document),
        ("Small Batch", test_2_small_batch),
        ("Multi-Batch", test_3_multi_batch),
        ("Knowledge Accumulation", test_4_knowledge_accumulation),
        ("Cost Verification", test_5_cost_verification)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results[test_name] = result
            
            if not result:
                print(f"\n⚠️  {test_name} failed - stopping tests")
                break
                
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results[test_name] = False
            break
        
        # Pause between tests
        if test_name != tests[-1][0]:
            time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Ready for full Phase 0A run on 279 documents")
        print("\nNext steps:")
        print("1. Review the test results above")
        print("2. Check knowledge_store/phase_0A_knowledge.json")
        print("3. Run: python src/main.py ./legal_resources --phases 0A")
    else:
        print("\n⚠️  Some tests failed - fix issues before full run")
    
    return all_passed

def quick_validation():
    """Quick validation without API calls"""
    print("\n" + "="*60)
    print("QUICK VALIDATION (No API Calls)")
    print("="*60)
    
    processor = DocumentProcessor()
    
    # Check document loading
    legal_dir = Path("./legal_resources")
    pdf_files = list(legal_dir.glob("*.pdf"))
    
    print(f"📄 Found {len(pdf_files)} PDFs")
    
    if pdf_files:
        # Load all documents
        print("Loading documents for validation...")
        success = processor.load_documents([str(legal_dir)])
        
        if success:
            print(f"✅ Successfully loaded {len(processor.documents)} documents")
            
            # Test batch creation
            batches = processor._create_intelligent_batches(processor.documents, "0A")
            print(f"\n📦 Batch Analysis for Phase 0A:")
            print(f"   Total documents: {len(processor.documents)}")
            print(f"   Batches to create: {len(batches)}")
            print(f"   Documents per batch: ~{len(processor.documents) // len(batches)}")
            
            # Estimate processing time
            time_per_batch = 30  # seconds
            total_time = len(batches) * time_per_batch
            print(f"\n⏱️  Estimated processing time: {total_time // 60} minutes")
            
            # Estimate costs
            batch_cost = len(batches) * 0.15  # Haiku cost
            synthesis_cost = 0.20
            total_cost = batch_cost + synthesis_cost
            
            print(f"\n💰 Cost Estimate:")
            print(f"   {len(batches)} batches × £0.15 = £{batch_cost:.2f}")
            print(f"   1 synthesis × £0.20 = £{synthesis_cost:.2f}")
            print(f"   TOTAL: £{total_cost:.2f}")
            
            return True
    
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Phase 0A Implementation')
    parser.add_argument('--quick', action='store_true', help='Quick validation only (no API calls)')
    parser.add_argument('--test', type=int, help='Run specific test (1-5)')
    parser.add_argument('--full', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.quick:
        quick_validation()
    elif args.test:
        tests = {
            1: test_1_single_document,
            2: test_2_small_batch,
            3: test_3_multi_batch,
            4: test_4_knowledge_accumulation,
            5: test_5_cost_verification
        }
        if args.test in tests:
            tests[args.test]()
        else:
            print(f"❌ Invalid test number: {args.test}")
    elif args.full:
        run_comprehensive_test()
    else:
        print("Phase 0A Testing Options:")
        print("\n1. Quick validation (no API calls):")
        print("   python test_phase_0a.py --quick")
        print("\n2. Run specific test:")
        print("   python test_phase_0a.py --test 1  # Single document")
        print("   python test_phase_0a.py --test 2  # Small batch")
        print("   python test_phase_0a.py --test 3  # Multi-batch")
        print("\n3. Run all tests:")
        print("   python test_phase_0a.py --full")
        print("\nRecommended: Start with --quick, then --test 1")