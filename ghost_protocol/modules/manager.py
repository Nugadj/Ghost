"""
Ghost Protocol Module Manager
"""

import asyncio
import logging
import importlib
import inspect
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core import EventBus, ServerModule, ClientModule, BeaconModule


class ModuleManager:
    """Manages loadable modules"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger("ghost_protocol.modules")
        
        # Loaded modules
        self.server_modules: Dict[str, ServerModule] = {}
        self.client_modules: Dict[str, ClientModule] = {}
        self.beacon_modules: Dict[str, BeaconModule] = {}
        
    async def initialize(self) -> bool:
        """Initialize module manager"""
        try:
            # Load core modules
            await self._load_core_modules()
            
            self.logger.info("Module manager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize module manager: {e}")
            return False
            
    async def shutdown(self) -> bool:
        """Shutdown module manager"""
        try:
            # Unload all modules
            for module_name in list(self.server_modules.keys()):
                await self.unload_server_module(module_name)
                
            for module_name in list(self.client_modules.keys()):
                await self.unload_client_module(module_name)
                
            for module_name in list(self.beacon_modules.keys()):
                await self.unload_beacon_module(module_name)
                
            self.logger.info("Module manager shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error shutting down module manager: {e}")
            return False
            
    async def _load_core_modules(self):
        """Load core modules"""
        try:
            # Import and load core modules
            from .reconnaissance import ReconnaissanceModule
            from .weaponization import WeaponizationModule  
            from .delivery import DeliveryModule
            from .lateral_movement import LateralMovementModule
            from .user_exploitation import UserExploitationModule
            from .reporting import ReportingModule
            
            # Load server modules
            modules = [
                ("reconnaissance", ReconnaissanceModule),
                ("weaponization", WeaponizationModule),
                ("delivery", DeliveryModule), 
                ("lateral_movement", LateralMovementModule),
                ("user_exploitation", UserExploitationModule),
                ("reporting", ReportingModule)
            ]
            
            for name, module_class in modules:
                try:
                    module = module_class(name, self.config.get(f"modules.{name}", {}))
                    if await module.initialize():
                        self.server_modules[name] = module
                        self.logger.info(f"Loaded core module: {name}")
                    else:
                        self.logger.error(f"Failed to initialize module: {name}")
                except Exception as e:
                    self.logger.error(f"Error loading module {name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error loading core modules: {e}")
            
    async def load_server_module(self, module_path: str, module_name: Optional[str] = None) -> Optional[ServerModule]:
        """Load a server module"""
        try:
            if not module_name:
                module_name = Path(module_path).stem
                
            # Import module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find ServerModule class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, ServerModule) and 
                    obj != ServerModule):
                    
                    # Create instance
                    instance = obj(module_name, self.config.get(f"modules.{module_name}", {}))
                    
                    if await instance.initialize():
                        self.server_modules[module_name] = instance
                        self.logger.info(f"Loaded server module: {module_name}")
                        return instance
                        
            self.logger.error(f"No ServerModule class found in {module_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading server module {module_path}: {e}")
            return None
            
    async def unload_server_module(self, module_name: str) -> bool:
        """Unload a server module"""
        try:
            if module_name not in self.server_modules:
                return False
                
            module = self.server_modules[module_name]
            await module.shutdown()
            
            del self.server_modules[module_name]
            self.logger.info(f"Unloaded server module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading server module {module_name}: {e}")
            return False
            
    def get_server_module(self, module_name: str) -> Optional[ServerModule]:
        """Get server module by name"""
        return self.server_modules.get(module_name)
        
    def list_server_modules(self) -> List[str]:
        """List loaded server modules"""
        return list(self.server_modules.keys())
        
    async def load_client_module(self, module_path: str, module_name: Optional[str] = None) -> Optional[ClientModule]:
        """Load a client module"""
        # Similar implementation to load_server_module but for ClientModule
        pass
        
    async def unload_client_module(self, module_name: str) -> bool:
        """Unload a client module"""
        # Similar implementation to unload_server_module
        pass
        
    async def load_beacon_module(self, module_path: str, module_name: Optional[str] = None) -> Optional[BeaconModule]:
        """Load a beacon module"""
        # Similar implementation to load_server_module but for BeaconModule
        pass
        
    async def unload_beacon_module(self, module_name: str) -> bool:
        """Unload a beacon module"""
        # Similar implementation to unload_server_module
        pass
        
    async def handle_command(self, command: str, args: Dict[str, Any], 
                           user_id: str, operation_id: Optional[str]) -> Dict[str, Any]:
        """Handle module commands"""
        try:
            if command == "module_list":
                return {
                    "success": True,
                    "modules": {
                        "server": self.list_server_modules(),
                        "client": list(self.client_modules.keys()),
                        "beacon": list(self.beacon_modules.keys())
                    }
                }
                
            elif command == "module_execute":
                module_name = args.get("module")
                module_command = args.get("command")
                module_args = args.get("args", {})
                
                if not module_name or not module_command:
                    return {"success": False, "error": "Module and command required"}
                    
                # Find and execute on appropriate module
                if module_name in self.server_modules:
                    module = self.server_modules[module_name]
                    result = await module.execute_command(module_command, module_args)
                    return {"success": True, "result": result}
                else:
                    return {"success": False, "error": f"Module '{module_name}' not found"}
                    
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
                
        except Exception as e:
            self.logger.error(f"Error handling command {command}: {e}")
            return {"success": False, "error": str(e)}
