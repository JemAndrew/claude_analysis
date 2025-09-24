#!/usr/bin/env python3
"""
Complete System Verification Script for Litigation Analysis
Run this to verify everything is configured correctly
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class SystemVerifier:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def verify_all(self):
        """Run all verification checks"""
        print("="*60)
        print("LITIGATION ANALYSIS SYSTEM VERIFICATION")
        print("="*60)
        
        # 1. Check directory structure
        self.check_directories()
        
        # 2. Check configuration files
        self.check_config_files()
        
        # 3. Check API key
        self.check_api_key()
        
        # 4. Check Python modules
        self.check_modules()
        
        # 5. Check document loading
        self.check_documents()
        
        # 6. Verify settings.json structure
        self.verify_settings_structure()
        
        # 7. Test cost tracking
        self.test_cost_tracking()
        
        # Print results
        self.print_results()
        
    def check_directories(self):
        """Verify all required directories exist"""
        required_dirs = [
            "config",
            "src",
            "documents",
            "legal_resources",
            "knowledge_store",
            "outputs",
            "costs"
        ]
        
        for dir_name in required_dirs:
            path = Path(dir_name)
            if path.exists():
                self.successes.append(f"✅ Directory exists: {dir_name}/")
            else:
                path.mkdir(exist_ok=True)
                self.warnings.append(f"⚠️ Created missing directory: {dir_name}/")
    
    def check_config_files(self):
        """Check configuration files"""
        # Check settings.json
        settings_path = Path("config/settings.json")
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    
                # Verify critical keys
                if 'model' in settings and 'investigation' in settings:
                    self.successes.append("✅ settings.json properly configured")
                else:
                    self.issues.append("❌ settings.json missing critical keys")
            except json.JSONDecodeError:
                self.issues.append("❌ settings.json is not valid JSON")
        else:
            self.issues.append("❌ settings.json not found")
            
    def check_api_key(self):
        """Check API key configuration"""
        env_path = Path("config/.env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
                if 'ANTHROPIC_API_KEY=' in content:
                    if 'your_api_key_here' in content:
                        self.issues.append("❌ API key not set (still placeholder)")
                    else:
                        self.successes.append("✅ API key configured")
        else:
            self.issues.append("❌ config/.env file missing")
    
    def check_modules(self):
        """Check all Python modules exist"""
        required_modules = [
            "src/api_client.py",
            "src/document_processor.py",
            "src/knowledge_manage.py",
            "src/phase_prompts.py",
            "src/output_generator.py",
            "src/main.py"
        ]
        
        for module in required_modules:
            if Path(module).exists():
                self.successes.append(f"✅ Module found: {module}")
            else:
                self.issues.append(f"❌ Missing module: {module}")
    
    def check_documents(self):
        """Check document directories"""
        legal_dir = Path("legal_resources")
        pdf_count = len(list(legal_dir.glob("*.pdf")))
        
        if pdf_count > 0:
            self.successes.append(f"✅ Found {pdf_count} PDFs in legal_resources/")
        else:
            self.warnings.append("⚠️ No PDFs found in legal_resources/")
    
    def verify_settings_structure(self):
        """Verify settings.json has correct structure for api_client.py"""
        settings_path = Path("config/settings.json")
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Check for model configuration
            try:
                primary_model = settings['model']['primary']['name']
                if primary_model == "claude-opus-4-1-20250805":
                    self.successes.append("✅ Correct Opus 4.1 model configured")
                else:
                    self.warnings.append(f"⚠️ Using model: {primary_model}")
            except KeyError:
                self.issues.append("❌ settings.json missing model.primary.name")
                
    def test_cost_tracking(self):
        """Test cost tracking setup"""
        costs_dir = Path("costs")
        if costs_dir.exists():
            self.successes.append("✅ Cost tracking directory ready")
        else:
            costs_dir.mkdir(exist_ok=True)
            self.warnings.append("⚠️ Created costs/ directory")
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "="*60)
        print("VERIFICATION RESULTS")
        print("="*60)
        
        if self.successes:
            print("\n✅ SUCCESSES:")
            for success in self.successes:
                print(f"   {success}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.issues:
            print("\n❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"   {issue}")
        
        # Overall status
        print("\n" + "="*60)
        if not self.issues:
            print("🎉 SYSTEM READY FOR LITIGATION ANALYSIS!")
            print("\nNext steps:")
            print("1. Place your documents in legal_resources/")
            print("2. Run: python src/main.py ./legal_resources --estimate-only")
            print("3. Review cost estimate")
            print("4. Run: python src/main.py ./legal_resources")
        else:
            print("⚠️ FIX CRITICAL ISSUES BEFORE RUNNING")
            print("\nRequired fixes:")
            for issue in self.issues:
                print(f"   • {issue.replace('❌ ', '')}")

if __name__ == "__main__":
    verifier = SystemVerifier()
    verifier.verify_all()