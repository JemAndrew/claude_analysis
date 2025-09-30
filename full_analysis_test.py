import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv(override=True)

from core.orchestrator import LitigationOrchestrator

orchestrator = LitigationOrchestrator()

print("Starting FULL AUTONOMOUS ANALYSIS...")
print("This will take 30-90 minutes and cost $20-50")
print("\nPress Ctrl+C to cancel, or wait 5 seconds to continue...")

import time
time.sleep(5)

results = orchestrator.execute_full_analysis(
    start_phase='0',
    max_iterations=5  # Start with 5 investigation iterations
)

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print(f"Check reports: {orchestrator.config.reports_dir}")