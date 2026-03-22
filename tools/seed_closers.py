"""Seed door closer data — LCN 4040XP, Norton 7500, Sargent 281."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


CLOSER_FINISHES = [
    ("ALM",  "ALM - Aluminum"),
    ("DKB",  "DKB - Dark Bronze"),
    ("BLK",  "BLK - Black"),
    ("689",  "689 - Aluminum Painted"),
    ("690",  "690 - Dark Bronze Painted (Statuary)"),
    ("691",  "691 - Dull Bronze Painted (Light)"),
    ("695",  "695 - Gold Painted"),
    ("696",  "696 - Brass / Bronze Painted"),
]


def seed(conn):
    _seed_lcn_4040xp(conn)
    _seed_norton_7500(conn)
    _seed_sargent_281(conn)
    print("  LCN 4040XP + Norton 7500 + Sargent 281 seeded.")


# ═════════════════════════════════════════════════════════════════════
# LCN 4040XP Series Door Closer
# ═════════════════════════════════════════════════════════════════════

def _seed_lcn_4040xp(conn):
    f = fid(conn,
            "LCN",
            "4040XP Series Door Closer",
            "Door Closer",
            "4040XP-{arm_type} {finish}",
            "LCN 4040XP {arm_type} {finish}")

    slot(conn, f, 1, "arm_type",     "Arm Type",         1)
    slot(conn, f, 2, "finish",       "Finish",           1)
    slot(conn, f, 3, "mounting",     "Mounting",         1)
    slot(conn, f, 4, "size",         "Spring Size",      1)
    slot(conn, f, 5, "cover",        "Cover",            0)
    slot(conn, f, 6, "hold_open",    "Hold Open",        0)

    arm_types = [
        ("REG",   "Regular Arm (Pull Side)"),
        ("CUSH",  "Cushion Arm (Pull Side)"),
        ("TBSRT", "Track / Slide Arm (Pull Side)"),
        ("HW",    "Hold-Open Extra Duty Arm"),
        ("SHCUSH","Slim Line Hold Open Cush Arm"),
        ("EDA",   "Extra Duty Arm"),
    ]
    options(conn, f, "arm_type", arm_types)

    options(conn, f, "finish", CLOSER_FINISHES)

    mountings = [
        ("REG",  "Regular (Hinge Side, Pull)"),
        ("PA",   "Parallel Arm (Push Side)"),
        ("TJ",   "Top Jamb (Push Side)"),
    ]
    options(conn, f, "mounting", mountings)

    sizes = [
        ("1",  "Size 1"),
        ("2",  "Size 2"),
        ("3",  "Size 3"),
        ("4",  "Size 4"),
        ("5",  "Size 5"),
        ("6",  "Size 6"),
        ("1-6","Size 1-6 (Adjustable)"),
    ]
    options(conn, f, "size", sizes)

    covers = [
        ("NONE",  "No Cover"),
        ("METAL", "Metal Cover"),
        ("PLSTC", "Plastic Cover"),
    ]
    options(conn, f, "cover", covers)

    hold_open = [
        ("NONE",    "No Hold Open"),
        ("FHOSRT",  "Friction Hold Open (Arm-Based)"),
        ("MHOSRT",  "Magnetic Hold Open"),
    ]
    options(conn, f, "hold_open", hold_open)


# ═════════════════════════════════════════════════════════════════════
# Norton 7500 Series Door Closer
# ═════════════════════════════════════════════════════════════════════

def _seed_norton_7500(conn):
    f = fid(conn,
            "Norton",
            "7500 Series Door Closer",
            "Door Closer",
            "7500-{arm_type} {finish}",
            "Norton 7500 {arm_type} {finish}")

    slot(conn, f, 1, "arm_type",  "Arm Type",       1)
    slot(conn, f, 2, "finish",    "Finish",          1)
    slot(conn, f, 3, "mounting",  "Mounting",        1)
    slot(conn, f, 4, "size",      "Spring Size",     1)
    slot(conn, f, 5, "cover",     "Cover",           0)

    arm_types = [
        ("REG",  "Regular Arm"),
        ("CUSH", "Cushion Stop Arm"),
        ("SN",   "CloserPlus Arm (Slide/Track)"),
        ("HO",   "Hold-Open Arm"),
        ("EDA",  "Extra Duty Arm"),
    ]
    options(conn, f, "arm_type", arm_types)

    options(conn, f, "finish", CLOSER_FINISHES)

    mountings = [
        ("REG", "Regular (Hinge Side, Pull)"),
        ("PA",  "Parallel Arm (Push Side)"),
        ("TJ",  "Top Jamb (Push Side)"),
    ]
    options(conn, f, "mounting", mountings)

    sizes = [
        ("1",  "Size 1"),
        ("2",  "Size 2"),
        ("3",  "Size 3"),
        ("4",  "Size 4"),
        ("5",  "Size 5"),
        ("6",  "Size 6"),
        ("1-6","Size 1-6 (Adjustable)"),
    ]
    options(conn, f, "size", sizes)

    covers = [
        ("NONE",  "No Cover"),
        ("METAL", "Metal Cover"),
    ]
    options(conn, f, "cover", covers)


# ═════════════════════════════════════════════════════════════════════
# Sargent 281 Series Door Closer
# ═════════════════════════════════════════════════════════════════════

def _seed_sargent_281(conn):
    f = fid(conn,
            "Sargent",
            "281 Series Door Closer",
            "Door Closer",
            "281-{arm_type} {finish}",
            "Sargent 281 {arm_type} {finish}")

    slot(conn, f, 1, "arm_type",  "Arm Type",     1)
    slot(conn, f, 2, "finish",    "Finish",        1)
    slot(conn, f, 3, "mounting",  "Mounting",      1)
    slot(conn, f, 4, "size",      "Spring Size",   1)
    slot(conn, f, 5, "cover",     "Cover",         0)

    arm_types = [
        ("REG",  "Regular Arm"),
        ("CUSH", "Cushion Stop Arm"),
        ("TB",   "Track/Slide Arm"),
        ("HO",   "Hold-Open Arm"),
        ("CPDA", "Compression Arm"),
    ]
    options(conn, f, "arm_type", arm_types)

    sar_closer_finishes = [
        ("EN",   "EN - Aluminum / Satin Aluminum"),
        ("BSP",  "BSP - Black Suede Powder Coat"),
        ("10BE", "10BE - Dark Bronze"),
        ("26D",  "26D - Satin Chrome"),
        ("3",    "3 - Bright Brass"),
    ]
    options(conn, f, "finish", sar_closer_finishes)

    mountings = [
        ("REG", "Regular (Hinge Side, Pull)"),
        ("PA",  "Parallel Arm (Push Side)"),
        ("TJ",  "Top Jamb (Push Side)"),
    ]
    options(conn, f, "mounting", mountings)

    sizes = [
        ("1",  "Size 1"),
        ("2",  "Size 2"),
        ("3",  "Size 3"),
        ("4",  "Size 4"),
        ("5",  "Size 5"),
        ("6",  "Size 6"),
        ("1-6","Size 1-6 (Adjustable)"),
    ]
    options(conn, f, "size", sizes)

    covers = [
        ("NONE",  "No Cover"),
        ("METAL", "Metal Cover"),
    ]
    options(conn, f, "cover", covers)
