"""
Main Application Window for Eisenhower Matrix To-Do App

WHAT THIS SCRIPT DOES:
- Creates the main Tkinter application window
- Builds the Eisenhower Matrix layout (matrix, notes, timer, monitor)
- Loads task and note data
- Starts system monitoring in a background thread
- Integrates Outlook calendar safely (optional, non-breaking)
- Handles clean shutdown of background processes

HOW TO RUN:
1. From your project root directory:
   python3 main.py

2. Make sure dependencies are installed:
   python3 -m pip install -r requirements.txt

NOTES:
- Outlook integration will NOT crash the app if it fails
- Integration only runs after all components are initialized
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import time
import psutil


class EisenhowerMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eisenhower Matrix - Task Manager")
        self.root.geometry("1400x900")

        print("Initializing application...")

        # Initialize data manager
        from data.data_manager import DataManager
        self.data_manager = DataManager()

        # Core state
        self.current_date = datetime.now().date()
        self.monitoring = True

        # Timer state
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_thread = None

        # Outlook integration
        self.outlook_sync = None

        # Layout settings
        self.layout_settings = {
            "matrix_height_ratio": 0.55,
            "notes_height_ratio": 0.15,
            "bottom_height_ratio": 0.30
        }

        # Build application
        self.setup_ui()
        self.load_data()
        self.bind_keys()
        self.start_system_monitoring()

        # Initialize Outlook LAST (important)
        self.initialize_outlook_integration()

        print("Application initialized successfully")

    def setup_ui(self):
        print("Setting up UI...")

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_header(main_frame)

        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        total_height = 700

        matrix_height = int(total_height * self.layout_settings["matrix_height_ratio"])
        notes_height = int(total_height * self.layout_settings["notes_height_ratio"])
        bottom_height = int(total_height * self.layout_settings["bottom_height_ratio"])

        # Matrix
        self.matrix_frame = tk.Frame(content_frame, height=matrix_height)
        self.matrix_frame.pack(fill=tk.BOTH, expand=True)
        self.matrix_frame.pack_propagate(False)

        self.setup_matrix()

        # Notes
        notes_frame = tk.Frame(content_frame, height=notes_height)
        notes_frame.pack(fill=tk.X, pady=(10, 5))
        notes_frame.pack_propagate(False)

        self.setup_notes(notes_frame)

        # Bottom
        bottom_frame = tk.Frame(content_frame, height=bottom_height)
        bottom_frame.pack(fill=tk.X)
        bottom_frame.pack_propagate(False)

        timer_frame = tk.Frame(bottom_frame)
        timer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        monitor_frame = tk.Frame(bottom_frame)
        monitor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_timer(timer_frame)
        self.setup_system_monitor(monitor_frame)

        print("UI setup complete")

    def setup_header(self, parent):
        header = tk.Frame(parent, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        nav = tk.Frame(header, bg="#2c3e50")
        nav.pack(side=tk.LEFT, padx=20, pady=15)

        tk.Button(nav, text="◀", command=self.prev_day).pack(side=tk.LEFT)

        self.date_label = tk.Label(nav, fg="white", bg="#2c3e50")
        self.date_label.pack(side=tk.LEFT, padx=10)

        tk.Button(nav, text="▶", command=self.next_day).pack(side=tk.LEFT)

        tk.Button(header, text="Settings", command=self.open_settings).pack(
            side=tk.RIGHT, padx=20
        )

        self.update_date_display()

    def setup_matrix(self):
        from ui.components.matrix_widget import MatrixWidget
        self.matrix_widget = MatrixWidget(self.matrix_frame, self)

    def setup_timer(self, parent):
        from ui.components.timer_widget import TimerWidget
        self.timer_widget = TimerWidget(parent, self)

    def setup_system_monitor(self, parent):
        from ui.components.monitor_widget import MonitorWidget
        self.monitor_widget = MonitorWidget(parent, self)

    def setup_notes(self, parent):
        from ui.components.notes_widget import NotesWidget
        self.notes_widget = NotesWidget(parent, self)

    def initialize_outlook_integration(self):
        print("Initializing Outlook integration...")

        try:
            from outlook_integration import OutlookCalendarSync

            self.outlook_sync = OutlookCalendarSync(
                data_manager=self.data_manager,
                matrix_widget=self.matrix_widget
            )

            if hasattr(self.outlook_sync, "start_periodic_sync"):
                self.outlook_sync.start_periodic_sync()

            print("Outlook integration ready")

        except Exception as e:
            print("Outlook integration failed:", str(e))
            self.outlook_sync = None

    def open_settings(self):
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.root, self)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.data_manager.settings_data.update(dialog.result)
            self.data_manager.save_settings()

    def prev_day(self):
        self.current_date -= timedelta(days=1)
        self.refresh_data()

    def next_day(self):
        self.current_date += timedelta(days=1)
        self.refresh_data()

    def update_date_display(self):
        self.date_label.config(
            text=self.current_date.strftime("%A, %B %d, %Y")
        )

    def refresh_data(self):
        self.update_date_display()
        self.load_data()

    def load_data(self):
        if hasattr(self, "matrix_widget"):
            self.matrix_widget.load_tasks()
        if hasattr(self, "notes_widget"):
            self.notes_widget.load_notes()

    def start_system_monitoring(self):
        def monitor():
            while self.monitoring:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    mem = psutil.virtual_memory().percent

                    if hasattr(self, "monitor_widget"):
                        self.root.after(
                            0,
                            lambda: self.monitor_widget.update_stats(
                                cpu, mem, datetime.now().strftime("%H:%M:%S")
                            )
                        )
                except Exception:
                    continue

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def bind_keys(self):
        self.root.bind("<Left>", lambda e: self.prev_day())
        self.root.bind("<Right>", lambda e: self.next_day())

    def on_closing(self):
        print("Shutting down application...")

        self.monitoring = False
        self.timer_running = False

        if self.outlook_sync:
            try:
                if hasattr(self.outlook_sync, "cleanup"):
                    self.outlook_sync.cleanup()
            except Exception as e:
                print("Outlook cleanup error:", str(e))

        time.sleep(0.1)

        self.root.quit()
        self.root.destroy()
