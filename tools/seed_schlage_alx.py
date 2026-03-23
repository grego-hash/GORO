"""Seed Schlage ALX Series cylindrical lock data.

Schlage ALX Series — Grade 2 cylindrical (bored) lockset.
Part number: ALX{function} {lever} {finish}

6-column pricing: Standard levers × 3 finish tiers + Premium levers × 3 finish tiers.
Premium levers (LON, OME) add +$22 across all functions.
Base reference = 626 finish + standard lever.
Finish adders: tier1 (605-643e) = -$12, tier3 (613/626AM) = +$18.
"""

from seed_helpers import fid, slot, options, rule, conflict_all, price, price_bulk


def seed(conn):
    _seed_alx(conn)
    print("  Schlage ALX Series seeded.")


def _seed_alx(conn):
    f = fid(conn,
            "Schlage",
            "ALX Series Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever} {finish}",
            "Schlage ALX Series {function} {lever} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "finish",        "Finish",         1)

    # ── Functions ──
    functions = [
        # Non-keyed
        ("ALX10",   "ALX10 - Passage"),
        ("ALX40",   "ALX40 - Privacy / Bath"),
        ("ALXV40",  "ALXV40 - Vandlgard Privacy"),
        ("ALX44",   "ALX44 - Hospital Privacy"),
        ("ALXV44",  "ALXV44 - Vandlgard Hospital Privacy"),
        ("ALX170",  "ALX170 - Single Dummy Trim"),
        ("ALX172",  "ALX172 - Double Dummy Trim"),
        # Keyed
        ("ALX25",   "ALX25 - Exit Lock (blank × lever)"),
        ("ALX50",   "ALX50 - Entry / Office"),
        ("ALXV50",  "ALXV50 - Vandlgard Entry / Office"),
        ("ALX53",   "ALX53 - Entrance"),
        ("ALXV53",  "ALXV53 - Vandlgard Entrance"),
        ("ALX70",   "ALX70 - Classroom"),
        ("ALXV70",  "ALXV70 - Vandlgard Classroom"),
        ("ALX80",   "ALX80 - Storeroom"),
        ("ALXV80",  "ALXV80 - Vandlgard Storeroom"),
    ]
    options(conn, f, "function", functions)

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

    # Non-keyed → hide cylinder
    non_keyed = {"ALX10", "ALX40", "ALXV40", "ALX44", "ALXV44", "ALX170", "ALX172"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Lever Designs ──
    options(conn, f, "lever", [
        # Standard levers (tier 1-3 pricing columns 1-3)
        ("ATH", "ATH - Athens"),
        ("BRW", "BRW - Broadway"),
        ("BRK", "BRK - Brookshire"),
        ("LAT", "LAT - Latitude"),
        ("SAT", "SAT - Saturn"),
        ("RHO", "RHO - Rhodes"),
        ("SPA", "SPA - Sparta"),
        ("TLR", "TLR - Tubular Return"),
        # Premium levers (+$22 adder)
        ("LON", "LON - Longitude"),
        ("OME", "OME - Omega"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("606",  "606 - Satin Brass"),
        ("612",  "612 - Satin Bronze"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("619",  "619 - Satin Nickel"),
        ("622",  "622 - Flat Black"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
        ("626AM","626AM - Antimicrobial Satin Chrome"),
        ("643e", "643e - Aged Bronze"),
    ])

    # ==============================================================
    # PRICING — Schlage ALX Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base at 626 finish + standard lever
    _function_base_prices = [
        ("ALX10",   307.00),
        ("ALX40",   346.00),
        ("ALXV40",  346.00),
        ("ALX44",   346.00),
        ("ALXV44",  346.00),
        ("ALX170",  190.00),
        ("ALX172",  288.00),
        ("ALX25",   263.00),
        ("ALX50",   428.00),
        ("ALXV50",  428.00),
        ("ALX53",   428.00),
        ("ALXV53",  428.00),
        ("ALX70",   428.00),
        ("ALXV70",  428.00),
        ("ALX80",   428.00),
        ("ALXV80",  428.00),
    ]
    price_bulk(conn, f, "function", _function_base_prices, price_type="base")

    # Finish adders (relative to 626 base)
    # tier1 (605-643e) = -$12, tier2 (626)=0, tier3 (613/626AM) = +$18
    price_bulk(conn, f, "finish", [
        ("626",    0.00),
        ("605",  -12.00),
        ("606",  -12.00),
        ("612",  -12.00),
        ("619",  -12.00),
        ("622",  -12.00),
        ("625",  -12.00),
        ("643e", -12.00),
        ("613",   18.00),
        ("626AM", 18.00),
    ], price_type="adder")

    # Premium lever adder (LON, OME = +$22 vs standard levers)
    price_bulk(conn, f, "lever", [
        ("ATH",  0.00),
        ("BRW",  0.00),
        ("BRK",  0.00),
        ("LAT",  0.00),
        ("SAT",  0.00),
        ("RHO",  0.00),
        ("SPA",  0.00),
        ("TLR",  0.00),
        ("LON", 22.00),
        ("OME", 22.00),
    ], price_type="adder")

    # Cylinder adders (open keyway)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",   0.00),
        ("P",    0.00),
        ("Z",   34.00),
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
