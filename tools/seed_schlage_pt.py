"""Seed Schlage PT Series tubular lock data.

Schlage PT Series — tubular lever lock (non-keyed only).
Part number: PT{function} {lever} {rose} {finish}
"""

from seed_helpers import fid, slot, options, price, price_bulk


def seed(conn):
    _seed_pt(conn)
    print("  Schlage PT Series seeded.")


def _seed_pt(conn):
    f = fid(conn,
            "Schlage",
            "PT Series Tubular Lock",
            "Tubular Lockset",
            "{function} {lever} {rose} {finish}",
            "Schlage PT Series {function} {lever} {rose} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function", "Function",   1)
    slot(conn, f, 2, "lever",   "Lever Design", 1)
    slot(conn, f, 3, "rose",    "Rose",         1)
    slot(conn, f, 4, "finish",  "Finish",       1)

    # ── Functions (all non-keyed) ──
    options(conn, f, "function", [
        ("PT10",  "PT10 - Passage"),
        ("PT40",  "PT40 - Privacy"),
        ("PT170", "PT170 - Single Dummy Trim"),
        ("PT172", "PT172 - Double Dummy Trim"),
    ])

    # ── Levers ──
    options(conn, f, "lever", [
        ("ATH", "ATH - Athens"),
        ("BRW", "BRW - Broadway"),
        ("LAT", "LAT - Latitude"),
        ("LON", "LON - Longitude"),
        ("NEP", "NEP - Neptune"),
        ("PLA", "PLA - Playa"),
        ("RHO", "RHO - Rhodes"),
        ("SEL", "SEL - Selena"),
        ("TLR", "TLR - Tubular"),
        ("TWO", "TWO - Two"),
    ])

    # ── Roses ──
    options(conn, f, "rose", [
        ("A", "A - Round Rose"),
        ("C", "C - Square Rose"),
        ("D", "D - Decorative Rose"),
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
    # PRICING — Schlage PT Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices at 622/626 tier
    price_bulk(conn, f, "function", [
        ("PT10",  208.00),
        ("PT40",  230.00),
        ("PT170",  93.00),
        ("PT172", 186.00),
    ], price_type="base")

    # Finish adders (relative to 622/626 base)
    price_bulk(conn, f, "finish", [
        ("622",    0.00),
        ("626",    0.00),
        ("613",   12.00),
        ("619",   12.00),
        ("625",   12.00),
        ("643e",  12.00),
    ], price_type="adder")
