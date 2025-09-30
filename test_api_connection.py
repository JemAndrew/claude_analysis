import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv(override=True)

import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

models = [
    'claude-sonnet-4-5-20250929',      # Sonnet 4.5
    'claude-opus-4-1-20250805',        # Opus 4.1
    'claude-3-5-sonnet-20241022',      # Sonnet 3.5
    'claude-3-haiku-20240307',         # Haiku 3
    'claude-3-opus-20240229',          # Opus 3
]

print("Testing model access...\n")

for model in models:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        print(f"✅ {model} WORKS")
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"❌ {model}: {error_msg}")