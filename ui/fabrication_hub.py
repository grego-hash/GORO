"""Fabrication Hub dialog.

Central dialog for fabrication-related tools. Currently hosts the
Prep Codes / Templates editor, with room to add more categories later.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.utils import clamped_size

_FAB_DEFAULTS_PATH = Path.home() / ".goro" / "fab_defaults.json"


def load_fab_defaults() -> dict:
    """Return fab defaults dict with keys 'width_deduction' and 'undercut'."""
    defaults = {"width_deduction": "3/16", "undercut": "3/4"}
    try:
        if _FAB_DEFAULTS_PATH.exists():
            with open(_FAB_DEFAULTS_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                defaults.update(stored)
    except Exception:
        pass
    return defaults


def _save_fab_defaults(data: dict) -> None:
    _FAB_DEFAULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_FAB_DEFAULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _hub_button(title: str, description: str, callback) -> QPushButton:
    btn = QPushButton(f"{title}\n{description}")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    btn.setMinimumHeight(60)
    btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
    btn.setStyleSheet(
        "QPushButton { text-align: left; padding: 12px 16px; "
        "border: 1px solid #555; border-radius: 6px; background: #2a2a2a; color: #e0e0e0; }"
        "QPushButton:hover { background: #333; border-color: #007acc; }"
    )
    btn.clicked.connect(callback)
    return btn


class FabricationHubDialog(QDialog):
    """Landing dialog for fabrication-related tools."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Fabrication")
        self.resize(*clamped_size(500, 400))
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("Fabrication")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #ffffff;")
        root.addWidget(title)

        subtitle = QLabel("Tools for door fabrication sheets, prep codes, and machining templates.")
        subtitle.setStyleSheet("color: #aaa; font-size: 11px;")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        root.addSpacing(8)

        # Prep Codes / Templates button
        btn_prep = _hub_button(
            "Prep Codes / Templates",
            "View, add, and edit the master prep-code lookup table.",
            self._open_prep_codes,
        )
        root.addWidget(btn_prep)

        # Lock Models button
        btn_lock_models = _hub_button(
            "Lock Models",
            "View, add, and edit lock model details by locktype (Mortise, Cylindrical, etc.).",
            self._open_lock_models,
        )
        root.addWidget(btn_lock_models)

        # Hinge Specs button
        btn_hinge_specs = _hub_button(
            "Hinge Specs",
            "View, add, and edit hinge machining specs by manufacturer and door height.",
            self._open_hinge_specs,
        )
        root.addWidget(btn_hinge_specs)

        # ── Fab Sheet Defaults ──────────────────────────────────────
        defaults_box = QGroupBox("Fab Sheet Defaults")
        defaults_box.setStyleSheet(
            "QGroupBox { font-weight: bold; color: #e0e0e0; border: 1px solid #555; "
            "margin-top: 8px; padding-top: 14px; border-radius: 6px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }"
        )
        form = QFormLayout(defaults_box)
        form.setContentsMargins(16, 16, 16, 12)
        form.setSpacing(8)

        defs = load_fab_defaults()

        self._ded_edit = QLineEdit(defs.get("width_deduction", "3/16"))
        self._ded_edit.setFixedWidth(80)
        self._ded_edit.setStyleSheet("background: #1e1e1e; color: #ccc; border: 1px solid #555; padding: 4px;")
        form.addRow("Width Deduction:", self._ded_edit)

        self._ucut_edit = QLineEdit(defs.get("undercut", "3/4"))
        self._ucut_edit.setFixedWidth(80)
        self._ucut_edit.setStyleSheet("background: #1e1e1e; color: #ccc; border: 1px solid #555; padding: 4px;")
        form.addRow("Undercut:", self._ucut_edit)

        self._hbs_edit = QLineEdit(defs.get("hinge_backset", "1/4"))
        self._hbs_edit.setFixedWidth(80)
        self._hbs_edit.setStyleSheet("background: #1e1e1e; color: #ccc; border: 1px solid #555; padding: 4px;")
        form.addRow("Hinge Backset:", self._hbs_edit)

        self._ded_edit.textChanged.connect(self._on_defaults_changed)
        self._ucut_edit.textChanged.connect(self._on_defaults_changed)
        self._hbs_edit.textChanged.connect(self._on_defaults_changed)

        root.addWidget(defaults_box)

        # Placeholder for future categories
        # btn_machining = _hub_button(
        #     "Machining Templates",
        #     "Define hinge spacing, lock locations, and other machining details.",
        #     self._open_machining_templates,
        # )
        # root.addWidget(btn_machining)

        root.addStretch()

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _open_prep_codes(self) -> None:
        from ui.prep_codes_editor import PrepCodesEditorDialog
        dlg = PrepCodesEditorDialog(parent=self)
        dlg.exec()

    def _open_lock_models(self) -> None:
        from ui.lock_models_editor import LockModelsEditorDialog
        dlg = LockModelsEditorDialog(parent=self)
        dlg.exec()

    def _open_hinge_specs(self) -> None:
        from ui.hinge_specs_editor import HingeSpecsEditorDialog
        dlg = HingeSpecsEditorDialog(parent=self)
        dlg.exec()

    def _on_defaults_changed(self) -> None:
        """Persist fab sheet defaults whenever the user edits them."""
        _save_fab_defaults({
            "width_deduction": self._ded_edit.text().strip(),
            "undercut": self._ucut_edit.text().strip(),
            "hinge_backset": self._hbs_edit.text().strip(),
        })
