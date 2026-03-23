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

VD_LEVERS = [
    ("06",  "06 - Knurled Lever"),
    ("17",  "17 - Standard Lever"),
    ("26",  "26 - Straight Lever"),
    ("15",  "15 - Contoured Lever"),
    ("03",  "03 - Knob"),
    ("BRN", "BRN - Breakaway Lever"),
    ("07",  "07 - Bent Lever"),
    ("13",  "13 - Heavy-Duty Lever"),
]

VD_SIZES = [
    ("3FT",   "3' (36\")"),
    ("3.5FT", "3'-6\" (42\")"),
    ("4FT",   "4' (48\")"),
    ("5FT",   "5' (60\")"),
    ("6FT",   "6' (72\")"),
]

VD_TRIM = [
    ("EO",     "EO - Exit Only (No Outside Trim)"),
    ("NL",     "NL - Night Latch Trim"),
    ("NL-OP",  "NL-OP - Night Latch Optional Pull"),
    ("L",      "L - Lever Trim"),
    ("L-BE",   "L-BE - Lever Trim w/ Blank Escutcheon"),
    ("TP",     "TP - Thumbpiece Trim"),
    ("996L",   "996L - Classroom Lever Trim"),
    ("996L-R", "996L-R - Classroom Lever w/ Indicator"),
    ("PT",     "PT - Pull Trim"),
    ("386",    "386 - Pull Handle Trim"),
    ("388",    "388 - Escutcheon Lever Trim"),
    ("389",    "389 - Escutcheon Lever Trim w/ Cylinder"),
]

VD_ELECTRIC = [
    ("NONE",     "Non-Electric"),
    ("EL",       "EL - Electric Latch Retraction (24VDC)"),
    ("EL-2",     "EL - Electric Latch Retraction (12VDC)"),
    ("QEL",      "QEL - Quiet Electric Latch Retraction (24VDC)"),
    ("QEL-2",    "QEL - Quiet Electric Latch Retraction (12VDC)"),
    ("RX",       "RX - Request to Exit Switch"),
    ("LX",       "LX - Latch Bolt Monitor Switch"),
    ("EL-RX",    "EL + RX - Elec Latch Retraction + Request to Exit"),
    ("QEL-RX",   "QEL + RX - Quiet ELR + Request to Exit"),
    ("EL-LX",    "EL + LX - Elec Latch Retraction + Latch Monitor"),
    ("QEL-LX",   "QEL + LX - Quiet ELR + Latch Monitor"),
]

VD_MONITORING = [
    ("NONE",    "None"),
    ("RX",      "RX - Request to Exit Switch"),
    ("LX",      "LX - Latch Bolt Monitor"),
    ("DPS",     "DPS - Door Position Switch"),
    ("RX-LX",   "RX + LX"),
    ("RX-DPS",  "RX + DPS"),
    ("LX-DPS",  "LX + DPS"),
    ("CX",      "CX - Continuous Monitoring"),
]


def seed(conn):
    _seed_98_99(conn)
    _seed_22(conn)
    print("  Von Duprin 98/99 + 22 seeded.")


# ═════════════════════════════════════════════════════════════════════
# 98/99 Series — Rim, SVR, CVR, Mortise Exit Devices
# ═════════════════════════════════════════════════════════════════════

def _seed_98_99(conn):
    f = fid(conn,
            "Von Duprin",
            "98/99 Series Exit Device",
            "Exit Device",
            "{device_model}-{trim_type} {finish}",
            "Von Duprin {device_model} {trim_type} {finish}")

    slot(conn, f, 1,  "device_model",   "Device Model",               1)
    slot(conn, f, 2,  "trim_type",      "Outside Trim",               1)
    slot(conn, f, 3,  "lever",          "Lever Design",               0)
    slot(conn, f, 4,  "finish",         "Finish",                     1)
    slot(conn, f, 5,  "size",           "Device Size",                1)
    slot(conn, f, 6,  "dogging",        "Dogging Option",             0)
    slot(conn, f, 7,  "electric",       "Electrified Option",         0)
    slot(conn, f, 8,  "monitoring",     "Monitoring / Switches",      0)
    slot(conn, f, 9,  "special",        "Special Options (PA/AX)",    0)
    slot(conn, f, 10, "thumbturn",      "Inside Thumbturn",           0)

    # ── Device Models (actual Von Duprin model numbers) ──
    device_models = [
        # 98 platform (Rim)
        ("98",       "98 - Rim Exit Device"),
        ("98-2",     "98-2 - Rim Exit Device (Fire Rated)"),
        ("9875",     "9875 - Mortise Lock Exit Device"),
        ("9875-2",   "9875-2 - Mortise Lock Exit (Fire Rated)"),
        ("9848",     "9848 - Concealed Vertical Rod"),
        ("9848-2",   "9848-2 - Concealed Vertical Rod (Fire Rated)"),
        ("9852",     "9852 - Surface Vertical Rod (Wide Stile)"),
        ("9852-2",   "9852-2 - Surface Vertical Rod, Wide Stile (Fire Rated)"),
        # 99 platform (Surface Vertical Rod)
        ("99",       "99 - Surface Vertical Rod"),
        ("99-2",     "99-2 - Surface Vertical Rod (Fire Rated)"),
        ("9927",     "9927 - Surface Bolt Exit Device"),
        ("9927-2",   "9927-2 - Surface Bolt Exit (Fire Rated)"),
        ("9947",     "9947 - Concealed Vertical Rod"),
        ("9947-2",   "9947-2 - Concealed Vertical Rod (Fire Rated)"),
        ("9950",     "9950 - Surface Vertical Rod (Top Rod Only)"),
        ("9950-2",   "9950-2 - Surface Vertical Rod, Top Rod Only (Fire Rated)"),
        ("9975",     "9975 - Mortise Lock Exit Device"),
        ("9975-2",   "9975-2 - Mortise Lock Exit (Fire Rated)"),
    ]
    options(conn, f, "device_model", device_models)

    options(conn, f, "trim_type", VD_TRIM)
    options(conn, f, "lever", VD_LEVERS)

    # Lever only visible when trim_type has a lever
    lever_trims = {"L", "L-BE", "996L", "996L-R", "388", "389"}
    no_lever_trims = [t[0] for t in VD_TRIM if t[0] not in lever_trims]
    for tv in no_lever_trims:
        for lv in VD_LEVERS:
            rule(conn, f, "conflict", "trim_type", tv, "lever", lv[0],
                 "Lever not applicable for this trim type")

    options(conn, f, "finish", VD_FINISHES)
    options(conn, f, "size", VD_SIZES)

    # ── Dogging ──
    dogging = [
        ("STD",  "Standard Dogging (Hex Key)"),
        ("CD",   "CD - Cylinder Dogging"),
        ("LD",   "LD - Less Dogging (No Dogging)"),
        ("SD",   "SD - Special Dogging"),
    ]
    options(conn, f, "dogging", dogging)

    # Fire-rated devices must be LD (less dogging)
    fire_models = [m[0] for m in device_models if "-2" in m[0]]
    for fm in fire_models:
        restrict(conn, f, "device_model", fm, "dogging", ["LD"],
                 "Fire-rated devices require LD (Less Dogging)")

    options(conn, f, "electric", VD_ELECTRIC)
    options(conn, f, "monitoring", VD_MONITORING)

    # ── Special Options (PA, AX, etc.) ──
    special_opts = [
        ("NONE",    "None"),
        ("PA",      "PA - Power Assist (ADA Reduced Force)"),
        ("AX",      "AX - Auxiliary Control (Fire Pin)"),
        ("PA-AX",   "PA + AX - Power Assist + Auxiliary Control"),
        ("FS",      "FS - Fire Pin Strike"),
        ("WS",      "WS - Weather Seal"),
        ("SS",      "SS - Security Screws"),
        ("HC",      "HC - Hospital Coating (Antimicrobial)"),
    ]
    options(conn, f, "special", special_opts)

    # ── Inside Thumbturn ──
    thumbturn = [
        ("NONE",  "None (Standard)"),
        ("TL",    "TL - Inside Thumbturn Lever"),
        ("AT",    "AT - Anti-Tamper Thumbturn"),
    ]
    options(conn, f, "thumbturn", thumbturn)


# ═════════════════════════════════════════════════════════════════════
# 22 Series — Concealed Vertical Rod Exit Device
# ═════════════════════════════════════════════════════════════════════

def _seed_22(conn):
    f = fid(conn,
            "Von Duprin",
            "22 Series Concealed Vertical Rod",
            "Exit Device",
            "{device_model}-{trim_type} {finish}",
            "Von Duprin {device_model} {trim_type} {finish}")

    slot(conn, f, 1,  "device_model",  "Device Model",               1)
    slot(conn, f, 2,  "trim_type",     "Outside Trim",               1)
    slot(conn, f, 3,  "lever",         "Lever Design",               0)
    slot(conn, f, 4,  "finish",        "Finish",                     1)
    slot(conn, f, 5,  "size",          "Device Size",                1)
    slot(conn, f, 6,  "dogging",       "Dogging Option",             0)
    slot(conn, f, 7,  "electric",      "Electrified Option",         0)
    slot(conn, f, 8,  "monitoring",    "Monitoring / Switches",      0)
    slot(conn, f, 9,  "special",       "Special Options (PA/AX)",    0)

    device_models_22 = [
        ("2227",     "2227 - Concealed Vertical Rod"),
        ("2227-2",   "2227-2 - Concealed Vertical Rod (Fire Rated)"),
        ("2227-6",   "2227-6 - Concealed Vertical Rod (Wood Door)"),
        ("2270",     "2270 - Concealed Vertical Rod (Wide Stile)"),
        ("2270-2",   "2270-2 - Concealed Vert Rod, Wide Stile (Fire Rated)"),
    ]
    options(conn, f, "device_model", device_models_22)

    options(conn, f, "trim_type", VD_TRIM)
    options(conn, f, "lever", VD_LEVERS)

    lever_trims = {"L", "L-BE", "996L", "996L-R", "388", "389"}
    no_lever_trims = [t[0] for t in VD_TRIM if t[0] not in lever_trims]
    for tv in no_lever_trims:
        for lv in VD_LEVERS:
            rule(conn, f, "conflict", "trim_type", tv, "lever", lv[0],
                 "Lever not applicable for this trim type")

    options(conn, f, "finish", VD_FINISHES)
    options(conn, f, "size", VD_SIZES)

    dogging_22 = [
        ("STD",  "Standard Dogging (Hex Key)"),
        ("CD",   "CD - Cylinder Dogging"),
        ("LD",   "LD - Less Dogging (No Dogging)"),
    ]
    options(conn, f, "dogging", dogging_22)

    fire_models_22 = [m[0] for m in device_models_22 if "-2" in m[0]]
    for fm in fire_models_22:
        restrict(conn, f, "device_model", fm, "dogging", ["LD"],
                 "Fire-rated devices require LD (Less Dogging)")

    options(conn, f, "electric", VD_ELECTRIC)
    options(conn, f, "monitoring", VD_MONITORING)

    special_22 = [
        ("NONE",    "None"),
        ("PA",      "PA - Power Assist (ADA Reduced Force)"),
        ("AX",      "AX - Auxiliary Control (Fire Pin)"),
        ("PA-AX",   "PA + AX - Power Assist + Auxiliary Control"),
        ("FS",      "FS - Fire Pin Strike"),
        ("WS",      "WS - Weather Seal"),
        ("SS",      "SS - Security Screws"),
    ]
    options(conn, f, "special", special_22)
