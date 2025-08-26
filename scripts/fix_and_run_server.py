#!/usr/bin/env python3
"""
Fix and run Ghost Protocol server
"""

import os
import sys
import subprocess
import asyncio
import logging

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def install_package():
    """Install Ghost Protocol package in development mode"""
    print("Installing Ghost Protocol package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✓ Ghost Protocol package installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install package: {e}")
        return False

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        import ghost_protocol
        from ghost_protocol.core import Config, EventBus
        from ghost_protocol.database.manager import DatabaseManager
        from ghost_protocol.server.core import TeamServerCore
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def create_data_directory():
    """Create data directory for SQLite database"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✓ Created {data_dir} directory")
    else:
        print(f"✓ {data_dir} directory already exists")

async def test_server_startup():
    """Test server startup without running indefinitely"""
    print("Testing server startup...")
    try:
        from ghost_protocol.core import Config, EventBus
        from ghost_protocol.server.core import TeamServerCore
        
        # Create configuration
        config = Config()
        event_bus = EventBus()
        
        # Create server core
        server_core = TeamServerCore(config, event_bus)
        
        # Test initialization
        success = await server_core.initialize()
        if success:
            print("✓ Server core initialized successfully")
            
            # Test shutdown
            await server_core.shutdown()
            print("✓ Server core shutdown successfully")
            return True
        else:
            print("✗ Server core initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Server startup test failed: {e}")
        return False

def run_server():
    """Run the Ghost Protocol server"""
    print("Starting Ghost Protocol server...")
    try:
        # Use the console command if available
        subprocess.check_call([sys.executable, "-m", "ghost_protocol.server.main"])
    except subprocess.CalledProcessError as e:
        print(f"Server exited with error: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped by user")

async def main():
    """Main function"""
    setup_logging()
    
    print("Ghost Protocol Server Setup and Test")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        return False
    
    # Step 2: Install package
    if not install_package():
        return False
    
    # Step 3: Test imports
    if not test_imports():
        return False
    
    # Step 4: Create data directory
    create_data_directory()
    
    # Step 5: Test server startup
    if not await test_server_startup():
        return False
    
    print("\n" + "=" * 50)
    print("All tests passed! Ghost Protocol is ready to run.")
    print("=" * 50)
    
    # Ask user if they want to start the server
    response = input("\nDo you want to start the server now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        run_server()
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
