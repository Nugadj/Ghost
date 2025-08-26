"""
Ghost Protocol Console View - Enhanced with history, autocompletion, and advanced features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QLabel, QCompleter, QFrame,
    QSplitter, QListWidget, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
from typing import List, Dict, Any
import re
from datetime import datetime


class ConsoleView(QWidget):
    """
    Enhanced console widget with:
    - Command history with search functionality (Ctrl+F)
    - Auto-completion for commands (Tab)
    - Syntax highlighting for commands
    - Multiple console tabs for different sessions
    - Command output formatting
    """
    
    # Signals
    command_executed = pyqtSignal(str)
    beacon_command_executed = pyqtSignal(str, str)  # beacon_id, command
    
    def __init__(self, client_core):
        super().__init__()
        self.client_core = client_core
        self.command_history = []
        self.history_index = -1
        self.available_commands = []
        self.current_beacon_id = None
        
        self.init_ui()
        self.setup_autocompletion()
        
        # Auto-refresh available commands
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_commands)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def init_ui(self):
        """Initialize the enhanced console UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Create splitter for console and history
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left side - Main console
        self.create_main_console(main_splitter)
        
        # Right side - Command history and help
        self.create_side_panel(main_splitter)
        
        # Set splitter sizes
        main_splitter.setSizes([600, 200])
        
        # Command input area
        self.create_input_area(layout)
        
        # Status bar
        self.create_status_bar(layout)
        
        # Initial welcome message
        self.append_output("Ghost Protocol Console v1.0", "system")
        self.append_output("Type 'help' for available commands", "system")
        self.append_output("Use Tab for command completion, Ctrl+F to search history", "system")
        self.append_output("", "system")
        
    def create_main_console(self, parent_splitter):
        """Create the main console area"""
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(4, 4, 4, 4)
        
        # Console header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        self.console_title = QLabel("Main Console")
        self.console_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(self.console_title)
        
        header_layout.addStretch()
        
        # Console controls
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_console)
        header_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("Save Log")
        save_btn.clicked.connect(self.save_console_log)
        header_layout.addWidget(save_btn)
        
        console_layout.addWidget(header_frame)
        
        # Console output with enhanced formatting
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 10))
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #404040;
            }
        """)
        console_layout.addWidget(self.console_output)
        
        parent_splitter.addWidget(console_widget)
        
    def create_side_panel(self, parent_splitter):
        """Create side panel with history and help"""
        side_widget = QWidget()
        side_layout = QVBoxLayout(side_widget)
        side_layout.setContentsMargins(4, 4, 4, 4)
        
        # Tabbed side panel
        self.side_tabs = QTabWidget()
        
        # Command history tab
        self.create_history_tab()
        self.side_tabs.addTab(self.history_widget, "History")
        
        # Help tab
        self.create_help_tab()
        self.side_tabs.addTab(self.help_widget, "Help")
        
        # Beacons tab
        self.create_beacons_tab()
        self.side_tabs.addTab(self.beacons_widget, "Beacons")
        
        side_layout.addWidget(self.side_tabs)
        
        parent_splitter.addWidget(side_widget)
        
    def create_history_tab(self):
        """Create command history tab"""
        self.history_widget = QWidget()
        history_layout = QVBoxLayout(self.history_widget)
        
        # History search
        history_search = QLineEdit()
        history_search.setPlaceholderText("Search history...")
        history_search.textChanged.connect(self.filter_history)
        history_layout.addWidget(history_search)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.use_history_command)
        history_layout.addWidget(self.history_list)
        
        # History controls
        history_controls = QHBoxLayout()
        
        clear_history_btn = QPushButton("Clear")
        clear_history_btn.clicked.connect(self.clear_history)
        history_controls.addWidget(clear_history_btn)
        
        export_history_btn = QPushButton("Export")
        export_history_btn.clicked.connect(self.export_history)
        history_controls.addWidget(export_history_btn)
        
        history_layout.addLayout(history_controls)
        
    def create_help_tab(self):
        """Create help tab"""
        self.help_widget = QWidget()
        help_layout = QVBoxLayout(self.help_widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFont(QFont("Consolas", 9))
        help_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
            }
        """)
        
        help_content = """
GHOST PROTOCOL COMMANDS

Core Commands:
  help                 - Show this help
  clear                - Clear console
  exit                 - Exit console
  status               - Show connection status

Server Commands:
  connect <host> <port> - Connect to server
  disconnect           - Disconnect from server
  listeners            - List active listeners
  listener <name>      - Create new listener

Beacon Commands:
  beacons              - List active beacons
  interact <id>        - Interact with beacon
  kill <id>            - Kill specific beacon
  killall              - Kill all beacons

Session Commands:
  sessions             - List all sessions
  session <id>         - Switch to session
  background           - Background current session

File Operations:
  upload <local> <remote> - Upload file
  download <remote> <local> - Download file
  ls [path]            - List directory
  cd <path>            - Change directory
  pwd                  - Print working directory

System Commands:
  ps                   - List processes
  kill <pid>           - Kill process
  shell <command>      - Execute shell command
  screenshot           - Take screenshot

Keyboard Shortcuts:
  Tab                  - Auto-complete command
  Ctrl+F               - Search history
  Up/Down Arrow        - Navigate history
  Ctrl+C               - Cancel current command
  Ctrl+L               - Clear screen
        """
        
        help_text.setPlainText(help_content.strip())
        help_layout.addWidget(help_text)
        
    def create_beacons_tab(self):
        """Create beacons tab for quick beacon selection"""
        self.beacons_widget = QWidget()
        beacons_layout = QVBoxLayout(self.beacons_widget)
        
        beacons_layout.addWidget(QLabel("Active Beacons:"))
        
        self.beacons_list = QListWidget()
        self.beacons_list.itemDoubleClicked.connect(self.interact_with_beacon)
        beacons_layout.addWidget(self.beacons_list)
        
        # Beacon controls
        beacon_controls = QHBoxLayout()
        
        refresh_beacons_btn = QPushButton("Refresh")
        refresh_beacons_btn.clicked.connect(self.refresh_beacons_list)
        beacon_controls.addWidget(refresh_beacons_btn)
        
        beacons_layout.addLayout(beacon_controls)
        
    def create_input_area(self, parent_layout):
        """Create enhanced command input area"""
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        input_layout = QVBoxLayout(input_frame)
        
        # Context indicator
        self.context_label = QLabel("Main Console")
        self.context_label.setFont(QFont("Arial", 9))
        self.context_label.setStyleSheet("color: #888888;")
        input_layout.addWidget(self.context_label)
        
        # Command input line
        command_layout = QHBoxLayout()
        
        self.prompt_label = QLabel("ghost> ")
        self.prompt_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.prompt_label.setStyleSheet("color: #00ff00;")
        command_layout.addWidget(self.prompt_label)
        
        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Consolas", 10))
        self.command_input.returnPressed.connect(self.execute_command)
        self.command_input.keyPressEvent = self.handle_key_press
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        command_layout.addWidget(self.command_input)
        
        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(self.execute_command)
        execute_button.setShortcut("Ctrl+Return")
        command_layout.addWidget(execute_button)
        
        input_layout.addLayout(command_layout)
        parent_layout.addWidget(input_frame)
        
    def create_status_bar(self, parent_layout):
        """Create status bar"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.command_count_label = QLabel("Commands: 0")
        status_layout.addWidget(self.command_count_label)
        
        self.time_label = QLabel()
        self.update_time()
        status_layout.addWidget(self.time_label)
        
        # Update time every second
        time_timer = QTimer()
        time_timer.timeout.connect(self.update_time)
        time_timer.start(1000)
        
        parent_layout.addWidget(status_frame)
        
    def setup_autocompletion(self):
        """Setup command autocompletion"""
        self.refresh_commands()
        
        # Create completer
        self.completer = QCompleter(self.available_commands)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.command_input.setCompleter(self.completer)
        
    def refresh_commands(self):
        """Refresh available commands list"""
        base_commands = [
            "help", "clear", "exit", "status", "connect", "disconnect",
            "listeners", "listener", "beacons", "interact", "kill", "killall",
            "sessions", "session", "background", "upload", "download", "ls",
            "cd", "pwd", "ps", "shell", "screenshot", "sleep", "jitter"
        ]
        
        # Add beacon-specific commands if connected
        if self.client_core and hasattr(self.client_core, 'get_beacons'):
            beacons = self.client_core.get_beacons()
            for beacon in beacons:
                beacon_id = beacon.get('beacon_id', '')[:8]
                base_commands.extend([
                    f"interact {beacon_id}",
                    f"kill {beacon_id}"
                ])
                
        self.available_commands = sorted(list(set(base_commands)))
        
        # Update completer
        if hasattr(self, 'completer'):
            model = QStringListModel(self.available_commands)
            self.completer.setModel(model)

    def handle_key_press(self, event):
        """Handle enhanced key press events"""
        if event.key() == Qt.Key.Key_Up:
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                self.command_input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.setText(self.command_history[self.history_index])
            elif self.history_index == len(self.command_history) - 1:
                self.history_index = len(self.command_history)
                self.command_input.clear()
        elif event.key() == Qt.Key.Key_Tab:
            # Handle tab completion manually if needed
            current_text = self.command_input.text()
            if current_text and not self.completer.popup().isVisible():
                self.completer.setCompletionPrefix(current_text)
                if self.completer.completionCount() == 1:
                    self.command_input.setText(self.completer.currentCompletion())
                    return
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_F:
                self.show_search_dialog()
                return
            elif event.key() == Qt.Key.Key_L:
                self.clear_console()
                return
            elif event.key() == Qt.Key.Key_C:
                self.cancel_command()
                return
                
        # Call original key press handler
        QLineEdit.keyPressEvent(self.command_input, event)
        
    def execute_command(self):
        """Execute command with enhanced processing"""
        command = self.command_input.text().strip()
        if not command:
            return
            
        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
            self.update_history_list()
        self.history_index = len(self.command_history)
        
        # Display command with timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.current_beacon_id:
            prompt = f"beacon_{self.current_beacon_id[:8]}> "
        else:
            prompt = "ghost> "
            
        self.append_output(f"[{timestamp}] {prompt}{command}", "command")
        
        # Clear input
        self.command_input.clear()
        
        # Update command count
        self.command_count_label.setText(f"Commands: {len(self.command_history)}")
        
        # Process command
        self.process_command(command)
        
        # Emit appropriate signal
        if self.current_beacon_id:
            self.beacon_command_executed.emit(self.current_beacon_id, command)
        else:
            self.command_executed.emit(command)
            
    def process_command(self, command: str):
        """Process the executed command with enhanced functionality"""
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Core commands
        if cmd == "help":
            self.show_help()
        elif cmd == "clear":
            self.clear_console()
        elif cmd == "exit":
            self.exit_console()
        elif cmd == "status":
            self.show_status()
        elif cmd == "beacons":
            self.list_beacons()
        elif cmd == "listeners":
            self.list_listeners()
        elif cmd == "interact":
            if args:
                self.interact_with_beacon_id(args[0])
            else:
                self.append_output("Usage: interact <beacon_id>", "error")
        elif cmd == "background":
            self.background_session()
        elif cmd == "kill":
            if args:
                self.kill_beacon(args[0])
            else:
                self.append_output("Usage: kill <beacon_id>", "error")
        elif cmd == "killall":
            self.kill_all_beacons()
        elif cmd == "sessions":
            self.list_sessions()
        else:
            # If we're in a beacon session, send command to beacon
            if self.current_beacon_id:
                self.append_output(f"Sending command to beacon {self.current_beacon_id[:8]}...", "info")
                # Implementation would send command to specific beacon
            else:
                self.append_output(f"Unknown command: {cmd}", "error")
                self.append_output("Type 'help' for available commands", "info")

    def append_output(self, text: str, message_type: str = "normal"):
        """Append formatted text to console output"""
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Set format based on message type
        format = QTextCharFormat()
        
        if message_type == "command":
            format.setForeground(QColor("#00ff00"))
        elif message_type == "error":
            format.setForeground(QColor("#ff4444"))
        elif message_type == "warning":
            format.setForeground(QColor("#ffaa00"))
        elif message_type == "info":
            format.setForeground(QColor("#4488ff"))
        elif message_type == "success":
            format.setForeground(QColor("#44ff44"))
        elif message_type == "system":
            format.setForeground(QColor("#888888"))
        else:
            format.setForeground(QColor("#ffffff"))
            
        cursor.setCharFormat(format)
        cursor.insertText(text + "\n")
        
        # Auto-scroll to bottom
        self.console_output.setTextCursor(cursor)
        
    def interact_with_beacon_id(self, beacon_id: str):
        """Switch to beacon interaction mode"""
        # Find full beacon ID
        if self.client_core and hasattr(self.client_core, 'get_beacons'):
            beacons = self.client_core.get_beacons()
            for beacon in beacons:
                full_id = beacon.get('beacon_id', '')
                if full_id.startswith(beacon_id):
                    self.current_beacon_id = full_id
                    hostname = beacon.get('hostname', 'Unknown')
                    self.console_title.setText(f"Beacon Console - {hostname}")
                    self.context_label.setText(f"Interacting with beacon {beacon_id} ({hostname})")
                    self.prompt_label.setText(f"beacon_{beacon_id}> ")
                    self.prompt_label.setStyleSheet("color: #ff8800;")
                    self.append_output(f"Interacting with beacon {beacon_id} ({hostname})", "success")
                    self.append_output("Type 'background' to return to main console", "info")
                    return
                    
        self.append_output(f"Beacon {beacon_id} not found", "error")
        
    def background_session(self):
        """Return to main console"""
        if self.current_beacon_id:
            self.current_beacon_id = None
            self.console_title.setText("Main Console")
            self.context_label.setText("Main Console")
            self.prompt_label.setText("ghost> ")
            self.prompt_label.setStyleSheet("color: #00ff00;")
            self.append_output("Returned to main console", "info")
        else:
            self.append_output("Not in a beacon session", "warning")

    def update_history_list(self):
        """Update the history list widget"""
        self.history_list.clear()
        for i, cmd in enumerate(reversed(self.command_history[-50:])):  # Show last 50 commands
            self.history_list.addItem(f"{len(self.command_history) - i}: {cmd}")
            
    def refresh_beacons_list(self):
        """Refresh the beacons list"""
        self.beacons_list.clear()
        if self.client_core and hasattr(self.client_core, 'get_beacons'):
            beacons = self.client_core.get_beacons()
            for beacon in beacons:
                beacon_id = beacon.get('beacon_id', '')[:8]
                hostname = beacon.get('hostname', 'Unknown')
                status = beacon.get('status', 'unknown')
                self.beacons_list.addItem(f"{beacon_id} - {hostname} ({status})")
                
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def show_help(self):
        """Show help information"""
        self.side_tabs.setCurrentIndex(1)  # Switch to help tab
        self.append_output("Help information displayed in side panel", "info")
        
    def clear_console(self):
        """Clear console output"""
        self.console_output.clear()
        self.append_output("Console cleared", "system")
        
    def save_console_log(self):
        """Save console log to file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Console Log", f"ghost_console_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.console_output.toPlainText())
                self.append_output(f"Console log saved to {file_path}", "success")
            except Exception as e:
                self.append_output(f"Failed to save log: {str(e)}", "error")

    def show_search_dialog(self):
        """Show search dialog for command history"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton
        
        class SearchDialog(QDialog):
            def __init__(self, parent):
                super().__init__(parent)
                self.setWindowTitle("Search Command History")
                self.setModal(True)
                
                layout = QVBoxLayout(self)
                
                self.search_input = QLineEdit()
                self.search_input.setPlaceholderText("Enter search term...")
                layout.addWidget(self.search_input)
                
                search_button = QPushButton("Search")
                search_button.clicked.connect(self.search)
                layout.addWidget(search_button)
                
            def search(self):
                search_term = self.search_input.text().strip()
                if search_term:
                    filtered_history = [cmd for cmd in self.parent().command_history if search_term.lower() in cmd.lower()]
                    self.parent().history_list.clear()
                    for cmd in filtered_history:
                        self.parent().history_list.addItem(cmd)
                self.accept()
        
        dialog = SearchDialog(self)
        dialog.exec()
        
    def use_history_command(self, item):
        """Use selected command from history"""
        self.command_input.setText(item.text().split(": ", 1)[1])
        self.command_input.setFocus()
        
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.update_history_list()
        self.append_output("Command history cleared", "system")
        
    def export_history(self):
        """Export command history to file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Command History", f"ghost_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for cmd in self.command_history:
                        f.write(cmd + "\n")
                self.append_output(f"Command history exported to {file_path}", "success")
            except Exception as e:
                self.append_output(f"Failed to export history: {str(e)}", "error")

    def filter_history(self, text):
        """Filter history based on search text"""
        if text:
            filtered_history = [cmd for cmd in self.command_history if text.lower() in cmd.lower()]
            self.history_list.clear()
            for cmd in filtered_history:
                self.history_list.addItem(cmd)
        else:
            self.update_history_list()

    def kill_beacon(self, beacon_id: str):
        """Kill a specific beacon"""
        if self.client_core and hasattr(self.client_core, 'kill_beacon'):
            if self.client_core.kill_beacon(beacon_id):
                self.append_output(f"Beacon {beacon_id} killed successfully", "success")
            else:
                self.append_output(f"Failed to kill beacon {beacon_id}", "error")
        else:
            self.append_output("Beacon data not available", "error")

    def kill_all_beacons(self):
        """Kill all beacons"""
        if self.client_core and hasattr(self.client_core, 'kill_all_beacons'):
            if self.client_core.kill_all_beacons():
                self.append_output("All beacons killed successfully", "success")
            else:
                self.append_output("Failed to kill all beacons", "error")
        else:
            self.append_output("Beacon data not available", "error")

    def list_sessions(self):
        """List all sessions"""
        if self.client_core and hasattr(self.client_core, 'get_sessions'):
            sessions = self.client_core.get_sessions()
            if sessions:
                self.append_output(f"Active sessions: {len(sessions)}")
                for session in sessions:
                    self.append_output(f"  {session.get('id', 'N/A')} - {session.get('name', 'N/A')}")
            else:
                self.append_output("No active sessions")
        else:
            self.append_output("Session data not available", "error")

    def exit_console(self):
        """Exit the console"""
        self.parent().close()
        self.append_output("Exiting console...", "system")

    def interact_with_beacon(self, item):
        """Interact with selected beacon"""
        beacon_id = item.text().split(" - ", 1)[0]
        self.interact_with_beacon_id(beacon_id)
