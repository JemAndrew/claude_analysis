# src/main.py
"""
Main orchestrator for the 6-Phase Progressive Learning Investigation System
Opus 4.1 Enhanced for Lismore Capital v VR Capital Arbitration
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging

# Run the investigation using the investigator module
from investigator import ProgressiveLearningInvestigator

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run Opus 4.1 enhanced progressive learning investigation"""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Please add ANTHROPIC_API_KEY to your .env file")
        return
    
    print("\n" + "="*70)
    print("⚡ INITIALISING CLAUDE OPUS 4.1")
    print("🎯 Target: Complete Lismore Defence Victory")
    print("="*70)
    
    investigator = ProgressiveLearningInvestigator(
        api_key=api_key,
        project_root="."  # Using current directory structure
    )
    
    # Check for required directories
    required_dirs = [
        "documents/processed/text",
        "legal_resources",
        "case_context",
        "outputs",
        "memory"
    ]
    
    for dir_path in required_dirs:
        dir_path = Path(dir_path)
        if not dir_path.exists():
            print(f"⚠️ Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    print("\n✅ System ready. Beginning investigation...")
    
    try:
        await investigator.run_progressive_investigation()
        
        print("\n" + "="*70)
        print("🏆 INVESTIGATION COMPLETE")
        print("📊 Opus 4.1 has identified case-winning evidence")
        print("⚖️ Ready for tribunal deployment")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        print(f"\n❌ Investigation error: {e}")
        print("Please check logs for details")


if __name__ == "__main__":
    asyncio.run(main())