"""Seed NGP (National Guard Products) pricing from extracted pricebook data.

Reads data/ngp_pricebook_data.json (produced by extract_ngp_pricebook.py)
and creates families, slots, options, and pricing for all NGP products.

NGP Price List, Effective February 1, 2026.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

from seed_helpers import fid, slot, options, price, price_bulk

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "ngp_pricebook_data.json"

MFR = "NGP"

# ── Simple families: part_no → price ─────────────────────────────────
SIMPLE_FAMILIES = {
    "Threshold Fasteners":          ("Threshold Fasteners",          "Threshold"),
    "Threshold Assembly Components": ("Threshold Assembly Components", "Threshold"),
    "Ramps":                        ("Ramps",                        "Threshold"),
    "Seals & Gasketing":            ("Seals & Gasketing",            "Door Seal / Gasketing"),
    "Thresholds":                   ("Thresholds",                   "Threshold"),
    "Replacement Gasketing Inserts": ("Replacement Gasketing Inserts", "Door Seal / Gasketing"),
    "Hinge Electric Options & Parts": ("Hinge Electric Options & Parts", "Continuous Hinge"),
    "Security Lite Kits - L-VGLF":  ("Security Lite Kits - L-VGLF",  "Lite Kit / Vision Panel"),
    "Sliding Door Hardware":        ("Sliding Door Hardware",        "Sliding Door Hardware"),
}

# ── Size families: part_no + size → price ────────────────────────────
SIZE_FAMILIES = {
    "Thresholds for Floor Closers": ("Thresholds for Floor Closers", "Threshold"),
    "Door Edges & Astragals":       ("Door Edges & Astragals",       "Door Edge / Astragal"),
}

# ── Length families: part_no + length → price ────────────────────────
LENGTH_FAMILIES = {
    "Continuous Geared Hinges":     ("Continuous Geared Hinges",     "Continuous Hinge"),
    "SS Continuous Hinges":         ("SS Continuous Hinges",         "Continuous Hinge"),
}

# ── Grid families: width + height → price (one product per family) ──
GRID_FAMILIES = {
    # Lite Kits
    "Lite Kits - Standard":          ("Lite Kits - Standard",          "Lite Kit / Vision Panel"),
    "Lite Kits - Pyran F":           ("Lite Kits - Pyran F",           "Lite Kit / Vision Panel"),
    "Lite Kits - 20T Fire-Rated":    ("Lite Kits - 20T Fire-Rated",    "Lite Kit / Vision Panel"),
    "Lite Kits - Variable Thickness": ("Lite Kits - Variable Thickness", "Lite Kit / Vision Panel"),
    "Lite Kits - Security Grille":   ("Lite Kits - Security Grille",   "Lite Kit / Vision Panel"),
    "Lite Kits - Stainless Steel":   ("Lite Kits - Stainless Steel",   "Lite Kit / Vision Panel"),
    "Lite Kits - Stainless SP":      ("Lite Kits - Stainless SP",      "Lite Kit / Vision Panel"),
    "Lite Kits - SG-10 Security":    ("Lite Kits - SG-10 Security",    "Lite Kit / Vision Panel"),
    "Lite Kits - SSD Sliding Door":  ("Lite Kits - SSD Sliding Door",  "Lite Kit / Vision Panel"),
    "Lite Kits - BR-7 Security":     ("Lite Kits - BR-7 Security",     "Lite Kit / Vision Panel"),
    "Lite Kits - Hurricane":         ("Lite Kits - Hurricane",         "Lite Kit / Vision Panel"),
    # Louvers
    "Louvers - Steel AFDL":          ("Louvers - Steel AFDL",          "Louver"),
    "Louvers - FDLS Inverted":       ("Louvers - FDLS Inverted",       "Louver"),
    "Louvers - SS316":               ("Louvers - SS316",               "Louver"),
    "Louvers - Aluminum":            ("Louvers - Aluminum",            "Louver"),
    "Louvers - Adjustable Blade":    ("Louvers - Adjustable Blade",    "Louver"),
    "Louvers - PLSL Security":       ("Louvers - PLSL Security",       "Louver"),
    "Louvers - L-VRSG-2 Grille":     ("Louvers - L-VRSG-2 Grille",    "Louver"),
    "Louvers - L-VRSG-3 Grille":     ("Louvers - L-VRSG-3 Grille",    "Louver"),
    "Louvers - FLDL-SG Fire-Rated":  ("Louvers - FLDL-SG Fire-Rated", "Louver"),
    # Glass
    "Glass - Pyran F":               ("Glass - Pyran F",               "Glass"),
    "Glass - FireLite NT":           ("Glass - FireLite NT",           "Glass"),
    "Glass - Protect3 Wired":        ("Glass - Protect3 Wired",        "Glass"),
    "Glass - 20T Tempered":          ("Glass - 20T Tempered",          "Glass"),
    "Glass - Tempered 1/4 in":       ("Glass - Tempered 1/4 in",       "Glass"),
    # Security Grille Face Plates
    "Security Grille Face Plates":   ("Security Grille Face Plates",   "Louver"),
}


def _load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _seed_simple_family(conn, items, family_name, hw_category):
    """Simple family: part_no → price."""
    fam_id = fid(conn, MFR, family_name, hw_category,
                 "{part_no}",
                 f"NGP {family_name} {{part_no}}")

    slot(conn, fam_id, 1, "part_no", "Part Number", 1)

    parts = {}
    pricing = {}
    for it in items:
        pn = it["part_no"]
        parts[pn] = it.get("description", "")
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
    """Size-based family: part_no + size → price."""
    fam_id = fid(conn, MFR, family_name, hw_category,
                 "{part_no} {size}",
                 f"NGP {family_name} {{part_no}} {{size}}")

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

    def _size_sort_key(s):
        m = re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 0

    options(conn, fam_id, "size",
            [(sz, sz) for sz in sorted(sizes, key=_size_sort_key)])

    rows = 0
    for key, amt in pricing.items():
        price(conn, fam_id, "part_no:size", key, amt, "base")
        rows += 1

    return rows


def _seed_length_family(conn, items, family_name, hw_category):
    """Length-based family: part_no + length → price."""
    fam_id = fid(conn, MFR, family_name, hw_category,
                 "{part_no} {length}",
                 f"NGP {family_name} {{part_no}} {{length}}")

    slot(conn, fam_id, 1, "part_no", "Part Number", 1)
    slot(conn, fam_id, 2, "length", "Length", 1)

    parts = {}
    lengths = set()
    pricing = {}

    for it in items:
        pn = it["part_no"]
        ln = it.get("length", "")
        if not ln:
            continue
        parts[pn] = it.get("description", "")
        lengths.add(ln)
        key = f"{pn}:{ln}"
        if key not in pricing:
            pricing[key] = it["price"]

    options(conn, fam_id, "part_no",
            [(pn, f"{pn} - {desc[:60]}") if desc else (pn, pn)
             for pn, desc in sorted(parts.items())])

    def _len_sort_key(s):
        m = re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 0

    options(conn, fam_id, "length",
            [(ln, f'{ln}"') for ln in sorted(lengths, key=_len_sort_key)])

    rows = 0
    for key, amt in pricing.items():
        price(conn, fam_id, "part_no:length", key, amt, "base")
        rows += 1

    return rows


def _seed_grid_family(conn, items, family_name, hw_category):
    """Grid family: width + height → price (optionally with product slot)."""
    # Detect multi-product families
    products = sorted(set(it["part_no"] for it in items))
    multi = len(products) > 1

    if multi:
        fam_id = fid(conn, MFR, family_name, hw_category,
                     "{product} {width}x{height}",
                     f"NGP {family_name} {{product}} {{width}}\" x {{height}}\"")
        slot(conn, fam_id, 1, "product", "Product", 1)
        slot(conn, fam_id, 2, "width", "Width (in)", 1)
        slot(conn, fam_id, 3, "height", "Height (in)", 1)
        options(conn, fam_id, "product",
                [(p, p) for p in products])
    else:
        fam_id = fid(conn, MFR, family_name, hw_category,
                     "{width}x{height}",
                     f"NGP {family_name} {{width}}\" x {{height}}\"")
        slot(conn, fam_id, 1, "width", "Width (in)", 1)
        slot(conn, fam_id, 2, "height", "Height (in)", 1)

    widths = set()
    heights = set()
    pricing = {}

    for it in items:
        w = it.get("width", "")
        h = it.get("height", "")
        if not w or not h:
            continue
        widths.add(w)
        heights.add(h)
        if multi:
            key = f"{it['part_no']}:{w}:{h}"
        else:
            key = f"{w}:{h}"
        if key not in pricing:
            pricing[key] = it["price"]

    def _num_sort(s):
        m = re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 0

    options(conn, fam_id, "width",
            [(w, f'{w}"') for w in sorted(widths, key=_num_sort)])

    options(conn, fam_id, "height",
            [(h, f'{h}"') for h in sorted(heights, key=_num_sort)])

    rows = 0
    if multi:
        for key, amt in pricing.items():
            price(conn, fam_id, "product:width:height", key, amt, "base")
            rows += 1
    else:
        for key, amt in pricing.items():
            price(conn, fam_id, "width:height", key, amt, "base")
            rows += 1

    return rows


# ── Main seed entry point ────────────────────────────────────────────

def seed(conn):
    data = _load_data()

    by_cat = defaultdict(list)
    for item in data:
        by_cat[item["category"]].append(item)

    total_families = 0
    total_pricing = 0

    # Simple families
    for cat_key, (family_name, hw_category) in sorted(SIMPLE_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_simple_family(conn, items, family_name, hw_category)
        print(f"  NGP {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    # Size families
    for cat_key, (family_name, hw_category) in sorted(SIZE_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_size_family(conn, items, family_name, hw_category)
        print(f"  NGP {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    # Length families
    for cat_key, (family_name, hw_category) in sorted(LENGTH_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_length_family(conn, items, family_name, hw_category)
        print(f"  NGP {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    # Grid families
    for cat_key, (family_name, hw_category) in sorted(GRID_FAMILIES.items()):
        items = by_cat.get(cat_key, [])
        if not items:
            continue
        rows = _seed_grid_family(conn, items, family_name, hw_category)
        print(f"  NGP {family_name}: {rows} pricing rows")
        total_families += 1
        total_pricing += rows

    print(f"  NGP TOTAL: {total_families} families, {total_pricing} pricing rows")
