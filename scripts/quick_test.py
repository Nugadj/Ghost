#!/usr/bin/env python3
"""
Quick Test Script for Ghost Protocol
Tests basic functionality and reports issues
"""

import sys
import subprocess
import importlib
import asyncio
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    required_modules = [
        'ghost_protocol',
        'ghost_protocol.core',
        'ghost_protocol.server.main',
        'ghost_protocol.client.main',
        'ghost_protocol.beacon.main',
        'ghost_protocol.database.models',
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_dependencies():
    """Test if all dependencies are installed"""
    print("\nTesting dependencies...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("✗ requirements.txt not found")
        return []
    
    failed_deps = []
    
    for dep in requirements:
        try:
            importlib.import_module(dep.replace('-', '_'))
            print(f"✓ {dep}")
        except ImportError:
            try:
                # Try alternative import names
                alt_names = {
                    'python-jose': 'jose',
                    'python-multipart': 'multipart',
                    'python-dotenv': 'dotenv',
                    'email-validator': 'email_validator',
                    'pynacl': 'nacl',
                }
                alt_name = alt_names.get(dep, dep)
                importlib.import_module(alt_name)
                print(f"✓ {dep} (as {alt_name})")
            except ImportError:
                print(f"✗ {dep}")
                failed_deps.append(dep)
    
    return failed_deps

def test_console_commands():
    """Test if console commands are available"""
    print("\nTesting console commands...")
    
    commands = ['gpserver', 'ghost', 'gpbeacon']
    failed_commands = []
    
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--help'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                print(f"✓ {cmd}")
            else:
                print(f"✗ {cmd}: Command failed")
                failed_commands.append(cmd)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"✗ {cmd}: Command not found")
            failed_commands.append(cmd)
    
    return failed_commands

async def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        # Test core imports
        from ghost_protocol.core.base import GhostProtocolCore
        from ghost_protocol.database.models import Base
        print("✓ Core classes imported successfully")
        
        # Test configuration
        from ghost_protocol.core.config import Config
        config = Config()
        print("✓ Configuration loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Ghost Protocol Quick Test")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test dependencies
    failed_deps = test_dependencies()
    
    # Test console commands
    failed_commands = test_console_commands()
    
    # Test basic functionality
    basic_test_passed = asyncio.run(test_basic_functionality())
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    if failed_imports:
        print(f"✗ Failed imports: {', '.join(failed_imports)}")
    else:
        print("✓ All imports successful")
    
    if failed_deps:
        print(f"✗ Missing dependencies: {', '.join(failed_deps)}")
        print("  Run: pip install -r requirements.txt")
    else:
        print("✓ All dependencies installed")
    
    if failed_commands:
        print(f"✗ Missing console commands: {', '.join(failed_commands)}")
        print("  Run: pip install -e .")
    else:
        print("✓ All console commands available")
    
    if basic_test_passed:
        print("✓ Basic functionality working")
    else:
        print("✗ Basic functionality issues detected")
    
    # Overall status
    all_passed = not (failed_imports or failed_deps or failed_commands) and basic_test_passed
    
    if all_passed:
        print("\n🎉 All tests passed! Ghost Protocol is ready to use.")
        print("\nNext steps:")
        print("1. Start the server: gpserver")
        print("2. Start the client: ghost")
        print("3. Run full tests: python -m pytest tests/")
        return 0
    else:
        print("\n⚠️  Some issues detected. Please fix the above errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
