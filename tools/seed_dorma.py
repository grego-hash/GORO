"""Seed Dorma — TS closers, ED automatic operators."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_ts_closers(conn)
    _seed_auto_operators(conn)
    print("  Dorma closers + automatic operators seeded.")


# ═════════════════════════════════════════════════════════════════════
# Dorma TS Series Closers
# ═════════════════════════════════════════════════════════════════════

def _seed_ts_closers(conn):
    # ── TS 72 / TS 73 (Standard Duty) ──
    f = fid(conn, "Dorma", "TS 72/73 Door Closer",
            "Door Closer",
            "TS {model} {arm_type} {finish}",
            "Dorma TS {model} {arm_type} {finish}")

    slot(conn, f, 1, "model",     "Model",       1)
    slot(conn, f, 2, "arm_type",  "Arm Type",    1)
    slot(conn, f, 3, "mounting",  "Mounting",    1)
    slot(conn, f, 4, "size",      "Size",         1)
    slot(conn, f, 5, "finish",    "Finish",       1)
    slot(conn, f, 6, "cover",     "Cover",        0)

    options(conn, f, "model", [
        ("72",  "TS 72 - Standard Duty"),
        ("73",  "TS 73 - Standard Duty w/ Backcheck"),
        ("73V", "TS 73V - Standard Duty w/ Hold-Open"),
    ])

    arms = [
        ("REG",  "Regular Arm"),
        ("HO",   "Hold-Open Arm"),
        ("SA",   "Slide Arm / Track"),
    ]
    options(conn, f, "arm_type", arms)

    options(conn, f, "mounting", [
        ("PULL","Pull Side (Regular)"),
        ("PUSH","Push Side (Top Jamb)"),
        ("PA",  "Parallel Arm"),
    ])

    options(conn, f, "size", [("2","2"),("3","3"),("4","4"),("5","5")])

    finishes = [
        ("689","689 - Aluminum"),
        ("690","690 - Dark Bronze"),
        ("691","691 - Bright Chrome"),
        ("693","693 - Black"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "cover", [("NONE","None"),("CL","Slim Line Cover")])

    # ── TS 93 (Heavy Duty) ──
    f2 = fid(conn, "Dorma", "TS 93 Heavy Duty Door Closer",
             "Door Closer",
             "TS 93 {arm_type} {finish}",
             "Dorma TS 93 {arm_type} {finish}")

    slot(conn, f2, 1, "arm_type", "Arm Type",    1)
    slot(conn, f2, 2, "mounting", "Mounting",    1)
    slot(conn, f2, 3, "size",     "Size",         1)
    slot(conn, f2, 4, "finish",   "Finish",       1)
    slot(conn, f2, 5, "cover",    "Cover",        0)

    options(conn, f2, "arm_type", [
        ("REG",   "Regular Arm"),
        ("HO",    "Hold-Open Arm"),
        ("SA",    "Slide Arm / Track"),
        ("SA-HO", "Slide Arm w/ Hold-Open"),
    ])

    options(conn, f2, "mounting", [
        ("PULL","Pull Side (Regular)"),
        ("PUSH","Push Side (Top Jamb)"),
        ("PA",  "Parallel Arm"),
    ])

    options(conn, f2, "size", [("2","2"),("3","3"),("4","4"),("5","5"),("6","6")])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "cover", [("NONE","None"),("CL","Slim Line Cover"),("FC","Full Cover")])


# ═════════════════════════════════════════════════════════════════════
# Dorma ED / Automatic Operators
# ═════════════════════════════════════════════════════════════════════

def _seed_auto_operators(conn):
    # ── ED 900 / ED 700 ──
    f = fid(conn, "Dorma", "ED 900/700 Automatic Operator",
            "Automatic Operator",
            "ED {model} {power} {finish}",
            "Dorma ED {model} {power} {finish}")

    slot(conn, f, 1, "model",  "Model",          1)
    slot(conn, f, 2, "power",  "Power Source",    1)
    slot(conn, f, 3, "finish", "Finish",          1)
    slot(conn, f, 4, "sensor", "Activation",      0)

    models = [
        ("900",  "ED 900 - Low Energy Swing Operator"),
        ("950",  "ED 950 - Low Energy Swing (ADA)"),
        ("700",  "ED 700 - Full Power Swing Operator"),
        ("200",  "ED 200 - Sliding Door Operator"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "power", [
        ("120VAC","120VAC"),
        ("24VDC", "24VDC"),
    ])

    finishes = [
        ("689","689 - Aluminum"),
        ("690","690 - Dark Bronze"),
        ("691","691 - Bright Chrome"),
        ("BLK","BLK - Black"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "sensor", [
        ("NONE",  "None (Push Plate Only)"),
        ("MA",    "Motion Detector (Activation)"),
        ("MAP",   "Motion Detector (Activation + Presence)"),
        ("PB",    "Push Button Activation"),
    ])
