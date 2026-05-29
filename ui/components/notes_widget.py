"""
Notes Widget

Provides daily notes functionality with auto-save capability.
"""

import tkinter as tk
from datetime import datetime

class NotesWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.setup_notes()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Notes widget initialized")
    
    def setup_notes(self):
        """Setup notes UI"""
        notes_frame = tk.LabelFrame(self.parent, text="Daily Notes", 
                                   font=("Arial", 12, "bold"),
                                   bg="#f0f0f0", padx=10, pady=10)
        notes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notes text area with scrollbar
        text_frame = tk.Frame(notes_frame, bg="#f0f0f0")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notes_text = tk.Text(text_frame, height=6, wrap=tk.WORD,
                                 font=("Arial", 10), bg="white", fg="#2c3e50",
                                 relief=tk.SUNKEN, bd=1, padx=5, pady=5)
        
        notes_scrollbar = tk.Scrollbar(text_frame, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)
        
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Auto-save functionality
        self.notes_text.bind('<KeyRelease>', self.auto_save_notes)
        self.notes_text.bind('<FocusOut>', self.save_notes)
        
        # Status indicator
        self.save_status = tk.Label(notes_frame, text="Ready", 
                                   font=("Arial", 8), bg="#f0f0f0", fg="#7f8c8d")
        self.save_status.pack(anchor=tk.E, pady=2)
        
        # Placeholder text
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder text when notes are empty"""
        if not self.notes_text.get("1.0", tk.END).strip():
            self.notes_text.insert("1.0", "Enter your daily notes here...")
            self.notes_text.config(fg="#bdc3c7")
            self.notes_text.bind('<FocusIn>', self.clear_placeholder)
    
    def clear_placeholder(self, event=None):
        """Clear placeholder text when user starts typing"""
        if self.notes_text.get("1.0", tk.END).strip() == "Enter your daily notes here...":
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.config(fg="#2c3e50")
        self.notes_text.unbind('<FocusIn>')
    
    def auto_save_notes(self, event=None):
        """Auto-save notes with a slight delay"""
        self.save_status.config(text="Typing...", fg="#f39c12")
        
        # Cancel previous auto-save if user is still typing
        if hasattr(self, 'auto_save_job'):
            self.app.root.after_cancel(self.auto_save_job)
        
        # Schedule auto-save after 2 seconds of inactivity
        self.auto_save_job = self.app.root.after(2000, self.save_notes)
    
    def save_notes(self, event=None):
        """Save notes to data manager"""
        notes_content = self.notes_text.get("1.0", tk.END).strip()
        
        # Don't save placeholder text
        if notes_content == "Enter your daily notes here...":
            notes_content = ""
        
        date_str = self.app.current_date.isoformat()
        self.app.data_manager.notes_data[date_str] = notes_content
        self.app.data_manager.save_notes()
        
        self.save_status.config(text="Saved ✓", fg="#27ae60")
        
        # Reset status after 2 seconds
        self.app.root.after(2000, lambda: self.save_status.config(text="Ready", fg="#7f8c8d"))
    
    def load_notes(self):
        """Load notes for current date"""
        notes = self.app.data_manager.get_notes_for_date(self.app.current_date)
        
        self.notes_text.delete("1.0", tk.END)
        
        if notes:
            self.notes_text.insert("1.0", notes)
            self.notes_text.config(fg="#2c3e50")
        else:
            self.show_placeholder()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Notes loaded for {self.app.current_date}")
