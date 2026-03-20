
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except Exception:
    HAS_PDF2IMAGE = False

# Configure Poppler for bundled installation
from core.poppler_utils import configure_pdf2image, get_poppler_path
configure_pdf2image()
from PyQt6.QtCore import Qt, QPoint, QRect, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel


# ----------------------------
# Image Region Selection Widget
# ----------------------------

class PagePreviewWidget(QLabel):
    """Widget for displaying a clickable PDF page preview."""
    def __init__(self, page_num, pixmap):
        super().__init__()
        self.page_num = page_num
        self.is_selected = False
        self.is_hovered = False
        
        # Scale pixmap to reasonable thumbnail size
        if pixmap.width() > 200 or pixmap.height() > 260:
            pixmap = pixmap.scaled(200, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.preview_pixmap = pixmap
        self.setPixmap(pixmap)
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add border styling
        self.setStyleSheet(
            "QLabel { "
            "border: 2px solid #555; "
            "background-color: #2d2d2d; "
            "padding: 5px; "
            "}"
        )
    
    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()
    
    def set_hovered(self, hovered):
        self.is_hovered = hovered
        self.update_style()
    
    def update_style(self):
        if self.is_selected:
            border_color = "#00c800"
            border_width = 3
        elif self.is_hovered:
            border_color = "#007acc"
            border_width = 3
        else:
            border_color = "#555"
            border_width = 2
        
        self.setStyleSheet(
            f"QLabel {{ "
            f"border: {border_width}px solid {border_color}; "
            f"background-color: #2d2d2d; "
            f"padding: 5px; "
            f"}}"
        )
    
    def enterEvent(self, event):
        self.set_hovered(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.set_hovered(False)
        super().leaveEvent(event)


class TableSelectionWidget(QLabel):
    """Widget for visually selecting a table from multiple detected tables."""
    def __init__(self, pixmap, table_bboxes, page_width, page_height):
        super().__init__()
        self.original_pixmap = pixmap
        self.table_bboxes = table_bboxes  # List of (x0, y0, x1, y1) in PDF coordinates
        self.page_width = page_width
        self.page_height = page_height
        self.selected_index = None
        self.hovered_index = None
        self.zoom_level = 1.0
        self.scroll_area = None  # Will be set after creation
        
        # Calculate scale factor from PDF coordinates to pixmap coordinates
        self.scale_x = pixmap.width() / page_width
        self.scale_y = pixmap.height() / page_height
        
        self.setPixmap(pixmap)
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Start centered
        self.setMouseTracking(True)
    
    def set_scroll_area(self, scroll_area):
        """Set reference to containing scroll area for dynamic alignment."""
        self.scroll_area = scroll_area
    
    def set_zoom(self, zoom_level):
        """Set zoom level and update display."""
        self.zoom_level = zoom_level
        scaled_pixmap = self.original_pixmap.scaled(
            int(self.original_pixmap.width() * zoom_level),
            int(self.original_pixmap.height() * zoom_level),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)
        
        # Dynamically adjust alignment based on whether image fits in viewport
        if self.scroll_area:
            viewport_size = self.scroll_area.viewport().size()
            image_fits = (scaled_pixmap.width() <= viewport_size.width() and 
                         scaled_pixmap.height() <= viewport_size.height())
            
            if image_fits:
                # Image fits - center it
                self.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setMinimumSize(viewport_size)  # Fill viewport for centering
            else:
                # Image larger than viewport - align top-left for scrolling
                self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.setFixedSize(scaled_pixmap.size())
        else:
            # No scroll area reference - use fixed size
            self.setFixedSize(scaled_pixmap.size())
        
        self.update()
        
    def _pdf_to_pixmap_coords(self, x0, top, x1, bottom):
        """Convert PDF coordinates to pixmap coordinates."""
        px0 = int(x0 * self.scale_x * self.zoom_level)
        py0 = int(top * self.scale_y * self.zoom_level)
        px1 = int(x1 * self.scale_x * self.zoom_level)
        py1 = int(bottom * self.scale_y * self.zoom_level)
        return px0, py0, px1, py1
    
    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.hovered_index = None
        
        # Check if mouse is over any table (reverse order for overlapping tables)
        for i in reversed(range(len(self.table_bboxes))):
            bbox = self.table_bboxes[i]
            x0, top, x1, bottom = self._pdf_to_pixmap_coords(*bbox)
            if x0 <= pos.x() <= x1 and top <= pos.y() <= bottom:
                self.hovered_index = i
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                break
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            # Check which table was clicked (reverse order for overlapping tables)
            for i in reversed(range(len(self.table_bboxes))):
                bbox = self.table_bboxes[i]
                x0, top, x1, bottom = self._pdf_to_pixmap_coords(*bbox)
                if x0 <= pos.x() <= x1 and top <= pos.y() <= bottom:
                    self.selected_index = i
                    self.update()
                    break
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Draw all table bounding boxes
        for i, bbox in enumerate(self.table_bboxes):
            x0, top, x1, bottom = self._pdf_to_pixmap_coords(*bbox)
            
            # Choose color and style based on state
            if i == self.selected_index:
                pen = QPen(QColor(0, 200, 0), 3, Qt.PenStyle.SolidLine)  # Green for selected
            elif i == self.hovered_index:
                pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)  # Blue for hover
            else:
                pen = QPen(QColor(200, 200, 200), 2, Qt.PenStyle.DashLine)  # Gray for others
            
            painter.setPen(pen)
            painter.drawRect(x0, top, x1 - x0, bottom - top)
            
            # Draw table number label
            label = f"Table {i + 1}"
            label_bg = QColor(0, 120, 215) if i == self.hovered_index else QColor(100, 100, 100)
            if i == self.selected_index:
                label_bg = QColor(0, 200, 0)
            
            painter.fillRect(x0, top - 25, 80, 25, label_bg)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(x0 + 5, top - 7, label)
    
    def get_selected_index(self):
        """Return the index of the selected table, or None."""
        return self.selected_index


class ImageRegionSelection(QLabel):
    """Widget for selecting a rectangular region on an image."""
    def __init__(self, pixmap):
        super().__init__()
        self.original_pixmap = pixmap
        self.setPixmap(pixmap)
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.update()
    
    def mouseMoveEvent(self, event):
        if self.start_point:
            self.end_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            self.end_point = event.pos()
            # Calculate selection rectangle
            start = self.start_point
            end = self.end_point
            x = min(start.x(), end.x())
            y = min(start.y(), end.y())
            width = abs(end.x() - start.x())
            height = abs(end.y() - start.y())
            self.selection_rect = QRect(x, y, width, height)
            self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start_point and self.end_point:
            painter = QPainter(self)
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            
            start = self.start_point
            end = self.end_point
            x = min(start.x(), end.x())
            y = min(start.y(), end.y())
            width = abs(end.x() - start.x())
            height = abs(end.y() - start.y())
            
            painter.drawRect(x, y, width, height)
    
    def get_selection(self):
        """Return the selected rectangle, or None if no selection."""
        return self.selection_rect


# ----------------------------
# PDF Conversion Worker Thread
# ----------------------------

class PDFConversionWorker(QThread):
    """Background thread for converting PDF pages to images without blocking UI."""
    finished = pyqtSignal(list)  # Emits list of PIL images
    error = pyqtSignal(str)  # Emits error message
    progress = pyqtSignal(str)  # Emits progress message
    
    def __init__(self, pdf_path, dpi=30):
        super().__init__()
        self.pdf_path = pdf_path
        self.dpi = dpi
    
    def run(self):
        """Convert PDF to images in background thread."""
        try:
            if HAS_PDF2IMAGE:
                self.progress.emit("Converting PDF pages to images...")
                poppler_path = get_poppler_path()
                images = convert_from_path(
                    self.pdf_path,
                    dpi=self.dpi,
                    poppler_path=poppler_path
                )
                self.progress.emit(f"Successfully converted {len(images)} pages")
                self.finished.emit(images)
            else:
                self.error.emit("pdf2image library not installed")
        except Exception as e:
            self.error.emit(str(e))

