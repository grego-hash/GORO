"""
GORO Home Screen - Landing page with logo and navigation buttons
"""

import json
import re
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
    QFrame, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, QSettings, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from core.constants import ORG_NAME, APP_NAME, APP_DISPLAY_NAME
from core.models import get_paths, list_bids, list_projects
from core.utils import sanitize_name, parse_due_date


class HomeScreen(QWidget):
    """Home screen with logo and navigation buttons."""
    
    # Signals for navigation
    navigate_to_bids = pyqtSignal()
    navigate_to_projects = pyqtSignal()
    navigate_to_calendar = pyqtSignal()
    navigate_to_tasks = pyqtSignal()
    navigate_to_vendors = pyqtSignal()
    navigate_to_customers = pyqtSignal()
    navigate_to_my_company = pyqtSignal()
    navigate_to_preferences = pyqtSignal()
    navigate_to_quoted_lookup = pyqtSignal()
    navigate_to_fabrication = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Allow home screen to resize freely
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.paths = get_paths(self.settings)
        self._action_columns = 0
        self._overview_columns = 0
        self._kpi_columns = 0
        self._action_cards = []
        self._tab_order_applied = False
        self._kpi_scan_truncated = False
        self._home_mode = str(self.settings.value("home_workspace_mode", "bids") or "bids").strip().lower()
        if self._home_mode not in {"bids", "projects"}:
            self._home_mode = "bids"
        self._kpi_scope = str(self.settings.value("home_kpi_scope", "me") or "me").strip().lower()
        if self._kpi_scope not in {"me", "all"}:
            self._kpi_scope = "me"
        self._top_customers_period = str(self.settings.value("home_top_customers_period", "ytd") or "ytd").strip().lower()
        if self._top_customers_period not in {"ytd", "all"}:
            self._top_customers_period = "ytd"
        # Top-customer scope is intentionally synced with KPI scope.
        self._top_customers_scope = self._kpi_scope
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the home screen UI."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        root_layout.addWidget(self.scroll_area)

        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)

        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(24)
        self.main_layout = layout

        self.hero_panel = QFrame()
        self.hero_panel.setObjectName("heroPanel")
        self.hero_layout = QHBoxLayout(self.hero_panel)
        self.hero_layout.setContentsMargins(24, 18, 24, 18)
        self.hero_layout.setSpacing(18)

        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        from pathlib import Path
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / "goro_logo.png"
        self._logo_source_pixmap = None
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                self._logo_source_pixmap = pixmap
                self.logo_label.setPixmap(
                    self._logo_source_pixmap.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)
                )
            else:
                self.logo_label.setText(APP_DISPLAY_NAME)
                font = QFont("Segoe UI", 54, QFont.Weight.Bold)
                self.logo_label.setFont(font)
        else:
            self.logo_label.setText(APP_DISPLAY_NAME)
            font = QFont("Segoe UI", 54, QFont.Weight.Bold)
            self.logo_label.setFont(font)

        logo_layout.addWidget(self.logo_label)
        self.hero_layout.addWidget(logo_container, 0, Qt.AlignmentFlag.AlignVCenter)

        hero_text_container = QWidget()
        hero_text_layout = QVBoxLayout(hero_text_container)
        hero_text_layout.setContentsMargins(0, 0, 0, 0)
        hero_text_layout.setSpacing(4)

        self.hero_title = QLabel("Home")
        self.hero_title.setObjectName("heroTitle")
        self.hero_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.hero_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hero_text_layout.addWidget(self.hero_title)

        self.hero_subtitle = QLabel("Your bids, tasks, and deadlines in one place")
        self.hero_subtitle.setObjectName("heroSubtitle")
        self.hero_subtitle.setFont(QFont("Segoe UI", 10))
        self.hero_subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hero_text_layout.addWidget(self.hero_subtitle)

        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(0, 4, 0, 2)
        mode_row.setSpacing(8)
        self.btn_mode_bids = self._create_quick_button("Bidding", lambda: self._set_home_mode("bids"))
        self.btn_mode_bids.setCheckable(True)
        self.btn_mode_bids.setProperty("class", "scopeToggle")
        self.btn_mode_bids.setMaximumWidth(110)
        mode_row.addWidget(self.btn_mode_bids)
        self.btn_mode_projects = self._create_quick_button("Projects", lambda: self._set_home_mode("projects"))
        self.btn_mode_projects.setCheckable(True)
        self.btn_mode_projects.setProperty("class", "scopeToggle")
        self.btn_mode_projects.setMaximumWidth(110)
        mode_row.addWidget(self.btn_mode_projects)
        mode_row.addStretch(1)
        hero_text_layout.addLayout(mode_row)

        self.hero_context = QLabel()
        self.hero_context.setObjectName("heroContext")
        self.hero_context.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        hero_text_layout.addWidget(self.hero_context)
        hero_text_layout.addStretch(1)
        self.hero_layout.addWidget(hero_text_container, 1)

        self.hero_open_bids = self._create_quick_button("Open Bids", self._open_primary_workspace)
        self.hero_open_bids.setProperty("class", "heroPrimary")
        self.hero_open_tasks = self._create_quick_button("Open Tasks", self.navigate_to_tasks.emit)
        self.hero_open_tasks.setProperty("class", "heroSecondary")

        hero_actions = QVBoxLayout()
        hero_actions.setContentsMargins(0, 0, 0, 0)
        hero_actions.setSpacing(8)
        hero_actions.addWidget(self.hero_open_bids)
        hero_actions.addWidget(self.hero_open_tasks)
        hero_actions.addStretch(1)
        self.hero_layout.addLayout(hero_actions)

        layout.addWidget(self.hero_panel)

        self.overview_panel = QFrame()
        self.overview_panel.setObjectName("overviewPanel")
        self.overview_grid = QGridLayout(self.overview_panel)
        self.overview_grid.setContentsMargins(18, 18, 18, 18)
        self.overview_grid.setHorizontalSpacing(14)
        self.overview_grid.setVerticalSpacing(14)

        self.summary_panel = QFrame()
        self.summary_panel.setObjectName("summaryPanel")
        summary_layout = QVBoxLayout(self.summary_panel)
        summary_layout.setContentsMargins(18, 18, 18, 18)
        summary_layout.setSpacing(12)

        summary_header = QHBoxLayout()
        summary_header.setContentsMargins(0, 0, 0, 0)
        summary_header.setSpacing(8)

        self.summary_title = QLabel("This Week")
        self.summary_title.setObjectName("panelTitle")
        self.summary_title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        summary_header.addWidget(self.summary_title)
        summary_header.addStretch(1)

        self.btn_scope_me = self._create_quick_button("Me", lambda: self._set_kpi_scope("me"))
        self.btn_scope_me.setCheckable(True)
        self.btn_scope_me.setProperty("class", "scopeToggle")
        self.btn_scope_me.setMinimumHeight(30)
        self.btn_scope_me.setMaximumWidth(58)
        summary_header.addWidget(self.btn_scope_me)

        self.btn_scope_all = self._create_quick_button("All", lambda: self._set_kpi_scope("all"))
        self.btn_scope_all.setCheckable(True)
        self.btn_scope_all.setProperty("class", "scopeToggle")
        self.btn_scope_all.setMinimumHeight(30)
        self.btn_scope_all.setMaximumWidth(58)
        summary_header.addWidget(self.btn_scope_all)

        self.btn_recompute_kpis = self._create_quick_button("Recompute KPIs", self._on_recompute_kpis)
        self.btn_recompute_kpis.setProperty("class", "quickButton")
        self.btn_recompute_kpis.setMinimumHeight(30)
        self.btn_recompute_kpis.setMaximumWidth(130)
        summary_header.addWidget(self.btn_recompute_kpis)
        summary_layout.addLayout(summary_header)

        self._update_scope_toggle_buttons()

        week_span = self._get_week_span_label()
        self.summary_period = QLabel(week_span)
        self.summary_period.setObjectName("summaryPeriod")
        self.summary_period.setFont(QFont("Segoe UI", 10))
        summary_layout.addWidget(self.summary_period)

        self.kpi_grid = QGridLayout()
        self.kpi_grid.setHorizontalSpacing(10)
        self.kpi_grid.setVerticalSpacing(10)
        summary_layout.addLayout(self.kpi_grid)

        self.kpi_cards = {
            "overdue": self._create_stat_card("Overdue Items", "Loading..."),
            "due_today": self._create_stat_card("Due Today", "Loading..."),
            "due_week": self._create_stat_card("Due This Week", "Loading..."),
            "open_tasks": self._create_stat_card("Open Tasks (My)", "Loading..."),
            "active_bids": self._create_stat_card("Active Bids (My)", "Loading..."),
            "submitted_week": self._create_stat_card("Submitted This Week", "Loading..."),
            "ytd_submitted": self._create_stat_card("YTD Submitted", "Loading..."),
            "win_rate_ytd": self._create_stat_card("Win Rate YTD", "Loading..."),
            "ytd_awarded": self._create_stat_card("YTD Awarded", "Loading..."),
            "aging": self._create_stat_card("Aging Bids", "Loading..."),
        }

        for idx, card in enumerate(self.kpi_cards.values()):
            row = idx // 2
            col = idx % 2
            self.kpi_grid.addWidget(card, row, col)

        summary_layout.addStretch(1)

        self.quick_panel = QFrame()
        self.quick_panel.setObjectName("quickPanel")
        quick_layout = QVBoxLayout(self.quick_panel)
        quick_layout.setContentsMargins(18, 18, 18, 18)
        quick_layout.setSpacing(12)

        self.quick_title = QLabel("Top Customers")
        self.quick_title.setObjectName("panelTitle")
        self.quick_title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        quick_header = QHBoxLayout()
        quick_header.setContentsMargins(0, 0, 0, 0)
        quick_header.setSpacing(8)
        quick_header.addWidget(self.quick_title)
        quick_header.addStretch(1)

        self.btn_top_scope_me = self._create_quick_button("Me", lambda: self._set_top_customers_scope("me"))
        self.btn_top_scope_me.setCheckable(True)
        self.btn_top_scope_me.setProperty("class", "scopeToggle")
        self.btn_top_scope_me.setMinimumHeight(30)
        self.btn_top_scope_me.setMaximumWidth(58)
        quick_header.addWidget(self.btn_top_scope_me)

        self.btn_top_scope_all = self._create_quick_button("All", lambda: self._set_top_customers_scope("all"))
        self.btn_top_scope_all.setCheckable(True)
        self.btn_top_scope_all.setProperty("class", "scopeToggle")
        self.btn_top_scope_all.setMinimumHeight(30)
        self.btn_top_scope_all.setMaximumWidth(58)
        quick_header.addWidget(self.btn_top_scope_all)

        self.btn_top_period_ytd = self._create_quick_button("YTD", lambda: self._set_top_customers_period("ytd"))
        self.btn_top_period_ytd.setCheckable(True)
        self.btn_top_period_ytd.setProperty("class", "scopeToggle")
        self.btn_top_period_ytd.setMinimumHeight(30)
        self.btn_top_period_ytd.setMaximumWidth(58)
        quick_header.addWidget(self.btn_top_period_ytd)

        self.btn_top_period_all = self._create_quick_button("All", lambda: self._set_top_customers_period("all"))
        self.btn_top_period_all.setCheckable(True)
        self.btn_top_period_all.setProperty("class", "scopeToggle")
        self.btn_top_period_all.setMinimumHeight(30)
        self.btn_top_period_all.setMaximumWidth(58)
        quick_header.addWidget(self.btn_top_period_all)

        quick_layout.addLayout(quick_header)

        self.top_customers_grid = QGridLayout()
        self.top_customers_grid.setHorizontalSpacing(14)
        self.top_customers_grid.setVerticalSpacing(6)
        quick_layout.addLayout(self.top_customers_grid)

        self.project_focus_widget = QWidget()
        self.project_focus_layout = QVBoxLayout(self.project_focus_widget)
        self.project_focus_layout.setContentsMargins(0, 0, 0, 0)
        self.project_focus_layout.setSpacing(8)
        self.project_focus_sections: list[tuple[QLabel, list[QLabel]]] = []
        project_section_titles = ["Top PM Workloads", "Due Next", "Missing PM / Due Date"]
        for section_title in project_section_titles:
            heading = QLabel(section_title)
            heading.setObjectName("rankColumnTitle")
            heading.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            self.project_focus_layout.addWidget(heading)
            labels: list[QLabel] = []
            for _ in range(3):
                item_label = QLabel("-")
                item_label.setObjectName("rankItem")
                item_label.setWordWrap(True)
                self.project_focus_layout.addWidget(item_label)
                labels.append(item_label)
            self.project_focus_sections.append((heading, labels))
        self.project_focus_widget.hide()
        quick_layout.addWidget(self.project_focus_widget)
        quick_layout.addStretch(1)

        self.submitted_budget_title = QLabel("Top 5 Total Submitted - Budgets (YTD)")
        self.submitted_budget_title.setObjectName("rankColumnTitle")
        self.submitted_budget_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.top_customers_grid.addWidget(self.submitted_budget_title, 0, 0)

        self.submitted_proposal_title = QLabel("Top 5 Total Submitted - Proposals (YTD)")
        self.submitted_proposal_title.setObjectName("rankColumnTitle")
        self.submitted_proposal_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.top_customers_grid.addWidget(self.submitted_proposal_title, 0, 1)

        self.top_sell_labels: list[QLabel] = []
        self.top_awarded_labels: list[QLabel] = []
        for idx in range(5):
            sell_lbl = QLabel(f"{idx + 1}. -")
            sell_lbl.setObjectName("rankItem")
            sell_lbl.setWordWrap(True)
            self.top_customers_grid.addWidget(sell_lbl, idx + 1, 0)
            self.top_sell_labels.append(sell_lbl)

            awarded_lbl = QLabel(f"{idx + 1}. -")
            awarded_lbl.setObjectName("rankItem")
            awarded_lbl.setWordWrap(True)
            self.top_customers_grid.addWidget(awarded_lbl, idx + 1, 1)
            self.top_awarded_labels.append(awarded_lbl)

        self.awarded_sell_title = QLabel("Top 5 by Awarded Sell Amount (YTD)")
        self.awarded_sell_title.setObjectName("rankColumnTitle")
        self.awarded_sell_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.top_customers_grid.addWidget(self.awarded_sell_title, 6, 0)

        self.win_rate_title = QLabel("Top 5 by Win Rate (YTD)")
        self.win_rate_title.setObjectName("rankColumnTitle")
        self.win_rate_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.top_customers_grid.addWidget(self.win_rate_title, 6, 1)

        self.top_awarded_sell_labels: list[QLabel] = []
        self.top_win_rate_labels: list[QLabel] = []
        for idx in range(5):
            awarded_sell_lbl = QLabel(f"{idx + 1}. -")
            awarded_sell_lbl.setObjectName("rankItem")
            awarded_sell_lbl.setWordWrap(True)
            self.top_customers_grid.addWidget(awarded_sell_lbl, idx + 7, 0)
            self.top_awarded_sell_labels.append(awarded_sell_lbl)

            win_rate_lbl = QLabel(f"{idx + 1}. -")
            win_rate_lbl.setObjectName("rankItem")
            win_rate_lbl.setWordWrap(True)
            self.top_customers_grid.addWidget(win_rate_lbl, idx + 7, 1)
            self.top_win_rate_labels.append(win_rate_lbl)

        self._update_top_customers_scope_buttons()
        self._update_top_customers_period_buttons()

        self.overview_grid.addWidget(self.summary_panel, 0, 0)
        self.overview_grid.addWidget(self.quick_panel, 0, 1)
        self.overview_grid.setColumnStretch(0, 3)
        self.overview_grid.setColumnStretch(1, 2)
        layout.addWidget(self.overview_panel)

        self.actions_title = QLabel("Quick Actions")
        self.actions_title.setObjectName("sectionTitle")
        self.actions_title.setFont(QFont("Segoe UI", 15, QFont.Weight.DemiBold))
        layout.addWidget(self.actions_title)

        self.actions_panel = QFrame()
        self.actions_panel.setObjectName("actionsPanel")
        self.actions_grid = QGridLayout(self.actions_panel)
        self.actions_grid.setContentsMargins(20, 20, 20, 20)
        self.actions_grid.setHorizontalSpacing(14)
        self.actions_grid.setVerticalSpacing(14)
        layout.addWidget(self.actions_panel)

        self.btn_bids = self._create_action_card(
            "Bids", "Open active bid pipeline and board views.", self._open_primary_workspace, True
        )
        self.btn_calendar = self._create_action_card(
            "Calendar", "Switch to calendar and due-date planning.", self.navigate_to_calendar.emit, True
        )
        self.btn_tasks = self._create_action_card(
            "Tasks", "Review task queue and next assignments.", self.navigate_to_tasks.emit, True
        )
        self.btn_vendors = self._create_action_card(
            "Vendors", "Manage vendor relationships and quotes.", self.navigate_to_vendors.emit, False
        )
        self.btn_customers = self._create_action_card(
            "Customers", "Access customer records and communication.", self.navigate_to_customers.emit, False
        )
        self.btn_my_company = self._create_action_card(
            "My Company", "Open company settings and account details.", self.navigate_to_my_company.emit, False
        )
        self.btn_preferences = self._create_action_card(
            "Preferences", "Adjust themes, defaults, and behavior.", self.navigate_to_preferences.emit, False
        )
        self.btn_quoted_lookup = self._create_action_card(
            "Quoted Lookup", "Find quoted door, frame, and hardware pricing matches.", self.navigate_to_quoted_lookup.emit, False
        )
        self.btn_fabrication = self._create_action_card(
            "Fabrication", "Manage prep codes, templates, and fabrication tools.", self.navigate_to_fabrication.emit, False
        )

        self._action_cards = [
            self.btn_bids,
            self.btn_calendar,
            self.btn_tasks,
            self.btn_vendors,
            self.btn_customers,
            self.btn_my_company,
            self.btn_preferences,
            self.btn_quoted_lookup,
            self.btn_fabrication,
        ]

        self._menu_buttons = [
            self.btn_bids,
            self.btn_calendar,
            self.btn_tasks,
            self.btn_vendors,
            self.btn_customers,
            self.btn_my_company,
            self.btn_preferences,
            self.btn_quoted_lookup,
            self.btn_fabrication,
        ]

        self._update_home_mode_buttons()
        self._apply_home_mode()
        self._update_responsive_metrics()

    def _on_recompute_kpis(self) -> None:
        self.refresh_overview_stats(time_budget_seconds=None)

    def _update_scope_toggle_buttons(self) -> None:
        scope = self._kpi_scope
        self.btn_scope_me.blockSignals(True)
        self.btn_scope_all.blockSignals(True)
        self.btn_scope_me.setChecked(scope == "me")
        self.btn_scope_all.setChecked(scope == "all")
        self.btn_scope_me.blockSignals(False)
        self.btn_scope_all.blockSignals(False)

    def _update_home_mode_buttons(self) -> None:
        self.btn_mode_bids.blockSignals(True)
        self.btn_mode_projects.blockSignals(True)
        self.btn_mode_bids.setChecked(self._home_mode == "bids")
        self.btn_mode_projects.setChecked(self._home_mode == "projects")
        self.btn_mode_bids.blockSignals(False)
        self.btn_mode_projects.blockSignals(False)

    def _set_home_mode(self, mode: str) -> None:
        new_mode = str(mode or "").strip().lower()
        if new_mode not in {"bids", "projects"}:
            return
        if new_mode == self._home_mode:
            return

        self._home_mode = new_mode
        self.settings.setValue("home_workspace_mode", new_mode)
        self._update_home_mode_buttons()
        self._apply_home_mode()
        self.refresh_overview_stats(time_budget_seconds=None)

    def _open_primary_workspace(self) -> None:
        if self._home_mode == "projects":
            self.navigate_to_projects.emit()
            return
        self.navigate_to_bids.emit()

    def _apply_home_mode(self) -> None:
        in_projects = self._home_mode == "projects"
        if in_projects:
            self.hero_title.setText("Project Management")
            self.hero_subtitle.setText("Operational priorities, deadlines, and active project ownership")
            self.hero_open_bids.setText("Open Projects")
            self.summary_title.setText("Project Snapshot")
            self.actions_title.setText("Project Actions")
            self.quick_title.setText("Project Focus")
            self.btn_bids.setText("Projects\nOpen active project records and detail views.")
            self.btn_calendar.setText("Calendar\nReview due dates, milestones, and task deadlines.")
            self.btn_tasks.setText("Tasks\nWork your project task queue and assignments.")
            self.btn_vendors.setText("Vendors\nTrack vendors, subs, and external coordination.")
            self.btn_customers.setText("Customers\nReview customer records and communication history.")
            self.btn_my_company.setText("My Company\nManage internal contacts, PM roster, and defaults.")
            self.btn_preferences.setText("Preferences\nAdjust themes, defaults, and behavior.")
            self.btn_quoted_lookup.setText("Quoted Lookup\nFind quoted door, frame, and hardware pricing matches.")
        else:
            self.hero_title.setText("Home")
            self.hero_subtitle.setText("Your bids, tasks, and deadlines in one place")
            self.hero_open_bids.setText("Open Bids")
            self.summary_title.setText("This Week")
            self.actions_title.setText("Quick Actions")
            self.quick_title.setText("Top Customers")
            self.btn_bids.setText("Bids\nOpen active bid pipeline and board views.")
            self.btn_calendar.setText("Calendar\nSwitch to calendar and due-date planning.")
            self.btn_tasks.setText("Tasks\nReview task queue and next assignments.")
            self.btn_vendors.setText("Vendors\nManage vendor relationships and quotes.")
            self.btn_customers.setText("Customers\nAccess customer records and communication.")
            self.btn_my_company.setText("My Company\nOpen company settings and account details.")
            self.btn_preferences.setText("Preferences\nAdjust themes, defaults, and behavior.")
            self.btn_quoted_lookup.setText("Quoted Lookup\nFind quoted door, frame, and hardware pricing matches.")

        for widget in (
            self.btn_scope_me,
            self.btn_scope_all,
            self.btn_top_scope_me,
            self.btn_top_scope_all,
            self.btn_top_period_ytd,
            self.btn_top_period_all,
            self.submitted_budget_title,
            self.submitted_proposal_title,
            self.awarded_sell_title,
            self.win_rate_title,
        ):
            widget.setVisible(not in_projects)
        for label_group in (
            self.top_sell_labels,
            self.top_awarded_labels,
            self.top_awarded_sell_labels,
            self.top_win_rate_labels,
        ):
            for label in label_group:
                label.setVisible(not in_projects)
        self.project_focus_widget.setVisible(in_projects)

    def _set_kpi_scope(self, scope: str) -> None:
        new_scope = str(scope or "").strip().lower()
        if new_scope not in {"me", "all"}:
            return
        if new_scope == self._kpi_scope:
            return

        self._kpi_scope = new_scope
        self._top_customers_scope = new_scope
        self.settings.setValue("home_kpi_scope", new_scope)
        self.settings.setValue("home_top_customers_scope", new_scope)
        self._update_scope_toggle_buttons()
        self._update_top_customers_scope_buttons()
        self.refresh_overview_stats(time_budget_seconds=None)

    def _update_top_customers_period_buttons(self) -> None:
        period = self._top_customers_period
        self.btn_top_period_ytd.blockSignals(True)
        self.btn_top_period_all.blockSignals(True)
        self.btn_top_period_ytd.setChecked(period == "ytd")
        self.btn_top_period_all.setChecked(period == "all")
        self.btn_top_period_ytd.blockSignals(False)
        self.btn_top_period_all.blockSignals(False)

    def _set_top_customers_period(self, period: str) -> None:
        new_period = str(period or "").strip().lower()
        if new_period not in {"ytd", "all"}:
            return
        if new_period == self._top_customers_period:
            return

        self._top_customers_period = new_period
        self.settings.setValue("home_top_customers_period", new_period)
        self._update_top_customers_period_buttons()
        self.refresh_overview_stats(time_budget_seconds=None)

    def _update_top_customers_scope_buttons(self) -> None:
        scope = self._top_customers_scope
        self.btn_top_scope_me.blockSignals(True)
        self.btn_top_scope_all.blockSignals(True)
        self.btn_top_scope_me.setChecked(scope == "me")
        self.btn_top_scope_all.setChecked(scope == "all")
        self.btn_top_scope_me.blockSignals(False)
        self.btn_top_scope_all.blockSignals(False)

    def _set_top_customers_scope(self, scope: str) -> None:
        new_scope = str(scope or "").strip().lower()
        if new_scope not in {"me", "all"}:
            return
        if new_scope == self._top_customers_scope:
            return

        self._top_customers_scope = new_scope
        self._kpi_scope = new_scope
        self.settings.setValue("home_top_customers_scope", new_scope)
        self.settings.setValue("home_kpi_scope", new_scope)
        self._update_top_customers_scope_buttons()
        self._update_scope_toggle_buttons()
        self.refresh_overview_stats(time_budget_seconds=None)

    def _apply_tab_order(self) -> None:
        pairs = [
            (self.hero_open_bids, self.hero_open_tasks),
            (self.hero_open_tasks, self.btn_mode_bids),
            (self.btn_mode_bids, self.btn_mode_projects),
            (self.btn_mode_projects, self.btn_scope_me),
            (self.btn_scope_me, self.btn_scope_all),
            (self.btn_scope_all, self.btn_recompute_kpis),
            (self.btn_recompute_kpis, self.btn_top_scope_me),
            (self.btn_top_scope_me, self.btn_top_scope_all),
            (self.btn_top_scope_all, self.btn_top_period_ytd),
            (self.btn_top_period_ytd, self.btn_top_period_all),
            (self.btn_bids, self.btn_calendar),
            (self.btn_calendar, self.btn_tasks),
            (self.btn_tasks, self.btn_vendors),
            (self.btn_vendors, self.btn_customers),
            (self.btn_customers, self.btn_my_company),
            (self.btn_my_company, self.btn_preferences),
            (self.btn_preferences, self.btn_quoted_lookup),
            (self.btn_top_period_all, self.btn_bids),
            (self.btn_quoted_lookup, self.hero_open_bids),
        ]
        for first, second in pairs:
            if first.window() is second.window():
                QWidget.setTabOrder(first, second)

        self._tab_order_applied = True

    def _create_action_card(self, title: str, description: str, callback, primary: bool) -> QPushButton:
        button = QPushButton(f"{title}\n{description}")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        button.setProperty("role", "primary" if primary else "secondary")
        button.setProperty("class", "actionCard")
        button.clicked.connect(callback)
        return button

    def _create_quick_button(self, label: str, callback) -> QPushButton:
        button = QPushButton(label)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setMinimumHeight(38)
        button.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        button.setProperty("class", "quickButton")
        button.clicked.connect(callback)
        return button

    def _create_stat_card(self, title: str, detail: str) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(2)

        value_label = QLabel("0")
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        card_layout.addWidget(value_label)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        card_layout.addWidget(title_label)

        detail_label = QLabel(detail)
        detail_label.setObjectName("statDetail")
        detail_label.setWordWrap(True)
        detail_label.setFont(QFont("Segoe UI", 9))
        card_layout.addWidget(detail_label)

        card.setProperty("value_label", value_label)
        card.setProperty("title_label", title_label)
        card.setProperty("detail_label", detail_label)
        return card

    def _set_stat_card_text(self, card: QFrame, value_text: str, title: str, detail: str, alert: bool = False) -> None:
        value_label = card.property("value_label")
        title_label = card.property("title_label")
        detail_label = card.property("detail_label")
        if isinstance(value_label, QLabel):
            value_label.setText(value_text)
        if isinstance(title_label, QLabel):
            title_label.setText(title)
        if isinstance(detail_label, QLabel):
            detail_label.setText(detail)

        card.setProperty("alert", alert)
        card.style().unpolish(card)
        card.style().polish(card)

    def _week_bounds(self) -> tuple[date, date]:
        today = date.today()
        start = today.fromordinal(today.toordinal() - (today.isoweekday() - 1))
        end = date.fromordinal(start.toordinal() + 6)
        return start, end

    def _tasks_file_path(self) -> Path:
        username = str(self.settings.value("username", "") or "").strip()
        if not username:
            username = "default"
        safe_name = sanitize_name(username) or "default"
        return self.paths.root / f"tasks_{safe_name}.json"

    def _current_username(self) -> str:
        return str(self.settings.value("username", "") or "").strip()

    def _safe_read_bid_info(self, bid_path: Path) -> dict:
        fp = bid_path / "info.json"
        if not fp.exists() or not fp.is_file():
            return {}
        try:
            # Read with a hard cap to avoid full-file blocking reads on startup.
            max_bytes = 512_000
            with open(fp, "rb") as fh:
                raw = fh.read(max_bytes + 1)
            if len(raw) > max_bytes:
                return {}
            if not raw:
                return {}
            payload = json.loads(raw.decode("utf-8", errors="ignore"))
            return payload if isinstance(payload, dict) else {}
        except KeyboardInterrupt:
            # If a terminal interrupt occurs mid-refresh, treat this record as unread.
            return {}
        except Exception:
            return {}

    def _collect_project_records(self, time_budget_seconds: float | None = None) -> list[dict]:
        records = []
        started = time.monotonic()
        timed_out = False

        for project_path in list_projects(self.paths.projects):
            if time_budget_seconds is not None and (time.monotonic() - started > time_budget_seconds):
                timed_out = True
                break

            try:
                info = self._safe_read_bid_info(project_path)
            except KeyboardInterrupt:
                timed_out = True
                break
            due_dt = parse_due_date(str(info.get("due_date", "")).strip())
            created_dt = self._parse_iso_date(str(info.get("created_at", "")).strip())
            try:
                modified_dt = date.fromtimestamp(project_path.stat().st_mtime)
            except Exception:
                modified_dt = date.today()
            if created_dt is None:
                created_dt = modified_dt

            records.append({
                "name": project_path.name,
                "path": project_path,
                "due_date": due_dt,
                "created_date": created_dt,
                "modified_date": modified_dt,
                "project_manager": str(info.get("project_manager", "")).strip(),
                "status": str(info.get("status", "Active")).strip(),
            })

        self._kpi_scan_truncated = timed_out
        return records

    def _set_project_focus_section(self, section_index: int, title: str, rows: list[str]) -> None:
        if section_index < 0 or section_index >= len(self.project_focus_sections):
            return
        heading, labels = self.project_focus_sections[section_index]
        heading.setText(title)
        for idx, label in enumerate(labels):
            label.setText(rows[idx] if idx < len(rows) else "-")

    def _parse_iso_date(self, raw: str) -> date | None:
        text = str(raw or "").strip()
        if not text:
            return None
        text = text.replace("Z", "+00:00")
        try:
            return date.fromisoformat(text[:10])
        except Exception:
            return None

    def _parse_money(self, raw) -> float:
        if raw is None:
            return 0.0
        if isinstance(raw, (int, float)):
            return float(raw)
        txt = str(raw).strip()
        if not txt or txt == "-":
            return 0.0
        cleaned = re.sub(r"[^0-9.\-]", "", txt)
        if not cleaned:
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _format_currency_short(self, value: float) -> str:
        if value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        if value >= 1_000:
            return f"${value / 1_000:.1f}K"
        return f"${value:,.0f}"

    def _extract_customer_name(self, info: dict) -> str:
        raw_gcs = info.get("gcs", []) if isinstance(info, dict) else []
        if isinstance(raw_gcs, list):
            for item in raw_gcs:
                gc_name = str(item or "").strip()
                if gc_name:
                    return gc_name
        legacy_gc = str(info.get("gc", "") if isinstance(info, dict) else "").strip()
        return legacy_gc

    def _collect_user_bid_records(self, time_budget_seconds: float | None = None, scope_all: bool = False) -> list[dict]:
        username = self._current_username().lower()
        records = []
        started = time.monotonic()
        timed_out = False

        roots = [
            (self.paths.bids, "pending"),
            (self.paths.submitted, "submitted"),
            (self.paths.awarded, "awarded"),
        ]

        for root_path, fallback_status in roots:
            if not root_path.exists():
                continue

            for bid_path in sorted(root_path.iterdir()):
                if time_budget_seconds is not None and (time.monotonic() - started > time_budget_seconds):
                    timed_out = True
                    break

                if not bid_path.is_dir():
                    continue

                try:
                    info = self._safe_read_bid_info(bid_path)
                except KeyboardInterrupt:
                    timed_out = True
                    break
                if not scope_all:
                    estimator = str(info.get("estimator", "")).strip().lower()
                    if username:
                        if not estimator or estimator != username:
                            continue

                status = str(info.get("status", "")).strip().lower() or fallback_status
                due_dt = parse_due_date(str(info.get("due_date", "")).strip())

                created_dt = self._parse_iso_date(str(info.get("created_at", "")).strip())
                try:
                    modified_dt = date.fromtimestamp(bid_path.stat().st_mtime)
                except Exception:
                    modified_dt = date.today()
                if created_dt is None:
                    created_dt = modified_dt

                # Authoritative value only: manual override or explicit bid_total.
                manual_value = self._parse_money(info.get("manual_bid_total", None))
                if manual_value > 0.0:
                    value = manual_value
                else:
                    value = self._parse_money(info.get("bid_total", None))

                customer_name = self._extract_customer_name(info)
                proposal_type = str(info.get("proposal_type", "")).strip().lower()

                records.append({
                    "status": status,
                    "due_date": due_dt,
                    "created_date": created_dt,
                    "modified_date": modified_dt,
                    "value": value,
                    "customer": customer_name,
                    "proposal_type": proposal_type,
                })

            if timed_out:
                break

        # Projects promoted from awarded bids count toward bid KPIs (YTD Awarded, Win Rate, etc.)
        if not timed_out and self.paths.projects.exists():
            for project_path in sorted(self.paths.projects.iterdir()):
                if time_budget_seconds is not None and (time.monotonic() - started > time_budget_seconds):
                    timed_out = True
                    break

                if not project_path.is_dir():
                    continue

                try:
                    info = self._safe_read_bid_info(project_path)
                except KeyboardInterrupt:
                    timed_out = True
                    break
                promoted_at_raw = str(info.get("promoted_at", "")).strip()
                if not promoted_at_raw:
                    continue

                if not scope_all:
                    estimator = str(info.get("estimator", "")).strip().lower()
                    if username:
                        if not estimator or estimator != username:
                            continue

                award_dt = self._parse_iso_date(promoted_at_raw)
                try:
                    modified_dt = award_dt or date.fromtimestamp(project_path.stat().st_mtime)
                except Exception:
                    modified_dt = date.today()

                due_dt = parse_due_date(str(info.get("due_date", "")).strip())
                created_dt = self._parse_iso_date(str(info.get("created_at", "")).strip())
                if created_dt is None:
                    created_dt = modified_dt

                # Use contract_amount locked in at promotion; fall back to workbook/manual totals
                value = self._parse_money(info.get("contract_amount", None))
                if value <= 0.0:
                    value = self._parse_money(info.get("manual_bid_total", None))
                if value <= 0.0:
                    value = self._parse_money(info.get("bid_total", None))

                customer_name = self._extract_customer_name(info)
                proposal_type = str(info.get("proposal_type", "")).strip().lower()

                records.append({
                    "status": "awarded",
                    "due_date": due_dt,
                    "created_date": created_dt,
                    "modified_date": modified_dt,
                    "value": value,
                    "customer": customer_name,
                    "proposal_type": proposal_type,
                })

        self._kpi_scan_truncated = timed_out

        return records

    def _load_open_task_due_dates(self, scope_all: bool = False) -> list[date]:
        if scope_all:
            task_files = sorted(self.paths.root.glob("tasks_*.json"))
        else:
            task_file = self._tasks_file_path()
            task_files = [task_file] if task_file.exists() else []

        due_dates: list[date] = []
        for task_file in task_files:
            try:
                payload = json.loads(task_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
            if not isinstance(tasks, list):
                continue

            for task in tasks:
                if not isinstance(task, dict):
                    continue
                if bool(task.get("completed", False)):
                    continue
                due = parse_due_date(str(task.get("due_date", "")).strip())
                if due is not None:
                    due_dates.append(due)
        return due_dates

    def refresh_overview_stats(self, time_budget_seconds: float | None = None) -> None:
        if self._home_mode == "projects":
            self._refresh_project_overview_stats(time_budget_seconds=time_budget_seconds)
            return

        today = date.today()
        week_start, week_end = self._week_bounds()
        self.summary_period.setText(f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
        current_user = self._current_username()
        scope_all = self._kpi_scope == "all"
        scope_text = "All" if scope_all else "Me"
        if current_user:
            self.hero_context.setText(f"Signed in as {current_user} | KPI Scope: {scope_text}")
        else:
            self.hero_context.setText(f"No user selected | KPI Scope: {scope_text}")

        bid_records = self._collect_user_bid_records(time_budget_seconds=time_budget_seconds, scope_all=scope_all)
        active_statuses = {"pending", "takeoff", "revising"}
        year_start = date(today.year, 1, 1)

        active_bids = [r for r in bid_records if r["status"] in active_statuses]
        bid_due_dates = [r["due_date"] for r in active_bids if r["due_date"] is not None]
        task_due_dates = self._load_open_task_due_dates(scope_all=scope_all)

        bids_today = sum(1 for d in bid_due_dates if d == today)
        tasks_today = sum(1 for d in task_due_dates if d == today)

        bids_week = sum(1 for d in bid_due_dates if week_start <= d <= week_end)
        tasks_week = sum(1 for d in task_due_dates if week_start <= d <= week_end)

        overdue_bids = sum(1 for d in bid_due_dates if d < today)
        overdue_tasks = sum(1 for d in task_due_dates if d < today)
        overdue_total = overdue_bids + overdue_tasks

        open_tasks_count = len(task_due_dates)
        active_bids_count = len(active_bids)

        submitted_this_week = sum(
            1 for r in bid_records
            if r["status"] == "submitted" and week_start <= r["modified_date"] <= week_end
        )

        # Submitted-to-date includes bids currently submitted as well as those
        # already decided (awarded/archived) this year.
        submitted_to_date_statuses = {"submitted", "awarded", "archived"}
        submitted_ytd_records = [
            r for r in bid_records
            if r["status"] in submitted_to_date_statuses and year_start <= r["modified_date"] <= today
        ]
        submitted_budget_ytd_records = [
            r for r in submitted_ytd_records
            if str(r.get("proposal_type", "")).strip().lower() == "budget"
        ]
        submitted_proposal_ytd_records = [
            r for r in submitted_ytd_records
            if str(r.get("proposal_type", "")).strip().lower() == "proposal"
        ]
        submitted_open_ytd_records = [
            r for r in bid_records
            if r["status"] == "submitted" and year_start <= r["modified_date"] <= today
        ]
        ytd_submitted_value = sum(float(r["value"] or 0.0) for r in submitted_ytd_records)
        ytd_submitted_budget_value = sum(float(r["value"] or 0.0) for r in submitted_budget_ytd_records)
        ytd_submitted_proposal_value = sum(float(r["value"] or 0.0) for r in submitted_proposal_ytd_records)
        submitted_missing_values = sum(1 for r in submitted_ytd_records if float(r.get("value") or 0.0) <= 0.0)

        awarded_ytd_records = [
            r for r in bid_records
            if r["status"] == "awarded" and year_start <= r["modified_date"] <= today
        ]
        ytd_awarded_value = sum(float(r["value"] or 0.0) for r in awarded_ytd_records)
        awarded_missing_values = sum(1 for r in awarded_ytd_records if float(r.get("value") or 0.0) <= 0.0)

        wins_ytd = len(awarded_ytd_records)
        archived_ytd_records = [
            r for r in bid_records
            if r["status"] == "archived" and year_start <= r["modified_date"] <= today
        ]
        kills_ytd = len(archived_ytd_records)
        submitted_ytd_count = len(submitted_ytd_records)
        win_rate_denominator = len(submitted_open_ytd_records) + kills_ytd
        win_rate_ytd = (wins_ytd / win_rate_denominator * 100.0) if win_rate_denominator > 0 else 0.0

        three_months_ago = date.fromordinal(today.toordinal() - 90)
        aging_bids = sum(
            1 for r in bid_records
            if r["status"] == "submitted" and r["modified_date"] <= three_months_ago
        )

        submitted_budget_by_customer: dict[str, float] = defaultdict(float)
        submitted_proposal_by_customer: dict[str, float] = defaultdict(float)
        awarded_sell_by_customer: dict[str, float] = defaultdict(float)
        customer_awarded_count: dict[str, int] = defaultdict(int)
        customer_submitted_count: dict[str, int] = defaultdict(int)
        customer_archived_count: dict[str, int] = defaultdict(int)
        period_all = self._top_customers_period == "all"
        top_scope_all = self._top_customers_scope == "all"
        top_scope_tag = "ALL" if top_scope_all else "ME"
        period_tag = "ALL" if period_all else "YTD"
        sell_column_label = f"Top 5 Total Submitted - Budgets ({period_tag})"
        awarded_column_label = f"Top 5 Total Submitted - Proposals ({period_tag})"
        awarded_sell_label = f"Top 5 by Awarded Sell Amount ({period_tag})"
        win_rate_label = f"Top 5 by Win Rate ({period_tag})"
        self.quick_title.setText(f"Top Customers ({top_scope_tag})")
        self.submitted_budget_title.setText(sell_column_label)
        self.submitted_proposal_title.setText(awarded_column_label)
        self.awarded_sell_title.setText(awarded_sell_label)
        self.win_rate_title.setText(win_rate_label)

        top_customer_records = bid_records
        if top_scope_all != scope_all:
            primary_scan_truncated = self._kpi_scan_truncated
            top_customer_records = self._collect_user_bid_records(
                time_budget_seconds=time_budget_seconds,
                scope_all=top_scope_all,
            )
            self._kpi_scan_truncated = primary_scan_truncated or self._kpi_scan_truncated

        for record in top_customer_records:
            customer_name = str(record.get("customer", "")).strip()
            if not customer_name:
                continue

            in_period = period_all or (year_start <= record["modified_date"] <= today)
            if not in_period:
                continue
            if record["status"] not in submitted_to_date_statuses:
                continue

            proposal_type = str(record.get("proposal_type", "")).strip().lower()
            amount = float(record.get("value", 0.0) or 0.0)
            if proposal_type == "budget":
                submitted_budget_by_customer[customer_name] += amount
            elif proposal_type == "proposal":
                submitted_proposal_by_customer[customer_name] += amount

            if record["status"] == "awarded":
                awarded_sell_by_customer[customer_name] += amount
                customer_awarded_count[customer_name] += 1
            elif record["status"] == "submitted":
                customer_submitted_count[customer_name] += 1
            elif record["status"] == "archived":
                customer_archived_count[customer_name] += 1

        top_sell = sorted(
            submitted_budget_by_customer.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )[:5]
        top_awarded = sorted(
            submitted_proposal_by_customer.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )[:5]

        top_awarded_sell = sorted(
            awarded_sell_by_customer.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )[:5]

        win_rate_rows: list[tuple[str, float, int, int]] = []
        customers_for_win_rate = set(customer_awarded_count) | set(customer_submitted_count) | set(customer_archived_count)
        for customer_name in customers_for_win_rate:
            submitted_count = int(customer_submitted_count.get(customer_name, 0))
            archived_count = int(customer_archived_count.get(customer_name, 0))
            awarded_count = int(customer_awarded_count.get(customer_name, 0))
            base_denominator = submitted_count + archived_count
            if base_denominator <= 0 and awarded_count <= 0:
                continue

            denominator = base_denominator if base_denominator > 0 else awarded_count
            rate = (awarded_count / denominator) * 100.0
            win_rate_rows.append((customer_name, rate, awarded_count, denominator))

        top_win_rate = sorted(
            win_rate_rows,
            key=lambda item: (-item[1], -item[3], item[0].lower()),
        )[:5]

        for idx, label in enumerate(self.top_sell_labels):
            if idx < len(top_sell):
                name, amount = top_sell[idx]
                label.setText(f"{idx + 1}. {name}  -  {self._format_currency_short(float(amount))}")
            else:
                label.setText(f"{idx + 1}. -")

        for idx, label in enumerate(self.top_awarded_labels):
            if idx < len(top_awarded):
                name, amount = top_awarded[idx]
                label.setText(f"{idx + 1}. {name}  -  {self._format_currency_short(float(amount))}")
            else:
                label.setText(f"{idx + 1}. -")

        for idx, label in enumerate(self.top_awarded_sell_labels):
            if idx < len(top_awarded_sell):
                name, amount = top_awarded_sell[idx]
                label.setText(f"{idx + 1}. {name}  -  {self._format_currency_short(float(amount))}")
            else:
                label.setText(f"{idx + 1}. -")

        for idx, label in enumerate(self.top_win_rate_labels):
            if idx < len(top_win_rate):
                name, rate, awarded_count, denominator = top_win_rate[idx]
                label.setText(f"{idx + 1}. {name}  -  {rate:.0f}% ({awarded_count}/{denominator})")
            else:
                label.setText(f"{idx + 1}. -")

        self._set_stat_card_text(
            self.kpi_cards["overdue"],
            str(overdue_total),
            "Overdue Items",
            f"{overdue_bids} bids, {overdue_tasks} tasks.",
            alert=overdue_total > 0,
        )
        self._set_stat_card_text(
            self.kpi_cards["due_today"],
            str(bids_today + tasks_today),
            "Due Today",
            f"{bids_today} bids, {tasks_today} tasks.",
        )
        self._set_stat_card_text(
            self.kpi_cards["due_week"],
            str(bids_week + tasks_week),
            "Due This Week",
            f"{bids_week} bids, {tasks_week} tasks due by Sunday.",
        )
        self._set_stat_card_text(
            self.kpi_cards["open_tasks"],
            str(open_tasks_count),
            f"Open Tasks ({'All' if scope_all else 'My'})",
            "Incomplete tasks across all users." if scope_all else "Incomplete tasks assigned to you.",
        )
        self._set_stat_card_text(
            self.kpi_cards["active_bids"],
            str(active_bids_count),
            f"Active Bids ({'All' if scope_all else 'My'})",
            "Pending, Takeoff, and Revising statuses.",
        )
        self._set_stat_card_text(
            self.kpi_cards["submitted_week"],
            str(submitted_this_week),
            "Submitted This Week",
            "Based on submitted bid folder activity.",
        )
        self._set_stat_card_text(
            self.kpi_cards["ytd_submitted"],
            self._format_currency_short(ytd_submitted_value),
            "YTD Submitted",
            (
                f"Proposals {self._format_currency_short(ytd_submitted_proposal_value)} ({len(submitted_proposal_ytd_records)}), "
                f"Budgets {self._format_currency_short(ytd_submitted_budget_value)} ({len(submitted_budget_ytd_records)})."
                if submitted_missing_values == 0
                else (
                    f"Proposals {self._format_currency_short(ytd_submitted_proposal_value)} ({len(submitted_proposal_ytd_records)}), "
                    f"Budgets {self._format_currency_short(ytd_submitted_budget_value)} ({len(submitted_budget_ytd_records)}), "
                    f"{submitted_missing_values} missing totals."
                )
            ),
        )
        self._set_stat_card_text(
            self.kpi_cards["win_rate_ytd"],
            f"{win_rate_ytd:.0f}%",
            "Win Rate YTD",
            f"{wins_ytd} awarded / ({len(submitted_open_ytd_records)} submitted + {kills_ytd} archived) in {today.year}.",
        )
        self._set_stat_card_text(
            self.kpi_cards["ytd_awarded"],
            self._format_currency_short(ytd_awarded_value),
            "YTD Awarded",
            (
                f"{len(awarded_ytd_records)} awarded bids in {today.year}."
                if awarded_missing_values == 0
                else f"{len(awarded_ytd_records)} awarded ({awarded_missing_values} missing totals)."
            ),
        )
        self._set_stat_card_text(
            self.kpi_cards["aging"],
            str(aging_bids),
            "Aging Bids",
            "Submitted over 3 months ago and not archived.",
            alert=aging_bids > 0,
        )

        if self._kpi_scan_truncated:
            self.summary_period.setText(
                f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')} (partial scan)"
            )

    def _refresh_project_overview_stats(self, time_budget_seconds: float | None = None) -> None:
        today = date.today()
        week_start, week_end = self._week_bounds()
        self.summary_period.setText(f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
        current_user = self._current_username()
        scope_text = "Projects"
        if current_user:
            self.hero_context.setText(f"Signed in as {current_user} | Workspace: {scope_text}")
        else:
            self.hero_context.setText(f"No user selected | Workspace: {scope_text}")

        project_records = self._collect_project_records(time_budget_seconds=time_budget_seconds)
        task_due_dates = self._load_open_task_due_dates(scope_all=self._kpi_scope == "all")
        project_due_dates = [r["due_date"] for r in project_records if r["due_date"] is not None]
        year_start = date(today.year, 1, 1)
        month_start = date(today.year, today.month, 1)

        projects_today = sum(1 for d in project_due_dates if d == today)
        tasks_today = sum(1 for d in task_due_dates if d == today)
        projects_week = sum(1 for d in project_due_dates if week_start <= d <= week_end)
        tasks_week = sum(1 for d in task_due_dates if week_start <= d <= week_end)
        overdue_projects = sum(1 for d in project_due_dates if d < today)
        overdue_tasks = sum(1 for d in task_due_dates if d < today)
        open_tasks_count = len(task_due_dates)
        active_projects_count = len(project_records)
        projects_created_week = sum(1 for r in project_records if week_start <= r["created_date"] <= week_end)
        projects_created_ytd = sum(1 for r in project_records if year_start <= r["created_date"] <= today)
        assigned_pm_count = sum(1 for r in project_records if r["project_manager"])
        pm_coverage = (assigned_pm_count / active_projects_count * 100.0) if active_projects_count else 0.0
        due_this_month = sum(1 for d in project_due_dates if month_start <= d <= today)
        stale_projects = sum(1 for r in project_records if (today.toordinal() - r["modified_date"].toordinal()) >= 30)
        missing_due = sum(1 for r in project_records if r["due_date"] is None)
        missing_pm = sum(1 for r in project_records if not r["project_manager"])

        pm_counts: dict[str, int] = defaultdict(int)
        for record in project_records:
            pm_name = record["project_manager"] or "Unassigned"
            pm_counts[pm_name] += 1
        top_pm_rows = [
            f"{idx + 1}. {name}  -  {count} active"
            for idx, (name, count) in enumerate(sorted(pm_counts.items(), key=lambda item: (-item[1], item[0].lower()))[:3])
        ]

        upcoming_rows = []
        upcoming_projects = sorted(
            [r for r in project_records if r["due_date"] is not None and r["due_date"] >= today],
            key=lambda record: (record["due_date"], record["name"].lower()),
        )[:3]
        for idx, record in enumerate(upcoming_projects):
            due_value = record["due_date"].strftime("%Y-%m-%d") if record["due_date"] is not None else "-"
            upcoming_rows.append(f"{idx + 1}. {record['name']}  -  {due_value}")

        gap_rows = []
        gap_candidates = [
            r for r in project_records
            if not r["project_manager"] or r["due_date"] is None
        ][:3]
        for idx, record in enumerate(gap_candidates):
            missing_bits = []
            if not record["project_manager"]:
                missing_bits.append("PM")
            if record["due_date"] is None:
                missing_bits.append("Due")
            gap_rows.append(f"{idx + 1}. {record['name']}  -  Missing {', '.join(missing_bits)}")

        self._set_project_focus_section(0, "Top PM Workloads", top_pm_rows)
        self._set_project_focus_section(1, "Due Next", upcoming_rows)
        self._set_project_focus_section(2, "Missing PM / Due Date", gap_rows)

        self._set_stat_card_text(
            self.kpi_cards["overdue"],
            str(overdue_projects + overdue_tasks),
            "Overdue Items",
            f"{overdue_projects} projects, {overdue_tasks} tasks.",
            alert=(overdue_projects + overdue_tasks) > 0,
        )
        self._set_stat_card_text(
            self.kpi_cards["due_today"],
            str(projects_today + tasks_today),
            "Due Today",
            f"{projects_today} projects, {tasks_today} tasks.",
        )
        self._set_stat_card_text(
            self.kpi_cards["due_week"],
            str(projects_week + tasks_week),
            "Due This Week",
            f"{projects_week} projects, {tasks_week} tasks due by Sunday.",
        )
        self._set_stat_card_text(
            self.kpi_cards["open_tasks"],
            str(open_tasks_count),
            "Open Tasks",
            "Incomplete tasks across your PM workflow.",
        )
        self._set_stat_card_text(
            self.kpi_cards["active_bids"],
            str(active_projects_count),
            "Active Projects",
            "Project records currently in the projects workspace.",
        )
        self._set_stat_card_text(
            self.kpi_cards["submitted_week"],
            str(projects_created_week),
            "Created This Week",
            "Projects added this week.",
        )
        self._set_stat_card_text(
            self.kpi_cards["ytd_submitted"],
            str(projects_created_ytd),
            "Created YTD",
            f"Projects created in {today.year}.",
        )
        self._set_stat_card_text(
            self.kpi_cards["win_rate_ytd"],
            f"{pm_coverage:.0f}%",
            "PM Coverage",
            f"{assigned_pm_count} of {active_projects_count} projects have a PM assigned.",
        )
        self._set_stat_card_text(
            self.kpi_cards["ytd_awarded"],
            str(due_this_month),
            "Due This Month",
            "Projects with due dates in the current month.",
        )
        self._set_stat_card_text(
            self.kpi_cards["aging"],
            str(stale_projects),
            "Stale Projects",
            f"{missing_pm} missing PM, {missing_due} missing due date.",
            alert=stale_projects > 0 or missing_pm > 0 or missing_due > 0,
        )

        if self._kpi_scan_truncated:
            self.summary_period.setText(
                f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')} (partial scan)"
            )

    def _get_week_span_label(self) -> str:
        today = QDate.currentDate()
        start = today.addDays(1 - today.dayOfWeek())
        end = start.addDays(6)
        return f"{start.toString('MMM d')} - {end.toString('MMM d, yyyy')}"

    def _clear_action_grid(self):
        while self.actions_grid.count():
            item = self.actions_grid.takeAt(0)
            if item is not None and item.widget() is not None:
                item.widget().setParent(self.actions_panel)

    def _relayout_action_cards(self, columns: int):
        columns = max(1, columns)
        if columns == self._action_columns:
            return

        self._action_columns = columns
        self._clear_action_grid()
        for idx, card in enumerate(self._action_cards):
            row = idx // columns
            col = idx % columns
            self.actions_grid.addWidget(card, row, col)

        for col in range(columns):
            self.actions_grid.setColumnStretch(col, 1)

    def _relayout_overview(self, columns: int):
        columns = 1 if columns <= 1 else 2
        if columns == self._overview_columns:
            return

        self._overview_columns = columns
        self.overview_grid.removeWidget(self.summary_panel)
        self.overview_grid.removeWidget(self.quick_panel)
        if columns == 1:
            self.overview_grid.addWidget(self.summary_panel, 0, 0)
            self.overview_grid.addWidget(self.quick_panel, 1, 0)
            self.overview_grid.setColumnStretch(0, 1)
        else:
            self.overview_grid.addWidget(self.summary_panel, 0, 0)
            self.overview_grid.addWidget(self.quick_panel, 0, 1)
            self.overview_grid.setColumnStretch(0, 3)
            self.overview_grid.setColumnStretch(1, 2)

    def _relayout_kpis(self, columns: int):
        columns = max(1, min(5, columns))
        if columns == self._kpi_columns:
            return

        self._kpi_columns = columns
        while self.kpi_grid.count():
            item = self.kpi_grid.takeAt(0)
            if item and item.widget():
                item.widget().setParent(self.summary_panel)

        cards = list(self.kpi_cards.values())
        for idx, card in enumerate(cards):
            row = idx // columns
            col = idx % columns
            self.kpi_grid.addWidget(card, row, col)

        for col in range(columns):
            self.kpi_grid.setColumnStretch(col, 1)

    def _update_responsive_metrics(self):
        width = max(480, self.width())
        height = max(480, self.height())

        margin = max(18, min(60, int(width * 0.05)))
        spacing = max(12, min(28, int(height * 0.02)))
        self.main_layout.setContentsMargins(margin, margin, margin, margin)
        self.main_layout.setSpacing(spacing)

        hero_padding = max(16, min(32, int(width * 0.02)))
        self.hero_layout.setContentsMargins(hero_padding, hero_padding, hero_padding, hero_padding)

        logo_width = max(130, min(220, int(width * 0.13)))
        if self._logo_source_pixmap is not None:
            self.logo_label.setPixmap(
                self._logo_source_pixmap.scaledToWidth(logo_width, Qt.TransformationMode.SmoothTransformation)
            )

        self.hero_open_bids.setMinimumHeight(max(34, min(42, int(height * 0.05))))
        self.hero_open_tasks.setMinimumHeight(max(34, min(42, int(height * 0.05))))

        if width < 1200:
            self._relayout_overview(1)
        else:
            self._relayout_overview(2)

        if width < 900:
            self._relayout_kpis(1)
        elif width < 1200:
            self._relayout_kpis(2)
        elif width < 1550:
            self._relayout_kpis(3)
        else:
            self._relayout_kpis(5)

        if width < 900:
            columns = 1
        elif width < 1320:
            columns = 2
        else:
            columns = 4
        self._relayout_action_cards(columns)

        button_width = max(220, min(420, int(width * 0.30)))
        button_height = max(68, min(100, int(height * 0.12)))
        for btn in self._menu_buttons:
            btn.setMinimumSize(button_width, button_height)

        self.hero_title.setFont(QFont("Segoe UI", max(20, min(30, int(width * 0.018))), QFont.Weight.Bold))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_metrics()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._tab_order_applied:
            self._apply_tab_order()
        QTimer.singleShot(0, lambda: self.refresh_overview_stats(time_budget_seconds=1.5))
        # Keep startup refresh bounded to prevent long UI stalls on large datasets.
        QTimer.singleShot(350, lambda: self.refresh_overview_stats(time_budget_seconds=2.0))
    
    def apply_theme(self, theme_colors: dict):
        """Apply theme colors to the home screen."""
        c = theme_colors

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['window_bg']};
                color: {c['text_primary']};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QFrame#heroPanel, QFrame#overviewPanel, QFrame#actionsPanel {{
                background-color: {c['panel_bg']};
                border: 1px solid {c['splitter']};
                border-radius: 14px;
            }}
            QFrame#summaryPanel, QFrame#quickPanel {{
                background-color: {c['window_bg']};
                border: 1px solid {c['splitter']};
                border-radius: 12px;
            }}
            QLabel#heroTitle {{
                color: {c['text_primary']};
                background: transparent;
            }}
            QLabel#heroSubtitle {{
                color: {c['text_secondary']};
                background: transparent;
            }}
            QLabel#heroContext {{
                color: {c['button_text']};
                background-color: {c['accent']};
                border-radius: 8px;
                padding: 4px 10px;
            }}
            QLabel#panelTitle {{
                color: {c['text_primary']};
                background: transparent;
            }}
            QLabel#rankColumnTitle {{
                color: {c['text_primary']};
                background: transparent;
                padding-bottom: 4px;
            }}
            QLabel#rankItem {{
                color: {c['text_secondary']};
                background: transparent;
                padding: 2px 0;
            }}
            QLabel#summaryPeriod, QLabel#statDetail {{
                color: {c['text_secondary']};
                background: transparent;
            }}
            QLabel#statValue {{
                color: {c['accent']};
                background: transparent;
            }}
            QLabel#statTitle {{
                color: {c['text_primary']};
                background: transparent;
            }}
            QFrame#statCard {{
                background-color: {c['panel_bg']};
                border: 1px solid {c['splitter']};
                border-radius: 10px;
            }}
            QFrame#statCard[alert="true"] {{
                border: 1px solid #C94F4F;
                background-color: rgba(201, 79, 79, 0.10);
            }}
            QFrame#statCard[alert="true"] QLabel#statValue {{
                color: #E57373;
            }}
            QLabel#sectionTitle {{
                color: {c['text_primary']};
            }}
            QPushButton[class="quickButton"] {{
                background-color: {c['hover_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['splitter']};
                border-radius: 8px;
                padding: 8px 12px;
                text-align: center;
            }}
            QPushButton[class="quickButton"]:hover {{
                border-color: {c['splitter_hover']};
                background-color: {c['panel_bg']};
            }}
            QPushButton[class="quickButton"]:focus {{
                border: 2px solid {c['accent']};
            }}
            QPushButton[class="scopeToggle"] {{
                background-color: {c['panel_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['splitter']};
                border-radius: 8px;
                padding: 6px 10px;
                font-weight: 700;
            }}
            QPushButton[class="scopeToggle"]:checked {{
                background-color: {c['accent']};
                color: {c['button_text']};
                border-color: {c['accent']};
            }}
            QPushButton[class="scopeToggle"]:hover {{
                border-color: {c['splitter_hover']};
            }}
            QPushButton[class="heroPrimary"] {{
                background-color: {c['accent']};
                color: {c['button_text']};
                border: 1px solid {c['accent']};
                border-radius: 9px;
                padding: 8px 14px;
                font-weight: 700;
            }}
            QPushButton[class="heroPrimary"]:hover {{
                background-color: {c['accent_hover']};
                border-color: {c['accent_hover']};
            }}
            QPushButton[class="heroSecondary"] {{
                background-color: {c['panel_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['splitter']};
                border-radius: 9px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton[class="heroSecondary"]:hover {{
                background-color: {c['hover_bg']};
                border-color: {c['splitter_hover']};
            }}
            QPushButton[class="actionCard"] {{
                text-align: left;
                border-radius: 12px;
                border: 1px solid {c['splitter']};
                padding: 14px 16px;
                line-height: 1.3;
                font-weight: 600;
            }}
            QPushButton[class="actionCard"]:focus {{
                border: 2px solid {c['accent']};
            }}
            QPushButton[class="actionCard"][role="primary"] {{
                background-color: {c['accent']};
                color: {c['button_text']};
                border-color: {c['accent']};
            }}
            QPushButton[class="actionCard"][role="primary"]:hover {{
                background-color: {c['accent_hover']};
                border-color: {c['accent_hover']};
            }}
            QPushButton[class="actionCard"][role="primary"]:pressed {{
                background-color: {c['accent']};
            }}
            QPushButton[class="actionCard"][role="secondary"] {{
                background-color: {c['panel_bg']};
                color: {c['text_primary']};
                border-color: {c['splitter']};
            }}
            QPushButton[class="actionCard"][role="secondary"]:hover {{
                background-color: {c['hover_bg']};
                border-color: {c['splitter_hover']};
            }}
            QPushButton[class="actionCard"][role="secondary"]:pressed {{
                background-color: {c['hover_bg']};
            }}
        """)

        self.logo_label.setStyleSheet(f"""
            QLabel {{
                color: {c['accent']};
                background: transparent;
            }}
        """)

