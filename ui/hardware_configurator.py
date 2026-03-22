"""Hardware Configurator wizard dialog."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.hw_configurator_db import (
    assemble_description,
    assemble_part_number,
    get_families,
    get_family,
    get_manufacturers,
    get_slots,
    get_valid_options,
    init_db,
)


class HardwareConfiguratorDialog(QDialog):
    """Wizard dialog for configuring a hardware part from the rules DB."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Configurator")
        self.setMinimumSize(540, 500)

        self._family_id: int | None = None
        self._slot_combos: dict[str, QComboBox] = {}
        self._slot_rows: dict[str, tuple[QLabel, QWidget]] = {}

        # Populated on accept
        self.result_data: dict | None = None

        init_db()
        self._build_ui()
        self._load_manufacturers()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -- Product selection --
        top_group = QGroupBox("Product Selection")
        top_form = QFormLayout(top_group)

        self.mfr_combo = QComboBox()
        self.mfr_combo.currentIndexChanged.connect(self._on_manufacturer_changed)
        top_form.addRow("Manufacturer:", self.mfr_combo)

        self.family_combo = QComboBox()
        self.family_combo.currentIndexChanged.connect(self._on_family_changed)
        top_form.addRow("Product Family:", self.family_combo)

        layout.addWidget(top_group)

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

        for lbl in (
            self.preview_mfr,
            self.preview_part,
            self.preview_desc,
            self.preview_finish,
            self.preview_category,
        ):
            lbl.setWordWrap(True)

        prev_form.addRow("Manufacturer:", self.preview_mfr)
        prev_form.addRow("Part Number:", self.preview_part)
        prev_form.addRow("Description:", self.preview_desc)
        prev_form.addRow("Finish:", self.preview_finish)
        prev_form.addRow("Category:", self.preview_category)

        layout.addWidget(preview_group)

        # -- Buttons --
        btn_layout = QHBoxLayout()
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
        for mfr in get_manufacturers():
            self.mfr_combo.addItem(mfr, mfr)
        self.mfr_combo.blockSignals(False)
        self.mfr_combo.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # Cascading selection handlers
    # ------------------------------------------------------------------

    def _on_manufacturer_changed(self):
        mfr = self.mfr_combo.currentData()
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

        if not family_id:
            return

        slots = get_slots(family_id)
        for slot in slots:
            combo = QComboBox()
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            combo.setProperty("slot_name", slot["slot_name"])
            combo.currentIndexChanged.connect(self._on_slot_changed)
            self._slot_combos[slot["slot_name"]] = combo

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
        if not self._family_id:
            return

        selections = self._get_current_selections()
        slots = get_slots(self._family_id)

        for slot in slots:
            sname = slot["slot_name"]
            combo = self._slot_combos.get(sname)
            if not combo:
                continue

            valid = get_valid_options(self._family_id, sname, selections)
            label, widget = self._slot_rows.get(sname, (None, None))

            # Hide optional slots with no valid options
            if not slot["required"] and len(valid) == 0:
                if label:
                    label.setVisible(False)
                combo.setVisible(False)
                continue
            else:
                if label:
                    label.setVisible(True)
                combo.setVisible(True)

            # Preserve current selection if still valid
            current_val = combo.currentData()

            combo.blockSignals(True)
            combo.clear()
            combo.addItem("-- Select --", None)
            for opt in valid:
                display = opt["display_name"] if opt["display_name"] else opt["value"]
                combo.addItem(display, opt["value"])

            # Restore previous selection if still present
            if current_val:
                for i in range(combo.count()):
                    if combo.itemData(i) == current_val:
                        combo.setCurrentIndex(i)
                        break

            combo.blockSignals(False)

    def _on_slot_changed(self):
        self._refresh_all_slots()
        self._update_preview()

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
            ):
                lbl.setText("")
            self.add_btn.setEnabled(False)
            return

        family = get_family(self._family_id)
        if not family:
            self.add_btn.setEnabled(False)
            return

        selections = self._get_current_selections()

        self.preview_mfr.setText(family["manufacturer"])
        self.preview_part.setText(assemble_part_number(self._family_id, selections))
        self.preview_desc.setText(assemble_description(self._family_id, selections))
        self.preview_category.setText(family["category"])

        # Show the finish display name if a "finish" slot exists
        finish_val = selections.get("finish", "")
        self.preview_finish.setText(finish_val)

        # Enable Add only when all required slots are filled
        slots = get_slots(self._family_id)
        all_required = all(
            slot["slot_name"] in selections
            for slot in slots
            if slot["required"]
        )
        self.add_btn.setEnabled(all_required)

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
        }
        self.accept()
