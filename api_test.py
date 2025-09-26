# test_current_models.py
import os
from dotenv import load_dotenv
import anthropic

load_dotenv(override=True)
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Try current model names
models = [
    "claude-3-5-haiku-20241022",    # Haiku 3.5
    "claude-3-5-sonnet-latest",     # Sonnet 4
    "claude-3-opus-latest",          # Opus 4.x
    "claude-3-sonnet-20241022",     # Alternative Sonnet name
]

for model in models:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "test"}]
        )
        print(f"✅ {model} WORKS!")
        break
    except Exception as e:
        error = str(e)[:80]
        print(f"❌ {model}: {error}")