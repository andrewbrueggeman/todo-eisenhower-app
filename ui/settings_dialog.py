import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import messagebox


class SettingsDialog:
    DEFAULT_QUADRANT_NAMES = {
        "quadrant_1": "Critical Actions",
        "quadrant_2": "Strategic Work",
        "quadrant_3": "Routine Tasks",
        "quadrant_4": "Backlog/Opportunities"
    }

    def _cleanup_mousewheel(self):
        try:
            self.dialog.unbind_all("<MouseWheel>")
            self.dialog.unbind_all("<Button-4>")
            self.dialog.unbind_all("<Button-5>")
        except Exception:
            pass

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.result = None
        self._settings_canvas = None
        self.quadrant_name_vars = {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Settings")
        self.dialog.resizable(True, True)

        self.center_dialog()
        self.dialog.update_idletasks()

        self.dialog.lift(aboveThis=parent)
        self.dialog.focus_force()
        self.dialog.attributes("-topmost", True)

        self.dialog.grab_set()

        self.setup_ui()

    def center_dialog(self):
        self.dialog.update_idletasks()

        width, height = 720, 820
        x = self.parent.winfo_rootx() + (
            self.parent.winfo_width() - width
        ) // 2
        y = self.parent.winfo_rooty() + (
            self.parent.winfo_height() - height
        ) // 2

        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        self.dialog.minsize(680, 700)

    def setup_ui(self):
        container = tk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        def resize_scroll_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_scroll_frame)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._bind_mousewheel(canvas)

        main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main_frame,
            text="Application Settings",
            font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        layout_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(layout_tab, text="Layout & Visibility")
        self.setup_layout_tab(layout_tab)

        appearance_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(appearance_tab, text="Appearance")
        self.setup_appearance_tab(appearance_tab)

        timer_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(timer_tab, text="Timer Settings")
        self.setup_timer_tab(timer_tab)

        quadrant_names_tab = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(quadrant_names_tab, text="Quadrant Names")
        self.setup_quadrant_names_tab(quadrant_names_tab)

        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(
            btn_frame,
            text="Save Settings",
            command=self.save,
            bg="#4CAF50",
            fg="black",
            activeforeground="black",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=(10, 0))

        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            bg="#95a5a6",
            fg="black",
            activeforeground="black",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)

    def _bind_mousewheel(self, canvas):
        self._settings_canvas = canvas

        def on_enter(event):
            self.dialog.bind_all(
                "<MouseWheel>",
                self._on_mousewheel
            )
            self.dialog.bind_all(
                "<Button-4>",
                self._on_mousewheel_linux_up
            )
            self.dialog.bind_all(
                "<Button-5>",
                self._on_mousewheel_linux_down
            )

        def on_leave(event):
            self.dialog.unbind_all("<MouseWheel>")
            self.dialog.unbind_all("<Button-4>")
            self.dialog.unbind_all("<Button-5>")

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

    def _on_mousewheel(self, event):
        if self._settings_canvas is None:
            return

        delta = event.delta

        if delta == 0:
            return

        if abs(delta) < 120:
            step = -1 if delta > 0 else 1
        else:
            step = int(-1 * (delta / 120))

        self._settings_canvas.yview_scroll(step, "units")

    def _on_mousewheel_linux_up(self, event):
        if self._settings_canvas is not None:
            self._settings_canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        if self._settings_canvas is not None:
            self._settings_canvas.yview_scroll(1, "units")

    def setup_layout_tab(self, parent):
        layout_settings = self.app.data_manager.settings_data.get(
            "layout",
            {}
        )

        visibility_frame = tk.LabelFrame(
            parent,
            text="Component Visibility",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        visibility_frame.pack(fill=tk.X, pady=(0, 20))

        self.show_timer_var = tk.BooleanVar(
            value=layout_settings.get("show_timer", True)
        )
        tk.Checkbutton(
            visibility_frame,
            text="Show Pomodoro Timer",
            variable=self.show_timer_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, pady=3)

        self.show_notes_var = tk.BooleanVar(
            value=layout_settings.get("show_notes", True)
        )
        tk.Checkbutton(
            visibility_frame,
            text="Show Daily Notes",
            variable=self.show_notes_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, pady=3)

        self.show_monitor_var = tk.BooleanVar(
            value=layout_settings.get("show_monitor", True)
        )
        tk.Checkbutton(
            visibility_frame,
            text="Show System Monitor (CPU/RAM)",
            variable=self.show_monitor_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, pady=3)

        view_frame = tk.LabelFrame(
            parent,
            text="Matrix View",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        view_frame.pack(fill=tk.X, pady=(0, 20))

        row = tk.Frame(view_frame)
        row.pack(fill=tk.X, pady=8)

        tk.Label(
            row,
            text="Display Range:",
            width=20,
            anchor=tk.W,
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.matrix_view_mode_var = tk.StringVar(
            value=self.app.data_manager.settings_data.get(
                "matrix_view_mode",
                "1_day"
            )
        )

        ttk.Combobox(
            row,
            textvariable=self.matrix_view_mode_var,
            values=["1_day", "2_day", "1_week"],
            state="readonly",
            width=15,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        tk.Label(
            view_frame,
            text=(
                "1_day = Today only | 2_day = Today + Tomorrow | "
                "1_week = Today + next 6 days"
            ),
            font=("Arial", 10, "italic"),
            fg="#555555"
        ).pack(anchor=tk.W, pady=(4, 0))

        position_frame = tk.LabelFrame(
            parent,
            text="Layout Positioning",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        position_frame.pack(fill=tk.X, pady=(0, 20))

        positions = ["top", "middle", "bottom"]

        matrix_frame = tk.Frame(position_frame)
        matrix_frame.pack(fill=tk.X, pady=8)

        tk.Label(
            matrix_frame,
            text="Eisenhower Matrix:",
            width=20,
            anchor=tk.W,
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.matrix_pos_var = tk.StringVar(
            value=layout_settings.get("matrix_position", "top")
        )

        ttk.Combobox(
            matrix_frame,
            textvariable=self.matrix_pos_var,
            values=positions,
            state="readonly",
            width=15,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        notes_frame = tk.Frame(position_frame)
        notes_frame.pack(fill=tk.X, pady=8)

        tk.Label(
            notes_frame,
            text="Daily Notes:",
            width=20,
            anchor=tk.W,
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.notes_pos_var = tk.StringVar(
            value=layout_settings.get("notes_position", "middle")
        )

        ttk.Combobox(
            notes_frame,
            textvariable=self.notes_pos_var,
            values=positions,
            state="readonly",
            width=15,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        bottom_frame = tk.Frame(position_frame)
        bottom_frame.pack(fill=tk.X, pady=8)

        tk.Label(
            bottom_frame,
            text="Timer & Monitor:",
            width=20,
            anchor=tk.W,
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.bottom_pos_var = tk.StringVar(
            value=layout_settings.get("bottom_position", "bottom")
        )

        ttk.Combobox(
            bottom_frame,
            textvariable=self.bottom_pos_var,
            values=positions,
            state="readonly",
            width=15,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        note_frame = tk.Frame(
            parent,
            bg="#fff3cd",
            relief=tk.RAISED,
            bd=1
        )
        note_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            note_frame,
            text="⚠️ Layout changes require app restart to take effect",
            fg="#856404",
            bg="#fff3cd",
            font=("Arial", 10, "italic"),
            padx=10,
            pady=8
        ).pack()

    def setup_appearance_tab(self, parent):
        settings = self.app.data_manager.settings_data

        button_frame = tk.LabelFrame(
            parent,
            text="Add Task Button Colors",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        button_frame.pack(fill=tk.X, pady=(0, 20))

        self.button_bg_color = settings.get(
            "add_task_button_bg",
            "#4CAF50"
        )
        self.button_fg_color = settings.get(
            "add_task_button_fg",
            "black"
        )

        bg_frame = tk.Frame(button_frame)
        bg_frame.pack(fill=tk.X, pady=8)

        tk.Label(
            bg_frame,
            text="Background Color:",
            font=("Arial", 11),
            width=18,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.bg_color_preview = tk.Label(
            bg_frame,
            text="  Sample  ",
            bg=self.button_bg_color,
            fg=self.button_fg_color,
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=3
        )
        self.bg_color_preview.pack(side=tk.LEFT, padx=(10, 5))

        tk.Button(
            bg_frame,
            text="Choose Color",
            command=self.choose_bg_color,
            bg="#3498db",
            fg="black",
            activeforeground="black",
            font=("Arial", 10),
            padx=10
        ).pack(side=tk.LEFT, padx=5)

        fg_frame = tk.Frame(button_frame)
        fg_frame.pack(fill=tk.X, pady=8)

        tk.Label(
            fg_frame,
            text="Text Color:",
            font=("Arial", 11),
            width=18,
            anchor=tk.W
        ).pack(side=tk.LEFT)

        self.fg_color_preview = tk.Label(
            fg_frame,
            text="  Sample  ",
            bg=self.button_bg_color,
            fg=self.button_fg_color,
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=3
        )
        self.fg_color_preview.pack(side=tk.LEFT, padx=(10, 5))

        tk.Button(
            fg_frame,
            text="Choose Color",
            command=self.choose_fg_color,
            bg="#3498db",
            fg="black",
            activeforeground="black",
            font=("Arial", 10),
            padx=10
        ).pack(side=tk.LEFT, padx=5)

        presets_frame = tk.LabelFrame(
            parent,
            text="Quick Presets",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        presets_frame.pack(fill=tk.X, pady=(0, 20))

        presets = [
            ("Green & Black (Default)", "#4CAF50", "black"),
            ("Black & White", "#000000", "white"),
            ("Blue & Black", "#2196F3", "black"),
            ("Dark Gray & White", "#424242", "white"),
            ("Red & Black", "#f44336", "black"),
            ("Purple & Black", "#9C27B0", "black")
        ]

        preset_buttons_frame = tk.Frame(presets_frame)
        preset_buttons_frame.pack(fill=tk.X)

        for name, bg, fg in presets:
            preset_btn = tk.Button(
                preset_buttons_frame,
                text=name,
                command=lambda b=bg, f=fg: self.apply_preset(b, f),
                bg=bg,
                fg=fg,
                font=("Arial", 10),
                padx=10,
                pady=3,
                width=25
            )
            preset_btn.pack(anchor=tk.W, pady=2)

        note_frame = tk.Frame(
            parent,
            bg="#e8f5e9",
            relief=tk.RAISED,
            bd=1
        )
        note_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            note_frame,
            text="💡 Changes take effect immediately when you save settings",
            fg="#2e7d32",
            bg="#e8f5e9",
            font=("Arial", 10, "italic"),
            padx=10,
            pady=8
        ).pack()

    def choose_bg_color(self):
        color = colorchooser.askcolor(
            color=self.button_bg_color,
            title="Choose Background Color"
        )

        if color[1]:
            self.button_bg_color = color[1]
            self.update_color_previews()

    def choose_fg_color(self):
        color = colorchooser.askcolor(
            color=self.button_fg_color,
            title="Choose Text Color"
        )

        if color[1]:
            self.button_fg_color = color[1]
            self.update_color_previews()

    def apply_preset(self, bg_color, fg_color):
        self.button_bg_color = bg_color
        self.button_fg_color = fg_color
        self.update_color_previews()

    def update_color_previews(self):
        self.bg_color_preview.config(
            bg=self.button_bg_color,
            fg=self.button_fg_color
        )
        self.fg_color_preview.config(
            bg=self.button_bg_color,
            fg=self.button_fg_color
        )

    def setup_timer_tab(self, parent):
        settings = self.app.data_manager.settings_data

        timer_frame = tk.LabelFrame(
            parent,
            text="Timer Preferences",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        timer_frame.pack(fill=tk.X, pady=(0, 20))

        duration_frame = tk.Frame(timer_frame)
        duration_frame.pack(fill=tk.X, pady=8)

        tk.Label(
            duration_frame,
            text="Default Duration:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.default_duration_var = tk.StringVar(
            value=str(
                settings.get(
                    "default_timer_duration",
                    settings.get("timer_last_duration", "25")
                )
            )
        )

        duration_options = ["10s", "5", "15", "25", "30", "45", "60"]

        ttk.Combobox(
            duration_frame,
            textvariable=self.default_duration_var,
            values=duration_options,
            state="readonly",
            width=10,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(10, 5))

        tk.Label(
            duration_frame,
            text="(used when the timer loads or is reset)",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.auto_restart_var = tk.BooleanVar(
            value=settings.get("auto_restart_timer", False)
        )

        tk.Checkbutton(
            timer_frame,
            text="Auto-restart timer after completion",
            variable=self.auto_restart_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, pady=8)

        alert_frame = tk.LabelFrame(
            parent,
            text="Alert Settings",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        alert_frame.pack(fill=tk.X)

        tk.Label(
            alert_frame,
            text="✨ When timer finishes:",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))

        tk.Label(
            alert_frame,
            text="• Entire app window flashes red",
            font=("Arial", 10)
        ).pack(anchor=tk.W, padx=20)

        tk.Label(
            alert_frame,
            text="• System beep sound plays",
            font=("Arial", 10)
        ).pack(anchor=tk.W, padx=20)

        tk.Label(
            alert_frame,
            text="• Timer display shows completion message",
            font=("Arial", 10)
        ).pack(anchor=tk.W, padx=20)

    def setup_quadrant_names_tab(self, parent):
        settings = self.app.data_manager.settings_data
        saved_names = settings.get("quadrant_names", {})

        if not isinstance(saved_names, dict):
            saved_names = {}

        names_frame = tk.LabelFrame(
            parent,
            text="Quadrant Display Names",
            font=("Arial", 12, "bold"),
            padx=12,
            pady=12
        )
        names_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            names_frame,
            text=(
                "These names appear in the matrix, task dialog, and "
                "Move To menu. Task assignments will not be changed."
            ),
            font=("Arial", 10, "italic"),
            fg="#555555",
            justify=tk.LEFT,
            wraplength=590
        ).pack(anchor=tk.W, pady=(0, 15))

        quadrant_rows = [
            ("Q1", "quadrant_1"),
            ("Q2", "quadrant_2"),
            ("Q3", "quadrant_3"),
            ("Q4", "quadrant_4")
        ]

        for quadrant_number, quadrant_id in quadrant_rows:
            row = tk.Frame(names_frame)
            row.pack(fill=tk.X, pady=6)

            tk.Label(
                row,
                text=f"{quadrant_number}:",
                width=5,
                anchor=tk.W,
                font=("Arial", 11, "bold")
            ).pack(side=tk.LEFT)

            default_name = self.DEFAULT_QUADRANT_NAMES[quadrant_id]
            current_name = saved_names.get(quadrant_id, default_name)

            if not isinstance(current_name, str) or not current_name.strip():
                current_name = default_name

            self.quadrant_name_vars[quadrant_id] = tk.StringVar(
                value=current_name.strip()
            )

            tk.Entry(
                row,
                textvariable=self.quadrant_name_vars[quadrant_id],
                font=("Arial", 11),
                width=42
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            parent,
            text="Restore Default Names",
            command=self.restore_default_quadrant_names,
            bg="#d5dbdb",
            fg="black",
            activeforeground="black",
            font=("Arial", 10),
            padx=12,
            pady=5
        ).pack(anchor=tk.W)

        note_frame = tk.Frame(
            parent,
            bg="#e8f5e9",
            relief=tk.RAISED,
            bd=1
        )
        note_frame.pack(fill=tk.X, pady=(18, 0))

        tk.Label(
            note_frame,
            text=(
                "Changes take effect immediately after saving. "
                "Existing tasks remain assigned to their current quadrants."
            ),
            fg="#2e7d32",
            bg="#e8f5e9",
            font=("Arial", 10, "italic"),
            padx=10,
            pady=8,
            justify=tk.LEFT,
            wraplength=590
        ).pack(anchor=tk.W)

    def restore_default_quadrant_names(self):
        for quadrant_id, default_name in self.DEFAULT_QUADRANT_NAMES.items():
            if quadrant_id in self.quadrant_name_vars:
                self.quadrant_name_vars[quadrant_id].set(default_name)

    def save(self):
        positions = [
            self.matrix_pos_var.get(),
            self.notes_pos_var.get(),
            self.bottom_pos_var.get()
        ]

        if len(set(positions)) != 3:
            messagebox.showwarning(
                "Invalid Layout",
                "Each component must have a unique position "
                "(top, middle, bottom)."
            )
            return

        quadrant_names = {}

        for quadrant_id, name_var in self.quadrant_name_vars.items():
            name = name_var.get().strip()

            if not name:
                messagebox.showwarning(
                    "Invalid Quadrant Name",
                    "Each quadrant must have a name. Please enter a name "
                    "for every quadrant."
                )
                return

            quadrant_names[quadrant_id] = name

        selected_default_duration = self.default_duration_var.get()

        self.result = {
            "layout": {
                "show_timer": self.show_timer_var.get(),
                "show_notes": self.show_notes_var.get(),
                "show_monitor": self.show_monitor_var.get(),
                "matrix_position": self.matrix_pos_var.get(),
                "notes_position": self.notes_pos_var.get(),
                "bottom_position": self.bottom_pos_var.get()
            },
            "matrix_view_mode": self.matrix_view_mode_var.get(),
            "quadrant_names": quadrant_names,
            "default_timer_duration": selected_default_duration,
            "timer_last_duration": selected_default_duration,
            "auto_restart_timer": self.auto_restart_var.get(),
            "add_task_button_bg": self.button_bg_color,
            "add_task_button_fg": self.button_fg_color
        }

        self.app.data_manager.settings_data.update(self.result)
        self.app.data_manager.save_settings()

        if hasattr(self.app, "timer_widget"):
            self.app.timer_widget.apply_default_duration_from_settings()

        if hasattr(self.app, "matrix_widget"):
            self.app.refresh_data()

        messagebox.showinfo(
            "Settings Saved",
            "Settings saved successfully!\n\n"
            "Quadrant names, timer default, matrix view, and button colors "
            "have been updated.\n"
            "Layout position changes will take effect after restarting "
            "the application."
        )

        self._cleanup_mousewheel()

        try:
            self.dialog.attributes("-topmost", False)
        except Exception:
            pass

        self.dialog.destroy()

    def cancel(self):
        self._cleanup_mousewheel()

        try:
            self.dialog.attributes("-topmost", False)
        except Exception:
            pass

        self.dialog.destroy()
