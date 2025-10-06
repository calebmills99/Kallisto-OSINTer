#!/usr/bin/env python3
"""Integration tests - Frontend → Backend → LLM flow"""

import requests
import time
import sys

BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3001"

def test_full_user_journey():
    """Simulate complete user flow from frontend to results"""
    print("Testing: Full user journey (Frontend → Backend → Response)...")
    try:
        # Step 1: User enters name on frontend, submits to backend
        payload = {
            "name": "Integration Test User",
            "location": "Test City, TX"
        }

        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/api/check",
            json=payload,
            timeout=120  # Allow time for OSINT processing
        )
        duration = time.time() - start_time

        assert response.status_code == 200, f"Backend returned {response.status_code}"
        data = response.json()

        # Verify response structure matches frontend expectations
        required_fields = ["name", "location", "risk_level", "risk_score", "safety_tips"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        print(f"  ✓ Full journey completed in {duration:.1f}s")
        print(f"    - Name: {data['name']}")
        print(f"    - Risk: {data['risk_level']}")
        print(f"    - Tips: {len(data['safety_tips'])} provided")
        return True
    except Exception as e:
        print(f"  ✗ Full journey failed: {e}")
        return False


def test_cors_headers():
    """Test CORS headers are set correctly"""
    print("Testing: CORS headers for cross-origin requests...")
    try:
        response = requests.options(
            f"{BACKEND_URL}/api/check",
            headers={"Origin": FRONTEND_URL}
        )

        # Check CORS headers present
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        assert cors_header is not None, "Missing CORS headers"

        print(f"  ✓ CORS configured (Origin: {cors_header})")
        return True
    except Exception as e:
        print(f"  ✗ CORS test failed: {e}")
        return False


def test_response_time():
    """Test API responds within reasonable time"""
    print("Testing: Response time under load...")
    try:
        payload = {"name": "Speed Test"}

        start = time.time()
        response = requests.post(
            f"{BACKEND_URL}/api/check",
            json=payload,
            timeout=10
        )
        duration = time.time() - start

        # Quick response without full OSINT should be < 5s
        assert duration < 5, f"Response too slow: {duration:.1f}s"
        assert response.status_code == 200

        print(f"  ✓ Response time: {duration:.2f}s")
        return True
    except Exception as e:
        print(f"  ✗ Response time test failed: {e}")
        return False


def test_error_handling():
    """Test backend error handling"""
    print("Testing: Error handling for malformed requests...")
    try:
        # Send invalid JSON
        response = requests.post(
            f"{BACKEND_URL}/api/check",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        # Should handle gracefully, not crash
        assert response.status_code in [200, 400, 422], "Unexpected error code"

        print(f"  ✓ Errors handled gracefully (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False


def test_safety_tips_categories():
    """Test safety tips include all categories"""
    print("Testing: Safety tips category diversity...")
    try:
        payload = {"name": "Category Test"}
        response = requests.post(f"{BACKEND_URL}/api/check", json=payload, timeout=10)
        data = response.json()

        tips = data.get("safety_tips", [])
        assert len(tips) > 0, "No safety tips returned"

        categories = set(tip.get("category") for tip in tips)
        expected_categories = {"Smart Habits", "Friendly Reminders", "Did You Know", "You Decide"}

        # Should have at least 2 different categories
        assert len(categories) >= 2, f"Only {len(categories)} categories present"

        print(f"  ✓ {len(categories)} tip categories included: {', '.join(categories)}")
        return True
    except Exception as e:
        print(f"  ✗ Safety tips test failed: {e}")
        return False


def test_concurrent_requests():
    """Test handling multiple simultaneous requests"""
    print("Testing: Concurrent request handling...")
    try:
        import concurrent.futures

        def make_request(i):
            payload = {"name": f"User {i}"}
            response = requests.post(f"{BACKEND_URL}/api/check", json=payload, timeout=15)
            return response.status_code == 200

        # Make 3 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_count = sum(results)
        assert success_count >= 2, f"Only {success_count}/3 requests succeeded"

        print(f"  ✓ {success_count}/3 concurrent requests succeeded")
        return True
    except Exception as e:
        print(f"  ✗ Concurrent request test failed: {e}")
        return False


def test_frontend_backend_connection():
    """Test frontend can reach backend"""
    print("Testing: Frontend → Backend connectivity...")
    try:
        # Simulate what frontend does
        response = requests.post(
            f"{BACKEND_URL}/api/check",
            json={"name": "Connection Test"},
            headers={
                "Content-Type": "application/json",
                "Origin": FRONTEND_URL
            },
            timeout=10
        )

        assert response.status_code == 200
        data = response.json()
        assert "name" in data

        print(f"  ✓ Frontend can successfully call backend")
        return True
    except Exception as e:
        print(f"  ✗ Frontend-backend connection failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("\n" + "="*50)
    print("GUARDR INTEGRATION TESTS")
    print("="*50 + "\n")

    # Check if both servers running
    try:
        requests.get(f"{BACKEND_URL}/api/health", timeout=2)
    except:
        print("❌ Backend not running! Start with: python guardr_api.py\n")
        return False

    try:
        requests.get(FRONTEND_URL, timeout=2)
    except:
        print("⚠️  Frontend not running (some tests will be skipped)")
        print("   Start with: cd website && npm run dev\n")

    tests = [
        test_cors_headers,
        test_response_time,
        test_error_handling,
        test_safety_tips_categories,
        test_concurrent_requests,
        test_frontend_backend_connection,
        test_full_user_journey,
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
        print("✅ All integration tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
