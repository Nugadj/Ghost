"""
Ghost Protocol Team Server Core
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..core import Config, EventBus
from ..database.manager import DatabaseManager
from ..database.models import Beacon, Session, Command, CommandResult


class TeamServerCore:
    """Ghost Protocol Team Server Core Implementation"""
    
    def __init__(self, config: Config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.db_manager: Optional[DatabaseManager] = None
        self.listeners: Dict[str, Any] = {}
        self.beacons: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Server state
        self._running = False
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the team server core"""
        try:
            self.logger.info("Initializing Team Server Core")
            
            self.db_manager = DatabaseManager(config=self.config)
            if not await self.db_manager.initialize():
                self.logger.error("Failed to initialize database manager")
                return False
            
            # Setup event handlers
            await self._setup_event_handlers()
            
            # Initialize listeners (HTTP/HTTPS/DNS)
            await self._initialize_listeners()
            
            self._initialized = True
            self.logger.info("Team Server Core initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Team Server Core: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the team server core"""
        try:
            self.logger.info("Shutting down Team Server Core")
            self._running = False
            
            # Shutdown listeners
            for listener_id, listener in self.listeners.items():
                try:
                    await listener.shutdown()
                    self.logger.info(f"Listener {listener_id} shut down successfully")
                except Exception as e:
                    self.logger.error(f"Error shutting down listener {listener_id}: {e}")
            
            # Shutdown database
            if self.db_manager:
                await self.db_manager.shutdown()
            
            self.logger.info("Team Server Core shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during Team Server Core shutdown: {e}")
            return False
    
    async def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe("beacon.checkin", self._handle_beacon_checkin)
        self.event_bus.subscribe("beacon.output", self._handle_beacon_output)
        self.event_bus.subscribe("command.execute", self._handle_command_execute)
        self.event_bus.subscribe("session.create", self._handle_session_create)
        self.event_bus.subscribe("session.close", self._handle_session_close)
    
    async def _initialize_listeners(self):
        """Initialize C2 listeners"""
        try:
            # HTTP Listener
            if hasattr(self.config.server, 'http_enabled') and self.config.server.http_enabled:
                try:
                    http_listener = HTTPListener(
                        host=getattr(self.config.server, 'http_host', '127.0.0.1'),
                        port=getattr(self.config.server, 'http_port', 8080),
                        server_core=self
                    )
                    await http_listener.start()
                    self.listeners["http"] = http_listener
                    self.logger.info(f"HTTP listener started on {getattr(self.config.server, 'http_host', '127.0.0.1')}:{getattr(self.config.server, 'http_port', 8080)}")
                except Exception as e:
                    self.logger.warning(f"Failed to start HTTP listener: {e}")
            
            # HTTPS Listener
            if hasattr(self.config.server, 'https_enabled') and self.config.server.https_enabled:
                try:
                    https_listener = HTTPSListener(
                        host=getattr(self.config.server, 'https_host', '127.0.0.1'),
                        port=getattr(self.config.server, 'https_port', 8443),
                        cert_file=getattr(self.config.server, 'cert_file', 'server.crt'),
                        key_file=getattr(self.config.server, 'key_file', 'server.key'),
                        server_core=self
                    )
                    await https_listener.start()
                    self.listeners["https"] = https_listener
                    self.logger.info(f"HTTPS listener started on {getattr(self.config.server, 'https_host', '127.0.0.1')}:{getattr(self.config.server, 'https_port', 8443)}")
                except Exception as e:
                    self.logger.warning(f"Failed to start HTTPS listener: {e}")
            
            # DNS Listener
            if hasattr(self.config.server, 'dns_enabled') and self.config.server.dns_enabled:
                try:
                    dns_listener = DNSListener(
                        host=getattr(self.config.server, 'dns_host', '127.0.0.1'),
                        port=getattr(self.config.server, 'dns_port', 53),
                        server_core=self
                    )
                    await dns_listener.start()
                    self.listeners["dns"] = dns_listener
                    self.logger.info(f"DNS listener started on {getattr(self.config.server, 'dns_host', '127.0.0.1')}:{getattr(self.config.server, 'dns_port', 53)}")
                except Exception as e:
                    self.logger.warning(f"Failed to start DNS listener: {e}")
                
        except Exception as e:
            self.logger.error(f"Error initializing listeners: {e}")
            
    async def _handle_beacon_checkin(self, event_data: Dict[str, Any]):
        """Handle beacon check-in events"""
        try:
            beacon_id = event_data.get("beacon_id")
            beacon_data = event_data.get("data", {})
            
            if beacon_id not in self.beacons:
                # New beacon
                self.beacons[beacon_id] = {
                    "id": beacon_id,
                    "first_seen": datetime.now(timezone.utc),
                    "last_seen": datetime.now(timezone.utc),
                    "system_info": beacon_data.get("system_info", {}),
                    "status": "active"
                }
                
                # Store in database
                if self.db_manager:
                    await self.db_manager.create_beacon(
                        beacon_id=beacon_id,
                        system_info=beacon_data.get("system_info", {}),
                        listener_id=event_data.get("listener_id")
                    )
                
                self.logger.info(f"New beacon registered: {beacon_id}")
            else:
                # Update existing beacon
                self.beacons[beacon_id]["last_seen"] = datetime.now(timezone.utc)
                self.beacons[beacon_id]["status"] = "active"
                
                if self.db_manager:
                    await self.db_manager.update_beacon_checkin(beacon_id)
                
        except Exception as e:
            self.logger.error(f"Error handling beacon checkin: {e}")
    
    async def _handle_beacon_output(self, event_data: Dict[str, Any]):
        """Handle beacon command output"""
        try:
            beacon_id = event_data.get("beacon_id")
            command_id = event_data.get("command_id")
            output = event_data.get("output", "")
            
            if self.db_manager:
                await self.db_manager.store_command_result(
                    command_id=command_id,
                    beacon_id=beacon_id,
                    output=output,
                    success=event_data.get("success", True)
                )
            
            self.logger.info(f"Command output received from beacon {beacon_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling beacon output: {e}")
    
    async def _handle_command_execute(self, event_data: Dict[str, Any]):
        """Handle command execution requests"""
        try:
            beacon_id = event_data.get("beacon_id")
            command = event_data.get("command")
            args = event_data.get("args", {})
            
            if beacon_id in self.beacons:
                # Queue command for beacon
                command_id = await self._queue_beacon_command(beacon_id, command, args)
                self.logger.info(f"Command {command_id} queued for beacon {beacon_id}")
            else:
                self.logger.warning(f"Command for unknown beacon: {beacon_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling command execute: {e}")
    
    async def _handle_session_create(self, event_data: Dict[str, Any]):
        """Handle session creation"""
        try:
            session_id = event_data.get("session_id")
            beacon_id = event_data.get("beacon_id")
            session_type = event_data.get("type", "shell")
            
            self.sessions[session_id] = {
                "id": session_id,
                "beacon_id": beacon_id,
                "type": session_type,
                "created": datetime.now(timezone.utc),
                "status": "active"
            }
            
            if self.db_manager:
                await self.db_manager.create_session(
                    session_id=session_id,
                    beacon_id=beacon_id,
                    session_type=session_type
                )
            
            self.logger.info(f"Session {session_id} created for beacon {beacon_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
    
    async def _handle_session_close(self, event_data: Dict[str, Any]):
        """Handle session closure"""
        try:
            session_id = event_data.get("session_id")
            
            if session_id in self.sessions:
                self.sessions[session_id]["status"] = "closed"
                self.sessions[session_id]["closed"] = datetime.now(timezone.utc)
                
                if self.db_manager:
                    await self.db_manager.close_session(session_id)
                
                self.logger.info(f"Session {session_id} closed")
            
        except Exception as e:
            self.logger.error(f"Error closing session: {e}")
    
    async def _queue_beacon_command(self, beacon_id: str, command: str, args: Dict[str, Any]) -> str:
        """Queue a command for execution on a beacon"""
        import uuid
        
        command_id = str(uuid.uuid4())
        
        if self.db_manager:
            await self.db_manager.create_command(
                command_id=command_id,
                beacon_id=beacon_id,
                command=command,
                args=args
            )
        
        return command_id
    
    def get_beacons(self) -> List[Dict[str, Any]]:
        """Get all registered beacons"""
        return list(self.beacons.values())
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return list(self.sessions.values())
    
    def get_listeners(self) -> Dict[str, Any]:
        """Get listener status"""
        return {
            listener_id: {
                "type": listener_id,
                "status": "running" if hasattr(listener, "_running") and listener._running else "stopped"
            }
            for listener_id, listener in self.listeners.items()
        }


class HTTPListener:
    """HTTP C2 Listener"""
    
    def __init__(self, host: str, port: int, server_core: TeamServerCore):
        self.host = host
        self.port = port
        self.server_core = server_core
        self.logger = logging.getLogger(f"{__name__}.HTTPListener")
        self._running = False
        self.server = None
    
    async def start(self):
        """Start the HTTP listener"""
        try:
            from aiohttp import web, web_runner
            
            app = web.Application()
            app.router.add_get("/", self.handle_beacon_checkin)
            app.router.add_post("/", self.handle_beacon_checkin)
            app.router.add_get("/{path:.*}", self.handle_beacon_request)
            app.router.add_post("/{path:.*}", self.handle_beacon_request)
            
            runner = web_runner.AppRunner(app)
            await runner.setup()
            
            site = web_runner.TCPSite(runner, self.host, self.port)
            await site.start()
            
            self._running = True
            self.server = runner
            
        except Exception as e:
            self.logger.error(f"Failed to start HTTP listener: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the HTTP listener"""
        if self.server:
            await self.server.cleanup()
        self._running = False
    
    async def handle_beacon_checkin(self, request):
        """Handle beacon check-in requests"""
        from aiohttp import web
        
        try:
            # Extract beacon data from request
            beacon_id = request.headers.get("X-Beacon-ID")
            if not beacon_id:
                return web.Response(status=404)
            
            # Get system info if POST
            system_info = {}
            if request.method == "POST":
                try:
                    data = await request.json()
                    system_info = data.get("system_info", {})
                except:
                    pass
            
            self.server_core.event_bus.emit("beacon.checkin", {
                "beacon_id": beacon_id,
                "listener_id": "http",
                "data": {"system_info": system_info}
            })
            
            # Return any queued commands
            commands = await self._get_queued_commands(beacon_id)
            return web.json_response({"commands": commands})
            
        except Exception as e:
            self.logger.error(f"Error handling beacon checkin: {e}")
            return web.Response(status=500)
    
    async def handle_beacon_request(self, request):
        """Handle general beacon requests"""
        from aiohttp import web
        
        # Basic 404 response for non-beacon traffic
        return web.Response(status=404)
    
    async def _get_queued_commands(self, beacon_id: str) -> List[Dict[str, Any]]:
        """Get queued commands for beacon"""
        if self.server_core.db_manager:
            return await self.server_core.db_manager.get_pending_commands(beacon_id)
        return []


class HTTPSListener(HTTPListener):
    """HTTPS C2 Listener"""
    
    def __init__(self, host: str, port: int, cert_file: str, key_file: str, server_core: TeamServerCore):
        super().__init__(host, port, server_core)
        self.cert_file = cert_file
        self.key_file = key_file
        self.logger = logging.getLogger(f"{__name__}.HTTPSListener")
    
    async def start(self):
        """Start the HTTPS listener"""
        try:
            import ssl
            from aiohttp import web, web_runner
            
            # Create SSL context
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(self.cert_file, self.key_file)
            
            app = web.Application()
            app.router.add_get("/", self.handle_beacon_checkin)
            app.router.add_post("/", self.handle_beacon_checkin)
            app.router.add_get("/{path:.*}", self.handle_beacon_request)
            app.router.add_post("/{path:.*}", self.handle_beacon_request)
            
            runner = web_runner.AppRunner(app)
            await runner.setup()
            
            site = web_runner.TCPSite(runner, self.host, self.port, ssl_context=ssl_context)
            await site.start()
            
            self._running = True
            self.server = runner
            
        except Exception as e:
            self.logger.error(f"Failed to start HTTPS listener: {e}")
            raise


class DNSListener:
    """DNS C2 Listener"""
    
    def __init__(self, host: str, port: int, server_core: TeamServerCore):
        self.host = host
        self.port = port
        self.server_core = server_core
        self.logger = logging.getLogger(f"{__name__}.DNSListener")
        self._running = False
        self.server = None
    
    async def start(self):
        """Start the DNS listener"""
        try:
            # Basic DNS server implementation
            # This is a placeholder - full DNS C2 would require more complex implementation
            self._running = True
            self.logger.info(f"DNS listener placeholder started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start DNS listener: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the DNS listener"""
        self._running = False
