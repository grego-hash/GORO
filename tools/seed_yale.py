"""Seed Yale 8800FL Mortise Lock and 4700LN Cylindrical Lock data."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


YALE_FINISHES = [
    ("605",  "605 - Bright Brass"),
    ("606",  "606 - Satin Brass"),
    ("612",  "612 - Satin Bronze"),
    ("613",  "613 - Oil Rubbed Bronze"),
    ("619",  "619 - Satin Nickel"),
    ("622",  "622 - Flat Black"),
    ("625",  "625 - Bright Chrome"),
    ("626",  "626 - Satin Chrome"),
    ("630",  "630 - Satin Stainless Steel"),
    ("643e", "643e - Aged Bronze"),
]


def seed(conn):
    _seed_8800fl(conn)
    _seed_4700ln(conn)
    print("  Yale 8800FL + 4700LN seeded.")


# ═════════════════════════════════════════════════════════════════════
# 8800FL Series Mortise Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_8800fl(conn):
    f = fid(conn,
            "Yale",
            "8800FL Series Mortise Lock",
            "Mortise Lockset",
            "{function} {lever} {rose} {finish}",
            "Yale 8800FL {function} {lever} {rose} {finish}")

    slot(conn, f, 1, "function",      "Function",       1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose / Escutcheon", 1)
    slot(conn, f, 5, "finish",        "Finish",         1)
    slot(conn, f, 6, "handing",       "Handing",        0)
    slot(conn, f, 7, "thumbturn",     "Thumbturn",      0)

    functions = [
        ("8801FL", "8801FL - Passage"),
        ("8802FL", "8802FL - Privacy"),
        ("8805FL", "8805FL - Storeroom"),
        ("8806FL", "8806FL - Hospital Privacy"),
        ("8807FL", "8807FL - Classroom"),
        ("8808FL", "8808FL - Classroom Security"),
        ("8809FL", "8809FL - Entrance"),
        ("8810FL", "8810FL - Storeroom (Double Cyl.)"),
        ("8822FL", "8822FL - Institution"),
        ("8824FL", "8824FL - Dormitory"),
        ("8828FL", "8828FL - Exit"),
        ("8829FL", "8829FL - Faculty Restroom"),
        ("8831FL", "8831FL - Corridor (Deadbolt)"),
        ("8846FL", "8846FL - Entrance (Deadbolt)"),
        ("8847FL", "8847FL - Apartment / Vestibule"),
        ("8848FL", "8848FL - Office / Entry"),
        ("8860FL", "8860FL - Entrance / Corridor"),
        ("8862FL", "8862FL - Vandlgard Storeroom"),
    ]
    options(conn, f, "function", functions)

    cylinder_types = [
        ("6PIN",  "6-Pin Conventional"),
        ("PARA",  "Para Keyway"),
        ("LFIC",  "LFIC - Large Format IC"),
        ("SFIC",  "SFIC - Small Format IC"),
        ("LESS",  "Less Cylinder"),
        ("CONST", "Construction Core"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    non_keyed = {"8801FL", "8802FL", "8806FL", "8828FL"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    levers = [
        ("AU",  "AU - Augusta"),
        ("CR",  "CR - Carmel"),
        ("MA",  "MA - Monroe"),
        ("MO",  "MO - Monroe"),
        ("PB",  "PB - Pacific Beach"),
        ("SB",  "SB - Stanton"),
        ("TR",  "TR - Troy"),
        ("WS",  "WS - Windsor"),
    ]
    options(conn, f, "lever", levers)

    roses = [
        ("LC",  "LC - Escutcheon Plate"),
        ("RR",  "RR - Round Rose"),
        ("SR",  "SR - Square Rose"),
        ("SC",  "SC - Sectional Trim"),
        ("WR",  "WR - Wide Rose"),
    ]
    options(conn, f, "rose", roses)

    options(conn, f, "finish", YALE_FINISHES)

    handing = [("LH", "Left Hand"), ("RH", "Right Hand"),
               ("LHR", "Left Hand Reverse"), ("RHR", "Right Hand Reverse")]
    options(conn, f, "handing", handing)

    thumbturn_options = [("STD", "Standard Thumbturn")]
    options(conn, f, "thumbturn", thumbturn_options)
    tt_funcs = {"8802FL", "8809FL", "8824FL", "8829FL", "8831FL",
                "8846FL", "8847FL", "8848FL", "8860FL"}
    no_tt = [fn[0] for fn in functions if fn[0] not in tt_funcs]
    for func_val in no_tt:
        for tt in thumbturn_options:
            rule(conn, f, "conflict", "function", func_val, "thumbturn", tt[0],
                 "Thumbturn not applicable")


# ═════════════════════════════════════════════════════════════════════
# 4700LN Series Cylindrical Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_4700ln(conn):
    f = fid(conn,
            "Yale",
            "4700LN Series Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever}{rose} {finish}",
            "Yale 4700LN {function} {lever}{rose} {finish}")

    slot(conn, f, 1, "function",      "Function",       1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose",           1)
    slot(conn, f, 5, "finish",        "Finish",         1)

    functions = [
        ("4701LN", "4701LN - Passage"),
        ("4702LN", "4702LN - Privacy"),
        ("4705LN", "4705LN - Storeroom"),
        ("4706LN", "4706LN - Hospital Privacy"),
        ("4707LN", "4707LN - Classroom"),
        ("4708LN", "4708LN - Classroom Security"),
        ("4709LN", "4709LN - Entrance"),
        ("4722LN", "4722LN - Institutional"),
        ("4724LN", "4724LN - Dormitory"),
        ("4727LN", "4727LN - Vandlgard Storeroom"),
        ("4760LN", "4760LN - Privacy"),
    ]
    options(conn, f, "function", functions)

    cylinder_types = [
        ("6PIN",  "6-Pin Conventional"),
        ("PARA",  "Para Keyway"),
        ("LFIC",  "LFIC - Large Format IC"),
        ("SFIC",  "SFIC - Small Format IC"),
        ("LESS",  "Less Cylinder"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    non_keyed = {"4701LN", "4702LN", "4706LN", "4760LN"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    levers = [
        ("AU",  "AU - Augusta"),
        ("CR",  "CR - Carmel"),
        ("MA",  "MA - Monroe"),
        ("PB",  "PB - Pacific Beach"),
        ("SB",  "SB - Stanton"),
        ("TR",  "TR - Troy"),
        ("WS",  "WS - Windsor"),
    ]
    options(conn, f, "lever", levers)

    roses = [
        ("RR", "RR - Round Rose"),
        ("SR", "SR - Square Rose"),
        ("LC", "LC - Escutcheon Plate"),
        ("SC", "SC - Sectional Rose"),
    ]
    options(conn, f, "rose", roses)

    options(conn, f, "finish", YALE_FINISHES)
