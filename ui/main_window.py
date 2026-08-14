import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import time
import psutil
import os
import sys

# Add current directory to path to allow importing local modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class EisenhowerMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eisenhower Matrix - Task Manager")
        self.root.geometry("1400x900")

        try:
            from data.data_manager import DataManager
            self.data_manager = DataManager()
        except ImportError:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from data.data_manager import DataManager
            self.data_manager = DataManager()

        self.current_date = datetime.now().date()
        self.monitoring = True
        self.timer_running = False
        self.outlook_sync = None

        self.setup_ui()
        self.load_data()
        self.bind_keys()

        settings = self.data_manager.settings_data.get('layout', {})
        if settings.get('show_monitor', True):
            self.start_system_monitoring()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_header(self.main_frame)

        self.content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        settings = self.data_manager.settings_data.get('layout', {})

        self.matrix_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.notes_frame = tk.Frame(self.content_frame, bg="#f0f0f0", height=150)
        self.bottom_frame = tk.Frame(self.content_frame, bg="#f0f0f0", height=200)

        self.notes_frame.pack_propagate(False)
        self.bottom_frame.pack_propagate(False)

        show_notes = settings.get('show_notes', True)
        show_bottom = settings.get('show_timer', True) or settings.get('show_monitor', True)

        if show_bottom:
            self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        if show_notes:
            self.notes_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.matrix_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        self.setup_matrix()

        if show_notes:
            self.setup_notes(self.notes_frame)

        if show_bottom:
            if settings.get('show_timer', True):
                self.timer_frame = tk.Frame(self.bottom_frame, bg="#f0f0f0")
                self.timer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
                self.setup_timer(self.timer_frame)

            if settings.get('show_monitor', True):
                self.monitor_frame = tk.Frame(self.bottom_frame, bg="#f0f0f0")
                self.monitor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
                self.setup_system_monitor(self.monitor_frame)

    def setup_header(self, parent):
        header = tk.Frame(parent, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        nav = tk.Frame(header, bg="#2c3e50")
        nav.pack(side=tk.LEFT, padx=20, pady=15)

        btn_prev = tk.Button(nav, text="◀", command=self.prev_day, cursor="hand2")
        btn_prev.grid(row=0, column=0)

        self.date_label = tk.Label(
            nav,
            fg="white",
            bg="#2c3e50",
            font=("Arial", 12, "bold"),
            width=35,
            anchor="center"
        )
        self.date_label.grid(row=0, column=1, padx=10)

        btn_next = tk.Button(nav, text="▶", command=self.next_day, cursor="hand2")
        btn_next.grid(row=0, column=2)

        btn_today = tk.Button(nav, text="Today", command=self.go_today, cursor="hand2", padx=10)
        btn_today.grid(row=0, column=3, padx=(15, 0))

        tk.Button(
            header,
            text="⚙️ Settings",
            command=self.open_settings,
            cursor="hand2",
            padx=10
        ).pack(side=tk.RIGHT, padx=20)

        self.update_date_display()

    def setup_matrix(self):
        try:
            from ui.components.matrix_widget import MatrixWidget
            self.matrix_widget = MatrixWidget(self.matrix_frame, self)
        except Exception as e:
            tk.Label(
                self.matrix_frame,
                text=f"Error loading matrix widget: {e}",
                fg="red",
                bg="#f0f0f0"
            ).pack(pady=20)

    def setup_timer(self, parent):
        try:
            from ui.components.timer_widget import TimerWidget
            self.timer_widget = TimerWidget(parent, self)
        except Exception as e:
            tk.Label(parent, text=f"Timer Widget Error:\n{e}", fg="red", bg="#f0f0f0").pack(pady=20)

    def setup_system_monitor(self, parent):
        try:
            from ui.components.monitor_widget import MonitorWidget
            self.monitor_widget = MonitorWidget(parent, self)
        except Exception as e:
            tk.Label(parent, text=f"Monitor Widget Error:\n{e}", fg="red", bg="#f0f0f0").pack(pady=20)

    def setup_notes(self, parent):
        try:
            from ui.components.notes_widget import NotesWidget
            self.notes_widget = NotesWidget(parent, self)
        except Exception as e:
            tk.Label(parent, text=f"Notes Widget Error:\n{e}", fg="red", bg="#f0f0f0").pack(pady=20)

    def open_settings(self):
        try:
            from ui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self.root, self)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load settings dialog: {e}")

    def _change_date(self, new_date):
        """Centralized date change handler that protects unsaved notes."""
        if hasattr(self, "notes_widget"):
            if not self.notes_widget.check_unsaved_changes():
                return

        self.current_date = new_date
        self.refresh_data()

    def go_today(self):
        self._change_date(datetime.now().date())

    def prev_day(self):
        self._change_date(self.current_date - timedelta(days=1))

    def next_day(self):
        self._change_date(self.current_date + timedelta(days=1))

    def update_date_display(self):
        date_str = self.current_date.strftime("%A, %B %d, %Y")
        if self.current_date == datetime.now().date():
            date_str += " (Today)"
        self.date_label.config(text=date_str)

    def refresh_data(self):
        self.update_date_display()

        if hasattr(self, "matrix_widget"):
            self.matrix_widget.load_tasks()

        if hasattr(self, "notes_widget"):
            self.notes_widget.load_notes()

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
                    current_time = datetime.now().strftime("%I:%M:%S %p")

                    if hasattr(self, "monitor_widget") and hasattr(self.monitor_widget, "update_stats"):
                        self.root.after(
                            0,
                            lambda: self.monitor_widget.update_stats(cpu, mem, current_time)
                        )
                except Exception:
                    pass

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def bind_keys(self):
        self.root.bind("<Left>", lambda e: self.prev_day())
        self.root.bind("<Right>", lambda e: self.next_day())

    def on_closing(self):
        try:
            if hasattr(self, "notes_widget") and self.notes_widget.unsaved_changes:
                self.notes_widget.save_notes(silent=True)
        except Exception as e:
            print(f"Error auto-saving notes on close: {e}")
    
        self.monitoring = False
        self.timer_running = False
        time.sleep(0.1)
        self.root.quit()
        self.root.destroy()

