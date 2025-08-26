"""
Pivot Graph View - Node-based visualization showing Beacon chains
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
import networkx as nx
from typing import Dict, List, Any

from ..core import ClientCore


class PivotGraphView(QWidget):
    """
    Pivot Graph visualization mode showing:
    - Node-based visualization showing Beacon chains
    - OS-specific icons for different system types
    - Privilege indicators for compromised systems
    - Link type visualization (named pipe, TCP, DNS, HTTP/S)
    - Status indicators for connection health
    """
    
    beacon_selected = pyqtSignal(str)  # beacon_id
    
    def __init__(self, client_core: ClientCore):
        super().__init__()
        self.client_core = client_core
        self.graph = nx.DiGraph()
        self.node_positions = {}
        self.selected_beacon = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the pivot graph UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Control panel
        control_panel = QFrame()
        control_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        control_layout = QHBoxLayout(control_panel)
        
        # Layout controls
        control_layout.addWidget(QLabel("Layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Spring", "Hierarchical", "Circular", "Tree"])
        self.layout_combo.currentTextChanged.connect(self.update_layout)
        control_layout.addWidget(self.layout_combo)
        
        control_layout.addSeparator()
        
        # Filter controls
        control_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter beacons...")
        self.filter_input.textChanged.connect(self.apply_filter)
        control_layout.addWidget(self.filter_input)
        
        # Zoom controls
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_btn)
        
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(reset_view_btn)
        
        control_layout.addStretch()
        
        layout.addWidget(control_panel)
        
        # Graph canvas
        self.graph_canvas = GraphCanvas(self)
        layout.addWidget(self.graph_canvas, 1)
        
        # Status panel
        status_panel = QFrame()
        status_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_panel)
        
        self.status_label = QLabel("No beacons connected")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.legend_label = QLabel("Legend: 🟢 Active | 🟡 Idle | 🔴 Disconnected | 👑 Admin | 👤 User")
        status_layout.addWidget(self.legend_label)
        
        layout.addWidget(status_panel)
        
    def refresh(self):
        """Refresh the graph with current beacon data"""
        if not self.client_core.active_connection:
            return
            
        # Get beacon data from client core
        beacons = self.client_core.get_beacons()
        self.update_graph(beacons)
        
    def update_graph(self, beacons: List[Dict[str, Any]]):
        """Update the graph with beacon data"""
        self.graph.clear()
        
        # Add nodes for each beacon
        for beacon in beacons:
            beacon_id = beacon.get('beacon_id', '')
            hostname = beacon.get('hostname', 'Unknown')
            ip_address = beacon.get('ip_address', '0.0.0.0')
            os_type = beacon.get('os_type', 'unknown')
            privilege_level = beacon.get('privilege_level', 'user')
            status = beacon.get('status', 'unknown')
            
            self.graph.add_node(beacon_id, 
                              hostname=hostname,
                              ip_address=ip_address,
                              os_type=os_type,
                              privilege_level=privilege_level,
                              status=status)
            
        # Add edges for pivot relationships
        for beacon in beacons:
            beacon_id = beacon.get('beacon_id', '')
            parent_beacon = beacon.get('parent_beacon_id')
            
            if parent_beacon and parent_beacon in self.graph:
                pivot_type = beacon.get('pivot_type', 'tcp')
                self.graph.add_edge(parent_beacon, beacon_id, 
                                  pivot_type=pivot_type)
                
        # Update layout
        self.update_layout()
        
        # Update status
        beacon_count = len(beacons)
        active_count = len([b for b in beacons if b.get('status') == 'active'])
        self.status_label.setText(f"{beacon_count} beacons ({active_count} active)")
        
        # Refresh canvas
        self.graph_canvas.update()
        
    def update_layout(self):
        """Update node positions based on selected layout"""
        if not self.graph.nodes():
            return
            
        layout_type = self.layout_combo.currentText().lower()
        
        if layout_type == "spring":
            self.node_positions = nx.spring_layout(self.graph, k=2, iterations=50)
        elif layout_type == "hierarchical":
            self.node_positions = nx.nx_agraph.graphviz_layout(self.graph, prog='dot')
        elif layout_type == "circular":
            self.node_positions = nx.circular_layout(self.graph)
        elif layout_type == "tree":
            self.node_positions = nx.nx_agraph.graphviz_layout(self.graph, prog='twopi')
        else:
            self.node_positions = nx.spring_layout(self.graph)
            
        self.graph_canvas.update()
        
    def apply_filter(self, filter_text: str):
        """Apply filter to visible nodes"""
        # Implementation for filtering nodes based on text
        self.graph_canvas.filter_text = filter_text.lower()
        self.graph_canvas.update()
        
    def zoom_in(self):
        """Zoom in on the graph"""
        self.graph_canvas.zoom_factor *= 1.2
        self.graph_canvas.update()
        
    def zoom_out(self):
        """Zoom out on the graph"""
        self.graph_canvas.zoom_factor /= 1.2
        self.graph_canvas.update()
        
    def reset_view(self):
        """Reset view to default"""
        self.graph_canvas.zoom_factor = 1.0
        self.graph_canvas.pan_offset = [0, 0]
        self.graph_canvas.update()


class GraphCanvas(QWidget):
    """Canvas widget for drawing the network graph"""
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
        self.zoom_factor = 1.0
        self.pan_offset = [0, 0]
        self.filter_text = ""
        self.setMinimumSize(400, 300)
        
    def paintEvent(self, event):
        """Paint the network graph"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        
        if not self.parent_view.graph.nodes():
            # Draw "no data" message
            painter.setPen(QPen(QColor("#888888")))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                           "No beacon data available")
            return
            
        # Apply transformations
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pan_offset[0], self.pan_offset[1])
        
        # Draw edges first
        self.draw_edges(painter)
        
        # Draw nodes
        self.draw_nodes(painter)
        
    def draw_edges(self, painter):
        """Draw edges between nodes"""
        for edge in self.parent_view.graph.edges(data=True):
            source, target, data = edge
            
            if (source not in self.parent_view.node_positions or 
                target not in self.parent_view.node_positions):
                continue
                
            # Get positions
            source_pos = self.parent_view.node_positions[source]
            target_pos = self.parent_view.node_positions[target]
            
            # Scale positions to widget size
            width, height = self.width(), self.height()
            x1 = int(source_pos[0] * width * 0.8 + width * 0.1)
            y1 = int(source_pos[1] * height * 0.8 + height * 0.1)
            x2 = int(target_pos[0] * width * 0.8 + width * 0.1)
            y2 = int(target_pos[1] * height * 0.8 + height * 0.1)
            
            # Set edge color based on pivot type
            pivot_type = data.get('pivot_type', 'tcp')
            color_map = {
                'tcp': QColor("#0078d4"),
                'named_pipe': QColor("#00bcf2"),
                'dns': QColor("#8764b8"),
                'http': QColor("#107c10"),
                'https': QColor("#00b7c3")
            }
            
            edge_color = color_map.get(pivot_type, QColor("#888888"))
            painter.setPen(QPen(edge_color, 2))
            painter.drawLine(x1, y1, x2, y2)
            
            # Draw arrow head
            self.draw_arrow_head(painter, x1, y1, x2, y2, edge_color)
            
    def draw_arrow_head(self, painter, x1, y1, x2, y2, color):
        """Draw arrow head on edge"""
        import math
        
        # Calculate arrow head
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 10
        arrow_angle = math.pi / 6
        
        # Arrow head points
        x3 = x2 - arrow_length * math.cos(angle - arrow_angle)
        y3 = y2 - arrow_length * math.sin(angle - arrow_angle)
        x4 = x2 - arrow_length * math.cos(angle + arrow_angle)
        y4 = y2 - arrow_length * math.sin(angle + arrow_angle)
        
        painter.setBrush(QBrush(color))
        painter.drawPolygon([
            (int(x2), int(y2)),
            (int(x3), int(y3)),
            (int(x4), int(y4))
        ])
        
    def draw_nodes(self, painter):
        """Draw nodes representing beacons"""
        for node_id, data in self.parent_view.graph.nodes(data=True):
            if node_id not in self.parent_view.node_positions:
                continue
                
            # Apply filter
            if self.filter_text:
                hostname = data.get('hostname', '').lower()
                ip_address = data.get('ip_address', '').lower()
                if (self.filter_text not in hostname and 
                    self.filter_text not in ip_address):
                    continue
                    
            # Get position
            pos = self.parent_view.node_positions[node_id]
            width, height = self.width(), self.height()
            x = int(pos[0] * width * 0.8 + width * 0.1)
            y = int(pos[1] * height * 0.8 + height * 0.1)
            
            # Node appearance based on status and privilege
            status = data.get('status', 'unknown')
            privilege = data.get('privilege_level', 'user')
            os_type = data.get('os_type', 'unknown')
            
            # Status colors
            status_colors = {
                'active': QColor("#107c10"),
                'idle': QColor("#ffb900"),
                'disconnected': QColor("#d13438"),
                'unknown': QColor("#888888")
            }
            
            node_color = status_colors.get(status, QColor("#888888"))
            
            # Draw node circle
            node_radius = 25 if privilege == 'admin' else 20
            painter.setBrush(QBrush(node_color))
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.drawEllipse(x - node_radius, y - node_radius, 
                              node_radius * 2, node_radius * 2)
            
            # Draw privilege indicator
            if privilege == 'admin':
                painter.setPen(QPen(QColor("#ffb900"), 2))
                painter.drawText(x - 8, y + 5, "👑")
            else:
                painter.setPen(QPen(QColor("#ffffff"), 2))
                painter.drawText(x - 8, y + 5, "👤")
                
            # Draw hostname label
            hostname = data.get('hostname', 'Unknown')
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawText(x - 40, y + 35, hostname[:12])
