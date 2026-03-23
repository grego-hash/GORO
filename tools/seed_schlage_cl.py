"""Seed Schlage CL Series cabinet lock data.

Schlage CL Series — cabinet locks (door, drawer, cam, ratchet).
"""

from seed_helpers import fid, slot, options, price, price_bulk


def seed(conn):
    _seed_cl(conn)
    print("  Schlage CL Series seeded.")


def _seed_cl(conn):
    f = fid(conn,
            "Schlage",
            "CL Series Cabinet Lock",
            "Cabinet Lock",
            "{function} {finish}",
            "Schlage CL Series {function} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function", "Function", 1)
    slot(conn, f, 2, "finish",  "Finish",    1)

    # ── Functions ──
    options(conn, f, "function", [
        # Conventional cylinder
        ("CL100PB",  "CL100PB - Door Cabinet Lock (Conv 6-Pin)"),
        ("CL200PB",  "CL200PB - Drawer Cabinet Lock (Conv 6-Pin)"),
        # Primus controlled access
        ("CL174PB",  "CL174PB - Door Cabinet Lock (Primus)"),
        ("CL274PB",  "CL274PB - Drawer Cabinet Lock (Primus)"),
        # Primus UL437
        ("CL154PB",  "CL154PB - Door Cabinet Lock (Primus UL437)"),
        ("CL254PB",  "CL254PB - Drawer Cabinet Lock (Primus UL437)"),
        # FSIC
        ("CL777R",   "CL777R - Door Cabinet Lock (FSIC)"),
        ("CL888R",   "CL888R - Drawer Cabinet Lock (FSIC)"),
        ("CL920R",   "CL920R - FSIC Cam Lock"),
        # FSIC Primus
        ("CL774R",   "CL774R - Door Cabinet Lock (FSIC Primus)"),
        ("CL874R",   "CL874R - Drawer Cabinet Lock (FSIC Primus)"),
        ("CL974R",   "CL974R - FSIC Cam Lock (Primus)"),
        # FSIC Ratchet
        ("CL929R",   "CL929R - Ratchet Lock (FSIC)"),
        # SFIC (626 only)
        ("CL721G",   "CL721G - Door Cabinet Lock (SFIC)"),
        ("CL771G",   "CL771G - Drawer Cabinet Lock (SFIC)"),
        ("CL720G",   "CL720G - SFIC Cam Lock"),
        ("CL728G",   "CL728G - SFIC Mail Box Lock"),
        ("CL729G",   "CL729G - SFIC Ratchet Lock"),
    ])

    # ── Finishes ──
    options(conn, f, "finish", [
        ("605", "605 - Bright Brass"),
        ("626", "626 - Satin Chrome"),
    ])

    # ==============================================================
    # PRICING — Schlage CL Series Price Book (effective 2/27/26)
    # ==============================================================
    # All CL functions have flat pricing (605/626 same price)
    price_bulk(conn, f, "function", [
        ("CL100PB",  237.00),
        ("CL200PB",  237.00),
        ("CL174PB",  359.00),
        ("CL274PB",  359.00),
        ("CL154PB",  428.00),
        ("CL254PB",  428.00),
        ("CL777R",   275.00),
        ("CL888R",   275.00),
        ("CL920R",   224.00),
        ("CL774R",   397.00),
        ("CL874R",   397.00),
        ("CL974R",   346.00),
        ("CL929R",   290.00),
        ("CL721G",   248.00),
        ("CL771G",   248.00),
        ("CL720G",   231.00),
        ("CL728G",   184.00),
        ("CL729G",   297.00),
    ], price_type="base")

    # Finish adders (both same price → 0)
    price_bulk(conn, f, "finish", [
        ("605", 0.00),
        ("626", 0.00),
    ], price_type="adder")
