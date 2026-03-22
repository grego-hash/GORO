"""Seed Stanley automatic operators and Global Door Controls budget closers."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_stanley(conn)
    _seed_gdc(conn)
    print("  Stanley + Global Door Controls seeded.")


# ═════════════════════════════════════════════════════════════════════
# Stanley Automatic Door Operators
# ═════════════════════════════════════════════════════════════════════

def _seed_stanley(conn):
    # ── D4990 Low Energy Swing Operator ──
    f = fid(conn, "Stanley", "D4990 Low Energy Operator",
            "Automatic Operator",
            "D4990 {function} {voltage} {finish}",
            "Stanley D4990 Low Energy Swing Operator {function} {voltage} {finish}")

    slot(conn, f, 1, "function", "Function",  1)
    slot(conn, f, 2, "voltage",  "Voltage",   1)
    slot(conn, f, 3, "arm",      "Arm Type",  1)
    slot(conn, f, 4, "finish",   "Finish",    1)

    options(conn, f, "function", [
        ("Push","Push Side Mount"),
        ("Pull","Pull Side Mount"),
    ])
    options(conn, f, "voltage", [
        ("120VAC","120VAC"),("240VAC","240VAC"),
    ])
    options(conn, f, "arm", [
        ("PA","PA - Push Arm"),
        ("RA","RA - Regular Arm"),
        ("TBA","TBA - Track/Slide Arm"),
    ])
    options(conn, f, "finish", [
        ("AL","AL - Aluminum"),("DK","DK - Dark Bronze"),
        ("BK","BK - Black"),
    ])

    # ── Magic-Force / Magic-Swing Operator ──
    f2 = fid(conn, "Stanley", "Magic-Force Operator",
             "Automatic Operator",
             "Magic-Force {mode} {voltage} {finish}",
             "Stanley Magic-Force/Magic-Swing {mode} {voltage} {finish}")

    slot(conn, f2, 1, "mode",    "Mode",     1)
    slot(conn, f2, 2, "voltage", "Voltage",  1)
    slot(conn, f2, 3, "finish",  "Finish",   1)

    options(conn, f2, "mode", [
        ("Full Power","Full Power Swing"),
        ("Low Energy","Low Energy Swing"),
    ])
    options(conn, f2, "voltage", [
        ("120VAC","120VAC"),("240VAC","240VAC"),
    ])
    options(conn, f2, "finish", [
        ("AL","AL - Aluminum"),("DK","DK - Dark Bronze"),
        ("BK","BK - Black"),
    ])

    # ── Dura-Glide Sliding Door Operator ──
    f3 = fid(conn, "Stanley", "Dura-Glide Sliding Operator",
             "Automatic Operator",
             "Dura-Glide {model} {voltage} {finish}",
             "Stanley Dura-Glide {model} Sliding Door Operator {voltage} {finish}")

    slot(conn, f3, 1, "model",   "Model",   1)
    slot(conn, f3, 2, "voltage", "Voltage", 1)
    slot(conn, f3, 3, "finish",  "Finish",  1)

    options(conn, f3, "model", [
        ("2000","Dura-Glide 2000 - Single Slide"),
        ("2000B","Dura-Glide 2000 - Bi-Part"),
        ("3000","Dura-Glide 3000 - ICU/Break-Out"),
        ("5000","Dura-Glide 5000 - Full Break-Out"),
    ])
    options(conn, f3, "voltage", [
        ("120VAC","120VAC"),("240VAC","240VAC"),
    ])
    options(conn, f3, "finish", [
        ("AL","AL - Aluminum"),("DK","DK - Dark Bronze"),
        ("BK","BK - Black"),("SS","SS - Stainless Steel"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Global Door Controls – Budget Closers
# ═════════════════════════════════════════════════════════════════════

def _seed_gdc(conn):
    # ── GDC Surface Closer ──
    f = fid(conn, "Global Door Controls", "Surface Closer",
            "Closer",
            "TC200 {size} {arm} {finish}",
            "Global Door Controls TC200 Size {size} {arm} {finish}")

    slot(conn, f, 1, "size",   "Size",     1)
    slot(conn, f, 2, "arm",    "Arm Type", 1)
    slot(conn, f, 3, "finish", "Finish",   1)

    options(conn, f, "size", [
        ("1","Size 1 (interior light)"),
        ("2","Size 2 (interior medium)"),
        ("3","Size 3 (interior standard)"),
        ("4","Size 4 (exterior standard)"),
        ("5","Size 5 (exterior heavy)"),
        ("6","Size 6 (exterior extra-heavy)"),
    ])
    options(conn, f, "arm", [
        ("REG","Regular / Standard Arm"),
        ("PA","Parallel Arm"),
        ("TJ","Top Jamb"),
    ])
    options(conn, f, "finish", [
        ("AL","AL - Aluminum"),("DU","DU - Dark Bronze"),
        ("BK","BK - Black"),
    ])

    # ── GDC Spring Hinge ──
    f2 = fid(conn, "Global Door Controls", "Spring Hinge",
             "Spring Hinge",
             "CPS {size} {finish}",
             "Global Door Controls CPS Spring Hinge {size} {finish}")

    slot(conn, f2, 1, "size",   "Size",   1)
    slot(conn, f2, 2, "finish", "Finish", 1)

    options(conn, f2, "size", [
        ("3.5x3.5", "3-1/2\" x 3-1/2\""),
        ("4x4",     "4\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
    ])
    options(conn, f2, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless Steel"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("P",    "P - Primed for Paint"),
    ])
