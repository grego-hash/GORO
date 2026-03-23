"""Seed Schlage HL Series hospital latch data.

Schlage HL Series — hospital push/pull latches.
Two sub-families:
  1) HL Tubular (bored) push/pull latch   — HL6, PL7, PL8
  2) HL Mortise push/pull latch            — HL6-9xxx
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk


def seed(conn):
    _seed_hl_tubular(conn)
    _seed_hl_mortise(conn)
    print("  Schlage HL Series seeded.")


# ─────────────────────────────────────────────────────────────────
# HL TUBULAR (BORED) PUSH/PULL LATCH
# ─────────────────────────────────────────────────────────────────

def _seed_hl_tubular(conn):
    f = fid(conn,
            "Schlage",
            "HL Series Tubular Hospital Latch",
            "Hospital Latch",
            "{function} {finish}",
            "Schlage HL Tubular {function} {finish}")

    slot(conn, f, 1, "function", "Function", 1)
    slot(conn, f, 2, "finish",   "Finish",   1)

    # ── Functions ──
    options(conn, f, "function", [
        # HL6 Push/Pull Latch (passage — non-keyed)
        ("HL6-2",  "HL6-2 - Push/Pull Latch 2-3/4\" BS"),
        ("HL6-3",  "HL6-3 - Push/Pull Latch 3-3/4\" BS"),
        ("HL6-5",  "HL6-5 - Push/Pull Latch 5\" BS"),
        ("HL6-7",  "HL6-7 - Push/Pull Latch 7\" BS"),
        # PL7 Privacy (push-side thumbturn)
        ("PL7-2",  "PL7-2 - Privacy Push-Side TT 2-3/4\" BS"),
        ("PL7-3",  "PL7-3 - Privacy Push-Side TT 3-3/4\" BS"),
        ("PL7-5",  "PL7-5 - Privacy Push-Side TT 5\" BS"),
        ("PL7-7",  "PL7-7 - Privacy Push-Side TT 7\" BS"),
        # PL8 Privacy (pull-side thumbturn)
        ("PL8-2",  "PL8-2 - Privacy Pull-Side TT 2-3/4\" BS"),
        ("PL8-3",  "PL8-3 - Privacy Pull-Side TT 3-3/4\" BS"),
        ("PL8-5",  "PL8-5 - Privacy Pull-Side TT 5\" BS"),
        ("PL8-7",  "PL8-7 - Privacy Pull-Side TT 7\" BS"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("606",  "606 - Satin Brass"),
        ("612",  "612 - Satin Bronze"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
        ("629",  "629 - Bright Stainless"),
        ("630",  "630 - Satin Stainless"),
    ])

    # ── Pricing ──
    # Base at 626
    price_bulk(conn, f, "function", [
        ("HL6-2",  573.00),
        ("HL6-3",  573.00),
        ("HL6-5",  573.00),
        ("HL6-7",  654.00),
        ("PL7-2",  747.00),
        ("PL7-3",  747.00),
        ("PL7-5",  747.00),
        ("PL7-7",  832.00),
        ("PL8-2",  747.00),
        ("PL8-3",  747.00),
        ("PL8-5",  747.00),
        ("PL8-7",  832.00),
    ], price_type="base")

    # Finish adders (relative to 626)
    # tier1 (626)=0, tier2 (605/606/612/625)=+$12, tier3 (613/629/630)=+$30
    price_bulk(conn, f, "finish", [
        ("626",   0.00),
        ("605",  12.00),
        ("606",  12.00),
        ("612",  12.00),
        ("625",  12.00),
        ("613",  30.00),
        ("629",  30.00),
        ("630",  30.00),
    ], price_type="adder")


# ─────────────────────────────────────────────────────────────────
# HL MORTISE PUSH/PULL LATCH
# ─────────────────────────────────────────────────────────────────

def _seed_hl_mortise(conn):
    f = fid(conn,
            "Schlage",
            "HL Series Mortise Hospital Latch",
            "Hospital Latch",
            "{function} {finish}",
            "Schlage HL Mortise {function} {finish}")

    slot(conn, f, 1, "function", "Function", 1)
    slot(conn, f, 2, "finish",   "Finish",   1)

    # ── Functions ──
    options(conn, f, "function", [
        ("HL6-9010",      "HL6-9010 - Passage"),
        ("HL6-9040",      "HL6-9040 - Privacy (thumbturn)"),
        ("HL6-9050",      "HL6-9050 - Office / Inner Entry (thumbturn)"),
        ("HL6-9060",      "HL6-9060 - Apartment Entrance"),
        ("HL6-9070",      "HL6-9070 - Classroom"),
        ("HL6-9080",      "HL6-9080 - Storeroom"),
        ("HL6-9082",      "HL6-9082 - Institution"),
        ("HL6-9092EL",    "HL6-9092EL - Storeroom Electric Locking"),
        ("HL6-9092EU",    "HL6-9092EU - Storeroom Electric Unlocking"),
        ("HL6-9095EL",    "HL6-9095EL - Institution Electric Locking"),
        ("HL6-9095EU",    "HL6-9095EU - Institution Electric Unlocking"),
        ("HL6-9453",      "HL6-9453 - Entrance (thumbturn)"),
        ("HL6-9456",      "HL6-9456 - Dormitory Exit (thumbturn)"),
        ("HL6-9465",      "HL6-9465 - Closet / Storeroom"),
        ("HL6-9466",      "HL6-9466 - Store / Utility"),
        ("HL6-9473",      "HL6-9473 - Dorm Bedroom (thumbturn)"),
        ("HL6-9485",      "HL6-9485 - Faculty Restroom / Hotel (thumbturn)"),
        ("HL6-9486",      "HL6-9486 - Faculty Restroom / Hotel (thumbturn)"),
        # Paddles only
        ("HL6-9000RK",    "HL6-9000RK - Mortise Paddles Only"),
        ("HL6-9000RK-95", "HL6-9000RK-95 - Mortise Paddles Only (L9095)"),
        # Von Duprin pull
        ("HL6Q-7500",     "HL6Q-7500 - Pull Latch for Von Duprin Exit"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605",  "605 - Bright Brass"),
        ("606",  "606 - Satin Brass"),
        ("612",  "612 - Satin Bronze"),
        ("613",  "613 - Oil Rubbed Bronze"),
        ("625",  "625 - Bright Chrome"),
        ("626",  "626 - Satin Chrome"),
        ("630",  "630 - Satin Stainless"),
    ])

    # ── Pricing ──
    # Base at 626
    price_bulk(conn, f, "function", [
        ("HL6-9010",       1564.00),
        ("HL6-9040",       1636.00),
        ("HL6-9050",       1636.00),
        ("HL6-9060",       1564.00),
        ("HL6-9070",       1564.00),
        ("HL6-9080",       1564.00),
        ("HL6-9082",       1564.00),
        ("HL6-9092EL",     2723.00),
        ("HL6-9092EU",     2723.00),
        ("HL6-9095EL",     2723.00),
        ("HL6-9095EU",     2723.00),
        ("HL6-9453",       1636.00),
        ("HL6-9456",       1636.00),
        ("HL6-9465",       1636.00),
        ("HL6-9466",       1636.00),
        ("HL6-9473",       1636.00),
        ("HL6-9485",       1636.00),
        ("HL6-9486",       1636.00),
        ("HL6-9000RK",      673.00),
        ("HL6-9000RK-95",   673.00),
        ("HL6Q-7500",       437.00),
    ], price_type="base")

    # Finish adders (relative to 626)
    # tier1 (626)=0, tier2 (605/606/612/625)=+$12, tier3 (613/630)=+$30
    price_bulk(conn, f, "finish", [
        ("626",   0.00),
        ("605",  12.00),
        ("606",  12.00),
        ("612",  12.00),
        ("625",  12.00),
        ("613",  30.00),
        ("630",  30.00),
    ], price_type="adder")
