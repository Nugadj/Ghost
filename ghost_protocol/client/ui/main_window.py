"""
Ghost Protocol Main Window
"""

import asyncio
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTabWidget, QStatusBar, QMenuBar,
    QMessageBox, QInputDialog, QLabel, QToolBar,
    QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction

from ..core import ClientCore
from ...core import Config
from .connection_dialog import ConnectionDialog
from .beacon_view import BeaconView
from .listener_view import ListenerView
from .console_view import ConsoleView
from .pivot_graph_view import PivotGraphView
from .sessions_table_view import SessionsTableView
from .targets_table_view import TargetsTableView


class MainWindow(QMainWindow):
    """Main application window following Ghost Protocol architecture specifications"""
    
    # Signals
    status_updated = pyqtSignal(str)
    
    def __init__(self, client_core: ClientCore, config: Config):
        super().__init__()
        
        self.client_core = client_core
        self.config = config
        
        self.current_visualization_mode = "pivot_graph"
        
        # Setup UI
        self.init_ui()
        
        # Setup timers
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        # Connect signals
        self.status_updated.connect(self.update_status_bar)
        
    def init_ui(self):
        """Initialize the user interface according to architecture specifications"""
        self.setWindowTitle("Ghost Protocol - Adversary Simulation Platform")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_toolbar()
        
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(main_splitter)
        
        self.create_visualization_pane(main_splitter)
        
        self.create_console_pane(main_splitter)
        
        main_splitter.setSizes([600, 400])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
        # Apply theme
        self.apply_theme()
        
    def create_toolbar(self):
        """Create toolbar with primary actions and visualization switching"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Connection management
        connect_action = QAction("Connect", self)
        connect_action.setToolTip("Connect to Team Server")
        connect_action.triggered.connect(self.show_connection_dialog)
        toolbar.addAction(connect_action)
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.setToolTip("Disconnect from Team Server")
        disconnect_action.triggered.connect(self.disconnect_from_server)
        toolbar.addAction(disconnect_action)
        
        toolbar.addSeparator()
        
        # Listener configuration
        new_listener_action = QAction("New Listener", self)
        new_listener_action.setToolTip("Create new listener")
        new_listener_action.triggered.connect(self.show_new_listener_dialog)
        toolbar.addAction(new_listener_action)
        
        toolbar.addSeparator()
        
        toolbar.addWidget(QLabel("View:"))
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Pivot Graph", "Sessions Table", "Targets Table"])
        self.view_selector.currentTextChanged.connect(self.switch_visualization_mode)
        toolbar.addWidget(self.view_selector)
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setToolTip("Refresh data from server")
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
    def create_visualization_pane(self, parent_splitter):
        """Create top pane with configurable visualization modes"""
        from PyQt6.QtWidgets import QStackedWidget
        
        self.visualization_stack = QStackedWidget()
        parent_splitter.addWidget(self.visualization_stack)
        
        # 1. Pivot Graph - Node-based visualization showing Beacon chains
        self.pivot_graph_view = PivotGraphView(self.client_core)
        self.visualization_stack.addWidget(self.pivot_graph_view)
        
        # 2. Sessions Table - Tabular view of active Beacons
        self.sessions_table_view = SessionsTableView(self.client_core)
        self.visualization_stack.addWidget(self.sessions_table_view)
        
        # 3. Targets Table - Organization of systems by target group
        self.targets_table_view = TargetsTableView(self.client_core)
        self.visualization_stack.addWidget(self.targets_table_view)
        
        # Set default view
        self.visualization_stack.setCurrentWidget(self.pivot_graph_view)
        
    def create_console_pane(self, parent_splitter):
        """Create bottom pane with tabbed interface for consoles and tools"""
        self.bottom_tabs = QTabWidget()
        self.bottom_tabs.setTabsClosable(True)
        self.bottom_tabs.setMovable(True)
        self.bottom_tabs.tabCloseRequested.connect(self.close_tab)
        
        self.console_view = ConsoleView(self.client_core)
        self.bottom_tabs.addTab(self.console_view, "Main Console")
        
        self.beacon_view = BeaconView(self.client_core)
        self.listener_view = ListenerView(self.client_core)
        
        self.bottom_tabs.addTab(self.beacon_view, "Beacon Management")
        self.bottom_tabs.addTab(self.listener_view, "Listener Management")
        
        parent_splitter.addWidget(self.bottom_tabs)
        
    def switch_visualization_mode(self, mode_text):
        """Switch between visualization modes"""
        mode_map = {
            "Pivot Graph": (self.pivot_graph_view, "pivot_graph"),
            "Sessions Table": (self.sessions_table_view, "sessions_table"),
            "Targets Table": (self.targets_table_view, "targets_table")
        }
        
        if mode_text in mode_map:
            widget, mode_key = mode_map[mode_text]
            self.visualization_stack.setCurrentWidget(widget)
            self.current_visualization_mode = mode_key
            self.status_updated.emit(f"Switched to {mode_text} view")
            
    def close_tab(self, index):
        """Close tab with confirmation for important tabs"""
        if index == 0:  # Don't close main console
            return
            
        tab_name = self.bottom_tabs.tabText(index)
        reply = QMessageBox.question(
            self, "Close Tab", 
            f"Close '{tab_name}' tab?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            widget = self.bottom_tabs.widget(index)
            self.bottom_tabs.removeTab(index)
            widget.deleteLater()
            
    def show_new_listener_dialog(self):
        """Show new listener creation dialog"""
        # Implementation would show listener configuration dialog
        QMessageBox.information(self, "New Listener", "Listener creation dialog not implemented yet")

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        connect_action = QAction("Connect to Server", self)
        connect_action.setShortcut("Ctrl+N")
        connect_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect_from_server)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connection status
        self.connection_label = QLabel("Not Connected")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # Initial status
        self.update_status_bar("Ready")
        
    def apply_theme(self):
        """Apply enhanced dark theme following design guidelines"""
        if self.config.client.ui_theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QToolBar {
                    background-color: #2d2d2d;
                    border: none;
                    spacing: 3px;
                    padding: 4px;
                }
                QToolBar QToolButton {
                    background-color: #404040;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 6px 12px;
                    margin: 1px;
                    color: #ffffff;
                }
                QToolBar QToolButton:hover {
                    background-color: #4a4a4a;
                    border-color: #666666;
                }
                QToolBar QToolButton:pressed {
                    background-color: #363636;
                }
                QComboBox {
                    background-color: #404040;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 4px 8px;
                    color: #ffffff;
                    min-width: 120px;
                }
                QComboBox:hover {
                    border-color: #666666;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #ffffff;
                    margin-right: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    selection-background-color: #404040;
                    color: #ffffff;
                }
                QSplitter::handle {
                    background-color: #555555;
                    height: 3px;
                }
                QSplitter::handle:hover {
                    background-color: #666666;
                }
                QStackedWidget {
                    background-color: #1e1e1e;
                    border: 1px solid #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #1e1e1e;
                    top: -1px;
                }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    border-bottom: 2px solid #0078d4;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #404040;
                }
                QTabBar::close-button {
                    image: none;
                    background-color: #666666;
                    border-radius: 2px;
                    width: 12px;
                    height: 12px;
                }
                QTabBar::close-button:hover {
                    background-color: #888888;
                }
                QMenuBar {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border-bottom: 1px solid #555555;
                    padding: 2px;
                }
                QMenuBar::item {
                    padding: 6px 12px;
                    border-radius: 3px;
                }
                QMenuBar::item:selected {
                    background-color: #404040;
                }
                QMenu {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 20px;
                    border-radius: 3px;
                }
                QMenu::item:selected {
                    background-color: #404040;
                }
                QStatusBar {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border-top: 1px solid #555555;
                    padding: 2px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)

    def show_connection_dialog(self):
        """Show connection dialog"""
        dialog = ConnectionDialog(self)
        if dialog.exec():
            host, port, username, password = dialog.get_connection_info()
            asyncio.create_task(self.connect_to_server(host, port, username, password))
            
    async def connect_to_server(self, host: str, port: int, username: str, password: str):
        """Connect to server"""
        self.status_updated.emit("Connecting...")
        
        success = await self.client_core.connect_to_server(host, port, username, password)
        
        if success:
            self.connection_label.setText(f"Connected to {host}:{port}")
            self.status_updated.emit("Connected")
            await self.refresh_data()
        else:
            self.connection_label.setText("Connection Failed")
            self.status_updated.emit("Connection failed")
            QMessageBox.critical(self, "Connection Error", "Failed to connect to server")
            
    def disconnect_from_server(self):
        """Disconnect from server"""
        # Implementation would go here
        self.connection_label.setText("Not Connected")
        self.status_updated.emit("Disconnected")
        
    async def refresh_data(self):
        """Refresh data from server"""
        if self.client_core.active_connection:
            self.status_updated.emit("Refreshing...")
            await self.client_core.refresh_data()
            
            self.pivot_graph_view.refresh()
            self.sessions_table_view.refresh()
            self.targets_table_view.refresh()
            self.beacon_view.refresh()
            self.listener_view.refresh()
            
            self.status_updated.emit("Ready")
            
    def update_status_bar(self, message: str):
        """Update status bar message"""
        self.status_bar.showMessage(message, 5000)
        
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Ghost Protocol", 
                         "Ghost Protocol v1.0\n\n"
                         "Python-based adversary simulation platform\n"
                         "for security training and testing.")
        
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(self, "Exit", "Are you sure you want to exit?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Cleanup
            self.refresh_timer.stop()
            event.accept()
        else:
            event.ignore()
