import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class NotesWidget:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.unsaved_changes = False
        self.setup_notes()

    def setup_notes(self):
        notes_container = tk.Frame(self.parent, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        notes_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        header_frame = tk.Frame(notes_container, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(
            header_frame,
            text="Daily Notes",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="black"
        ).pack(side=tk.LEFT)

        self.save_button = tk.Button(
            header_frame,
            text="Save",
            command=self.save_notes,
            bg="#3498db",
            fg="black",
            activebackground="#2e86c1",
            activeforeground="black",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=3
        )
        self.save_button.pack(side=tk.RIGHT)

        text_frame = tk.Frame(notes_container, bg="white", relief=tk.SUNKEN, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.notes_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="white",
            fg="#2c3e50",
            padx=10,
            pady=10,
            relief=tk.FLAT,
            insertbackground="#2c3e50"
        )

        scrollbar = tk.Scrollbar(text_frame, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=scrollbar.set)

        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_label = tk.Label(
            notes_container,
            text="",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.status_label.pack(pady=(0, 10))

        self.notes_text.bind("<KeyRelease>", self.on_text_change)
        self.notes_text.bind("<Control-s>", self._handle_ctrl_s)

        self.load_notes()

    def _handle_ctrl_s(self, event=None):
        self.save_notes()
        return "break"

    def on_text_change(self, event=None):
        self.unsaved_changes = True
        self.status_label.config(text="Unsaved changes", fg="#f39c12")

    def save_notes(self, silent=False):
        try:
            notes_content = self.notes_text.get("1.0", tk.END).rstrip()

            self.app.data_manager.notes_data["shared_notes"] = notes_content
            success = self.app.data_manager.save_notes()

            if success:
                self.unsaved_changes = False
                self.status_label.config(
                    text=f"Saved at {datetime.now().strftime('%H:%M:%S')}",
                    fg="#27ae60"
                )
                return True
            else:
                self.status_label.config(text="Save failed", fg="#e74c3c")
                if not silent:
                    messagebox.showerror("Error", "Failed to save notes. Check file permissions.")
                return False

        except Exception as e:
            self.status_label.config(text="Save error", fg="#e74c3c")
            if not silent:
                messagebox.showerror("Error", f"Error saving notes: {str(e)}")
            return False

    def load_notes(self):
        try:
            notes_content = self.app.data_manager.get_shared_notes()

            self.notes_text.delete("1.0", tk.END)
            if notes_content:
                self.notes_text.insert("1.0", notes_content)

            self.unsaved_changes = False
            self.status_label.config(
                text="Persistent notes shared across all dates",
                fg="#7f8c8d"
            )

        except Exception as e:
            self.status_label.config(text="Load error", fg="#e74c3c")
            print(f"Error loading notes: {e}")

    def refresh_for_current_date(self):
        self.load_notes()

    def check_unsaved_changes(self):
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved notes. Do you want to save them before continuing?"
            )

            if result is True:
                return self.save_notes()
            elif result is False:
                return True
            else:
                return False

        return True
