"""Prep-code lookup database.

Loads ``data/Prep_Codes.csv`` and exposes helpers for:
* category-filtered code lists (for dropdown delegates)
* code -> detail resolution  (for fab-sheet auto-populate)
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional


# Normalise category names used in the Hardware table's Category column
# to the canonical category names used in Prep_Codes.csv.
_CATEGORY_ALIASES: Dict[str, str] = {
    "hinge": "Hinge",
    "lock": "Locktype",
    "locktype": "Locktype",
    "panic": "Locktype",
    "flushbolt": "Flushbolt",
    "flush bolt": "Flushbolt",
    "oh stop": "Overhead Stop",
    "overhead stop": "Overhead Stop",
    "drop bottom": "Door Bottom",
    "door bottom": "Door Bottom",
    "hold open": "Hold Open",
    "lever cl": "Lever CL",
    "etw": "Lever CL",
}


class PrepCodeEntry:
    """One row from the prep-code database."""
    __slots__ = ("category", "code", "description", "size", "template", "lock_backset", "lock_strike_offset")

    def __init__(
        self,
        category: str,
        code: str,
        description: str,
        size: str,
        template: str,
        lock_backset: str = "",
        lock_strike_offset: str = "",
    ) -> None:
        self.category = category
        self.code = code
        self.description = description
        self.size = size
        self.template = template
        self.lock_backset = lock_backset
        self.lock_strike_offset = lock_strike_offset


class LockModelEntry:
    """One row from the lock-models database."""
    __slots__ = ("locktype", "model", "description", "size", "template")

    def __init__(self, locktype: str, model: str, description: str, size: str, template: str) -> None:
        self.locktype = locktype
        self.model = model
        self.description = description
        self.size = size
        self.template = template


class PrepCodeDB:
    """In-memory prep-code database loaded from a CSV file."""

    def __init__(self) -> None:
        self._entries: List[PrepCodeEntry] = []
        self._by_code: Dict[str, PrepCodeEntry] = {}
        self._by_category: Dict[str, List[PrepCodeEntry]] = {}
        self._lock_models: List[LockModelEntry] = []
        self._lock_models_by_type: Dict[str, List[LockModelEntry]] = {}

    # ── Loading ─────────────────────────────────────────────────────

    @classmethod
    def from_csv(cls, csv_path: Path) -> "PrepCodeDB":
        db = cls()
        if not csv_path.exists():
            return db
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat = (row.get("Category") or "").strip()
                code = (row.get("Code") or "").strip()
                desc = (row.get("Description") or "").strip()
                size = (row.get("Size") or "").strip()
                tmpl = (row.get("Template") or "").strip()
                lbs = (row.get("Lock Backset") or "").strip()
                lso = (row.get("Strike Offset") or "").strip()
                if not code:
                    continue
                entry = PrepCodeEntry(cat, code, desc, size, tmpl, lbs, lso)
                db._entries.append(entry)
                db._by_code[code.upper()] = entry
                db._by_category.setdefault(cat, []).append(entry)
        # Load lock models from companion CSV
        lock_csv = csv_path.parent / "Lock_Models.csv"
        if lock_csv.exists():
            with open(lock_csv, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    lt = (row.get("Locktype") or "").strip()
                    model = (row.get("Model") or "").strip()
                    desc = (row.get("Description") or "").strip()
                    size = (row.get("Size") or "").strip()
                    tmpl = (row.get("Template") or "").strip()
                    if not model:
                        continue
                    lm = LockModelEntry(lt, model, desc, size, tmpl)
                    db._lock_models.append(lm)
                    db._lock_models_by_type.setdefault(lt.upper(), []).append(lm)
        return db

    @classmethod
    def load_default(cls) -> "PrepCodeDB":
        """Load from the standard ``data/Prep_Codes.csv`` location."""
        csv_path = Path(__file__).resolve().parent.parent / "data" / "Prep_Codes.csv"
        return cls.from_csv(csv_path)

    # ── Queries ─────────────────────────────────────────────────────

    def lookup(self, code: str) -> Optional[PrepCodeEntry]:
        """Look up a single prep code (case-insensitive)."""
        return self._by_code.get(code.strip().upper())

    def codes_for_category(self, hw_category: str) -> List[str]:
        """Return the list of prep codes valid for a hardware category.

        *hw_category* is the value from the Hardware table's Category
        column (e.g. "Hinge", "Lock", "FlushBolt").  It is normalised
        via ``_CATEGORY_ALIASES`` before lookup.
        """
        canonical = _CATEGORY_ALIASES.get(hw_category.strip().lower(), "")
        entries = self._by_category.get(canonical, [])
        return [e.code for e in entries]

    def descriptions_for_category(self, category: str) -> List[str]:
        """Return unique Description values for a category (e.g. 'Hinge')."""
        entries = self._by_category.get(category, [])
        seen: set[str] = set()
        result: List[str] = []
        for e in entries:
            if e.description and e.description not in seen:
                seen.add(e.description)
                result.append(e.description)
        return result

    def entry_by_description(self, category: str, description: str) -> Optional[PrepCodeEntry]:
        """Find the first entry matching a category + description."""
        desc_upper = description.strip().upper()
        for e in self._by_category.get(category, []):
            if e.description.upper() == desc_upper:
                return e
        return None

    def all_categories(self) -> List[str]:
        return list(self._by_category.keys())

    def locktype_descriptions(self) -> List[str]:
        """Return Locktype Description values from Prep_Codes.csv.

        These serve as the subcategory names (MORTISE, CYLINDRICAL, etc.)
        that populate the Lock Type dropdown on the fab sheet.
        """
        entries = self._by_category.get("Locktype", [])
        return [e.description for e in entries if e.description]

    def models_for_locktype(self, locktype_desc: str) -> List[LockModelEntry]:
        """Return Lock_Models.csv entries for a locktype description."""
        return list(self._lock_models_by_type.get(locktype_desc.strip().upper(), []))

    def resolve_for_fab_sheet(self, prep_string: str) -> Dict[str, str]:
        """Given a canonical prep string (e.g. 'H45+LMOR+DB411'),
        resolve each code and return a dict of fab-sheet field overrides.

        The returned keys match the field names used in FabSheetCanvas.
        """
        if not prep_string:
            return {}

        codes = [c.strip() for c in prep_string.split("+") if c.strip()]
        result: Dict[str, str] = {}

        for code in codes:
            entry = self.lookup(code)
            if not entry:
                continue
            cat = entry.category

            if cat == "Hinge":
                result["hinge_type"] = entry.description
                result["hinge_size"] = entry.size
                result["hinge_template"] = entry.template
                result["dspec_hinges"] = entry.description
            elif cat == "Locktype":
                result["lock_type"] = entry.description
                result["lock_template"] = entry.template
                result["mach_lock_type"] = entry.description
                result["dspec_locktype"] = entry.description
                if entry.lock_backset:
                    result["lock_backset"] = entry.lock_backset
                if entry.lock_strike_offset:
                    result["lock_strike_offset"] = entry.lock_strike_offset
            elif cat == "Door Bottom":
                result["mach_door_bottom"] = entry.description
                result["dspec_door_bottom"] = entry.description
            elif cat == "Flushbolt":
                result["mach_flushbolt"] = entry.description
                result["dspec_flushbolt"] = entry.description
            elif cat == "Overhead Stop":
                result["mach_overhead_stop"] = entry.description
                result["dspec_overhead_stop"] = entry.description
            elif cat == "Hold Open":
                pass  # future use
            elif cat == "Lever CL":
                result["lock_cl_floor"] = entry.description
                result["frame_floor_to_lever_cl"] = entry.size if entry.size else entry.description

        return result
