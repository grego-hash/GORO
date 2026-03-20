"""Data models and filesystem operations for GORO 1.0."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QMessageBox

from core.constants import INFO_FILE


# ----------------------------
# Filesystem layout helpers
# ----------------------------

def ensure_dirs(root: Path) -> Tuple[Path, Path, Path, Path]:
    bids = root / "bids"
    projects = root / "projects"
    submitted = root / "submitted"
    awarded = root / "awarded"
    bids.mkdir(parents=True, exist_ok=True)
    projects.mkdir(parents=True, exist_ok=True)
    submitted.mkdir(parents=True, exist_ok=True)
    awarded.mkdir(parents=True, exist_ok=True)
    return bids, projects, submitted, awarded


def list_projects(projects_root: Path) -> List[Path]:
    if not projects_root.exists():
        return []
    return sorted([p for p in projects_root.iterdir() if p.is_dir()])


def list_bids(bids_root: Path) -> List[Path]:
    if not bids_root.exists():
        return []
    return sorted([p for p in bids_root.iterdir() if p.is_dir()])


def read_info(path: Path) -> Dict:
    fp = path / INFO_FILE
    if fp.exists():
        try:
            return json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def write_info(path: Path, payload: Dict) -> None:
    fp = path / INFO_FILE
    try:
        fp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        QMessageBox.warning(None, "info.json", f"Could not write info.json:\n{e}")


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


# ----------------------------
# Data model helpers
# ----------------------------

@dataclass
class Paths:
    root: Path
    bids: Path
    projects: Path
    submitted: Path
    awarded: Path


def get_paths(settings: QSettings) -> Paths:
    root_str = settings.value("root_dir", "", type=str)
    if root_str:
        root = Path(root_str)
    else:
        root = Path(__file__).resolve().parent.parent / "data"
    bids, projects, submitted, awarded = ensure_dirs(root)
    return Paths(root, bids, projects, submitted, awarded)

