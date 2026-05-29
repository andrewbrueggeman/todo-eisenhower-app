"""
Eisenhower Matrix Widget

Handles the 4-quadrant task matrix display and management.
Supports task creation, editing, completion, and organization.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class MatrixWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.quadrant_frames = {}
        self.task_listboxes = {}
        
        self.setup_matrix()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Matrix widget initialized")
    
    def setup_matrix(self):
        """Setup the Eisenhower Matrix layout"""
        # Matrix title
        title_label = tk.Label(self.parent, text="To Do List & Prioritization Matrix", 
                              font=("Arial", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 15))
        
        # Matrix grid container
        matrix_container = tk.Frame(self.parent, bg="#f0f0f0")
        matrix_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for equal sizing
        matrix_container.grid_rowconfigure(0, weight=1)
        matrix_container.grid_rowconfigure(1, weight=1)
        matrix_container.grid_columnconfigure(0, weight=1)
        matrix_container.grid_columnconfigure(1, weight=1)
        
        # Quadrant definitions
        quadrants = [
            ("Q1: Urgent & Important\n(Do First)", "quadrant_1", 0, 0),
            ("Q2: Important, Not Urgent\n(Schedule)", "quadrant_2", 0, 1),
            ("Q3: Urgent, Not Important\n(Delegate)", "quadrant_3", 1, 0),
            ("Q4: Not Urgent, Not Important\n(Eliminate)", "quadrant_4", 1, 1)
        ]
        
        for title, quad_id, row, col in quadrants:
            self.create_quadrant(matrix_container, title, quad_id, row, col)
    
    def create_quadrant(self, parent, title, quad_id, row, col):
        """Create a single quadrant with tasks and controls"""
        # Main quadrant frame
        quad_frame = tk.Frame(parent, bg="#d3d3d3", relief=tk.RAISED, bd=2)
        quad_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Title
        title_label = tk.Label(quad_frame, text=title, font=("Arial", 12, "bold"),
                              bg="#d3d3d3", wraplength=250)
        title_label.pack(pady=8)
        
        # Task list frame with scrollbar
        list_frame = tk.Frame(quad_frame, bg="#d3d3d3")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        # Scrollable canvas for tasks
        canvas = tk.Canvas(list_frame, bg="#d3d3d3", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#d3d3d3")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store references
        self.quadrant_frames[quad_id] = scrollable_frame
        self.task_listboxes[quad_id] = []
        
        # Add task button
        add_btn = tk.Button(quad_frame, text="+ Add Task", 
                           command=lambda: self.add_task(quad_id),
                           bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                           relief=tk.FLAT, padx=15, pady=5)
        add_btn.pack(pady=8)
    
    def create_task_widget(self, parent, task_data, quad_id, task_index):
        """Create a task widget with checkbox and text"""
        task_frame = tk.Frame(parent, bg="#d3d3d3", pady=3)
        task_frame.pack(fill=tk.X, padx=3, pady=2)
        
        # Checkbox
        var = tk.BooleanVar(value=task_data.get('completed', False))
        checkbox = tk.Checkbutton(task_frame, variable=var, bg="#d3d3d3",
                                 command=lambda: self.toggle_task_completion(quad_id, task_index, var.get()))
        checkbox.pack(side=tk.LEFT, padx=(0, 8))
        
        # Task text with completion styling
        text_bg = "#90EE90" if task_data.get('completed', False) else "white"
        text_fg = "#666666" if task_data.get('completed', False) else "black"
        
        task_label = tk.Label(task_frame, text=task_data['text'], 
                             bg=text_bg, fg=text_fg, 
                             font=("Arial", 10), wraplength=220, justify=tk.LEFT,
                             relief=tk.RAISED, bd=1, padx=8, pady=4)
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind double-click for editing
        task_label.bind("<Double-Button-1>", 
                       lambda e: self.edit_task(quad_id, task_index))
        
        # Right-click context menu for delete
        task_label.bind("<Button-3>", 
                       lambda e: self.show_context_menu(e, quad_id, task_index))
        
        return {
            'frame': task_frame,
            'checkbox': checkbox,
            'label': task_label,
            'var': var
        }
    
    def show_context_menu(self, event, quad_id, task_index):
        """Show right-click context menu"""
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Edit Task", 
                                command=lambda: self.edit_task(quad_id, task_index))
        context_menu.add_separator()
        context_menu.add_command(label="Delete Task", 
                                command=lambda: self.delete_task(quad_id, task_index))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def add_task(self, quadrant):
        """Add a new task to the specified quadrant"""
        from ui.task_dialog import TaskEditDialog
        
        dialog = TaskEditDialog(self.app.root, "", quadrant)
        self.app.root.wait_window(dialog.dialog)
        
        if dialog.result:
            task_data = {
                'text': dialog.result['text'],
                'completed': False,
                'created_date': self.app.current_date.isoformat(),
                'created_time': datetime.now().strftime('%H:%M:%S')
            }
            
            # Add to data manager
            date_str = self.app.current_date.isoformat()
            if date_str not in self.app.data_manager.tasks_data:
                self.app.data_manager.tasks_data[date_str] = {
                    "quadrant_1": [],
                    "quadrant_2": [],
                    "quadrant_3": [],
                    "quadrant_4": []
                }
            
            self.app.data_manager.tasks_data[date_str][dialog.result['quadrant']].append(task_data)
            self.app.data_manager.save_tasks()
            self.load_tasks()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Added task to {dialog.result['quadrant']}: {task_data['text'][:50]}...")
    
    def edit_task(self, quadrant, task_index):
        """Edit an existing task"""
        from ui.task_dialog import TaskEditDialog
        
        tasks = self.app.data_manager.get_tasks_for_date(self.app.current_date)
        
        if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
            current_task = tasks[quadrant][task_index]
            
            dialog = TaskEditDialog(self.app.root, current_task['text'], quadrant)
            self.app.root.wait_window(dialog.dialog)
            
            if dialog.result:
                # Update task text
                current_task['text'] = dialog.result['text']
                current_task['modified_date'] = self.app.current_date.isoformat()
                current_task['modified_time'] = datetime.now().strftime('%H:%M:%S')
                
                # Handle quadrant change
                if dialog.result['quadrant'] != quadrant:
                    date_str = self.app.current_date.isoformat()
                    # Remove from current quadrant
                    self.app.data_manager.tasks_data[date_str][quadrant].pop(task_index)
                    
                    # Add to new quadrant
                    if date_str not in self.app.data_manager.tasks_data:
                        self.app.data_manager.tasks_data[date_str] = {
                            "quadrant_1": [], "quadrant_2": [], "quadrant_3": [], "quadrant_4": []
                        }
                    self.app.data_manager.tasks_data[date_str][dialog.result['quadrant']].append(current_task)
                
                self.app.data_manager.save_tasks()
                self.load_tasks()
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Edited task: {current_task['text'][:50]}...")
    
    def toggle_task_completion(self, quadrant, task_index, completed):
        """Toggle task completion status"""
        tasks = self.app.data_manager.get_tasks_for_date(self.app.current_date)
        
        if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
            date_str = self.app.current_date.isoformat()
            self.app.data_manager.tasks_data[date_str][quadrant][task_index]['completed'] = completed
            
            # Add completion timestamp
            if completed:
                self.app.data_manager.tasks_data[date_str][quadrant][task_index]['completed_date'] = self.app.current_date.isoformat()
                self.app.data_manager.tasks_data[date_str][quadrant][task_index]['completed_time'] = datetime.now().strftime('%H:%M:%S')
            
            self.app.data_manager.save_tasks()
            self.load_tasks()
            
            status = "completed" if completed else "uncompleted"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Task marked as {status}")
    
    def delete_task(self, quadrant, task_index):
        """Delete a task after confirmation"""
        if messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?"):
            tasks = self.app.data_manager.get_tasks_for_date(self.app.current_date)
            
            if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
                date_str = self.app.current_date.isoformat()
                deleted_task = self.app.data_manager.tasks_data[date_str][quadrant].pop(task_index)
                self.app.data_manager.save_tasks()
                self.load_tasks()
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Deleted task: {deleted_task['text'][:50]}...")
    
    def load_tasks(self):
        """Load and display tasks for current date"""
        # Clear existing task widgets
        for quad_id in self.quadrant_frames:
            for widget in self.quadrant_frames[quad_id].winfo_children():
                widget.destroy()
            self.task_listboxes[quad_id] = []
        
        # Load tasks for current date
        tasks = self.app.data_manager.get_tasks_for_date(self.app.current_date)
        
        for quad_id in ['quadrant_1', 'quadrant_2', 'quadrant_3', 'quadrant_4']:
            if quad_id in tasks:
                for i, task_data in enumerate(tasks[quad_id]):
                    widget = self.create_task_widget(
                        self.quadrant_frames[quad_id], 
                        task_data, 
                        quad_id, 
                        i
                    )
                    self.task_listboxes[quad_id].append(widget)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Tasks loaded for {self.app.current_date}")
