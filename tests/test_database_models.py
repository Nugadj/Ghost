"""
Tests for Ghost Protocol database models
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from ghost_protocol.database.models import (
    User, Listener, Beacon, Session, Command, CommandResult,
    Module, Operation, Task, AuditLog, LogEntry
)


class TestUserModel:
    """Test the User model"""
    
    def test_user_creation(self, db_session):
        """Test creating a user"""
        user = User(
            id="user-123",
            username="testuser",
            password_hash="hashed_password",
            email="test@example.com",
            role="operator"
        )
        
        db_session.add(user)
        db_session.commit()
        
        retrieved_user = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.role == "operator"
        assert retrieved_user.is_active is True
    
    def test_user_unique_constraints(self, db_session):
        """Test user unique constraints"""
        user1 = User(
            id="user-123",
            username="testuser",
            password_hash="hash1",
            email="test@example.com"
        )
        
        user2 = User(
            id="user-456",
            username="testuser",  # Duplicate username
            password_hash="hash2",
            email="test2@example.com"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestListenerModel:
    """Test the Listener model"""
    
    def test_listener_creation(self, db_session):
        """Test creating a listener"""
        listener = Listener(
            id="listener-123",
            name="HTTP Listener",
            protocol="http",
            host="0.0.0.0",
            port=8080,
            status="running"
        )
        
        db_session.add(listener)
        db_session.commit()
        
        retrieved = db_session.query(Listener).filter_by(name="HTTP Listener").first()
        assert retrieved is not None
        assert retrieved.protocol == "http"
        assert retrieved.port == 8080
        assert retrieved.status == "running"


class TestBeaconModel:
    """Test the Beacon model"""
    
    def test_beacon_creation(self, db_session):
        """Test creating a beacon"""
        # First create a listener
        listener = Listener(
            id="listener-123",
            name="Test Listener",
            protocol="http",
            host="0.0.0.0",
            port=8080
        )
        db_session.add(listener)
        db_session.commit()
        
        # Create beacon
        beacon = Beacon(
            id="beacon-123",
            listener_id="listener-123",
            hostname="test-host",
            username="test-user",
            os_name="Windows",
            os_version="10",
            architecture="x64",
            pid=1234
        )
        
        db_session.add(beacon)
        db_session.commit()
        
        retrieved = db_session.query(Beacon).filter_by(hostname="test-host").first()
        assert retrieved is not None
        assert retrieved.listener_id == "listener-123"
        assert retrieved.username == "test-user"
        assert retrieved.status == "active"
    
    def test_beacon_listener_relationship(self, db_session):
        """Test beacon-listener relationship"""
        listener = Listener(
            id="listener-123",
            name="Test Listener",
            protocol="http",
            host="0.0.0.0",
            port=8080
        )
        
        beacon = Beacon(
            id="beacon-123",
            listener_id="listener-123",
            hostname="test-host"
        )
        
        db_session.add(listener)
        db_session.add(beacon)
        db_session.commit()
        
        # Test relationship
        retrieved_beacon = db_session.query(Beacon).first()
        assert retrieved_beacon.listener.name == "Test Listener"
        
        retrieved_listener = db_session.query(Listener).first()
        assert len(retrieved_listener.beacons) == 1
        assert retrieved_listener.beacons[0].hostname == "test-host"


class TestCommandModel:
    """Test the Command model"""
    
    def test_command_creation(self, db_session):
        """Test creating a command"""
        # Setup dependencies
        listener = Listener(
            id="listener-123",
            name="Test Listener",
            protocol="http",
            host="0.0.0.0",
            port=8080
        )
        
        beacon = Beacon(
            id="beacon-123",
            listener_id="listener-123",
            hostname="test-host"
        )
        
        command = Command(
            id="command-123",
            beacon_id="beacon-123",
            command="whoami",
            args={"verbose": True},
            status="pending"
        )
        
        db_session.add_all([listener, beacon, command])
        db_session.commit()
        
        retrieved = db_session.query(Command).filter_by(command="whoami").first()
        assert retrieved is not None
        assert retrieved.beacon_id == "beacon-123"
        assert retrieved.args == {"verbose": True}
        assert retrieved.status == "pending"


class TestAuditLogModel:
    """Test the AuditLog model"""
    
    def test_audit_log_creation(self, db_session):
        """Test creating an audit log entry"""
        user = User(
            id="user-123",
            username="testuser",
            password_hash="hash"
        )
        
        audit_log = AuditLog(
            id="audit-123",
            event_type="user_login",
            user_id="user-123",
            description="User logged in successfully",
            source_ip="192.168.1.100",
            log_metadata={"browser": "Chrome"}
        )
        
        db_session.add_all([user, audit_log])
        db_session.commit()
        
        retrieved = db_session.query(AuditLog).filter_by(event_type="user_login").first()
        assert retrieved is not None
        assert retrieved.user_id == "user-123"
        assert retrieved.source_ip == "192.168.1.100"
        assert retrieved.log_metadata == {"browser": "Chrome"}
