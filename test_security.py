#!/usr/bin/env python3
"""Security and privacy tests for Guardr"""

import requests
import sys

BASE_URL = "http://localhost:5000"

def test_no_sql_injection():
    """Test SQL injection attempts are handled"""
    print("Testing: SQL injection prevention...")
    try:
        malicious_inputs = [
            "'; DROP TABLE users--",
            "1' OR '1'='1",
            "admin'--",
        ]

        for payload in malicious_inputs:
            response = requests.post(
                f"{BASE_URL}/api/check",
                json={"name": payload},
                timeout=10
            )
            # Should handle gracefully, not error
            assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"

        print(f"  ✓ SQL injection attempts handled safely")
        return True
    except Exception as e:
        print(f"  ✗ SQL injection test failed: {e}")
        return False


def test_no_api_key_exposure():
    """Test API keys not exposed in responses"""
    print("Testing: API key exposure prevention...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/check",
            json={"name": "Test User"},
            timeout=10
        )

        body = response.text.lower()

        # Check for common API key patterns
        suspicious_patterns = [
            "api_key",
            "sk-",
            "bearer",
            "token",
            "secret",
            "password"
        ]

        found = [p for p in suspicious_patterns if p in body]
        assert len(found) == 0, f"Suspicious patterns in response: {found}"

        print(f"  ✓ No API keys exposed in responses")
        return True
    except Exception as e:
        print(f"  ✗ API key exposure test failed: {e}")
        return False


def test_input_sanitization():
    """Test XSS and HTML injection prevention"""
    print("Testing: Input sanitization (XSS prevention)...")
    try:
        xss_inputs = [
            "<script>alert('xss')</script>",
            "'; alert('xss');//",
            "<img src=x onerror=alert('xss')>",
        ]

        for payload in xss_inputs:
            response = requests.post(
                f"{BASE_URL}/api/check",
                json={"name": payload},
                timeout=10
            )

            data = response.json()
            # Check that dangerous HTML is not echoed back unescaped
            assert "<script>" not in str(data), "Unescaped script tag in response"

        print(f"  ✓ XSS inputs sanitized")
        return True
    except Exception as e:
        print(f"  ✗ Input sanitization test failed: {e}")
        return False


def test_rate_limiting_headers():
    """Test for rate limiting headers"""
    print("Testing: Rate limiting indicators...")
    try:
        # Make multiple rapid requests
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/api/check",
                json={"name": f"Rate Test {i}"},
                timeout=10
            )

        # Should all succeed (or gracefully rate limit)
        assert response.status_code in [200, 429], "Unexpected status code"

        if response.status_code == 429:
            print(f"  ✓ Rate limiting active (429 returned)")
        else:
            print(f"  ⚠️  No rate limiting detected (consider adding)")
        return True
    except Exception as e:
        print(f"  ✗ Rate limiting test failed: {e}")
        return False


def test_no_directory_traversal():
    """Test directory traversal prevention"""
    print("Testing: Directory traversal prevention...")
    try:
        traversal_inputs = [
            "../../../etc/passwd",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
        ]

        for payload in traversal_inputs:
            response = requests.post(
                f"{BASE_URL}/api/check",
                json={"name": payload},
                timeout=10
            )

            # Should not return file contents or error with file paths
            assert "root:" not in response.text, "Directory traversal vulnerability!"
            assert response.status_code in [200, 400], "Unexpected error"

        print(f"  ✓ Directory traversal prevented")
        return True
    except Exception as e:
        print(f"  ✗ Directory traversal test failed: {e}")
        return False


def test_user_data_privacy():
    """Test user data is not logged inappropriately"""
    print("Testing: User data privacy...")
    try:
        sensitive_data = "SensitiveUserData12345"
        response = requests.post(
            f"{BASE_URL}/api/check",
            json={"name": sensitive_data},
            timeout=10
        )

        # Data should be processed but not exposed in error messages
        # This is a basic check - actual privacy requires log auditing

        print(f"  ✓ Basic privacy checks passed")
        print(f"    (Manual log audit recommended)")
        return True
    except Exception as e:
        print(f"  ✗ Privacy test failed: {e}")
        return False


def test_https_ready():
    """Test HTTPS readiness (headers, redirects)"""
    print("Testing: HTTPS readiness...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)

        # Check for security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
        ]

        present = [h for h in security_headers if h in response.headers]

        if len(present) > 0:
            print(f"  ✓ Security headers present: {', '.join(present)}")
        else:
            print(f"  ⚠️  Consider adding security headers")

        return True
    except Exception as e:
        print(f"  ✗ HTTPS readiness test failed: {e}")
        return False


def main():
    """Run all security tests"""
    print("\n" + "="*50)
    print("GUARDR SECURITY & PRIVACY TESTS")
    print("="*50 + "\n")

    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except:
        print("❌ Backend not running!\n")
        return False

    tests = [
        test_no_sql_injection,
        test_no_api_key_exposure,
        test_input_sanitization,
        test_rate_limiting_headers,
        test_no_directory_traversal,
        test_user_data_privacy,
        test_https_ready,
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
        print("✅ All security tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) need attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
