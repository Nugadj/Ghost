@echo off
REM Ghost Protocol Test Runner for Windows

echo Ghost Protocol Test Runner
echo ==========================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo 🔍 Running environment debug...
python scripts/debug_environment.py

echo.
echo 🧪 Running comprehensive tests...
python scripts/run_all_tests.py

echo.
echo ✅ Test run complete!
pause
