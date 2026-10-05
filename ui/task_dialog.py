import tkinter as tk
from datetime import datetime, date, timedelta
import calendar


class CalendarWidget:
    def __init__(self, parent, selected_date=None, on_date_change=None):
        self.parent = parent
        self.selected_date = selected_date or date.today()
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year
        self.on_date_change = on_date_change
        self.day_buttons = {}
        self.calendar_obj = calendar.Calendar(firstweekday=6)
        self.setup_calendar()

    def setup_calendar(self):
        self.outer_frame = tk.Frame(self.parent, bg="#f0f0f0")
        self.outer_frame.pack(fill=tk.X, expand=False)

        header_frame = tk.Frame(
            self.outer_frame,
            bg="#d6eaf8",
            relief=tk.GROOVE,
            bd=1
        )
        header_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Button(
            header_frame,
            text="◀",
            command=self.prev_month,
            bg="#d6eaf8",
            fg="black",
            activebackground="#c6dbef",
            activeforeground="black",
            relief=tk.FLAT,
            font=("Arial", 10, "bold"),
            padx=8,
            pady=3
        ).pack(side=tk.LEFT, padx=4, pady=4)

        self.month_label = tk.Label(
            header_frame,
            text="",
            bg="#d6eaf8",
            fg="black",
            font=("Arial", 11, "bold")
        )
        self.month_label.pack(side=tk.LEFT, expand=True)

        tk.Button(
            header_frame,
            text="▶",
            command=self.next_month,
            bg="#d6eaf8",
            fg="black",
            activebackground="#c6dbef",
            activeforeground="black",
            relief=tk.FLAT,
            font=("Arial", 10, "bold"),
            padx=8,
            pady=3
        ).pack(side=tk.RIGHT, padx=4, pady=4)

        days_frame = tk.Frame(self.outer_frame, bg="#dfe6e9")
        days_frame.pack(fill=tk.X)

        for i, day_name in enumerate(
            ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        ):
            lbl = tk.Label(
                days_frame,
                text=day_name,
                bg="#dfe6e9",
                fg="black",
                font=("Arial", 8, "bold"),
                width=4
            )
            lbl.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
            days_frame.grid_columnconfigure(i, weight=1)

        self.grid_frame = tk.Frame(self.outer_frame, bg="#f0f0f0")
        self.grid_frame.pack(fill=tk.X, expand=False)

        self.update_calendar()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.update_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.update_calendar()

    def update_calendar(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.day_buttons = {}
        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        cal = self.calendar_obj.monthdayscalendar(
            self.current_year,
            self.current_month
        )
        today = date.today()

        for row_idx, week in enumerate(cal):
            for col_idx, day_num in enumerate(week):
                self.grid_frame.grid_columnconfigure(col_idx, weight=1)

                if day_num == 0:
                    lbl = tk.Label(
                        self.grid_frame,
                        text="",
                        bg="#f7f7f7",
                        width=4,
                        height=1
                    )
                    lbl.grid(
                        row=row_idx,
                        column=col_idx,
                        padx=1,
                        pady=1,
                        sticky="nsew"
                    )
                    continue

                day_date = date(
                    self.current_year,
                    self.current_month,
                    day_num
                )

                bg = "white"
                fg = "black"
                relief = tk.RAISED
                border = 1

                if day_date == today:
                    bg = "#fdeaa7"

                if day_date == self.selected_date:
                    bg = "#1f5fa8"
                    fg = "white"
                    relief = tk.SUNKEN
                    border = 3

                btn = tk.Button(
                    self.grid_frame,
                    text=str(day_num),
                    bg=bg,
                    fg=fg,
                    activebackground="#1f5fa8",
                    activeforeground="white",
                    relief=relief,
                    bd=border,
                    highlightthickness=0,
                    font=("Arial", 9, "bold"),
                    command=lambda d=day_date: self.select_date(d)
                )
                btn.grid(
                    row=row_idx,
                    column=col_idx,
                    padx=1,
                    pady=1,
                    sticky="nsew",
                    ipadx=3,
                    ipady=4
                )

                self.day_buttons[day_date] = btn

    def select_date(self, new_date):
        self.selected_date = new_date
        self.current_month = new_date.month
        self.current_year = new_date.year
        self.update_calendar()

        if self.on_date_change:
            self.on_date_change(new_date)

    def get_selected_date(self):
        return self.selected_date


class TaskDialog:
    DEFAULT_QUADRANT_NAMES = {
        "quadrant_1": "Critical Actions",
        "quadrant_2": "Strategic Work",
        "quadrant_3": "Routine Tasks",
        "quadrant_4": "Backlog/Opportunities"
    }

    def __init__(self, parent, task_data=None, current_date=None, mode="add"):
        self.parent = parent
        self.result = None
        self.task_data = task_data.copy() if task_data else {}
        self.current_date = self._coerce_date(current_date) or date.today()
        self.mode = mode

        self.quick_buttons = {}
        self.quick_dates = {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.resizable(True, True)
        self.dialog.minsize(640, 700)
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.mode == "copy":
            title = "Copy Task"
        elif self.mode == "move":
            title = "Move Task"
        elif self.mode == "edit":
            title = "Edit Task"
        else:
            title = "Add Task"

        self.dialog.title(title)

        self.center_dialog()
        self.dialog.update_idletasks()

        self.dialog.lift(aboveThis=parent)
        self.dialog.focus_force()
        self.dialog.attributes("-topmost", True)
        self.dialog.grab_set()

        self.setup_dialog()

        self.dialog.bind("<Escape>", lambda e: self.cancel())
        self.dialog.bind_all("<Control-Return>", lambda e: self.save())
        self.dialog.after(150, self._safe_focus_text)

    def _coerce_date(self, value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        return None

    def _safe_focus_text(self):
        try:
            if self.dialog.winfo_exists():
                self.text_entry.focus_set()
        except Exception:
            pass

    def center_dialog(self):
        self.dialog.update_idletasks()

        width, height = 640, 700
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = max(self.parent.winfo_width(), 800)
        ph = max(self.parent.winfo_height(), 700)

        x = px + (pw - width) // 2
        y = py + (ph - height) // 2

        if y < 28:
            y = 28

        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _normalize_wheel_step(self, delta):
        if delta == 0:
            return 0

        if abs(delta) < 120:
            step = -1 if delta > 0 else 1
        else:
            step = int(-1 * (delta / 120))

        if step == 0:
            step = -1 if delta > 0 else 1

        return step

    def _scroll_canvas(self, step):
        self.canvas.yview_scroll(step, "units")

    def _scroll_text_or_canvas(self, widget, step):
        try:
            first, last = widget.yview()

            if (last - first) < 1.0:
                widget.yview_scroll(step, "units")
            else:
                self._scroll_canvas(step)

        except Exception:
            self._scroll_canvas(step)

    def _on_canvas_mousewheel(self, event):
        step = self._normalize_wheel_step(event.delta)

        if step != 0:
            self._scroll_canvas(step)

        return "break"

    def _on_canvas_linux_scroll_up(self, event):
        self._scroll_canvas(-1)
        return "break"

    def _on_canvas_linux_scroll_down(self, event):
        self._scroll_canvas(1)
        return "break"

    def _on_text_mousewheel(self, event):
        step = self._normalize_wheel_step(event.delta)

        if step != 0:
            self._scroll_text_or_canvas(event.widget, step)

        return "break"

    def _on_text_linux_scroll_up(self, event):
        self._scroll_text_or_canvas(event.widget, -1)
        return "break"

    def _on_text_linux_scroll_down(self, event):
        self._scroll_text_or_canvas(event.widget, 1)
        return "break"

    def _bind_mousewheel_recursive(self, widget):
        try:
            if not widget.winfo_exists():
                return
        except Exception:
            return

        widget_class = widget.winfo_class()

        if widget_class == "Text":
            widget.bind("<MouseWheel>", self._on_text_mousewheel)
            widget.bind("<Button-4>", self._on_text_linux_scroll_up)
            widget.bind("<Button-5>", self._on_text_linux_scroll_down)
        else:
            widget.bind("<MouseWheel>", self._on_canvas_mousewheel)
            widget.bind("<Button-4>", self._on_canvas_linux_scroll_up)
            widget.bind("<Button-5>", self._on_canvas_linux_scroll_down)

        for child in widget.winfo_children():
            try:
                if child.winfo_exists():
                    self._bind_mousewheel_recursive(child)
            except Exception:
                pass

    def setup_dialog(self):
        outer = tk.Frame(self.dialog, bg="#f0f0f0")
        outer.pack(fill=tk.BOTH, expand=True)

        title_frame = tk.Frame(outer, bg="#f0f0f0")
        title_frame.pack(fill=tk.X, padx=18, pady=18)

        tk.Label(
            title_frame,
            text=self.dialog.title(),
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(anchor=tk.W)

        content_container = tk.Frame(outer, bg="#f0f0f0")
        content_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=18,
            pady=(0, 0)
        )

        self.canvas = tk.Canvas(
            content_container,
            bg="#f0f0f0",
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            content_container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        def resize_inner(event):
            self.canvas.itemconfig(self.window_id, width=event.width)

        self.canvas.bind("<Configure>", resize_inner)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._build_form(self.scrollable_frame)

        self.dialog.after(
            100,
            lambda: self._bind_mousewheel_recursive(self.dialog)
        )

        bottom = tk.Frame(outer, bg="#f0f0f0")
        bottom.pack(fill=tk.X, padx=18, pady=14)

        sep = tk.Frame(bottom, height=1, bg="#d0d0d0")
        sep.pack(fill=tk.X, pady=(0, 10))

        btn_row = tk.Frame(bottom, bg="#f0f0f0")
        btn_row.pack(fill=tk.X)

        save_text = "Save Task"

        if self.mode == "move":
            save_text = "Move Task"
        elif self.mode == "copy":
            save_text = "Copy Task"

        tk.Button(
            btn_row,
            text="Cancel",
            command=self.cancel,
            bg="#d5dbdb",
            fg="black",
            activebackground="#cfd4d4",
            activeforeground="black",
            font=("Arial", 11, "bold"),
            padx=18,
            pady=7
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_row,
            text=save_text,
            command=self.save,
            bg="#a9dfbf",
            fg="black",
            activebackground="#97d7b0",
            activeforeground="black",
            font=("Arial", 11, "bold"),
            padx=18,
            pady=7
        ).pack(side=tk.RIGHT, padx=(0, 10))

        tk.Label(
            bottom,
            text="Tip: Press Ctrl+Enter to save",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        ).pack(anchor=tk.E, pady=(6, 0))

    def _get_quadrant_display_names(self):
        quadrant_names = self.DEFAULT_QUADRANT_NAMES.copy()

        app = getattr(self.parent, "eisenhower_app", None)

        if app is None or not hasattr(app, "data_manager"):
            return quadrant_names

        saved_names = app.data_manager.settings_data.get(
            "quadrant_names",
            {}
        )

        if not isinstance(saved_names, dict):
            return quadrant_names

        for quadrant_id, default_name in self.DEFAULT_QUADRANT_NAMES.items():
            saved_name = saved_names.get(quadrant_id)

            if isinstance(saved_name, str) and saved_name.strip():
                quadrant_names[quadrant_id] = saved_name.strip()
            else:
                quadrant_names[quadrant_id] = default_name

        return quadrant_names

    def _build_form(self, parent):
        tk.Label(
            parent,
            text="Task Description *",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(anchor=tk.W)

        text_frame = tk.Frame(
            parent,
            bg="white",
            relief=tk.SUNKEN,
            bd=1
        )
        text_frame.pack(fill=tk.X, pady=(5, 8))

        self.text_entry = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=4
        )
        text_scrollbar = tk.Scrollbar(
            text_frame,
            command=self.text_entry.yview
        )
        self.text_entry.configure(
            yscrollcommand=text_scrollbar.set
        )

        self.text_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        if self.task_data.get("text"):
            self.text_entry.insert("1.0", self.task_data["text"])

        self.validation_label = tk.Label(
            parent,
            text="",
            bg="#f0f0f0",
            fg="#c0392b",
            font=("Arial", 10)
        )
        self.validation_label.pack(anchor=tk.W, pady=(0, 8))

        tk.Label(
            parent,
            text="Notes (optional)",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(anchor=tk.W)

        notes_frame = tk.Frame(
            parent,
            bg="white",
            relief=tk.SUNKEN,
            bd=1
        )
        notes_frame.pack(fill=tk.X, pady=(5, 10))

        self.notes_entry = tk.Text(
            notes_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            height=3
        )
        notes_scrollbar = tk.Scrollbar(
            notes_frame,
            command=self.notes_entry.yview
        )
        self.notes_entry.configure(
            yscrollcommand=notes_scrollbar.set
        )

        self.notes_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        if self.task_data.get("notes"):
            self.notes_entry.insert("1.0", self.task_data["notes"])

        tk.Label(
            parent,
            text="Eisenhower Quadrant *",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(anchor=tk.W)

        self.quadrant_var = tk.StringVar(
            value=self.task_data.get("quadrant", "quadrant_1")
        )

        quadrant_frame = tk.Frame(parent, bg="#f0f0f0")
        quadrant_frame.pack(fill=tk.X, pady=(5, 10))

        quadrant_names = self._get_quadrant_display_names()

        quadrants = [
            ("Q1 - " + quadrant_names["quadrant_1"], "quadrant_1"),
            ("Q2 - " + quadrant_names["quadrant_2"], "quadrant_2"),
            ("Q3 - " + quadrant_names["quadrant_3"], "quadrant_3"),
            ("Q4 - " + quadrant_names["quadrant_4"], "quadrant_4")
        ]

        for label, value in quadrants:
            rb = tk.Radiobutton(
                quadrant_frame,
                text=label,
                value=value,
                variable=self.quadrant_var,
                bg="#f0f0f0",
                fg="black",
                activebackground="#f0f0f0",
                activeforeground="black",
                selectcolor="white",
                anchor="w",
                font=("Arial", 10)
            )
            rb.pack(fill=tk.X, padx=6, pady=1)

        tk.Label(
            parent,
            text="Assign Date *",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(anchor=tk.W)

        initial_date = (
            self._coerce_date(self.task_data.get("date"))
            or self.current_date
        )

        selected_frame = tk.Frame(
            parent,
            bg="#eaf2f8",
            relief=tk.RAISED,
            bd=1
        )
        selected_frame.pack(fill=tk.X, pady=(6, 8))

        tk.Label(
            selected_frame,
            text="Selected Date",
            font=("Arial", 10, "bold"),
            bg="#eaf2f8",
            fg="black"
        ).pack(pady=(6, 0))

        self.selected_date_label = tk.Label(
            selected_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg="#eaf2f8",
            fg="black"
        )
        self.selected_date_label.pack(pady=(0, 8))

        self.selection_feedback_label = tk.Label(
            parent,
            text="No date change yet.",
            font=("Arial", 10, "italic"),
            bg="#f0f0f0",
            fg="#1f5fa8"
        )
        self.selection_feedback_label.pack(anchor=tk.W, pady=(0, 8))

        quick_frame = tk.LabelFrame(
            parent,
            text="Quick Select",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="black",
            padx=8,
            pady=8
        )
        quick_frame.pack(fill=tk.X, pady=(0, 8))

        today = date.today()
        self.quick_dates = {
            "Today": today,
            "Tomorrow": today + timedelta(days=1),
            "Next Week": today + timedelta(days=7)
        }

        quick_buttons = tk.Frame(quick_frame, bg="#f0f0f0")
        quick_buttons.pack(fill=tk.X)

        for label, quick_date in self.quick_dates.items():
            btn = tk.Button(
                quick_buttons,
                text=label,
                command=lambda d=quick_date: self.set_quick_date(d),
                bg="#d5dbdb",
                fg="black",
                activebackground="#cfd4d4",
                activeforeground="black",
                font=("Arial", 10, "bold"),
                relief=tk.RAISED,
                bd=1,
                padx=10,
                pady=6
            )
            btn.pack(
                side=tk.LEFT,
                expand=True,
                fill=tk.X,
                padx=3,
                pady=3
            )
            self.quick_buttons[label] = btn

        calendar_holder = tk.Frame(parent, bg="#f0f0f0")
        calendar_holder.pack(fill=tk.X, pady=(0, 12))

        self.calendar_widget = CalendarWidget(
            calendar_holder,
            selected_date=initial_date,
            on_date_change=self.on_date_changed
        )

        self.update_selected_date_display(
            self.calendar_widget.get_selected_date()
        )
        self.update_quick_button_styles(
            self.calendar_widget.get_selected_date()
        )

    def set_quick_date(self, quick_date):
        self.calendar_widget.select_date(quick_date)

    def on_date_changed(self, selected_date):
        self.update_selected_date_display(selected_date)
        self.update_quick_button_styles(selected_date)

        self.selection_feedback_label.config(
            text=(
                "Selection changed to "
                f"{selected_date.strftime('%A, %B %d, %Y')}"
            )
        )

    def update_selected_date_display(self, selected=None):
        selected = selected or self.calendar_widget.get_selected_date()

        self.selected_date_label.config(
            text=selected.strftime("%A, %B %d, %Y")
        )

    def update_quick_button_styles(self, selected_date):
        for label, btn in self.quick_buttons.items():
            quick_date = self.quick_dates[label]

            if selected_date == quick_date:
                btn.config(
                    bg="#1f5fa8",
                    fg="white",
                    activebackground="#174a82",
                    activeforeground="white",
                    relief=tk.SUNKEN,
                    bd=3
                )
            else:
                btn.config(
                    bg="#d5dbdb",
                    fg="black",
                    activebackground="#cfd4d4",
                    activeforeground="black",
                    relief=tk.RAISED,
                    bd=1
                )

    def save(self):
        text = self.text_entry.get("1.0", tk.END).strip()

        if not text:
            self.validation_label.config(
                text="Task description is required."
            )
            return

        selected_date = self.calendar_widget.get_selected_date()

        self.result = {
            "text": text,
            "notes": self.notes_entry.get("1.0", tk.END).strip(),
            "date": selected_date.isoformat(),
            "quadrant": self.quadrant_var.get(),
            "completed": self.task_data.get("completed", False)
        }

        try:
            self.dialog.unbind_all("<Control-Return>")
        except Exception:
            pass

        try:
            self.dialog.attributes("-topmost", False)
        except Exception:
            pass

        self.dialog.destroy()

    def cancel(self):
        self.result = None

        try:
            self.dialog.unbind_all("<Control-Return>")
        except Exception:
            pass

        try:
            self.dialog.attributes("-topmost", False)
        except Exception:
            pass

        self.dialog.destroy()
