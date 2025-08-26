"""
Ghost Protocol Team Server Main Application
"""

import sys
import asyncio
import argparse
from typing import Optional

from ..core import GhostProtocolCore, Config, setup_logging
from .core import TeamServerCore


class TeamServer(GhostProtocolCore):
    """Ghost Protocol Team Server"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        self.server_core: Optional[TeamServerCore] = None
        
    async def initialize(self) -> bool:
        """Initialize the team server"""
        try:
            self.logger.info("Initializing Ghost Protocol Team Server")
            
            # Initialize server core
            self.server_core = TeamServerCore(self.config, self.event_bus)
            if not await self.server_core.initialize():
                return False
                
            self.logger.info("Team server initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize team server: {e}")
            return False
            
    async def shutdown(self) -> bool:
        """Shutdown the team server"""
        try:
            self.logger.info("Shutting down Ghost Protocol Team Server")
            
            if self.server_core:
                await self.server_core.shutdown()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error during server shutdown: {e}")
            return False
            
    async def run_forever(self) -> None:
        """Run the server until stopped"""
        try:
            self.logger.info("Team server is running. Press Ctrl+C to stop.")
            
            while self.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Server interrupted by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")


def main():
    """Main entry point for the team server"""
    parser = argparse.ArgumentParser(description="Ghost Protocol Team Server")
    parser.add_argument("host", nargs="?", default="0.0.0.0", help="Server host address")
    parser.add_argument("password", nargs="?", default="", help="Server password")
    parser.add_argument("--port", type=int, default=50050, help="Server port")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("ghost_protocol.server", args.log_level)
    
    # Load configuration
    config = Config(args.config)
    config.server.host = args.host
    config.server.port = args.port
    config.server.password = args.password
    
    if not hasattr(config.server, 'http_enabled'):
        config.server.http_enabled = True
    if not hasattr(config.server, 'http_host'):
        config.server.http_host = args.host
    if not hasattr(config.server, 'http_port'):
        config.server.http_port = 8080
    if not hasattr(config.server, 'https_enabled'):
        config.server.https_enabled = False
    if not hasattr(config.server, 'https_host'):
        config.server.https_host = args.host
    if not hasattr(config.server, 'https_port'):
        config.server.https_port = 8443
    if not hasattr(config.server, 'dns_enabled'):
        config.server.dns_enabled = False
    if not hasattr(config.server, 'dns_host'):
        config.server.dns_host = args.host
    if not hasattr(config.server, 'dns_port'):
        config.server.dns_port = 53
    
    server = TeamServer(config)
    
    async def run_server():
        try:
            if await server.start():
                await server.run_forever()
                return 0
            else:
                print("Failed to start server")
                return 1
        except Exception as e:
            print(f"Server error: {e}")
            return 1
        finally:
            try:
                await server.stop()
            except Exception as e:
                print(f"Error during shutdown: {e}")
    
    try:
        result = asyncio.run(run_server())
        sys.exit(result or 0)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


def _main():
    """Entry point wrapper to handle module execution properly"""
    if __name__ == "__main__":
        main()
    else:
        # Handle python -m execution
        main()


if __name__ == "__main__":
    main()
else:
    # This handles python -m ghost_protocol.server.main execution
    _main()
