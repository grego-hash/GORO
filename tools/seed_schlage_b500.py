"""Seed Schlage B500 Series deadbolt data.

Schlage B500 Series — Grade 2 deadbolt.
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk


def seed(conn):
    _seed_b500(conn)
    print("  Schlage B500 Series seeded.")


def _seed_b500(conn):
    f = fid(conn,
            "Schlage",
            "B500 Series Deadbolt",
            "Deadbolt",
            "{function} {cylinder_type} {finish}",
            "Schlage B500 Series {function} {cylinder_type} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "finish",        "Finish",         1)

    # ── Functions ──
    functions_all = [
        # Keyless (non-keyed)
        ("B572",   "B572 - Door Bolt with Coin Turn"),
        ("B572F",  "B572F - UL Door Bolt with Coin Turn"),
        ("B580",   "B580 - Door Bolt"),
        ("B580F",  "B580F - UL Door Bolt"),
        ("B581",   "B581 - Door Bolt with Trim"),
        ("B581F",  "B581F - UL Door Bolt with Trim"),
        # Single cylinder
        ("B560",   "B560 - Single Cyl Deadbolt"),
        ("B560F",  "B560F - UL Single Cyl Deadbolt"),
        ("B561",   "B561 - Cyl x Blank Plate Deadbolt"),
        ("B561F",  "B561F - UL Cyl x Blank Plate Deadbolt"),
        ("B563",   "B563 - Classroom Deadbolt"),
        ("B563F",  "B563F - UL Classroom Deadbolt"),
        # Double cylinder
        ("B562",   "B562 - Double Cyl Deadbolt"),
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

    # Keyless (door bolts) → hide cylinder
    keyless = {"B572", "B572F", "B580", "B580F", "B581", "B581F"}
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
    # PRICING — Schlage B500 Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 626 finish (tier 2)
    price_bulk(conn, f, "function", [
        ("B572",   131.00),
        ("B572F",  142.00),
        ("B580",   112.00),
        ("B580F",  123.00),
        ("B581",   112.00),
        ("B581F",  123.00),
        ("B560",   142.00),
        ("B560F",  153.00),
        ("B561",   142.00),
        ("B561F",  153.00),
        ("B563",   151.00),
        ("B563F",  162.00),
        ("B562",   190.00),
    ], price_type="base")

    # Finish adders (relative to 626)
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
        ("626AM",  50.00),
    ], price_type="adder")

    # Cylinder type adders (single cylinder, open keyway)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",    0.00),
        ("P",     0.00),
        ("Z",    34.00),
        ("L",   -23.00),
        ("R",   190.00),
        ("T",   190.00),
        ("M",   224.00),
        ("J",    57.00),
        ("G",   146.00),
        ("H",   182.00),
        ("BDC",  57.00),
        ("B",    57.00),
    ], price_type="adder")
