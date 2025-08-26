"""
Sessions Table View - Tabular view of active Beacons
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
    QLabel, QComboBox, QFrame, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QAction
from typing import Dict, List, Any
from datetime import datetime

from ..core import ClientCore


class SessionsTableView(QWidget):
    """
    Sessions Table visualization mode showing:
    - Tabular view of active Beacons
    - Columns for IP, hostname, egress listener, last check-in time, OS, and privilege level
    - Sortable and filterable
    - Right-click context menu for common actions
    """
    
    beacon_selected = pyqtSignal(str)  # beacon_id
    beacon_action_requested = pyqtSignal(str, str)  # beacon_id, action
    
    def __init__(self, client_core: ClientCore):
        super().__init__()
        self.client_core = client_core
        self.beacons_data = []
        
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
        
    def init_ui(self):
        """Initialize the sessions table UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Control panel
        control_panel = QFrame()
        control_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        control_layout = QHBoxLayout(control_panel)
        
        # Filter controls
        control_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter sessions...")
        self.filter_input.textChanged.connect(self.apply_filter)
        control_layout.addWidget(self.filter_input)
        
        # Status filter
        control_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Idle", "Disconnected"])
        self.status_filter.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.status_filter)
        
        # OS filter
        control_layout.addWidget(QLabel("OS:"))
        self.os_filter = QComboBox()
        self.os_filter.addItems(["All", "Windows", "Linux", "macOS"])
        self.os_filter.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.os_filter)
        
        control_layout.addStretch()
        
        # Action buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        control_layout.addWidget(refresh_btn)
        
        kill_all_btn = QPushButton("Kill All")
        kill_all_btn.clicked.connect(self.kill_all_beacons)
        kill_all_btn.setStyleSheet("QPushButton { background-color: #d13438; }")
        control_layout.addWidget(kill_all_btn)
        
        layout.addWidget(control_panel)
        
        # Sessions table
        self.sessions_table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.sessions_table, 1)
        
        # Status panel
        status_panel = QFrame()
        status_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_panel)
        
        self.status_label = QLabel("0 sessions")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.last_update_label = QLabel("Last updated: Never")
        status_layout.addWidget(self.last_update_label)
        
        layout.addWidget(status_panel)
        
    def setup_table(self):
        """Setup the sessions table"""
        # Define columns as specified in architecture
        columns = [
            "Beacon ID", "IP Address", "Hostname", "Egress Listener", 
            "Last Check-in", "OS", "Privilege Level", "Status", "Actions"
        ]
        
        self.sessions_table.setColumnCount(len(columns))
        self.sessions_table.setHorizontalHeaderLabels(columns)
        
        # Configure table
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sessions_table.setAlternatingRowColors(True)
        self.sessions_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.sessions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Beacon ID
        header.resizeSection(0, 100)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # IP Address
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Hostname
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Listener
        header.resizeSection(3, 120)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Last Check-in
        header.resizeSection(4, 140)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # OS
        header.resizeSection(5, 80)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Privilege
        header.resizeSection(6, 100)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Status
        header.resizeSection(7, 80)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)  # Actions
        header.resizeSection(8, 100)
        
        # Connect signals
        self.sessions_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.sessions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sessions_table.customContextMenuRequested.connect(self.show_context_menu)
        
    def refresh(self):
        """Refresh the table with current beacon data"""
        if not self.client_core.active_connection:
            return
            
        # Get beacon data from client core
        self.beacons_data = self.client_core.get_beacons()
        self.update_table()
        
        # Update status
        self.last_update_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
    def update_table(self):
        """Update the table with beacon data"""
        # Apply filters
        filtered_data = self.apply_filters(self.beacons_data)
        
        # Update table
        self.sessions_table.setRowCount(len(filtered_data))
        
        for row, beacon in enumerate(filtered_data):
            # Beacon ID
            beacon_id = beacon.get('beacon_id', '')[:8]  # Show first 8 chars
            self.sessions_table.setItem(row, 0, QTableWidgetItem(beacon_id))
            
            # IP Address
            ip_address = beacon.get('ip_address', '0.0.0.0')
            self.sessions_table.setItem(row, 1, QTableWidgetItem(ip_address))
            
            # Hostname
            hostname = beacon.get('hostname', 'Unknown')
            self.sessions_table.setItem(row, 2, QTableWidgetItem(hostname))
            
            # Egress Listener
            listener = beacon.get('listener_name', 'Unknown')
            self.sessions_table.setItem(row, 3, QTableWidgetItem(listener))
            
            # Last Check-in
            last_checkin = beacon.get('last_checkin', 'Never')
            if isinstance(last_checkin, datetime):
                last_checkin = last_checkin.strftime('%Y-%m-%d %H:%M:%S')
            self.sessions_table.setItem(row, 4, QTableWidgetItem(str(last_checkin)))
            
            # OS
            os_type = beacon.get('os_type', 'Unknown')
            os_item = QTableWidgetItem(os_type)
            # Set OS icon/color
            if 'windows' in os_type.lower():
                os_item.setBackground(QColor("#0078d4"))
            elif 'linux' in os_type.lower():
                os_item.setBackground(QColor("#ff6b35"))
            elif 'macos' in os_type.lower():
                os_item.setBackground(QColor("#888888"))
            self.sessions_table.setItem(row, 5, os_item)
            
            # Privilege Level
            privilege = beacon.get('privilege_level', 'user')
            privilege_item = QTableWidgetItem(privilege.title())
            if privilege == 'admin':
                privilege_item.setBackground(QColor("#ffb900"))
                privilege_item.setForeground(QColor("#000000"))
            self.sessions_table.setItem(row, 6, privilege_item)
            
            # Status
            status = beacon.get('status', 'unknown')
            status_item = QTableWidgetItem(status.title())
            # Set status color
            status_colors = {
                'active': QColor("#107c10"),
                'idle': QColor("#ffb900"),
                'disconnected': QColor("#d13438"),
                'unknown': QColor("#888888")
            }
            if status in status_colors:
                status_item.setBackground(status_colors[status])
                if status != 'idle':
                    status_item.setForeground(QColor("#ffffff"))
                else:
                    status_item.setForeground(QColor("#000000"))
            self.sessions_table.setItem(row, 7, status_item)
            
            # Actions (placeholder)
            actions_item = QTableWidgetItem("...")
            self.sessions_table.setItem(row, 8, actions_item)
            
        # Update status label
        total_count = len(self.beacons_data)
        filtered_count = len(filtered_data)
        active_count = len([b for b in filtered_data if b.get('status') == 'active'])
        
        if total_count != filtered_count:
            self.status_label.setText(f"{filtered_count} of {total_count} sessions ({active_count} active)")
        else:
            self.status_label.setText(f"{total_count} sessions ({active_count} active)")
            
    def apply_filters(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filters to the data"""
        filtered_data = data.copy()
        
        # Text filter
        filter_text = self.filter_input.text().lower()
        if filter_text:
            filtered_data = [
                beacon for beacon in filtered_data
                if (filter_text in beacon.get('hostname', '').lower() or
                    filter_text in beacon.get('ip_address', '').lower() or
                    filter_text in beacon.get('beacon_id', '').lower())
            ]
            
        # Status filter
        status_filter = self.status_filter.currentText()
        if status_filter != "All":
            filtered_data = [
                beacon for beacon in filtered_data
                if beacon.get('status', '').lower() == status_filter.lower()
            ]
            
        # OS filter
        os_filter = self.os_filter.currentText()
        if os_filter != "All":
            filtered_data = [
                beacon for beacon in filtered_data
                if os_filter.lower() in beacon.get('os_type', '').lower()
            ]
            
        return filtered_data
        
    def apply_filter(self):
        """Apply filters and update table"""
        self.update_table()
        
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.sessions_table.currentRow()
        if current_row >= 0:
            beacon_id_item = self.sessions_table.item(current_row, 0)
            if beacon_id_item:
                beacon_id = beacon_id_item.text()
                self.beacon_selected.emit(beacon_id)
                
    def show_context_menu(self, position):
        """Show context menu for beacon actions"""
        item = self.sessions_table.itemAt(position)
        if not item:
            return
            
        row = item.row()
        beacon_id_item = self.sessions_table.item(row, 0)
        if not beacon_id_item:
            return
            
        beacon_id = beacon_id_item.text()
        
        menu = QMenu(self)
        
        # Common actions as specified in architecture
        interact_action = QAction("Interact", self)
        interact_action.triggered.connect(lambda: self.beacon_action_requested.emit(beacon_id, "interact"))
        menu.addAction(interact_action)
        
        menu.addSeparator()
        
        file_browser_action = QAction("File Browser", self)
        file_browser_action.triggered.connect(lambda: self.beacon_action_requested.emit(beacon_id, "file_browser"))
        menu.addAction(file_browser_action)
        
        process_list_action = QAction("Process List", self)
        process_list_action.triggered.connect(lambda: self.beacon_action_requested.emit(beacon_id, "process_list"))
        menu.addAction(process_list_action)
        
        screenshot_action = QAction("Screenshot", self)
        screenshot_action.triggered.connect(lambda: self.beacon_action_requested.emit(beacon_id, "screenshot"))
        menu.addAction(screenshot_action)
        
        menu.addSeparator()
        
        pivot_action = QAction("Pivot", self)
        pivot_action.triggered.connect(lambda: self.beacon_action_requested.emit(beacon_id, "pivot"))
        menu.addAction(pivot_action)
        
        menu.addSeparator()
        
        kill_action = QAction("Kill Beacon", self)
        kill_action.triggered.connect(lambda: self.beacon_action_requested.emit(beacon_id, "kill"))
        menu.addAction(kill_action)
        
        menu.exec(self.sessions_table.mapToGlobal(position))
        
    def kill_all_beacons(self):
        """Kill all active beacons"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Kill All Beacons",
            "Are you sure you want to kill all active beacons?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Implementation would kill all beacons
            for beacon in self.beacons_data:
                if beacon.get('status') == 'active':
                    beacon_id = beacon.get('beacon_id', '')
                    self.beacon_action_requested.emit(beacon_id, "kill")
