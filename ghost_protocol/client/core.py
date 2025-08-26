"""
Ghost Protocol Client Core - Enhanced with console management and session handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
import httpx
import websockets
import json
from datetime import datetime
from enum import Enum

from ..core import EventBus, EventType, Config


class SessionType(Enum):
    """Types of console sessions"""
    MAIN = "main"
    BEACON = "beacon"
    LISTENER = "listener"
    MODULE = "module"


class ConsoleSession:
    """Represents a console session"""
    
    def __init__(self, session_id: str, session_type: SessionType, 
                 name: str, target_id: Optional[str] = None):
        self.session_id = session_id
        self.session_type = session_type
        self.name = name
        self.target_id = target_id  # beacon_id, listener_id, etc.
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.command_history: List[Dict[str, Any]] = []
        self.is_active = True
        
    def add_command(self, command: str, output: str, success: bool = True):
        """Add command to session history"""
        self.command_history.append({
            "timestamp": datetime.now(),
            "command": command,
            "output": output,
            "success": success
        })
        self.last_activity = datetime.now()
        
    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commands from session"""
        return self.command_history[-limit:] if self.command_history else []


class ServerConnection:
    """Represents a connection to a team server"""
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.http_client: Optional[httpx.AsyncClient] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.access_token: Optional[str] = None
        self.connected = False
        
        self.logger = logging.getLogger(f"ghost_protocol.client.connection.{host}")
        
    async def connect(self) -> bool:
        """Connect to the server"""
        try:
            # Create HTTP client
            self.http_client = httpx.AsyncClient(
                base_url=f"http://{self.host}:{self.port}",
                timeout=30.0
            )
            
            # Authenticate
            response = await self.http_client.post("/api/v1/auth/login", json={
                "username": self.username,
                "password": self.password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                
                # Set authorization header
                self.http_client.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                # Connect WebSocket
                await self._connect_websocket()
                
                self.connected = True
                self.logger.info(f"Connected to server {self.host}:{self.port}")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
            
    async def disconnect(self) -> bool:
        """Disconnect from the server"""
        try:
            if self.websocket:
                await self.websocket.close()
                
            if self.http_client:
                await self.http_client.aclose()
                
            self.connected = False
            self.logger.info("Disconnected from server")
            return True
            
        except Exception as e:
            self.logger.error(f"Disconnect error: {e}")
            return False
            
    async def _connect_websocket(self) -> None:
        """Connect WebSocket for real-time updates"""
        try:
            ws_url = f"ws://{self.host}:{self.port}/ws/client_{self.username}"
            self.websocket = await websockets.connect(ws_url)
            self.logger.info("WebSocket connected")
            
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            
    async def send_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to server"""
        try:
            if not self.connected or not self.http_client:
                return {"success": False, "error": "Not connected"}
                
            response = await self.http_client.post("/api/v1/command", json={
                "command": command,
                "args": args
            })
            
            return response.json()
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class ClientCore:
    """Enhanced client core with console management functionality"""
    
    def __init__(self, config: Config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger("ghost_protocol.client.core")
        
        # Server connections
        self.connections: Dict[str, ServerConnection] = {}
        self.active_connection: Optional[ServerConnection] = None
        
        # Client state
        self.operations: Dict[str, Dict] = {}
        self.beacons: Dict[str, Dict] = {}
        self.listeners: Dict[str, Dict] = {}
        self.targets: Dict[str, Dict] = {}
        self.sessions_data: Dict[str, Dict] = {}
        
        self.console_sessions: Dict[str, ConsoleSession] = {}
        self.active_session_id: Optional[str] = None
        self.command_callbacks: Dict[str, Callable] = {}
        
        # Initialize main console session
        main_session = ConsoleSession("main", SessionType.MAIN, "Main Console")
        self.console_sessions["main"] = main_session
        self.active_session_id = "main"
        
    async def initialize(self) -> bool:
        """Initialize client core"""
        try:
            self.logger.info("Initializing client core")
            
            self._register_command_handlers()
            
            # Auto-connect if configured
            if self.config.client.auto_connect:
                await self.connect_to_server(
                    self.config.client.server_host,
                    self.config.client.server_port
                )
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize client core: {e}")
            return False
            
    def _register_command_handlers(self):
        """Register default command handlers"""
        self.command_callbacks.update({
            "beacons": self._handle_beacons_command,
            "listeners": self._handle_listeners_command,
            "targets": self._handle_targets_command,
            "sessions": self._handle_sessions_command,
            "interact": self._handle_interact_command,
            "background": self._handle_background_command,
            "kill": self._handle_kill_command,
            "killall": self._handle_killall_command,
            "upload": self._handle_upload_command,
            "download": self._handle_download_command,
            "screenshot": self._handle_screenshot_command,
            "shell": self._handle_shell_command,
            "ps": self._handle_ps_command,
            "ls": self._handle_ls_command,
            "cd": self._handle_cd_command,
            "pwd": self._handle_pwd_command
        })
        
    async def shutdown(self) -> bool:
        """Shutdown client core"""
        try:
            # Disconnect all connections
            for connection in self.connections.values():
                await connection.disconnect()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error shutting down client core: {e}")
            return False
            
    async def connect_to_server(self, host: str, port: int, 
                              username: str = "admin", password: str = "") -> bool:
        """Connect to a team server"""
        try:
            connection_id = f"{host}:{port}"
            
            if connection_id in self.connections:
                self.logger.warning(f"Already connected to {connection_id}")
                return True
                
            connection = ServerConnection(host, port, username, password)
            
            if await connection.connect():
                self.connections[connection_id] = connection
                self.active_connection = connection
                
                # Publish connection event
                await self.event_bus.publish_event(
                    EventType.USER_LOGIN,
                    {"server": f"{host}:{port}", "username": username}
                )
                
                # Initial data refresh
                await self.refresh_data()
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to server: {e}")
            return False
            
    async def disconnect_from_server(self, connection_id: str) -> bool:
        """Disconnect from a server"""
        try:
            if connection_id not in self.connections:
                return False
                
            connection = self.connections[connection_id]
            await connection.disconnect()
            
            del self.connections[connection_id]
            
            if self.active_connection == connection:
                self.active_connection = None
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from server: {e}")
            return False
            
    async def execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command on active server"""
        try:
            if not self.active_connection:
                return {"success": False, "error": "No active connection"}
                
            return await self.active_connection.send_command(command, args)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def process_console_command(self, command_line: str, session_id: str = None) -> Dict[str, Any]:
        """Process console command with session context"""
        if not session_id:
            session_id = self.active_session_id or "main"
            
        session = self.console_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Invalid session"}
            
        parts = command_line.strip().split()
        if not parts:
            return {"success": False, "error": "Empty command"}
            
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            # Check for registered command handler
            if command in self.command_callbacks:
                result = await self.command_callbacks[command](args, session)
            else:
                # Handle session-specific commands
                if session.session_type == SessionType.BEACON:
                    result = await self._handle_beacon_command(command, args, session)
                elif session.session_type == SessionType.LISTENER:
                    result = await self._handle_listener_command(command, args, session)
                else:
                    result = {"success": False, "error": f"Unknown command: {command}"}
                    
            # Add to session history
            session.add_command(
                command_line, 
                result.get("output", ""), 
                result.get("success", False)
            )
            
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            session.add_command(command_line, str(e), False)
            return error_result
            
    def create_console_session(self, session_type: SessionType, name: str, 
                             target_id: Optional[str] = None) -> str:
        """Create a new console session"""
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        session = ConsoleSession(session_id, session_type, name, target_id)
        self.console_sessions[session_id] = session
        
        return session_id
        
    def switch_console_session(self, session_id: str) -> bool:
        """Switch to a different console session"""
        if session_id in self.console_sessions:
            self.active_session_id = session_id
            return True
        return False
        
    def close_console_session(self, session_id: str) -> bool:
        """Close a console session"""
        if session_id == "main":
            return False  # Cannot close main session
            
        if session_id in self.console_sessions:
            del self.console_sessions[session_id]
            
            # Switch to main if this was active
            if self.active_session_id == session_id:
                self.active_session_id = "main"
                
            return True
        return False
        
    def get_console_sessions(self) -> List[Dict[str, Any]]:
        """Get list of console sessions"""
        return [
            {
                "session_id": session.session_id,
                "name": session.name,
                "type": session.session_type.value,
                "target_id": session.target_id,
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "is_active": session.session_id == self.active_session_id,
                "command_count": len(session.command_history)
            }
            for session in self.console_sessions.values()
        ]
        
    async def _handle_beacons_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle beacons command"""
        await self.refresh_data()
        
        if not self.beacons:
            return {"success": True, "output": "No active beacons"}
            
        output_lines = [f"Active beacons ({len(self.beacons)}):"]
        for beacon_id, beacon in self.beacons.items():
            hostname = beacon.get('hostname', 'Unknown')
            ip_address = beacon.get('ip_address', '0.0.0.0')
            status = beacon.get('status', 'unknown')
            last_checkin = beacon.get('last_checkin', 'Never')
            
            output_lines.append(f"  {beacon_id[:8]} - {hostname} ({ip_address}) [{status}] - {last_checkin}")
            
        return {"success": True, "output": "\n".join(output_lines)}
        
    async def _handle_listeners_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle listeners command"""
        await self.refresh_data()
        
        if not self.listeners:
            return {"success": True, "output": "No active listeners"}
            
        output_lines = [f"Active listeners ({len(self.listeners)}):"]
        for listener_id, listener in self.listeners.items():
            name = listener.get('name', 'Unknown')
            host = listener.get('host', '0.0.0.0')
            port = listener.get('port', 0)
            protocol = listener.get('protocol', 'unknown')
            status = listener.get('status', 'unknown')
            
            output_lines.append(f"  {name} - {protocol}://{host}:{port} [{status}]")
            
        return {"success": True, "output": "\n".join(output_lines)}
        
    async def _handle_targets_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle targets command"""
        await self.refresh_data()
        
        if not self.targets:
            return {"success": True, "output": "No targets discovered"}
            
        output_lines = [f"Discovered targets ({len(self.targets)}):"]
        for target_id, target in self.targets.items():
            hostname = target.get('hostname', 'Unknown')
            ip_address = target.get('ip_address', '0.0.0.0')
            os_type = target.get('os_type', 'Unknown')
            status = target.get('status', 'unknown')
            
            output_lines.append(f"  {ip_address} - {hostname} ({os_type}) [{status}]")
            
        return {"success": True, "output": "\n".join(output_lines)}
        
    async def _handle_sessions_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle sessions command"""
        sessions = self.get_console_sessions()
        
        output_lines = [f"Console sessions ({len(sessions)}):"]
        for sess in sessions:
            active_marker = " *" if sess["is_active"] else ""
            output_lines.append(f"  {sess['session_id']} - {sess['name']} ({sess['type']}){active_marker}")
            
        return {"success": True, "output": "\n".join(output_lines)}
        
    async def _handle_interact_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle interact command"""
        if not args:
            return {"success": False, "error": "Usage: interact <beacon_id>"}
            
        beacon_id_prefix = args[0]
        
        # Find matching beacon
        matching_beacon = None
        for beacon_id, beacon in self.beacons.items():
            if beacon_id.startswith(beacon_id_prefix):
                matching_beacon = beacon
                break
                
        if not matching_beacon:
            return {"success": False, "error": f"Beacon {beacon_id_prefix} not found"}
            
        # Create beacon session
        hostname = matching_beacon.get('hostname', 'Unknown')
        session_name = f"Beacon - {hostname}"
        new_session_id = self.create_console_session(SessionType.BEACON, session_name, beacon_id)
        
        # Switch to new session
        self.switch_console_session(new_session_id)
        
        return {
            "success": True, 
            "output": f"Interacting with beacon {beacon_id_prefix} ({hostname})",
            "session_switch": new_session_id
        }
        
    async def _handle_background_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle background command"""
        if session.session_id == "main":
            return {"success": False, "error": "Already in main console"}
            
        self.switch_console_session("main")
        return {
            "success": True, 
            "output": "Backgrounded session, returned to main console",
            "session_switch": "main"
        }
        
    async def _handle_beacon_command(self, command: str, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle beacon-specific commands"""
        if not session.target_id:
            return {"success": False, "error": "No beacon associated with session"}
            
        # Send command to specific beacon
        result = await self.execute_command("beacon_command", {
            "beacon_id": session.target_id,
            "command": command,
            "args": args
        })
        
        return result
        
    async def _handle_listener_command(self, command: str, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle listener-specific commands"""
        if not session.target_id:
            return {"success": False, "error": "No listener associated with session"}
            
        # Send command to specific listener
        result = await self.execute_command("listener_command", {
            "listener_id": session.target_id,
            "command": command,
            "args": args
        })
        
        return result

    async def refresh_data(self) -> None:
        """Refresh data from server"""
        try:
            if not self.active_connection:
                return
                
            # Refresh operations
            result = await self.execute_command("list_operations", {})
            if result.get("success"):
                self.operations = {op["operation_id"]: op for op in result.get("operations", [])}
                
            # Refresh beacons
            result = await self.execute_command("beacon_list", {})
            if result.get("success"):
                self.beacons = {b["beacon_id"]: b for b in result.get("beacons", [])}
                
            # Refresh listeners
            result = await self.execute_command("listener_list", {})
            if result.get("success"):
                self.listeners = {l["listener_id"]: l for l in result.get("listeners", [])}
                
            # Refresh targets
            result = await self.execute_command("target_list", {})
            if result.get("success"):
                self.targets = {t["target_id"]: t for t in result.get("targets", [])}
                
            # Refresh sessions
            result = await self.execute_command("session_list", {})
            if result.get("success"):
                self.sessions_data = {s["session_id"]: s for s in result.get("sessions", [])}
                
        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
            
    def get_server_status(self) -> Dict[str, Any]:
        """Get server connection status"""
        return {
            "connected": self.active_connection is not None,
            "server": f"{self.active_connection.host}:{self.active_connection.port}" if self.active_connection else None,
            "operations": len(self.operations),
            "beacons": len(self.beacons),
            "listeners": len(self.listeners),
            "targets": len(self.targets),
            "console_sessions": len(self.console_sessions)
        }
        
    def get_beacons(self) -> List[Dict[str, Any]]:
        """Get list of beacons for UI components"""
        return list(self.beacons.values())
        
    def get_listeners(self) -> List[Dict[str, Any]]:
        """Get list of listeners for UI components"""
        return list(self.listeners.values())
        
    def get_targets(self) -> List[Dict[str, Any]]:
        """Get list of targets for UI components"""
        return list(self.targets.values())
        
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get list of sessions for UI components"""
        return list(self.sessions_data.values())
        
    async def kill_beacon(self, beacon_id: str) -> bool:
        """Kill a specific beacon"""
        result = await self.execute_command("beacon_kill", {"beacon_id": beacon_id})
        return result.get("success", False)
        
    async def kill_all_beacons(self) -> bool:
        """Kill all beacons"""
        result = await self.execute_command("beacon_kill_all", {})
        return result.get("success", False)
        
    # Placeholder command handlers for file operations and system commands
    async def _handle_kill_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle kill command"""
        if not args:
            return {"success": False, "error": "Usage: kill <beacon_id>"}
        return await self._handle_beacon_command("kill", args, session)
        
    async def _handle_killall_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle killall command"""
        result = await self.kill_all_beacons()
        return {"success": result, "output": "All beacons killed" if result else "Failed to kill beacons"}
        
    async def _handle_upload_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle upload command"""
        if len(args) < 2:
            return {"success": False, "error": "Usage: upload <local_file> <remote_path>"}
        return await self._handle_beacon_command("upload", args, session)
        
    async def _handle_download_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle download command"""
        if len(args) < 2:
            return {"success": False, "error": "Usage: download <remote_file> <local_path>"}
        return await self._handle_beacon_command("download", args, session)
        
    async def _handle_screenshot_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle screenshot command"""
        return await self._handle_beacon_command("screenshot", args, session)
        
    async def _handle_shell_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle shell command"""
        if not args:
            return {"success": False, "error": "Usage: shell <command>"}
        return await self._handle_beacon_command("shell", args, session)
        
    async def _handle_ps_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle ps command"""
        return await self._handle_beacon_command("ps", args, session)
        
    async def _handle_ls_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle ls command"""
        return await self._handle_beacon_command("ls", args, session)
        
    async def _handle_cd_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle cd command"""
        if not args:
            return {"success": False, "error": "Usage: cd <path>"}
        return await self._handle_beacon_command("cd", args, session)
        
    async def _handle_pwd_command(self, args: List[str], session: ConsoleSession) -> Dict[str, Any]:
        """Handle pwd command"""
        return await self._handle_beacon_command("pwd", args, session)
