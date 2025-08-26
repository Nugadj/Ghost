"""
Ghost Protocol Event System
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone


class EventType(Enum):
    """Event type enumeration"""
    # User events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    
    # Beacon events
    BEACON_CHECKIN = "beacon_checkin"
    BEACON_OUTPUT = "beacon_output"
    BEACON_TASK = "beacon_task"
    BEACON_DISCONNECT = "beacon_disconnect"
    
    # Listener events
    LISTENER_STARTED = "listener_started"
    LISTENER_STOPPED = "listener_stopped"
    LISTENER_ERROR = "listener_error"
    
    # Operation events
    OPERATION_CREATED = "operation_created"
    OPERATION_STARTED = "operation_started"
    OPERATION_COMPLETED = "operation_completed"
    
    # Module events
    MODULE_LOADED = "module_loaded"
    MODULE_UNLOADED = "module_unloaded"
    MODULE_ERROR = "module_error"
    
    # System events
    SERVER_STARTED = "server_started"
    SERVER_STOPPED = "server_stopped"
    CLIENT_CONNECTED = "client_connected"
    CLIENT_DISCONNECTED = "client_disconnected"


@dataclass
class Event:
    """Event data structure"""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = None
    source: str = "system"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class EventBus:
    """Event bus for inter-component communication"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
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
            
    def subscribe(self, event_type, callback: Callable) -> None:
        """Subscribe to an event type"""
        if isinstance(event_type, str):
            # Convert string to EventType if possible, otherwise use as-is
            try:
                event_type_obj = EventType(event_type)
            except ValueError:
                # Create a temporary EventType-like object for logging
                event_type_obj = type('TempEventType', (), {'value': event_type})()
        else:
            event_type_obj = event_type
            
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to {event_type_obj.value if hasattr(event_type_obj, 'value') else event_type}")
        
    def unsubscribe(self, event_type, callback: Callable) -> None:
        """Unsubscribe from an event type"""
        if isinstance(event_type, str):
            try:
                event_type_obj = EventType(event_type)
            except ValueError:
                event_type_obj = type('TempEventType', (), {'value': event_type})()
        else:
            event_type_obj = event_type
            
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                self.logger.debug(f"Unsubscribed from {event_type_obj.value if hasattr(event_type_obj, 'value') else event_type}")
            except ValueError:
                pass
                
    async def publish_event(self, event_type, data: Dict[str, Any], 
                          source: str = "system") -> None:
        """Publish an event"""
        if not self._running:
            return
            
        if isinstance(event_type, str):
            try:
                event_type_enum = EventType(event_type)
            except ValueError:
                # Create a temporary EventType-like object
                event_type_enum = type('TempEventType', (), {'value': event_type})()
                event_type_enum.value = event_type
        else:
            event_type_enum = event_type
            
        event = Event(event_type_enum, data, source=source)
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
            
        # Notify subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")
                    
        self.logger.debug(f"Published event: {event_type_enum.value if hasattr(event_type_enum, 'value') else event_type}")

    def get_event_history(self, event_type: Optional[EventType] = None, 
                         limit: int = 100) -> List[Event]:
        """Get event history"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
            
        return events[-limit:] if limit else events
        
    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get number of subscribers for an event type"""
        return len(self.subscribers.get(event_type, []))
