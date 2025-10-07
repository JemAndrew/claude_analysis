#!/usr/bin/env python3
"""
Phase 0 Dry Test - Comprehensive Path and Dependency Checker
Tests all imports, paths, and configuration for Phase 0
British English throughout - Acting for Lismore

Run from project root: python test_phase_0.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Colour codes for terminal output
class Colours:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colours.BOLD}{Colours.BLUE}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colours.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colours.GREEN}✅ {text}{Colours.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colours.RED}❌ {text}{Colours.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colours.YELLOW}⚠️  {text}{Colours.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colours.BLUE}ℹ️  {text}{Colours.RESET}")


class Phase0DryTest:
    """Comprehensive dry test for Phase 0"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def run_all_tests(self) -> bool:
        """
        Run all tests
        
        Returns:
            True if all critical tests pass, False otherwise
        """
        print_header("PHASE 0 DRY TEST - LISMORE v PROCESS HOLDINGS")
        print("This test validates all paths, imports, and dependencies")
        print("without running Phase 0 or making API calls.\n")
        
        tests = [
            ("Project Structure", self.test_project_structure),
            ("Python Environment", self.test_python_environment),
            ("Core Imports", self.test_core_imports),
            ("Configuration", self.test_configuration),
            ("Source Data Path", self.test_source_data_path),
            ("Output Directories", self.test_output_directories),
            ("Phase 0 Module", self.test_phase0_module),
            ("Prompts Module", self.test_prompts_module),
            ("API Client", self.test_api_client),
            ("Document Loader", self.test_document_loader),
            ("Deduplication", self.test_deduplication),
            ("Knowledge Graph", self.test_knowledge_graph),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print_header(f"TEST: {test_name}")
            try:
                result = test_func()
                if result:
                    print_success(f"{test_name} - PASSED\n")
                else:
                    print_error(f"{test_name} - FAILED\n")
                    all_passed = False
            except Exception as e:
                print_error(f"{test_name} - EXCEPTION: {e}\n")
                all_passed = False
                import traceback
                traceback.print_exc()
        
        # Print summary
        self.print_summary()
        
        return all_passed
    
    def test_project_structure(self) -> bool:
        """Test project directory structure"""
        required_paths = [
            "src",
            "src/core",
            "src/api",
            "src/utils",
            "src/prompts",
            "src/memory",
        ]
        
        all_exist = True
        for path_str in required_paths:
            path = self.project_root / path_str
            if path.exists():
                print_success(f"Found: {path_str}")
            else:
                print_error(f"Missing: {path_str}")
                self.errors.append(f"Missing directory: {path_str}")
                all_exist = False
        
        return all_exist
    
    def test_python_environment(self) -> bool:
        """Test Python version and environment"""
        print_info(f"Python version: {sys.version}")
        print_info(f"Python executable: {sys.executable}")
        
        if sys.version_info >= (3, 8):
            print_success("Python version is 3.8 or higher")
            return True
        else:
            print_error("Python version must be 3.8 or higher")
            self.errors.append("Incorrect Python version")
            return False
    
    def test_core_imports(self) -> bool:
        """Test that core Python modules can be imported"""
        core_modules = ['json', 're', 'pathlib', 'typing', 'datetime']
        
        all_imported = True
        for module in core_modules:
            try:
                __import__(module)
                print_success(f"Imported: {module}")
            except ImportError as e:
                print_error(f"Failed to import: {module} - {e}")
                self.errors.append(f"Cannot import {module}")
                all_imported = False
        
        return all_imported
    
    def test_configuration(self) -> bool:
        """Test configuration module"""
        try:
            # Add src to path
            src_path = self.project_root / "src"
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            
            from core.config import Config
            print_success("Imported Config class")
            
            # Try to initialise config
            config = Config()
            print_success("Initialised Config instance")
            
            # Check key attributes
            required_attrs = [
                'project_root',
                'source_root',
                'output_dir',
                'analysis_dir',
                'haiku_model',
                'sonnet_model',
                'token_config',
                'deduplication_config',
            ]
            
            for attr in required_attrs:
                if hasattr(config, attr):
                    print_success(f"Config has attribute: {attr}")
                else:
                    print_error(f"Config missing attribute: {attr}")
                    self.errors.append(f"Config missing: {attr}")
                    return False
            
            # Print configuration summary
            print_info(f"Project root: {config.project_root}")
            print_info(f"Source root: {config.source_root}")
            print_info(f"Output dir: {config.output_dir}")
            print_info(f"Analysis dir: {config.analysis_dir}")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import Config: {e}")
            self.errors.append(f"Config import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Config initialisation failed: {e}")
            self.errors.append(f"Config init failed: {e}")
            return False
    
    def test_source_data_path(self) -> bool:
        """Test that source data path exists"""
        try:
            from core.config import Config
            config = Config()
            
            source_root = Path(config.source_root)
            
            if source_root.exists():
                print_success(f"Source data path exists: {source_root}")
                
                # Check if it's a directory
                if source_root.is_dir():
                    print_success("Source path is a directory")
                    
                    # Count subdirectories
                    subdirs = [d for d in source_root.iterdir() if d.is_dir()]
                    print_info(f"Found {len(subdirs)} subdirectories")
                    
                    # Show first few subdirectories
                    if subdirs:
                        print_info("Sample subdirectories:")
                        for subdir in subdirs[:5]:
                            print(f"    - {subdir.name}")
                    
                    return True
                else:
                    print_error("Source path is not a directory")
                    self.errors.append("Source path is not a directory")
                    return False
            else:
                print_error(f"Source data path does not exist: {source_root}")
                print_warning("This is expected if SharePoint sync is not set up")
                self.warnings.append("Source data path not found")
                return False
                
        except Exception as e:
            print_error(f"Error checking source data path: {e}")
            self.errors.append(f"Source path check failed: {e}")
            return False
    
    def test_output_directories(self) -> bool:
        """Test output directory creation"""
        try:
            from core.config import Config
            config = Config()
            
            # Test directories
            test_dirs = [
                config.output_dir,
                config.analysis_dir,
                config.analysis_dir / "phase_0",
            ]
            
            all_ok = True
            for test_dir in test_dirs:
                # Create if doesn't exist
                test_dir.mkdir(parents=True, exist_ok=True)
                
                if test_dir.exists():
                    print_success(f"Output directory OK: {test_dir.name}")
                else:
                    print_error(f"Cannot create directory: {test_dir}")
                    self.errors.append(f"Cannot create: {test_dir}")
                    all_ok = False
            
            return all_ok
            
        except Exception as e:
            print_error(f"Error with output directories: {e}")
            self.errors.append(f"Output directories failed: {e}")
            return False
    
    def test_phase0_module(self) -> bool:
        """Test Phase 0 module import"""
        try:
            from core.phase_0 import Phase0Executor
            print_success("Imported Phase0Executor class")
            
            # Check class has required methods
            required_methods = ['__init__', 'execute', '_load_documents_from_folders']
            
            for method in required_methods:
                if hasattr(Phase0Executor, method):
                    print_success(f"Phase0Executor has method: {method}")
                else:
                    print_warning(f"Phase0Executor missing method: {method}")
                    self.warnings.append(f"Missing method: {method}")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import Phase0Executor: {e}")
            self.errors.append(f"Phase0Executor import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing Phase0Executor: {e}")
            self.errors.append(f"Phase0Executor test failed: {e}")
            return False
    
    def test_prompts_module(self) -> bool:
        """Test prompts module"""
        try:
            from prompts.phase_0_prompts import Phase0Prompts
            print_success("Imported Phase0Prompts class")
            
            # Try to initialise
            prompts = Phase0Prompts()
            print_success("Initialised Phase0Prompts instance")
            
            # Check for required prompt methods
            required_prompts = [
                'stage_1_pleadings_analysis',
                'stage_2_tribunal_signals',
                'stage_3_smoking_guns',
            ]
            
            for prompt_name in required_prompts:
                if hasattr(prompts, prompt_name):
                    print_success(f"Found prompt: {prompt_name}")
                else:
                    print_error(f"Missing prompt: {prompt_name}")
                    self.errors.append(f"Missing prompt: {prompt_name}")
                    return False
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import Phase0Prompts: {e}")
            self.errors.append(f"Phase0Prompts import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing Phase0Prompts: {e}")
            self.errors.append(f"Phase0Prompts test failed: {e}")
            return False
    
    def test_api_client(self) -> bool:
        """Test API client module"""
        try:
            from api.client import ClaudeAPIClient
            print_success("Imported ClaudeAPIClient class")
            
            # Check for .env file
            env_file = self.project_root / ".env"
            if env_file.exists():
                print_success("Found .env file")
            else:
                print_warning(".env file not found - API key will need to be set")
                self.warnings.append(".env file missing")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import ClaudeAPIClient: {e}")
            self.errors.append(f"ClaudeAPIClient import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing ClaudeAPIClient: {e}")
            self.errors.append(f"ClaudeAPIClient test failed: {e}")
            return False
    
    def test_document_loader(self) -> bool:
        """Test document loader module"""
        try:
            from utils.document_loader import DocumentLoader
            print_success("Imported DocumentLoader class")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import DocumentLoader: {e}")
            self.errors.append(f"DocumentLoader import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing DocumentLoader: {e}")
            self.errors.append(f"DocumentLoader test failed: {e}")
            return False
    
    def test_deduplication(self) -> bool:
        """Test deduplication module"""
        try:
            from utils.deduplication import DocumentDeduplicator
            print_success("Imported DocumentDeduplicator class")
            
            # Try to initialise
            deduplicator = DocumentDeduplicator(
                similarity_threshold=0.95,
                prefix_chars=10000,
                enable_semantic=False
            )
            print_success("Initialised DocumentDeduplicator instance")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import DocumentDeduplicator: {e}")
            self.errors.append(f"DocumentDeduplicator import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing DocumentDeduplicator: {e}")
            self.errors.append(f"DocumentDeduplicator test failed: {e}")
            return False
    
    def test_knowledge_graph(self) -> bool:
        """Test knowledge graph module"""
        try:
            from intelligence.knowledge_graph import KnowledgeGraph
            print_success("Imported KnowledgeGraph class")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import KnowledgeGraph: {e}")
            self.errors.append(f"KnowledgeGraph import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing KnowledgeGraph: {e}")
            self.errors.append(f"KnowledgeGraph test failed: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        if self.errors:
            print_error(f"ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print()
        
        if self.warnings:
            print_warning(f"WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()
        
        if not self.errors:
            print_success("✨ ALL CRITICAL TESTS PASSED!")
            print_info("\nPhase 0 is ready to run.")
            print_info("Execute with: python main.py phase0")
        else:
            print_error("❌ SOME TESTS FAILED")
            print_info("\nPlease resolve the errors above before running Phase 0.")
        
        print()


def main():
    """Run the dry test"""
    tester = Phase0DryTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()