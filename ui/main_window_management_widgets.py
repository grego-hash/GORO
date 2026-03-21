"""Management widgets extracted from main_window.py."""

import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSplitter,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .dialogs import LaborSettingsDialog
from .main_window_hw_groups import write_hardware_groups_pdf
from .main_window_ui_helpers import QFileDialog, QMessageBox
from core.optional_services import HAS_REPORTLAB
from widgets.table_helpers import ComboBoxDelegate, NoRowHeaderTable


class VendorsWidget(QWidget):
    """Custom widget for managing vendors with contact information."""
    
    def __init__(self, parent=None, data_path: Optional[Path] = None):
        super().__init__(parent)
        self.current_vendor = None
        self.changes_made = False
        self.data_path = Path(data_path) if data_path is not None else (Path(__file__).resolve().parent.parent / "data")
        self.vendors_info = {}  # {vendor_name: {'address': '', 'phone': '', 'website': '', 'email': '', 'capabilities': {}}}
        self.vendors_contacts = {}  # {vendor_name: [(contact_name, position, email, phone, is_default), ...]}
        
        # Define capability categories
        self.capability_categories = {
            'Doors': ['Hollow Metal Doors', 'Wood Doors', 'Aluminum Doors', 'Misc. Doors'],
            'Frames': ['Hollow Metal Frames', 'Aluminum Frames', 'Misc. Frames'],
            'Hardware': ['Hardware']
        }
        
        self.setup_ui()
        self.load_vendors_data()
    
    def setup_ui(self):
        """Setup the UI layout with vendor list and contact details."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL: Vendor list with search
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        vendor_label = QLabel("Vendors")
        vendor_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search vendors...")
        self.search_box.textChanged.connect(self.filter_vendors)
        
        # Button layout for vendors
        vendor_button_layout = QHBoxLayout()
        add_vendor_button = QPushButton("Add")
        add_vendor_button.setMaximumWidth(70)
        add_vendor_button.clicked.connect(self.add_new_vendor)
        
        del_vendor_button = QPushButton("Delete")
        del_vendor_button.setMaximumWidth(70)
        del_vendor_button.clicked.connect(self.delete_current_vendor)
        
        vendor_button_layout.addWidget(add_vendor_button)
        vendor_button_layout.addWidget(del_vendor_button)
        vendor_button_layout.addStretch()
        
        self.vendors_list = QListWidget()
        self.vendors_list.setMinimumWidth(200)
        self.vendors_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.vendors_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.vendors_list.itemSelectionChanged.connect(self.on_vendor_selected)
        
        left_layout.addWidget(vendor_label)
        left_layout.addWidget(self.search_box)
        left_layout.addLayout(vendor_button_layout)
        left_layout.addWidget(self.vendors_list)
        
        # RIGHT PANEL: Vendor details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        details_label = QLabel("Vendor Details")
        details_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Vendor name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Vendor Name:")
        self.vendor_name_field = QLineEdit()
        self.vendor_name_field.setPlaceholderText("Enter vendor name...")
        self.vendor_name_field.textChanged.connect(self.on_vendor_name_changed)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.vendor_name_field)
        
        # Vendor information fields
        info_label = QLabel("Vendor Information")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        
        info_form = QFormLayout()
        info_form.setSpacing(8)
        
        self.vendor_address_field = QLineEdit()
        self.vendor_address_field.setPlaceholderText("Street address...")
        self.vendor_address_field.textChanged.connect(self.on_vendor_info_changed)
        
        self.vendor_phone_field = QLineEdit()
        self.vendor_phone_field.setPlaceholderText("Main phone number...")
        self.vendor_phone_field.textChanged.connect(self.on_vendor_info_changed)
        
        self.vendor_website_field = QLineEdit()
        self.vendor_website_field.setPlaceholderText("https://...")
        self.vendor_website_field.textChanged.connect(self.on_vendor_info_changed)
        
        self.vendor_email_field = QLineEdit()
        self.vendor_email_field.setPlaceholderText("general@vendor.com")
        self.vendor_email_field.textChanged.connect(self.on_vendor_info_changed)
        
        info_form.addRow("Address:", self.vendor_address_field)
        info_form.addRow("Phone:", self.vendor_phone_field)
        info_form.addRow("Website:", self.vendor_website_field)
        info_form.addRow("Email:", self.vendor_email_field)
        
        # Vendor Capabilities section
        capabilities_label = QLabel("Vendor Capabilities")
        capabilities_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        
        # Create checkboxes for capabilities
        capabilities_widget = QWidget()
        capabilities_layout = QVBoxLayout(capabilities_widget)
        capabilities_layout.setContentsMargins(0, 0, 0, 0)
        capabilities_layout.setSpacing(5)
        
        self.capability_checkboxes = {}
        
        for category, items in self.capability_categories.items():
            # Category label
            category_label = QLabel(f"{category}:")
            category_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
            capabilities_layout.addWidget(category_label)
            
            # Checkboxes for items in category
            for item in items:
                checkbox = QCheckBox(item)
                checkbox.stateChanged.connect(self.on_capability_changed)
                capabilities_layout.addWidget(checkbox)
                self.capability_checkboxes[item] = checkbox
        
        # Contacts section
        contacts_label = QLabel("Contacts")
        contacts_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        
        # Button layout for contacts
        contacts_button_layout = QHBoxLayout()
        add_contact_button = QPushButton("Add Contact")
        add_contact_button.setMaximumWidth(120)
        add_contact_button.clicked.connect(self.add_new_contact)
        
        del_contact_button = QPushButton("Delete")
        del_contact_button.setMaximumWidth(70)
        del_contact_button.clicked.connect(self.delete_selected_contact)
        
        contacts_button_layout.addWidget(add_contact_button)
        contacts_button_layout.addWidget(del_contact_button)
        contacts_button_layout.addStretch()
        
        self.contacts_table = NoRowHeaderTable()
        self.contacts_table.setColumnCount(5)
        self.contacts_table.setHorizontalHeaderLabels(["Default", "Name", "Position", "Email", "Phone"])
        _ct_hdr = self.contacts_table.horizontalHeader()
        assert _ct_hdr is not None
        _ct_hdr.setStretchLastSection(True)
        self.contacts_table.setColumnWidth(0, 60)  # Default checkbox column
        self.contacts_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.contacts_table.setStyleSheet("""
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
        self.contacts_table.itemChanged.connect(self.on_contact_changed)
        self.contacts_table.cellClicked.connect(self.on_contact_cell_clicked)
        
        right_layout.addWidget(details_label)
        right_layout.addLayout(name_layout)
        right_layout.addWidget(info_label)
        right_layout.addLayout(info_form)
        right_layout.addWidget(capabilities_label)
        right_layout.addWidget(capabilities_widget)
        right_layout.addWidget(contacts_label)
        right_layout.addLayout(contacts_button_layout)
        right_layout.addWidget(self.contacts_table)
        
        # Add panels to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def load_vendors_data(self):
        """Load vendors data from CSV files."""
        # Load vendor information
        vendors_info_path = self.data_path / "vendors_info.csv"
        if vendors_info_path.exists():
            try:
                with open(vendors_info_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    # Check for both old and new formats
                    has_capabilities = headers and len(headers) > 5
                    
                    for row in reader:
                        if len(row) >= 5:
                            vendor_name = row[0].strip()
                            self.vendors_info[vendor_name] = {
                                'address': row[1].strip(),
                                'phone': row[2].strip(),
                                'website': row[3].strip(),
                                'email': row[4].strip(),
                                'capabilities': {}
                            }
                            
                            # Load capabilities if present
                            if has_capabilities and len(row) > 5:
                                # Capabilities stored as comma-separated in column 5
                                capabilities_str = row[5].strip()
                                if capabilities_str:
                                    for cap in capabilities_str.split('|'):
                                        cap = cap.strip()
                                        if cap:
                                            self.vendors_info[vendor_name]['capabilities'][cap] = True
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Could not load vendors_info.csv:\n{e}")
        
        # Load vendor contacts
        vendors_contacts_path = self.data_path / "vendors_contacts.csv"
        if vendors_contacts_path.exists():
            try:
                with open(vendors_contacts_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    if headers and headers == ["Vendor Name", "Contact Name", "Position", "Email", "Phone", "Default"]:
                        for row in reader:
                            if len(row) >= 6:
                                vendor_name = row[0].strip()
                                contact_name = row[1].strip()
                                position = row[2].strip()
                                email = row[3].strip()
                                phone = row[4].strip()
                                is_default = row[5].strip().lower() == 'true'
                                
                                if vendor_name not in self.vendors_contacts:
                                    self.vendors_contacts[vendor_name] = []
                                
                                self.vendors_contacts[vendor_name].append((contact_name, position, email, phone, is_default))
                                
                                # Ensure vendor exists in vendors_info
                                if vendor_name not in self.vendors_info:
                                    self.vendors_info[vendor_name] = {'address': '', 'phone': '', 'website': '', 'email': '', 'capabilities': {}}
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Could not load vendors_contacts.csv:\n{e}")
        
        # Populate vendors list
        self.populate_vendors_list()
    
    def populate_vendors_list(self):
        """Populate the vendors list widget."""
        self.vendors_list.clear()
        # Combine vendors from both info and contacts
        all_vendors = set(self.vendors_info.keys()) | set(self.vendors_contacts.keys())
        for vendor_name in sorted(all_vendors):
            self.vendors_list.addItem(vendor_name)
    
    def filter_vendors(self, search_text):
        """Filter vendors list based on search text."""
        search_text = search_text.lower()
        for i in range(self.vendors_list.count()):
            item = self.vendors_list.item(i)
            if item is None:
                continue
            vendor_name = item.text().lower()
            item.setHidden(search_text not in vendor_name)
    
    def add_new_vendor(self):
        """Add a new vendor."""
        vendor_name, ok = QInputDialog.getText(self, "New Vendor", "Enter vendor name:")
        if ok and vendor_name.strip():
            vendor_name = vendor_name.strip()
            if vendor_name in self.vendors_info or vendor_name in self.vendors_contacts:
                QMessageBox.warning(self, "Duplicate Vendor", f"Vendor '{vendor_name}' already exists.")
                return
            
            self.vendors_info[vendor_name] = {'address': '', 'phone': '', 'website': '', 'email': '', 'capabilities': {}}
            self.vendors_contacts[vendor_name] = []
            self.populate_vendors_list()
            
            # Select the new vendor
            items = self.vendors_list.findItems(vendor_name, Qt.MatchFlag.MatchExactly)
            if items:
                self.vendors_list.setCurrentItem(items[0])
            
            self.changes_made = True
    
    def delete_current_vendor(self):
        """Delete the currently selected vendor."""
        if not self.current_vendor:
            QMessageBox.warning(self, "No Selection", "Please select a vendor to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete vendor '{self.current_vendor}' and all its contacts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.current_vendor in self.vendors_info:
                del self.vendors_info[self.current_vendor]
            if self.current_vendor in self.vendors_contacts:
                del self.vendors_contacts[self.current_vendor]
            self.current_vendor = None
            self.populate_vendors_list()
            self.clear_details_panel()
            self.changes_made = True
    
    def on_vendor_selected(self):
        """Handle vendor selection change."""
        items = self.vendors_list.selectedItems()
        if not items:
            self.current_vendor = None
            self.clear_details_panel()
            return
        
        vendor_name = items[0].text()
        self.current_vendor = vendor_name
        self.load_vendor_details()
    
    def load_vendor_details(self):
        """Load details for the currently selected vendor."""
        if not self.current_vendor:
            return
        
        # Update vendor name field
        self.vendor_name_field.blockSignals(True)
        self.vendor_name_field.setText(self.current_vendor)
        self.vendor_name_field.blockSignals(False)
        
        # Load vendor information
        vendor_info = self.vendors_info.get(self.current_vendor, {'address': '', 'phone': '', 'website': '', 'email': '', 'capabilities': {}})
        
        self.vendor_address_field.blockSignals(True)
        self.vendor_phone_field.blockSignals(True)
        self.vendor_website_field.blockSignals(True)
        self.vendor_email_field.blockSignals(True)
        
        self.vendor_address_field.setText(vendor_info.get('address', ''))
        self.vendor_phone_field.setText(vendor_info.get('phone', ''))
        self.vendor_website_field.setText(vendor_info.get('website', ''))
        self.vendor_email_field.setText(vendor_info.get('email', ''))
        
        self.vendor_address_field.blockSignals(False)
        self.vendor_phone_field.blockSignals(False)
        self.vendor_website_field.blockSignals(False)
        self.vendor_email_field.blockSignals(False)
        
        # Load capabilities
        capabilities = vendor_info.get('capabilities', {})
        for capability_name, checkbox in self.capability_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(capabilities.get(capability_name, False))
            checkbox.blockSignals(False)
        
        # Load contacts
        self.contacts_table.blockSignals(True)
        self.contacts_table.setRowCount(0)
        
        contacts = self.vendors_contacts.get(self.current_vendor, [])
        for contact_name, position, email, phone, is_default in contacts:
            row = self.contacts_table.rowCount()
            self.contacts_table.insertRow(row)
            
            # Default checkbox
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Checked if is_default else Qt.CheckState.Unchecked)
            self.contacts_table.setItem(row, 0, checkbox_item)
            
            self.contacts_table.setItem(row, 1, QTableWidgetItem(contact_name))
            self.contacts_table.setItem(row, 2, QTableWidgetItem(position))
            self.contacts_table.setItem(row, 3, QTableWidgetItem(email))
            self.contacts_table.setItem(row, 4, QTableWidgetItem(phone))
        
        self.contacts_table.blockSignals(False)
    
    def clear_details_panel(self):
        """Clear the details panel."""
        self.vendor_name_field.blockSignals(True)
        self.vendor_name_field.clear()
        self.vendor_name_field.blockSignals(False)
        
        self.vendor_address_field.blockSignals(True)
        self.vendor_phone_field.blockSignals(True)
        self.vendor_website_field.blockSignals(True)
        self.vendor_email_field.blockSignals(True)
        
        self.vendor_address_field.clear()
        self.vendor_phone_field.clear()
        self.vendor_website_field.clear()
        self.vendor_email_field.clear()
        
        self.vendor_address_field.blockSignals(False)
        self.vendor_phone_field.blockSignals(False)
        self.vendor_website_field.blockSignals(False)
        self.vendor_email_field.blockSignals(False)
        
        # Clear capabilities
        for checkbox in self.capability_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        
        self.contacts_table.blockSignals(True)
        self.contacts_table.setRowCount(0)
        self.contacts_table.blockSignals(False)
    
    def on_vendor_name_changed(self):
        """Handle vendor name field change."""
        if not self.current_vendor:
            return
        
        new_name = self.vendor_name_field.text().strip()
        if not new_name:
            return
        
        if new_name == self.current_vendor:
            return
        
        # Check if new name already exists
        if (new_name in self.vendors_info or new_name in self.vendors_contacts) and new_name != self.current_vendor:
            QMessageBox.warning(self, "Duplicate Vendor", f"Vendor '{new_name}' already exists.")
            self.vendor_name_field.setText(self.current_vendor)
            return
        
        # Rename vendor
        if self.current_vendor in self.vendors_info:
            self.vendors_info[new_name] = self.vendors_info.pop(self.current_vendor)
        if self.current_vendor in self.vendors_contacts:
            self.vendors_contacts[new_name] = self.vendors_contacts.pop(self.current_vendor)
        
        old_vendor = self.current_vendor
        self.current_vendor = new_name
        
        # Update list
        self.populate_vendors_list()
        items = self.vendors_list.findItems(new_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.vendors_list.setCurrentItem(items[0])
        
        self.changes_made = True
    
    def on_vendor_info_changed(self):
        """Handle vendor information field changes."""
        if not self.current_vendor:
            return
        
        # Ensure vendor exists in vendors_info
        if self.current_vendor not in self.vendors_info:
            self.vendors_info[self.current_vendor] = {'capabilities': {}}
        
        # Preserve existing capabilities when updating info
        existing_capabilities = self.vendors_info[self.current_vendor].get('capabilities', {})
        
        # Update vendor information
        self.vendors_info[self.current_vendor] = {
            'address': self.vendor_address_field.text().strip(),
            'phone': self.vendor_phone_field.text().strip(),
            'website': self.vendor_website_field.text().strip(),
            'email': self.vendor_email_field.text().strip(),
            'capabilities': existing_capabilities
        }
        
        self.changes_made = True
    
    def on_capability_changed(self):
        """Handle capability checkbox change."""
        if not self.current_vendor:
            return
        
        # Ensure vendor exists in vendors_info
        if self.current_vendor not in self.vendors_info:
            self.vendors_info[self.current_vendor] = {'address': '', 'phone': '', 'website': '', 'email': '', 'capabilities': {}}
        
        # Update capabilities based on checkboxes
        capabilities = {}
        for capability_name, checkbox in self.capability_checkboxes.items():
            if checkbox.isChecked():
                capabilities[capability_name] = True
        
        self.vendors_info[self.current_vendor]['capabilities'] = capabilities
        self.changes_made = True
    
    def add_new_contact(self):
        """Add a new contact to the current vendor."""
        if not self.current_vendor:
            QMessageBox.warning(self, "No Vendor", "Please select a vendor first.")
            return
        
        row = self.contacts_table.rowCount()
        self.contacts_table.insertRow(row)
        
        # Default checkbox
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        checkbox_item.setCheckState(Qt.CheckState.Unchecked)
        self.contacts_table.setItem(row, 0, checkbox_item)
        
        self.contacts_table.setItem(row, 1, QTableWidgetItem(""))
        self.contacts_table.setItem(row, 2, QTableWidgetItem(""))
        self.contacts_table.setItem(row, 3, QTableWidgetItem(""))
        self.contacts_table.setItem(row, 4, QTableWidgetItem(""))
        
        self.changes_made = True
    
    def delete_selected_contact(self):
        """Delete the currently selected contact."""
        current_row = self.contacts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a contact to delete.")
            return
        
        self.contacts_table.removeRow(current_row)
        self.save_current_vendor_contacts()
        self.changes_made = True
    
    def on_contact_changed(self, item):
        """Handle contact table cell change."""
        if self.current_vendor:
            self.save_current_vendor_contacts()
            self.changes_made = True
    
    def on_contact_cell_clicked(self, row, col):
        """Handle contact cell click for default checkbox."""
        if col == 0:  # Default checkbox column
            # Ensure only one checkbox is checked
            clicked_item = self.contacts_table.item(row, 0)
            if clicked_item and clicked_item.checkState() == Qt.CheckState.Checked:
                # Uncheck all other checkboxes
                self.contacts_table.blockSignals(True)
                for r in range(self.contacts_table.rowCount()):
                    if r != row:
                        item = self.contacts_table.item(r, 0)
                        if item:
                            item.setCheckState(Qt.CheckState.Unchecked)
                self.contacts_table.blockSignals(False)
                
                self.save_current_vendor_contacts()
                self.changes_made = True
    
    def save_current_vendor_contacts(self):
        """Save current vendor's contact data from the table."""
        if not self.current_vendor:
            return
        
        contacts = []
        for row in range(self.contacts_table.rowCount()):
            checkbox_item = self.contacts_table.item(row, 0)
            name_item = self.contacts_table.item(row, 1)
            position_item = self.contacts_table.item(row, 2)
            email_item = self.contacts_table.item(row, 3)
            phone_item = self.contacts_table.item(row, 4)
            
            is_default = checkbox_item.checkState() == Qt.CheckState.Checked if checkbox_item else False
            
            contacts.append((
                name_item.text().strip() if name_item else "",
                position_item.text().strip() if position_item else "",
                email_item.text().strip() if email_item else "",
                phone_item.text().strip() if phone_item else "",
                is_default
            ))
        
        self.vendors_contacts[self.current_vendor] = contacts
    
    def save_to_csv(self):
        """Save vendors data to CSV files."""
        if not self.changes_made:
            return
        
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Save vendor information with capabilities
        vendors_info_path = self.data_path / "vendors_info.csv"
        info_rows = [["Vendor Name", "Address", "Phone", "Website", "Email", "Capabilities"]]
        for vendor_name in sorted(self.vendors_info.keys()):
            info = self.vendors_info[vendor_name]
            # Convert capabilities dict to pipe-separated string
            capabilities = info.get('capabilities', {})
            capabilities_str = '|'.join([cap for cap, enabled in capabilities.items() if enabled])
            
            info_rows.append([
                vendor_name,
                info.get('address', ''),
                info.get('phone', ''),
                info.get('website', ''),
                info.get('email', ''),
                capabilities_str
            ])
        
        try:
            with open(vendors_info_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(info_rows)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save vendors_info.csv:\n{e}")
            return
        
        # Save vendor contacts
        vendors_contacts_path = self.data_path / "vendors_contacts.csv"
        contacts_rows = [["Vendor Name", "Contact Name", "Position", "Email", "Phone", "Default"]]
        for vendor_name in sorted(self.vendors_contacts.keys()):
            contacts = self.vendors_contacts[vendor_name]
            if contacts:
                for contact_name, position, email, phone, is_default in contacts:
                    contacts_rows.append([
                        vendor_name,
                        contact_name,
                        position,
                        email,
                        phone,
                        'True' if is_default else 'False'
                    ])
        
        try:
            with open(vendors_contacts_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(contacts_rows)
            self.changes_made = False
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save vendors_contacts.csv:\n{e}")


class MyCompanyWidget(QWidget):
    """Company management widget mirroring customer details layout without customer list or bids/projects."""

    def __init__(self, parent=None, data_path: Optional[Path] = None):
        super().__init__(parent)
        self.changes_made = False

        self.data_path = Path(data_path) if data_path is not None else (Path(__file__).resolve().parent.parent / "data")
        self.company_info_csv = self.data_path / "company_info.csv"
        self.company_contacts_csv = self.data_path / "company_contacts.csv"
        self.logo_path = Path.home() / ".goro" / "company_logo.png"

        self.company_info = {
            "name": "",
            "address": "",
            "phone": "",
            "website": "",
            "email": "",
            "accent_color": "#7a0000",
        }
        self.company_contacts = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        details_label = QLabel("Company Details")
        details_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        name_layout = QHBoxLayout()
        name_label = QLabel("Company Name:")
        self.company_name_field = QLineEdit()
        self.company_name_field.setPlaceholderText("Enter company name...")
        self.company_name_field.textChanged.connect(self.on_company_info_changed)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.company_name_field)

        info_label = QLabel("Company Information")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")

        info_form = QFormLayout()
        info_form.setSpacing(8)

        self.company_address_field = QLineEdit()
        self.company_address_field.setPlaceholderText("Street address...")
        self.company_address_field.textChanged.connect(self.on_company_info_changed)

        self.company_phone_field = QLineEdit()
        self.company_phone_field.setPlaceholderText("Main phone number...")
        self.company_phone_field.textChanged.connect(self.on_company_info_changed)

        self.company_website_field = QLineEdit()
        self.company_website_field.setPlaceholderText("https://...")
        self.company_website_field.textChanged.connect(self.on_company_info_changed)

        self.company_email_field = QLineEdit()
        self.company_email_field.setPlaceholderText("info@company.com")
        self.company_email_field.textChanged.connect(self.on_company_info_changed)

        info_form.addRow("Address:", self.company_address_field)
        info_form.addRow("Phone:", self.company_phone_field)
        info_form.addRow("Website:", self.company_website_field)
        info_form.addRow("Email:", self.company_email_field)

        contacts_label = QLabel("Contacts")
        contacts_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")

        contacts_button_layout = QHBoxLayout()
        add_contact_button = QPushButton("Add Contact")
        add_contact_button.setMaximumWidth(120)
        add_contact_button.clicked.connect(self.add_new_contact)

        del_contact_button = QPushButton("Delete")
        del_contact_button.setMaximumWidth(70)
        del_contact_button.clicked.connect(self.delete_selected_contact)

        contacts_button_layout.addWidget(add_contact_button)
        contacts_button_layout.addWidget(del_contact_button)
        contacts_button_layout.addStretch()

        self.contacts_table = NoRowHeaderTable()
        self.contacts_table.setColumnCount(5)
        self.contacts_table.setHorizontalHeaderLabels(["Default", "Name", "Position", "Email", "Phone"])
        _ct_hdr = self.contacts_table.horizontalHeader()
        assert _ct_hdr is not None
        _ct_hdr.setStretchLastSection(True)
        self.contacts_table.setColumnWidth(0, 60)
        self.contacts_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.contacts_table.setStyleSheet("""
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
        self.contacts_table.itemChanged.connect(self.on_contact_changed)
        self.contacts_table.cellClicked.connect(self.on_contact_cell_clicked)

        logo_label = QLabel("Company Logo")
        logo_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")

        logo_row = QHBoxLayout()
        self.logo_status_label = QLabel("No logo uploaded")
        btn_upload_logo = QPushButton("Upload Logo")
        btn_clear_logo = QPushButton("Clear Logo")
        btn_upload_logo.clicked.connect(self.upload_logo)
        btn_clear_logo.clicked.connect(self.clear_logo)
        logo_row.addWidget(self.logo_status_label)
        logo_row.addStretch()
        logo_row.addWidget(btn_upload_logo)
        logo_row.addWidget(btn_clear_logo)

        main_layout.addWidget(details_label)
        main_layout.addLayout(name_layout)
        main_layout.addWidget(info_label)
        main_layout.addLayout(info_form)
        main_layout.addWidget(contacts_label)
        main_layout.addLayout(contacts_button_layout)
        main_layout.addWidget(self.contacts_table)

        labor_label = QLabel("Labor Automation")
        labor_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        labor_row = QHBoxLayout()
        labor_btn = QPushButton("Edit Labor Defaults...")
        labor_btn.clicked.connect(self.open_labor_defaults)
        labor_row.addWidget(labor_btn)
        labor_row.addStretch()

        main_layout.addWidget(labor_label)
        main_layout.addLayout(labor_row)

        accent_label = QLabel("Accent Color")
        accent_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")

        accent_row = QHBoxLayout()
        self.accent_swatch = QFrame()
        self.accent_swatch.setFixedSize(36, 24)
        self.accent_swatch.setFrameShape(QFrame.Shape.Box)
        self._update_swatch(self.company_info["accent_color"])

        btn_pick_color = QPushButton("Choose Color...")
        btn_pick_color.clicked.connect(self.pick_accent_color)
        btn_reset_color = QPushButton("Reset to Default")
        btn_reset_color.clicked.connect(self.reset_accent_color)

        accent_row.addWidget(self.accent_swatch)
        accent_row.addWidget(btn_pick_color)
        accent_row.addWidget(btn_reset_color)
        accent_row.addStretch()

        main_layout.addWidget(accent_label)
        main_layout.addLayout(accent_row)

        main_layout.addWidget(logo_label)
        main_layout.addLayout(logo_row)

    def load_data(self):
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.logo_path.parent.mkdir(parents=True, exist_ok=True)

        if self.company_info_csv.exists():
            try:
                with open(self.company_info_csv, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    row = next(reader, None)
                    if row:
                        self.company_info["name"] = row.get("Company Name", "").strip()
                        self.company_info["address"] = row.get("Address", "").strip()
                        self.company_info["phone"] = row.get("Phone", "").strip()
                        self.company_info["website"] = row.get("Website", "").strip()
                        self.company_info["email"] = row.get("Email", "").strip()
                        self.company_info["accent_color"] = row.get("Accent Color", "").strip() or "#7a0000"
            except Exception:
                pass

        self.company_contacts = []
        if self.company_contacts_csv.exists():
            try:
                with open(self.company_contacts_csv, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.company_contacts.append((
                            row.get("Contact Name", "").strip(),
                            row.get("Position", "").strip(),
                            row.get("Email", "").strip(),
                            row.get("Phone", "").strip(),
                            row.get("Default", "").strip().lower() == "true",
                        ))
            except Exception:
                pass

        self.company_name_field.blockSignals(True)
        self.company_address_field.blockSignals(True)
        self.company_phone_field.blockSignals(True)
        self.company_website_field.blockSignals(True)
        self.company_email_field.blockSignals(True)

        self.company_name_field.setText(self.company_info["name"])
        self.company_address_field.setText(self.company_info["address"])
        self.company_phone_field.setText(self.company_info["phone"])
        self.company_website_field.setText(self.company_info["website"])
        self.company_email_field.setText(self.company_info["email"])

        self.company_name_field.blockSignals(False)
        self.company_address_field.blockSignals(False)
        self.company_phone_field.blockSignals(False)
        self.company_website_field.blockSignals(False)
        self.company_email_field.blockSignals(False)

        self._update_swatch(self.company_info["accent_color"])
        self._load_contacts_table()
        self._refresh_logo_status()
        self.changes_made = False

    def _load_contacts_table(self):
        self.contacts_table.blockSignals(True)
        self.contacts_table.setRowCount(0)
        for contact_name, position, email, phone, is_default in self.company_contacts:
            row = self.contacts_table.rowCount()
            self.contacts_table.insertRow(row)

            default_item = QTableWidgetItem()
            default_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            default_item.setCheckState(Qt.CheckState.Checked if is_default else Qt.CheckState.Unchecked)
            self.contacts_table.setItem(row, 0, default_item)
            self.contacts_table.setItem(row, 1, QTableWidgetItem(contact_name))
            self.contacts_table.setItem(row, 2, QTableWidgetItem(position))
            self.contacts_table.setItem(row, 3, QTableWidgetItem(email))
            self.contacts_table.setItem(row, 4, QTableWidgetItem(phone))
        self.contacts_table.blockSignals(False)

    def _update_swatch(self, hex_color: str):
        self.accent_swatch.setStyleSheet(
            f"background-color: {hex_color}; border: 1px solid #555;"
        )

    def pick_accent_color(self):
        current = QColor(self.company_info.get("accent_color", "#7a0000"))
        color = QColorDialog.getColor(current, self, "Select Accent Color")
        if color.isValid():
            hex_val = color.name()  # e.g. '#ab1234'
            self.company_info["accent_color"] = hex_val
            self._update_swatch(hex_val)
            self.changes_made = True

    def reset_accent_color(self):
        self.company_info["accent_color"] = "#7a0000"
        self._update_swatch("#7a0000")
        self.changes_made = True

    def _refresh_logo_status(self):
        if self.logo_path.exists():
            self.logo_status_label.setText(f"Logo: {self.logo_path.name}")
        else:
            self.logo_status_label.setText("No logo uploaded")

    def on_company_info_changed(self):
        self.company_info = {
            "name": self.company_name_field.text().strip(),
            "address": self.company_address_field.text().strip(),
            "phone": self.company_phone_field.text().strip(),
            "website": self.company_website_field.text().strip(),
            "email": self.company_email_field.text().strip(),
            "accent_color": self.company_info.get("accent_color", "#7a0000"),
        }
        self.changes_made = True

    def add_new_contact(self):
        row = self.contacts_table.rowCount()
        self.contacts_table.insertRow(row)
        default_item = QTableWidgetItem()
        default_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        default_item.setCheckState(Qt.CheckState.Unchecked)
        self.contacts_table.setItem(row, 0, default_item)
        for col in range(1, 5):
            self.contacts_table.setItem(row, col, QTableWidgetItem(""))
        self.changes_made = True

    def delete_selected_contact(self):
        current_row = self.contacts_table.currentRow()
        if current_row >= 0:
            self.contacts_table.removeRow(current_row)
            self.update_contacts_from_table()
            self.changes_made = True

    def on_contact_changed(self, item):
        self.update_contacts_from_table()
        self.changes_made = True

    def on_contact_cell_clicked(self, row, col):
        if col == 0:
            item = self.contacts_table.item(row, col)
            if item and item.checkState() == Qt.CheckState.Checked:
                self.contacts_table.blockSignals(True)
                for r in range(self.contacts_table.rowCount()):
                    if r != row:
                        other_item = self.contacts_table.item(r, 0)
                        if other_item:
                            other_item.setCheckState(Qt.CheckState.Unchecked)
                self.contacts_table.blockSignals(False)
            self.update_contacts_from_table()
            self.changes_made = True

    def update_contacts_from_table(self):
        contacts = []
        for row in range(self.contacts_table.rowCount()):
            default_item = self.contacts_table.item(row, 0)
            name_item = self.contacts_table.item(row, 1)
            position_item = self.contacts_table.item(row, 2)
            email_item = self.contacts_table.item(row, 3)
            phone_item = self.contacts_table.item(row, 4)

            is_default = default_item.checkState() == Qt.CheckState.Checked if default_item else False
            name = name_item.text().strip() if name_item else ""
            position = position_item.text().strip() if position_item else ""
            email = email_item.text().strip() if email_item else ""
            phone = phone_item.text().strip() if phone_item else ""
            contacts.append((name, position, email, phone, is_default))

        self.company_contacts = contacts

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Company Logo",
            str(Path.home()),
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
        )
        if not file_path:
            return
        try:
            self.logo_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_path, self.logo_path)
            self._refresh_logo_status()
            self.changes_made = True
        except Exception as e:
            QMessageBox.warning(self, "Logo", f"Could not upload logo:\n{e}")

    def clear_logo(self):
        try:
            if self.logo_path.exists():
                self.logo_path.unlink()
            self._refresh_logo_status()
            self.changes_made = True
        except Exception as e:
            QMessageBox.warning(self, "Logo", f"Could not clear logo:\n{e}")

    def open_labor_defaults(self):
        dialog = LaborSettingsDialog(self)
        dialog.exec()

    def save_to_csv(self):
        self.on_company_info_changed()
        self.update_contacts_from_table()
        self.data_path.mkdir(parents=True, exist_ok=True)

        info_rows = [["Company Name", "Address", "Phone", "Website", "Email", "Accent Color"], [
            self.company_info.get("name", ""),
            self.company_info.get("address", ""),
            self.company_info.get("phone", ""),
            self.company_info.get("website", ""),
            self.company_info.get("email", ""),
            self.company_info.get("accent_color", "#7a0000"),
        ]]

        with open(self.company_info_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(info_rows)

        contacts_rows = [["Contact Name", "Position", "Email", "Phone", "Default"]]
        for contact_name, position, email, phone, is_default in self.company_contacts:
            contacts_rows.append([
                contact_name,
                position,
                email,
                phone,
                'True' if is_default else 'False',
            ])
        with open(self.company_contacts_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(contacts_rows)

        self.changes_made = False


class CustomerWidget(QWidget):
    """Custom widget for managing customers with contact information and bid/project tracking."""
    
    def __init__(self, parent=None, data_path: Optional[Path] = None):
        super().__init__(parent)
        self.current_customer = None
        self.changes_made = False
        self.data_path = Path(data_path) if data_path is not None else (Path(__file__).resolve().parent.parent / "data")
        self.customers_info = {}  # {customer_name: {'address': '', 'phone': '', 'website': '', 'email': ''}}
        self.customers_contacts = {}  # {customer_name: [(contact_name, position, email, phone, is_default), ...]}
        
        self.setup_ui()
        self.load_customers_data()
    
    def setup_ui(self):
        """Setup the UI layout with customer list and details."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL: Customer list with search
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        customer_label = QLabel("Customers")
        customer_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search customers...")
        self.search_box.textChanged.connect(self.filter_customers)
        
        # Button layout for customers
        customer_button_layout = QHBoxLayout()
        add_customer_button = QPushButton("Add")
        add_customer_button.setMaximumWidth(70)
        add_customer_button.clicked.connect(self.add_new_customer)
        
        del_customer_button = QPushButton("Delete")
        del_customer_button.setMaximumWidth(70)
        del_customer_button.clicked.connect(self.delete_current_customer)
        
        customer_button_layout.addWidget(add_customer_button)
        customer_button_layout.addWidget(del_customer_button)
        customer_button_layout.addStretch()
        
        self.customers_list = QListWidget()
        self.customers_list.setMinimumWidth(200)
        self.customers_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.customers_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.customers_list.itemSelectionChanged.connect(self.on_customer_selected)
        
        left_layout.addWidget(customer_label)
        left_layout.addWidget(self.search_box)
        left_layout.addLayout(customer_button_layout)
        left_layout.addWidget(self.customers_list)
        
        # RIGHT PANEL: Customer details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        details_label = QLabel("Customer Details")
        details_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Customer name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Customer Name:")
        self.customer_name_field = QLineEdit()
        self.customer_name_field.setPlaceholderText("Enter customer name...")
        self.customer_name_field.textChanged.connect(self.on_customer_name_changed)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.customer_name_field)
        
        # Customer information fields
        info_label = QLabel("Customer Information")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        
        info_form = QFormLayout()
        info_form.setSpacing(8)
        
        self.customer_address_field = QLineEdit()
        self.customer_address_field.setPlaceholderText("Street address...")
        self.customer_address_field.textChanged.connect(self.on_customer_info_changed)
        
        self.customer_phone_field = QLineEdit()
        self.customer_phone_field.setPlaceholderText("Main phone number...")
        self.customer_phone_field.textChanged.connect(self.on_customer_info_changed)
        
        self.customer_website_field = QLineEdit()
        self.customer_website_field.setPlaceholderText("https://...")
        self.customer_website_field.textChanged.connect(self.on_customer_info_changed)
        
        self.customer_email_field = QLineEdit()
        self.customer_email_field.setPlaceholderText("general@customer.com")
        self.customer_email_field.textChanged.connect(self.on_customer_info_changed)
        
        info_form.addRow("Address:", self.customer_address_field)
        info_form.addRow("Phone:", self.customer_phone_field)
        info_form.addRow("Website:", self.customer_website_field)
        info_form.addRow("Email:", self.customer_email_field)
        
        # Contacts section
        contacts_label = QLabel("Contacts")
        contacts_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        
        # Button layout for contacts
        contacts_button_layout = QHBoxLayout()
        add_contact_button = QPushButton("Add Contact")
        add_contact_button.setMaximumWidth(120)
        add_contact_button.clicked.connect(self.add_new_contact)
        
        del_contact_button = QPushButton("Delete")
        del_contact_button.setMaximumWidth(70)
        del_contact_button.clicked.connect(self.delete_selected_contact)
        
        contacts_button_layout.addWidget(add_contact_button)
        contacts_button_layout.addWidget(del_contact_button)
        contacts_button_layout.addStretch()
        
        self.contacts_table = NoRowHeaderTable()
        self.contacts_table.setColumnCount(5)
        self.contacts_table.setHorizontalHeaderLabels(["Default", "Name", "Position", "Email", "Phone"])
        _ct_hdr = self.contacts_table.horizontalHeader()
        assert _ct_hdr is not None
        _ct_hdr.setStretchLastSection(True)
        self.contacts_table.setColumnWidth(0, 60)  # Default checkbox column
        self.contacts_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.contacts_table.setStyleSheet("""
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
        self.contacts_table.itemChanged.connect(self.on_contact_changed)
        self.contacts_table.cellClicked.connect(self.on_contact_cell_clicked)
        
        # Bids section
        bids_projects_label = QLabel("Bids")
        bids_projects_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        
        self.bids_projects_table = NoRowHeaderTable()
        self.bids_projects_table.setColumnCount(5)
        self.bids_projects_table.setHorizontalHeaderLabels(["Name", "Type", "Status", "Active Value", "Opening Count"])
        _bp_hdr = self.bids_projects_table.horizontalHeader()
        assert _bp_hdr is not None
        _bp_hdr.setStretchLastSection(True)
        self.bids_projects_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.bids_projects_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.bids_projects_table.setStyleSheet("""
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
        
        right_layout.addWidget(details_label)
        right_layout.addLayout(name_layout)
        right_layout.addWidget(info_label)
        right_layout.addLayout(info_form)
        right_layout.addWidget(contacts_label)
        right_layout.addLayout(contacts_button_layout)
        right_layout.addWidget(self.contacts_table)
        right_layout.addWidget(bids_projects_label)
        right_layout.addWidget(self.bids_projects_table)
        
        # Add panels to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def load_customers_data(self):
        """Load customers data from CSV files."""
        data_path = self.data_path
        
        # Load customers info
        customers_info_path = data_path / "customers_info.csv"
        if customers_info_path.exists():
            try:
                with open(customers_info_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    for row in reader:
                        if len(row) >= 5:
                            customer_name = row[0].strip()
                            self.customers_info[customer_name] = {
                                'address': row[1].strip(),
                                'phone': row[2].strip(),
                                'website': row[3].strip(),
                                'email': row[4].strip()
                            }
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Could not load customers_info.csv:\n{e}")
        
        # Load customer contacts
        customers_contacts_path = data_path / "customers_contacts.csv"
        if customers_contacts_path.exists():
            try:
                with open(customers_contacts_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    for row in reader:
                        if len(row) >= 6:
                            customer_name = row[0].strip()
                            contact_name = row[1].strip()
                            position = row[2].strip()
                            email = row[3].strip()
                            phone = row[4].strip()
                            is_default = row[5].strip().lower() == 'true'
                            
                            if customer_name not in self.customers_contacts:
                                self.customers_contacts[customer_name] = []
                            self.customers_contacts[customer_name].append(
                                (contact_name, position, email, phone, is_default)
                            )
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Could not load customers_contacts.csv:\n{e}")
        
        # Populate customer list
        self.populate_customer_list()
    
    def populate_customer_list(self):
        """Populate the customer list widget."""
        self.customers_list.clear()
        for customer_name in sorted(self.customers_info.keys()):
            self.customers_list.addItem(customer_name)
    
    def filter_customers(self, search_text):
        """Filter customers based on search text."""
        search_text = search_text.lower()
        for i in range(self.customers_list.count()):
            item = self.customers_list.item(i)
            if item is None:
                continue
            customer_name = item.text().lower()
            item.setHidden(search_text not in customer_name)
    
    def on_customer_selected(self):
        """Handle customer selection."""
        selected_items = self.customers_list.selectedItems()
        if not selected_items:
            self.current_customer = None
            self.clear_customer_details()
            return
        
        self.current_customer = selected_items[0].text()
        self.load_customer_details()
    
    def clear_customer_details(self):
        """Clear all customer detail fields."""
        self.customer_name_field.blockSignals(True)
        self.customer_address_field.blockSignals(True)
        self.customer_phone_field.blockSignals(True)
        self.customer_website_field.blockSignals(True)
        self.customer_email_field.blockSignals(True)
        
        self.customer_name_field.clear()
        self.customer_address_field.clear()
        self.customer_phone_field.clear()
        self.customer_website_field.clear()
        self.customer_email_field.clear()
        
        self.customer_name_field.blockSignals(False)
        self.customer_address_field.blockSignals(False)
        self.customer_phone_field.blockSignals(False)
        self.customer_website_field.blockSignals(False)
        self.customer_email_field.blockSignals(False)
        
        self.contacts_table.setRowCount(0)
        self.bids_projects_table.setRowCount(0)
    
    def load_customer_details(self):
        """Load details for the current customer."""
        if not self.current_customer:
            return
        
        # Block signals to prevent marking as changed
        self.customer_name_field.blockSignals(True)
        self.customer_address_field.blockSignals(True)
        self.customer_phone_field.blockSignals(True)
        self.customer_website_field.blockSignals(True)
        self.customer_email_field.blockSignals(True)
        
        # Load customer info
        info = self.customers_info.get(self.current_customer, {})
        self.customer_name_field.setText(self.current_customer)
        self.customer_address_field.setText(info.get('address', ''))
        self.customer_phone_field.setText(info.get('phone', ''))
        self.customer_website_field.setText(info.get('website', ''))
        self.customer_email_field.setText(info.get('email', ''))
        
        # Unblock signals
        self.customer_name_field.blockSignals(False)
        self.customer_address_field.blockSignals(False)
        self.customer_phone_field.blockSignals(False)
        self.customer_website_field.blockSignals(False)
        self.customer_email_field.blockSignals(False)
        
        # Load contacts
        self.load_customer_contacts()
        
        # Load bids
        self.load_customer_bids_projects()
    
    def load_customer_contacts(self):
        """Load contacts for the current customer."""
        self.contacts_table.blockSignals(True)
        self.contacts_table.setRowCount(0)
        
        contacts = self.customers_contacts.get(self.current_customer, [])
        for contact_name, position, email, phone, is_default in contacts:
            row = self.contacts_table.rowCount()
            self.contacts_table.insertRow(row)
            
            # Default checkbox
            default_item = QTableWidgetItem()
            default_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            default_item.setCheckState(Qt.CheckState.Checked if is_default else Qt.CheckState.Unchecked)
            self.contacts_table.setItem(row, 0, default_item)
            
            # Contact details
            self.contacts_table.setItem(row, 1, QTableWidgetItem(contact_name))
            self.contacts_table.setItem(row, 2, QTableWidgetItem(position))
            self.contacts_table.setItem(row, 3, QTableWidgetItem(email))
            self.contacts_table.setItem(row, 4, QTableWidgetItem(phone))
        
        self.contacts_table.blockSignals(False)
    
    def load_customer_bids_projects(self):
        """Load bids for the current customer."""
        if not self.current_customer:
            return
        
        self.bids_projects_table.setRowCount(0)
        
        # Get all bids
        from core.models import list_bids, read_info
        
        all_items = []
        current_customer_stripped = self.current_customer.strip()
        
        # Load bids
        try:
            bids_root = self.data_path / "bids"
            bids = list_bids(bids_root)
            for bid_path in bids:
                bid_name = bid_path.name
                info = read_info(bid_path)
                raw_gcs = info.get("gcs", [])
                bid_gcs = [str(x).strip() for x in raw_gcs] if isinstance(raw_gcs, list) else []
                if not bid_gcs:
                    gc_legacy = str(info.get("gc", "")).strip()
                    if gc_legacy:
                        bid_gcs = [gc_legacy]
                if current_customer_stripped in bid_gcs:
                    all_items.append((bid_name, info, bid_path))
        except Exception:
            pass
        
        # Populate table
        for item_name, info, item_path in all_items:
            row = self.bids_projects_table.rowCount()
            self.bids_projects_table.insertRow(row)
            
            # Name
            self.bids_projects_table.setItem(row, 0, QTableWidgetItem(item_name))
            
            # Type (Proposal/Budget)
            proposal_type = info.get("proposal_type", "")
            self.bids_projects_table.setItem(row, 1, QTableWidgetItem(proposal_type))
            
            # Status
            status = info.get("status", "")
            self.bids_projects_table.setItem(row, 2, QTableWidgetItem(status))
            
            # Active Workbook Value
            active_value = self._get_active_workbook_value(item_path, info)
            value_str = f"${active_value:,.2f}" if active_value is not None else ""
            self.bids_projects_table.setItem(row, 3, QTableWidgetItem(value_str))
            
            # Opening Count
            opening_count = self._get_opening_count(item_path, info)
            count_str = str(opening_count) if opening_count is not None else ""
            self.bids_projects_table.setItem(row, 4, QTableWidgetItem(count_str))
    
    def _get_active_workbook_value(self, item_path, info):
        """Get the active workbook total value.
        
        Note: To properly calculate bid totals, the actual Excel workbook 
        would need to be opened and evaluated. For now, this returns the 
        stored value from info.json if available.
        """
        try:
            # Check if bid_total is stored in info.json (preferred method)
            bid_total = info.get("bid_total", None)
            if bid_total is not None:
                try:
                    return float(bid_total)
                except (ValueError, TypeError):
                    pass
            
            # Otherwise return None (will show as empty in the table)
            return None
        except Exception:
            return None
    
    def _get_opening_count(self, item_path, info):
        """Get the count of openings from Schedule.csv."""
        try:
            active_workbook = info.get("active_workbook", "")
            if not active_workbook:
                return None
            
            workbook_path = item_path / active_workbook
            if not workbook_path.exists():
                return None
            
            # Read Schedule.csv
            schedule_path = workbook_path / "Schedule.csv"
            if not schedule_path.exists():
                return None
            
            with open(schedule_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                count = sum(1 for row in reader if row and any(cell.strip() for cell in row))
                return count
        except Exception:
            return None
    
    def on_customer_name_changed(self):
        """Handle customer name change."""
        if not self.current_customer:
            return
        
        new_name = self.customer_name_field.text().strip()
        if new_name and new_name != self.current_customer:
            # Rename customer
            if new_name in self.customers_info:
                QMessageBox.warning(self, "Duplicate Name", "A customer with this name already exists.")
                self.customer_name_field.blockSignals(True)
                self.customer_name_field.setText(self.current_customer)
                self.customer_name_field.blockSignals(False)
                return
            
            # Update data structures
            self.customers_info[new_name] = self.customers_info.pop(self.current_customer)
            if self.current_customer in self.customers_contacts:
                self.customers_contacts[new_name] = self.customers_contacts.pop(self.current_customer)
            
            # Update list
            old_name = self.current_customer
            self.current_customer = new_name
            self.populate_customer_list()
            
            # Reselect new name
            items = self.customers_list.findItems(new_name, Qt.MatchFlag.MatchExactly)
            if items:
                self.customers_list.setCurrentItem(items[0])
            
            self.changes_made = True
    
    def on_customer_info_changed(self):
        """Handle change to customer info fields."""
        if not self.current_customer:
            return
        
        # Update customer info
        if self.current_customer in self.customers_info:
            self.customers_info[self.current_customer] = {
                'address': self.customer_address_field.text().strip(),
                'phone': self.customer_phone_field.text().strip(),
                'website': self.customer_website_field.text().strip(),
                'email': self.customer_email_field.text().strip()
            }
            self.changes_made = True
    
    def add_new_customer(self):
        """Add a new customer."""
        # Generate unique name
        base_name = "New Customer"
        name = base_name
        counter = 1
        while name in self.customers_info:
            name = f"{base_name} {counter}"
            counter += 1
        
        # Add to data
        self.customers_info[name] = {'address': '', 'phone': '', 'website': '', 'email': ''}
        self.customers_contacts[name] = []
        
        # Update list
        self.populate_customer_list()
        
        # Select new customer
        items = self.customers_list.findItems(name, Qt.MatchFlag.MatchExactly)
        if items:
            self.customers_list.setCurrentItem(items[0])
        
        self.changes_made = True
    
    def delete_current_customer(self):
        """Delete the currently selected customer."""
        if not self.current_customer:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Customer",
            f"Are you sure you want to delete customer '{self.current_customer}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from data
            self.customers_info.pop(self.current_customer, None)
            self.customers_contacts.pop(self.current_customer, None)
            
            # Update list
            self.current_customer = None
            self.populate_customer_list()
            self.clear_customer_details()
            
            self.changes_made = True
    
    def add_new_contact(self):
        """Add a new contact for the current customer."""
        if not self.current_customer:
            return
        
        row = self.contacts_table.rowCount()
        self.contacts_table.insertRow(row)
        
        # Default checkbox
        default_item = QTableWidgetItem()
        default_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        default_item.setCheckState(Qt.CheckState.Unchecked)
        self.contacts_table.setItem(row, 0, default_item)
        
        # Empty contact fields
        for col in range(1, 5):
            self.contacts_table.setItem(row, col, QTableWidgetItem(""))
        
        self.changes_made = True
    
    def delete_selected_contact(self):
        """Delete the currently selected contact."""
        current_row = self.contacts_table.currentRow()
        if current_row >= 0:
            self.contacts_table.removeRow(current_row)
            self.update_customer_contacts_from_table()
            self.changes_made = True
    
    def on_contact_changed(self, item):
        """Handle contact table item change."""
        self.update_customer_contacts_from_table()
        self.changes_made = True
    
    def on_contact_cell_clicked(self, row, col):
        """Handle contact cell click (for default checkbox)."""
        if col == 0:  # Default checkbox column
            # Uncheck all others if this one is being checked
            item = self.contacts_table.item(row, col)
            if item and item.checkState() == Qt.CheckState.Checked:
                for r in range(self.contacts_table.rowCount()):
                    if r != row:
                        other_item = self.contacts_table.item(r, 0)
                        if other_item:
                            other_item.setCheckState(Qt.CheckState.Unchecked)
            self.update_customer_contacts_from_table()
            self.changes_made = True
    
    def update_customer_contacts_from_table(self):
        """Update customer contacts data from table."""
        if not self.current_customer:
            return
        
        contacts = []
        for row in range(self.contacts_table.rowCount()):
            default_item = self.contacts_table.item(row, 0)
            name_item = self.contacts_table.item(row, 1)
            position_item = self.contacts_table.item(row, 2)
            email_item = self.contacts_table.item(row, 3)
            phone_item = self.contacts_table.item(row, 4)
            
            is_default = default_item.checkState() == Qt.CheckState.Checked if default_item else False
            name = name_item.text().strip() if name_item else ""
            position = position_item.text().strip() if position_item else ""
            email = email_item.text().strip() if email_item else ""
            phone = phone_item.text().strip() if phone_item else ""
            
            contacts.append((name, position, email, phone, is_default))
        
        self.customers_contacts[self.current_customer] = contacts
    
    def save_to_csv(self):
        """Save customers data to CSV files."""
        data_path = self.data_path
        data_path.mkdir(exist_ok=True)
        
        # Save customer info
        customers_info_path = data_path / "customers_info.csv"
        info_rows = [["Customer Name", "Address", "Phone", "Website", "Email"]]
        for customer_name in sorted(self.customers_info.keys()):
            info = self.customers_info[customer_name]
            info_rows.append([
                customer_name,
                info.get('address', ''),
                info.get('phone', ''),
                info.get('website', ''),
                info.get('email', '')
            ])
        
        try:
            with open(customers_info_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(info_rows)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save customers_info.csv:\n{e}")
            return
        
        # Save customer contacts
        customers_contacts_path = data_path / "customers_contacts.csv"
        contacts_rows = [["Customer Name", "Contact Name", "Position", "Email", "Phone", "Default"]]
        for customer_name in sorted(self.customers_contacts.keys()):
            contacts = self.customers_contacts[customer_name]
            if contacts:
                for contact_name, position, email, phone, is_default in contacts:
                    contacts_rows.append([
                        customer_name,
                        contact_name,
                        position,
                        email,
                        phone,
                        'True' if is_default else 'False'
                    ])
        
        try:
            with open(customers_contacts_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(contacts_rows)
            self.changes_made = False
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save customers_contacts.csv:\n{e}")



