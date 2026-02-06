#!/usr/bin/env python3
"""Complete test suite runner - All tests in one go"""

import subprocess
import sys
import time

TEST_SUITES = [
    ("Backend Basic", "test_backend_basic.py"),
    ("Integration", "test_integration.py"),
    ("OpenRouter LLM", "test_openrouter.py"),
    ("Security & Privacy", "test_security.py"),
    ("Speed & Performance", "test_speed.py"),
]

def run_test_suite(name, script):
    """Run a single test suite"""
    print(f"\n{'='*70}")
    print(f"RUNNING: {name}")
    print(f"{'='*70}\n")

    try:
        # Source env vars and run test
        result = subprocess.run(
            f"source /home/nobby/Kallisto-OSINTer/api-keys.zsh && python {script}",
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=300
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Test suite '{name}' timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Test suite '{name}' crashed: {e}")
        return False


def check_prerequisites():
    """Check if backend and frontend are running"""
    import requests

    backend_running = False
    frontend_running = False

    try:
        requests.get("http://localhost:5000/api/health", timeout=2)
        backend_running = True
    except:
        pass

    try:
        requests.get("http://localhost:3001", timeout=2)
        frontend_running = True
    except:
        pass

    return backend_running, frontend_running


def main():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("GUARDR COMPLETE TEST SUITE")
    print("="*70)

    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    backend_running, frontend_running = check_prerequisites()

    if not backend_running:
        print("❌ Backend is NOT running (http://localhost:5000)")
        print("   Start with: python guardr_api.py")
        print("\n⚠️  Continuing with limited tests...\n")
    else:
        print("✓ Backend is running")

    if not frontend_running:
        print("⚠️  Frontend is NOT running (http://localhost:3001)")
        print("   Start with: cd website && npm run dev")
        print("   Some integration tests will be skipped\n")
    else:
        print("✓ Frontend is running")

    if not backend_running:
        print("\n❌ Cannot run tests without backend. Exiting.\n")
        return False

    time.sleep(2)

    # Run all test suites
    results = {}
    start_time = time.time()

    for name, script in TEST_SUITES:
        success = run_test_suite(name, script)
        results[name] = success
        time.sleep(1)  # Brief pause between suites

    total_time = time.time() - start_time

    # Final summary
    print("\n" + "="*70)
    print("COMPLETE TEST SUITE SUMMARY")
    print("="*70)

    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} - {name}")

    passed = sum(results.values())
    total = len(results)

    print("\n" + "="*70)
    print(f"OVERALL: {passed}/{total} test suites passed")
    print(f"Total execution time: {total_time/60:.1f} minutes")
    print("="*70)

    if passed == total:
        print("\n🎉 ALL TEST SUITES PASSED!")
        print("\n✅ GUARDR IS READY FOR DEPLOYMENT")
        return True
    elif passed >= total * 0.8:
        print(f"\n⚠️  {total - passed} suite(s) failed")
        print("\n🔧 REVIEW FAILURES BEFORE DEPLOYMENT")
        return False
    else:
        print(f"\n❌ {total - passed} suite(s) failed")
        print("\n🚫 NOT READY FOR DEPLOYMENT")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
        sys.exit(1)
