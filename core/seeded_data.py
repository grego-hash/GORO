from __future__ import annotations

import csv
import shutil
from pathlib import Path


_APP_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _APP_ROOT / "data"
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
    live_path = _DATA_DIR / filename
    seed_path = _SEED_DIR / filename

    should_restore = not live_path.exists() or not _csv_has_data_rows(live_path)
    if should_restore and seed_path.exists():
        live_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed_path, live_path)

    return live_path
