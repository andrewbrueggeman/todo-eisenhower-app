import tkinter as tk
from datetime import datetime
import psutil

class MonitorWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_monitor()
    
    def setup_monitor(self):
        # Main container
        monitor_container = tk.Frame(self.parent, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        monitor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title
        tk.Label(monitor_container, text="🖥️ System Monitor", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(10, 5))
        
        # Stats frame
        stats_frame = tk.Frame(monitor_container, bg="#f0f0f0")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # CPU Usage
        cpu_frame = tk.Frame(stats_frame, bg="#f0f0f0")
        cpu_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cpu_frame, text="CPU:", font=("Arial", 11, "bold"), bg="#f0f0f0", width=8, anchor="w").pack(side=tk.LEFT)
        self.cpu_label = tk.Label(cpu_frame, text="0.0%", font=("Arial", 11), bg="#f0f0f0", fg="#2c3e50")
        self.cpu_label.pack(side=tk.LEFT)
        
        self.cpu_bar = tk.Canvas(cpu_frame, height=15, bg="white", relief=tk.SUNKEN, bd=1)
        self.cpu_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Memory Usage
        mem_frame = tk.Frame(stats_frame, bg="#f0f0f0")
        mem_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(mem_frame, text="Memory:", font=("Arial", 11, "bold"), bg="#f0f0f0", width=8, anchor="w").pack(side=tk.LEFT)
        self.mem_label = tk.Label(mem_frame, text="0.0%", font=("Arial", 11), bg="#f0f0f0", fg="#2c3e50")
        self.mem_label.pack(side=tk.LEFT)
        
        self.mem_bar = tk.Canvas(mem_frame, height=15, bg="white", relief=tk.SUNKEN, bd=1)
        self.mem_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Current Time
        time_frame = tk.Frame(stats_frame, bg="#f0f0f0")
        time_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(time_frame, text="Time:", font=("Arial", 11, "bold"), bg="#f0f0f0", width=8, anchor="w").pack(side=tk.LEFT)
        self.time_label = tk.Label(time_frame, text="00:00:00", font=("Arial", 11), bg="#f0f0f0", fg="#2c3e50")
        self.time_label.pack(side=tk.LEFT)
        
        # System Info
        info_frame = tk.Frame(stats_frame, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, pady=(15, 5))
        
        try:
            cpu_count = psutil.cpu_count()
            total_mem = psutil.virtual_memory().total / (1024**3)  # GB
            tk.Label(info_frame, text=f"Cores: {cpu_count} | RAM: {total_mem:.1f}GB", 
                    font=("Arial", 9), bg="#f0f0f0", fg="#7f8c8d").pack()
        except:
            tk.Label(info_frame, text="System info unavailable", 
                    font=("Arial", 9), bg="#f0f0f0", fg="#7f8c8d").pack()
    
    def update_stats(self, cpu_percent, mem_percent, current_time):
        # Update text labels
        self.cpu_label.config(text=f"{cpu_percent:.1f}%")
        self.mem_label.config(text=f"{mem_percent:.1f}%")
        self.time_label.config(text=current_time)
        
        # Update CPU bar
        self.cpu_bar.delete("all")
        bar_width = self.cpu_bar.winfo_width()
        if bar_width > 1:
            cpu_width = (cpu_percent / 100) * bar_width
            color = self._get_usage_color(cpu_percent)
            self.cpu_bar.create_rectangle(0, 0, cpu_width, 15, fill=color, outline="")
        
        # Update Memory bar
        self.mem_bar.delete("all")
        bar_width = self.mem_bar.winfo_width()
        if bar_width > 1:
            mem_width = (mem_percent / 100) * bar_width
            color = self._get_usage_color(mem_percent)
            self.mem_bar.create_rectangle(0, 0, mem_width, 15, fill=color, outline="")
    
    def _get_usage_color(self, percent):
        if percent < 50:
            return "#27ae60"  # Green
        elif percent < 80:
            return "#f39c12"  # Orange
        else:
            return "#e74c3c"  # Red
