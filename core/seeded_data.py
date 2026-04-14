from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

from PyQt6.QtCore import QSettings

from core.constants import APP_NAME, ORG_NAME
from core.models import resolve_data_root


def _resolve_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


_APP_ROOT = _resolve_app_root()
_SEED_DIR = _APP_ROOT / "seed_data"


def _csv_has_data_rows(path: Path) -> bool:
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if any(str(cell).strip() for cell in row):
                    return True
    except OSError:
        return False
    return False


def ensure_seeded_csv(filename: str) -> Path:
    """Return the live data path, repairing it from a seed copy when blank.

    This protects installed updates from carrying forward missing or header-only
    CSV files while still preserving legitimate user-customized populated files.
    """
    settings = QSettings(ORG_NAME, APP_NAME)
    live_path = resolve_data_root(settings) / filename
    seed_path = _SEED_DIR / filename

    should_restore = not live_path.exists() or not _csv_has_data_rows(live_path)
    if should_restore and seed_path.exists():
        live_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed_path, live_path)

    return live_path
