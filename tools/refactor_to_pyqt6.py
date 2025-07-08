#!/usr/bin/env python3
"""Bulk refactor helper to migrate project from PyQt5 to PyQt6.

Run once from project root:
    python tools/refactor_to_pyqt6.py

It will:
1. Replace import strings `PyQt5` → `PyQt6`.
2. Replace `PyQt6.QtChart` naming to `PyQt6.QtCharts` if needed.
3. Update `.exec_(` calls to `.exec(`.
4. Update High-DPI application attributes to new enum path.
The script prints each modified file path.
"""
from __future__ import annotations
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1] / "src"
patterns = [
    # (pattern, replacement)
    (re.compile(r"PyQt5\.QtChart"), "PyQt6.QtCharts"),
    (re.compile(r"PyQt5"), "PyQt6"),
    (re.compile(r"\.exec_\("), ".exec("),
    (
        re.compile(r"Qt\.AA_EnableHighDpiScaling"),
        "Qt.ApplicationAttribute.AA_EnableHighDpiScaling",
    ),
    (
        re.compile(r"Qt\.AA_UseHighDpiPixmaps"),
        "Qt.ApplicationAttribute.AA_UseHighDpiPixmaps",
    ),
]

changed_files = 0
for path in ROOT.rglob("*.py"):
    text = path.read_text(encoding="utf-8")
    new_text = text
    for pattern, repl in patterns:
        new_text = pattern.sub(repl, new_text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        changed_files += 1
        print("updated", path)
print(f"Refactor completed. {changed_files} files modified.") 