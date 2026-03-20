from pathlib import Path
from typing import Callable, List, Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .main_window_ui_helpers import QMessageBox


class SendToAlternateDialog(QDialog):
    """Dialog for sending selected schedule openings to an alternate."""

    def __init__(self, existing_alternates, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send to Alternate")
        self.setMinimumWidth(400)
        self.existing_alternates = sorted(existing_alternates)
        self.selected_alternate = None
        self.remove_from_schedule = False

        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        alt_layout = QHBoxLayout()
        alt_label = QLabel("Alternate Number:")

        self.alt_combo = QComboBox()
        self.alt_combo.setEditable(True)
        self.alt_combo.addItem("")
        for alt_num in self.existing_alternates:
            self.alt_combo.addItem(alt_num)

        alt_layout.addWidget(alt_label)
        alt_layout.addWidget(self.alt_combo)
        layout.addLayout(alt_layout)

        self.remove_checkbox = QCheckBox("Remove selected openings from Schedule")
        layout.addWidget(self.remove_checkbox)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Send")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def get_result(self):
        """Get the selected alternate and remove flag."""
        alt_num = self.alt_combo.currentText().strip()
        if not alt_num:
            QMessageBox.warning(self, "Invalid Input", "Please enter or select an alternate number.")
            return None, False

        return alt_num, self.remove_checkbox.isChecked()


class ScheduleBreakoutDialog(QDialog):
    """Dialog for selecting primary and secondary breakout headers."""

    def __init__(self, schedule_headers: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Breakouts")
        self.setMinimumWidth(420)

        self._headers = [str(h).strip() for h in schedule_headers if str(h).strip()]
        self.primary_header: Optional[str] = None
        self.secondary_header: Optional[str] = None

        layout = QVBoxLayout(self)

        info_label = QLabel("Select a primary breakout and optional secondary breakout.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form = QFormLayout()
        self.primary_combo = QComboBox()
        self.primary_combo.addItems(self._headers)
        form.addRow("Primary breakout:", self.primary_combo)

        self.secondary_combo = QComboBox()
        self.secondary_combo.addItem("(None)")
        self.secondary_combo.addItems(self._headers)
        form.addRow("Secondary breakout:", self.secondary_combo)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        primary = self.primary_combo.currentText().strip()
        secondary = self.secondary_combo.currentText().strip()

        if not primary:
            QMessageBox.warning(self, "Breakouts", "Please select a primary breakout header.")
            return

        if secondary == "(None)":
            secondary = ""

        if secondary and secondary.lower() == primary.lower():
            QMessageBox.warning(self, "Breakouts", "Primary and secondary breakouts must be different.")
            return

        self.primary_header = primary
        self.secondary_header = secondary or None
        self.accept()

    def get_selection(self) -> Tuple[Optional[str], Optional[str]]:
        return self.primary_header, self.secondary_header


class DetailsPopupWindow(QDialog):
    """Detached popup window showing bid details."""

    def __init__(
        self,
        details_widget: QWidget,
        parent=None,
        close_guard: Optional[Callable[[], bool]] = None,
        title: str = "Bid Details",
    ):
        super().__init__(parent)
        self._close_guard = close_guard
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(details_widget)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def closeEvent(self, event):
        if self._close_guard and not self._close_guard():
            event.ignore()
            return
        event.accept()


class VendorsDialog(QDialog):
    """Dialog for managing vendors and their contacts."""

    def __init__(self, parent=None, data_path: Optional[Path] = None, vendors_widget_cls=None):
        super().__init__(parent)
        if vendors_widget_cls is None:
            raise ValueError("vendors_widget_cls is required")

        self.setWindowTitle("Vendors Management")
        self.setMinimumSize(800, 400)

        self.vendors_widget = vendors_widget_cls(self, data_path=data_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vendors_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def save_and_close(self):
        """Save changes and close."""
        self.vendors_widget.save_to_csv()
        QMessageBox.information(self, "Saved", "Vendors data saved successfully.")
        self.accept()

    def closeEvent(self, event):
        """Handle close event - check for unsaved changes."""
        if self.vendors_widget.changes_made:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if reply == QMessageBox.StandardButton.Save:
                self.vendors_widget.save_to_csv()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()


class CustomerDialog(QDialog):
    """Dialog for managing customers and their contacts."""

    def __init__(
        self,
        parent=None,
        data_path: Optional[Path] = None,
        initial_customer: str = "",
        start_add_contact: bool = False,
        customer_widget_cls=None,
    ):
        super().__init__(parent)
        if customer_widget_cls is None:
            raise ValueError("customer_widget_cls is required")

        self.setWindowTitle("Customers Management")
        self.setMinimumSize(900, 500)

        self.customer_widget = customer_widget_cls(self, data_path=data_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.customer_widget)

        initial_customer = initial_customer.strip()
        if initial_customer:
            self._select_initial_customer(initial_customer)
        if start_add_contact:
            self._prepare_add_contact_mode(initial_customer)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _select_initial_customer(self, customer_name: str):
        items = self.customer_widget.customers_list.findItems(customer_name, Qt.MatchFlag.MatchFixedString)
        if items:
            self.customer_widget.customers_list.setCurrentItem(items[0])
            self.customer_widget.customers_list.scrollToItem(items[0])

    def _prepare_add_contact_mode(self, customer_name: str):
        target = customer_name.strip()
        if not target:
            return

        items = self.customer_widget.customers_list.findItems(target, Qt.MatchFlag.MatchFixedString)
        if not items:
            self.customer_widget.customers_info[target] = {"address": "", "phone": "", "website": "", "email": ""}
            self.customer_widget.customers_contacts[target] = []
            self.customer_widget.populate_customer_list()
            items = self.customer_widget.customers_list.findItems(target, Qt.MatchFlag.MatchFixedString)

        if items:
            self.customer_widget.customers_list.setCurrentItem(items[0])
            self.customer_widget.customers_list.scrollToItem(items[0])

        self.customer_widget.add_new_contact()
        row = self.customer_widget.contacts_table.rowCount() - 1
        if row >= 0:
            self.customer_widget.contacts_table.setCurrentCell(row, 1)
            self.customer_widget.contacts_table.editItem(self.customer_widget.contacts_table.item(row, 1))

    def save_and_close(self):
        """Save changes and close."""
        self.customer_widget.save_to_csv()
        QMessageBox.information(self, "Saved", "Customers data saved successfully.")
        self.accept()

    def closeEvent(self, event):
        """Handle close event - check for unsaved changes."""
        if self.customer_widget.changes_made:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if reply == QMessageBox.StandardButton.Save:
                self.customer_widget.save_to_csv()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()


class MyCompanyDialog(QDialog):
    """Dialog for managing company info, contacts, and staff lists."""

    def __init__(self, parent=None, data_path: Optional[Path] = None, company_widget_cls=None):
        super().__init__(parent)
        if company_widget_cls is None:
            raise ValueError("company_widget_cls is required")

        self.setWindowTitle("My Company")
        self.setMinimumSize(900, 650)

        self.company_widget = company_widget_cls(self, data_path=data_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.company_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def save_and_close(self):
        self.company_widget.save_to_csv()
        QMessageBox.information(self, "Saved", "My Company data saved successfully.")
        self.accept()

    def closeEvent(self, event):
        if self.company_widget.changes_made:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if reply == QMessageBox.StandardButton.Save:
                self.company_widget.save_to_csv()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()

