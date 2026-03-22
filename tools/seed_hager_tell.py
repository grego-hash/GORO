"""Seed Hager 3800 tubular lever locks and Tell Manufacturing budget cylindrical."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_hager_3800(conn)
    _seed_tell(conn)
    print("  Hager 3800 + Tell Manufacturing seeded.")


# ═════════════════════════════════════════════════════════════════════
# Hager 3800 Series Tubular Lever Lock  (Grade 2)
# ═════════════════════════════════════════════════════════════════════

def _seed_hager_3800(conn):
    f = fid(conn, "Hager", "3800 Tubular Lever Lock",
            "Cylindrical Lock",
            "3800 {function} {lever} {finish}",
            "Hager 3800 {function} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",     1)
    slot(conn, f, 2, "lever",    "Lever Design", 1)
    slot(conn, f, 3, "finish",   "Finish",       1)

    options(conn, f, "function", [
        ("3810", "3810 - Passage"),
        ("3820", "3820 - Privacy"),
        ("3853", "3853 - Entry"),
        ("3870", "3870 - Classroom"),
        ("3880", "3880 - Storeroom"),
        ("3817", "3817 - Dummy Trim"),
    ])

    options(conn, f, "lever", [
        ("WTN","Withnell Lever"),
        ("SQR","August Lever"),
        ("LON","London Lever"),
        ("ARC","Archer Lever"),
    ])

    options(conn, f, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US26", "US26 - Bright Chrome"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Tell Manufacturing – Budget Cylindrical Locks  (Grade 2)
# ═════════════════════════════════════════════════════════════════════

def _seed_tell(conn):
    f = fid(conn, "Tell Manufacturing", "LC2000 Cylindrical Lock",
            "Cylindrical Lock",
            "LC2000 {function} {lever} {finish}",
            "Tell LC2000 {function} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",     1)
    slot(conn, f, 2, "lever",    "Lever Design", 1)
    slot(conn, f, 3, "finish",   "Finish",       1)

    options(conn, f, "function", [
        ("Passage",   "Passage"),
        ("Privacy",   "Privacy"),
        ("Entry",     "Keyed Entry"),
        ("Classroom", "Classroom"),
        ("Storeroom", "Storeroom"),
    ])

    options(conn, f, "lever", [
        ("LX","LX - Standard Lever"),
        ("EX","EX - Economy Lever"),
    ])

    options(conn, f, "finish", [
        ("26D","26D - Satin Chrome"),
        ("32D","32D - Satin Stainless"),
        ("10B","10B - Oil Rubbed Bronze"),
    ])

    # ── Tell Guard Commercial Grade 1 Closer ──
    f2 = fid(conn, "Tell Manufacturing", "DC100 Closer",
             "Closer",
             "DC100 {size} {arm} {finish}",
             "Tell DC100 Closer Size {size} {arm} {finish}")

    slot(conn, f2, 1, "size",   "Size",     1)
    slot(conn, f2, 2, "arm",    "Arm Type", 1)
    slot(conn, f2, 3, "finish", "Finish",   1)

    options(conn, f2, "size", [
        ("1-4","Size 1-4"),
        ("3-6","Size 3-6"),
    ])

    options(conn, f2, "arm", [
        ("REG","Regular Arm"),
        ("PA", "Parallel Arm"),
        ("TJ", "Top Jamb"),
    ])

    options(conn, f2, "finish", [
        ("AL","AL - Aluminum"),
        ("DU","DU - Dark Bronze"),
        ("BK","BK - Black"),
    ])
