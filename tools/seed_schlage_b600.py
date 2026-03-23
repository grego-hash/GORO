"""Seed Schlage B600 Series deadbolt data.

Schlage B600 Series — Grade 1 deadbolt.
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk


def seed(conn):
    _seed_b600(conn)
    print("  Schlage B600 Series seeded.")


def _seed_b600(conn):
    f = fid(conn,
            "Schlage",
            "B600 Series Deadbolt",
            "Deadbolt",
            "{function} {cylinder_type} {finish}",
            "Schlage B600 Series {function} {cylinder_type} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "finish",        "Finish",         1)

    # ── Functions ──
    functions_all = [
        # Keyless
        ("B672", "B672 - Door Bolt with Coin Turn"),
        ("B680", "B680 - Door Bolt"),
        # Single cylinder
        ("B660", "B660 - Single Cyl Deadbolt"),
        ("B661", "B661 - Cyl x Blank Plate Deadbolt"),
        ("B663", "B663 - Classroom Deadbolt"),
        ("B664", "B664 - Cylinder Only Deadbolt"),
        # Double cylinder
        ("B662", "B662 - Double Cyl Deadbolt"),
    ]
    options(conn, f, "function", functions_all)

    # ── Cylinder Type ──
    cylinder_types = [
        ("P6",  "P6 - Conventional 6-Pin"),
        ("P",   "P - Conventional 5-Pin"),
        ("Z",   "Z - Everest SL 7-Pin"),
        ("L",   "L - Less Conventional Cylinder"),
        ("R",   "R - FSIC"),
        ("T",   "T - FSIC Construction Core"),
        ("M",   "M - Everest SL FSIC 7-Pin"),
        ("J",   "J - Less FSIC"),
        ("G",   "G - SFIC 7-Pin"),
        ("H",   "H - Refundable Construction SFIC"),
        ("BDC", "BDC - Disposable Construction SFIC"),
        ("B",   "B - Less SFIC"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # Keyless → hide cylinder
    keyless = {"B672", "B680"}
    for fv in keyless:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", fv, "cylinder_type", ct[0],
                 "No cylinder for keyless function")

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",   "605 - Bright Brass"),
        ("606",   "606 - Satin Brass"),
        ("609",   "609 - Antique Brass"),
        ("612",   "612 - Satin Bronze"),
        ("613",   "613 - Oil Rubbed Bronze"),
        ("619",   "619 - Satin Nickel"),
        ("622",   "622 - Flat Black"),
        ("625",   "625 - Bright Chrome"),
        ("626",   "626 - Satin Chrome"),
        ("626AM", "626AM - Antimicrobial Satin Chrome"),
        ("643e",  "643e - Aged Bronze"),
    ])

    # ==============================================================
    # PRICING — Schlage B600 Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 626 finish
    price_bulk(conn, f, "function", [
        ("B672", 322.00),
        ("B680", 260.00),
        ("B660", 336.00),
        ("B661", 336.00),
        ("B662", 429.00),
        ("B663", 349.00),
        ("B664", 333.00),
    ], price_type="base")

    # Finish adders (relative to 626)
    # B600: 626 base, 605-643e = -6, 613 = +10, 626AM = +42
    # But B672/B680 door bolts have different structure: 626→base, 605-643e=-3, 613=-5
    # Using weighted average based on main deadbolt functions
    price_bulk(conn, f, "finish", [
        ("626",     0.00),
        ("605",    -6.00),
        ("606",    -6.00),
        ("609",    -6.00),
        ("612",    -6.00),
        ("619",    -6.00),
        ("622",    -6.00),
        ("625",    -6.00),
        ("643e",   -6.00),
        ("613",    10.00),
        ("626AM",  42.00),
    ], price_type="adder")

    # Cylinder type adders (single cylinder, open keyway)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",    0.00),
        ("P",     0.00),
        ("Z",    34.00),
        ("L",   -80.00),
        ("R",    47.00),
        ("T",    47.00),
        ("M",    81.00),
        ("J",   -69.00),
        ("G",   135.00),
        ("H",    70.00),
        ("BDC",   0.00),
        ("B",     0.00),
    ], price_type="adder")
