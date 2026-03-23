"""Seed Schlage A-Series (budget cylindrical), AL-Series (mid-grade), B-Series (deadbolts)."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_a_series(conn)
    _seed_al_series(conn)
    _seed_b_series(conn)
    print("  Schlage A/AL/B Series seeded.")


# ═════════════════════════════════════════════════════════════════════
# Schlage A-Series – Budget Cylindrical (Grade 2)
# ═════════════════════════════════════════════════════════════════════

def _seed_a_series(conn):
    f = fid(conn, "Schlage", "A-Series Cylindrical Lock",
            "Cylindrical Lock",
            "A{function} {keyway} {lever} {finish}",
            "Schlage A-Series A{function} {keyway} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",      1)
    slot(conn, f, 2, "keyway",   "Keyway",        1)
    slot(conn, f, 3, "lever",    "Lever Design",  1)
    slot(conn, f, 4, "finish",   "Finish",        1)

    options(conn, f, "function", [
        ("10S", "A10S - Passage"),
        ("25D", "A25D - Exit (no key)"),
        ("40S", "A40S - Privacy (Bath/Bed)"),
        ("53PD","A53PD - Entry"),
        ("70PD","A70PD - Classroom"),
        ("73PD","A73PD - Classroom Security"),
        ("80PD","A80PD - Storeroom"),
        ("85PD","A85PD - Faculty Restroom"),
        ("170", "A170 - Dummy Trim"),
    ])

    options(conn, f, "keyway", [
        ("CE", "CE - Schlage CE"),
        ("C",  "C - Schlage C"),
        ("N/A","N/A (Passage / Privacy)"),
    ])

    options(conn, f, "lever", [
        ("PLY","Plymouth Knob"),
        ("TUL","Tulip Knob"),
        ("ORB","Orbit Knob"),
        ("GEO","Georgian Knob"),
        ("ACC","Accent Lever"),
        ("MER","Merano Lever"),
        ("BEL","Bell Knob"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("605","605 - Bright Brass"),
        ("613","613 - Oil Rubbed Bronze"),
        ("619","619 - Satin Nickel"),
        ("625","625 - Bright Chrome"),
        ("609","609 - Antique Brass"),
        ("612","612 - Satin Bronze"),
        ("643e","643e - Aged Bronze"),
    ])

    # Passage / Privacy don't use keyway
    for fn in ("10S", "40S", "170"):
        restrict(conn, f, "function", fn, "keyway", ["N/A"],
                 f"A-Series {fn} has no cylinder")


# ═════════════════════════════════════════════════════════════════════
# Schlage AL-Series – Mid-Grade Cylindrical (Grade 2)
# ═════════════════════════════════════════════════════════════════════

def _seed_al_series(conn):
    f = fid(conn, "Schlage", "AL-Series Cylindrical Lock",
            "Cylindrical Lock",
            "AL{function} {keyway} {lever} {finish}",
            "Schlage AL-Series AL{function} {keyway} {lever} {finish}")

    slot(conn, f, 1, "function",  "Function",      1)
    slot(conn, f, 2, "keyway",    "Keyway",        1)
    slot(conn, f, 3, "lever",     "Lever Design",  1)
    slot(conn, f, 4, "finish",    "Finish",        1)

    options(conn, f, "function", [
        ("10S", "AL10S - Passage"),
        ("25D", "AL25D - Exit"),
        ("40S", "AL40S - Privacy"),
        ("53A", "AL53A - Entry"),
        ("70J", "AL70J - Classroom"),
        ("72J", "AL72J - Classroom Security"),
        ("80J", "AL80J - Storeroom"),
        ("85J", "AL85J - Faculty Restroom"),
        ("170", "AL170 - Dummy Trim"),
    ])

    options(conn, f, "keyway", [
        ("SAT","SAT - Saturn (6-pin)"),
        ("JUP","JUP - Jupiter (7-pin)"),
        ("N/A","N/A (Passage / Privacy)"),
    ])

    options(conn, f, "lever", [
        ("SAT","Saturn Lever"),
        ("JUP","Jupiter Lever"),
        ("MER","Mercury Lever"),
        ("NEP","Neptune Lever"),
        ("OME","Omega Lever"),
        ("ATH","Athens Lever"),
        ("RHO","Rhodes Lever"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("605","605 - Bright Brass"),
        ("613","613 - Oil Rubbed Bronze"),
        ("619","619 - Satin Nickel"),
        ("643E","643E - Aged Bronze"),
        ("625","625 - Bright Chrome"),
        ("612","612 - Satin Bronze"),
        ("622","622 - Flat Black"),
    ])

    for fn in ("10S", "40S", "170"):
        restrict(conn, f, "function", fn, "keyway", ["N/A"],
                 f"AL-Series {fn} has no cylinder")


# ═════════════════════════════════════════════════════════════════════
# Schlage B-Series – Deadbolts
# ═════════════════════════════════════════════════════════════════════

def _seed_b_series(conn):
    f = fid(conn, "Schlage", "B-Series Deadbolt",
            "Deadbolt",
            "B{function} {keyway} {finish}",
            "Schlage B-Series B{function} Deadbolt {keyway} {finish}")

    slot(conn, f, 1, "function", "Function",  1)
    slot(conn, f, 2, "keyway",   "Keyway",    1)
    slot(conn, f, 3, "finish",   "Finish",    1)

    options(conn, f, "function", [
        ("60N","B60N - Single Cylinder"),
        ("62N","B62N - Double Cylinder"),
        ("80N","B80N - Auxiliary (no key)"),
        ("81N","B81N - Auxiliary Deadlock"),
        ("160N","B160N - Single Cyl + Thumbturn"),
        ("560N","B560N - Single Cyl (Grade 2 Commercial)"),
        ("562N","B562N - Double Cyl (Grade 2 Commercial)"),
        ("660P","B660P - Single Cyl Thumbturn (Grade 1)"),
        ("663P","B663P - Classroom Deadbolt (Grade 1)"),
    ])

    options(conn, f, "keyway", [
        ("C",  "C - Schlage C"),
        ("CE", "CE - Schlage CE"),
        ("N/A","N/A (Auxiliary)"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("605","605 - Bright Brass"),
        ("613","613 - Oil Rubbed Bronze"),
        ("619","619 - Satin Nickel"),
        ("625","625 - Bright Chrome"),
        ("609","609 - Antique Brass"),
        ("612","612 - Satin Bronze"),
        ("643e","643e - Aged Bronze"),
    ])

    for fn in ("80N", "81N"):
        restrict(conn, f, "function", fn, "keyway", ["N/A"],
                 f"B-Series {fn} has no cylinder")
