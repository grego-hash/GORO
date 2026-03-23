"""Seed Schlage CS210 Series interconnect lock data.

Schlage CS210 — interconnect deadbolt + knob/lever.
"""

from seed_helpers import fid, slot, options, rule, conflict_all, price, price_bulk


def seed(conn):
    _seed_cs210(conn)
    print("  Schlage CS210 Series seeded.")


def _seed_cs210(conn):
    f = fid(conn,
            "Schlage",
            "CS210 Series Interconnect",
            "Interconnect Lockset",
            "{function} {lever} {finish}",
            "Schlage CS210 Series {function} {lever} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "finish",        "Finish",         1)

    # ── Functions ──
    options(conn, f, "function", [
        ("CS210-B60",  "CS210-B60 - Entrance, Residential Spin Ring"),
        ("CS210-B500", "CS210-B500 - Entrance, Commercial Spin Ring"),
    ])

    # ── Cylinder Type ──
    cylinder_types = [
        ("P6",  "P6 - Conventional 6-Pin"),
        ("P",   "P - Conventional 6-Pin (keyed 5)"),
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

    # ── Lever Designs ──
    options(conn, f, "lever", [
        ("ACC", "ACC - Accent"),
        ("AVA", "AVA - Avalon"),
        ("BRK", "BRK - Brookshire"),
        ("BRW", "BRW - Broadway"),
        ("CHP", "CHP - Champagne"),
        ("CLT", "CLT - Camelot"),
        ("ELA", "ELA - Elan"),
        ("FLA", "FLA - Flair"),
        ("JAZ", "JAZ - Jazz"),
        ("JUP", "JUP - Jupiter"),
        ("LAT", "LAT - Latitude"),
        ("LON", "LON - Longitude"),
        ("MER", "MER - Merano"),
        ("MNH", "MNH - Manhattan"),
        ("NEP", "NEP - Neptune"),
        ("SAT", "SAT - Saturn"),
        ("STA", "STA - St. Annes"),
        ("VLA", "VLA - Vilana"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("609",  "609 - Antique Brass"),
        ("619",  "619 - Satin Nickel"),
        ("622",  "622 - Flat Black"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
        ("643e", "643e - Aged Bronze"),
    ])

    # ==============================================================
    # PRICING — Schlage CS210 Price Book (effective 2/27/26)
    # ==============================================================
    # Base at 626 finish
    price_bulk(conn, f, "function", [
        ("CS210-B60",  672.00),
        ("CS210-B500", 672.00),
    ], price_type="base")

    # Finish adders (relative to 626 base)
    price_bulk(conn, f, "finish", [
        ("626",   0.00),
        ("605",  13.00),
        ("609",  13.00),
        ("619",  13.00),
        ("622",  13.00),
        ("625",  13.00),
        ("643e", 13.00),
    ], price_type="adder")

    # Cylinder adders (open keyway)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",   0.00),
        ("P",    0.00),
        ("Z",    34.00),
        ("L",  -103.00),
        ("R",    50.00),
        ("T",    50.00),
        ("M",    84.00),
        ("J",   -66.00),
        ("G",   135.00),
        ("H",    70.00),
        ("BDC",   0.00),
        ("B",     0.00),
    ], price_type="adder")
