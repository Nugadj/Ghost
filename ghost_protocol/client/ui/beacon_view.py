"""
Ghost Protocol Beacon View
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class BeaconView(QWidget):
    """Widget for displaying and managing beacons"""
    
    def __init__(self, client_core):
        super().__init__()
        self.client_core = client_core
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Active Beacons")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Beacon table
        self.beacon_table = QTableWidget()
        self.beacon_table.setColumnCount(6)
        self.beacon_table.setHorizontalHeaderLabels([
            "ID", "Computer", "User", "Process", "Last Seen", "Status"
        ])
        
        # Configure table
        header = self.beacon_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.beacon_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.beacon_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.beacon_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.interact_button = QPushButton("Interact")
        self.interact_button.setEnabled(False)
        self.interact_button.clicked.connect(self.interact_with_beacon)
        
        self.kill_button = QPushButton("Kill")
        self.kill_button.setEnabled(False)
        self.kill_button.clicked.connect(self.kill_beacon)
        
        button_layout.addWidget(self.interact_button)
        button_layout.addWidget(self.kill_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.beacon_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def refresh(self):
        """Refresh beacon data"""
        # Clear existing data
        self.beacon_table.setRowCount(0)
        
        # Get beacon data from client core
        if hasattr(self.client_core, 'get_beacons'):
            beacons = self.client_core.get_beacons()
            
            for i, beacon in enumerate(beacons):
                self.beacon_table.insertRow(i)
                self.beacon_table.setItem(i, 0, QTableWidgetItem(str(beacon.get('id', ''))))
                self.beacon_table.setItem(i, 1, QTableWidgetItem(beacon.get('computer', '')))
                self.beacon_table.setItem(i, 2, QTableWidgetItem(beacon.get('user', '')))
                self.beacon_table.setItem(i, 3, QTableWidgetItem(beacon.get('process', '')))
                self.beacon_table.setItem(i, 4, QTableWidgetItem(beacon.get('last_seen', '')))
                self.beacon_table.setItem(i, 5, QTableWidgetItem(beacon.get('status', '')))
        
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.beacon_table.selectedItems()) > 0
        self.interact_button.setEnabled(has_selection)
        self.kill_button.setEnabled(has_selection)
        
    def interact_with_beacon(self):
        """Interact with selected beacon"""
        # Implementation would go here
        pass
        
    def kill_beacon(self):
        """Kill selected beacon"""
        # Implementation would go here
        pass
