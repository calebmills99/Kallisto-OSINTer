#!/usr/bin/env python3
"""OpenRouter integration tests"""

import os
import sys
from src.llm.openrouter_client import OpenRouterClient

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    print("Testing: OpenRouter API connection...")
    try:
        key = os.getenv("OPEN_ROUTER_API_KEY")
        assert key, "OPEN_ROUTER_API_KEY not set"

        client = OpenRouterClient(api_key=key, default_model="openai/gpt-4o-mini")

        response = client.chat_completion(
            prompt="Say 'OK' if you can hear me",
            system_prompt="You are a test assistant",
            temperature=0.1,
            max_tokens=10
        )

        assert len(response) > 0, "Empty response from OpenRouter"
        print(f"  ✓ OpenRouter connected (response: '{response}')")
        return True
    except Exception as e:
        print(f"  ✗ OpenRouter connection failed: {e}")
        return False


def test_multiple_models():
    """Test different model availability"""
    print("Testing: Multiple model support...")
    try:
        key = os.getenv("OPEN_ROUTER_API_KEY")

        models_to_test = [
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
        ]

        results = []
        for model in models_to_test:
            try:
                client = OpenRouterClient(api_key=key, default_model=model)
                response = client.chat_completion(
                    prompt="Hi",
                    system_prompt="Brief",
                    temperature=0.1,
                    max_tokens=5
                )
                results.append(f"{model.split('/')[1]}: ✓")
            except Exception as e:
                results.append(f"{model.split('/')[1]}: ✗")

        print(f"  Models tested: {', '.join(results)}")
        return True
    except Exception as e:
        print(f"  ✗ Model testing failed: {e}")
        return False


def test_json_output():
    """Test structured JSON responses"""
    print("Testing: JSON-structured responses...")
    try:
        key = os.getenv("OPEN_ROUTER_API_KEY")
        client = OpenRouterClient(api_key=key, default_model="openai/gpt-4o-mini")

        response = client.chat_completion(
            prompt='Output exactly: {"status":"ok"}',
            system_prompt="You output only valid JSON",
            temperature=0.1,
            max_tokens=20
        )

        import json
        # Response might have markdown formatting
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        assert "status" in data, "JSON parsing failed"

        print(f"  ✓ JSON responses working")
        return True
    except Exception as e:
        print(f"  ✗ JSON test failed: {e}")
        return False


def test_rate_limiting():
    """Test rapid successive calls"""
    print("Testing: Rate limiting / rapid calls...")
    try:
        key = os.getenv("OPEN_ROUTER_API_KEY")
        client = OpenRouterClient(api_key=key, default_model="openai/gpt-4o-mini")

        # Make 3 rapid calls
        for i in range(3):
            response = client.chat_completion(
                prompt=f"Count: {i+1}",
                system_prompt="Brief",
                temperature=0.1,
                max_tokens=5
            )
            assert len(response) > 0

        print(f"  ✓ 3 rapid calls succeeded")
        return True
    except Exception as e:
        print(f"  ✗ Rate limiting test failed: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid requests"""
    print("Testing: Error handling...")
    try:
        # Test with invalid API key
        client = OpenRouterClient(api_key="invalid_key", default_model="openai/gpt-4o-mini")

        try:
            response = client.chat_completion(
                prompt="Test",
                system_prompt="Test",
                temperature=0.1,
                max_tokens=5
            )
            print(f"  ✗ Should have raised error with invalid key")
            return False
        except RuntimeError:
            print(f"  ✓ Invalid key correctly rejected")
            return True
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False


def main():
    """Run all OpenRouter tests"""
    print("\n" + "="*50)
    print("OPENROUTER LLM INTEGRATION TESTS")
    print("="*50 + "\n")

    # Load API keys
    os.system("source /home/nobby/Kallisto-OSINTer/api-keys.zsh")

    if not os.getenv("OPEN_ROUTER_API_KEY"):
        print("❌ OPEN_ROUTER_API_KEY not set in environment\n")
        return False

    tests = [
        test_openrouter_connection,
        test_multiple_models,
        test_json_output,
        test_rate_limiting,
        test_error_handling,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("="*50)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*50)

    if passed == total:
        print("✅ All OpenRouter tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
