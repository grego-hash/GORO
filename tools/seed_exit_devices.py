"""Seed Sargent 80 Series and Corbin Russwin ED5000 Series exit device data."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


SAR_EXIT_FINISHES = [
    ("US3",   "US3 - Bright Brass"),
    ("US4",   "US4 - Satin Brass"),
    ("US10",  "US10 - Satin Bronze"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US26",  "US26 - Bright Chrome"),
    ("US26D", "US26D - Satin Chrome"),
    ("US28",  "US28 - Satin Aluminum"),
    ("US32D", "US32D - Satin Stainless Steel"),
    ("BSP",   "BSP - Black Suede Powder Coat"),
]

CR_EXIT_FINISHES = [
    ("605",   "605 - Bright Brass"),
    ("606",   "606 - Satin Brass"),
    ("612",   "612 - Satin Bronze"),
    ("613",   "613 - Oil Rubbed Bronze"),
    ("625",   "625 - Bright Chrome"),
    ("626",   "626 - Satin Chrome"),
    ("628",   "628 - Satin Aluminum"),
    ("630",   "630 - Satin Stainless Steel"),
]


def seed(conn):
    _seed_sargent_80(conn)
    _seed_ed5000(conn)
    print("  Sargent 80 + Corbin Russwin ED5000 seeded.")


# ═════════════════════════════════════════════════════════════════════
# Sargent 80 Series Exit Devices
# ═════════════════════════════════════════════════════════════════════

def _seed_sargent_80(conn):
    f = fid(conn,
            "Sargent",
            "80 Series Exit Device",
            "Exit Device",
            "{device_type}-{trim_type} {finish}",
            "Sargent 80 {device_type} {trim_type} {finish}")

    slot(conn, f, 1, "device_type", "Device Type",        1)
    slot(conn, f, 2, "trim_type",   "Outside Trim",       1)
    slot(conn, f, 3, "lever",       "Lever Design",       0)
    slot(conn, f, 4, "finish",      "Finish",             1)
    slot(conn, f, 5, "size",        "Device Size",        1)
    slot(conn, f, 6, "voltage",     "Electrified Option",  0)

    device_types = [
        ("8804",   "8804 - Rim Exit (Storeroom)"),
        ("8810",   "8810 - Rim Exit (Passage)"),
        ("8813",   "8813 - Rim Exit (Classroom)"),
        ("8815",   "8815 - Rim Exit (Night Latch)"),
        ("8888",   "8888 - Rim Exit (Exit Only)"),
        ("8904",   "8904 - Mortise Lock Exit (Storeroom)"),
        ("8910",   "8910 - Mortise Lock Exit (Passage)"),
        ("8913",   "8913 - Mortise Lock Exit (Classroom)"),
        ("12-8804","12-8804 - Surface Vert Rod (Storeroom)"),
        ("12-8810","12-8810 - Surface Vert Rod (Passage)"),
        ("12-8813","12-8813 - Surface Vert Rod (Classroom)"),
        ("12-8888","12-8888 - Surface Vert Rod (Exit Only)"),
    ]
    options(conn, f, "device_type", device_types)

    trim_types = [
        ("EO",  "EO - Exit Only"),
        ("NL",  "NL - Night Latch"),
        ("ET",  "ET - Escutcheon Trim (Lever)"),
        ("PT",  "PT - Pull Trim"),
        ("996", "996 - Classroom Lever Trim"),
    ]
    options(conn, f, "trim_type", trim_types)

    levers = [
        ("LA", "LA - L-Design Standard"),
        ("LB", "LB - B-Design"),
        ("LE", "LE - E-Design"),
        ("LJ", "LJ - J-Design"),
        ("LN", "LN - N-Design"),
        ("LW", "LW - W-Design"),
    ]
    options(conn, f, "lever", levers)

    lever_trims = {"ET", "996"}
    no_lever_trims = [t[0] for t in trim_types if t[0] not in lever_trims]
    for tv in no_lever_trims:
        for lv in levers:
            rule(conn, f, "conflict", "trim_type", tv, "lever", lv[0],
                 "Lever not applicable for this trim type")

    options(conn, f, "finish", SAR_EXIT_FINISHES)

    sizes = [
        ("3FT",  "3' (36\")"),
        ("4FT",  "4' (48\")"),
        ("5FT",  "5' (60\")"),
        ("6FT",  "6' (72\")"),
    ]
    options(conn, f, "size", sizes)

    voltage_options = [
        ("NONE", "Non-Electric"),
        ("EL",   "EL - Electric Latch Retraction"),
        ("RX",   "RX - Request to Exit"),
        ("LX",   "LX - Latch Monitor"),
    ]
    options(conn, f, "voltage", voltage_options)


# ═════════════════════════════════════════════════════════════════════
# Corbin Russwin ED5000 Series Exit Devices
# ═════════════════════════════════════════════════════════════════════

def _seed_ed5000(conn):
    f = fid(conn,
            "Corbin Russwin",
            "ED5000 Series Exit Device",
            "Exit Device",
            "ED{device_type}-{trim_type} {finish}",
            "Corbin Russwin ED5000 {device_type} {trim_type} {finish}")

    slot(conn, f, 1, "device_type", "Device Type",        1)
    slot(conn, f, 2, "trim_type",   "Outside Trim",       1)
    slot(conn, f, 3, "lever",       "Lever Design",       0)
    slot(conn, f, 4, "finish",      "Finish",             1)
    slot(conn, f, 5, "size",        "Device Size",        1)
    slot(conn, f, 6, "voltage",     "Electrified Option",  0)

    device_types = [
        ("ED5200",   "ED5200 - Rim Exit"),
        ("ED5200A",  "ED5200A - Rim Exit (Fire Rated)"),
        ("ED5400",   "ED5400 - Surface Vertical Rod"),
        ("ED5400A",  "ED5400A - Surface Vert Rod (Fire Rated)"),
        ("ED5600",   "ED5600 - Mortise Lock Exit"),
        ("ED5600A",  "ED5600A - Mortise Lock Exit (Fire Rated)"),
        ("ED5800",   "ED5800 - Concealed Vertical Rod"),
        ("ED5800A",  "ED5800A - Concealed Vert Rod (Fire Rated)"),
    ]
    options(conn, f, "device_type", device_types)

    trim_types = [
        ("EO",  "EO - Exit Only"),
        ("NL",  "NL - Night Latch"),
        ("L",   "L - Lever Trim"),
        ("PT",  "PT - Pull Trim"),
        ("CL",  "CL - Classroom Lever Trim"),
    ]
    options(conn, f, "trim_type", trim_types)

    levers = [
        ("NAC", "NAC - Newport"),
        ("SAC", "SAC - Sargent"),
        ("LWM", "LWM - Lustra"),
        ("DSM", "DSM - Dirke"),
        ("GRC", "GRC - Grier"),
        ("MZD", "MZD - Montrose"),
        ("RGC", "RGC - Regis"),
    ]
    options(conn, f, "lever", levers)

    lever_trims = {"L", "CL"}
    no_lever_trims = [t[0] for t in trim_types if t[0] not in lever_trims]
    for tv in no_lever_trims:
        for lv in levers:
            rule(conn, f, "conflict", "trim_type", tv, "lever", lv[0],
                 "Lever not applicable for this trim type")

    options(conn, f, "finish", CR_EXIT_FINISHES)

    sizes = [
        ("3FT",  "3' (36\")"),
        ("4FT",  "4' (48\")"),
        ("5FT",  "5' (60\")"),
        ("6FT",  "6' (72\")"),
    ]
    options(conn, f, "size", sizes)

    voltage_options = [
        ("NONE", "Non-Electric"),
        ("EL",   "EL - Electric Latch Retraction"),
        ("QEL",  "QEL - Quiet Electric Latch Retraction"),
        ("RX",   "RX - Request to Exit"),
        ("LX",   "LX - Latch Monitor"),
    ]
    options(conn, f, "voltage", voltage_options)
