import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import messagebox

class SettingsDialog:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Settings")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.center_dialog()
        self.setup_ui()
        
    def center_dialog(self):
        self.dialog.update_idletasks()
        width, height = 650, 700  # Made slightly wider for color picker
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - height) // 2
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Application Settings", font=("Arial", 16, "bold")).pack(anchor=tk.W, pady=(0, 20))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Layout Tab
        layout_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(layout_tab, text="Layout & Visibility")
        self.setup_layout_tab(layout_tab)
        
        # Appearance Tab (NEW!)
        appearance_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(appearance_tab, text="Appearance")
        self.setup_appearance_tab(appearance_tab)
        
        # Timer Tab
        timer_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(timer_tab, text="Timer Settings")
        self.setup_timer_tab(timer_tab)
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(btn_frame, text="Save Settings", command=self.save, 
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8).pack(side=tk.RIGHT, padx=(10, 0))
        tk.Button(btn_frame, text="Cancel", command=self.cancel, 
                  bg="#95a5a6", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8).pack(side=tk.RIGHT)
        
    def setup_layout_tab(self, parent):
        settings = self.app.data_manager.settings_data.get('layout', {})
        
        # Component Visibility
        visibility_frame = tk.LabelFrame(parent, text="Component Visibility", font=("Arial", 12, "bold"), padx=10, pady=10)
        visibility_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.show_timer_var = tk.BooleanVar(value=settings.get('show_timer', True))
        tk.Checkbutton(visibility_frame, text="Show Pomodoro Timer", variable=self.show_timer_var, 
                       font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        
        self.show_notes_var = tk.BooleanVar(value=settings.get('show_notes', True))
        tk.Checkbutton(visibility_frame, text="Show Daily Notes", variable=self.show_notes_var, 
                       font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        
        self.show_monitor_var = tk.BooleanVar(value=settings.get('show_monitor', True))
        tk.Checkbutton(visibility_frame, text="Show System Monitor (CPU/RAM)", variable=self.show_monitor_var, 
                       font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        
        # Layout Positioning
        position_frame = tk.LabelFrame(parent, text="Layout Positioning", font=("Arial", 12, "bold"), padx=10, pady=10)
        position_frame.pack(fill=tk.X, pady=(0, 20))
        
        positions = ["top", "middle", "bottom"]
        
        matrix_frame = tk.Frame(position_frame)
        matrix_frame.pack(fill=tk.X, pady=8)
        tk.Label(matrix_frame, text="Eisenhower Matrix:", width=20, anchor=tk.W, font=("Arial", 11)).pack(side=tk.LEFT)
        self.matrix_pos_var = tk.StringVar(value=settings.get('matrix_position', 'top'))
        ttk.Combobox(matrix_frame, textvariable=self.matrix_pos_var, values=positions, 
                     state="readonly", width=15, font=("Arial", 10)).pack(side=tk.LEFT)
        
        notes_frame = tk.Frame(position_frame)
        notes_frame.pack(fill=tk.X, pady=8)
        tk.Label(notes_frame, text="Daily Notes:", width=20, anchor=tk.W, font=("Arial", 11)).pack(side=tk.LEFT)
        self.notes_pos_var = tk.StringVar(value=settings.get('notes_position', 'middle'))
        ttk.Combobox(notes_frame, textvariable=self.notes_pos_var, values=positions, 
                     state="readonly", width=15, font=("Arial", 10)).pack(side=tk.LEFT)
        
        bottom_frame = tk.Frame(position_frame)
        bottom_frame.pack(fill=tk.X, pady=8)
        tk.Label(bottom_frame, text="Timer & Monitor:", width=20, anchor=tk.W, font=("Arial", 11)).pack(side=tk.LEFT)
        self.bottom_pos_var = tk.StringVar(value=settings.get('bottom_position', 'bottom'))
        ttk.Combobox(bottom_frame, textvariable=self.bottom_pos_var, values=positions, 
                     state="readonly", width=15, font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Note about restart
        note_frame = tk.Frame(parent, bg="#fff3cd", relief=tk.RAISED, bd=1)
        note_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(note_frame, text="⚠️ Layout changes require app restart to take effect", 
                 fg="#856404", bg="#fff3cd", font=("Arial", 10, "italic"), padx=10, pady=8).pack()
    
    def setup_appearance_tab(self, parent):
        """NEW TAB: Appearance settings including button colors"""
        settings = self.app.data_manager.settings_data
        
        # Add Task Button Colors
        button_frame = tk.LabelFrame(parent, text="Add Task Button Colors", font=("Arial", 12, "bold"), padx=10, pady=10)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Current colors
        self.button_bg_color = settings.get('add_task_button_bg', '#4CAF50')  # Default green
        self.button_fg_color = settings.get('add_task_button_fg', 'white')     # Default white
        
        # Background color
        bg_frame = tk.Frame(button_frame)
        bg_frame.pack(fill=tk.X, pady=8)
        tk.Label(bg_frame, text="Background Color:", font=("Arial", 11), width=18, anchor=tk.W).pack(side=tk.LEFT)
        
        self.bg_color_preview = tk.Label(bg_frame, text="  Sample  ", bg=self.button_bg_color, fg=self.button_fg_color, 
                                        font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=10, pady=3)
        self.bg_color_preview.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Button(bg_frame, text="Choose Color", command=self.choose_bg_color, 
                  bg="#3498db", fg="white", font=("Arial", 10), padx=10).pack(side=tk.LEFT, padx=5)
        
        # Text color
        fg_frame = tk.Frame(button_frame)
        fg_frame.pack(fill=tk.X, pady=8)
        tk.Label(fg_frame, text="Text Color:", font=("Arial", 11), width=18, anchor=tk.W).pack(side=tk.LEFT)
        
        self.fg_color_preview = tk.Label(fg_frame, text="  Sample  ", bg=self.button_bg_color, fg=self.button_fg_color, 
                                        font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2, padx=10, pady=3)
        self.fg_color_preview.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Button(fg_frame, text="Choose Color", command=self.choose_fg_color, 
                  bg="#3498db", fg="white", font=("Arial", 10), padx=10).pack(side=tk.LEFT, padx=5)
        
        # Preset color combinations
        presets_frame = tk.LabelFrame(parent, text="Quick Presets", font=("Arial", 12, "bold"), padx=10, pady=10)
        presets_frame.pack(fill=tk.X, pady=(0, 20))
        
        presets = [
            ("Green & White (Default)", "#4CAF50", "white"),
            ("Black & White", "#000000", "white"),
            ("Blue & White", "#2196F3", "white"),
            ("Dark Gray & White", "#424242", "white"),
            ("Red & White", "#f44336", "white"),
            ("Purple & White", "#9C27B0", "white")
        ]
        
        preset_buttons_frame = tk.Frame(presets_frame)
        preset_buttons_frame.pack(fill=tk.X)
        
        for i, (name, bg, fg) in enumerate(presets):
            row = i // 2
            col = i % 2
            
            btn_frame = tk.Frame(preset_buttons_frame)
            if col == 0:
                btn_frame.pack(fill=tk.X, pady=2)
            else:
                btn_frame.pack(fill=tk.X, pady=2)
            
            preset_btn = tk.Button(btn_frame, text=name, command=lambda b=bg, f=fg: self.apply_preset(b, f),
                                  bg=bg, fg=fg, font=("Arial", 10), padx=10, pady=3, width=25)
            if col == 0:
                preset_btn.pack(side=tk.LEFT, padx=(0, 5))
            else:
                preset_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Note
        note_frame = tk.Frame(parent, bg="#e8f5e9", relief=tk.RAISED, bd=1)
        note_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(note_frame, text="💡 Changes take effect immediately when you save settings", 
                 fg="#2e7d32", bg="#e8f5e9", font=("Arial", 10, "italic"), padx=10, pady=8).pack()
        
    def choose_bg_color(self):
        color = colorchooser.askcolor(color=self.button_bg_color, title="Choose Background Color")
        if color[1]:  # color[1] is the hex value
            self.button_bg_color = color[1]
            self.update_color_previews()
    
    def choose_fg_color(self):
        color = colorchooser.askcolor(color=self.button_fg_color, title="Choose Text Color")
        if color[1]:  # color[1] is the hex value
            self.button_fg_color = color[1]
            self.update_color_previews()
    
    def apply_preset(self, bg_color, fg_color):
        self.button_bg_color = bg_color
        self.button_fg_color = fg_color
        self.update_color_previews()
    
    def update_color_previews(self):
        self.bg_color_preview.config(bg=self.button_bg_color, fg=self.button_fg_color)
        self.fg_color_preview.config(bg=self.button_bg_color, fg=self.button_fg_color)
        
    def setup_timer_tab(self, parent):
        settings = self.app.data_manager.settings_data
        
        # Timer Preferences
        timer_frame = tk.LabelFrame(parent, text="Timer Preferences", font=("Arial", 12, "bold"), padx=10, pady=10)
        timer_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Default duration
        duration_frame = tk.Frame(timer_frame)
        duration_frame.pack(fill=tk.X, pady=8)
        tk.Label(duration_frame, text="Default Duration:", font=("Arial", 11)).pack(side=tk.LEFT)
        
        self.default_duration_var = tk.StringVar(value=str(settings.get('timer_last_duration', 25)))
        duration_options = ["5", "15", "25", "30", "45", "60"]
        ttk.Combobox(duration_frame, textvariable=self.default_duration_var, values=duration_options, 
                     state="readonly", width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(duration_frame, text="minutes", font=("Arial", 11)).pack(side=tk.LEFT)
        
        # Auto-restart option
        self.auto_restart_var = tk.BooleanVar(value=settings.get('auto_restart_timer', False))
        tk.Checkbutton(timer_frame, text="Auto-restart timer after completion", 
                       variable=self.auto_restart_var, font=("Arial", 11)).pack(anchor=tk.W, pady=8)
        
        # Alert Settings
        alert_frame = tk.LabelFrame(parent, text="Alert Settings", font=("Arial", 12, "bold"), padx=10, pady=10)
        alert_frame.pack(fill=tk.X)
        
        tk.Label(alert_frame, text="✨ When timer finishes:", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        tk.Label(alert_frame, text="• Entire app window flashes red", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        tk.Label(alert_frame, text="• System beep sound plays", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        tk.Label(alert_frame, text="• Timer display shows completion message", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        
    def save(self):
        positions = [self.matrix_pos_var.get(), self.notes_pos_var.get(), self.bottom_pos_var.get()]
        if len(set(positions)) != 3:
            messagebox.showwarning("Invalid Layout", "Each component must have a unique position (top, middle, bottom).")
            return
            
        self.result = {
            "layout": {
                "show_timer": self.show_timer_var.get(),
                "show_notes": self.show_notes_var.get(),
                "show_monitor": self.show_monitor_var.get(),
                "matrix_position": self.matrix_pos_var.get(),
                "notes_position": self.notes_pos_var.get(),
                "bottom_position": self.bottom_pos_var.get()
            },
            "timer_last_duration": int(self.default_duration_var.get()),
            "auto_restart_timer": self.auto_restart_var.get(),
            # NEW: Button color settings
            "add_task_button_bg": self.button_bg_color,
            "add_task_button_fg": self.button_fg_color
        }
        
        self.app.data_manager.settings_data.update(self.result)
        self.app.data_manager.save_settings()
        
        # Refresh the matrix widget to apply new button colors immediately
        if hasattr(self.app, 'matrix_widget'):
            self.app.matrix_widget.setup_matrix()
            self.app.matrix_widget.load_tasks()
        
        messagebox.showinfo("Settings Saved", "Settings saved successfully!\n\nButton colors have been updated immediately.\nLayout changes will take effect after restarting the application.")
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()
