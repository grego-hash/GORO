"""Category-aware Prep Code combo-box delegate for the hardware table.

When a cell in the Prep Code column is edited, reads the Category value
from the same row and shows only the matching prep codes in the dropdown.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from core.prep_codes import PrepCodeDB


class PrepCodeDelegate(QStyledItemDelegate):
    """Editable combo that filters prep codes by the row's Category value."""

    def __init__(
        self,
        db: PrepCodeDB,
        category_col: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._db = db
        self._category_col = category_col

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        combo = QComboBox(parent)
        combo.setEditable(True)

        # Read the Category value from the same row
        model = index.model()
        cat_value = ""
        if model is not None:
            cat_index = model.index(index.row(), self._category_col)
            cat_value = str(cat_index.data(Qt.ItemDataRole.DisplayRole) or "").strip()

        codes = self._db.codes_for_category(cat_value) if cat_value else []
        combo.addItems(codes)
        combo.setCurrentIndex(-1)
        line_edit = combo.lineEdit()
        if line_edit is not None:
            line_edit.clear()
        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        if isinstance(editor, QComboBox):
            if not index.isValid():
                return
            value = index.data(Qt.ItemDataRole.EditRole)
            if value:
                editor.setCurrentText(str(value))
            else:
                editor.setCurrentIndex(-1)
                line_edit = editor.lineEdit()
                if line_edit is not None:
                    line_edit.clear()

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        if isinstance(editor, QComboBox):
            if not index.isValid():
                return
            if index.row() < 0 or index.column() < 0:
                return
            if index.row() >= model.rowCount(index.parent()):
                return
            if index.column() >= model.columnCount(index.parent()):
                return
            model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        editor.setGeometry(option.rect)
