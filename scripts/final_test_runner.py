"""
Final comprehensive test runner for Ghost Protocol
"""

import subprocess
import sys
import os
from pathlib import Path


def run_final_tests():
    """Run all tests and provide comprehensive report"""
    print("=" * 60)
    print("GHOST PROTOCOL FINAL TEST SUITE")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"Running tests from: {project_root}")
    print()
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=ghost_protocol", 
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
        "--tb=short"
    ]
    
    print("Running command:", " ".join(cmd))
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        print("-" * 60)
        print(f"Test execution completed with exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
            print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print("❌ Some tests failed. Check output above for details.")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_final_tests()
    sys.exit(exit_code)
