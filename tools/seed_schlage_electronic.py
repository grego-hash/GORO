"""Seed Schlage electronic access locks — CO-Series, NDE/NDE80, Control."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_co_series(conn)
    _seed_nde(conn)
    _seed_control(conn)
    print("  Schlage CO-Series + NDE + Control seeded.")


# ═════════════════════════════════════════════════════════════════════
# Schlage CO-100 / CO-200 Series
# ═════════════════════════════════════════════════════════════════════

def _seed_co_series(conn):
    f = fid(conn, "Schlage", "CO-100 Standalone Electronic Lock",
            "Electronic Lock",
            "CO-100-{chassis}-{reader} {lever} {finish}",
            "Schlage CO-100 {chassis} {reader} {lever} {finish}")

    slot(conn, f, 1, "chassis",  "Lock Chassis",       1)
    slot(conn, f, 2, "reader",   "Reader Module",      1)
    slot(conn, f, 3, "function", "Function",           1)
    slot(conn, f, 4, "lever",    "Lever Design",       1)
    slot(conn, f, 5, "finish",   "Finish",             1)
    slot(conn, f, 6, "keyway",   "Keyway",             0)

    chassis = [
        ("CY",  "CY - Cylindrical (Bored)"),
        ("MS",  "MS - Mortise"),
    ]
    options(conn, f, "chassis", chassis)

    readers = [
        ("KP",  "KP - Keypad Only"),
        ("MG",  "MG - Magnetic Stripe"),
        ("PR",  "PR - Proximity (HID)"),
        ("SK",  "SK - Smart Card"),
        ("RX",  "RX - Multi-Technology"),
    ]
    options(conn, f, "reader", readers)

    functions = [
        ("993R",  "993R - Entry, Classroom / Storeroom"),
        ("993S",  "993S - Entry, Storeroom"),
        ("993M",  "993M - Entry, Privacy"),
        ("993L",  "993L - Entry, Classroom"),
        ("993BD", "993BD - Entry, Classroom w/ Deadbolt"),
    ]
    options(conn, f, "function", functions)

    levers = [
        ("SPK",   "SPK - Sparta Knob"),
        ("ATH",   "ATH - Athens Lever"),
        ("RHO",   "RHO - Rhodes Lever"),
        ("LAT",   "LAT - Latitude Lever"),
        ("BRW",   "BRW - Broadway Lever"),
        ("NEP",   "NEP - Neptune Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("626", "626 - Satin Chrome"),
        ("643E","643E - Aged Bronze"),
        ("605", "605 - Bright Brass"),
        ("612", "612 - Satin Bronze"),
        ("619", "619 - Satin Nickel"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "keyway", [
        ("C",    "C - Schlage C Keyway"),
        ("CE",   "CE - Schlage CE Keyway"),
        ("FSIC", "FSIC - Full Size IC"),
        ("SFIC", "SFIC - Small Format IC"),
    ])

    # ── CO-200 (Networked) ──
    f2 = fid(conn, "Schlage", "CO-200 Networked Electronic Lock",
             "Electronic Lock",
             "CO-200-{chassis}-{reader} {lever} {finish}",
             "Schlage CO-200 {chassis} {reader} {lever} {finish}")

    slot(conn, f2, 1, "chassis",  "Lock Chassis",   1)
    slot(conn, f2, 2, "reader",   "Reader Module",  1)
    slot(conn, f2, 3, "function", "Function",       1)
    slot(conn, f2, 4, "lever",    "Lever Design",   1)
    slot(conn, f2, 5, "finish",   "Finish",         1)
    slot(conn, f2, 6, "network",  "Network Type",   1)

    options(conn, f2, "chassis", chassis)
    options(conn, f2, "reader", readers)
    options(conn, f2, "function", functions)
    options(conn, f2, "lever", levers)
    options(conn, f2, "finish", finishes)

    options(conn, f2, "network", [
        ("RS485", "RS-485 Hardwired"),
        ("PIR",   "PIR - Panel Interface (Wiegand)"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Schlage NDE / NDE80 Wireless
# ═════════════════════════════════════════════════════════════════════

def _seed_nde(conn):
    f = fid(conn, "Schlage", "NDE Wireless Electronic Lock",
            "Electronic Lock",
            "NDE-{reader} {function} {lever} {finish}",
            "Schlage NDE {reader} {function} {lever} {finish}")

    slot(conn, f, 1, "reader",   "Reader Type",     1)
    slot(conn, f, 2, "function", "Function",        1)
    slot(conn, f, 3, "lever",    "Lever Design",    1)
    slot(conn, f, 4, "finish",   "Finish",          1)
    slot(conn, f, 5, "keyway",   "Keyway",          0)

    readers = [
        ("MG",  "MG - Magnetic Stripe"),
        ("PR",  "PR - Proximity (HID)"),
        ("RX",  "RX - Multi-Technology"),
        ("SK",  "SK - Smart Card"),
        ("MT",  "MT - Multi-Tech (SEOS + BLE)"),
    ]
    options(conn, f, "reader", readers)

    functions = [
        ("RHO",    "Storeroom"),
        ("CLA",    "Classroom"),
        ("OFF",    "Office"),
        ("PRIV",   "Privacy"),
    ]
    options(conn, f, "function", functions)

    levers = [
        ("ATH", "ATH - Athens"),
        ("RHO", "RHO - Rhodes"),
        ("LAT", "LAT - Latitude"),
        ("BRW", "BRW - Broadway"),
        ("NEP", "NEP - Neptune"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("626", "626 - Satin Chrome"),
        ("643E","643E - Aged Bronze"),
        ("619", "619 - Satin Nickel"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "keyway", [
        ("C",    "C - Schlage C Keyway"),
        ("CE",   "CE - Schlage CE Keyway"),
        ("FSIC", "FSIC - Full Size IC"),
        ("SFIC", "SFIC - Small Format IC"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Schlage Control Smart Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_control(conn):
    f = fid(conn, "Schlage", "Control Smart Deadbolt / Lever",
            "Electronic Lock",
            "BE467/FE410 {style} {finish}",
            "Schlage Control {style} {finish}")

    slot(conn, f, 1, "model",   "Model Type",    1)
    slot(conn, f, 2, "style",   "Style",         1)
    slot(conn, f, 3, "finish",  "Finish",        1)

    options(conn, f, "model", [
        ("BE467", "BE467 - Deadbolt"),
        ("FE410", "FE410 - Lever"),
    ])

    options(conn, f, "style", [
        ("CEN", "CEN - Century Trim"),
        ("LAT", "LAT - Latitude Lever"),
        ("BRW", "BRW - Broadway Lever"),
    ])

    options(conn, f, "finish", [
        ("626", "626 - Satin Chrome"),
        ("619", "619 - Satin Nickel"),
        ("643E","643E - Aged Bronze"),
    ])

    # Deadbolt only gets trim style, not lever
    restrict(conn, f, "model", "BE467", "style", ["CEN"],
             "Deadbolt only gets Century trim")
