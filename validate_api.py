#!/usr/bin/env python3
"""
Quick API Validation Script
Tests if API calls will work BEFORE running full caching process
British English throughout
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
current_dir = Path(__file__).resolve().parent
for _ in range(5):
    env_path = current_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break
    current_dir = current_dir.parent

import anthropic
from typing import Dict, Any


def validate_api_params(api_params: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate that API parameters are correctly formatted
    
    Returns:
        (is_valid, error_message)
    """
    # Check all keys are strings
    non_string_keys = [k for k in api_params.keys() if not isinstance(k, str)]
    if non_string_keys:
        return False, f"Non-string keys found: {non_string_keys}"
    
    # Check required parameters
    required_params = ['model', 'max_tokens', 'messages']
    missing_params = [p for p in required_params if p not in api_params]
    if missing_params:
        return False, f"Missing required parameters: {missing_params}"
    
    # Validate messages format
    if not isinstance(api_params['messages'], list):
        return False, "messages must be a list"
    
    for msg in api_params['messages']:
        if not isinstance(msg, dict):
            return False, "Each message must be a dict"
        if 'role' not in msg or 'content' not in msg:
            return False, "Each message needs 'role' and 'content'"
    
    # Validate thinking parameter if present
    if 'thinking' in api_params:
        thinking = api_params['thinking']
        if not isinstance(thinking, dict):
            return False, "'thinking' must be a dict"
        if 'type' not in thinking or thinking['type'] != 'enabled':
            return False, "'thinking' must have type='enabled'"
        if 'budget_tokens' not in thinking:
            return False, "'thinking' must have 'budget_tokens'"
    
    return True, "All validations passed"


def test_basic_call():
    """Test a basic API call without extended thinking"""
    print("\n" + "="*70)
    print("TEST 1: Basic API Call (no extended thinking)")
    print("="*70)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build basic API params
    api_params = {
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 100,
        'temperature': 1.0,
        'messages': [
            {'role': 'user', 'content': 'Say "API test successful" in exactly 3 words'}
        ]
    }
    
    # Validate params
    is_valid, msg = validate_api_params(api_params)
    if not is_valid:
        print(f"❌ Validation failed: {msg}")
        return False
    
    print(f"✅ Parameters validated: {msg}")
    
    # Test API call
    try:
        print("📡 Calling Claude API...")
        response = client.messages.create(**api_params)
        response_text = response.content[0].text
        print(f"✅ API call successful!")
        print(f"   Response: {response_text}")
        print(f"   Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
        return True
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        return False


def test_extended_thinking_call():
    """Test API call WITH extended thinking"""
    print("\n" + "="*70)
    print("TEST 2: Extended Thinking Call")
    print("="*70)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build API params with extended thinking
    api_params = {
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 16000,
        'temperature': 1.0,  # ✅ STRING KEY, not variable value
        'messages': [
            {
                'role': 'user',
                'content': 'Think carefully about why 2+2=4, then explain in 20 words.'
            }
        ],
        'thinking': {
            'type': 'enabled',
            'budget_tokens': 10000
        }
    }
    
    # Validate params
    is_valid, msg = validate_api_params(api_params)
    if not is_valid:
        print(f"❌ Validation failed: {msg}")
        return False
    
    print(f"✅ Parameters validated: {msg}")
    
    # Test API call
    try:
        print("🧠 Calling Claude API with extended thinking...")
        response = client.messages.create(**api_params)
        
        # Extract response
        response_text = ""
        thinking_text = ""
        
        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == 'thinking':
                    thinking_text = getattr(block, 'thinking', '')
                elif block.type == 'text':
                    response_text += block.text
        
        print(f"✅ API call successful!")
        print(f"   Thinking tokens: {len(thinking_text.split())}")
        print(f"   Response: {response_text[:100]}...")
        print(f"   Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        return False


def test_with_cache():
    """Test API call with prompt caching"""
    print("\n" + "="*70)
    print("TEST 3: Prompt Caching Call")
    print("="*70)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build API params with caching
    system = [
        {
            "type": "text",
            "text": "You are a legal assistant analysing tribunal documents for Lismore.",
            "cache_control": {"type": "ephemeral"}
        },
        {
            "type": "text",
            "text": "<pleadings>This is cached pleadings text...</pleadings>",
            "cache_control": {"type": "ephemeral"}
        }
    ]
    
    api_params = {
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 16000,
        'temperature': 1.0,
        'system': system,
        'messages': [
            {'role': 'user', 'content': 'Summarise the pleadings in 10 words'}
        ]
    }
    
    # Validate params
    is_valid, msg = validate_api_params(api_params)
    if not is_valid:
        print(f"❌ Validation failed: {msg}")
        return False
    
    print(f"✅ Parameters validated: {msg}")
    
    # Test API call
    try:
        print("💾 Calling Claude API with prompt caching...")
        response = client.messages.create(**api_params)
        
        response_text = response.content[0].text
        usage = response.usage
        
        print(f"✅ API call successful!")
        print(f"   Response: {response_text}")
        print(f"   Cache creation: {getattr(usage, 'cache_creation_input_tokens', 0)} tokens")
        print(f"   Cache read: {getattr(usage, 'cache_read_input_tokens', 0)} tokens")
        print(f"   Input: {usage.input_tokens}, Output: {usage.output_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        return False


def test_combined_cache_and_thinking():
    """Test API call with BOTH caching AND extended thinking"""
    print("\n" + "="*70)
    print("TEST 4: Caching + Extended Thinking (YOUR ACTUAL USE CASE)")
    print("="*70)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build system with caching
    system = [
        {
            "type": "text",
            "text": "You are a legal assistant. Think carefully about all questions.",
            "cache_control": {"type": "ephemeral"}
        }
    ]
    
    # Build API params with BOTH features
    api_params = {
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 200,
        'temperature': 1.0,  # ✅ CRITICAL: String key 'temperature', not variable
        'system': system,
        'messages': [
            {
                'role': 'user',
                'content': 'What are 3 key elements of a strong legal argument? Think step by step.'
            }
        ],
        'thinking': {
            'type': 'enabled',
            'budget_tokens': 10000
        }
    }
    
    # Validate params
    is_valid, msg = validate_api_params(api_params)
    if not is_valid:
        print(f"❌ Validation failed: {msg}")
        print(f"   API params keys: {list(api_params.keys())}")
        print(f"   Non-string keys: {[k for k in api_params.keys() if not isinstance(k, str)]}")
        return False
    
    print(f"✅ Parameters validated: {msg}")
    
    # Test API call
    try:
        print("🧠💾 Calling Claude API with caching + thinking...")
        response = client.messages.create(**api_params)
        
        # Extract response and thinking
        response_text = ""
        thinking_text = ""
        
        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == 'thinking':
                    thinking_text = getattr(block, 'thinking', '')
                elif block.type == 'text':
                    response_text += block.text
        
        usage = response.usage
        
        print(f"✅ API call successful!")
        print(f"   Thinking: {len(thinking_text.split())} words")
        print(f"   Response: {response_text[:80]}...")
        print(f"   Cache creation: {getattr(usage, 'cache_creation_input_tokens', 0)} tokens")
        print(f"   Cache read: {getattr(usage, 'cache_read_input_tokens', 0)} tokens")
        print(f"   Input: {usage.input_tokens}, Output: {usage.output_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        print(f"   This is the error your actual code is hitting!")
        return False


def main():
    """Run all validation tests"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "API VALIDATION SUITE" + " "*28 + "║")
    print("║" + " "*15 + "Tests API calls before caching" + " "*23 + "║")
    print("╚" + "═"*68 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("Basic Call", test_basic_call()))
    results.append(("Extended Thinking", test_extended_thinking_call()))
    results.append(("Caching", test_with_cache()))
    results.append(("Caching + Thinking", test_combined_cache_and_thinking()))
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 All tests passed! Your API calls will work.")
        print("   You can now run the full caching process with confidence.")
        return 0
    else:
        print("\n❌ Some tests failed. Fix these issues before running full process.")
        print("   This saves you from waiting 15 minutes only to hit an error!")
        return 1


if __name__ == '__main__':
    sys.exit(main())