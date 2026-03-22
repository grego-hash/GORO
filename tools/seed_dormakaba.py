"""Seed Dormakaba — Simplex pushbutton, E-Plex electronic, BTS floor closers."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_simplex(conn)
    _seed_eplex(conn)
    _seed_bts(conn)
    print("  Dormakaba Simplex + E-Plex + BTS seeded.")


# ═════════════════════════════════════════════════════════════════════
# Simplex Pushbutton Locks
# ═════════════════════════════════════════════════════════════════════

def _seed_simplex(conn):
    # ── 5000 Series (Cylindrical) ──
    f = fid(conn, "Dormakaba", "Simplex 5000 Pushbutton Cylindrical",
            "Pushbutton Lock",
            "5000-{function} {lever} {finish}",
            "Simplex 5000 {function} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",       1)
    slot(conn, f, 2, "lever",    "Lever / Knob",   1)
    slot(conn, f, 3, "finish",   "Finish",         1)

    functions = [
        ("26D",  "Entry - Passage when Unlocked"),
        ("26DW", "Entry w/ Key Override"),
        ("66",   "Passage / Office"),
        ("04",   "Privacy"),
    ]
    options(conn, f, "function", functions)

    levers = [
        ("K",   "Knob"),
        ("L",   "Lever"),
        ("LL",  "Long Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("26D",  "26D - Satin Chrome"),
        ("10B",  "10B - Oil Rubbed Bronze"),
        ("3",    "3 - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    # ── L1000 Series (Mortise) ──
    f2 = fid(conn, "Dormakaba", "Simplex L1000 Pushbutton Mortise",
             "Pushbutton Lock",
             "L1000-{function} {lever} {finish}",
             "Simplex L1000 {function} {lever} {finish}")

    slot(conn, f2, 1, "function", "Function",       1)
    slot(conn, f2, 2, "lever",    "Lever Design",   1)
    slot(conn, f2, 3, "finish",   "Finish",         1)
    slot(conn, f2, 4, "thumbturn","Thumbturn",      0)

    mort_funcs = [
        ("22",  "Entry - Passage when Unlocked"),
        ("26",  "Entry w/ Deadbolt"),
        ("64",  "Storeroom - Always Locked"),
        ("02",  "Classroom"),
    ]
    options(conn, f2, "function", mort_funcs)

    options(conn, f2, "lever", [
        ("L",  "Standard Lever"),
        ("LL", "Long Lever"),
        ("J",  "Hospital Lever"),
    ])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "thumbturn", [("NONE","None"),("TT","Thumbturn")])

    # Only Entry w/ Deadbolt gets thumbturn
    restrict(conn, f2, "function", "26", "thumbturn", ["TT", "NONE"],
             "Deadbolt function gets thumbturn option")
    for fn in ["22", "64", "02"]:
        restrict(conn, f2, "function", fn, "thumbturn", ["NONE"],
                 f"Function {fn} no thumbturn")


# ═════════════════════════════════════════════════════════════════════
# E-Plex Electronic Keypad Locks
# ═════════════════════════════════════════════════════════════════════

def _seed_eplex(conn):
    f = fid(conn, "Dormakaba", "E-Plex 2000/5000 Electronic",
            "Electronic Lock",
            "E-Plex {model} {lever} {finish}",
            "Dormakaba E-Plex {model} {lever} {finish}")

    slot(conn, f, 1, "model",    "Model",          1)
    slot(conn, f, 2, "function", "Function",       1)
    slot(conn, f, 3, "lever",    "Lever Design",   1)
    slot(conn, f, 4, "finish",   "Finish",         1)

    models = [
        ("E2000",  "E2000 - Standalone Keypad (Cylindrical)"),
        ("E2700",  "E2700 - Standalone Keypad w/ Key Override"),
        ("E5000",  "E5000 - Networked Keypad (Cylindrical)"),
        ("E5200",  "E5200 - Networked Keypad (Mortise)"),
        ("E5700",  "E5700 - Networked Keypad w/ Prox"),
    ]
    options(conn, f, "model", models)

    functions = [
        ("ENT",   "Entry"),
        ("STR",   "Storeroom"),
        ("CLS",   "Classroom"),
        ("OFF",   "Office"),
    ]
    options(conn, f, "function", functions)

    options(conn, f, "lever", [
        ("L",   "Standard Lever"),
        ("LL",  "Long Lever"),
        ("J",   "Hospital Lever"),
    ])

    options(conn, f, "finish", [
        ("26D","26D - Satin Chrome"),
        ("10B","10B - Oil Rubbed Bronze"),
        ("3",  "3 - Polished Brass"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Dormakaba BTS Floor Closers
# ═════════════════════════════════════════════════════════════════════

def _seed_bts(conn):
    f = fid(conn, "Dormakaba", "BTS Floor Closer",
            "Floor Closer",
            "BTS {model} {spindle} {cover} {finish}",
            "Dormakaba BTS {model} {spindle} {cover} {finish}")

    slot(conn, f, 1, "model",     "Model",           1)
    slot(conn, f, 2, "spindle",   "Spindle Type",    1)
    slot(conn, f, 3, "cover",     "Cover Plate",     1)
    slot(conn, f, 4, "finish",    "Finish",          1)
    slot(conn, f, 5, "hold_open", "Hold-Open",       0)

    models = [
        ("65",  "BTS 65 - Standard Duty, 105° Max"),
        ("75V", "BTS 75V - Medium Duty, 105° Max"),
        ("80",  "BTS 80 - Heavy Duty, 180° Max"),
        ("80F", "BTS 80F - Heavy Duty, Fire Rated"),
        ("84",  "BTS 84 - Extra Heavy Duty, Ext Arm"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "spindle", [
        ("CS",   "Center Hung Spindle"),
        ("OS",   "Offset Spindle"),
    ])

    options(conn, f, "cover", [
        ("CP",   "CP - Standard Cover Plate"),
        ("FCP",  "FCP - Flush Cover Plate"),
    ])

    finishes = [
        ("689",  "689 - Aluminum"),
        ("690",  "690 - Dark Bronze"),
        ("691",  "691 - Bright Chrome"),
        ("695",  "695 - Satin Brass"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "hold_open", [
        ("NONE","None"),
        ("HO",  "HO - Hold-Open"),
        ("SHO", "SHO - Selective Hold-Open"),
    ])
