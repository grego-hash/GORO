"""Seed pulls, protection, and trim — Rockwood, Trimco, Don-Jo."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_rockwood(conn)
    _seed_trimco(conn)
    _seed_donjo(conn)
    print("  Rockwood + Trimco + Don-Jo seeded.")


# ═════════════════════════════════════════════════════════════════════
# Rockwood
# ═════════════════════════════════════════════════════════════════════

def _seed_rockwood(conn):
    # ── Pull Handles ──
    f = fid(conn, "Rockwood", "Pull Handle",
            "Pull / Push",
            "RM{model} {size} {finish}",
            "Rockwood RM{model} {size} {finish}")

    slot(conn, f, 1, "model",  "Model",       1)
    slot(conn, f, 2, "size",   "Length",       1)
    slot(conn, f, 3, "finish", "Finish",       1)
    slot(conn, f, 4, "mount",  "Mounting",     1)

    models = [
        ("BF100", "BF100 - Straight Pull"),
        ("BF102", "BF102 - Offset Pull"),
        ("BF107", "BF107 - Round Pull"),
        ("BF110", "BF110 - Straight Pull, Cast"),
        ("BF157", "BF157 - Hospital Pull"),
    ]
    options(conn, f, "model", models)

    sizes = [
        ("8",  "8\" CTC"),
        ("10", "10\" CTC"),
        ("12", "12\" CTC"),
    ]
    options(conn, f, "size", sizes)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US28", "US28 - Satin Aluminum"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "mount", [
        ("TM", "TM - Thru-Mount (Back-to-Back)"),
        ("SM", "SM - Surface Mount"),
    ])

    # ── Push Plates ──
    f2 = fid(conn, "Rockwood", "Push Plate",
             "Push / Pull Plate",
             "{model} {size} {finish}",
             "Rockwood {model} {size} {finish}")

    slot(conn, f2, 1, "model",  "Model",    1)
    slot(conn, f2, 2, "size",   "Size",     1)
    slot(conn, f2, 3, "finish", "Finish",   1)

    pp_models = [
        ("70A",   "70A - Push Plate, Square Corner"),
        ("70B",   "70B - Push Plate, Round Corner"),
        ("70C",   "70C - Push Plate, Beveled Edge"),
        ("76",    "76 - Hospital Push Plate"),
    ]
    options(conn, f2, "model", pp_models)

    pp_sizes = [
        ("3.5x15",  "3-1/2\" x 15\""),
        ("4x16",    "4\" x 16\""),
        ("6x16",    "6\" x 16\""),
        ("8x16",    "8\" x 16\""),
    ]
    options(conn, f2, "size", pp_sizes)
    options(conn, f2, "finish", finishes)

    # ── Kick Plates ──
    f3 = fid(conn, "Rockwood", "Kick Plate",
             "Protection Plate",
             "K1050 {height} {width} {finish}",
             "Rockwood K1050 {height} x {width} {finish}")

    slot(conn, f3, 1, "height", "Height",     1)
    slot(conn, f3, 2, "width",  "Width",      1)
    slot(conn, f3, 3, "finish", "Finish",     1)
    slot(conn, f3, 4, "corner", "Corners",    1)

    options(conn, f3, "height", [
        ("6",  "6\""),("8",  "8\""),("10", "10\""),("12", "12\""),
    ])
    options(conn, f3, "width", [
        ("28",  "28\" (2'-4\")"),("30","30\" (2'-6\")"),
        ("32",  "32\" (2'-8\")"),("34","34\" (2'-10\")"),
        ("36",  "36\" (3'-0\")"),("42","42\" (3'-6\")"),
    ])
    options(conn, f3, "finish", finishes)
    options(conn, f3, "corner", [("SQ","Square"),("RD","Rounded"),("BV","Beveled")])

    # ── Mop Plates ──
    f4 = fid(conn, "Rockwood", "Mop/Armor Plate",
             "Protection Plate",
             "K1050 {height} {width} {finish}",
             "Rockwood Mop Plate {height} x {width} {finish}")

    slot(conn, f4, 1, "height", "Height",   1)
    slot(conn, f4, 2, "width",  "Width",    1)
    slot(conn, f4, 3, "finish", "Finish",   1)

    options(conn, f4, "height", [("4","4\""),("6","6\"")])
    options(conn, f4, "width", [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),("42","42\""),
    ])
    options(conn, f4, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Trimco
# ═════════════════════════════════════════════════════════════════════

def _seed_trimco(conn):
    # ── Hospital Push/Pull ──
    f = fid(conn, "Trimco", "1001A Hospital Push/Pull",
            "Pull / Push",
            "1001A {size} {finish}",
            "Trimco 1001A {size} {finish}")

    slot(conn, f, 1, "size",   "Size (CTC)",  1)
    slot(conn, f, 2, "finish", "Finish",       1)

    options(conn, f, "size", [
        ("8",  "8\" CTC"),
        ("10", "10\" CTC"),
        ("12", "12\" CTC"),
    ])

    finishes = [
        ("630", "630 - Satin Stainless"),
        ("626", "626 - Satin Chrome"),
        ("628", "628 - Satin Aluminum"),
        ("613", "613 - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    # ── Flush Pulls / Edge Pulls ──
    f2 = fid(conn, "Trimco", "Flush Pull / Edge Pull",
             "Pull / Push",
             "{model} {finish}",
             "Trimco {model} {finish}")

    slot(conn, f2, 1, "model",  "Model",   1)
    slot(conn, f2, 2, "finish", "Finish",  1)

    models = [
        ("1064",   "1064 - Flush Pull, 1\" x 3-1/4\""),
        ("1069",   "1069 - Flush Pull, 2\" x 7\""),
        ("1064-2", "1064-2 - Flush Pull, 1\" x 4\""),
        ("5002",   "5002 - Edge Pull"),
        ("5003",   "5003 - Edge Pull, Heavy Duty"),
    ]
    options(conn, f2, "model", models)
    options(conn, f2, "finish", finishes)

    # ── Push Plates ──
    f3 = fid(conn, "Trimco", "Push Plate",
             "Push / Pull Plate",
             "{model} {size} {finish}",
             "Trimco {model} {size} {finish}")

    slot(conn, f3, 1, "model",  "Model",   1)
    slot(conn, f3, 2, "size",   "Size",    1)
    slot(conn, f3, 3, "finish", "Finish",  1)

    options(conn, f3, "model", [
        ("1001",  "1001 - Round Corner"),
        ("1001B", "1001B - Beveled Edge"),
        ("1003",  "1003 - Square Corner"),
    ])
    options(conn, f3, "size", [
        ("3.5x15", "3-1/2\" x 15\""),
        ("4x16",   "4\" x 16\""),
        ("6x16",   "6\" x 16\""),
    ])
    options(conn, f3, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Don-Jo
# ═════════════════════════════════════════════════════════════════════

def _seed_donjo(conn):
    # ── Door Wraps ──
    f = fid(conn, "Don-Jo", "Door Wrap",
            "Door Wrap / Reinforcer",
            "{model} {finish}",
            "Don-Jo {model} {finish}")

    slot(conn, f, 1, "model",   "Model",           1)
    slot(conn, f, 2, "finish",  "Finish",           1)
    slot(conn, f, 3, "handing", "Handing",          0)

    models = [
        ("504-CW", "504-CW - Full Mortise Wrap-Around, 4-1/4\" x 9\""),
        ("514-CW", "514-CW - Full Mortise Wrap-Around, 4-3/4\" x 9\""),
        ("80-CW",  "80-CW - Cylindrical Lock Wrap-Around, 4-1/4\" x 9\""),
        ("81-CW",  "81-CW - Cylindrical Lock Wrap-Around, 4-3/4\" x 12\""),
        ("4-CW",   "4-CW - Deadbolt Wrap-Around"),
        ("13-CW",  "13-CW - Latch/Lock Combo Wrap-Around"),
    ]
    options(conn, f, "model", models)

    finishes = [
        ("630",  "630 - Satin Stainless"),
        ("628",  "628 - Satin Aluminum"),
        ("612",  "612 - Satin Bronze"),
        ("605",  "605 - Polished Brass"),
        ("613",  "613 - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "handing", [("LH","Left Hand"),("RH","Right Hand")])

    # ── Latch Guards ──
    f2 = fid(conn, "Don-Jo", "Latch Guard / Protector",
             "Latch Guard",
             "{model} {finish}",
             "Don-Jo {model} {finish}")

    slot(conn, f2, 1, "model",  "Model",    1)
    slot(conn, f2, 2, "finish", "Finish",   1)

    guards = [
        ("LP-107",  "LP-107 - Latch Protector, 7\" Outswing"),
        ("LP-110",  "LP-110 - Latch Protector, 10\" Outswing"),
        ("LP-207",  "LP-207 - Latch Protector, 7\" Inswing"),
        ("LP-210",  "LP-210 - Latch Protector, 10\" Inswing"),
        ("PLP-111", "PLP-111 - Pin Latch Protector"),
    ]
    options(conn, f2, "model", guards)
    options(conn, f2, "finish", finishes)

    # ── Kick / Protection Plates ──
    f3 = fid(conn, "Don-Jo", "Protection Plate",
             "Protection Plate",
             "K-{height}x{width} {finish}",
             "Don-Jo Kick Plate {height} x {width} {finish}")

    slot(conn, f3, 1, "height", "Height",   1)
    slot(conn, f3, 2, "width",  "Width",    1)
    slot(conn, f3, 3, "finish", "Finish",   1)
    slot(conn, f3, 4, "corner", "Corners",  1)

    options(conn, f3, "height", [("6","6\""),("8","8\""),("10","10\""),("12","12\"")])
    options(conn, f3, "width", [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),("42","42\""),
    ])
    options(conn, f3, "finish", finishes)
    options(conn, f3, "corner", [("SQ","Square"),("RD","Rounded"),("BV","Beveled")])
