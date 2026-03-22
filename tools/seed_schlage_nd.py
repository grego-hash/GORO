"""Seed Schlage ND Series cylindrical lock data.

Schlage ND Series — Grade 1 cylindrical (bored) lockset.
Part number: ND{function} {lever}{rose} {finish}
"""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


# ── Standard BHMA finishes shared across Schlage ──
SCHLAGE_FINISHES = [
    ("605",  "605 - Bright Brass"),
    ("606",  "606 - Satin Brass"),
    ("609",  "609 - Antique Brass"),
    ("612",  "612 - Satin Bronze"),
    ("613",  "613 - Oil Rubbed Bronze"),
    ("619",  "619 - Satin Nickel"),
    ("622",  "622 - Flat Black"),
    ("625",  "625 - Bright Chrome"),
    ("626",  "626 - Satin Chrome"),
    ("643e", "643e - Aged Bronze"),
]


def seed(conn):
    _seed_nd_cylindrical(conn)
    print("  Schlage ND Series seeded.")


def _seed_nd_cylindrical(conn):
    f = fid(conn,
            "Schlage",
            "ND Series Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever}{rose} {finish}",
            "Schlage ND Series {function} {lever}{rose} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)  # optional, hidden for non-keyed
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose / Escutcheon", 1)
    slot(conn, f, 5, "finish",        "Finish",         1)

    # ── Functions ──
    functions = [
        ("ND10S",  "ND10S - Passage"),
        ("ND25D",  "ND25D - Exit Lock"),
        ("ND40S",  "ND40S - Privacy / Bath"),
        ("ND44S",  "ND44S - Hospital Privacy"),
        ("ND50PD", "ND50PD - Entry / Office"),
        ("ND53PD", "ND53PD - Entrance"),
        ("ND60PD", "ND60PD - Vestibule / Apartment"),
        ("ND70PD", "ND70PD - Classroom"),
        ("ND75PD", "ND75PD - Classroom Security"),
        ("ND80PD", "ND80PD - Storeroom"),
        ("ND82PD", "ND82PD - Institution"),
        ("ND85PD", "ND85PD - Faculty Restroom"),
        ("ND91PD", "ND91PD - Entrance / Office (Vandlgard)"),
        ("ND94PD", "ND94PD - Vandlgard Storeroom"),
        ("ND95PD", "ND95PD - Classroom Security w/ Indicator"),
        ("ND96PD", "ND96PD - Storeroom w/ Indicator"),
        ("ND97PD", "ND97PD - Corridor"),
    ]
    options(conn, f, "function", functions)

    # ── Cylinder Type ──
    cylinder_types = [
        ("C",   "C - Conventional 6-Pin (C Keyway)"),
        ("CE",  "CE - Conventional Everest"),
        ("CP",  "CP - Conventional Primus"),
        ("CEP", "CEP - Conventional Everest Primus"),
        ("J",   "J - Less FSIC"),
        ("R",   "R - FSIC Construction Core"),
        ("F",   "F - FSIC 6-Pin"),
        ("FE",  "FE - FSIC Everest"),
        ("FP",  "FP - FSIC Primus"),
        ("FEP", "FEP - FSIC Everest Primus"),
        ("G",   "G - SFIC 7-Pin"),
        ("H",   "H - SFIC Construction Core"),
        ("BD",  "BD - SFIC Best-Type D Core"),
        ("B",   "B - Less SFIC"),
        ("L",   "L - Less Cylinder"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # Non-keyed functions → hide cylinder
    non_keyed = {"ND10S", "ND25D", "ND40S", "ND44S"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Lever Designs ──
    levers = [
        ("ATH", "ATH - Athens"),
        ("SPA", "SPA - Sparta"),
        ("RHO", "RHO - Rhodes"),
        ("TLR", "TLR - Tubular Return"),
        ("BRW", "BRW - Broadway"),
        ("LON", "LON - Longitude"),
        ("LAT", "LAT - Latitude"),
        ("ACC", "ACC - Accent"),
        ("MER", "MER - Merano"),
        ("OME", "OME - Omega"),
        ("GRW", "GRW - Greenwich"),
        ("JUP", "JUP - Jupiter (Healthcare)"),
        ("SAT", "SAT - Saturn (Healthcare)"),
        ("NEP", "NEP - Neptune (Healthcare)"),
    ]
    options(conn, f, "lever", levers)

    # ── Rose / Escutcheon ──
    roses = [
        ("RLD", "RLD - Standard Round Rose"),
        ("ECS", "ECS - Escutcheon Plate"),
    ]
    options(conn, f, "rose", roses)

    # ── Finishes ──
    options(conn, f, "finish", SCHLAGE_FINISHES)

    # ── Finish restrictions for select lever designs ──
    # Longitude/Latitude/Merano/Accent → limited finishes
    limited_finish_levers = ["LON", "LAT", "MER", "ACC"]
    limited_finishes = ["605", "606", "609", "612", "613", "619", "625", "626"]
    for lev in limited_finish_levers:
        restrict(conn, f, "lever", lev, "finish", limited_finishes,
                 "Limited finishes for designer lever")

    # Healthcare levers (JUP/SAT/NEP) → 626 and 630 typically
    healthcare_finishes = ["619", "625", "626"]
    for lev in ["JUP", "SAT", "NEP"]:
        restrict(conn, f, "lever", lev, "finish", healthcare_finishes,
                 "Healthcare lever finish restriction")
