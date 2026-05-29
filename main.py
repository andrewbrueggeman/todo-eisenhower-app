"""
Eisenhower Matrix To-Do Application - Main Entry Point

A productivity application that helps organize tasks using the Eisenhower Matrix
with integrated timer, system monitoring, and daily notes.

Usage:
    python main.py

Features:
- Eisenhower Matrix task organization
- Configurable UI layout
- Focus timer with presets
- System resource monitoring
- Daily notes with auto-save
- Data persistence across sessions
"""

import tkinter as tk
import os
import sys
from datetime import datetime

def main():
    """Main application entry point"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Eisenhower Matrix To-Do Application...")
    
    # Ensure required directories exist
    os.makedirs("data_files", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("ui/components", exist_ok=True)
    
    # Create main window
    root = tk.Tk()
    
    try:
        from ui.main_window import EisenhowerMatrixApp
        app = EisenhowerMatrixApp(root)
        
        # Set up proper cleanup
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Application started successfully")
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Error importing UI components: {e}")
        print("Please ensure all UI files are properly created.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
