"""Seed institutional / behavioral health — Marks USA, Townsteel."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_marks(conn)
    _seed_townsteel(conn)
    print("  Marks USA + Townsteel seeded.")


# ═════════════════════════════════════════════════════════════════════
# Marks USA — 5SS Series Institutional Mortise Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_marks(conn):
    f = fid(conn, "Marks USA", "5SS Series Institutional Mortise Lock",
            "Mortise Lock",
            "5SS-{function} {lever} {finish}",
            "Marks 5SS {function} {lever} {finish}")

    slot(conn, f, 1, "function",      "Function",          1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",     1)
    slot(conn, f, 3, "lever",         "Lever Design",      1)
    slot(conn, f, 4, "finish",        "Finish",            1)
    slot(conn, f, 5, "thumbturn",     "Thumbturn",         0)

    functions = [
        ("ENT",  "Entry / Office"),
        ("CLS",  "Classroom"),
        ("STR",  "Storeroom"),
        ("PRV",  "Privacy"),
        ("SEC",  "Classroom Security (Lockdown)"),
        ("APT",  "Apartment Entry"),
        ("PSG",  "Passage"),
        ("DB",   "Deadbolt Only"),
    ]
    options(conn, f, "function", functions)

    cyls = [
        ("STD",  "Standard 6-Pin"),
        ("IC",   "IC Core Prep"),
        ("SFIC", "SFIC - Small Format IC"),
        ("FSIC", "FSIC - Full Size IC"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("LV1",  "Standard Lever"),
        ("LV2",  "Institutional Lever"),
        ("LV3",  "Ligature-Resistant Lever"),
        ("LV5",  "Knurled Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "thumbturn", [("NONE","None"),("TT","Thumbturn")])

    # Passage/Privacy → no cylinder
    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")

    # Only deadbolt/apartment function gets thumbturn
    for fn in ["ENT", "CLS", "STR", "PRV", "SEC", "PSG"]:
        restrict(conn, f, "function", fn, "thumbturn", ["NONE"],
                 f"{fn} → no thumbturn")

    # ── Marks 195SS Series Cylindrical ──
    f2 = fid(conn, "Marks USA", "195SS Institutional Cylindrical Lock",
             "Cylindrical Lock",
             "195SS-{function} {lever} {finish}",
             "Marks 195SS {function} {lever} {finish}")

    slot(conn, f2, 1, "function",      "Function",        1)
    slot(conn, f2, 2, "cylinder_type", "Cylinder Type",   1)
    slot(conn, f2, 3, "lever",         "Lever / Knob",    1)
    slot(conn, f2, 4, "finish",        "Finish",          1)

    options(conn, f2, "function", [
        ("ENT","Entry / Office"),("CLS","Classroom"),
        ("STR","Storeroom"),("PSG","Passage"),("PRV","Privacy"),
    ])
    options(conn, f2, "cylinder_type", cyls)
    options(conn, f2, "lever", [
        ("K",  "Knob"),("L",  "Standard Lever"),
        ("IL", "Institutional Lever"),
    ])
    options(conn, f2, "finish", finishes)

    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f2, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")


# ═════════════════════════════════════════════════════════════════════
# Townsteel — Ligature Resistant Hardware
# ═════════════════════════════════════════════════════════════════════

def _seed_townsteel(conn):
    # ── CRX-A / CRX-K Ligature-Resistant Cylindrical ──
    f = fid(conn, "Townsteel", "CRX Ligature-Resistant Cylindrical Lock",
            "Ligature-Resistant Lock",
            "CRX-{function} {lever} {finish}",
            "Townsteel CRX {function} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",        1)
    slot(conn, f, 2, "lever",    "Trim Design",     1)
    slot(conn, f, 3, "finish",   "Finish",          1)

    functions = [
        ("ENT", "Entry / Office"),
        ("CLS", "Classroom"),
        ("STR", "Storeroom"),
        ("PSG", "Passage"),
        ("PRV", "Privacy"),
        ("SEC", "Classroom Security (Lockdown)"),
    ]
    options(conn, f, "function", functions)

    levers = [
        ("A",  "Anti-Ligature Lever (Rotating)"),
        ("K",  "Anti-Ligature Knob"),
        ("AL", "Anti-Ligature Lever (Fixed Return)"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
    ]
    options(conn, f, "finish", finishes)

    # ── MRX-A Ligature-Resistant Mortise ──
    f2 = fid(conn, "Townsteel", "MRX Ligature-Resistant Mortise Lock",
             "Ligature-Resistant Lock",
             "MRX-{function} {lever} {finish}",
             "Townsteel MRX {function} {lever} {finish}")

    slot(conn, f2, 1, "function", "Function",       1)
    slot(conn, f2, 2, "lever",    "Trim Design",    1)
    slot(conn, f2, 3, "finish",   "Finish",         1)
    slot(conn, f2, 4, "thumbturn","Thumbturn",      0)

    options(conn, f2, "function", functions)
    options(conn, f2, "lever", levers)
    options(conn, f2, "finish", finishes)
    options(conn, f2, "thumbturn", [("NONE","None"),("ALT","Anti-Ligature Thumbturn")])

    # Only Entry/Apartment gets thumbturn
    for fn in ["CLS", "STR", "PSG", "PRV", "SEC"]:
        restrict(conn, f2, "function", fn, "thumbturn", ["NONE"],
                 f"{fn} → no thumbturn")

    # ── Ligature-Resistant Trim for Exit Devices ──
    f3 = fid(conn, "Townsteel", "Anti-Ligature Exit Trim",
             "Ligature-Resistant Trim",
             "TRX-{model} {finish}",
             "Townsteel TRX {model} Exit Trim {finish}")

    slot(conn, f3, 1, "model",  "Trim Model",  1)
    slot(conn, f3, 2, "finish", "Finish",       1)

    options(conn, f3, "model", [
        ("L",  "Lever Trim (Anti-Ligature)"),
        ("K",  "Knob Trim (Anti-Ligature)"),
        ("PT", "Pull Trim (Anti-Ligature)"),
    ])
    options(conn, f3, "finish", finishes)
