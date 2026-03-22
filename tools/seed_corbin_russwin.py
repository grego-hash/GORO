"""Seed Corbin Russwin ML2000 Mortise Lock and CL3300 Cylindrical Lock data."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


# ── Standard BHMA finishes for Corbin Russwin ──
CR_FINISHES = [
    ("605",  "605 - Bright Brass"),
    ("606",  "606 - Satin Brass"),
    ("612",  "612 - Satin Bronze"),
    ("613",  "613 - Oil Rubbed Bronze"),
    ("618",  "618 - Bright Nickel"),
    ("619",  "619 - Satin Nickel"),
    ("622",  "622 - Flat Black"),
    ("625",  "625 - Bright Chrome"),
    ("626",  "626 - Satin Chrome"),
    ("630",  "630 - Satin Stainless Steel"),
    ("643e", "643e - Aged Bronze"),
]


def seed(conn):
    _seed_ml2000(conn)
    _seed_cl3300(conn)
    print("  Corbin Russwin ML2000 + CL3300 seeded.")


# ═════════════════════════════════════════════════════════════════════
# ML2000 Series Mortise Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_ml2000(conn):
    f = fid(conn,
            "Corbin Russwin",
            "ML2000 Series Mortise Lock",
            "Mortise Lockset",
            "ML{function} {cylinder_type} {lever} {escutcheon} {finish}",
            "Corbin Russwin ML2000 {function} {lever} {escutcheon} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",        1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",   0)
    slot(conn, f, 3, "lever",         "Lever Design",    1)
    slot(conn, f, 4, "escutcheon",    "Escutcheon",      1)
    slot(conn, f, 5, "finish",        "Finish",          1)
    slot(conn, f, 6, "handing",       "Handing",         0)
    slot(conn, f, 7, "thumbturn",     "Thumbturn",       0)

    # ── Functions ──
    functions = [
        ("ML2010", "ML2010 - Passage"),
        ("ML2020", "ML2020 - Privacy"),
        ("ML2024", "ML2024 - Entrance / Apartment (Deadbolt)"),
        ("ML2030", "ML2030 - Entrance / Apartment"),
        ("ML2032", "ML2032 - Institution"),
        ("ML2042", "ML2042 - Entrance (Deadbolt + Deadlatch)"),
        ("ML2051", "ML2051 - Office / Entry"),
        ("ML2053", "ML2053 - Entrance"),
        ("ML2054", "ML2054 - Corridor (Deadbolt + Indicator)"),
        ("ML2055", "ML2055 - Classroom"),
        ("ML2056", "ML2056 - Classroom Security"),
        ("ML2057", "ML2057 - Storeroom"),
        ("ML2058", "ML2058 - Storeroom (Deadbolt)"),
        ("ML2059", "ML2059 - Vestibule"),
        ("ML2065", "ML2065 - Dormitory / Bedroom"),
        ("ML2067", "ML2067 - Asylum / Institution"),
    ]
    options(conn, f, "function", functions)

    # ── Cylinder Type ──
    cylinder_types = [
        ("6PIN",  "6-Pin Conventional (Standard)"),
        ("LFIC",  "LFIC - Large Format IC"),
        ("SFIC",  "SFIC - Small Format IC"),
        ("LESS",  "Less Cylinder"),
        ("CONST", "Construction Core"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # Non-keyed: hide cylinder
    non_keyed = {"ML2010", "ML2020"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Lever Designs ──
    levers = [
        ("NAC",  "NAC - Newport"),
        ("SAC",  "SAC - Sargent"),
        ("LWM",  "LWM - Lustra"),
        ("DSM",  "DSM - Dirke"),
        ("MUM",  "MUM - Munroe"),
        ("RSM",  "RSM - Regis"),
        ("CSM",  "CSM - Corsica"),
        ("GRC",  "GRC - Grier"),
        ("NSA",  "NSA - Newport Anti-Microbial"),
    ]
    options(conn, f, "lever", levers)

    # ── Escutcheons ──
    escutcheons = [
        ("M",  "M - Montrose (Full Escutcheon)"),
        ("N",  "N - Norwood (Sectional)"),
        ("S",  "S - Sterling (Sectional)"),
        ("C",  "C - Citation (Sectional)"),
        ("E",  "E - Essex (Full Escutcheon)"),
    ]
    options(conn, f, "escutcheon", escutcheons)

    # ── Finishes ──
    options(conn, f, "finish", CR_FINISHES)

    # ── Handing ──
    handing = [("LH", "LH - Left Hand"), ("RH", "RH - Right Hand")]
    options(conn, f, "handing", handing)

    # ── Thumbturn ──
    thumbturn_options = [
        ("STD", "Standard Thumbturn"),
    ]
    options(conn, f, "thumbturn", thumbturn_options)

    thumbturn_funcs = {"ML2020", "ML2024", "ML2030", "ML2042", "ML2051",
                       "ML2053", "ML2054", "ML2065"}
    no_tt = [fn[0] for fn in functions if fn[0] not in thumbturn_funcs]
    for func_val in no_tt:
        for tt in thumbturn_options:
            rule(conn, f, "conflict", "function", func_val, "thumbturn", tt[0],
                 "Thumbturn not applicable")


# ═════════════════════════════════════════════════════════════════════
# CL3300 Series Cylindrical Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_cl3300(conn):
    f = fid(conn,
            "Corbin Russwin",
            "CL3300 Series Cylindrical Lock",
            "Cylindrical Lockset",
            "CL{function} {lever} {finish}",
            "Corbin Russwin CL3300 {function} {lever} {finish}")

    slot(conn, f, 1, "function",      "Function",       1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose",           1)
    slot(conn, f, 5, "finish",        "Finish",         1)

    functions = [
        ("CL3310", "CL3310 - Passage"),
        ("CL3320", "CL3320 - Privacy"),
        ("CL3351", "CL3351 - Entry / Office"),
        ("CL3353", "CL3353 - Entrance"),
        ("CL3355", "CL3355 - Classroom"),
        ("CL3357", "CL3357 - Storeroom"),
        ("CL3370", "CL3370 - Classroom"),
        ("CL3372", "CL3372 - Institution"),
        ("CL3380", "CL3380 - Vestibule"),
        ("CL3390", "CL3390 - Full Dummy"),
    ]
    options(conn, f, "function", functions)

    cylinder_types = [
        ("6PIN",  "6-Pin Conventional"),
        ("LFIC",  "LFIC - Large Format IC"),
        ("SFIC",  "SFIC - Small Format IC"),
        ("LESS",  "Less Cylinder"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    non_keyed = {"CL3310", "CL3320", "CL3390"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    levers = [
        ("NAC", "NAC - Newport"),
        ("SAC", "SAC - Sargent"),
        ("LWM", "LWM - Lustra"),
        ("DSM", "DSM - Dirke"),
        ("MUM", "MUM - Munroe"),
        ("GRC", "GRC - Grier"),
    ]
    options(conn, f, "lever", levers)

    roses = [
        ("NZD", "NZD - Princeton Rose"),
        ("PZD", "PZD - Pacific Rose"),
    ]
    options(conn, f, "rose", roses)

    options(conn, f, "finish", CR_FINISHES)
