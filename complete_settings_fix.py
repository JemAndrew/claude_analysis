# complete_settings_fix.py - Check what api_client.py needs and fix it
import json
from pathlib import Path

print("="*60)
print("ANALYZING API_CLIENT.PY REQUIREMENTS")
print("="*60)

# Read api_client.py to understand what it expects
api_client_path = Path("src/api_client.py")
with open(api_client_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find all references to self.settings and self.model_config
print("\nFound settings references:")
for i, line in enumerate(lines, start=1):
    if 'self.model_config[' in line or 'self.settings[' in line:
        if i > 195 and i < 220:  # Around the __init__ method
            print(f"Line {i}: {line.strip()}")

# Based on line 206: self.opus_model = self.model_config['primary']['name']
# The structure needs to be:
correct_settings = {
    "model": {
        "primary": {
            "name": "claude-opus-4-1-20250805",
            "max_tokens": 4000
        },
        "secondary": {
            "name": "claude-3-haiku-20240307",
            "max_tokens": 2000
        },
        "temperature": {
            "phase_0a": 0.3,
            "phase_0b": 0.3,
            "phase_1": 0.3,
            "phase_2": 0.3,
            "phase_3": 0.4,
            "phase_4": 0.4,
            "phase_5": 0.5,
            "phase_6": 0.5,
            "phase_7": 0.7,
            "default": 0.3
        },
        "haiku_phases": ["phase_0a", "phase_0b", "phase_1"],
        "opus_phases": ["phase_2", "phase_3", "phase_4", "phase_5", "phase_6", "phase_7"]
    },
    "investigation": {
        "max_tokens": 4000,
        "haiku_max_tokens": 2000,
        "batch_size": 5,
        "rate_limit_delay": 3
    },
    "api": {
        "rate_limit": 20,
        "timeout": 60,
        "max_retries": 3
    }
}

# Save the corrected settings
settings_path = Path("config/settings.json")
with open(settings_path, 'w') as f:
    json.dump(correct_settings, f, indent=2)

print("\n✅ Created correct settings structure at config/settings.json")
print("\nSettings structure now includes:")
print("  - model.primary.name: claude-opus-4-1-20250805")
print("  - model.secondary.name: claude-3-haiku-20240307")
print("  - model.temperature: phase-specific settings")
print("  - investigation: max_tokens and other settings")

# Also check if .env file has API key
env_path = Path("config/.env")
if env_path.exists():
    with open(env_path, 'r') as f:
        content = f.read()
        if 'ANTHROPIC_API_KEY=' in content and 'your_api_key_here' not in content:
            print("\n✅ API key appears to be set in config/.env")
        else:
            print("\n⚠️  Remember to add your actual API key to config/.env")
            print("    Edit config/.env and replace 'your_api_key_here' with your key")
else:
    print("\n⚠️  No .env file found at config/.env")
    with open(env_path, 'w') as f:
        f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
    print("    Created config/.env - ADD YOUR API KEY")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. If you haven't already, add your API key to config/.env")
print("2. Run: python test_phase_0a.py --quick")
print("\nThis should now work!")