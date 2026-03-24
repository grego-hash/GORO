"""Hardware Configurator wizard dialog."""

import json

from PyQt6.QtCore import Qt, QSortFilterProxyModel, QStringListModel
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QCompleter,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.constants import ORG_NAME, APP_NAME
from core.hw_configurator_db import (
    assemble_description,
    assemble_part_number,
    delete_favorite,
    get_families,
    get_family,
    get_favorites,
    get_list_price,
    get_manufacturers,
    get_slots,
    get_valid_options,
    init_db,
    save_favorite,
)


# ------------------------------------------------------------------
# Searchable combo box — editable with live substring filtering
# ------------------------------------------------------------------

class SearchableComboBox(QComboBox):
    """A QComboBox that filters its dropdown list as the user types."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Completer with substring (contains) matching
        self._completer = QCompleter(self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self.setCompleter(self._completer)

        # Update completer model whenever items change
        self.model().dataChanged.connect(self._sync_completer)
        self.model().rowsInserted.connect(self._sync_completer)
        self.model().rowsRemoved.connect(self._sync_completer)

    def _sync_completer(self, *_args):
        items = [self.itemText(i) for i in range(self.count())]
        model = QStringListModel(items, self)
        self._completer.setModel(model)

    def focusInEvent(self, event):
        """Select all text on focus so user can start typing immediately."""
        super().focusInEvent(event)
        self.lineEdit().selectAll()


class HardwareConfiguratorDialog(QDialog):
    """Wizard dialog for configuring a hardware part from the rules DB."""

    # Sentinel for the Favorites pseudo-manufacturer
    _FAV_SENTINEL = "__FAVORITES__"

    def __init__(self, parent=None, *, edit_family_id: int | None = None,
                 edit_selections: dict[str, str] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Configurator")
        self.setMinimumSize(540, 600)

        self._family_id: int | None = None
        self._slot_combos: dict[str, SearchableComboBox] = {}
        self._slot_rows: dict[str, tuple[QLabel, QWidget]] = {}
        self._required_slots: set[str] = set()
        self._refreshing: bool = False

        # Populated on accept
        self.result_data: dict | None = None

        # Current user (for favorites)
        from PyQt6.QtCore import QSettings
        settings = QSettings(ORG_NAME, APP_NAME)
        self._username = str(settings.value("username", "") or "").strip()

        init_db()
        self._build_ui()
        self._load_manufacturers()

        # If editing an existing configured part, restore state
        if edit_family_id is not None:
            self._restore_edit_state(edit_family_id, edit_selections or {})

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -- Product selection --
        top_group = QGroupBox("Product Selection")
        top_form = QFormLayout(top_group)

        self.mfr_combo = SearchableComboBox()
        self.mfr_combo.currentIndexChanged.connect(self._on_manufacturer_changed)
        top_form.addRow("Manufacturer:", self.mfr_combo)

        self.family_combo = SearchableComboBox()
        self.family_combo.currentIndexChanged.connect(self._on_family_changed)
        top_form.addRow("Product Family:", self.family_combo)

        layout.addWidget(top_group)

        # -- Favorites panel (shown when ★ Favorites is selected) --
        self._fav_group = QGroupBox("Saved Favorites")
        fav_layout = QVBoxLayout(self._fav_group)
        self._fav_list = QListWidget()
        self._fav_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._fav_list.itemDoubleClicked.connect(self._on_fav_double_clicked)
        fav_layout.addWidget(self._fav_list)

        fav_btn_row = QHBoxLayout()
        self._fav_load_btn = QPushButton("Load")
        self._fav_load_btn.clicked.connect(self._load_selected_favorite)
        fav_btn_row.addWidget(self._fav_load_btn)
        self._fav_del_btn = QPushButton("Delete")
        self._fav_del_btn.clicked.connect(self._delete_selected_favorite)
        fav_btn_row.addWidget(self._fav_del_btn)
        fav_btn_row.addStretch()
        fav_layout.addLayout(fav_btn_row)

        self._fav_group.setVisible(False)
        layout.addWidget(self._fav_group)

        # -- Dynamic option slots --
        options_group = QGroupBox("Options")
        options_outer = QVBoxLayout(options_group)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._slots_container = QWidget()
        self._slots_layout = QFormLayout(self._slots_container)
        scroll.setWidget(self._slots_container)
        options_outer.addWidget(scroll)

        layout.addWidget(options_group, 1)

        # -- Preview panel --
        preview_group = QGroupBox("Preview")
        prev_form = QFormLayout(preview_group)

        self.preview_mfr = QLabel("")
        self.preview_part = QLabel("")
        self.preview_desc = QLabel("")
        self.preview_finish = QLabel("")
        self.preview_category = QLabel("")
        self.preview_price = QLabel("")

        for lbl in (
            self.preview_mfr,
            self.preview_part,
            self.preview_desc,
            self.preview_finish,
            self.preview_category,
            self.preview_price,
        ):
            lbl.setWordWrap(True)

        prev_form.addRow("Manufacturer:", self.preview_mfr)
        prev_form.addRow("Part Number:", self.preview_part)
        prev_form.addRow("Description:", self.preview_desc)
        prev_form.addRow("Finish:", self.preview_finish)
        prev_form.addRow("Category:", self.preview_category)
        prev_form.addRow("List Price:", self.preview_price)

        layout.addWidget(preview_group)

        # -- Buttons --
        btn_layout = QHBoxLayout()

        self.save_fav_btn = QPushButton("★ Save to Favorites")
        self.save_fav_btn.setEnabled(False)
        self.save_fav_btn.clicked.connect(self._on_save_favorite)
        btn_layout.addWidget(self.save_fav_btn)

        btn_layout.addStretch()

        self.add_btn = QPushButton("Add to Hardware")
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(self.add_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_manufacturers(self):
        self.mfr_combo.blockSignals(True)
        self.mfr_combo.clear()
        self.mfr_combo.addItem("-- Select Manufacturer --", None)
        # Pin Favorites at top if user has any
        if self._username:
            self.mfr_combo.addItem("★ Favorites", self._FAV_SENTINEL)
        for mfr in get_manufacturers():
            self.mfr_combo.addItem(mfr, mfr)
        self.mfr_combo.blockSignals(False)
        self.mfr_combo.setCurrentIndex(0)

    def _restore_edit_state(self, family_id: int, selections: dict[str, str]):
        """Pre-populate the dialog for editing an existing configured part."""
        family = get_family(family_id)
        if not family:
            return

        # Select the manufacturer
        mfr = family["manufacturer"]
        for i in range(self.mfr_combo.count()):
            if self.mfr_combo.itemData(i) == mfr:
                self.mfr_combo.setCurrentIndex(i)
                break

        # Select the product family
        for i in range(self.family_combo.count()):
            if self.family_combo.itemData(i) == family_id:
                self.family_combo.setCurrentIndex(i)
                break

        # Block signals during restoration to prevent cascade rebuilds
        for combo in self._slot_combos.values():
            combo.blockSignals(True)

        for slot_name, value in selections.items():
            combo = self._slot_combos.get(slot_name)
            if combo is None:
                continue
            for i in range(combo.count()):
                if combo.itemData(i) == value:
                    combo.setCurrentIndex(i)
                    break

        for combo in self._slot_combos.values():
            combo.blockSignals(False)

        self._refresh_all_slots()
        self._update_preview()

    # ------------------------------------------------------------------
    # Cascading selection handlers
    # ------------------------------------------------------------------

    def _on_manufacturer_changed(self):
        mfr = self.mfr_combo.currentData()

        is_fav = mfr == self._FAV_SENTINEL
        self._fav_group.setVisible(is_fav)
        self.family_combo.setVisible(not is_fav)
        # Hide the "Product Family:" label in the form when showing favorites
        fam_label = self._find_form_label(self.family_combo)
        if fam_label is not None:
            fam_label.setVisible(not is_fav)

        if is_fav:
            self._populate_favorites_list()
            # Clear family / slots
            self.family_combo.blockSignals(True)
            self.family_combo.clear()
            self.family_combo.blockSignals(False)
            self._family_id = None
            self._build_slot_combos(None)
            self._update_preview()
            return

        self.family_combo.blockSignals(True)
        self.family_combo.clear()
        self.family_combo.addItem("-- Select Product Family --", None)
        if mfr:
            for fam in get_families(mfr):
                self.family_combo.addItem(fam["name"], fam["id"])
        self.family_combo.blockSignals(False)
        self.family_combo.setCurrentIndex(0)
        self._on_family_changed()

    def _on_family_changed(self):
        family_id = self.family_combo.currentData()
        self._family_id = family_id
        self._build_slot_combos(family_id)
        self._update_preview()

    # ------------------------------------------------------------------
    # Dynamic slot UI
    # ------------------------------------------------------------------

    def _build_slot_combos(self, family_id):
        """Rebuild the dynamic slot combo boxes for the selected family."""
        # Clear existing rows
        while self._slots_layout.rowCount() > 0:
            self._slots_layout.removeRow(0)
        self._slot_combos.clear()
        self._slot_rows.clear()
        self._required_slots.clear()

        if not family_id:
            return

        slots = get_slots(family_id)
        for slot in slots:
            combo = SearchableComboBox()
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            combo.setProperty("slot_name", slot["slot_name"])
            combo.currentIndexChanged.connect(self._on_slot_changed)
            self._slot_combos[slot["slot_name"]] = combo

            if slot["required"]:
                self._required_slots.add(slot["slot_name"])

            label_text = slot["slot_label"]
            if slot["required"]:
                label_text += " *"
            label = QLabel(label_text)

            self._slots_layout.addRow(label, combo)
            self._slot_rows[slot["slot_name"]] = (label, combo)

        # Populate all slots with initial options
        self._refresh_all_slots()

    def _get_current_selections(self) -> dict[str, str]:
        sels: dict[str, str] = {}
        for slot_name, combo in self._slot_combos.items():
            val = combo.currentData()
            if val:
                sels[slot_name] = val
        return sels

    def _refresh_all_slots(self):
        if not self._family_id or self._refreshing:
            return

        self._refreshing = True
        try:
            for combo in self._slot_combos.values():
                combo.blockSignals(True)

            selections = self._get_current_selections()
            slots = get_slots(self._family_id)

            for slot in slots:
                sname = slot["slot_name"]
                combo = self._slot_combos.get(sname)
                if combo is None:
                    continue

                valid = get_valid_options(self._family_id, sname, selections)
                label, widget = self._slot_rows.get(sname, (None, None))

                # Hide optional slots with no valid options
                if not slot["required"] and len(valid) == 0:
                    if label is not None:
                        label.setVisible(False)
                    combo.setVisible(False)
                    continue
                else:
                    if label is not None:
                        label.setVisible(True)
                    combo.setVisible(True)

                # Preserve current selection if still valid
                current_val = combo.currentData()

                combo.clear()
                placeholder = (
                    "-- Please Select --" if slot["required"] else "-- Select --"
                )
                combo.addItem(placeholder, None)
                for opt in valid:
                    display = opt["display_name"] if opt["display_name"] else opt["value"]
                    combo.addItem(display, opt["value"])

                # Restore previous selection if still present
                if current_val:
                    for i in range(combo.count()):
                        if combo.itemData(i) == current_val:
                            combo.setCurrentIndex(i)
                            break

            for combo in self._slot_combos.values():
                combo.blockSignals(False)

            # Apply required-field styling
            self._apply_required_styling()
        finally:
            self._refreshing = False

    def _on_slot_changed(self):
        self._refresh_all_slots()
        self._update_preview()

    # ------------------------------------------------------------------
    # Required-field visual feedback
    # ------------------------------------------------------------------

    _STYLE_REQUIRED_EMPTY = (
        "SearchableComboBox { border: 1px solid #804040; "
        "background-color: #3a2020; }"
    )
    _STYLE_NORMAL = ""

    def _apply_required_styling(self):
        """Highlight required slots that have no selection."""
        selections = self._get_current_selections()
        for slot_name in self._required_slots:
            combo = self._slot_combos.get(slot_name)
            if combo is None:
                continue
            if slot_name not in selections:
                combo.setStyleSheet(self._STYLE_REQUIRED_EMPTY)
            else:
                combo.setStyleSheet(self._STYLE_NORMAL)

    # ------------------------------------------------------------------
    # Preview
    # ------------------------------------------------------------------

    def _update_preview(self):
        if not self._family_id:
            for lbl in (
                self.preview_mfr,
                self.preview_part,
                self.preview_desc,
                self.preview_finish,
                self.preview_category,
                self.preview_price,
            ):
                lbl.setText("")
            self.add_btn.setEnabled(False)
            self.save_fav_btn.setEnabled(False)
            return

        family = get_family(self._family_id)
        if not family:
            self.add_btn.setEnabled(False)
            self.save_fav_btn.setEnabled(False)
            return

        selections = self._get_current_selections()

        self.preview_mfr.setText(family["manufacturer"])
        self.preview_part.setText(assemble_part_number(self._family_id, selections))
        self.preview_desc.setText(assemble_description(self._family_id, selections))
        self.preview_category.setText(family["category"])

        # Show the finish display name if a "finish" slot exists
        finish_val = selections.get("finish", "")
        self.preview_finish.setText(finish_val)

        # Compute and display list price (if pricing data exists)
        list_price = get_list_price(self._family_id, selections)
        if list_price is not None:
            self.preview_price.setText(f"${list_price:,.2f}")
        else:
            self.preview_price.setText("")

        # Enable Add only when all required slots are filled
        slots = get_slots(self._family_id)
        all_required = all(
            slot["slot_name"] in selections
            for slot in slots
            if slot["required"]
        )
        self.add_btn.setEnabled(all_required)
        self.save_fav_btn.setEnabled(all_required and bool(self._username))

    # ------------------------------------------------------------------
    # Accept
    # ------------------------------------------------------------------

    def _on_accept(self):
        if not self._family_id:
            return

        family = get_family(self._family_id)
        if not family:
            return

        selections = self._get_current_selections()

        self.result_data = {
            "manufacturer": family["manufacturer"],
            "part_number": assemble_part_number(self._family_id, selections),
            "description": assemble_description(self._family_id, selections),
            "finish": selections.get("finish", ""),
            "category": family["category"],
            "list_price": get_list_price(self._family_id, selections),
            "family_id": self._family_id,
            "selections": dict(selections),
        }
        self.accept()

    # ------------------------------------------------------------------
    # Favorites helpers
    # ------------------------------------------------------------------

    def _find_form_label(self, widget):
        """Find the QLabel associated with *widget* in a QFormLayout."""
        parent = widget.parent()
        if parent is None:
            return None
        lay = parent.layout()
        if not isinstance(lay, QFormLayout):
            return None
        for row in range(lay.rowCount()):
            item = lay.itemAt(row, QFormLayout.ItemRole.FieldRole)
            if item is not None and item.widget() is widget:
                label_item = lay.itemAt(row, QFormLayout.ItemRole.LabelRole)
                if label_item is not None:
                    return label_item.widget()
        return None

    def _populate_favorites_list(self):
        """Fill the favorites QListWidget from DB for the current user."""
        self._fav_list.clear()
        if not self._username:
            return
        favs = get_favorites(self._username)
        for fav in favs:
            display = f"{fav['label']}  —  {fav['part_number']}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, fav)
            self._fav_list.addItem(item)

    def _on_fav_double_clicked(self, item: QListWidgetItem):
        """Double-clicking a favorite loads it immediately."""
        self._load_favorite_from_item(item)

    def _load_selected_favorite(self):
        """Load button handler."""
        items = self._fav_list.selectedItems()
        if not items:
            return
        self._load_favorite_from_item(items[0])

    def _load_favorite_from_item(self, item: QListWidgetItem):
        """Apply a saved favorite: jump to the correct manufacturer/family
        and restore all slot selections."""
        fav = item.data(Qt.ItemDataRole.UserRole)
        if not fav:
            return

        family_id = fav["family_id"]
        family = get_family(family_id)
        if not family:
            QMessageBox.warning(
                self,
                "Favorite Unavailable",
                "The product family for this favorite no longer exists.",
            )
            return

        mfr = family["manufacturer"]

        # Switch manufacturer combo (this triggers _on_manufacturer_changed)
        self.mfr_combo.blockSignals(True)
        for i in range(self.mfr_combo.count()):
            if self.mfr_combo.itemData(i) == mfr:
                self.mfr_combo.setCurrentIndex(i)
                break
        self.mfr_combo.blockSignals(False)

        # Rebuild the family dropdown for that manufacturer
        self.family_combo.blockSignals(True)
        self.family_combo.clear()
        self.family_combo.addItem("-- Select Product Family --", None)
        for f in get_families(mfr):
            self.family_combo.addItem(f["name"], f["id"])
        self.family_combo.blockSignals(False)

        # Select the correct family
        for i in range(self.family_combo.count()):
            if self.family_combo.itemData(i) == family_id:
                self.family_combo.setCurrentIndex(i)
                break

        # Build slots (triggers _on_family_changed path)
        self._family_id = family_id
        self._build_slot_combos(family_id)

        # Show the family/slots panels (hide favorites panel)
        self._fav_group.setVisible(False)
        self.family_combo.setVisible(True)
        fam_label = self._find_form_label(self.family_combo)
        if fam_label is not None:
            fam_label.setVisible(True)

        # Restore saved selections
        try:
            saved_sels = json.loads(fav.get("selections_json", "{}"))
        except (json.JSONDecodeError, TypeError):
            saved_sels = {}

        if saved_sels:
            for slot_name, value in saved_sels.items():
                combo = self._slot_combos.get(slot_name)
                if combo is None:
                    continue
                combo.blockSignals(True)
                for i in range(combo.count()):
                    if combo.itemData(i) == value:
                        combo.setCurrentIndex(i)
                        break
                combo.blockSignals(False)

            # Re-apply rules and update preview
            self._refresh_all_slots()

        self._update_preview()

    def _on_save_favorite(self):
        """Prompt for a label and save the current configuration."""
        if not self._family_id or not self._username:
            return

        family = get_family(self._family_id)
        if not family:
            return

        selections = self._get_current_selections()
        part_number = assemble_part_number(self._family_id, selections)

        label, ok = QInputDialog.getText(
            self,
            "Save Favorite",
            "Enter a name for this favorite:",
            text=part_number,
        )
        if not ok or not label.strip():
            return

        save_favorite(
            username=self._username,
            label=label.strip(),
            family_id=self._family_id,
            selections=selections,
            part_number=part_number,
            description=assemble_description(self._family_id, selections),
            manufacturer=family["manufacturer"],
            category=family["category"],
            finish=selections.get("finish", ""),
        )

        QMessageBox.information(self, "Saved", f"Favorite \"{label.strip()}\" saved.")

    def _delete_selected_favorite(self):
        """Delete the selected favorite from the list and DB."""
        items = self._fav_list.selectedItems()
        if not items:
            return
        fav = items[0].data(Qt.ItemDataRole.UserRole)
        if not fav:
            return

        reply = QMessageBox.question(
            self,
            "Delete Favorite",
            f"Delete favorite \"{fav['label']}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        delete_favorite(fav["id"])
        self._populate_favorites_list()
