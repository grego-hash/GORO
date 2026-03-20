"""GORO 1.0 - Main Application Entry Point"""

import sys
import os
from pathlib import Path

from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtWidgets import QApplication

from core.constants import ORG_NAME, APP_NAME, APP_VERSION, APP_ID
from app_controller import GOROApp
from core.theme_utils import get_palette_colors
from core.update_utils import check_for_updates_on_startup


APP_ROOT = Path(__file__).resolve().parent


def main():
    """Application entry point."""
    # Fix Qt plugin path issues on Windows
    if sys.platform == "win32":
        # Set Qt plugin path to help find platform plugins
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
        qt_plugin_path = pyqt6_path / "Qt6" / "plugins"
        if qt_plugin_path.exists():
            # Set multiple environment variables that Qt might check
            os.environ["QT_PLUGIN_PATH"] = str(qt_plugin_path)
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(qt_plugin_path / "platforms")
        
        # Set AppUserModelID for proper taskbar behavior
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    
    # Load theme from settings
    settings = QSettings(ORG_NAME, APP_NAME)
    theme = settings.value("theme", "Dark")
    
    # Set palette based on theme
    palette = QPalette()
    colors = get_palette_colors(theme, settings)
    palette.setColor(QPalette.ColorRole.Window, QColor(colors['window_bg']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text_primary']))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors['base']))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['alt_base']))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['tooltip_base']))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['tooltip_text']))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors['text_primary']))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors['button']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['button_text']))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['bright_text']))
    palette.setColor(QPalette.ColorRole.Link, QColor(colors['link']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['highlight']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['highlight_text']))
    app.setPalette(palette)

    # Use the .ico file for the application-level icon
    icon_path = APP_ROOT / "assets" / "icons" / "GORO_LOGO.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    goro_app = GOROApp()
    goro_app.show()

    # Delay update check slightly so startup remains responsive.
    QTimer.singleShot(
        1500,
        lambda: check_for_updates_on_startup(
            parent=goro_app.stacked_widget,
            settings=settings,
            current_version=APP_VERSION,
        ),
    )

    try:
        exit_code = app.exec()
    except KeyboardInterrupt:
        # When launched from a terminal, Ctrl+C should close quietly.
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

