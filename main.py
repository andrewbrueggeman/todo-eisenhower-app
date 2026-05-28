#!/usr/bin/env python3
"""
Eisenhower Matrix To-Do List Application

This application combines a to-do list with the Eisenhower Matrix (4 quadrants),
integrates with Microsoft Outlook calendar, includes a productivity timer,
and monitors system resources.

Features:
- Daily view with 4-quadrant task organization
- Outlook calendar integration
- Productivity timer with presets (1, 10, 15, 30, 45, 60 minutes)
- System resource monitoring (CPU/Memory)
- Task completion tracking and migration
- Daily notes section

Usage:
Run this script to launch the application. The app will create data files
in the 'data_files' directory to store your tasks, settings, and notes.

Navigation:
- Use left/right arrow keys to navigate between days
- Double-click tasks to edit them
- Timer will flash red when complete and auto-restart after acknowledgment
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json

# Import our custom modules
from data.data_manager import DataManager

class TodoEisenhowerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eisenhower Matrix To-Do List")
        self.root.geometry("1400x1000")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize data manager
        self.data_manager = DataManager()
        self.current_date = datetime.now().date()
        
        # Timer variables
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_duration = 20 * 60  # Default 20 minutes
        self.timer_job = None
        
        # Setup UI
        self.setup_ui()
        self.setup_keyboard_bindings()
        self.load_day_data()
        
        # Start system monitoring
        self.update_system_stats()
        
        print("✓ Tkinter application initialized successfully")
        print("✓ Data files ready")
        print("✓ GUI components loaded")
        
    def setup_ui(self):
        """Set up the main user interface"""
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(1, weight=3)  # Matrix gets most space
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header section
        self.create_header()
        
        # Eisenhower Matrix
        self.create_eisenhower_matrix()
        
        # Daily notes section
        self.create_notes_section()
        
        # Bottom section (timer and system monitor)
        self.create_bottom_section()
        
    def create_header(self):
        """Create the header with date display and navigation"""
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Previous day button
        ttk.Button(header_frame, text="◀ Prev", 
                  command=self.previous_day).grid(row=0, column=0, padx=5)
        
        # Current date display
        self.date_label = ttk.Label(header_frame, text="", 
                                   font=('Arial', 18, 'bold'))
        self.date_label.grid(row=0, column=1, padx=20)
        self.update_date_display()
        
        # Next day button
        ttk.Button(header_frame, text="Next ▶", 
                  command=self.next_day).grid(row=0, column=2, padx=5)
        
        # Add task button
        ttk.Button(header_frame, text="+ Add Task", 
                  command=self.add_new_task).grid(row=0, column=3, padx=10)
        
    def create_eisenhower_matrix(self):
        """Create the 4-quadrant Eisenhower Matrix"""
        # Main matrix frame
        matrix_frame = ttk.LabelFrame(self.root, text="Eisenhower Matrix", padding=10)
        matrix_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        
        # Configure grid for 2x2 layout
        matrix_frame.grid_rowconfigure(0, weight=1)
        matrix_frame.grid_rowconfigure(1, weight=1)
        matrix_frame.grid_columnconfigure(0, weight=1)
        matrix_frame.grid_columnconfigure(1, weight=1)
        
        # Quadrant definitions - all same color now
        uniform_color = "#f8f9fa"  # Light gray for all quadrants
        quadrants = [
            ("URGENT & IMPORTANT\n(Quadrant 1)", 0, 0, uniform_color, "quadrant_1"),
            ("URGENT & NOT IMPORTANT\n(Quadrant 2)", 0, 1, uniform_color, "quadrant_2"),
            ("NOT URGENT & NOT IMPORTANT\n(Quadrant 3)", 1, 1, uniform_color, "quadrant_3"),
            ("NOT URGENT & IMPORTANT\n(Quadrant 4)", 1, 0, uniform_color, "quadrant_4")
        ]
        
        self.quadrant_widgets = {}
        
        for label_text, row, col, bg_color, quad_key in quadrants:
            # Create quadrant frame
            quad_frame = ttk.LabelFrame(matrix_frame, text=label_text, padding=5)
            quad_frame.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
            quad_frame.grid_rowconfigure(0, weight=1)
            quad_frame.grid_columnconfigure(0, weight=1)
            
            # Scrollable text widget for tasks
            text_frame = ttk.Frame(quad_frame)
            text_frame.grid(row=0, column=0, sticky='nsew')
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
            
            # Text widget with scrollbar
            text_widget = tk.Text(text_frame, wrap=tk.WORD, height=15, width=30,
                                 font=('Arial', 10), bg=bg_color)
            scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')
            
            # Bind double-click for editing
            text_widget.bind('<Double-Button-1>', lambda e, q=quad_key: self.edit_task(e, q))
            
            # Store references
            self.quadrant_widgets[quad_key] = {
                'frame': quad_frame,
                'text_widget': text_widget,
                'scrollbar': scrollbar
            }
            
    def create_notes_section(self):
        """Create the daily notes section"""
        notes_frame = ttk.LabelFrame(self.root, text="Daily Notes", padding=10)
        notes_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        notes_frame.grid_columnconfigure(0, weight=1)
        
        # Notes text widget
        self.notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD, 
                                 font=('Arial', 10))
        self.notes_text.grid(row=0, column=0, sticky='ew')
        self.notes_text.insert('1.0', "What went well today?")
        
        # Bind text changes to auto-save
        self.notes_text.bind('<KeyRelease>', self.save_notes)
        
    def create_bottom_section(self):
        """Create timer and system monitor section"""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=5)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        # Timer section
        timer_frame = ttk.LabelFrame(bottom_frame, text="Productivity Timer", padding=10)
        timer_frame.grid(row=0, column=0, sticky='nsew', padx=5)
        
        # Timer preset buttons
        preset_frame = ttk.Frame(timer_frame)
        preset_frame.grid(row=0, column=0, pady=5)
        
        presets = [1, 10, 15, 30, 45, 60]
        for i, preset in enumerate(presets):
            btn = ttk.Button(preset_frame, text=f"{preset}m", width=6,
                           command=lambda p=preset: self.set_timer(p))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
        
        # Timer display
        self.timer_display = ttk.Label(timer_frame, text="00:00", 
                                      font=('Arial', 16, 'bold'))
        self.timer_display.grid(row=1, column=0, pady=10)
        
        # Timer control buttons
        control_frame = ttk.Frame(timer_frame)
        control_frame.grid(row=2, column=0)
        
        self.pause_btn = ttk.Button(control_frame, text="Pause", 
                                   command=self.toggle_timer, state='disabled')
        self.pause_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", 
                                  command=self.stop_timer, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # System monitor section
        monitor_frame = ttk.LabelFrame(bottom_frame, text="System Monitor", padding=10)
        monitor_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        
        self.cpu_label = ttk.Label(monitor_frame, text="CPU: 0%", font=('Arial', 12))
        self.cpu_label.grid(row=0, column=0, pady=5)
        
        self.memory_label = ttk.Label(monitor_frame, text="Memory: 0%", font=('Arial', 12))
        self.memory_label.grid(row=1, column=0, pady=5)
        
        self.refresh_label = ttk.Label(monitor_frame, text="Last refresh: Now", 
                                      font=('Arial', 9), foreground='gray')
        self.refresh_label.grid(row=2, column=0, pady=5)
        
    def setup_keyboard_bindings(self):
        """Set up keyboard shortcuts"""
        self.root.bind('<Left>', lambda e: self.previous_day())
        self.root.bind('<Right>', lambda e: self.next_day())
        self.root.focus_set()  # Allow root to receive key events
        
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
        self.date_label.config(text=formatted_date)
        
    def load_day_data(self):
        """Load tasks and notes for current day"""
        print(f"📅 Loading data for {self.current_date}")
        
        # Load tasks for each quadrant
        tasks_data = self.data_manager.get_tasks_for_date(self.current_date)
        
        for quad_key, widget_info in self.quadrant_widgets.items():
            text_widget = widget_info['text_widget']
            text_widget.delete('1.0', tk.END)
            
            # Load tasks for this quadrant
            tasks = tasks_data.get(quad_key, [])
            for task in tasks:
                task_text = task.get('text', '')
                if task.get('completed', False):
                    task_text = f"✓ {task_text}"
                text_widget.insert(tk.END, f"• {task_text}\n")
        
        # Load notes
        notes = self.data_manager.get_notes_for_date(self.current_date)
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert('1.0', notes if notes else "What went well today?")
        
    def add_new_task(self):
        """Add a new task"""
        task_text = simpledialog.askstring("New Task", "Enter task description:")
        if task_text:
            # Ask for quadrant
            quadrant = simpledialog.askinteger("Quadrant", 
                                             "Select quadrant (1-4):", 
                                             minvalue=1, maxvalue=4)
            if quadrant:
                quad_key = f"quadrant_{quadrant}"
                
                # Add to data
                date_str = self.current_date.isoformat()
                if date_str not in self.data_manager.tasks_data:
                    self.data_manager.tasks_data[date_str] = {
                        "quadrant_1": [], "quadrant_2": [], 
                        "quadrant_3": [], "quadrant_4": []
                    }
                
                task_id = len(self.data_manager.tasks_data[date_str][quad_key]) + 1
                new_task = {
                    "id": task_id,
                    "text": task_text,
                    "completed": False,
                    "source": "manual"
                }
                
                self.data_manager.tasks_data[date_str][quad_key].append(new_task)
                self.data_manager.save_tasks()
                
                # Refresh display
                self.load_day_data()
                print(f"✓ Added task: {task_text} to {quad_key}")
    
    def edit_task(self, event, quadrant):
        """Edit a task when double-clicked"""
        # This is a placeholder - we'll implement full editing later
        messagebox.showinfo("Edit Task", f"Task editing for {quadrant} - Coming soon!")
        
    def save_notes(self, event=None):
        """Save daily notes"""
        notes_content = self.notes_text.get('1.0', tk.END).strip()
        date_str = self.current_date.isoformat()
        self.data_manager.notes_data[date_str] = notes_content
        self.data_manager.save_notes()
        
    def set_timer(self, minutes):
        """Set timer to specified minutes"""
        self.timer_duration = minutes * 60
        self.timer_seconds = self.timer_duration
        self.update_timer_display()
        self.start_timer()
        print(f"✓ Timer set to {minutes} minutes")
        
    def start_timer(self):
        """Start the timer"""
        self.timer_running = True
        self.pause_btn.config(state='normal', text='Pause')
        self.stop_btn.config(state='normal')
        self.timer_tick()
        
    def timer_tick(self):
        """Timer countdown logic"""
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            self.timer_job = self.root.after(1000, self.timer_tick)
        elif self.timer_seconds <= 0:
            self.timer_finished()
            
    def update_timer_display(self):
        """Update timer display"""
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_display.config(text=f"{minutes:02d}:{seconds:02d}")
        
    def toggle_timer(self):
        """Pause/resume timer"""
        if self.timer_running:
            self.timer_running = False
            self.pause_btn.config(text='Resume')
            if self.timer_job:
                self.root.after_cancel(self.timer_job)
        else:
            self.timer_running = True
            self.pause_btn.config(text='Pause')
            self.timer_tick()
            
    def stop_timer(self):
        """Stop timer and reset"""
        self.timer_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.timer_seconds = 0
        self.update_timer_display()
        self.pause_btn.config(state='disabled', text='Pause')
        self.stop_btn.config(state='disabled')
        
    def timer_finished(self):
        """Handle timer completion"""
        self.timer_running = False
        # Flash the window (simplified version)
        self.root.configure(bg='red')
        self.root.after(500, lambda: self.root.configure(bg='white'))
        self.root.after(1000, lambda: self.root.configure(bg='#f0f0f0'))
        
        # Show completion dialog
        result = messagebox.askyesno("Timer Complete!", 
                                   "Timer finished! Restart with same duration?")
        if result:
            self.timer_seconds = self.timer_duration
            self.start_timer()
        else:
            self.stop_timer()
            
    def update_system_stats(self):
        """Update CPU and memory usage"""
        try:
            import psutil
            
            # Get CPU usage with a 1-second interval for accuracy
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            
            self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
            self.memory_label.config(text=f"Memory: {memory_percent:.1f}%")
            
            now = datetime.now().strftime("%H:%M:%S")
            self.refresh_label.config(text=f"Last refresh: {now}")
            print(f"✓ System stats updated: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%")
            
        except ImportError:
            self.cpu_label.config(text="CPU: psutil not available")
            self.memory_label.config(text="Memory: psutil not available")
            print("⚠️ psutil not installed - system monitoring disabled")
            
        except Exception as e:
            print(f"⚠️ System monitoring error: {e}")
            self.cpu_label.config(text="CPU: Error")
            self.memory_label.config(text="Memory: Error")
            
        # Schedule next update
        self.root.after(30000, self.update_system_stats)  # Update every 30 seconds

def main():
    """Main entry point"""
    # Create data directory if it doesn't exist
    if not os.path.exists('data_files'):
        os.makedirs('data_files')
        print("✓ Created data_files directory")
    
    # Initialize and run application
    app = TodoEisenhowerApp()
    print("🚀 Starting Eisenhower Matrix To-Do Application...")
    app.root.mainloop()

if __name__ == "__main__":
    main()
