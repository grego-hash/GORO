"""Seed Arrow — budget commercial cylindrical and mortise locks."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_arrow_cylindrical(conn)
    _seed_arrow_mortise(conn)
    _seed_arrow_exit(conn)
    print("  Arrow locks + exit devices seeded.")


# ═════════════════════════════════════════════════════════════════════
# Arrow GLK / RL Series Cylindrical Lockset
# ═════════════════════════════════════════════════════════════════════

def _seed_arrow_cylindrical(conn):
    f = fid(conn, "Arrow", "GLK Series Cylindrical Lock",
            "Cylindrical Lock",
            "GLK-{function} {lever} {finish}",
            "Arrow GLK {function} {lever} {finish}")

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
        ("HOT", "Hotel / Motel"),
    ]
    options(conn, f, "function", functions)

    cyls = [
        ("STD",  "Standard 6-Pin"),
        ("IC",   "IC Core Prep"),
        ("SFIC", "SFIC - Small Format IC"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("SIE",  "Sierra Lever"),
        ("HAR",  "Harper Lever"),
        ("DON",  "Donovan Lever"),
        ("BRD",  "Broadway Lever"),
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


# ═════════════════════════════════════════════════════════════════════
# Arrow AM Series Mortise Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_arrow_mortise(conn):
    f = fid(conn, "Arrow", "AM Series Mortise Lock",
            "Mortise Lock",
            "AM-{function} {lever} {finish}",
            "Arrow AM {function} {lever} {finish}")

    slot(conn, f, 1, "function",      "Function",        1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",   1)
    slot(conn, f, 3, "lever",         "Lever Design",    1)
    slot(conn, f, 4, "escutcheon",    "Escutcheon",      1)
    slot(conn, f, 5, "finish",        "Finish",          1)
    slot(conn, f, 6, "thumbturn",     "Thumbturn",       0)

    functions = [
        ("ENT", "Entry / Office"),
        ("CLS", "Classroom"),
        ("STR", "Storeroom"),
        ("PSG", "Passage"),
        ("PRV", "Privacy"),
        ("APT", "Apartment Entry"),
    ]
    options(conn, f, "function", functions)

    cyls = [
        ("STD",  "Standard 6-Pin"),
        ("IC",   "IC Core Prep"),
        ("SFIC", "SFIC - Small Format IC"),
    ]
    options(conn, f, "cylinder_type", cyls)

    levers = [
        ("SIE",  "Sierra Lever"),
        ("HAR",  "Harper Lever"),
        ("DON",  "Donovan Lever"),
    ]
    options(conn, f, "lever", levers)

    options(conn, f, "escutcheon", [("ROS","Rose"),("PLT","Plate")])

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "thumbturn", [("NONE","None"),("TT","Thumbturn")])

    for fn in ["PSG", "PRV"]:
        conflict_all(conn, f, "function", [fn], "cylinder_type",
                     [c[0] for c in cyls], f"{fn} hides cylinder")
    for fn in ["ENT", "CLS", "STR", "PSG", "PRV"]:
        restrict(conn, f, "function", fn, "thumbturn", ["NONE"],
                 f"{fn} → no thumbturn")


# ═════════════════════════════════════════════════════════════════════
# Arrow S1200 Exit Device
# ═════════════════════════════════════════════════════════════════════

def _seed_arrow_exit(conn):
    f = fid(conn, "Arrow", "S1200 Series Exit Device",
            "Exit Device",
            "S1200-{model} {trim} {finish}",
            "Arrow S1200 {model} {trim} {finish}")

    slot(conn, f, 1, "model",   "Device Type",   1)
    slot(conn, f, 2, "trim",    "Trim Type",      1)
    slot(conn, f, 3, "finish",  "Finish",         1)
    slot(conn, f, 4, "size",    "Door Width",     1)
    slot(conn, f, 5, "handing", "Handing",        1)

    options(conn, f, "model", [
        ("RIM",  "Rim Exit Device"),
        ("SVR",  "SVR - Surface Vertical Rod"),
        ("CVR",  "CVR - Concealed Vertical Rod"),
        ("MORT", "Mortise Exit Device"),
    ])

    options(conn, f, "trim", [
        ("EO", "EO - Exit Only"),
        ("LT", "LT - Lever Trim"),
        ("PT", "PT - Pull Trim"),
    ])

    options(conn, f, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US28", "US28 - Satin Aluminum"),
    ])

    options(conn, f, "size", [("36","36\""),("48","48\"")])
    options(conn, f, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])
