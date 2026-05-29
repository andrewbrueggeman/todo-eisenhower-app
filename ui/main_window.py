"""
Main Application Window for Eisenhower Matrix To-Do App

Handles the main window layout, component arrangement, and overall application flow.
Supports configurable UI layout through settings.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import psutil

class EisenhowerMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eisenhower Matrix - Task Manager")
        self.root.geometry("1400x900")  # Increased size for better layout
        
        # Initialize data manager
        from data.data_manager import DataManager
        self.data_manager = DataManager()
        
        # Current date
        self.current_date = datetime.now().date()
        
        # Timer variables
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_thread = None
        
        # System monitoring
        self.monitoring = True
        
        # UI Layout settings (can be modified via settings dialog)
        self.layout_settings = {
            'matrix_height_ratio': 0.55,  # 60% of screen for matrix
            'notes_height_ratio': 0.15,  # 20% for notes
            'bottom_height_ratio': 0.3   # 20% for timer/monitor
        }
        
        self.setup_ui()
        self.load_data()
        self.bind_keys()
        self.start_system_monitoring()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Eisenhower Matrix app initialized successfully")
    
    def setup_ui(self):
        """Setup the main UI with configurable layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with date navigation and settings
        self.setup_header(main_frame)
        
        # Content area with configurable layout
        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Calculate actual heights based on available space
        total_content_height = 700  # Approximate content area height
        
        matrix_height = int(total_content_height * self.layout_settings['matrix_height_ratio'])
        notes_height = int(total_content_height * self.layout_settings['notes_height_ratio'])
        bottom_height = int(total_content_height * self.layout_settings['bottom_height_ratio'])
        
        # Top section - Eisenhower Matrix
        self.matrix_frame = tk.Frame(content_frame, bg="#f0f0f0", height=matrix_height)
        self.matrix_frame.pack(fill=tk.BOTH, expand=True)
        self.matrix_frame.pack_propagate(False)  # Maintain fixed height
        
        self.setup_matrix()
        
        # Middle section - Notes
        notes_frame = tk.Frame(content_frame, bg="#f0f0f0", height=notes_height)
        notes_frame.pack(fill=tk.X, pady=(10, 5))
        notes_frame.pack_propagate(False)  # Maintain fixed height
        
        self.setup_notes(notes_frame)
        
        # Bottom section - Timer and Monitor
        bottom_frame = tk.Frame(content_frame, bg="#f0f0f0", height=bottom_height)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        bottom_frame.pack_propagate(False)  # Maintain fixed height
        
        # Split bottom into timer (left) and monitor (right)
        timer_frame = tk.Frame(bottom_frame, bg="#f0f0f0")
        timer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        monitor_frame = tk.Frame(bottom_frame, bg="#f0f0f0")
        monitor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.setup_timer(timer_frame)
        self.setup_system_monitor(monitor_frame)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Layout applied - Matrix: {matrix_height}px, Notes: {notes_height}px, Bottom: {bottom_height}px")
    
    def setup_header(self, parent):
        """Setup header with navigation and settings"""
        header_frame = tk.Frame(parent, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Left side - Date navigation
        nav_frame = tk.Frame(header_frame, bg="#2c3e50")
        nav_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.prev_btn = tk.Button(nav_frame, text="◀", font=("Arial", 16, "bold"),
                                 command=self.prev_day, bg="#34495e", fg="white",
                                 relief=tk.FLAT, padx=10)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_label = tk.Label(nav_frame, font=("Arial", 18, "bold"),
                                  bg="#2c3e50", fg="white")
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = tk.Button(nav_frame, text="▶", font=("Arial", 16, "bold"),
                                 command=self.next_day, bg="#34495e", fg="white",
                                 relief=tk.FLAT, padx=10)
        self.next_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right side - Settings button
        settings_frame = tk.Frame(header_frame, bg="#2c3e50")
        settings_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.settings_btn = tk.Button(settings_frame, text="⚙️ Settings", 
                                     font=("Arial", 12, "bold"),
                                     command=self.open_settings, bg="#34495e", fg="white",
                                     relief=tk.FLAT, padx=15)
        self.settings_btn.pack()
        
        self.update_date_display()
    
    def setup_matrix(self):
        """Setup the Eisenhower Matrix"""
        from ui.components.matrix_widget import MatrixWidget
        self.matrix_widget = MatrixWidget(self.matrix_frame, self)
    
    def setup_timer(self, parent):
        """Setup the timer component"""
        from ui.components.timer_widget import TimerWidget
        self.timer_widget = TimerWidget(parent, self)
    
    def setup_system_monitor(self, parent):
        """Setup the system monitor component"""
        from ui.components.monitor_widget import MonitorWidget
        self.monitor_widget = MonitorWidget(parent, self)
    
    def setup_notes(self, parent):
        """Setup the notes component"""
        from ui.components.notes_widget import NotesWidget
        self.notes_widget = NotesWidget(parent, self)
    
    def open_settings(self):
        """Open settings dialog"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.apply_settings(dialog.result)
    
    def apply_settings(self, settings):
        """Apply new settings to the application"""
        self.layout_settings.update(settings.get('layout', {}))
        
        # Save settings to data manager
        self.data_manager.settings_data.update(settings)
        self.data_manager.save_settings()
        
        # Refresh UI if layout changed
        if 'layout' in settings:
            messagebox.showinfo("Settings", "Layout changes will take effect after restarting the application.")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Settings updated")
    
    def prev_day(self):
        self.current_date -= timedelta(days=1)
        self.update_date_display()
        self.load_data()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Navigated to previous day: {self.current_date}")
    
    def next_day(self):
        self.current_date += timedelta(days=1)
        self.update_date_display()
        self.load_data()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Navigated to next day: {self.current_date}")
    
    def update_date_display(self):
        formatted_date = self.current_date.strftime("%A, %B %d, %Y")
        self.date_label.config(text=formatted_date)
    
    def load_data(self):
        """Load data for current date"""
        if hasattr(self, 'matrix_widget'):
            self.matrix_widget.load_tasks()
        if hasattr(self, 'notes_widget'):
            self.notes_widget.load_notes()
    
    def start_system_monitoring(self):
        """Start system monitoring in background thread"""
        def update_system_info():
            while self.monitoring:
                try:
                    if not self.monitoring:  # Double-check
                        break
                        
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    if hasattr(self, 'monitor_widget') and self.monitoring:
                        try:
                            self.root.after(0, lambda: self.monitor_widget.update_stats(
                                cpu_percent, memory_percent, current_time))
                        except tk.TclError:
                            # Window has been destroyed, stop monitoring
                            break
                except Exception:
                    # If any error occurs, just continue or break if monitoring is stopped
                    if not self.monitoring:
                        break
                    continue
        
        monitor_thread = threading.Thread(target=update_system_info)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def bind_keys(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Left>', lambda e: self.prev_day())
        self.root.bind('<Right>', lambda e: self.next_day())
        self.root.focus_set()
    
    def on_closing(self):
        """Handle application closing"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Application closing...")
        
        # Stop monitoring first
        self.monitoring = False
        
        # Stop timer if running
        self.timer_running = False
        
        # Give threads a moment to stop
        import time
        time.sleep(0.1)
        
        # Destroy the window
        self.root.quit()  # Use quit() instead of destroy()
        self.root.destroy()
