"""Helpers for checking and prompting application updates."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QUrl

from core.constants import (
    DEFAULT_UPDATE_MANIFEST_URL,
    UPDATE_CHECK_INTERVAL_HOURS,
    UPDATE_REQUEST_TIMEOUT_SECONDS,
)


@dataclass(frozen=True)
class UpdateInfo:
    """Normalized update manifest values."""

    latest_version: str
    download_url: str
    release_notes: str = ""


def _to_bool(value: Any, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_version(version: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", version or "")
    if not parts:
        return (0,)
    return tuple(int(part) for part in parts[:4])


def _is_newer_version(latest: str, current: str) -> bool:
    latest_tuple = _normalize_version(latest)
    current_tuple = _normalize_version(current)
    for latest_part, current_part in zip_longest(latest_tuple, current_tuple, fillvalue=0):
        if latest_part > current_part:
            return True
        if latest_part < current_part:
            return False
    return False


def _parse_manifest(payload: dict[str, Any]) -> UpdateInfo | None:
    latest_version = str(payload.get("latest_version") or payload.get("version") or "").strip()
    download_url = str(
        payload.get("download_url")
        or payload.get("url")
        or payload.get("installer_url")
        or ""
    ).strip()
    release_notes = str(payload.get("release_notes") or payload.get("notes") or "").strip()

    if not latest_version:
        return None
    return UpdateInfo(latest_version=latest_version, download_url=download_url, release_notes=release_notes)


def _is_absolute_url(value: str) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme)


def _resolve_local_installer_url(manifest_path: Path, update: UpdateInfo) -> str:
    # Hosted URLs are usable as-is.
    if _is_absolute_url(update.download_url):
        parsed = urlparse(update.download_url)
        if parsed.scheme.lower() in {"http", "https"}:
            return update.download_url

        # For local file URLs, prefer same-folder resolution by filename.
        if parsed.scheme.lower() == "file":
            installer_name = Path(parsed.path).name
            if installer_name:
                candidate = (manifest_path.parent / installer_name).resolve()
                if candidate.is_file():
                    return candidate.as_uri()

    # Relative installer path in manifest: resolve relative to manifest folder.
    if update.download_url:
        absolute_hint = Path(update.download_url)
        if absolute_hint.is_absolute():
            installer_name = absolute_hint.name
            if installer_name:
                candidate = (manifest_path.parent / installer_name).resolve()
                if candidate.is_file():
                    return candidate.as_uri()

        candidate = (manifest_path.parent / update.download_url).resolve()
        if candidate.is_file():
            return candidate.as_uri()

    # No path provided (or file missing): find installer in the same folder.
    version = re.escape(update.latest_version)
    pattern = f"GORO-Setup-{version}-*.exe"
    matches = sorted(
        manifest_path.parent.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if matches:
        return matches[0].resolve().as_uri()

    return ""


def _fetch_manifest(manifest_url: str, timeout_seconds: int) -> dict[str, Any] | None:
    request = Request(
        manifest_url,
        headers={
            "User-Agent": "GORO-UpdateChecker/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
            payload = json.loads(body)
            if isinstance(payload, dict):
                return payload
            return None
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def _fetch_manifest_file(manifest_path: Path) -> dict[str, Any] | None:
    try:
        # Accept UTF-8 files both with and without BOM.
        body = manifest_path.read_text(encoding="utf-8-sig")
        payload = json.loads(body)
        if isinstance(payload, dict):
            return payload
        return None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _resolve_local_manifest_path(settings: QSettings) -> Path | None:
    configured_path = str(settings.value("updates/manifest_path", "")).strip()
    if configured_path:
        candidate = Path(configured_path)
        if candidate.exists() and candidate.is_file():
            return candidate

    root_dir = str(settings.value("root_dir", "")).strip()
    if root_dir:
        root = Path(root_dir)
    else:
        root = Path(__file__).resolve().parent.parent / "data"

    candidate = root / "updates.json"  # inside selected data folder
    if candidate.exists() and candidate.is_file():
        return candidate
    return None


def _resolve_remote_manifest_url(settings: QSettings) -> str:
    manifest_url = str(settings.value("updates/manifest_url", "")).strip()
    if manifest_url:
        return manifest_url

    manifest_url = os.environ.get("GORO_UPDATE_URL", "").strip()
    if manifest_url:
        return manifest_url

    return DEFAULT_UPDATE_MANIFEST_URL.strip()


def _should_check_now(settings: QSettings, interval_hours: int) -> bool:
    if interval_hours <= 0:
        return True

    last_check = str(settings.value("updates/last_check_utc", "")).strip()
    if not last_check:
        return True

    try:
        last_check_dt = datetime.fromisoformat(last_check)
    except ValueError:
        return True

    if last_check_dt.tzinfo is None:
        last_check_dt = last_check_dt.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) >= last_check_dt + timedelta(hours=interval_hours)


def _record_check_time(settings: QSettings) -> None:
    settings.setValue("updates/last_check_utc", datetime.now(timezone.utc).isoformat())


def _open_download_target(download_url: str) -> tuple[bool, str]:
    qurl = QUrl.fromUserInput(download_url)

    if qurl.isLocalFile():
        local_path = Path(qurl.toLocalFile())
        if not local_path.is_file():
            return False, f"Installer not found:\n{local_path}"

        try:
            if os.name == "nt":
                os.startfile(str(local_path))  # type: ignore[attr-defined]
                return True, ""

            if QDesktopServices.openUrl(QUrl.fromLocalFile(str(local_path))):
                return True, ""

            return False, f"Could not open installer:\n{local_path}"
        except Exception as exc:
            return False, f"Could not open installer:\n{local_path}\n\n{exc}"

    if QDesktopServices.openUrl(qurl):
        return True, ""

    return False, f"Could not open update URL:\n{download_url}"


def _show_update_prompt(parent: QWidget | None, settings: QSettings, update: UpdateInfo) -> None:
    skipped_version = str(settings.value("updates/skipped_version", "")).strip()
    if skipped_version == update.latest_version:
        return

    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Information)
    dialog.setWindowTitle("Update Available")
    dialog.setText(f"A new version is available: {update.latest_version}")

    if update.release_notes:
        dialog.setInformativeText(update.release_notes)
    else:
        dialog.setInformativeText("Would you like to download the latest installer now?")

    download_button = dialog.addButton("Download", QMessageBox.ButtonRole.AcceptRole)
    skip_button = dialog.addButton("Skip This Version", QMessageBox.ButtonRole.DestructiveRole)
    dialog.addButton("Later", QMessageBox.ButtonRole.RejectRole)

    dialog.exec()
    clicked = dialog.clickedButton()

    if clicked == download_button:
        opened, error_message = _open_download_target(update.download_url)
        if not opened:
            QMessageBox.warning(parent, "Update Download", error_message)
        return
    if clicked == skip_button:
        settings.setValue("updates/skipped_version", update.latest_version)


def check_for_updates_manual(
    parent: QWidget | None,
    settings: QSettings,
    current_version: str,
) -> None:
    """Manually triggered update check — bypasses throttle and always gives feedback."""
    payload = None
    used_local_manifest = False

    manifest_url = _resolve_remote_manifest_url(settings)
    if manifest_url:
        payload = _fetch_manifest(manifest_url, UPDATE_REQUEST_TIMEOUT_SECONDS)

    local_manifest = _resolve_local_manifest_path(settings)
    if not payload and local_manifest is not None:
        used_local_manifest = True
        payload = _fetch_manifest_file(local_manifest)
        if payload is None:
            QMessageBox.information(
                parent,
                "Check for Updates",
                f"Found update manifest at:\n{local_manifest}\n\nBut it is not valid JSON.",
            )
            return

    if not payload:
        QMessageBox.information(parent, "Check for Updates", "No update manifest found. Could not check for updates.")
        return

    update = _parse_manifest(payload)
    if not update:
        QMessageBox.information(parent, "Check for Updates", "Update manifest is invalid or unreadable.")
        return

    if used_local_manifest and local_manifest is not None:
        update = UpdateInfo(
            latest_version=update.latest_version,
            download_url=_resolve_local_installer_url(local_manifest, update),
            release_notes=update.release_notes,
        )

    if not update.download_url:
        QMessageBox.information(parent, "Check for Updates", "Update manifest found, but download_url is missing or invalid.")
        return

    if not _is_newer_version(update.latest_version, current_version):
        QMessageBox.information(parent, "Check for Updates", f"You're up to date!\nCurrent version: {current_version}")
        return

    # Reset any skipped version so the prompt always shows for manual checks
    settings.remove("updates/skipped_version")
    _show_update_prompt(parent, settings, update)


def check_for_updates_on_startup(
    parent: QWidget | None,
    settings: QSettings,
    current_version: str,
) -> None:
    """Check for updates and optionally prompt user with a Download action."""
    if not _to_bool(settings.value("updates/enabled", True), default=True):
        return
    if not _should_check_now(settings, UPDATE_CHECK_INTERVAL_HOURS):
        return

    payload = None
    used_local_manifest = False

    manifest_url = _resolve_remote_manifest_url(settings)
    if manifest_url:
        payload = _fetch_manifest(manifest_url, UPDATE_REQUEST_TIMEOUT_SECONDS)

    local_manifest = _resolve_local_manifest_path(settings)
    if not payload and local_manifest is not None:
        used_local_manifest = True
        payload = _fetch_manifest_file(local_manifest)

    _record_check_time(settings)
    if not payload:
        return

    update = _parse_manifest(payload)
    if not update:
        return

    if used_local_manifest and local_manifest is not None:
        update = UpdateInfo(
            latest_version=update.latest_version,
            download_url=_resolve_local_installer_url(local_manifest, update),
            release_notes=update.release_notes,
        )

    if not update.download_url:
        return

    if not _is_newer_version(update.latest_version, current_version):
        return

    _show_update_prompt(parent, settings, update)
