import sys

from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtWidgets import QMessageBox, QSizePolicy, QStackedWidget

from core.constants import APP_NAME, APP_DISPLAY_NAME, ORG_NAME
from ui.home_screen import HomeScreen
from main_window import MainWindow
from core.theme_utils import get_home_theme_colors


class GOROApp:
    """Main application controller managing navigation between screens."""

    def __init__(self):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setWindowTitle(APP_DISPLAY_NAME)
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_window = None

        self.home_screen = HomeScreen()
        self.home_screen.navigate_to_bids.connect(self.show_bids)
        self.home_screen.navigate_to_projects.connect(self.show_projects)
        self.home_screen.navigate_to_calendar.connect(self.show_calendar)
        self.home_screen.navigate_to_tasks.connect(self.show_tasks)
        self.home_screen.navigate_to_vendors.connect(self.show_vendors)
        self.home_screen.navigate_to_customers.connect(self.show_customers)
        self.home_screen.navigate_to_my_company.connect(self.show_my_company)
        self.home_screen.navigate_to_preferences.connect(self.show_preferences)
        self.home_screen.navigate_to_quoted_lookup.connect(self.show_quoted_lookup)
        self.stacked_widget.addWidget(self.home_screen)

        settings = QSettings(ORG_NAME, APP_NAME)
        theme = settings.value("theme", "Dark")
        self._apply_home_theme(theme)

    def _ensure_main_window(self) -> MainWindow:
        if self.main_window is None:
            self.main_window = MainWindow(home_callback=self.show_home, defer_initial_refresh=True)
            self.stacked_widget.addWidget(self.main_window)
        return self.main_window

    def _show_main_window(self) -> MainWindow:
        window = self._ensure_main_window()
        self.stacked_widget.setCurrentWidget(window)
        if hasattr(window, "ensure_initial_list_loaded"):
            QTimer.singleShot(0, window.ensure_initial_list_loaded)
        return window

    def _apply_home_theme(self, theme):
        """Apply theme colors to home screen."""
        settings = QSettings(ORG_NAME, APP_NAME)
        colors = get_home_theme_colors(theme, settings)
        self.home_screen.apply_theme(colors)

        if theme == "Custom" and "opacity" in colors:
            try:
                opacity_value = int(colors["opacity"])
                opacity_value = max(50, min(100, opacity_value))

                if sys.platform == "win32":
                    self._set_windows_opacity(opacity_value)
                else:
                    self.stacked_widget.setWindowOpacity(opacity_value / 100.0)
            except (ValueError, TypeError):
                if sys.platform == "win32":
                    self._set_windows_opacity(100)
                else:
                    self.stacked_widget.setWindowOpacity(1.0)
        else:
            if sys.platform == "win32":
                self._set_windows_opacity(100)
            else:
                self.stacked_widget.setWindowOpacity(1.0)

    def _set_windows_opacity(self, opacity_percent: int):
        """Set window opacity using Windows API."""
        try:
            import ctypes
            from ctypes import wintypes

            hwnd = int(self.stacked_widget.winId())

            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            LWA_ALPHA = 0x00000002

            GetWindowLongW = ctypes.windll.user32.GetWindowLongW
            GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
            GetWindowLongW.restype = wintypes.DWORD

            SetWindowLongW = ctypes.windll.user32.SetWindowLongW
            SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.DWORD]
            SetWindowLongW.restype = wintypes.DWORD

            SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes
            SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_byte, wintypes.DWORD]
            SetLayeredWindowAttributes.restype = wintypes.BOOL

            ex_style = GetWindowLongW(hwnd, GWL_EXSTYLE)

            if not (ex_style & WS_EX_LAYERED):
                SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)

            alpha = int((opacity_percent / 100.0) * 255)
            alpha = max(0, min(255, alpha))

            SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)

        except Exception:
            pass

    def show_bids(self):
        """Navigate to main window with bids filter."""
        window = self._show_main_window()

        if hasattr(window, "set_category"):
            window.set_category("bids")

    def show_projects(self):
        """Navigate to main window with projects filter."""
        window = self._show_main_window()

        if hasattr(window, "set_category"):
            window.set_category("projects")

    def show_calendar(self):
        """Navigate to main window with calendar view enabled."""
        window = self._show_main_window()
        if hasattr(window, "set_category"):
            window.set_category("bids")
        if hasattr(window, "show_calendar_view"):
            window.show_calendar_view()
        elif hasattr(window, "_set_main_view"):
            window._set_main_view(True)

    def show_tasks(self):
        """Navigate to main window with tasks list view enabled."""
        window = self._show_main_window()
        if hasattr(window, "show_tasks_view"):
            window.show_tasks_view()
        elif hasattr(window, "open_task_manager"):
            window.open_task_manager()

    def show_home(self):
        """Navigate back to home screen."""
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def show_vendors(self):
        """Navigate to vendors screen."""
        window = self._show_main_window()

        if hasattr(window, "open_vendors"):
            window.open_vendors()

    def show_customers(self):
        """Navigate to customers screen."""
        window = self._show_main_window()

        if hasattr(window, "open_customers"):
            window.open_customers()

    def show_my_company(self):
        """Navigate to my company screen."""
        window = self._show_main_window()

        if hasattr(window, "open_my_company"):
            window.open_my_company()

    def show_preferences(self):
        """Open preferences dialog."""
        window = self._ensure_main_window()

        window.open_preferences()

    def show_quoted_lookup(self):
        """Open quoted pricing lookup from the Home screen."""
        window = self._show_main_window()
        if hasattr(window, "open_quoted_lookup_from_home"):
            window.open_quoted_lookup_from_home()

    def _maybe_show_first_install_tutorial(self):
        """Show the first-install setup tutorial once per user profile."""
        settings = QSettings(ORG_NAME, APP_NAME)
        tutorial_done = settings.value("first_install_tutorial_completed", False, type=bool)
        if tutorial_done:
            return

        prompt = QMessageBox(self.stacked_widget)
        prompt.setIcon(QMessageBox.Icon.Information)
        prompt.setWindowTitle("Welcome to GORO")
        prompt.setText("First-time setup tutorial")
        prompt.setInformativeText(
            "This quick setup will guide you through:\n"
            "1) Choosing a custom Data folder\n"
            "2) Entering My Company details\n"
            "3) Setting your active user in Preferences"
        )
        start_btn = prompt.addButton("Start Setup", QMessageBox.ButtonRole.AcceptRole)
        skip_btn = prompt.addButton("Skip", QMessageBox.ButtonRole.RejectRole)
        later_btn = prompt.addButton("Later", QMessageBox.ButtonRole.DestructiveRole)
        prompt.setDefaultButton(start_btn)
        prompt.exec()

        clicked = prompt.clickedButton()
        if clicked == start_btn:
            self._run_first_install_tutorial()
            settings.setValue("first_install_tutorial_completed", True)
        elif clicked == skip_btn:
            settings.setValue("first_install_tutorial_completed", True)
        else:
            # Later: ask again on next startup until completed or skipped.
            pass

    def _run_first_install_tutorial(self):
        """Run guided first-install setup steps."""
        window = self._show_main_window()

        QMessageBox.information(
            window,
            "Setup Step 1 of 3",
            "Choose your Data folder now.\n\n"
            "Recommended: pick a location outside the app install folder "
            "(for example OneDrive or a shared company directory).",
        )
        previous_root = str(getattr(window.paths, "root", ""))
        if hasattr(window, "choose_data_folder"):
            window.choose_data_folder()
        current_root = str(getattr(window.paths, "root", ""))
        if current_root and current_root != previous_root:
            QMessageBox.information(
                window,
                "Data Folder Updated",
                f"Data folder set to:\n{current_root}",
            )
        else:
            QMessageBox.information(
                window,
                "Data Folder Unchanged",
                "No folder was selected, so the current Data folder was kept.",
            )

        QMessageBox.information(
            window,
            "Setup Step 2 of 3",
            "Next: set up your company profile and contacts/users.\n\n"
            "In My Company, add your company details and add contacts.\n"
            "Use the Position column for roles like Estimator or Project Manager.",
        )
        window.open_my_company()

        QMessageBox.information(
            window,
            "Setup Step 3 of 3",
            "Last: choose your active username in Preferences.\n\n"
            "Tip: usernames are pulled from My Company contacts.",
        )
        window.open_preferences()

        QMessageBox.information(
            window,
            "Setup Complete",
            "Initial setup is complete. You can revisit these anytime from Home:\n"
            "- Preferences (for Data folder and username)\n"
            "- My Company (for company details and contacts/users)",
        )

    def show(self):
        """Show the application window."""
        self.stacked_widget.showMaximized()

        QTimer.singleShot(400, self._maybe_show_first_install_tutorial)

        if sys.platform == "win32":
            settings = QSettings(ORG_NAME, APP_NAME)
            theme = settings.value("theme", "Dark")
            if theme == "Custom":
                colors = get_home_theme_colors(theme, settings)
                if "opacity" in colors:
                    try:
                        opacity_value = int(colors["opacity"])
                        opacity_value = max(50, min(100, opacity_value))
                        QTimer.singleShot(50, lambda: self._set_windows_opacity(opacity_value))
                    except (ValueError, TypeError):
                        pass

