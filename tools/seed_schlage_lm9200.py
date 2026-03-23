"""Seed Schlage LM9200 Series electrified mortise lock data.

Schlage LM9200 — large format mortise lock (electrified).
Complex structure with:
  - Rose Trim vs Escutcheon Trim
  - Non-fire-rated (no suffix) / Fire-rated wood (F suffix) / Hollow metal (M suffix)
  - Standard levers vs M Collection levers (+adder)
  - Multiple finish tiers

Pricing model:
  Base at 626 finish, Rose Trim, Non-fire-rated, Standard lever.
  Adders: finish, trim (Esc vs Rose), fire-rating, M Collection lever.
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk


def seed(conn):
    _seed_lm9200(conn)
    print("  Schlage LM9200 Series seeded.")


def _seed_lm9200(conn):
    f = fid(conn,
            "Schlage",
            "LM9200 Series Electrified Mortise Lock",
            "Mortise Lockset",
            "{function} {fire_rating} {lever} {rose} {finish}",
            "Schlage LM9200 {function} {fire_rating} {lever}{rose} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",        1)
    slot(conn, f, 2, "fire_rating",   "Fire Rating",     1)
    slot(conn, f, 3, "cylinder_type", "Cylinder Type",    0)
    slot(conn, f, 4, "lever",         "Lever Design",     1)
    slot(conn, f, 5, "rose",          "Rose / Trim",      1)
    slot(conn, f, 6, "finish",        "Finish",           1)

    # ── Functions ──
    options(conn, f, "function", [
        ("LM9210",  "LM9210 - Passage"),
        ("LM9225",  "LM9225 - Exit Lock"),
        ("LM9250",  "LM9250 - Office / Entry"),
        ("LM9256",  "LM9256 - Corridor"),
        ("LM9270",  "LM9270 - Classroom"),
        ("LM9280",  "LM9280 - Storeroom"),
        ("LM9271",  "LM9271 - Classroom Security"),
    ])

    # ── Fire Rating ──
    options(conn, f, "fire_rating", [
        ("STD",  "Standard (Non-Fire-Rated)"),
        ("F",    "F - Fire-Rated (Wood Door)"),
        ("M",    "M - Fire-Rated (Hollow Metal)"),
    ])

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

    # ── Lever Design ──
    options(conn, f, "lever", [
        # Standard levers
        ("ATH", "ATH - Athens"),
        ("AST", "AST - Astoria"),
        ("BRW", "BRW - Broadway"),
        ("LAT", "LAT - Latitude"),
        ("LON", "LON - Longitude"),
        ("MER", "MER - Merano"),
        ("RHO", "RHO - Rhodes"),
        ("SPA", "SPA - Sparta"),
        ("TLR", "TLR - Tubular Return"),
        # M Collection (premium)
        ("M51", "M51 - M Collection Lever"),
        ("M52", "M52 - M Collection Lever"),
        ("M53", "M53 - M Collection Lever"),
        ("M54", "M54 - M Collection Lever"),
        ("M55", "M55 - M Collection Lever"),
        ("M56", "M56 - M Collection Lever"),
        ("M57", "M57 - M Collection Lever"),
        ("M61", "M61 - M Collection Lever"),
        ("M62", "M62 - M Collection Lever"),
        ("M63", "M63 - M Collection Lever"),
    ])

    # ── Rose / Trim ──
    options(conn, f, "rose", [
        ("A", "A - Rose Trim"),
        ("B", "B - Rose Trim"),
        ("C", "C - Rose Trim"),
        ("N", "N - Escutcheon Trim"),
        ("L", "L - Escutcheon Trim"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("606",  "606 - Satin Brass"),
        ("609",  "609 - Antique Brass"),
        ("612",  "612 - Satin Bronze"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("619",  "619 - Satin Nickel"),
        ("622",  "622 - Flat Black"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
        ("629",  "629 - Bright Stainless"),
        ("630",  "630 - Satin Stainless"),
        ("643e", "643e - Aged Bronze"),
    ])

    # ==============================================================
    # PRICING — Schlage LM9200 Price Book (effective 2/27/26)
    # ==============================================================
    # Base at 626, Rose Trim, Non-fire-rated, Standard lever
    price_bulk(conn, f, "function", [
        ("LM9210",  4963.00),
        ("LM9225",  4751.00),
        ("LM9250",  5280.00),
        ("LM9256",  5415.00),
        ("LM9270",  5280.00),
        ("LM9280",  5280.00),
        ("LM9271",  5426.00),
    ], price_type="base")

    # Finish adders (relative to 626)
    # Rose Trim: tier1 (605-643e) = +$122, tier2 (626)=0, prem (613/629/630)=+$140
    # We use Rose Trim finish diffs as base; Esc correction below.
    price_bulk(conn, f, "finish", [
        ("626",    0.00),
        ("605",  122.00),
        ("606",  122.00),
        ("609",  122.00),
        ("612",  122.00),
        ("619",  122.00),
        ("622",  122.00),
        ("625",  122.00),
        ("643e", 122.00),
        ("613",  140.00),
        ("629",  140.00),
        ("630",  140.00),
    ], price_type="adder")

    # Rose/Trim adder: Escutcheon adds +$139 vs Rose at 626
    price_bulk(conn, f, "rose", [
        ("A",   0.00),
        ("B",   0.00),
        ("C",   0.00),
        ("N", 139.00),
        ("L", 139.00),
    ], price_type="adder")

    # Compound correction: Escutcheon + non-626 finishes
    # Escutcheon finish diff is only +$12 std / +$30 prem (vs Rose +$122/+$140).
    # Correction = actual_esc_diff - rose_diff => -$110 for all non-626
    esc_finish_corrections = []
    for esc_rose in ("N", "L"):
        for fin in ("605", "606", "609", "612", "619", "622", "625", "643e"):
            esc_finish_corrections.append((f"{esc_rose}:{fin}", -110.00))
        for fin in ("613", "629", "630"):
            esc_finish_corrections.append((f"{esc_rose}:{fin}", -110.00))
    price_bulk(conn, f, "rose:finish", esc_finish_corrections, price_type="adder")

    # Fire-rating adder (F or M suffix adds ~$233 for most functions)
    # LM9210F=$5196 vs LM9210=$4963 → +$233
    # LM9250F=$5513 vs LM9250=$5280 → +$233
    price_bulk(conn, f, "fire_rating", [
        ("STD",  0.00),
        ("F",  233.00),
        ("M",  233.00),
    ], price_type="adder")

    # M Collection lever adder
    # M Collection lever pricing is higher; from pricebook ~+$350-450 range.
    # Using average difference from standard lever prices.
    m_collection_adder = 400.00
    m_levers = ["M51", "M52", "M53", "M54", "M55", "M56", "M57", "M61", "M62", "M63"]
    std_levers = ["ATH", "AST", "BRW", "LAT", "LON", "MER", "RHO", "SPA", "TLR"]
    lever_adders = [(lev, 0.00) for lev in std_levers]
    lever_adders += [(lev, m_collection_adder) for lev in m_levers]
    price_bulk(conn, f, "lever", lever_adders, price_type="adder")

    # Cylinder adders (same as L/PM series — open keyway)
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
