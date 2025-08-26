#!/usr/bin/env python3
"""
Install Ghost Protocol and run basic functionality test
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main installation and test function"""
    print("Ghost Protocol Installation and Test Script")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Install package in development mode
    if not run_command("pip install -e .", "Installing Ghost Protocol in development mode"):
        print("❌ Failed to install Ghost Protocol")
        return False
    
    # Install additional dependencies
    if not run_command("pip install aiosqlite", "Installing SQLite async driver"):
        print("❌ Failed to install aiosqlite")
        return False
    
    # Test imports
    print("\n" + "="*50)
    print("Testing imports...")
    print("="*50)
    
    try:
        import ghost_protocol
        print("✅ ghost_protocol imported successfully")
        
        from ghost_protocol.core import Config
        print("✅ Config imported successfully")
        
        from ghost_protocol.database.manager import DatabaseManager
        print("✅ DatabaseManager imported successfully")
        
        from ghost_protocol.server.main import TeamServer
        print("✅ TeamServer imported successfully")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test configuration
    print("\n" + "="*50)
    print("Testing configuration...")
    print("="*50)
    
    try:
        config = Config()
        print(f"✅ Config created: {config.database.use_sqlite}")
        
        db_url = config.get_database_url()
        print(f"✅ Database URL: {db_url}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    # Test database initialization
    print("\n" + "="*50)
    print("Testing database initialization...")
    print("="*50)
    
    try:
        import asyncio
        
        async def test_db():
            config = Config()
            db_manager = DatabaseManager(config=config)
            
            success = await db_manager.initialize()
            if success:
                print("✅ Database initialized successfully")
                await db_manager.shutdown()
                return True
            else:
                print("❌ Database initialization failed")
                return False
        
        if asyncio.run(test_db()):
            print("✅ Database test passed")
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    # Test console commands
    print("\n" + "="*50)
    print("Testing console commands...")
    print("="*50)
    
    commands = ["gpserver --help", "ghost --help", "gpbeacon --help"]
    
    for cmd in commands:
        if run_command(cmd, f"Testing {cmd.split()[0]} command"):
            print(f"✅ {cmd.split()[0]} command available")
        else:
            print(f"⚠️  {cmd.split()[0]} command may not be properly installed")
    
    print("\n" + "="*60)
    print("🎉 Ghost Protocol installation and basic tests completed!")
    print("="*60)
    print("\nTo start the server, run:")
    print("  python -m ghost_protocol.server.main")
    print("\nOr use the console command:")
    print("  gpserver")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
