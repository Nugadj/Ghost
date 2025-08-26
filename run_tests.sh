#!/bin/bash
# Ghost Protocol Test Runner Script

echo "Ghost Protocol - Comprehensive Test Runner"
echo "=========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "Consider running: python -m venv ghost_protocol_env && source ghost_protocol_env/bin/activate"
fi

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# Run quick test
echo -e "\n1. Running Quick Test..."
python scripts/quick_test.py

# Run unit tests
echo -e "\n2. Running Unit Tests..."
python -m pytest tests/ -v --tb=short

# Run integration tests
echo -e "\n3. Running Integration Tests..."
python -m pytest tests/test_integration.py -v

# Run security tests
echo -e "\n4. Running Security Tests..."
python -m pytest tests/test_security.py -v

# Run comprehensive analysis
echo -e "\n5. Running Comprehensive Analysis..."
python scripts/run_comprehensive_tests.py

# Code quality checks
echo -e "\n6. Running Code Quality Checks..."
echo "Formatting check..."
black --check ghost_protocol/ || echo "Run 'black ghost_protocol/' to fix formatting"

echo "Linting check..."
flake8 ghost_protocol/ || echo "Fix linting issues reported above"

echo -e "\n=========================================="
echo "Test run complete!"
echo "Check the output above for any issues."
