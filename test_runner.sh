#!/bin/bash
# Ghost Protocol Test Runner for Linux/Mac

echo "Ghost Protocol Test Runner"
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7 or higher."
    exit 1
fi

echo "🔍 Running environment debug..."
python3 scripts/debug_environment.py

echo -e "\n🧪 Running comprehensive tests..."
python3 scripts/run_all_tests.py

echo -e "\n✅ Test run complete!"
