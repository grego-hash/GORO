"""HardwareGroupsWidget extracted from main_window.py."""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from .main_window_hw_groups import write_hardware_groups_pdf
from .main_window_ui_helpers import QFileDialog, QMessageBox
from core.optional_services import HAS_REPORTLAB
from widgets.table_helpers import ComboBoxDelegate, NoRowHeaderTable


def _row_has_text(row):
    return any(str(cell).strip() for cell in row)


def _trim_trailing_blank_rows(rows):
    trimmed = list(rows)
    while trimmed and not _row_has_text(trimmed[-1]):
        trimmed.pop()
    return trimmed


def load_dropdown_options(csv_path):
    """Load dropdown options from CSV file. Returns dict mapping column names to option lists."""
    options_dict = {}

    if not Path(csv_path).exists():
        return options_dict

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])

            for header in headers:
                if header.strip():
                    options_dict[header.strip()] = []

            for row in reader:
                for i, value in enumerate(row):
                    if i < len(headers) and headers[i].strip():
                        val = value.strip()
                        if val and val not in options_dict[headers[i].strip()]:
                            options_dict[headers[i].strip()].append(val)

    except Exception:
        pass

    return options_dict


def _get_dropdown_values_for_header(dropdown_options, header_name):
    """Return dropdown values for a header using case-insensitive matching."""
    header_key = str(header_name).strip()
    if not header_key:
        return []

    header_lower = header_key.lower()
    if header_lower in ("width", "height", "phase"):
        return []

    values = dropdown_options.get(header_key)
    if values:
        return values

    for option_header, option_values in dropdown_options.items():
        if str(option_header).strip().lower() == header_lower and option_values:
            return option_values

    return []


def _table_row_has_content(table, row_idx):
    for col_idx in range(table.columnCount()):
        item = table.item(row_idx, col_idx)
        if not item:
            continue
        if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            if item.checkState() == Qt.CheckState.Checked:
                return True
        if item.text().strip():
            return True

    return False


def _ensure_single_trailing_blank_row(table, checkbox_cols=None):
    last_content_row = -1
    for row_idx in range(table.rowCount()):
        if _table_row_has_content(table, row_idx):
            last_content_row = row_idx

    desired_rows = max(last_content_row + 2, 1)
    if table.rowCount() != desired_rows:
        table.setRowCount(desired_rows)

    if checkbox_cols:
        last_row = desired_rows - 1
        for col_idx in checkbox_cols:
            if col_idx < 0 or col_idx >= table.columnCount():
                continue
            item = table.item(last_row, col_idx)
            if item is None:
                item = QTableWidgetItem("")
                table.setItem(last_row, col_idx, item)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if item.checkState() != Qt.CheckState.Checked:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.setText("")


def _move_blank_rows_to_bottom(table):
    """Reorder table rows so completely blank rows always stay at the bottom."""
    row_count = table.rowCount()
    col_count = table.columnCount()
    if row_count <= 1 or col_count <= 0:
        return

    non_blank_rows = []
    blank_rows = []
    for row_idx in range(row_count):
        if _table_row_has_content(table, row_idx):
            non_blank_rows.append(row_idx)
        else:
            blank_rows.append(row_idx)

    if not blank_rows or blank_rows == list(range(row_count - len(blank_rows), row_count)):
        return

    row_items = []
    for row_idx in range(row_count):
        current_row = []
        for col_idx in range(col_count):
            current_row.append(table.takeItem(row_idx, col_idx))
        row_items.append(current_row)

    ordered_rows = non_blank_rows + blank_rows
    table.blockSignals(True)
    try:
        for new_row_idx, source_row_idx in enumerate(ordered_rows):
            for col_idx, item in enumerate(row_items[source_row_idx]):
                if item is not None:
                    table.setItem(new_row_idx, col_idx, item)
    finally:
        table.blockSignals(False)


class HardwareGroupsWidget(QWidget):
    """Custom widget for managing hardware groups with assigned openings."""
    
    def __init__(self, workbook_path, schedule_data, hardware_all_data, hardware_groups_data, hardware_csv_path, parent=None):
        super().__init__(parent)
        self.workbook_path = workbook_path
        self.hardware_csv_path = hardware_csv_path  # Actual path to Hardware.csv
        self.schedule_headers, self.schedule_rows = schedule_data
        self.hardware_all_headers, self.hardware_all_rows = hardware_all_data
        self.hardware_groups_headers, self.hardware_groups_rows = hardware_groups_data
        self.current_group = None
        self.changes_made = False
        self.hardware_table_widget = None  # Reference to Hardware table widget for live updates
        
        self.setup_ui()
        self.load_hardware_groups()
    
    def setup_ui(self):
        """Setup the UI layout."""
        main_layout = QHBoxLayout(self)
        
        # Left side: Hardware Group selection and parts table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Hardware Group selector
        group_selector_layout = QHBoxLayout()
        group_label = QLabel("Hardware Group:")
        self.group_combo = QComboBox()
        self.group_combo.setEditable(False)
        self.group_combo.setMinimumWidth(300)
        self.group_combo.currentTextChanged.connect(self.on_group_changed)
        
        # Completed checkbox
        self.completed_checkbox = QCheckBox("Completed")
        self.completed_checkbox.stateChanged.connect(self.on_completed_changed)
        
        group_selector_layout.addWidget(group_label)
        group_selector_layout.addWidget(self.group_combo)
        group_selector_layout.addStretch()
        group_selector_layout.addWidget(self.completed_checkbox)
        
        left_layout.addLayout(group_selector_layout)
        
        # Add Hardware Part button
        add_part_button = QPushButton("Add Hardware Part")
        add_part_button.clicked.connect(self.show_add_hardware_part_dialog)
        add_part_button.setMaximumWidth(150)
        left_layout.addWidget(add_part_button)

        pdf_groups_button = QPushButton("PDF Hardware Groups")
        pdf_groups_button.clicked.connect(lambda: self.export_hardware_groups_pdf())
        pdf_groups_button.setMaximumWidth(180)
        left_layout.addWidget(pdf_groups_button)
        
        # Hardware parts table
        self.parts_table = NoRowHeaderTable()
        self.parts_table.setColumnCount(4)
        self.parts_table.setHorizontalHeaderLabels(["Hardware Part", "COUNT", "COST", "LABOR"])
        _pt_header = self.parts_table.horizontalHeader()
        assert _pt_header is not None
        _pt_header.setStretchLastSection(False)
        _pt_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        _pt_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        _pt_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        _pt_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.parts_table.setColumnWidth(1, 80)
        self.parts_table.setColumnWidth(2, 100)
        self.parts_table.setColumnWidth(3, 100)
        
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
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #007acc;
                padding: 2px;
            }
        """)
        
        self.parts_table.itemChanged.connect(self.on_part_changed)
        
        # Add dropdown delegate for Hardware Part column
        hardware_parts = self.get_hardware_part_list()
        if hardware_parts:
            parts_delegate = ComboBoxDelegate(hardware_parts, self.parts_table)
            self.parts_table.setItemDelegateForColumn(0, parts_delegate)
        
        left_layout.addWidget(self.parts_table)
        
        # Right side: Assigned Openings
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
        
        # Add widgets to main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
    
    def apply_theme(self, theme_colors):
        """Apply theme colors to all tables in this widget."""
        c = theme_colors
        
        # Parts table style
        parts_style = f"""
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
        self.parts_table.setStyleSheet(parts_style)
        
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
    
    def get_hardware_part_list(self):
        """Get list of all hardware parts from Hardware_All data."""
        parts = []
        
        # Find Hardware Part column
        catalog_col = None
        for idx, header in enumerate(self.hardware_all_headers):
            if header.strip().lower() == "hardware part":
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
        
        # Populate combo box
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItem("")  # Empty option
        for group in sorted(groups):
            self.group_combo.addItem(group)
        self.group_combo.blockSignals(False)
        
        # Select first group if available
        if self.group_combo.count() > 1:
            self.group_combo.setCurrentIndex(1)

    def reload_from_disk(self, schedule_data, hardware_all_data, hardware_groups_data):
        """Refresh hardware groups data from workbook CSV files without rebuilding the dialog."""
        current_group = self.current_group
        self.schedule_headers, self.schedule_rows = schedule_data
        self.hardware_all_headers, self.hardware_all_rows = hardware_all_data
        self.hardware_groups_headers, self.hardware_groups_rows = hardware_groups_data
        self.load_hardware_groups()
        self.changes_made = False

        if current_group:
            idx = self.group_combo.findText(current_group)
            if idx >= 0:
                self.group_combo.setCurrentIndex(idx)
                return
        if self.group_combo.count() > 1:
            self.group_combo.setCurrentIndex(1)
    
    def on_group_changed(self, group_name):
        """Handle hardware group selection change."""
        # Save the previous group's data before switching
        self.save_data()
        
        self.current_group = group_name
        self.load_group_parts()
        self.load_assigned_openings()
        self.update_completed_status()
    
    def update_completed_status(self):
        """Update the completed checkbox based on saved data."""
        if not self.current_group:
            self.completed_checkbox.setChecked(False)
            return
        
        # Check if this group is marked as completed in the data
        for row in self.hardware_groups_rows:
            if len(row) > 0 and row[0].strip() == self.current_group:
                # Check completed column (last column)
                if len(row) > 5:
                    completed_text = row[5].strip().lower()
                    self.completed_checkbox.blockSignals(True)
                    self.completed_checkbox.setChecked(completed_text in ("yes", "x", "1", "true", "checked"))
                    self.completed_checkbox.blockSignals(False)
                return
        
        self.completed_checkbox.blockSignals(True)
        self.completed_checkbox.setChecked(False)
        self.completed_checkbox.blockSignals(False)
    
    def on_completed_changed(self, state):
        """Handle completed checkbox change."""
        self.changes_made = True
        self.save_data()
    
    def load_group_parts(self):
        """Load hardware parts for the selected group."""
        self.parts_table.blockSignals(True)
        self.parts_table.setRowCount(0)
        
        if not self.current_group:
            self.parts_table.blockSignals(False)
            return
        
        # Load parts for this group from hardware_groups_data
        for row in self.hardware_groups_rows:
            if len(row) > 1 and row[0].strip() == self.current_group:
                part_name = row[1].strip() if len(row) > 1 else ""
                count = row[2].strip() if len(row) > 2 else ""
                cost = row[3].strip() if len(row) > 3 else ""
                labor = row[4].strip() if len(row) > 4 else ""
                
                if part_name:  # Only add rows with part names
                    row_idx = self.parts_table.rowCount()
                    self.parts_table.setRowCount(row_idx + 1)
                    
                    # Hardware Part (editable with dropdown)
                    part_item = QTableWidgetItem(part_name)
                    self.parts_table.setItem(row_idx, 0, part_item)
                    
                    # COUNT (editable)
                    count_item = QTableWidgetItem(count)
                    self.parts_table.setItem(row_idx, 1, count_item)
                    
                    # COST (calculated, read-only)
                    cost_item = QTableWidgetItem(cost)
                    cost_item.setFlags(cost_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    cost_item.setBackground(QColor(60, 60, 60))
                    cost_item.setForeground(QColor(200, 200, 200))
                    self.parts_table.setItem(row_idx, 2, cost_item)
                    
                    # LABOR (calculated, read-only)
                    labor_item = QTableWidgetItem(labor)
                    labor_item.setFlags(labor_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    labor_item.setBackground(QColor(60, 60, 60))
                    labor_item.setForeground(QColor(200, 200, 200))
                    self.parts_table.setItem(row_idx, 3, labor_item)
        
        # Add one empty row for adding new parts
        row_idx = self.parts_table.rowCount()
        self.parts_table.setRowCount(row_idx + 1)
        
        self.parts_table.blockSignals(False)
    
    def on_part_changed(self, item):
        """Handle changes to parts table."""
        if not self.current_group or not item:
            return
        
        row = item.row()
        col = item.column()
        
        # If Hardware Part or COUNT changed, recalculate COST and LABOR
        if col in (0, 1):
            self.recalculate_row(row)
        
        # No automatic cleanup - users can delete rows via right-click context menu
        self.changes_made = True
        self.save_data()
    
    def recalculate_row(self, row):
        """Recalculate COST and LABOR for a row."""
        part_item = self.parts_table.item(row, 0)
        count_item = self.parts_table.item(row, 1)
        
        part_name = part_item.text().strip() if part_item else ""
        count_text = count_item.text().strip() if count_item else ""
        
        # If part is empty (deleted), zero out COST and LABOR
        if not part_name:
            self.parts_table.blockSignals(True)
            
            # Zero out COST
            cost_item = self.parts_table.item(row, 2)
            if cost_item:
                cost_item.setText("$0.00")
            else:
                cost_item = QTableWidgetItem("$0.00")
                cost_item.setFlags(cost_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                cost_item.setBackground(QColor(60, 60, 60))
                cost_item.setForeground(QColor(200, 200, 200))
                self.parts_table.setItem(row, 2, cost_item)
            
            # Zero out LABOR
            labor_item = self.parts_table.item(row, 3)
            if labor_item:
                labor_item.setText("0.00")
            else:
                labor_item = QTableWidgetItem("0.00")
                labor_item.setFlags(labor_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                labor_item.setBackground(QColor(60, 60, 60))
                labor_item.setForeground(QColor(200, 200, 200))
                self.parts_table.setItem(row, 3, labor_item)
            
            self.parts_table.blockSignals(False)
            return
        
        try:
            count = float(count_text) if count_text else 0
        except ValueError:
            count = 0
        
        # Find part in Hardware_All
        part_cost = 0.0
        part_labor = 0.0
        part_found = False
        
        # Find column indices in Hardware_All
        catalog_col = None
        cost_col = None
        labor_col = None
        
        for idx, header in enumerate(self.hardware_all_headers):
            h_lower = header.strip().lower()
            if h_lower == "hardware part":
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
                        part_found = True
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
        
        # Don't auto-add parts from dropdown selections - only through "Add Hardware Part" button
        # This prevents duplicate entries and unwanted additions
        # if not part_found and part_name:
        #     self.add_part_to_hardware_all(part_name)
        
        # Calculate totals
        total_cost = part_cost * count
        total_labor = part_labor * count
        
        # Update COST column (block signals to avoid triggering change events)
        self.parts_table.blockSignals(True)
        cost_item = self.parts_table.item(row, 2)
        if cost_item:
            cost_item.setText(f"${total_cost:.2f}")
        else:
            cost_item = QTableWidgetItem(f"${total_cost:.2f}")
            cost_item.setFlags(cost_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            cost_item.setBackground(QColor(60, 60, 60))
            cost_item.setForeground(QColor(200, 200, 200))
            self.parts_table.setItem(row, 2, cost_item)
        
        # Update LABOR column (with 2 decimal format)
        labor_item = self.parts_table.item(row, 3)
        if labor_item:
            labor_item.setText(f"{total_labor:.2f}")
        else:
            labor_item = QTableWidgetItem(f"{total_labor:.2f}")
            labor_item.setFlags(labor_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            labor_item.setBackground(QColor(60, 60, 60))
            labor_item.setForeground(QColor(200, 200, 200))
            self.parts_table.setItem(row, 3, labor_item)
        
        self.parts_table.blockSignals(False)
    
    def cleanup_blank_rows(self):
        """Removed - users can delete rows via right-click context menu."""
        pass
    
    def add_part_to_hardware_all(self, part_name):
        """Add a new hardware part to the Hardware table (only used by Add Hardware Part dialog)."""
        # This method is intentionally left empty - all logic moved to dialog
        # to prevent accidental duplicate adds from the groups tab
        pass
    
    def refresh_parts_dropdown(self):
        """Refresh the Hardware Part dropdown delegate."""
        hardware_parts = self.get_hardware_part_list()
        # Add empty option at the beginning to allow clearing/deleting a part
        dropdown_items = [""] + hardware_parts if hardware_parts else [""]
        parts_delegate = ComboBoxDelegate(dropdown_items, self.parts_table)
        self.parts_table.setItemDelegateForColumn(0, parts_delegate)
    
    def refresh_hardware_table(self):
        """Reload the Hardware table from CSV after adding a new part."""
        if not self.hardware_table_widget:
            return
        
        try:
            # Reload CSV data
            with open(self.hardware_csv_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if not rows:
                return
            
            headers = rows[0]
            data_rows = _trim_trailing_blank_rows(rows[1:])
            
            # Update table
            table = self.hardware_table_widget
            table.blockSignals(True)
            table.setRowCount(len(data_rows) + 1)  # +1 for empty row
            
            # Find Quoted column
            quoted_col_idx = None
            for idx, header in enumerate(headers):
                if header.strip().lower() == "quoted":
                    quoted_col_idx = idx
                    break
            
            for r, row in enumerate(data_rows):
                for c in range(len(headers)):
                    v = row[c] if c < len(row) else ""
                    item = QTableWidgetItem(str(v) if v else "")
                    
                    # Make Quoted column checkable
                    if c == quoted_col_idx:
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        text = str(v).strip().lower() if v else ""
                        if text in ("yes", "x", "1", "true", "checked"):
                            item.setCheckState(Qt.CheckState.Checked)
                        else:
                            item.setCheckState(Qt.CheckState.Unchecked)
                        item.setText("")
                    
                    table.setItem(r, c, item)
            
            # Initialize Quoted column for empty row
            if quoted_col_idx is not None:
                last_row = len(data_rows)
                item = QTableWidgetItem("")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                table.setItem(last_row, quoted_col_idx, item)
            
            table.blockSignals(False)
        except Exception as e:
            pass
    
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
            if self.hardware_table_widget:
                table = self.hardware_table_widget
                
                # Find Hardware Part column
                hardware_part_col = None
                cost_col = None
                labor_col = None
                quoted_col_idx = None
                
                for idx, header in enumerate(self.hardware_all_headers):
                    h = header.strip().lower()
                    if h == "hardware part":
                        hardware_part_col = idx
                    elif h == "material cost":
                        cost_col = idx
                    elif h == "field labor":
                        labor_col = idx
                    elif h == "quoted":
                        quoted_col_idx = idx
                
                # Find a row where Hardware Part column is empty
                target_row = None
                if hardware_part_col is not None:
                    for r in range(table.rowCount()):
                        cell = table.item(r, hardware_part_col)
                        if not cell or not cell.text().strip():
                            target_row = r
                            break
                
                # If no empty Hardware Part cell found, add a new row
                if target_row is None:
                    target_row = table.rowCount()
                    table.setRowCount(target_row + 1)
                
                # Block signals while updating to avoid multiple change events
                table.blockSignals(True)
                
                # Set the cells
                new_row = ["", part_name, "", "", f"{cost:.2f}", f"{labor:.2f}", "", "", ""]
                for c, value in enumerate(new_row):
                    if c >= table.columnCount():
                        break
                    item = QTableWidgetItem(str(value) if value else "")
                    if c == quoted_col_idx:
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        item.setText("")
                    table.setItem(target_row, c, item)
                
                table.blockSignals(False)
                
                # Sync data from table back to widget (same logic as on_hardware_table_changed)
                # Read headers
                headers = []
                for col in range(table.columnCount()):
                    header_item = table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"Column {col}")
                
                # Read data from table rows (include all rows with content)
                rows = []
                for row in range(table.rowCount()):
                    row_data = []
                    has_any_content = False
                    
                    for col in range(table.columnCount()):
                        cell_item = table.item(row, col)
                        if cell_item:
                            # Handle checkboxes
                            if cell_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                                checked = cell_item.checkState() == Qt.CheckState.Checked
                                cell_value = "Yes" if checked else ""
                                if checked:
                                    has_any_content = True
                            else:
                                cell_value = cell_item.text()
                                if cell_value.strip():
                                    has_any_content = True
                            row_data.append(cell_value)
                        else:
                            row_data.append("")
                    
                    if has_any_content:
                        rows.append(row_data)
                
                # Update widget data
                self.hardware_all_headers = headers
                self.hardware_all_rows = rows
                
                # Refresh dropdown with updated data
                self.refresh_parts_dropdown()
                
                QMessageBox.information(dialog, "Add Hardware Part", f"Added '{part_name}' to Hardware tab.")
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Add Hardware Part", "Hardware table not found.")
        
        add_button.clicked.connect(on_add)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
    
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
        
        # Remove existing rows for this group
        self.hardware_groups_rows = [row for row in self.hardware_groups_rows if len(row) == 0 or row[0].strip() != self.current_group]
        
        # Add current group's data - save ALL rows, don't filter by content
        completed_text = "Yes" if self.completed_checkbox.isChecked() else ""
        
        for row_idx in range(self.parts_table.rowCount()):
            part_item = self.parts_table.item(row_idx, 0)
            count_item = self.parts_table.item(row_idx, 1)
            cost_item = self.parts_table.item(row_idx, 2)
            labor_item = self.parts_table.item(row_idx, 3)
            
            part_name = part_item.text().strip() if part_item else ""
            count = count_item.text().strip() if count_item else ""
            cost = cost_item.text().strip() if cost_item else ""
            labor = labor_item.text().strip() if labor_item else ""
            
            # Save all rows, including empty ones - the user added them intentionally
            new_row = [self.current_group, part_name, count, cost, labor, completed_text]
            self.hardware_groups_rows.append(new_row)
    
    def get_updated_data(self):
        """Return the updated hardware groups data for saving."""
        # Make sure current group is saved
        self.save_data()
        return self.hardware_groups_headers, self.hardware_groups_rows

    def export_hardware_groups_pdf(self, parent_widget=None) -> None:
        """Generate and save a Hardware Groups PDF in two-column layout."""
        if not HAS_REPORTLAB:
            QMessageBox.warning(
                parent_widget or self, "PDF Hardware Groups",
                "ReportLab is not installed. Run: pip install reportlab"
            )
            return

        # Build groups_data from current rows
        # HardwareGroupsWidget stores: [group_name, part_name, count, cost, labor, completed]
        hw_headers_lower = [str(h).strip().lower() for h in self.hardware_all_headers]
        hw_part_col = hw_headers_lower.index("hardware part") if "hardware part" in hw_headers_lower else None
        hw_mfr_col = hw_headers_lower.index("mfr") if "mfr" in hw_headers_lower else None
        hw_finish_col = hw_headers_lower.index("finish") if "finish" in hw_headers_lower else None
        hw_category_col = hw_headers_lower.index("category") if "category" in hw_headers_lower else None

        part_meta_lookup: dict = {}
        if hw_part_col is not None:
            for hw_row in self.hardware_all_rows:
                if len(hw_row) <= hw_part_col:
                    continue
                part_name_key = hw_row[hw_part_col].strip().lower()
                if not part_name_key:
                    continue
                part_meta_lookup[part_name_key] = {
                    "mfr": hw_row[hw_mfr_col].strip() if hw_mfr_col is not None and len(hw_row) > hw_mfr_col else "",
                    "finish": hw_row[hw_finish_col].strip() if hw_finish_col is not None and len(hw_row) > hw_finish_col else "",
                    "category": hw_row[hw_category_col].strip() if hw_category_col is not None and len(hw_row) > hw_category_col else "",
                }

        groups_data: dict = {}
        for row in self.hardware_groups_rows:
            group_name = row[0].strip() if len(row) > 0 else ""
            if not group_name:
                continue
            part_name = row[1].strip() if len(row) > 1 else ""
            if not part_name:
                continue
            qty = row[2].strip() if len(row) > 2 else ""
            part_meta = part_meta_lookup.get(part_name.lower(), {})
            if group_name not in groups_data:
                groups_data[group_name] = []
            groups_data[group_name].append({
                "part_name": part_name,
                "qty": qty,
                "mfr": part_meta.get("mfr", ""),
                "finish": part_meta.get("finish", ""),
                "category": part_meta.get("category", ""),
            })

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


def load_dropdown_options(csv_path):
    """Load dropdown options from CSV file. Returns dict mapping column names to option lists."""
    options_dict = {}
    
    if not os.path.exists(csv_path):
        return options_dict
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            
            # Initialize empty lists for each column
            for header in headers:
                if header.strip():
                    options_dict[header.strip()] = []
            
            # Read all rows and collect values by column
            for row in reader:
                for i, value in enumerate(row):
                    if i < len(headers) and headers[i].strip():
                        val = value.strip()
                        if val and val not in options_dict[headers[i].strip()]:
                            options_dict[headers[i].strip()].append(val)
    
    except Exception:
        pass
    
    return options_dict


def _get_dropdown_values_for_header(dropdown_options, header_name):
    """Return dropdown values for a header using case-insensitive matching."""
    header_key = str(header_name).strip()
    if not header_key:
        return []

    # Blacklist: columns that should never get dropdowns
    header_lower = header_key.lower()
    if header_lower in ("width", "height", "phase"):
        return []

    values = dropdown_options.get(header_key)
    if values:
        return values

    for option_header, option_values in dropdown_options.items():
        if str(option_header).strip().lower() == header_lower and option_values:
            return option_values

    return []


def _row_has_text(row):
    return any(str(cell).strip() for cell in row)


def _trim_trailing_blank_rows(rows):
    trimmed = list(rows)
    while trimmed and not _row_has_text(trimmed[-1]):
        trimmed.pop()
    return trimmed


def _table_row_has_content(table, row_idx):
    for col_idx in range(table.columnCount()):
        item = table.item(row_idx, col_idx)
        if not item:
            continue
        if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            if item.checkState() == Qt.CheckState.Checked:
                return True
        if item.text().strip():
            return True

    return False


def _ensure_single_trailing_blank_row(table, checkbox_cols=None):
    last_content_row = -1
    for row_idx in range(table.rowCount()):
        if _table_row_has_content(table, row_idx):
            last_content_row = row_idx

    desired_rows = max(last_content_row + 2, 1)
    if table.rowCount() != desired_rows:
        table.setRowCount(desired_rows)

    if checkbox_cols:
        last_row = desired_rows - 1
        for col_idx in checkbox_cols:
            if col_idx < 0 or col_idx >= table.columnCount():
                continue
            item = table.item(last_row, col_idx)
            if item is None:
                item = QTableWidgetItem("")
                table.setItem(last_row, col_idx, item)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if item.checkState() != Qt.CheckState.Checked:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.setText("")


def _move_blank_rows_to_bottom(table):
    """Reorder table rows so completely blank rows always stay at the bottom."""
    row_count = table.rowCount()
    col_count = table.columnCount()
    if row_count <= 1 or col_count <= 0:
        return

    non_blank_rows = []
    blank_rows = []
    for row_idx in range(row_count):
        if _table_row_has_content(table, row_idx):
            non_blank_rows.append(row_idx)
        else:
            blank_rows.append(row_idx)

    if not blank_rows or blank_rows == list(range(row_count - len(blank_rows), row_count)):
        return

    row_items = []
    for row_idx in range(row_count):
        current_row = []
        for col_idx in range(col_count):
            current_row.append(table.takeItem(row_idx, col_idx))
        row_items.append(current_row)

    ordered_rows = non_blank_rows + blank_rows
    table.blockSignals(True)
    try:
        for new_row_idx, source_row_idx in enumerate(ordered_rows):
            for col_idx, item in enumerate(row_items[source_row_idx]):
                if item is not None:
                    table.setItem(new_row_idx, col_idx, item)
    finally:
        table.blockSignals(False)



