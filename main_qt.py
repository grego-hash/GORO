"""GORO 1.0 - Main Application Entry Point"""

import sys
import os
from pathlib import Path

from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtWidgets import QApplication, QMessageBox

from core.constants import ORG_NAME, APP_NAME, APP_VERSION, APP_ID
from app_controller import GOROApp
from core.models import export_data_root_changes, resolve_data_root_state
from core.theme_utils import get_palette_colors
from core.update_utils import check_for_updates_on_startup


APP_ROOT = Path(__file__).resolve().parent

PENDING_EXPORT_FLAG = "data_root/pending_fallback_export"
PENDING_EXPORT_SOURCE = "data_root/pending_fallback_source"
PENDING_EXPORT_DEST = "data_root/pending_fallback_destination"


def _queue_fallback_export(settings: QSettings, source_root: Path, destination_root: Path) -> None:
    settings.setValue(PENDING_EXPORT_FLAG, True)
    settings.setValue(PENDING_EXPORT_SOURCE, str(source_root))
    settings.setValue(PENDING_EXPORT_DEST, str(destination_root))


def _clear_fallback_export(settings: QSettings) -> None:
    settings.remove(PENDING_EXPORT_FLAG)
    settings.remove(PENDING_EXPORT_SOURCE)
    settings.remove(PENDING_EXPORT_DEST)


def _prompt_for_pending_export(parent, settings: QSettings, configured_root: Path) -> None:
    pending_export = settings.value(PENDING_EXPORT_FLAG, False, type=bool)
    pending_source = str(settings.value(PENDING_EXPORT_SOURCE, "") or "").strip()
    pending_dest = str(settings.value(PENDING_EXPORT_DEST, "") or "").strip()
    if not pending_export or not pending_source:
        return

    source_root = Path(pending_source)
    destination_root = Path(pending_dest) if pending_dest else configured_root
    if destination_root != configured_root:
        destination_root = configured_root
    if not source_root.exists() or not source_root.is_dir():
        _clear_fallback_export(settings)
        return

    reply = QMessageBox.question(
        parent,
        "Export Local Data Changes",
        "Your default data folder is available again.\n\n"
        "GORO used a local fallback data folder while it was unavailable.\n"
        "Do you want to export local changes to the default data folder now?\n\n"
        f"Local folder: {source_root}\n"
        f"Default folder: {destination_root}",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if reply != QMessageBox.StandardButton.Yes:
        return

    try:
        copied_files, skipped_files = export_data_root_changes(source_root, destination_root)
    except OSError as exc:
        QMessageBox.warning(
            parent,
            "Export Local Data Changes",
            f"Could not export local changes to the default data folder:\n{exc}",
        )
        return

    _clear_fallback_export(settings)
    QMessageBox.information(
        parent,
        "Export Local Data Changes",
        "Local data export completed.\n\n"
        f"Copied files: {copied_files}\n"
        f"Unchanged files skipped: {skipped_files}",
    )


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
    data_root_state = resolve_data_root_state(settings)
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

    if data_root_state.using_fallback and data_root_state.configured_root is not None:
        _queue_fallback_export(settings, data_root_state.fallback_root, data_root_state.configured_root)
        QMessageBox.warning(
            goro_app.stacked_widget,
            "Data Folder Unavailable",
            "The configured data folder is unavailable.\n\n"
            "GORO will use a local fallback folder for now.\n"
            "When the default data folder is available again, you can export local changes on startup.\n\n"
            f"Configured folder: {data_root_state.configured_root}\n"
            f"Using fallback folder: {data_root_state.fallback_root}",
        )
    elif data_root_state.configured_available and data_root_state.configured_root is not None:
        _prompt_for_pending_export(goro_app.stacked_widget, settings, data_root_state.configured_root)

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

