"""Seed BEST 45H Series Mortise Lock data."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


BEST_FINISHES = [
    ("605",  "605 - Bright Brass"),
    ("606",  "606 - Satin Brass"),
    ("612",  "612 - Satin Bronze"),
    ("613",  "613 - Oil Rubbed Bronze"),
    ("619",  "619 - Satin Nickel"),
    ("625",  "625 - Bright Chrome"),
    ("626",  "626 - Satin Chrome"),
    ("630",  "630 - Satin Stainless Steel"),
    ("643e", "643e - Aged Bronze"),
]


def seed(conn):
    _seed_45h(conn)
    print("  BEST 45H seeded.")


def _seed_45h(conn):
    f = fid(conn,
            "BEST",
            "45H Series Mortise Lock",
            "Mortise Lockset",
            "45H{function} {cylinder_type} {lever}{escutcheon} {finish}",
            "BEST 45H {function} {lever}{escutcheon} {finish}")

    slot(conn, f, 1, "function",      "Function",       1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "escutcheon",    "Escutcheon",     1)
    slot(conn, f, 5, "finish",        "Finish",         1)
    slot(conn, f, 6, "handing",       "Handing",        0)
    slot(conn, f, 7, "thumbturn",     "Thumbturn",      0)

    functions = [
        ("45HCA",  "45HCA - Passage"),
        ("45HBA",  "45HBA - Privacy / Bath"),
        ("45HDA",  "45HDA - Apartment / Vestibule"),
        ("45HFA",  "45HFA - Dormitory"),
        ("45HGA",  "45HGA - Classroom"),
        ("45HHA",  "45HHA - Storeroom"),
        ("45HJA",  "45HJA - Institution"),
        ("45HKA",  "45HKA - Entrance"),
        ("45HLA",  "45HLA - Corridor (Deadbolt)"),
        ("45HMA",  "45HMA - Faculty Restroom"),
        ("45HNA",  "45HNA - Classroom Security"),
        ("45HPA",  "45HPA - Office / Entry"),
        ("45HRA",  "45HRA - Entrance w/ Deadbolt"),
        ("45HTA",  "45HTA - Vandlgard Storeroom"),
        ("45HWA",  "45HWA - Corridor w/ Indicator"),
    ]
    options(conn, f, "function", functions)

    cylinder_types = [
        ("STD",   "Standard 7-Pin (BEST Keyway)"),
        ("ARR",   "Arrow Keyway"),
        ("CORE",  "Standard Core"),
        ("CCORE", "Construction Core"),
        ("LESS",  "Less Core"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    non_keyed = {"45HCA", "45HBA"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    levers = [
        ("D",   "D - D-Design"),
        ("H",   "H - H-Design"),
        ("J",   "J - J-Design"),
        ("K",   "K - K-Design"),
        ("N",   "N - N-Design"),
        ("S",   "S - S-Design"),
        ("W",   "W - W-Design"),
        ("V",   "V - V-Design (Vandlgard)"),
        ("R",   "R - R-Design (Return)"),
        ("L",   "L - L-Design (Decorative)"),
    ]
    options(conn, f, "lever", levers)

    escutcheons = [
        ("T",  "T - T-Plate (Full Escutcheon)"),
        ("N",  "N - N-Plate (Sectional)"),
        ("W",  "W - W-Plate (Windsor)"),
        ("O",  "O - O-Plate (Oval Sectional)"),
    ]
    options(conn, f, "escutcheon", escutcheons)

    options(conn, f, "finish", BEST_FINISHES)

    handing = [("LH", "Left Hand"), ("RH", "Right Hand"),
               ("LHR", "Left Hand Reverse"), ("RHR", "Right Hand Reverse")]
    options(conn, f, "handing", handing)

    thumbturn_options = [
        ("STD", "Standard Thumbturn"),
        ("BVL", "Beveled Thumbturn"),
        ("ADA", "ADA Compliant Thumbturn"),
    ]
    options(conn, f, "thumbturn", thumbturn_options)
    tt_funcs = {"45HBA", "45HDA", "45HFA", "45HKA", "45HLA",
                "45HMA", "45HPA", "45HRA", "45HWA"}
    no_tt = [fn[0] for fn in functions if fn[0] not in tt_funcs]
    for func_val in no_tt:
        for tt in thumbturn_options:
            rule(conn, f, "conflict", "function", func_val, "thumbturn", tt[0],
                 "Thumbturn not applicable")
