"""
Ghost Protocol Database Manager
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

try:
    import asyncpg
    import sqlalchemy as sa
    from sqlalchemy import create_engine
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from .models import Base, Beacon, Session, Command, CommandResult, User, Listener
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False


class DatabaseManager:
    """Database management for Ghost Protocol"""
    
    def __init__(self, database_url: str = None, config=None):
        self.config = config or {}
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.async_engine = None
        self.async_session = None
        self._initialized = False
    
    def setup_database(self):
        """Setup synchronous database for testing purposes"""
        if not HAS_DATABASE:
            self.logger.warning("Database dependencies not available")
            return False
        
        try:
            # Create synchronous engine for setup
            if self.database_url:
                engine_url = self.database_url.replace('+asyncpg', '').replace('+aiomysql', '').replace('+aiosqlite', '')
            else:
                engine_url = 'sqlite:///ghost_protocol.db'
            
            self.engine = create_engine(engine_url)
            Base.metadata.create_all(self.engine)
            
            self.logger.info("Database setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup database: {e}")
            return False
        
    async def initialize(self) -> bool:
        """Initialize database connection"""
        try:
            if not HAS_DATABASE:
                self.logger.warning("Database dependencies not available, using in-memory storage")
                return True
            
            if isinstance(self.config, str):
                # If config is a string, treat it as database URL
                db_url = self.config
            elif hasattr(self.config, 'get_database_url'):
                # If config has get_database_url method, use it
                db_url = self.config.get_database_url()
            elif self.database_url:
                # Use provided database URL
                db_url = self.database_url
            else:
                # Use SQLite as fallback
                db_url = "sqlite+aiosqlite:///data/ghost_protocol.db"
                # Ensure data directory exists
                import os
                os.makedirs("data", exist_ok=True)
            
            self.logger.info(f"Connecting to database: {db_url.split('://')[0]}://...")
            
            # Create async engine
            self.async_engine = create_async_engine(
                db_url,
                echo=self.config.get('debug', False) if isinstance(self.config, dict) else False,
                pool_pre_ping=True
            )
            
            # Create session factory
            self.async_session = sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._initialized = True
            self.logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        self.logger.info("Database connections closed")
    
    def _build_database_url(self) -> str:
        """Build database URL from configuration"""
        if isinstance(self.config, dict):
            db_config = self.config.get('database', {})
        else:
            db_config = getattr(self.config, 'database', {}) if hasattr(self.config, 'database') else {}
        
        if isinstance(db_config, dict):
            url = db_config.get('url')
            if url:
                return url
            
            # Build from components
            driver = db_config.get('driver', 'postgresql+asyncpg')
            username = db_config.get('username', 'ghost')
            password = db_config.get('password', 'protocol')
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 5432)
            database = db_config.get('database', 'ghost_protocol')
            
            return f"{driver}://{username}:{password}@{host}:{port}/{database}"
        else:
            # Handle object-style config
            if hasattr(db_config, 'url') and db_config.url:
                return db_config.url
            
            # Build from components
            driver = getattr(db_config, 'driver', 'postgresql+asyncpg')
            username = getattr(db_config, 'username', 'ghost')
            password = getattr(db_config, 'password', 'protocol')
            host = getattr(db_config, 'host', 'localhost')
            port = getattr(db_config, 'port', 5432)
            database = getattr(db_config, 'database', 'ghost_protocol')
            
            return f"{driver}://{username}:{password}@{host}:{port}/{database}"
    
    async def create_beacon(self, beacon_id: str, system_info: Dict[str, Any], listener_id: str) -> bool:
        """Create a new beacon record"""
        if not self._initialized or not HAS_DATABASE:
            return True
        
        try:
            async with self.async_session() as session:
                beacon = Beacon(
                    id=beacon_id,
                    listener_id=listener_id,
                    hostname=system_info.get('hostname', 'unknown'),
                    username=system_info.get('username', 'unknown'),
                    os_name=system_info.get('os_name', 'unknown'),
                    os_version=system_info.get('os_version', 'unknown'),
                    architecture=system_info.get('architecture', 'unknown'),
                    pid=system_info.get('pid', 0),
                    system_info=json.dumps(system_info),
                    first_seen=datetime.now(timezone.utc),
                    last_seen=datetime.now(timezone.utc),
                    status='active'
                )
                
                session.add(beacon)
                await session.commit()
                
            self.logger.info(f"Created beacon record: {beacon_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create beacon: {e}")
            return False
    
    async def update_beacon_checkin(self, beacon_id: str) -> bool:
        """Update beacon last seen timestamp"""
        if not self._initialized or not HAS_DATABASE:
            return True
        
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    sa.update(Beacon)
                    .where(Beacon.id == beacon_id)
                    .values(last_seen=datetime.now(timezone.utc), status='active')
                )
                await session.commit()
                
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update beacon checkin: {e}")
            return False
    
    async def create_session(self, session_id: str, beacon_id: str, session_type: str) -> bool:
        """Create a new session record"""
        if not self._initialized or not HAS_DATABASE:
            return True
        
        try:
            async with self.async_session() as session:
                session_record = Session(
                    id=session_id,
                    beacon_id=beacon_id,
                    session_type=session_type,
                    created_at=datetime.now(timezone.utc),
                    status='active'
                )
                
                session.add(session_record)
                await session.commit()
                
            self.logger.info(f"Created session: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return False
    
    async def close_session(self, session_id: str) -> bool:
        """Close a session"""
        if not self._initialized or not HAS_DATABASE:
            return True
        
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    sa.update(Session)
                    .where(Session.id == session_id)
                    .values(status='closed', closed_at=datetime.now(timezone.utc))
                )
                await session.commit()
                
            return result.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to close session: {e}")
            return False
    
    async def create_command(self, command_id: str, beacon_id: str, command: str, args: Dict[str, Any]) -> bool:
        """Create a new command record"""
        if not self._initialized or not HAS_DATABASE:
            return True
        
        try:
            async with self.async_session() as session:
                command_record = Command(
                    id=command_id,
                    beacon_id=beacon_id,
                    command=command,
                    args=json.dumps(args),
                    created_at=datetime.now(timezone.utc),
                    status='pending'
                )
                
                session.add(command_record)
                await session.commit()
                
            self.logger.info(f"Created command: {command_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create command: {e}")
            return False
    
    async def get_pending_commands(self, beacon_id: str) -> List[Dict[str, Any]]:
        """Get pending commands for a beacon"""
        if not self._initialized or not HAS_DATABASE:
            return []
        
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    sa.select(Command)
                    .where(Command.beacon_id == beacon_id, Command.status == 'pending')
                    .order_by(Command.created_at)
                )
                
                commands = result.scalars().all()
                
                # Mark commands as sent
                if commands:
                    await session.execute(
                        sa.update(Command)
                        .where(Command.beacon_id == beacon_id, Command.status == 'pending')
                        .values(status='sent', sent_at=datetime.now(timezone.utc))
                    )
                    await session.commit()
                
                return [
                    {
                        "id": cmd.id,
                        "command": cmd.command,
                        "args": json.loads(cmd.args) if cmd.args else {}
                    }
                    for cmd in commands
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get pending commands: {e}")
            return []
    
    async def store_command_result(self, command_id: str, beacon_id: str, output: str, success: bool) -> bool:
        """Store command execution result"""
        if not self._initialized or not HAS_DATABASE:
            return True
        
        try:
            async with self.async_session() as session:
                # Create result record
                result_record = CommandResult(
                    id=f"{command_id}_result",
                    command_id=command_id,
                    beacon_id=beacon_id,
                    output=output,
                    success=success,
                    received_at=datetime.now(timezone.utc)
                )
                
                session.add(result_record)
                
                # Update command status
                await session.execute(
                    sa.update(Command)
                    .where(Command.id == command_id)
                    .values(status='completed', completed_at=datetime.now(timezone.utc))
                )
                
                await session.commit()
                
            self.logger.info(f"Stored command result: {command_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store command result: {e}")
            return False
    
    async def get_beacons(self) -> List[Dict[str, Any]]:
        """Get all beacons"""
        if not self._initialized or not HAS_DATABASE:
            return []
        
        try:
            async with self.async_session() as session:
                result = await session.execute(sa.select(Beacon))
                beacons = result.scalars().all()
                
                return [
                    {
                        "id": beacon.id,
                        "hostname": beacon.hostname,
                        "username": beacon.username,
                        "os_name": beacon.os_name,
                        "os_version": beacon.os_version,
                        "architecture": beacon.architecture,
                        "pid": beacon.pid,
                        "first_seen": beacon.first_seen.isoformat() if beacon.first_seen else None,
                        "last_seen": beacon.last_seen.isoformat() if beacon.last_seen else None,
                        "status": beacon.status,
                        "listener_id": beacon.listener_id
                    }
                    for beacon in beacons
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get beacons: {e}")
            return []
    
    async def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions"""
        if not self._initialized or not HAS_DATABASE:
            return []
        
        try:
            async with self.async_session() as session:
                result = await session.execute(sa.select(Session))
                sessions = result.scalars().all()
                
                return [
                    {
                        "id": sess.id,
                        "beacon_id": sess.beacon_id,
                        "session_type": sess.session_type,
                        "created_at": sess.created_at.isoformat() if sess.created_at else None,
                        "closed_at": sess.closed_at.isoformat() if sess.closed_at else None,
                        "status": sess.status
                    }
                    for sess in sessions
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get sessions: {e}")
            return []
