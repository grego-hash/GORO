"""Door Fabrication Sheet dialog.

Displays one sheet per unique (Door Type, Prep String) combination,
closely mirroring the Walters & Wolf Excel fab-sheet template.
Users can navigate sheets, edit blank fields, and export to PDF.
"""

from __future__ import annotations

import json
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import Qt, QSize, QUrl, QSettings
from PyQt6.QtGui import QCloseEvent, QDesktopServices, QFont, QPainter, QPen, QColor, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from ui.fab_sheet_builder import FabSheet
from core.constants import ORG_NAME, APP_NAME
from core.utils import clamped_size


# ── Style constants ─────────────────────────────────────────────────
# No forced colors — inherit from the application's active theme.
# Only minimal structural styling is applied (borders, padding).

_BORDER = "#555"
_ACCENT = "#e0e0e0"
_LABEL_FG = "#cccccc"


# ── Helpers ─────────────────────────────────────────────────────────

def _label(text: str, bold: bool = False, size: int = 0, color: str = "") -> QLabel:
    lbl = QLabel(text)
    parts: list[str] = []
    if bold:
        parts.append("font-weight: bold")
    if size:
        parts.append(f"font-size: {size}px")
    if color:
        parts.append(f"color: {color}")
    if parts:
        lbl.setStyleSheet("; ".join(parts))
    return lbl


def _field(default: str = "", read_only: bool = False, width: int = 0) -> QLineEdit:
    le = QLineEdit(default)
    if read_only:
        le.setReadOnly(True)
        le.setStyleSheet(
            f"background: #2a2a2a; color: #cccccc; border: 1px solid {_BORDER}; "
            "padding: 2px 6px;"
        )
    else:
        le.setStyleSheet(
            f"background: #1e1e1e; color: #cccccc; border: 1px solid {_BORDER}; "
            "padding: 2px 6px;"
        )
    if width:
        le.setFixedWidth(width)
    return le


def _section_box(title: str, title_color: str = "") -> QGroupBox:
    tc = title_color or _ACCENT
    box = QGroupBox(title)
    box.setStyleSheet(
        f"QGroupBox {{ font-weight: bold; color: {tc}; border: 1px solid {_BORDER}; "
        f"border-radius: 6px; margin-top: 10px; padding: 8px; padding-top: 16px; }}"
        f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; }}"
    )
    return box


def _combo(items: list[str] | None = None, editable: bool = True) -> QComboBox:
    cb = QComboBox()
    cb.setEditable(editable)
    cb.setStyleSheet(
        f"background: #1e1e1e; color: #cccccc; border: 1px solid {_BORDER}; padding: 2px 4px;"
    )
    cb.addItem("")
    if items:
        cb.addItems(items)
    return cb


def _parse_dim(text: str) -> float | None:
    """Parse a dimension string into decimal inches.

    Accepts formats like: "36", "3/16", "35 13/16", "3'-0", "3-0", "3-6 1/2".
    Returns None if unparseable.
    """
    s = text.strip().replace('"', '').replace('\u201d', '')
    if not s:
        return None
    try:
        # feet-inches with apostrophe: e.g. "3'-0" or "3'-6 1/2"
        if "'" in s:
            parts = s.split("'")
            feet = float(parts[0].strip())
            inch_part = parts[1].lstrip("-").strip()
            inches = _parse_dim(inch_part) if inch_part else 0.0
            if inches is None:
                inches = 0.0
            return feet * 12 + inches
        # feet-inches with dash only: e.g. "3-0", "3-6", "3-4 1/2"
        # Detect: starts with digit(s), then a dash, then digit(s) — and no "/"
        if "-" in s and "/" not in s:
            parts = s.split("-", 1)
            left = parts[0].strip()
            right = parts[1].strip()
            if left and right and left.replace(".", "", 1).isdigit():
                feet = float(left)
                inches = _parse_dim(right) if right else 0.0
                if inches is None:
                    inches = 0.0
                return feet * 12 + inches
        # mixed number: "35 13/16"
        if " " in s and "/" in s:
            whole, frac = s.rsplit(" ", 1)
            return float(whole) + float(Fraction(frac))
        # simple fraction: "3/16"
        if "/" in s:
            return float(Fraction(s))
        # plain decimal / integer
        return float(s)
    except (ValueError, ZeroDivisionError):
        return None


def _dim_to_str(value: float) -> str:
    """Convert a decimal-inch value to a compact fractional string.

    Uses 16ths precision.  Returns e.g. '35 13/16' or '36'.
    """
    if value < 0:
        return f"-{_dim_to_str(-value)}"
    whole = int(value)
    remainder = value - whole
    sixteenths = round(remainder * 16)
    if sixteenths == 16:
        whole += 1
        sixteenths = 0
    if sixteenths == 0:
        return str(whole) if whole else "0"
    frac = Fraction(sixteenths, 16)
    return f"{whole} {frac}" if whole else str(frac)


# ── Single sheet canvas widget ──────────────────────────────────────

class FabSheetCanvas(QWidget):
    """Renders one fabrication sheet in a layout mimicking the Excel template."""

    def __init__(
        self,
        sheet: FabSheet,
        job_name: str = "",
        parent: Optional[QWidget] = None,
        on_completed_changed: Optional[Callable[[bool], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._sheet = sheet
        self._job_name = job_name
        self._on_completed_changed = on_completed_changed
        self._fields: dict[str, QLineEdit | QComboBox | QCheckBox] = {}
        self._other_hw_rows: list[QLineEdit] = []
        self._other_hw_fields_layout: Optional[QVBoxLayout] = None
        self._add_other_hw_btn: Optional[QPushButton] = None
        first = self._sheet.first()
        self._door_tab_notes_text = (first.comments if first else "") or ""
        # Load prep code DB once for populating all dropdowns
        try:
            from core.prep_codes import PrepCodeDB
            self._prep_db = PrepCodeDB.load_default()
        except Exception:
            self._prep_db = None
        self._build_ui()
        self._auto_populate_from_prep_codes()

    def _auto_populate_from_prep_codes(self) -> None:
        """Fill blank machining fields from the prep code database."""
        if not self._sheet.prep_string:
            return
        try:
            from core.prep_codes import PrepCodeDB
            db = PrepCodeDB.load_default()
            overrides = db.resolve_for_fab_sheet(self._sheet.prep_string)
            for key, value in overrides.items():
                field = self._fields.get(key)
                if field is None:
                    continue
                if isinstance(field, QComboBox):
                    if not field.currentText().strip():
                        matched = False
                        for i in range(field.count()):
                            if field.itemText(i).upper() == value.upper():
                                field.setCurrentIndex(i)
                                matched = True
                                break
                        if not matched:
                            field.setCurrentText(value)
                elif isinstance(field, QLineEdit):
                    if not field.text().strip() and not field.isReadOnly():
                        field.setText(value)
        except Exception:
            pass

    # ── public access ───────────────────────────────────────────────

    @property
    def sheet(self) -> FabSheet:
        return self._sheet

    def field_value(self, key: str) -> str:
        f = self._fields.get(key)
        if f is None:
            return ""
        if isinstance(f, QComboBox):
            return f.currentText().strip()
        if isinstance(f, QLineEdit):
            return f.text().strip()
        if isinstance(f, QCheckBox):
            return "Yes" if f.isChecked() else ""
        return ""

    def is_completed(self) -> bool:
        cb = self._fields.get("completed")
        return isinstance(cb, QCheckBox) and cb.isChecked()

    def set_completed(self, completed: bool) -> None:
        cb = self._fields.get("completed")
        if isinstance(cb, QCheckBox):
            prior = cb.blockSignals(True)
            cb.setChecked(completed)
            cb.blockSignals(prior)
        self._set_sheet_locked(completed)

    def _on_completed_toggled(self, checked: bool) -> None:
        self._set_sheet_locked(checked)
        if self._on_completed_changed:
            self._on_completed_changed(bool(checked))

    def _set_sheet_locked(self, locked: bool) -> None:
        for key, field in self._fields.items():
            if key == "completed":
                continue
            field.setEnabled(not locked)
        if self._add_other_hw_btn is not None:
            self._add_other_hw_btn.setEnabled(not locked)

    def _calc_initial_prefit(self) -> None:
        """Set initial prefit leaf sizes (active_width − deduction, height − undercut).

        Reads persisted defaults from ~/.goro/fab_defaults.json.
        Called once during build.  User can freely overwrite the values.
        """
        from ui.fabrication_hub import load_fab_defaults
        defs = load_fab_defaults()
        ded = _parse_dim(defs.get("width_deduction", "3/16"))
        ucut = _parse_dim(defs.get("undercut", "3/4"))
        hbs = defs.get("hinge_backset", "1/4")
        fh = _parse_dim(self._fields["frame_opening_h"].text())

        # Auto-fill hinge backset from default
        bs_f = self._fields.get("hinge_backset")
        if isinstance(bs_f, QLineEdit) and not bs_f.text().strip() and hbs:
            bs_f.setText(hbs)

        first = self._sheet.first()

        # Active leaf prefit: door active width − width deduction
        # Fall back to frame opening width if active_width not available
        act_w = _parse_dim(first.active_width) if first and first.active_width else None
        if act_w is not None and not act_w:
            act_w = None  # skip zero values from empty templates
        if act_w is None:
            act_w = _parse_dim(self._fields["frame_opening_w"].text())
        if act_w is not None and ded is not None:
            self._fields["prep_leaf_w"].setText(_dim_to_str(act_w - ded))
        if fh is not None and ucut is not None:
            self._fields["prep_leaf_h"].setText(_dim_to_str(fh - ucut))

        # Inactive leaf prefit (for unequal pairs)
        inact_w = _parse_dim(first.inactive_width) if first and first.inactive_width else None
        if inact_w is not None and ded is not None:
            self._fields["inactive_leaf_w"].setText(_dim_to_str(inact_w - ded))
            self._inactive_leaf_label.setVisible(True)
            self._inactive_leaf_widget.setVisible(True)
        if fh is not None and ucut is not None and inact_w is not None:
            self._fields["inactive_leaf_h"].setText(_dim_to_str(fh - ucut))

    def _fill_lite_from_door_tab(self) -> None:
        """Auto-fill Light/Louver fields from the door tab's lite_details.

        Fields sourced from door tabs are set read-only so the user
        edits them on the door tab instead.
        """
        first = self._sheet.first()
        if not first or not first.lite_details:
            return
        ld = first.lite_details
        _ro_style = f"background: #2a2a2a; color: #cccccc; border: 1px solid {_BORDER};"
        for key in ("lite_kit", "lite_glass_thickness", "lite_width",
                     "lite_height", "lite_lockstile", "lite_top_rail",
                     "lite_bottom_rail"):
            val = ld.get(key, "")
            if not val:
                continue
            f = self._fields.get(key)
            if isinstance(f, QLineEdit) and not f.text().strip():
                f.setText(val)
                f.setReadOnly(True)
                f.setStyleSheet(_ro_style)
        # For non-aluminum doors, calculate bottom rail = opening height − lite height
        br_f = self._fields.get("lite_bottom_rail")
        if isinstance(br_f, QLineEdit) and not br_f.text().strip():
            is_aluminum = first.door_type.upper().startswith("AL")
            if not is_aluminum:
                h_field = self._fields.get("frame_opening_h")
                h_text = h_field.text().strip() if isinstance(h_field, QLineEdit) else ""
                open_h = _parse_dim(h_text) if h_text else None
                lite_h = _parse_dim(ld.get("lite_height", ""))
                if open_h and lite_h and open_h > lite_h:
                    br_f.setText(_dim_to_str(open_h - lite_h))
                    br_f.setReadOnly(True)
                    br_f.setStyleSheet(_ro_style)
        # Factory glaze checkbox
        fg = ld.get("lite_factory_glaze", "")
        if fg:
            cb = self._fields.get("lite_factory_glaze")
            if isinstance(cb, QCheckBox):
                cb.setChecked(fg.upper() in ("YES", "TRUE", "1", "X"))
                cb.setEnabled(False)

    # ── UI construction ─────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(8)

        first = self._sheet.first()

        # ── TOP HEADER AREA ─────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        logo_label = QLabel()
        logo_path = Path.home() / ".goro" / "company_logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path))
            logo_label.setPixmap(pix.scaled(QSize(170, 56), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("COMPANY LOGO")
            logo_label.setStyleSheet(f"font-weight: bold; font-size: 12px; color: {_LABEL_FG};")
        logo_label.setMinimumWidth(180)
        header_row.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title_block.addWidget(_label("DOOR MACHINING SHEET", bold=True, size=14, color="#ffffff"))
        title_block.addWidget(
            _label(
                f"{self._sheet.key.label()}  •  {len(self._sheet.openings)} opening(s)",
                size=10,
                color="#9ca3af",
            )
        )
        title_block.addStretch()
        header_row.addLayout(title_block, 1)

        completed_cb = QCheckBox("Completed")
        completed_cb.setStyleSheet("font-weight: bold; color: #cccccc;")
        completed_cb.toggled.connect(self._on_completed_toggled)
        self._fields["completed"] = completed_cb
        header_row.addWidget(completed_cb, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        outer.addLayout(header_row)

        # Project + detail cards
        cards = QHBoxLayout()
        cards.setSpacing(8)

        project_box = _section_box("PROJECT")
        project_grid = QGridLayout(project_box)
        project_grid.setHorizontalSpacing(8)
        project_grid.setVerticalSpacing(6)

        project_grid.addWidget(_label("JOB NAME:", bold=True), 0, 0)
        self._fields["job_name"] = _field(self._job_name, read_only=True)
        project_grid.addWidget(self._fields["job_name"], 0, 1, 1, 3)

        project_grid.addWidget(_label("JOB NUMBER:", bold=True), 0, 4)
        self._fields["job_number"] = _field("", width=80)
        project_grid.addWidget(self._fields["job_number"], 0, 5)

        project_grid.addWidget(_label("DOOR TYPE:", bold=True, color="#ffcc00"), 1, 0)
        self._fields["door_type"] = _field(self._sheet.door_type, read_only=True)
        project_grid.addWidget(self._fields["door_type"], 1, 1)

        project_grid.addWidget(_label("FRAME OPENING:", bold=True), 1, 2)
        size_row = QHBoxLayout()
        self._fields["frame_opening_w"] = _field(first.width if first else "", width=50)
        size_row.addWidget(self._fields["frame_opening_w"])
        size_row.addWidget(_label("x"))
        self._fields["frame_opening_h"] = _field(first.height if first else "", width=50)
        size_row.addWidget(self._fields["frame_opening_h"])
        size_row.addStretch()
        size_w = QWidget()
        size_w.setLayout(size_row)
        project_grid.addWidget(size_w, 1, 3)

        project_grid.addWidget(_label("Fire Rating:", bold=True), 1, 4)
        self._fields["fire_rating"] = _field(first.rating_fire if first else "", read_only=bool(first and first.rating_fire))
        project_grid.addWidget(self._fields["fire_rating"], 1, 5)

        project_grid.addWidget(_label("STC Rating:", bold=True), 2, 4)
        self._fields["stc_rating"] = _field(first.stc if first else "", read_only=bool(first and first.stc))
        project_grid.addWidget(self._fields["stc_rating"], 2, 5)

        project_grid.addWidget(_label("PREFIT LEAF:", bold=True), 2, 0)
        leaf_row = QHBoxLayout()
        self._fields["prep_leaf_w"] = _field("", width=70)
        leaf_row.addWidget(self._fields["prep_leaf_w"])
        leaf_row.addWidget(_label("x"))
        self._fields["prep_leaf_h"] = _field("", width=70)
        leaf_row.addWidget(self._fields["prep_leaf_h"])
        leaf_row.addStretch()
        leaf_w = QWidget()
        leaf_w.setLayout(leaf_row)
        project_grid.addWidget(leaf_w, 2, 1)

        # Row 4: Inactive Leaf Prefit Size (only shown for unequal pairs)
        inactive_w = first.inactive_width if first else ""
        self._inactive_leaf_label = _label("INACTIVE LEAF PREFIT:", bold=True)
        inactive_leaf_row = QHBoxLayout()
        self._fields["inactive_leaf_w"] = _field("", width=70)
        inactive_leaf_row.addWidget(self._fields["inactive_leaf_w"])
        inactive_leaf_row.addWidget(_label("x"))
        self._fields["inactive_leaf_h"] = _field("", width=70)
        inactive_leaf_row.addWidget(self._fields["inactive_leaf_h"])
        inactive_leaf_row.addStretch()
        inactive_leaf_widget = QWidget()
        inactive_leaf_widget.setLayout(inactive_leaf_row)
        self._inactive_leaf_widget = inactive_leaf_widget

        project_grid.addWidget(self._inactive_leaf_label, 3, 0)
        project_grid.addWidget(inactive_leaf_widget, 3, 1)

        cards.addWidget(project_box, 3)

        detail_box = _section_box("DOOR TAB DETAILS")
        detail_layout = QVBoxLayout(detail_box)
        detail_layout.setContentsMargins(8, 6, 8, 8)
        door_details = first.door_details if first else {}
        detail_lines = [f"{k}: {v}" for k, v in door_details.items()]
        detail_text = QTextEdit()
        detail_text.setReadOnly(True)
        detail_text.setPlainText("\n".join(detail_lines))
        detail_text.setStyleSheet(
            f"background: #2a2a2a; color: #cccccc; border: 1px solid {_BORDER}; "
            f"font-size: 10px; padding: 4px;"
        )
        detail_text.setMinimumHeight(110)
        detail_text.setMaximumHeight(180)
        detail_layout.addWidget(detail_text)
        cards.addWidget(detail_box, 2)

        outer.addLayout(cards)

        # Show/hide inactive row based on whether inactive width exists
        has_inactive = bool(inactive_w)
        self._inactive_leaf_label.setVisible(has_inactive)
        self._inactive_leaf_widget.setVisible(has_inactive)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {_BORDER};")
        outer.addWidget(sep)

        # ── MAIN BODY: 4-column layout ──────────────────────────────
        body = QHBoxLayout()
        body.setSpacing(8)

        # COL 1: Hinges + Lock
        col1 = QVBoxLayout()
        col1.setSpacing(8)
        col1.addWidget(self._build_hinges_section())
        col1.addWidget(self._build_lock_section())
        col1.addStretch()

        # COL 2: Machining specs
        col2 = QVBoxLayout()
        col2.setSpacing(8)
        col2.addWidget(self._build_machining_right_section())
        col2.addStretch()

        # COL 3: Light/Louver + Other HW
        col3 = QVBoxLayout()
        col3.setSpacing(8)
        col3.addWidget(self._build_light_louver_section())
        col3.addWidget(self._build_other_hw_section())
        col3.addStretch()

        # COL 4: Door Numbers grid
        col4 = QVBoxLayout()
        col4.setSpacing(8)
        col4.addWidget(self._build_door_numbers_section())
        col4.addStretch()

        body.addLayout(col1, 3)
        body.addLayout(col2, 2)
        body.addLayout(col3, 3)
        body.addLayout(col4, 2)
        outer.addLayout(body, 1)

        # Calculate initial prefit values and defaults (including hinge backset)
        # after all body fields are created.
        self._calc_initial_prefit()

        # Auto-fill Light/Louver fields from door tab data
        # (must run after _build_light_louver_section creates the fields)
        self._fill_lite_from_door_tab()

    # ── Section builders ────────────────────────────────────────────

    def _build_hinges_section(self) -> QGroupBox:
        box = _section_box("HINGES")
        grid = QGridLayout(box)
        grid.setSpacing(4)

        self._fields["hinge_type"] = _combo()
        if self._prep_db:
            for desc in self._prep_db.descriptions_for_category("Hinge"):
                self._fields["hinge_type"].addItem(desc)
        grid.addWidget(self._fields["hinge_type"], 0, 0, 1, 2)

        grid.addWidget(_label("Template No.:"), 1, 0)
        self._fields["hinge_template"] = _field("")
        grid.addWidget(self._fields["hinge_template"], 1, 1)

        grid.addWidget(_label("Size:"), 2, 0)
        self._fields["hinge_size"] = _field("")
        grid.addWidget(self._fields["hinge_size"], 2, 1)

        grid.addWidget(_label("Hinge Backset:"), 3, 0)
        self._fields["hinge_backset"] = _field("")
        grid.addWidget(self._fields["hinge_backset"], 3, 1)

        # ── Hinge Locations (from Hinge Spec table) ─────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #555;")
        grid.addWidget(sep, 4, 0, 1, 2)

        grid.addWidget(_label("Spec:"), 5, 0)
        mfr_combo = _combo(editable=False)
        try:
            from core.hinge_specs import HingeSpecDB
            self._hinge_spec_db = HingeSpecDB.load()
            for m in self._hinge_spec_db.manufacturers():
                mfr_combo.addItem(m)
        except Exception:
            self._hinge_spec_db = None
        mfr_combo.addItem("Custom")
        self._fields["hinge_manufacturer"] = mfr_combo
        grid.addWidget(mfr_combo, 5, 1)

        grid.addWidget(_label("Hinge 1:"), 6, 0)
        self._fields["hinge_d1"] = _field("")
        grid.addWidget(self._fields["hinge_d1"], 6, 1)

        grid.addWidget(_label("Hinge 2:"), 7, 0)
        self._fields["hinge_d2"] = _field("")
        grid.addWidget(self._fields["hinge_d2"], 7, 1)

        grid.addWidget(_label("Hinge 3:"), 8, 0)
        self._fields["hinge_d3"] = _field("")
        grid.addWidget(self._fields["hinge_d3"], 8, 1)

        grid.addWidget(_label("Hinge 4:"), 9, 0)
        self._fields["hinge_d4"] = _field("")
        grid.addWidget(self._fields["hinge_d4"], 9, 1)

        grid.addWidget(_label("WIRE CHASE:"), 10, 0)
        self._fields["wire_chase"] = QCheckBox()
        grid.addWidget(self._fields["wire_chase"], 10, 1)

        # Wire: hinge selection → auto-fill template and size
        self._fields["hinge_type"].currentTextChanged.connect(self._on_hinge_changed)
        # Wire: manufacturer selection → auto-fill D1-D4 + lock centerline
        mfr_combo.currentTextChanged.connect(self._on_hinge_manufacturer_changed)

        return box

    def _on_hinge_changed(self, desc: str) -> None:
        db = self._prep_db
        if not db or not desc.strip():
            return
        entry = db.entry_by_description("Hinge", desc)
        if entry:
            tmpl = self._fields.get("hinge_template")
            if isinstance(tmpl, QLineEdit) and entry.template:
                tmpl.setText(entry.template)
            size = self._fields.get("hinge_size")
            if isinstance(size, QLineEdit) and entry.size:
                size.setText(entry.size)

    def _on_hinge_manufacturer_changed(self, mfr: str) -> None:
        """Look up hinge spec by manufacturer + door height, fill D1-D4."""
        db = getattr(self, "_hinge_spec_db", None)
        if not db or not mfr.strip() or mfr == "Custom":
            return
        # Get door height from frame_opening_h
        h_field = self._fields.get("frame_opening_h")
        h_text = h_field.text().strip() if isinstance(h_field, QLineEdit) else ""
        h_val = _parse_dim(h_text) if h_text else None
        if h_val is None or h_val <= 0:
            return
        spec = db.lookup(mfr, h_val)
        if not spec:
            return
        # Fill D1-D4
        for key in ("hinge_d1", "hinge_d2", "hinge_d3", "hinge_d4"):
            f = self._fields.get(key)
            if isinstance(f, QLineEdit):
                attr = key.replace("hinge_", "")  # d1, d2, d3, d4
                f.setText(getattr(spec, attr, ""))
        # Auto-set hinge qty based on D4
        qty_f = self._fields.get("hinge_qty")
        if isinstance(qty_f, QLineEdit):
            qty_f.setText("4" if spec.d4.strip() else "3")
        # Auto-fill lock centerline if a lock type is already selected
        self._apply_lock_centerline_from_spec(spec)

    def _apply_lock_centerline_from_spec(self, spec=None) -> None:
        """Fill lock_center from hinge spec based on current lock type."""
        if spec is None:
            db = getattr(self, "_hinge_spec_db", None)
            mfr_f = self._fields.get("hinge_manufacturer")
            mfr = mfr_f.currentText().strip() if isinstance(mfr_f, QComboBox) else ""
            if not db or not mfr or mfr == "Custom":
                return
            h_field = self._fields.get("frame_opening_h")
            h_text = h_field.text().strip() if isinstance(h_field, QLineEdit) else ""
            h_val = _parse_dim(h_text) if h_text else None
            if h_val is None or h_val <= 0:
                return
            spec = db.lookup(mfr, h_val)
            if not spec:
                return
        lock_type_f = self._fields.get("lock_type")
        if not isinstance(lock_type_f, QComboBox):
            return
        lock_type = lock_type_f.currentText().strip()
        if not lock_type:
            return
        centerline = spec.lock_centerline(lock_type)
        if centerline and centerline.lower() != "per template":
            lc_f = self._fields.get("lock_center")
            if isinstance(lc_f, QLineEdit):
                lc_f.setText(centerline)
        self._apply_strike_center_from_offset()

    def _is_pair_door(self) -> bool:
        first = self._sheet.first()
        if not first:
            return False
        inact_w = _parse_dim((first.inactive_width or "").strip())
        if inact_w is not None and inact_w > 0:
            return True
        # Equal pairs may not have inactive width populated; use opening width fallback.
        open_w = _parse_dim((first.width or "").strip())
        if open_w is not None and open_w > 48.0:
            return True
        return bool((first.inactive_elevation or "").strip())

    def _apply_strike_center_from_offset(self) -> None:
        """Auto-fill strike center from lock center + strike offset (pairs only)."""
        if not self._is_pair_door():
            return
        offset_txt = (getattr(self, "_lock_strike_offset", "") or "").strip()
        if not offset_txt:
            return
        lc_f = self._fields.get("lock_center")
        sc_f = self._fields.get("lock_strike_center")
        if not isinstance(lc_f, QLineEdit) or not isinstance(sc_f, QLineEdit):
            return
        center = _parse_dim(lc_f.text().strip())
        offset = _parse_dim(offset_txt)
        if center is None or offset is None:
            return
        sc_f.setText(_dim_to_str(center + offset))

    def _build_lock_section(self) -> QGroupBox:
        box = _section_box("LOCK")
        grid = QGridLayout(box)
        grid.setSpacing(4)
        grid.setColumnMinimumWidth(0, 130)
        grid.setColumnStretch(1, 1)

        # Type combo – populated from Locktype descriptions in Prep_Codes.csv
        type_combo = _combo()
        type_combo.setMinimumWidth(160)
        self._lock_db = self._prep_db
        if self._lock_db:
            for desc in self._lock_db.locktype_descriptions():
                type_combo.addItem(desc)
        self._fields["lock_type"] = type_combo
        grid.addWidget(type_combo, 0, 0, 1, 2)

        # Model combo – filtered by selected type
        grid.addWidget(_label("Lockstyle:"), 1, 0)
        model_combo = _combo()
        model_combo.setMinimumWidth(120)
        self._lock_model_combo = model_combo
        self._fields["lock_lockstyle"] = model_combo
        grid.addWidget(model_combo, 1, 1)

        grid.addWidget(_label("Description:"), 2, 0)
        self._fields["lock_description"] = _field("")
        grid.addWidget(self._fields["lock_description"], 2, 1)

        grid.addWidget(_label("Template No.:"), 3, 0)
        self._fields["lock_template"] = _field("")
        grid.addWidget(self._fields["lock_template"], 3, 1)

        grid.addWidget(_label("Top of Door to Center of Lock:"), 4, 0, 1, 2)
        self._fields["lock_center"] = _field("")
        grid.addWidget(self._fields["lock_center"], 5, 0, 1, 2)

        grid.addWidget(_label("Lock Backset:"), 6, 0)
        self._fields["lock_backset"] = _field("")
        grid.addWidget(self._fields["lock_backset"], 6, 1)

        grid.addWidget(_label("Top of Door to Center of Strike:"), 7, 0)
        self._fields["lock_strike_center"] = _field("")
        grid.addWidget(self._fields["lock_strike_center"], 7, 1)

        # Wire: type selection → populate model combo
        type_combo.currentTextChanged.connect(self._on_lock_type_changed)
        model_combo.currentTextChanged.connect(self._on_lock_model_changed)
        self._fields["lock_center"].textChanged.connect(lambda _: self._apply_strike_center_from_offset())

        return box

    def _on_lock_type_changed(self, lock_type: str) -> None:
        # Clear all lock detail fields when the type changes
        for key in ("lock_template", "lock_description", "lock_center",
                    "lock_backset", "lock_strike_center"):
            f = self._fields.get(key)
            if isinstance(f, QLineEdit):
                f.clear()
        self._lock_strike_offset = ""
        combo = self._lock_model_combo
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("")
        db = getattr(self, "_lock_db", None)
        if db and lock_type.strip():
            for entry in db.models_for_locktype(lock_type):
                combo.addItem(entry.model)
            # Fill template and default backset from Locktype entry in Prep_Codes.csv
            pc_entry = db.entry_by_description("Locktype", lock_type)
            if pc_entry:
                if pc_entry.template:
                    tmpl = self._fields.get("lock_template")
                    if isinstance(tmpl, QLineEdit):
                        tmpl.setText(pc_entry.template)
                if pc_entry.lock_backset:
                    bs_f = self._fields.get("lock_backset")
                    if isinstance(bs_f, QLineEdit):
                        bs_f.setText(pc_entry.lock_backset)
                self._lock_strike_offset = pc_entry.lock_strike_offset
        combo.blockSignals(False)
        # Auto-fill lock centerline from hinge spec if manufacturer selected
        self._apply_lock_centerline_from_spec()
        self._apply_strike_center_from_offset()

    def _on_lock_model_changed(self, model_text: str) -> None:
        db = getattr(self, "_lock_db", None)
        if not db or not model_text.strip():
            return
        lock_type = ""
        type_field = self._fields.get("lock_type")
        if isinstance(type_field, QComboBox):
            lock_type = type_field.currentText().strip()
        for entry in db.models_for_locktype(lock_type):
            if entry.model == model_text.strip():
                if entry.template:
                    tmpl_f = self._fields.get("lock_template")
                    if isinstance(tmpl_f, QLineEdit):
                        tmpl_f.setText(entry.template)
                if entry.description:
                    desc_f = self._fields.get("lock_description")
                    if isinstance(desc_f, QLineEdit):
                        desc_f.setText(entry.description)
                break

    def _build_light_louver_section(self) -> QGroupBox:
        box = _section_box("LIGHT OR LOUVER")
        grid = QGridLayout(box)
        grid.setSpacing(4)
        grid.addWidget(_label("KIT:"), 0, 0)
        self._fields["lite_kit"] = _field("")
        grid.addWidget(self._fields["lite_kit"], 0, 1)
        grid.addWidget(_label("GLASS THICKNESS:"), 1, 0)
        self._fields["lite_glass_thickness"] = _field("")
        grid.addWidget(self._fields["lite_glass_thickness"], 1, 1)

        size_lbl = QHBoxLayout()
        size_lbl.addWidget(_label("SIZE:"))
        size_lbl.addStretch()
        size_lbl.addWidget(_label("WIDTH"))
        size_lbl.addWidget(_label("HEIGHT"))
        size_w = QWidget()
        size_w.setLayout(size_lbl)
        grid.addWidget(size_w, 2, 0, 1, 2)

        size_vals = QHBoxLayout()
        self._fields["lite_width"] = _field("", width=50)
        size_vals.addWidget(self._fields["lite_width"])
        size_vals.addWidget(_label("x"))
        self._fields["lite_height"] = _field("", width=50)
        size_vals.addWidget(self._fields["lite_height"])
        size_vals.addStretch()
        sv_w = QWidget()
        sv_w.setLayout(size_vals)
        grid.addWidget(sv_w, 3, 0, 1, 2)

        grid.addWidget(_label("LOCKSTILE:"), 4, 0)
        self._fields["lite_lockstile"] = _field("")
        grid.addWidget(self._fields["lite_lockstile"], 4, 1)
        grid.addWidget(_label("TOP RAIL:"), 5, 0)
        self._fields["lite_top_rail"] = _field("")
        grid.addWidget(self._fields["lite_top_rail"], 5, 1)
        grid.addWidget(_label("BOTTOM RAIL:"), 6, 0)
        self._fields["lite_bottom_rail"] = _field("")
        grid.addWidget(self._fields["lite_bottom_rail"], 6, 1)
        grid.addWidget(_label("FACTORY GLAZE:"), 7, 0)
        self._fields["lite_factory_glaze"] = QCheckBox()
        grid.addWidget(self._fields["lite_factory_glaze"], 7, 1)
        return box

    def _build_bottom_rail_section(self) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 4, 0, 4)
        row.addWidget(_label("BOTTOM RAIL:", bold=True))
        self._fields["bottom_rail"] = _field("")
        row.addWidget(self._fields["bottom_rail"])
        row.addSpacing(12)
        row.addWidget(_label("WIRE CHASE:", bold=True))
        self._fields["wire_chase"] = QCheckBox()
        row.addWidget(self._fields["wire_chase"])
        row.addStretch()
        return w

    def _build_other_hw_section(self) -> QGroupBox:
        box = _section_box("NOTES / OTHER HARDWARE")
        layout = QVBoxLayout(box)

        self._other_hw_fields_layout = QVBoxLayout()
        self._other_hw_fields_layout.setContentsMargins(0, 0, 0, 0)
        self._other_hw_fields_layout.setSpacing(4)
        layout.addLayout(self._other_hw_fields_layout)

        # First line auto-fills from the source door-tab Notes/Comments cell.
        self._add_other_hw_line(self._door_tab_notes_text)
        self._add_other_hw_line()
        self._add_other_hw_line()

        self._add_other_hw_btn = QPushButton("Add Line")
        self._add_other_hw_btn.setMaximumWidth(100)
        self._add_other_hw_btn.clicked.connect(self._add_other_hw_line)
        layout.addWidget(self._add_other_hw_btn, 0, Qt.AlignmentFlag.AlignLeft)
        return box

    def _add_other_hw_line(self, default: str = "") -> None:
        if self._other_hw_fields_layout is None:
            return
        idx = len(self._other_hw_rows) + 1
        key = "other_hw" if idx == 1 else f"other_hw_{idx}"
        line = _field(default)
        self._fields[key] = line
        self._other_hw_rows.append(line)
        self._other_hw_fields_layout.addWidget(line)
        if self.is_completed():
            line.setEnabled(False)

    def _build_machining_right_section(self) -> QGroupBox:
        """Right-column machining specs: Strike-Temp, Flushbolt, OH Stop, Door Bottom."""
        box = _section_box("MACHINING SPECS")
        vbox = QVBoxLayout(box)
        vbox.setSpacing(6)

        # Each sub-section: label, combo (populated from prep DB), Template No. field
        specs = [
            ("STRIKE - TEMP.", "mach_strike_temp", "mach_strike_temp_tmpl", None),
            ("FLUSHBOLT", "mach_flushbolt", "mach_flushbolt_tmpl", "Flushbolt"),
            ("OVERHEAD STOP", "mach_overhead_stop", "mach_overhead_stop_tmpl", "Overhead Stop"),
            ("DOOR BOTTOM", "mach_door_bottom", "mach_door_bottom_tmpl", "Door Bottom"),
        ]
        for title, combo_key, tmpl_key, category in specs:
            lbl = _label(title, bold=True)
            vbox.addWidget(lbl)
            cb = _combo()
            if category and self._prep_db:
                for desc in self._prep_db.descriptions_for_category(category):
                    cb.addItem(desc)
            self._fields[combo_key] = cb
            vbox.addWidget(cb)
            tmpl_row = QHBoxLayout()
            tmpl_row.addWidget(_label("TEMPLATE NO."))
            self._fields[tmpl_key] = _field("")
            tmpl_row.addWidget(self._fields[tmpl_key])
            tw = QWidget()
            tw.setLayout(tmpl_row)
            vbox.addWidget(tw)

            # Wire: combo selection → auto-fill template
            if category:
                cb.currentTextChanged.connect(
                    lambda desc, cat=category, tkey=tmpl_key: self._on_mach_combo_changed(desc, cat, tkey)
                )

        vbox.addStretch()
        return box

    def _on_mach_combo_changed(self, desc: str, category: str, tmpl_key: str) -> None:
        db = self._prep_db
        if not db or not desc.strip():
            return
        entry = db.entry_by_description(category, desc)
        if entry and entry.template:
            tmpl = self._fields.get(tmpl_key)
            if isinstance(tmpl, QLineEdit):
                tmpl.setText(entry.template)

    def _build_door_numbers_section(self) -> QGroupBox:
        box = _section_box("DOOR NO.")
        grid = QGridLayout(box)
        grid.setSpacing(2)

        total_lbl = _label(
            f"TOTAL DOORS THIS PAGE: {len(self._sheet.openings)}", bold=True
        )
        grid.addWidget(total_lbl, 0, 0, 1, 3)

        # Header row
        grid.addWidget(_label("#", bold=True), 1, 0)
        grid.addWidget(_label("OPENING", bold=True), 1, 1)
        grid.addWidget(_label("HANDING", bold=True), 1, 2)

        display_rows = min(len(self._sheet.openings), 15)
        for i in range(display_rows):
            o = self._sheet.openings[i]
            row_idx = i + 2
            grid.addWidget(_label(str(i + 1)), row_idx, 0)
            grid.addWidget(_field(o.opening_number, read_only=True), row_idx, 1)
            grid.addWidget(_field(o.handing, read_only=True), row_idx, 2)

        return box


# ── Main dialog ─────────────────────────────────────────────────────

class FabSheetDialog(QDialog):
    """Multi-sheet fab-sheet viewer / editor with PDF export."""

    def __init__(
        self,
        sheets: List[FabSheet],
        job_name: str = "",
        workbook_path: Optional[Path] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Door Fabrication Sheets")
        self.resize(*clamped_size(1280, 860))
        self._settings = QSettings(ORG_NAME, APP_NAME)
        self._sheets = sheets
        self._job_name = job_name
        self._workbook_path = workbook_path
        self._canvases: dict[int, FabSheetCanvas] = {}
        self._active_row = -1
        self._state_path = Path.home() / ".goro" / "fab_sheet_state.json"
        self._scope_key = str(self._workbook_path.resolve()) if self._workbook_path else f"job::{self._job_name}"
        self._sheet_state: Dict[str, Dict[str, object]] = {}
        self._suppress_list_item_changed = False
        self._load_sheet_state()
        self._build_ui()

    # ── UI construction ─────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: sheet list
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.addWidget(_label("Fab Sheets", bold=True, size=12))

        self._sheet_list = QListWidget()
        self._sheet_list.setMinimumWidth(220)
        self._sheet_list.setStyleSheet(
            "QListWidget { background: #1e1e1e; color: #cccccc; }"
            "QListWidget::item:selected { background: #007acc; color: #fff; }"
        )
        for i, sh in enumerate(self._sheets):
            item = QListWidgetItem(self._sheet_item_text(i))
            item.setData(Qt.ItemDataRole.UserRole, i)
            self._sheet_list.addItem(item)
        self._sheet_list.currentRowChanged.connect(self._on_sheet_selected)
        left_layout.addWidget(self._sheet_list)

        # Right panel: scroll area with the sheet canvas
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { background: #252526; border: none; }")

        placeholder = QLabel("Select a fab sheet from the list.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-size: 14px;")
        self._scroll.setWidget(placeholder)

        splitter.addWidget(left)
        splitter.addWidget(self._scroll)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        # Bottom button row
        btn_row = QHBoxLayout()
        btn_prev = QPushButton("◀ Previous")
        btn_prev.clicked.connect(self._prev_sheet)
        btn_next = QPushButton("Next ▶")
        btn_next.clicked.connect(self._next_sheet)
        btn_preview = QPushButton("Preview Current PDF")
        btn_preview.clicked.connect(self._preview_current_pdf)
        btn_preview_all = QPushButton("Preview All PDFs")
        btn_preview_all.clicked.connect(self._preview_all_pdf)
        btn_export = QPushButton("Export Current PDF")
        btn_export.clicked.connect(self._export_current_pdf)
        btn_export_all = QPushButton("Export All PDFs")
        btn_export_all.clicked.connect(self._export_all_pdf)
        self._auto_open_cb = QCheckBox("Auto-open after export")
        self._auto_open_cb.setChecked(self._settings.value("fab_sheet/auto_open_after_export", True, type=bool))
        self._auto_open_cb.toggled.connect(self._on_auto_open_toggled)
        btn_row.addWidget(btn_prev)
        btn_row.addWidget(btn_next)
        btn_row.addStretch()
        btn_row.addWidget(self._auto_open_cb)
        btn_row.addWidget(btn_preview)
        btn_row.addWidget(btn_preview_all)
        btn_row.addWidget(btn_export)
        btn_row.addWidget(btn_export_all)
        root.addLayout(btn_row)

        # Auto-select first item
        if self._sheets:
            self._sheet_list.setCurrentRow(0)

    # ── Navigation ──────────────────────────────────────────────────

    def _sheet_state_key(self, sheet: FabSheet) -> str:
        return f"{sheet.key.door_type}|{sheet.key.prep_string}"

    def _sheet_item_text(self, row: int) -> str:
        if row < 0 or row >= len(self._sheets):
            return ""
        sh = self._sheets[row]
        base = f"{sh.key.label()}  ({len(sh.openings)})"
        if self._is_sheet_completed(row):
            return f"{base}  ✓"
        return base

    def _is_sheet_completed(self, row: int) -> bool:
        if row < 0 or row >= len(self._sheets):
            return False
        saved = self._sheet_state.get(self._sheet_state_key(self._sheets[row]), {})
        if not isinstance(saved, dict):
            return False
        return bool(saved.get("_completed", False))

    def _set_list_item_completed(self, row: int, completed: bool) -> None:
        if row < 0 or row >= self._sheet_list.count():
            return
        item = self._sheet_list.item(row)
        if item is None:
            return
        item.setText(self._sheet_item_text(row))

    def _load_sheet_state(self) -> None:
        try:
            if not self._state_path.exists():
                return
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            scope_data = data.get(self._scope_key, {}) if isinstance(data, dict) else {}
            if isinstance(scope_data, dict):
                self._sheet_state = scope_data
        except Exception:
            self._sheet_state = {}

    def _persist_sheet_state(self) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            payload: Dict[str, object] = {}
            if self._state_path.exists():
                existing = json.loads(self._state_path.read_text(encoding="utf-8"))
                if isinstance(existing, dict):
                    payload = existing
            payload[self._scope_key] = self._sheet_state
            self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            # Persistence failures should not block normal UI flow.
            return

    def _capture_row_state(self, row: int) -> None:
        if row < 0 or row >= len(self._sheets):
            return
        canvas = self._canvases.get(row)
        if canvas is None:
            return
        values: Dict[str, object] = {}
        for key, f in canvas._fields.items():
            if key == "job_name":
                # Always derive job name from current workbook context.
                continue
            if key == "completed":
                continue
            if isinstance(f, QLineEdit):
                values[key] = f.text().strip()
            elif isinstance(f, QComboBox):
                values[key] = f.currentText().strip()
            elif isinstance(f, QCheckBox):
                values[key] = f.isChecked()
        values["_completed"] = canvas.is_completed()
        self._sheet_state[self._sheet_state_key(self._sheets[row])] = values

    def _apply_row_state(self, row: int) -> None:
        if row < 0 or row >= len(self._sheets):
            return
        canvas = self._canvases.get(row)
        if canvas is None:
            return
        saved = self._sheet_state.get(self._sheet_state_key(self._sheets[row]))
        if not isinstance(saved, dict):
            return

        completed = bool(saved.get("_completed", False))
        canvas.set_completed(completed)
        self._set_list_item_completed(row, completed)

        priority = [
            "hinge_type",
            "hinge_manufacturer",
            "lock_type",
            "lock_lockstyle",
            "mach_strike_temp",
            "mach_flushbolt",
            "mach_overhead_stop",
            "mach_door_bottom",
        ]
        keys = [k for k in priority if k in saved]
        keys.extend([
            k for k in saved.keys()
            if k not in keys and k not in ("_completed", "job_name", "completed")
        ])
        for key in keys:
            if key in ("_completed", "job_name", "completed"):
                continue
            if key.startswith("other_hw"):
                suffix = key.replace("other_hw", "", 1)
                target_idx = 1
                if suffix.startswith("_") and suffix[1:].isdigit():
                    target_idx = int(suffix[1:])
                canvas_other_rows = getattr(canvas, "_other_hw_rows", [])
                while len(canvas_other_rows) < target_idx and hasattr(canvas, "_add_other_hw_line"):
                    canvas._add_other_hw_line()  # type: ignore[attr-defined]
            f = canvas._fields.get(key)
            val = saved.get(key)
            if f is None or val is None:
                continue
            if isinstance(f, QLineEdit):
                f.setText(str(val))
            elif isinstance(f, QComboBox):
                text = str(val)
                idx = f.findText(text)
                if idx >= 0:
                    f.setCurrentIndex(idx)
                else:
                    f.setCurrentText(text)
            elif isinstance(f, QCheckBox):
                if isinstance(val, bool):
                    f.setChecked(val)
                else:
                    f.setChecked(str(val).strip().lower() in ("1", "true", "yes", "x"))

    def _on_canvas_completed_changed(self, row: int, completed: bool) -> None:
        if row < 0 or row >= len(self._sheets):
            return
        key = self._sheet_state_key(self._sheets[row])
        saved = self._sheet_state.get(key, {})
        if not isinstance(saved, dict):
            saved = {}
        saved["_completed"] = bool(completed)
        self._sheet_state[key] = saved
        self._set_list_item_completed(row, bool(completed))

    def closeEvent(self, event: QCloseEvent) -> None:
        self._capture_row_state(self._active_row)
        self._persist_sheet_state()
        super().closeEvent(event)

    def _on_sheet_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._sheets):
            return
        # Save outgoing sheet state before switching.
        self._capture_row_state(self._active_row)
        self._persist_sheet_state()
        # Detach current widget so QScrollArea doesn't delete it
        old = self._scroll.takeWidget()
        if old is not None:
            old.setParent(self)
            old.hide()
        if row not in self._canvases:
            self._canvases[row] = FabSheetCanvas(
                self._sheets[row],
                self._job_name,
                self,
                on_completed_changed=lambda checked, _row=row: self._on_canvas_completed_changed(_row, checked),
            )
            self._apply_row_state(row)
        self._scroll.setWidget(self._canvases[row])
        self._active_row = row

    def _prev_sheet(self) -> None:
        cur = self._sheet_list.currentRow()
        if cur > 0:
            self._sheet_list.setCurrentRow(cur - 1)

    def _next_sheet(self) -> None:
        cur = self._sheet_list.currentRow()
        if cur < len(self._sheets) - 1:
            self._sheet_list.setCurrentRow(cur + 1)

    # ── PDF export ──────────────────────────────────────────────────

    def _on_auto_open_toggled(self, checked: bool) -> None:
        self._settings.setValue("fab_sheet/auto_open_after_export", checked)

    def _auto_open_enabled(self) -> bool:
        return bool(self._settings.value("fab_sheet/auto_open_after_export", True, type=bool))

    def _field_overrides_for_index(self, idx: int) -> Dict[str, str]:
        canvas_widget = self._canvases.get(idx)
        field_overrides: Dict[str, str] = {}
        if canvas_widget:
            for k in canvas_widget._fields:
                v = canvas_widget.field_value(k)
                if v:
                    field_overrides[k] = v
        return field_overrides

    def _open_pdf_file(self, path: str) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).resolve())))

    def _preview_current_pdf(self) -> None:
        idx = self._sheet_list.currentRow()
        if idx < 0 or idx >= len(self._sheets):
            QMessageBox.information(self, "Preview", "No sheet selected.")
            return
        from ui.fab_sheet_pdf import render_fab_sheet_pdf

        sheet = self._sheets[idx]
        field_overrides = self._field_overrides_for_index(idx)
        safe_dt = sheet.door_type.replace("/", "-").replace("\\", "-") if sheet.door_type else "FabSheet"
        out = Path(tempfile.gettempdir()) / f"GORO-Preview-{safe_dt}.pdf"
        try:
            render_fab_sheet_pdf(str(out), sheet, self._job_name, field_overrides)
        except (PermissionError, OSError) as exc:
            QMessageBox.warning(self, "Preview", f"Could not generate preview PDF.\n\nError: {exc}")
            return
        self._open_pdf_file(str(out))

    def _preview_all_pdf(self) -> None:
        if not self._sheets:
            QMessageBox.information(self, "Preview All", "No fab sheets to preview.")
            return
        from ui.fab_sheet_pdf import render_fab_sheets_pdf

        overrides_by_index = {
            i: self._field_overrides_for_index(i)
            for i in range(len(self._sheets))
            if self._canvases.get(i) is not None
        }
        out = Path(tempfile.gettempdir()) / "GORO-Preview-All-Fab-Sheets.pdf"
        try:
            render_fab_sheets_pdf(str(out), self._sheets, self._job_name, overrides_by_index)
        except (PermissionError, OSError) as exc:
            QMessageBox.warning(self, "Preview All", f"Could not generate preview PDF.\n\nError: {exc}")
            return
        self._open_pdf_file(str(out))

    def _export_current_pdf(self) -> None:
        idx = self._sheet_list.currentRow()
        if idx < 0 or idx >= len(self._sheets):
            QMessageBox.information(self, "Export", "No sheet selected.")
            return
        from ui.fab_sheet_pdf import render_fab_sheet_pdf
        sheet = self._sheets[idx]

        default_dir = str(self._workbook_path) if self._workbook_path else ""
        safe_dt = sheet.door_type.replace("/", "-").replace("\\", "-") if sheet.door_type else "FabSheet"
        default_name = f"Fab Sheet - {safe_dt}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Fab Sheet PDF",
            str(Path(default_dir) / default_name) if default_dir else default_name,
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        field_overrides = self._field_overrides_for_index(idx)

        try:
            render_fab_sheet_pdf(path, sheet, self._job_name, field_overrides)
        except PermissionError as exc:
            QMessageBox.warning(
                self,
                "Export",
                "Could not save the PDF due to a file permission error.\n\n"
                "Close the PDF if it is open, or choose a different folder/file name, then try again.\n\n"
                f"Path: {path}\n"
                f"Error: {exc}",
            )
            return
        except OSError as exc:
            QMessageBox.warning(
                self,
                "Export",
                f"Could not save the PDF.\n\nPath: {path}\nError: {exc}",
            )
            return
        if self._auto_open_enabled():
            self._open_pdf_file(path)
        QMessageBox.information(self, "Export", f"PDF saved to:\n{path}")

    def _export_all_pdf(self) -> None:
        if not self._sheets:
            QMessageBox.information(self, "Export All", "No fab sheets to export.")
            return
        from ui.fab_sheet_pdf import render_fab_sheet_pdf

        default_dir = str(self._workbook_path) if self._workbook_path else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", default_dir)
        if not folder:
            return

        count = 0
        first_export = ""
        failed: list[str] = []
        for i, sheet in enumerate(self._sheets):
            field_overrides = self._field_overrides_for_index(i)

            safe_dt = sheet.door_type.replace("/", "-").replace("\\", "-") if sheet.door_type else "FabSheet"
            safe_prep = sheet.prep_string.replace("+", "_") if sheet.prep_string else "NP"
            out = Path(folder) / f"Fab Sheet - {safe_dt} [{safe_prep}].pdf"
            try:
                render_fab_sheet_pdf(str(out), sheet, self._job_name, field_overrides)
                count += 1
                if count == 1:
                    first_export = str(out)
            except (PermissionError, OSError) as exc:
                failed.append(f"{out.name}: {exc}")

        if failed:
            details = "\n".join(failed[:8])
            more = ""
            if len(failed) > 8:
                more = f"\n... and {len(failed) - 8} more"
            QMessageBox.warning(
                self,
                "Export All",
                f"Exported {count} fab sheet PDFs to:\n{folder}\n\n"
                f"{len(failed)} file(s) could not be written:\n{details}{more}",
            )
            return

        if self._auto_open_enabled():
            if count == 1 and first_export:
                self._open_pdf_file(first_export)
            elif count > 1:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(folder).resolve())))
        QMessageBox.information(self, "Export All", f"Exported {count} fab sheet PDFs to:\n{folder}")
