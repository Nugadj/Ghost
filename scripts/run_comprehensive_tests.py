"""
Comprehensive test runner for Ghost Protocol
"""

import subprocess
import sys
import os
import json
from datetime import datetime


def run_tests():
    """Run all tests and generate comprehensive report"""
    
    print("🧪 Starting Ghost Protocol Comprehensive Test Suite")
    print("=" * 60)
    
    # Test categories to run
    test_categories = [
        ("Core Base Classes", "tests/test_core_base.py"),
        ("Database Models", "tests/test_database_models.py"),
        ("Server Main", "tests/test_server_main.py"),
        ("Integration Tests", "tests/test_integration.py"),
        ("Security Tests", "tests/test_security.py"),
    ]
    
    results = {}
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    for category_name, test_file in test_categories:
        print(f"\n📋 Running {category_name}...")
        print("-" * 40)
        
        try:
            # Run pytest with coverage and detailed output
            cmd = [
                sys.executable, "-m", "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--cov=ghost_protocol",
                "--cov-report=term-missing",
                "--json-report",
                f"--json-report-file=test_results_{category_name.lower().replace(' ', '_')}.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse results
            if result.returncode == 0:
                print(f"✅ {category_name}: PASSED")
                status = "PASSED"
            else:
                print(f"❌ {category_name}: FAILED")
                status = "FAILED"
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            
            results[category_name] = {
                "status": status,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            print(f"💥 Error running {category_name}: {e}")
            results[category_name] = {
                "status": "ERROR",
                "error": str(e),
                "return_code": -1
            }
    
    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    for category, result in results.items():
        status_emoji = "✅" if result["status"] == "PASSED" else "❌" if result["status"] == "FAILED" else "💥"
        print(f"{status_emoji} {category}: {result['status']}")
    
    # Check for missing dependencies
    print("\n🔍 DEPENDENCY ANALYSIS")
    print("-" * 30)
    
    missing_deps = check_dependencies()
    if missing_deps:
        print("❌ Missing dependencies found:")
        for dep in missing_deps:
            print(f"   - {dep}")
    else:
        print("✅ All dependencies available")
    
    # Check for import issues
    print("\n📦 IMPORT ANALYSIS")
    print("-" * 20)
    
    import_issues = check_imports()
    if import_issues:
        print("❌ Import issues found:")
        for issue in import_issues:
            print(f"   - {issue}")
    else:
        print("✅ All imports working")
    
    # Generate final summary
    passed_count = sum(1 for r in results.values() if r["status"] == "PASSED")
    failed_count = sum(1 for r in results.values() if r["status"] == "FAILED")
    error_count = sum(1 for r in results.values() if r["status"] == "ERROR")
    
    print(f"\n📈 FINAL SUMMARY")
    print("-" * 15)
    print(f"Total Test Categories: {len(results)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"💥 Errors: {error_count}")
    
    if failed_count == 0 and error_count == 0:
        print("\n🎉 ALL TESTS PASSED! Ghost Protocol is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {failed_count + error_count} issues found. Please review the failures above.")
        return 1


def check_dependencies():
    """Check for missing dependencies"""
    missing = []
    
    required_deps = [
        "fastapi", "uvicorn", "sqlalchemy", "pytest", "pytest-asyncio",
        "cryptography", "bcrypt", "PyQt6", "redis", "httpx"
    ]
    
    for dep in required_deps:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            missing.append(dep)
    
    return missing


def check_imports():
    """Check for import issues in the codebase"""
    issues = []
    
    # Test core imports
    try:
        from ghost_protocol.core.base import GhostProtocolCore
    except ImportError as e:
        issues.append(f"Core base import failed: {e}")
    
    try:
        from ghost_protocol.database.models import Base, User
    except ImportError as e:
        issues.append(f"Database models import failed: {e}")
    
    try:
        from ghost_protocol.server.main import TeamServer
    except ImportError as e:
        issues.append(f"Server main import failed: {e}")
    
    # Check for missing core modules
    core_modules = [
        "ghost_protocol.core.config",
        "ghost_protocol.core.events",
        "ghost_protocol.server.core",
        "ghost_protocol.client.main",
        "ghost_protocol.beacon.main"
    ]
    
    for module in core_modules:
        try:
            __import__(module)
        except ImportError as e:
            issues.append(f"Missing module {module}: {e}")
    
    return issues


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
