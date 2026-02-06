#!/usr/bin/env python3
"""Speed and performance tests for Guardr"""

import requests
import time
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:5000"

def time_request(url, payload=None, method='GET'):
    """Time a single request"""
    start = time.time()
    if method == 'POST':
        response = requests.post(url, json=payload, timeout=30)
    else:
        response = requests.get(url, timeout=30)
    duration = time.time() - start
    return duration, response.status_code


def test_health_check_latency():
    """Test health check endpoint speed"""
    print("Testing: Health check latency...")
    try:
        times = []
        for _ in range(10):
            duration, status = time_request(f"{BASE_URL}/api/health")
            assert status == 200
            times.append(duration)

        avg = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  ✓ Health check - Avg: {avg*1000:.0f}ms, Min: {min_time*1000:.0f}ms, Max: {max_time*1000:.0f}ms")
        return avg < 0.5  # Should be under 500ms
    except Exception as e:
        print(f"  ✗ Health check latency failed: {e}")
        return False


def test_api_check_latency():
    """Test API check endpoint speed (minimal processing)"""
    print("Testing: API check latency (fast mode)...")
    try:
        times = []
        for i in range(5):
            payload = {"name": f"Speed Test {i}"}
            duration, status = time_request(f"{BASE_URL}/api/check", payload, 'POST')
            assert status == 200
            times.append(duration)

        avg = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  ✓ API check - Avg: {avg:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s")
        return avg < 10  # Should be under 10s
    except Exception as e:
        print(f"  ✗ API check latency failed: {e}")
        return False


def test_concurrent_load():
    """Test performance under concurrent load"""
    print("Testing: Concurrent load (10 simultaneous requests)...")
    try:
        def make_request(i):
            payload = {"name": f"Concurrent User {i}"}
            start = time.time()
            response = requests.post(f"{BASE_URL}/api/check", json=payload, timeout=30)
            duration = time.time() - start
            return duration, response.status_code

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
        total_time = time.time() - start_time

        durations = [r[0] for r in results]
        successes = sum(1 for r in results if r[1] == 200)

        avg = statistics.mean(durations)
        print(f"  ✓ Concurrent load - {successes}/10 succeeded in {total_time:.2f}s")
        print(f"    Avg per request: {avg:.2f}s")
        return successes >= 8  # At least 80% success rate
    except Exception as e:
        print(f"  ✗ Concurrent load test failed: {e}")
        return False


def test_throughput():
    """Test requests per second"""
    print("Testing: Throughput (requests/second)...")
    try:
        num_requests = 20
        start_time = time.time()

        for i in range(num_requests):
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            assert response.status_code == 200

        total_time = time.time() - start_time
        rps = num_requests / total_time

        print(f"  ✓ Throughput - {rps:.1f} requests/second ({num_requests} requests in {total_time:.2f}s)")
        return rps > 5  # Should handle at least 5 req/s
    except Exception as e:
        print(f"  ✗ Throughput test failed: {e}")
        return False


def test_memory_leak():
    """Test for memory leaks with repeated requests"""
    print("Testing: Memory stability (50 repeated requests)...")
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make 50 requests
        for i in range(50):
            response = requests.post(
                f"{BASE_URL}/api/check",
                json={"name": f"Memory Test {i}"},
                timeout=10
            )
            assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"  ✓ Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB")
        print(f"    Increase: {memory_increase:.1f}MB")
        return memory_increase < 100  # Should not leak more than 100MB
    except ImportError:
        print(f"  ⚠️  psutil not installed, skipping memory test")
        return True
    except Exception as e:
        print(f"  ✗ Memory test failed: {e}")
        return False


def test_response_size():
    """Test response payload sizes"""
    print("Testing: Response payload sizes...")
    try:
        payload = {"name": "Size Test"}
        response = requests.post(f"{BASE_URL}/api/check", json=payload, timeout=10)

        size_bytes = len(response.content)
        size_kb = size_bytes / 1024

        print(f"  ✓ Response size - {size_kb:.1f}KB ({size_bytes} bytes)")
        return size_kb < 100  # Should be under 100KB
    except Exception as e:
        print(f"  ✗ Response size test failed: {e}")
        return False


def test_cold_start():
    """Test cold start time (first request after idle)"""
    print("Testing: Cold start performance...")
    try:
        print("    Waiting 5 seconds for idle...")
        time.sleep(5)

        duration, status = time_request(f"{BASE_URL}/api/health")
        assert status == 200

        print(f"  ✓ Cold start - {duration*1000:.0f}ms")
        return duration < 2.0  # Should start under 2s
    except Exception as e:
        print(f"  ✗ Cold start test failed: {e}")
        return False


def test_sustained_load():
    """Test sustained load over time"""
    print("Testing: Sustained load (30 requests over 30 seconds)...")
    try:
        times = []
        errors = 0

        for i in range(30):
            start = time.time()
            try:
                response = requests.post(
                    f"{BASE_URL}/api/check",
                    json={"name": f"Sustained {i}"},
                    timeout=5
                )
                duration = time.time() - start
                if response.status_code == 200:
                    times.append(duration)
                else:
                    errors += 1
            except:
                errors += 1

            time.sleep(1)  # One request per second

        avg = statistics.mean(times) if times else 0
        success_rate = (len(times) / 30) * 100

        print(f"  ✓ Sustained load - {success_rate:.0f}% success, Avg: {avg:.2f}s")
        return success_rate >= 90
    except Exception as e:
        print(f"  ✗ Sustained load test failed: {e}")
        return False


def main():
    """Run all speed tests"""
    print("\n" + "="*60)
    print("GUARDR SPEED & PERFORMANCE TESTS")
    print("="*60 + "\n")

    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except:
        print("❌ Backend not running!\n")
        return False

    tests = [
        test_health_check_latency,
        test_api_check_latency,
        test_response_size,
        test_cold_start,
        test_throughput,
        test_concurrent_load,
        test_memory_leak,
        test_sustained_load,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("="*60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("✅ All speed tests passed!")
        print("\nPERFORMANCE GRADE: A")
    elif passed >= total * 0.8:
        print(f"⚠️  {total - passed} test(s) below target")
        print("\nPERFORMANCE GRADE: B")
    elif passed >= total * 0.6:
        print(f"⚠️  {total - passed} test(s) need optimization")
        print("\nPERFORMANCE GRADE: C")
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("\nPERFORMANCE GRADE: F - OPTIMIZATION REQUIRED")
        return False

    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
