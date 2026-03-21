"""Hinge Specs editor dialog.

Table-based editor for ``data/Hinge_Specs.csv`` — lets users view, add,
edit, and delete hinge/lock machining specifications per manufacturer and
door height.  Accessible from the Fabrication Hub.
"""

from __future__ import annotations

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

from core.hinge_specs import HingeSpec, HingeSpecDB
from core.utils import clamped_size

_HEADERS = [
    "Manufacturer", "Height", "D1", "D2", "D3", "D4",
    "Cylindrical", "Mortise", "Rim_Panic",
    "CVR_Panic", "SVR_Panic", "Mortise_Panic", "Concealed_Cable",
]


class HingeSpecsEditorDialog(QDialog):
    """Full CRUD editor for the Hinge_Specs.csv file."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Hinge Specs")
        self.resize(*clamped_size(1100, 620))
        self._dirty = False
        self._build_ui()
        self._load_data()

    # ── UI ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel(
            "Manage hinge & lock machining specs by manufacturer and door height. "
            "Changes are saved when you click Save."
        ))
        hdr.addStretch()
        root.addLayout(hdr)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter by Manufacturer:"))
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("All")
        self._filter_combo.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self._filter_combo)
        filter_row.addStretch()
        root.addLayout(filter_row)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        header = self._table.horizontalHeader()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for c in range(2, len(_HEADERS)):
            header.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)
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
        btn_save.clicked.connect(self._save_data)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self._close_dialog)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    # ── Data I/O ────────────────────────────────────────────────────

    def _load_data(self) -> None:
        db = HingeSpecDB.load()
        self._table.blockSignals(True)
        self._table.setRowCount(0)

        mfrs = set()
        for spec in db.all_rows():
            mfrs.add(spec.manufacturer)
            r = self._table.rowCount()
            self._table.setRowCount(r + 1)
            vals = [
                spec.manufacturer, str(spec.height),
                spec.d1, spec.d2, spec.d3, spec.d4,
                spec.cylindrical, spec.mortise, spec.rim_panic,
                spec.cvr_panic, spec.svr_panic, spec.mortise_panic,
                spec.concealed_cable,
            ]
            for c, v in enumerate(vals):
                self._table.setItem(r, c, QTableWidgetItem(v))

        # Populate manufacturer filter
        cur = self._filter_combo.currentText()
        self._filter_combo.blockSignals(True)
        self._filter_combo.clear()
        self._filter_combo.addItem("All")
        for m in sorted(mfrs):
            self._filter_combo.addItem(m)
        if cur and self._filter_combo.findText(cur) >= 0:
            self._filter_combo.setCurrentText(cur)
        self._filter_combo.blockSignals(False)

        self._table.blockSignals(False)
        self._dirty = False

    def _save_data(self) -> None:
        rows: List[HingeSpec] = []
        for r in range(self._table.rowCount()):
            vals = []
            for c in range(len(_HEADERS)):
                item = self._table.item(r, c)
                vals.append(item.text().strip() if item else "")
            if not any(vals):
                continue
            rows.append(HingeSpec(
                manufacturer=vals[0],
                height=int(float(vals[1])) if vals[1] else 0,
                d1=vals[2], d2=vals[3], d3=vals[4], d4=vals[5],
                cylindrical=vals[6], mortise=vals[7], rim_panic=vals[8],
                cvr_panic=vals[9], svr_panic=vals[10], mortise_panic=vals[11],
                concealed_cable=vals[12],
            ))
        HingeSpecDB.save(rows)
        self._dirty = False
        QMessageBox.information(self, "Saved", "Hinge specs saved successfully.")

    # ── Row operations ──────────────────────────────────────────────

    def _add_row(self) -> None:
        self._table.blockSignals(True)
        r = self._table.rowCount()
        self._table.setRowCount(r + 1)
        mfr = self._filter_combo.currentText()
        if mfr == "All":
            mfr = ""
        for c in range(len(_HEADERS)):
            val = mfr if c == 0 else ""
            self._table.setItem(r, c, QTableWidgetItem(val))
        self._table.blockSignals(False)
        self._table.scrollToBottom()
        self._table.editItem(self._table.item(r, 0))
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

    def _apply_filter(self, manufacturer: str) -> None:
        for r in range(self._table.rowCount()):
            mfr_item = self._table.item(r, 0)
            mfr_text = mfr_item.text().strip() if mfr_item else ""
            show = manufacturer == "All" or mfr_text == manufacturer
            self._table.setRowHidden(r, not show)

    # ── Dirty tracking ──────────────────────────────────────────────

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        self._dirty = True

    def _close_dialog(self) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Close without saving?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.accept()
