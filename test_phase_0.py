import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment variables BEFORE importing anything else
from dotenv import load_dotenv
load_dotenv(override=True)  # Add override=True

from core.orchestrator import LitigationOrchestrator

orchestrator = LitigationOrchestrator()

print("Executing Phase 0: Legal Knowledge...")
results = orchestrator.execute_phase('0')

print(f"\nPhase 0 Complete!")
print(f"Documents: {results.get('documents_processed', 0)}")
print(f"Tokens: {results['metadata']['input_tokens']:,} in / {results['metadata']['output_tokens']:,} out")