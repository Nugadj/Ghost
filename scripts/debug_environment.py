#!/usr/bin/env python3
"""
Debug Environment Script
Provides detailed information about the Python environment and project setup
"""

import sys
import os
import site
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")

def debug_python_environment():
    print_header("PYTHON ENVIRONMENT DEBUG")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    print(f"\nPython Path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")
    
    print(f"\nSite Packages:")
    for path in site.getsitepackages():
        print(f"  {path}")
    
    print(f"\nUser Site: {site.getusersitepackages()}")

def debug_project_structure():
    print_header("PROJECT STRUCTURE DEBUG")
    
    current_dir = Path(".")
    
    print("Project files and directories:")
    for item in sorted(current_dir.rglob("*")):
        if item.is_file() and not item.name.startswith('.') and 'egg-info' not in str(item):
            print(f"  📄 {item}")
        elif item.is_dir() and not item.name.startswith('.') and 'egg-info' not in str(item):
            print(f"  📁 {item}/")

def debug_package_installation():
    print_header("PACKAGE INSTALLATION DEBUG")
    
    # Check if setup.py exists and is valid
    if os.path.exists("setup.py"):
        print("✅ setup.py found")
        try:
            with open("setup.py", "r") as f:
                content = f.read()
                if "ghost_protocol" in content:
                    print("✅ setup.py contains ghost_protocol references")
                else:
                    print("⚠️  setup.py may not be configured correctly")
        except Exception as e:
            print(f"❌ Error reading setup.py: {e}")
    else:
        print("❌ setup.py not found")
    
    # Check requirements.txt
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found")
    
    # Check __init__.py files
    init_files = list(Path(".").rglob("__init__.py"))
    print(f"\n__init__.py files found: {len(init_files)}")
    for init_file in init_files:
        print(f"  {init_file}")

if __name__ == "__main__":
    debug_python_environment()
    debug_project_structure()
    debug_package_installation()
