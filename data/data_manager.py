"""
Data Manager for Eisenhower Matrix To-Do Application

Handles all data operations including:
- Loading and saving tasks to JSON files
- Managing daily notes
- Task migration logic
- Settings persistence
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List, Any

class DataManager:
    def __init__(self):
        self.data_dir = "data_files"
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        self.notes_file = os.path.join(self.data_dir, "daily_notes.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data structures
        self.tasks_data = self.load_tasks()
        self.notes_data = self.load_notes()
        self.settings_data = self.load_settings()
        
        print("✓ Data manager initialized")
        print(f"✓ Tasks file: {self.tasks_file}")
        print(f"✓ Notes file: {self.notes_file}")
        
    def load_tasks(self) -> Dict:
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️ Error loading tasks: {e}")
            return {}
            
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks_data, f, indent=2, default=str)
            print("✓ Tasks saved successfully")
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")
            
    def load_notes(self) -> Dict:
        """Load daily notes from JSON file"""
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️ Error loading notes: {e}")
            return {}
            
    def save_notes(self):
        """Save daily notes to JSON file"""
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(self.notes_data, f, indent=2)
            print("✓ Notes saved successfully")
        except Exception as e:
            print(f"❌ Error saving notes: {e}")
            
    def load_settings(self) -> Dict:
        """Load application settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return {
                "timer_last_duration": 20,
                "auto_restart_timer": True,
                "outlook_sync_enabled": True,
                "outlook_last_sync": None
            }
        except Exception as e:
            print(f"⚠️ Error loading settings: {e}")
            return {}
            
    def save_settings(self):
        """Save application settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings_data, f, indent=2)
            print("✓ Settings saved successfully")
        except Exception as e:
            print(f"❌ Error saving settings: {e}")

    def get_tasks_for_date(self, target_date: date) -> Dict:
        """Get all tasks for a specific date"""
        date_str = target_date.isoformat()
        return self.tasks_data.get(date_str, {
            "quadrant_1": [],
            "quadrant_2": [],
            "quadrant_3": [],
            "quadrant_4": []
        })
        
    def get_notes_for_date(self, target_date: date) -> str:
        """Get notes for a specific date"""
        date_str = target_date.isoformat()
        return self.notes_data.get(date_str, "")
