"""
Ghost Protocol Database Models
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(String(20), default='operator')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)


class Listener(Base):
    """C2 Listener model"""
    __tablename__ = 'listeners'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    protocol = Column(String(20), nullable=False)  # http, https, dns
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String(20), default='stopped')
    config = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)
    
    # Relationships
    beacons = relationship("Beacon", back_populates="listener")


class Beacon(Base):
    """Beacon model for tracking compromised hosts"""
    __tablename__ = 'beacons'
    
    id = Column(String(36), primary_key=True)
    listener_id = Column(String(36), ForeignKey('listeners.id'), nullable=False)
    hostname = Column(String(255))
    username = Column(String(100))
    os_name = Column(String(50))
    os_version = Column(String(100))
    architecture = Column(String(20))
    pid = Column(Integer)
    system_info = Column(JSON)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default='active')  # active, inactive, lost
    
    # Relationships
    listener = relationship("Listener", back_populates="beacons")
    sessions = relationship("Session", back_populates="beacon")
    commands = relationship("Command", back_populates="beacon")
    command_results = relationship("CommandResult", back_populates="beacon")


class Session(Base):
    """Interactive session model"""
    __tablename__ = 'sessions'
    
    id = Column(String(36), primary_key=True)
    beacon_id = Column(String(36), ForeignKey('beacons.id'), nullable=False)
    session_type = Column(String(20), default='shell')  # shell, meterpreter, etc
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime)
    status = Column(String(20), default='active')  # active, closed
    
    # Relationships
    beacon = relationship("Beacon", back_populates="sessions")


class Command(Base):
    """Command model for tracking executed commands"""
    __tablename__ = 'commands'
    
    id = Column(String(36), primary_key=True)
    beacon_id = Column(String(36), ForeignKey('beacons.id'), nullable=False)
    session_id = Column(String(36), ForeignKey('sessions.id'))
    command = Column(String(500), nullable=False)
    args = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, completed, failed
    
    # Relationships
    beacon = relationship("Beacon", back_populates="commands")
    session = relationship("Session")
    results = relationship("CommandResult", back_populates="command")


class CommandResult(Base):
    """Command execution result model"""
    __tablename__ = 'command_results'
    
    id = Column(String(36), primary_key=True)
    command_id = Column(String(36), ForeignKey('commands.id'), nullable=False)
    beacon_id = Column(String(36), ForeignKey('beacons.id'), nullable=False)
    output = Column(Text)
    success = Column(Boolean, default=True)
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    command = relationship("Command", back_populates="results")
    beacon = relationship("Beacon", back_populates="command_results")


class Module(Base):
    """Module model for tracking loaded modules"""
    __tablename__ = 'modules'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    module_type = Column(String(50), nullable=False)  # server, client, beacon
    version = Column(String(20))
    description = Column(Text)
    config = Column(JSON)
    enabled = Column(Boolean, default=True)
    loaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Operation(Base):
    """Operation model for tracking red team operations"""
    __tablename__ = 'operations'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime)
    status = Column(String(20), default='active')  # active, completed, paused
    operation_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict


class Task(Base):
    """Task model for tracking scheduled tasks"""
    __tablename__ = 'tasks'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    config = Column(JSON)


class AuditLog(Base):
    """Audit log model for tracking system events"""
    __tablename__ = 'audit_logs'
    
    id = Column(String(36), primary_key=True)
    event_type = Column(String(50), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'))
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source_ip = Column(String(45))  # IPv6 compatible
    log_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Relationships
    user = relationship("User")


class LogEntry(Base):
    """Log entry model for audit trail"""
    __tablename__ = 'log_entries'
    
    id = Column(String(36), primary_key=True)
    level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    source = Column(String(100))  # beacon_id, user_id, etc
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    log_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
