"""
System Monitor Widget

Displays real-time system resource usage including CPU, memory, and time.
"""

import tkinter as tk
from datetime import datetime

class MonitorWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.setup_monitor()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitor widget initialized")
    
    def setup_monitor(self):
        """Setup system monitor UI"""
        monitor_frame = tk.LabelFrame(self.parent, text="System Monitor", 
                                     font=("Arial", 12, "bold"),
                                     bg="#f0f0f0", padx=10, pady=10)
        monitor_frame.pack(fill=tk.BOTH, expand=True)
        
        # CPU usage
        cpu_frame = tk.Frame(monitor_frame, bg="#f0f0f0")
        cpu_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(cpu_frame, text="CPU:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", width=8, anchor=tk.W).pack(side=tk.LEFT)
        
        self.cpu_label = tk.Label(cpu_frame, text="0.0%", 
                                 font=("Arial", 10), bg="#f0f0f0", fg="#3498db")
        self.cpu_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Memory usage
        memory_frame = tk.Frame(monitor_frame, bg="#f0f0f0")
        memory_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(memory_frame, text="Memory:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", width=8, anchor=tk.W).pack(side=tk.LEFT)
        
        self.memory_label = tk.Label(memory_frame, text="0.0%", 
                                    font=("Arial", 10), bg="#f0f0f0", fg="#e74c3c")
        self.memory_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Current time
        time_frame = tk.Frame(monitor_frame, bg="#f0f0f0")
        time_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(time_frame, text="Time:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", width=8, anchor=tk.W).pack(side=tk.LEFT)
        
        self.time_label = tk.Label(time_frame, text="--:--:--", 
                                  font=("Arial", 10), bg="#f0f0f0", fg="#27ae60")
        self.time_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status indicator
        self.status_label = tk.Label(monitor_frame, text="Monitoring active", 
                                    font=("Arial", 8), bg="#f0f0f0", fg="#7f8c8d")
        self.status_label.pack(pady=2)
    
    def update_stats(self, cpu_percent, memory_percent, current_time):
        """Update system statistics display"""
        try:
            # Check if widgets still exist before updating
            if not hasattr(self, 'cpu_label') or not self.cpu_label.winfo_exists():
                return
            
            # Update CPU with color coding
            self.cpu_label.config(text=f"{cpu_percent:.1f}%")
            if cpu_percent > 80:
                self.cpu_label.config(fg="#e74c3c")  # Red for high usage
            elif cpu_percent > 60:
                self.cpu_label.config(fg="#f39c12")  # Orange for medium usage
            else:
                self.cpu_label.config(fg="#3498db")  # Blue for normal usage
            
            # Update Memory with color coding
            if hasattr(self, 'memory_label') and self.memory_label.winfo_exists():
                self.memory_label.config(text=f"{memory_percent:.1f}%")
                if memory_percent > 85:
                    self.memory_label.config(fg="#e74c3c")  # Red for high usage
                elif memory_percent > 70:
                    self.memory_label.config(fg="#f39c12")  # Orange for medium usage
                else:
                    self.memory_label.config(fg="#27ae60")  # Green for normal usage
            
            # Update time - Convert to 12-hour format
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                from datetime import datetime
                time_obj = datetime.strptime(current_time, "%H:%M:%S")
                formatted_time = time_obj.strftime("%I:%M:%S %p")
                self.time_label.config(text=formatted_time)
                
        except tk.TclError:
            # Widget has been destroyed, stop trying to update
            return
        except Exception as e:
            # Any other error, just return silently
            return
