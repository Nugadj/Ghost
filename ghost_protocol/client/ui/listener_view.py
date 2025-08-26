"""
Ghost Protocol Listener View
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ListenerView(QWidget):
    """Widget for displaying and managing listeners"""
    
    def __init__(self, client_core):
        super().__init__()
        self.client_core = client_core
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Active Listeners")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Listener table
        self.listener_table = QTableWidget()
        self.listener_table.setColumnCount(5)
        self.listener_table.setHorizontalHeaderLabels([
            "Name", "Type", "Host", "Port", "Status"
        ])
        
        # Configure table
        header = self.listener_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.listener_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.listener_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.listener_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Listener")
        self.start_button.clicked.connect(self.start_listener)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_listener)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.listener_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def refresh(self):
        """Refresh listener data"""
        # Clear existing data
        self.listener_table.setRowCount(0)
        
        # Get listener data from client core
        if hasattr(self.client_core, 'get_listeners'):
            listeners = self.client_core.get_listeners()
            
            for i, listener in enumerate(listeners):
                self.listener_table.insertRow(i)
                self.listener_table.setItem(i, 0, QTableWidgetItem(listener.get('name', '')))
                self.listener_table.setItem(i, 1, QTableWidgetItem(listener.get('type', '')))
                self.listener_table.setItem(i, 2, QTableWidgetItem(listener.get('host', '')))
                self.listener_table.setItem(i, 3, QTableWidgetItem(str(listener.get('port', ''))))
                self.listener_table.setItem(i, 4, QTableWidgetItem(listener.get('status', '')))
        
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.listener_table.selectedItems()) > 0
        self.stop_button.setEnabled(has_selection)
        
    def start_listener(self):
        """Start a new listener"""
        # Implementation would go here
        pass
        
    def stop_listener(self):
        """Stop selected listener"""
        # Implementation would go here
        pass
