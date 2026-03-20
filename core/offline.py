"""Offline working copy management for GORO.

Workflow:
1. create_offline_copy() — copies a bid/project folder to the local data folder,
   stamps a baseline milestone, and marks both the live and local info.json.
2. detect_offline_changes() — diffs the local copy against its baseline to find
   what the user changed.
3. apply_offline_changes() — copies modified/added files back to the live record.
4. clear_offline_flag() — removes the checkout metadata from the live info.json.
5. get_affected_workbooks() — identifies which 4.Workbooks subfolders have changes
   so milestones can be created on them before merging.
"""

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from core.constants import INFO_FILE
from core.milestones import Milestone, compare_workbooks, create_milestone, list_milestones
from core.models import read_info, write_info


OFFLINE_BASELINE_MILESTONE_NAME = "offline_baseline"


def create_offline_copy(
    live_path: Path,
    local_root: Path,
    user: str,
) -> Tuple[Path, str]:
    """Create an offline working copy of a record.

    Copies the record folder to ``local_root/offline_copies/``, captures a
    baseline milestone inside the local copy for later diffing, and writes
    checkout metadata into both the live and local ``info.json`` files.

    Returns ``(local_copy_path, started_at_iso)``.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    copy_name = f"{live_path.name}_offline_{timestamp}"
    local_copies_dir = local_root / "offline_copies"
    local_copies_dir.mkdir(parents=True, exist_ok=True)
    local_copy_path = local_copies_dir / copy_name

    # Copy record folder to local (skip .milestones from the live source)
    local_copy_path.mkdir(parents=True, exist_ok=True)
    for item in live_path.iterdir():
        if item.name == ".milestones":
            continue
        if item.is_file():
            shutil.copy2(item, local_copy_path / item.name)
        elif item.is_dir():
            shutil.copytree(item, local_copy_path / item.name, dirs_exist_ok=True)

    started_at = datetime.now().isoformat()

    # Baseline milestone — the reference point we diff against on return
    create_milestone(
        local_copy_path,
        OFFLINE_BASELINE_MILESTONE_NAME,
        f"Offline baseline captured at checkout by {user} on {started_at[:10]}",
    )

    # Stamp offline metadata into the local copy's info.json
    local_info = read_info(local_copy_path)
    local_info["offline_mode"] = True
    local_info["offline_source_path"] = str(live_path)
    local_info["offline_baseline_name"] = OFFLINE_BASELINE_MILESTONE_NAME
    local_info["offline_checked_out_by"] = user
    local_info["offline_checked_out_at"] = started_at
    write_info(local_copy_path, local_info)

    # Stamp checkout flag into the live record's info.json
    live_info = read_info(live_path)
    live_info["offline_checkout_active"] = True
    live_info["offline_checkout_user"] = user
    live_info["offline_checkout_started_at"] = started_at
    live_info["offline_checkout_local_path"] = str(local_copy_path)
    write_info(live_path, live_info)

    return local_copy_path, started_at


def get_offline_baseline(local_path: Path) -> Optional[Milestone]:
    """Return the offline baseline milestone stored in a local copy, or None."""
    for ms in list_milestones(local_path):
        if ms.name == OFFLINE_BASELINE_MILESTONE_NAME:
            return ms
    return None


def detect_offline_changes(local_path: Path) -> dict:
    """Compare the local copy's current state against its offline baseline.

    Returns a :func:`~core.milestones.compare_workbooks` dict, or an empty
    dict if no baseline milestone is found.
    """
    baseline = get_offline_baseline(local_path)
    if baseline is None:
        return {}
    return compare_workbooks(local_path, baseline)


def clear_offline_flag(live_path: Path) -> None:
    """Remove offline checkout metadata from the live record's info.json."""
    info = read_info(live_path)
    for key in (
        "offline_checkout_active",
        "offline_checkout_user",
        "offline_checkout_started_at",
        "offline_checkout_local_path",
    ):
        info.pop(key, None)
    write_info(live_path, info)


def apply_offline_changes(local_path: Path, live_path: Path, changes: dict) -> int:
    """Copy modified and added files from the offline copy to the live record.

    ``info.json`` is intentionally skipped — it carries checkout metadata, not
    user data, and should never be overwritten on the live record.

    Returns the number of files copied.
    """
    copied = 0
    for rel_path in changes.get("modified", []) + changes.get("added", []):
        if Path(rel_path).name == INFO_FILE:
            continue
        src = local_path / rel_path
        dst = live_path / rel_path
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    return copied


def get_affected_workbooks(live_path: Path, changes: dict) -> List[Path]:
    """Return live workbook paths (inside ``4.Workbooks/``) that contain changed files.

    Used to decide which workbooks need a safety milestone before merging.
    """
    workbooks_dir = live_path / "4.Workbooks"
    if not workbooks_dir.exists():
        return []
    affected: set = set()
    all_rel = (
        changes.get("modified", [])
        + changes.get("added", [])
        + changes.get("removed", [])
    )
    for rel_path in all_rel:
        parts = Path(rel_path).parts
        if len(parts) >= 2 and parts[0] == "4.Workbooks":
            wb = workbooks_dir / parts[1]
            if wb.exists():
                affected.add(wb)
    return sorted(affected)
