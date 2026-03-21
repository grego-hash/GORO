"""Milestone management dialogs for GORO 1.0."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QInputDialog, QSplitter, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.utils import clamped_size

from core.milestones import (
    Milestone, list_milestones, create_milestone, delete_milestone,
    revert_to_milestone, copy_milestone_to_new_workbook, compare_workbooks
)


class CreateMilestoneDialog(QDialog):
    """Dialog for creating a new milestone."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Milestone")
        self.setMinimumWidth(400)
        
        # Milestone name
        layout = QVBoxLayout(self)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Milestone Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., 'Initial Draft', 'Final Review'")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Description
        layout.addWidget(QLabel("Description (optional):"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Add notes about this milestone...")
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton("Create")
        self.btn_cancel = QPushButton("Cancel")
        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        self.btn_create.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
    
    def get_data(self) -> tuple:
        """Return (name, description)."""
        return self.name_edit.text().strip(), self.desc_edit.toPlainText().strip()


class MilestoneCompareDialog(QDialog):
    """Dialog showing comparison results between workbook and milestone."""
    
    def __init__(self, changes: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workbook Comparison")
        self.setMinimumSize(*clamped_size(900, 700))
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>Summary of all changes between current workbook and milestone:</b>"))
        
        # Store changes for later reference
        self.changes = changes
        
        # Create main details table showing ALL changes
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(5)
        self.details_table.setHorizontalHeaderLabels(["File", "Item", "Field", "Old Value", "New Value"])
        self.details_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.details_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.details_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.details_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.details_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Populate with all changes
        self._populate_all_changes()
        
        layout.addWidget(self.details_table)
        
        # Summary - show only data changes
        total_changes = self.details_table.rowCount()
        num_files_modified = len(changes.get('csv_details', {}))
        summary_lines = [
            f"Total Data Changes: {total_changes}",
            f"Files Modified: {num_files_modified}"
        ]
        summary = QLabel(" | ".join(summary_lines))
        summary.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 4px;")
        layout.addWidget(summary)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
    
    def _populate_all_changes(self):
        """Populate the table with all changes from all files."""
        csv_details = self.changes.get('csv_details', {})
        
        # Process each file with CSV details
        for file_path, details in sorted(csv_details.items()):
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1] if '\\' in file_path else file_path
            # Remove .csv extension
            if file_name.lower().endswith('.csv'):
                file_name = file_name[:-4]
            
            # Modified rows
            for row_info in details.get('modified_rows', []):
                row_id = row_info.get('row_identifier')
                row_idx = row_info['row_index']
                
                # Use identifier if available, otherwise use row number
                item_label = row_id if row_id else f"Row {row_idx}"
                
                changes = row_info['changes']
                for change in changes:
                    detail_row = self.details_table.rowCount()
                    self.details_table.setRowCount(detail_row + 1)
                    
                    # File name
                    file_item = QTableWidgetItem(file_name)
                    file_item.setForeground(QColor(100, 100, 100))
                    self.details_table.setItem(detail_row, 0, file_item)
                    
                    # Item identifier (Opening, Door Type, etc.)
                    item_item = QTableWidgetItem(item_label)
                    item_item.setForeground(QColor(0, 100, 200))
                    self.details_table.setItem(detail_row, 1, item_item)
                    
                    # Field name
                    field_item = QTableWidgetItem(change['field'])
                    self.details_table.setItem(detail_row, 2, field_item)
                    
                    # Old value
                    old_item = QTableWidgetItem(change['old_value'])
                    old_item.setBackground(QColor(255, 230, 230))
                    self.details_table.setItem(detail_row, 3, old_item)
                    
                    # New value
                    new_item = QTableWidgetItem(change['new_value'])
                    new_item.setBackground(QColor(230, 255, 230))
                    self.details_table.setItem(detail_row, 4, new_item)
            
            # Added rows
            for row_data in details.get('added_rows', []):
                detail_row = self.details_table.rowCount()
                self.details_table.setRowCount(detail_row + 1)
                
                row_id = row_data.get('identifier')
                row_idx = row_data.get('index')
                item_label = row_id if row_id else f"Row {row_idx}"
                
                file_item = QTableWidgetItem(file_name)
                file_item.setForeground(QColor(100, 100, 100))
                self.details_table.setItem(detail_row, 0, file_item)
                
                item_item = QTableWidgetItem(item_label)
                item_item.setForeground(QColor(0, 150, 0))
                self.details_table.setItem(detail_row, 1, item_item)
                
                msg_item = QTableWidgetItem("ADDED")
                msg_item.setBackground(QColor(200, 255, 200))
                msg_item.setForeground(QColor(0, 150, 0))
                self.details_table.setItem(detail_row, 2, msg_item)
                self.details_table.setSpan(detail_row, 2, 1, 3)
            
            # Removed rows
            for row_data in details.get('removed_rows', []):
                detail_row = self.details_table.rowCount()
                self.details_table.setRowCount(detail_row + 1)
                
                row_id = row_data.get('identifier')
                row_idx = row_data.get('index')
                item_label = row_id if row_id else f"Row {row_idx}"
                
                file_item = QTableWidgetItem(file_name)
                file_item.setForeground(QColor(100, 100, 100))
                self.details_table.setItem(detail_row, 0, file_item)
                
                item_item = QTableWidgetItem(item_label)
                item_item.setForeground(QColor(150, 0, 0))
                self.details_table.setItem(detail_row, 1, item_item)
                
                msg_item = QTableWidgetItem("REMOVED")
                msg_item.setBackground(QColor(255, 230, 230))
                msg_item.setForeground(QColor(150, 0, 0))
                self.details_table.setItem(detail_row, 2, msg_item)
                self.details_table.setSpan(detail_row, 2, 1, 3)
        
        # All CSV data (including from added/removed files) is now in csv_details
        # So we don't need to handle them separately
        
        # If no changes at all
        if self.details_table.rowCount() == 0:
            self.details_table.setRowCount(1)
            msg_item = QTableWidgetItem("No changes detected")
            msg_item.setForeground(QColor(128, 128, 128))
            self.details_table.setItem(0, 0, msg_item)
            self.details_table.setSpan(0, 0, 1, 5)


class ManageMilestonesDialog(QDialog):
    """Dialog for managing milestones of a workbook."""
    
    def __init__(self, workbook_path: Path, workbook_name: str = "", parent=None, view_schedule_callback=None):
        super().__init__(parent)
        self.workbook_path = workbook_path
        self.workbook_name = workbook_name
        self._view_schedule_callback = view_schedule_callback
        self.setWindowTitle(f"Manage Milestones - {workbook_name}")
        self.setMinimumSize(*clamped_size(700, 500))
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Milestones for {workbook_name}:</b>"))
        
        # Splitter for milestones list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Left: Milestones list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.milestones_list = QListWidget()
        self.milestones_list.itemSelectionChanged.connect(self._on_milestone_selected)
        left_layout.addWidget(self.milestones_list)
        
        # Load milestones
        self.milestones = list_milestones(workbook_path)
        for milestone in self.milestones:
            item = QListWidgetItem(milestone.name)
            item.setData(Qt.ItemDataRole.UserRole, milestone)
            self.milestones_list.addItem(item)
        
        if not self.milestones:
            self.milestones_list.addItem(QListWidgetItem("(No milestones)"))
        
        splitter.addWidget(left_widget)
        
        # Right: Milestone details and actions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Details
        right_layout.addWidget(QLabel("<b>Details:</b>"))
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.lbl_name = QLineEdit()
        self.lbl_name.setReadOnly(True)
        name_layout.addWidget(self.lbl_name)
        right_layout.addLayout(name_layout)
        
        # Created
        created_layout = QHBoxLayout()
        created_layout.addWidget(QLabel("Created:"))
        self.lbl_created = QLineEdit()
        self.lbl_created.setReadOnly(True)
        created_layout.addWidget(self.lbl_created)
        right_layout.addLayout(created_layout)
        
        # Description
        right_layout.addWidget(QLabel("Description:"))
        self.lbl_description = QTextEdit()
        self.lbl_description.setReadOnly(True)
        self.lbl_description.setMaximumHeight(100)
        right_layout.addWidget(self.lbl_description)
        
        right_layout.addStretch()
        
        # Actions
        right_layout.addWidget(QLabel("<b>Actions:</b>"))
        
        actions_layout = QVBoxLayout()
        
        self.btn_copy = QPushButton("Copy to New Workbook")
        self.btn_copy.clicked.connect(self._copy_milestone)
        self.btn_copy.setEnabled(False)
        actions_layout.addWidget(self.btn_copy)
        
        self.btn_revert = QPushButton("Revert to This Milestone")
        self.btn_revert.clicked.connect(self._revert_milestone)
        self.btn_revert.setEnabled(False)
        actions_layout.addWidget(self.btn_revert)
        
        self.btn_compare = QPushButton("Compare with Current")
        self.btn_compare.clicked.connect(self._compare_milestone)
        self.btn_compare.setEnabled(False)
        actions_layout.addWidget(self.btn_compare)
        
        self.btn_view = QPushButton("View Milestone (Read-Only)")
        self.btn_view.clicked.connect(self._view_milestone)
        self.btn_view.setEnabled(False)
        actions_layout.addWidget(self.btn_view)
        
        self.btn_delete = QPushButton("Delete Milestone")
        self.btn_delete.setStyleSheet("color: red;")
        self.btn_delete.clicked.connect(self._delete_milestone)
        self.btn_delete.setEnabled(False)
        actions_layout.addWidget(self.btn_delete)
        
        right_layout.addLayout(actions_layout)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
    
    def _on_milestone_selected(self):
        """Handle milestone selection."""
        selected = self.milestones_list.selectedItems()
        if not selected:
            self.lbl_name.clear()
            self.lbl_created.clear()
            self.lbl_description.clear()
            self.btn_copy.setEnabled(False)
            self.btn_revert.setEnabled(False)
            self.btn_compare.setEnabled(False)
            self.btn_view.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return
        
        item = selected[0]
        milestone = item.data(Qt.ItemDataRole.UserRole)
        
        if milestone:
            self.lbl_name.setText(milestone.name)
            if milestone.created:
                try:
                    dt = datetime.fromisoformat(milestone.created.replace('Z', '+00:00'))
                    created_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    created_str = milestone.created
            else:
                created_str = "(Unknown)"
            self.lbl_created.setText(created_str)
            self.lbl_description.setText(milestone.description)
            
            self.btn_copy.setEnabled(True)
            self.btn_revert.setEnabled(True)
            self.btn_compare.setEnabled(True)
            self.btn_view.setEnabled(True)
            self.btn_delete.setEnabled(True)
    
    def _copy_milestone(self):
        """Copy milestone to a new workbook."""
        selected = self.milestones_list.selectedItems()
        if not selected:
            return
        
        milestone = selected[0].data(Qt.ItemDataRole.UserRole)
        if not milestone:
            return
        
        # Ask for new workbook name
        new_name, ok = QInputDialog.getText(
            self,
            "Copy Milestone",
            "Enter name for new workbook:",
            text=f"{self.workbook_name}_copy"
        )
        
        if not ok or not new_name.strip():
            return
        
        # Determine new workbook path
        parent_path = self.workbook_path.parent
        new_workbook_path = parent_path / new_name.strip()
        
        if new_workbook_path.exists():
            QMessageBox.warning(
                self,
                "Copy Milestone",
                f"Workbook '{new_name}' already exists."
            )
            return
        
        # Copy the milestone
        if copy_milestone_to_new_workbook(milestone, new_workbook_path):
            QMessageBox.information(
                self,
                "Copy Milestone",
                f"Milestone copied to new workbook:\n{new_workbook_path.name}"
            )
        else:
            QMessageBox.warning(
                self,
                "Copy Milestone",
                "Failed to copy milestone."
            )
    
    def _revert_milestone(self):
        """Revert workbook to selected milestone."""
        selected = self.milestones_list.selectedItems()
        if not selected:
            return
        
        milestone = selected[0].data(Qt.ItemDataRole.UserRole)
        if not milestone:
            return
        
        # Confirm
        reply = QMessageBox.warning(
            self,
            "Revert to Milestone",
            f"This will replace all current workbook contents with:\n\n'{milestone.name}'\n\nThis cannot be undone. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if revert_to_milestone(self.workbook_path, milestone):
            QMessageBox.information(
                self,
                "Revert to Milestone",
                f"Workbook reverted to '{milestone.name}'.\n\nPlease refresh the workbook in the main window."
            )
        else:
            QMessageBox.warning(
                self,
                "Revert to Milestone",
                "Failed to revert to milestone."
            )
    
    def _compare_milestone(self):
        """Compare current workbook with selected milestone."""
        selected = self.milestones_list.selectedItems()
        if not selected:
            return
        
        milestone = selected[0].data(Qt.ItemDataRole.UserRole)
        if not milestone:
            return
        
        changes = compare_workbooks(self.workbook_path, milestone)
        
        dialog = MilestoneCompareDialog(changes, self)
        dialog.exec()
    
    def _view_milestone(self):
        """Open the milestone for viewing in read-only mode."""
        selected = self.milestones_list.selectedItems()
        if not selected:
            return
        
        milestone = selected[0].data(Qt.ItemDataRole.UserRole)
        if not milestone:
            return
        
        if callable(self._view_schedule_callback):
            self._view_schedule_callback(workbook_path=milestone.milestone_path, read_only=True)
    
    def _delete_milestone(self):
        """Delete selected milestone."""
        selected = self.milestones_list.selectedItems()
        if not selected:
            return
        
        milestone = selected[0].data(Qt.ItemDataRole.UserRole)
        if not milestone:
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Delete Milestone",
            f"Delete milestone '{milestone.name}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if delete_milestone(milestone):
            # Remove from list
            self.milestones_list.takeItem(self.milestones_list.row(selected[0]))
            self.lbl_name.clear()
            self.lbl_created.clear()
            self.lbl_description.clear()
            self.btn_copy.setEnabled(False)
            self.btn_revert.setEnabled(False)
            self.btn_compare.setEnabled(False)
            self.btn_delete.setEnabled(False)
            
            if self.milestones_list.count() == 0:
                self.milestones_list.addItem(QListWidgetItem("(No milestones)"))
            
            QMessageBox.information(
                self,
                "Delete Milestone",
                "Milestone deleted."
            )
        else:
            QMessageBox.warning(
                self,
                "Delete Milestone",
                "Failed to delete milestone."
            )


class ReturnOfflineCopyDialog(QDialog):
    """Dialog for returning an offline working copy to the live record.

    Presents a summary of changed files and offers three actions:
    - Apply Changes to Live Record (prompts for a safety milestone name after closing)
    - Discard Offline Copy (clear flag, no files changed)
    - Cancel (do nothing)
    """

    CHOICE_APPLY = "apply"
    CHOICE_DISCARD = "discard"

    def __init__(self, changes: dict, checkout_info: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Return Offline Copy")
        self.setMinimumSize(640, 460)
        self.choice: Optional[str] = None

        layout = QVBoxLayout(self)

        user = checkout_info.get("offline_checked_out_by", "Unknown")
        started = str(checkout_info.get("offline_checked_out_at", ""))[:10]
        layout.addWidget(QLabel(f"<b>Offline copy created by {user} on {started}</b>"))

        modified = changes.get("modified", [])
        added = changes.get("added", [])
        removed = changes.get("removed", [])
        total = len(modified) + len(added) + len(removed)

        if total == 0:
            layout.addWidget(QLabel("\nNo changes were made in this offline copy."))
        else:
            summary = (
                f"{len(modified)} file(s) modified,  "
                f"{len(added)} file(s) added,  "
                f"{len(removed)} file(s) removed"
            )
            layout.addWidget(QLabel(f"\n<b>Changes detected:</b>  {summary}"))

            self.file_list = QListWidget()
            for f in modified:
                itm = QListWidgetItem(f"\u25CF  Modified    {f}")
                itm.setForeground(QColor("#FFA726"))
                self.file_list.addItem(itm)
            for f in added:
                itm = QListWidgetItem(f"\u25CF  Added       {f}")
                itm.setForeground(QColor("#66BB6A"))
                self.file_list.addItem(itm)
            for f in removed:
                itm = QListWidgetItem(f"\u25CF  Removed     {f}")
                itm.setForeground(QColor("#EF5350"))
                self.file_list.addItem(itm)
            layout.addWidget(self.file_list)

            layout.addWidget(QLabel(
                "\n<i>Applying changes will first prompt you to create a milestone on the live\n"
                "record so you can roll back if needed.</i>"
            ))

        layout.addWidget(QLabel("\nWhat would you like to do?"))

        btn_layout = QHBoxLayout()

        if total > 0:
            self.btn_apply = QPushButton("Apply Changes to Live Record")
            self.btn_apply.clicked.connect(self._apply)
            btn_layout.addWidget(self.btn_apply)

        label = "Clear Offline Flag" if total == 0 else "Discard Offline Copy"
        self.btn_discard = QPushButton(label)
        self.btn_discard.clicked.connect(self._discard)
        btn_layout.addWidget(self.btn_discard)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)
        self._has_changes = total > 0

    def _apply(self):
        self.choice = self.CHOICE_APPLY
        self.accept()

    def _discard(self):
        self.choice = self.CHOICE_DISCARD
        self.accept()

    def has_changes(self) -> bool:
        return self._has_changes

