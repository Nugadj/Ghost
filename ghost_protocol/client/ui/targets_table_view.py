"""
Targets Table View - Organization of systems by target group
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
    QLabel, QComboBox, QFrame, QMenu, QTreeWidget, QTreeWidgetItem,
    QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QAction
from typing import Dict, List, Any
from datetime import datetime

from ..core import ClientCore


class TargetsTableView(QWidget):
    """
    Targets Table visualization mode showing:
    - Organization of systems by target group
    - Columns for IP, NetBIOS name, notes, OS, and active Beacon status
    - Custom tagging support
    - Integration with reconnaissance findings
    """
    
    target_selected = pyqtSignal(str)  # target_id
    target_action_requested = pyqtSignal(str, str)  # target_id, action
    
    def __init__(self, client_core: ClientCore):
        super().__init__()
        self.client_core = client_core
        self.targets_data = []
        self.target_groups = {}
        
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(15000)  # Refresh every 15 seconds
        
    def init_ui(self):
        """Initialize the targets table UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Control panel
        control_panel = QFrame()
        control_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        control_layout = QHBoxLayout(control_panel)
        
        # Filter controls
        control_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter targets...")
        self.filter_input.textChanged.connect(self.apply_filter)
        control_layout.addWidget(self.filter_input)
        
        # Group filter
        control_layout.addWidget(QLabel("Group:"))
        self.group_filter = QComboBox()
        self.group_filter.addItem("All Groups")
        self.group_filter.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.group_filter)
        
        # Status filter
        control_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Compromised", "Discovered", "Unknown"])
        self.status_filter.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.status_filter)
        
        control_layout.addStretch()
        
        # Action buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        control_layout.addWidget(refresh_btn)
        
        add_target_btn = QPushButton("Add Target")
        add_target_btn.clicked.connect(self.add_target)
        control_layout.addWidget(add_target_btn)
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.import_targets)
        control_layout.addWidget(import_btn)
        
        layout.addWidget(control_panel)
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(content_splitter, 1)
        
        # Left side - Target groups tree
        self.create_groups_panel(content_splitter)
        
        # Right side - Targets table with tabs
        self.create_targets_panel(content_splitter)
        
        # Set splitter sizes
        content_splitter.setSizes([200, 600])
        
        # Status panel
        status_panel = QFrame()
        status_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_panel)
        
        self.status_label = QLabel("0 targets")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.last_update_label = QLabel("Last updated: Never")
        status_layout.addWidget(self.last_update_label)
        
        layout.addWidget(status_panel)
        
    def create_groups_panel(self, parent_splitter):
        """Create the target groups tree panel"""
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        groups_layout.setContentsMargins(4, 4, 4, 4)
        
        groups_layout.addWidget(QLabel("Target Groups"))
        
        self.groups_tree = QTreeWidget()
        self.groups_tree.setHeaderLabel("Groups")
        self.groups_tree.itemSelectionChanged.connect(self.on_group_selection_changed)
        groups_layout.addWidget(self.groups_tree)
        
        # Group management buttons
        group_buttons_layout = QHBoxLayout()
        
        add_group_btn = QPushButton("Add Group")
        add_group_btn.clicked.connect(self.add_group)
        group_buttons_layout.addWidget(add_group_btn)
        
        edit_group_btn = QPushButton("Edit")
        edit_group_btn.clicked.connect(self.edit_group)
        group_buttons_layout.addWidget(edit_group_btn)
        
        groups_layout.addLayout(group_buttons_layout)
        
        parent_splitter.addWidget(groups_widget)
        
    def create_targets_panel(self, parent_splitter):
        """Create the targets table panel with tabs"""
        targets_widget = QWidget()
        targets_layout = QVBoxLayout(targets_widget)
        targets_layout.setContentsMargins(4, 4, 4, 4)
        
        # Tabbed interface for different views
        self.targets_tabs = QTabWidget()
        
        # Main targets table
        self.create_targets_table()
        self.targets_tabs.addTab(self.targets_table, "Targets")
        
        # Services view
        self.create_services_table()
        self.targets_tabs.addTab(self.services_table, "Services")
        
        # Vulnerabilities view
        self.create_vulnerabilities_table()
        self.targets_tabs.addTab(self.vulnerabilities_table, "Vulnerabilities")
        
        targets_layout.addWidget(self.targets_tabs)
        
        parent_splitter.addWidget(targets_widget)
        
    def create_targets_table(self):
        """Create the main targets table"""
        self.targets_table = QTableWidget()
        
        # Define columns as specified in architecture
        columns = [
            "IP Address", "NetBIOS Name", "Hostname", "OS", "Status", 
            "Active Beacon", "Tags", "Notes", "Last Seen"
        ]
        
        self.targets_table.setColumnCount(len(columns))
        self.targets_table.setHorizontalHeaderLabels(columns)
        
        # Configure table
        self.targets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.targets_table.setAlternatingRowColors(True)
        self.targets_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.targets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # IP Address
        header.resizeSection(0, 120)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # NetBIOS Name
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Hostname
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # OS
        header.resizeSection(3, 100)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Status
        header.resizeSection(4, 100)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Active Beacon
        header.resizeSection(5, 100)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Tags
        header.resizeSection(6, 120)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Notes
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)  # Last Seen
        header.resizeSection(8, 140)
        
        # Connect signals
        self.targets_table.itemSelectionChanged.connect(self.on_target_selection_changed)
        self.targets_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.targets_table.customContextMenuRequested.connect(self.show_target_context_menu)
        
    def create_services_table(self):
        """Create the services table"""
        self.services_table = QTableWidget()
        
        columns = ["IP Address", "Port", "Protocol", "Service", "Version", "Status", "Banner"]
        self.services_table.setColumnCount(len(columns))
        self.services_table.setHorizontalHeaderLabels(columns)
        
        self.services_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setSortingEnabled(True)
        
    def create_vulnerabilities_table(self):
        """Create the vulnerabilities table"""
        self.vulnerabilities_table = QTableWidget()
        
        columns = ["IP Address", "CVE", "Severity", "Service", "Description", "Status"]
        self.vulnerabilities_table.setColumnCount(len(columns))
        self.vulnerabilities_table.setHorizontalHeaderLabels(columns)
        
        self.vulnerabilities_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vulnerabilities_table.setAlternatingRowColors(True)
        self.vulnerabilities_table.setSortingEnabled(True)
        
    def refresh(self):
        """Refresh the table with current target data"""
        if not self.client_core.active_connection:
            return
            
        # Get target data from client core
        self.targets_data = self.client_core.get_targets()
        self.update_groups()
        self.update_tables()
        
        # Update status
        self.last_update_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
    def update_groups(self):
        """Update the target groups tree"""
        self.groups_tree.clear()
        
        # Group targets by their group attribute
        groups = {}
        for target in self.targets_data:
            group_name = target.get('group', 'Default')
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(target)
            
        # Add groups to tree
        for group_name, targets in groups.items():
            group_item = QTreeWidgetItem([f"{group_name} ({len(targets)})"])
            self.groups_tree.addTopLevelItem(group_item)
            
            # Add targets as children
            for target in targets:
                target_name = target.get('hostname') or target.get('ip_address', 'Unknown')
                target_item = QTreeWidgetItem([target_name])
                target_item.setData(0, Qt.ItemDataRole.UserRole, target.get('target_id'))
                group_item.addChild(target_item)
                
        # Update group filter combo
        current_selection = self.group_filter.currentText()
        self.group_filter.clear()
        self.group_filter.addItem("All Groups")
        self.group_filter.addItems(sorted(groups.keys()))
        
        # Restore selection if possible
        index = self.group_filter.findText(current_selection)
        if index >= 0:
            self.group_filter.setCurrentIndex(index)
            
    def update_tables(self):
        """Update all tables with current data"""
        self.update_targets_table()
        self.update_services_table()
        self.update_vulnerabilities_table()
        
    def update_targets_table(self):
        """Update the targets table"""
        # Apply filters
        filtered_data = self.apply_filters(self.targets_data)
        
        # Update table
        self.targets_table.setRowCount(len(filtered_data))
        
        for row, target in enumerate(filtered_data):
            # IP Address
            ip_address = target.get('ip_address', '0.0.0.0')
            self.targets_table.setItem(row, 0, QTableWidgetItem(ip_address))
            
            # NetBIOS Name
            netbios_name = target.get('netbios_name', '')
            self.targets_table.setItem(row, 1, QTableWidgetItem(netbios_name))
            
            # Hostname
            hostname = target.get('hostname', '')
            self.targets_table.setItem(row, 2, QTableWidgetItem(hostname))
            
            # OS
            os_type = target.get('os_type', 'Unknown')
            os_item = QTableWidgetItem(os_type)
            if 'windows' in os_type.lower():
                os_item.setBackground(QColor("#0078d4"))
            elif 'linux' in os_type.lower():
                os_item.setBackground(QColor("#ff6b35"))
            elif 'macos' in os_type.lower():
                os_item.setBackground(QColor("#888888"))
            self.targets_table.setItem(row, 3, os_item)
            
            # Status
            status = target.get('status', 'unknown')
            status_item = QTableWidgetItem(status.title())
            status_colors = {
                'compromised': QColor("#d13438"),
                'discovered': QColor("#ffb900"),
                'unknown': QColor("#888888")
            }
            if status in status_colors:
                status_item.setBackground(status_colors[status])
                if status != 'discovered':
                    status_item.setForeground(QColor("#ffffff"))
                else:
                    status_item.setForeground(QColor("#000000"))
            self.targets_table.setItem(row, 4, status_item)
            
            # Active Beacon
            has_beacon = target.get('has_active_beacon', False)
            beacon_item = QTableWidgetItem("Yes" if has_beacon else "No")
            if has_beacon:
                beacon_item.setBackground(QColor("#107c10"))
                beacon_item.setForeground(QColor("#ffffff"))
            self.targets_table.setItem(row, 5, beacon_item)
            
            # Tags
            tags = target.get('tags', [])
            tags_text = ", ".join(tags) if isinstance(tags, list) else str(tags)
            self.targets_table.setItem(row, 6, QTableWidgetItem(tags_text))
            
            # Notes
            notes = target.get('notes', '')
            self.targets_table.setItem(row, 7, QTableWidgetItem(notes))
            
            # Last Seen
            last_seen = target.get('last_seen', 'Never')
            if isinstance(last_seen, datetime):
                last_seen = last_seen.strftime('%Y-%m-%d %H:%M:%S')
            self.targets_table.setItem(row, 8, QTableWidgetItem(str(last_seen)))
            
        # Update status label
        total_count = len(self.targets_data)
        filtered_count = len(filtered_data)
        compromised_count = len([t for t in filtered_data if t.get('status') == 'compromised'])
        
        if total_count != filtered_count:
            self.status_label.setText(f"{filtered_count} of {total_count} targets ({compromised_count} compromised)")
        else:
            self.status_label.setText(f"{total_count} targets ({compromised_count} compromised)")
            
    def update_services_table(self):
        """Update the services table"""
        # Get services data from targets
        services_data = []
        for target in self.targets_data:
            target_services = target.get('services', [])
            for service in target_services:
                service['ip_address'] = target.get('ip_address')
                services_data.append(service)
                
        self.services_table.setRowCount(len(services_data))
        
        for row, service in enumerate(services_data):
            self.services_table.setItem(row, 0, QTableWidgetItem(service.get('ip_address', '')))
            self.services_table.setItem(row, 1, QTableWidgetItem(str(service.get('port', ''))))
            self.services_table.setItem(row, 2, QTableWidgetItem(service.get('protocol', '')))
            self.services_table.setItem(row, 3, QTableWidgetItem(service.get('service_name', '')))
            self.services_table.setItem(row, 4, QTableWidgetItem(service.get('version', '')))
            self.services_table.setItem(row, 5, QTableWidgetItem(service.get('status', '')))
            self.services_table.setItem(row, 6, QTableWidgetItem(service.get('banner', '')))
            
    def update_vulnerabilities_table(self):
        """Update the vulnerabilities table"""
        # Get vulnerabilities data from targets
        vulns_data = []
        for target in self.targets_data:
            target_vulns = target.get('vulnerabilities', [])
            for vuln in target_vulns:
                vuln['ip_address'] = target.get('ip_address')
                vulns_data.append(vuln)
                
        self.vulnerabilities_table.setRowCount(len(vulns_data))
        
        for row, vuln in enumerate(vulns_data):
            self.vulnerabilities_table.setItem(row, 0, QTableWidgetItem(vuln.get('ip_address', '')))
            self.vulnerabilities_table.setItem(row, 1, QTableWidgetItem(vuln.get('cve', '')))
            
            # Severity with color coding
            severity = vuln.get('severity', 'Unknown')
            severity_item = QTableWidgetItem(severity)
            severity_colors = {
                'Critical': QColor("#d13438"),
                'High': QColor("#ff6b35"),
                'Medium': QColor("#ffb900"),
                'Low': QColor("#107c10")
            }
            if severity in severity_colors:
                severity_item.setBackground(severity_colors[severity])
                if severity in ['Critical', 'High']:
                    severity_item.setForeground(QColor("#ffffff"))
                else:
                    severity_item.setForeground(QColor("#000000"))
            self.vulnerabilities_table.setItem(row, 2, severity_item)
            
            self.vulnerabilities_table.setItem(row, 3, QTableWidgetItem(vuln.get('service', '')))
            self.vulnerabilities_table.setItem(row, 4, QTableWidgetItem(vuln.get('description', '')))
            self.vulnerabilities_table.setItem(row, 5, QTableWidgetItem(vuln.get('status', '')))


    def apply_filters(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filters to the data"""
        filtered_data = data.copy()
        
        # Text filter
        filter_text = self.filter_input.text().lower()
        if filter_text:
            filtered_data = [
                target for target in filtered_data
                if (filter_text in target.get('hostname', '').lower() or
                    filter_text in target.get('ip_address', '').lower() or
                    filter_text in target.get('netbios_name', '').lower() or
                    filter_text in str(target.get('tags', '')).lower())
            ]
            
        # Group filter
        group_filter = self.group_filter.currentText()
        if group_filter != "All Groups":
            filtered_data = [
                target for target in filtered_data
                if target.get('group', 'Default') == group_filter
            ]
            
        # Status filter
        status_filter = self.status_filter.currentText()
        if status_filter != "All":
            filtered_data = [
                target for target in filtered_data
                if target.get('status', '').lower() == status_filter.lower()
            ]
            
        return filtered_data
        
    def apply_filter(self):
        """Apply filters and update tables"""
        self.update_tables()
        
    def on_group_selection_changed(self):
        """Handle group selection change"""
        current_item = self.groups_tree.currentItem()
        if current_item and current_item.parent():  # Target item
            target_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if target_id:
                self.target_selected.emit(target_id)
                
    def on_target_selection_changed(self):
        """Handle target selection change"""
        current_row = self.targets_table.currentRow()
        if current_row >= 0:
            # Find target_id from the row data
            ip_address = self.targets_table.item(current_row, 0).text()
            for target in self.targets_data:
                if target.get('ip_address') == ip_address:
                    target_id = target.get('target_id', '')
                    self.target_selected.emit(target_id)
                    break
                    
    def show_target_context_menu(self, position):
        """Show context menu for target actions"""
        item = self.targets_table.itemAt(position)
        if not item:
            return
            
        row = item.row()
        ip_address = self.targets_table.item(row, 0).text()
        
        # Find target_id
        target_id = None
        for target in self.targets_data:
            if target.get('ip_address') == ip_address:
                target_id = target.get('target_id', '')
                break
                
        if not target_id:
            return
            
        menu = QMenu(self)
        
        # Target actions
        scan_action = QAction("Scan Target", self)
        scan_action.triggered.connect(lambda: self.target_action_requested.emit(target_id, "scan"))
        menu.addAction(scan_action)
        
        exploit_action = QAction("Exploit", self)
        exploit_action.triggered.connect(lambda: self.target_action_requested.emit(target_id, "exploit"))
        menu.addAction(exploit_action)
        
        menu.addSeparator()
        
        edit_action = QAction("Edit Target", self)
        edit_action.triggered.connect(lambda: self.target_action_requested.emit(target_id, "edit"))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Target", self)
        delete_action.triggered.connect(lambda: self.target_action_requested.emit(target_id, "delete"))
        menu.addAction(delete_action)
        
        menu.exec(self.targets_table.mapToGlobal(position))
        
    def add_target(self):
        """Add new target"""
        # Implementation would show add target dialog
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Add Target", "Add target dialog not implemented yet")
        
    def add_group(self):
        """Add new target group"""
        from PyQt6.QtWidgets import QInputDialog
        
        group_name, ok = QInputDialog.getText(self, "Add Group", "Group name:")
        if ok and group_name:
            # Implementation would add the group
            pass
            
    def edit_group(self):
        """Edit selected group"""
        current_item = self.groups_tree.currentItem()
        if current_item and not current_item.parent():  # Group item
            # Implementation would show edit group dialog
            pass
            
    def import_targets(self):
        """Import targets from file"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Targets", "", 
            "CSV Files (*.csv);;XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(self, "Import", f"Import from {file_path} not implemented yet")
