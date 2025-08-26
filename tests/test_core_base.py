"""
Tests for Ghost Protocol core base classes
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from ghost_protocol.core.base import GhostProtocolCore, ServerModule, ClientModule, BeaconModule
from ghost_protocol.core.config import Config


class TestGhostProtocolCore:
    """Test the base GhostProtocolCore class"""
    
    class MockCore(GhostProtocolCore):
        """Mock implementation for testing"""
        
        def __init__(self, config=None):
            super().__init__(config)
            self.init_called = False
            self.shutdown_called = False
            
        async def initialize(self):
            self.init_called = True
            return True
            
        async def shutdown(self):
            self.shutdown_called = True
            return True
    
    @pytest.mark.asyncio
    async def test_core_initialization(self, test_config):
        """Test core component initialization"""
        core = self.MockCore(test_config)
        
        assert not core.is_running
        assert not core._initialized
        
        result = await core.start()
        
        assert result is True
        assert core.is_running
        assert core._initialized
        assert core.init_called
    
    @pytest.mark.asyncio
    async def test_core_shutdown(self, test_config):
        """Test core component shutdown"""
        core = self.MockCore(test_config)
        
        await core.start()
        assert core.is_running
        
        result = await core.stop()
        
        assert result is True
        assert not core.is_running
        assert core.shutdown_called
    
    @pytest.mark.asyncio
    async def test_double_start_prevention(self, test_config):
        """Test that starting twice doesn't cause issues"""
        core = self.MockCore(test_config)
        
        result1 = await core.start()
        result2 = await core.start()
        
        assert result1 is True
        assert result2 is True
        assert core.is_running
    
    @pytest.mark.asyncio
    async def test_stop_without_start(self, test_config):
        """Test stopping without starting"""
        core = self.MockCore(test_config)
        
        result = await core.stop()
        
        assert result is True
        assert not core.is_running


class TestServerModule:
    """Test the ServerModule base class"""
    
    class MockServerModule(ServerModule):
        """Mock server module for testing"""
        
        def __init__(self, name="test_module"):
            super().__init__(name)
            self.init_called = False
            self.shutdown_called = False
            
        async def initialize(self):
            self.init_called = True
            return True
            
        async def shutdown(self):
            self.shutdown_called = True
            return True
            
        def get_capabilities(self):
            return {"test": True}
            
        def get_commands(self):
            return {"test_cmd": "Test command"}
            
        async def execute_command(self, command, args):
            return {"result": f"Executed {command} with {args}"}
    
    def test_module_creation(self):
        """Test server module creation"""
        module = self.MockServerModule("test_module")
        
        assert module.name == "test_module"
        assert module.config == {}
        assert hasattr(module, 'logger')
    
    @pytest.mark.asyncio
    async def test_module_lifecycle(self):
        """Test module initialization and shutdown"""
        module = self.MockServerModule()
        
        result = await module.initialize()
        assert result is True
        assert module.init_called
        
        result = await module.shutdown()
        assert result is True
        assert module.shutdown_called
    
    def test_capabilities_and_commands(self):
        """Test module capabilities and commands"""
        module = self.MockServerModule()
        
        capabilities = module.get_capabilities()
        assert capabilities == {"test": True}
        
        commands = module.get_commands()
        assert commands == {"test_cmd": "Test command"}
    
    @pytest.mark.asyncio
    async def test_command_execution(self):
        """Test command execution"""
        module = self.MockServerModule()
        
        result = await module.execute_command("test_cmd", {"arg1": "value1"})
        
        assert result["result"] == "Executed test_cmd with {'arg1': 'value1'}"


class TestClientModule:
    """Test the ClientModule base class"""
    
    class MockClientModule(ClientModule):
        """Mock client module for testing"""
        
        def __init__(self, name="test_client_module"):
            super().__init__(name)
            self.init_called = False
            self.shutdown_called = False
            
        async def initialize(self):
            self.init_called = True
            return True
            
        async def shutdown(self):
            self.shutdown_called = True
            return True
    
    def test_client_module_creation(self):
        """Test client module creation"""
        module = self.MockClientModule("test_client")
        
        assert module.name == "test_client"
        assert module.config == {}
        assert hasattr(module, 'logger')
    
    @pytest.mark.asyncio
    async def test_client_module_lifecycle(self):
        """Test client module lifecycle"""
        module = self.MockClientModule()
        
        result = await module.initialize()
        assert result is True
        assert module.init_called
        
        result = await module.shutdown()
        assert result is True
        assert module.shutdown_called


class TestBeaconModule:
    """Test the BeaconModule base class"""
    
    class MockBeaconModule(BeaconModule):
        """Mock beacon module for testing"""
        
        def __init__(self, name="test_beacon_module"):
            super().__init__(name)
            
        async def execute(self, command, args):
            return {"output": f"Executed {command}", "success": True}
            
        def get_system_info(self):
            return {"os": "Windows", "arch": "x64"}
    
    def test_beacon_module_creation(self):
        """Test beacon module creation"""
        module = self.MockBeaconModule("test_beacon")
        
        assert module.name == "test_beacon"
        assert module.config == {}
    
    @pytest.mark.asyncio
    async def test_beacon_command_execution(self):
        """Test beacon command execution"""
        module = self.MockBeaconModule()
        
        result = await module.execute("whoami", {})
        
        assert result["output"] == "Executed whoami"
        assert result["success"] is True
    
    def test_beacon_system_info(self):
        """Test beacon system info retrieval"""
        module = self.MockBeaconModule()
        
        info = module.get_system_info()
        
        assert info["os"] == "Windows"
        assert info["arch"] == "x64"
