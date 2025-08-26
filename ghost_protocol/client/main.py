"""
Ghost Protocol Client Application
"""

import sys
import asyncio
import argparse
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from ..core import GhostProtocolCore, Config, setup_logging
from .core import ClientCore
from .ui import MainWindow


class ClientApplication(GhostProtocolCore):
    """Ghost Protocol Client Application"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        
        # Qt Application
        self.qt_app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        
        # Client core
        self.client_core: Optional[ClientCore] = None
        
    async def initialize(self) -> bool:
        """Initialize the client application"""
        try:
            self.logger.info("Initializing Ghost Protocol Client")
            
            # Initialize Qt application
            if not QApplication.instance():
                self.qt_app = QApplication(sys.argv)
                self.qt_app.setApplicationName("Ghost Protocol")
                self.qt_app.setApplicationVersion("1.0.0")
                
            # Initialize client core
            self.client_core = ClientCore(self.config, self.event_bus)
            if not await self.client_core.initialize():
                return False
                
            # Initialize main window
            self.main_window = MainWindow(self.client_core, self.config)
            
            self.logger.info("Client application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize client application: {e}")
            return False
            
    async def shutdown(self) -> bool:
        """Shutdown the client application"""
        try:
            self.logger.info("Shutting down Ghost Protocol Client")
            
            if self.main_window:
                self.main_window.close()
                
            if self.client_core:
                await self.client_core.shutdown()
                
            if self.qt_app:
                self.qt_app.quit()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error during client shutdown: {e}")
            return False
            
    def run(self) -> int:
        """Run the client application"""
        try:
            # Initialize async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize application
            if not loop.run_until_complete(self.start()):
                return 1
                
            # Show main window
            if self.main_window:
                self.main_window.show()
                
            # Setup async event loop integration
            timer = QTimer()
            timer.timeout.connect(lambda: loop.run_until_complete(asyncio.sleep(0.01)))
            timer.start(10)  # 10ms timer
            
            # Run Qt event loop
            result = self.qt_app.exec() if self.qt_app else 1
            
            # Cleanup
            loop.run_until_complete(self.stop())
            loop.close()
            
            return result
            
        except KeyboardInterrupt:
            self.logger.info("Client interrupted by user")
            return 0
        except Exception as e:
            self.logger.error(f"Client error: {e}")
            return 1


def main():
    """Main entry point for the client"""
    parser = argparse.ArgumentParser(description="Ghost Protocol Client")
    parser.add_argument("--server", help="Server address")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("ghost_protocol.client", args.log_level)
    
    # Load configuration
    config = Config(args.config)
    if args.server:
        config.client.server_host = args.server
    if args.port:
        config.client.server_port = args.port
        
    # Create and run client
    client = ClientApplication(config)
    sys.exit(client.run())


if __name__ == "__main__":
    main()
