"""Seed Ives hardware pricing from extracted pricebook data.

Reads data/ives_pricebook_data.json (produced by extract_ives_pricebook.py)
and creates families, slots, options, and pricing for all Ives products.

Pricebook #16, Effective February 27, 2026 (CAN edition).
"""

import json
from collections import defaultdict
from pathlib import Path

from seed_helpers import fid, slot, options, price, price_bulk

# ─── Data loader ──────────────────────────────────────────────────────

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "ives_pricebook_data.json"

# BHMA → user-friendly display name
BHMA_DISPLAY = {
    "600": "USP - Primed",
    "602": "US2C",
    "603": "US2G",
    "604": "US2C - Zinc",
    "605": "US3 - Bright Brass",
    "606": "US4 - Satin Brass",
    "609": "US5 - Antique Brass",
    "610": "US9 - Bright Bronze",
    "612": "US10 - Satin Bronze",
    "613": "US10B - Oil Rubbed Bronze",
    "618": "US14 - Bright Nickel",
    "619": "US15 - Satin Nickel",
    "621": "US15A",
    "622": "BLK - Black",
    "625": "US26 - Bright Chrome",
    "626": "US26D - Satin Chrome",
    "628": "US28 - Satin Aluminum",
    "629": "US32 - Bright Stainless",
    "630": "US32D - Satin Stainless",
    "632": "US3 - Bright Brass (Steel)",
    "633": "US4 - Satin Brass (Steel)",
    "636": "US7 - French Gray",
    "638": "US5 - Antique Brass (Steel)",
    "639": "US10 - Satin Bronze (Steel)",
    "640": "US10B - Oil Rubbed Bronze (Steel)",
    "641": "US10A (Steel)",
    "643E": "643E - Aged Bronze",
    "645": "US14 (Steel)",
    "646": "US15 - Satin Nickel (Steel)",
    "647": "US15A (Steel)",
    "651": "US26 - Bright Chrome (Steel)",
    "652": "US26D - Satin Chrome (Steel)",
    "666": "A3 - Bright Brass (Alum)",
    "667": "A4 - Satin Brass (Alum)",
    "668": "A10 - Satin Bronze (Alum)",
    "689": "SP28 - Satin Aluminum",
    "691": "SP10 - Satin Bronze",
    "695": "SP313 - Dark Bronze",
    "703": "A10B - Dark Bronze (Alum)",
    "706": "SP4 - Satin Brass",
    "710": "313 - Dark Bronze Anodized",
    "711": "315 - Flat Black",
    "716": "643E - Aged Bronze",
}


def _finish_display(bhma):
    return BHMA_DISPLAY.get(bhma, bhma)


def _load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    # Filter out items whose BHMA field is actually a price (starts with '$')
    clean = [it for it in raw if not str(it.get("bhma", "")).startswith("$")]
    skipped = len(raw) - len(clean)
    if skipped:
        print(f"  [Ives] Skipped {skipped} items with invalid BHMA codes")
    return clean


# ─── Family builders ──────────────────────────────────────────────────

def _clean_size(s):
    """Normalize size string."""
    s = s.strip()
    # Remove metric measurements in parentheses
    s = s.split("(")[0].strip()
    # Remove newlines
    s = s.replace("\n", " ").strip()
    return s


def _seed_architectural_hinges(conn, items):
    """Architectural Hinges — model + size + finish → price."""
    fam_id = fid(conn, "Ives", "Architectural Hinges", "Hinge",
                 "{model} {size} {finish}", "Ives {model} {size} {finish}")

    # Collect unique models, sizes, finishes
    models = {}  # model_name → description
    sizes = set()
    finishes = {}  # bhma → display
    prices = {}  # (model, size, bhma) → price

    for it in items:
        m = it["model"]
        sz = _clean_size(it.get("size", ""))
        bhma = it["bhma"]
        sub = it.get("substrate", "")

        if not sz or not bhma:
            continue

        models[m] = it.get("description", "")
        sizes.add(sz)
        # Distinguish finishes by substrate+bhma for unique key
        fkey = f"{bhma}_{sub[0]}" if sub else bhma
        finishes[fkey] = (bhma, sub, _finish_display(bhma) + (f" [{sub}]" if sub else ""))

        # Compound pricing key: model:size:finish_key
        pkey = (m, sz, fkey)
        # Keep last (overwrites if duplicate)
        prices[pkey] = it["price"]

    # Slots
    slot(conn, fam_id, 1, "model", "Hinge Model", 1)
    slot(conn, fam_id, 2, "size", "Size", 1)
    slot(conn, fam_id, 3, "finish", "Finish", 1)
    slot(conn, fam_id, 4, "suffix", "Options", 0)

    # Options
    model_opts = [(m, f"{m} - {d[:40]}") if d else (m, m) for m, d in sorted(models.items())]
    options(conn, fam_id, "model", model_opts)

    size_list = sorted(sizes, key=lambda s: (len(s), s))
    options(conn, fam_id, "size", [(s, s) for s in size_list])

    finish_opts = sorted(finishes.items(), key=lambda x: x[1][0])
    options(conn, fam_id, "finish", [(fk, disp) for fk, (_, __, disp) in finish_opts])

    options(conn, fam_id, "suffix", [
        ("TW", "TW - Transfer Wire"),
        ("NRP", "NRP - Non-Removable Pin"),
    ])

    # Pricing — compound key "model:size:finish"
    for (m, sz, fk), amt in prices.items():
        price(conn, fam_id, "model:size:finish", f"{m}:{sz}:{fk}", amt, "base")

    return len(prices)


def _seed_continuous_geared(conn, items):
    """Continuous Geared Hinges — model + length + finish → price."""
    fam_id = fid(conn, "Ives", "Continuous Geared Hinges", "Continuous Hinge",
                 "{model} {length} {finish}", "Ives {model} {length} {finish}")

    models = {}
    lengths = set()
    finishes = set()
    prices = {}

    for it in items:
        m = it["model"]
        length = it.get("length", "").strip()
        bhma = it["bhma"]
        if not length or not bhma:
            continue

        models[m] = it.get("description", "")
        lengths.add(length)
        finishes.add(bhma)
        prices[(m, length, bhma)] = it["price"]

    slot(conn, fam_id, 1, "model", "Model", 1)
    slot(conn, fam_id, 2, "length", "Length", 1)
    slot(conn, fam_id, 3, "finish", "Finish", 1)
    slot(conn, fam_id, 4, "suffix", "Options", 0)

    options(conn, fam_id, "model",
            [(m, f"{m} - {d[:40]}") if d else (m, m) for m, d in sorted(models.items())])
    options(conn, fam_id, "length",
            [(l, l) for l in sorted(lengths, key=lambda x: float(x.replace('"', '').replace("'", "")) if x.replace('"', '').replace("'", "").replace('.', '').isdigit() else 0)])
    options(conn, fam_id, "finish",
            [(b, f"{b} - {_finish_display(b)}") for b in sorted(finishes)])
    options(conn, fam_id, "suffix", [
        ("TW", "TW - Transfer Wire"),
        ("NRP", "NRP - Non-Removable Pin"),
    ])

    for (m, l, b), amt in prices.items():
        price(conn, fam_id, "model:length:finish", f"{m}:{l}:{b}", amt, "base")

    return len(prices)


def _seed_pin_barrel(conn, items):
    """Pin & Barrel Continuous Hinges."""
    fam_id = fid(conn, "Ives", "Pin & Barrel Continuous Hinges", "Continuous Hinge",
                 "{model} {length} {finish}", "Ives {model} {length} {finish}")

    models = {}
    lengths = set()
    finishes = set()
    prices = {}

    for it in items:
        m = it["model"]
        length = it.get("length", "Standard").strip()
        bhma = it["bhma"]
        if not bhma:
            continue

        models[m] = it.get("description", "")
        lengths.add(length)
        finishes.add(bhma)
        prices[(m, length, bhma)] = it["price"]

    slot(conn, fam_id, 1, "model", "Model", 1)
    slot(conn, fam_id, 2, "length", "Length", 1)
    slot(conn, fam_id, 3, "finish", "Finish", 1)
    slot(conn, fam_id, 4, "suffix", "Options", 0)

    options(conn, fam_id, "model",
            [(m, f"{m} - {d[:40]}") if d else (m, m) for m, d in sorted(models.items())])
    options(conn, fam_id, "length", [(l, l) for l in sorted(lengths)])
    options(conn, fam_id, "finish",
            [(b, f"{b} - {_finish_display(b)}") for b in sorted(finishes)])
    options(conn, fam_id, "suffix", [
        ("TW", "TW - Transfer Wire"),
        ("NRP", "NRP - Non-Removable Pin"),
    ])

    for (m, l, b), amt in prices.items():
        price(conn, fam_id, "model:length:finish", f"{m}:{l}:{b}", amt, "base")

    return len(prices)


def _seed_pivots(conn, items):
    """Pivots — model + finish → price (with optional lb_rating)."""
    fam_id = fid(conn, "Ives", "Pivots", "Pivot",
                 "{model} {finish}", "Ives {model} Pivot {finish}")

    models = {}
    finishes = set()
    prices = {}

    for it in items:
        m = it["model"]
        bhma = it["bhma"]
        lb = it.get("lb_rating", "").strip()
        if not bhma:
            continue

        desc = it.get("description", "")
        if lb:
            desc = f"{desc} ({lb} lb)" if desc else f"{lb} lb"
        models[m] = desc
        finishes.add(bhma)
        prices[(m, bhma)] = it["price"]

    slot(conn, fam_id, 1, "model", "Model", 1)
    slot(conn, fam_id, 2, "finish", "Finish", 1)

    options(conn, fam_id, "model",
            [(m, f"{m} - {d[:50]}") if d else (m, m) for m, d in sorted(models.items())])
    options(conn, fam_id, "finish",
            [(b, f"{b} - {_finish_display(b)}") for b in sorted(finishes)])

    for (m, b), amt in prices.items():
        price(conn, fam_id, "model:finish", f"{m}:{b}", amt, "base")

    return len(prices)


def _seed_model_finish_family(conn, items, name, category,
                              has_model_number=True):
    """Generic family with model + finish → price.
    Used for flush bolts, coordinators, surface bolts, stops, etc.
    """
    fam_id = fid(conn, "Ives", name, category,
                 "{model} {finish}", f"Ives {name} {{model}} {{finish}}")

    models = {}
    finishes = set()
    prices = {}

    for it in items:
        m = it["model"]
        bhma = it["bhma"]
        if not bhma:
            continue

        models[m] = it.get("description", "")
        finishes.add(bhma)
        prices[(m, bhma)] = it["price"]

    slot(conn, fam_id, 1, "model", "Model", 1)
    slot(conn, fam_id, 2, "finish", "Finish", 1)

    options(conn, fam_id, "model",
            [(m, f"{m} - {d[:50]}") if d else (m, m) for m, d in sorted(models.items())])
    options(conn, fam_id, "finish",
            [(b, f"{b} - {_finish_display(b)}") for b in sorted(finishes)])

    for (m, b), amt in prices.items():
        price(conn, fam_id, "model:finish", f"{m}:{b}", amt, "base")

    return len(prices)


def _seed_pulls_with_ctc(conn, items, name, category):
    """Pulls with pull CTC dimension — model + finish → price."""
    # CTC is embedded in model_number, just use model+finish for pricing
    return _seed_model_finish_family(conn, items, name, category)


def _seed_edge_guards(conn, items):
    """Edge Guards — model + size + finish → price."""
    fam_id = fid(conn, "Ives", "Edge Guards", "Door Accessory",
                 "{model} {size} {finish}", "Ives Edge Guard {model} {size} {finish}")

    models = set()
    sizes = set()
    finishes = set()
    prices = {}

    for it in items:
        m = it["model"]
        sz = it.get("size", "").strip()
        bhma = it["bhma"]
        if not sz or not bhma:
            continue

        models.add(m)
        sizes.add(sz)
        finishes.add(bhma)
        prices[(m, sz, bhma)] = it["price"]

    slot(conn, fam_id, 1, "model", "Model", 1)
    slot(conn, fam_id, 2, "size", "Size", 1)
    slot(conn, fam_id, 3, "finish", "Finish", 1)

    options(conn, fam_id, "model", [(m, m) for m in sorted(models)])
    options(conn, fam_id, "size", [(s, s) for s in sorted(sizes)])
    options(conn, fam_id, "finish",
            [(b, f"{b} - {_finish_display(b)}") for b in sorted(finishes)])

    for (m, sz, b), amt in prices.items():
        price(conn, fam_id, "model:size:finish", f"{m}:{sz}:{b}", amt, "base")

    return len(prices)


def _seed_long_door_pulls(conn, items):
    """Long Door Pulls — model + length + finish → price."""
    fam_id = fid(conn, "Ives", "Long Door Pulls", "Pull",
                 "{model} {length} {finish}", "Ives {model} {length} {finish}")

    models = {}
    lengths = set()
    finishes = set()
    prices = {}

    for it in items:
        m = it["model"]
        length = it.get("length", "").strip()
        bhma = it["bhma"]
        if not bhma:
            continue

        models[m] = it.get("description", "")
        if length:
            lengths.add(length)
        finishes.add(bhma)
        key = (m, length or "STD", bhma)
        prices[key] = it["price"]

    slot(conn, fam_id, 1, "model", "Model", 1)
    slot(conn, fam_id, 2, "length", "Length", 1)
    slot(conn, fam_id, 3, "finish", "Finish", 1)

    options(conn, fam_id, "model",
            [(m, f"{m} - {d[:40]}") if d else (m, m) for m, d in sorted(models.items())])
    options(conn, fam_id, "length", [(l, l) for l in sorted(lengths)])
    options(conn, fam_id, "finish",
            [(b, f"{b} - {_finish_display(b)}") for b in sorted(finishes)])

    for (m, l, b), amt in prices.items():
        price(conn, fam_id, "model:length:finish", f"{m}:{l}:{b}", amt, "base")

    return len(prices)


def _seed_push_pull_plates(conn, items):
    """Push & Pull Plates — model + finish → price."""
    return _seed_model_finish_family(conn, items, "Push & Pull Plates", "Plate")


# ═════════════════════════════════════════════════════════════════════
#  Main seed function
# ═════════════════════════════════════════════════════════════════════

# Category → builder mapping for simple model+finish families
_SIMPLE_FAMILIES = {
    "Flush Bolts": ("Flush Bolts", "Flush Bolt"),
    "Coordinators": ("Coordinators", "Door Accessory"),
    "Surface Bolts": ("Surface Bolts", "Surface Bolt"),
    "Door Guards": ("Door Guards", "Door Accessory"),
    "Roller Latches": ("Roller Latches", "Latch"),
    "Angle Stops": ("Angle Stops", "Door Stop"),
    "Latches & Catches": ("Latches & Catches", "Latch"),
    "Floor Stops": ("Floor Stops", "Door Stop"),
    "Floor Stops & Holders": ("Floor Stops & Holders", "Door Stop"),
    "Wall Stops & Bumpers": ("Wall Stops & Bumpers", "Door Stop"),
    "Wall Stops & Holders": ("Wall Stops & Holders", "Door Stop"),
    "Door Holders": ("Door Holders", "Door Holder"),
    "Residential Door Stops": ("Residential Door Stops", "Door Stop"),
    "Door Silencers": ("Door Silencers", "Door Accessory"),
    "Lock Guards": ("Lock Guards", "Door Accessory"),
    "Viewers": ("Viewers", "Door Accessory"),
    "Exterior Hardware": ("Exterior Hardware", "Door Accessory"),
    "Brackets & Hooks": ("Brackets & Hooks", "Door Accessory"),
    "Window Hardware": ("Window Hardware", "Window Hardware"),
    "Vandal Resistant Trim": ("Vandal Resistant Trim", "Door Accessory"),
    "Flush Pulls": ("Flush Pulls", "Pull"),
    "Sliding Door Pulls": ("Sliding Door Pulls", "Pull"),
    "Decorative Pulls": ("Decorative Pulls", "Pull"),
    "Architectural Pulls": ("Architectural Pulls", "Pull"),
    "Rescue Hardware": ("Rescue Hardware", "Door Accessory"),
    "Protection Plates": ("Protection Plates", "Plate"),
}


def seed(conn):
    """Seed ALL Ives product families from pricebook data."""
    data = _load_data()

    # Group items by category
    by_cat = defaultdict(list)
    for item in data:
        by_cat[item["category"]].append(item)

    total = 0
    families = 0

    # Special families with unique slot structures
    if "Architectural Hinges" in by_cat:
        n = _seed_architectural_hinges(conn, by_cat["Architectural Hinges"])
        print(f"  Ives Architectural Hinges: {n} pricing rows")
        total += n
        families += 1

    if "Continuous Geared Hinges" in by_cat:
        n = _seed_continuous_geared(conn, by_cat["Continuous Geared Hinges"])
        print(f"  Ives Continuous Geared Hinges: {n} pricing rows")
        total += n
        families += 1

    if "Pin & Barrel Continuous Hinges" in by_cat:
        n = _seed_pin_barrel(conn, by_cat["Pin & Barrel Continuous Hinges"])
        print(f"  Ives Pin & Barrel Continuous Hinges: {n} pricing rows")
        total += n
        families += 1

    if "Pivots" in by_cat:
        n = _seed_pivots(conn, by_cat["Pivots"])
        print(f"  Ives Pivots: {n} pricing rows")
        total += n
        families += 1

    if "Edge Guards" in by_cat:
        n = _seed_edge_guards(conn, by_cat["Edge Guards"])
        print(f"  Ives Edge Guards: {n} pricing rows")
        total += n
        families += 1

    if "Long Door Pulls" in by_cat:
        n = _seed_long_door_pulls(conn, by_cat["Long Door Pulls"])
        print(f"  Ives Long Door Pulls: {n} pricing rows")
        total += n
        families += 1

    if "Push & Pull Plates" in by_cat:
        n = _seed_push_pull_plates(conn, by_cat["Push & Pull Plates"])
        print(f"  Ives Push & Pull Plates: {n} pricing rows")
        total += n
        families += 1

    # All simple model+finish families
    for cat, (name, hw_cat) in sorted(_SIMPLE_FAMILIES.items()):
        if cat in by_cat:
            n = _seed_model_finish_family(conn, by_cat[cat], name, hw_cat)
            print(f"  Ives {name}: {n} pricing rows")
            total += n
            families += 1

    print(f"  Ives TOTAL: {families} families, {total} pricing rows")
