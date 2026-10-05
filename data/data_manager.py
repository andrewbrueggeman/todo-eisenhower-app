"""
Enhanced Data Manager for Eisenhower Matrix To-Do Application
With startup-only automatic task migration, safer date normalization,
task reordering/move helpers for same-date quadrant organization,
and packaged-app data stored in a folder NEXT TO the .app bundle.

Migration behavior:
    Incomplete tasks from prior days are MOVED to the target day, not copied.
    Completed tasks remain on their original dates.
"""
import json
import os
import shutil
import sys
from datetime import date, datetime, timedelta
from typing import Dict


class DataManager:
    QUADRANTS = ("quadrant_1", "quadrant_2", "quadrant_3", "quadrant_4")

    DEFAULT_QUADRANT_NAMES = {
        "quadrant_1": "Critical Actions",
        "quadrant_2": "Strategic Work",
        "quadrant_3": "Routine Tasks",
        "quadrant_4": "Backlog/Opportunities"
    }

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
            store data in a sibling folder NEXT TO the .app bundle

        Example:
            dist/
                Eisenhower Matrix.app
                EisenhowerMatrixData/

        Source run:
            use project_root/data_files
        """
        if getattr(sys, "frozen", False):
            executable_dir = os.path.dirname(os.path.abspath(sys.executable))
            app_contents_dir = os.path.dirname(executable_dir)
            app_bundle_dir = os.path.dirname(app_contents_dir)
            app_parent_dir = os.path.dirname(app_bundle_dir)

            return os.path.join(app_parent_dir, "EisenhowerMatrixData")

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
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

    def _default_settings(self):
        return {
            "default_timer_duration": "25",
            "timer_last_duration": "25",
            "auto_restart_timer": False,
            "outlook_sync_enabled": False,
            "auto_migrate_tasks": True,
            "matrix_view_mode": "1_day",
            "quadrant_names": self.DEFAULT_QUADRANT_NAMES.copy(),
            "layout": {
                "show_timer": True,
                "show_notes": True,
                "show_monitor": True,
                "matrix_position": "top",
                "notes_position": "middle",
                "bottom_position": "bottom"
            }
        }

    def _empty_day(self) -> Dict:
        return {
            "quadrant_1": [],
            "quadrant_2": [],
            "quadrant_3": [],
            "quadrant_4": []
        }

    def _normalize_date(self, value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            value = value.strip()

            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        return None

    def _date_to_key(self, value):
        normalized = self._normalize_date(value)

        if normalized is None:
            raise ValueError(f"Invalid date value: {value}")

        return normalized.isoformat()

    def _ensure_day_exists(self, target_date):
        date_str = self._date_to_key(target_date)

        if date_str not in self.tasks_data:
            self.tasks_data[date_str] = self._empty_day()

    def _normalize_task(
        self,
        task: Dict,
        fallback_date=None,
        fallback_quadrant=None
    ):
        if not isinstance(task, dict):
            return None

        normalized = dict(task)
        normalized["text"] = str(task.get("text", "")).strip()
        normalized["notes"] = str(task.get("notes", "")).strip()
        normalized["completed"] = bool(task.get("completed", False))
        normalized["quadrant"] = task.get(
            "quadrant",
            fallback_quadrant or "quadrant_1"
        )

        task_date = (
            self._normalize_date(task.get("date"))
            or self._normalize_date(fallback_date)
        )

        if task_date is not None:
            normalized["date"] = task_date.isoformat()

        for field in ("migrated_from", "migrated_on"):
            if field in normalized:
                normalized_field_date = self._normalize_date(
                    normalized.get(field)
                )

                if normalized_field_date is not None:
                    normalized[field] = normalized_field_date.isoformat()

        return normalized

    def _normalize_day_data(self, day_data, fallback_date):
        normalized_day = self._empty_day()

        if not isinstance(day_data, dict):
            return normalized_day

        for quadrant in self.QUADRANTS:
            tasks = day_data.get(quadrant, [])

            if not isinstance(tasks, list):
                continue

            for task in tasks:
                normalized_task = self._normalize_task(
                    task,
                    fallback_date=fallback_date,
                    fallback_quadrant=quadrant
                )

                if normalized_task and normalized_task.get("text"):
                    normalized_day[quadrant].append(normalized_task)

        return normalized_day

    def _normalize_tasks_data(self, raw_data):
        normalized = {}

        if not isinstance(raw_data, dict):
            return normalized

        for raw_date_key, raw_day_data in raw_data.items():
            normalized_date = self._normalize_date(raw_date_key)

            if normalized_date is None:
                continue

            date_key = normalized_date.isoformat()

            if date_key not in normalized:
                normalized[date_key] = self._empty_day()

            normalized_day = self._normalize_day_data(
                raw_day_data,
                fallback_date=date_key
            )

            for quadrant in self.QUADRANTS:
                normalized[date_key][quadrant].extend(
                    normalized_day[quadrant]
                )

        return normalized

    def _task_signature(self, task: Dict) -> tuple:
        return (
            task.get("text", "").strip(),
            task.get("notes", "").strip(),
            bool(task.get("completed", False))
        )

    def _existing_signatures_for_day(self, target_date) -> set:
        date_str = self._date_to_key(target_date)
        signatures = set()

        if date_str not in self.tasks_data:
            return signatures

        for quadrant in self.QUADRANTS:
            for task in self.tasks_data[date_str].get(quadrant, []):
                signatures.add((quadrant, self._task_signature(task)))

        return signatures

    def load_tasks(self) -> Dict:
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    return self._normalize_tasks_data(raw_data)

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
                json.dump(
                    self.tasks_data,
                    f,
                    indent=2,
                    default=str,
                    ensure_ascii=False
                )

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
                    return (
                        data
                        if isinstance(data, dict)
                        else {"shared_notes": ""}
                    )

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
                json.dump(
                    self.notes_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

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
        defaults = self._default_settings()

        try:
            if not os.path.exists(self.settings_file):
                return defaults

            with open(self.settings_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            if not isinstance(loaded, dict):
                return defaults

            layout = loaded.get("layout", {})
            if not isinstance(layout, dict):
                layout = {}

            saved_quadrant_names = loaded.get("quadrant_names", {})
            if not isinstance(saved_quadrant_names, dict):
                saved_quadrant_names = {}

            merged = defaults.copy()
            merged.update(
                {
                    key: value
                    for key, value in loaded.items()
                    if key not in ("layout", "quadrant_names")
                }
            )

            merged_layout = defaults["layout"].copy()
            merged_layout.update(layout)
            merged["layout"] = merged_layout

            merged_quadrant_names = defaults["quadrant_names"].copy()

            for quadrant_id in self.QUADRANTS:
                saved_name = saved_quadrant_names.get(quadrant_id)

                if isinstance(saved_name, str) and saved_name.strip():
                    merged_quadrant_names[quadrant_id] = saved_name.strip()

            merged["quadrant_names"] = merged_quadrant_names

            if "default_timer_duration" not in merged:
                merged["default_timer_duration"] = str(
                    merged.get("timer_last_duration", "25")
                )
            else:
                merged["default_timer_duration"] = str(
                    merged["default_timer_duration"]
                )

            merged["timer_last_duration"] = str(
                merged.get(
                    "timer_last_duration",
                    merged["default_timer_duration"]
                )
            )

            return merged

        except Exception as e:
            print(f"❌ Error loading settings: {e}")
            return defaults

    def save_settings(self):
        try:
            temp_file = self.settings_file + ".tmp"

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.settings_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)

            os.rename(temp_file, self.settings_file)

            return True

        except Exception as e:
            print(f"❌ ERROR saving settings: {e}")
            return False

    def run_startup_migration_for_today(self, today):
        auto_migrate = self.settings_data.get("auto_migrate_tasks", True)

        if auto_migrate:
            self._migrate_incomplete_tasks_to_target(today)

    def _migrate_incomplete_tasks_to_target(self, target_date):
        """
        Move incomplete tasks from prior days to the target date.

        Important behavior:
            - Incomplete prior-day tasks are moved, not copied.
            - The source task is removed from the prior date.
            - If the same task already exists on the target date, the prior-day
              copy is still removed to prevent duplicate lingering tasks.
            - Completed prior-day tasks are left untouched.
            - Migration scans the previous 7 days.
        """
        try:
            target_date_obj = self._normalize_date(target_date)

            if target_date_obj is None:
                return

            target_date_str = target_date_obj.isoformat()
            self._ensure_day_exists(target_date_obj)

            existing_signatures = self._existing_signatures_for_day(
                target_date_obj
            )

            moved_count = 0
            removed_duplicate_count = 0
            changed = False

            for days_back in range(1, 8):
                previous_date = target_date_obj - timedelta(days=days_back)
                previous_date_str = previous_date.isoformat()

                if previous_date_str not in self.tasks_data:
                    continue

                for quadrant in self.QUADRANTS:
                    original_tasks = self.tasks_data[
                        previous_date_str
                    ].get(quadrant, [])

                    if not isinstance(original_tasks, list):
                        self.tasks_data[previous_date_str][quadrant] = []
                        changed = True
                        continue

                    remaining_tasks = []

                    for task in original_tasks:
                        if task.get("completed", False):
                            remaining_tasks.append(task)
                            continue

                        signature = (
                            quadrant,
                            self._task_signature(task)
                        )

                        if signature not in existing_signatures:
                            migrated_task = task.copy()
                            migrated_task["migrated_from"] = previous_date_str
                            migrated_task["migrated_on"] = target_date_str
                            migrated_task["date"] = target_date_str
                            migrated_task["quadrant"] = quadrant

                            self.tasks_data[target_date_str][quadrant].append(
                                migrated_task
                            )

                            existing_signatures.add(signature)
                            moved_count += 1

                        else:
                            removed_duplicate_count += 1

                        changed = True

                    self.tasks_data[previous_date_str][quadrant] = (
                        remaining_tasks
                    )

            if changed:
                self.save_tasks()

                if moved_count > 0 and removed_duplicate_count > 0:
                    print(
                        f"✓ Moved {moved_count} incomplete tasks to "
                        f"{target_date_str}; removed "
                        f"{removed_duplicate_count} duplicate prior-day tasks"
                    )

                elif moved_count > 0:
                    print(
                        f"✓ Moved {moved_count} incomplete tasks to "
                        f"{target_date_str}"
                    )

                elif removed_duplicate_count > 0:
                    print(
                        f"✓ Removed {removed_duplicate_count} duplicate "
                        f"prior-day tasks already present on {target_date_str}"
                    )

        except Exception as e:
            print(f"❌ Error during startup migration: {e}")

    def get_tasks_for_date(self, target_date) -> Dict:
        date_str = self._date_to_key(target_date)
        self._ensure_day_exists(date_str)

        return self.tasks_data.get(date_str, self._empty_day())

    def get_migration_summary(self, target_date) -> Dict:
        date_str = self._date_to_key(target_date)

        if date_str not in self.tasks_data:
            return {
                "total": 0,
                "by_quadrant": {},
                "source_dates": []
            }

        migrated_count = 0
        by_quadrant = {
            "quadrant_1": 0,
            "quadrant_2": 0,
            "quadrant_3": 0,
            "quadrant_4": 0
        }
        source_dates = set()

        for quadrant in self.QUADRANTS:
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

    def add_task(self, target_date, quadrant: str, task_data: Dict) -> bool:
        try:
            date_str = self._date_to_key(target_date)

            if date_str not in self.tasks_data:
                self.tasks_data[date_str] = self._empty_day()

            normalized_task = self._normalize_task(
                task_data,
                fallback_date=date_str,
                fallback_quadrant=quadrant
            )
            normalized_task["date"] = date_str
            normalized_task["quadrant"] = quadrant

            self.tasks_data[date_str][quadrant].append(normalized_task)

            return self.save_tasks()

        except Exception as e:
            print(f"❌ Error adding task: {e}")
            return False

    def update_task(
        self,
        target_date,
        quadrant: str,
        task_index: int,
        task_data: Dict
    ) -> bool:
        try:
            date_str = self._date_to_key(target_date)

            if (
                date_str in self.tasks_data
                and quadrant in self.tasks_data[date_str]
            ):
                if 0 <= task_index < len(
                    self.tasks_data[date_str][quadrant]
                ):
                    normalized_task = self._normalize_task(
                        task_data,
                        fallback_date=date_str,
                        fallback_quadrant=quadrant
                    )
                    normalized_task["date"] = date_str
                    normalized_task["quadrant"] = quadrant

                    self.tasks_data[date_str][quadrant][task_index] = (
                        normalized_task
                    )

                    return self.save_tasks()

            return False

        except Exception as e:
            print(f"❌ Error updating task: {e}")
            return False

    def delete_task(
        self,
        target_date,
        quadrant: str,
        task_index: int
    ) -> bool:
        try:
            date_str = self._date_to_key(target_date)

            if (
                date_str in self.tasks_data
                and quadrant in self.tasks_data[date_str]
            ):
                if 0 <= task_index < len(
                    self.tasks_data[date_str][quadrant]
                ):
                    self.tasks_data[date_str][quadrant].pop(task_index)

                    return self.save_tasks()

            return False

        except Exception as e:
            print(f"❌ Error deleting task: {e}")
            return False

    def move_task_within_quadrant(
        self,
        target_date,
        quadrant: str,
        task_index: int,
        direction: str
    ) -> bool:
        try:
            date_str = self._date_to_key(target_date)

            if date_str not in self.tasks_data:
                return False

            if quadrant not in self.tasks_data[date_str]:
                return False

            tasks = self.tasks_data[date_str][quadrant]

            if not (0 <= task_index < len(tasks)):
                return False

            if direction == "up":
                if task_index == 0:
                    return False

                tasks[task_index - 1], tasks[task_index] = (
                    tasks[task_index],
                    tasks[task_index - 1]
                )

            elif direction == "down":
                if task_index >= len(tasks) - 1:
                    return False

                tasks[task_index + 1], tasks[task_index] = (
                    tasks[task_index],
                    tasks[task_index + 1]
                )

            elif direction == "top":
                if task_index == 0:
                    return False

                task = tasks.pop(task_index)
                tasks.insert(0, task)

            elif direction == "bottom":
                if task_index >= len(tasks) - 1:
                    return False

                task = tasks.pop(task_index)
                tasks.append(task)

            else:
                return False

            return self.save_tasks()

        except Exception as e:
            print(f"❌ Error moving task within quadrant: {e}")
            return False

    def move_task_to_quadrant(
        self,
        target_date,
        from_quadrant: str,
        task_index: int,
        to_quadrant: str
    ) -> bool:
        try:
            date_str = self._date_to_key(target_date)

            if to_quadrant not in self.QUADRANTS:
                return False

            if date_str not in self.tasks_data:
                return False

            if from_quadrant not in self.tasks_data[date_str]:
                return False

            if to_quadrant not in self.tasks_data[date_str]:
                self.tasks_data[date_str][to_quadrant] = []

            source_tasks = self.tasks_data[date_str][from_quadrant]

            if not (0 <= task_index < len(source_tasks)):
                return False

            if from_quadrant == to_quadrant:
                return False

            task = source_tasks.pop(task_index)
            task["quadrant"] = to_quadrant
            task["date"] = date_str

            self.tasks_data[date_str][to_quadrant].append(task)

            return self.save_tasks()

        except Exception as e:
            print(f"❌ Error moving task to another quadrant: {e}")
            return False

    def get_notes_for_date(self, target_date) -> str:
        return self.get_shared_notes()

    def _backup_file(self, filepath: str):
        if os.path.exists(filepath):
            try:
                shutil.copy2(filepath, f"{filepath}.backup")
            except Exception:
                pass
