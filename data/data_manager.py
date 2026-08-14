"""
Enhanced Data Manager for Eisenhower Matrix To-Do Application
With Startup-Only Automatic Task Migration
"""
import json
import os
import shutil
import sys
from datetime import date, timedelta
from typing import Dict


class DataManager:
    def __init__(self):
        self.data_dir = self._get_data_directory()
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        self.notes_file = os.path.join(self.data_dir, "daily_notes.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")

        self._setup_data_directory()

        self.tasks_data = self.load_tasks()
        self.notes_data = self.load_notes()
        self.settings_data = self.load_settings()

        print("✓ Data manager initialized")
        print(f"✓ Data directory: {self.data_dir}")
        print(f"✓ Tasks file: {self.tasks_file}")
        print(f"✓ Notes file: {self.notes_file}")
        print(f"✓ Settings file: {self.settings_file}")

    def _get_data_directory(self):
        """
        Packaged app:
            store data inside a folder next to the executable

        Source run:
            use project_root/data_files
        """
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
            return os.path.join(exe_dir, "EisenhowerMatrixData")

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(project_root, "data_files")

    def _setup_data_directory(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            test_file = os.path.join(self.data_dir, ".test_write")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            print(f"❌ ERROR: Cannot write to data directory: {e}")
            raise

    def _empty_day(self) -> Dict:
        return {
            "quadrant_1": [],
            "quadrant_2": [],
            "quadrant_3": [],
            "quadrant_4": []
        }

    def _ensure_day_exists(self, target_date: date):
        date_str = target_date.isoformat()
        if date_str not in self.tasks_data:
            self.tasks_data[date_str] = self._empty_day()

    def _task_signature(self, task: Dict) -> tuple:
        return (
            task.get("text", "").strip(),
            task.get("notes", "").strip(),
            bool(task.get("completed", False))
        )

    def _existing_signatures_for_day(self, target_date: date) -> set:
        date_str = target_date.isoformat()
        signatures = set()

        if date_str not in self.tasks_data:
            return signatures

        for quadrant in ["quadrant_1", "quadrant_2", "quadrant_3", "quadrant_4"]:
            for task in self.tasks_data[date_str].get(quadrant, []):
                signatures.add((quadrant, self._task_signature(task)))

        return signatures

    def load_tasks(self) -> Dict:
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ Error loading tasks: {e}")
            self._backup_file(self.tasks_file)
            return {}

    def save_tasks(self):
        try:
            if os.path.exists(self.tasks_file):
                self._backup_file(self.tasks_file)

            temp_file = self.tasks_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks_data, f, indent=2, default=str, ensure_ascii=False)

            if os.path.exists(self.tasks_file):
                os.remove(self.tasks_file)
            os.rename(temp_file, self.tasks_file)
            return True
        except Exception as e:
            print(f"❌ ERROR saving tasks: {e}")
            return False

    def load_notes(self) -> Dict:
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            return {"shared_notes": ""}
        except Exception as e:
            print(f"❌ Error loading notes: {e}")
            self._backup_file(self.notes_file)
            return {"shared_notes": ""}

    def save_notes(self):
        try:
            if os.path.exists(self.notes_file):
                self._backup_file(self.notes_file)

            temp_file = self.notes_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.notes_data, f, indent=2, ensure_ascii=False)

            if os.path.exists(self.notes_file):
                os.remove(self.notes_file)
            os.rename(temp_file, self.notes_file)
            return True
        except Exception as e:
            print(f"❌ ERROR saving notes: {e}")
            return False

    def get_shared_notes(self) -> str:
        return self.notes_data.get("shared_notes", "")

    def load_settings(self) -> Dict:
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {
                "timer_last_duration": 25,
                "auto_restart_timer": False,
                "outlook_sync_enabled": False,
                "auto_migrate_tasks": True,
                "layout": {
                    "show_timer": True,
                    "show_notes": True,
                    "show_monitor": True,
                    "matrix_position": "top",
                    "notes_position": "middle",
                    "bottom_position": "bottom"
                }
            }
        except Exception as e:
            print(f"❌ Error loading settings: {e}")
            return {}

    def save_settings(self):
        try:
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.settings_data, f, indent=2, ensure_ascii=False)

            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
            os.rename(temp_file, self.settings_file)
            return True
        except Exception as e:
            print(f"❌ ERROR saving settings: {e}")
            return False

    def run_startup_migration_for_today(self, today: date):
        auto_migrate = self.settings_data.get("auto_migrate_tasks", True)
        if auto_migrate:
            self._migrate_incomplete_tasks_to_target(today)

    def _migrate_incomplete_tasks_to_target(self, target_date: date):
        try:
            target_date_str = target_date.isoformat()
            self._ensure_day_exists(target_date)

            existing_signatures = self._existing_signatures_for_day(target_date)
            migration_count = 0

            for days_back in range(1, 8):
                previous_date = target_date - timedelta(days=days_back)
                previous_date_str = previous_date.isoformat()

                if previous_date_str not in self.tasks_data:
                    continue

                for quadrant in ["quadrant_1", "quadrant_2", "quadrant_3", "quadrant_4"]:
                    for task in self.tasks_data[previous_date_str].get(quadrant, []):
                        if task.get("completed", False):
                            continue

                        sig = (quadrant, self._task_signature(task))
                        if sig in existing_signatures:
                            continue

                        migrated_task = task.copy()
                        migrated_task["migrated_from"] = previous_date_str
                        migrated_task["migrated_on"] = target_date_str

                        self.tasks_data[target_date_str][quadrant].append(migrated_task)
                        existing_signatures.add(sig)
                        migration_count += 1

            if migration_count > 0:
                self.save_tasks()
                print(f"✓ Migrated {migration_count} incomplete tasks to {target_date_str}")

        except Exception as e:
            print(f"❌ Error during startup migration: {e}")

    def get_tasks_for_date(self, target_date: date) -> Dict:
        self._ensure_day_exists(target_date)
        return self.tasks_data.get(target_date.isoformat(), self._empty_day())

    def get_migration_summary(self, target_date: date) -> Dict:
        date_str = target_date.isoformat()

        if date_str not in self.tasks_data:
            return {"total": 0, "by_quadrant": {}, "source_dates": []}

        migrated_count = 0
        by_quadrant = {
            "quadrant_1": 0,
            "quadrant_2": 0,
            "quadrant_3": 0,
            "quadrant_4": 0
        }
        source_dates = set()

        for quadrant in ["quadrant_1", "quadrant_2", "quadrant_3", "quadrant_4"]:
            if quadrant in self.tasks_data[date_str]:
                for task in self.tasks_data[date_str][quadrant]:
                    if "migrated_from" in task:
                        migrated_count += 1
                        by_quadrant[quadrant] += 1
                        source_dates.add(task["migrated_from"])

        return {
            "total": migrated_count,
            "by_quadrant": by_quadrant,
            "source_dates": sorted(list(source_dates))
        }

    def add_task(self, target_date: date, quadrant: str, task_data: Dict) -> bool:
        try:
            date_str = target_date.isoformat()
            if date_str not in self.tasks_data:
                self.tasks_data[date_str] = self._empty_day()

            self.tasks_data[date_str][quadrant].append(task_data)
            return self.save_tasks()
        except Exception as e:
            print(f"❌ Error adding task: {e}")
            return False

    def update_task(self, target_date: date, quadrant: str, task_index: int, task_data: Dict) -> bool:
        try:
            date_str = target_date.isoformat()
            if date_str in self.tasks_data and quadrant in self.tasks_data[date_str]:
                if 0 <= task_index < len(self.tasks_data[date_str][quadrant]):
                    self.tasks_data[date_str][quadrant][task_index] = task_data
                    return self.save_tasks()
            return False
        except Exception as e:
            print(f"❌ Error updating task: {e}")
            return False

    def delete_task(self, target_date: date, quadrant: str, task_index: int) -> bool:
        try:
            date_str = target_date.isoformat()
            if date_str in self.tasks_data and quadrant in self.tasks_data[date_str]:
                if 0 <= task_index < len(self.tasks_data[date_str][quadrant]):
                    self.tasks_data[date_str][quadrant].pop(task_index)
                    return self.save_tasks()
            return False
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
            return False

    def get_notes_for_date(self, target_date: date) -> str:
        return self.get_shared_notes()

    def _backup_file(self, filepath: str):
        if os.path.exists(filepath):
            try:
                shutil.copy2(filepath, f"{filepath}.backup")
            except Exception:
                pass
