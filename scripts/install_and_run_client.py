#!/usr/bin/env python3
"""
Install dependencies and run Ghost Protocol Client
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main installation and testing function"""
    print("Ghost Protocol Client Installation & Test")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Step 1: Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install requirements. Please check your Python environment.")
        return 1
    
    # Step 2: Install project in development mode
    if not run_command("pip install -e .", "Installing Ghost Protocol in development mode"):
        print("❌ Failed to install Ghost Protocol. Please check setup.py.")
        return 1
    
    # Step 3: Test PyQt6 import
    print("\n" + "="*50)
    print("🧪 Testing PyQt6 Import")
    print("="*50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        print("✅ PyQt6 import - SUCCESS")
    except ImportError as e:
        print(f"❌ PyQt6 import - FAILED: {e}")
        print("💡 Try: pip install PyQt6==6.6.1")
        return 1
    
    # Step 4: Test Ghost Protocol client import
    print("\n" + "="*50)
    print("🧪 Testing Ghost Protocol Client Import")
    print("="*50)
    
    try:
        from ghost_protocol.client.main import ClientApplication
        print("✅ Ghost Protocol client import - SUCCESS")
    except ImportError as e:
        print(f"❌ Ghost Protocol client import - FAILED: {e}")
        return 1
    
    # Step 5: Test client initialization (without GUI)
    print("\n" + "="*50)
    print("🧪 Testing Client Initialization")
    print("="*50)
    
    try:
        # Test basic client creation
        from ghost_protocol.core.config import Config
        config = Config()
        client = ClientApplication(config)
        print("✅ Client creation - SUCCESS")
    except Exception as e:
        print(f"❌ Client creation - FAILED: {e}")
        return 1
    
    # Step 6: Show available commands
    print("\n" + "="*50)
    print("🚀 Available Commands")
    print("="*50)
    print("To run the Ghost Protocol client:")
    print("  python -m ghost_protocol.client.main")
    print("  ghost  # (if console scripts are installed)")
    print("\nTo run with custom server:")
    print("  python -m ghost_protocol.client.main --server 127.0.0.1 --port 8443")
    
    print("\n✅ All tests passed! Ghost Protocol client is ready to use.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
