"""CombinedHardwareWidget extracted from main_window.py."""

import csv
import re
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QRadioButton,
    QScrollArea,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.constants import APP_NAME, ORG_NAME
from core.email_utils import (
    filter_table_by_vendor,
    get_vendor_list_from_table,
    launch_outlook_with_pdf,
    load_vendor_contacts,
)
from core.models import resolve_data_root
from .dialogs import VendorQuoteDialog
from .main_window_hw_groups import write_hardware_groups_pdf
from .main_window_hardware_groups_widget import (
    _ensure_single_trailing_blank_row,
    _trim_trailing_blank_rows,
    _get_dropdown_values_for_header,
    load_dropdown_options,
)
from .main_window_ui_helpers import QMessageBox
from .hardware_configurator import HardwareConfiguratorDialog
from core.optional_services import HAS_REPORTLAB
from widgets.table_helpers import ComboBoxDelegate, HardwarePasteEventFilter, NoRowHeaderTable


class CombinedHardwareWidget(QWidget):
    """Combined widget showing Hardware table, Groups, and Assigned Openings."""

    def __init__(self, workbook_path, schedule_data, hardware_all_data, hardware_groups_data, hardware_csv_path, parent=None, mark_changed_callback=None):
        super().__init__(parent)
        self.workbook_path = workbook_path
        self.hardware_csv_path = hardware_csv_path
        self.mark_changed_callback = mark_changed_callback
        self.schedule_headers, self.schedule_rows = schedule_data
        self.hardware_all_headers, self.hardware_all_rows = hardware_all_data
        self.hardware_groups_headers, self.hardware_groups_rows = hardware_groups_data
        self.current_group = None
        self.changes_made = False
        self._hardware_old_values = {}
        self.hardware_part_col_idx = None
        self.hardware_count_col_idx = None
        self.hardware_part_id_col_idx = None
        self.hardware_groups_part_id_col_idx = None
        self.hardware_table: NoRowHeaderTable
        self._hardware_paste_filter: HardwarePasteEventFilter | None = None
        self.hardware_filter_edit: QLineEdit
        self.hardware_filter_column_combo: QComboBox
        self.group_list: QListWidget
        self.completed_checkbox: QCheckBox

        self._ensure_part_ids()
        
        self.setup_ui()
        self.load_hardware_table()
        self._install_hardware_paste_filter()
        self.load_hardware_groups()
        # Initial calculation of hardware counts
        self.recalculate_all_hardware_counts()
    
    def setup_ui(self):
        """Setup the three-panel UI layout."""
        main_layout = QHBoxLayout(self)
        
        # Create horizontal splitter for three sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL: Hardware Table with checkboxes
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_header_layout = QHBoxLayout()

        add_part_button = QPushButton("Add New Hardware Part")
        add_part_button.clicked.connect(self.show_add_hardware_part_dialog)
        add_part_button.setMaximumWidth(200)
        left_header_layout.addWidget(add_part_button)

        configure_part_button = QPushButton("Configure Part")
        configure_part_button.clicked.connect(self.show_configure_part_wizard)
        configure_part_button.setMaximumWidth(160)
        left_header_layout.addWidget(configure_part_button)

        consolidate_button = QPushButton("Consolidate")
        consolidate_button.clicked.connect(self.consolidate_hardware_parts)
        consolidate_button.setMaximumWidth(160)
        left_header_layout.addWidget(consolidate_button)

        email_quote_button = QPushButton("Email Quote")
        email_quote_button.clicked.connect(self.email_hardware_quote)
        email_quote_button.setMaximumWidth(140)
        left_header_layout.addWidget(email_quote_button)

        left_label = QLabel("Hardware - All Parts")
        left_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_header_layout.addWidget(left_label)
        left_header_layout.addStretch()

        left_layout.addLayout(left_header_layout)

        filter_row = QHBoxLayout()
        filter_label = QLabel("Filter:")
        filter_row.addWidget(filter_label)

        self.hardware_filter_edit = QLineEdit()
        self.hardware_filter_edit.setPlaceholderText("Type to filter hardware parts...")
        self.hardware_filter_edit.textChanged.connect(self.apply_hardware_filter)
        filter_row.addWidget(self.hardware_filter_edit, 1)

        self.hardware_filter_column_combo = QComboBox()
        self.hardware_filter_column_combo.addItem("All Columns", -1)
        for idx, header in enumerate(self.hardware_all_headers):
            header_text = str(header).strip() if header else ""
            if header_text.lower() == "part id":
                continue
            self.hardware_filter_column_combo.addItem(header_text or f"Column {idx + 1}", idx)
        self.hardware_filter_column_combo.currentIndexChanged.connect(self.apply_hardware_filter)
        filter_row.addWidget(self.hardware_filter_column_combo)

        clear_filter_button = QPushButton("Clear")
        clear_filter_button.setMaximumWidth(90)
        clear_filter_button.clicked.connect(self.clear_hardware_filter)
        filter_row.addWidget(clear_filter_button)

        left_layout.addLayout(filter_row)
        
        self.hardware_table = NoRowHeaderTable()
        self.hardware_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | 
                                           QAbstractItemView.EditTrigger.EditKeyPressed | 
                                           QAbstractItemView.EditTrigger.AnyKeyPressed)
        self.hardware_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.hardware_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.hardware_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        left_layout.addWidget(self.hardware_table)
        
        # MIDDLE PANEL: Hardware Groups
        middle_widget = QWidget()
        middle_layout = QHBoxLayout(middle_widget)

        # Group list (scrollable)
        group_list_widget = QWidget()
        group_list_layout = QVBoxLayout(group_list_widget)
        group_label = QLabel("Hardware Groups")
        group_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.group_list = QListWidget()
        self.group_list.setMinimumWidth(150)
        self.group_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.group_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.group_list.currentItemChanged.connect(self.on_group_selected)

        group_list_layout.addWidget(group_label)
        group_list_layout.addWidget(self.group_list)

        # Group detail area (buttons + parts table)
        group_detail_widget = QWidget()
        group_detail_layout = QVBoxLayout(group_detail_widget)
        
        # Button row
        button_layout = QHBoxLayout()
        
        create_group_button = QPushButton("Create New Group")
        create_group_button.clicked.connect(self.create_new_hardware_group)
        create_group_button.setMaximumWidth(150)
        button_layout.addWidget(create_group_button)
        
        add_selected_button = QPushButton("Add Selected to Group")
        add_selected_button.clicked.connect(self.add_selected_to_group)
        add_selected_button.setMaximumWidth(200)
        button_layout.addWidget(add_selected_button)
        
        remove_selected_button = QPushButton("Remove Selected")
        remove_selected_button.clicked.connect(self.remove_selected_from_group)
        remove_selected_button.setMaximumWidth(200)
        button_layout.addWidget(remove_selected_button)
        
        delete_group_button = QPushButton("Delete Group")
        delete_group_button.clicked.connect(self.delete_current_group)
        delete_group_button.setMaximumWidth(150)
        button_layout.addWidget(delete_group_button)

        pdf_groups_button = QPushButton("PDF Hardware Groups")
        pdf_groups_button.clicked.connect(lambda: self.export_hardware_groups_pdf(self.parent()))
        pdf_groups_button.setMaximumWidth(180)
        button_layout.addWidget(pdf_groups_button)

        button_layout.addStretch()
        
        group_detail_layout.addLayout(button_layout)

        # Group status row
        group_status_layout = QHBoxLayout()
        self.prep_string_label = QLabel("Prep: —")
        self.prep_string_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        group_status_layout.addWidget(self.prep_string_label)
        group_status_layout.addStretch()
        self.completed_checkbox = QCheckBox("Completed")
        self.completed_checkbox.stateChanged.connect(self.on_group_completed_changed)
        group_status_layout.addWidget(self.completed_checkbox)
        group_detail_layout.addLayout(group_status_layout)
        
        # Hardware parts table for selected group
        self.parts_table = NoRowHeaderTable()
        self.parts_table.setColumnCount(7)
        self.parts_table.setHorizontalHeaderLabels(["Select", "Hardware Part", "MFR", "Finish", "Category", "Prep Code", "COUNT"])
        parts_header = self.parts_table.horizontalHeader()
        assert parts_header is not None
        parts_header.setStretchLastSection(False)
        parts_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        parts_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        parts_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        parts_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        parts_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        parts_header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        parts_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.parts_table.setColumnWidth(0, 60)
        self.parts_table.setColumnWidth(6, 80)
        
        self.parts_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        
        self.parts_table.itemChanged.connect(self.on_part_changed)
        
        # Enable row context menu for parts table
        self.parts_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.parts_table.customContextMenuRequested.connect(self.show_parts_context_menu)
        
        group_detail_layout.addWidget(self.parts_table)

        middle_layout.addWidget(group_list_widget)
        middle_layout.addWidget(group_detail_widget)
        middle_layout.setStretch(0, 0)
        middle_layout.setStretch(1, 1)
        
        # RIGHT PANEL: Assigned Openings
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        openings_label = QLabel("Assigned Openings")
        openings_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(openings_label)
        
        self.openings_table = NoRowHeaderTable()
        self.openings_table.setColumnCount(3)
        self.openings_table.setHorizontalHeaderLabels(["Assigned Openings", "Door Type", "Frame Type"])
        _ot_header = self.openings_table.horizontalHeader()
        assert _ot_header is not None
        _ot_header.setStretchLastSection(True)
        self.openings_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.openings_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.openings_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d30;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                color: #cccccc;
            }
        """)
        
        right_layout.addWidget(self.openings_table)
        
        # Add panels to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(middle_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)  # Hardware table gets more space
        splitter.setStretchFactor(1, 2)  # Groups table
        splitter.setStretchFactor(2, 1)  # Openings table
        
        main_layout.addWidget(splitter)

    def apply_theme(self, theme_colors):
        """Apply theme colors to all tables in this widget."""
        c = theme_colors
        
        # Hardware table style
        hardware_style = f"""
            QTableWidget {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                gridline-color: {c['gridline']};
            }}
            QTableWidget::item {{
                color: {c['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: {c['selection_bg']};
                color: {c['selection_text']};
            }}
        """
        self.hardware_table.setStyleSheet(hardware_style)
        
        # Group list style
        group_style = f"""
            QListWidget {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                gridline-color: {c['gridline']};
            }}
            QListWidget::item:selected {{
                background-color: {c['selection_bg']};
                color: {c['selection_text']};
            }}
        """
        self.group_list.setStyleSheet(group_style)
        
        # Parts table style (same as hardware)
        self.parts_table.setStyleSheet(hardware_style)
        
        # Openings table style
        openings_style = f"""
            QTableWidget {{
                background-color: {c['panel_bg']};
                color: {c['text_primary']};
                gridline-color: {c['gridline']};
            }}
            QTableWidget::item {{
                color: {c['text_primary']};
            }}
        """
        self.openings_table.setStyleSheet(openings_style)

    def _get_header_index(self, headers, name):
        name_lower = name.strip().lower()
        for idx, header in enumerate(headers):
            if header.strip().lower() == name_lower:
                return idx
        return None

    def _get_hardware_groups_qty_indices(self):
        """Return all existing quantity-like column indices in priority order."""
        qty_indices = []
        for header_name in ("Qty", "Count", "Quantity"):
            idx = self._get_header_index(self.hardware_groups_headers, header_name)
            if idx is not None and idx not in qty_indices:
                qty_indices.append(idx)
        return qty_indices

    def _read_hardware_group_row_qty(self, row, qty_indices=None):
        """Read quantity from a row using the first non-empty qty-like column."""
        if qty_indices is None:
            qty_indices = self._get_hardware_groups_qty_indices()
        if not qty_indices:
            return ""

        for qty_idx in qty_indices:
            if len(row) > qty_idx:
                value = str(row[qty_idx]).strip()
                if value:
                    return value

        primary_idx = qty_indices[0]
        if len(row) > primary_idx:
            return str(row[primary_idx]).strip()
        return ""

    def _ensure_part_ids(self):
        part_id_idx = self._get_header_index(self.hardware_all_headers, "Part ID")
        if part_id_idx is None:
            self.hardware_all_headers.append("Part ID")
            for row in self.hardware_all_rows:
                row.append("")
            part_id_idx = len(self.hardware_all_headers) - 1
        self.hardware_part_id_col_idx = part_id_idx

        for row in self.hardware_all_rows:
            if len(row) <= part_id_idx:
                row.extend([""] * (part_id_idx + 1 - len(row)))
            if not str(row[part_id_idx]).strip():
                row[part_id_idx] = self._generate_part_id()

        self._normalize_hardware_groups_schema()

    def _generate_part_id(self):
        return uuid.uuid4().hex

    def _normalize_hardware_groups_schema(self):
        """Normalize hardware groups data structure - ensure key columns exist without deleting data."""
        # Ensure headers have required columns.
        required_headers = ["Hardware Group", "Part ID", "Completed"]
        for req_header in required_headers:
            if req_header not in self.hardware_groups_headers:
                self.hardware_groups_headers.insert(len(self.hardware_groups_headers), req_header)

        # Ensure at least one quantity-like column exists.
        if not self._get_hardware_groups_qty_indices():
            self.hardware_groups_headers.append("Qty")
        
        # Get column indices
        group_idx = self._get_header_index(self.hardware_groups_headers, "Hardware Group")
        if group_idx is None:
            group_idx = 0
        part_id_idx = self._get_header_index(self.hardware_groups_headers, "Part ID")
        completed_idx = self._get_header_index(self.hardware_groups_headers, "Completed")
        
        # Expand rows to have all required columns (non-destructive)
        for row in self.hardware_groups_rows:
            while len(row) < len(self.hardware_groups_headers):
                row.append("")
        
        # Set column indices for later reference
        if part_id_idx is not None:
            self.hardware_groups_part_id_col_idx = part_id_idx

    def _get_part_id_for_name(self, part_name):
        if not part_name or self.hardware_part_id_col_idx is None:
            return ""
        table_match_row = None
        if self.hardware_table is not None and self.hardware_part_col_idx is not None:
            part_col_in_table = self.hardware_part_col_idx + 1
            part_id_col_in_table = self.hardware_part_id_col_idx + 1
            for row_idx in range(self.hardware_table.rowCount()):
                part_item = self.hardware_table.item(row_idx, part_col_in_table)
                if part_item and part_item.text().strip().lower() == part_name.lower():
                    part_id_item = self.hardware_table.item(row_idx, part_id_col_in_table)
                    if part_id_item and part_id_item.text().strip():
                        return part_id_item.text().strip()
                    table_match_row = row_idx
                    break
        part_name_col = self._get_hardware_part_col_idx()
        for row in self.hardware_all_rows:
            if len(row) > max(part_name_col, self.hardware_part_id_col_idx):
                name = row[part_name_col].strip()
                if name.lower() == part_name.lower():
                    part_id = row[self.hardware_part_id_col_idx].strip()
                    if part_id and table_match_row is not None and self.hardware_table is not None:
                        part_id_item = self.hardware_table.item(table_match_row, self.hardware_part_id_col_idx + 1)
                        if part_id_item is None:
                            part_id_item = QTableWidgetItem("")
                            part_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                            part_id_item.setBackground(QColor(60, 60, 60))
                            part_id_item.setForeground(QColor(200, 200, 200))
                            self.hardware_table.setItem(table_match_row, self.hardware_part_id_col_idx + 1, part_id_item)
                        part_id_item.setText(part_id)
                    return part_id
        return ""

    def _get_part_name_for_id(self, part_id):
        if not part_id or self.hardware_part_id_col_idx is None:
            return ""
        if self.hardware_table is not None and self.hardware_part_col_idx is not None:
            part_col_in_table = self.hardware_part_col_idx + 1
            part_id_col_in_table = self.hardware_part_id_col_idx + 1
            for row_idx in range(self.hardware_table.rowCount()):
                part_id_item = self.hardware_table.item(row_idx, part_id_col_in_table)
                if part_id_item and part_id_item.text().strip() == part_id:
                    part_item = self.hardware_table.item(row_idx, part_col_in_table)
                    return part_item.text().strip() if part_item else ""
        part_name_col = self._get_hardware_part_col_idx()
        for row in self.hardware_all_rows:
            if len(row) > max(part_name_col, self.hardware_part_id_col_idx):
                if row[self.hardware_part_id_col_idx].strip() == part_id:
                    return row[part_name_col].strip()
        return ""

    def _get_hardware_row_by_part_id(self, part_id):
        if not part_id:
            return {}

        if self.hardware_table is not None and self.hardware_part_id_col_idx is not None:
            part_id_col_in_table = self.hardware_part_id_col_idx + 1
            for row_idx in range(self.hardware_table.rowCount()):
                part_id_item = self.hardware_table.item(row_idx, part_id_col_in_table)
                if part_id_item and part_id_item.text().strip() == part_id:
                    row_values = {}
                    for col_idx, header in enumerate(self.hardware_all_headers):
                        item = self.hardware_table.item(row_idx, col_idx + 1)
                        value = item.text().strip() if item else ""
                        row_values[header.strip().lower()] = value
                    return row_values

        for row in self.hardware_all_rows:
            if self.hardware_part_id_col_idx is not None and len(row) > self.hardware_part_id_col_idx and row[self.hardware_part_id_col_idx].strip() == part_id:
                row_values = {}
                for col_idx, header in enumerate(self.hardware_all_headers):
                    value = row[col_idx].strip() if col_idx < len(row) and row[col_idx] else ""
                    row_values[header.strip().lower()] = value
                return row_values

        return {}

    def get_group_prep_string(self, group_name: str) -> str:
        """Return the canonical prep string for a hardware group.

        Collects every non-blank Prep Code from the parts assigned to the group,
        de-duplicates them, sorts alphabetically, and joins with '+'.
        E.g. parts with codes 'LP', 'CL', 'LP' → 'CL+LP'
        """
        group_idx = self._get_header_index(self.hardware_groups_headers, "Hardware Group")
        if group_idx is None:
            group_idx = 0
        part_id_idx = self._get_header_index(self.hardware_groups_headers, "Part ID")
        if part_id_idx is None:
            return ""

        codes: set[str] = set()
        for row in self.hardware_groups_rows:
            row_group = row[group_idx].strip() if len(row) > group_idx else ""
            if row_group != group_name:
                continue
            part_id = row[part_id_idx].strip() if len(row) > part_id_idx else ""
            if not part_id:
                continue
            hw_row = self._get_hardware_row_by_part_id(part_id)
            code = hw_row.get("prep code", "").strip()
            if code:
                codes.add(code)

        return "+".join(sorted(codes))

    def _refresh_prep_string_label(self):
        """Update the prep string label for the currently selected group."""
        if not hasattr(self, "prep_string_label") or self.prep_string_label is None:
            return
        if not self.current_group:
            self.prep_string_label.setText("Prep: \u2014")
            return
        s = self.get_group_prep_string(self.current_group)
        self.prep_string_label.setText(f"Prep: {s}" if s else "Prep: \u2014")

    def load_hardware_table(self):
        """Load all hardware parts into the left table with checkboxes."""
        try:
            self.hardware_table.itemChanged.disconnect(self.on_hardware_table_changed)
        except Exception:
            pass
        try:
            self.hardware_table.itemClicked.disconnect(self.on_hardware_table_clicked)
        except Exception:
            pass
        previous_current_handler = getattr(self, "_hardware_current_item_changed_handler", None)
        if previous_current_handler is not None:
            try:
                self.hardware_table.currentItemChanged.disconnect(previous_current_handler)
            except Exception:
                pass
        try:
            self.hardware_table.customContextMenuRequested.disconnect(self.show_hardware_context_menu)
        except Exception:
            pass

        self.hardware_table.blockSignals(True)
        self.hardware_table.setSortingEnabled(False)
        
        # Set up columns including checkbox column
        cols = ["Select"] + self.hardware_all_headers
        self.hardware_table.setColumnCount(len(cols))
        self.hardware_table.setHorizontalHeaderLabels(cols)
        
        # Keep exactly one trailing blank row
        row_count = len(self.hardware_all_rows) + 1
        self.hardware_table.setRowCount(row_count)
        
        # Find Quoted column index in original data
        quoted_col_idx = None
        count_col_idx = None
        part_id_col_idx = None
        part_col_idx = self._get_hardware_part_col_idx()
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() == "quoted":
                quoted_col_idx = idx
            if header.strip().lower() in ("count", "qty", "quantity"):
                count_col_idx = idx
            if header.strip().lower() == "part id":
                part_id_col_idx = idx
        self.hardware_part_col_idx = part_col_idx
        self.hardware_count_col_idx = count_col_idx
        self.hardware_part_id_col_idx = part_id_col_idx
        
        # Load existing data and fill remaining rows with empty editable cells
        for row_idx in range(row_count):
            # Checkbox in first column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setText("")
            self.hardware_table.setItem(row_idx, 0, checkbox_item)
            
            # Get row data if it exists, otherwise use empty values
            if row_idx < len(self.hardware_all_rows):
                row_data = self.hardware_all_rows[row_idx]
            else:
                row_data = [""] * len(self.hardware_all_headers)

            part_name = row_data[part_col_idx].strip() if part_col_idx is not None and part_col_idx < len(row_data) else ""
            if part_id_col_idx is not None:
                part_id = row_data[part_id_col_idx].strip() if part_id_col_idx < len(row_data) else ""
                if not part_id and part_name:
                    part_id = self._generate_part_id()
                    if part_id_col_idx < len(row_data):
                        row_data[part_id_col_idx] = part_id
                    if row_idx < len(self.hardware_all_rows) and part_id_col_idx < len(self.hardware_all_rows[row_idx]):
                        self.hardware_all_rows[row_idx][part_id_col_idx] = part_id
            
            # Rest of the columns
            for col_idx in range(len(self.hardware_all_headers)):
                value = row_data[col_idx] if col_idx < len(row_data) else ""
                item = QTableWidgetItem(str(value) if value else "")
                
                # Handle Quoted column as checkbox
                if col_idx == quoted_col_idx:
                    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    item.setCheckState(Qt.CheckState.Checked if str(value).lower() == "yes" else Qt.CheckState.Unchecked)
                    item.setText("")
                elif col_idx == part_id_col_idx:
                    # Part ID is internal; prevent manual edits
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setBackground(QColor(60, 60, 60))
                    item.setForeground(QColor(200, 200, 200))
                elif col_idx == count_col_idx:
                    # Count is calculated; prevent manual edits
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setBackground(QColor(60, 60, 60))
                    item.setForeground(QColor(200, 200, 200))
                else:
                    # Make sure non-checkbox cells are editable
                    item.setFlags(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                
                self.hardware_table.setItem(row_idx, col_idx + 1, item)  # +1 because of Select column
        
        # Resize columns
        self.hardware_table.resizeColumnsToContents()
        _hw_header = self.hardware_table.horizontalHeader()
        assert _hw_header is not None
        _hw_header.setStretchLastSection(True)

        if part_id_col_idx is not None:
            self.hardware_table.setColumnHidden(part_id_col_idx + 1, True)
        
        # Connect change handlers - use multiple signals to catch both text and checkbox changes
        self.hardware_table.itemChanged.connect(self.on_hardware_table_changed)
        self.hardware_table.itemClicked.connect(self.on_hardware_table_clicked)

        def on_hardware_current_item_changed(current, previous, old_vals=self._hardware_old_values):
            if current:
                key = (current.row(), current.column())
                old_vals[key] = current.text()

        self._hardware_current_item_changed_handler = on_hardware_current_item_changed
        self.hardware_table.currentItemChanged.connect(self._hardware_current_item_changed_handler)

        # Enable row context menu for hardware table
        self.hardware_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.hardware_table.customContextMenuRequested.connect(self.show_hardware_context_menu)

        # Set up vendor dropdown delegate for Vendor column
        vendor_col_idx = None
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() == "vendor":
                vendor_col_idx = idx
                break

        if vendor_col_idx is not None:
            vendors_data = self._load_vendors_for_hardware()
            filtered_vendors = []
            for vendor_name, vendor_info in vendors_data.items():
                raw_capabilities = vendor_info.get('capabilities', [])
                capabilities = [str(cap).strip() for cap in raw_capabilities if str(cap).strip()]

                if not capabilities:
                    continue

                capabilities_lower = {cap.lower() for cap in capabilities}
                if "hardware" in capabilities_lower:
                    filtered_vendors.append(vendor_name)

            vendor_names = sorted(set(filtered_vendors))
            if vendor_names:
                delegate = ComboBoxDelegate(vendor_names, self.hardware_table)
                self.hardware_table.setItemDelegateForColumn(vendor_col_idx + 1, delegate)

        # Set up editable Category dropdown delegate populated from Hardware Auto Labor settings
        category_col_idx = None
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() == "category":
                category_col_idx = idx
                break

        if category_col_idx is not None:
            settings = QSettings(ORG_NAME, APP_NAME)
            default_hw_map = (
                "Hinge=0.125\n"
                "ETW=0.5\n"
                "Lock=1\n"
                "Panic=1.5\n"
                "Cylinder=0.25\n"
                "Electric strike=1\n"
                "FlushBolt=0.5\n"
                "Coordinator=0.5\n"
                "Closer=0.75\n"
                "Protection Plate=0.5\n"
                "Pretection Plate=0.5\n"
                "Wall/ Floor Stop=0.5\n"
                "OH Stop=0.75\n"
                "Smoke seal=0.25\n"
                "Drop Bottom=0.5\n"
                "Threshold=0.5\n"
                "Power Supply=0.25"
            )
            hw_map_text = settings.value("labor_hw_map", default_hw_map, type=str)
            categories = []
            for line in hw_map_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                if "=" in line:
                    category = line.split("=", 1)[0].strip()
                elif ":" in line:
                    category = line.split(":", 1)[0].strip()
                else:
                    continue
                if category and category not in categories:
                    categories.append(category)

            if categories:
                delegate = ComboBoxDelegate(categories, self.hardware_table, editable=True)
                self.hardware_table.setItemDelegateForColumn(category_col_idx + 1, delegate)

        # Set up category-aware Prep Code dropdown delegate
        prep_code_col_idx = None
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() == "prep code":
                prep_code_col_idx = idx
                break

        if prep_code_col_idx is not None:
            from core.prep_codes import PrepCodeDB
            from core.prep_code_delegate import PrepCodeDelegate
            prep_db = PrepCodeDB.load_default()
            cat_col_in_table = (category_col_idx + 1) if category_col_idx is not None else -1
            if cat_col_in_table > 0:
                prep_delegate = PrepCodeDelegate(prep_db, cat_col_in_table, self.hardware_table)
                self.hardware_table.setItemDelegateForColumn(prep_code_col_idx + 1, prep_delegate)

        self.hardware_table.setSortingEnabled(True)
        self.apply_hardware_filter()
        self.hardware_table.blockSignals(False)

    def reload_from_disk(self, schedule_data, hardware_all_data, hardware_groups_data):
        """Refresh the widget from workbook CSV data without rebuilding the dialog."""
        current_group = self.current_group
        self.schedule_headers, self.schedule_rows = schedule_data
        self.hardware_all_headers, self.hardware_all_rows = hardware_all_data
        self.hardware_groups_headers, self.hardware_groups_rows = hardware_groups_data
        self._ensure_part_ids()
        self.load_hardware_table()
        self.load_hardware_groups()
        self.recalculate_all_hardware_counts()
        self.changes_made = False

        if current_group:
            matches = self.group_list.findItems(current_group, Qt.MatchFlag.MatchExactly)
            if matches:
                self.group_list.setCurrentItem(matches[0])

    def clear_hardware_filter(self):
        """Clear active hardware table filters."""
        if self.hardware_filter_edit is not None:
            self.hardware_filter_edit.clear()
        if self.hardware_filter_column_combo is not None:
            self.hardware_filter_column_combo.setCurrentIndex(0)
        self.apply_hardware_filter()

    def _is_hardware_row_blank(self, row_idx):
        """Return True when a hardware row has no data in non-checkbox columns."""
        if not self.hardware_table:
            return True

        for col in range(1, self.hardware_table.columnCount()):
            if self.hardware_part_id_col_idx is not None and col == self.hardware_part_id_col_idx + 1:
                continue
            item = self.hardware_table.item(row_idx, col)
            if not item:
                continue
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                if item.checkState() == Qt.CheckState.Checked:
                    return False
                continue
            if item.text().strip():
                return False
        return True

    def _initialize_hardware_table_row(self, row_idx):
        """Ensure a hardware table row has properly configured items in every column."""
        if not self.hardware_table:
            return

        table = self.hardware_table
        if row_idx < 0 or row_idx >= table.rowCount():
            return

        # Select checkbox column
        select_item = table.item(row_idx, 0)
        if select_item is None:
            select_item = QTableWidgetItem("")
            select_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            select_item.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(row_idx, 0, select_item)

        quoted_col_idx = self._get_header_index(self.hardware_all_headers, "quoted")

        for data_col_idx in range(len(self.hardware_all_headers)):
            table_col_idx = data_col_idx + 1
            item = table.item(row_idx, table_col_idx)

            if data_col_idx == quoted_col_idx:
                if item is None:
                    item = QTableWidgetItem("")
                    table.setItem(row_idx, table_col_idx, item)
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setText("")
                continue

            if item is None:
                item = QTableWidgetItem("")
                table.setItem(row_idx, table_col_idx, item)

            if data_col_idx == self.hardware_part_id_col_idx or data_col_idx == self.hardware_count_col_idx:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setBackground(QColor(60, 60, 60))
                item.setForeground(QColor(200, 200, 200))
            else:
                item.setFlags(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

    def _ensure_hardware_table_has_trailing_blank_row(self):
        """Ensure at least one editable blank row exists at the bottom without shrinking existing rows."""
        if not self.hardware_table:
            return

        table = self.hardware_table
        if table.rowCount() == 0:
            table.setRowCount(1)

        last_row_idx = table.rowCount() - 1
        if not self._is_hardware_row_blank(last_row_idx):
            table.setRowCount(table.rowCount() + 1)
            last_row_idx = table.rowCount() - 1

        self._initialize_hardware_table_row(last_row_idx)

    def apply_hardware_filter(self):
        """Apply text filter to Hardware - All Parts rows."""
        if not self.hardware_table:
            return

        filter_text = ""
        if self.hardware_filter_edit is not None:
            filter_text = self.hardware_filter_edit.text().strip().lower()

        selected_data_col = -1
        if self.hardware_filter_column_combo is not None:
            selected_data_col = self.hardware_filter_column_combo.currentData()
            if selected_data_col is None:
                selected_data_col = -1

        for row in range(self.hardware_table.rowCount()):
            if self._is_hardware_row_blank(row):
                self.hardware_table.setRowHidden(row, False if not filter_text else True)
                continue

            if not filter_text:
                self.hardware_table.setRowHidden(row, False)
                continue

            row_match = False
            if selected_data_col == -1:
                for col in range(1, self.hardware_table.columnCount()):
                    if self.hardware_part_id_col_idx is not None and col == self.hardware_part_id_col_idx + 1:
                        continue
                    item = self.hardware_table.item(row, col)
                    text = item.text().lower() if item else ""
                    if filter_text in text:
                        row_match = True
                        break
            else:
                table_col = selected_data_col + 1
                if table_col >= self.hardware_table.columnCount():
                    row_match = True
                else:
                    item = self.hardware_table.item(row, table_col)
                    text = item.text().lower() if item else ""
                    row_match = filter_text in text

            self.hardware_table.setRowHidden(row, not row_match)
    
    def _load_vendors_for_hardware(self):
        """Load vendors from CSV for hardware dropdown."""
        from pathlib import Path
        import csv
        
        settings = QSettings(ORG_NAME, APP_NAME)
        data_dir = resolve_data_root(settings)
        vendors_info_path = data_dir / "vendors_info.csv"
        
        vendors_data = {}
        
        if vendors_info_path.exists():
            try:
                with open(vendors_info_path, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        vendor_name = row.get('Vendor Name', '').strip()
                        if not vendor_name:
                            continue
                        
                        # Parse capabilities (pipe-separated string)
                        capabilities_str = row.get('Capabilities', '')
                        capabilities = []
                        if capabilities_str:
                            capabilities = [cap.strip() for cap in capabilities_str.split('|') if cap.strip()]
                        
                        vendors_data[vendor_name] = {'capabilities': capabilities}
            except Exception:
                pass
        
        return vendors_data

    def _collect_hardware_table_data(self) -> List[dict]:
        """Return hardware table rows as dictionaries keyed by hardware headers."""
        self.commit_pending_edits()

        table_data: List[dict] = []
        for row_idx in range(self.hardware_table.rowCount()):
            if self._is_hardware_row_blank(row_idx):
                continue

            row_dict = {}
            for col_idx, header in enumerate(self.hardware_all_headers):
                item = self.hardware_table.item(row_idx, col_idx + 1)
                row_dict[header] = item.text().strip() if item else ""
            table_data.append(row_dict)

        return table_data

    def _get_hardware_quote_bid_context(self) -> tuple[Optional[object], Optional[Path], str]:
        """Find the hosting main window, current bid path, and display name for email subjects."""
        host = self.parent()
        while host is not None:
            if hasattr(host, "_log_vendor_quote_as_communication"):
                break
            parent_getter = getattr(host, "parent", None)
            host = parent_getter() if callable(parent_getter) else None

        bid_path = None
        bid_name = ""

        if host is not None:
            candidate_path = getattr(host, "_current_editing_path", None)
            if isinstance(candidate_path, Path):
                bid_path = candidate_path
                bid_name = candidate_path.name

        if not bid_name and isinstance(self.workbook_path, Path):
            bid_path = self.workbook_path.parent.parent if len(self.workbook_path.parents) >= 2 else self.workbook_path.parent
            bid_name = bid_path.name if isinstance(bid_path, Path) else ""

        return host, bid_path if isinstance(bid_path, Path) else None, bid_name

    def _resolve_vendor_contacts_csv(self) -> Path:
        """Resolve the vendor contacts CSV used for quote emails."""
        if isinstance(self.workbook_path, Path):
            root_path = self.workbook_path
            while root_path.parent != root_path:
                candidate = root_path.parent / "vendors_contacts.csv"
                if candidate.exists():
                    return candidate
                root_path = root_path.parent

        settings = QSettings(ORG_NAME, APP_NAME)
        return resolve_data_root(settings) / "vendors_contacts.csv"

    def email_hardware_quote(self) -> None:
        """Email a vendor quote for the hardware table using a hardware-only PDF layout."""
        if not HAS_REPORTLAB:
            QMessageBox.warning(
                self,
                "Email Quote",
                "ReportLab is not installed. Run: pip install reportlab",
            )
            return

        try:
            table_data = self._collect_hardware_table_data()
            vendors = get_vendor_list_from_table(table_data, vendor_column="Vendor")

            if not vendors:
                QMessageBox.warning(
                    self,
                    "No Vendors",
                    "No vendors found in the Hardware table. Add vendors to rows before emailing quotes.",
                )
                return

            vendor_dlg = VendorQuoteDialog(vendors, self)
            if vendor_dlg.exec() != QDialog.DialogCode.Accepted:
                return

            selected_vendor = vendor_dlg.get_selected_vendor()
            filtered_data = filter_table_by_vendor(table_data, selected_vendor, vendor_column="Vendor")
            if not filtered_data:
                QMessageBox.warning(self, "No Data", f"No hardware rows found for vendor: {selected_vendor}")
                return

            vendor_contacts = load_vendor_contacts(self._resolve_vendor_contacts_csv())
            vendor_email = vendor_contacts.get(selected_vendor, "")
            if not vendor_email:
                available_vendors = ", ".join(vendor_contacts.keys()) if vendor_contacts else "None"
                QMessageBox.warning(
                    self,
                    "Vendor Not Found",
                    f"No email found for vendor: '{selected_vendor}'\n\n"
                    f"Available vendors:\n{available_vendors}\n\n"
                    "Please check the vendor name in the Hardware table matches vendors_contacts.csv.",
                )
                return

            host, bid_path, bid_name = self._get_hardware_quote_bid_context()
            pdf_path = self._generate_hardware_quote_pdf(selected_vendor, filtered_data, bid_name)
            if not pdf_path:
                QMessageBox.warning(self, "PDF Error", "Failed to generate the hardware quote PDF.")
                return

            settings = QSettings(ORG_NAME, APP_NAME)
            email_body = settings.value(
                "quote_email_template",
                "Hello,\n\nPlease provide a quote for the items listed in the attached PDF.\n\nThank you,\nBid Team",
                type=str,
            )

            bid_prefix = f"{bid_name} - " if bid_name else ""
            email_subject = f"Quote Request - {bid_prefix}Hardware - {selected_vendor}"
            success = launch_outlook_with_pdf(
                recipient_email=vendor_email,
                subject=email_subject,
                body=email_body,
                pdf_path=pdf_path,
            )

            if not success:
                QMessageBox.warning(self, "Error", f"Could not launch Outlook. PDF saved to:\n{pdf_path}")
                return

            QMessageBox.information(
                self,
                "Success",
                f"Email opened in Outlook for {selected_vendor}\n\n"
                f"Email: {vendor_email}\n"
                f"PDF: {pdf_path.name}",
            )

            if host is not None and bid_path and bid_path.exists():
                try:
                    host._log_vendor_quote_as_communication(
                        bid_path=bid_path,
                        table_name="Hardware",
                        vendor_name=selected_vendor,
                        vendor_email=vendor_email,
                        pdf_path=pdf_path,
                        email_subject=email_subject,
                        email_body=email_body,
                    )
                except Exception:
                    pass
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to email hardware quote:\n{exc}")

    def _generate_hardware_quote_pdf(
        self,
        vendor_name: str,
        data: List[dict],
        bid_name: str = "",
    ) -> Optional[Path]:
        """Generate a letter-size portrait PDF for the selected hardware vendor."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

            temp_dir = Path(tempfile.gettempdir()) / "GORO_Quotes"
            temp_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = temp_dir / f"Hardware_{vendor_name.replace(' ', '_')}_{timestamp}.pdf"

            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                leftMargin=0.5 * inch,
                rightMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch,
            )

            styles = getSampleStyleSheet()
            elements = []

            from core.constants import load_company_accent_color, accent_text_color
            _accent = load_company_accent_color()
            _hdr_txt = accent_text_color(_accent)

            from reportlab.lib.styles import ParagraphStyle
            title_style = ParagraphStyle(
                'AccentTitle',
                parent=styles['Heading2'],
                textColor=colors.HexColor(_accent),
            )
            bid_prefix = f"{bid_name} - " if bid_name else ""
            elements.append(
                Paragraph(
                    f"<b>{bid_prefix}Hardware - Quote Request for {vendor_name}</b>",
                    title_style,
                )
            )
            elements.append(Spacer(1, 0.2 * inch))

            display_columns = [
                ("Manufacturer", ["MFR", "Manufacturer"]),
                ("Part", ["Hardware Part", "Part", "Part Name"]),
                ("Finish", ["Finish"]),
                ("Category", ["Category"]),
                ("Count", ["COUNT", "Count", "Qty", "Quantity"]),
            ]

            resolved_columns = []
            sample_row = data[0] if data else {}
            for label, aliases in display_columns:
                actual_key = next((alias for alias in aliases if alias in sample_row), aliases[0])
                resolved_columns.append((label, actual_key))

            table_rows = [[label for label, _ in resolved_columns]]
            for row in data:
                table_rows.append([str(row.get(actual_key, "")).strip() for _, actual_key in resolved_columns])

            col_widths = [1.3 * inch, 2.9 * inch, 1.0 * inch, 1.45 * inch, 0.85 * inch]
            quote_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
            quote_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(_accent)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(_hdr_txt)),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-2, -1), "LEFT"),
                    ("ALIGN", (-1, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ])
            )
            elements.append(quote_table)
            doc.build(elements)
            return pdf_path
        except Exception:
            return None
    
    def on_hardware_table_clicked(self, item):
        """Handle hardware table clicks (especially checkbox changes)."""
        # Force update of hardware data when cells are clicked (especially checkboxes)
        QTimer.singleShot(50, lambda: self.on_hardware_table_changed())

    def _sync_group_parts_to_hardware(self, prune_missing=False):
        """Keep hardware groups in sync with hardware parts list."""
        valid_part_ids = set()

        if self.hardware_part_col_idx is not None:
            part_col_in_table = self.hardware_part_col_idx + 1
            part_id_col_in_table = None
            if self.hardware_part_id_col_idx is not None:
                part_id_col_in_table = self.hardware_part_id_col_idx + 1

            for row_idx in range(self.hardware_table.rowCount()):
                part_item = self.hardware_table.item(row_idx, part_col_in_table)
                part_name = part_item.text().strip() if part_item else ""
                if not part_name:
                    continue
                if part_id_col_in_table is not None:
                    part_id_item = self.hardware_table.item(row_idx, part_id_col_in_table)
                    if part_id_item is None:
                        part_id_item = QTableWidgetItem("")
                        part_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                        part_id_item.setBackground(QColor(60, 60, 60))
                        part_id_item.setForeground(QColor(200, 200, 200))
                        self.hardware_table.setItem(row_idx, part_id_col_in_table, part_id_item)
                    if not part_id_item.text().strip():
                        part_id_item.setText(self._generate_part_id())
                    part_id = part_id_item.text().strip()
                    if part_id:
                        valid_part_ids.add(part_id)

        if self.hardware_groups_part_id_col_idx is None:
            self.hardware_groups_part_id_col_idx = self._get_header_index(self.hardware_groups_headers, "Part ID")

        synced_rows = []
        for row in self.hardware_groups_rows:
            part_id = ""
            if self.hardware_groups_part_id_col_idx is not None and len(row) > self.hardware_groups_part_id_col_idx:
                part_id = row[self.hardware_groups_part_id_col_idx].strip()

            if prune_missing and part_id and part_id not in valid_part_ids:
                continue

            synced_rows.append(row)
        self.hardware_groups_rows = synced_rows
    
    def show_hardware_context_menu(self, pos):
        """Show context menu for hardware table row operations."""
        item = self.hardware_table.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        
        # Create context menu
        menu = QMenu(self.hardware_table)
        copy_action = menu.addAction("Copy Row")
        delete_action = menu.addAction("Delete Row")
        menu.addSeparator()
        insert_action = menu.addAction("Insert Row Above")
        
        action = menu.exec(self.hardware_table.mapToGlobal(pos))
        
        if action == copy_action:
            # Copy row to clipboard
            row_data = []
            for c in range(1, self.hardware_table.columnCount()):  # Skip checkbox column
                item = self.hardware_table.item(row, c)
                if item:
                    if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                        row_data.append("Yes" if item.checkState() == Qt.CheckState.Checked else "")
                    else:
                        row_data.append(item.text())
                else:
                    row_data.append("")
            QApplication.clipboard().setText("\t".join(row_data))  # type: ignore[union-attr]
            QMessageBox.information(self, "Copy Row", f"Row {row + 1} copied to clipboard")
        
        elif action == delete_action:
            # Delete row
            reply = QMessageBox.question(
                self,
                "Delete Row",
                f"Delete row {row + 1}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.hardware_table.removeRow(row)
                self.changes_made = True
                self._sync_group_parts_to_hardware(prune_missing=True)
                if self.current_group:
                    self.load_group_parts()
                self.recalculate_all_hardware_counts()
        
        elif action == insert_action:
            # Insert new row above
            self.hardware_table.insertRow(row)
            self._initialize_hardware_table_row(row)
            self.changes_made = True
    
    def show_parts_context_menu(self, pos):
        """Show context menu for parts table row operations."""
        item = self.parts_table.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        
        # Create context menu
        menu = QMenu(self.parts_table)
        copy_action = menu.addAction("Copy Row")
        delete_action = menu.addAction("Delete Row")
        menu.addSeparator()
        insert_action = menu.addAction("Insert Row Above")
        
        action = menu.exec(self.parts_table.mapToGlobal(pos))
        
        if action == copy_action:
            # Copy row to clipboard
            row_data = []
            for c in range(1, self.parts_table.columnCount()):  # Skip checkbox column
                item = self.parts_table.item(row, c)
                if item:
                    if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                        row_data.append("Yes" if item.checkState() == Qt.CheckState.Checked else "")
                    else:
                        row_data.append(item.text())
                else:
                    row_data.append("")
            QApplication.clipboard().setText("\t".join(row_data))  # type: ignore[union-attr]
            QMessageBox.information(self, "Copy Row", f"Row {row + 1} copied to clipboard")
        
        elif action == delete_action:
            # Delete row
            reply = QMessageBox.question(
                self,
                "Delete Row",
                f"Delete row {row + 1}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.parts_table.removeRow(row)
                self.changes_made = True
                self.save_data()
        
        elif action == insert_action:
            # Insert new row above
            self.parts_table.insertRow(row)
            # Add checkbox in first column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            self.parts_table.setItem(row, 0, checkbox_item)
            self.changes_made = True
    
    def calculate_hardware_counts(self):
        """Calculate total count for each hardware part based on groups and schedule usage."""
        # Find column indices
        catalog_col = None
        count_col = None
        for idx, header in enumerate(self.hardware_all_headers):
            h_lower = header.strip().lower()
            if h_lower in ("hardware part", "catalog number", "part number"):
                catalog_col = idx
            elif h_lower in ("count", "qty", "quantity"):
                count_col = idx
        
        if catalog_col is None or count_col is None:
            return
        
        # Find Hardware Group column in Schedule
        hw_group_col = None
        for idx, header in enumerate(self.schedule_headers):
            if header.strip().lower() == "hardware group":
                hw_group_col = idx
                break
        
        if hw_group_col is None:
            return
        
        # Calculate count for each hardware part
        part_counts_by_id = {}  # {part_id: total_count}
        part_counts_by_name = {}  # {part_name: total_count}

        group_part_id_idx = self._get_header_index(self.hardware_groups_headers, "Part ID")
        group_part_name_idx = self._get_header_index(self.hardware_groups_headers, "Hardware Part")
        if group_part_name_idx is None:
            group_part_name_idx = self._get_header_index(self.hardware_groups_headers, "Part")
        qty_indices = self._get_hardware_groups_qty_indices()
        group_col_idx = self._get_header_index(self.hardware_groups_headers, "Hardware Group")
        if group_col_idx is None:
            group_col_idx = 0

        if not qty_indices:
            return
        
        # For each hardware group in hardware_groups_rows
        for group_row in self.hardware_groups_rows:
            if len(group_row) < 3:
                continue

            group_name = group_row[group_col_idx].strip() if len(group_row) > group_col_idx else ""
            part_id = group_row[group_part_id_idx].strip() if group_part_id_idx is not None and len(group_row) > group_part_id_idx else ""
            part_name = group_row[group_part_name_idx].strip() if group_part_name_idx is not None and len(group_row) > group_part_name_idx else ""

            if not group_name:
                continue

            # Get count of this part in this group
            count_text = self._read_hardware_group_row_qty(group_row, qty_indices)
            try:
                part_count_in_group = float(count_text) if count_text else 0
            except (ValueError, TypeError):
                part_count_in_group = 0
            
            # Count how many times this group appears in schedule
            group_usage_count = 0
            for schedule_row in self.schedule_rows:
                if len(schedule_row) > hw_group_col:
                    schedule_group = schedule_row[hw_group_col].strip()
                    if schedule_group.lower() == group_name.lower():
                        group_usage_count += 1
            
            # Add to total count for this part
            total_for_this_instance = part_count_in_group * group_usage_count
            if part_id:
                if part_id in part_counts_by_id:
                    part_counts_by_id[part_id] += total_for_this_instance
                else:
                    part_counts_by_id[part_id] = total_for_this_instance
            else:
                key = part_name.lower()
                if not key:
                    continue
                if key in part_counts_by_name:
                    part_counts_by_name[key] += total_for_this_instance
                else:
                    part_counts_by_name[key] = total_for_this_instance
        
        # Update hardware_all_rows with calculated counts
        for row in self.hardware_all_rows:
            if len(row) > max(catalog_col, count_col):
                part_name = row[catalog_col].strip()
                part_id = ""
                if self.hardware_part_id_col_idx is not None and len(row) > self.hardware_part_id_col_idx:
                    part_id = row[self.hardware_part_id_col_idx].strip()

                if part_id and part_id in part_counts_by_id:
                    row[count_col] = str(int(part_counts_by_id[part_id]))
                elif part_name and part_name.lower() in part_counts_by_name:
                    row[count_col] = str(int(part_counts_by_name[part_name.lower()]))
                else:
                    row[count_col] = "0"

        # Update hardware table directly for live display
        part_col_in_table = catalog_col + 1  # Table has a checkbox column first
        count_col_in_table = count_col + 1
        self.hardware_table.blockSignals(True)
        for row_idx in range(self.hardware_table.rowCount()):
            part_item = self.hardware_table.item(row_idx, part_col_in_table)
            part_name = part_item.text().strip() if part_item else ""
            part_id = ""
            if self.hardware_part_id_col_idx is not None:
                part_id_item = self.hardware_table.item(row_idx, self.hardware_part_id_col_idx + 1)
                part_id = part_id_item.text().strip() if part_id_item else ""
            if not part_id and part_name:
                part_id = self._get_part_id_for_name(part_name)

            if part_id and part_id in part_counts_by_id:
                count_value = str(int(part_counts_by_id[part_id]))
            elif part_name and part_name.lower() in part_counts_by_name:
                count_value = str(int(part_counts_by_name[part_name.lower()]))
            else:
                count_value = ""
            count_item = self.hardware_table.item(row_idx, count_col_in_table)
            if count_item:
                count_item.setText(count_value)
            else:
                self.hardware_table.setItem(row_idx, count_col_in_table, QTableWidgetItem(count_value))
        self.hardware_table.blockSignals(False)
    
    def update_hardware_table_counts(self):
        """Update the hardware table display with current counts."""
        self.hardware_table.blockSignals(True)
        
        # Find Count column index in headers
        count_col = None
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() in ("count", "qty", "quantity"):
                count_col = idx
                break
        
        if count_col is not None:
            for row_idx in range(self.hardware_table.rowCount()):
                if row_idx < len(self.hardware_all_rows):
                    row_data = self.hardware_all_rows[row_idx]
                    if len(row_data) > count_col:
                        count_value = row_data[count_col]
                        # Update table item (remember column 0 is checkbox, so add 1)
                        count_item = self.hardware_table.item(row_idx, count_col + 1)
                        if count_item:
                            count_item.setText(str(count_value))
        
        self.hardware_table.blockSignals(False)
    
    def recalculate_all_hardware_counts(self):
        """Full recalculation of hardware counts and update display."""
        self.calculate_hardware_counts()
    
    def on_hardware_table_changed(self, item=None):
        """Handle changes to hardware table - just mark as changed, don't rebuild data."""
        # Simply mark that changes were made - don't rebuild hardware_all_rows
        # The table IS the source of truth now, not hardware_all_rows
        self.changes_made = True
        
        # Trigger auto-save for the dialog
        if self.mark_changed_callback:
            self.mark_changed_callback()
        
        # Refresh dropdown in parts table since hardware parts may have changed
        self.refresh_parts_dropdown()

        if item is not None and self.hardware_part_col_idx is not None:
            part_col_in_table = self.hardware_part_col_idx + 1
            if item.column() == part_col_in_table:
                new_value = item.text().strip()
                if self.hardware_part_id_col_idx is not None:
                    part_id_col_in_table = self.hardware_part_id_col_idx + 1
                    part_id_item = self.hardware_table.item(item.row(), part_id_col_in_table)
                    if part_id_item is None:
                        part_id_item = QTableWidgetItem("")
                        part_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                        part_id_item.setBackground(QColor(60, 60, 60))
                        part_id_item.setForeground(QColor(200, 200, 200))
                        self.hardware_table.setItem(item.row(), part_id_col_in_table, part_id_item)
                    if not part_id_item.text().strip() and new_value:
                        part_id_item.setText(self._generate_part_id())
                    part_id = part_id_item.text().strip()
                    if part_id and new_value:
                        self._sync_group_parts_to_hardware()
                        if self.current_group:
                            self.load_group_parts()
                        self.recalculate_all_hardware_counts()

        # Keep calculated counts up to date when hardware parts change
        if item is not None:
            count_col_idx = None
            for idx, header in enumerate(self.hardware_all_headers):
                if header.strip().lower() in ("count", "qty", "quantity"):
                    count_col_idx = idx
                    break
            if count_col_idx is None or item.column() != count_col_idx + 1:
                self.recalculate_all_hardware_counts()

        # Refresh current group lookups (MFR/Finish/Category) after hardware edits
        self.refresh_current_group_metadata()

        quoted_col_idx = self._get_header_index(self.hardware_all_headers, "quoted")
        checkbox_cols = [0]
        if quoted_col_idx is not None:
            checkbox_cols.append(quoted_col_idx + 1)
        self.hardware_table.blockSignals(True)
        self._ensure_hardware_table_has_trailing_blank_row()
        self.hardware_table.blockSignals(False)
        self.apply_hardware_filter()

    def consolidate_hardware_parts(self):
        """Consolidate duplicate hardware rows by exact Part + Finish match."""
        part_col_idx = self._get_header_index(self.hardware_all_headers, "Hardware Part")
        finish_col_idx = self._get_header_index(self.hardware_all_headers, "FINISH")
        if finish_col_idx is None:
            finish_col_idx = self._get_header_index(self.hardware_all_headers, "Finish")

        if part_col_idx is None or finish_col_idx is None:
            QMessageBox.warning(
                self,
                "Consolidate",
                "Could not find required columns 'Hardware Part' and 'FINISH'."
            )
            return

        part_col = part_col_idx + 1
        finish_col = finish_col_idx + 1
        part_id_col = self.hardware_part_id_col_idx + 1 if self.hardware_part_id_col_idx is not None else None

        def ensure_part_id(row_idx):
            if part_id_col is None:
                return ""
            item = self.hardware_table.item(row_idx, part_id_col)
            if item is None:
                item = QTableWidgetItem("")
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setBackground(QColor(60, 60, 60))
                item.setForeground(QColor(200, 200, 200))
                self.hardware_table.setItem(row_idx, part_id_col, item)
            if not item.text().strip():
                item.setText(self._generate_part_id())
            return item.text().strip()

        def row_summary(row_idx):
            bits = []
            for col_idx, header in enumerate(self.hardware_all_headers):
                if header.strip().lower() == "part id":
                    continue
                item = self.hardware_table.item(row_idx, col_idx + 1)
                if not item:
                    continue
                if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                    if item.checkState() == Qt.CheckState.Checked:
                        bits.append(f"{header}: Yes")
                    continue
                value = item.text().strip()
                if value:
                    bits.append(f"{header}: {value}")
            return " | ".join(bits) if bits else "Blank row"

        duplicates = {}
        for row_idx in range(self.hardware_table.rowCount()):
            part_item = self.hardware_table.item(row_idx, part_col)
            finish_item = self.hardware_table.item(row_idx, finish_col)
            part = part_item.text().strip() if part_item else ""
            finish = finish_item.text().strip() if finish_item else ""
            if not part:
                continue
            key = (part.lower(), finish.lower())
            duplicates.setdefault(key, []).append(row_idx)

        dup_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
        if not dup_groups:
            QMessageBox.information(self, "Consolidate", "No duplicates found for Part + Finish.")
            return

        replace_map = {}
        rows_to_remove = set()

        for (part_key, finish_key), rows in dup_groups.items():
            part_label = part_key.strip()
            finish_label = finish_key.strip() if finish_key else "(blank)"

            dlg = QDialog(self)
            dlg.setWindowTitle("Consolidate Hardware")
            layout = QVBoxLayout(dlg)
            layout.addWidget(QLabel(f"Duplicate rows found for Part '{part_label}' and Finish '{finish_label}'."))
            layout.addWidget(QLabel("Choose which row to keep (others will be removed), or keep both."))

            group = QButtonGroup(dlg)
            for idx, row_idx in enumerate(rows):
                summary = row_summary(row_idx)
                rb = QRadioButton(summary)
                if idx == 0:
                    rb.setChecked(True)
                group.addButton(rb, idx)
                layout.addWidget(rb)

            keep_both = QRadioButton("Keep both (no changes)")
            group.addButton(keep_both, len(rows))
            layout.addWidget(keep_both)

            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btn_box.accepted.connect(dlg.accept)
            btn_box.rejected.connect(dlg.reject)
            layout.addWidget(btn_box)

            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            selected_id = group.checkedId()
            if selected_id == len(rows):
                continue

            keep_row = rows[selected_id]
            keep_part_id = ensure_part_id(keep_row)

            for row_idx in rows:
                if row_idx == keep_row:
                    continue
                old_part_id = ensure_part_id(row_idx)
                if old_part_id:
                    replace_map[old_part_id] = keep_part_id
                rows_to_remove.add(row_idx)

        if not replace_map and not rows_to_remove:
            return

        if replace_map:
            for row in self.hardware_groups_rows:
                if self.hardware_groups_part_id_col_idx is None:
                    continue
                if len(row) <= self.hardware_groups_part_id_col_idx:
                    continue
                part_id = row[self.hardware_groups_part_id_col_idx].strip()
                if part_id in replace_map:
                    row[self.hardware_groups_part_id_col_idx] = replace_map[part_id]

        if rows_to_remove:
            self.hardware_table.blockSignals(True)
            for row_idx in sorted(rows_to_remove, reverse=True):
                self.hardware_table.removeRow(row_idx)
            quoted_col_idx = self._get_header_index(self.hardware_all_headers, "quoted")
            checkbox_cols = [0]
            if quoted_col_idx is not None:
                checkbox_cols.append(quoted_col_idx + 1)
            _ensure_single_trailing_blank_row(self.hardware_table, checkbox_cols)
            self.hardware_table.blockSignals(False)

        # Rebuild hardware_all_rows from table for consistency
        updated_rows = []
        for row_idx in range(self.hardware_table.rowCount()):
            row_data = []
            for col_idx in range(1, self.hardware_table.columnCount()):
                cell_item = self.hardware_table.item(row_idx, col_idx)
                if cell_item:
                    if cell_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                        row_data.append("Yes" if cell_item.checkState() == Qt.CheckState.Checked else "")
                    else:
                        row_data.append(cell_item.text())
                else:
                    row_data.append("")
            updated_rows.append(row_data)
            self.hardware_all_rows = updated_rows

        self._sync_group_parts_to_hardware(prune_missing=True)
        if self.current_group:
            self.load_group_parts()
        self.recalculate_all_hardware_counts()
        self.on_hardware_table_changed()
        QMessageBox.information(self, "Consolidate", "Consolidation complete.")

    def _install_hardware_paste_filter(self):
        if not self.hardware_table:
            return

        quoted_col_idx = self._get_header_index(self.hardware_all_headers, "quoted")
        checkbox_cols = [0]
        if quoted_col_idx is not None:
            checkbox_cols.append(quoted_col_idx + 1)

        skip_cols = []
        if self.hardware_part_id_col_idx is not None:
            skip_cols.append(self.hardware_part_id_col_idx + 1)

        readonly_cols = []
        if self.hardware_count_col_idx is not None:
            readonly_cols.append(self.hardware_count_col_idx + 1)

        def on_paste_callback():
            """Called after paste to ensure Part IDs and trigger save."""
            self._ensure_all_part_ids()
            self.on_hardware_table_changed()

        self._hardware_paste_filter = HardwarePasteEventFilter(
            self.hardware_table,
            checkbox_cols=checkbox_cols,
            skip_cols=skip_cols,
            readonly_cols=readonly_cols,
            change_callback=on_paste_callback,
            ensure_row_callback=self._ensure_hardware_table_has_trailing_blank_row
        )
        self.hardware_table.installEventFilter(self._hardware_paste_filter)
    
    def _ensure_all_part_ids(self):
        """Ensure all hardware rows with part names have Part IDs."""
        if self.hardware_part_id_col_idx is None or self.hardware_part_col_idx is None:
            return
        
        part_col = self.hardware_part_col_idx + 1  # +1 for checkbox column
        part_id_col = self.hardware_part_id_col_idx + 1  # +1 for checkbox column
        
        self.hardware_table.blockSignals(True)
        for row_idx in range(self.hardware_table.rowCount()):
            part_item = self.hardware_table.item(row_idx, part_col)
            part_name = part_item.text().strip() if part_item else ""
            
            if not part_name:
                continue
            
            # Check if Part ID exists
            part_id_item = self.hardware_table.item(row_idx, part_id_col)
            if part_id_item is None:
                part_id_item = QTableWidgetItem("")
                part_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                part_id_item.setBackground(QColor(60, 60, 60))
                part_id_item.setForeground(QColor(200, 200, 200))
                self.hardware_table.setItem(row_idx, part_id_col, part_id_item)
            
            # Generate Part ID if missing
            if not part_id_item.text().strip():
                part_id_item.setText(self._generate_part_id())
        
        self.hardware_table.blockSignals(False)

    def refresh_current_group_metadata(self):
        """Refresh lookup fields for the currently selected group."""
        if not self.current_group:
            return

        self.parts_table.blockSignals(True)
        for row_idx in range(self.parts_table.rowCount()):
            part_item = self.parts_table.item(row_idx, 1)
            part_name = part_item.text().strip() if part_item else ""
            part_id = part_item.data(Qt.ItemDataRole.UserRole) if part_item else ""

            if not part_id and part_name:
                part_id = self._get_part_id_for_name(part_name)
                if part_id and part_item:
                    part_item.setData(Qt.ItemDataRole.UserRole, part_id)

            if part_id:
                new_name = self._get_part_name_for_id(part_id)
                if new_name and part_item and new_name != part_name:
                    part_item.setText(new_name)

                hw_row = self._get_hardware_row_by_part_id(part_id)
                mfr = hw_row.get("mfr", "")
                finish = hw_row.get("finish", "")
                category = hw_row.get("category", "")
                prep_code = hw_row.get("prep code", "")
            else:
                mfr = ""
                finish = ""
                category = ""
                prep_code = ""

            for col_idx, value in ((2, mfr), (3, finish), (4, category), (5, prep_code)):
                cell_item = self.parts_table.item(row_idx, col_idx)
                if cell_item is None:
                    cell_item = QTableWidgetItem("")
                    cell_item.setFlags(cell_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.parts_table.setItem(row_idx, col_idx, cell_item)
                cell_item.setText(value)

        self.parts_table.blockSignals(False)
        self._refresh_prep_string_label()
    
    def recalculate_all_parts_in_current_group(self):
        """No longer used - cost and labor removed from Hardware Groups."""
        pass
    
    def add_selected_to_group(self):
        """Add selected hardware parts to the currently selected group."""
        if not self.current_group:
            QMessageBox.warning(self, "Add to Group", "Please select a hardware group first.")
            return
        
        # Resolve Hardware Part column directly from the visible table header.
        part_col_in_table = None
        for table_col in range(1, self.hardware_table.columnCount()):  # Skip Select checkbox column
            header_item = self.hardware_table.horizontalHeaderItem(table_col)
            header_text = header_item.text().strip().lower() if header_item and header_item.text() else ""
            if header_text in ("hardware part", "catalog number", "part number", "part"):
                part_col_in_table = table_col
                break

        if part_col_in_table is None:
            fallback_part_col_idx = self._get_hardware_part_col_idx()
            if fallback_part_col_idx is None:
                QMessageBox.warning(self, "Add to Group", "Could not find the Hardware Part column.")
                return
            part_col_in_table = 1 + fallback_part_col_idx

        if part_col_in_table <= 0 or part_col_in_table >= self.hardware_table.columnCount():
            QMessageBox.warning(self, "Add to Group", "Could not find the Hardware Part column.")
            return

        # Find selected parts from checkboxes first.
        selected_parts = []
        selected_part_names = set()

        def add_part_from_row(row_idx):
            if row_idx < 0 or row_idx >= self.hardware_table.rowCount():
                return
            part_item = self.hardware_table.item(row_idx, part_col_in_table)
            part_name = part_item.text().strip() if part_item else ""
            if part_name and part_name.lower() not in selected_part_names:
                selected_parts.append(part_name)
                selected_part_names.add(part_name.lower())

        selection_model = self.hardware_table.selectionModel()
        selected_index_rows = {index.row() for index in self.hardware_table.selectedIndexes()}
        if selection_model is not None:
            selected_index_rows.update(index.row() for index in selection_model.selectedRows())
        current_item = self.hardware_table.currentItem()
        current_row = current_item.row() if current_item else -1

        for row in range(self.hardware_table.rowCount()):
            checkbox_item = self.hardware_table.item(row, 0)
            is_checked = checkbox_item is not None and checkbox_item.checkState() == Qt.CheckState.Checked

            # Backup read path via model data in case item flags/state are not surfaced normally.
            if not is_checked:
                _model = self.hardware_table.model()
                assert _model is not None
                model_index = _model.index(row, 0)
                model_check_state = model_index.data(Qt.ItemDataRole.CheckStateRole) if model_index.isValid() else None
                is_checked = model_check_state == Qt.CheckState.Checked

            if is_checked:
                add_part_from_row(row)

        # Fallback: if no checkboxes are checked, use selected rows
        if not selected_parts:
            selected_rows = sorted(selected_index_rows)
            if not selected_rows and current_row >= 0:
                selected_rows = [current_row]
            for row in selected_rows:
                add_part_from_row(row)

        if not selected_parts:
            QMessageBox.information(
                self,
                "Add to Group",
                "No hardware parts selected. Check the Select box or highlight a row and try again."
            )
            return
        
        # Add each selected part to the parts table
        self.parts_table.blockSignals(True)
        
        for part_name in selected_parts:
            # Check if part already exists in group
            already_exists = False
            for row in range(self.parts_table.rowCount()):
                item = self.parts_table.item(row, 1)  # Column 1 is Hardware Part
                if item and item.text().strip().lower() == part_name.lower():
                    already_exists = True
                    break
            
            if already_exists:
                continue
            
            # Add new row
            row_idx = self.parts_table.rowCount()
            self.parts_table.setRowCount(row_idx + 1)
            
            # Checkbox in first column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setText("")
            self.parts_table.setItem(row_idx, 0, checkbox_item)
            
            # Hardware Part (read-only)
            part_id = self._get_part_id_for_name(part_name)
            part_item = QTableWidgetItem(part_name)
            part_item.setFlags(part_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if part_id:
                part_item.setData(Qt.ItemDataRole.UserRole, part_id)
            self.parts_table.setItem(row_idx, 1, part_item)
            
            # Get MFR, Finish, Category from Hardware table by Part ID
            mfr = ""
            finish = ""
            category = ""
            prep_code = ""
            if part_id:
                hw_row = self._get_hardware_row_by_part_id(part_id)
                mfr = hw_row.get("mfr", "")
                finish = hw_row.get("finish", "")
                category = hw_row.get("category", "")
                prep_code = hw_row.get("prep code", "")
            
            # MFR (read-only)
            mfr_item = QTableWidgetItem(mfr)
            mfr_item.setFlags(mfr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.parts_table.setItem(row_idx, 2, mfr_item)
            
            # Finish (read-only)
            finish_item = QTableWidgetItem(finish)
            finish_item.setFlags(finish_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.parts_table.setItem(row_idx, 3, finish_item)
            
            # Category (read-only)
            category_item = QTableWidgetItem(category)
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.parts_table.setItem(row_idx, 4, category_item)
            
            # Prep Code (read-only — edit via hardware table)
            prep_code_item = QTableWidgetItem(prep_code)
            prep_code_item.setFlags(prep_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.parts_table.setItem(row_idx, 5, prep_code_item)
            
            # COUNT (default 1, editable)
            count_item = QTableWidgetItem("1")
            self.parts_table.setItem(row_idx, 6, count_item)
        
        self.parts_table.blockSignals(False)
        
        # Uncheck all selected items
        for row in range(self.hardware_table.rowCount()):
            checkbox_item = self.hardware_table.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)
        
        self.changes_made = True
        self.save_data()
        
        # Trigger auto-save
        if self.mark_changed_callback:
            self.mark_changed_callback()
        
        QMessageBox.information(self, "Add to Group", f"Added {len(selected_parts)} part(s) to {self.current_group}.")
    
    def remove_selected_from_group(self):
        """Remove selected parts from the current group."""
        if not self.current_group:
            QMessageBox.warning(self, "No Group Selected", "Please select a hardware group first.")
            return
        
        # Get rows with checked checkboxes
        rows_to_remove = []
        for row in range(self.parts_table.rowCount()):
            checkbox_item = self.parts_table.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                rows_to_remove.append(row)
        
        if not rows_to_remove:
            QMessageBox.information(self, "No Parts Selected", "Please select parts to remove by checking the checkboxes.")
            return
        
        # Remove rows in reverse order to avoid index issues
        self.parts_table.blockSignals(True)
        for row in sorted(rows_to_remove, reverse=True):
            self.parts_table.removeRow(row)
        self.parts_table.blockSignals(False)
        
        self.changes_made = True
        self.save_data()
        
        # Trigger auto-save
        if self.mark_changed_callback:
            self.mark_changed_callback()
        
        QMessageBox.information(self, "Remove from Group", f"Removed {len(rows_to_remove)} part(s) from {self.current_group}.")
    
    def create_new_hardware_group(self):
        """Create a new hardware group and add it to the group list."""
        # Prompt user for group name
        ok_pressed = False
        group_name = ""
        
        while True:
            group_name, ok_pressed = QInputDialog.getText(
                self,
                "Create New Hardware Group",
                "Enter the name for the new hardware group:",
                text=""
            )
            
            if not ok_pressed:
                return
            
            group_name = group_name.strip()
            
            # Validate input
            if not group_name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a group name.")
                continue
            
            # Check if group already exists
            group_exists = False
            for row in self.hardware_groups_rows:
                if len(row) > 0 and row[0].strip().lower() == group_name.lower():
                    group_exists = True
                    break
            
            if group_exists:
                QMessageBox.warning(
                    self,
                    "Group Already Exists",
                    f"A hardware group named '{group_name}' already exists."
                )
                continue
            
            # Group name is valid and unique
            break
        
        # Add the new group to hardware_groups_rows with an empty row
        # Ensure the headers exist
        self._normalize_hardware_groups_schema()
        
        # Create a new row with the group name and empty values for other columns
        new_row = [""] * len(self.hardware_groups_headers)
        new_row[0] = group_name  # Hardware Group column
        
        self.hardware_groups_rows.append(new_row)
        
        # Mark as changed and save
        self.changes_made = True
        self.save_data()
        
        # Trigger auto-save
        if self.mark_changed_callback:
            self.mark_changed_callback()
        
        # Reload the groups list
        self.load_hardware_groups()
        
        # Select the newly created group
        matches = self.group_list.findItems(group_name, Qt.MatchFlag.MatchExactly)
        if matches:
            self.group_list.setCurrentItem(matches[0])
        
        QMessageBox.information(
            self,
            "Group Created",
            f"New hardware group '{group_name}' has been created successfully."
        )
    
    def delete_current_group(self):
        """Delete the current hardware group after confirmation."""
        if not self.current_group:
            QMessageBox.warning(self, "No Group Selected", "Please select a hardware group to delete.")
            return
        
        # Check if the group is assigned to any openings in the Schedule
        hw_group_col = None
        for idx, header in enumerate(self.schedule_headers):
            if header.strip().lower() == "hardware group":
                hw_group_col = idx
                break
        
        if hw_group_col is not None:
            assigned_openings = []
            opening_num_col = None
            
            # Find opening number column for better error message
            for idx, header in enumerate(self.schedule_headers):
                if header.strip().lower() in ("opening #", "opening number"):
                    opening_num_col = idx
                    break
            
            # Check if this group is used in any schedule rows
            for row in self.schedule_rows:
                if len(row) > hw_group_col:
                    schedule_group = row[hw_group_col].strip()
                    if schedule_group.lower() == self.current_group.lower():
                        opening_num = ""
                        if opening_num_col is not None and len(row) > opening_num_col:
                            opening_num = row[opening_num_col].strip()
                        assigned_openings.append(opening_num if opening_num else "Unknown")
            
            if assigned_openings:
                opening_list = ", ".join(assigned_openings[:10])  # Show first 10
                if len(assigned_openings) > 10:
                    opening_list += f"... and {len(assigned_openings) - 10} more"
                
                QMessageBox.warning(
                    self,
                    "Cannot Delete Group",
                    f"Hardware group '{self.current_group}' is currently assigned to {len(assigned_openings)} opening(s) in the Schedule.\n\n"
                    f"Openings: {opening_list}\n\n"
                    f"Please remove this group from all openings before deleting it."
                )
                return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Hardware Group",
            f"Are you sure you want to delete group '{self.current_group}'?\n\n"
            f"This will remove all parts assigned to this group and cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        group_to_delete = self.current_group
        
        # Remove all rows from hardware_groups_rows that match this group
        self.hardware_groups_rows = [
            row for row in self.hardware_groups_rows 
            if len(row) > 0 and row[0].strip().lower() != group_to_delete.lower()
        ]
        
        # Clear current selection
        self.current_group = None
        self.parts_table.setRowCount(0)
        self.completed_checkbox.setChecked(False)
        
        # Mark as changed and save
        self.changes_made = True
        self.save_data()
        
        # Trigger auto-save
        if self.mark_changed_callback:
            self.mark_changed_callback()
        
        # Reload the groups list
        self.load_hardware_groups()
        
        # Recalculate hardware counts
        self.recalculate_all_hardware_counts()
        
        QMessageBox.information(self, "Delete Group", f"Hardware group '{group_to_delete}' has been deleted.")
    
    def _get_hardware_part_col_idx(self):
        """Get the index of the Part Number column in hardware_all_headers."""
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() in ("hardware part", "catalog number", "part number"):
                return idx
        return 1  # Default to Part Number column (second column)
    
    def get_hardware_part_list(self):
        """Get list of all hardware parts from Hardware data."""
        parts = []
        
        # Find Part Number column
        catalog_col = None
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() in ("hardware part", "catalog number", "part number"):
                catalog_col = idx
                break
        
        if catalog_col is None:
            return parts
        
        # Collect all hardware parts
        for row in self.hardware_all_rows:
            if len(row) > catalog_col:
                part = row[catalog_col].strip()
                if part:
                    parts.append(part)
        
        return sorted(parts)
    
    def load_hardware_groups(self):
        """Load all unique hardware groups from Schedule."""
        # Get all unique hardware groups from Schedule
        hardware_group_col = None
        for idx, header in enumerate(self.schedule_headers):
            if header.strip().lower() == "hardware group":
                hardware_group_col = idx
                break
        
        if hardware_group_col is None:
            return
        
        # Collect unique hardware groups
        groups = set()
        for row in self.schedule_rows:
            if len(row) > hardware_group_col:
                group = row[hardware_group_col].strip()
                # Filter out empty strings and checkbox values (TRUE/FALSE)
                if group and group.upper() not in ("TRUE", "FALSE"):
                    groups.add(group)
        
        # Also add any groups from hardware_groups_data that may have been removed from schedule
        for row in self.hardware_groups_rows:
            if len(row) > 0:
                group = row[0].strip()
                # Filter out checkbox values
                if group and group.upper() not in ("TRUE", "FALSE"):
                    groups.add(group)
        
        # Populate group list
        completed_map = self._get_group_completed_map()
        current_group = self.current_group
        self.group_list.blockSignals(True)
        self.group_list.clear()
        for group in sorted(groups):
            display = f"{group} ✓" if completed_map.get(group) else group
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, group)
            self.group_list.addItem(item)
        self.group_list.blockSignals(False)

        # Restore selection when possible, otherwise select first
        if current_group:
            matches = self.group_list.findItems(current_group, Qt.MatchFlag.MatchExactly)
            if matches:
                self.group_list.setCurrentItem(matches[0])
            elif self.group_list.count() > 0:
                self.group_list.setCurrentRow(0)
            else:
                self.on_group_changed("")
        elif self.group_list.count() > 0:
            self.group_list.setCurrentRow(0)
        else:
            self.on_group_changed("")
        
        # Refresh dropdown
        self.refresh_parts_dropdown()
    
    def on_group_changed(self, group_name):
        """Handle hardware group selection change."""
        # Save the previous group's data before switching
        self.save_data()
        
        self.current_group = group_name
        if self.completed_checkbox is not None:
            completed_map = self._get_group_completed_map()
            self.completed_checkbox.blockSignals(True)
            self.completed_checkbox.setChecked(bool(completed_map.get(group_name)))
            self.completed_checkbox.blockSignals(False)
        self.load_group_parts()
        self.load_assigned_openings()

    def on_group_selected(self, current, previous):
        """Handle selection changes from the group list."""
        if not current:
            group_name = ""
        else:
            group_name = current.data(Qt.ItemDataRole.UserRole) or current.text().strip()
        self.on_group_changed(group_name)

    def on_group_completed_changed(self, state):
        """Handle completed status changes for the current group."""
        if not self.current_group:
            return

        completed = self.completed_checkbox.isChecked() if self.completed_checkbox else False
        self._update_group_completed_display(self.current_group, completed)
        self.changes_made = True
        self.save_data()
    
    def load_group_parts(self):
        """Load hardware parts for the selected group."""
        self.parts_table.blockSignals(True)
        self.parts_table.setRowCount(0)
        
        if not self.current_group:
            self.parts_table.blockSignals(False)
            return
        
        group_idx = self._get_header_index(self.hardware_groups_headers, "Hardware Group")
        if group_idx is None:
            group_idx = 0
        part_id_idx = self._get_header_index(self.hardware_groups_headers, "Part ID")
        qty_indices = self._get_hardware_groups_qty_indices()

        # Load parts for this group from hardware_groups_data
        for row in self.hardware_groups_rows:
            row_group = row[group_idx].strip() if len(row) > group_idx else ""
            if row_group == self.current_group:
                part_id = row[part_id_idx].strip() if part_id_idx is not None and len(row) > part_id_idx else ""
                part_name = self._get_part_name_for_id(part_id) if part_id else ""
                count = self._read_hardware_group_row_qty(row, qty_indices)
                
                if part_name:  # Only add rows with part names
                    row_idx = self.parts_table.rowCount()
                    self.parts_table.setRowCount(row_idx + 1)
                    
                    # Checkbox in first column
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                    checkbox_item.setText("")
                    self.parts_table.setItem(row_idx, 0, checkbox_item)
                    
                    # Hardware Part (read-only)
                    part_item = QTableWidgetItem(part_name)
                    part_item.setFlags(part_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if part_id:
                        part_item.setData(Qt.ItemDataRole.UserRole, part_id)
                    self.parts_table.setItem(row_idx, 1, part_item)
                    
                    # Get MFR, Finish, Category, Prep Code from Hardware table by Part ID
                    mfr = ""
                    finish = ""
                    category = ""
                    prep_code = ""
                    if part_id:
                        hw_row = self._get_hardware_row_by_part_id(part_id)
                        mfr = hw_row.get("mfr", "")
                        finish = hw_row.get("finish", "")
                        category = hw_row.get("category", "")
                        prep_code = hw_row.get("prep code", "")
                    
                    # MFR (read-only)
                    mfr_item = QTableWidgetItem(mfr)
                    mfr_item.setFlags(mfr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.parts_table.setItem(row_idx, 2, mfr_item)
                    
                    # Finish (read-only)
                    finish_item = QTableWidgetItem(finish)
                    finish_item.setFlags(finish_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.parts_table.setItem(row_idx, 3, finish_item)
                    
                    # Category (read-only)
                    category_item = QTableWidgetItem(category)
                    category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.parts_table.setItem(row_idx, 4, category_item)
                    
                    # Prep Code (read-only — edit via hardware table)
                    prep_code_item = QTableWidgetItem(prep_code)
                    prep_code_item.setFlags(prep_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.parts_table.setItem(row_idx, 5, prep_code_item)
                    
                    # COUNT (editable)
                    count_item = QTableWidgetItem(count)
                    self.parts_table.setItem(row_idx, 6, count_item)
        
        self.parts_table.blockSignals(False)
        self._refresh_prep_string_label()

    def _get_group_completed_map(self):
        completed_idx = self._get_header_index(self.hardware_groups_headers, "Completed")
        if completed_idx is None:
            return {}

        completed_map = {}
        for row in self.hardware_groups_rows:
            if len(row) <= completed_idx:
                continue
            group = row[0].strip() if len(row) > 0 else ""
            if not group or group in completed_map:
                continue
            value = row[completed_idx].strip().lower()
            completed_map[group] = value in ("yes", "true", "1", "checked")
        return completed_map

    def _update_group_completed_display(self, group_name, completed):
        if not self.group_list:
            return
        matches = self.group_list.findItems(group_name, Qt.MatchFlag.MatchExactly)
        if not matches:
            matches = []
            for i in range(self.group_list.count()):
                item = self.group_list.item(i)
                if item is not None and item.data(Qt.ItemDataRole.UserRole) == group_name:
                    matches.append(item)
        for item in matches:
            display = f"{group_name} ✓" if completed else group_name
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, group_name)
    
    def on_part_changed(self, item):
        """Handle changes to parts table."""
        if not self.current_group or not item:
            return
        
        row = item.row()
        col = item.column()
        
        # Only COUNT column (5) can trigger recalculation, but we're not calculating cost/labor anymore
        # Just save the data
        
        # No automatic cleanup - users can delete rows via right-click context menu
        self.changes_made = True
        self.save_data()
        
        # Trigger auto-save
        if self.mark_changed_callback:
            self.mark_changed_callback()
    
    def recalculate_row(self, row):
        """Recalculate COST and LABOR for a row in parts table."""
        part_item = self.parts_table.item(row, 1)  # Column 1 is Hardware Part
        count_item = self.parts_table.item(row, 2)  # Column 2 is COUNT
        
        part_name = part_item.text().strip() if part_item else ""
        count_text = count_item.text().strip() if count_item else ""
        
        # If part is empty (deleted), zero out COST and LABOR
        if not part_name:
            self.parts_table.blockSignals(True)
            
            # Zero out COST
            cost_item = self.parts_table.item(row, 3)  # Column 3 is COST
            if cost_item:
                cost_item.setText("$0.00")
            else:
                cost_item = QTableWidgetItem("$0.00")
                cost_item.setFlags(cost_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                cost_item.setBackground(QColor(60, 60, 60))
                cost_item.setForeground(QColor(200, 200, 200))
                self.parts_table.setItem(row, 3, cost_item)
            
            # Zero out LABOR
            labor_item = self.parts_table.item(row, 4)  # Column 4 is LABOR
            if labor_item:
                labor_item.setText("$0.00")
            else:
                labor_item = QTableWidgetItem("$0.00")
                labor_item.setFlags(labor_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                labor_item.setBackground(QColor(60, 60, 60))
                labor_item.setForeground(QColor(200, 200, 200))
                self.parts_table.setItem(row, 4, labor_item)
            
            self.parts_table.blockSignals(False)
            return
        
        try:
            count = float(count_text) if count_text else 0
        except ValueError:
            count = 0
        
        # Find part in Hardware
        part_cost = 0.0
        part_labor = 0.0
        
        # Find column indices in Hardware
        catalog_col = None
        cost_col = None
        labor_col = None
        
        for idx, header in enumerate(self.hardware_all_headers):
            h_lower = header.strip().lower()
            if h_lower in ("hardware part", "catalog number", "part number"):
                catalog_col = idx
            elif h_lower == "material cost":
                cost_col = idx
            elif h_lower == "field labor":
                labor_col = idx
        
        if catalog_col is not None:
            for hw_row in self.hardware_all_rows:
                if len(hw_row) > catalog_col:
                    catalog_num = hw_row[catalog_col].strip()
                    if catalog_num.lower() == part_name.lower():
                        # Get cost
                        if cost_col is not None and len(hw_row) > cost_col:
                            try:
                                cost_str = hw_row[cost_col].strip().replace('$', '').replace(',', '')
                                part_cost = float(cost_str) if cost_str else 0.0
                            except ValueError:
                                part_cost = 0.0
                        
                        # Get labor
                        if labor_col is not None and len(hw_row) > labor_col:
                            try:
                                labor_str = hw_row[labor_col].strip().replace('$', '').replace(',', '')
                                part_labor = float(labor_str) if labor_str else 0.0
                            except ValueError:
                                part_labor = 0.0
                        break
        
        # Calculate totals
        total_cost = part_cost * count
        total_labor = part_labor * count
        
        # Update COST column (block signals to avoid triggering change events)
        self.parts_table.blockSignals(True)
        cost_item = self.parts_table.item(row, 3)  # Column 3 is COST
        if cost_item:
            cost_item.setText(f"${total_cost:.2f}")
        else:
            cost_item = QTableWidgetItem(f"${total_cost:.2f}")
            cost_item.setFlags(cost_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            cost_item.setBackground(QColor(60, 60, 60))
            cost_item.setForeground(QColor(200, 200, 200))
            self.parts_table.setItem(row, 3, cost_item)
        
        # Update LABOR column
        labor_item = self.parts_table.item(row, 4)  # Column 4 is LABOR
        if labor_item:
            labor_item.setText(f"${total_labor:.2f}")
        else:
            labor_item = QTableWidgetItem(f"${total_labor:.2f}")
            labor_item.setFlags(labor_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            labor_item.setBackground(QColor(60, 60, 60))
            labor_item.setForeground(QColor(200, 200, 200))
            self.parts_table.setItem(row, 4, labor_item)
        
        self.parts_table.blockSignals(False)
    
    def cleanup_blank_rows(self):
        """Removed - users can delete rows via right-click context menu."""
        pass
    
    def refresh_parts_dropdown(self):
        """Refresh the Hardware Part dropdown delegate."""
        hardware_parts = self.get_hardware_part_list()
        # Add empty option at the beginning to allow clearing/deleting a part
        dropdown_items = [""] + hardware_parts if hardware_parts else [""]
        parts_delegate = ComboBoxDelegate(dropdown_items, self.parts_table)
        self.parts_table.setItemDelegateForColumn(0, parts_delegate)
    
    def show_add_hardware_part_dialog(self):
        """Show dialog to add a new hardware part."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Hardware Part")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Part Name
        part_layout = QHBoxLayout()
        part_layout.addWidget(QLabel("Hardware Part:"))
        part_input = QLineEdit()
        part_input.setPlaceholderText("Enter part name/number")
        part_layout.addWidget(part_input)
        layout.addLayout(part_layout)
        
        # Material Cost
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("Material Cost:"))
        cost_input = QLineEdit()
        cost_input.setText("0.00")
        cost_input.setPlaceholderText("0.00")
        cost_layout.addWidget(cost_input)
        layout.addLayout(cost_layout)
        
        # Field Labor
        labor_layout = QHBoxLayout()
        labor_layout.addWidget(QLabel("Field Labor:"))
        labor_input = QLineEdit()
        labor_input.setText("0.00")
        labor_input.setPlaceholderText("0.00")
        labor_layout.addWidget(labor_input)
        layout.addLayout(labor_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        def on_add():
            part_name = part_input.text().strip()
            if not part_name:
                QMessageBox.warning(dialog, "Add Hardware Part", "Please enter a hardware part name.")
                return
            
            # Validate cost and labor
            try:
                cost = float(cost_input.text().strip() or "0")
                labor = float(labor_input.text().strip() or "0")
            except ValueError:
                QMessageBox.warning(dialog, "Add Hardware Part", "Material Cost and Field Labor must be numbers.")
                return
            
            # Add to Hardware table
            table = self.hardware_table
            
            # Find Hardware Part column
            hardware_part_col = self._get_hardware_part_col_idx()
            
            # Find Quoted column index
            quoted_col_idx = None
            for idx, header in enumerate(self.hardware_all_headers):
                if header.strip().lower() == "quoted":
                    quoted_col_idx = idx
                    break
            
            # Find a row where Hardware Part column is empty
            target_row = None
            for r in range(table.rowCount()):
                cell = table.item(r, hardware_part_col + 1)  # +1 for checkbox column
                if not cell or not cell.text().strip():
                    target_row = r
                    break
            
            # If no empty Hardware Part cell found, add a new row
            if target_row is None:
                target_row = table.rowCount()
                table.setRowCount(target_row + 1)
            
            # Block signals while updating
            table.blockSignals(True)
            
            # Set the cells (skip first column which is checkbox)
            new_row = ["", part_name, "", "", f"{cost:.2f}", f"{labor:.2f}", "", "", ""]
            for c, value in enumerate(new_row):
                if c >= len(self.hardware_all_headers):
                    break
                item = QTableWidgetItem(str(value) if value else "")
                if c == quoted_col_idx:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    item.setText("")
                elif self.hardware_part_id_col_idx is not None and c == self.hardware_part_id_col_idx:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setBackground(QColor(60, 60, 60))
                    item.setForeground(QColor(200, 200, 200))
                    if not item.text().strip():
                        item.setText(self._generate_part_id())
                else:
                    # Make sure non-checkbox cells are editable
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                table.setItem(target_row, c + 1, item)  # +1 for checkbox column
            
            # Set checkbox in first column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setText("")
            table.setItem(target_row, 0, checkbox_item)
            
            table.blockSignals(False)
            
            # Trigger sync manually
            self.on_hardware_table_changed(checkbox_item)
            
            self.changes_made = True
            
            QMessageBox.information(dialog, "Add Hardware Part", f"Added '{part_name}' to Hardware table.")
            dialog.accept()
        
        add_button.clicked.connect(on_add)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()

    def show_configure_part_wizard(self):
        """Launch the Hardware Configurator wizard and insert the result."""
        dlg = HardwareConfiguratorDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.result_data:
            return

        data = dlg.result_data
        table = self.hardware_table

        # Resolve column indices by name
        mfr_col = self._get_header_index(self.hardware_all_headers, "MFR")
        part_col = self._get_hardware_part_col_idx()
        finish_col = self._get_header_index(self.hardware_all_headers, "FINISH")
        if finish_col is None:
            finish_col = self._get_header_index(self.hardware_all_headers, "Finish")
        category_col = self._get_header_index(self.hardware_all_headers, "Category")
        quoted_col = self._get_header_index(self.hardware_all_headers, "Quoted")

        # Find a row where Hardware Part is empty, otherwise append
        target_row = None
        for r in range(table.rowCount()):
            cell = table.item(r, part_col + 1)  # +1 for checkbox column
            if not cell or not cell.text().strip():
                target_row = r
                break
        if target_row is None:
            target_row = table.rowCount()
            table.setRowCount(target_row + 1)

        table.blockSignals(True)

        # Build a row of empty strings, then fill the configured columns
        row_values = [""] * len(self.hardware_all_headers)
        if mfr_col is not None:
            row_values[mfr_col] = data["manufacturer"]
        if part_col is not None:
            row_values[part_col] = data["part_number"]
        if finish_col is not None:
            row_values[finish_col] = data["finish"]
        if category_col is not None:
            row_values[category_col] = data["category"]

        for c, value in enumerate(row_values):
            if c >= len(self.hardware_all_headers):
                break
            item = QTableWidgetItem(str(value) if value else "")
            if quoted_col is not None and c == quoted_col:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setText("")
            elif self.hardware_part_id_col_idx is not None and c == self.hardware_part_id_col_idx:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setBackground(QColor(60, 60, 60))
                item.setForeground(QColor(200, 200, 200))
                if not item.text().strip():
                    item.setText(self._generate_part_id())
            else:
                item.setFlags(
                    item.flags()
                    | Qt.ItemFlag.ItemIsEditable
                    | Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                )
            table.setItem(target_row, c + 1, item)  # +1 for checkbox column

        # Checkbox in column 0
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        checkbox_item.setCheckState(Qt.CheckState.Unchecked)
        checkbox_item.setText("")
        table.setItem(target_row, 0, checkbox_item)

        table.blockSignals(False)
        self.on_hardware_table_changed(checkbox_item)
        self.changes_made = True

        QMessageBox.information(
            self,
            "Configure Part",
            f"Added '{data['part_number']}' to Hardware table.",
        )

    def load_assigned_openings(self):
        """Load assigned openings for the selected hardware group."""
        self.openings_table.setRowCount(0)
        
        if not self.current_group:
            return
        
        # Find relevant columns in Schedule
        hardware_group_col = None
        opening_num_col = None
        door_type_col = None
        frame_type_col = None
        
        for idx, header in enumerate(self.schedule_headers):
            h_lower = header.strip().lower()
            if h_lower == "hardware group":
                hardware_group_col = idx
            elif h_lower == "opening number":
                opening_num_col = idx
            elif h_lower == "door type":
                door_type_col = idx
            elif h_lower == "frame type":
                frame_type_col = idx
        
        if hardware_group_col is None:
            return
        
        # Find all openings with this hardware group
        for row in self.schedule_rows:
            if len(row) > hardware_group_col and row[hardware_group_col].strip() == self.current_group:
                opening_num = row[opening_num_col].strip() if opening_num_col is not None and len(row) > opening_num_col else ""
                door_type = row[door_type_col].strip() if door_type_col is not None and len(row) > door_type_col else ""
                frame_type = row[frame_type_col].strip() if frame_type_col is not None and len(row) > frame_type_col else ""
                
                row_idx = self.openings_table.rowCount()
                self.openings_table.setRowCount(row_idx + 1)
                
                self.openings_table.setItem(row_idx, 0, QTableWidgetItem(opening_num))
                self.openings_table.setItem(row_idx, 1, QTableWidgetItem(door_type))
                self.openings_table.setItem(row_idx, 2, QTableWidgetItem(frame_type))
    
    def save_data(self):
        """Save the hardware groups data back to memory (will be saved to CSV by parent dialog)."""
        if not self.current_group:
            return

        group_idx = self._get_header_index(self.hardware_groups_headers, "Hardware Group")
        if group_idx is None:
            self.hardware_groups_headers.insert(0, "Hardware Group")
            for row in self.hardware_groups_rows:
                row.insert(0, "")
            group_idx = 0

        part_id_idx = self._get_header_index(self.hardware_groups_headers, "Part ID")
        if part_id_idx is None:
            self.hardware_groups_headers.append("Part ID")
            for row in self.hardware_groups_rows:
                row.append("")
            part_id_idx = len(self.hardware_groups_headers) - 1

        qty_idx = self._get_header_index(self.hardware_groups_headers, "Qty")
        if qty_idx is None:
            qty_idx = self._get_header_index(self.hardware_groups_headers, "Count")
        if qty_idx is None:
            qty_idx = self._get_header_index(self.hardware_groups_headers, "Quantity")
        if qty_idx is None:
            self.hardware_groups_headers.append("Qty")
            for row in self.hardware_groups_rows:
                row.append("")
            qty_idx = len(self.hardware_groups_headers) - 1
        qty_indices = self._get_hardware_groups_qty_indices()
        if not qty_indices:
            qty_indices = [qty_idx]

        completed_idx = self._get_header_index(self.hardware_groups_headers, "Completed")
        if completed_idx is None:
            self.hardware_groups_headers.append("Completed")
            for row in self.hardware_groups_rows:
                row.append("")
            completed_idx = len(self.hardware_groups_headers) - 1

        completed_value = "Yes" if self.completed_checkbox and self.completed_checkbox.isChecked() else ""
        
        # Remove existing rows for this group
        self.hardware_groups_rows = [
            row for row in self.hardware_groups_rows
            if len(row) <= group_idx or row[group_idx].strip() != self.current_group
        ]
        
        # Add current group's data - save ALL rows, don't filter by content
        if self.parts_table.rowCount() == 0:
            blank_row = [""] * len(self.hardware_groups_headers)
            blank_row[group_idx] = self.current_group
            blank_row[part_id_idx] = ""
            for q_idx in qty_indices:
                blank_row[q_idx] = ""
            blank_row[completed_idx] = completed_value
            self.hardware_groups_rows.append(blank_row)
        else:
            for row_idx in range(self.parts_table.rowCount()):
                # Skip column 0 (checkbox), read from columns 1-5
                part_item = self.parts_table.item(row_idx, 1)  # Column 1 is Hardware Part
                count_item = self.parts_table.item(row_idx, 6)  # Column 6 is COUNT
                
                part_name = part_item.text().strip() if part_item else ""
                count = count_item.text().strip() if count_item else ""
                part_id = ""
                if part_item:
                    part_id = part_item.data(Qt.ItemDataRole.UserRole) or ""
                if not part_id and part_name:
                    part_id = self._get_part_id_for_name(part_name)
                
                # Save all rows, including empty ones - the user added them intentionally
                new_row = [""] * len(self.hardware_groups_headers)
                new_row[group_idx] = self.current_group
                new_row[part_id_idx] = part_id
                for q_idx in qty_indices:
                    new_row[q_idx] = count
                new_row[completed_idx] = completed_value
                self.hardware_groups_rows.append(new_row)
        
        # Recalculate hardware counts after saving group data
        self.recalculate_all_hardware_counts()
    
    def get_updated_data(self):
        """Return the updated data for saving - read hardware table directly."""
        self.commit_pending_edits()

        # Save current group
        self.save_data()
        
        # Read hardware data directly from the table (table is now the source of truth)
        updated_hardware_rows = []
        for row in range(self.hardware_table.rowCount()):
            row_data = []
            
            # Skip first column (checkbox), start from column 1
            for col in range(1, self.hardware_table.columnCount()):
                cell_item = self.hardware_table.item(row, col)
                if cell_item:
                    # Handle checkboxes
                    if cell_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                        checked = cell_item.checkState() == Qt.CheckState.Checked
                        cell_value = "Yes" if checked else ""
                    else:
                        cell_value = cell_item.text()
                    row_data.append(cell_value)
                else:
                    row_data.append("")
            
            # Save all rows - don't filter by content
            # The table is the source of truth
            updated_hardware_rows.append(row_data)
        
        # Return both hardware and hardware groups data
        return {
            'hardware': (self.hardware_all_headers, updated_hardware_rows),
            'hardware_groups': (self.hardware_groups_headers, self.hardware_groups_rows)
        }

    def commit_pending_edits(self):
        """Force any in-progress table cell edits to commit before saving."""
        for table in (self.hardware_table, self.parts_table):
            if table is None:
                continue

            current_item = table.currentItem()
            if current_item is not None:
                try:
                    table.closePersistentEditor(current_item)
                except Exception:
                    pass

            model = table.model()
            if model is not None and hasattr(model, "submit"):
                try:
                    model.submit()
                except Exception:
                    pass

            table.clearFocus()

        QApplication.processEvents()

    def _build_hardware_groups_pdf_data(self) -> "dict[str, list[dict[str, str]]]":
        """Return group_name -> part rows with qty and hardware metadata."""
        groups_data: dict = {}
        group_col = self._get_header_index(self.hardware_groups_headers, "Hardware Group")
        if group_col is None:
            group_col = 0
        part_id_col = self._get_header_index(self.hardware_groups_headers, "Part ID")
        qty_indices = self._get_hardware_groups_qty_indices()
        for row in self.hardware_groups_rows:
            group_name = row[group_col].strip() if len(row) > group_col else ""
            if not group_name:
                continue
            part_id = row[part_id_col].strip() if part_id_col is not None and len(row) > part_id_col else ""
            part_name = self._get_part_name_for_id(part_id) if part_id else ""
            qty = self._read_hardware_group_row_qty(row, qty_indices)
            if not part_name:
                continue
            mfr = ""
            finish = ""
            category = ""
            if part_id:
                hw_row = self._get_hardware_row_by_part_id(part_id)
                mfr = hw_row.get("mfr", "")
                finish = hw_row.get("finish", "")
                category = hw_row.get("category", "")
            if group_name not in groups_data:
                groups_data[group_name] = []
            groups_data[group_name].append({
                "part_name": part_name,
                "qty": qty,
                "mfr": mfr,
                "finish": finish,
                "category": category,
            })
        return groups_data

    def export_hardware_groups_pdf(self, parent_widget=None) -> None:
        """Generate and save a Hardware Groups PDF in two-column layout."""
        if not HAS_REPORTLAB:
            QMessageBox.warning(
                parent_widget or self, "PDF Hardware Groups",
                "ReportLab is not installed. Run: pip install reportlab"
            )
            return

        # Persist any in-progress edits before reading data
        self.save_data()
        groups_data = self._build_hardware_groups_pdf_data()

        if not groups_data:
            QMessageBox.information(
                parent_widget or self, "PDF Hardware Groups",
                "No hardware groups data to export."
            )
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H%M")
        default_name = f"Hardware Groups - {timestamp}.pdf"
        save_path: Optional[Path] = None

        if self.workbook_path:
            bid_path = self.workbook_path.parent.parent
            proposals_dir = bid_path / "3.Proposals"
            if not proposals_dir.exists():
                try:
                    for child in bid_path.iterdir():
                        if child.is_dir() and child.name.lower().startswith("3.proposal"):
                            proposals_dir = child
                            break
                except Exception:
                    pass
            proposals_dir.mkdir(parents=True, exist_ok=True)
            save_path = proposals_dir / default_name

        if save_path is None:
            file_path_str, _ = QFileDialog.getSaveFileName(
                parent_widget or self, "Save Hardware Groups PDF",
                default_name, "PDF Files (*.pdf)"
            )
            if not file_path_str:
                return
            save_path = Path(file_path_str)

        if save_path.suffix.lower() != ".pdf":
            save_path = save_path.with_suffix(".pdf")

        if save_path.exists():
            stem, suffix = save_path.stem, save_path.suffix
            i = 2
            while True:
                candidate = save_path.with_name(f"{stem} ({i}){suffix}")
                if not candidate.exists():
                    save_path = candidate
                    break
                i += 1

        try:
            write_hardware_groups_pdf(str(save_path), groups_data)
            QMessageBox.information(
                parent_widget or self, "PDF Hardware Groups",
                f"PDF saved to:\n{save_path}"
            )
        except Exception as e:
            QMessageBox.warning(
                parent_widget or self, "PDF Hardware Groups",
                f"Failed to generate PDF:\n{e}"
            )


class AlternatesSelectionWidget(QWidget):
    """Widget for selecting alternates in the proposal with checkboxes."""
    
    def __init__(
        self,
        alternates_widget,
        parent=None,
        item_label_singular: str = "Alternate",
        item_label_plural: str = "Alternates",
    ):
        super().__init__(parent)
        self.alternates_widget = alternates_widget
        self.item_label_singular = item_label_singular
        self.item_label_plural = item_label_plural
        self.alt_checkboxes = {}  # {alt_num: QCheckBox}
        self.alt_labels = {}      # {alt_num: QLabel (description + total)}
        self.alt_openings_checkboxes = {}  # {alt_num: QCheckBox for opening numbers}
        self.last_known_alts = set()  # Track alternates to detect changes
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollable list of alternates
        self.scroll_area: QScrollArea = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        
        self.scroll_widget: QWidget = QWidget()
        self.scroll_layout: QVBoxLayout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Populate initial alternates
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh the UI to reflect current alternates from the widget."""
        # Clear existing checkboxes
        self.alt_checkboxes.clear()
        self.alt_labels.clear()
        self.alt_openings_checkboxes.clear()
        
        # Clear layout
        while self.scroll_layout.count():
            _layout_item = self.scroll_layout.takeAt(0)
            if _layout_item is not None:
                _w = _layout_item.widget()
                if _w is not None:
                    _w.deleteLater()
        
        # Populate alternates
        all_alts = set(self.alternates_widget.alternates_openings_data.keys()) | \
                   set(self.alternates_widget.alternates_costs_data.keys()) | \
                   set(self.alternates_widget.alternates_subcontractor_data.keys()) | \
                   set(self.alternates_widget.alternates_details_data.keys())
        
        # Update tracked alternates
        self.last_known_alts = all_alts.copy()
        
        def sort_key(value):
            txt = (value or "").strip()
            if txt.isdigit():
                return (0, int(txt), txt)
            return (1, 0, txt.lower())
        
        for alt_num in sorted(all_alts, key=sort_key):
            alt_row = QHBoxLayout()
            alt_row.setContentsMargins(0, 0, 0, 0)
            alt_row.setSpacing(8)
            
            # Main select checkbox
            checkbox = QCheckBox()
            checkbox.setMaximumWidth(30)
            self.alt_checkboxes[alt_num] = checkbox
            alt_row.addWidget(checkbox)
            
            # Get description and total sell
            details = self.alternates_widget.alternates_details_data.get(alt_num, {})
            description = details.get('description', '')
            label_text = f"{self.item_label_singular} {alt_num}"
            if description:
                label_text += f": {description}"
            
            label = QLabel(label_text)
            self.alt_labels[alt_num] = label
            alt_row.addWidget(label, 1)
            
            # Opening numbers checkbox (per-alternate)
            opening_checkbox = QCheckBox("Opening #")
            opening_checkbox.setMaximumWidth(80)
            self.alt_openings_checkboxes[alt_num] = opening_checkbox
            alt_row.addWidget(opening_checkbox)
            
            alt_widget = QWidget()
            alt_widget.setLayout(alt_row)
            self.scroll_layout.addWidget(alt_widget)
        
        self.scroll_layout.addStretch()
    
    def update_descriptions(self):
        """Update label text with current descriptions from alternates widget."""
        for alt_num, label in self.alt_labels.items():
            details = self.alternates_widget.alternates_details_data.get(alt_num, {})
            description = details.get('description', '')
            label_text = f"{self.item_label_singular} {alt_num}"
            if description:
                label_text += f": {description}"
            label.setText(label_text)
    
    def get_text(self) -> str:
        """Build text representation of selected alternates for proposal."""
        # Get current alternates
        all_alts = set(self.alternates_widget.alternates_openings_data.keys()) | \
                   set(self.alternates_widget.alternates_costs_data.keys()) | \
                   set(self.alternates_widget.alternates_subcontractor_data.keys()) | \
                   set(self.alternates_widget.alternates_details_data.keys())
        
        # Check if alternates have changed and refresh UI if needed
        if all_alts != self.last_known_alts:
            self.refresh_ui()
        else:
            # Even if alternates didn't change, descriptions might have - update them
            self.update_descriptions()
        
        lines = []
        total_selected = 0.0
        
        def sort_key(value):
            txt = (value or "").strip()
            if txt.isdigit():
                return (0, int(txt), txt)
            return (1, 0, txt.lower())
        
        for alt_num in sorted(all_alts, key=sort_key):
            if alt_num not in self.alt_checkboxes or not self.alt_checkboxes[alt_num].isChecked():
                continue
            
            # Get details
            details = self.alternates_widget.alternates_details_data.get(alt_num, {})
            description = details.get('description', '')
            
            # Calculate total sell for this alternate
            self.alternates_widget.current_alternate = alt_num
            self.alternates_widget.load_alternate_costs()
            self.alternates_widget.load_alternate_subcontractor()
            self.alternates_widget.load_alternate_details()
            self.alternates_widget._recalculate_current_alternate_sell()
            
            total_sell_text = self.alternates_widget.total_sell_value_label.text()
            
            # Extract numeric value from total_sell_text (e.g., "$1,234.56" -> 1234.56)
            try:
                total_value = float(total_sell_text.replace('$', '').replace(',', ''))
                total_selected += total_value
            except (ValueError, AttributeError):
                total_value = 0.0
            
            # Build line
            line = f"{self.item_label_singular} {alt_num}"
            if description:
                line += f": {description}"
            line += f" - {total_sell_text}"
            lines.append(line)
            
            # Add opening numbers if this alternate's opening checkbox is checked
            if alt_num in self.alt_openings_checkboxes and self.alt_openings_checkboxes[alt_num].isChecked():
                openings = self.alternates_widget.alternates_openings_data.get(alt_num, [])
                if openings:
                    opening_nums = [op[0] for op in openings if op[0].strip()]
                    if opening_nums:
                        lines.append(f"  Opening #: {', '.join(opening_nums)}")
        
        # Add total if there are selected alternates
        if lines:
            lines.append("")
            lines.append(f"Total {self.item_label_plural}: ${total_selected:,.2f}")
        
        return "\n".join(lines) if lines else ""


class ChangeOrdersSelectionWidget(AlternatesSelectionWidget):
    """Proposal selection widget for change orders."""

    def __init__(self, change_orders_widget, parent=None):
        super().__init__(
            change_orders_widget,
            parent=parent,
            item_label_singular="Change Order",
            item_label_plural="Change Orders",
        )


class AdminMiscSelectionWidget(QWidget):
    """Widget for selecting Admin/Misc Cost rows to include in proposal breakouts."""

    def __init__(
        self,
        workbook_path: Path,
        initial_text: str = "",
        parent=None,
        rows_provider: Optional[Callable[[], Optional[List[Tuple[str, str, float]]]]] = None,
    ):
        super().__init__(parent)
        self.workbook_path = workbook_path
        self.rows_provider = rows_provider
        self.item_checkboxes = {}  # {row_key: QCheckBox}
        self.row_meta = []  # [(row_key, description, sell_value)]
        self.last_known_rows = []
        self.setup_ui()
        self.refresh_ui(initial_text)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)

        self.info_label = QLabel("Select Admin/Misc Cost items to include in Breakouts:")
        main_layout.addWidget(self.info_label)

        self.scroll_area: QScrollArea = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(120)

        self.scroll_widget: QWidget = QWidget()
        self.scroll_layout: QVBoxLayout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)

        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

    def _admin_misc_csv_path(self) -> Optional[Path]:
        direct = self.workbook_path / "Admin_Misc_Cost.csv"
        if direct.exists():
            return direct

        try:
            for path in sorted(self.workbook_path.glob("*.csv")):
                if "admin_misc_cost" in path.stem.lower():
                    return path
        except Exception:
            return None
        return None

    def _parse_money(self, value: str) -> float:
        try:
            text = str(value or "").replace("$", "").replace(",", "").strip()
            return float(text) if text else 0.0
        except Exception:
            return 0.0

    def _load_admin_misc_rows(self) -> List[Tuple[str, str, float]]:
        if self.rows_provider is not None:
            try:
                provider_rows = self.rows_provider()
                if provider_rows is not None:
                    return provider_rows
            except Exception:
                pass

        csv_path = self._admin_misc_csv_path()
        if csv_path is None:
            return []

        try:
            with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception:
            return []

        if not rows:
            return []

        headers = [str(h).strip() for h in rows[0]]
        data_rows = rows[1:]

        desc_idx = -1
        sell_idx = -1
        total_cost_idx = -1
        for idx, header in enumerate(headers):
            normalized = header.lower()
            if normalized == "description":
                desc_idx = idx
            elif normalized == "sell":
                sell_idx = idx
            elif normalized == "total cost":
                total_cost_idx = idx

        value_idx = sell_idx if sell_idx >= 0 else total_cost_idx
        if desc_idx < 0:
            return []

        loaded = []
        for row_idx, row in enumerate(data_rows):
            if not row:
                continue
            description = str(row[desc_idx]).strip() if desc_idx < len(row) else ""
            if not description:
                continue

            value_text = str(row[value_idx]).strip() if value_idx >= 0 and value_idx < len(row) else ""
            value_num = self._parse_money(value_text)
            row_key = f"{row_idx}:{description}"
            loaded.append((row_key, description, value_num))

        return loaded

    def _selected_descriptions_from_text(self, text: str) -> set[str]:
        selected = set()
        for line in str(text or "").splitlines():
            content = line.strip()
            if not content:
                continue
            if content.lower().startswith("total selected admin/misc"):
                continue
            if " - " in content:
                selected.add(content.split(" - ", 1)[0].strip())
            else:
                selected.add(content)
        return selected

    def refresh_ui(self, initial_text: str = ""):
        previously_checked = set()
        for row_key, checkbox in self.item_checkboxes.items():
            if checkbox.isChecked():
                previously_checked.add(row_key)

        initial_selected_descriptions = self._selected_descriptions_from_text(initial_text)
        rows = self._load_admin_misc_rows()

        self.row_meta = rows
        self.last_known_rows = rows.copy()
        self.item_checkboxes.clear()

        while self.scroll_layout.count():
            _layout_item = self.scroll_layout.takeAt(0)
            if _layout_item is not None:
                _w = _layout_item.widget()
                if _w is not None:
                    _w.deleteLater()

        if not rows:
            empty_label = QLabel("No Admin/Misc Cost rows found.")
            self.scroll_layout.addWidget(empty_label)
            self.scroll_layout.addStretch()
            return

        for row_key, description, sell_value in rows:
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            checkbox = QCheckBox()
            checkbox.setMaximumWidth(30)
            should_check = (row_key in previously_checked) or (description in initial_selected_descriptions)
            checkbox.setChecked(should_check)
            self.item_checkboxes[row_key] = checkbox
            row_layout.addWidget(checkbox)

            value_text = f"${sell_value:,.2f}"
            label = QLabel(f"{description} - {value_text}")
            row_layout.addWidget(label, 1)

            row_widget = QWidget()
            row_widget.setLayout(row_layout)
            self.scroll_layout.addWidget(row_widget)

        self.scroll_layout.addStretch()

    def apply_saved_text(self, text: str):
        self.refresh_ui(text)

    def get_text(self) -> str:
        current_rows = self._load_admin_misc_rows()
        if current_rows != self.last_known_rows:
            self.refresh_ui()

        lines = []
        total_selected = 0.0

        for row_key, description, sell_value in self.row_meta:
            checkbox = self.item_checkboxes.get(row_key)
            if checkbox is None or not checkbox.isChecked():
                continue

            lines.append(f"{description} - ${sell_value:,.2f}")
            total_selected += sell_value

        if lines:
            lines.append("")
            lines.append(f"Total Selected Admin/Misc: ${total_selected:,.2f}")

        return "\n".join(lines) if lines else ""


class AlternatesWidget(QWidget):
    """Custom widget for managing alternates with openings and costs."""
    
    def __init__(
        self,
        workbook_path,
        schedule_data,
        parent=None,
        change_callback=None,
        storage_path=None,
        item_label_singular: str = "Alternate",
        item_label_plural: str = "Alternates",
        data_file_prefix: str = "Alternates",
        record_number_header: str = "Alternate Number",
        ohp_rate_override: Optional[float] = None,
    ):
        super().__init__(parent)
        self.workbook_path = workbook_path
        self.storage_path = storage_path if storage_path is not None else workbook_path
        self.schedule_headers, self.schedule_rows = schedule_data
        self.item_label_singular = item_label_singular
        self.item_label_plural = item_label_plural
        self.data_file_prefix = data_file_prefix
        self.record_number_header = record_number_header
        self.current_alternate = None
        self.changes_made = False
        self.change_callback = change_callback
        self.alternates_openings_data = {}  # {alternate_num: [(opening_num, door_type, frame_type, hw_group, add_or_deduct), ...]}
        self.alternates_costs_data = {}     # {alternate_num: [(desc, count, material_per_unit, hours_per_unit, add_or_deduct), ...]}
        self.alternates_subcontractor_data = {}  # {alternate_num: [(desc, cost, add_or_deduct), ...]}
        self.alternates_details_data = {}   # {alternate_num: {'description': '', 'delivery_count': '', 'ot_hours': '', 'sub_ohp': ''}}
        self.financials_table: QTableWidget | None = None
        self.financials_headers: list[str] = []
        self.financials_rate_col_idx: int | None = None
        self.ohp_rate_override: Optional[float] = ohp_rate_override
        self._updating_alternate_details = False
        self.description_edit: QLineEdit
        self.delivery_count_edit: QLineEdit
        self.ot_hours_edit: QLineEdit
        self.sub_ohp_edit: QLineEdit
        self.total_sell_value_label: QLabel
        self.sell_summary_labels: dict[str, QLabel] = {}
        self.include_parking_checkbox: QCheckBox
        self.include_supervision_checkbox: QCheckBox
        self.subcontractor_table: NoRowHeaderTable
        
        self.setup_ui()
        self.load_alternates_data()
    
    def setup_ui(self):
        """Setup the UI layout with alternates list, openings, and costs."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # LEFT PANEL: Alternates list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        alt_label = QLabel(self.item_label_plural)
        alt_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Button layout for alternates
        alt_button_layout = QHBoxLayout()
        add_alt_button = QPushButton("Add")
        add_alt_button.setMaximumWidth(70)
        add_alt_button.clicked.connect(self.add_new_alternate)
        
        del_alt_button = QPushButton("Delete")
        del_alt_button.setMaximumWidth(70)
        del_alt_button.clicked.connect(self.delete_current_alternate)
        
        alt_button_layout.addWidget(add_alt_button)
        alt_button_layout.addWidget(del_alt_button)
        alt_button_layout.addStretch()
        
        self.alternates_list = QListWidget()
        self.alternates_list.setMinimumWidth(150)
        self.alternates_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.alternates_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.alternates_list.itemSelectionChanged.connect(self.on_alternate_selected)
        
        left_layout.addWidget(alt_label)
        left_layout.addLayout(alt_button_layout)
        left_layout.addWidget(self.alternates_list)
        
        # MIDDLE PANEL: Openings for selected alternate
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        openings_label = QLabel("Openings")
        openings_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Button layout for openings
        openings_button_layout = QHBoxLayout()
        add_opening_button = QPushButton("Add Opening")
        add_opening_button.setMaximumWidth(120)
        add_opening_button.clicked.connect(self.add_new_opening)
        
        del_opening_button = QPushButton("Delete")
        del_opening_button.setMaximumWidth(70)
        del_opening_button.clicked.connect(self.delete_selected_opening)
        
        openings_button_layout.addWidget(add_opening_button)
        openings_button_layout.addWidget(del_opening_button)
        openings_button_layout.addStretch()
        
        self.openings_table = NoRowHeaderTable()
        self.openings_table.setColumnCount(5)
        self.openings_table.setHorizontalHeaderLabels(["Opening #", "Door Type", "Frame Type", "Hardware Group", "Add/Deduct"])
        _ot_header2 = self.openings_table.horizontalHeader()
        assert _ot_header2 is not None
        _ot_header2.setStretchLastSection(True)
        self.openings_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.openings_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.openings_table.itemChanged.connect(self.on_opening_changed)
        
        # Context menu for row deletion
        self.openings_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.openings_table.customContextMenuRequested.connect(self.show_opening_context_menu)
        
        middle_layout.addWidget(openings_label)
        middle_layout.addLayout(openings_button_layout)
        middle_layout.addWidget(self.openings_table)
        
        # RIGHT PANEL: Costs for selected alternate
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        details_group = QGroupBox(f"{self.item_label_singular} Details & Sell")
        details_layout = QGridLayout(details_group)
        details_layout.setContentsMargins(8, 8, 8, 8)
        details_layout.setHorizontalSpacing(8)
        details_layout.setVerticalSpacing(6)

        self.description_edit = QLineEdit()
        self.description_edit.textChanged.connect(self.on_alternate_detail_changed)
        details_layout.addWidget(QLabel("Description"), 0, 0)
        details_layout.addWidget(self.description_edit, 0, 1, 1, 3)

        self.delivery_count_edit = QLineEdit()
        self.delivery_count_edit.textChanged.connect(self.on_alternate_detail_changed)
        details_layout.addWidget(QLabel("Delivery Hours"), 1, 0)
        details_layout.addWidget(self.delivery_count_edit, 1, 1)

        self.ot_hours_edit = QLineEdit()
        self.ot_hours_edit.textChanged.connect(self.on_alternate_detail_changed)
        details_layout.addWidget(QLabel("OT Hours"), 2, 0)
        details_layout.addWidget(self.ot_hours_edit, 2, 1)

        self.sub_ohp_edit = QLineEdit()
        self.sub_ohp_edit.textChanged.connect(self.on_alternate_detail_changed)
        details_layout.addWidget(QLabel("Sub OH & P (%)"), 1, 2)
        details_layout.addWidget(self.sub_ohp_edit, 1, 3)

        self.include_parking_checkbox = QCheckBox("Include Parking")
        self.include_parking_checkbox.setChecked(True)
        self.include_parking_checkbox.toggled.connect(self.on_alternate_detail_changed)
        details_layout.addWidget(self.include_parking_checkbox, 2, 2)

        self.include_supervision_checkbox = QCheckBox("Include Supervision")
        self.include_supervision_checkbox.setChecked(True)
        self.include_supervision_checkbox.toggled.connect(self.on_alternate_detail_changed)
        details_layout.addWidget(self.include_supervision_checkbox, 2, 3)

        def add_summary_row(row_idx, label_text, key):
            label = QLabel(label_text)
            value_label = QLabel("$0.00")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            details_layout.addWidget(label, row_idx, 0, 1, 3)
            details_layout.addWidget(value_label, row_idx, 3)
            self.sell_summary_labels[key] = value_label

        add_summary_row(3, "Material Total", "material_total")
        add_summary_row(4, "Labor Total", "labor_total")
        add_summary_row(5, "Parking", "parking")
        add_summary_row(6, "Supervision", "supervision")
        add_summary_row(7, "Hard Cost Total", "hard_cost_total")
        add_summary_row(8, "OH & P", "ohp")
        add_summary_row(9, "Sub OH & P", "sub_ohp")

        total_sell_label = QLabel("Total Sell")
        total_sell_label.setStyleSheet("font-weight: bold;")
        self.total_sell_value_label = QLabel("$0.00")
        self.total_sell_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.total_sell_value_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        details_layout.addWidget(total_sell_label, 10, 0, 1, 3)
        details_layout.addWidget(self.total_sell_value_label, 10, 3)

        right_layout.addWidget(details_group)
        
        costs_label = QLabel("Additional Costs (Non-Opening Specific)")
        costs_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Button layout for costs
        costs_button_layout = QHBoxLayout()
        add_cost_button = QPushButton("Add Cost")
        add_cost_button.setMaximumWidth(100)
        add_cost_button.clicked.connect(self.add_new_cost)
        
        del_cost_button = QPushButton("Delete")
        del_cost_button.setMaximumWidth(70)
        del_cost_button.clicked.connect(self.delete_selected_cost)
        
        costs_button_layout.addWidget(add_cost_button)
        costs_button_layout.addWidget(del_cost_button)
        costs_button_layout.addStretch()
        
        self.costs_table = NoRowHeaderTable()
        self.costs_table.setColumnCount(5)
        self.costs_table.setHorizontalHeaderLabels(["Description", "Count", "Material per Unit", "Hours per Unit", "Add/Deduct"])
        _ct_header = self.costs_table.horizontalHeader()
        assert _ct_header is not None
        _ct_header.setStretchLastSection(False)
        _ct_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        _ct_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        _ct_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        _ct_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        _ct_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.costs_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.costs_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.costs_table.itemChanged.connect(self.on_cost_changed)
        
        # Context menu for cost row deletion
        self.costs_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.costs_table.customContextMenuRequested.connect(self.show_cost_context_menu)
        
        right_layout.addWidget(costs_label)
        right_layout.addLayout(costs_button_layout)
        right_layout.addWidget(self.costs_table)

        # SUBCONTRACTOR COSTS section
        subcontractor_label = QLabel("Subcontractor Costs")
        subcontractor_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        subcontractor_button_layout = QHBoxLayout()
        add_subcontractor_button = QPushButton("Add Subcontractor")
        add_subcontractor_button.setMaximumWidth(150)
        add_subcontractor_button.clicked.connect(self.add_new_subcontractor)

        del_subcontractor_button = QPushButton("Delete")
        del_subcontractor_button.setMaximumWidth(70)
        del_subcontractor_button.clicked.connect(self.delete_selected_subcontractor)

        subcontractor_button_layout.addWidget(add_subcontractor_button)
        subcontractor_button_layout.addWidget(del_subcontractor_button)
        subcontractor_button_layout.addStretch()

        self.subcontractor_table = NoRowHeaderTable()
        self.subcontractor_table.setColumnCount(3)
        self.subcontractor_table.setHorizontalHeaderLabels(["Description", "Cost", "Add/Deduct"])
        _st_header = self.subcontractor_table.horizontalHeader()
        assert _st_header is not None
        _st_header.setStretchLastSection(True)
        self.subcontractor_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.subcontractor_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.subcontractor_table.itemChanged.connect(self.on_subcontractor_changed)

        # Context menu for subcontractor row deletion
        self.subcontractor_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.subcontractor_table.customContextMenuRequested.connect(self.show_subcontractor_context_menu)

        right_layout.addWidget(subcontractor_label)
        right_layout.addLayout(subcontractor_button_layout)
        right_layout.addWidget(self.subcontractor_table)
        
        # Add all panels to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(middle_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)  # Alternates list narrow
        splitter.setStretchFactor(1, 1)  # Openings take more space
        splitter.setStretchFactor(2, 1)  # Costs take equal space
        
        main_layout.addWidget(splitter)
        self._set_detail_inputs_enabled(False)
    
    def apply_theme(self, theme_colors):
        """Apply theme colors to all tables in this widget."""
        c = theme_colors
        table_style = f"""
            QTableWidget {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                gridline-color: {c['gridline']};
            }}
            QTableWidget::item {{
                color: {c['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: {c['selection_bg']};
                color: {c['selection_text']};
            }}
        """
        self.openings_table.setStyleSheet(table_style)
        self.costs_table.setStyleSheet(table_style)

        if self.description_edit is not None:
            edit_style = (
                f"background-color: {c['input_bg']};"
                f"color: {c['text_primary']};"
                f"border: 1px solid {c['input_border']};"
                "padding: 4px;"
            )
            self.description_edit.setStyleSheet(edit_style)
            self.delivery_count_edit.setStyleSheet(edit_style)
            self.ot_hours_edit.setStyleSheet(edit_style)
            self.sub_ohp_edit.setStyleSheet(edit_style)

        if self.total_sell_value_label is not None:
            self.total_sell_value_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {c['text_primary']};")
        
        list_style = f"""
            QListWidget {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
            }}
            QListWidget::item:selected {{
                background-color: {c['selection_bg']};
                color: {c['selection_text']};
            }}
        """
        self.alternates_list.setStyleSheet(list_style)
    
    def load_alternates_data(self):
        """Load alternates data from CSV files."""
        alternates_openings_path = self._managed_csv_path()
        alternates_costs_path = self._managed_csv_path("_Costs")
        alternates_subcontractor_path = self._managed_csv_path("_Subcontractor")
        alternates_details_path = self._managed_csv_path("_Details")
        
        # Load openings data
        if alternates_openings_path.exists():
            try:
                with open(alternates_openings_path, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                
                if rows and len(rows) > 1:
                    for row in rows[1:]:  # Skip header
                        if len(row) >= 4:
                            alt_num = row[0].strip()
                            opening_num = row[1].strip()
                            door_type = row[2].strip()
                            frame_type = row[3].strip()
                            hw_group = row[4].strip() if len(row) > 4 else ""
                            add_deduct = self._normalize_add_deduct(row[5].strip() if len(row) > 5 else "")
                            
                            if alt_num:
                                if alt_num not in self.alternates_openings_data:
                                    self.alternates_openings_data[alt_num] = []
                                self.alternates_openings_data[alt_num].append((opening_num, door_type, frame_type, hw_group, add_deduct))
            except Exception:
                pass

        # Load additional costs data
        if alternates_costs_path.exists():
            try:
                with open(alternates_costs_path, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    rows = list(reader)

                if rows and len(rows) > 1:
                    for row in rows[1:]:
                        if len(row) >= 5:
                            alt_num = row[0].strip()
                            desc = row[1].strip()
                            count = row[2].strip()
                            material = row[3].strip()
                            hours = row[4].strip()
                            add_deduct = self._normalize_add_deduct(row[5].strip() if len(row) > 5 else "")
                            if alt_num and desc:
                                if alt_num not in self.alternates_costs_data:
                                    self.alternates_costs_data[alt_num] = []
                                self.alternates_costs_data[alt_num].append((desc, count, material, hours, add_deduct))
            except Exception:
                pass

        # Load subcontractor costs data
        if alternates_subcontractor_path.exists():
            try:
                with open(alternates_subcontractor_path, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    rows = list(reader)

                if rows and len(rows) > 1:
                    for row in rows[1:]:
                        if len(row) >= 3:
                            alt_num = row[0].strip()
                            desc = row[1].strip()
                            cost = row[2].strip()
                            add_deduct = self._normalize_add_deduct(row[3].strip() if len(row) > 3 else "")
                            if alt_num and desc:
                                if alt_num not in self.alternates_subcontractor_data:
                                    self.alternates_subcontractor_data[alt_num] = []
                                self.alternates_subcontractor_data[alt_num].append((desc, cost, add_deduct))
            except Exception:
                pass

        # Load per-alternate detail data
        if alternates_details_path.exists():
            try:
                with open(alternates_details_path, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        alt_num = (row.get(self.record_number_header) or row.get('Alternate Number') or '').strip()
                        if not alt_num:
                            continue
                        self.alternates_details_data[alt_num] = {
                            'description': (row.get('Description') or '').strip(),
                            'delivery_count': ((row.get('Delivery Hours') or row.get('Delivery Count')) or '').strip(),
                            'ot_hours': (row.get('OT Hours') or '').strip(),
                            'sub_ohp': (row.get('Sub OH & P') or '').strip(),
                            'include_parking': (row.get('Include Parking') or '1').strip(),
                            'include_supervision': (row.get('Include Supervision') or '1').strip(),
                        }
            except Exception:
                pass

        all_alts = set(self.alternates_openings_data.keys()) | set(self.alternates_costs_data.keys()) | set(self.alternates_subcontractor_data.keys()) | set(self.alternates_details_data.keys())
        for alt_num in all_alts:
            self.alternates_openings_data.setdefault(alt_num, [])
            self.alternates_costs_data.setdefault(alt_num, [])
            self.alternates_subcontractor_data.setdefault(alt_num, [])
            self.alternates_details_data.setdefault(
                alt_num,
                {
                    'description': '',
                    'delivery_count': '0',
                    'ot_hours': '0',
                    'sub_ohp': '0',
                    'include_parking': '1',
                    'include_supervision': '1',
                },
            )
        
        # Populate alternates list
        self.update_alternates_list()
    
    def update_alternates_list(self):
        """Update the alternates list widget."""
        previous_selection = None
        current_item = self.alternates_list.currentItem()
        if current_item:
            previous_selection = current_item.text()
        elif self.current_alternate:
            previous_selection = self.current_alternate

        self.alternates_list.blockSignals(True)
        self.alternates_list.clear()
        
        all_alts = set(self.alternates_openings_data.keys()) | set(self.alternates_costs_data.keys()) | set(self.alternates_subcontractor_data.keys()) | set(self.alternates_details_data.keys())
        def sort_key(value):
            txt = (value or "").strip()
            if txt.isdigit():
                return (0, int(txt), txt)
            return (1, 0, txt.lower())
        for alt_num in sorted(all_alts, key=sort_key):
            self.alternates_list.addItem(alt_num)
        
        self.alternates_list.blockSignals(False)

        # Keep list selection stable so external updates do not drop the current alternate context.
        if previous_selection:
            matches = self.alternates_list.findItems(previous_selection, Qt.MatchFlag.MatchExactly)
            if matches:
                self.alternates_list.setCurrentItem(matches[0])
    
    def on_alternate_selected(self):
        """Handle selection of an alternate."""
        current_item = self.alternates_list.currentItem()
        new_alternate = current_item.text() if current_item else None

        # Only save when actually switching alternates; this avoids overwriting
        # externally added openings when the same alternate is reselected.
        if self.current_alternate and new_alternate != self.current_alternate:
            self.save_current_alternate_data()

        if current_item:
            self.current_alternate = new_alternate
            self.load_alternate_openings()
            self.load_alternate_costs()
            self.load_alternate_subcontractor()
            self.load_alternate_details()
            self._set_detail_inputs_enabled(True)
            self._recalculate_current_alternate_sell()
        else:
            self.current_alternate = None
            self.openings_table.setRowCount(0)
            self.costs_table.setRowCount(0)
            self.subcontractor_table.setRowCount(0)
            self._set_detail_inputs_enabled(False)
    
    def load_alternate_openings(self):
        """Load openings for the current alternate."""
        self.openings_table.blockSignals(True)
        self.openings_table.setRowCount(0)
        
        if not self.current_alternate:
            self.openings_table.blockSignals(False)
            return
        
        openings = self.alternates_openings_data.get(self.current_alternate, [])
        for opening in openings:
            opening_num = str(opening[0]).strip() if len(opening) > 0 else ""
            door_type = str(opening[1]).strip() if len(opening) > 1 else ""
            frame_type = str(opening[2]).strip() if len(opening) > 2 else ""
            hw_group = str(opening[3]).strip() if len(opening) > 3 else ""
            add_deduct = self._normalize_add_deduct(str(opening[4]).strip() if len(opening) > 4 else "")
            row_idx = self.openings_table.rowCount()
            self.openings_table.setRowCount(row_idx + 1)
            
            self.openings_table.setItem(row_idx, 0, QTableWidgetItem(opening_num))
            self.openings_table.setItem(row_idx, 1, QTableWidgetItem(door_type))
            self.openings_table.setItem(row_idx, 2, QTableWidgetItem(frame_type))
            self.openings_table.setItem(row_idx, 3, QTableWidgetItem(hw_group))
            self._set_add_deduct_cell(self.openings_table, row_idx, 4, add_deduct)
        
        # Add empty row for new entries
        row_idx = self.openings_table.rowCount()
        self.openings_table.setRowCount(row_idx + 1)
        self._set_add_deduct_cell(self.openings_table, row_idx, 4, "Add")
        
        self.openings_table.blockSignals(False)
    
    def load_alternate_costs(self):
        """Load costs for the current alternate."""
        self.costs_table.blockSignals(True)
        self.costs_table.setRowCount(0)
        
        if not self.current_alternate:
            self.costs_table.blockSignals(False)
            return
        
        costs = self.alternates_costs_data.get(self.current_alternate, [])
        for cost_row in costs:
            desc = str(cost_row[0]).strip() if len(cost_row) > 0 else ""
            count = str(cost_row[1]).strip() if len(cost_row) > 1 else ""
            material = str(cost_row[2]).strip() if len(cost_row) > 2 else ""
            hours = str(cost_row[3]).strip() if len(cost_row) > 3 else ""
            add_deduct = self._normalize_add_deduct(str(cost_row[4]).strip() if len(cost_row) > 4 else "")
            row_idx = self.costs_table.rowCount()
            self.costs_table.setRowCount(row_idx + 1)
            
            self.costs_table.setItem(row_idx, 0, QTableWidgetItem(desc))
            self.costs_table.setItem(row_idx, 1, QTableWidgetItem(count))
            self.costs_table.setItem(row_idx, 2, QTableWidgetItem(material))
            self.costs_table.setItem(row_idx, 3, QTableWidgetItem(hours))
            self._set_add_deduct_cell(self.costs_table, row_idx, 4, add_deduct)
        
        # Add empty row for new entries
        row_idx = self.costs_table.rowCount()
        self.costs_table.setRowCount(row_idx + 1)
        self._set_add_deduct_cell(self.costs_table, row_idx, 4, "Add")
        
        self.costs_table.blockSignals(False)

    def load_alternate_subcontractor(self):
        """Load subcontractor costs for the current alternate."""
        self.subcontractor_table.blockSignals(True)
        self.subcontractor_table.setRowCount(0)
        
        if not self.current_alternate:
            self.subcontractor_table.blockSignals(False)
            return
        
        subcontractors = self.alternates_subcontractor_data.get(self.current_alternate, [])
        for subcontractor_row in subcontractors:
            desc = str(subcontractor_row[0]).strip() if len(subcontractor_row) > 0 else ""
            cost = str(subcontractor_row[1]).strip() if len(subcontractor_row) > 1 else ""
            add_deduct = self._normalize_add_deduct(str(subcontractor_row[2]).strip() if len(subcontractor_row) > 2 else "")
            row_idx = self.subcontractor_table.rowCount()
            self.subcontractor_table.setRowCount(row_idx + 1)
            
            self.subcontractor_table.setItem(row_idx, 0, QTableWidgetItem(desc))
            self.subcontractor_table.setItem(row_idx, 1, QTableWidgetItem(cost))
            self._set_add_deduct_cell(self.subcontractor_table, row_idx, 2, add_deduct)
        
        # Add empty row for new entries
        row_idx = self.subcontractor_table.rowCount()
        self.subcontractor_table.setRowCount(row_idx + 1)
        self._set_add_deduct_cell(self.subcontractor_table, row_idx, 2, "Add")
        
        self.subcontractor_table.blockSignals(False)

    def reload_from_disk(self):
        """Refresh alternates data from workbook CSV files without rebuilding the dialog."""
        current_alternate = self.current_alternate
        self.alternates_openings_data = {}
        self.alternates_costs_data = {}
        self.alternates_subcontractor_data = {}
        self.alternates_details_data = {}
        self.load_alternates_data()
        self.changes_made = False

        if current_alternate:
            matches = self.alternates_list.findItems(current_alternate, Qt.MatchFlag.MatchExactly)
            if matches:
                self.alternates_list.setCurrentItem(matches[0])
                return
        self.on_alternate_selected()
    
    def add_new_alternate(self):
        """Add a new alternate."""
        text, ok = QInputDialog.getText(
            self,
            f"Add {self.item_label_singular}",
            f"Enter {self.item_label_singular.lower()} number:",
        )
        if ok and text.strip():
            alt_num = text.strip()
            if alt_num not in self.alternates_openings_data:
                self.alternates_openings_data[alt_num] = []
            if alt_num not in self.alternates_costs_data:
                self.alternates_costs_data[alt_num] = []
            if alt_num not in self.alternates_subcontractor_data:
                self.alternates_subcontractor_data[alt_num] = []
            if alt_num not in self.alternates_details_data:
                self.alternates_details_data[alt_num] = {
                    'description': '',
                    'delivery_count': '0',
                    'ot_hours': '0',
                    'sub_ohp': '0',
                    'include_parking': '1',
                    'include_supervision': '1',
                }
            
            self.update_alternates_list()
            self.changes_made = True
            if self.change_callback:
                self.change_callback()
            
            # Select the newly added alternate
            for i in range(self.alternates_list.count()):
                _alt_item = self.alternates_list.item(i)
                if _alt_item is not None and _alt_item.text() == alt_num:
                    self.alternates_list.setCurrentRow(i)
                    break
    
    def delete_current_alternate(self):
        """Delete the current alternate."""
        if not self.current_alternate:
            return
        
        reply = QMessageBox.question(
            self,
            f"Delete {self.item_label_singular}",
            f"Delete {self.item_label_singular.lower()} {self.current_alternate}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.alternates_openings_data.pop(self.current_alternate, None)
            self.alternates_costs_data.pop(self.current_alternate, None)
            self.alternates_subcontractor_data.pop(self.current_alternate, None)
            self.alternates_details_data.pop(self.current_alternate, None)
            self.current_alternate = None
            self.update_alternates_list()
            self.openings_table.setRowCount(0)
            self.costs_table.setRowCount(0)
            self.subcontractor_table.setRowCount(0)
            self._set_detail_inputs_enabled(False)
            self.changes_made = True
            if self.change_callback:
                self.change_callback()
    
    def add_new_opening(self):
        """Add a new opening row."""
        if not self.current_alternate:
            QMessageBox.warning(
                self,
                f"No {self.item_label_singular}",
                f"Please select or create a {self.item_label_singular.lower()} first.",
            )
            return
        
        row_idx = self.openings_table.rowCount()
        self.openings_table.setRowCount(row_idx + 1)
        self._set_add_deduct_cell(self.openings_table, row_idx, 4, "Add")
        self.changes_made = True
        if self.change_callback:
            self.change_callback()
    
    def delete_selected_opening(self):
        """Delete selected opening row."""
        row = self.openings_table.currentRow()
        if row < 0:
            return
        
        self.openings_table.removeRow(row)
        self.changes_made = True
        if self.change_callback:
            self.change_callback()
        self.save_current_alternate_data()
    
    def add_new_cost(self):
        """Add a new cost row."""
        if not self.current_alternate:
            QMessageBox.warning(
                self,
                f"No {self.item_label_singular}",
                f"Please select or create a {self.item_label_singular.lower()} first.",
            )
            return
        
        row_idx = self.costs_table.rowCount()
        self.costs_table.setRowCount(row_idx + 1)
        self._set_add_deduct_cell(self.costs_table, row_idx, 4, "Add")
        self.changes_made = True
        if self.change_callback:
            self.change_callback()
    
    def delete_selected_cost(self):
        """Delete selected cost row."""
        row = self.costs_table.currentRow()
        if row < 0:
            return
        
        self.costs_table.removeRow(row)
        self.changes_made = True
        if self.change_callback:
            self.change_callback()
        self.save_current_alternate_data()

    def add_new_subcontractor(self):
        """Add a new subcontractor row."""
        if not self.current_alternate:
            QMessageBox.warning(
                self,
                f"No {self.item_label_singular}",
                f"Please select or create a {self.item_label_singular.lower()} first.",
            )
            return
        
        row_idx = self.subcontractor_table.rowCount()
        self.subcontractor_table.setRowCount(row_idx + 1)
        self._set_add_deduct_cell(self.subcontractor_table, row_idx, 2, "Add")
        self.changes_made = True
        if self.change_callback:
            self.change_callback()
    
    def delete_selected_subcontractor(self):
        """Delete selected subcontractor row."""
        row = self.subcontractor_table.currentRow()
        if row < 0:
            return
        
        self.subcontractor_table.removeRow(row)
        self.changes_made = True
        if self.change_callback:
            self.change_callback()
        self.save_current_alternate_data()
    
    def on_opening_changed(self, item):
        """Handle opening table item change."""
        self.changes_made = True
        self.save_current_alternate_data()
        QTimer.singleShot(0, self._recalculate_current_alternate_sell)
        if self.change_callback:
            self.change_callback()
    
    def on_cost_changed(self, item):
        """Handle cost table item change."""
        self.changes_made = True
        QTimer.singleShot(0, self._recalculate_current_alternate_sell)
        if self.change_callback:
            self.change_callback()

    def on_subcontractor_changed(self, item):
        """Handle subcontractor table item change."""
        self.changes_made = True
        QTimer.singleShot(0, self._recalculate_current_alternate_sell)
        if self.change_callback:
            self.change_callback()

    def on_alternate_detail_changed(self):
        """Handle alternate detail edits."""
        if self._updating_alternate_details:
            return
        self.changes_made = True
        self._recalculate_current_alternate_sell()
        if self.change_callback:
            self.change_callback()

    def _set_detail_inputs_enabled(self, enabled: bool):
        if self.description_edit is not None:
            self.description_edit.setEnabled(enabled)
            self.delivery_count_edit.setEnabled(enabled)
            self.ot_hours_edit.setEnabled(enabled)
            self.sub_ohp_edit.setEnabled(enabled)
            self.include_parking_checkbox.setEnabled(enabled)
            self.include_supervision_checkbox.setEnabled(enabled)
        if not enabled:
            if self.description_edit is not None:
                self._updating_alternate_details = True
                self.description_edit.setText("")
                self.delivery_count_edit.setText("")
                self.ot_hours_edit.setText("")
                self.sub_ohp_edit.setText("")
                self.include_parking_checkbox.setChecked(True)
                self.include_supervision_checkbox.setChecked(True)
                self._updating_alternate_details = False
            self._set_sell_summary_values({
                'material_total': 0.0,
                'labor_total': 0.0,
                'parking': 0.0,
                'supervision': 0.0,
                'hard_cost_total': 0.0,
                'ohp': 0.0,
                'sub_ohp': 0.0,
                'total_sell': 0.0,
            })

    def _parse_boolish(self, value: object, default: bool = True) -> bool:
        if value is None:
            return default
        text = str(value).strip().lower()
        if not text:
            return default
        if text in ("1", "true", "yes", "y", "on", "checked"):
            return True
        if text in ("0", "false", "no", "n", "off", "unchecked"):
            return False
        return default

    def _set_sell_summary_values(self, values: Dict[str, float]):
        for key, label in self.sell_summary_labels.items():
            value = values.get(key, 0.0)
            label.setText(f"${value:,.2f}")
        if self.total_sell_value_label is not None:
            self.total_sell_value_label.setText(f"${values.get('total_sell', 0.0):,.2f}")

    def _normalize_add_deduct(self, value: str) -> str:
        text = (value or "").strip().lower()
        if text.startswith("d"):
            return "Deduct"
        return "Add"

    def _set_add_deduct_cell(self, table: QTableWidget, row: int, column: int, value: str):
        combo = QComboBox(table)
        combo.addItems(["Add", "Deduct"])
        combo.blockSignals(True)
        combo.setCurrentText(self._normalize_add_deduct(value))
        combo.blockSignals(False)
        combo.currentTextChanged.connect(self.on_add_deduct_changed)
        # Style the combo box for better readability
        combo.setStyleSheet("""
            QComboBox {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
                padding: 2px;
                font-size: 8pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #cccccc;
                selection-background-color: #007acc;
                padding: 2px;
            }
        """)
        table.setCellWidget(row, column, combo)

    def _get_add_deduct_value(self, table: QTableWidget, row: int, column: int) -> str:
        widget = table.cellWidget(row, column)
        if isinstance(widget, QComboBox):
            return self._normalize_add_deduct(widget.currentText())
        item = table.item(row, column)
        return self._normalize_add_deduct(item.text() if item else "")

    def on_add_deduct_changed(self, _value: str):
        self.changes_made = True
        self.save_current_alternate_data()
        QTimer.singleShot(0, self._recalculate_current_alternate_sell)
        if self.change_callback:
            self.change_callback()

    def _parse_number(self, value: str) -> float:
        raw = (value or "").strip()
        is_percent = raw.endswith("%")
        cleaned = raw.replace("$", "").replace(",", "").replace("%", "")
        if not cleaned:
            return 0.0
        try:
            parsed = float(cleaned)
            return (parsed / 100.0) if is_percent else parsed
        except ValueError:
            return 0.0

    def _parse_optional_number(self, value: str) -> Optional[float]:
        cleaned = (value or "").strip().replace("$", "").replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _find_column_index(self, headers: List[str], aliases: List[str]) -> Optional[int]:
        alias_set = {a.strip().lower() for a in aliases}
        for idx, header in enumerate(headers):
            if str(header or "").strip().lower() in alias_set:
                return idx
        return None

    def _get_schedule_opening_lookup(self) -> Dict[str, Dict[str, object]]:
        lookup: Dict[str, Dict[str, object]] = {}
        headers = self.schedule_headers or []
        rows = self.schedule_rows or []

        opening_col = self._find_column_index(headers, ["opening #", "opening number"])
        if opening_col is None:
            return lookup

        door_type_col = self._find_column_index(headers, ["door type"])
        frame_type_col = self._find_column_index(headers, ["frame type"])
        hw_group_col = self._find_column_index(headers, ["hardware group"])
        count_col = self._find_column_index(headers, ["count", "qty", "quantity"])
        door_cost_col = self._find_column_index(headers, ["door cost"])
        frame_cost_col = self._find_column_index(headers, ["frame cost"])
        hw_cost_col = self._find_column_index(headers, ["hardware cost"])
        door_labor_col = self._find_column_index(headers, ["door labor"])
        frame_labor_col = self._find_column_index(headers, ["frame labor"])
        hw_labor_col = self._find_column_index(headers, ["hardware labor"])

        for row in rows:
            if len(row) <= opening_col:
                continue
            opening_num = str(row[opening_col] or "").strip()
            if not opening_num:
                continue

            def get_text(col_idx: Optional[int]) -> str:
                if col_idx is None or len(row) <= col_idx:
                    return ""
                return str(row[col_idx] or "").strip()

            count = self._parse_number(get_text(count_col)) if count_col is not None else 1.0
            if count <= 0:
                count = 1.0

            lookup[opening_num.lower()] = {
                "door_type": get_text(door_type_col),
                "frame_type": get_text(frame_type_col),
                "hw_group": get_text(hw_group_col),
                "count": count,
                "door_cost": self._parse_optional_number(get_text(door_cost_col)),
                "frame_cost": self._parse_optional_number(get_text(frame_cost_col)),
                "hw_cost": self._parse_optional_number(get_text(hw_cost_col)),
                "door_labor": self._parse_optional_number(get_text(door_labor_col)),
                "frame_labor": self._parse_optional_number(get_text(frame_labor_col)),
                "hw_labor": self._parse_optional_number(get_text(hw_labor_col)),
            }

        return lookup

    def _read_csv_rows(self, csv_path: Path) -> Tuple[List[str], List[List[str]]]:
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
            if not rows:
                return [], []
            headers = [str(h or "") for h in rows[0]]
            data_rows = [[str(cell or "") for cell in row] for row in rows[1:]]
            return headers, data_rows
        except Exception:
            return [], []

    def _build_type_unit_lookup(self, item_type: str) -> Dict[str, Tuple[float, float]]:
        lookup: Dict[str, Tuple[float, float]] = {}
        if not self.workbook_path.exists():
            return lookup

        for csv_path in self.workbook_path.glob("*.csv"):
            stem = csv_path.stem.strip().lower()
            if stem in ("schedule", "alternates", "alternates_costs", "alternates_subcontractor", "alternates_details"):
                continue
            if item_type == "door":
                if "door" not in stem:
                    continue
            elif item_type == "frame":
                if "frame" not in stem:
                    continue
            else:
                continue

            headers, rows = self._read_csv_rows(csv_path)
            if not headers:
                continue

            if item_type == "door":
                type_col = self._find_column_index(headers, ["door type"])
            else:
                type_col = self._find_column_index(headers, ["frame type"])

            unit_cost_col = self._find_column_index(headers, ["unit material cost", "material cost"])
            unit_labor_col = self._find_column_index(headers, ["unit labor", "field labor"])
            if type_col is None:
                continue

            for row in rows:
                if len(row) <= type_col:
                    continue
                type_name = row[type_col].strip()
                if not type_name:
                    continue
                key = type_name.lower()
                if key in lookup:
                    continue

                material = self._parse_number(row[unit_cost_col] if unit_cost_col is not None and len(row) > unit_cost_col else "")
                labor = self._parse_number(row[unit_labor_col] if unit_labor_col is not None and len(row) > unit_labor_col else "")
                lookup[key] = (material, labor)

        return lookup

    def _build_hardware_group_unit_lookup(self) -> Dict[str, Tuple[float, float]]:
        if not self.workbook_path.exists():
            return {}

        def normalize_stem(value: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", (value or "").lower())

        hardware_path: Optional[Path] = None
        groups_path: Optional[Path] = None

        for csv_path in self.workbook_path.glob("*.csv"):
            stem_norm = normalize_stem(csv_path.stem)
            if stem_norm == "hardware":
                hardware_path = csv_path
            elif stem_norm in ("hardwaregroups", "hardwaregroup"):
                groups_path = csv_path

        if not hardware_path or not groups_path:
            return {}

        hw_headers, hw_rows = self._read_csv_rows(hardware_path)
        grp_headers, grp_rows = self._read_csv_rows(groups_path)
        if not hw_headers or not grp_headers:
            return {}

        hw_part_id_col = self._find_column_index(hw_headers, ["part id"])
        hw_part_name_col = self._find_column_index(hw_headers, ["hardware part", "catalog number", "part number", "part"])
        hw_cost_col = self._find_column_index(hw_headers, ["unit material cost", "material cost"])
        hw_labor_col = self._find_column_index(hw_headers, ["unit labor", "field labor"])

        part_by_id: Dict[str, Tuple[float, float]] = {}
        part_by_name: Dict[str, Tuple[float, float]] = {}

        for row in hw_rows:
            part_id = row[hw_part_id_col].strip() if hw_part_id_col is not None and len(row) > hw_part_id_col else ""
            part_name = row[hw_part_name_col].strip() if hw_part_name_col is not None and len(row) > hw_part_name_col else ""
            material = self._parse_number(row[hw_cost_col] if hw_cost_col is not None and len(row) > hw_cost_col else "")
            labor = self._parse_number(row[hw_labor_col] if hw_labor_col is not None and len(row) > hw_labor_col else "")

            if part_id and part_id not in part_by_id:
                part_by_id[part_id] = (material, labor)
            if part_name:
                key = part_name.lower()
                if key not in part_by_name:
                    part_by_name[key] = (material, labor)

        grp_group_col = self._find_column_index(grp_headers, ["hardware group"])
        grp_part_id_col = self._find_column_index(grp_headers, ["part id"])
        grp_part_name_col = self._find_column_index(grp_headers, ["hardware part", "part"])
        grp_qty_col = self._find_column_index(grp_headers, ["qty", "count", "quantity"])

        if grp_group_col is None or grp_qty_col is None:
            return {}

        totals: Dict[str, Tuple[float, float]] = {}
        for row in grp_rows:
            if len(row) <= max(grp_group_col, grp_qty_col):
                continue

            group_name = row[grp_group_col].strip()
            if not group_name:
                continue

            qty = self._parse_number(row[grp_qty_col]) if len(row) > grp_qty_col else 0.0
            if qty <= 0:
                continue

            part_id = row[grp_part_id_col].strip() if grp_part_id_col is not None and len(row) > grp_part_id_col else ""
            part_name = row[grp_part_name_col].strip() if grp_part_name_col is not None and len(row) > grp_part_name_col else ""

            if part_id and part_id in part_by_id:
                unit_material, unit_labor = part_by_id.get(part_id, (0.0, 0.0))
            elif part_name:
                unit_material, unit_labor = part_by_name.get(part_name.lower(), (0.0, 0.0))
            else:
                unit_material, unit_labor = (0.0, 0.0)

            current_material, current_labor = totals.get(group_name.lower(), (0.0, 0.0))
            totals[group_name.lower()] = (
                current_material + (unit_material * qty),
                current_labor + (unit_labor * qty),
            )

        return totals

    def _get_current_alternate_opening_totals(self) -> Tuple[float, float]:
        if not self.current_alternate:
            return 0.0, 0.0

        openings = self.alternates_openings_data.get(self.current_alternate, [])
        if not openings:
            return 0.0, 0.0

        schedule_lookup = self._get_schedule_opening_lookup()
        door_lookup = self._build_type_unit_lookup("door")
        frame_lookup = self._build_type_unit_lookup("frame")
        hardware_lookup = self._build_hardware_group_unit_lookup()

        material_total = 0.0
        labor_total = 0.0

        for opening in openings:
            opening_num = str(opening[0]).strip() if len(opening) > 0 else ""
            raw_door_type = str(opening[1]).strip() if len(opening) > 1 else ""
            raw_frame_type = str(opening[2]).strip() if len(opening) > 2 else ""
            raw_hw_group = str(opening[3]).strip() if len(opening) > 3 else ""
            door_type = raw_door_type
            frame_type = raw_frame_type
            hw_group = raw_hw_group
            add_deduct = self._normalize_add_deduct(str(opening[4]).strip() if len(opening) > 4 else "")
            sign = -1.0 if add_deduct == "Deduct" else 1.0

            schedule_row = schedule_lookup.get(opening_num.lower()) if opening_num else None
            count_multiplier = 1.0
            if schedule_row:
                count_multiplier = float(str(schedule_row.get("count", 1.0)))
                if not door_type:
                    door_type = str(schedule_row.get("door_type", ""))
                if not frame_type:
                    frame_type = str(schedule_row.get("frame_type", ""))
                if not hw_group:
                    hw_group = str(schedule_row.get("hw_group", ""))

            opening_material = 0.0
            opening_labor = 0.0
            include_door = bool(raw_door_type)
            include_frame = bool(raw_frame_type)
            include_hw = bool(raw_hw_group)

            # If the alternate row doesn't specify components, treat it as a full-opening entry.
            if not (include_door or include_frame or include_hw):
                include_door = bool(door_type)
                include_frame = bool(frame_type)
                include_hw = bool(hw_group)

            def _add_component(include_component: bool,
                               schedule_cost: Optional[float],
                               schedule_labor: Optional[float],
                               lookup_name: str,
                               lookup_table: Dict[str, Tuple[float, float]]):
                nonlocal opening_material, opening_labor
                if not include_component:
                    return
                if schedule_cost is not None or schedule_labor is not None:
                    if schedule_cost is not None:
                        opening_material += float(str(schedule_cost))
                    if schedule_labor is not None:
                        opening_labor += float(str(schedule_labor))
                    return
                if not lookup_name:
                    return
                unit_material, unit_labor = lookup_table.get(lookup_name.lower(), (0.0, 0.0))
                opening_material += unit_material * count_multiplier
                opening_labor += unit_labor * count_multiplier

            _add_component(
                include_door,
                schedule_row.get("door_cost") if schedule_row else None,
                schedule_row.get("door_labor") if schedule_row else None,
                door_type,
                door_lookup,
            )
            _add_component(
                include_frame,
                schedule_row.get("frame_cost") if schedule_row else None,
                schedule_row.get("frame_labor") if schedule_row else None,
                frame_type,
                frame_lookup,
            )
            _add_component(
                include_hw,
                schedule_row.get("hw_cost") if schedule_row else None,
                schedule_row.get("hw_labor") if schedule_row else None,
                hw_group,
                hardware_lookup,
            )

            material_total += opening_material * sign
            labor_total += opening_labor * sign

        return material_total, labor_total

    def _get_financials_rate(self, label: str) -> float:
        target = (label or "").strip().lower()

        if self.financials_table is not None and self.financials_rate_col_idx is not None:
            for row in range(self.financials_table.rowCount()):
                desc_item = self.financials_table.item(row, 0)
                if not desc_item:
                    continue
                desc = desc_item.text().strip().lower().rstrip(':')
                if desc == target.rstrip(':'):
                    rate_item = self.financials_table.item(row, self.financials_rate_col_idx)
                    if rate_item:
                        return self._parse_number(rate_item.text())

        financials_csv = self.workbook_path / "Financials.csv"
        if financials_csv.exists():
            try:
                with open(financials_csv, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                if rows:
                    headers = rows[0]
                    rate_col = None
                    for idx, header in enumerate(headers):
                        if (header or "").strip().lower() == "rate":
                            rate_col = idx
                            break
                    if rate_col is not None:
                        for row in rows[1:]:
                            if not row:
                                continue
                            desc = (row[0] if len(row) > 0 else "").strip().lower().rstrip(':')
                            if desc == target.rstrip(':'):
                                return self._parse_number(row[rate_col] if len(row) > rate_col else "")
            except Exception:
                pass

        return 0.0

    def _get_current_alternate_totals(self) -> Tuple[float, float]:
        material_sub_total = 0.0
        labor_hours_total = 0.0
        for row in range(self.costs_table.rowCount()):
            desc_item = self.costs_table.item(row, 0)
            if not desc_item or not desc_item.text().strip():
                continue
            count_item = self.costs_table.item(row, 1)
            material_item = self.costs_table.item(row, 2)
            hours_item = self.costs_table.item(row, 3)

            count = self._parse_number(count_item.text() if count_item else "")
            material = self._parse_number(material_item.text() if material_item else "")
            hours = self._parse_number(hours_item.text() if hours_item else "")
            add_deduct = self._get_add_deduct_value(self.costs_table, row, 4)
            sign = -1.0 if add_deduct == "Deduct" else 1.0

            material_sub_total += material * count * sign
            labor_hours_total += hours * count * sign

        return material_sub_total, labor_hours_total

    def _get_subcontractor_total(self) -> float:
        """Sum all subcontractor costs."""
        subcontractor_total = 0.0
        for row in range(self.subcontractor_table.rowCount()):
            cost_item = self.subcontractor_table.item(row, 1)
            if not cost_item:
                continue
            cost = self._parse_number(cost_item.text())
            add_deduct = self._get_add_deduct_value(self.subcontractor_table, row, 2)
            sign = -1.0 if add_deduct == "Deduct" else 1.0
            subcontractor_total += cost * sign
        return subcontractor_total

    def _managed_csv_path(self, suffix: str = "") -> Path:
        return self.storage_path / f"{self.data_file_prefix}{suffix}.csv"

    def _recalculate_current_alternate_sell(self):
        if not self.current_alternate:
            return

        material_sub_total, labor_hours_total = self._get_current_alternate_totals()
        opening_material_total, opening_labor_total = self._get_current_alternate_opening_totals()
        material_sub_total += opening_material_total
        labor_hours_total += opening_labor_total
        subcontractor_total = self._get_subcontractor_total()

        misc_material_rate = self._get_financials_rate("misc. material")
        tax_rate = self._get_financials_rate("tax")
        labor_rate = self._get_financials_rate("labor")
        misc_labor_rate = self._get_financials_rate("misc. labor")
        ot_rate = self._get_financials_rate("ot rate")
        parking_rate = self._get_financials_rate("parking")
        supervision_rate = self._get_financials_rate("supervision")
        ohp_rate = self.ohp_rate_override if self.ohp_rate_override is not None else self._get_financials_rate("oh & p")

        delivery_hours = self._parse_number(self.delivery_count_edit.text() if self.delivery_count_edit else "")
        ot_hours = self._parse_number(self.ot_hours_edit.text() if self.ot_hours_edit else "")
        sub_ohp_percentage = self._parse_number(self.sub_ohp_edit.text() if self.sub_ohp_edit else "")
        include_parking = self.include_parking_checkbox.isChecked() if self.include_parking_checkbox else True
        include_supervision = self.include_supervision_checkbox.isChecked() if self.include_supervision_checkbox else True

        misc_material = material_sub_total * misc_material_rate
        tax = (material_sub_total + misc_material) * tax_rate
        material_total = material_sub_total + misc_material + tax

        labor = labor_hours_total * labor_rate
        delivery_labor = delivery_hours * labor_rate
        labor += delivery_labor
        labor += (ot_hours * ot_rate)
        misc_labor = labor * misc_labor_rate
        labor_total = labor + misc_labor

        parking = 0.0
        if include_parking and labor_rate > 0:
            parking = (labor_total / labor_rate / 8.0) * parking_rate
        supervision = labor_total * supervision_rate if include_supervision else 0.0

        hard_cost_total = material_total + labor_total + parking + supervision
        ohp = 0.0
        if ohp_rate < 1:
            ohp = (hard_cost_total / (1 - ohp_rate)) - hard_cost_total

        # Subcontractor costs get marked up by Sub OH & P percentage
        sub_ohp_markup = subcontractor_total * (sub_ohp_percentage / 100.0)
        subcontractor_with_ohp = subcontractor_total + sub_ohp_markup

        total_sell = hard_cost_total + ohp + subcontractor_with_ohp

        self._set_sell_summary_values({
            'material_total': material_total,
            'labor_total': labor_total,
            'parking': parking,
            'supervision': supervision,
            'hard_cost_total': hard_cost_total,
            'ohp': ohp,
            'sub_ohp': sub_ohp_markup,
            'total_sell': total_sell,
        })

    def load_alternate_details(self):
        """Load details for the current alternate."""
        if not self.current_alternate or self.description_edit is None:
            return

        details = self.alternates_details_data.get(
            self.current_alternate,
            {
                'description': '',
                'delivery_count': '0',
                'ot_hours': '0',
                'sub_ohp': '0',
                'include_parking': '1',
                'include_supervision': '1',
            },
        )
        self._updating_alternate_details = True
        self.description_edit.setText(details.get('description', ''))
        self.delivery_count_edit.setText(details.get('delivery_count', '0'))
        self.ot_hours_edit.setText(details.get('ot_hours', '0'))
        self.sub_ohp_edit.setText(details.get('sub_ohp', '0'))
        self.include_parking_checkbox.setChecked(self._parse_boolish(details.get('include_parking', '1'), default=True))
        self.include_supervision_checkbox.setChecked(self._parse_boolish(details.get('include_supervision', '1'), default=True))
        self._updating_alternate_details = False

    def set_financials_source(self, financials_table: QTableWidget, financials_headers: List[str]):
        """Provide the Financials table so alternate sell calculations can mirror current rates."""
        self.financials_table = financials_table
        self.financials_headers = financials_headers or []
        self.financials_rate_col_idx = None
        for idx, header in enumerate(self.financials_headers):
            if (header or "").strip().lower() == "rate":
                self.financials_rate_col_idx = idx
                break
        self._recalculate_current_alternate_sell()

    def refresh_financial_inputs(self):
        """Refresh sell summary after financial rate updates."""
        self._recalculate_current_alternate_sell()
    
    def show_opening_context_menu(self, pos):
        """Show context menu for opening rows."""
        item = self.openings_table.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self.openings_table)
        delete_action = menu.addAction("Delete Row")
        
        action = menu.exec(self.openings_table.mapToGlobal(pos))
        if action == delete_action:
            self.delete_selected_opening()
    
    def show_cost_context_menu(self, pos):
        """Show context menu for cost rows."""
        item = self.costs_table.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self.costs_table)
        delete_action = menu.addAction("Delete Row")
        
        action = menu.exec(self.costs_table.mapToGlobal(pos))
        if action == delete_action:
            self.delete_selected_cost()

    def show_subcontractor_context_menu(self, pos):
        """Show context menu for subcontractor rows."""
        item = self.subcontractor_table.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self.subcontractor_table)
        delete_action = menu.addAction("Delete Row")
        
        action = menu.exec(self.subcontractor_table.mapToGlobal(pos))
        if action == delete_action:
            self.delete_selected_subcontractor()
    
    def save_current_alternate_data(self):
        """Save current alternate's openings and costs to data structures."""
        if not self.current_alternate:
            return
        
        # Save openings
        openings = []
        for row in range(self.openings_table.rowCount()):
            opening_num = self.openings_table.item(row, 0)
            door_type = self.openings_table.item(row, 1)
            frame_type = self.openings_table.item(row, 2)
            hw_group = self.openings_table.item(row, 3)
            add_deduct = self._get_add_deduct_value(self.openings_table, row, 4)
            
            opening_num_text = opening_num.text().strip() if opening_num else ""
            if opening_num_text:  # Only save non-empty rows
                openings.append((
                    opening_num_text,
                    door_type.text().strip() if door_type else "",
                    frame_type.text().strip() if frame_type else "",
                    hw_group.text().strip() if hw_group else "",
                    add_deduct,
                ))
        
        self.alternates_openings_data[self.current_alternate] = openings
        
        # Save costs
        costs = []
        for row in range(self.costs_table.rowCount()):
            desc = self.costs_table.item(row, 0)
            count = self.costs_table.item(row, 1)
            material = self.costs_table.item(row, 2)
            hours = self.costs_table.item(row, 3)
            add_deduct = self._get_add_deduct_value(self.costs_table, row, 4)
            
            desc_text = desc.text().strip() if desc else ""
            if desc_text:  # Only save non-empty rows
                costs.append((
                    desc_text,
                    count.text().strip() if count else "",
                    material.text().strip() if material else "",
                    hours.text().strip() if hours else "",
                    add_deduct,
                ))
        
        self.alternates_costs_data[self.current_alternate] = costs

        # Save subcontractor costs
        subcontractors = []
        for row in range(self.subcontractor_table.rowCount()):
            desc = self.subcontractor_table.item(row, 0)
            cost = self.subcontractor_table.item(row, 1)
            add_deduct = self._get_add_deduct_value(self.subcontractor_table, row, 2)
            
            desc_text = desc.text().strip() if desc else ""
            if desc_text:  # Only save non-empty rows
                subcontractors.append((
                    desc_text,
                    cost.text().strip() if cost else "",
                    add_deduct,
                ))
        
        self.alternates_subcontractor_data[self.current_alternate] = subcontractors

        # Save details
        description = self.description_edit.text().strip() if self.description_edit else ""
        delivery_count = self.delivery_count_edit.text().strip() if self.delivery_count_edit else "0"
        ot_hours = self.ot_hours_edit.text().strip() if self.ot_hours_edit else "0"
        sub_ohp = self.sub_ohp_edit.text().strip() if self.sub_ohp_edit else "0"
        include_parking = "1" if (self.include_parking_checkbox.isChecked() if self.include_parking_checkbox else True) else "0"
        include_supervision = "1" if (self.include_supervision_checkbox.isChecked() if self.include_supervision_checkbox else True) else "0"
        self.alternates_details_data[self.current_alternate] = {
            'description': description,
            'delivery_count': delivery_count,
            'ot_hours': ot_hours,
            'sub_ohp': sub_ohp,
            'include_parking': include_parking,
            'include_supervision': include_supervision,
        }
    
    def save_to_csv(self):
        """Save alternates data to CSV files."""
        if not self.changes_made:
            return
        
        alternates_openings_path = self._managed_csv_path()
        alternates_costs_path = self._managed_csv_path("_Costs")
        alternates_subcontractor_path = self._managed_csv_path("_Subcontractor")
        alternates_details_path = self._managed_csv_path("_Details")
        
        openings_rows = [[self.record_number_header, "Opening #", "Door Type", "Frame Type", "Hardware Group", "Add/Deduct"]]
        for alt_num in sorted(self.alternates_openings_data.keys()):
            for opening in self.alternates_openings_data[alt_num]:
                opening_num = str(opening[0]) if len(opening) > 0 else ""
                door_type = str(opening[1]) if len(opening) > 1 else ""
                frame_type = str(opening[2]) if len(opening) > 2 else ""
                hw_group = str(opening[3]) if len(opening) > 3 else ""
                add_deduct = self._normalize_add_deduct(str(opening[4]) if len(opening) > 4 else "")
                openings_rows.append([alt_num, opening_num, door_type, frame_type, hw_group, add_deduct])

        costs_rows = [[self.record_number_header, "Description", "Count", "Material per Unit", "Hours per Unit", "Add/Deduct"]]
        for alt_num in sorted(self.alternates_costs_data.keys()):
            for cost_row in self.alternates_costs_data[alt_num]:
                desc = str(cost_row[0]) if len(cost_row) > 0 else ""
                count = str(cost_row[1]) if len(cost_row) > 1 else ""
                material = str(cost_row[2]) if len(cost_row) > 2 else ""
                hours = str(cost_row[3]) if len(cost_row) > 3 else ""
                add_deduct = self._normalize_add_deduct(str(cost_row[4]) if len(cost_row) > 4 else "")
                costs_rows.append([alt_num, desc, count, material, hours, add_deduct])

        subcontractor_rows = [[self.record_number_header, "Description", "Cost", "Add/Deduct"]]
        for alt_num in sorted(self.alternates_subcontractor_data.keys()):
            for subcontractor_row in self.alternates_subcontractor_data[alt_num]:
                desc = str(subcontractor_row[0]) if len(subcontractor_row) > 0 else ""
                cost = str(subcontractor_row[1]) if len(subcontractor_row) > 1 else ""
                add_deduct = self._normalize_add_deduct(str(subcontractor_row[2]) if len(subcontractor_row) > 2 else "")
                subcontractor_rows.append([alt_num, desc, cost, add_deduct])

        details_rows = [[self.record_number_header, "Description", "Delivery Hours", "OT Hours", "Sub OH & P", "Include Parking", "Include Supervision"]]
        for alt_num in sorted(self.alternates_details_data.keys()):
            details = self.alternates_details_data.get(alt_num, {})
            details_rows.append([
                alt_num,
                details.get('description', ''),
                details.get('delivery_count', '0'),
                details.get('ot_hours', '0'),
                details.get('sub_ohp', '0'),
                details.get('include_parking', '1'),
                details.get('include_supervision', '1'),
            ])
        
        try:
            with open(alternates_openings_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(openings_rows)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save {alternates_openings_path.name}:\n{e}")

        try:
            with open(alternates_costs_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(costs_rows)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save {alternates_costs_path.name}:\n{e}")

        try:
            with open(alternates_subcontractor_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(subcontractor_rows)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save {alternates_subcontractor_path.name}:\n{e}")

        try:
            with open(alternates_details_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(details_rows)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save {alternates_details_path.name}:\n{e}")
        
        self.changes_made = False


class ChangeOrdersWidget(AlternatesWidget):
    """Custom widget for managing project change orders with the Alternates layout."""

    def __init__(self, workbook_path, schedule_data, parent=None, change_callback=None, storage_path=None, ohp_rate_override: Optional[float] = None):
        super().__init__(
            workbook_path,
            schedule_data,
            parent=parent,
            change_callback=change_callback,
            storage_path=storage_path,
            item_label_singular="Change Order",
            item_label_plural="Change Orders",
            data_file_prefix="Change_Orders",
            record_number_header="Change Order Number",
            ohp_rate_override=ohp_rate_override,
        )



