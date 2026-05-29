"""
Settings Dialog

Provides configuration options for the application including:
- UI layout customization
- Timer preferences
- System monitoring settings
- Data management options
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import shutil
import json

class SettingsDialog:
    def __init__(self, parent, app):
        self.result = None
        self.parent = parent
        self.app = app
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Application Settings")
        self.dialog.geometry("700x650")  # Increased from 650x600
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        self.dialog.minsize(600, 550)  # Set minimum size
        
        # Center the dialog
        self.center_dialog()
        
        # Configure dialog styling
        self.dialog.configure(bg="#f0f0f0")
        
        # Load current settings
        self.current_settings = self.load_current_settings()
        
        self.setup_dialog()
        
        # Keyboard bindings
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Settings dialog opened")
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 700
        dialog_height = 650
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def load_current_settings(self):
        """Load current application settings"""
        return {
            'layout': self.app.layout_settings.copy(),
            'timer': {
                'default_duration': self.app.data_manager.settings_data.get('timer_last_duration', 25),
                'auto_restart': self.app.data_manager.settings_data.get('auto_restart_timer', True),
                'sound_enabled': self.app.data_manager.settings_data.get('timer_sound_enabled', True)
            },
            'monitoring': {
                'enabled': True,
                'update_interval': self.app.data_manager.settings_data.get('monitor_update_interval', 1)
            },
            'outlook': {
                'sync_enabled': self.app.data_manager.settings_data.get('outlook_sync_enabled', True),
                'sync_days_ahead': self.app.data_manager.settings_data.get('outlook_sync_days', 7)
            }
        }
    
    def setup_dialog(self):
        """Setup dialog UI components"""
        # Main container with padding
        main_frame = tk.Frame(self.dialog, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = tk.Label(main_frame, text="⚙️ Application Settings",
                               font=("Arial", 18, "bold"), 
                               bg="#f0f0f0", fg="#2c3e50")
        header_label.pack(pady=(0, 20))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Setup tabs
        self.setup_layout_tab()
        self.setup_timer_tab()
        
        # Button section - THIS WAS MISSING!
        self.setup_buttons(main_frame)
    def setup_layout_tab(self):
        """Setup UI layout configuration tab"""
        layout_frame = ttk.Frame(self.notebook)
        self.notebook.add(layout_frame, text="🎨 Layout")
        
        content_frame = tk.Frame(layout_frame, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Layout options
        tk.Label(content_frame, text="UI Component Heights", 
                font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(anchor=tk.W, pady=(0, 15))
        
        # Matrix height - Expanded range
        matrix_frame = tk.Frame(content_frame, bg="#f0f0f0")
        matrix_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(matrix_frame, text="Eisenhower Matrix:", 
                font=("Arial", 11), bg="#f0f0f0", width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        self.matrix_height_var = tk.DoubleVar(value=self.current_settings['layout']['matrix_height_ratio'])
        matrix_scale = tk.Scale(matrix_frame, from_=0.3, to=0.9, resolution=0.05,  # Expanded from 0.4-0.8
                               orient=tk.HORIZONTAL, variable=self.matrix_height_var,
                               bg="#f0f0f0", font=("Arial", 9), length=300)  # Made slider longer
        matrix_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.matrix_percent_label = tk.Label(matrix_frame, text="60%", font=("Arial", 9), 
                                            bg="#f0f0f0", fg="#7f8c8d", width=6)
        self.matrix_percent_label.pack(side=tk.RIGHT)
        
        # Update percentage display for matrix
        def update_matrix_percent(*args):
            self.matrix_percent_label.config(text=f"{int(self.matrix_height_var.get() * 100)}%")
        
        self.matrix_height_var.trace('w', update_matrix_percent)
        update_matrix_percent()
        
        # Notes height - Expanded range
        notes_frame = tk.Frame(content_frame, bg="#f0f0f0")
        notes_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(notes_frame, text="Notes Section:", 
                font=("Arial", 11), bg="#f0f0f0", width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        self.notes_height_var = tk.DoubleVar(value=self.current_settings['layout']['notes_height_ratio'])
        notes_scale = tk.Scale(notes_frame, from_=0.05, to=0.5, resolution=0.05,  # Expanded from 0.1-0.4
                              orient=tk.HORIZONTAL, variable=self.notes_height_var,
                              bg="#f0f0f0", font=("Arial", 9), length=300)  # Made slider longer
        notes_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.notes_percent_label = tk.Label(notes_frame, text="20%", font=("Arial", 9), 
                                           bg="#f0f0f0", fg="#7f8c8d", width=6)
        self.notes_percent_label.pack(side=tk.RIGHT)
        
        # Update percentage display for notes
        def update_notes_percent(*args):
            self.notes_percent_label.config(text=f"{int(self.notes_height_var.get() * 100)}%")
        
        self.notes_height_var.trace('w', update_notes_percent)
        update_notes_percent()
        
        # Bottom section height - Expanded range
        bottom_frame = tk.Frame(content_frame, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(bottom_frame, text="Timer/Monitor:", 
                font=("Arial", 11), bg="#f0f0f0", width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        self.bottom_height_var = tk.DoubleVar(value=self.current_settings['layout']['bottom_height_ratio'])
        bottom_scale = tk.Scale(bottom_frame, from_=0.1, to=0.6, resolution=0.05,  # Expanded from 0.1-0.3
                               orient=tk.HORIZONTAL, variable=self.bottom_height_var,
                               bg="#f0f0f0", font=("Arial", 9), length=300)  # Made slider longer
        bottom_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.bottom_percent_label = tk.Label(bottom_frame, text="20%", font=("Arial", 9), 
                                            bg="#f0f0f0", fg="#7f8c8d", width=6)
        self.bottom_percent_label.pack(side=tk.RIGHT)
        
        # Update percentage display for bottom
        def update_bottom_percent(*args):
            self.bottom_percent_label.config(text=f"{int(self.bottom_height_var.get() * 100)}%")
        
        self.bottom_height_var.trace('w', update_bottom_percent)
        update_bottom_percent()
        
        # Reset button
        reset_btn = tk.Button(content_frame, text="🔄 Reset to Default", 
                             command=self.reset_layout_defaults,
                             bg="#3498db", fg="white", font=("Arial", 10),
                             relief=tk.FLAT, padx=15, pady=5)
        reset_btn.pack(pady=15)
        
        # Layout preview info
        info_label = tk.Label(content_frame, 
                             text="💡 Layout changes will take effect after restarting the application.",
                             font=("Arial", 9), bg="#f0f0f0", fg="#7f8c8d", wraplength=500)
        info_label.pack(pady=10)
        
        # Total percentage display
        total_frame = tk.Frame(content_frame, bg="#f0f0f0")
        total_frame.pack(fill=tk.X, pady=10)
        
        self.total_label = tk.Label(total_frame, text="Total: 100%", 
                                   font=("Arial", 11, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.total_label.pack()
        
        # Update total percentage
        def update_total(*args):
            total = (self.matrix_height_var.get() + self.notes_height_var.get() + 
                    self.bottom_height_var.get()) * 100
            color = "#27ae60" if 95 <= total <= 105 else "#e74c3c"
            self.total_label.config(text=f"Total: {total:.0f}%", fg=color)
        
        # Bind all sliders to update total
        self.matrix_height_var.trace('w', update_total)
        self.notes_height_var.trace('w', update_total)
        self.bottom_height_var.trace('w', update_total)
        update_total()
    
    def setup_timer_tab(self):
        """Setup timer configuration tab"""
        timer_frame = ttk.Frame(self.notebook)
        self.notebook.add(timer_frame, text="⏱️ Timer")
        
        content_frame = tk.Frame(timer_frame, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Default timer duration
        tk.Label(content_frame, text="Timer Preferences", 
                font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(anchor=tk.W, pady=(0, 15))
        
        duration_frame = tk.Frame(content_frame, bg="#f0f0f0")
        duration_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(duration_frame, text="Default Duration (minutes):", 
                font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT)
        
        self.timer_duration_var = tk.IntVar(value=self.current_settings['timer']['default_duration'])
        duration_spinbox = tk.Spinbox(duration_frame, from_=1, to=120, 
                                     textvariable=self.timer_duration_var,
                                     font=("Arial", 11), width=10)
        duration_spinbox.pack(side=tk.RIGHT)
        
        # Auto-restart option
        self.auto_restart_var = tk.BooleanVar(value=self.current_settings['timer']['auto_restart'])
        auto_restart_cb = tk.Checkbutton(content_frame, text="Auto-restart timer after completion",
                                        variable=self.auto_restart_var, font=("Arial", 11),
                                        bg="#f0f0f0", activebackground="#f0f0f0")
        auto_restart_cb.pack(anchor=tk.W, pady=10)
        
        # Sound notification option
        self.sound_enabled_var = tk.BooleanVar(value=self.current_settings['timer']['sound_enabled'])
        sound_cb = tk.Checkbutton(content_frame, text="Enable sound notifications",
                                 variable=self.sound_enabled_var, font=("Arial", 11),
                                 bg="#f0f0f0", activebackground="#f0f0f0")
        sound_cb.pack(anchor=tk.W, pady=5)
    def setup_buttons(self, parent):
        """Setup dialog action buttons"""
        button_frame = tk.Frame(parent, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", 
                              command=self.cancel,
                              bg="#95a5a6", fg="white", font=("Arial", 11, "bold"),
                              relief=tk.FLAT, padx=20, pady=8)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Apply button
        apply_btn = tk.Button(button_frame, text="✅ Apply Settings", 
                             command=self.apply_settings,
                             bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                             relief=tk.FLAT, padx=20, pady=8)
        apply_btn.pack(side=tk.RIGHT)
    
    def reset_layout_defaults(self):
        """Reset layout settings to defaults"""
        self.matrix_height_var.set(0.6)
        self.notes_height_var.set(0.2)
        self.bottom_height_var.set(0.2)
        messagebox.showinfo("Layout Reset", "Layout settings have been reset to defaults.")
    
    def apply_settings(self):
        """Apply all settings changes"""
        try:
            # Collect all settings
            new_settings = {
                'layout': {
                    'matrix_height_ratio': self.matrix_height_var.get(),
                    'notes_height_ratio': self.notes_height_var.get(),
                    'bottom_height_ratio': self.bottom_height_var.get()
                },
                'timer_last_duration': self.timer_duration_var.get(),
                'auto_restart_timer': self.auto_restart_var.get(),
                'timer_sound_enabled': self.sound_enabled_var.get()
            }
            
            self.result = new_settings
            
            # Update the app's layout settings (for next restart)
            if 'layout' in new_settings:
                self.app.layout_settings.update(new_settings['layout'])
            
            # Save to data manager
            self.app.data_manager.settings_data.update(new_settings)
            self.app.data_manager.save_settings()
            
            messagebox.showinfo("Settings Applied", 
                               "✅ Settings have been saved successfully!\n\n" +
                               "Layout changes will take effect when you restart the application.")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Settings applied successfully")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"❌ Failed to apply settings:\n{str(e)}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error applying settings: {e}")
