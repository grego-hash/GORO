"""Constants and configuration values for GORO 1.0."""

from PyQt6.QtGui import QColor

# ----------------------------
# App constants & defaults
# ----------------------------

ORG_NAME = "OropezaApps"
APP_NAME = "GORO 2.3"
APP_VERSION = "2.5.8"
APP_ID = "OropezaApps.GORO"
APP_DISPLAY_NAME = f"GORO {APP_VERSION}"

# 0 means check for updates on every app startup.
UPDATE_CHECK_INTERVAL_HOURS = 0
UPDATE_REQUEST_TIMEOUT_SECONDS = 3
DEFAULT_UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/grego-hash/GORO/main/updates.json"

DEFAULT_NAME_TEMPLATES = {
    "bids": "Bid_{YYYY}-{###}",
}

INFO_FILE = "info.json"

BID_STATUSES = ["Pending", "Takeoff", "Revising", "Submitted", "Awarded", "Archived"]
PROJECT_STATUSES = ["Submittals", "Production", "Installation", "Punchlist", "Complete"]

# Light red for overdue rows
OVERDUE_BG = QColor(255, 235, 235)































