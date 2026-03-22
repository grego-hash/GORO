"""Seed hinges and pivots — McKinney, Ives, ABH."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_mckinney(conn)
    _seed_ives_hinges(conn)
    _seed_abh(conn)
    print("  McKinney + Ives Hinges + ABH seeded.")


# ═════════════════════════════════════════════════════════════════════
# McKinney Hinges
# ═════════════════════════════════════════════════════════════════════

def _seed_mckinney(conn):
    # ── Full Mortise Butt Hinge (TA Series) ──
    f = fid(conn, "McKinney", "TA Full Mortise Butt Hinge",
            "Hinge",
            "TA{weight}{size} {finish}",
            "McKinney TA{weight}{size} {finish}")

    slot(conn, f, 1, "weight",    "Weight Class",     1)
    slot(conn, f, 2, "size",      "Size",             1)
    slot(conn, f, 3, "finish",    "Finish",           1)
    slot(conn, f, 4, "nrp",       "NRP (Non-Removable Pin)", 0)
    slot(conn, f, 5, "corners",   "Corner Type",      1)
    slot(conn, f, 6, "bearing",   "Bearing Type",     0)

    weights = [
        ("2714", "2714 - Standard Weight (.123 gauge)"),
        ("2314", "2314 - Heavy Weight (.180 gauge)"),
    ]
    options(conn, f, "weight", weights)

    hinge_sizes = [
        ("3.5x3.5", "3-1/2\" x 3-1/2\""),
        ("4x4",     "4\" x 4\""),
        ("4.5x4",   "4-1/2\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
        ("5x4.5",   "5\" x 4-1/2\""),
        ("5x5",     "5\" x 5\""),
    ]
    options(conn, f, "size", hinge_sizes)

    hinge_finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless Steel"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US4",  "US4 - Satin Brass"),
        ("US26", "US26 - Polished Chrome"),
        ("P",    "P - Primed for Paint"),
    ]
    options(conn, f, "finish", hinge_finishes)

    options(conn, f, "nrp", [("NO","No"),("NRP","NRP - Non-Removable Pin")])
    options(conn, f, "corners", [("SQ","Square"),("RAD","5/8\" Radius")])
    options(conn, f, "bearing", [("NONE","Plain Bearing"),("BB","Ball Bearing")])

    # ── Swing Clear Hinge ──
    f2 = fid(conn, "McKinney", "Swing Clear Hinge",
             "Hinge",
             "T4A{weight}{size} {finish}",
             "McKinney T4A{weight}{size} Swing Clear {finish}")

    slot(conn, f2, 1, "weight",  "Weight Class",  1)
    slot(conn, f2, 2, "size",    "Size",           1)
    slot(conn, f2, 3, "finish",  "Finish",         1)

    options(conn, f2, "weight", weights)
    options(conn, f2, "size", [
        ("4.5x4",   "4-1/2\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
        ("5x5",     "5\" x 5\""),
    ])
    options(conn, f2, "finish", hinge_finishes)

    # ── Continuous Geared Hinge ──
    f3 = fid(conn, "McKinney", "MCK Continuous Geared Hinge",
             "Continuous Hinge",
             "MCK-{model} {length} {finish}",
             "McKinney Continuous Geared {model} {length} {finish}")

    slot(conn, f3, 1, "model",   "Model / Application", 1)
    slot(conn, f3, 2, "length",  "Length",               1)
    slot(conn, f3, 3, "finish",  "Finish",               1)

    cont_models = [
        ("FG",  "Full Surface, Geared"),
        ("HG",  "Half Surface, Geared"),
        ("FS",  "Full Mortise, Geared"),
        ("HM",  "Half Mortise, Geared"),
    ]
    options(conn, f3, "model", cont_models)

    options(conn, f3, "length", [
        ("79", "79\" (6'-7\")"),
        ("83", "83\" (6'-11\")"),
        ("85", "85\" (7'-1\")"),
        ("95", "95\" (7'-11\")"),
    ])
    options(conn, f3, "finish", [
        ("CL",   "CL - Clear Anodized"),
        ("DU",   "DU - Dark Bronze Anodized"),
        ("BK",   "BK - Black Anodized"),
    ])

    # ── Electric Hinge (ETW) ──
    f4 = fid(conn, "McKinney", "ElectroLynx Electric Hinge",
             "Electric Hinge",
             "TA{weight}{size}-E {wires} {finish}",
             "McKinney TA{weight}{size}-E {wires} {finish}")

    slot(conn, f4, 1, "weight", "Weight Class",   1)
    slot(conn, f4, 2, "size",   "Size",            1)
    slot(conn, f4, 3, "wires",  "Wire Count",      1)
    slot(conn, f4, 4, "finish", "Finish",          1)

    options(conn, f4, "weight", weights)
    options(conn, f4, "size", [
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
        ("5x4.5",   "5\" x 4-1/2\""),
        ("5x5",     "5\" x 5\""),
    ])
    options(conn, f4, "wires", [
        ("4W","4 Wire"),("6W","6 Wire"),("8W","8 Wire"),
        ("12W","12 Wire"),
    ])
    options(conn, f4, "finish", hinge_finishes)


# ═════════════════════════════════════════════════════════════════════
# Ives Hinges / Pivots
# ═════════════════════════════════════════════════════════════════════

def _seed_ives_hinges(conn):
    # ── 5BB Full Mortise Butt Hinge ──
    f = fid(conn, "Ives", "5BB Full Mortise Ball Bearing Hinge",
            "Hinge",
            "5BB1{size} {finish}",
            "Ives 5BB1{size} {finish}")

    slot(conn, f, 1, "size",    "Size",              1)
    slot(conn, f, 2, "finish",  "Finish",            1)
    slot(conn, f, 3, "nrp",     "NRP",               0)
    slot(conn, f, 4, "corners", "Corner Type",       1)

    sizes = [
        ("3.5x3.5", "3-1/2\" x 3-1/2\""),
        ("4x4",     "4\" x 4\""),
        ("4.5x4",   "4-1/2\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
        ("5x4.5",   "5\" x 4-1/2\""),
        ("5x5",     "5\" x 5\""),
    ]
    options(conn, f, "size", sizes)

    ives_finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless Steel"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US4",  "US4 - Satin Brass"),
        ("P",    "P - Primed for Paint"),
    ]
    options(conn, f, "finish", ives_finishes)

    options(conn, f, "nrp", [("NO","No"),("NRP","NRP - Non-Removable Pin")])
    options(conn, f, "corners", [("SQ","Square"),("RAD","5/8\" Radius")])

    # ── Ives Pivots ──
    f2 = fid(conn, "Ives", "7200 Series Pivot",
             "Pivot",
             "7255 {finish}",
             "Ives 7255 {finish}")

    slot(conn, f2, 1, "model",   "Model",    1)
    slot(conn, f2, 2, "finish",  "Finish",   1)
    slot(conn, f2, 3, "handing", "Handing",  1)

    options(conn, f2, "model", [
        ("7200",  "7200 - Offset Pivot Set, Surface Mount"),
        ("7215",  "7215 - Offset Pivot Set, Intermediate"),
        ("7236",  "7236 - Offset Pivot Set, Floor Plate"),
        ("7255",  "7255 - Center Hung Pivot Set"),
    ])
    options(conn, f2, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US28", "US28 - Satin Aluminum"),
        ("US32D","US32D - Satin Stainless"),
    ])
    options(conn, f2, "handing", [("LH","Left Hand"),("RH","Right Hand")])

    # ── Ives Continuous Hinge ──
    f3 = fid(conn, "Ives", "Continuous Geared Hinge",
             "Continuous Hinge",
             "{model} {length} {finish}",
             "Ives Continuous Geared {model} {length} {finish}")

    slot(conn, f3, 1, "model",  "Model / Mounting",  1)
    slot(conn, f3, 2, "length", "Length",             1)
    slot(conn, f3, 3, "finish", "Finish",             1)

    options(conn, f3, "model", [
        ("224HD",  "224HD - Full Surface"),
        ("224XY",  "224XY - Full Mortise"),
        ("112HD",  "112HD - Half Surface"),
        ("112XY",  "112XY - Half Mortise"),
    ])
    options(conn, f3, "length", [
        ("79","79\" (6'-7\")"),("83","83\" (6'-11\")"),
        ("85","85\" (7'-1\")"),("95","95\" (7'-11\")"),
    ])
    options(conn, f3, "finish", [
        ("CL","CL - Clear Anodized"),
        ("DU","DU - Dark Bronze Anodized"),
        ("BK","BK - Black Anodized"),
    ])


# ═════════════════════════════════════════════════════════════════════
# ABH Pivots / Hospital Hardware
# ═════════════════════════════════════════════════════════════════════

def _seed_abh(conn):
    # ── Center Hung Pivot ──
    f = fid(conn, "ABH", "Pivot Set",
            "Pivot",
            "{model} {finish}",
            "ABH {model} {finish}")

    slot(conn, f, 1, "model",   "Model",    1)
    slot(conn, f, 2, "finish",  "Finish",   1)
    slot(conn, f, 3, "handing", "Handing",  1)

    models = [
        ("0117",  "0117 - Center Hung Pivot Set"),
        ("0117-T","0117-T - Center Hung Pivot Set, Transom"),
        ("0127",  "0127 - Offset Pivot Set"),
        ("A110",  "A110 - Intermediate Pivot"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US28", "US28 - Satin Aluminum"),
    ])
    options(conn, f, "handing", [("LH","Left Hand"),("RH","Right Hand")])

    # ── Hospital Tip (Ligature Resistant) ──
    f2 = fid(conn, "ABH", "Hospital / Behavioral Health Hinge",
             "Hospital Hinge",
             "{model} {size} {finish}",
             "ABH {model} {size} {finish}")

    slot(conn, f2, 1, "model",  "Model",     1)
    slot(conn, f2, 2, "size",   "Size",      1)
    slot(conn, f2, 3, "finish", "Finish",    1)

    hosp_models = [
        ("A500",   "A500 - Ligature Resistant, Full Mortise"),
        ("A500HD", "A500HD - Ligature Resistant, Heavy Duty"),
        ("A501",   "A501 - Ligature Resistant, Half Surface"),
    ]
    options(conn, f2, "model", hosp_models)

    options(conn, f2, "size", [
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
        ("5x4.5",   "5\" x 4-1/2\""),
        ("5x5",     "5\" x 5\""),
    ])
    options(conn, f2, "finish", [
        ("US32D","US32D - Satin Stainless Steel"),
        ("US26D","US26D - Satin Chrome"),
    ])

    # ── Continuous Hinges ──
    f3 = fid(conn, "ABH", "Continuous Geared Hinge",
             "Continuous Hinge",
             "A110{model} {length} {finish}",
             "ABH Continuous Geared {model} {length} {finish}")

    slot(conn, f3, 1, "model",  "Mounting Type",  1)
    slot(conn, f3, 2, "length", "Length",          1)
    slot(conn, f3, 3, "finish", "Finish",          1)

    options(conn, f3, "model", [
        ("FM",  "FM - Full Mortise"),
        ("FS",  "FS - Full Surface"),
        ("HM",  "HM - Half Mortise"),
        ("HS",  "HS - Half Surface"),
    ])
    options(conn, f3, "length", [
        ("79","79\" (6'-7\")"),("83","83\" (6'-11\")"),
        ("85","85\" (7'-1\")"),("95","95\" (7'-11\")"),
    ])
    options(conn, f3, "finish", [
        ("CL","CL - Clear Anodized"),
        ("DU","DU - Dark Bronze Anodized"),
        ("BK","BK - Black Anodized"),
    ])
