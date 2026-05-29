"""
Timer Widget

Provides focus timer functionality with presets and controls.
Supports different timer durations and visual feedback.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime

class TimerWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.setup_timer()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer widget initialized")
    
    def setup_timer(self):
        """Setup timer UI components"""
        timer_frame = tk.LabelFrame(self.parent, text="Focus Timer", 
                                   font=("Arial", 12, "bold"),
                                   bg="#f0f0f0", padx=10, pady=10)
        timer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Timer display
        self.timer_display = tk.Label(timer_frame, text="00:00", 
                                     font=("Arial", 20, "bold"), bg="#f0f0f0",
                                     fg="#2c3e50")
        self.timer_display.pack(pady=8)
        
        # Preset buttons in a more compact layout
        presets_frame = tk.Frame(timer_frame, bg="#f0f0f0")
        presets_frame.pack(fill=tk.X, pady=5)
        
        presets = [1, 10, 15, 30, 45, 60]
        for i, minutes in enumerate(presets):
            btn = tk.Button(presets_frame, text=f"{minutes}m",
                           command=lambda m=minutes: self.set_timer(m),
                           bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                           relief=tk.FLAT, padx=8, pady=2)
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
        
        # Configure grid weights for equal button sizing
        for i in range(3):
            presets_frame.grid_columnconfigure(i, weight=1)
        
        # Control buttons
        controls_frame = tk.Frame(timer_frame, bg="#f0f0f0")
        controls_frame.pack(fill=tk.X, pady=8)
        
        self.start_btn = tk.Button(controls_frame, text="Start", 
                                  command=self.start_timer,
                                  bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                                  relief=tk.FLAT, padx=10, pady=3)
        self.start_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.stop_btn = tk.Button(controls_frame, text="Stop", 
                                 command=self.stop_timer,
                                 bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                                 relief=tk.FLAT, padx=10, pady=3)
        self.stop_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Status indicator
        self.status_label = tk.Label(timer_frame, text="Ready", 
                                    font=("Arial", 9), bg="#f0f0f0", fg="#7f8c8d")
        self.status_label.pack(pady=2)
    
    def set_timer(self, minutes):
        """Set timer to specified minutes"""
        self.app.timer_seconds = minutes * 60
        self.update_timer_display()
        self.status_label.config(text=f"Set to {minutes} minutes", fg="#3498db")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer set to {minutes} minutes")
    
    def start_timer(self):
        """Start the timer"""
        if not self.app.timer_running and self.app.timer_seconds > 0:
            self.app.timer_running = True
            self.status_label.config(text="Running...", fg="#27ae60")
            self.start_btn.config(state=tk.DISABLED)
            
            self.app.timer_thread = threading.Thread(target=self.run_timer)
            self.app.timer_thread.daemon = True
            self.app.timer_thread.start()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer started")
        elif self.app.timer_seconds == 0:
            self.status_label.config(text="Please set a timer first", fg="#e74c3c")
    
    def stop_timer(self):
        """Stop the timer"""
        self.app.timer_running = False
        self.status_label.config(text="Stopped", fg="#e74c3c")
        self.start_btn.config(state=tk.NORMAL)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer stopped")
    
    def run_timer(self):
        """Timer countdown loop"""
        while self.app.timer_running and self.app.timer_seconds > 0:
            time.sleep(1)
            if self.app.timer_running:
                self.app.timer_seconds -= 1
                self.app.root.after(0, self.update_timer_display)
        
        if self.app.timer_seconds == 0:
            self.app.root.after(0, self.timer_finished)
    
    def update_timer_display(self):
        """Update timer display"""
        minutes = self.app.timer_seconds // 60
        seconds = self.app.timer_seconds % 60
        self.timer_display.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Change color as timer gets low
        if self.app.timer_seconds <= 60:  # Last minute
            self.timer_display.config(fg="#e74c3c")
        elif self.app.timer_seconds <= 300:  # Last 5 minutes
            self.timer_display.config(fg="#f39c12")
        else:
            self.timer_display.config(fg="#2c3e50")
    
    def timer_finished(self):
        """Handle timer completion"""
        self.app.timer_running = False
        self.status_label.config(text="Completed!", fg="#27ae60")
        self.start_btn.config(state=tk.NORMAL)
        self.timer_display.config(fg="#27ae60")
        
        # Show completion message
        messagebox.showinfo("Timer Finished", "Focus session completed!\n\nGreat work! 🎉")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer finished - focus session completed")
