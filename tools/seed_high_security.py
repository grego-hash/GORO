"""Seed high-security cylinders — Medeco, Mul-T-Lock."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_medeco(conn)
    _seed_multlock(conn)
    print("  Medeco + Mul-T-Lock seeded.")


# ═════════════════════════════════════════════════════════════════════
# Medeco High-Security Cylinders
# ═════════════════════════════════════════════════════════════════════

def _seed_medeco(conn):
    # ── Mortise / Rim / KIL Cylinders ──
    f = fid(conn, "Medeco", "High-Security Cylinder",
            "Cylinder",
            "{keyway}-{type} {length} {finish}",
            "Medeco {keyway} {type} {length} {finish}")

    slot(conn, f, 1, "keyway",  "Keyway / Platform", 1)
    slot(conn, f, 2, "type",    "Cylinder Type",      1)
    slot(conn, f, 3, "length",  "Cylinder Length",    1)
    slot(conn, f, 4, "finish",  "Finish",             1)

    keyways = [
        ("M3",      "M3 - Medeco3 (Slider + Rotation)"),
        ("X4",      "X4 - Medeco4 (Slider + Rotation + Side Bit)"),
        ("MX",      "MX - Medeco Maxum (Budget High-Sec)"),
    ]
    options(conn, f, "keyway", keyways)

    cyl_types = [
        ("MORT",   "Mortise Cylinder (1-1/8\")"),
        ("MORT-2", "Mortise Cylinder (1-1/4\")"),
        ("RIM",    "Rim Cylinder"),
        ("KIL",    "Key-in-Lever Cylinder"),
        ("KILD",   "Key-in-Deadbolt Cylinder"),
        ("SFIC",   "SFIC - Small Format IC Core"),
        ("FSIC",   "FSIC - Full Size IC Core"),
    ]
    options(conn, f, "type", cyl_types)

    options(conn, f, "length", [
        ("1-1/8",  "1-1/8\""),
        ("1-1/4",  "1-1/4\""),
        ("1-3/8",  "1-3/8\""),
        ("1-1/2",  "1-1/2\""),
    ])

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US26", "US26 - Polished Chrome"),
    ]
    options(conn, f, "finish", finishes)

    # IC cores don't have length
    for ic in ["SFIC", "FSIC"]:
        restrict(conn, f, "type", ic, "length", ["1-1/8"],
                 f"{ic} core → standard length only")

    # ── Medeco Maxum Deadbolt ──
    f2 = fid(conn, "Medeco", "Maxum Deadbolt",
             "Deadbolt",
             "Maxum-{function} {finish}",
             "Medeco Maxum {function} Deadbolt {finish}")

    slot(conn, f2, 1, "function", "Function",   1)
    slot(conn, f2, 2, "finish",   "Finish",     1)

    options(conn, f2, "function", [
        ("SC",   "Single Cylinder"),
        ("DC",   "Double Cylinder"),
        ("DCTT", "Double Cylinder w/ Thumbturn"),
    ])
    options(conn, f2, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Mul-T-Lock High-Security Cylinders
# ═════════════════════════════════════════════════════════════════════

def _seed_multlock(conn):
    f = fid(conn, "Mul-T-Lock", "High-Security Cylinder",
            "Cylinder",
            "{keyway}-{type} {finish}",
            "Mul-T-Lock {keyway} {type} {finish}")

    slot(conn, f, 1, "keyway", "Keyway / Platform", 1)
    slot(conn, f, 2, "type",   "Cylinder Type",      1)
    slot(conn, f, 3, "length", "Cylinder Length",     1)
    slot(conn, f, 4, "finish", "Finish",              1)

    keyways = [
        ("MT5+",   "MT5+ (Telescopic Pins + Sidebar)"),
        ("Interactive", "Interactive+ (Telescopic Pins)"),
        ("Classic", "Classic (Pin-in-Pin)"),
    ]
    options(conn, f, "keyway", keyways)

    cyl_types = [
        ("MORT",  "Mortise Cylinder"),
        ("RIM",   "Rim Cylinder"),
        ("KIL",   "Key-in-Lever Cylinder"),
        ("SFIC",  "SFIC Core"),
        ("FSIC",  "FSIC Core"),
    ]
    options(conn, f, "type", cyl_types)

    options(conn, f, "length", [
        ("1-1/8","1-1/8\""),
        ("1-1/4","1-1/4\""),
        ("1-3/8","1-3/8\""),
        ("1-1/2","1-1/2\""),
    ])

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US3",  "US3 - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    for ic in ["SFIC", "FSIC"]:
        restrict(conn, f, "type", ic, "length", ["1-1/8"],
                 f"{ic} core → standard length only")

    # ── Mul-T-Lock Hercular Deadbolt ──
    f2 = fid(conn, "Mul-T-Lock", "Hercular Deadbolt",
             "Deadbolt",
             "Hercular-{function} {finish}",
             "Mul-T-Lock Hercular {function} Deadbolt {finish}")

    slot(conn, f2, 1, "function", "Function",   1)
    slot(conn, f2, 2, "finish",   "Finish",     1)

    options(conn, f2, "function", [
        ("SC",  "Single Cylinder"),
        ("DC",  "Double Cylinder"),
    ])
    options(conn, f2, "finish", finishes)
