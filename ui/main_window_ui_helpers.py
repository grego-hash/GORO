from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import QDate, QRect, Qt, QUrl
from PyQt6.QtGui import QColor, QDesktopServices, QFontMetrics, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCalendarWidget,
    QFileDialog as QtFileDialog,
    QInputDialog as QtInputDialog,
    QLineEdit,
    QListWidget,
    QMessageBox as QtMessageBox,
    QTreeWidget,
    QWidget,
)


def _resolve_transient_parent(parent: Optional[QWidget] = None) -> Optional[QWidget]:
    if isinstance(parent, QWidget) and parent.isVisible():
        resolved_parent = parent
    else:
        resolved_parent = None

    active_modal = QApplication.activeModalWidget()
    if isinstance(active_modal, QWidget) and active_modal.isVisible():
        return active_modal

    active_window = QApplication.activeWindow()
    if not isinstance(active_window, QWidget) or not active_window.isVisible():
        return resolved_parent

    if resolved_parent is None:
        return active_window

    parent_window = resolved_parent.window()
    active_top_level = active_window.window()
    if active_top_level is not parent_window:
        return active_window

    return resolved_parent


class QMessageBox(QtMessageBox):
    @classmethod
    def information(cls, parent, title, text, *args, **kwargs):
        return QtMessageBox.information(_resolve_transient_parent(parent), title, text, *args, **kwargs)

    @classmethod
    def warning(cls, parent, title, text, *args, **kwargs):
        return QtMessageBox.warning(_resolve_transient_parent(parent), title, text, *args, **kwargs)

    @classmethod
    def question(cls, parent, title, text, *args, **kwargs):
        return QtMessageBox.question(_resolve_transient_parent(parent), title, text, *args, **kwargs)

    @classmethod
    def critical(cls, parent, title, text, *args, **kwargs):
        return QtMessageBox.critical(_resolve_transient_parent(parent), title, text, *args, **kwargs)


class QFileDialog(QtFileDialog):
    @classmethod
    def getOpenFileName(cls, parent=None, *args, **kwargs):
        return QtFileDialog.getOpenFileName(_resolve_transient_parent(parent), *args, **kwargs)

    @classmethod
    def getOpenFileNames(cls, parent=None, *args, **kwargs):
        return QtFileDialog.getOpenFileNames(_resolve_transient_parent(parent), *args, **kwargs)

    @classmethod
    def getSaveFileName(cls, parent=None, *args, **kwargs):
        return QtFileDialog.getSaveFileName(_resolve_transient_parent(parent), *args, **kwargs)

    @classmethod
    def getExistingDirectory(cls, parent=None, *args, **kwargs):
        return QtFileDialog.getExistingDirectory(_resolve_transient_parent(parent), *args, **kwargs)


class QInputDialog(QtInputDialog):
    @classmethod
    def getText(cls, parent, title, label, *args, **kwargs):
        return QtInputDialog.getText(_resolve_transient_parent(parent), title, label, *args, **kwargs)

    @classmethod
    def getItem(cls, parent, title, label, items, *args, **kwargs):
        return QtInputDialog.getItem(_resolve_transient_parent(parent), title, label, items, *args, **kwargs)

    @classmethod
    def getInt(cls, parent, title, label, *args, **kwargs):
        return QtInputDialog.getInt(_resolve_transient_parent(parent), title, label, *args, **kwargs)

    @classmethod
    def getDouble(cls, parent, title, label, *args, **kwargs):
        return QtInputDialog.getDouble(_resolve_transient_parent(parent), title, label, *args, **kwargs)


class BidTaskCalendarWidget(QCalendarWidget):
    """Calendar widget that paints bid/task indicators directly in day cells."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries_by_date: Dict[QDate, List[Dict]] = {}

    def set_entries_by_date(self, entries_by_date: Dict[QDate, List[Dict]]):
        self._entries_by_date = entries_by_date
        self.updateCells()

    def paintCell(self, painter: QPainter, rect: QRect, date: QDate):
        super().paintCell(painter, rect, date)

        entries = self._entries_by_date.get(date, [])
        if not entries:
            return

        left_pad = 4
        right_pad = 4
        top_pad = 16
        bottom_pad = 3
        line_height = 12
        line_spacing = 2

        usable_width = max(12, rect.width() - left_pad - right_pad)
        available_height = max(0, rect.height() - top_pad - bottom_pad)
        max_lines = max(1, available_height // (line_height + line_spacing))

        draw_entries = entries[:max_lines]
        remaining = len(entries) - len(draw_entries)

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        font = painter.font()
        font.setPointSize(max(7, font.pointSize() - 1))
        painter.setFont(font)
        fm = QFontMetrics(font)

        for idx, entry in enumerate(draw_entries):
            entry_kind = str(entry.get("kind", ""))
            proposal_type = str(entry.get("proposal_type", "")).strip().lower()
            name = str(entry.get("name", "")).strip()

            if entry_kind == "task":
                label = f"Task: {name}" if name else "Task"
            else:
                label = f"Bid: {name}" if name else "Bid"

            if entry_kind == "task":
                color = QColor("#7f8c8d")
            elif proposal_type == "proposal":
                color = QColor("#2d6aa8")
            elif proposal_type == "budget":
                color = QColor("#2e7d46")
            else:
                color = QColor("#6f42c1")

            y = rect.top() + top_pad + idx * (line_height + line_spacing)
            pill_rect = QRect(rect.left() + left_pad, y, usable_width, line_height)
            painter.fillRect(pill_rect, color)

            text_rect = QRect(pill_rect.left() + 2, pill_rect.top(), max(1, pill_rect.width() - 4), pill_rect.height())
            text = fm.elidedText(label, Qt.TextElideMode.ElideRight, text_rect.width())
            painter.setPen(QColor("#ffffff"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
            painter.setPen(Qt.PenStyle.NoPen)

        if remaining > 0:
            more_y = rect.top() + top_pad + len(draw_entries) * (line_height + line_spacing)
            more_rect = QRect(rect.left() + left_pad, more_y, usable_width, line_height)
            painter.fillRect(more_rect, QColor("#444444"))
            painter.setPen(QColor("#d0d0d0"))
            painter.drawText(
                QRect(more_rect.left() + 2, more_rect.top(), max(1, more_rect.width() - 4), more_rect.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                f"+{remaining} more",
            )

        painter.restore()


class BidBoardStatusListWidget(QListWidget):
    """QListWidget that reports cross-column bid drops back to MainWindow."""

    def __init__(self, status_name: str, drop_callback, parent=None):
        super().__init__(parent)
        self.status_name = status_name
        self._drop_callback = drop_callback

    def dropEvent(self, event):
        source_list = event.source()
        moved_path = ""
        source_status = ""

        if isinstance(source_list, BidBoardStatusListWidget):
            source_status = source_list.status_name
            source_item = source_list.currentItem()
            if source_item is not None:
                moved_path = str(source_item.data(Qt.ItemDataRole.UserRole) or "")

        super().dropEvent(event)

        if not moved_path:
            current_item = self.currentItem()
            if current_item is not None:
                moved_path = str(current_item.data(Qt.ItemDataRole.UserRole) or "")

        if moved_path and source_status and source_status != self.status_name:
            self._drop_callback(source_status, self.status_name, moved_path)


class FolderDropTreeWidget(QTreeWidget):
    """Tree widget that accepts external drops and internal folder moves."""

    def __init__(self, resolve_target_callback, drop_callback, move_callback, parent=None):
        super().__init__(parent)
        self._resolve_target_callback = resolve_target_callback
        self._drop_callback = drop_callback
        self._move_callback = move_callback
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, event):
        if event.source() is self:
            event.acceptProposedAction()
            return
        mime = event.mimeData()
        if mime is not None and mime.hasUrls() and any(url.isLocalFile() for url in mime.urls()):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.source() is self:
            source_item = self.currentItem()
            target_item = self.itemAt(event.position().toPoint())
            if source_item is None:
                event.ignore()
                return
            if source_item.data(0, Qt.ItemDataRole.UserRole + 2):
                event.ignore()
                return
            source_kind = source_item.data(0, Qt.ItemDataRole.UserRole + 1)
            if source_kind and source_kind != "folder":
                event.ignore()
                return
            source_path = self._resolve_target_callback(source_item)
            target_path = self._resolve_target_callback(target_item)
            if source_path is not None and target_path is not None and source_path != target_path:
                event.acceptProposedAction()
                return
            event.ignore()
            return

        mime = event.mimeData()
        if mime is None or not mime.hasUrls() or not any(url.isLocalFile() for url in mime.urls()):
            super().dragMoveEvent(event)
            return
        item = self.itemAt(event.position().toPoint())
        target = self._resolve_target_callback(item)
        if target is not None:
            event.acceptProposedAction()
            return
        event.ignore()

    def dropEvent(self, event):
        if event.source() is self:
            source_item = self.currentItem()
            if source_item is None:
                event.ignore()
                return
            if source_item.data(0, Qt.ItemDataRole.UserRole + 2):
                event.ignore()
                return
            source_kind = source_item.data(0, Qt.ItemDataRole.UserRole + 1)
            if source_kind and source_kind != "folder":
                event.ignore()
                return
            source_path = self._resolve_target_callback(source_item)
            target_item = self.itemAt(event.position().toPoint())
            destination = self._resolve_target_callback(target_item)
            if source_path is None or destination is None:
                event.ignore()
                return
            handled = bool(self._move_callback(source_path, destination))
            if handled:
                event.acceptProposedAction()
            else:
                event.ignore()
            return

        mime = event.mimeData()
        if mime is None or not mime.hasUrls():
            super().dropEvent(event)
            return

        source_paths: List[Path] = []
        for url in mime.urls():
            if not url.isLocalFile():
                continue
            local_path = Path(url.toLocalFile())
            if local_path.exists():
                source_paths.append(local_path)

        if not source_paths:
            event.ignore()
            return

        item = self.itemAt(event.position().toPoint())
        destination = self._resolve_target_callback(item)
        if destination is None:
            event.ignore()
            return

        handled = bool(self._drop_callback(destination, source_paths))
        if handled:
            event.acceptProposedAction()
        else:
            event.ignore()


class FileDropLineEdit(QLineEdit):
    """Line edit that accepts local files via drag and drop."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.textChanged.connect(self._update_openable_style)
        self._update_openable_style()

    def _openable_url(self) -> Optional[QUrl]:
        raw = self.text().strip()
        if not raw:
            return None
        try:
            local = Path(raw)
            if local.exists():
                return QUrl.fromLocalFile(str(local))
        except Exception:
            pass
        url = QUrl.fromUserInput(raw)
        if url.isValid() and url.scheme():
            return url
        return None

    def _update_openable_style(self):
        url = self._openable_url()
        if url is None:
            self.setStyleSheet("")
            self.setToolTip("")
            return
        if url.scheme().lower() in ("http", "https"):
            self.setStyleSheet("QLineEdit { color: #4ea1ff; }")
            self.setToolTip("Link detected. Double-click or Ctrl+Click to open.")
        else:
            self.setStyleSheet("")
            self.setToolTip("Path detected. Double-click or Ctrl+Click to open.")

    def _open_current_value(self) -> bool:
        url = self._openable_url()
        if url is None:
            return False
        return bool(QDesktopServices.openUrl(url))

    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime is not None and mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime is not None and mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    self.setText(url.toLocalFile())
                    event.acceptProposedAction()
                    return
        super().dropEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            if self._open_current_value():
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._open_current_value():
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        act_open = menu.addAction("Open Link/File")
        act_open.setEnabled(self._openable_url() is not None)
        chosen = menu.exec(event.globalPos())
        if chosen == act_open:
            self._open_current_value()

