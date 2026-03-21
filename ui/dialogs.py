"""Dialog classes for GORO 1.0."""

import csv
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from PyQt6.QtCore import QDate, QSettings
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFileDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit,
    QColorDialog, QMessageBox, QSlider
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.constants import BID_STATUSES, ORG_NAME, APP_NAME, APP_VERSION
from core.update_utils import check_for_updates_manual


# ----------------------------
# Dialogs (Create / Due Date)
# ----------------------------

class CustomThemeDialog(QDialog):
    """Dialog for creating or editing a custom theme."""

    def __init__(self, parent=None, name: str = "", colors: Optional[dict] = None):
        super().__init__(parent)
        self.setWindowTitle("Custom Theme")
        self.setMinimumWidth(420)
        self._colors = colors or {}

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("e.g., Blue Steel")
        form.addRow("Theme Name:", self.name_edit)

        self.color_fields = {}
        color_keys = [
            ("window_bg", "Window Background"),
            ("panel_bg", "Panel Background"),
            ("text_primary", "Primary Text"),
            ("text_secondary", "Secondary Text"),
            ("accent", "Accent"),
            ("accent_hover", "Accent Hover"),
            ("button_text", "Button Text"),
            ("splitter", "Divider/Border"),
            ("splitter_hover", "Divider Hover"),
            ("hover_bg", "Hover Background"),
        ]

        for key, label in color_keys:
            row = QHBoxLayout()
            edit = QLineEdit(self._colors.get(key, ""))
            edit.setPlaceholderText("#RRGGBB")
            btn = QPushButton("Pick")
            btn.clicked.connect(lambda _=False, k=key, e=edit: self._pick_color(k, e))
            row.addWidget(edit)
            row.addWidget(btn)
            form.addRow(f"{label}:", row)
            self.color_fields[key] = edit

        # Add opacity slider
        opacity_row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(50)  # 50% minimum opacity
        self.opacity_slider.setMaximum(100)  # 100% fully opaque
        opacity_value = int(self._colors.get('opacity', 100))
        self.opacity_slider.setValue(opacity_value)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        self.opacity_label = QLabel(f"{opacity_value}%")
        self.opacity_label.setMinimumWidth(40)
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        opacity_row.addWidget(self.opacity_slider)
        opacity_row.addWidget(self.opacity_label)
        form.addRow("Window Opacity:", opacity_row)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def _pick_color(self, key: str, edit: QLineEdit):
        current = edit.text().strip() or self._colors.get(key, "")
        initial = QColor(current) if current else QColor("#ffffff")
        color = QColorDialog.getColor(initial, self, f"Select {key} color")
        if color.isValid():
            edit.setText(color.name())

    def get_theme_data(self) -> Tuple[str, dict]:
        name = self.name_edit.text().strip()
        colors = {k: v.text().strip() for k, v in self.color_fields.items() if v.text().strip()}
        # Add opacity value
        colors['opacity'] = self.opacity_slider.value()
        return name, colors


class LaborSettingsDialog(QDialog):
    """Dialog for editing default labor settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Labor Defaults")
        self.setMinimumWidth(420)
        self.settings = QSettings(ORG_NAME, APP_NAME)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        def _get_float_setting(key: str, default: float) -> float:
            try:
                return float(self.settings.value(key, default))
            except Exception:
                return default

        self.door_single_hours_edit = QLineEdit(str(_get_float_setting("labor_doors_single_hours", 1.0)))
        self.door_single_load_edit = QLineEdit(str(_get_float_setting("labor_doors_single_load", 0.25)))
        self.door_pair_hours_edit = QLineEdit(str(_get_float_setting("labor_doors_pair_hours", 2.0)))
        self.door_pair_load_edit = QLineEdit(str(_get_float_setting("labor_doors_pair_load", 0.5)))

        form.addRow("Doors - Single Field Hours:", self.door_single_hours_edit)
        form.addRow("Doors - Single Field Load & Dist:", self.door_single_load_edit)
        form.addRow("Doors - Pair Field Hours:", self.door_pair_hours_edit)
        form.addRow("Doors - Pair Field Load & Dist:", self.door_pair_load_edit)

        self.hm_kd_hours_edit = QLineEdit(str(_get_float_setting("labor_hm_kd_hours", 1.0)))
        self.hm_kd_load_edit = QLineEdit(str(_get_float_setting("labor_hm_kd_load", 0.25)))
        self.hm_welded_hours_edit = QLineEdit(str(_get_float_setting("labor_hm_welded_hours", 3.0)))
        self.hm_welded_load_edit = QLineEdit(str(_get_float_setting("labor_hm_welded_load", 1.0)))
        self.hm_sidelite_add_edit = QLineEdit(str(_get_float_setting("labor_hm_sidelite_per_foot", 0.5)))

        form.addRow("HM - Knock Down Field Hours:", self.hm_kd_hours_edit)
        form.addRow("HM - Knock Down Field Load & Dist:", self.hm_kd_load_edit)
        form.addRow("HM - Welded Field Hours:", self.hm_welded_hours_edit)
        form.addRow("HM - Welded Field Load & Dist:", self.hm_welded_load_edit)
        form.addRow("HM - Sidelite Hours per Foot:", self.hm_sidelite_add_edit)

        self.alum_width_threshold_edit = QLineEdit(str(_get_float_setting("labor_alum_width_threshold", 4.0)))
        self.alum_under_hours_edit = QLineEdit(str(_get_float_setting("labor_alum_under_hours", 1.5)))
        self.alum_over_hours_edit = QLineEdit(str(_get_float_setting("labor_alum_over_hours", 2.0)))
        self.alum_load_edit = QLineEdit(str(_get_float_setting("labor_alum_load", 0.125)))
        self.alum_sidelite_add_edit = QLineEdit(str(_get_float_setting("labor_alum_sidelite_per_foot", 0.5)))

        form.addRow("Aluminum - Width Threshold (ft):", self.alum_width_threshold_edit)
        form.addRow("Aluminum - Under Threshold Hours:", self.alum_under_hours_edit)
        form.addRow("Aluminum - Over Threshold Hours:", self.alum_over_hours_edit)
        form.addRow("Aluminum - Field Load & Dist:", self.alum_load_edit)
        form.addRow("Aluminum - Sidelite Hours per Foot:", self.alum_sidelite_add_edit)

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
        hw_map_value = self.settings.value("labor_hw_map", default_hw_map, type=str)
        self.hw_map_edit = QTextEdit()
        self.hw_map_edit.setPlainText(hw_map_value)
        self.hw_map_edit.setMinimumHeight(120)
        form.addRow("Hardware Category Hours (one per line: Category=Hours):", self.hw_map_edit)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.clicked.connect(self._save_and_accept)
        btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def _save_and_accept(self):
        try:
            # Door labor settings
            self.settings.setValue("labor_doors_single_hours", float(self.door_single_hours_edit.text()))
            self.settings.setValue("labor_doors_single_load", float(self.door_single_load_edit.text()))
            self.settings.setValue("labor_doors_pair_hours", float(self.door_pair_hours_edit.text()))
            self.settings.setValue("labor_doors_pair_load", float(self.door_pair_load_edit.text()))
            
            # HM labor settings
            self.settings.setValue("labor_hm_kd_hours", float(self.hm_kd_hours_edit.text()))
            self.settings.setValue("labor_hm_kd_load", float(self.hm_kd_load_edit.text()))
            self.settings.setValue("labor_hm_welded_hours", float(self.hm_welded_hours_edit.text()))
            self.settings.setValue("labor_hm_welded_load", float(self.hm_welded_load_edit.text()))
            self.settings.setValue("labor_hm_sidelite_per_foot", float(self.hm_sidelite_add_edit.text()))
            
            # Aluminum labor settings
            self.settings.setValue("labor_alum_width_threshold", float(self.alum_width_threshold_edit.text()))
            self.settings.setValue("labor_alum_under_hours", float(self.alum_under_hours_edit.text()))
            self.settings.setValue("labor_alum_over_hours", float(self.alum_over_hours_edit.text()))
            self.settings.setValue("labor_alum_load", float(self.alum_load_edit.text()))
            self.settings.setValue("labor_alum_sidelite_per_foot", float(self.alum_sidelite_add_edit.text()))
            
            # Hardware hours mapping
            self.settings.setValue("labor_hw_map", self.hw_map_edit.toPlainText())
            
            self.accept()
        except ValueError:
            # Handle invalid numeric input
            QMessageBox.warning(self, "Invalid Input", "Please check that all numeric fields contain valid numbers.")

class CreateBidDialog(QDialog):
    def __init__(
        self,
        parent,
        default_name: str,
        default_status: str = "Pending",
        default_due: Optional[QDate] = None,
        estimators: Optional[List[str]] = None,
        customers: Optional[List[str]] = None,
        customer_contacts: Optional[Dict[str, List[str]]] = None,
        customer_manager_callback: Optional[Callable[[str, bool], Tuple[List[str], Dict[str, List[str]]]]] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Create Bid")
        self.customers = customers or []
        self.customer_contacts = customer_contacts or {}
        self.customer_manager_callback = customer_manager_callback
        self.name_edit = QLineEdit(default_name)
        self.status_combo = QComboBox()
        self.status_combo.addItems(BID_STATUSES)
        if default_status in BID_STATUSES:
            self.status_combo.setCurrentText(default_status)
        self.estimator_combo = QComboBox()
        self.estimator_combo.setEditable(False)
        if estimators:
            self.estimator_combo.addItems(estimators)
        self.due_edit = QDateEdit()
        self.due_edit.setCalendarPopup(True)
        self.due_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_edit.setDate(default_due or QDate.currentDate())
        self.gc_combo = QComboBox()
        self.gc_combo.setEditable(True)
        self.gc_combo.addItems(self.customers)
        self.gc_add_button = QPushButton("+")
        self.gc_add_button.setToolTip("Open Customers Management to add a new GC")
        self.gc_add_button.setFixedWidth(28)
        self.poc_combo = QComboBox()
        self.poc_combo.setEditable(True)
        self.poc_combo.addItem("")
        self.poc_add_button = QPushButton("+")
        self.poc_add_button.setToolTip("Open Customers Management for selected GC to add a Point Of Contact")
        self.poc_add_button.setFixedWidth(28)
        self.gc_combo.currentTextChanged.connect(self._on_gc_selected)
        self.gc_add_button.clicked.connect(self._open_customer_manager_for_gc)
        self.poc_add_button.clicked.connect(self._open_customer_manager_for_poc)
        self.proposal_combo = QComboBox()
        self.proposal_combo.addItems(["Proposal", "Budget"])
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Address")
        self.project_info_edit = QLineEdit()
        self.project_info_edit.setPlaceholderText("Project Information")

        gc_row = QHBoxLayout()
        gc_row.addWidget(self.gc_combo, 1)
        gc_row.addWidget(self.gc_add_button)

        poc_row = QHBoxLayout()
        poc_row.addWidget(self.poc_combo, 1)
        poc_row.addWidget(self.poc_add_button)

        form = QFormLayout(self)
        form.addRow("Name:", self.name_edit)
        form.addRow("Status:", self.status_combo)
        form.addRow("Estimator:", self.estimator_combo)
        form.addRow("Due date:", self.due_edit)
        form.addRow("GC:", gc_row)
        form.addRow("Point Of Contact:", poc_row)
        form.addRow("Type:", self.proposal_combo)
        form.addRow("Address:", self.address_edit)
        form.addRow("Project Info:", self.project_info_edit)

        btns = QHBoxLayout()
        ok = QPushButton("Create")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        form.addRow(btns)

    def _on_gc_selected(self):
        """Update Point Of Contact dropdown when GC is selected."""
        gc_name = self.gc_combo.currentText().strip()
        current_poc = self.poc_combo.currentText().strip()
        self.poc_combo.clear()
        self.poc_combo.addItem("")
        
        if gc_name in self.customer_contacts:
            contacts = self.customer_contacts[gc_name]
            self.poc_combo.addItems(contacts)
        if current_poc:
            self.poc_combo.setEditText(current_poc)

    def _open_customer_manager_for_gc(self):
        if not self.customer_manager_callback:
            return
        selected_gc = self.gc_combo.currentText().strip()
        selected_poc = self.poc_combo.currentText().strip()
        customers, contacts = self.customer_manager_callback(selected_gc, False)
        self.customers = customers or []
        self.customer_contacts = contacts or {}

        self.gc_combo.blockSignals(True)
        self.gc_combo.clear()
        self.gc_combo.addItems(self.customers)
        if selected_gc:
            self.gc_combo.setEditText(selected_gc)
        self.gc_combo.blockSignals(False)

        self._on_gc_selected()
        if selected_poc:
            self.poc_combo.setEditText(selected_poc)

    def _open_customer_manager_for_poc(self):
        if not self.customer_manager_callback:
            return
        selected_gc = self.gc_combo.currentText().strip()
        if not selected_gc:
            QMessageBox.information(self, "Select GC", "Select a GC first, then add a Point Of Contact.")
            return

        selected_poc = self.poc_combo.currentText().strip()
        customers, contacts = self.customer_manager_callback(selected_gc, True)
        self.customers = customers or []
        self.customer_contacts = contacts or {}

        self.gc_combo.blockSignals(True)
        self.gc_combo.clear()
        self.gc_combo.addItems(self.customers)
        self.gc_combo.setEditText(selected_gc)
        self.gc_combo.blockSignals(False)

        self._on_gc_selected()
        if selected_poc:
            self.poc_combo.setEditText(selected_poc)

    def values(self) -> Tuple[str, str, str, str, str, str, str, str, str]:
        name = self.name_edit.text().strip()
        status = self.status_combo.currentText()
        estimator = self.estimator_combo.currentText().strip()
        due = self.due_edit.date().toString("yyyy-MM-dd")
        gc = self.gc_combo.currentText().strip()
        poc = self.poc_combo.currentText().strip()
        proposal_type = self.proposal_combo.currentText()
        address = self.address_edit.text().strip()
        project_info = self.project_info_edit.text().strip()
        return name, status, estimator, due, gc, poc, proposal_type, address, project_info


class EditDueDateDialog(QDialog):
    def __init__(self, parent, current_due: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Due Date")
        self.due_edit = QDateEdit()
        self.due_edit.setCalendarPopup(True)
        self.due_edit.setDisplayFormat("yyyy-MM-dd")
        if current_due:
            try:
                y, m, d = [int(x) for x in current_due.split("-")]
                self.due_edit.setDate(QDate(y, m, d))
            except Exception:
                self.due_edit.setDate(QDate.currentDate())
        else:
            self.due_edit.setDate(QDate.currentDate())

        form = QFormLayout(self)
        form.addRow("Due date:", self.due_edit)
        btns = QHBoxLayout()
        ok = QPushButton("Save")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        form.addRow(btns)

    def value(self) -> str:
        return self.due_edit.date().toString("yyyy-MM-dd")


class PreferencesDialog(QDialog):
    """Dialog for managing user preferences including username and theme."""
    
    def __init__(self, parent, data_folder: Path):
        super().__init__(parent)
        self.setWindowTitle("User Preferences")
        self.data_folder = data_folder
        self.company_contacts_csv = self.data_folder / "company_contacts.csv"
        self.settings = QSettings(ORG_NAME, APP_NAME)
        
        # Load usernames from company contacts
        self.contact_names = self._load_company_contact_names()
        
        # Main layout
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Username selection
        self.username_combo = QComboBox()
        self.username_combo.setEditable(False)
        usernames = sorted(self.contact_names)
        self.username_combo.addItems(usernames)
        current_username = self.settings.value("username", "")
        if current_username:
            index = self.username_combo.findText(current_username)
            if index >= 0:
                self.username_combo.setCurrentIndex(index)
            else:
                self.username_combo.addItem(current_username)
                self.username_combo.setCurrentText(current_username)
        self.username_combo.currentTextChanged.connect(self._on_username_changed)
        form.addRow("Username:", self.username_combo)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Custom"])
        current_theme = self.settings.value("theme", "Dark")
        if current_theme not in ("Dark", "Light", "Custom"):
            current_theme = "Dark"
        self.theme_combo.setCurrentText(current_theme)
        form.addRow("Theme:", self.theme_combo)

        # Custom theme selection
        self.custom_themes = self._load_custom_themes()
        self.custom_theme_combo = QComboBox()
        self._refresh_custom_theme_combo()
        self.custom_theme_combo.setMinimumWidth(180)

        self.btn_new_theme = QPushButton("New...")
        self.btn_edit_theme = QPushButton("Edit...")
        self.btn_delete_theme = QPushButton("Delete")

        self.btn_new_theme.clicked.connect(self._new_custom_theme)
        self.btn_edit_theme.clicked.connect(self._edit_custom_theme)
        self.btn_delete_theme.clicked.connect(self._delete_custom_theme)
        self.custom_theme_combo.currentTextChanged.connect(
            lambda _text: self._on_theme_changed(self.theme_combo.currentText())
        )

        custom_row = QHBoxLayout()
        custom_row.addWidget(self.custom_theme_combo)
        custom_row.addWidget(self.btn_new_theme)
        custom_row.addWidget(self.btn_edit_theme)
        custom_row.addWidget(self.btn_delete_theme)
        form.addRow("Custom Theme:", custom_row)

        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self._on_theme_changed(self.theme_combo.currentText())
        
        layout.addLayout(form)

        proposal_label = QLabel("Proposal Boilerplate:")
        proposal_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(proposal_label)

        proposal_form = QFormLayout()
        clarifications_default = self.settings.value("proposal_boilerplate_clarifications", "", type=str)
        exclusions_default = self.settings.value("proposal_boilerplate_exclusions", "", type=str)

        self.clarifications_boilerplate_edit = QTextEdit()
        self.clarifications_boilerplate_edit.setPlainText(clarifications_default)
        self.clarifications_boilerplate_edit.setMinimumHeight(100)
        proposal_form.addRow("Clarifications boilerplate:", self.clarifications_boilerplate_edit)

        self.exclusions_boilerplate_edit = QTextEdit()
        self.exclusions_boilerplate_edit.setPlainText(exclusions_default)
        self.exclusions_boilerplate_edit.setMinimumHeight(100)
        proposal_form.addRow("Exclusions boilerplate:", self.exclusions_boilerplate_edit)

        layout.addLayout(proposal_form)

        # Quote Email Template section
        email_label = QLabel("Quote Request Email:")
        email_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(email_label)

        email_form = QFormLayout()
        quote_email_default = self.settings.value("quote_email_template", 
            "Hello,\n\nPlease provide a quote for the items listed in the attached PDF.\n\nThank you,\nBid Team", type=str)

        self.quote_email_template_edit = QTextEdit()
        self.quote_email_template_edit.setPlainText(quote_email_default)
        self.quote_email_template_edit.setMinimumHeight(80)
        email_form.addRow("Quote request template:", self.quote_email_template_edit)

        layout.addLayout(email_form)

        # OCR section
        ocr_label = QLabel("OCR:")
        ocr_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(ocr_label)

        ocr_form = QFormLayout()
        tesseract_default = self.settings.value("tesseract_path", "", type=str)

        self.tesseract_path_edit = QLineEdit(tesseract_default)
        self.tesseract_path_edit.setPlaceholderText("Leave blank to use bundled OCR or auto-detect")

        browse_tesseract_btn = QPushButton("Browse...")

        def on_browse_tesseract():
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Tesseract Executable",
                str(Path.home()),
                "Executables (*.exe);;All Files (*)"
            )
            if file_path:
                self.tesseract_path_edit.setText(file_path)

        browse_tesseract_btn.clicked.connect(on_browse_tesseract)

        tesseract_row = QHBoxLayout()
        tesseract_row.addWidget(self.tesseract_path_edit)
        tesseract_row.addWidget(browse_tesseract_btn)
        ocr_form.addRow("Tesseract Path:", tesseract_row)

        ocr_hint = QLabel("Optional. If blank, GORO uses the bundled OCR engine first, then GORO_TESSERACT_PATH, PATH, and common install folders.")
        ocr_hint.setWordWrap(True)
        ocr_form.addRow("", ocr_hint)

        layout.addLayout(ocr_form)

        
        # Updates section
        updates_label = QLabel("Updates:")
        updates_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(updates_label)

        updates_row = QHBoxLayout()
        self.btn_check_updates = QPushButton("Check for Updates")
        self.btn_check_updates.clicked.connect(self._check_for_updates)
        updates_row.addWidget(self.btn_check_updates)
        self.btn_run_setup_tutorial = QPushButton("Run Setup Tutorial")
        self.btn_run_setup_tutorial.clicked.connect(self._run_setup_tutorial)
        updates_row.addWidget(self.btn_run_setup_tutorial)
        updates_row.addStretch()
        layout.addLayout(updates_row)

        # Buttons
        btns = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self._save_and_accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
    
    def _load_company_contact_names(self) -> List[str]:
        """Load contact names from company_contacts.csv."""
        names = []
        if self.company_contacts_csv.exists():
            try:
                with open(self.company_contacts_csv, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get('Contact Name', '').strip()
                        if name:
                            names.append(name)
            except Exception:
                pass
        return sorted(set(names))
    
    def _on_username_changed(self, username: str):
        """Handle username selection changes."""
        return

    def _load_custom_themes(self) -> dict:
        raw = self.settings.value("custom_themes", "")
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_custom_themes(self):
        try:
            self.settings.setValue("custom_themes", json.dumps(self.custom_themes))
        except Exception:
            self.settings.setValue("custom_themes", "")

    def _refresh_custom_theme_combo(self):
        self.custom_theme_combo.clear()
        names = sorted(self.custom_themes.keys())
        if names:
            self.custom_theme_combo.addItems(names)
            saved_name = self.settings.value("custom_theme_name", "")
            if saved_name and saved_name in names:
                self.custom_theme_combo.setCurrentText(saved_name)
        else:
            self.custom_theme_combo.addItem("(none)")

    def _on_theme_changed(self, theme: str):
        is_custom = theme == "Custom"
        self.custom_theme_combo.setEnabled(is_custom)
        self.btn_new_theme.setEnabled(True)
        self.btn_edit_theme.setEnabled(is_custom and self.custom_theme_combo.currentText() != "(none)")
        self.btn_delete_theme.setEnabled(is_custom and self.custom_theme_combo.currentText() != "(none)")

    def _new_custom_theme(self):
        dialog = CustomThemeDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        name, colors = dialog.get_theme_data()
        if not name:
            QMessageBox.warning(self, "Custom Theme", "Please enter a theme name.")
            return
        if name in self.custom_themes:
            QMessageBox.warning(self, "Custom Theme", f"Theme '{name}' already exists.")
            return
        self.custom_themes[name] = colors
        self._save_custom_themes()
        self._refresh_custom_theme_combo()
        self.custom_theme_combo.setCurrentText(name)
        self.theme_combo.setCurrentText("Custom")

    def _edit_custom_theme(self):
        name = self.custom_theme_combo.currentText()
        if not name or name == "(none)":
            return
        colors = self.custom_themes.get(name, {})
        dialog = CustomThemeDialog(self, name=name, colors=colors)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        new_name, new_colors = dialog.get_theme_data()
        if not new_name:
            QMessageBox.warning(self, "Custom Theme", "Please enter a theme name.")
            return
        if new_name != name and new_name in self.custom_themes:
            QMessageBox.warning(self, "Custom Theme", f"Theme '{new_name}' already exists.")
            return
        if new_name != name:
            self.custom_themes.pop(name, None)
        self.custom_themes[new_name] = new_colors
        self._save_custom_themes()
        self._refresh_custom_theme_combo()
        self.custom_theme_combo.setCurrentText(new_name)
        self.theme_combo.setCurrentText("Custom")

    def _delete_custom_theme(self):
        name = self.custom_theme_combo.currentText()
        if not name or name == "(none)":
            return
        reply = QMessageBox.question(
            self,
            "Delete Theme",
            f"Delete custom theme '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.custom_themes.pop(name, None)
        self._save_custom_themes()
        self._refresh_custom_theme_combo()
    
    def _check_for_updates(self):
        """Manually trigger an update check."""
        check_for_updates_manual(self, self.settings, APP_VERSION)

    def _run_setup_tutorial(self):
        """Run the first-install setup tutorial on demand."""
        parent_window = self.parent()
        if parent_window is None:
            QMessageBox.warning(self, "Setup Tutorial", "Could not find the main window.")
            return

        QMessageBox.information(
            self,
            "Setup Step 1 of 3",
            "Choose your Data folder now.\n\n"
            "Recommended: pick a location outside the app install folder "
            "(for example OneDrive or a shared company directory).",
        )

        previous_root = str(getattr(getattr(parent_window, "paths", None), "root", ""))
        if hasattr(parent_window, "choose_data_folder"):
            parent_window.choose_data_folder()
        current_root = str(getattr(getattr(parent_window, "paths", None), "root", ""))
        if current_root and current_root != previous_root:
            QMessageBox.information(
                self,
                "Data Folder Updated",
                f"Data folder set to:\n{current_root}",
            )
        else:
            QMessageBox.information(
                self,
                "Data Folder Unchanged",
                "No folder was selected, so the current Data folder was kept.",
            )

        QMessageBox.information(
            self,
            "Setup Step 2 of 3",
            "Next: set up your company profile and contacts/users.\n\n"
            "In My Company, add your company details and add contacts.\n"
            "Use the Position column for roles like Estimator or Project Manager.",
        )
        if hasattr(parent_window, "open_my_company"):
            parent_window.open_my_company()

        QMessageBox.information(
            self,
            "Setup Step 3 of 3",
            "Last: choose your active username here in Preferences.\n\n"
            "Tip: usernames are pulled from My Company contacts.\n"
            "Click Save when done.",
        )

        self.settings.setValue("first_install_tutorial_completed", True)
        QMessageBox.information(
            self,
            "Setup Complete",
            "Setup tutorial completed.\n"
            "You can run it again any time from Preferences.",
        )

    def _save_and_accept(self):
        """Save preferences and update users.csv."""
        username = self.username_combo.currentText().strip()
        theme = self.theme_combo.currentText()
        
        if not username:
            return
        
        # Save to QSettings
        self.settings.setValue("username", username)
        self.settings.setValue("theme", theme)
        if theme == "Custom":
            custom_name = self.custom_theme_combo.currentText()
            if not custom_name or custom_name == "(none)":
                QMessageBox.warning(self, "Custom Theme", "Select or create a custom theme first.")
                return
            self.settings.setValue("custom_theme_name", custom_name)

        self.settings.setValue(
            "proposal_boilerplate_clarifications",
            self.clarifications_boilerplate_edit.toPlainText().strip()
        )
        self.settings.setValue(
            "proposal_boilerplate_exclusions",
            self.exclusions_boilerplate_edit.toPlainText().strip()
        )
        self.settings.setValue(
            "quote_email_template",
            self.quote_email_template_edit.toPlainText().strip()
        )
        self.settings.setValue("tesseract_path", self.tesseract_path_edit.text().strip())
        
        self.accept()

class VendorQuoteDialog(QDialog):
    """Dialog for selecting a vendor to email a quote to."""
    
    def __init__(self, vendors: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Vendor for Quote")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Select vendor to email quote to:")
        layout.addWidget(label)
        
        self.vendor_combo = QComboBox()
        self.vendor_combo.addItems(vendors)
        layout.addWidget(self.vendor_combo)
        
        # Button layout
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Send Quote Email")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def get_selected_vendor(self) -> str:
        """Get the selected vendor name."""
        return self.vendor_combo.currentText()
