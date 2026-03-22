"""Seed value-line commercial hardware — DCI, PDQ, Cal-Royal."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_dci(conn)
    _seed_pdq(conn)
    _seed_cal_royal(conn)
    print("  DCI + PDQ + Cal-Royal seeded.")


# ═════════════════════════════════════════════════════════════════════
# DCI (Door Controls International) — Self-Closing Hinges
# ═════════════════════════════════════════════════════════════════════

def _seed_dci(conn):
    f = fid(conn, "DCI", "Self-Closing Spring Hinge",
            "Spring Hinge",
            "{model} {size} {finish}",
            "DCI {model} Spring Hinge {size} {finish}")

    slot(conn, f, 1, "model",  "Model",      1)
    slot(conn, f, 2, "size",   "Size",        1)
    slot(conn, f, 3, "finish", "Finish",      1)

    options(conn, f, "model", [
        ("2800",  "2800 - Commercial Spring Hinge, UL Listed"),
        ("2801",  "2801 - Spring Hinge, Adjustable Tension"),
        ("2803",  "2803 - Spring Hinge w/ Hold-Open"),
    ])

    options(conn, f, "size", [
        ("3.5x3.5", "3-1/2\" x 3-1/2\""),
        ("4x4",     "4\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
    ])

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("P",    "P - Primed for Paint"),
    ]
    options(conn, f, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# PDQ — Commercial Cylindrical & Mortise Locks
# ═════════════════════════════════════════════════════════════════════

def _seed_pdq(conn):
    # ── GT Series Cylindrical ──
    f = fid(conn, "PDQ", "GT Series Cylindrical Lock",
            "Cylindrical Lock",
            "GT-{function} {lever} {finish}",
            "PDQ GT {function} {lever} {finish}")

    slot(conn, f, 1, "function",      "Function",        1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",   1)
    slot(conn, f, 3, "lever",         "Lever Design",    1)
    slot(conn, f, 4, "finish",        "Finish",          1)

    functions = [
        ("ENT", "Entry / Office"),
        ("CLS", "Classroom"),
        ("STR", "Storeroom"),
        ("PSG", "Passage"),
        ("PRV", "Privacy"),
        ("CMS", "Communicating"),
    ]
    options(conn, f, "function", functions)

    cyls = [
        ("STD",  "Standard 6-Pin"),
        ("IC",   "IC Core Prep"),
        ("SFIC", "SFIC - Small Format IC"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("SA",  "SA - St. Albans Lever"),
        ("SD",  "SD - Stanford Lever"),
        ("SE",  "SE - Sierra Lever"),
        ("SV",  "SV - Seville Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")

    # ── MR Series Mortise ──
    f2 = fid(conn, "PDQ", "MR Series Mortise Lock",
             "Mortise Lock",
             "MR-{function} {lever} {finish}",
             "PDQ MR {function} {lever} {finish}")

    slot(conn, f2, 1, "function",      "Function",        1)
    slot(conn, f2, 2, "cylinder_type", "Cylinder Type",   1)
    slot(conn, f2, 3, "lever",         "Lever Design",    1)
    slot(conn, f2, 4, "escutcheon",    "Escutcheon",      1)
    slot(conn, f2, 5, "finish",        "Finish",          1)
    slot(conn, f2, 6, "thumbturn",     "Thumbturn",       0)

    mort_funcs = [
        ("ENT", "Entry / Office"),
        ("CLS", "Classroom"),
        ("STR", "Storeroom"),
        ("PSG", "Passage"),
        ("PRV", "Privacy"),
        ("APT", "Apartment Entry"),
        ("DB",  "Deadbolt Only"),
    ]
    options(conn, f2, "function", mort_funcs)
    options(conn, f2, "cylinder_type", cyls)
    options(conn, f2, "lever", levers)

    options(conn, f2, "escutcheon", [
        ("ER", "ER - Rose Escutcheon"),
        ("EP", "EP - Plate Escutcheon"),
    ])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "thumbturn", [("NONE","None"),("TT","Thumbturn")])

    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f2, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")
    for fn in ["ENT", "CLS", "STR", "PSG", "PRV"]:
        restrict(conn, f2, "function", fn, "thumbturn", ["NONE"],
                 f"{fn} → no thumbturn")

    # ── SD Series Exit Device ──
    f3 = fid(conn, "PDQ", "SD Series Exit Device",
             "Exit Device",
             "SD-{model} {trim} {finish}",
             "PDQ SD {model} {trim} {finish}")

    slot(conn, f3, 1, "model",   "Device Type",    1)
    slot(conn, f3, 2, "trim",    "Trim Type",       1)
    slot(conn, f3, 3, "lever",   "Lever Design",    0)
    slot(conn, f3, 4, "finish",  "Finish",          1)
    slot(conn, f3, 5, "size",    "Door Width",      1)
    slot(conn, f3, 6, "handing", "Handing",         1)

    options(conn, f3, "model", [
        ("4200",  "4200 - Rim Exit Device"),
        ("4300",  "4300 - Mortise Exit Device"),
        ("4500",  "4500 - SVR Exit Device"),
        ("4700",  "4700 - CVR Exit Device"),
    ])

    trims = [
        ("BP",  "BP - Bar Only (No Trim)"),
        ("LT",  "LT - Lever Trim"),
        ("PT",  "PT - Pull Trim"),
    ]
    options(conn, f3, "trim", trims)
    options(conn, f3, "lever", levers)
    options(conn, f3, "finish", finishes)
    options(conn, f3, "size", [("36","36\""),("48","48\"")])
    options(conn, f3, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    for t in ["BP", "PT"]:
        conflict_all(conn, f3, "trim", [t], "lever",
                     [l[0] for l in levers], f"Trim {t} hides lever")


# ═════════════════════════════════════════════════════════════════════
# Cal-Royal — Value-Line Commercial Hardware
# ═════════════════════════════════════════════════════════════════════

def _seed_cal_royal(conn):
    # ── NM Series Cylindrical ──
    f = fid(conn, "Cal-Royal", "NM Series Cylindrical Lock",
            "Cylindrical Lock",
            "NM-{function} {lever} {finish}",
            "Cal-Royal NM {function} {lever} {finish}")

    slot(conn, f, 1, "function",      "Function",        1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",   1)
    slot(conn, f, 3, "lever",         "Lever Design",    1)
    slot(conn, f, 4, "finish",        "Finish",          1)

    functions = [
        ("ENT", "Entry / Office"),
        ("CLS", "Classroom"),
        ("STR", "Storeroom"),
        ("PSG", "Passage"),
        ("PRV", "Privacy"),
    ]
    options(conn, f, "function", functions)

    cyls = [
        ("STD","Standard 6-Pin"),
        ("IC", "IC Core Prep"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("GE", "Genesee Lever"),
        ("EX", "Exeter Lever"),
        ("HE", "Heritage Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")

    # ── 9800 Series Exit Device ──
    f2 = fid(conn, "Cal-Royal", "9800 Series Exit Device",
             "Exit Device",
             "9800-{model} {trim} {finish}",
             "Cal-Royal 9800 {model} {trim} {finish}")

    slot(conn, f2, 1, "model",   "Device Type",   1)
    slot(conn, f2, 2, "trim",    "Trim Type",      1)
    slot(conn, f2, 3, "finish",  "Finish",         1)
    slot(conn, f2, 4, "size",    "Door Width",     1)
    slot(conn, f2, 5, "handing", "Handing",        1)

    options(conn, f2, "model", [
        ("RIM",  "Rim Exit"),
        ("SVR",  "SVR - Surface Vertical Rod"),
        ("CVR",  "CVR - Concealed Vertical Rod"),
    ])
    options(conn, f2, "trim", [
        ("NL",  "NL - No Lever (Exit Only)"),
        ("LT",  "LT - Lever Trim"),
        ("PT",  "PT - Pull Trim"),
    ])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "size", [("36","36\""),("48","48\"")])
    options(conn, f2, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])
