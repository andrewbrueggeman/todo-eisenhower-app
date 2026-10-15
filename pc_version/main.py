"""
Eisenhower Matrix To-Do Application - Main Entry Point
"""
import sys
import tkinter as tk
from datetime import datetime


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Eisenhower Matrix To-Do Application...")

    root = tk.Tk()

    try:
        from ui.main_window import EisenhowerMatrixApp
        app = EisenhowerMatrixApp(root)

        if hasattr(app, "on_closing"):
            root.protocol("WM_DELETE_WINDOW", app.on_closing)
        else:
            root.protocol("WM_DELETE_WINDOW", root.destroy)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Application started successfully")
        root.mainloop()

    except Exception as e:
        print(f"Unexpected startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
