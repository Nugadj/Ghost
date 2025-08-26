"""
Ghost Protocol Base Classes
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from .config import Config
from .events import EventBus


class GhostProtocolCore(ABC):
    """Base class for Ghost Protocol components"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.event_bus = EventBus()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
        self._running = False
        
    async def start(self) -> bool:
        """Start the component"""
        if self._running:
            return True
            
        try:
            # Initialize event bus
            await self.event_bus.initialize()
            
            # Initialize component
            if await self.initialize():
                self._initialized = True
                self._running = True
                self.logger.info(f"{self.__class__.__name__} started successfully")
                return True
            else:
                self.logger.error(f"Failed to initialize {self.__class__.__name__}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting {self.__class__.__name__}: {e}")
            return False
            
    async def stop(self) -> bool:
        """Stop the component"""
        if not self._running:
            return True
            
        try:
            self._running = False
            
            # Shutdown component
            await self.shutdown()
            
            # Shutdown event bus
            await self.event_bus.shutdown()
            
            self.logger.info(f"{self.__class__.__name__} stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping {self.__class__.__name__}: {e}")
            return False
            
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the component"""
        pass
        
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the component"""
        pass
        
    @property
    def is_running(self) -> bool:
        """Check if component is running"""
        return self._running


class ServerModule(ABC):
    """Base class for server modules"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"ghost_protocol.modules.{name}")
        self.capabilities: Dict[str, Any] = {}
        self.commands: Dict[str, str] = {}
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the module"""
        pass
        
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the module"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get module capabilities"""
        pass
        
    @abstractmethod
    def get_commands(self) -> Dict[str, str]:
        """Get available commands"""
        pass
        
    @abstractmethod
    async def execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        pass
        
    def register_routes(self, app) -> None:
        """Register FastAPI routes (optional)"""
        pass
        
    async def handle_beacon_output(self, beacon_id: str, output: Dict[str, Any]) -> None:
        """Handle beacon output (optional)"""
        pass
        
    def get_db_migrations(self) -> List[str]:
        """Get database migrations (optional)"""
        return []


class ClientModule(ABC):
    """Base class for client modules"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"ghost_protocol.client.modules.{name}")
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the module"""
        pass
        
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the module"""
        pass
        
    def create_ui_components(self, parent) -> None:
        """Create UI components (optional)"""
        pass


class BeaconModule(ABC):
    """Base class for beacon modules"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    async def execute(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command on the beacon"""
        pass
        
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        pass

class EventBus:
    """Event bus for inter-component communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        self.logger = logging.getLogger("ghost_protocol.events")
        self._running = False
        
    async def initialize(self) -> bool:
        """Initialize the event bus"""
        try:
            self._running = True
            self.logger.info("Event bus initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize event bus: {e}")
            return False
            
    async def shutdown(self) -> bool:
        """Shutdown the event bus"""
        try:
            self._running = False
            self.subscribers.clear()
            self.logger.info("Event bus shutdown completed")
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down event bus: {e}")
            return False
            
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to {event_type}")
        
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                self.logger.debug(f"Unsubscribed from {event_type}")
            except ValueError:
                pass
                
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event synchronously"""
        if not self._running:
            return
            
        # Add to history
        event_data = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.event_history.append(event_data)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
            
        # Notify subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")
                    
        self.logger.debug(f"Emitted event: {event_type}")
