"""
Ghost Protocol Configuration Management
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 50050
    password: str = ""
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    kill_date: Optional[str] = None
    malleable_c2_profile: Optional[str] = None


@dataclass  
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    username: str = "ghost_protocol"
    password: str = ""
    database: str = "ghost_protocol"
    use_sqlite: bool = True  # Added SQLite option
    sqlite_path: str = "data/ghost_protocol.db"  # Added SQLite path


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    database: int = 0


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    password_min_length: int = 8


@dataclass
class ClientConfig:
    """Client configuration"""
    server_host: str = "localhost"
    server_port: int = 50050
    auto_connect: bool = False
    ui_theme: str = "dark"


@dataclass
class BeaconConfig:
    """Beacon configuration"""
    sleep_time: int = 60
    jitter: int = 20
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    proxy_url: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/ghost_protocol.log"
    max_size: str = "10MB"
    backup_count: int = 5


class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.server = ServerConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.security = SecurityConfig()
        self.client = ClientConfig()
        self.beacon = BeaconConfig()
        self.logging = LoggingConfig()
        self.modules: Dict[str, Dict[str, Any]] = {}
        
        # Load configuration from file
        if config_file:
            self.load_from_file(config_file)
        else:
            # Try to load from default locations
            self._load_default_config()
            
        # Override with environment variables
        self._load_from_env()
        
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from YAML file"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
                
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                
            self._update_from_dict(data)
            
        except Exception as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")
            
    def _load_default_config(self) -> None:
        """Load configuration from default locations"""
        default_paths = [
            "ghost_protocol.yaml",
            "config/ghost_protocol.yaml", 
            "ghost_protocol/config/ghost_protocol.yaml",
            os.path.expanduser("~/.ghost_protocol/config.yaml"),
            "/etc/ghost_protocol/config.yaml"
        ]
        
        for path in default_paths:
            if Path(path).exists():
                self.load_from_file(path)
                break
                
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # Server configuration
        if os.getenv("GP_SERVER_HOST"):
            self.server.host = os.getenv("GP_SERVER_HOST")
        if os.getenv("GP_SERVER_PORT"):
            self.server.port = int(os.getenv("GP_SERVER_PORT"))
        if os.getenv("GP_SERVER_PASSWORD"):
            self.server.password = os.getenv("GP_SERVER_PASSWORD")
            
        # Database configuration
        if os.getenv("GP_DB_HOST"):
            self.database.host = os.getenv("GP_DB_HOST")
        if os.getenv("GP_DB_PORT"):
            self.database.port = int(os.getenv("GP_DB_PORT"))
        if os.getenv("GP_DB_USER"):
            self.database.username = os.getenv("GP_DB_USER")
        if os.getenv("GP_DB_PASSWORD"):
            self.database.password = os.getenv("GP_DB_PASSWORD")
        if os.getenv("GP_DB_NAME"):
            self.database.database = os.getenv("GP_DB_NAME")
        if os.getenv("GP_USE_SQLITE"):
            self.database.use_sqlite = os.getenv("GP_USE_SQLITE").lower() == "true"
        if os.getenv("GP_SQLITE_PATH"):
            self.database.sqlite_path = os.getenv("GP_SQLITE_PATH")
            
        # Security configuration
        if os.getenv("GP_SECRET_KEY"):
            self.security.secret_key = os.getenv("GP_SECRET_KEY")
            
    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        if "server" in data:
            server_data = data["server"]
            self.server.host = server_data.get("host", self.server.host)
            self.server.port = server_data.get("port", self.server.port)
            self.server.password = server_data.get("password", self.server.password)
            self.server.cert_file = server_data.get("cert_file", self.server.cert_file)
            self.server.key_file = server_data.get("key_file", self.server.key_file)
            
        if "database" in data:
            db_data = data["database"]
            self.database.host = db_data.get("host", self.database.host)
            self.database.port = db_data.get("port", self.database.port)
            self.database.username = db_data.get("username", self.database.username)
            self.database.password = db_data.get("password", self.database.password)
            self.database.database = db_data.get("database", self.database.database)
            self.database.use_sqlite = db_data.get("use_sqlite", self.database.use_sqlite)
            self.database.sqlite_path = db_data.get("sqlite_path", self.database.sqlite_path)
            
        if "redis" in data:
            redis_data = data["redis"]
            self.redis.host = redis_data.get("host", self.redis.host)
            self.redis.port = redis_data.get("port", self.redis.port)
            self.redis.password = redis_data.get("password", self.redis.password)
            self.redis.database = redis_data.get("database", self.redis.database)
            
        if "security" in data:
            sec_data = data["security"]
            self.security.secret_key = sec_data.get("secret_key", self.security.secret_key)
            self.security.algorithm = sec_data.get("algorithm", self.security.algorithm)
            self.security.access_token_expire_minutes = sec_data.get("access_token_expire_minutes", self.security.access_token_expire_minutes)
            
        if "client" in data:
            client_data = data["client"]
            self.client.server_host = client_data.get("server_host", self.client.server_host)
            self.client.server_port = client_data.get("server_port", self.client.server_port)
            self.client.auto_connect = client_data.get("auto_connect", self.client.auto_connect)
            self.client.ui_theme = client_data.get("ui_theme", self.client.ui_theme)
            
        if "beacon" in data:
            beacon_data = data["beacon"]
            self.beacon.sleep_time = beacon_data.get("sleep_time", self.beacon.sleep_time)
            self.beacon.jitter = beacon_data.get("jitter", self.beacon.jitter)
            self.beacon.user_agent = beacon_data.get("user_agent", self.beacon.user_agent)
            
        if "logging" in data:
            log_data = data["logging"]
            self.logging.level = log_data.get("level", self.logging.level)
            self.logging.file = log_data.get("file", self.logging.file)
            
        if "modules" in data:
            self.modules = data["modules"]
            
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database.use_sqlite:
            # Ensure data directory exists
            import os
            os.makedirs(os.path.dirname(self.database.sqlite_path), exist_ok=True)
            return f"sqlite+aiosqlite:///{self.database.sqlite_path}"
        
        # PostgreSQL connection (original code)
        if self.database.password:
            return f"postgresql+asyncpg://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.database}"
        else:
            return f"postgresql+asyncpg://{self.database.username}@{self.database.host}:{self.database.port}/{self.database.database}"
            
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.database}"
        else:
            return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.database}"
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split(".")
        obj = self
        
        for k in keys:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            elif isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                return default
                
        return obj
