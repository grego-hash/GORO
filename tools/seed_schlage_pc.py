"""Seed Schlage PC Series cylindrical lock data.

Schlage PC Series — cylindrical lever lock.
Part number: PC{function} {lever} {finish}
"""

from seed_helpers import fid, slot, options, rule, conflict_all, price, price_bulk


def seed(conn):
    _seed_pc(conn)
    print("  Schlage PC Series seeded.")


def _seed_pc(conn):
    f = fid(conn,
            "Schlage",
            "PC Series Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever} {finish}",
            "Schlage PC Series {function} {lever} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "finish",        "Finish",         1)

    # ── Functions ──
    functions = [
        ("PC10",  "PC10 - Passage"),
        ("PC40",  "PC40 - Privacy"),
        ("PC170", "PC170 - Single Dummy Trim"),
        ("PC172", "PC172 - Double Dummy Trim"),
        ("PC50",  "PC50 - Entrance/Office"),
        ("PC53",  "PC53 - Entrance"),
        ("PC70",  "PC70 - Classroom"),
        ("PC80",  "PC80 - Storeroom"),
    ]
    options(conn, f, "function", functions)

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

    # Non-keyed → hide cylinder
    non_keyed = {"PC10", "PC40", "PC170", "PC172"}
    for fv in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", fv, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Levers ──
    options(conn, f, "lever", [
        ("ATH", "ATH - Athens"),
        ("BRK", "BRK - Boardwalk"),
        ("BRW", "BRW - Broadway"),
        ("LAT", "LAT - Latitude"),
        ("LON", "LON - Longitude"),
        ("RHO", "RHO - Rhodes"),
        ("SPA", "SPA - Sparta"),
        ("TLR", "TLR - Tubular"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("613",  "613 - Oil Rubbed Bronze"),
        ("619",  "619 - Satin Nickel"),
        ("622",  "622 - Flat Black"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
        ("643e", "643e - Aged Bronze"),
    ])

    # ==============================================================
    # PRICING — Schlage PC Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 622/626 finish
    price_bulk(conn, f, "function", [
        ("PC10",  447.00),
        ("PC40",  504.00),
        ("PC170", 192.00),
        ("PC172", 294.00),
        ("PC50",  670.00),
        ("PC53",  670.00),
        ("PC70",  670.00),
        ("PC80",  670.00),
    ], price_type="base")

    # Finish adders (relative to 622/626)
    price_bulk(conn, f, "finish", [
        ("622",    0.00),
        ("626",    0.00),
        ("613",   12.00),
        ("619",   12.00),
        ("625",   12.00),
        ("643e",  12.00),
    ], price_type="adder")

    # Cylinder type adders (single cylinder, open keyway)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",    0.00),
        ("P",     0.00),
        ("Z",    34.00),
        ("L",  -103.00),
        ("R",    50.00),
        ("T",    50.00),
        ("M",    84.00),
        ("J",   -66.00),
        ("G",    69.00),
        ("H",    33.00),
        ("BDC", -66.00),
        ("B",   -66.00),
    ], price_type="adder")
