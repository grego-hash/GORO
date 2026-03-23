"""Seed Schlage S Series cylindrical lock data.

Schlage S Series — cylindrical healthcare lever lock.
Part number: S{function} {lever} {finish}
"""

from seed_helpers import fid, slot, options, rule, conflict_all, price, price_bulk


def seed(conn):
    _seed_s(conn)
    print("  Schlage S Series seeded.")


def _seed_s(conn):
    f = fid(conn,
            "Schlage",
            "S Series Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever} {finish}",
            "Schlage S Series {function} {lever} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "finish",        "Finish",         1)

    # ── Functions ──
    functions = [
        ("S10",  "S10 - Passage"),
        ("S40",  "S40 - Privacy"),
        ("S170", "S170 - Single Dummy Trim"),
        ("S51",  "S51 - Entrance"),
        ("S70",  "S70 - Classroom"),
        ("S80",  "S80 - Storeroom"),
    ]
    options(conn, f, "function", functions)

    # ── Cylinder Type ──
    cylinder_types = [
        ("P6", "P6 - Conventional 6-Pin"),
        ("P",  "P - Conventional 5-Pin"),
        ("Z",  "Z - Everest SL 7-Pin"),
        ("L",  "L - Less Conventional Cylinder"),
        ("R",  "R - FSIC"),
        ("T",  "T - FSIC Construction Core"),
        ("M",  "M - Everest SL FSIC 7-Pin"),
        ("J",  "J - Less FSIC"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # Non-keyed → hide cylinder
    non_keyed = {"S10", "S40", "S170"}
    for fv in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", fv, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Levers ──
    options(conn, f, "lever", [
        ("FLA", "FLA - Flair"),
        ("JUP", "JUP - Jupiter"),
        ("NEP", "NEP - Neptune"),
        ("SAT", "SAT - Saturn"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("606",  "606 - Satin Brass"),
        ("609",  "609 - Antique Brass"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("619",  "619 - Satin Nickel"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
    ])

    # ==============================================================
    # PRICING — Schlage S Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 626 finish
    price_bulk(conn, f, "function", [
        ("S10",  356.00),
        ("S40",  439.00),
        ("S170", 166.00),
        ("S51",  557.00),
        ("S70",  557.00),
        ("S80",  557.00),
    ], price_type="base")

    # Finish adders (relative to 626)
    price_bulk(conn, f, "finish", [
        ("626",    0.00),
        ("605",   12.00),
        ("606",   12.00),
        ("609",   12.00),
        ("619",   12.00),
        ("625",   12.00),
        ("613",   30.00),
    ], price_type="adder")

    # Cylinder type adders
    price_bulk(conn, f, "cylinder_type", [
        ("P6",    0.00),
        ("P",     0.00),
        ("Z",    34.00),
        ("L",  -103.00),
        ("R",    50.00),
        ("T",    50.00),
        ("M",    84.00),
        ("J",   -66.00),
    ], price_type="adder")
