"""Seed Zero International pricing from extracted pricebook data.

Reads data/zero_pricebook_data.json (produced by extract_zero_pricebook.py)
and creates families, slots, options, and pricing for all Zero products.

Pricebook #13, Effective February 27, 2026.
"""

import json
from collections import defaultdict
from pathlib import Path

from seed_helpers import fid, slot, options, price, price_bulk

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "zero_pricebook_data.json"

# ── Finish suffix → display name (derived from BHMA cross-reference on page 6) ──
FINISH_DISPLAY = {
    "A":     "A - Aluminum Mill Finish",
    "AA":    "AA - Aluminum Clear Anodized (628)",
    "B":     "B - Bronze Architectural Mill",
    "BK":    "BK - Black Anodized (711)",
    "D":     "D - Dark Bronze Anodized (710)",
    "G":     "G - Gold Anodized (688)",
    "SP":    "SP - Steel Prime",
    "STST":  "STST - Stainless Steel",
    "B-POL": "B-POL - Polished Bronze",
    "B-ORB": "B-ORB - Oil Rubbed Bronze (613)",
    "B-SAT": "B-SAT - Satin Polished Bronze",
}

# ── Categories that use simple part_no → price (per-foot or each) ──
SIMPLE_FAMILIES = {
    "Thresholds":                             ("Thresholds", "Threshold"),
    "Half Thresholds":                        ("Half Thresholds", "Threshold"),
    "Carpet Divider Thresholds":              ("Carpet Divider Thresholds", "Threshold"),
    "Offset & Rabbeted Thresholds":           ("Offset & Rabbeted Thresholds", "Threshold"),
    "Interlocking Bronze Threshold Systems":  ("Interlocking Bronze Threshold Systems", "Threshold"),
    "Thermal Break Thresholds":               ("Thermal Break Thresholds", "Threshold"),
    "Adjustable Thresholds":                  ("Adjustable Thresholds", "Threshold"),
    "Ramps":                                  ("Ramps", "Threshold"),
    "Specialized Threshold Solutions":        ("Specialized Threshold Solutions", "Threshold"),
    "Perimeter Seal Accessories":             ("Perimeter Seal Accessories", "Door Seal / Gasketing"),
    "Door Sweeps":                            ("Door Sweeps", "Door Seal / Gasketing"),
    "Door Shoes":                             ("Door Shoes", "Door Seal / Gasketing"),
    "Adjustable Sealing Systems":             ("Adjustable Sealing Systems", "Door Seal / Gasketing"),
    "Head & Jamb Gasketing":                  ("Head & Jamb Gasketing", "Door Seal / Gasketing"),
    "Intumescent Seals":                      ("Intumescent Seals", "Door Seal / Gasketing"),
    "Meeting Stiles":                         ("Meeting Stiles", "Door Seal / Gasketing"),
    "Astragals":                              ("Astragals", "Door Seal / Gasketing"),
    "Door Closer Mounting Brackets":          ("Door Closer Mounting Brackets", "Door Accessory"),
    "Pile Brush Seals":                       ("Pile Brush Seals", "Weatherstripping"),
    "Cushion-Spring Seals":                   ("Cushion-Spring Seals", "Weatherstripping"),
    "Jamb Seals for Windows":                 ("Jamb Seals for Windows", "Weatherstripping"),
    "PSA Weatherstripping for Glass":         ("PSA Weatherstripping for Glass", "Weatherstripping"),
    "Glass Edge Protection":                  ("Glass Edge Protection", "Weatherstripping"),
    "Sound Control Systems":                  ("Sound Control Systems", "Door Seal / Gasketing"),
    "Cam Lift Hinges":                        ("Cam Lift Hinges", "Hinge"),
    "Flood Barrier Shields":                  ("Flood Barrier Shields", "Door Accessory"),
    "Finger Guards":                          ("Finger Guards", "Door Accessory"),
    "Replacement Rubber":                     ("Replacement Rubber", "Door Seal / Gasketing"),
}

# Categories with size-based pricing (door bottoms)
SIZE_FAMILIES = {
    "Heavy Duty Door Bottoms":     ("Heavy Duty Door Bottoms", "Door Bottom / Sweep"),
    "Regular Duty Door Bottoms":   ("Regular Duty Door Bottoms", "Door Bottom / Sweep"),
    "Light Duty Door Bottoms":     ("Light Duty Door Bottoms", "Door Bottom / Sweep"),
    "Sliding & Pocket Door Bottoms": ("Sliding & Pocket Door Bottoms", "Door Bottom / Sweep"),
    "ADA Compliant Door Bottoms":  ("ADA Compliant Door Bottoms", "Door Bottom / Sweep"),
}

# Categories with length-based pricing (weatherstripping)
LENGTH_FAMILIES = {
    "Kerf Frame Weatherstripping":      ("Kerf Frame Weatherstripping", "Weatherstripping"),
    "Self-Adhesive Weatherstripping":   ("Self-Adhesive Weatherstripping", "Weatherstripping"),
}


def _load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _seed_simple_family(conn, items, family_name, hw_category):
    """Simple family: part_no → price. One slot (part_no), pricing keyed on part_no."""
    fam_id = fid(conn, "Zero International", family_name, hw_category,
                 "{part_no}",
                 f"Zero {family_name} {{part_no}}")

    slot(conn, fam_id, 1, "part_no", "Part Number", 1)

    # Gather unique part numbers and deduplicate
    parts = {}
    pricing = {}
    for it in items:
        pn = it["part_no"]
        parts[pn] = it.get("description", "")
        # Store price and unit; first seen wins
        if pn not in pricing:
            pricing[pn] = it["price"]

    options(conn, fam_id, "part_no",
            [(pn, f"{pn} - {desc[:60]}") if desc else (pn, pn)
             for pn, desc in sorted(parts.items())])

    rows = 0
    for pn, amt in pricing.items():
        price(conn, fam_id, "part_no", pn, amt, "base")
        rows += 1

    return rows


def _seed_size_family(conn, items, family_name, hw_category):
    """Door bottoms: part_no + size → price."""
    fam_id = fid(conn, "Zero International", family_name, hw_category,
                 "{part_no} {size}",
                 f"Zero {family_name} {{part_no}} {{size}}")

    slot(conn, fam_id, 1, "part_no", "Part Number", 1)
    slot(conn, fam_id, 2, "size", "Size", 1)

    parts = {}
    sizes = set()
    pricing = {}

    for it in items:
        pn = it["part_no"]
        sz = it.get("size", "")
        if not sz:
            continue
        parts[pn] = it.get("description", "")
        sizes.add(sz)
        key = f"{pn}:{sz}"
        if key not in pricing:
            pricing[key] = it["price"]

    options(conn, fam_id, "part_no",
            [(pn, f"{pn} - {desc[:60]}") if desc else (pn, pn)
             for pn, desc in sorted(parts.items())])

    # Sort sizes by first numeric value for natural ordering
    import re as _re
    def _size_sort_key(s):
        m = _re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 0

    options(conn, fam_id, "size",
            [(sz, sz) for sz in sorted(sizes, key=_size_sort_key)])

    rows = 0
    for key, amt in pricing.items():
        price(conn, fam_id, "part_no:size", key, amt, "base")
        rows += 1

    return rows


def _seed_length_family(conn, items, family_name, hw_category):
    """Weatherstripping: part_no + length → price."""
    fam_id = fid(conn, "Zero International", family_name, hw_category,
                 "{part_no} {length}",
                 f"Zero {family_name} {{part_no}} {{length}}")

    slot(conn, fam_id, 1, "part_no", "Part Number", 1)

    parts = {}
    lengths = set()
    pricing = {}

    for it in items:
        pn = it["part_no"]
        ln = it.get("length", "")
        if not ln:
            # Some items are per-foot with no length dimension — treat as simple
            key = pn
            parts[pn] = it.get("description", "")
            if key not in pricing:
                pricing[key] = it["price"]
            continue
        parts[pn] = it.get("description", "")
        lengths.add(ln)
        key = f"{pn}:{ln}"
        if key not in pricing:
            pricing[key] = it["price"]

    options(conn, fam_id, "part_no",
            [(pn, f"{pn} - {desc[:60]}") if desc else (pn, pn)
             for pn, desc in sorted(parts.items())])

    if lengths:
        slot(conn, fam_id, 2, "length", "Length", 1)
        import re as _re
        def _len_sort_key(s):
            m = _re.search(r'(\d+)', s)
            return int(m.group(1)) if m else 0
        options(conn, fam_id, "length",
                [(ln, ln) for ln in sorted(lengths, key=_len_sort_key)])

    rows = 0
    for key, amt in pricing.items():
        if ":" in key:
            price(conn, fam_id, "part_no:length", key, amt, "base")
        else:
            price(conn, fam_id, "part_no", key, amt, "base")
        rows += 1

    return rows


# ── Main seed entry point ────────────────────────────────────────────

def seed(conn):
    data = _load_data()

    # Group by category
    by_cat = defaultdict(list)
    for item in data:
        by_cat[item["category"]].append(item)

    total_families = 0
    total_pricing = 0

    # Simple families (part_no → price)
    for cat_key, (family_name, hw_category) in sorted(SIMPLE_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_simple_family(conn, items, family_name, hw_category)
        print(f"  Zero {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    # Size families (door bottoms: part_no + size → price)
    for cat_key, (family_name, hw_category) in sorted(SIZE_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_size_family(conn, items, family_name, hw_category)
        print(f"  Zero {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    # Length families (weatherstripping: part_no + length → price)
    for cat_key, (family_name, hw_category) in sorted(LENGTH_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_length_family(conn, items, family_name, hw_category)
        print(f"  Zero {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    print(f"  Zero TOTAL: {total_families} families, {total_pricing} pricing rows")
