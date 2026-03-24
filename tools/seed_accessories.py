"""Seed accessories — Ives (door accessories), Hager (hinges), Pemko (seals)."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    # Ives accessories now seeded via seed_ives_pricebook.py (Batch 9)
    _seed_hager_hinges(conn)
    _seed_pemko(conn)
    print("  Hager + Pemko seeded.")


# ═════════════════════════════════════════════════════════════════════
# Ives Door Accessories
# ═════════════════════════════════════════════════════════════════════

def _seed_ives(conn):
    # ── Wall Stops / Floor Stops ──
    f = fid(conn,
            "Ives",
            "Door Stops & Holders",
            "Door Accessory",
            "{product_type} {finish}",
            "Ives {product_type} {finish}")

    slot(conn, f, 1, "product_type", "Product Type",  1)
    slot(conn, f, 2, "finish",       "Finish",        1)

    products = [
        ("WS401",  "WS401 - Wall Stop, Concave, Rubber Bumper"),
        ("WS402",  "WS402 - Wall Stop, Convex, Rubber Bumper"),
        ("WS406",  "WS406 - Wall Stop, Dome"),
        ("WS407",  "WS407 - Wall Stop, Dome (Heavy Duty)"),
        ("FS436",  "FS436 - Floor Stop, Dome, Heavy Duty"),
        ("FS438",  "FS438 - Floor Stop, Universal, Heavy Duty"),
        ("FS439",  "FS439 - Floor Stop, Dome (Cast)"),
        ("RL30",   "RL30 - Roller Latch"),
        ("RL32",   "RL32 - Roller Latch (Heavy Duty)"),
        ("WS44",   "WS44 - Wall Stop & Holder, Magnetic"),
        ("WS45",   "WS45 - Wall Stop & Holder, Rigid"),
        ("FS441",  "FS441 - Floor Stop, Low Profile"),
        ("?"   ,   "Other — Specify in Notes"),
    ]
    options(conn, f, "product_type", products)

    finishes = [
        ("US3",   "US3 - Bright Brass"),
        ("US4",   "US4 - Satin Brass"),
        ("US10B", "US10B - Oil Rubbed Bronze"),
        ("US26",  "US26 - Bright Chrome"),
        ("US26D", "US26D - Satin Chrome"),
        ("US32D", "US32D - Satin Stainless Steel"),
        ("US15",  "US15 - Satin Nickel"),
        ("USP",   "USP - Primed for Paint"),
    ]
    options(conn, f, "finish", finishes)

    # ── Coordinators ──
    f2 = fid(conn,
             "Ives",
             "Door Coordinators",
             "Door Accessory",
             "{coordinator} {size} {finish}",
             "Ives {coordinator} {size} {finish}")

    slot(conn, f2, 1, "coordinator", "Coordinator",  1)
    slot(conn, f2, 2, "size",        "Size",         1)
    slot(conn, f2, 3, "finish",      "Finish",       1)

    coordinators = [
        ("COR50",  "COR50 - Standard Series Coordinator"),
        ("COR60",  "COR60 - Heavy-Duty Coordinator"),
        ("COR65",  "COR65 - Heavy-Duty (Wide Frame)"),
        ("COR70",  "COR70 - Extra Heavy-Duty Coordinator"),
    ]
    options(conn, f2, "coordinator", coordinators)

    sizes = [
        ("5FT",   "5' (60\")"),
        ("6FT",   "6' (72\")"),
        ("8FT",   "8' (96\")"),
        ("10FT",  "10' (120\")"),
    ]
    options(conn, f2, "size", sizes)

    coord_finishes = [
        ("US28",  "US28 - Satin Aluminum"),
        ("SP28",  "SP28 - Sprayed Aluminum"),
        ("DU",    "DU - Dark Bronze"),
        ("SP313", "SP313 - Sprayed Dark Bronze"),
        ("US32D", "US32D - Satin Stainless Steel"),
        ("US3",   "US3 - Polished Brass"),
    ]
    options(conn, f2, "finish", coord_finishes)

    # ── Silencers / Bumpers ──
    f3 = fid(conn,
             "Ives",
             "Door Silencers",
             "Door Accessory",
             "{silencer}",
             "Ives {silencer}")

    slot(conn, f3, 1, "silencer",  "Silencer Type",  1)

    silencers = [
        ("SR64",   "SR64 - Screw-In Silencer (Metal Door)"),
        ("SR65",   "SR65 - Drive-In Silencer (Wood Door)"),
        ("FB61T",  "FB61T - Flat Bumper"),
        ("SR66",   "SR66 - Screw-In Silencer (Extra Quiet)"),
        ("FB60",   "FB60 - Round Bumper (Self-Adhesive)"),
    ]
    options(conn, f3, "silencer", silencers)


# ═════════════════════════════════════════════════════════════════════
# Hager Hinges
# ═════════════════════════════════════════════════════════════════════

def _seed_hager_hinges(conn):
    # ── Butt / Mortise Hinges ──
    f = fid(conn,
            "Hager",
            "Full Mortise Butt Hinge",
            "Hinge",
            "{hinge_type} {size} {finish}",
            "Hager {hinge_type} {size} {finish}")

    slot(conn, f, 1, "hinge_type",  "Hinge Model",   1)
    slot(conn, f, 2, "size",        "Size",           1)
    slot(conn, f, 3, "finish",      "Finish",         1)
    slot(conn, f, 4, "corners",     "Corners",        0)
    slot(conn, f, 5, "nrp",         "Non-Removable Pin", 0)
    slot(conn, f, 6, "etw",         "Electric Through-Wire (ETW)", 0)

    hinges = [
        ("BB1168",  "BB1168 - Full Mortise, 5-Knuckle, Ball Bearing (Standard Weight)"),
        ("BB1279",  "BB1279 - Full Mortise, 5-Knuckle, Ball Bearing (Heavy Weight)"),
        ("BB1191",  "BB1191 - Full Mortise, 5-Knuckle, Ball Bearing (Concealed)"),
        ("RC1842",  "RC1842 - Full Mortise, 5-Knuckle, Ball Bearing (Residential)"),
        ("1250",    "1250 - Full Mortise, 5-Knuckle, Plain Bearing"),
        ("1279",    "1279 - Full Mortise, 5-Knuckle, Plain Bearing (Heavy)"),
        ("BB1199",  "BB1199 - Full Mortise, 5-Knuckle, Ball Bearing (Architectural)"),
        ("WT1279",  "WT1279 - Full Mortise, 5-Knuckle, Heavy Weight (Wide Throw)"),
    ]
    options(conn, f, "hinge_type", hinges)

    sizes = [
        ("3.5x3.5", "3-1/2\" x 3-1/2\""),
        ("4x4",     "4\" x 4\""),
        ("4.5x4",   "4-1/2\" x 4\""),
        ("4.5x4.5", "4-1/2\" x 4-1/2\""),
        ("5x4.5",   "5\" x 4-1/2\""),
        ("5x5",     "5\" x 5\""),
    ]
    options(conn, f, "size", sizes)

    finishes = [
        ("US3",   "US3 - Bright Brass"),
        ("US4",   "US4 - Satin Brass"),
        ("US10B", "US10B - Oil Rubbed Bronze"),
        ("US15",  "US15 - Satin Nickel"),
        ("US26",  "US26 - Bright Chrome"),
        ("US26D", "US26D - Satin Chrome"),
        ("US32D", "US32D - Satin Stainless Steel"),
        ("USP",   "USP - Prime Coat (Paint Grade)"),
    ]
    options(conn, f, "finish", finishes)

    corners = [
        ("SQ", "Square Corners"),
        ("R",  "5/8\" Radius Corners"),
    ]
    options(conn, f, "corners", corners)

    nrp = [
        ("STD", "Standard (Removable Pin)"),
        ("NRP", "NRP - Non-Removable Pin"),
    ]
    options(conn, f, "nrp", nrp)

    etw = [
        ("NONE", "None (Standard Hinge)"),
        ("4W",   "ETW - 4 Wire"),
        ("8W",   "ETW - 8 Wire"),
        ("12W",  "ETW - 12 Wire"),
    ]
    options(conn, f, "etw", etw)

    # ── Swing Clear Hinges ──
    f2 = fid(conn,
             "Hager",
             "Swing Clear Hinge",
             "Hinge",
             "{hinge_type} {size} {finish}",
             "Hager {hinge_type} {size} {finish}")

    slot(conn, f2, 1, "hinge_type", "Hinge Model",  1)
    slot(conn, f2, 2, "size",       "Size",          1)
    slot(conn, f2, 3, "finish",     "Finish",        1)

    sc_hinges = [
        ("1260",   "1260 - Swing Clear, Full Mortise, Plain Bearing"),
        ("BB1260", "BB1260 - Swing Clear, Full Mortise, Ball Bearing"),
    ]
    options(conn, f2, "hinge_type", sc_hinges)
    options(conn, f2, "size", sizes)
    options(conn, f2, "finish", finishes)

    # ── Continuous (Piano) Hinges ──
    f3 = fid(conn,
             "Hager",
             "Continuous Geared Hinge",
             "Hinge",
             "{hinge_type} {size} {finish}",
             "Hager {hinge_type} {size} {finish}")

    slot(conn, f3, 1, "hinge_type", "Hinge Type",  1)
    slot(conn, f3, 2, "size",       "Door Height",  1)
    slot(conn, f3, 3, "finish",     "Finish",       1)

    cont_hinges = [
        ("780-110", "780-110 - Concealed Leaf, Full Surface"),
        ("780-112", "780-112 - Concealed Leaf, Half Surface"),
        ("780-224", "780-224 - Heavy-Duty Full Surface"),
        ("780-157", "780-157 - Full Mortise, Concealed Leaf"),
        ("780-210", "780-210 - Full Surface, Wide Throw"),
    ]
    options(conn, f3, "hinge_type", cont_hinges)

    cont_sizes = [
        ("79",   "79\" (6'-7\")"),
        ("83",   "83\" (6'-11\")"),
        ("84",   "84\" (7'-0\")"),
        ("95",   "95\" (7'-11\")"),
        ("96",   "96\" (8'-0\")"),
        ("119",  "119\" (9'-11\")"),
        ("120",  "120\" (10'-0\")"),
    ]
    options(conn, f3, "size", cont_sizes)

    cont_finishes = [
        ("CLR",   "CLR - Clear Anodized"),
        ("DKB",   "DKB - Dark Bronze Anodized"),
        ("BLK",   "BLK - Black Anodized"),
        ("USP",   "USP - Prime Coat"),
        ("SS",    "SS - Stainless Steel"),
        ("GLD",   "GLD - Gold Anodized"),
    ]
    options(conn, f3, "finish", cont_finishes)


# ═════════════════════════════════════════════════════════════════════
# Pemko Thresholds, Gasketing & Sweeps
# ═════════════════════════════════════════════════════════════════════

def _seed_pemko(conn):
    # ── Thresholds ──
    f = fid(conn,
            "Pemko",
            "Threshold",
            "Threshold / Seal",
            "{threshold_type} {size} {finish}",
            "Pemko {threshold_type} {size} {finish}")

    slot(conn, f, 1, "threshold_type", "Threshold Type",  1)
    slot(conn, f, 2, "size",           "Width / Length",   1)
    slot(conn, f, 3, "finish",         "Finish",          1)

    thresholds = [
        ("170A",  "170A - Saddle Threshold, Mill Finish"),
        ("171A",  "171A - Saddle Threshold, 1/4\" Rise"),
        ("271A",  "271A - Saddle Threshold, 1/2\" Rise"),
        ("272A",  "272A - Saddle Threshold, Fluted Top"),
        ("150B",  "150B - Bumper Threshold, Rubber Insert"),
        ("152B",  "152B - Bumper Threshold, 1/2\" Height"),
        ("44850", "44850 - ADA Compliant, Offset Saddle"),
        ("171DT", "171DT - Thermal Break Saddle Threshold"),
        ("270A",  "270A - Saddle Threshold, Flat Top"),
        ("172A",  "172A - Saddle Threshold, 3/8\" Rise"),
    ]
    options(conn, f, "threshold_type", thresholds)

    sizes = [
        ("3FT",  "36\""),
        ("4FT",  "48\""),
        ("5FT",  "60\""),
        ("6FT",  "72\""),
        ("8FT",  "96\""),
    ]
    options(conn, f, "size", sizes)

    finishes = [
        ("AL",  "AL - Mill Aluminum"),
        ("DK",  "DK - Dark Bronze Anodized"),
        ("BL",  "BL - Black Anodized"),
        ("SS",  "SS - Stainless Steel"),
        ("PB",  "PB - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    # ── Door Sweeps / Bottom Seals ──
    f2 = fid(conn,
             "Pemko",
             "Door Sweep / Bottom Seal",
             "Threshold / Seal",
             "{sweep_type} {size}",
             "Pemko {sweep_type} {size}")

    slot(conn, f2, 1, "sweep_type",  "Sweep Type",    1)
    slot(conn, f2, 2, "size",        "Door Width",    1)

    sweeps = [
        ("18061",  "18061 - Surface-Mount Brush Sweep"),
        ("18100",  "18100 - Surface-Mount Neoprene Sweep"),
        ("18200",  "18200 - Surface-Mount Vinyl Sweep"),
        ("315CN",  "315CN - Auto Door Bottom (Mortised)"),
        ("320CN",  "320CN - Auto Door Bottom (Surface)"),
        ("411ARK", "411ARK - Acoustic Automatic Seal"),
        ("345CNB", "345CNB - Automatic Door Bottom (Heavy Duty)"),
        ("18062",  "18062 - Surface-Mount Brush Sweep (Heavy Duty)"),
        ("18063",  "18063 - Surface-Mount Brush Sweep (Extra Long)"),
    ]
    options(conn, f2, "sweep_type", sweeps)
    options(conn, f2, "size", sizes)

    # ── Perimeter Gasketing ──
    f3 = fid(conn,
             "Pemko",
             "Perimeter Gasketing",
             "Threshold / Seal",
             "{gasket_type} {size}",
             "Pemko {gasket_type} {size}")

    slot(conn, f3, 1, "gasket_type", "Gasket Type",    1)
    slot(conn, f3, 2, "size",        "Length",          1)

    gaskets = [
        ("S44D",   "S44D - Silicone Smoke Seal"),
        ("S773",   "S773 - Surface-Mount Smoke Seal (Adhesive)"),
        ("303AS",  "303AS - Kerf-In Silicone Seal"),
        ("2848",   "2848 - Surface-Mount Pile Weatherstrip"),
        ("S88D",   "S88D - Smoke & Sound Seal (High Performance)"),
        ("319AS",  "319AS - Kerf-In Neoprene Seal"),
        ("S767",   "S767 - Adhesive Smoke Seal (Intumescent)"),
    ]
    options(conn, f3, "gasket_type", gaskets)

    gasket_sizes = [
        ("3FT",  "36\""),
        ("7FT",  "84\""),
        ("8FT",  "96\""),
        ("17FT", "204\" (3-Piece Door Kit)"),
        ("20FT", "240\" (Roll)"),
    ]
    options(conn, f3, "size", gasket_sizes)
