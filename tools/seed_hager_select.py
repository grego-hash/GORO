"""Seed Hager 3500 cylindrical locksets + SELECT continuous hinges."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_hager_3500(conn)
    _seed_select(conn)
    print("  Hager 3500 + SELECT SL hinges seeded.")


# ═════════════════════════════════════════════════════════════════════
# Hager 3500 Series Cylindrical Lockset
# ═════════════════════════════════════════════════════════════════════

def _seed_hager_3500(conn):
    f = fid(conn, "Hager", "3500 Series Cylindrical Lock",
            "Cylindrical Lock",
            "3500-{function} {lever} {rose} {finish}",
            "Hager 3500 {function} {lever} {rose} {finish}")

    slot(conn, f, 1, "function",      "Function",            1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",       1)
    slot(conn, f, 3, "lever",         "Lever Design",        1)
    slot(conn, f, 4, "rose",          "Rose",                1)
    slot(conn, f, 5, "finish",        "Finish",              1)

    functions = [
        ("ENT",   "Entry / Office"),
        ("CLS",   "Classroom"),
        ("STR",   "Storeroom"),
        ("PSG",   "Passage"),
        ("PRV",   "Privacy"),
        ("CMS",   "Communicating"),
        ("HOT",   "Hotel / Motel"),
    ]
    options(conn, f, "function", functions)

    cyls = [
        ("STD",  "Standard 6-pin"),
        ("IC",   "IC Core Prep"),
        ("SFIC", "SFIC - Small Format IC"),
        ("FSIC", "FSIC - Full Size IC"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("WIT",  "Withnell Lever"),
        ("ARC",  "Archer Lever"),
        ("BRN",  "Barton Lever"),
        ("AUG",  "August Lever"),
        ("ELN",  "Elaine Lever"),
    ]
    options(conn, f, "lever", levers)

    options(conn, f, "rose", [
        ("RND",  "Round Rose"),
        ("SQ",   "Square Rose"),
    ])

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US26", "US26 - Polished Chrome"),
        ("US4",  "US4 - Satin Brass"),
    ]
    options(conn, f, "finish", finishes)

    # Passage/Privacy hide cylinder type
    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls],
                     f"{fn} function hides cylinder")


# ═════════════════════════════════════════════════════════════════════
# SELECT SL Series Continuous Hinges
# ═════════════════════════════════════════════════════════════════════

def _seed_select(conn):
    # ── Geared Continuous ──
    f = fid(conn, "SELECT", "SL Continuous Geared Hinge",
            "Continuous Hinge",
            "SL{model} {length} {finish}",
            "SELECT SL{model} Continuous Geared {length} {finish}")

    slot(conn, f, 1, "model",   "Mounting Type",  1)
    slot(conn, f, 2, "length",  "Length",          1)
    slot(conn, f, 3, "finish",  "Finish",          1)

    models = [
        ("11",  "SL11 - Full Surface"),
        ("21",  "SL21 - Half Surface"),
        ("12",  "SL12 - Full Mortise"),
        ("22",  "SL22 - Half Mortise"),
        ("11HD","SL11HD - Full Surface, Heavy Duty"),
    ]
    options(conn, f, "model", models)

    lengths = [
        ("79",  "79\" (6'-7\")"),
        ("83",  "83\" (6'-11\")"),
        ("85",  "85\" (7'-1\")"),
        ("95",  "95\" (7'-11\")"),
    ]
    options(conn, f, "length", lengths)

    finishes = [
        ("CL",  "CL - Clear Anodized"),
        ("DU",  "DU - Dark Bronze Anodized"),
        ("BK",  "BK - Black Anodized"),
        ("P",   "P - Primed for Paint"),
    ]
    options(conn, f, "finish", finishes)

    # ── Electric Continuous (ePivot) ──
    f2 = fid(conn, "SELECT", "SL Electric Continuous Hinge",
             "Electric Hinge",
             "SL{model}-E {wires} {length} {finish}",
             "SELECT SL{model}-E {wires} {length} {finish}")

    slot(conn, f2, 1, "model",  "Mounting Type",     1)
    slot(conn, f2, 2, "wires",  "Wire Count",        1)
    slot(conn, f2, 3, "length", "Length",             1)
    slot(conn, f2, 4, "finish", "Finish",             1)

    options(conn, f2, "model", [
        ("11",  "SL11 - Full Surface"),
        ("21",  "SL21 - Half Surface"),
        ("12",  "SL12 - Full Mortise"),
    ])

    options(conn, f2, "wires", [
        ("4W",  "4 Wire"),
        ("8W",  "8 Wire"),
        ("12W", "12 Wire"),
    ])

    options(conn, f2, "length", lengths)
    options(conn, f2, "finish", finishes)
