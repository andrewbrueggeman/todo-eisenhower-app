import tkinter as tk
import threading
import time


class TimerWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.timer_running = False
        self.timer_paused = False
        self.timer_thread = None

        self.flashing = False
        self.flash_on = False
        self.original_bg = None

        self.timer_run_id = 0
        self.has_started_once = False

        self.duration_options = ["10s", "5", "15", "25", "30", "45", "60"]
        self.default_duration = self._get_default_duration_value()
        self.time_left = self._duration_value_to_seconds(self.default_duration)

        self.setup_timer()

    def _get_default_duration_value(self):
        settings = getattr(self.app.data_manager, "settings_data", {})
        raw_value = settings.get("default_timer_duration", settings.get("timer_last_duration", "25"))
        raw_value = str(raw_value).strip()

        if raw_value in self.duration_options:
            return raw_value

        if raw_value.isdigit() and raw_value in self.duration_options:
            return raw_value

        return "25"

    def _duration_value_to_seconds(self, value):
        if value == "10s":
            return 10
        return int(value) * 60

    def setup_timer(self):
        timer_container = tk.Frame(self.parent, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        timer_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.timer_container = timer_container

        tk.Label(
            timer_container,
            text="⏰ Timer",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(pady=(8, 3))

        self.time_display = tk.Label(
            timer_container,
            text="",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        self.time_display.pack(pady=5)

        duration_frame = tk.Frame(timer_container, bg="#f0f0f0")
        duration_frame.pack(pady=5)

        tk.Label(
            duration_frame,
            text="Duration:",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="black"
        ).pack(side=tk.LEFT, padx=(0, 3))

        self.duration_var = tk.StringVar(value=self.default_duration)
        duration_menu = tk.OptionMenu(
            duration_frame,
            self.duration_var,
            *self.duration_options,
            command=self.change_duration
        )
        duration_menu.config(
            font=("Arial", 9),
            bg="#d9d9d9",
            fg="black",
            activebackground="#c8c8c8",
            activeforeground="black",
            relief=tk.RAISED,
            bd=2,
            highlightthickness=0,
            padx=5
        )
        duration_menu.pack(side=tk.LEFT, padx=2)

        self.duration_unit_label = tk.Label(
            duration_frame,
            text="sec" if self.duration_var.get() == "10s" else "min",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="black"
        )
        self.duration_unit_label.pack(side=tk.LEFT, padx=(2, 0))

        button_frame = tk.Frame(timer_container, bg="#f0f0f0")
        button_frame.pack(pady=8, fill=tk.X, padx=10)

        self.start_button = tk.Button(
            button_frame,
            text="▶ Start",
            command=self.start_timer,
            bg="#145a32",
            fg="white",
            activebackground="#0e3d22",
            activeforeground="white",
            disabledforeground="#d0d0d0",
            font=("Arial", 9, "bold"),
            padx=8,
            pady=4,
            width=8,
            relief=tk.RAISED,
            bd=2,
            highlightthickness=0
        )
        self.start_button.pack(side=tk.LEFT, padx=2, expand=True)

        self.pause_button = tk.Button(
            button_frame,
            text="⏸ Pause",
            command=self.pause_timer,
            bg="#9c640c",
            fg="white",
            activebackground="#7e5109",
            activeforeground="white",
            disabledforeground="#d0d0d0",
            font=("Arial", 9, "bold"),
            padx=8,
            pady=4,
            width=8,
            state=tk.DISABLED,
            relief=tk.RAISED,
            bd=2,
            highlightthickness=0
        )
        self.pause_button.pack(side=tk.LEFT, padx=2, expand=True)

        self.reset_button = tk.Button(
            button_frame,
            text="🔄 Restart",
            command=self.reset_timer,
            bg="#922b21",
            fg="white",
            activebackground="#6e1f18",
            activeforeground="white",
            disabledforeground="#d0d0d0",
            font=("Arial", 9, "bold"),
            padx=8,
            pady=4,
            width=8,
            relief=tk.RAISED,
            bd=2,
            highlightthickness=0
        )
        self.reset_button.pack(side=tk.LEFT, padx=2, expand=True)

        self.status_label = tk.Label(
            timer_container,
            text="Ready to start",
            font=("Arial", 8),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.status_label.pack(pady=(3, 8))

        self.update_display()

    def _duration_to_seconds(self):
        return self._duration_value_to_seconds(self.duration_var.get())

    def start_timer(self):
        if self.flashing:
            return

        if not self.timer_running:
            self.timer_running = True
            self.timer_paused = False
            self.has_started_once = True
            self.timer_run_id += 1
            current_run_id = self.timer_run_id

            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL, text="⏸ Pause")
            self.status_label.config(text="Running...", fg="#27ae60")

            self.timer_thread = threading.Thread(
                target=self._run_timer,
                args=(current_run_id,),
                daemon=True
            )
            self.timer_thread.start()

    def pause_timer(self):
        if self.timer_running:
            self.timer_paused = not self.timer_paused
            if self.timer_paused:
                self.pause_button.config(text="▶ Resume")
                self.status_label.config(text="Paused", fg="#f39c12")
            else:
                self.pause_button.config(text="⏸ Pause")
                self.status_label.config(text="Running...", fg="#27ae60")

    def reset_timer(self):
        self.timer_run_id += 1
        self.timer_running = False
        self.timer_paused = False

        self._stop_flashing()

        selected_duration = self.duration_var.get()
        self.duration_unit_label.config(text="sec" if selected_duration == "10s" else "min")

        self.time_left = self._duration_value_to_seconds(selected_duration)
        self.update_display()

        self.time_display.config(fg="#2c3e50")

        if self.has_started_once:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
            self.status_label.config(text="Restarting...", fg="#3498db")
            self.start_timer()
        else:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
            self.status_label.config(text="Ready to start", fg="#7f8c8d")

    def change_duration(self, value):
        self.duration_unit_label.config(text="sec" if value == "10s" else "min")

        if not self.timer_running and not self.flashing:
            self.time_left = self._duration_value_to_seconds(value)
            if value == "10s":
                self.status_label.config(text="Duration set to 10 seconds", fg="#3498db")
            else:
                self.status_label.config(text=f"Duration set to {value} minutes", fg="#3498db")
            self.update_display()

    def apply_default_duration_from_settings(self):
        if not self.timer_running and not self.flashing:
            default_duration = self._get_default_duration_value()
            self.duration_var.set(default_duration)
            self.duration_unit_label.config(text="sec" if default_duration == "10s" else "min")
            self.time_left = self._duration_value_to_seconds(default_duration)
            self.update_display()
            self.status_label.config(text="Default timer updated", fg="#3498db")

    def _run_timer(self, run_id):
        while self.timer_running and run_id == self.timer_run_id and self.time_left > 0:
            if not self.timer_paused:
                self.time_left -= 1
                self.app.root.after(0, self.update_display)
            time.sleep(1)

        if self.timer_running and run_id == self.timer_run_id and self.time_left <= 0:
            self.app.root.after(0, self._timer_finished)

    def _timer_finished(self):
        self.timer_running = False
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
        self.status_label.config(text="Time's up! Press Restart to begin again.", fg="#e74c3c")

        self.flashing = True
        self.flash_on = False
        self.original_bg = self.app.root.cget("bg")
        self._flash_app()

        self.app.root.bell()

    def _flash_app(self):
        if not self.flashing:
            self._restore_normal_colors()
            return

        if self.flash_on:
            self.app.root.config(bg=self.original_bg)
            self.app.main_frame.config(bg="#f0f0f0")
            self.timer_container.config(bg="#f0f0f0")
            self.time_display.config(fg="#e74c3c", bg="#f0f0f0")
            self.status_label.config(bg="#f0f0f0", fg="#e74c3c")
            self.flash_on = False
        else:
            self.app.root.config(bg="#ff0000")
            self.app.main_frame.config(bg="#ff0000")
            self.timer_container.config(bg="#ff0000")
            self.time_display.config(fg="#ffffff", bg="#ff0000")
            self.status_label.config(bg="#ff0000", fg="#ffffff")
            self.flash_on = True

        self.app.root.after(300, self._flash_app)

    def _restore_normal_colors(self):
        try:
            self.app.root.config(bg=self.original_bg or "#f0f0f0")
        except Exception:
            pass
        try:
            self.app.main_frame.config(bg="#f0f0f0")
        except Exception:
            pass
        try:
            self.timer_container.config(bg="#f0f0f0")
        except Exception:
            pass
        try:
            self.time_display.config(fg="#2c3e50", bg="#f0f0f0")
            self.status_label.config(bg="#f0f0f0", fg="#7f8c8d")
        except Exception:
            pass

    def _stop_flashing(self):
        self.flashing = False
        self.flash_on = False
        self._restore_normal_colors()

    def update_display(self):
        if self.time_left >= 60:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_display.config(text=f"{minutes:02d}:{seconds:02d}")
        else:
            self.time_display.config(text=f"{self.time_left}s")
