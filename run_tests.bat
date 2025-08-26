@echo off
REM Ghost Protocol Test Runner Script for Windows

echo Ghost Protocol - Comprehensive Test Runner
echo ==========================================

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Warning: No virtual environment detected
    echo Consider running: python -m venv ghost_protocol_env ^&^& ghost_protocol_env\Scripts\activate
)

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt
pip install -e .

REM Run quick test
echo.
echo 1. Running Quick Test...
python scripts/quick_test.py

REM Run unit tests
echo.
echo 2. Running Unit Tests...
python -m pytest tests/ -v --tb=short

REM Run integration tests
echo.
echo 3. Running Integration Tests...
python -m pytest tests/test_integration.py -v

REM Run security tests
echo.
echo 4. Running Security Tests...
python -m pytest tests/test_security.py -v

REM Run comprehensive analysis
echo.
echo 5. Running Comprehensive Analysis...
python scripts/run_comprehensive_tests.py

REM Code quality checks
echo.
echo 6. Running Code Quality Checks...
echo Formatting check...
black --check ghost_protocol/ || echo Run 'black ghost_protocol/' to fix formatting

echo Linting check...
flake8 ghost_protocol/ || echo Fix linting issues reported above

echo.
echo ==========================================
echo Test run complete!
echo Check the output above for any issues.
pause
