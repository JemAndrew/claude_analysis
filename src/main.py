#!/usr/bin/env python3
"""
Simplified Main Entry Point
Clean CLI for litigation intelligence system
"""

import os
import argparse
import json
from pathlib import Path
from typing import List, Optional
from api_client import ClaudeAPIClient
from document_processor import DocumentProcessor


class LitigationSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        # Load API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize components
        self.api_client = ClaudeAPIClient(api_key)
        self.processor = DocumentProcessor(self.api_client)
        
        # Track progress
        self.progress_file = Path("outputs/.progress.json")
        self.completed_phases = self._load_progress()
    
    def run_phase(self, phase: str) -> None:
        """Execute a single phase"""
        
        if phase in self.completed_phases:
            print(f"⚠️  Phase {phase} already completed. Use --force to re-run.")
            return
        
        # Execute phase
        results = self.processor.execute_phase(f"phase_{phase}")
        
        # Mark complete
        self.completed_phases.append(phase)
        self._save_progress()
    
    def run_all(self, start_from: Optional[str] = None) -> None:
        """Run all phases in sequence"""
        
        phases = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        if start_from:
            try:
                start_idx = phases.index(start_from)
                phases = phases[start_idx:]
                print(f"Starting from Phase {start_from}")
            except ValueError:
                print(f"Invalid phase: {start_from}")
                return
        
        for phase in phases:
            if phase not in self.completed_phases:
                self.run_phase(phase)
            else:
                print(f"Skipping completed Phase {phase}")
    
    def show_status(self) -> None:
        """Display system status"""
        
        print("\n" + "="*60)
        print("LITIGATION INTELLIGENCE SYSTEM STATUS")
        print("="*60)
        
        all_phases = ["0A", "0B", "1", "2", "3", "4", "5", "6", "7"]
        
        for phase in all_phases:
            status = "✅ Complete" if phase in self.completed_phases else "⏳ Pending"
            
            # Check for outputs
            phase_dir = Path(f"outputs/phase_{phase}")
            if phase_dir.exists():
                synthesis = phase_dir / "synthesis.md"
                reports = list((phase_dir / "reports").glob("*.md")) if (phase_dir / "reports").exists() else []
                print(f"Phase {phase}: {status}")
                if synthesis.exists():
                    print(f"  📄 Synthesis: {synthesis.stat().st_size // 1024}KB")
                if reports:
                    print(f"  📊 Reports: {len(reports)} generated")
            else:
                print(f"Phase {phase}: {status}")
        
        print("\n" + "="*60)
        
        # Document counts
        print("\nDOCUMENT INVENTORY:")
        
        paths = {
            "Legal Resources": Path("legal_resources/processed/text"),
            "Case Context": Path("case_context/processed/text"),
            "Main Documents": Path("documents/processed/text")
        }
        
        for name, path in paths.items():
            if path.exists():
                count = len(list(path.glob("*.txt")))
                print(f"  {name}: {count} documents")
        
        print("="*60)
    
    def reset(self, phase: Optional[str] = None) -> None:
        """Reset progress for re-run"""
        
        if phase:
            if phase in self.completed_phases:
                self.completed_phases.remove(phase)
                print(f"Reset Phase {phase}")
                
                # Delete phase outputs
                phase_dir = Path(f"outputs/phase_{phase}")
                if phase_dir.exists():
                    import shutil
                    shutil.rmtree(phase_dir)
                    print(f"Deleted {phase_dir}")
        else:
            # Reset all
            self.completed_phases = []
            print("Reset all phases")
        
        self._save_progress()
    
    def _load_progress(self) -> List[str]:
        """Load completed phases"""
        
        if self.progress_file.exists():
            with open(self.progress_file, "r") as f:
                data = json.load(f)
                return data.get("completed_phases", [])
        return []
    
    def _save_progress(self) -> None:
        """Save progress state"""
        
        self.progress_file.parent.mkdir(exist_ok=True)
        with open(self.progress_file, "w") as f:
            json.dump({"completed_phases": self.completed_phases}, f, indent=2)


def main():
    """CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Litigation Intelligence System - Lismore v Process Holdings"
    )
    
    parser.add_argument(
        "--phase",
        choices=["0A", "0B", "1", "2", "3", "4", "5", "6", "7"],
        help="Run specific phase"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all phases in sequence"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status"
    )
    
    parser.add_argument(
        "--reset",
        nargs="?",
        const="all",
        help="Reset progress (optionally specify phase)"
    )
    
    parser.add_argument(
        "--start-from",
        choices=["0A", "0B", "1", "2", "3", "4", "5", "6", "7"],
        help="When using --all, start from specific phase"
    )
    
    args = parser.parse_args()
    
    # Initialize system
    system = LitigationSystem()
    
    # Execute command
    if args.status:
        system.show_status()
    
    elif args.reset:
        if args.reset == "all":
            system.reset()
        else:
            system.reset(args.reset)
    
    elif args.all:
        system.run_all(start_from=args.start_from)
    
    elif args.phase:
        system.run_phase(args.phase)
    
    else:
        # Default: show status
        system.show_status()
        print("\nUsage:")
        print("  python main.py --phase 0A        # Run Phase 0A")
        print("  python main.py --all              # Run all phases")
        print("  python main.py --status           # Show progress")
        print("  python main.py --reset 1          # Reset Phase 1")


if __name__ == "__main__":
    main()