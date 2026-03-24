"""Seed Trimco pricebook data from extracted CSVs.

Reads:
  data/trimco_boxed_items.csv      – model, description, finish, price
  data/trimco_ap_items.csv         – family, size, finish, price
  data/trimco_specialty_items.csv  – model, description, finish, price

Trimco Price List 26, Effective February 27, 2026 (CAN edition).
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

from seed_helpers import fid, slot, options, price

DATA = Path(__file__).resolve().parent.parent / "data"
MFR = "Trimco"

# ── Finish display names ────────────────────────────────────────────

FINISH_DISPLAY = {
    "605":     "605 - Bright Brass",
    "605/606": "605/606 - Bright/Satin Brass",
    "606":     "606 - Satin Brass",
    "609":     "609 - Antique Brass",
    "611":     "611 - Bright Bronze",
    "611/612": "611/612 - Bright/Satin Bronze",
    "612":     "612 - Satin Bronze",
    "612E":    "612E - Dark Oxidized Satin Bronze",
    "613":     "613 - Oil Rubbed Bronze",
    "613E":    "613E - Dark Oxidized Bronze",
    "622":     "622 - Flat Black",
    "625":     "625 - Bright Chrome",
    "625/626": "625/626 - Bright/Satin Chrome",
    "626":     "626 - Satin Chrome",
    "628":     "628 - Satin Aluminum",
    "629":     "629 - Bright Stainless",
    "630":     "630 - Satin Stainless",
    "690":     "690 - Dark Bronze",
    "710CU":   "710CU - Healthy Hardware (Copper)",
    "316P":    "316P - Polished Stainless 316",
    "316S":    "316S - Satin Stainless 316",
    "313":     "313 - Dark Bronze Anodized",
    "335":     "335 - Black Anodized",
    "710":     "710 - Healthy Hardware",
    "712":     "712 - Oil Rubbed Bronze Anodized",
    "SPECIAL": "Special Finish (Quote)",
    # Mastercraft Bronze finishes
    "DB":  "DB - Dark Bronze",
    "SB":  "SB - Satin Bronze",
    "SNB": "SNB - Satin Nickel Bronze",
    # Plastic plate colors
    "Black":          "Black",
    "Nubia Brown":    "Nubia Brown",
    "Clear Plastic":  "Clear Plastic",
    "Khaki Brown":    "Khaki Brown",
    "Beige":          "Beige",
    "Grey":           "Grey",
    "Dove Grey":      "Dove Grey",
    "Frosty White":   "Frosty White",
}


def _finish_display(code):
    return FINISH_DISPLAY.get(code, code)


# ── Boxed item categorization ───────────────────────────────────────

def _categorize(model, desc):
    """Assign a boxed-price model to a product family."""
    d = desc.lower() if desc else ""
    m = model

    if m.startswith("BP"):
        return "Back Plates"
    if m.startswith("MasterCraft") or m.startswith("STANLEY") or m.startswith("PIERCE") or m.startswith("LAVA"):
        return "Mastercraft Bronze"
    if m.startswith("K"):
        return "Edge Guards"

    if "push plate" in d and "pull" not in d:
        return "Push Plates"
    if "pull plate" in d:
        return "Pull Plates"
    if "push" in d and "pull" in d and ("latch" in d or "set" in d):
        return "Push/Pull Latch Sets"
    if "push bar" in d:
        return "Push Bars"
    if "push/pull" in d and "latch" not in d:
        return "Push Bars"
    if "flush pull" in d or "flush cup" in d:
        return "Flush Pulls"
    if "concealed" in d and "pull" in d:
        return "Flush Pulls"
    if "cane bolt" in d:
        return "Cane Bolts"
    if "hospital pull" in d:
        return "Hospital Pulls"
    if "anti-vandal" in d or "tuf-lok" in d:
        return "Anti-Vandal"
    if "ada" in d or "restroom sign" in d:
        return "ADA Signs"
    if "knocker" in d:
        return "Door Knockers"
    if "catch" in d or "ball catch" in d:
        return "Catches & Latches"
    if "roller latch" in d:
        return "Catches & Latches"
    if "latchset" in d or "latchbolt" in d:
        return "Push/Pull Latch Sets"
    if "coordinator" in d:
        return "Coordinators"
    if "flushbolt" in d or "flush bolt" in d:
        return "Flush Bolts"
    if "surface bolt" in d:
        return "Surface Bolts"
    if "strike" in d and "dust" in d:
        return "Dust Proof Strikes"
    if "strike" in d:
        return "Strikes"
    if "wall stop" in d or "wall bumper" in d or "concave" in d:
        return "Wall Stops & Bumpers"
    if "floor stop" in d:
        return "Floor Stops & Holders"
    if "door holder" in d or ("hold" in d and "open" in d):
        return "Door Holders"
    if "kickdown" in d:
        return "Door Holders"
    if ("base stop" in d or "door stop" in d or "hinge pin" in d
            or "dome stop" in d):
        return "Door Stops"
    if "roller stop" in d or "angle stop" in d:
        return "Roller Stops"
    if "pull" in d and "offset" in d:
        return "Offset Pulls"
    if "grab bar" in d:
        return "Grab Bars"
    if "pull" in d:
        return "Door Pulls"
    if "astragal" in d or "lock astragal" in d:
        return "Astragals"
    if "edge guard" in d or "finger guard" in d:
        return "Edge Guards"
    if "chain" in d or "swing arm" in d or "security door" in d:
        return "Security Hardware"
    if "emergency" in d or "hold open tool" in d:
        return "Security Hardware"
    if "plunger" in d:
        return "Door Holders"
    if "anchor" in d or "spacer" in d or "adapter" in d:
        return "Push/Pull Latch Sets"
    if "indicator" in d or "filler" in d:
        return "Miscellaneous"

    return "Miscellaneous"


# ── Category metadata ────────────────────────────────────────────────

BOXED_CATEGORIES = {
    "ADA Signs":             "Signage",
    "Anti-Vandal":           "Anti-Vandal Hardware",
    "Astragals":             "Astragal",
    "Back Plates":           "Back Plate",
    "Cane Bolts":            "Cane Bolt",
    "Catches & Latches":     "Catch / Latch",
    "Coordinators":          "Coordinator",
    "Door Holders":          "Door Holder",
    "Door Knockers":         "Door Knocker",
    "Door Pulls":            "Pull / Push",
    "Door Stops":            "Door Stop",
    "Dust Proof Strikes":    "Strike",
    "Edge Guards":           "Edge Guard",
    "Floor Stops & Holders": "Floor Stop / Holder",
    "Flush Bolts":           "Flush Bolt",
    "Flush Pulls":           "Flush Pull",
    "Grab Bars":             "Grab Bar",
    "Hospital Pulls":        "Pull / Push",
    "Mastercraft Bronze":    "Decorative Hardware",
    "Miscellaneous":         "Miscellaneous",
    "Offset Pulls":          "Pull / Push",
    "Pull Plates":           "Push / Pull Plate",
    "Push Bars":             "Push Bar",
    "Push Plates":           "Push / Pull Plate",
    "Push/Pull Latch Sets":  "Push / Pull Latch",
    "Roller Stops":          "Roller Stop",
    "Security Hardware":     "Security Hardware",
    "Strikes":               "Strike",
    "Surface Bolts":         "Surface Bolt",
    "Wall Stops & Bumpers":  "Wall Stop / Bumper",
}

# AP series metadata
AP_SERIES = {
    "AP100": ("AP100 Straight Bent & Mitered Pulls", "Architectural Pull"),
    "AP200": ("AP200 Offset Bent Pulls",             "Architectural Pull"),
    "AP300": ("AP300 Adjustable Pulls",              "Architectural Pull"),
    "AP400": ("AP400 Standard Ladder Pulls",         "Architectural Pull"),
    "AP500": ("AP500 Black Anodized Grip Pulls",     "Architectural Pull"),
    "AP600": ("AP600 Leather Wrapped Pulls",         "Architectural Pull"),
    "AP700": ("AP700 Square/Rectangular Pulls",      "Architectural Pull"),
    "APC":   ("APC Closet/Cabinet Pulls",            "Architectural Pull"),
}


# ── Loaders ──────────────────────────────────────────────────────────

def _load_boxed():
    with open(DATA / "trimco_boxed_items.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_ap():
    with open(DATA / "trimco_ap_items.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_specialty():
    with open(DATA / "trimco_specialty_items.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_protection_plates():
    with open(DATA / "trimco_protection_plates.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Seeders ──────────────────────────────────────────────────────────

def _seed_boxed(conn):
    """Seed all boxed-price families."""
    rows = _load_boxed()

    # Group by category
    groups = defaultdict(list)
    for r in rows:
        cat = _categorize(r["model"], r["description"])
        groups[cat].append(r)

    total_families = 0
    total_prices = 0

    for cat_name in sorted(groups.keys()):
        items = groups[cat_name]
        hw_cat = BOXED_CATEGORIES.get(cat_name, "Miscellaneous")

        # Collect unique models and finishes for this family
        model_map = {}  # model → description
        finishes_used = set()
        pricing = {}  # (model, finish) → price

        for r in items:
            m, d, fin = r["model"], r["description"], r["finish"]
            amt = float(r["price"])
            if amt <= 0:
                continue
            if m not in model_map or (d and not model_map[m]):
                model_map[m] = d
            finishes_used.add(fin)
            pricing[(m, fin)] = amt

        if not pricing:
            continue

        f = fid(conn, MFR, cat_name, hw_cat,
                "{model} {finish}",
                f"Trimco {cat_name} {{model}} {{finish}}")

        slot(conn, f, 1, "model",  "Model",  1)
        slot(conn, f, 2, "finish", "Finish", 1)

        # Model options sorted
        model_opts = []
        for m in sorted(model_map.keys()):
            d = model_map[m]
            display = f"{m} - {d[:50]}" if d else m
            model_opts.append((m, display))
        options(conn, f, "model", model_opts)

        # Finish options sorted
        finish_opts = [(fin, _finish_display(fin)) for fin in sorted(finishes_used)]
        options(conn, f, "finish", finish_opts)

        # Compound pricing
        for (m, fin), amt in pricing.items():
            price(conn, f, "model:finish", f"{m}:{fin}", amt, "base")

        total_families += 1
        total_prices += len(pricing)

    return total_families, total_prices


def _seed_ap(conn):
    """Seed AP series families."""
    rows = _load_ap()

    # Group by series prefix
    series_groups = defaultdict(list)
    for r in rows:
        fam = r["family"]
        # Determine series: AP1xx→AP100, AP4xx→AP400, APCxx→APC
        if fam.startswith("APC"):
            series = "APC"
        else:
            m = re.match(r"(AP\d)", fam)
            if m:
                series = m.group(1) + "00"
            else:
                series = "APC"
        series_groups[series].append(r)

    total_families = 0
    total_prices = 0

    for series_key in sorted(series_groups.keys()):
        items = series_groups[series_key]
        family_name, hw_cat = AP_SERIES.get(series_key, (series_key, "Architectural Pull"))

        # Collect unique models, sizes, finishes
        models_set = set()
        sizes_set = set()
        finishes_set = set()
        pricing = {}

        for r in items:
            fam, sz, fin = r["family"], r["size"], r["finish"]
            amt = float(r["price"])
            if amt <= 0:
                continue
            # Skip the "Finishes" and "Special" duplicates from extraction artifacts
            if fin in ("Finishes",):
                continue
            # Normalize "Special" to "SPECIAL"
            if fin == "Special":
                fin = "SPECIAL"
            models_set.add(fam)
            sizes_set.add(sz)
            finishes_set.add(fin)
            pricing[(fam, sz, fin)] = amt

        if not pricing:
            continue

        f = fid(conn, MFR, family_name, hw_cat,
                "{model} {size} {finish}",
                f"Trimco {family_name} {{model}} {{size}} {{finish}}")

        slot(conn, f, 1, "model",  "Model",  1)
        slot(conn, f, 2, "size",   "Size",   1)
        slot(conn, f, 3, "finish", "Finish", 1)

        # Model options
        model_opts = [(m, m) for m in sorted(models_set)]
        options(conn, f, "model", model_opts)

        # Size options, sorted numerically
        def size_key(s):
            m = re.search(r"(\d+)", s)
            return int(m.group(1)) if m else 0
        size_opts = [(s, s) for s in sorted(sizes_set, key=size_key)]
        options(conn, f, "size", size_opts)

        # Finish options
        finish_opts = [(fin, _finish_display(fin)) for fin in sorted(finishes_set)]
        options(conn, f, "finish", finish_opts)

        # Compound pricing: model:size:finish
        for (mod, sz, fin), amt in pricing.items():
            price(conn, f, "model:size:finish", f"{mod}:{sz}:{fin}", amt, "base")

        total_families += 1
        total_prices += len(pricing)

    return total_families, total_prices


def _seed_specialty(conn):
    """Seed specialty items (UHF, LDH, UFP, UCT, 9-Series)."""
    rows = _load_specialty()

    # Group by model prefix
    groups = defaultdict(list)
    for r in rows:
        m = r["model"]
        if m.startswith("UHF"):
            groups["UHF Ultimate Slide Lock"].append(r)
        elif m.startswith("LDH"):
            groups["LDH Lockdown Hardware"].append(r)
        elif m.startswith("UFP"):
            groups["UFP Ultimate Foot Pull"].append(r)
        elif m.startswith("UCT"):
            groups["UCT Ultimate Counter Tops"].append(r)
        elif m.startswith("9"):
            groups["9-Series Mortise Locks"].append(r)
        else:
            groups["Specialty Products"].append(r)

    cat_map = {
        "UHF Ultimate Slide Lock":    "Slide Lock",
        "LDH Lockdown Hardware":      "Lockdown Hardware",
        "UFP Ultimate Foot Pull":     "Foot Pull",
        "UCT Ultimate Counter Tops":  "Counter Top",
        "9-Series Mortise Locks":     "Mortise Lock",
        "Specialty Products":         "Miscellaneous",
    }

    total_families = 0
    total_prices = 0

    for grp_name in sorted(groups.keys()):
        items = groups[grp_name]
        hw_cat = cat_map.get(grp_name, "Miscellaneous")

        model_map = {}
        finishes_used = set()
        pricing = {}

        for r in items:
            m, d, fin = r["model"], r["description"], r["finish"]
            amt = float(r["price"])
            if amt <= 0:
                continue
            if m not in model_map or (d and not model_map[m]):
                model_map[m] = d
            finishes_used.add(fin)
            pricing[(m, fin)] = amt

        if not pricing:
            continue

        f = fid(conn, MFR, grp_name, hw_cat,
                "{model} {finish}",
                f"Trimco {grp_name} {{model}} {{finish}}")

        slot(conn, f, 1, "model",  "Model",  1)
        slot(conn, f, 2, "finish", "Finish", 1)

        model_opts = []
        for m in sorted(model_map.keys()):
            d = model_map[m]
            display = f"{m} - {d[:50]}" if d else m
            model_opts.append((m, display))
        options(conn, f, "model", model_opts)

        finish_opts = [(fin, _finish_display(fin)) for fin in sorted(finishes_used)]
        options(conn, f, "finish", finish_opts)

        for (m, fin), amt in pricing.items():
            price(conn, f, "model:finish", f"{m}:{fin}", amt, "base")

        total_families += 1
        total_prices += len(pricing)

    return total_families, total_prices


# ── Protection plates mapping ────────────────────────────────────────

PROTECTION_PLATE_CATEGORIES = {
    "Armor Plate":                "Door Protection Plate",
    "Mop Plate":                  "Door Protection Plate",
    "Kick Plate":                 "Door Protection Plate",
    "Stretcher Plate":            "Door Protection Plate",
    "Handicap Kick Plate":        "Door Protection Plate",
    "Self-Illuminated Exit Sign": "Door Protection Plate",
    "Plastic Kick Plate":         "Door Protection Plate",
}

MATERIAL_DISPLAY = {
    '.038"': '.038" Gauge',
    '.050"': '.050" Gauge',
    '.064"': '.064" Gauge',
    '.125"': '.125" Diamond Plate',
    '1/8"':  '1/8" Plastic',
}


def _seed_protection_plates(conn):
    """Seed door protection plate families from page 79.

    Pricing is per 100 square inches.
    """
    rows = _load_protection_plates()

    # Group by plate_type
    groups = defaultdict(list)
    for r in rows:
        groups[r["plate_type"]].append(r)

    total_families = 0
    total_prices = 0

    for plate_type in sorted(groups.keys()):
        items = groups[plate_type]
        hw_cat = PROTECTION_PLATE_CATEGORIES.get(plate_type, "Door Protection Plate")

        model_map = {}       # model → material
        finishes_used = set()
        pricing = {}         # (model, finish) → price

        for r in items:
            m, mat, fin = r["model"], r["material"], r["finish"]
            amt = float(r["price"])
            if amt <= 0:
                continue
            model_map[m] = mat
            finishes_used.add(fin)
            pricing[(m, fin)] = amt

        if not pricing:
            continue

        family_name = f"{plate_type}s" if not plate_type.endswith("s") else plate_type
        f = fid(conn, MFR, family_name, hw_cat,
                "{model} {finish}",
                f"Trimco {family_name} {{model}} {{finish}} (per 100 sq in)")

        slot(conn, f, 1, "model",  "Model",  1)
        slot(conn, f, 2, "finish", "Finish", 1)

        # Model options: show model + material gauge
        model_opts = []
        for m in sorted(model_map.keys()):
            mat = model_map[m]
            mat_disp = MATERIAL_DISPLAY.get(mat, mat)
            model_opts.append((m, f"{m} - {mat_disp}"))
        options(conn, f, "model", model_opts)

        # Finish options
        finish_opts = [(fin, _finish_display(fin)) for fin in sorted(finishes_used)]
        options(conn, f, "finish", finish_opts)

        # Compound pricing: model:finish
        for (m, fin), amt in pricing.items():
            price(conn, f, "model:finish", f"{m}:{fin}", amt, "base")

        total_families += 1
        total_prices += len(pricing)

    return total_families, total_prices


# ── Public API ───────────────────────────────────────────────────────

def seed(conn):
    """Seed all Trimco pricebook data."""
    bf, bp = _seed_boxed(conn)
    af, ap_ = _seed_ap(conn)
    sf, sp = _seed_specialty(conn)
    pf, pp = _seed_protection_plates(conn)

    total_f = bf + af + sf + pf
    total_p = bp + ap_ + sp + pp
    print(f"  Trimco: {total_f} families, {total_p:,} pricing rows "
          f"(boxed={bp:,}, AP={ap_:,}, specialty={sp}, protection={pp})")
