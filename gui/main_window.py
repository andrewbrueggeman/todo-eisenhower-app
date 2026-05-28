"""
Main Window for Eisenhower Matrix To-Do Application

This module contains the main window layout with:
- Daily view header with navigation
- 4-quadrant Eisenhower Matrix
- Daily notes section
- Timer and system monitor widgets
"""

from datetime import datetime, timedelta
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QTextEdit, QGridLayout,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt, QTimer, pyqtSignal
from PySide6.QtGui import QFont, QPalette

class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.current_date = datetime.now().date()
        
        self.setWindowTitle("Eisenhower Matrix To-Do List")
        self.setGeometry(100, 100, 1200, 900)
        
        # Set up the UI
        self.setup_ui()
        self.setup_keyboard_navigation()
        
        print(f"✓ Main window initialized for date: {self.current_date}")
        
    def setup_ui(self):
        """Set up the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Header section (date and navigation)
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Eisenhower Matrix (4 quadrants)
        matrix_widget = self.create_eisenhower_matrix()
        main_layout.addWidget(matrix_widget, stretch=3)  # Takes most space
        
        # Daily notes section
        notes_widget = self.create_notes_section()
        main_layout.addWidget(notes_widget, stretch=1)
        
        # Bottom section (timer and system monitor)
        bottom_layout = self.create_bottom_section()
        main_layout.addLayout(bottom_layout)
        
    def create_header(self):
        """Create the header with date display and navigation"""
        header_layout = QHBoxLayout()
        
        # Previous day button
        self.prev_button = QPushButton("◀ Prev")
        self.prev_button.clicked.connect(self.previous_day)
        header_layout.addWidget(self.prev_button)
        
        # Current date display
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.date_label.setFont(font)
        self.update_date_display()
        header_layout.addWidget(self.date_label, stretch=1)
        
        # Next day button
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self.next_day)
        header_layout.addWidget(self.next_button)
        
        return header_layout
        
    def create_eisenhower_matrix(self):
        """Create the 4-quadrant Eisenhower Matrix"""
        # Create a frame to contain the matrix
        matrix_frame = QFrame()
        matrix_frame.setFrameStyle(QFrame.Box)
        
        # Grid layout for 2x2 matrix
        matrix_layout = QGridLayout(matrix_frame)
        matrix_layout.setSpacing(2)
        
        # Quadrant labels and colors
        quadrants = [
            ("URGENT & IMPORTANT\n(Quadrant 1)", 0, 0, "#ffebee"),  # Light red
            ("URGENT & NOT IMPORTANT\n(Quadrant 2)", 0, 1, "#fff3e0"),  # Light orange
            ("NOT URGENT & NOT IMPORTANT\n(Quadrant 3)", 1, 1, "#f3e5f5"),  # Light purple
            ("NOT URGENT & IMPORTANT\n(Quadrant 4)", 1, 0, "#e8f5e8")   # Light green
        ]
        
        self.quadrant_widgets = {}
        
        for label_text, row, col, bg_color in quadrants:
            quadrant_num = f"quadrant_{row * 2 + col + 1}"
            
            # Create quadrant container
            quadrant_widget = QWidget()
            quadrant_layout = QVBoxLayout(quadrant_widget)
            
            # Quadrant header
            header_label = QLabel(label_text)
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet(f"background-color: {bg_color}; padding: 5px; font-weight: bold;")
            quadrant_layout.addWidget(header_label)
            
            # Scrollable task area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet(f"background-color: {bg_color};")
            
            # Task container (we'll populate this later)
            task_container = QWidget()
            task_layout = QVBoxLayout(task_container)
            scroll_area.setWidget(task_container)
            
            quadrant_layout.addWidget(scroll_area)
            
            # Store references
            self.quadrant_widgets[quadrant_num] = {
                'widget': quadrant_widget,
                'scroll_area': scroll_area,
                'task_container': task_container,
                'task_layout': task_layout
            }
            
            matrix_layout.addWidget(quadrant_widget, row, col)
        
        return matrix_frame
        
    def create_notes_section(self):
        """Create the daily notes text area"""
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        
        # Notes label
        notes_label = QLabel("Daily Notes:")
        notes_label.setFont(QFont("Arial", 12, QFont.Bold))
        notes_layout.addWidget(notes_label)
        
        # Notes text area
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("What went well today?")
        self.notes_text.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_text)
        
        return notes_widget
        
    def create_bottom_section(self):
        """Create timer and system monitor section"""
        bottom_layout = QHBoxLayout()
        
        # Timer widget (placeholder for now)
        timer_widget = QWidget()
        timer_layout = QVBoxLayout(timer_widget)
        timer_label = QLabel("Timer")
        timer_label.setFont(QFont("Arial", 12, QFont.Bold))
        timer_layout.addWidget(timer_label)
        
        # Timer preset buttons
        preset_layout = QGridLayout()
        presets = [1, 10, 15, 30, 45, 60]
        for i, preset in enumerate(presets):
            btn = QPushButton(f"{preset}")
            preset_layout.addWidget(btn, i // 3, i % 3)
        timer_layout.addLayout(preset_layout)
        
        # Timer display (placeholder)
        timer_display = QLabel("00:00")
        timer_display.setAlignment(Qt.AlignCenter)
        timer_display.setFont(QFont("Arial", 16, QFont.Bold))
        timer_layout.addWidget(timer_display)
        
        bottom_layout.addWidget(timer_widget)
        
        # System monitor widget (placeholder for now)
        monitor_widget = QWidget()
        monitor_layout = QVBoxLayout(monitor_widget)
        monitor_label = QLabel("System Monitor")
        monitor_label.setFont(QFont("Arial", 12, QFont.Bold))
        monitor_layout.addWidget(monitor_label)
        
        cpu_label = QLabel("CPU: 0%")
        memory_label = QLabel("Memory: 0%")
        monitor_layout.addWidget(cpu_label)
        monitor_layout.addWidget(memory_label)
        
        bottom_layout.addWidget(monitor_widget)
        
        return bottom_layout
        
    def setup_keyboard_navigation(self):
        """Set up keyboard shortcuts for navigation"""
        # We'll implement this with key press events
        pass
        
    def keyPressEvent(self, event):
        """Handle keyboard navigation"""
        if event.key() == Qt.Key_Left:
            self.previous_day()
        elif event.key() == Qt.Key_Right:
            self.next_day()
        else:
            super().keyPressEvent(event)
            
    def previous_day(self):
        """Navigate to previous day"""
        self.current_date -= timedelta(days=1)
        self.update_date_display()
        self.load_day_data()
        print(f"✓ Navigated to: {self.current_date}")
        
    def next_day(self):
        """Navigate to next day"""
        self.current_date += timedelta(days=1)
        self.update_date_display()
        self.load_day_data()
        print(f"✓ Navigated to: {self.current_date}")
        
    def update_date_display(self):
        """Update the date display in header"""
        formatted_date = self.current_date.strftime("%a %m/%d/%Y")
        self.date_label.setText(formatted_date)
        
    def load_day_data(self):
        """Load tasks and notes for current day"""
        # We'll implement this when we create the data manager
        print(f"📅 Loading data for {self.current_date}")
