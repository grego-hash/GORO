"""Seed Sargent 8200 Series Mortise Lock, 10-Line Cylindrical Lock,
and 281 Series Door Closer data."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


SAR_FINISHES = [
    ("3",   "3 - Bright Brass"),
    ("4",   "4 - Satin Brass"),
    ("10",  "10 - Satin Bronze"),
    ("10B", "10B - Oil Rubbed Bronze"),
    ("10BE","10BE - Oil Rubbed Bronze, Antimicrobial"),
    ("26",  "26 - Bright Chrome"),
    ("26D", "26D - Satin Chrome"),
    ("32",  "32 - Bright Stainless"),
    ("32D", "32D - Satin Stainless Steel"),
    ("BSP", "BSP - Black Suede Powder Coat"),
]


def seed(conn):
    _seed_8200(conn)
    _seed_10_line(conn)
    print("  Sargent 8200 + 10-Line seeded.")


# ═════════════════════════════════════════════════════════════════════
# 8200 Series Mortise Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_8200(conn):
    f = fid(conn,
            "Sargent",
            "8200 Series Mortise Lock",
            "Mortise Lockset",
            "{function} {lever}{escutcheon} {finish}",
            "Sargent 8200 {function} {lever}{escutcheon} {finish}")

    slot(conn, f, 1, "function",      "Function",       1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "escutcheon",    "Escutcheon",     1)
    slot(conn, f, 5, "finish",        "Finish",         1)
    slot(conn, f, 6, "handing",       "Handing",        0)
    slot(conn, f, 7, "thumbturn",     "Thumbturn",      0)
    slot(conn, f, 8, "voltage",       "Electrified Voltage", 0)

    functions = [
        ("8204",  "8204 - Storeroom"),
        ("8205",  "8205 - Office / Entry"),
        ("8213",  "8213 - Classroom"),
        ("8215",  "8215 - Apartment / Passage"),
        ("8217",  "8217 - Institutional"),
        ("8224",  "8224 - Storeroom (Deadbolt)"),
        ("8225",  "8225 - Dormitory / Exit"),
        ("8237",  "8237 - Classroom Security"),
        ("8243",  "8243 - Vestibule"),
        ("8245",  "8245 - Dormitory / Bedroom"),
        ("8246",  "8246 - Privacy / Bath"),
        ("8255",  "8255 - Faculty Restroom"),
        ("8265",  "8265 - Entrance / Corridor"),
        ("8266",  "8266 - Passage"),
        ("8270",  "8270 - Entrance w/ Deadbolt"),
        ("8271",  "8271 - Corridor (Deadbolt + Indicator)"),
        # Electrified
        ("8204 LNL", "8204 LNL - Electrified Storeroom"),
        ("8205 LNL", "8205 LNL - Electrified Office / Entry"),
        ("8213 LNL", "8213 LNL - Electrified Classroom"),
        ("8270 LNL", "8270 LNL - Electrified Entrance"),
        ("8271 LNL", "8271 LNL - Electrified Corridor"),
    ]
    options(conn, f, "function", functions)

    cylinder_types = [
        ("6PIN",  "6-Pin Conventional"),
        ("LFIC",  "LFIC - Large Format IC"),
        ("SFIC",  "SFIC - Small Format IC"),
        ("RIM",   "Rim Cylinder"),
        ("LESS",  "Less Cylinder"),
        ("CONST", "Construction Core"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    non_keyed = {"8215", "8246", "8266"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    levers = [
        ("LA",  "LA - L-Design Standard"),
        ("LB",  "LB - B-Design"),
        ("LE",  "LE - E-Design"),
        ("LF",  "LF - F-Design"),
        ("LG",  "LG - G-Design"),
        ("LJ",  "LJ - J-Design"),
        ("LL",  "LL - L-Design"),
        ("LN",  "LN - N-Design"),
        ("LP",  "LP - P-Design"),
        ("LW",  "LW - W-Design"),
        ("LNL", "LNL - NL-Design (Ligature Resistant)"),
    ]
    options(conn, f, "lever", levers)

    escutcheons = [
        ("T",  "T - T-Escutcheon (Full)"),
        ("N",  "N - N-Escutcheon (Sectional)"),
        ("P",  "P - P-Escutcheon (Full)"),
        ("LE", "LE - LE-Escutcheon"),
    ]
    options(conn, f, "escutcheon", escutcheons)

    options(conn, f, "finish", SAR_FINISHES)

    handing = [("LH", "LH - Left Hand"), ("RH", "RH - Right Hand"),
               ("LHR", "LHR - Left Hand Reverse"), ("RHR", "RHR - Right Hand Reverse")]
    options(conn, f, "handing", handing)

    thumbturn_options = [("STD", "Standard Thumbturn")]
    options(conn, f, "thumbturn", thumbturn_options)
    tt_funcs = {"8246", "8205", "8225", "8245", "8265", "8270", "8271",
                "8205 LNL", "8270 LNL", "8271 LNL"}
    no_tt = [fn[0] for fn in functions if fn[0] not in tt_funcs]
    for func_val in no_tt:
        for tt in thumbturn_options:
            rule(conn, f, "conflict", "function", func_val, "thumbturn", tt[0],
                 "Thumbturn not applicable")

    # Voltage for electrified functions
    voltage_options = [
        ("12VDC",    "12VDC"),
        ("24VDC",    "24VDC"),
        ("12_24VDC", "12/24VDC Auto-Detect"),
    ]
    options(conn, f, "voltage", voltage_options)
    elec_funcs = {"8204 LNL", "8205 LNL", "8213 LNL", "8270 LNL", "8271 LNL"}
    mech_funcs = [fn[0] for fn in functions if fn[0] not in elec_funcs]
    for func_val in mech_funcs:
        for v in voltage_options:
            rule(conn, f, "conflict", "function", func_val, "voltage", v[0],
                 "Voltage not applicable for mechanical function")


# ═════════════════════════════════════════════════════════════════════
# 10-Line Cylindrical Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_10_line(conn):
    f = fid(conn,
            "Sargent",
            "10-Line Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever}{rose} {finish}",
            "Sargent 10-Line {function} {lever}{rose} {finish}")

    slot(conn, f, 1, "function",      "Function",       1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose",           1)
    slot(conn, f, 5, "finish",        "Finish",         1)

    functions = [
        ("10G04",  "10G04 - Storeroom"),
        ("10G05",  "10G05 - Entry / Office"),
        ("10G13",  "10G13 - Classroom"),
        ("10G15",  "10G15 - Passage / Closet"),
        ("10G16",  "10G16 - Passage"),
        ("10G17",  "10G17 - Institutional"),
        ("10G24",  "10G24 - Storeroom (Deadbolt)"),
        ("10G37",  "10G37 - Classroom Security"),
        ("10G38",  "10G38 - Classroom Security (Indicator)"),
        ("10G46",  "10G46 - Privacy / Bath"),
        ("10G54",  "10G54 - Corridor"),
        ("10G65",  "10G65 - Entrance / Corridor"),
        ("10G70",  "10G70 - Entrance w/ Deadbolt"),
    ]
    options(conn, f, "function", functions)

    cylinder_types = [
        ("6PIN",  "6-Pin Conventional"),
        ("LFIC",  "LFIC - Large Format IC"),
        ("SFIC",  "SFIC - Small Format IC"),
        ("LESS",  "Less Cylinder"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    non_keyed = {"10G15", "10G16", "10G46"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    levers = [
        ("LA",  "LA - L-Design Standard"),
        ("LB",  "LB - B-Design"),
        ("LE",  "LE - E-Design"),
        ("LG",  "LG - G-Design"),
        ("LJ",  "LJ - J-Design"),
        ("LL",  "LL - L-Design"),
        ("LN",  "LN - N-Design"),
        ("LP",  "LP - P-Design"),
        ("LW",  "LW - W-Design"),
    ]
    options(conn, f, "lever", levers)

    roses = [
        ("RN", "RN - Standard Rose"),
    ]
    options(conn, f, "rose", roses)

    options(conn, f, "finish", SAR_FINISHES)
