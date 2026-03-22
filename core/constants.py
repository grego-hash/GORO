"""Constants and configuration values for GORO 1.0."""

from PyQt6.QtGui import QColor

# ----------------------------
# App constants & defaults
# ----------------------------

ORG_NAME = "OropezaApps"
APP_NAME = "GORO 2.3"
APP_VERSION = "2.7.3"
APP_ID = "OropezaApps.GORO"
APP_DISPLAY_NAME = f"GORO {APP_VERSION}"

# 0 means check for updates on every app startup.
UPDATE_CHECK_INTERVAL_HOURS = 0
UPDATE_REQUEST_TIMEOUT_SECONDS = 8
DEFAULT_UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/grego-hash/GORO/main/updates.json"
DEFAULT_GITHUB_RELEASE_API_URL = "https://api.github.com/repos/grego-hash/GORO/releases/latest"

DEFAULT_NAME_TEMPLATES = {
    "bids": "Bid_{YYYY}-{###}",
}

INFO_FILE = "info.json"

BID_STATUSES = ["Pending", "Takeoff", "Revising", "Submitted", "Awarded", "Archived"]
PROJECT_STATUSES = ["Submittals", "Production", "Installation", "Punchlist", "Complete"]

# Light red for overdue rows
OVERDUE_BG = QColor(255, 235, 235)

DEFAULT_ACCENT_COLOR = "#7a0000"


def load_company_accent_color(data_root=None) -> str:
    """Return the company accent colour hex string from company_info.csv."""
    import csv
    from pathlib import Path

    if data_root is None:
        data_root = Path(__file__).resolve().parent.parent / "data"
    else:
        data_root = Path(data_root)
    ci_path = data_root / "company_info.csv"
    try:
        if ci_path.exists():
            with open(ci_path, "r", newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    val = row.get("Accent Color", "").strip()
                    if val:
                        return val
                    break
    except Exception:
        pass
    return DEFAULT_ACCENT_COLOR


def accent_text_color(hex_bg: str) -> str:
    """Return '#ffffff' or '#000000' for best contrast against *hex_bg*."""
    h = hex_bg.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except (ValueError, IndexError):
        return "#ffffff"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000000" if luminance > 150 else "#ffffff"














































