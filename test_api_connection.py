#!/usr/bin/env python3
"""
System Integration Test
Tests all critical components before full deployment
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        from core.config import Config
        from core.orchestrator import LitigationOrchestrator
        from api.client import ClaudeClient
        from api.context_manager import ContextManager
        from api.batch_manager import BatchManager
        from intelligence.knowledge_graph import KnowledgeGraph
        from utils.document_loader import DocumentLoader
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from core.config import Config
        config = Config()
        
        # Check paths exist
        assert config.input_dir.exists(), "Input directory doesn't exist"
        assert config.output_dir.exists(), "Output directory doesn't exist"
        assert config.knowledge_dir.exists(), "Knowledge directory doesn't exist"
        
        # Check critical config values
        assert hasattr(config, 'models'), "Missing models config"
        assert hasattr(config, 'token_config'), "Missing token config"
        assert hasattr(config, 'investigation_triggers'), "Missing investigation triggers"
        
        print("✓ Configuration valid")
        print(f"  Input dir: {config.input_dir}")
        print(f"  Output dir: {config.output_dir}")
        print(f"  Primary model: {config.models.get('primary', 'Not set')}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database initialisation"""
    print("\nTesting database...")
    try:
        from core.config import Config
        from intelligence.knowledge_graph import KnowledgeGraph
        
        config = Config()
        kg = KnowledgeGraph(config)
        
        stats = kg.get_statistics()
        print(f"✓ Database initialised successfully")
        print(f"  Entities: {stats.get('entities', 0)}")
        print(f"  Relationships: {stats.get('relationships', 0)}")
        print(f"  Database path: {config.graph_db_path}")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_loader():
    """Test document loading"""
    print("\nTesting document loader...")
    try:
        from core.config import Config
        from utils.document_loader import DocumentLoader
        
        config = Config()
        loader = DocumentLoader(config)
        
        # Try loading test documents
        test_dir = config.legal_knowledge_dir
        
        if test_dir.exists() and any(test_dir.iterdir()):
            docs = loader.load_directory(test_dir, max_docs=1)
            print(f"✓ Document loader functional: loaded {len(docs)} doc(s)")
            if docs:
                print(f"  Sample doc ID: {docs[0].get('id', 'N/A')}")
                print(f"  Content length: {len(docs[0].get('content', ''))} chars")
        else:
            print("⚠ No test documents found (this is OK if you haven't added documents yet)")
            print(f"  Expected location: {test_dir}")
        
        return True
    except Exception as e:
        print(f"✗ Document loader error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_manager():
    """Test batch manager"""
    print("\nTesting batch manager...")
    try:
        from core.config import Config
        from api.batch_manager import BatchManager
        
        config = Config()
        batch_manager = BatchManager(config)
        
        # Create mock documents
        mock_docs = [
            {'id': 'test1', 'content': 'Test document 1' * 100, 'metadata': {}},
            {'id': 'test2', 'content': 'Test document 2' * 100, 'metadata': {}},
            {'id': 'test3', 'content': 'Test document 3' * 100, 'metadata': {}}
        ]
        
        batches = batch_manager.create_semantic_batches(mock_docs, strategy='simple')
        
        print(f"✓ Batch manager functional")
        print(f"  Created {len(batches)} batch(es) from {len(mock_docs)} documents")
        return True
    except Exception as e:
        print(f"✗ Batch manager error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_client():
    """Test API client initialisation"""
    print("\nTesting API client...")
    try:
        import os
        from core.config import Config
        from api.client import ClaudeClient
        
        config = Config()
        
        # Check if API key is set
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠ ANTHROPIC_API_KEY not set in environment")
            print("  Set it in .env file or environment variables")
            return False
        
        client = ClaudeClient(config)
        
        print(f"✓ API client initialised")
        print(f"  API key found: {api_key[:15]}...")
        print(f"  Primary model: {config.models.get('primary', 'Not set')}")
        
        return True
    except Exception as e:
        print(f"✗ API client error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator():
    """Test orchestrator initialisation"""
    print("\nTesting orchestrator...")
    try:
        from core.orchestrator import LitigationOrchestrator
        
        orchestrator = LitigationOrchestrator()
        
        print(f"✓ Orchestrator initialised")
        print(f"  Phases completed: {len(orchestrator.state.get('phases_completed', []))}")
        print(f"  Active investigations: {len(orchestrator.state.get('active_investigations', []))}")
        
        return True
    except Exception as e:
        print(f"✗ Orchestrator error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LITIGATION INTELLIGENCE SYSTEM - INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))
    results.append(("Document Loader", test_document_loader()))
    results.append(("Batch Manager", test_batch_manager()))
    results.append(("API Client", test_api_client()))
    results.append(("Orchestrator", test_orchestrator()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - System ready for use")
        print("\nNext steps:")
        print("1. Add documents to data/input/legal_knowledge/")
        print("2. Add documents to data/input/case_context/")
        print("3. Add documents to data/input/disclosure/")
        print("4. Run: python main.py")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED - Fix errors before proceeding")
        print("\nReview the error messages above and:")
        print("1. Check all files are in the correct locations")
        print("2. Ensure .env file has ANTHROPIC_API_KEY")
        print("3. Verify all dependencies are installed")
        sys.exit(1)