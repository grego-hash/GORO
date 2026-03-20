"""Data models and filesystem operations for GORO 1.0."""

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


@dataclass(frozen=True)
class DataRootResolution:
    configured_root: Optional[Path]
    active_root: Path
    fallback_root: Path
    configured_available: bool
    using_fallback: bool


def default_data_root() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def unavailable_configured_data_root(settings: QSettings) -> Path | None:
    configured_root = str(settings.value("root_dir", "", type=str) or "").strip()
    if not configured_root:
        return None

    root = Path(configured_root)
    try:
        ensure_dirs(root)
    except OSError:
        return root
    return None


def resolve_data_root_state(settings: QSettings) -> DataRootResolution:
    configured_root_str = str(settings.value("root_dir", "", type=str) or "").strip()
    configured_root = Path(configured_root_str) if configured_root_str else None
    fallback_root = default_data_root()

    if configured_root is None:
        return DataRootResolution(
            configured_root=None,
            active_root=fallback_root,
            fallback_root=fallback_root,
            configured_available=False,
            using_fallback=False,
        )

    try:
        ensure_dirs(configured_root)
        return DataRootResolution(
            configured_root=configured_root,
            active_root=configured_root,
            fallback_root=fallback_root,
            configured_available=True,
            using_fallback=False,
        )
    except OSError:
        return DataRootResolution(
            configured_root=configured_root,
            active_root=fallback_root,
            fallback_root=fallback_root,
            configured_available=False,
            using_fallback=True,
        )


def export_data_root_changes(source_root: Path, destination_root: Path) -> Tuple[int, int]:
    ensure_dirs(destination_root)

    copied_files = 0
    skipped_files = 0
    for source_path in source_root.rglob("*"):
        relative_path = source_path.relative_to(source_root)
        destination_path = destination_root / relative_path

        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        should_copy = True
        if destination_path.exists():
            try:
                source_stat = source_path.stat()
                dest_stat = destination_path.stat()
                should_copy = (
                    source_stat.st_size != dest_stat.st_size
                    or source_stat.st_mtime > dest_stat.st_mtime + 1e-6
                )
            except OSError:
                should_copy = True

        if should_copy:
            shutil.copy2(source_path, destination_path)
            copied_files += 1
        else:
            skipped_files += 1

    return copied_files, skipped_files


def resolve_data_root(settings: QSettings) -> Path:
    return resolve_data_root_state(settings).active_root


def get_paths(settings: QSettings) -> Paths:
    root = resolve_data_root(settings)
    bids, projects, submitted, awarded = ensure_dirs(root)
    return Paths(root, bids, projects, submitted, awarded)

