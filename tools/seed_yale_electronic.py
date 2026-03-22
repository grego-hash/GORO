"""Seed Yale nexTouch (electronic mortise/cylindrical) and Yale Assure (smart locks)."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_nextouch(conn)
    _seed_assure(conn)
    _seed_au(conn)
    print("  Yale nexTouch + Assure + AU seeded.")


# ═════════════════════════════════════════════════════════════════════
# Yale nexTouch — Electronic Keypad/Prox Lock (Mortise & Cylindrical)
# ═════════════════════════════════════════════════════════════════════

def _seed_nextouch(conn):
    # ── nexTouch Mortise ──
    f = fid(conn, "Yale", "nexTouch Keypad Mortise Lock",
            "Electronic Lock",
            "NTM {function} {credential} {lever} {finish}",
            "Yale nexTouch NTM {function} {credential} {lever} {finish}")

    slot(conn, f, 1, "function",   "Function",        1)
    slot(conn, f, 2, "credential", "Credential Type", 1)
    slot(conn, f, 3, "lever",      "Lever Design",    1)
    slot(conn, f, 4, "finish",     "Finish",          1)

    options(conn, f, "function", [
        ("Entrance", "Entrance/Office"),
        ("Classroom","Classroom"),
        ("Storeroom","Storeroom"),
        ("Privacy",  "Privacy"),
    ])

    options(conn, f, "credential", [
        ("KP",   "KP - Keypad Only"),
        ("PROX", "PROX - Proximity Card"),
        ("KP+PROX","KP+PROX - Keypad + Proximity"),
        ("BLE",  "BLE - Bluetooth"),
    ])

    options(conn, f, "lever", [
        ("AU","AU Lever"),("MO","MO Lever"),
        ("HA","HA Lever"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("630","630 - Satin Stainless"),
        ("613","613 - Oil Rubbed Bronze"),
    ])

    # ── nexTouch Cylindrical ──
    f2 = fid(conn, "Yale", "nexTouch Keypad Cylindrical Lock",
             "Electronic Lock",
             "NTB {function} {credential} {lever} {finish}",
             "Yale nexTouch NTB {function} {credential} {lever} {finish}")

    slot(conn, f2, 1, "function",   "Function",        1)
    slot(conn, f2, 2, "credential", "Credential Type", 1)
    slot(conn, f2, 3, "lever",      "Lever Design",    1)
    slot(conn, f2, 4, "finish",     "Finish",          1)

    options(conn, f2, "function", [
        ("Entrance", "Entrance/Office"),
        ("Classroom","Classroom"),
        ("Storeroom","Storeroom"),
    ])

    options(conn, f2, "credential", [
        ("KP",   "KP - Keypad Only"),
        ("PROX", "PROX - Proximity Card"),
        ("KP+PROX","KP+PROX - Keypad + Proximity"),
    ])

    options(conn, f2, "lever", [
        ("AU","AU Lever"),("MO","MO Lever"),
    ])

    options(conn, f2, "finish", [
        ("626","626 - Satin Chrome"),
        ("630","630 - Satin Stainless"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Yale Assure Lock SL — Touchscreen Deadbolt (Commercial Grade)
# ═════════════════════════════════════════════════════════════════════

def _seed_assure(conn):
    f = fid(conn, "Yale", "Assure Lock SL",
            "Electronic Lock",
            "YRD256 {network} {finish}",
            "Yale Assure Lock SL YRD256 {network} {finish}")

    slot(conn, f, 1, "network", "Network Module", 1)
    slot(conn, f, 2, "finish",  "Finish",         1)

    options(conn, f, "network", [
        ("Standalone","Standalone (no module)"),
        ("Z-Wave",    "Z-Wave Plus"),
        ("Zigbee",    "Zigbee"),
        ("Wi-Fi",     "Wi-Fi"),
        ("BLE",       "Bluetooth Low Energy"),
    ])

    options(conn, f, "finish", [
        ("SN","SN - Satin Nickel"),
        ("BSP","BSP - Black Suede"),
        ("PB","PB - Polished Brass"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Yale AU Series — Commercial Lever Lock (Grade 1 Cylindrical)
# ═════════════════════════════════════════════════════════════════════

def _seed_au(conn):
    f = fid(conn, "Yale", "AU Series Cylindrical Lock",
            "Cylindrical Lock",
            "AU{function} {cylinder} {lever} {finish}",
            "Yale AU-Series AU{function} {cylinder} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",      1)
    slot(conn, f, 2, "cylinder", "Cylinder Type", 1)
    slot(conn, f, 3, "lever",    "Lever Design",  1)
    slot(conn, f, 4, "finish",   "Finish",        1)

    options(conn, f, "function", [
        ("5301","AU5301 - Passage"),
        ("5302","AU5302 - Privacy"),
        ("5305","AU5305 - Entry"),
        ("5307","AU5307 - Classroom"),
        ("5308","AU5308 - Storeroom"),
        ("5309","AU5309 - Classroom Security"),
        ("5403","AU5403 - Entrance/Office"),
    ])

    options(conn, f, "cylinder", [
        ("LFIC","LFIC - Large Format IC"),
        ("SFIC","SFIC - Small Format IC"),
        ("Conv","Conventional Cylinder"),
        ("N/A", "N/A (Passage / Privacy)"),
    ])

    options(conn, f, "lever", [
        ("AU","AU Lever"),("MO","MO Lever"),
        ("HA","HA Lever"),("PB","PB Lever"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("630","630 - Satin Stainless"),
        ("613","613 - Oil Rubbed Bronze"),
        ("605","605 - Bright Brass"),
    ])

    for fn in ("5301","5302"):
        restrict(conn, f, "function", fn, "cylinder", ["N/A"],
                 f"AU {fn} has no cylinder")
