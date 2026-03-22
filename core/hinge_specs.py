"""Hinge spec lookup table.

Loads manufacturer-based hinge machining specifications from
``data/Hinge_Specs.csv`` and provides a height-based lookup
(round up to nearest available height).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from core.seeded_data import ensure_seeded_csv

_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "Hinge_Specs.csv"

LOCK_COLUMNS = (
    "Cylindrical", "Mortise", "Rim_Panic",
    "CVR_Panic", "SVR_Panic", "Mortise_Panic", "Concealed_Cable",
)


@dataclass
class HingeSpec:
    manufacturer: str = ""
    height: int = 0
    d1: str = ""
    d2: str = ""
    d3: str = ""
    d4: str = ""
    cylindrical: str = ""
    mortise: str = ""
    rim_panic: str = ""
    cvr_panic: str = ""
    svr_panic: str = ""
    mortise_panic: str = ""
    concealed_cable: str = ""

    def lock_centerline(self, lock_type: str) -> str:
        """Return the lock centerline for a given lock type name."""
        key = lock_type.strip().lower().replace(" ", "_")
        mapping = {
            "cylindrical": self.cylindrical,
            "mortise": self.mortise,
            "rim_panic": self.rim_panic,
            "rim panic": self.rim_panic,
            "cvr_panic": self.cvr_panic,
            "cvr panic": self.cvr_panic,
            "svr_panic": self.svr_panic,
            "svr panic": self.svr_panic,
            "mortise_panic": self.mortise_panic,
            "mortise panic": self.mortise_panic,
            "concealed_cable": self.concealed_cable,
            "concealed cable": self.concealed_cable,
        }
        return mapping.get(key, "")


class HingeSpecDB:
    """In-memory hinge spec database loaded from CSV."""

    def __init__(self, rows: List[HingeSpec]) -> None:
        self._rows = rows
        # Index by manufacturer → sorted list of specs
        self._by_mfr: Dict[str, List[HingeSpec]] = {}
        for r in rows:
            self._by_mfr.setdefault(r.manufacturer, []).append(r)
        for specs in self._by_mfr.values():
            specs.sort(key=lambda s: s.height)

    # ── queries ─────────────────────────────────────────────────
    def manufacturers(self) -> List[str]:
        return sorted(self._by_mfr.keys())

    def lookup(self, manufacturer: str, height_inches: float) -> Optional[HingeSpec]:
        """Return the spec for *manufacturer* whose height >= *height_inches*.

        Rounds up to the nearest available height.  Returns ``None`` if the
        manufacturer is not found or height exceeds all entries.
        """
        specs = self._by_mfr.get(manufacturer)
        if not specs:
            return None
        for s in specs:
            if s.height >= height_inches:
                return s
        # height exceeds all entries → return the largest
        return specs[-1]

    def all_rows(self) -> List[HingeSpec]:
        return list(self._rows)

    # ── persistence ─────────────────────────────────────────────
    @classmethod
    def load(cls, path: Path | None = None) -> "HingeSpecDB":
        p = path or ensure_seeded_csv("Hinge_Specs.csv")
        rows: List[HingeSpec] = []
        if not p.exists():
            return cls(rows)
        with open(p, "r", encoding="utf-8-sig", newline="") as f:
            for rec in csv.DictReader(f):
                rows.append(HingeSpec(
                    manufacturer=rec.get("Manufacturer", "").strip(),
                    height=int(float(rec.get("Height", "0").strip() or "0")),
                    d1=rec.get("D1", "").strip(),
                    d2=rec.get("D2", "").strip(),
                    d3=rec.get("D3", "").strip(),
                    d4=rec.get("D4", "").strip(),
                    cylindrical=rec.get("Cylindrical", "").strip(),
                    mortise=rec.get("Mortise", "").strip(),
                    rim_panic=rec.get("Rim_Panic", "").strip(),
                    cvr_panic=rec.get("CVR_Panic", "").strip(),
                    svr_panic=rec.get("SVR_Panic", "").strip(),
                    mortise_panic=rec.get("Mortise_Panic", "").strip(),
                    concealed_cable=rec.get("Concealed_Cable", "").strip(),
                ))
        return cls(rows)

    @staticmethod
    def save(rows: List[HingeSpec], path: Path | None = None) -> None:
        p = path or _CSV_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "Manufacturer", "Height", "D1", "D2", "D3", "D4",
            "Cylindrical", "Mortise", "Rim_Panic",
            "CVR_Panic", "SVR_Panic", "Mortise_Panic", "Concealed_Cable",
        ]
        with open(p, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow({
                    "Manufacturer": r.manufacturer,
                    "Height": str(r.height),
                    "D1": r.d1, "D2": r.d2, "D3": r.d3, "D4": r.d4,
                    "Cylindrical": r.cylindrical,
                    "Mortise": r.mortise,
                    "Rim_Panic": r.rim_panic,
                    "CVR_Panic": r.cvr_panic,
                    "SVR_Panic": r.svr_panic,
                    "Mortise_Panic": r.mortise_panic,
                    "Concealed_Cable": r.concealed_cable,
                })
