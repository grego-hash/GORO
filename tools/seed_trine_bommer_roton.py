"""Seed Trine electric strikes, Bommer spring/double-acting hinges, Roton continuous hinges."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_trine(conn)
    _seed_bommer(conn)
    _seed_roton(conn)
    print("  Trine + Bommer + Roton seeded.")


# ═════════════════════════════════════════════════════════════════════
# Trine Electric Strikes
# ═════════════════════════════════════════════════════════════════════

def _seed_trine(conn):
    f = fid(conn, "Trine", "Electric Strike",
            "Electric Strike",
            "{model} {voltage} {finish}",
            "Trine {model} {voltage} {finish}")

    slot(conn, f, 1, "model",    "Model",      1)
    slot(conn, f, 2, "voltage",  "Voltage",    1)
    slot(conn, f, 3, "function", "Function",   1)
    slot(conn, f, 4, "finish",   "Finish",     1)

    models = [
        ("3000",   "3000 - Standard Duty, 4-7/8\" x 1-1/4\""),
        ("3234",   "3234 - Heavy Duty, ANSI"),
        ("3478",   "3478 - Heavy Duty, Offset"),
        ("4100",   "4100 - Center Hung, Adjustable"),
        ("4200",   "4200 - Surface Mount (Rim)"),
        ("EN400",  "EN400 - Economy Series"),
        ("EN950",  "EN950 - Premium Series"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "voltage", [
        ("12VDC","12VDC"),("24VDC","24VDC"),
        ("12VAC","12VAC"),("24VAC","24VAC"),
    ])

    options(conn, f, "function", [
        ("FS",  "FS - Fail Safe"),
        ("F",   "F - Fail Secure"),
    ])

    options(conn, f, "finish", [
        ("630","630 - Satin Stainless"),
        ("612","612 - Satin Bronze"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Bommer Spring Hinges & Double-Acting Hinges
# ═════════════════════════════════════════════════════════════════════

def _seed_bommer(conn):
    # ── Single-Acting Spring Hinge ──
    f = fid(conn, "Bommer", "Single-Acting Spring Hinge",
            "Spring Hinge",
            "{model} {size} {finish}",
            "Bommer {model} Spring Hinge {size} {finish}")

    slot(conn, f, 1, "model",  "Model",    1)
    slot(conn, f, 2, "size",   "Size",     1)
    slot(conn, f, 3, "finish", "Finish",   1)

    options(conn, f, "model", [
        ("4811",  "4811 - Residential / Light Duty"),
        ("4811-6","4811-6 - Standard Duty, UL Listed"),
        ("4812",  "4812 - Adjustable Tension"),
    ])

    options(conn, f, "size", [
        ("3.5x3.5", "3-1/2\" x 3-1/2\""),
        ("4x4",     "4\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
    ])

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("P",    "P - Primed for Paint"),
    ]
    options(conn, f, "finish", finishes)

    # ── Double-Acting Spring Hinge ──
    f2 = fid(conn, "Bommer", "Double-Acting Spring Hinge",
             "Spring Hinge",
             "{model} {size} {finish}",
             "Bommer {model} Double-Acting {size} {finish}")

    slot(conn, f2, 1, "model",  "Model",   1)
    slot(conn, f2, 2, "size",   "Size",    1)
    slot(conn, f2, 3, "finish", "Finish",  1)

    options(conn, f2, "model", [
        ("3029",  "3029 - Light Duty Double-Acting"),
        ("3029-6","3029-6 - Standard Duty Double-Acting"),
        ("3037",  "3037 - Heavy Duty Double-Acting"),
    ])

    options(conn, f2, "size", [
        ("5x5",     "5\" x 5\""),
        ("6x6",     "6\" x 6\""),
        ("8x8",     "8\" x 8\""),
    ])

    options(conn, f2, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Roton Continuous Hinges
# ═════════════════════════════════════════════════════════════════════

def _seed_roton(conn):
    f = fid(conn, "Roton", "Continuous Geared Hinge",
            "Continuous Hinge",
            "{model} {length} {finish}",
            "Roton {model} Continuous {length} {finish}")

    slot(conn, f, 1, "model",  "Mounting Type", 1)
    slot(conn, f, 2, "length", "Length",         1)
    slot(conn, f, 3, "finish", "Finish",         1)

    options(conn, f, "model", [
        ("780-112",  "780-112 - Full Surface"),
        ("780-210",  "780-210 - Full Mortise"),
        ("780-312",  "780-312 - Half Surface"),
        ("780-412",  "780-412 - Half Mortise"),
        ("780-112HD","780-112HD - Full Surface, Heavy Duty"),
    ])

    options(conn, f, "length", [
        ("79","79\" (6'-7\")"),("83","83\" (6'-11\")"),
        ("85","85\" (7'-1\")"),("95","95\" (7'-11\")"),
    ])

    options(conn, f, "finish", [
        ("CL","CL - Clear Anodized"),
        ("DU","DU - Dark Bronze Anodized"),
        ("BK","BK - Black Anodized"),
        ("P", "P - Primed for Paint"),
    ])

    # ── Roton Electric Continuous ──
    f2 = fid(conn, "Roton", "Electric Power Transfer Hinge",
             "Electric Hinge",
             "{model}-E {wires} {length} {finish}",
             "Roton {model}-E {wires} {length} {finish}")

    slot(conn, f2, 1, "model",  "Mounting Type",  1)
    slot(conn, f2, 2, "wires",  "Wire Count",     1)
    slot(conn, f2, 3, "length", "Length",          1)
    slot(conn, f2, 4, "finish", "Finish",          1)

    options(conn, f2, "model", [
        ("780-112", "780-112 - Full Surface"),
        ("780-210", "780-210 - Full Mortise"),
        ("780-312", "780-312 - Half Surface"),
    ])

    options(conn, f2, "wires", [
        ("4W","4 Wire"),("6W","6 Wire"),
        ("8W","8 Wire"),("12W","12 Wire"),
    ])

    options(conn, f2, "length", [
        ("79","79\""),("83","83\""),("85","85\""),("95","95\""),
    ])

    options(conn, f2, "finish", [
        ("CL","CL - Clear Anodized"),
        ("DU","DU - Dark Bronze Anodized"),
        ("BK","BK - Black Anodized"),
    ])
