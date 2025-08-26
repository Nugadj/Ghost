#!/usr/bin/env python3
"""
Comprehensive Test Runner for Ghost Protocol
Runs all tests and provides detailed error reporting
"""

import sys
import os
import subprocess
import importlib
import traceback
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n{'-'*40}")
    print(f"{title}")
    print(f"{'-'*40}")

def run_command(cmd, description):
    """Run a command and return success status and output"""
    print(f"\n🔄 {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            if result.stdout.strip():
                print(f"Output:\n{result.stdout}")
        else:
            print(f"❌ FAILED (Exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"Error:\n{result.stderr}")
            if result.stdout.strip():
                print(f"Output:\n{result.stdout}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT - Command took longer than 30 seconds")
        return False, "", "Timeout"
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False, "", str(e)

def test_python_environment():
    """Test Python environment and basic requirements"""
    print_section("Python Environment Check")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not os.path.exists("ghost_protocol"):
        print("❌ ERROR: ghost_protocol directory not found!")
        print("Make sure you're running this from the project root directory")
        return False
    
    return True

def test_installation():
    """Test if Ghost Protocol is properly installed"""
    print_section("Installation Check")
    
    # Try to install in development mode
    success, stdout, stderr = run_command("pip install -e .", "Installing Ghost Protocol in development mode")
    
    if not success:
        print("\n🔧 Trying alternative installation methods...")
        
        # Try installing dependencies first
        if os.path.exists("requirements.txt"):
            run_command("pip install -r requirements.txt", "Installing requirements")
        
        # Try installing with setup.py
        run_command("python setup.py develop", "Installing with setup.py develop")
    
    return success

def test_imports():
    """Test importing all Ghost Protocol modules"""
    print_section("Import Tests")
    
    modules_to_test = [
        "ghost_protocol",
        "ghost_protocol.core",
        "ghost_protocol.core.base",
        "ghost_protocol.server",
        "ghost_protocol.server.main",
        "ghost_protocol.client",
        "ghost_protocol.client.main",
        "ghost_protocol.beacon",
        "ghost_protocol.beacon.main",
        "ghost_protocol.database",
        "ghost_protocol.database.models",
        "ghost_protocol.modules",
        "ghost_protocol.modules.manager",
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"💥 {module_name}: {type(e).__name__}: {e}")
    
    print(f"\nImport Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count == total_count

def test_console_commands():
    """Test console commands"""
    print_section("Console Commands Test")
    
    commands = ["gpserver --help", "ghost --help", "gpbeacon --help"]
    
    for cmd in commands:
        run_command(cmd, f"Testing {cmd.split()[0]} command")

def run_unit_tests():
    """Run unit tests if they exist"""
    print_section("Unit Tests")
    
    if os.path.exists("tests"):
        # Try pytest first
        success, stdout, stderr = run_command("python -m pytest tests/ -v", "Running pytest")
        
        if not success:
            # Try unittest as fallback
            run_command("python -m unittest discover tests/ -v", "Running unittest")
    else:
        print("No tests directory found")

def run_manual_functionality_tests():
    """Run manual functionality tests"""
    print_section("Manual Functionality Tests")
    
    test_scripts = [
        "scripts/quick_test.py",
        "scripts/install_check.py"
    ]
    
    for script in test_scripts:
        if os.path.exists(script):
            run_command(f"python {script}", f"Running {script}")

def main():
    print_header("GHOST PROTOCOL COMPREHENSIVE TEST SUITE")
    
    # Step 1: Environment Check
    if not test_python_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return 1
    
    # Step 2: Installation
    print_header("INSTALLATION PHASE")
    installation_success = test_installation()
    
    # Step 3: Import Tests
    print_header("IMPORT TESTS")
    import_success = test_imports()
    
    # Step 4: Console Commands
    print_header("CONSOLE COMMANDS")
    test_console_commands()
    
    # Step 5: Unit Tests
    print_header("UNIT TESTS")
    run_unit_tests()
    
    # Step 6: Manual Tests
    print_header("MANUAL FUNCTIONALITY TESTS")
    run_manual_functionality_tests()
    
    # Final Summary
    print_header("TEST SUMMARY")
    print(f"Installation: {'✅ PASS' if installation_success else '❌ FAIL'}")
    print(f"Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    
    if installation_success and import_success:
        print("\n🎉 Ghost Protocol appears to be working correctly!")
        print("\nNext steps:")
        print("1. Try running: gpserver")
        print("2. Try running: ghost --help")
        print("3. Try running: gpbeacon --help")
    else:
        print("\n⚠️  Issues found. Please review the errors above.")
        print("\nCommon fixes:")
        print("1. Make sure you're in the project root directory")
        print("2. Try: pip install -e .")
        print("3. Check that all required dependencies are installed")
        print("4. Ensure Python path includes the project directory")
    
    return 0 if (installation_success and import_success) else 1

if __name__ == "__main__":
    sys.exit(main())
