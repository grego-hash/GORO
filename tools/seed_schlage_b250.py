"""Seed Schlage B250 Series deadlatch data.

Schlage B250 Series — deadlatch / night latch.
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk


def seed(conn):
    _seed_b250(conn)
    print("  Schlage B250 Series seeded.")


def _seed_b250(conn):
    f = fid(conn,
            "Schlage",
            "B250 Series Deadlatch",
            "Deadlatch",
            "{function} {cylinder_type} {finish}",
            "Schlage B250 Series {function} {cylinder_type} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  1)
    slot(conn, f, 3, "finish",        "Finish",         1)

    # ── Functions ──
    options(conn, f, "function", [
        ("B250", "B250 - Single Cylinder Deadlatch"),
        ("B252", "B252 - Double Cylinder Deadlatch"),
    ])

    # ── Cylinder Type ──
    cylinder_types = [
        ("P6", "P6 - Conventional 6-Pin"),
        ("P5", "P5 - Conventional 5-Pin"),
        ("Z",  "Z - Everest SL 7-Pin"),
        ("R",  "R - FSIC"),
        ("T",  "T - FSIC Construction Core"),
        ("M",  "M - Everest SL FSIC 7-Pin"),
        ("J",  "J - Less FSIC"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("606",  "606 - Satin Brass"),
        ("609",  "609 - Antique Brass"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("622",  "622 - Flat Black"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
    ])

    # ==============================================================
    # PRICING — Schlage B250 Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 605/606/626/622/625 tier
    price_bulk(conn, f, "function", [
        ("B250", 449.00),
        ("B252", 502.00),
    ], price_type="base")

    # Finish adders (relative to tier 1)
    price_bulk(conn, f, "finish", [
        ("605",    0.00),
        ("606",    0.00),
        ("622",    0.00),
        ("625",    0.00),
        ("626",    0.00),
        ("609",    6.00),
        ("613",   16.00),
    ], price_type="adder")

    # Cylinder type adders (single cylinder open keyway values)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",    0.00),
        ("P5",    0.00),
        ("Z",    34.00),
        ("R",    71.00),
        ("T",    71.00),
        ("M",   105.00),
        ("J",   -45.00),
    ], price_type="adder")
