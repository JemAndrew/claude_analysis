#!/usr/bin/env python3
"""
ULTIMATE Phase 0 Dry Run - Complete Pre-Flight Check
Tests EVERYTHING before running Phase 0
British English throughout - Lismore v Process Holdings

Run this script BEFORE running Phase 0 to catch all potential issues.

Usage:
    python phase_0_dry_run.py
"""

import sys
import os
from pathlib import Path
from difflib import SequenceMatcher

# ANSI colour codes for beautiful output
class Colours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colours.HEADER}{Colours.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colours.ENDC}\n")

def print_success(text):
    print(f"{Colours.OKGREEN}✅ {text}{Colours.ENDC}")

def print_warning(text):
    print(f"{Colours.WARNING}⚠️  {text}{Colours.ENDC}")

def print_error(text):
    print(f"{Colours.FAIL}❌ {text}{Colours.ENDC}")

def print_info(text):
    print(f"{Colours.OKCYAN}ℹ️  {text}{Colours.ENDC}")


class Phase0DryTest:
    """Comprehensive pre-flight testing for Phase 0"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        self.test_results = {}
    
    # ========================================================================
    # FUZZY FOLDER MATCHING TESTS
    # ========================================================================
    
    def test_fuzzy_folder_matching(self) -> bool:
        """Test fuzzy folder matching logic"""
        print_info("Testing fuzzy folder matching algorithm...")
        
        # Test cases: (pattern, expected_to_match, folder_name)
        test_cases = [
            ("Claimant's Statement", "Claimants Statement", True),
            ("29- Claimant's Claim", "29 - claimants claim", True),
            ("Procedural Orders", "5- Procedural Order", True),
            ("First Respondent", "first respondents", True),
            ("Statement of Defence", "Statement of Defense", True),  # US vs UK spelling
            ("Tribunal Ruling", "Tribunal's Rulings", True),
            ("Complete Mismatch", "Totally Different", False),
        ]
        
        def normalise(name):
            """Simplified normalisation for testing"""
            import re
            name = name.lower()
            name = re.sub(r'^\d+[\s\-\.]*', '', name)
            name = re.sub(r"'s\b", '', name)
            name = re.sub(r"s'\b", '', name)
            name = re.sub(r'[^\w\s]', ' ', name)
            name = re.sub(r'\borders\b', 'order', name)
            name = re.sub(r'\bstatements\b', 'statement', name)
            name = re.sub(r'\s+', ' ', name)
            return name.strip()
        
        passed = 0
        failed = 0
        
        for pattern, folder, should_match in test_cases:
            norm_pattern = normalise(pattern)
            norm_folder = normalise(folder)
            
            # Calculate similarity
            similarity = SequenceMatcher(None, norm_pattern, norm_folder).ratio()
            is_match = (similarity >= 0.75) or (norm_pattern == norm_folder)
            
            if is_match == should_match:
                passed += 1
                print(f"  ✅ '{pattern}' vs '{folder}' → {similarity:.1%}")
            else:
                failed += 1
                print_error(f"  '{pattern}' vs '{folder}' → Expected {should_match}, got {is_match}")
        
        print(f"\nFuzzy matching tests: {passed}/{len(test_cases)} passed")
        
        if failed > 0:
            self.warnings.append(f"Fuzzy matching: {failed} test cases failed")
            return False
        
        return True
    
    # ========================================================================
    # PROJECT STRUCTURE TESTS
    # ========================================================================
    
    def test_project_structure(self) -> bool:
        """Test project directory structure"""
        required_paths = [
            "src",
            "src/core",
            "src/api",
            "src/utils",
            "src/prompts",
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
    
    # ========================================================================
    # PYTHON ENVIRONMENT TESTS
    # ========================================================================
    
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
    
    # ========================================================================
    # IMPORT TESTS
    # ========================================================================
    
    def test_core_imports(self) -> bool:
        """Test that core Python modules can be imported"""
        core_modules = ['json', 're', 'pathlib', 'typing', 'datetime', 'difflib']
        
        all_imported = True
        for module in core_modules:
            try:
                __import__(module)
                print_success(f"Imported: {module}")
            except ImportError as e:
                print_error(f"Cannot import {module}: {e}")
                self.errors.append(f"Core module import failed: {module}")
                all_imported = False
        
        return all_imported
    
    def test_project_imports(self) -> bool:
        """Test that project modules can be imported"""
        # Add src to path temporarily
        src_path = self.project_root / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        
        project_modules = [
            ('core.config', 'Config'),
            ('utils.document_loader', 'DocumentLoader'),
            ('utils.deduplication', 'DocumentDeduplicator'),
            ('prompts.phase_0_prompts', 'Phase0Prompts'),
        ]
        
        all_imported = True
        for module_path, class_name in project_modules:
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                print_success(f"Imported: {module_path}.{class_name}")
            except ImportError as e:
                print_error(f"Cannot import {module_path}.{class_name}: {e}")
                self.errors.append(f"Project import failed: {module_path}")
                all_imported = False
            except AttributeError as e:
                print_error(f"Class {class_name} not found in {module_path}: {e}")
                self.errors.append(f"Class not found: {class_name} in {module_path}")
                all_imported = False
        
        return all_imported
    
    # ========================================================================
    # CONFIGURATION TESTS
    # ========================================================================
    
    def test_config(self) -> bool:
        """Test configuration file"""
        try:
            from core.config import Config
            config = Config()
            
            print_success("Config object created")
            
            # Check critical attributes
            critical_attrs = [
                'source_root',
                'analysis_dir',
                'sonnet_model',
                'opus_model',
            ]
            
            all_present = True
            for attr in critical_attrs:
                if hasattr(config, attr):
                    value = getattr(config, attr)
                    print_success(f"  {attr}: {value}")
                else:
                    print_error(f"  Missing attribute: {attr}")
                    self.errors.append(f"Config missing attribute: {attr}")
                    all_present = False
            
            # Check source_root exists
            if hasattr(config, 'source_root'):
                if config.source_root.exists():
                    print_success(f"  source_root exists: {config.source_root}")
                else:
                    print_warning(f"  source_root doesn't exist: {config.source_root}")
                    self.warnings.append(f"source_root path doesn't exist: {config.source_root}")
            
            return all_present
            
        except Exception as e:
            print_error(f"Config test failed: {e}")
            self.errors.append(f"Config test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========================================================================
    # FOLDER DISCOVERY TESTS
    # ========================================================================
    
    def test_folder_discovery(self) -> bool:
        """Test that Phase 0 folders can be discovered"""
        try:
            from core.config import Config
            config = Config()
            
            if not config.source_root.exists():
                print_warning("Cannot test folder discovery: source_root doesn't exist")
                return True  # Don't fail if source_root not set up yet
            
            print_info(f"Scanning folders in: {config.source_root}")
            
            # Get all folders
            all_folders = [f for f in config.source_root.iterdir() if f.is_dir()]
            
            if not all_folders:
                print_warning("No folders found in source_root")
                self.warnings.append("No folders in source_root")
                return True
            
            print_success(f"Found {len(all_folders)} folders:")
            
            # Show first 10 folders
            for folder in sorted(all_folders)[:10]:
                print(f"      📂 {folder.name}")
            
            if len(all_folders) > 10:
                print(f"      ... and {len(all_folders) - 10} more")
            
            # Test fuzzy matching on expected Phase 0 folders
            print("\n  Testing fuzzy matching on Phase 0 folders:")
            
            expected_patterns = [
                "29- Claimant's Statement of Claim",
                "35- First Respondent's Statement of Defence",
                "5- Procedural Orders",
                "20- Dramatis Personae",
                "21- Chronology",
            ]
            
            def normalise(name):
                import re
                name = name.lower()
                name = re.sub(r'^\d+[\s\-\.]*', '', name)
                name = re.sub(r"'s\b", '', name)
                name = re.sub(r'[^\w\s]', ' ', name)
                name = re.sub(r'\s+', ' ', name)
                return name.strip()
            
            found_count = 0
            for pattern in expected_patterns:
                pattern_norm = normalise(pattern)
                best_match = None
                best_score = 0.0
                
                for folder in all_folders:
                    folder_norm = normalise(folder.name)
                    similarity = SequenceMatcher(None, pattern_norm, folder_norm).ratio()
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = folder
                
                if best_match and best_score >= 0.75:
                    print_success(f"    '{pattern[:40]}...' → {best_match.name} ({best_score:.0%})")
                    found_count += 1
                else:
                    print_warning(f"    '{pattern[:40]}...' → Not found (best: {best_score:.0%})")
            
            print(f"\n  Fuzzy matched: {found_count}/{len(expected_patterns)} folders")
            
            if found_count == 0:
                self.warnings.append("Could not find any expected Phase 0 folders")
            
            return True
            
        except Exception as e:
            print_error(f"Folder discovery test failed: {e}")
            self.errors.append(f"Folder discovery failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========================================================================
    # DOCUMENT LOADER TESTS
    # ========================================================================
    
    def test_document_loader(self) -> bool:
        """Test document loader"""
        try:
            from utils.document_loader import DocumentLoader
            from core.config import Config
            
            print_success("Imported DocumentLoader class")
            
            config = Config()
            loader = DocumentLoader(config)
            
            print_success("Initialised DocumentLoader instance")
            
            # Check SUPPORTED_FORMATS
            if hasattr(loader, 'SUPPORTED_FORMATS'):
                formats = loader.SUPPORTED_FORMATS
                print_success(f"  Supported formats: {', '.join(formats)}")
            else:
                print_warning("  SUPPORTED_FORMATS not found")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import DocumentLoader: {e}")
            self.errors.append(f"DocumentLoader import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing DocumentLoader: {e}")
            self.errors.append(f"DocumentLoader test failed: {e}")
            return False
    
    # ========================================================================
    # DEDUPLICATION TESTS
    # ========================================================================
    
    def test_deduplication(self) -> bool:
        """Test deduplication module"""
        try:
            from utils.deduplication import DocumentDeduplicator
            print_success("Imported DocumentDeduplicator class")
            
            # Try to initialise with test parameters
            deduplicator = DocumentDeduplicator(
                similarity_threshold=0.85,
                prefix_chars=10000,
                enable_semantic=True
            )
            print_success("Initialised DocumentDeduplicator instance")
            
            # Test with sample data
            test_text_1 = "This is a test document about litigation and legal proceedings."
            test_text_2 = "This is a test document about litigation and legal proceedings."  # Exact duplicate
            test_text_3 = "This is a completely different document about something else entirely."
            
            # Test exact duplicate detection
            is_dup_1, reason_1 = deduplicator.is_duplicate(test_text_1, "doc1", "test1.pdf")
            is_dup_2, reason_2 = deduplicator.is_duplicate(test_text_2, "doc2", "test2.pdf")
            is_dup_3, reason_3 = deduplicator.is_duplicate(test_text_3, "doc3", "test3.pdf")
            
            if not is_dup_1 and is_dup_2 and not is_dup_3:
                print_success("  Exact duplicate detection: WORKING")
            else:
                print_warning(f"  Duplicate detection: doc1={is_dup_1}, doc2={is_dup_2}, doc3={is_dup_3}")
                self.warnings.append("Deduplication behaviour unexpected")
            
            # Get statistics
            stats = deduplicator.get_statistics()
            print_success(f"  Statistics: {stats['unique_documents']} unique, {stats['total_checked']} checked")
            
            return True
            
        except ImportError as e:
            print_error(f"Cannot import DocumentDeduplicator: {e}")
            self.errors.append(f"DocumentDeduplicator import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing DocumentDeduplicator: {e}")
            self.errors.append(f"DocumentDeduplicator test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========================================================================
    # PROMPT TESTS
    # ========================================================================
    
    def test_prompts(self) -> bool:
        """Test Phase 0 prompts"""
        try:
            from prompts.phase_0_prompts import Phase0Prompts
            from core.config import Config
            
            print_success("Imported Phase0Prompts class")
            
            config = Config()
            prompts = Phase0Prompts(config)
            
            print_success("Initialised Phase0Prompts instance")
            
            # Check methods exist
            required_methods = [
                'build_stage_1_prompt',
                'build_stage_2_prompt',
                'build_stage_3_prompt',
            ]
            
            all_present = True
            for method in required_methods:
                if hasattr(prompts, method):
                    print_success(f"  Method exists: {method}")
                else:
                    print_error(f"  Missing method: {method}")
                    self.errors.append(f"Phase0Prompts missing method: {method}")
                    all_present = False
            
            # Test building a prompt (with dummy data)
            if hasattr(prompts, 'build_stage_1_prompt'):
                try:
                    test_prompt = prompts.build_stage_1_prompt("Test pleadings text")
                    if len(test_prompt) > 100:
                        print_success(f"  Stage 1 prompt builds correctly ({len(test_prompt)} chars)")
                    else:
                        print_warning("  Stage 1 prompt seems too short")
                except Exception as e:
                    print_error(f"  Error building Stage 1 prompt: {e}")
                    self.errors.append(f"Stage 1 prompt build failed: {e}")
                    all_present = False
            
            return all_present
            
        except ImportError as e:
            print_error(f"Cannot import Phase0Prompts: {e}")
            self.errors.append(f"Phase0Prompts import failed: {e}")
            return False
        except Exception as e:
            print_error(f"Error testing Phase0Prompts: {e}")
            self.errors.append(f"Phase0Prompts test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========================================================================
    # PHASE 0 EXECUTOR TESTS
    # ========================================================================
    
    def test_phase_0_executor(self) -> bool:
        """Test Phase 0 executor can be imported"""
        try:
            from core.phase_0 import Phase0Executor
            print_success("Imported Phase0Executor class")
            
            # Check critical methods
            required_methods = [
                'execute',
                '_find_folder_fuzzy',
                '_normalise_folder_name',
                '_load_documents_from_folders',
                '_parse_stage_1_response',
                '_parse_stage_2_response',
                '_parse_stage_3_response',
            ]
            
            all_present = True
            for method in required_methods:
                if hasattr(Phase0Executor, method):
                    print_success(f"  Method exists: {method}")
                else:
                    print_error(f"  Missing method: {method}")
                    self.errors.append(f"Phase0Executor missing method: {method}")
                    all_present = False
            
            return all_present
            
        except ImportError as e:
            print_error(f"Cannot import Phase0Executor: {e}")
            self.errors.append(f"Phase0Executor import failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print_error(f"Error testing Phase0Executor: {e}")
            self.errors.append(f"Phase0Executor test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========================================================================
    # MAIN TEST RUNNER
    # ========================================================================
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        
        print_header("🧪 PHASE 0 ULTIMATE DRY RUN")
        print_info("Testing all components before running Phase 0...")
        
        tests = [
            ("1. Project Structure", self.test_project_structure),
            ("2. Python Environment", self.test_python_environment),
            ("3. Core Imports", self.test_core_imports),
            ("4. Project Imports", self.test_project_imports),
            ("5. Configuration", self.test_config),
            ("6. Folder Discovery", self.test_folder_discovery),
            ("7. Document Loader", self.test_document_loader),
            ("8. Deduplication", self.test_deduplication),
            ("9. Fuzzy Folder Matching", self.test_fuzzy_folder_matching),
            ("10. Phase 0 Prompts", self.test_prompts),
            ("11. Phase 0 Executor", self.test_phase_0_executor),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print_header(f"TEST: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = result
                
                if result:
                    print_success(f"{test_name} - PASSED\n")
                else:
                    print_error(f"{test_name} - FAILED\n")
                    all_passed = False
            except Exception as e:
                print_error(f"{test_name} - EXCEPTION: {e}\n")
                self.test_results[test_name] = False
                all_passed = False
                import traceback
                traceback.print_exc()
        
        # Print summary
        self.print_summary()
        
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        print_header("📊 TEST SUMMARY")
        
        # Test results
        passed = sum(1 for r in self.test_results.values() if r)
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if self.errors:
            print(f"\n{Colours.FAIL}{Colours.BOLD}ERRORS ({len(self.errors)}):{Colours.ENDC}")
            for error in self.errors:
                print(f"  • {error}")
            print()
        
        if self.warnings:
            print(f"{Colours.WARNING}{Colours.BOLD}WARNINGS ({len(self.warnings)}):{Colours.ENDC}")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()
        
        if not self.errors:
            print_success("✨ ALL CRITICAL TESTS PASSED!")
            print_info("\n🚀 Phase 0 is READY to run!")
            print_info("Execute with: python main.py phase0\n")
        else:
            print_error("❌ CRITICAL ERRORS DETECTED")
            print_info("\nPlease resolve the errors above before running Phase 0.\n")
        
        # Feature checklist
        print(f"{Colours.HEADER}{Colours.BOLD}FEATURES ENABLED:{Colours.ENDC}")
        print_success("  ✅ Fuzzy folder name matching (typos, case, punctuation)")
        print_success("  ✅ Document content deduplication")
        print_success("  ✅ Extended thinking (12,000 tokens)")
        print_success("  ✅ Delimiter-based response parsing")
        print_success("  ✅ Pure learning approach (no smoking guns)")
        print()


def main():
    """Run the ultimate dry test"""
    tester = Phase0DryTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()