"""Seed additional Allegion products: Von Duprin 33A/35A, Sargent 8900 Profile,
Sargent Harmony, Norton 5800 concealed closer."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_von_duprin_ext(conn)
    _seed_sargent_profile(conn)
    _seed_sargent_harmony(conn)
    _seed_norton_5800(conn)
    print("  Von Duprin (ext) + Sargent Profile/Harmony + Norton 5800 seeded.")


# ═════════════════════════════════════════════════════════════════════
# Von Duprin 33A / 35A Rim Exit Devices
# ═════════════════════════════════════════════════════════════════════

def _seed_von_duprin_ext(conn):
    f = fid(conn, "Von Duprin", "33A/35A Rim Exit Device",
            "Exit Device",
            "{model}-{style} {trim} {finish}",
            "Von Duprin {model}-{style} Rim Exit {trim} {finish}")

    slot(conn, f, 1, "model",  "Model",       1)
    slot(conn, f, 2, "style",  "Style",       1)
    slot(conn, f, 3, "trim",   "Trim",        1)
    slot(conn, f, 4, "lever",  "Lever",       0)
    slot(conn, f, 5, "finish", "Finish",      1)

    options(conn, f, "model", [
        ("33A","33A - Standard Rim, 3' Doors"),
        ("35A","35A - Standard Rim, 4' Doors"),
    ])

    options(conn, f, "style", [
        ("DT", "DT - Dummy/Passage"),
        ("NL", "NL - Night Latch (key outside)"),
        ("NL-OP","NL-OP - Night Latch w/ Outside Pull"),
        ("EO", "EO - Exit Only (no trim)"),
        ("TP", "TP - Thumbpiece Outside"),
    ])

    options(conn, f, "trim", [
        ("388","388 - Lever Trim"),
        ("386","386 - Pull Trim"),
        ("389","389 - Escutcheon Lever"),
        ("N/A","No Outside Trim"),
    ])

    options(conn, f, "lever", [
        ("17","17 Lever"),("06","06 Lever (Knob)"),
        ("15","15 Lever"),("03","03 Lever (Knob Round)"),
    ])

    options(conn, f, "finish", [
        ("630","630 - Satin Stainless"),
        ("626","626 - Satin Chrome"),
        ("313","313 - Dark Bronze"),
        ("710","710 - Black"),
    ])

    # No trim on EO style
    restrict(conn, f, "style", "EO", "trim", ["N/A"],
             "Exit Only has no outside trim")
    restrict(conn, f, "style", "DT", "trim", ["N/A"],
             "Dummy has no outside trim")

    # Lever only valid with lever trim options
    for st in ("EO","DT"):
        restrict(conn, f, "style", st, "lever", [],
                 f"{st} has no lever")


# ═════════════════════════════════════════════════════════════════════
# Sargent 8900 Profile Series  (Grade 1 Mortise)
# ═════════════════════════════════════════════════════════════════════

def _seed_sargent_profile(conn):
    f = fid(conn, "Sargent", "8900 Profile Mortise Lock",
            "Mortise Lock",
            "8900 {function} {cylinder} {lever} {rose} {finish}",
            "Sargent 8900 Profile {function} {cylinder} {lever} {rose} {finish}")

    slot(conn, f, 1, "function", "Function",      1)
    slot(conn, f, 2, "cylinder", "Cylinder Type", 1)
    slot(conn, f, 3, "lever",    "Lever Design",  1)
    slot(conn, f, 4, "rose",     "Rose",          1)
    slot(conn, f, 5, "finish",   "Finish",        1)

    options(conn, f, "function", [
        ("8905","8905 - Entrance/Office"),
        ("8908","8908 - Classroom"),
        ("8909","8909 - Classroom Security"),
        ("8915","8915 - Dormitory/Exit"),
        ("8920","8920 - Privacy"),
        ("8960","8960 - Apartment"),
        ("8965","8965 - Storeroom"),
        ("8970","8970 - Passage/Closet"),
    ])

    options(conn, f, "cylinder", [
        ("LFIC","LFIC - Large Format IC"),
        ("SFIC","SFIC - Small Format IC"),
        ("Conv","Conventional Cylinder"),
        ("T-Turn","Thumbturn (Privacy)"),
    ])

    options(conn, f, "lever", [
        ("LP","LP Lever"),("LL","LL Lever"),
        ("LW","LW Lever"),("LE","LE Lever"),
    ])

    options(conn, f, "rose", [
        ("RX","RX Rose"),("PS","PS Rose (Profile)"),
    ])

    options(conn, f, "finish", [
        ("26D","26D - Satin Chrome"),
        ("32D","32D - Satin Stainless"),
        ("10B","10B - Oil Rubbed Bronze"),
        ("3",  "3 - Polished Brass"),
        ("10BL","10BL - Satin Dark Bronze"),
    ])

    restrict(conn, f, "function", "8920", "cylinder", ["T-Turn"],
             "Privacy uses thumbturn only")
    restrict(conn, f, "function", "8970", "cylinder", ["T-Turn"],
             "Passage uses thumbturn/none")


# ═════════════════════════════════════════════════════════════════════
# Sargent Harmony Series  (Electronic / Smart Access)
# ═════════════════════════════════════════════════════════════════════

def _seed_sargent_harmony(conn):
    f = fid(conn, "Sargent", "Harmony Electronic Mortise Lock",
            "Electronic Lock",
            "HM {function} {credential} {lever} {finish}",
            "Sargent Harmony {function} {credential} {lever} {finish}")

    slot(conn, f, 1, "function",   "Function",        1)
    slot(conn, f, 2, "credential", "Credential Type", 1)
    slot(conn, f, 3, "lever",      "Lever Design",    1)
    slot(conn, f, 4, "finish",     "Finish",          1)

    options(conn, f, "function", [
        ("Classroom","Classroom"),
        ("Storeroom","Storeroom"),
        ("Entrance","Entrance/Office"),
        ("Privacy","Privacy"),
    ])

    options(conn, f, "credential", [
        ("KP",  "KP - Keypad Only"),
        ("PROX","PROX - Proximity Card"),
        ("SC",  "SC - Smart Card / iCLASS"),
        ("BLE", "BLE - Bluetooth Low Energy"),
    ])

    options(conn, f, "lever", [
        ("LP","LP Lever"),("LL","LL Lever"),
        ("LW","LW Lever"),
    ])

    options(conn, f, "finish", [
        ("26D","26D - Satin Chrome"),
        ("32D","32D - Satin Stainless"),
        ("10B","10B - Oil Rubbed Bronze"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Norton 5800 Concealed Closer
# ═════════════════════════════════════════════════════════════════════

def _seed_norton_5800(conn):
    f = fid(conn, "Norton", "5800 Concealed Closer",
            "Closer",
            "5800 {size} {function} {finish}",
            "Norton 5800 Concealed Closer Size {size} {function} {finish}")

    slot(conn, f, 1, "size",     "Size",     1)
    slot(conn, f, 2, "function", "Function", 1)
    slot(conn, f, 3, "finish",   "Finish",   1)

    options(conn, f, "size", [
        ("2-4","Size 2-4"),
        ("5-6","Size 5-6"),
    ])

    options(conn, f, "function", [
        ("REG","Regular (Hold Open)"),
        ("DA", "DA - Double Acting"),
        ("HO", "HO - Hold Open Track"),
    ])

    options(conn, f, "finish", [
        ("689","689 - Aluminum"),
        ("690","690 - Dark Bronze"),
        ("693","693 - Black"),
    ])
