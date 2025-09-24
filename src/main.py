# main.py (COMPLETE FILE)
"""
Main orchestrator for Lismore Capital document analysis system.
Coordinates all phases and generates comprehensive litigation intelligence.
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Import our modules
from document_processor import DocumentProcessor
from knowledge_manage import KnowledgeManager
from output_generator import OutputGenerator
from utils import (
    DocumentUtils, 
    AnalysisUtils, 
    ValidationUtils, 
    ConfigUtils,
    ReportUtils
)

class LismoreAnalyser:
    """Main orchestrator for the Lismore Capital analysis system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise the analyser
        
        Args:
            config_path: Optional path to configuration file
        """
        print(ReportUtils.format_header("LISMORE CAPITAL LITIGATION ANALYSER"))
        print("Initialising system...")
        
        # Load configuration
        self.config = ConfigUtils.load_config(config_path) if config_path else ConfigUtils.load_config()
        
        # Check environment
        env_checks = ConfigUtils.check_environment()
        if not env_checks['api_key']:
            print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
            sys.exit(1)
        
        # Initialise components
        self.document_processor = DocumentProcessor()
        self.knowledge_manage = self.document_processor.knowledge_manage
        self.output_generator = OutputGenerator(self.knowledge_manage)
        
        # Document storage
        self.documents = []
        self.document_paths = []
        
        print("✓ System initialised successfully")
        print(f"✓ Output directory: {self.config['output_dir']}")
        print(f"✓ Knowledge store: {self.config['knowledge_dir']}")
    
    def load_documents(self, paths: List[str]) -> bool:
        """
        Load documents from file paths or directory
        
        Args:
            paths: List of file paths or directory paths
            
        Returns:
            Success status
        """
        print(ReportUtils.format_section("LOADING DOCUMENTS"))
        
        all_files = []
        
        for path in paths:
            path_obj = Path(path)
            
            if path_obj.is_dir():
                # Load all documents from directory
                print(f"Scanning directory: {path}")
                for file_path in path_obj.rglob('*'):
                    if file_path.is_file():
                        all_files.append(str(file_path))
            elif path_obj.is_file():
                all_files.append(str(path_obj))
            else:
                print(f"Warning: Path not found: {path}")
        
        if not all_files:
            print("ERROR: No valid files found")
            return False
        
        print(f"Found {len(all_files)} files to process")
        
        # Extract text from each file
        for file_path in all_files:
            print(f"Processing: {os.path.basename(file_path)}")
            doc_data = DocumentUtils.extract_text_from_file(file_path)
            
            # Validate document
            is_valid, errors = ValidationUtils.validate_document_structure(doc_data)
            if not is_valid:
                print(f"  Warning: Document validation failed: {', '.join(errors)}")
                continue
            
            self.documents.append(doc_data)
            self.document_paths.append(file_path)
        
        print(f"\n✓ Successfully loaded {len(self.documents)} documents")
        
        # Load into document processor
        return self.document_processor.load_documents(self.document_paths)
    
    def run_analysis(self, phases: Optional[List[str]] = None, 
                    skip_reports: bool = False) -> Dict:
        """
        Run the analysis pipeline
        
        Args:
            phases: Optional list of specific phases to run (None = all)
            skip_reports: Whether to skip report generation
            
        Returns:
            Analysis results
        """
        print(ReportUtils.format_header("STARTING ANALYSIS"))
        
        if not self.documents:
            print("ERROR: No documents loaded")
            return {}
        
        # Determine which phases to run
        if phases:
            phases_to_run = phases
        else:
            phases_to_run = ['0A', '0B', '1', '2', '3', '4', '5', '6', '7']
        
        print(f"Phases to run: {', '.join(phases_to_run)}")
        
        results = {}
        completed_phases = self.knowledge_manage.get_completed_phases()
        
        # Run each phase
        for phase in phases_to_run:
            # Validate phase can be run
            can_run, error_msg = ValidationUtils.validate_phase_sequence(
                completed_phases, phase
            )
            
            if not can_run:
                print(f"ERROR: Cannot run phase {phase}: {error_msg}")
                continue
            
            print(f"\n{'='*60}")
            print(f"EXECUTING PHASE {phase}")
            print(f"{'='*60}")
            
            # Run the phase
            phase_result = self.document_processor.process_phase(phase)
            results[phase] = phase_result
            
            # Update completed phases
            completed_phases.append(phase)
            
            # Quick analysis preview
            self._show_phase_preview(phase, phase_result)
        
        # Generate reports unless skipped
        if not skip_reports and len(results) > 0:
            print(ReportUtils.format_header("GENERATING REPORTS"))
            self._generate_reports()
        
        # Generate final summary
        self._generate_final_summary(results)
        
        return results
    
    def _show_phase_preview(self, phase: str, result: Dict):
        """Show preview of phase results"""
        print(f"\n✓ Phase {phase} complete")
        
        # Show brief preview based on phase
        if phase in ['1', '2', '3', '4', '5', '6', '7']:
            findings = result.get('findings', {})
            if isinstance(findings, dict):
                if 'combined_insights' in findings:
                    preview = findings['combined_insights'][:500]
                elif 'analysis' in findings:
                    preview = findings['analysis'][:500]
                else:
                    preview = str(findings)[:500]
            else:
                preview = str(findings)[:500]
            
            print("\nKey findings preview:")
            print("-"*40)
            print(preview + "...")
    
    def _generate_reports(self):
        """Generate all reports"""
        print("\nGenerating comprehensive reports...")
        
        # Register documents with output generator
        self.output_generator.register_documents(self.documents)
        
        # Generate all phase reports
        all_reports = self.output_generator.generate_all_phase_reports(self.documents)
        
        # Generate table of contents
        toc = ReportUtils.generate_table_of_contents(all_reports)
        toc_file = f"{self.output_generator.output_dir}/TABLE_OF_CONTENTS.txt"
        with open(toc_file, 'w') as f:
            f.write(toc)
        
        print(f"\n✓ Generated table of contents: {toc_file}")
    
    def _generate_final_summary(self, results: Dict):
        """Generate final summary of analysis"""
        summary = [
            ReportUtils.format_header("ANALYSIS COMPLETE"),
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Documents Analysed: {len(self.documents)}",
            f"Phases Completed: {len(results)}/9",
            "\nCompleted Phases:"
        ]
        
        for phase in results:
            summary.append(f"  ✓ Phase {phase}")
        
        # Key statistics
        if self.documents:
            total_chars = sum(len(doc.get('content', '')) for doc in self.documents)
            summary.extend([
                f"\nDocument Statistics:",
                f"  Total Characters: {total_chars:,}",
                f"  Average Doc Size: {total_chars // len(self.documents):,} chars",
                f"  Document Types: {', '.join(set(doc.get('extension', 'unknown') for doc in self.documents))}"
            ])
        
        summary.extend([
            "\n" + "="*60,
            "NEXT STEPS:",
            "1. Review generated reports in ./outputs/",
            "2. Focus on Phase 6 smoking guns for immediate leverage",
            "3. Prepare litigation strategy based on Phase 4 theory",
            "4. Use Phase 7 insights for unconventional advantages",
            "="*60
        ])
        
        summary_text = '\n'.join(summary)
        print(summary_text)
        
        # Save summary
        summary_file = f"./outputs/ANALYSIS_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w') as f:
            f.write(summary_text)
    
    def run_single_phase(self, phase: str) -> Dict:
        """
        Run a single phase
        
        Args:
            phase: Phase identifier
            
        Returns:
            Phase results
        """
        print(f"Running single phase: {phase}")
        
        # Validate
        completed = self.knowledge_manage.get_completed_phases()
        can_run, error_msg = ValidationUtils.validate_phase_sequence(completed, phase)
        
        if not can_run:
            print(f"ERROR: {error_msg}")
            return {}
        
        return self.document_processor.process_phase(phase)
    
    def resume_analysis(self) -> Dict:
        """Resume analysis from last completed phase"""
        completed = self.knowledge_manage.get_completed_phases()
        all_phases = ['0A', '0B', '1', '2', '3', '4', '5', '6', '7']
        
        remaining = [p for p in all_phases if p not in completed]
        
        if not remaining:
            print("All phases already completed")
            return {}
        
        print(f"Resuming from phase {remaining[0]}")
        print(f"Completed phases: {', '.join(completed)}")
        print(f"Remaining phases: {', '.join(remaining)}")
        
        return self.run_analysis(phases=remaining)
    
    def clear_knowledge(self, phase: Optional[str] = None):
        """Clear knowledge store"""
        if phase:
            print(f"Clearing knowledge for phase {phase}")
            self.knowledge_manage.clear_knowledge(phase)
        else:
            print("Clearing all knowledge")
            self.knowledge_manage.clear_knowledge()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Lismore Capital Litigation Analysis System'
    )
    
    parser.add_argument(
        'documents',
        nargs='+',
        help='Paths to documents or directories to analyse'
    )
    
    parser.add_argument(
        '--phases',
        nargs='+',
        choices=['0A', '0B', '1', '2', '3', '4', '5', '6', '7'],
        help='Specific phases to run (default: all)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last completed phase'
    )
    
    parser.add_argument(
        '--skip-reports',
        action='store_true',
        help='Skip report generation'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear knowledge store before starting'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialise analyser
        analyser = LismoreAnalyser(config_path=args.config)
        
        # Clear if requested
        if args.clear:
            analyser.clear_knowledge()
        
        # Load documents
        if not analyser.load_documents(args.documents):
            print("Failed to load documents")
            sys.exit(1)
        
        # Run analysis
        if args.resume:
            results = analyser.resume_analysis()
        else:
            results = analyser.run_analysis(
                phases=args.phases,
                skip_reports=args.skip_reports
            )
        
        if results:
            print("\n✓ Analysis completed successfully")
            print(f"✓ Results saved to ./outputs/")
        else:
            print("\n⚠ Analysis completed with no results")
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()