#!/usr/bin/env python3
"""
Test script to verify Ghost Protocol server startup
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from ghost_protocol.core import Config, setup_logging
    from ghost_protocol.server.main import TeamServer
    print("✓ Successfully imported Ghost Protocol modules")
except ImportError as e:
    print(f"✗ Failed to import Ghost Protocol modules: {e}")
    sys.exit(1)

async def test_server_startup():
    """Test server startup and shutdown"""
    print("\nTesting Ghost Protocol Server Startup")
    print("=" * 50)
    
    try:
        # Setup logging
        setup_logging("ghost_protocol.test", "INFO")
        print("✓ Logging configured")
        
        # Create configuration
        config = Config()
        
        # Set basic server configuration
        config.server.host = "127.0.0.1"
        config.server.port = 50050
        config.server.password = "test123"
        
        # Add missing HTTP listener configuration
        config.server.http_enabled = True
        config.server.http_host = "127.0.0.1"
        config.server.http_port = 8080
        config.server.https_enabled = False
        config.server.dns_enabled = False
        
        print("✓ Configuration created")
        
        # Create server instance
        server = TeamServer(config)
        print("✓ Server instance created")
        
        # Test initialization
        print("\nTesting server initialization...")
        if await server.start():
            print("✓ Server initialized successfully")
            
            # Test basic functionality
            print("✓ Server is running")
            
            # Shutdown server
            print("\nShutting down server...")
            if await server.stop():
                print("✓ Server shutdown successfully")
            else:
                print("✗ Server shutdown failed")
                return False
                
        else:
            print("✗ Server initialization failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Ghost Protocol Server Startup Test")
    print("=" * 50)
    
    # Test server startup
    success = asyncio.run(test_server_startup())
    
    if success:
        print("\n✓ All server tests passed!")
        print("\nTo run the server manually:")
        print("python -m ghost_protocol.server.main")
        return 0
    else:
        print("\n✗ Server tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
