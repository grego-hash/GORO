"""Lock Models editor dialog.

Provides a table-based editor for ``data/Lock_Models.csv`` that lets
users view, add, edit, and delete lock model entries grouped by
locktype (which corresponds to the Description values of Locktype
entries in Prep_Codes.csv).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.seeded_data import ensure_seeded_csv
from core.utils import clamped_size

_CSV_HEADERS = ["Locktype", "Model", "Description", "Size", "Template"]

_DEFAULT_CSV = ensure_seeded_csv("Lock_Models.csv")


def _locktype_choices() -> List[str]:
    """Return locktype descriptions from Prep_Codes.csv (MORTISE, CYLINDRICAL, …)."""
    try:
        from core.prep_codes import PrepCodeDB
        db = PrepCodeDB.load_default()
        return db.locktype_descriptions()
    except Exception:
        return []


class LockModelsEditorDialog(QDialog):
    """Full CRUD editor for the Lock_Models.csv file."""

    def __init__(self, csv_path: Optional[Path] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Lock Models")
        self.resize(*clamped_size(960, 620))
        self._csv_path = csv_path or _DEFAULT_CSV
        self._dirty = False
        self._locktype_list = _locktype_choices()
        self._build_ui()
        self._load_csv()

    # ── UI ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Manage lock model definitions by locktype. Changes are saved when you click Save."))
        hdr.addStretch()
        root.addLayout(hdr)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter by Locktype:"))
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("All")
        self._filter_combo.addItems(self._locktype_list)
        self._filter_combo.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self._filter_combo)
        filter_row.addStretch()
        root.addLayout(filter_row)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(_CSV_HEADERS))
        self._table.setHorizontalHeaderLabels(_CSV_HEADERS)
        header = self._table.horizontalHeader()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self._table, 1)

        # Button row
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Row")
        btn_add.clicked.connect(self._add_row)
        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self._delete_selected)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_delete)
        btn_row.addStretch()

        btn_save = QPushButton("Save")
        btn_save.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        btn_save.clicked.connect(self._save_csv)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self._close_dialog)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    # ── Data I/O ────────────────────────────────────────────────────

    def _load_csv(self) -> None:
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        if self._csv_path.exists():
            with open(self._csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    r = self._table.rowCount()
                    self._table.setRowCount(r + 1)
                    for c, h in enumerate(_CSV_HEADERS):
                        val = (row.get(h) or "").strip()
                        self._table.setItem(r, c, QTableWidgetItem(val))
        self._table.blockSignals(False)
        self._dirty = False

    def _save_csv(self) -> None:
        self._csv_path.parent.mkdir(parents=True, exist_ok=True)
        rows: List[List[str]] = []
        for r in range(self._table.rowCount()):
            row_data = []
            for c in range(len(_CSV_HEADERS)):
                item = self._table.item(r, c)
                row_data.append(item.text().strip() if item else "")
            if any(row_data):
                rows.append(row_data)

        with open(self._csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(_CSV_HEADERS)
            writer.writerows(rows)

        self._dirty = False
        QMessageBox.information(self, "Saved", f"Lock models saved to:\n{self._csv_path}")

    # ── Row operations ──────────────────────────────────────────────

    def _add_row(self) -> None:
        self._table.blockSignals(True)
        r = self._table.rowCount()
        self._table.setRowCount(r + 1)
        lt = self._filter_combo.currentText()
        if lt == "All":
            lt = ""
        for c in range(len(_CSV_HEADERS)):
            val = lt if c == 0 else ""
            self._table.setItem(r, c, QTableWidgetItem(val))
        self._table.blockSignals(False)
        self._table.scrollToBottom()
        self._table.editItem(self._table.item(r, 1))
        self._dirty = True

    def _delete_selected(self) -> None:
        rows = sorted({idx.row() for idx in self._table.selectedIndexes()}, reverse=True)
        if not rows:
            return
        reply = QMessageBox.question(
            self, "Delete", f"Delete {len(rows)} selected row(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for r in rows:
            self._table.removeRow(r)
        self._dirty = True

    # ── Filter ──────────────────────────────────────────────────────

    def _apply_filter(self, locktype: str) -> None:
        for r in range(self._table.rowCount()):
            lt_item = self._table.item(r, 0)
            lt_text = lt_item.text().strip().upper() if lt_item else ""
            show = locktype == "All" or lt_text == locktype.strip().upper()
            self._table.setRowHidden(r, not show)

    # ── Dirty tracking ──────────────────────────────────────────────

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        self._dirty = True

    def _close_dialog(self) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                self._save_csv()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.accept()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._dirty:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                self._save_csv()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            else:
                event.accept()
        else:
            event.accept()
