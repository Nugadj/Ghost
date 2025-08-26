"""
Tests for Ghost Protocol server main functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from ghost_protocol.server.main import TeamServer, main
from ghost_protocol.core.config import Config


class TestTeamServer:
    """Test the TeamServer class"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, test_config):
        """Test server initialization"""
        with patch('ghost_protocol.server.main.TeamServerCore') as mock_core_class:
            mock_core = AsyncMock()
            mock_core.initialize.return_value = True
            mock_core_class.return_value = mock_core
            
            server = TeamServer(test_config)
            result = await server.initialize()
            
            assert result is True
            assert server.server_core is not None
            mock_core.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_server_initialization_failure(self, test_config):
        """Test server initialization failure"""
        with patch('ghost_protocol.server.main.TeamServerCore') as mock_core_class:
            mock_core = AsyncMock()
            mock_core.initialize.return_value = False
            mock_core_class.return_value = mock_core
            
            server = TeamServer(test_config)
            result = await server.initialize()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_server_shutdown(self, test_config):
        """Test server shutdown"""
        with patch('ghost_protocol.server.main.TeamServerCore') as mock_core_class:
            mock_core = AsyncMock()
            mock_core.initialize.return_value = True
            mock_core.shutdown.return_value = True
            mock_core_class.return_value = mock_core
            
            server = TeamServer(test_config)
            await server.initialize()
            
            result = await server.shutdown()
            
            assert result is True
            mock_core.shutdown.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_server_run_forever_keyboard_interrupt(self, test_config):
        """Test server run_forever with keyboard interrupt"""
        server = TeamServer(test_config)
        server._running = True
        
        # Mock sleep to raise KeyboardInterrupt after first call
        with patch('asyncio.sleep', side_effect=KeyboardInterrupt):
            await server.run_forever()
            # Should complete without error


class TestMainFunction:
    """Test the main function"""
    
    @patch('sys.argv', ['gpserver', '127.0.0.1', 'password123', '--port', '50051'])
    @patch('ghost_protocol.server.main.setup_logging')
    @patch('ghost_protocol.server.main.Config')
    @patch('asyncio.run')
    def test_main_function_with_args(self, mock_asyncio_run, mock_config_class, mock_setup_logging):
        """Test main function with command line arguments"""
        mock_config = Mock()
        mock_config.server = Mock()
        mock_config_class.return_value = mock_config
        mock_asyncio_run.return_value = 0
        
        # This would normally call sys.exit, so we need to catch it
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        mock_setup_logging.assert_called_once()
        mock_config_class.assert_called_once()
        assert mock_config.server.host == '127.0.0.1'
        assert mock_config.server.port == 50051
        assert mock_config.server.password == 'password123'
    
    @patch('sys.argv', ['gpserver'])
    @patch('ghost_protocol.server.main.setup_logging')
    @patch('ghost_protocol.server.main.Config')
    @patch('asyncio.run')
    def test_main_function_defaults(self, mock_asyncio_run, mock_config_class, mock_setup_logging):
        """Test main function with default arguments"""
        mock_config = Mock()
        mock_config.server = Mock()
        mock_config_class.return_value = mock_config
        mock_asyncio_run.return_value = 0
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        assert mock_config.server.host == '0.0.0.0'
        assert mock_config.server.port == 50050
        assert mock_config.server.password == ''
    
    @patch('sys.argv', ['gpserver'])
    @patch('ghost_protocol.server.main.setup_logging')
    @patch('ghost_protocol.server.main.Config')
    @patch('asyncio.run', side_effect=Exception("Test error"))
    def test_main_function_error(self, mock_asyncio_run, mock_config_class, mock_setup_logging):
        """Test main function with error"""
        mock_config = Mock()
        mock_config.server = Mock()
        mock_config_class.return_value = mock_config
        
        with patch('ghost_protocol.server.main.TeamServer') as mock_server_class:
            # Create a regular Mock instead of AsyncMock to avoid coroutine creation
            mock_server = Mock()
            mock_server_class.return_value = mock_server
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
