"""
Check which Claude models are being used in all Python files.
"""

import os
from pathlib import Path
import re

def check_models_in_files():
    """Scan all Python files for model strings."""
    
    # Known model strings
    known_models = {
        "claude-opus-4-1-20250805": "✅ Opus 4.1 (Most Powerful)",
        "claude-3-opus-20240229": "⚠️ Opus 3 (Old, deprecated)",
        "claude-3-5-sonnet-20241022": "⚠️ Sonnet 3.5 (Deprecated)",
        "claude-3-5-sonnet-latest": "❌ Invalid model string",
        "claude-3-haiku-20240307": "✓ Haiku (Fast, working)",
        "claude-opus-4-20250805": "❌ Invalid model string"
    }
    
    print("="*60)
    print("MODEL USAGE CHECK - ALL PYTHON FILES")
    print("="*60)
    
    # Get all Python files
    python_files = list(Path(".").glob("*.py"))
    
    findings = {}
    
    for file in python_files:
        if file.name == "check_models_in_code.py":
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find model strings
        models_found = []
        for model_string, description in known_models.items():
            if model_string in content:
                models_found.append((model_string, description))
        
        # Also check for generic model variable assignments
        model_patterns = [
            r'model\s*=\s*["\']([^"\']+)["\']',
            r'self\.model\s*=\s*["\']([^"\']+)["\']',
            r'"model":\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match not in [m[0] for m in models_found]:
                    if match in known_models:
                        models_found.append((match, known_models[match]))
                    else:
                        models_found.append((match, "❓ Unknown model"))
        
        if models_found:
            findings[file.name] = models_found
    
    # Display results
    if findings:
        print("\n📁 FILES AND THEIR MODELS:\n")
        for filename, models in findings.items():
            print(f"📄 {filename}:")
            for model, description in models:
                print(f"   {description}")
                print(f"   Model: {model}")
            print()
    else:
        print("\n⚠️ No model strings found in any Python files")
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    using_opus_41 = []
    using_old_models = []
    using_haiku = []
    
    for filename, models in findings.items():
        for model, desc in models:
            if "Opus 4.1" in desc:
                using_opus_41.append(filename)
            elif "⚠️" in desc or "❌" in desc:
                using_old_models.append(filename)
            elif "Haiku" in desc:
                using_haiku.append(filename)
    
    print(f"\n✅ Files using Opus 4.1: {len(set(using_opus_41))}")
    if using_opus_41:
        for f in set(using_opus_41):
            print(f"   - {f}")
    
    print(f"\n✓ Files using Haiku: {len(set(using_haiku))}")
    if using_haiku:
        for f in set(using_haiku):
            print(f"   - {f}")
    
    print(f"\n⚠️ Files using old/invalid models: {len(set(using_old_models))}")
    if using_old_models:
        for f in set(using_old_models):
            print(f"   - {f} (needs updating!)")
    
    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDED ACTION")
    print("="*60)
    
    if using_old_models:
        print("❗ You have files using outdated models. Update them to use:")
        print("   - For complex analysis: claude-opus-4-1-20250805")
        print("   - For quick tasks: claude-3-haiku-20240307")
    else:
        print("✅ All files are using current models!")
    
    print("\nTo update a file to use Opus 4.1, change the model string to:")
    print('   model = "claude-opus-4-1-20250805"')


def quick_test_opus():
    """Quick test to confirm Opus 4.1 is working."""
    print("\n" + "="*60)
    print("QUICK OPUS 4.1 TEST")
    print("="*60)
    
    from dotenv import load_dotenv
    from anthropic import Anthropic
    
    load_dotenv()
    
    try:
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        print("Testing Opus 4.1 connection...")
        response = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": "Say 'Opus 4.1 ready for Lismore analysis' if you're the most powerful model."
            }]
        )
        print(f"✅ Opus 4.1 says: {response.content[0].text}")
        return True
    except Exception as e:
        print(f"❌ Opus 4.1 test failed: {e}")
        return False


if __name__ == "__main__":
    # Check all files
    check_models_in_files()
    
    # Test Opus 4.1
    print("\nDo you want to test Opus 4.1 connection? (y/n): ", end="")
    if input().lower() == 'y':
        quick_test_opus()