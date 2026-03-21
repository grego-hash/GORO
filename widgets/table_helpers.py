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
    QTableWidgetSelectionRange,
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
        if self.editable:
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
            elif self.editable:
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

    def keyPressEvent(self, event) -> None:
        if event.matches(QKeySequence.StandardKey.Copy):
            if self.copy_selected_cells_to_clipboard():
                event.accept()
                return
        if (
            event.key() == Qt.Key.Key_D
            and bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        ):
            if self.fill_selection_down():
                event.accept()
                return
        super().keyPressEvent(event)

    def copy_selected_cells_to_clipboard(self) -> bool:
        """Copy the current cell selection as a tab-separated block."""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return False

        blocks: list[str] = []
        for selected_range in selected_ranges:
            lines: list[str] = []
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                row_values: list[str] = []
                for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    if self.isColumnHidden(col):
                        continue
                    item = self.item(row, col)
                    if item is None:
                        row_values.append("")
                        continue
                    if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                        row_values.append("Yes" if item.checkState() == Qt.CheckState.Checked else "")
                    else:
                        row_values.append(item.text())
                lines.append("\t".join(row_values))
            if lines:
                blocks.append("\n".join(lines))

        if not blocks:
            return False

        QApplication.clipboard().setText("\n\n".join(blocks))
        return True

    def fill_selection_down(self) -> bool:
        """Fill selected cells downward from the top value in each selected column."""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            current = self.currentIndex()
            if not current.isValid():
                return False
            selected_ranges = [
                QTableWidgetSelectionRange(
                    current.row(),
                    current.column(),
                    current.row(),
                    current.column(),
                )
            ]

        changed = False
        for selected_range in selected_ranges:
            top_row = selected_range.topRow()
            bottom_row = selected_range.bottomRow()
            left_col = selected_range.leftColumn()
            right_col = selected_range.rightColumn()

            for col in range(left_col, right_col + 1):
                if self.isColumnHidden(col):
                    continue

                source_row = self._find_fill_source_row(top_row, bottom_row, col)
                if source_row is None:
                    continue

                source_item = self.item(source_row, col)
                source_text = source_item.text() if source_item else ""
                source_checked = (
                    source_item.checkState() if source_item and source_item.flags() & Qt.ItemFlag.ItemIsUserCheckable
                    else Qt.CheckState.Unchecked
                )

                if top_row == bottom_row:
                    target_rows = [top_row]
                    if source_row == top_row:
                        continue
                else:
                    target_rows = [
                        row for row in range(top_row, bottom_row + 1)
                        if row != source_row and not self.isRowHidden(row)
                    ]

                for row in target_rows:
                    if self.isRowHidden(row):
                        continue

                    target_item = self.item(row, col)
                    if target_item is None:
                        target_item = QTableWidgetItem("")
                        self.setItem(row, col, target_item)

                    if not (target_item.flags() & Qt.ItemFlag.ItemIsEditable) and not (
                        target_item.flags() & Qt.ItemFlag.ItemIsUserCheckable
                    ):
                        continue

                    if target_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                        target_item.setCheckState(source_checked)
                        target_item.setText("")
                    else:
                        target_item.setText(source_text)
                    changed = True

        return changed

    def _find_fill_source_row(self, top_row: int, bottom_row: int, col: int) -> Optional[int]:
        """Return the preferred source row for fill-down in a column."""
        for row in range(top_row, bottom_row + 1):
            if self.isRowHidden(row):
                continue
            item = self.item(row, col)
            if item is None:
                continue
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                return row
            if item.text().strip():
                return row

        for row in range(top_row - 1, -1, -1):
            if self.isRowHidden(row):
                continue
            return row

        for row in range(top_row, bottom_row + 1):
            if not self.isRowHidden(row):
                return row
        return None


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

