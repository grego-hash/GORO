"""Seed Schlage PM Series mortise lock data.

Schlage PM Series — mortise lock (residential/commercial).
Part number: PM{function} {lever}{rose} {finish}

Pricing: base at 622/626 Rose Trim + simple finish adder + escutcheon adder.
Escutcheon (N) = Rose base + $29 (flat across all functions).
Finish tier 2 (613/619/625/643e) = +$12.
"""

from seed_helpers import fid, slot, options, rule, conflict_all, price, price_bulk


def seed(conn):
    _seed_pm(conn)
    print("  Schlage PM Series seeded.")


def _seed_pm(conn):
    f = fid(conn,
            "Schlage",
            "PM Series Mortise Lock",
            "Mortise Lockset",
            "{function} {lever}{rose} {finish}",
            "Schlage PM Series {function} {lever}{rose} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose / Trim",    1)
    slot(conn, f, 5, "finish",        "Finish",         1)

    # ── Functions ──
    functions = [
        # Non-keyed
        ("PM010",  "PM010 - Passage"),
        ("PM040",  "PM040 - Privacy / Bath"),
        ("PM044",  "PM044 - Hospital Privacy"),
        # Keyed single cylinder (P6 included)
        ("PM440",  "PM440 - Privacy / Bath Deadbolt"),
        ("PM444",  "PM444 - Hospital Privacy Deadbolt"),
        ("PM050",  "PM050 - Office / Entry"),
        ("PM056",  "PM056 - Corridor"),
        ("PM080",  "PM080 - Storeroom"),
        ("PM060",  "PM060 - Apartment / Vestibule"),
        ("PM071",  "PM071 - Classroom Security"),
        ("PM453",  "PM453 - Entrance Deadbolt"),
        ("PM456",  "PM456 - Corridor Deadbolt"),
        ("PM480",  "PM480 - Storeroom Deadbolt"),
        ("PM485",  "PM485 - Faculty Restroom"),
        ("PM457",  "PM457 - Dormitory Exit Deadbolt"),
        # Deadbolt-only functions (single trim)
        ("PM460",  "PM460 - Single Cylinder Deadbolt"),
        ("PM462",  "PM462 - Double Cylinder Deadbolt"),
        ("PM463",  "PM463 - Classroom Deadbolt"),
        ("PM464",  "PM464 - Deadbolt Turnpce Only"),
    ]
    options(conn, f, "function", functions)

    # ── Cylinder Type ──
    cylinder_types = [
        ("P6",  "P6 - Conventional 6-Pin"),
        ("L",   "L - Less Conventional Cylinder"),
        ("R",   "R - FSIC"),
        ("T",   "T - FSIC Construction Core"),
        ("J",   "J - Less FSIC"),
        ("G",   "G - SFIC 7-Pin"),
        ("H",   "H - Refundable Construction SFIC"),
        ("BDC", "BDC - Disposable Construction SFIC"),
        ("B",   "B - Less SFIC"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # Non-keyed → hide cylinder
    non_keyed = {"PM010", "PM040", "PM044"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Lever Designs ──
    options(conn, f, "lever", [
        ("ATH", "ATH - Athens"),
        ("PLA", "PLA - Plata"),
        ("BRW", "BRW - Broadway"),
        ("RHO", "RHO - Rhodes"),
        ("LAT", "LAT - Latitude"),
        ("SEL", "SEL - Select"),
        ("LON", "LON - Longitude"),
        ("TLR", "TLR - Tubular Return"),
        ("NEP", "NEP - Neptune"),
        ("TWO", "TWO - Two-Piece"),
    ])

    # ── Rose / Trim ──
    options(conn, f, "rose", [
        ("A", "A - Rose Trim"),
        ("C", "C - Rose Trim"),
        ("D", "D - Rose Trim"),
        ("N", "N - Escutcheon Trim"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("622",  "622 - Flat Black"),
        ("626",  "626 - Satin Chrome"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("619",  "619 - Satin Nickel"),
        ("625",  "625 - Bright Chrome"),
        ("643e", "643e - Aged Bronze"),
    ])

    # ==============================================================
    # PRICING — Schlage PM Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 622/626 finish, Rose Trim
    price_bulk(conn, f, "function", [
        ("PM010",   616.00),
        ("PM040",   788.00),
        ("PM044",   929.00),
        ("PM440",   983.00),
        ("PM444",  1120.00),
        ("PM050",   935.00),
        ("PM056",  1070.00),
        ("PM080",   935.00),
        ("PM060",  1286.00),
        ("PM071",  1080.00),
        ("PM453",   983.00),
        ("PM456",   983.00),
        ("PM480",  1442.00),
        ("PM485",  1240.00),
        ("PM457",  1440.00),
        # Deadbolt-only
        ("PM460",   388.00),
        ("PM462",   563.00),
        ("PM463",   563.00),
        ("PM464",   287.00),
    ], price_type="base")

    # Finish adders (relative to 622/626 base)
    price_bulk(conn, f, "finish", [
        ("622",   0.00),
        ("626",   0.00),
        ("613",  12.00),
        ("619",  12.00),
        ("625",  12.00),
        ("643e", 12.00),
    ], price_type="adder")

    # Rose/Trim adder: Escutcheon adds +$29, Rose = $0
    price_bulk(conn, f, "rose", [
        ("A",  0.00),
        ("C",  0.00),
        ("D",  0.00),
        ("N", 29.00),
    ], price_type="adder")

    # Cylinder adders (open keyway)
    price_bulk(conn, f, "cylinder_type", [
        ("P6",    0.00),
        ("L",  -130.00),
        ("R",   116.00),
        ("T",   116.00),
        ("J",     0.00),
        ("G",   151.00),
        ("H",    70.00),
        ("BDC", -18.00),
        ("B",   -23.00),
    ], price_type="adder")
