"""
Ghost Protocol Connection Dialog - Enhanced with server profiles and certificate management
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QSpinBox, QComboBox,
    QCheckBox, QTextEdit, QTabWidget, QWidget, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import json
import os
from typing import Dict, List, Any
from datetime import datetime
import hashlib


class ServerProfile:
    """Represents a server connection profile"""
    
    def __init__(self, name: str, host: str, port: int, username: str = "", 
                 password: str = "", certificate_fingerprint: str = "", 
                 auto_connect: bool = False):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.certificate_fingerprint = certificate_fingerprint
        self.auto_connect = auto_connect
        self.last_connected = None
        self.connection_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,  # In production, this should be encrypted
            "certificate_fingerprint": self.certificate_fingerprint,
            "auto_connect": self.auto_connect,
            "last_connected": self.last_connected.isoformat() if self.last_connected else None,
            "connection_count": self.connection_count
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServerProfile':
        """Create profile from dictionary"""
        profile = cls(
            data["name"], data["host"], data["port"],
            data.get("username", ""), data.get("password", ""),
            data.get("certificate_fingerprint", ""),
            data.get("auto_connect", False)
        )
        
        if data.get("last_connected"):
            profile.last_connected = datetime.fromisoformat(data["last_connected"])
        profile.connection_count = data.get("connection_count", 0)
        
        return profile


class ConnectionTestThread(QThread):
    """Thread for testing server connections"""
    
    connection_result = pyqtSignal(bool, str, str)  # success, message, certificate_fingerprint
    
    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        
    def run(self):
        """Test connection to server"""
        try:
            import socket
            import ssl
            
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            # Test basic connectivity
            result = sock.connect_ex((self.host, self.port))
            if result != 0:
                self.connection_result.emit(False, f"Cannot connect to {self.host}:{self.port}", "")
                return
                
            # Test SSL/TLS if applicable
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    fingerprint = hashlib.sha256(cert).hexdigest()
                    
                    self.connection_result.emit(True, "Connection successful (SSL)", fingerprint)
                    
            except ssl.SSLError:
                # Not SSL, but connection works
                self.connection_result.emit(True, "Connection successful (non-SSL)", "")
                
        except Exception as e:
            self.connection_result.emit(False, f"Connection failed: {str(e)}", "")
        finally:
            try:
                sock.close()
            except:
                pass


class ConnectionDialog(QDialog):
    """Enhanced dialog for connecting to Ghost Protocol server with profiles and certificate management"""
    
    connection_requested = pyqtSignal(str, int, str, str, str)  # host, port, username, password, profile_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profiles: List[ServerProfile] = []
        self.current_profile: ServerProfile = None
        self.profiles_file = os.path.expanduser("~/.ghost_protocol_profiles.json")
        
        self.init_ui()
        self.load_profiles()
        
    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle("Connect to Ghost Protocol Server")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header
        self.create_header(layout)
        
        # Tabbed interface
        self.tab_widget = QTabWidget()
        
        # Connection tab
        self.create_connection_tab()
        self.tab_widget.addTab(self.connection_widget, "Connection")
        
        # Profiles tab
        self.create_profiles_tab()
        self.tab_widget.addTab(self.profiles_widget, "Profiles")
        
        # Certificate tab
        self.create_certificate_tab()
        self.tab_widget.addTab(self.certificate_widget, "Certificate")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.create_status_bar(layout)
        
        # Button layout
        self.create_buttons(layout)
        
        # Apply theme
        self.apply_theme()
        
    def create_header(self, parent_layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Logo/Icon placeholder
        logo_label = QLabel("🛡️")
        logo_label.setFont(QFont("Arial", 24))
        header_layout.addWidget(logo_label)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        title_label = QLabel("Ghost Protocol Server Connection")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        desc_label = QLabel("Connect to a Ghost Protocol team server for adversary simulation operations")
        desc_label.setStyleSheet("color: #888888;")
        title_layout.addWidget(desc_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)
        
    def create_connection_tab(self):
        """Create connection configuration tab"""
        self.connection_widget = QWidget()
        layout = QVBoxLayout(self.connection_widget)
        
        # Server details group
        server_group = QGroupBox("Server Details")
        server_layout = QFormLayout(server_group)
        
        # Profile selector
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("New Connection")
        self.profile_combo.currentTextChanged.connect(self.on_profile_selected)
        server_layout.addRow("Profile:", self.profile_combo)
        
        # Host field
        self.host_edit = QLineEdit("127.0.0.1")
        self.host_edit.textChanged.connect(self.on_connection_details_changed)
        server_layout.addRow("Host:", self.host_edit)
        
        # Port field
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(8443)
        self.port_spin.valueChanged.connect(self.on_connection_details_changed)
        server_layout.addRow("Port:", self.port_spin)
        
        # Test connection button
        test_layout = QHBoxLayout()
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_button)
        
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        test_layout.addWidget(self.test_progress)
        
        test_layout.addStretch()
        server_layout.addRow("", test_layout)
        
        layout.addWidget(server_group)
        
        # Authentication group
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout(auth_group)
        
        # Username field
        self.username_edit = QLineEdit("admin")
        auth_layout.addRow("Username:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addRow("Password:", self.password_edit)
        
        # Remember credentials
        self.remember_checkbox = QCheckBox("Remember credentials")
        auth_layout.addRow("", self.remember_checkbox)
        
        layout.addWidget(auth_group)
        
        # Connection options group
        options_group = QGroupBox("Connection Options")
        options_layout = QFormLayout(options_group)
        
        # Auto-connect
        self.auto_connect_checkbox = QCheckBox("Auto-connect on startup")
        options_layout.addRow("", self.auto_connect_checkbox)
        
        # Verify certificate
        self.verify_cert_checkbox = QCheckBox("Verify server certificate")
        self.verify_cert_checkbox.setChecked(True)
        options_layout.addRow("", self.verify_cert_checkbox)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        
    def create_profiles_tab(self):
        """Create server profiles management tab"""
        self.profiles_widget = QWidget()
        layout = QHBoxLayout(self.profiles_widget)
        
        # Profiles list
        profiles_layout = QVBoxLayout()
        profiles_layout.addWidget(QLabel("Saved Profiles:"))
        
        self.profiles_list = QListWidget()
        self.profiles_list.itemSelectionChanged.connect(self.on_profile_list_selection)
        profiles_layout.addWidget(self.profiles_list)
        
        # Profile management buttons
        profile_buttons = QHBoxLayout()
        
        self.new_profile_button = QPushButton("New")
        self.new_profile_button.clicked.connect(self.new_profile)
        profile_buttons.addWidget(self.new_profile_button)
        
        self.edit_profile_button = QPushButton("Edit")
        self.edit_profile_button.clicked.connect(self.edit_profile)
        self.edit_profile_button.setEnabled(False)
        profile_buttons.addWidget(self.edit_profile_button)
        
        self.delete_profile_button = QPushButton("Delete")
        self.delete_profile_button.clicked.connect(self.delete_profile)
        self.delete_profile_button.setEnabled(False)
        profile_buttons.addWidget(self.delete_profile_button)
        
        profiles_layout.addLayout(profile_buttons)
        
        layout.addLayout(profiles_layout)
        
        # Profile details
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Profile Details:"))
        
        self.profile_details = QTextEdit()
        self.profile_details.setReadOnly(True)
        self.profile_details.setMaximumHeight(200)
        details_layout.addWidget(self.profile_details)
        
        # Import/Export buttons
        import_export_layout = QHBoxLayout()
        
        import_button = QPushButton("Import Profiles")
        import_button.clicked.connect(self.import_profiles)
        import_export_layout.addWidget(import_button)
        
        export_button = QPushButton("Export Profiles")
        export_button.clicked.connect(self.export_profiles)
        import_export_layout.addWidget(export_button)
        
        details_layout.addLayout(import_export_layout)
        details_layout.addStretch()
        
        layout.addLayout(details_layout)
        
    def create_certificate_tab(self):
        """Create certificate management tab"""
        self.certificate_widget = QWidget()
        layout = QVBoxLayout(self.certificate_widget)
        
        # Certificate info group
        cert_group = QGroupBox("Server Certificate Information")
        cert_layout = QVBoxLayout(cert_group)
        
        self.cert_info_text = QTextEdit()
        self.cert_info_text.setReadOnly(True)
        self.cert_info_text.setMaximumHeight(150)
        self.cert_info_text.setPlainText("No certificate information available.\nConnect to a server to view certificate details.")
        cert_layout.addWidget(self.cert_info_text)
        
        layout.addWidget(cert_group)
        
        # Certificate fingerprint group
        fingerprint_group = QGroupBox("Certificate Fingerprint Verification")
        fingerprint_layout = QFormLayout(fingerprint_group)
        
        self.fingerprint_edit = QLineEdit()
        self.fingerprint_edit.setReadOnly(True)
        self.fingerprint_edit.setPlaceholderText("SHA-256 fingerprint will appear here after connection test")
        fingerprint_layout.addRow("SHA-256 Fingerprint:", self.fingerprint_edit)
        
        # Fingerprint verification buttons
        fingerprint_buttons = QHBoxLayout()
        
        self.trust_button = QPushButton("Trust Certificate")
        self.trust_button.clicked.connect(self.trust_certificate)
        self.trust_button.setEnabled(False)
        fingerprint_buttons.addWidget(self.trust_button)
        
        self.clear_trust_button = QPushButton("Clear Trust")
        self.clear_trust_button.clicked.connect(self.clear_certificate_trust)
        fingerprint_buttons.addWidget(self.clear_trust_button)
        
        fingerprint_buttons.addStretch()
        fingerprint_layout.addRow("", fingerprint_buttons)
        
        layout.addWidget(fingerprint_group)
        
        # Certificate validation group
        validation_group = QGroupBox("Certificate Validation")
        validation_layout = QVBoxLayout(validation_group)
        
        validation_info = QLabel(
            "Ghost Protocol uses self-signed certificates by default. "
            "Verify the certificate fingerprint matches what your administrator provided "
            "to ensure secure communication."
        )
        validation_info.setWordWrap(True)
        validation_info.setStyleSheet("color: #888888;")
        validation_layout.addWidget(validation_info)
        
        layout.addWidget(validation_group)
        
        layout.addStretch()
        
    def create_status_bar(self, parent_layout):
        """Create status bar"""
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Ready to connect")
        self.status_label.setStyleSheet("color: #888888;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.connection_status_label = QLabel("Not connected")
        status_layout.addWidget(self.connection_status_label)
        
        parent_layout.addWidget(self.status_frame)
        
    def create_buttons(self, parent_layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        # Save profile button
        self.save_profile_button = QPushButton("Save Profile")
        self.save_profile_button.clicked.connect(self.save_current_profile)
        button_layout.addWidget(self.save_profile_button)
        
        button_layout.addStretch()
        
        # Main action buttons
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.connect_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.cancel_button)
        
        parent_layout.addLayout(button_layout)
        
    def apply_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom: 2px solid #0078d4;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
                color: #ffffff;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #363636;
            }
            QPushButton:default {
                border-color: #0078d4;
                background-color: #0078d4;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #404040;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
        
    def load_profiles(self):
        """Load server profiles from file"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    
                self.profiles = [ServerProfile.from_dict(profile_data) for profile_data in data]
                self.update_profiles_ui()
                
        except Exception as e:
            QMessageBox.warning(self, "Load Profiles", f"Failed to load profiles: {str(e)}")
            
    def save_profiles(self):
        """Save server profiles to file"""
        try:
            data = [profile.to_dict() for profile in self.profiles]
            
            os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            QMessageBox.warning(self, "Save Profiles", f"Failed to save profiles: {str(e)}")
            
    def update_profiles_ui(self):
        """Update profiles UI elements"""
        # Update profile combo
        current_text = self.profile_combo.currentText()
        self.profile_combo.clear()
        self.profile_combo.addItem("New Connection")
        
        for profile in self.profiles:
            self.profile_combo.addItem(profile.name)
            
        # Restore selection
        index = self.profile_combo.findText(current_text)
        if index >= 0:
            self.profile_combo.setCurrentIndex(index)
            
        # Update profiles list
        self.profiles_list.clear()
        for profile in self.profiles:
            item = QListWidgetItem(f"{profile.name} ({profile.host}:{profile.port})")
            item.setData(Qt.ItemDataRole.UserRole, profile)
            self.profiles_list.addItem(item)
            
    def on_profile_selected(self, profile_name: str):
        """Handle profile selection"""
        if profile_name == "New Connection":
            self.current_profile = None
            return
            
        # Find and load profile
        for profile in self.profiles:
            if profile.name == profile_name:
                self.current_profile = profile
                self.load_profile_to_ui(profile)
                break
                
    def load_profile_to_ui(self, profile: ServerProfile):
        """Load profile data to UI fields"""
        self.host_edit.setText(profile.host)
        self.port_spin.setValue(profile.port)
        self.username_edit.setText(profile.username)
        self.password_edit.setText(profile.password)
        self.auto_connect_checkbox.setChecked(profile.auto_connect)
        self.fingerprint_edit.setText(profile.certificate_fingerprint)
        
    def on_connection_details_changed(self):
        """Handle connection details change"""
        # Clear current profile if details changed
        if self.current_profile:
            if (self.host_edit.text() != self.current_profile.host or 
                self.port_spin.value() != self.current_profile.port):
                self.profile_combo.setCurrentText("New Connection")
                self.current_profile = None
                
    def test_connection(self):
        """Test connection to server"""
        host = self.host_edit.text().strip()
        port = self.port_spin.value()
        
        if not host:
            QMessageBox.warning(self, "Test Connection", "Please enter a host address")
            return
            
        self.test_button.setEnabled(False)
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Testing connection...")
        
        # Start connection test thread
        self.test_thread = ConnectionTestThread(host, port)
        self.test_thread.connection_result.connect(self.on_connection_test_result)
        self.test_thread.start()
        
    def on_connection_test_result(self, success: bool, message: str, fingerprint: str):
        """Handle connection test result"""
        self.test_button.setEnabled(True)
        self.test_progress.setVisible(False)
        
        if success:
            self.status_label.setText(message)
            self.connection_status_label.setText("Connection OK")
            self.connection_status_label.setStyleSheet("color: #44ff44;")
            
            if fingerprint:
                self.fingerprint_edit.setText(fingerprint)
                self.trust_button.setEnabled(True)
                self.update_certificate_info(fingerprint)
        else:
            self.status_label.setText(message)
            self.connection_status_label.setText("Connection Failed")
            self.connection_status_label.setStyleSheet("color: #ff4444;")
            
        # Show result message
        if success:
            QMessageBox.information(self, "Connection Test", message)
        else:
            QMessageBox.warning(self, "Connection Test", message)
            
    def update_certificate_info(self, fingerprint: str):
        """Update certificate information display"""
        cert_info = f"""Certificate Information:
SHA-256 Fingerprint: {fingerprint}

This is a self-signed certificate used by the Ghost Protocol server.
Verify this fingerprint matches the one provided by your administrator
to ensure secure communication.

Connection established: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.cert_info_text.setPlainText(cert_info)
        
    def trust_certificate(self):
        """Trust the current certificate"""
        fingerprint = self.fingerprint_edit.text()
        if not fingerprint:
            return
            
        reply = QMessageBox.question(
            self, "Trust Certificate",
            f"Do you want to trust this certificate?\n\nSHA-256: {fingerprint}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Store fingerprint for current connection
            if self.current_profile:
                self.current_profile.certificate_fingerprint = fingerprint
            self.status_label.setText("Certificate trusted")
            
    def clear_certificate_trust(self):
        """Clear certificate trust"""
        self.fingerprint_edit.clear()
        if self.current_profile:
            self.current_profile.certificate_fingerprint = ""
        self.status_label.setText("Certificate trust cleared")
        
    def save_current_profile(self):
        """Save current connection as profile"""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Save Profile", "Profile name:")
        if not ok or not name.strip():
            return
            
        # Check if profile name exists
        for profile in self.profiles:
            if profile.name == name.strip():
                reply = QMessageBox.question(
                    self, "Profile Exists",
                    f"Profile '{name}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                self.profiles.remove(profile)
                break
                
        # Create new profile
        profile = ServerProfile(
            name.strip(),
            self.host_edit.text().strip(),
            self.port_spin.value(),
            self.username_edit.text().strip(),
            self.password_edit.text() if self.remember_checkbox.isChecked() else "",
            self.fingerprint_edit.text(),
            self.auto_connect_checkbox.isChecked()
        )
        
        self.profiles.append(profile)
        self.save_profiles()
        self.update_profiles_ui()
        
        # Select the new profile
        self.profile_combo.setCurrentText(name.strip())
        
        QMessageBox.information(self, "Save Profile", f"Profile '{name}' saved successfully")
        
    def connect_to_server(self):
        """Connect to the selected server"""
        host = self.host_edit.text().strip()
        port = self.port_spin.value()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not host or not username:
            QMessageBox.warning(self, "Connection Error", "Please enter host and username")
            return
            
        # Update profile connection stats
        if self.current_profile:
            self.current_profile.last_connected = datetime.now()
            self.current_profile.connection_count += 1
            self.save_profiles()
            
        profile_name = self.current_profile.name if self.current_profile else "New Connection"
        
        # Emit connection signal
        self.connection_requested.emit(host, port, username, password, profile_name)
        
        # Accept dialog
        self.accept()
        
    def get_connection_info(self):
        """Get connection information (legacy method for compatibility)"""
        return (
            self.host_edit.text().strip(),
            self.port_spin.value(),
            self.username_edit.text().strip(),
            self.password_edit.text()
        )
        
    # Profile management methods
    def on_profile_list_selection(self):
        """Handle profile list selection"""
        current_item = self.profiles_list.currentItem()
        if current_item:
            profile = current_item.data(Qt.ItemDataRole.UserRole)
            self.show_profile_details(profile)
            self.edit_profile_button.setEnabled(True)
            self.delete_profile_button.setEnabled(True)
        else:
            self.profile_details.clear()
            self.edit_profile_button.setEnabled(False)
            self.delete_profile_button.setEnabled(False)
            
    def show_profile_details(self, profile: ServerProfile):
        """Show profile details"""
        details = f"""Profile: {profile.name}
Server: {profile.host}:{profile.port}
Username: {profile.username}
Auto-connect: {'Yes' if profile.auto_connect else 'No'}
Certificate trusted: {'Yes' if profile.certificate_fingerprint else 'No'}
Last connected: {profile.last_connected.strftime('%Y-%m-%d %H:%M:%S') if profile.last_connected else 'Never'}
Connection count: {profile.connection_count}
"""
        self.profile_details.setPlainText(details)
        
    def new_profile(self):
        """Create new profile"""
        self.tab_widget.setCurrentIndex(0)  # Switch to connection tab
        self.profile_combo.setCurrentText("New Connection")
        self.host_edit.clear()
        self.port_spin.setValue(8443)
        self.username_edit.setText("admin")
        self.password_edit.clear()
        self.auto_connect_checkbox.setChecked(False)
        self.fingerprint_edit.clear()
        
    def edit_profile(self):
        """Edit selected profile"""
        current_item = self.profiles_list.currentItem()
        if not current_item:
            return
            
        profile = current_item.data(Qt.ItemDataRole.UserRole)
        self.tab_widget.setCurrentIndex(0)  # Switch to connection tab
        self.profile_combo.setCurrentText(profile.name)
        
    def delete_profile(self):
        """Delete selected profile"""
        current_item = self.profiles_list.currentItem()
        if not current_item:
            return
            
        profile = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete profile '{profile.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profiles.remove(profile)
            self.save_profiles()
            self.update_profiles_ui()
            
    def import_profiles(self):
        """Import profiles from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Profiles", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                imported_profiles = [ServerProfile.from_dict(profile_data) for profile_data in data]
                self.profiles.extend(imported_profiles)
                self.save_profiles()
                self.update_profiles_ui()
                
                QMessageBox.information(
                    self, "Import Profiles", 
                    f"Successfully imported {len(imported_profiles)} profiles"
                )
                
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Failed to import profiles: {str(e)}")
                
    def export_profiles(self):
        """Export profiles to file"""
        if not self.profiles:
            QMessageBox.information(self, "Export Profiles", "No profiles to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Profiles", "ghost_protocol_profiles.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                data = [profile.to_dict() for profile in self.profiles]
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                QMessageBox.information(
                    self, "Export Profiles", 
                    f"Successfully exported {len(self.profiles)} profiles to {file_path}"
                )
                
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export profiles: {str(e)}")
