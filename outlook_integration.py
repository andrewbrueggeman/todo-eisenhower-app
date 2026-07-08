"""
Outlook Calendar Integration Module

WHAT THIS SCRIPT DOES:
- Connects to the local Outlook desktop application
- Reads accepted meetings from the default Outlook calendar
- Converts meetings into Eisenhower Matrix tasks
- Supports periodic background synchronization
- Works even if no dedicated settings_manager exists
- Can also be run directly from the command line for a quick self-test

HOW TO USE IN YOUR APP:
- Import OutlookCalendarSync from this module
- Initialize it from ui/main_window.py like this:

    self.outlook_sync = OutlookCalendarSync(
        data_manager=self.data_manager,
        matrix_widget=self.matrix_widget
    )

- Because settings_manager is optional, this fixes your current startup error

HOW TO RUN A QUICK SELF-TEST FROM TERMINAL:
- From your project root directory:
    python3 outlook_integration.py --self-test

OPTIONAL SELF-TEST ARGUMENTS:
- --days-ahead 2
- --sync-interval 1800

NOTES:
- This script only reads accepted meetings
- Meetings are added as Quadrant 1 tasks by default
- Outlook connection is opened and closed safely inside each sync call
"""

import argparse
import datetime
import logging
import threading
import time
from typing import Any, Dict, List, Optional

import pythoncom
import win32com.client


class OutlookCalendarSync:
    def __init__(
        self,
        data_manager=None,
        matrix_widget=None,
        settings_manager=None,
        sync_interval: Optional[int] = None,
        days_ahead: Optional[int] = None,
    ):
        """
        Initialize Outlook calendar synchronization.

        Args:
            data_manager: App data manager used for reading and writing tasks
            matrix_widget: UI widget used to refresh the matrix after sync
            settings_manager: Optional settings manager with get_settings()
            sync_interval: Optional override for sync interval in seconds
            days_ahead: Optional override for how many days ahead to sync
        """
        self.data_manager = data_manager
        self.matrix_widget = matrix_widget
        self.settings_manager = settings_manager

        self.sync_thread = None
        self.stop_sync = False

        self.default_sync_interval = 3600
        self.default_days_ahead = 1

        self.sync_interval_override = sync_interval
        self.days_ahead_override = days_ahead

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Outlook integration initialized")

    def get_sync_settings(self) -> Dict[str, int]:
        """
        Resolve sync configuration from the best available source.

        Priority:
        1. Constructor overrides
        2. settings_manager.get_settings()
        3. data_manager.settings_data
        4. Defaults
        """
        settings = {
            "sync_interval": self.default_sync_interval,
            "days_ahead": self.default_days_ahead,
        }

        try:
            if self.settings_manager and hasattr(self.settings_manager, "get_settings"):
                loaded_settings = self.settings_manager.get_settings()
                if isinstance(loaded_settings, dict):
                    settings["sync_interval"] = int(
                        loaded_settings.get("outlook_sync_interval", settings["sync_interval"])
                    )
                    settings["days_ahead"] = int(
                        loaded_settings.get("outlook_days_ahead", settings["days_ahead"])
                    )

            elif self.data_manager and hasattr(self.data_manager, "settings_data"):
                if isinstance(self.data_manager.settings_data, dict):
                    settings["sync_interval"] = int(
                        self.data_manager.settings_data.get(
                            "outlook_sync_interval",
                            settings["sync_interval"],
                        )
                    )
                    settings["days_ahead"] = int(
                        self.data_manager.settings_data.get(
                            "outlook_days_ahead",
                            settings["days_ahead"],
                        )
                    )
        except Exception as e:
            self.logger.warning(f"Could not read Outlook sync settings: {e}")

        if self.sync_interval_override is not None:
            settings["sync_interval"] = int(self.sync_interval_override)

        if self.days_ahead_override is not None:
            settings["days_ahead"] = int(self.days_ahead_override)

        return settings

    def connect_to_outlook(self):
        """
        Connect to Outlook and return the namespace and calendar folder.

        Returns:
            tuple(namespace, calendar) if successful, otherwise (None, None)
        """
        try:
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook_app.GetNamespace("MAPI")
            calendar = namespace.GetDefaultFolder(9)

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connected to Outlook successfully")
            return namespace, calendar

        except Exception as e:
            self.logger.error(f"Failed to connect to Outlook: {str(e)}")
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Failed to connect to Outlook: {str(e)}")
            return None, None

    def get_accepted_meetings(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve accepted meetings from Outlook calendar for the given date range.

        Args:
            start_date: Beginning of date range
            end_date: End of date range

        Returns:
            A list of meeting dictionaries
        """
        meetings: List[Dict[str, Any]] = []

        try:
            pythoncom.CoInitialize()

            namespace, calendar = self.connect_to_outlook()
            if not namespace or not calendar:
                return []

            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

            restriction = (
                f"[Start] >= '{start_datetime.strftime('%m/%d/%Y %I:%M %p')}' "
                f"AND [Start] <= '{end_datetime.strftime('%m/%d/%Y %I:%M %p')}'"
            )

            appointments = calendar.Items
            appointments.Sort("[Start]")

            try:
                appointments.IncludeRecurrences = True
            except Exception:
                pass

            filtered_appointments = appointments.Restrict(restriction)

            for appointment in filtered_appointments:
                try:
                    response_status = getattr(appointment, "ResponseStatus", None)
                    if response_status != 3:
                        continue

                    entry_id = getattr(appointment, "EntryID", None)
                    subject = getattr(appointment, "Subject", None) or "Untitled Meeting"
                    location = getattr(appointment, "Location", None) or "No location specified"
                    start_value = getattr(appointment, "Start", None)

                    if not entry_id or not start_value:
                        continue

                    meetings.append(
                        {
                            "id": f"outlook_{entry_id}",
                            "title": subject,
                            "start_time": start_value.strftime("%H:%M"),
                            "location": location,
                            "date": start_value.date().isoformat(),
                            "source": "outlook",
                            "quadrant": 1,
                            "completed": False,
                            "created_at": datetime.datetime.now().isoformat(),
                        }
                    )

                except Exception as item_error:
                    self.logger.warning(f"Error processing appointment: {item_error}")
                    continue

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Found {len(meetings)} accepted meetings")
            return meetings

        except Exception as e:
            self.logger.error(f"Error retrieving meetings: {str(e)}")
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error retrieving meetings: {str(e)}")
            return []

        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

    def _build_task_text(self, meeting: Dict[str, Any]) -> str:
        """
        Build the task text shown inside the matrix.
        """
        line_break = chr(10)
        return (
            f"📅 {meeting['title']}"
            f"{line_break}⏰ {meeting['start_time']}"
            f"{line_break}📍 {meeting['location']}"
        )

    def _refresh_ui(self):
        """
        Refresh the matrix widget safely if available.
        """
        if not self.matrix_widget:
            return

        try:
            if hasattr(self.matrix_widget, "refresh_current_day"):
                if hasattr(self.matrix_widget, "after"):
                    self.matrix_widget.after(0, self.matrix_widget.refresh_current_day)
                else:
                    self.matrix_widget.refresh_current_day()
        except Exception as e:
            self.logger.warning(f"Could not refresh matrix widget: {e}")

    def sync_meetings_to_tasks(self):
        """
        Sync Outlook meetings into the app's task system.
        """
        if not self.data_manager:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] No data manager available, skipping task sync")
            return

        try:
            settings = self.get_sync_settings()

            today = datetime.date.today()
            end_date = today + datetime.timedelta(days=settings["days_ahead"])

            print(
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
                f"Syncing meetings from {today} to {end_date}"
            )

            meetings = self.get_accepted_meetings(today, end_date)

            if not meetings:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] No accepted meetings found")
                return

            synced_count = 0

            for meeting in meetings:
                existing_tasks = self.data_manager.get_tasks_by_date(meeting["date"])
                if not isinstance(existing_tasks, list):
                    existing_tasks = []

                meeting_exists = any(
                    task.get("id") == meeting["id"] and task.get("source") == "outlook"
                    for task in existing_tasks
                    if isinstance(task, dict)
                )

                if meeting_exists:
                    continue

                task_data = {
                    "id": meeting["id"],
                    "text": self._build_task_text(meeting),
                    "quadrant": meeting["quadrant"],
                    "completed": meeting["completed"],
                    "source": meeting["source"],
                    "created_at": meeting["created_at"],
                    "meeting_data": {
                        "title": meeting["title"],
                        "start_time": meeting["start_time"],
                        "location": meeting["location"],
                    },
                }

                self.data_manager.add_task(meeting["date"], task_data)
                synced_count += 1

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Synced {synced_count} new meetings")
            self._refresh_ui()

        except Exception as e:
            self.logger.error(f"Error during meeting sync: {str(e)}")
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sync failed: {str(e)}")

    def _sync_worker(self):
        """
        Worker thread for periodic synchronization.
        """
        self.sync_meetings_to_tasks()

        while not self.stop_sync:
            try:
                settings = self.get_sync_settings()
                sync_interval = int(settings["sync_interval"])

                elapsed = 0
                while elapsed < sync_interval and not self.stop_sync:
                    time.sleep(10)
                    elapsed += 10

                if not self.stop_sync:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Running scheduled sync")
                    self.sync_meetings_to_tasks()

            except Exception as e:
                self.logger.error(f"Error in sync worker: {str(e)}")
                time.sleep(60)

    def start_periodic_sync(self):
        """
        Start periodic background synchronization.
        """
        if self.sync_thread and self.sync_thread.is_alive():
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sync thread already running")
            return

        self.stop_sync = False
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()

        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Periodic sync started")

    def stop_periodic_sync(self):
        """
        Stop periodic background synchronization.
        """
        self.stop_sync = True

        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)

        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Periodic sync stopped")

    def manual_sync(self):
        """
        Run a one-time manual sync in a background thread.
        """
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Manual sync triggered")
        threading.Thread(target=self.sync_meetings_to_tasks, daemon=True).start()

    def cleanup(self):
        """
        Clean up resources on application shutdown.
        """
        self.stop_periodic_sync()


def run_self_test(days_ahead: int):
    """
    Command-line self-test for Outlook connectivity and meeting retrieval.
    """
    sync = OutlookCalendarSync(days_ahead=days_ahead)

    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)

    meetings = sync.get_accepted_meetings(today, end_date)

    print("---- SELF TEST RESULT ----")
    print(f"Date range: {today} to {end_date}")
    print(f"Accepted meetings found: {len(meetings)}")

    for index, meeting in enumerate(meetings[:10], start=1):
        print(
            f"{index}. "
            f"{meeting['date']} "
            f"{meeting['start_time']} "
            f"{meeting['title']} "
            f"@ {meeting['location']}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Outlook calendar integration helper")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run a standalone Outlook connectivity and meeting retrieval test",
    )
    parser.add_argument(
        "--days-ahead",
        type=int,
        default=1,
        help="Number of days ahead to inspect during self-test",
    )
    parser.add_argument(
        "--sync-interval",
        type=int,
        default=3600,
        help="Optional sync interval override in seconds",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.self_test:
        run_self_test(days_ahead=args.days_ahead)
    else:
        print("This module is normally imported by the main application.")
        print("Use --self-test if you want to verify Outlook access from the command line.")


if __name__ == "__main__":
    main()
