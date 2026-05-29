"""
Task Edit Dialog

Provides a popup dialog for creating and editing tasks.
Supports task text editing and quadrant selection.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class TaskEditDialog:
        def __init__(self, parent, task_text="", quadrant="quadrant_1"):
            self.result = None
            self.parent = parent
        
            # Create dialog window
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Task Editor")
            self.dialog.geometry("500x400")  # Increased height from 350 to 400
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.resizable(True, True)  # Make it resizable
        
            # Center the dialog
            self.center_dialog()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 520
        dialog_height = 480
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_dialog(self, task_text, quadrant):
        """Setup dialog UI components"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = tk.Label(main_frame, 
                               text="✏️ Task Editor" if task_text else "➕ New Task",
                               font=("Arial", 16, "bold"), 
                               bg="#f0f0f0", fg="#2c3e50")
        header_label.pack(pady=(0, 20))
        
        # Task text section
        text_section = tk.Frame(main_frame, bg="#f0f0f0")
        text_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(text_section, text="Task Description:", 
                font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#34495e").pack(anchor=tk.W, pady=(0, 8))
        
        # Text entry with frame for better styling
        text_frame = tk.Frame(text_section, bg="white", relief=tk.SUNKEN, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_entry = tk.Text(text_frame, height=6, width=50, wrap=tk.WORD,
                                 font=("Arial", 11), bg="white", fg="#2c3e50",
                                 relief=tk.FLAT, padx=10, pady=8)
        
        text_scrollbar = tk.Scrollbar(text_frame, command=self.text_entry.yview)
        self.text_entry.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert existing text and select all
        if task_text:
            self.text_entry.insert("1.0", task_text)
            self.text_entry.tag_add(tk.SEL, "1.0", tk.END)
        
        # Character counter
        self.char_counter = tk.Label(text_section, text="0 characters", 
                                    font=("Arial", 9), bg="#f0f0f0", fg="#7f8c8d")
        self.char_counter.pack(anchor=tk.E, pady=(5, 0))
        
        # Bind text change event for character counter
        self.text_entry.bind('<KeyRelease>', self.update_char_counter)
        self.update_char_counter()
        
        # Quadrant selection section
        quadrant_section = tk.Frame(main_frame, bg="#f0f0f0")
        quadrant_section.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(quadrant_section, text="Priority Quadrant:", 
                font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#34495e").pack(anchor=tk.W, pady=(0, 10))
        
        # Quadrant selection with better styling
        self.quadrant_var = tk.StringVar(value=quadrant)
        
        quadrants = [
            ("🔥 Q1: Urgent & Important (Do First)", "quadrant_1", "#e74c3c"),
            ("📅 Q2: Important, Not Urgent (Schedule)", "quadrant_2", "#3498db"),
            ("👥 Q3: Urgent, Not Important (Delegate)", "quadrant_3", "#f39c12"),
            ("🗑️ Q4: Not Urgent, Not Important (Eliminate)", "quadrant_4", "#95a5a6")
        ]
        
        for text, value, color in quadrants:
            radio_frame = tk.Frame(quadrant_section, bg="#f0f0f0")
            radio_frame.pack(fill=tk.X, pady=2)
            
            radio = tk.Radiobutton(radio_frame, text=text, variable=self.quadrant_var, 
                                  value=value, font=("Arial", 10), bg="#f0f0f0",
                                  fg=color, selectcolor="white", 
                                  activebackground="#f0f0f0", activeforeground=color)
            radio.pack(anchor=tk.W, padx=10)
        
        # Button section
        button_section = tk.Frame(main_frame, bg="#f0f0f0")
        button_section.pack(fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_section, text="❌ Cancel", 
                              command=self.cancel,
                              bg="#95a5a6", fg="white", font=("Arial", 11, "bold"),
                              relief=tk.FLAT, padx=20, pady=8, cursor="hand2")
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Save button
        save_btn = tk.Button(button_section, text="💾 Save Task", 
                            command=self.save,
                            bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                            relief=tk.FLAT, padx=20, pady=8, cursor="hand2")
        save_btn.pack(side=tk.RIGHT)
        
        # Add hover effects
        self.add_button_hover_effects(save_btn, "#2ecc71", "#27ae60")
        self.add_button_hover_effects(cancel_btn, "#bdc3c7", "#95a5a6")
        
        # Validation label
        self.validation_label = tk.Label(button_section, text="", 
                                        font=("Arial", 9), bg="#f0f0f0")
        self.validation_label.pack(side=tk.LEFT)
    
    def add_button_hover_effects(self, button, hover_color, normal_color):
        """Add hover effects to buttons"""
        def on_enter(e):
            button.config(bg=hover_color)
        
        def on_leave(e):
            button.config(bg=normal_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def update_char_counter(self, event=None):
        """Update character counter"""
        text = self.text_entry.get("1.0", tk.END).strip()
        char_count = len(text)
        
        self.char_counter.config(text=f"{char_count} characters")
        
        # Color coding for length
        if char_count > 200:
            self.char_counter.config(fg="#e74c3c")  # Red for very long
        elif char_count > 100:
            self.char_counter.config(fg="#f39c12")  # Orange for long
        else:
            self.char_counter.config(fg="#7f8c8d")  # Gray for normal
    
    def handle_enter(self, event):
        """Handle Enter key - save if Ctrl+Enter, otherwise just newline"""
        if event.state & 0x4:  # Ctrl key pressed
            self.save()
        # Otherwise, let the text widget handle the Enter key normally
    
    def validate_input(self):
        """Validate user input"""
        text = self.text_entry.get("1.0", tk.END).strip()
        
        if not text:
            self.validation_label.config(text="⚠️ Task description cannot be empty", fg="#e74c3c")
            return False
        
        if len(text) > 500:
            self.validation_label.config(text="⚠️ Task description too long (max 500 characters)", fg="#e74c3c")
            return False
        
        self.validation_label.config(text="")
        return True
    
    def save(self):
        """Save the task"""
        if not self.validate_input():
            return
        
        text = self.text_entry.get("1.0", tk.END).strip()
        
        self.result = {
            'text': text,
            'quadrant': self.quadrant_var.get()
        }
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Task saved: {text[:50]}...")
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.result = None
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Task dialog cancelled")
        self.dialog.destroy()
