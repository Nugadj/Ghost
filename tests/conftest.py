"""
Pytest configuration and fixtures for Ghost Protocol tests
"""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ghost_protocol.database.models import Base
from ghost_protocol.core.config import Config
try:
    from ghost_protocol.core.events import EventBus
except ImportError:
    # Create a mock EventBus if the module doesn't exist
    class EventBus:
        def __init__(self):
            self.subscribers = {}
        
        async def initialize(self):
            pass
        
        async def shutdown(self):
            pass
        
        async def subscribe(self, event_type, handler):
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)
        
        async def publish(self, event_type, data):
            if event_type in self.subscribers:
                for handler in self.subscribers[event_type]:
                    await handler(event_type, data)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    engine.dispose()
    os.unlink(db_path)


@pytest.fixture
def db_session(temp_db):
    """Create a database session for testing"""
    Session = sessionmaker(bind=temp_db)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_config():
    """Create a test configuration"""
    config = Config()
    config.server.host = "127.0.0.1"
    config.server.port = 50051
    config.database.url = "sqlite:///test.db"
    return config


@pytest_asyncio.fixture
async def event_bus():
    """Create an event bus for testing"""
    bus = EventBus()
    await bus.initialize()
    yield bus
    await bus.shutdown()


@pytest.fixture
def mock_beacon():
    """Create a mock beacon for testing"""
    beacon = Mock()
    beacon.id = "test-beacon-123"
    beacon.hostname = "test-host"
    beacon.username = "test-user"
    beacon.os_name = "Windows"
    beacon.status = "active"
    return beacon


@pytest.fixture
def mock_listener():
    """Create a mock listener for testing"""
    listener = Mock()
    listener.id = "test-listener-123"
    listener.name = "test-http-listener"
    listener.protocol = "http"
    listener.host = "0.0.0.0"
    listener.port = 8080
    listener.status = "running"
    return listener
