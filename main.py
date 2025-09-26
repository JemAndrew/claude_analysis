#!/usr/bin/env python3
"""
Litigation Intelligence System - Main Entry Point
Optimised for maximum Claude utilisation - Lismore v Process Holdings
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config import config
from core.orchestrator import LitigationOrchestrator


class LitigationIntelligence:
    """Main entry point for litigation intelligence system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialise system"""
        
        # Load custom config if provided
        config_override = {}
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_override = json.load(f)
        
        # Initialise orchestrator
        self.orchestrator = LitigationOrchestrator(config_override)
        
        # Check API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        
        print("\n🎯 LITIGATION INTELLIGENCE SYSTEM")
        print("📁 Case: Lismore Capital v Process Holdings")
        print("🤖 Model: Claude Opus (Maximum Capability Mode)")
        print("=" * 60)
        
        # Confirm execution
        print("\nThis will:")
        print("  • Process all legal knowledge and case context")
        print("  • Analyse all disclosure documents")
        print("  • Spawn investigations automatically")
        print("  • Generate strategic reports")
        print("  • Create war room dashboard")
        print("\nEstimated time: 30-60 minutes")
        print("Estimated cost: $50-150 (depending on document volume)")
        
        response = input("\nProceed? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
        
        # Execute full analysis
        results = self.orchestrator.execute_full_analysis()
        
        # Print final summary
        self._print_final_summary(results)
    
    def run_single_phase(self, phase: str):
        """Execute single phase"""
        
        print(f"\n🎯 Executing Phase {phase}")
        print("=" * 60)
        
        # Execute phase
        results = self.orchestrator.execute_single_phase(phase)
        
        print(f"\n✅ Phase {phase} complete")
        print(f"Documents processed: {results.get('documents_processed', 0)}")
        
        return results
    
    def run_investigation(self, investigation_type: str, priority: float = 7.0):
        """Spawn and execute specific investigation"""
        
        print(f"\n🔍 Spawning Investigation: {investigation_type}")
        print("=" * 60)
        
        # Spawn investigation
        investigation_id = self.orchestrator.spawn_investigation(
            trigger_type=investigation_type,
            trigger_data={'manual_trigger': True},
            priority=priority
        )
        
        print(f"Investigation ID: {investigation_id}")
        print(f"Priority: {priority}")
        
        # Execute investigation
        investigation = {
            'id': investigation_id,
            'type': investigation_type,
            'priority': priority,
            'data': {'manual_trigger': True}
        }
        
        results = self.orchestrator._execute_investigation(investigation)
        
        print(f"\n✅ Investigation complete")
        return results
    
    def generate_reports(self):
        """Generate all strategic reports"""
        
        print("\n📊 Generating Strategic Reports")
        print("=" * 60)
        
        # Get all results
        results = {
            'phases': {},
            'investigations': []
        }
        
        # Load completed phases
        for phase in self.orchestrator.state.get('phases_completed', []):
            phase_dir = config.analysis_dir / f"phase_{phase}"
            if phase_dir.exists():
                synthesis_file = phase_dir / "synthesis.md"
                if synthesis_file.exists():
                    with open(synthesis_file, 'r') as f:
                        results['phases'][phase] = {'synthesis': f.read()}
        
        # Generate war room dashboard
        dashboard = self.orchestrator._generate_war_room_dashboard(results)
        
        print("✅ Reports generated")
        print(f"Location: {config.reports_dir}")
        
        return dashboard
    
    def show_status(self):
        """Show system status"""
        
        print("\n📈 SYSTEM STATUS")
        print("=" * 60)
        
        # Get statistics
        stats = self.orchestrator.knowledge_graph.get_statistics()
        
        print(f"\nKnowledge Graph Statistics:")
        print(f"  Entities: {stats['entities']}")
        print(f"  Relationships: {stats['relationships']}")
        print(f"  Contradictions: {stats['contradictions']}")
        print(f"  Patterns: {stats['patterns']}")
        print(f"  Timeline Events: {stats['timeline_events']}")
        print(f"  Active Investigations: {stats['active_investigations']}")
        print(f"  Discoveries: {stats['discoveries']}")
        
        # Show completed phases
        print(f"\nPhases Completed: {', '.join(self.orchestrator.state['phases_completed'])}")
        
        # Show API usage
        usage = self.orchestrator.api_client.get_usage_report()
        print(f"\nAPI Usage:")
        print(f"  Total Calls: {usage['summary']['total_calls']}")
        print(f"  Input Tokens: {usage['summary']['total_input_tokens']:,}")
        print(f"  Output Tokens: {usage['summary']['total_output_tokens']:,}")
        print(f"  Estimated Cost: ${usage['summary']['estimated_cost_usd']:.2f}")
        
        # Show active investigations
        investigations = self.orchestrator.knowledge_graph.get_investigation_queue(limit=5)
        if investigations:
            print(f"\nActive Investigations:")
            for inv in investigations:
                print(f"  • {inv['type']} (Priority: {inv['priority']:.1f})")
    
    def reset(self, confirm: bool = False):
        """Reset system state"""
        
        if not confirm:
            response = input("\n⚠️  This will delete all analysis. Are you sure? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled")
                return
        
        print("\nResetting system...")
        
        # Clear knowledge graph
        if config.graph_db_path.exists():
            config.graph_db_path.unlink()
        
        # Clear outputs
        import shutil
        if config.output_dir.exists():
            shutil.rmtree(config.output_dir)
        
        # Recreate directories
        config.output_dir.mkdir(parents=True, exist_ok=True)
        config.analysis_dir.mkdir(parents=True, exist_ok=True)
        config.investigations_dir.mkdir(parents=True, exist_ok=True)
        config.reports_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ System reset complete")
    
    def _print_final_summary(self, results: Dict):
        """Print final analysis summary"""
        
        print("\n" + "=" * 60)
        print("🎯 ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Count discoveries
        nuclear_count = 0
        critical_count = 0
        
        for phase_data in results.get('phases', {}).values():
            synthesis = phase_data.get('synthesis', '')
            nuclear_count += synthesis.count('[NUCLEAR]')
            critical_count += synthesis.count('[CRITICAL]')
        
        print(f"\nKey Discoveries:")
        print(f"  🔴 Nuclear (Case-ending): {nuclear_count}")
        print(f"  🟠 Critical (Major advantage): {critical_count}")
        
        # Show top findings
        if results.get('war_room_dashboard'):
            print(f"\n📊 War Room Dashboard generated")
            print(f"   Location: {config.reports_dir}")
        
        if results.get('final_synthesis'):
            print(f"\n📝 Strategic Synthesis complete")
            print(f"   Location: {config.reports_dir}")
        
        print("\n✅ All outputs saved to:", config.output_dir)


def main():
    """CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Litigation Intelligence System - Maximum Claude Utilisation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --full              # Run complete analysis
  python main.py --phase 0           # Run knowledge absorption
  python main.py --phase 1           # Run discovery phase
  python main.py --investigate contradiction --priority 9
  python main.py --status            # Show current status
  python main.py --reports           # Generate reports
  python main.py --reset             # Reset system
        """
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full analysis pipeline'
    )
    
    parser.add_argument(
        '--phase',
        type=str,
        choices=['0', '1', '2', '3', '4', '5', '6', '7'],
        help='Run specific phase'
    )
    
    parser.add_argument(
        '--investigate',
        type=str,
        help='Spawn investigation (e.g., contradiction, pattern, timeline)'
    )
    
    parser.add_argument(
        '--priority',
        type=float,
        default=7.0,
        help='Investigation priority (1-10)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status'
    )
    
    parser.add_argument(
        '--reports',
        action='store_true',
        help='Generate strategic reports'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset system (delete all analysis)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    args = parser.parse_args()
    
    # Initialise system
    try:
        system = LitigationIntelligence(config_path=args.config)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.full:
            system.run_full_analysis()
        
        elif args.phase:
            system.run_single_phase(args.phase)
        
        elif args.investigate:
            system.run_investigation(args.investigate, args.priority)
        
        elif args.status:
            system.show_status()
        
        elif args.reports:
            system.generate_reports()
        
        elif args.reset:
            system.reset()
        
        else:
            # Default: show status
            system.show_status()
            print("\nUse --help for options")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()