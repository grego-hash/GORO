"""Utility functions for GORO 1.0."""

import os
import platform
import shutil
import subprocess
from datetime import datetime, date
from functools import lru_cache
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox

from core.constants import BID_STATUSES


# ----------------------------
# Screen-aware sizing
# ----------------------------

def clamped_size(w: int, h: int, margin: int = 40) -> tuple[int, int]:
    """Return (width, height) clamped to the available screen geometry minus *margin*."""
    screen = QApplication.primaryScreen()
    if screen is not None:
        avail = screen.availableGeometry()
        w = min(w, avail.width() - margin)
        h = min(h, avail.height() - margin)
    return w, h


# ----------------------------
# OS helpers
# ----------------------------

@lru_cache(maxsize=1)
def get_system() -> str:
    """Get the OS system name (cached to avoid repeated WMI queries on Windows)."""
    return platform.system()


def open_in_file_manager(path: Path) -> None:
    """Open a folder in the OS file explorer."""
    try:
        if get_system() == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif get_system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        QMessageBox.warning(None, "Open Folder", f"Could not open folder:\n{e}")


def invalid_name_reason(name: str) -> Optional[str]:
    """Return a human-readable reason if the name is invalid; otherwise None."""
    name = name.strip()
    if not name:
        return "Name cannot be empty."
    if name in {".", ".."}:
        return "Invalid name."
    illegal = set('/\\:*?"<>|')
    if any(ch in illegal for ch in name):
        return r"Name cannot contain / \ : * ? \" < > |"
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if get_system() == "Windows" and name.upper() in reserved:
        return f"{name} is reserved on Windows."
    return None


def sanitize_name(name: str) -> str:
    """Remove invalid characters from a name."""
    name = name.strip()
    illegal = set('/\\:*?"<>|')
    sanitized = "".join(ch for ch in name if ch not in illegal)
    # If the result is a reserved name, append a suffix
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if get_system() == "Windows" and sanitized.upper() in reserved:
        sanitized += "_bid"
    return sanitized or "bid"


def human_bytes(num: int) -> str:
    """Format bytes as human-readable string."""
    size = float(num)
    for unit in ["B","KB","MB","GB","TB","PB"]:
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def dir_size(path: Path) -> int:
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file() and not p.is_symlink():
                total += p.stat().st_size
    except Exception:
        pass
    return total


# ----------------------------
# Name templating & autoincrement
# ----------------------------

def materialize_template(template: str, category: str) -> str:
    """Convert placeholders to concrete string (without number yet)."""
    year = datetime.now().year
    return template.replace("{YYYY}", str(year)).replace("{TYPE}", category[:-1].capitalize())


def next_increment_name(base_dir: Path, template: str, category: str) -> str:
    """
    Given a template like 'Bid_{YYYY}-{###}', find the next available number by scanning folders.
    """
    t = materialize_template(template, category)
    if "{###}" not in template:
        candidate = t
        if (base_dir / candidate).exists():
            i = 2
            while (base_dir / f"{candidate}_{i}").exists():
                i += 1
            return f"{candidate}_{i}"
        return candidate

    pre, post = t.split("{###}")
    max_n = 0
    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        if name.startswith(pre) and name.endswith(post):
            mid = name[len(pre): len(name) - len(post)]
            if mid.isdigit():
                max_n = max(max_n, int(mid))
    return f"{pre}{max_n+1:03d}{post}"


# ----------------------------
# Utils: due dates, sorting, duplicate names
# ----------------------------

def parse_due_date(due_str: Optional[str]) -> Optional[date]:
    if not due_str:
        return None
    try:
        y, m, d = [int(x) for x in due_str.split("-")]
        return date(y, m, d)
    except Exception:
        return None


def is_overdue(d: Optional[date]) -> bool:
    if d is None:
        return False
    return d < date.today()


def status_index(status: str) -> int:
    try:
        return BID_STATUSES.index(status)
    except ValueError:
        return len(BID_STATUSES)  # unknown at the end


def available_copy_name(base_dir: Path, base_name: str) -> str:
    """Generate '<name> - Copy', ' - Copy (2)' ... without collisions."""
    candidate = f"{base_name} - Copy"
    if not (base_dir / candidate).exists():
        return candidate
    n = 2
    while True:
        cand = f"{base_name} - Copy ({n})"
        if not (base_dir / cand).exists():
            return cand
        n += 1


def copy_template(template_path: Path, dest_path: Path) -> None:
    """Copy template folder structure to destination, skipping info.json."""
    if not template_path.exists():
        return
    
    dest_path.mkdir(parents=True, exist_ok=True)
    
    try:
        for item in template_path.iterdir():
            if item.is_file() and item.name != "info.json":
                shutil.copy2(item, dest_path / item.name)
            elif item.is_dir():
                subdir = dest_path / item.name
                copy_template(item, subdir)
    except Exception:
        pass  # Silently fail if template copying has issues

