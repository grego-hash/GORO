"""Fabrication Sheet data builder.

Groups schedule openings by (Door Type, canonical prep string) for
door machining / fabrication sheets.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _find_col(headers: List[str], candidates: List[str]) -> Optional[int]:
    """Return the index of the first matching header (case-insensitive)."""
    norm = {h.strip().lower(): i for i, h in enumerate(headers)}
    for c in candidates:
        idx = norm.get(c.strip().lower())
        if idx is not None:
            return idx
    return None


def _cell(row: List[str], idx: Optional[int]) -> str:
    if idx is None or idx >= len(row):
        return ""
    return (row[idx] or "").strip()


def compute_prep_string_from_csv(
    group_name: str,
    hw_groups_headers: List[str],
    hw_groups_rows: List[List[str]],
    hw_headers: List[str],
    hw_rows: List[List[str]],
) -> str:
    """Derive a canonical prep string for *group_name* from CSV data.

    Looks up every part assigned to the group via Part ID, reads its
    Prep Code from the hardware table, deduplicates, sorts, and joins
    with ``+``.
    """
    grp_idx = _find_col(hw_groups_headers, ["Hardware Group"])
    pid_idx = _find_col(hw_groups_headers, ["Part ID"])
    hw_pid_idx = _find_col(hw_headers, ["Part ID"])
    hw_prep_idx = _find_col(hw_headers, ["Prep Code"])
    if grp_idx is None or pid_idx is None or hw_pid_idx is None or hw_prep_idx is None:
        return ""

    # Build Part ID → Prep Code lookup from hardware rows
    prep_lookup: Dict[str, str] = {}
    for hr in hw_rows:
        pid = _cell(hr, hw_pid_idx)
        code = _cell(hr, hw_prep_idx)
        if pid and code:
            prep_lookup[pid] = code

    codes: set[str] = set()
    for row in hw_groups_rows:
        rg = _cell(row, grp_idx)
        if rg != group_name:
            continue
        pid = _cell(row, pid_idx)
        if pid and pid in prep_lookup:
            codes.add(prep_lookup[pid])

    return "+".join(sorted(codes))


# ── Fab-sheet grouping key ──────────────────────────────────────────

class FabSheetKey:
    """Immutable grouping key for a single fabrication sheet."""

    __slots__ = ("door_type", "prep_string")

    def __init__(self, door_type: str, prep_string: str) -> None:
        self.door_type = door_type
        self.prep_string = prep_string

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FabSheetKey):
            return NotImplemented
        return self.door_type == other.door_type and self.prep_string == other.prep_string

    def __hash__(self) -> int:
        return hash((self.door_type, self.prep_string))

    def label(self) -> str:
        if self.prep_string:
            return f"{self.door_type}  [{self.prep_string}]"
        return self.door_type or "(no door type)"


class FabSheetOpening:
    """One schedule opening that belongs to a fab sheet."""

    __slots__ = (
        "opening_number", "location", "building", "floor", "phase",
        "handing", "width", "height", "description",
        "rating_fire", "stc", "door_type", "material_type",
        "door_finish", "hardware_group", "frame_type",
        "frame_material", "frame_finish", "profile",
        "wall_tag", "wall_size", "count",
        "elevation", "inactive_elevation",
        "active_width", "inactive_width",
        "sidelite", "sidelite_2", "transom",
        "comments",
        "door_details",
        "lite_details",
    )

    def __init__(self, **kwargs: str) -> None:
        for slot in self.__slots__:
            if slot in ("door_details", "lite_details"):
                setattr(self, slot, kwargs.get(slot, {}))
            else:
                setattr(self, slot, kwargs.get(slot, ""))


class FabSheet:
    """All data for one fabrication sheet."""

    __slots__ = ("key", "openings")

    def __init__(self, key: FabSheetKey) -> None:
        self.key = key
        self.openings: List[FabSheetOpening] = []

    @property
    def door_type(self) -> str:
        return self.key.door_type

    @property
    def prep_string(self) -> str:
        return self.key.prep_string

    @property
    def door_numbers(self) -> List[str]:
        return [o.opening_number for o in self.openings if o.opening_number]

    # Convenience: first opening's common fields (all openings share Door Type)
    def first(self) -> Optional[FabSheetOpening]:
        return self.openings[0] if self.openings else None


# ── Column mapping helper ───────────────────────────────────────────

_OPENING_FIELD_MAP: List[Tuple[str, List[str]]] = [
    ("opening_number", ["Opening Number", "Opening", "Opening #", "Mark"]),
    ("location", ["Location"]),
    ("building", ["Building"]),
    ("floor", ["Floor"]),
    ("phase", ["Phase"]),
    ("handing", ["Handing", "Hand", "Swing"]),
    ("width", ["Width", "Door Width", "Nominal Width"]),
    ("height", ["Height", "Door Height", "Nominal Height"]),
    ("description", ["Description"]),
    ("rating_fire", ["Rating_Fire", "Fire Rating", "Rating"]),
    ("stc", ["STC"]),
    ("door_type", ["Door Type"]),
    ("material_type", ["Material Type"]),
    ("door_finish", ["Door Finish"]),
    ("hardware_group", ["Hardware Group"]),
    ("frame_type", ["Frame type", "Frame Type"]),
    ("frame_material", ["Frame Material"]),
    ("frame_finish", ["Frame Finish"]),
    ("profile", ["Profile"]),
    ("wall_tag", ["Wall Tag"]),
    ("wall_size", ["Wall Size"]),
    ("count", ["Count", "Qty"]),
    ("elevation", ["Elevation"]),
    ("inactive_elevation", ["Inactive Elevation"]),
    ("active_width", ["Active Width"]),
    ("inactive_width", ["Inactive Width", "Inactive Leaf Width", "Leaf 2 Width"]),
    ("sidelite", ["Sidelite"]),
    ("sidelite_2", ["Sidelite 2"]),
    ("transom", ["Transom"]),
    ("comments", ["Comments"]),
]


def build_fab_sheets(
    schedule_headers: List[str],
    schedule_rows: List[List[str]],
    hw_groups_headers: List[str],
    hw_groups_rows: List[List[str]],
    hw_headers: List[str],
    hw_rows: List[List[str]],
) -> List[FabSheet]:
    """Build an ordered list of :class:`FabSheet` from workbook CSV data."""

    # Resolve column indices for schedule fields
    col_map: Dict[str, Optional[int]] = {}
    for field, candidates in _OPENING_FIELD_MAP:
        col_map[field] = _find_col(schedule_headers, candidates)

    door_type_idx = col_map.get("door_type")
    hw_group_idx = col_map.get("hardware_group")

    # Pre-compute prep string per hardware group
    unique_groups: set[str] = set()
    for row in schedule_rows:
        g = _cell(row, hw_group_idx)
        if g:
            unique_groups.add(g)

    prep_cache: Dict[str, str] = {}
    for g in unique_groups:
        prep_cache[g] = compute_prep_string_from_csv(
            g, hw_groups_headers, hw_groups_rows, hw_headers, hw_rows,
        )

    # Group openings
    sheets_map: Dict[FabSheetKey, FabSheet] = {}
    sheet_order: List[FabSheetKey] = []

    for row in schedule_rows:
        dt = _cell(row, door_type_idx)
        if not dt:
            continue  # skip rows without a door type

        hw_grp = _cell(row, hw_group_idx)
        prep = prep_cache.get(hw_grp, "")
        key = FabSheetKey(dt, prep)

        if key not in sheets_map:
            sheets_map[key] = FabSheet(key)
            sheet_order.append(key)

        kwargs: Dict[str, str] = {}
        for field, _ in _OPENING_FIELD_MAP:
            kwargs[field] = _cell(row, col_map.get(field))

        sheets_map[key].openings.append(FabSheetOpening(**kwargs))

    result = [sheets_map[k] for k in sheet_order]
    return result


# Columns to exclude when building door_details for display
_DOOR_DETAIL_EXCLUDE = {
    "door type", "active width", "inactive width", "height",
    # cost / count / vendor columns
    "material cost", "glass cost", "kit cost", "freight",
    "field load & dist", "field hours", "unit material cost", "unit labor",
    "count", "counts", "quoted", "vendor",
    # lite / louver columns  (captured separately into lite_details)
    "glass", "glass thickness", "lite width", "lite height",
    "inactive lite width", "inactive lite height",
    "kit manf & mat'l", "lock stile", "stiles",
    "top rail", "bottom rail",
    "mid rail width", "mid rail top of door to cl",
    "inactive top rail", "inactive lock stile",
    "inactive mid rail width", "inactive mid rail top of door to cl",
    "factory glaze", "notes",
}

# Columns to capture into lite_details  (header-lower → fab-sheet key)
_LITE_COLUMN_MAP = {
    "kit manf & mat'l": "lite_kit",
    "glass thickness": "lite_glass_thickness",
    "lite width": "lite_width",
    "lite height": "lite_height",
    "lock stile": "lite_lockstile",
    "stiles": "lite_lockstile",          # Aluminum doors label
    "top rail": "lite_top_rail",
    "bottom rail": "lite_bottom_rail",
    "factory glaze": "lite_factory_glaze",
}


def _enrich_from_door_tables(sheets: List[FabSheet], workbook_path: Path) -> None:
    """Read door CSVs and fill active_width / inactive_width / door_details."""
    door_files = [
        "Hollow Metal Doors.csv", "Wood Doors.csv",
        "Aluminum Doors.csv", "Misc. Doors.csv",
    ]
    # Build Door Type -> (active_width, inactive_width, details_dict, lite_dict) lookup
    lookup: Dict[str, Tuple[str, str, Dict[str, str], Dict[str, str]]] = {}
    for fname in door_files:
        fp = workbook_path / fname
        if not fp.exists():
            continue
        with open(fp, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        if not rows:
            continue
        hdrs = rows[0]
        dt_idx = _find_col(hdrs, ["Door Type"])
        aw_idx = _find_col(hdrs, ["Active Width"])
        iw_idx = _find_col(hdrs, ["Inactive Width", "Inactive Leaf Width", "Leaf 2 Width"])
        if dt_idx is None:
            continue
        for r in rows[1:]:
            dt = _cell(r, dt_idx)
            if not dt or dt in lookup:
                continue
            aw = _cell(r, aw_idx) if aw_idx is not None else ""
            iw = _cell(r, iw_idx) if iw_idx is not None else ""
            # Collect all other non-excluded, non-empty columns
            details: Dict[str, str] = {}
            lite: Dict[str, str] = {}
            for ci, hdr in enumerate(hdrs):
                hdr_lower = hdr.strip().lower()
                if ci in (dt_idx, aw_idx, iw_idx):
                    continue
                val = _cell(r, ci)
                if not val or val in ("0", "FALSE", "0.00"):
                    continue
                # Lite/louver columns go into lite dict
                lite_key = _LITE_COLUMN_MAP.get(hdr_lower)
                if lite_key:
                    lite[lite_key] = val
                elif hdr_lower not in _DOOR_DETAIL_EXCLUDE:
                    details[hdr.strip()] = val
            lookup[dt] = (aw, iw, details, lite)

    for sheet in sheets:
        for o in sheet.openings:
            dt = o.door_type
            if dt in lookup:
                aw, iw, details, lite = lookup[dt]
                if not o.active_width and aw:
                    o.active_width = aw
                if not o.inactive_width and iw:
                    o.inactive_width = iw
                if not o.door_details and details:
                    o.door_details = details
                if not o.lite_details and lite:
                    o.lite_details = lite


def build_fab_sheets_from_files(
    workbook_path: Path,
) -> List[FabSheet]:
    """Convenience: read CSVs from a workbook folder and build sheets."""

    def _read(p: Path) -> Tuple[List[str], List[List[str]]]:
        if not p.exists():
            return [], []
        with open(p, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        if not rows:
            return [], []
        return rows[0], rows[1:]

    schedule_h, schedule_r = _read(workbook_path / "Schedule.csv")
    hw_h, hw_r = _read(workbook_path / "Hardware.csv")
    hwg_h, hwg_r = _read(workbook_path / "Hardware_Groups.csv")

    sheets = build_fab_sheets(schedule_h, schedule_r, hwg_h, hwg_r, hw_h, hw_r)
    _enrich_from_door_tables(sheets, workbook_path)
    return sheets
