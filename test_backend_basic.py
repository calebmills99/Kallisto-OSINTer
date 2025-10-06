#!/usr/bin/env python3
"""Basic functionality tests for Guardr backend"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing: Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", "Service not healthy"
        assert data.get("service") == "Guardr API", "Wrong service name"
        print("  ✓ Health check passed")
        return True
    except Exception as e:
        print(f"  ✗ Health check failed: {e}")
        return False


def test_api_check_name_only():
    """Test API check with name only"""
    print("Testing: Name-only verification...")
    try:
        payload = {"name": "Test User"}
        response = requests.post(
            f"{BASE_URL}/api/check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "name" in data, "Missing name field"
        assert "risk_level" in data, "Missing risk_level"
        assert "safety_tips" in data, "Missing safety_tips"
        assert len(data["safety_tips"]) > 0, "No safety tips returned"
        print(f"  ✓ Name verification passed (risk: {data['risk_level']})")
        return True
    except Exception as e:
        print(f"  ✗ Name verification failed: {e}")
        return False


def test_api_check_with_location():
    """Test API check with name and location"""
    print("Testing: Name + location verification...")
    try:
        payload = {
            "name": "Jane Smith",
            "location": "Austin, TX"
        }
        response = requests.post(
            f"{BASE_URL}/api/check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("name") == "Jane Smith", "Name mismatch"
        assert data.get("location") == "Austin, TX", "Location mismatch"
        print(f"  ✓ Location verification passed")
        return True
    except Exception as e:
        print(f"  ✗ Location verification failed: {e}")
        return False


def test_api_check_invalid_request():
    """Test API with invalid/empty request"""
    print("Testing: Invalid request handling...")
    try:
        payload = {}  # Empty payload
        response = requests.post(
            f"{BASE_URL}/api/check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200, "Should handle empty payload gracefully"
        data = response.json()
        assert data.get("risk_level") is not None, "Should return default risk level"
        print("  ✓ Invalid request handled gracefully")
        return True
    except Exception as e:
        print(f"  ✗ Invalid request test failed: {e}")
        return False


def test_safety_tips_rotation():
    """Test that safety tips are randomized"""
    print("Testing: Safety tips rotation...")
    try:
        payload = {"name": "Test User"}

        # Make two requests
        response1 = requests.post(f"{BASE_URL}/api/check", json=payload, timeout=10)
        response2 = requests.post(f"{BASE_URL}/api/check", json=payload, timeout=10)

        tips1 = response1.json()["safety_tips"]
        tips2 = response2.json()["safety_tips"]

        # Check that tips are different (randomized)
        tips1_messages = [t["message"] for t in tips1]
        tips2_messages = [t["message"] for t in tips2]

        # At least one tip should be different
        different = any(t1 != t2 for t1, t2 in zip(tips1_messages, tips2_messages))
        assert different or len(tips1) != len(tips2), "Safety tips should be randomized"

        print("  ✓ Safety tips are randomized")
        return True
    except Exception as e:
        print(f"  ✗ Safety tips rotation test failed: {e}")
        return False


def main():
    """Run all backend tests"""
    print("\n" + "="*50)
    print("GUARDR BACKEND FUNCTIONALITY TESTS")
    print("="*50 + "\n")

    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running!")
        print("   Start with: python guardr_api.py")
        return False

    tests = [
        test_health_check,
        test_api_check_name_only,
        test_api_check_with_location,
        test_api_check_invalid_request,
        test_safety_tips_rotation,
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
        print("✅ All backend tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
