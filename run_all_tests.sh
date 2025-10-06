#!/bin/bash
# Quick test runner - runs full suite with proper environment

echo "🚀 Starting Guardr Complete Test Suite"
echo ""

# Load API keys
source /home/nobby/Kallisto-OSINTer/api-keys.zsh

# Check if backend is running
if ! curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "❌ Backend not running!"
    echo "   Start backend first: python guardr_api.py"
    exit 1
fi

# Run full test suite
python test_full_suite.py

# Capture exit code
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 All tests passed! Ready for deployment."
else
    echo "❌ Some tests failed. Review output above."
fi

exit $exit_code
