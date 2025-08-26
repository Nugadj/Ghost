#!/usr/bin/env python3
"""
Ghost Protocol Installation Checker
Comprehensive verification of installation and dependencies
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_virtual_environment():
    """Check if running in virtual environment"""
    print("\nChecking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠ Not running in virtual environment (recommended)")
        return False

def check_package_installation():
    """Check if ghost_protocol package is installed"""
    print("\nChecking package installation...")
    try:
        import ghost_protocol
        print("✓ ghost_protocol package is installed")
        print(f"  Version: {getattr(ghost_protocol, '__version__', 'unknown')}")
        print(f"  Location: {ghost_protocol.__file__}")
        return True
    except ImportError as e:
        print(f"✗ ghost_protocol package not found: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\nChecking dependencies...")
    
    # Read requirements from file
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("✗ requirements.txt not found")
        return False
    
    with open(req_file) as f:
        requirements = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
    
    failed_imports = []
    for package in requirements:
        try:
            # Handle special cases
            if package == 'python-jose[cryptography]':
                package = 'jose'
            elif package == 'passlib[bcrypt]':
                package = 'passlib'
            elif package == 'uvicorn[standard]':
                package = 'uvicorn'
            
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nMissing dependencies: {', '.join(failed_imports)}")
        return False
    else:
        print("✓ All dependencies are installed")
        return True

def check_console_commands():
    """Check if console commands are available"""
    print("\nChecking console commands...")
    commands = ['gpserver', 'ghost', 'gpbeacon']
    
    available_commands = []
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--help'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                print(f"✓ {cmd} command available")
                available_commands.append(cmd)
            else:
                print(f"✗ {cmd} command failed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"✗ {cmd} command not found")
    
    return len(available_commands) == len(commands)

def check_file_structure():
    """Check if required files and directories exist"""
    print("\nChecking file structure...")
    
    required_paths = [
        "ghost_protocol/",
        "ghost_protocol/__init__.py",
        "ghost_protocol/core/",
        "ghost_protocol/server/",
        "ghost_protocol/client/",
        "ghost_protocol/beacon/",
        "ghost_protocol/database/",
        "setup.py",
        "requirements.txt"
    ]
    
    missing_paths = []
    for path in required_paths:
        if os.path.exists(path):
            print(f"✓ {path}")
        else:
            print(f"✗ {path}")
            missing_paths.append(path)
    
    return len(missing_paths) == 0

def check_database_connection():
    """Check database connectivity (if configured)"""
    print("\nChecking database connection...")
    try:
        from ghost_protocol.database.models import Base
        from ghost_protocol.core import Config
        
        # This is a basic check - actual connection testing would need configuration
        print("✓ Database models can be imported")
        return True
    except ImportError as e:
        print(f"✗ Database check failed: {e}")
        return False

def provide_installation_help():
    """Provide installation instructions based on failed checks"""
    print("\n" + "="*60)
    print("INSTALLATION HELP")
    print("="*60)
    
    print("\n1. If ghost_protocol package is not installed:")
    print("   pip install -e .")
    
    print("\n2. If dependencies are missing:")
    print("   pip install -r requirements.txt")
    
    print("\n3. If console commands are not available:")
    print("   pip uninstall ghost-protocol")
    print("   pip install -e .")
    
    print("\n4. If running outside virtual environment:")
    print("   python -m venv venv")
    print("   # Windows: venv\\Scripts\\activate")
    print("   # Linux/Mac: source venv/bin/activate")
    print("   pip install -e .")
    
    print("\n5. For development setup:")
    print("   pip install -e .[dev]")
    print("   pre-commit install")

def main():
    """Run all installation checks"""
    print("Ghost Protocol Installation Checker")
    print("="*50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("File Structure", check_file_structure),
        ("Package Installation", check_package_installation),
        ("Dependencies", check_dependencies),
        ("Console Commands", check_console_commands),
        ("Database Models", check_database_connection),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("INSTALLATION SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<30} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Installation is complete and working!")
        print("\nYou can now run:")
        print("  gpserver  # Start team server")
        print("  ghost     # Start client console")
        print("  gpbeacon  # Start beacon")
    else:
        print(f"\n⚠ {total - passed} issues found. See help below:")
        provide_installation_help()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
