"""Reusable table delegates and views for GORO UI."""

from typing import List, Optional

from PyQt6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QObject, QRect, Qt
from PyQt6.QtGui import QColor, QKeySequence, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHeaderView,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class ComboBoxDelegate(QStyledItemDelegate):
    """Custom delegate that shows an editable combo box for table cells."""

    def __init__(self, items: List[str], parent: Optional[QWidget] = None, editable: bool = False):
        super().__init__(parent)
        self.items = items
        self.editable = editable

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        combo = QComboBox(parent)
        combo.setEditable(self.editable)
        combo.addItems(self.items)
        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        if isinstance(editor, QComboBox):
            if not index.isValid():
                return
            value = index.data(Qt.ItemDataRole.EditRole)
            if value:
                editor.setCurrentText(str(value))

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


class VerticalHeaderView(QHeaderView):
    """Custom header view that displays text vertically."""

    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int) -> None:
        painter.save()
        painter.fillRect(rect, self.palette().button())
        painter.setPen(QPen(self.palette().mid().color()))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

        model = self.model()
        text = model.headerData(logicalIndex, self.orientation(), Qt.ItemDataRole.DisplayRole) if model else ""
        if text:
            painter.translate(rect.x() + rect.width() / 2, rect.y() + rect.height() - 5)
            painter.rotate(-90)
            painter.setPen(self.palette().text().color())
            painter.drawText(0, 0, str(text))

        painter.restore()


class NoRowHeaderTable(QTableWidget):
    """QTableWidget that hides row numbers by default."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.verticalHeader().setVisible(False)


class HardwarePasteEventFilter(QObject):
    """Event filter that enables multi-row/column paste in the hardware table."""

    def __init__(
        self,
        table,
        checkbox_cols=None,
        skip_cols=None,
        readonly_cols=None,
        change_callback=None,
        ensure_row_callback=None,
    ):
        super().__init__(table)
        self.table = table
        self.checkbox_cols = set(checkbox_cols or [])
        self.skip_cols = set(skip_cols or [])
        self.readonly_cols = set(readonly_cols or [])
        self.change_callback = change_callback
        self.ensure_row_callback = ensure_row_callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.matches(QKeySequence.StandardKey.Paste):
                self.handle_paste()
                return True
        return super().eventFilter(obj, event)

    def handle_paste(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return

        lines = text.split("\n")
        if lines and not lines[-1].strip():
            lines = lines[:-1]
        if not lines:
            return

        selected = self.table.selectedRanges()
        if not selected:
            start_row = 0
            start_col = 1
        else:
            start_row = selected[0].topRow()
            start_col = selected[0].leftColumn()
            if start_col == 0:
                start_col = 1

        selection_width = 1
        if selected:
            selection_width = max(1, selected[0].rightColumn() - selected[0].leftColumn() + 1)

        raw_rows = [line.rstrip("\r").split("\t") for line in lines]
        expected_width = max((len(row) for row in raw_rows), default=1)
        if selection_width > 1:
            expected_width = max(expected_width, selection_width)

        paste_data = []
        for row in raw_rows:
            normalized_row = list(row)
            if len(normalized_row) < expected_width:
                normalized_row.extend([""] * (expected_width - len(normalized_row)))
            paste_data.append(normalized_row)

        rows_needed = start_row + len(paste_data)
        if rows_needed > self.table.rowCount():
            self.table.blockSignals(True)
            self.table.setRowCount(rows_needed + 1)
            self.table.blockSignals(False)

        self.table.blockSignals(True)
        for row_offset, row_data in enumerate(paste_data):
            target_row = start_row + row_offset

            checkbox_item = self.table.item(target_row, 0)
            if checkbox_item is None:
                checkbox_item = QTableWidgetItem("")
                checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                checkbox_item.setText("")
                self.table.setItem(target_row, 0, checkbox_item)

            for col_offset, cell_value in enumerate(row_data):
                target_col = start_col + col_offset
                if target_col >= self.table.columnCount():
                    break
                if target_col in self.skip_cols:
                    continue

                item = self.table.item(target_row, target_col)
                if item is None:
                    item = QTableWidgetItem("")
                    self.table.setItem(target_row, target_col, item)

                if target_col in self.checkbox_cols:
                    value = cell_value.strip().lower()
                    checked = value in ("yes", "x", "1", "true", "checked")
                    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
                    item.setText("")
                elif target_col in self.readonly_cols:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setBackground(QColor(60, 60, 60))
                    item.setForeground(QColor(200, 200, 200))
                    item.setText(cell_value)
                else:
                    item.setFlags(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setText(cell_value)
        self.table.blockSignals(False)

        if self.change_callback:
            self.change_callback()
        if self.ensure_row_callback:
            self.ensure_row_callback()

