#!/usr/bin/env python3
"""Enable macOS two-finger scrolling with Tk 9 in Eisenhower Matrix.

Your diagnostic confirmed Tk 9.0.3 Aqua sends trackpad gestures as
<TouchpadScroll>, not <MouseWheel>. This updater adds TouchpadScroll support to
both Matrix quadrant lists and the task Add/Edit dialog.

Run from the top-level todo-eisenhower-app folder after quitting the app:
    python3 enable_tk9_mac_trackpad_scrolling_v6.py
"""
from __future__ import annotations

import ast
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
MATRIX_WIDGET = PROJECT_ROOT / "mac_version" / "ui" / "components" / "matrix_widget.py"
TASK_DIALOG = PROJECT_ROOT / "mac_version" / "ui" / "task_dialog.py"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def replace_once(text: str, old: str, new: str, description: str) -> str:
    count = text.count(old)
    if count != 1:
        fail(f"Could not apply '{description}': expected 1 matching block, found {count}. No files were changed.")
    return text.replace(old, new, 1)


def validate(path: Path, text: str) -> None:
    try:
        ast.parse(text, filename=str(path))
    except SyntaxError as error:
        fail(f"Updated {path.name} is not valid Python: {error}")


def backup_and_write(path: Path, text: str) -> None:
    backup = path.with_name(path.name + ".bak_before_tk9_touchpad_scroll_fix")
    if not backup.exists():
        shutil.copy2(path, backup)
        print(f"Created backup: {backup}")
    path.write_text(text, encoding="utf-8")
    print(f"Updated: {path}")


def update_matrix(text: str) -> str:
    text = replace_once(
        text,
        '''            self.app.root.bind_all(\n                "<Button-4>",\n                self._on_mousewheel_linux_up,\n                add="+"\n            )\n''',
        '''            self.app.root.bind_all(\n                "<TouchpadScroll>",\n                self._on_touchpad_scroll,\n                add="+"\n            )\n            self.app.root.bind_all(\n                "<Button-4>",\n                self._on_mousewheel_linux_up,\n                add="+"\n            )\n''',
        "Matrix TouchpadScroll binding",
    )

    text = replace_once(
        text,
        '''    def _on_mousewheel_linux_up(self, event):\n''',
        '''    def _touchpad_vertical_delta(self, event):\n        """Decode Tk 9's packed signed 16-bit deltaY from TouchpadScroll."""\n        packed_delta = int(getattr(event, "delta", 0))\n        delta_y = packed_delta & 0xFFFF\n\n        if delta_y >= 0x8000:\n            delta_y -= 0x10000\n\n        return delta_y\n\n    def _on_touchpad_scroll(self, event):\n        canvas = self._find_scroll_canvas(event.widget)\n\n        if canvas is None:\n            return None\n\n        delta_y = self._touchpad_vertical_delta(event)\n\n        if delta_y:\n            # Tk 9/Aqua provides a signed high-resolution vertical delta.\n            canvas.yview_scroll(-delta_y, "units")\n\n        return "break"\n\n    def _on_mousewheel_linux_up(self, event):\n''',
        "Matrix TouchpadScroll handler",
    )
    return text


def update_task_dialog(text: str) -> str:
    text = replace_once(
        text,
        '''        if widget_class == "Text":\n            widget.bind("<MouseWheel>", self._on_text_mousewheel)\n            widget.bind("<Button-4>", self._on_text_linux_scroll_up)\n''',
        '''        if widget_class == "Text":\n            widget.bind("<MouseWheel>", self._on_text_mousewheel)\n            widget.bind("<TouchpadScroll>", self._on_touchpad_scroll)\n            widget.bind("<Button-4>", self._on_text_linux_scroll_up)\n''',
        "dialog Text TouchpadScroll binding",
    )
    text = replace_once(
        text,
        '''        else:\n            widget.bind("<MouseWheel>", self._on_canvas_mousewheel)\n            widget.bind("<Button-4>", self._on_canvas_linux_scroll_up)\n''',
        '''        else:\n            widget.bind("<MouseWheel>", self._on_canvas_mousewheel)\n            widget.bind("<TouchpadScroll>", self._on_touchpad_scroll)\n            widget.bind("<Button-4>", self._on_canvas_linux_scroll_up)\n''',
        "dialog Canvas TouchpadScroll binding",
    )
    text = replace_once(
        text,
        '''    def _on_canvas_linux_scroll_up(self, event):\n''',
        '''    def _touchpad_vertical_delta(self, event):\n        """Decode Tk 9's packed signed 16-bit vertical TouchpadScroll delta."""\n        packed_delta = int(getattr(event, "delta", 0))\n        delta_y = packed_delta & 0xFFFF\n\n        if delta_y >= 0x8000:\n            delta_y -= 0x10000\n\n        return delta_y\n\n    def _on_touchpad_scroll(self, event):\n        delta_y = self._touchpad_vertical_delta(event)\n\n        if delta_y:\n            self._scroll_canvas(-delta_y)\n\n        return "break"\n\n    def _on_canvas_linux_scroll_up(self, event):\n''',
        "dialog TouchpadScroll handler",
    )
    return text


def main() -> None:
    if not MATRIX_WIDGET.is_file() or not TASK_DIALOG.is_file():
        fail("Run this from the top-level todo-eisenhower-app folder; expected the mac_version Matrix and task-dialog files.")

    original_matrix = MATRIX_WIDGET.read_text(encoding="utf-8")
    original_dialog = TASK_DIALOG.read_text(encoding="utf-8")
    updated_matrix = update_matrix(original_matrix)
    updated_dialog = update_task_dialog(original_dialog)

    validate(MATRIX_WIDGET, updated_matrix)
    validate(TASK_DIALOG, updated_dialog)
    backup_and_write(MATRIX_WIDGET, updated_matrix)
    backup_and_write(TASK_DIALOG, updated_dialog)

    print("\nTk 9 macOS TouchpadScroll support installed.")
    print("Restart with: cd mac_version && python3 main.py")


if __name__ == "__main__":
    main()
