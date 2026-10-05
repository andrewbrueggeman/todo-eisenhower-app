import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class MatrixWidget:
    SELECTED_BORDER_COLOR = "#2980b9"
    SELECTED_BG_COLOR = "#d6eaf8"
    NORMAL_BORDER_COLOR = "#cccccc"
    NORMAL_INCOMPLETE_BG = "#f8f9fa"
    NORMAL_COMPLETED_BG = "#e8f5e9"

    DEFAULT_QUADRANT_NAMES = {
        "quadrant_1": "Critical Actions",
        "quadrant_2": "Strategic Work",
        "quadrant_3": "Routine Tasks",
        "quadrant_4": "Backlog/Opportunities"
    }

    QUADRANT_NUMBERS = {
        "quadrant_1": "Q1",
        "quadrant_2": "Q2",
        "quadrant_3": "Q3",
        "quadrant_4": "Q4"
    }

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.quadrant_frames = {}
        self.task_widgets = {}
        self.main_scroll_canvas = None
        self.scroll_canvases = set()
        self.selected_task = None

        self.setup_matrix()

    def _is_multi_day_view(self):
        return len(self.app.get_visible_dates()) > 1

    def _quadrant_name(self, quadrant_id):
        saved_names = self.app.data_manager.settings_data.get(
            "quadrant_names",
            {}
        )

        if not isinstance(saved_names, dict):
            saved_names = {}

        default_name = self.DEFAULT_QUADRANT_NAMES.get(
            quadrant_id,
            "Quadrant"
        )
        saved_name = saved_names.get(quadrant_id, default_name)

        if not isinstance(saved_name, str) or not saved_name.strip():
            return default_name

        return saved_name.strip()

    def _quadrant_display_label(self, quadrant_id):
        quadrant_number = self.QUADRANT_NUMBERS.get(
            quadrant_id,
            ""
        )
        quadrant_name = self._quadrant_name(quadrant_id)

        return f"{quadrant_number}: {quadrant_name}"

    def setup_matrix(self):
        self._unbind_mousewheel()

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.quadrant_frames = {}
        self.task_widgets = {}
        self.main_scroll_canvas = None
        self.scroll_canvases = set()
        self.selected_task = None

        title_label = tk.Label(
            self.parent,
            text="To Do List & Prioritization Matrix",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=(0, 15))
        self._bind_clear_selection(title_label)

        self.outer_container = tk.Frame(self.parent, bg="#f0f0f0")
        self.outer_container.pack(fill=tk.BOTH, expand=True)
        self._bind_clear_selection(self.outer_container)

        visible_dates = self.app.get_visible_dates()

        if len(visible_dates) == 1:
            self._create_day_matrix(
                self.outer_container,
                visible_dates[0],
                single_view=True
            )
        else:
            canvas = tk.Canvas(
                self.outer_container,
                bg="#f0f0f0",
                highlightthickness=0
            )
            scrollbar = tk.Scrollbar(
                self.outer_container,
                orient="vertical",
                command=canvas.yview
            )
            scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

            self.main_scroll_canvas = canvas
            self._register_scroll_canvas(canvas)
            self._bind_clear_selection(canvas)
            self._bind_clear_selection(scrollable_frame)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            window_id = canvas.create_window(
                (0, 0),
                window=scrollable_frame,
                anchor="nw"
            )

            def resize_inner(event):
                canvas.itemconfig(window_id, width=event.width)

            canvas.bind("<Configure>", resize_inner)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for target_date in visible_dates:
                day_frame = tk.Frame(
                    scrollable_frame,
                    bg="#f0f0f0",
                    relief=tk.GROOVE,
                    bd=2
                )
                day_frame.pack(
                    fill=tk.BOTH,
                    expand=True,
                    padx=5,
                    pady=8
                )
                self._bind_clear_selection(day_frame)

                self._create_day_matrix(
                    day_frame,
                    target_date,
                    single_view=False
                )

        self._bind_mousewheel()

    def _bind_clear_selection(self, widget):
        try:
            widget.bind("<Button-1>", self._clear_selection_event)
        except Exception:
            pass

    def _clear_selection_event(self, event=None):
        self._clear_selection()
        return None

    def _register_scroll_canvas(self, canvas):
        self.scroll_canvases.add(canvas)

    def _find_scroll_canvas(self, widget):
        if self.main_scroll_canvas is not None and self._is_multi_day_view():
            return self.main_scroll_canvas

        current = widget

        while current is not None:
            if current in self.scroll_canvases:
                return current

            current = getattr(current, "master", None)

        return self.main_scroll_canvas

    def _bind_mousewheel(self):
        try:
            self.app.root.bind_all(
                "<MouseWheel>",
                self._on_mousewheel
            )
            self.app.root.bind_all(
                "<Button-4>",
                self._on_mousewheel_linux_up
            )
            self.app.root.bind_all(
                "<Button-5>",
                self._on_mousewheel_linux_down
            )
        except Exception:
            pass

    def _unbind_mousewheel(self):
        try:
            self.app.root.unbind_all("<MouseWheel>")
            self.app.root.unbind_all("<Button-4>")
            self.app.root.unbind_all("<Button-5>")
        except Exception:
            pass

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

    def _on_mousewheel(self, event):
        canvas = self._find_scroll_canvas(event.widget)

        if canvas is None:
            return "break"

        step = self._normalize_wheel_step(event.delta)

        if step != 0:
            canvas.yview_scroll(step, "units")

        return "break"

    def _on_mousewheel_linux_up(self, event):
        canvas = self._find_scroll_canvas(event.widget)

        if canvas is not None:
            canvas.yview_scroll(-1, "units")

        return "break"

    def _on_mousewheel_linux_down(self, event):
        canvas = self._find_scroll_canvas(event.widget)

        if canvas is not None:
            canvas.yview_scroll(1, "units")

        return "break"

    def _create_day_matrix(self, parent, target_date, single_view=False):
        if not single_view:
            day_label = target_date.strftime("%A, %B %d, %Y")

            if target_date == datetime.now().date():
                day_label += " (Today)"

            label = tk.Label(
                parent,
                text=day_label,
                font=("Arial", 14, "bold"),
                bg="#f0f0f0",
                fg="#2c3e50"
            )
            label.pack(pady=(8, 10))
            self._bind_clear_selection(label)

        matrix_container = tk.Frame(parent, bg="#f0f0f0")
        matrix_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )
        self._bind_clear_selection(matrix_container)

        matrix_container.grid_rowconfigure(0, weight=1)
        matrix_container.grid_rowconfigure(1, weight=1)
        matrix_container.grid_columnconfigure(0, weight=1)
        matrix_container.grid_columnconfigure(1, weight=1)

        quadrants = [
            (
                self._quadrant_display_label("quadrant_1"),
                "quadrant_1",
                0,
                0,
                "#f5b7b1"
            ),
            (
                self._quadrant_display_label("quadrant_2"),
                "quadrant_2",
                0,
                1,
                "#aed6f1"
            ),
            (
                self._quadrant_display_label("quadrant_3"),
                "quadrant_3",
                1,
                0,
                "#f9e79f"
            ),
            (
                self._quadrant_display_label("quadrant_4"),
                "quadrant_4",
                1,
                1,
                "#d7bde2"
            )
        ]

        date_key = target_date.isoformat()

        for title, quad_id, row, col, header_color in quadrants:
            combined_quad_id = f"{date_key}|{quad_id}"

            self.create_quadrant(
                matrix_container,
                title,
                combined_quad_id,
                target_date,
                quad_id,
                row,
                col,
                header_color
            )

    def _safe_button_colors(self):
        settings = self.app.data_manager.settings_data
        bg = settings.get("add_task_button_bg", "#4CAF50")
        fg = settings.get("add_task_button_fg", "black")

        if not isinstance(bg, str) or bg.lower() in (
            "#ffffff",
            "#feffff",
            "white"
        ):
            bg = "#2f2f2f"

        if not isinstance(fg, str) or fg.strip() == "":
            fg = "black"

        return bg, fg

    def create_quadrant(
        self,
        parent,
        title,
        combined_quad_id,
        target_date,
        quadrant_id,
        row,
        col,
        header_color
    ):
        quad_frame = tk.Frame(
            parent,
            bg="white",
            relief=tk.RAISED,
            bd=2
        )
        quad_frame.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="nsew"
        )
        self._bind_clear_selection(quad_frame)

        header_frame = tk.Frame(quad_frame, bg=header_color)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        self._bind_clear_selection(header_frame)

        title_frame = tk.Frame(header_frame, bg=header_color)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._bind_clear_selection(title_frame)

        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Arial", 12, "bold"),
            bg=header_color,
            fg="#1f1f1f",
            anchor="w"
        )
        title_label.pack(side=tk.LEFT, padx=(10, 4), pady=8)
        self._bind_clear_selection(title_label)

        button_bg, _button_fg = self._safe_button_colors()

        add_button = tk.Button(
            header_frame,
            text="+ Add",
            command=lambda d=target_date, q=quadrant_id:
                self.add_task_for_date(d, q),
            bg=button_bg,
            fg="black",
            activebackground=button_bg,
            activeforeground="black",
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            bd=1,
            padx=8,
            pady=3,
            cursor="hand2"
        )
        add_button.pack(side=tk.RIGHT, padx=(4, 10), pady=6)

        body_frame = tk.Frame(quad_frame, bg="white")
        body_frame.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=(6, 6)
        )
        self._bind_clear_selection(body_frame)

        canvas = tk.Canvas(
            body_frame,
            bg="white",
            highlightthickness=0
        )
        self._register_scroll_canvas(canvas)
        self._bind_clear_selection(canvas)

        scrollbar = tk.Scrollbar(
            body_frame,
            orient="vertical",
            command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg="white")
        self._bind_clear_selection(scrollable_frame)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        window_id = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        def resize_inner(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_inner)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.quadrant_frames[combined_quad_id] = scrollable_frame
        self.task_widgets[combined_quad_id] = []

    def _normal_task_bg(self, target_date, quadrant, task_index):
        try:
            tasks = self.app.data_manager.get_tasks_for_date(target_date)

            if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
                is_completed = tasks[quadrant][task_index].get(
                    "completed",
                    False
                )

                if is_completed:
                    return self.NORMAL_COMPLETED_BG

                return self.NORMAL_INCOMPLETE_BG

        except Exception:
            pass

        return self.NORMAL_INCOMPLETE_BG

    def _set_task_visual_bg(
        self,
        text_container,
        bg_color,
        border_color=None,
        border_width=None
    ):
        try:
            text_container.config(bg=bg_color)

            if border_color is not None:
                text_container.config(
                    highlightbackground=border_color
                )

            if border_width is not None:
                text_container.config(
                    highlightthickness=border_width
                )

            for child in text_container.winfo_children():
                try:
                    child.config(bg=bg_color)
                except Exception:
                    pass

                for grandchild in child.winfo_children():
                    try:
                        grandchild.config(bg=bg_color)
                    except Exception:
                        pass

        except Exception:
            pass

    def _restore_task_visual(self, selected_info):
        if not selected_info:
            return

        try:
            target_date = selected_info["date"]
            quadrant = selected_info["quadrant"]
            task_index = selected_info["index"]
            text_container = selected_info["container"]

            if not text_container.winfo_exists():
                return

            normal_bg = self._normal_task_bg(
                target_date,
                quadrant,
                task_index
            )

            self._set_task_visual_bg(
                text_container,
                normal_bg,
                border_color=self.NORMAL_BORDER_COLOR,
                border_width=1
            )

        except Exception:
            pass

    def _select_task(
        self,
        target_date,
        quadrant,
        task_index,
        text_container
    ):
        self._restore_task_visual(self.selected_task)

        self._set_task_visual_bg(
            text_container,
            self.SELECTED_BG_COLOR,
            border_color=self.SELECTED_BORDER_COLOR,
            border_width=2
        )

        self.selected_task = {
            "date": target_date,
            "quadrant": quadrant,
            "index": task_index,
            "container": text_container
        }

        return "break"

    def _clear_selection(self):
        self._restore_task_visual(self.selected_task)
        self.selected_task = None

    def create_task_widget(
        self,
        parent,
        task_data,
        target_date,
        quadrant,
        task_index
    ):
        task_frame = tk.Frame(parent, bg="white", pady=3)
        task_frame.pack(fill=tk.X, padx=3, pady=2)

        var = tk.BooleanVar(
            value=task_data.get("completed", False)
        )

        tk.Checkbutton(
            task_frame,
            variable=var,
            bg="white",
            command=lambda: self.toggle_task_completion(
                target_date,
                quadrant,
                task_index,
                var.get()
            )
        ).pack(side=tk.LEFT)

        is_completed = task_data.get("completed", False)

        if is_completed:
            text_bg = self.NORMAL_COMPLETED_BG
            text_fg = "#7f8c8d"
            font_style = ("Arial", 10, "overstrike")
        else:
            text_bg = self.NORMAL_INCOMPLETE_BG
            text_fg = "#2c3e50"
            font_style = ("Arial", 10)

        text_container = tk.Frame(
            task_frame,
            bg=text_bg,
            relief=tk.RAISED,
            bd=1,
            highlightbackground=self.NORMAL_BORDER_COLOR,
            highlightthickness=1
        )
        text_container.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True
        )

        task_label = tk.Label(
            text_container,
            text=task_data["text"],
            bg=text_bg,
            fg=text_fg,
            font=font_style,
            wraplength=250,
            justify=tk.LEFT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        task_label.bind(
            "<Button-1>",
            lambda e: self._select_task(
                target_date,
                quadrant,
                task_index,
                text_container
            )
        )
        text_container.bind(
            "<Button-1>",
            lambda e: self._select_task(
                target_date,
                quadrant,
                task_index,
                text_container
            )
        )

        task_label.bind(
            "<Double-Button-1>",
            lambda e: self.edit_task(
                target_date,
                quadrant,
                task_index
            )
        )

        task_label.bind(
            "<Button-2>",
            lambda e: self.show_context_menu(
                e,
                target_date,
                quadrant,
                task_index
            )
        )
        task_label.bind(
            "<Button-3>",
            lambda e: self.show_context_menu(
                e,
                target_date,
                quadrant,
                task_index
            )
        )
        task_label.bind(
            "<Control-Button-1>",
            lambda e: self.show_context_menu(
                e,
                target_date,
                quadrant,
                task_index
            )
        )

        text_container.bind(
            "<Button-2>",
            lambda e: self.show_context_menu(
                e,
                target_date,
                quadrant,
                task_index
            )
        )
        text_container.bind(
            "<Button-3>",
            lambda e: self.show_context_menu(
                e,
                target_date,
                quadrant,
                task_index
            )
        )
        text_container.bind(
            "<Control-Button-1>",
            lambda e: self.show_context_menu(
                e,
                target_date,
                quadrant,
                task_index
            )
        )

        if task_data.get("notes", "").strip():
            note_icon = tk.Label(
                text_container,
                text="Notes",
                bg=text_bg,
                fg="#5d6d7e",
                font=("Arial", 8, "bold"),
                cursor="hand2",
                padx=6
            )
            note_icon.pack(side=tk.RIGHT, padx=4)

            note_icon.bind(
                "<Button-1>",
                lambda e: self._select_task(
                    target_date,
                    quadrant,
                    task_index,
                    text_container
                )
            )
            note_icon.bind(
                "<Button-2>",
                lambda e: self.show_context_menu(
                    e,
                    target_date,
                    quadrant,
                    task_index
                )
            )
            note_icon.bind(
                "<Button-3>",
                lambda e: self.show_context_menu(
                    e,
                    target_date,
                    quadrant,
                    task_index
                )
            )
            note_icon.bind(
                "<Control-Button-1>",
                lambda e: self.show_context_menu(
                    e,
                    target_date,
                    quadrant,
                    task_index
                )
            )

        return {
            "frame": task_frame,
            "label": task_label,
            "var": var,
            "container": text_container
        }

    def show_notes(self, task_data):
        notes = task_data.get("notes", "").strip()

        if not notes:
            messagebox.showinfo(
                "Task Details",
                task_data["text"]
            )
            return

        popup = tk.Toplevel(self.app.root)
        popup.title("Task Notes")

        px = self.app.root.winfo_rootx()
        py = self.app.root.winfo_rooty()
        pw = max(self.app.root.winfo_width(), 800)
        ph = max(self.app.root.winfo_height(), 700)

        popup_x = px + (pw - 420) // 2
        popup_y = py + (ph - 320) // 2

        if popup_y < 28:
            popup_y = 28

        popup.geometry(f"420x320+{popup_x}+{popup_y}")
        popup.update_idletasks()

        popup.lift(aboveThis=self.app.root)
        popup.focus_force()
        popup.attributes("-topmost", True)
        popup.grab_set()

        popup.after(
            200,
            lambda: popup.attributes("-topmost", False)
        )

        main_frame = tk.Frame(
            popup,
            bg="white",
            padx=20,
            pady=20
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main_frame,
            text="Task:",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="gray"
        ).pack(anchor=tk.W)

        tk.Label(
            main_frame,
            text=task_data["text"],
            font=("Arial", 12),
            bg="white",
            wraplength=370,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 15))

        tk.Label(
            main_frame,
            text="Notes:",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="gray"
        ).pack(anchor=tk.W)

        notes_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#f9f9f9",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        notes_text.insert("1.0", notes)
        notes_text.configure(state=tk.DISABLED)
        notes_text.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(5, 15)
        )

        def close_popup():
            try:
                popup.attributes("-topmost", False)
            except Exception:
                pass

            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        tk.Button(
            main_frame,
            text="Close",
            command=close_popup,
            bg="#d5dbdb",
            fg="black",
            activebackground="#cfd4d4",
            activeforeground="black",
            padx=20
        ).pack()

    def show_context_menu(
        self,
        event,
        target_date,
        quadrant,
        task_index
    ):
        menu = tk.Menu(self.parent, tearoff=0)

        menu.add_command(
            label="Edit Task",
            command=lambda: self.edit_task(
                target_date,
                quadrant,
                task_index
            )
        )

        tasks = self.app.data_manager.get_tasks_for_date(target_date)

        if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
            task_data = tasks[quadrant][task_index]

            if task_data.get("notes", "").strip():
                menu.add_command(
                    label="View Notes",
                    command=lambda: self.show_notes(task_data)
                )

        move_menu = tk.Menu(menu, tearoff=0)

        move_menu.add_command(
            label="Move Up",
            command=lambda: self.move_task_up(
                target_date,
                quadrant,
                task_index
            )
        )
        move_menu.add_command(
            label="Move Down",
            command=lambda: self.move_task_down(
                target_date,
                quadrant,
                task_index
            )
        )
        move_menu.add_command(
            label="Move to Top",
            command=lambda: self.move_task_to_top(
                target_date,
                quadrant,
                task_index
            )
        )
        move_menu.add_command(
            label="Move to Bottom",
            command=lambda: self.move_task_to_bottom(
                target_date,
                quadrant,
                task_index
            )
        )

        move_menu.add_separator()

        for target_quadrant in (
            "quadrant_1",
            "quadrant_2",
            "quadrant_3",
            "quadrant_4"
        ):
            move_menu.add_command(
                label=(
                    f"Move to "
                    f"{self._quadrant_display_label(target_quadrant)}"
                ),
                command=lambda q=target_quadrant:
                    self.move_task_to_quadrant_direct(
                        target_date,
                        quadrant,
                        task_index,
                        q
                    )
            )

        menu.add_cascade(label="Move To...", menu=move_menu)

        menu.add_command(
            label="Move Task...",
            command=lambda: self.move_task(
                target_date,
                quadrant,
                task_index
            )
        )
        menu.add_command(
            label="Copy Task...",
            command=lambda: self.copy_task(
                target_date,
                quadrant,
                task_index
            )
        )

        menu.add_separator()

        menu.add_command(
            label="Delete Task",
            command=lambda: self.delete_task(
                target_date,
                quadrant,
                task_index
            )
        )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

        return "break"

    def move_task_up(self, target_date, quadrant, task_index):
        if self.app.data_manager.move_task_within_quadrant(
            target_date,
            quadrant,
            task_index,
            "up"
        ):
            self.load_tasks()

    def move_task_down(self, target_date, quadrant, task_index):
        if self.app.data_manager.move_task_within_quadrant(
            target_date,
            quadrant,
            task_index,
            "down"
        ):
            self.load_tasks()

    def move_task_to_top(self, target_date, quadrant, task_index):
        if self.app.data_manager.move_task_within_quadrant(
            target_date,
            quadrant,
            task_index,
            "top"
        ):
            self.load_tasks()

    def move_task_to_bottom(self, target_date, quadrant, task_index):
        if self.app.data_manager.move_task_within_quadrant(
            target_date,
            quadrant,
            task_index,
            "bottom"
        ):
            self.load_tasks()

    def move_task_to_quadrant_direct(
        self,
        target_date,
        from_quadrant,
        task_index,
        to_quadrant
    ):
        if from_quadrant == to_quadrant:
            return

        if self.app.data_manager.move_task_to_quadrant(
            target_date,
            from_quadrant,
            task_index,
            to_quadrant
        ):
            self.load_tasks()

    def add_task_for_date(self, target_date, quadrant):
        try:
            from ui.task_dialog import TaskDialog

            self._clear_selection()

            dialog = TaskDialog(
                self.app.root,
                {"quadrant": quadrant},
                target_date,
                mode="add"
            )

            self.app.root.wait_window(dialog.dialog)
            self._bind_mousewheel()

            if dialog.result:
                task_date = dialog.result["date"]

                if isinstance(task_date, str):
                    task_date = datetime.strptime(
                        task_date,
                        "%Y-%m-%d"
                    ).date()

                if self.app.data_manager.add_task(
                    task_date,
                    dialog.result["quadrant"],
                    dialog.result
                ):
                    self.load_tasks()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not open Add Task dialog.\n\nError details: {e}"
            )

    def edit_task(self, target_date, quadrant, task_index):
        try:
            from ui.task_dialog import TaskDialog

            tasks = self.app.data_manager.get_tasks_for_date(target_date)

            if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
                original_task = tasks[quadrant][task_index].copy()

                dialog = TaskDialog(
                    self.app.root,
                    original_task,
                    target_date,
                    mode="edit"
                )

                self.app.root.wait_window(dialog.dialog)
                self._bind_mousewheel()

                if dialog.result:
                    new_date = dialog.result["date"]

                    if isinstance(new_date, str):
                        new_date = datetime.strptime(
                            new_date,
                            "%Y-%m-%d"
                        ).date()

                    new_quadrant = dialog.result["quadrant"]
                    date_changed = new_date != target_date
                    quadrant_changed = new_quadrant != quadrant

                    if date_changed or quadrant_changed:
                        self.app.data_manager.delete_task(
                            target_date,
                            quadrant,
                            task_index
                        )
                        self.app.data_manager.add_task(
                            new_date,
                            new_quadrant,
                            dialog.result
                        )
                    else:
                        self.app.data_manager.update_task(
                            target_date,
                            quadrant,
                            task_index,
                            dialog.result
                        )

                    self.load_tasks()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not open Edit Task dialog.\n\nError details: {e}"
            )

    def move_task(self, target_date, quadrant, task_index):
        try:
            from ui.task_dialog import TaskDialog

            tasks = self.app.data_manager.get_tasks_for_date(target_date)

            if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
                original_task = tasks[quadrant][task_index].copy()

                dialog = TaskDialog(
                    self.app.root,
                    original_task,
                    target_date,
                    mode="move"
                )

                self.app.root.wait_window(dialog.dialog)
                self._bind_mousewheel()

                if dialog.result:
                    new_date = dialog.result["date"]

                    if isinstance(new_date, str):
                        new_date = datetime.strptime(
                            new_date,
                            "%Y-%m-%d"
                        ).date()

                    new_quadrant = dialog.result["quadrant"]

                    self.app.data_manager.delete_task(
                        target_date,
                        quadrant,
                        task_index
                    )
                    self.app.data_manager.add_task(
                        new_date,
                        new_quadrant,
                        dialog.result
                    )

                    self.load_tasks()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not move task.\n\nError details: {e}"
            )

    def copy_task(self, target_date, quadrant, task_index):
        try:
            from ui.task_dialog import TaskDialog

            tasks = self.app.data_manager.get_tasks_for_date(target_date)

            if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
                original_task = tasks[quadrant][task_index].copy()
                original_task["completed"] = False

                dialog = TaskDialog(
                    self.app.root,
                    original_task,
                    target_date,
                    mode="copy"
                )

                self.app.root.wait_window(dialog.dialog)
                self._bind_mousewheel()

                if dialog.result:
                    new_date = dialog.result["date"]

                    if isinstance(new_date, str):
                        new_date = datetime.strptime(
                            new_date,
                            "%Y-%m-%d"
                        ).date()

                    new_quadrant = dialog.result["quadrant"]

                    self.app.data_manager.add_task(
                        new_date,
                        new_quadrant,
                        dialog.result
                    )

                    self.load_tasks()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not copy task.\n\nError details: {e}"
            )

    def toggle_task_completion(
        self,
        target_date,
        quadrant,
        task_index,
        completed
    ):
        tasks = self.app.data_manager.get_tasks_for_date(target_date)

        if quadrant in tasks and 0 <= task_index < len(tasks[quadrant]):
            task_data = tasks[quadrant][task_index]
            task_data["completed"] = completed

            self.app.data_manager.update_task(
                target_date,
                quadrant,
                task_index,
                task_data
            )

            self.load_tasks()

    def delete_task(self, target_date, quadrant, task_index):
        if messagebox.askyesno(
            "Delete Task",
            "Are you sure you want to delete this task?"
        ):
            if self.app.data_manager.delete_task(
                target_date,
                quadrant,
                task_index
            ):
                self.load_tasks()

    def load_tasks(self):
        self.selected_task = None

        for combined_quad_id in self.quadrant_frames:
            for widget in self.quadrant_frames[
                combined_quad_id
            ].winfo_children():
                widget.destroy()

            self.task_widgets[combined_quad_id] = []

        visible_dates = self.app.get_visible_dates()

        for target_date in visible_dates:
            tasks = self.app.data_manager.get_tasks_for_date(target_date)
            date_key = target_date.isoformat()

            for quad_id in (
                "quadrant_1",
                "quadrant_2",
                "quadrant_3",
                "quadrant_4"
            ):
                combined_quad_id = f"{date_key}|{quad_id}"

                if (
                    quad_id in tasks
                    and combined_quad_id in self.quadrant_frames
                ):
                    for i, task_data in enumerate(tasks[quad_id]):
                        widget = self.create_task_widget(
                            self.quadrant_frames[combined_quad_id],
                            task_data,
                            target_date,
                            quad_id,
                            i
                        )

                        self.task_widgets[combined_quad_id].append(widget)
