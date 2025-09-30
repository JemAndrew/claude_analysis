#!/usr/bin/env python3
"""
Test Additional Claude Models Including Opus 4.1
Checks for newer models and API access levels
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic, APIError

# Colour codes
class Colours:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def test_model_detailed(client, model_name):
    """Test a model with detailed error reporting"""
    try:
        print(f"\n{Colours.CYAN}Testing: {model_name}{Colours.RESET}")
        
        response = client.messages.create(
            model=model_name,
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'Model working'"}]
        )
        
        print(f"{Colours.GREEN}  ✅ SUCCESS!{Colours.RESET}")
        print(f"  Response: {response.content[0].text[:50]}")
        return True, "Working"
        
    except APIError as e:
        error_dict = e.response.json() if hasattr(e, 'response') else {}
        error_type = error_dict.get('error', {}).get('type', 'unknown')
        error_msg = error_dict.get('error', {}).get('message', str(e))
        
        print(f"{Colours.RED}  ❌ FAILED{Colours.RESET}")
        print(f"  Error type: {error_type}")
        print(f"  Message: {error_msg}")
        
        # Specific error analysis
        if "not_found_error" in error_type:
            print(f"  → Model doesn't exist or no access")
        elif "authentication_error" in error_type:
            print(f"  → API key issue")
        elif "permission_error" in error_type:
            print(f"  → No permission for this model")
        elif "rate_limit_error" in error_type:
            print(f"  → Rate limited (model exists!)")
        elif "overloaded_error" in error_type:
            print(f"  → API overloaded (model exists!)")
            
        return False, error_msg
        
    except Exception as e:
        print(f"{Colours.RED}  ❌ UNEXPECTED ERROR{Colours.RESET}")
        print(f"  Error: {str(e)[:100]}")
        return False, str(e)


def main():
    print(f"\n{Colours.BOLD}{Colours.BLUE}{'='*60}{Colours.RESET}")
    print(f"{Colours.BOLD}{Colours.BLUE}   TESTING OPUS 4.1 AND ADDITIONAL MODELS{Colours.RESET}")
    print(f"{Colours.BOLD}{Colours.BLUE}{'='*60}{Colours.RESET}")
    
    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print(f"{Colours.RED}No API key found{Colours.RESET}")
        return
        
    print(f"\n{Colours.GREEN}API Key:{Colours.RESET} {api_key[:20]}...{api_key[-4:]}")
    
    # Check key type
    if "sk-ant-api03-" in api_key:
        print(f"{Colours.CYAN}Key Type:{Colours.RESET} Standard API Key (api03)")
    elif "sk-ant-" in api_key:
        print(f"{Colours.CYAN}Key Type:{Colours.RESET} API Key")
    else:
        print(f"{Colours.YELLOW}Key Type:{Colours.RESET} Unknown format")
    
    client = Anthropic(api_key=api_key)
    
    # Test comprehensive model list
    print(f"\n{Colours.BOLD}Testing All Possible Models:{Colours.RESET}")
    print("="*60)
    
    models_to_test = [
        # Opus 4 variants (hypothetical)
        "claude-opus-4-1-20250805",
        "claude-opus-4-20250805",
        "claude-4-opus-20250805",
        
        # Current Opus 3 variants
        "claude-3-opus-20240229",
        "claude-3-opus",
        "opus-3",
        
        # Sonnet 3.5 variants
        "claude-3-5-sonnet-20241022",
        "claude-3.5-sonnet-20241022",
        "claude-3-5-sonnet",
        
        # Sonnet 3 variants
        "claude-3-sonnet-20240229",
        "claude-3-sonnet",
        
        # Haiku variants
        "claude-3-haiku-20240307",
        "claude-3-haiku",
        
        # Possible alternate names
        "claude-opus",
        "claude-sonnet",
        "claude-haiku",
    ]
    
    working_models = []
    
    for model in models_to_test:
        success, message = test_model_detailed(client, model)
        if success:
            working_models.append(model)
        time.sleep(0.5)  # Avoid rate limiting
    
    # Summary
    print(f"\n{Colours.BOLD}{Colours.BLUE}{'='*60}{Colours.RESET}")
    print(f"{Colours.BOLD}{Colours.BLUE}   SUMMARY{Colours.RESET}")
    print(f"{Colours.BOLD}{Colours.BLUE}{'='*60}{Colours.RESET}")
    
    if working_models:
        print(f"\n{Colours.GREEN}✅ Working Models ({len(working_models)}):{Colours.RESET}")
        for model in working_models:
            print(f"  • {model}")
    else:
        print(f"\n{Colours.RED}❌ No models working{Colours.RESET}")
    
    # Diagnosis
    print(f"\n{Colours.BOLD}{Colours.YELLOW}📊 DIAGNOSIS:{Colours.RESET}")
    
    if len(working_models) == 0:
        print(f"{Colours.RED}Critical Issue: No models accessible{Colours.RESET}")
        print("\nPossible reasons:")
        print("1. API key has no credits")
        print("2. API key is restricted/limited")
        print("3. Account needs upgrade")
        
    elif len(working_models) == 1 and "haiku" in working_models[0].lower():
        print(f"{Colours.YELLOW}Limited Access: Only Haiku available{Colours.RESET}")
        print("\nThis suggests:")
        print("1. You may have a limited/trial API key")
        print("2. Your account tier only includes Haiku access")
        print("3. You need to upgrade for Opus/Sonnet access")
        
        print(f"\n{Colours.BOLD}For Lismore Analysis:{Colours.RESET}")
        print("• Haiku can handle document classification")
        print("• But complex analysis needs Opus/Sonnet")
        print("• Consider upgrading your API access")
        
    else:
        print(f"{Colours.GREEN}Good Access: Multiple models available{Colours.RESET}")
    
    # Check API account
    print(f"\n{Colours.BOLD}{Colours.CYAN}📝 NEXT STEPS:{Colours.RESET}")
    print("1. Check your Anthropic Console: https://console.anthropic.com")
    print("2. Verify your plan/tier in Settings")
    print("3. Check available models for your account")
    print("4. Ensure you have credits available")
    
    if "haiku" in str(working_models).lower():
        print(f"\n{Colours.BOLD}With Haiku only, you can still:{Colours.RESET}")
        print("• Classify documents")
        print("• Extract basic information")
        print("• Do initial document review")
        print("• But deep analysis will be limited")
    
    # Save results
    results = {
        "test_time": datetime.now().isoformat(),
        "api_key_preview": f"{api_key[:20]}...{api_key[-4:]}",
        "working_models": working_models,
        "models_tested": len(models_to_test),
        "diagnosis": "limited_access" if len(working_models) <= 1 else "normal"
    }
    
    with open("api_access_test.json", "w") as f:
        import json
        json.dump(results, f, indent=2)
    
    print(f"\n{Colours.CYAN}Results saved to: api_access_test.json{Colours.RESET}")


if __name__ == "__main__":
    main()