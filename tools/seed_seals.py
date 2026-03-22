"""Seed fire/smoke seals and perimeter seals — NGP, Zero International."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_ngp(conn)
    _seed_zero(conn)
    print("  NGP + Zero International seeded.")


# ═════════════════════════════════════════════════════════════════════
# NGP  (National Guard Products)
# ═════════════════════════════════════════════════════════════════════

def _seed_ngp(conn):
    # ── Fire/Smoke Gasketing (Door Frame) ──
    f = fid(conn, "NGP", "Fire/Smoke Seal",
            "Door Seal / Gasketing",
            "{model} {length}",
            "NGP {model} Fire/Smoke Seal {length}")

    slot(conn, f, 1, "model",   "Model",        1)
    slot(conn, f, 2, "length",  "Length",        1)
    slot(conn, f, 3, "finish",  "Finish / Color",0)

    models = [
        ("100N",    "100N - Silicone Smoke Seal (Head & Jamb)"),
        ("150SA",   "150SA - Adjustable Perimeter Seal"),
        ("200N",    "200N - Neoprene Smoke Seal"),
        ("250SA",   "250SA - Self-Adhesive Perimeter Seal"),
        ("9600",    "9600 - Meeting Stile Seal (Pairs)"),
        ("9700",    "9700 - Meeting Stile Astragal"),
    ]
    options(conn, f, "model", models)

    lengths = [
        ("36",  "36\" (3'-0\")"),
        ("42",  "42\" (3'-6\")"),
        ("48",  "48\" (4'-0\")"),
        ("79",  "79\" (6'-7\")"),
        ("83",  "83\" (6'-11\")"),
        ("85",  "85\" (7'-1\")"),
        ("96",  "96\" (8'-0\")"),
    ]
    options(conn, f, "length", lengths)

    options(conn, f, "finish", [
        ("BK",  "Black"),
        ("BR",  "Brown"),
        ("GR",  "Grey"),
        ("WH",  "White"),
    ])

    # ── Door Bottoms / Sweeps ──
    f2 = fid(conn, "NGP", "Door Bottom / Automatic Seal",
             "Door Bottom / Sweep",
             "{model} {width}",
             "NGP {model} {width}")

    slot(conn, f2, 1, "model",  "Model",        1)
    slot(conn, f2, 2, "width",  "Door Width",   1)
    slot(conn, f2, 3, "finish", "Finish",        0)

    bottoms = [
        ("8100",   "8100 - Automatic Door Bottom (Surface)"),
        ("8200",   "8200 - Automatic Door Bottom (Mortise)"),
        ("110NA",  "110NA - Neoprene/Aluminum Sweep"),
        ("6050",   "6050 - Surface-Applied Rain Drip"),
        ("15A",    "15A - Aluminum/Vinyl Sweep"),
        ("170NA",  "170NA - Heavy Duty Neoprene Sweep"),
    ]
    options(conn, f2, "model", bottoms)

    widths = [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),("42","42\""),("48","48\""),
    ]
    options(conn, f2, "width", widths)

    options(conn, f2, "finish", [
        ("AL",  "Aluminum"),
        ("DBA", "Dark Bronze Anodized"),
        ("BK",  "Black"),
    ])

    # ── Thresholds ──
    f3 = fid(conn, "NGP", "Threshold",
             "Threshold",
             "{model} {width} {finish}",
             "NGP {model} Threshold {width} {finish}")

    slot(conn, f3, 1, "model",  "Model / Profile", 1)
    slot(conn, f3, 2, "width",  "Door Width",       1)
    slot(conn, f3, 3, "finish", "Finish",            1)

    thresholds = [
        ("896N",  "896N - Saddle Threshold, 1/2\" High"),
        ("896A",  "896A - ADA Saddle Threshold, 1/4\" High"),
        ("897N",  "897N - Heavy Duty Saddle, 1/2\" High"),
        ("5050A", "5050A - Thermal Break Threshold"),
        ("515",   "515 - Bumper Threshold"),
    ]
    options(conn, f3, "model", thresholds)
    options(conn, f3, "width", widths)
    options(conn, f3, "finish", [
        ("AL","Aluminum"),("AB","Architectural Bronze"),("DB","Dark Bronze"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Zero International
# ═════════════════════════════════════════════════════════════════════

def _seed_zero(conn):
    # ── Intumescent Seal ──
    f = fid(conn, "Zero International", "Intumescent Fire/Smoke Seal",
            "Door Seal / Gasketing",
            "{model} {length}",
            "Zero Intl {model} Fire/Smoke Seal {length}")

    slot(conn, f, 1, "model",   "Model",          1)
    slot(conn, f, 2, "length",  "Length",          1)
    slot(conn, f, 3, "backing", "Backing Type",    0)

    int_models = [
        ("IF100","IF100 - Intumescent Fire Seal (1/16\" x 1/2\")"),
        ("IF200","IF200 - Intumescent Fire Seal (1/8\" x 1/2\")"),
        ("IF300","IF300 - Intumescent Fire Seal (1/8\" x 3/4\")"),
        ("IF400","IF400 - Intumescent Fire Seal (1/8\" x 1\")"),
        ("IF500","IF500 - Intumescent Wrap Strip"),
    ]
    options(conn, f, "model", int_models)

    lengths = [
        ("79", "79\" (6'-7\")"),
        ("83", "83\" (6'-11\")"),
        ("85", "85\" (7'-1\")"),
        ("96", "96\" (8'-0\")"),
    ]
    options(conn, f, "length", lengths)

    options(conn, f, "backing", [
        ("PSA","PSA - Pressure-Sensitive Adhesive"),
        ("NONE","None (Friction Fit)"),
    ])

    # ── Perimeter Gasketing ──
    f2 = fid(conn, "Zero International", "Perimeter Gasket",
             "Door Seal / Gasketing",
             "{model} {length}",
             "Zero Intl {model} Perimeter Gasket {length}")

    slot(conn, f2, 1, "model",  "Model",    1)
    slot(conn, f2, 2, "length", "Length",    1)

    gaskets = [
        ("50A",  "50A - Adjustable Perimeter Seal, Aluminum"),
        ("50N",  "50N - Adjustable Perimeter Seal, Neoprene"),
        ("30A",  "30A - Surface-Applied Seal"),
        ("68A",  "68A - Smoke & Sound Seal"),
        ("87A",  "87A - Magnetic Gasket"),
    ]
    options(conn, f2, "model", gaskets)
    options(conn, f2, "length", lengths)

    # ── Door Bottoms ──
    f3 = fid(conn, "Zero International", "Door Bottom / Automatic Seal",
             "Door Bottom / Sweep",
             "{model} {width}",
             "Zero Intl {model} Door Bottom {width}")

    slot(conn, f3, 1, "model",  "Model",        1)
    slot(conn, f3, 2, "width",  "Door Width",   1)
    slot(conn, f3, 3, "finish", "Finish",        0)

    zdb_models = [
        ("369AA", "369AA - Automatic Door Bottom (Surface)"),
        ("379AA", "379AA - Automatic Door Bottom (Semi-Mortise)"),
        ("889AA", "889AA - Heavy-Duty Automatic Door Bottom"),
        ("29A",   "29A - Neoprene/Aluminum Door Sweep"),
    ]
    options(conn, f3, "model", zdb_models)

    widths = [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),("42","42\""),("48","48\""),
    ]
    options(conn, f3, "width", widths)
    options(conn, f3, "finish", [
        ("AL","Aluminum"),("DBA","Dark Bronze Anodized"),("BK","Black"),
    ])
