"""Seed ASSA ABLOY misc (Sargent ASSA cylinders, Corbin Russwin Access 800,
Norton 6000 ADA operator) + Allegion misc (LCN 2010, Ives door stops extended)."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_assa_cylinders(conn)
    _seed_cr_access800(conn)
    _seed_norton_6000(conn)
    _seed_ives_stops(conn)
    print("  ASSA ABLOY misc + Allegion misc seeded.")


# ═════════════════════════════════════════════════════════════════════
# ASSA ABLOY – ASSA Twin / ASSA Max+ Cylinders
# ═════════════════════════════════════════════════════════════════════

def _seed_assa_cylinders(conn):
    f = fid(conn, "ASSA ABLOY", "ASSA High Security Cylinder",
            "Cylinder",
            "ASSA {keyway} {type} {length} {finish}",
            "ASSA {keyway} {type} Cylinder {length} {finish}")

    slot(conn, f, 1, "keyway", "Keyway / Platform", 1)
    slot(conn, f, 2, "type",   "Cylinder Type",     1)
    slot(conn, f, 3, "length", "Length",             1)
    slot(conn, f, 4, "finish", "Finish",             1)

    options(conn, f, "keyway", [
        ("Twin","Twin 6000 (6-pin, restricted)"),
        ("Max+","Max+ (7-pin, patented)"),
        ("P600","P600 (6-pin, master-keyable)"),
    ])

    options(conn, f, "type", [
        ("Mort","Mortise Cylinder"),
        ("Rim", "Rim Cylinder"),
        ("KIK", "Key-in-Knob"),
        ("LFIC","Large Format IC Core"),
        ("SFIC","Small Format IC Core"),
    ])

    options(conn, f, "length", [
        ("1-1/8","1-1/8\""),("1-1/4","1-1/4\""),
        ("1-3/8","1-3/8\""),("1-1/2","1-1/2\""),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("613","613 - Oil Rubbed Bronze"),
        ("606","606 - Satin Brass"),
    ])

    # IC cores don't use the length slot
    for ic in ("LFIC","SFIC"):
        restrict(conn, f, "type", ic, "length", ["1-1/8"],
                 f"IC cores have fixed length")


# ═════════════════════════════════════════════════════════════════════
# Corbin Russwin – Access 800 Electronic
# ═════════════════════════════════════════════════════════════════════

def _seed_cr_access800(conn):
    f = fid(conn, "Corbin Russwin", "Access 800 Electronic Lock",
            "Electronic Lock",
            "AD-800 {body} {credential} {lever} {finish}",
            "Corbin Russwin Access 800 {body} {credential} {lever} {finish}")

    slot(conn, f, 1, "body",       "Lock Body",       1)
    slot(conn, f, 2, "credential", "Credential Type", 1)
    slot(conn, f, 3, "lever",      "Lever Design",    1)
    slot(conn, f, 4, "finish",     "Finish",          1)

    options(conn, f, "body", [
        ("Mortise","Mortise Lock Body"),
        ("Cylindrical","Cylindrical Lock Body"),
        ("Exit Trim","Exit Device Trim"),
    ])

    options(conn, f, "credential", [
        ("KP","Keypad"),
        ("PROX","Proximity (HID)"),
        ("SC","Smart Card (iCLASS)"),
        ("Multi","Multi-Technology"),
    ])

    options(conn, f, "lever", [
        ("D",  "D Lever"),
        ("MO", "MO Lever"),
        ("RA", "RA Lever"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("630","630 - Satin Stainless"),
        ("613","613 - Oil Rubbed Bronze"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Norton 6000 Series ADA Low-Energy Operator
# ═════════════════════════════════════════════════════════════════════

def _seed_norton_6000(conn):
    f = fid(conn, "Norton", "6000 ADA Operator",
            "Automatic Operator",
            "6000 {mount} {voltage} {finish}",
            "Norton 6000 ADA Low-Energy Operator {mount} {voltage} {finish}")

    slot(conn, f, 1, "mount",   "Mounting",  1)
    slot(conn, f, 2, "voltage", "Voltage",   1)
    slot(conn, f, 3, "arm",     "Arm Type",  1)
    slot(conn, f, 4, "finish",  "Finish",    1)

    options(conn, f, "mount", [
        ("Push","Push Side"),
        ("Pull","Pull Side"),
    ])

    options(conn, f, "voltage", [
        ("120VAC","120VAC"),("24VDC","24VDC"),
    ])

    options(conn, f, "arm", [
        ("REG","Regular Arm"),
        ("PA", "Parallel Arm"),
        ("TJ", "Top Jamb"),
        ("SLD","Slide Track"),
    ])

    options(conn, f, "finish", [
        ("689","689 - Aluminum"),
        ("690","690 - Dark Bronze"),
        ("693","693 - Black"),
    ])


# ═════════════════════════════════════════════════════════════════════
# LCN 2010 – Concealed Overhead Closer (compact)
# ═════════════════════════════════════════════════════════════════════

def _seed_lcn_2010(conn):
    f = fid(conn, "LCN", "2010 Concealed Closer",
            "Closer",
            "2010 {size} {function}",
            "LCN 2010 Concealed Overhead Closer Size {size} {function}")

    slot(conn, f, 1, "size",     "Size",     1)
    slot(conn, f, 2, "function", "Function", 1)

    options(conn, f, "size", [
        ("2-4","Size 2-4"),
        ("5",  "Size 5"),
    ])

    options(conn, f, "function", [
        ("STD","Standard"),
        ("HO","Hold Open"),
        ("DA","Double Acting (non-hold-open)"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Ives – Door Stops (Extended)
# ═════════════════════════════════════════════════════════════════════

def _seed_ives_stops(conn):
    f = fid(conn, "Ives", "Door Stop",
            "Door Stop",
            "{model} {finish}",
            "Ives {model} Door Stop {finish}")

    slot(conn, f, 1, "model",  "Model",  1)
    slot(conn, f, 2, "finish", "Finish", 1)

    options(conn, f, "model", [
        ("WS406","WS406 - Wall Bumper (Convex)"),
        ("WS407","WS407 - Wall Bumper (Concave)"),
        ("FS436","FS436 - Floor Stop (Heavy Duty)"),
        ("FS438","FS438 - Floor Stop (Extra Heavy Duty)"),
        ("WS443","WS443 - Wall Stop & Holder"),
        ("OH","OH - Overhead Door Holder"),
    ])

    options(conn, f, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US26", "US26 - Bright Chrome"),
    ])
