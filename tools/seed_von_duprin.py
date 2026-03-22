"""Seed Von Duprin exit device data — 98/99 Series and 22 Series."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


VD_FINISHES = [
    ("US3",   "US3 - Bright Brass"),
    ("US4",   "US4 - Satin Brass"),
    ("US10",  "US10 - Satin Bronze"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US26",  "US26 - Bright Chrome"),
    ("US26D", "US26D - Satin Chrome"),
    ("US28",  "US28 - Satin Aluminum"),
    ("US32",  "US32 - Bright Stainless"),
    ("US32D", "US32D - Satin Stainless Steel"),
    ("SP28",  "SP28 - Sprayed Aluminum"),
    ("SP313", "SP313 - Sprayed Dark Bronze"),
]


def seed(conn):
    _seed_98_99(conn)
    _seed_22(conn)
    print("  Von Duprin 98/99 + 22 seeded.")


# ═════════════════════════════════════════════════════════════════════
# 98/99 Series — Rim & Vertical Rod Exit Devices
# ═════════════════════════════════════════════════════════════════════

def _seed_98_99(conn):
    f = fid(conn,
            "Von Duprin",
            "98/99 Series Exit Device",
            "Exit Device",
            "{device_type}-{trim_type} {finish}",
            "Von Duprin {device_type} {trim_type} {finish}")

    slot(conn, f, 1, "device_type", "Device Type",       1)
    slot(conn, f, 2, "trim_type",   "Outside Trim",      1)
    slot(conn, f, 3, "lever",       "Lever Design",      0)
    slot(conn, f, 4, "finish",      "Finish",            1)
    slot(conn, f, 5, "size",        "Device Size",       1)
    slot(conn, f, 6, "voltage",     "Electrified Option", 0)
    slot(conn, f, 7, "monitoring",  "Monitoring / Alarm", 0)

    device_types = [
        ("98",   "98 - Rim Exit Device"),
        ("99",   "99 - Surface Vertical Rod"),
        ("98-2", "98-2 - Rim Exit (Fire Rated)"),
        ("99-2", "99-2 - Surface Vertical Rod (Fire Rated)"),
        ("98NL", "98NL - Rim w/ Night Latch"),
        ("99NL", "99NL - Surface Vert Rod w/ Night Latch"),
        ("98EO", "98EO - Rim Exit Only (No Trim)"),
        ("99EO", "99EO - Surface Vert Rod Exit Only (No Trim)"),
    ]
    options(conn, f, "device_type", device_types)

    trim_types = [
        ("EO",     "EO - Exit Only (No Outside Trim)"),
        ("NL",     "NL - Night Latch Trim"),
        ("NL-OP",  "NL-OP - Night Latch Optional Pull"),
        ("L",      "L - Lever Trim"),
        ("L-BE",   "L-BE - Lever Trim w/ Blank Escutcheon"),
        ("TP",     "TP - Thumbpiece Trim"),
        ("996L",   "996L - Lever Trim for Classroom"),
        ("996L-R", "996L-R - Lever Trim Classroom w/ Indicator"),
    ]
    options(conn, f, "trim_type", trim_types)

    # Lever designs (shown only when trim has a lever)
    levers = [
        ("06",  "06 - Knurled"),
        ("17",  "17 - Lever Design"),
        ("26",  "26 - Lever Design"),
        ("BRN", "BRN - Breakaway"),
    ]
    options(conn, f, "lever", levers)

    # Lever only visible when trim_type is L/L-BE/996L/996L-R
    lever_trims = {"L", "L-BE", "996L", "996L-R"}
    no_lever_trims = [t[0] for t in trim_types if t[0] not in lever_trims]
    for tv in no_lever_trims:
        for lv in levers:
            rule(conn, f, "conflict", "trim_type", tv, "lever", lv[0],
                 "Lever not applicable for this trim type")

    options(conn, f, "finish", VD_FINISHES)

    sizes = [
        ("3FT",  "3' (36\")"),
        ("4FT",  "4' (48\")"),
    ]
    options(conn, f, "size", sizes)

    voltage_options = [
        ("NONE",     "Non-Electric"),
        ("EL",       "EL - Electric Latch Retraction"),
        ("QEL",      "QEL - Quiet Electric Latch Retraction"),
        ("RX",       "RX - Request to Exit"),
        ("LX",       "LX - Latch Monitor"),
        ("RX-LX",    "RX/LX - Request to Exit + Latch Monitor"),
        ("EL-RX",    "EL/RX - Elec Latch Retraction + RX"),
        ("QEL-RX",   "QEL/RX - Quiet ELR + RX"),
    ]
    options(conn, f, "voltage", voltage_options)

    monitoring_options = [
        ("NONE",  "None"),
        ("RX",    "RX - Request to Exit Switch"),
        ("LX",    "LX - Latch Bolt Monitor"),
        ("DPS",   "DPS - Door Position Switch"),
        ("RX-LX", "RX + LX"),
    ]
    options(conn, f, "monitoring", monitoring_options)


# ═════════════════════════════════════════════════════════════════════
# 22 Series — Concealed Vertical Rod Exit Device
# ═════════════════════════════════════════════════════════════════════

def _seed_22(conn):
    f = fid(conn,
            "Von Duprin",
            "22 Series Concealed Vertical Rod",
            "Exit Device",
            "{device_type}-{trim_type} {finish}",
            "Von Duprin {device_type} {trim_type} {finish}")

    slot(conn, f, 1, "device_type", "Device Type",       1)
    slot(conn, f, 2, "trim_type",   "Outside Trim",      1)
    slot(conn, f, 3, "lever",       "Lever Design",      0)
    slot(conn, f, 4, "finish",      "Finish",            1)
    slot(conn, f, 5, "size",        "Device Size",       1)
    slot(conn, f, 6, "voltage",     "Electrified Option", 0)

    device_types = [
        ("2227",   "2227 - Concealed Vertical Rod"),
        ("2227-2", "2227-2 - Concealed Vert Rod (Fire Rated)"),
        ("2227EO", "2227EO - Concealed Vert Rod Exit Only"),
    ]
    options(conn, f, "device_type", device_types)

    trim_types = [
        ("EO",    "EO - Exit Only"),
        ("NL",    "NL - Night Latch"),
        ("L",     "L - Lever Trim"),
        ("L-BE",  "L-BE - Lever Trim w/ Blank Escutcheon"),
        ("TP",    "TP - Thumbpiece"),
        ("996L",  "996L - Classroom Lever Trim"),
    ]
    options(conn, f, "trim_type", trim_types)

    levers = [
        ("06",  "06 - Knurled"),
        ("17",  "17 - Lever Design"),
        ("26",  "26 - Lever Design"),
    ]
    options(conn, f, "lever", levers)

    lever_trims = {"L", "L-BE", "996L"}
    no_lever_trims = [t[0] for t in trim_types if t[0] not in lever_trims]
    for tv in no_lever_trims:
        for lv in levers:
            rule(conn, f, "conflict", "trim_type", tv, "lever", lv[0],
                 "Lever not applicable for this trim type")

    options(conn, f, "finish", VD_FINISHES)

    sizes = [
        ("3FT",  "3' (36\")"),
        ("4FT",  "4' (48\")"),
    ]
    options(conn, f, "size", sizes)

    voltage_options = [
        ("NONE",   "Non-Electric"),
        ("EL",     "EL - Electric Latch Retraction"),
        ("QEL",    "QEL - Quiet Electric Latch Retraction"),
        ("RX",     "RX - Request to Exit"),
        ("LX",     "LX - Latch Monitor"),
    ]
    options(conn, f, "voltage", voltage_options)
