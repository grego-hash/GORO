"""Seed Falcon — exit devices and mortise/cylindrical locks."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_falcon_exit(conn)
    _seed_falcon_locks(conn)
    print("  Falcon exit devices + locks seeded.")


# ═════════════════════════════════════════════════════════════════════
# Falcon 24/25 Series Exit Devices
# ═════════════════════════════════════════════════════════════════════

def _seed_falcon_exit(conn):
    f = fid(conn, "Falcon", "24/25 Series Exit Device",
            "Exit Device",
            "{model} {trim} {finish}",
            "Falcon {model} {trim} {finish}")

    slot(conn, f, 1, "model",   "Device Type",    1)
    slot(conn, f, 2, "trim",    "Trim Type",       1)
    slot(conn, f, 3, "lever",   "Lever Design",    0)
    slot(conn, f, 4, "finish",  "Finish",          1)
    slot(conn, f, 5, "size",    "Door Width",      1)
    slot(conn, f, 6, "handing", "Handing",         1)

    models = [
        ("24-R",   "24-R - Rim Exit, Standard"),
        ("24-V",   "24-V - Vertical Rod, Surface"),
        ("24-C",   "24-C - Vertical Rod, Concealed"),
        ("25-R",   "25-R - Rim Exit, Fire Rated"),
        ("25-V",   "25-V - Vertical Rod, Fire Rated"),
        ("25-C",   "25-C - CVR, Fire Rated"),
        ("24-M",   "24-M - Mortise Exit"),
    ]
    options(conn, f, "model", models)

    trims = [
        ("EO",   "EO - Exit Only (No Trim)"),
        ("LT",   "LT - Lever Trim"),
        ("PT",   "PT - Pull Trim"),
        ("TP",   "TP - Thumbpiece Trim"),
        ("DT",   "DT - Dummy Trim"),
    ]
    options(conn, f, "trim", trims)

    levers = [
        ("DAN", "DAN - Dane Lever"),
        ("FAL", "FAL - Falcon Lever"),
        ("LON", "LON - Longitude Lever"),
        ("LAT", "LAT - Latitude Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US28", "US28 - Satin Aluminum"),
        ("US10B","US10B - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "size", [("36","36\""),("48","48\"")])
    options(conn, f, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    # Hide lever unless lever trim
    for t in ["EO", "PT", "TP", "DT"]:
        conflict_all(conn, f, "trim", [t], "lever",
                     [l[0] for l in levers], f"Trim {t} hides lever")

    # ── MA Series (Wide-Stile) ──
    f2 = fid(conn, "Falcon", "MA Series Exit Device",
             "Exit Device",
             "MA{model} {trim} {finish}",
             "Falcon MA{model} {trim} {finish}")

    slot(conn, f2, 1, "model",   "Device Type",   1)
    slot(conn, f2, 2, "trim",    "Trim Type",      1)
    slot(conn, f2, 3, "lever",   "Lever Design",   0)
    slot(conn, f2, 4, "finish",  "Finish",         1)
    slot(conn, f2, 5, "size",    "Door Width",     1)
    slot(conn, f2, 6, "handing", "Handing",        1)

    options(conn, f2, "model", [
        ("101",  "MA101 - Rim Exit"),
        ("301",  "MA301 - SVR Exit"),
        ("501",  "MA501 - CVR Exit"),
        ("201",  "MA201 - Mortise Exit"),
    ])
    options(conn, f2, "trim", trims)
    options(conn, f2, "lever", levers)
    options(conn, f2, "finish", finishes)
    options(conn, f2, "size", [("36","36\""),("48","48\"")])
    options(conn, f2, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    for t in ["EO", "PT", "TP", "DT"]:
        conflict_all(conn, f2, "trim", [t], "lever",
                     [l[0] for l in levers], f"Trim {t} hides lever")


# ═════════════════════════════════════════════════════════════════════
# Falcon W Series Cylindrical + MA Mortise Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_falcon_locks(conn):
    # ── W Series Cylindrical ──
    f = fid(conn, "Falcon", "W Series Cylindrical Lock",
            "Cylindrical Lock",
            "W{function} {lever} {finish}",
            "Falcon W {function} {lever} {finish}")

    slot(conn, f, 1, "function",      "Function",        1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",   1)
    slot(conn, f, 3, "lever",         "Lever Design",    1)
    slot(conn, f, 4, "rose",          "Rose",            1)
    slot(conn, f, 5, "finish",        "Finish",          1)

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
        ("FSIC", "FSIC - Full Size IC"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("DAN", "DAN - Dane Lever"),
        ("FAL", "FAL - Falcon Lever"),
        ("LON", "LON - Longitude Lever"),
        ("LAT", "LAT - Latitude Lever"),
        ("AGN", "AGN - Agion Antimicrobial Lever"),
    ]
    options(conn, f, "lever", levers)

    options(conn, f, "rose", [("RND","Round Rose"),("SQ","Square Rose")])

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

    # ── MA Series Mortise Lock ──
    f2 = fid(conn, "Falcon", "MA Series Mortise Lock",
             "Mortise Lock",
             "MA{function} {lever} {finish}",
             "Falcon MA {function} {lever} {finish}")

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
    options(conn, f2, "escutcheon", [("ROS","Rose"),("PLT","Plate")])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "thumbturn", [("NONE","None"),("TT","Thumbturn")])

    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f2, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")
    for fn in ["ENT", "CLS", "STR", "PSG", "PRV"]:
        restrict(conn, f2, "function", fn, "thumbturn", ["NONE"],
                 f"{fn} → no thumbturn")
