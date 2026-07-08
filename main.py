"""
Eisenhower Matrix To-Do Application - Main Entry Point

What this script does:
- Starts the main Tkinter application
- Ensures required folders exist
- Imports the real application class from ui.main_window
- Binds application shutdown cleanly

How to run:
python main.py
"""

import os
import sys
import tkinter as tk
from datetime import datetime


def main():
    """Main application entry point"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Eisenhower Matrix To-Do Application...")

    os.makedirs("data_files", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("ui/components", exist_ok=True)

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

    except ImportError as e:
        print(f"Import error while loading UI components: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
