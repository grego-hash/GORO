"""Seed Pemko extended (kickplates, astragals), Reese Enterprises, National Guard Products."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_pemko_ext(conn)
    _seed_reese(conn)
    _seed_national_guard(conn)
    print("  Pemko (ext) + Reese + National Guard seeded.")


# ═════════════════════════════════════════════════════════════════════
# Pemko – Kick Plates, Astragals, Coordinators
# ═════════════════════════════════════════════════════════════════════

def _seed_pemko_ext(conn):
    # ── Kick / Mop / Armor Plates ──
    f = fid(conn, "Pemko", "Kick / Mop / Armor Plate",
            "Door Protection",
            "{type} {width}x{height} {finish}",
            "Pemko {type} {width}x{height} {finish}")

    slot(conn, f, 1, "type",   "Plate Type", 1)
    slot(conn, f, 2, "width",  "Width",      1)
    slot(conn, f, 3, "height", "Height",     1)
    slot(conn, f, 4, "finish", "Finish",     1)

    options(conn, f, "type", [
        ("KP","Kick Plate"),
        ("MP","Mop Plate"),
        ("AP","Armor Plate"),
        ("SP","Stretch Plate"),
    ])

    options(conn, f, "width", [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),
    ])

    options(conn, f, "height", [
        ("8","8\""),("10","10\""),("12","12\""),
        ("16","16\""),("34","34\""),("42","42\""),
    ])

    options(conn, f, "finish", [
        ("630","630 - Satin Stainless"),
        ("652","652 - Satin Aluminum"),
        ("613","613 - Oil Rubbed Bronze"),
    ])

    # ── Astragals ──
    f2 = fid(conn, "Pemko", "Astragal",
             "Astragal",
             "{model} {length} {finish}",
             "Pemko {model} Astragal {length} {finish}")

    slot(conn, f2, 1, "model",  "Model",  1)
    slot(conn, f2, 2, "length", "Length", 1)
    slot(conn, f2, 3, "finish", "Finish", 1)

    options(conn, f2, "model", [
        ("352","352 - Overlapping T-Astragal"),
        ("357","357 - Meeting Stile Astragal"),
        ("399","399 - Fire-Rated Astragal"),
        ("553","553 - Split Astragal (Adjustable)"),
    ])

    options(conn, f2, "length", [
        ("79","79\""),("83","83\""),("85","85\""),("95","95\""),
    ])

    options(conn, f2, "finish", [
        ("AL","AL - Mill Aluminum"),
        ("CLR","CLR - Clear Anodized"),
        ("DK","DK - Dark Bronze Anodized"),
        ("SS","SS - Stainless Steel"),
    ])

    # ── Coordinators ──
    f3 = fid(conn, "Pemko", "Door Coordinator",
             "Coordinator",
             "CR {width} {finish}",
             "Pemko CR Door Coordinator {width} {finish}")

    slot(conn, f3, 1, "width",  "Width",  1)
    slot(conn, f3, 2, "finish", "Finish", 1)

    options(conn, f3, "width", [
        ("22","22\" (pair of 2'0\")"),
        ("28","28\" (pair of 2'6\")"),
        ("32","32\" (pair of 2'8\")"),
        ("36","36\" (pair of 3'0\")"),
        ("44","44\" (pair of 3'8\")"),
    ])

    options(conn, f3, "finish", [
        ("AL","AL - Aluminum"),
        ("DU","DU - Dark Bronze"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Reese Enterprises – Door Bottoms & Thresholds
# ═════════════════════════════════════════════════════════════════════

def _seed_reese(conn):
    f = fid(conn, "Reese Enterprises", "Door Bottom Sweep / Seal",
            "Seal / Sweep",
            "{model} {length}",
            "Reese {model} Door Bottom {length}")

    slot(conn, f, 1, "model",  "Model",  1)
    slot(conn, f, 2, "length", "Length", 1)

    options(conn, f, "model", [
        ("77","77 - Drip Cap / Rain Deflector"),
        ("R-15","R-15 - Automatic Door Bottom"),
        ("R-28","R-28 - Surface Mounted Sweep"),
        ("R-50","R-50 - Neoprene Sweep"),
    ])

    options(conn, f, "length", [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),("42","42\""),
    ])

    # ── Reese Threshold ──
    f2 = fid(conn, "Reese Enterprises", "Threshold",
             "Threshold",
             "{model} {width} {finish}",
             "Reese {model} Threshold {width} {finish}")

    slot(conn, f2, 1, "model",  "Profile",  1)
    slot(conn, f2, 2, "width",  "Width",    1)
    slot(conn, f2, 3, "finish", "Finish",   1)

    options(conn, f2, "model", [
        ("T-50","T-50 - Saddle Threshold"),
        ("T-66","T-66 - ADA Compliant Ramp"),
        ("T-90","T-90 - Heavy Duty Commercial"),
    ])

    options(conn, f2, "width", [
        ("28","28\""),("30","30\""),("32","32\""),
        ("36","36\""),("42","42\""),("48","48\""),
    ])

    options(conn, f2, "finish", [
        ("AL","AL - Mill Aluminum"),
        ("AB","AB - Anodized Bronze"),
        ("SS","SS - Stainless Steel"),
    ])


# ═════════════════════════════════════════════════════════════════════
# National Guard Products – Fire / Smoke / Sound Seals
# ═════════════════════════════════════════════════════════════════════

def _seed_national_guard(conn):
    # ── NGP-equivalent fire/smoke seals ──
    f = fid(conn, "National Guard Products", "Fire / Smoke Seal",
            "Seal / Gasket",
            "{model} {length}",
            "National Guard {model} {length}")

    slot(conn, f, 1, "model",  "Model",  1)
    slot(conn, f, 2, "length", "Length", 1)

    options(conn, f, "model", [
        ("4200","4200 - Silicone Fire/Smoke Gasket"),
        ("4300","4300 - Intumescent Fire Seal"),
        ("815V","815V - Surface Mount Gasket"),
        ("127NA","127NA - Concealed Perimeter Gasket"),
    ])

    options(conn, f, "length", [
        ("79","79\""),("83","83\""),("85","85\""),
        ("95","95\""),("17ft","17' (pair kit)"),
    ])

    # ── Sound Seal (STC rated) ──
    f2 = fid(conn, "National Guard Products", "Sound Seal / STC Gasket",
             "Sound Seal",
             "{model} {length}",
             "National Guard {model} Sound Seal {length}")

    slot(conn, f2, 1, "model",  "Model",  1)
    slot(conn, f2, 2, "length", "Length", 1)

    options(conn, f2, "model", [
        ("9500","9500 - Adjustable Perimeter Seal (STC43)"),
        ("9540","9540 - Automatic Door Bottom (STC45)"),
        ("9560","9560 - Surface Seal w/ Neoprene (STC40)"),
    ])

    options(conn, f2, "length", [
        ("36","36\""),("42","42\""),("48","48\""),
    ])
