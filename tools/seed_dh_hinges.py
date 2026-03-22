"""Seed Design Hardware (DH) continuous hinges — competitor to SELECT/Roton."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_dh_continuous(conn)
    _seed_dh_electric(conn)
    print("  Design Hardware (DH) hinges seeded.")


# ═════════════════════════════════════════════════════════════════════
# DH Continuous Geared Hinge
# ═════════════════════════════════════════════════════════════════════

def _seed_dh_continuous(conn):
    f = fid(conn, "Design Hardware (DH)", "Continuous Geared Hinge",
            "Continuous Hinge",
            "{model} {length} {finish}",
            "DH {model} Continuous Geared Hinge {length} {finish}")

    slot(conn, f, 1, "model",  "Mounting Type", 1)
    slot(conn, f, 2, "duty",   "Duty Rating",   1)
    slot(conn, f, 3, "length", "Length",         1)
    slot(conn, f, 4, "finish", "Finish",         1)

    options(conn, f, "model", [
        ("DH-26",  "DH-26 - Full Surface"),
        ("DH-26-S","DH-26-S - Full Surface, Security"),
        ("DH-35",  "DH-35 - Half Surface"),
        ("DH-37",  "DH-37 - Half Mortise"),
        ("DH-40",  "DH-40 - Full Mortise"),
        ("DH-40-S","DH-40-S - Full Mortise, Security"),
    ])

    options(conn, f, "duty", [
        ("STD","Standard Duty"),
        ("HD", "Heavy Duty"),
    ])

    options(conn, f, "length", [
        ("79","79\" (6'-7\")"), ("83","83\" (6'-11\")"),
        ("85","85\" (7'-1\")"), ("95","95\" (7'-11\")"),
        ("119","119\" (9'-11\")"),
    ])

    options(conn, f, "finish", [
        ("CL","CL - Clear Anodized"),
        ("DU","DU - Dark Bronze Anodized"),
        ("BK","BK - Black Anodized"),
        ("P", "P - Primed for Paint"),
    ])


# ═════════════════════════════════════════════════════════════════════
# DH Electric Power Transfer Hinge
# ═════════════════════════════════════════════════════════════════════

def _seed_dh_electric(conn):
    f = fid(conn, "Design Hardware (DH)", "Electric Power Transfer Hinge",
            "Electric Hinge",
            "{model}-EPT {wires} {length} {finish}",
            "DH {model}-EPT Electric {wires} {length} {finish}")

    slot(conn, f, 1, "model",  "Mounting Type", 1)
    slot(conn, f, 2, "wires",  "Wire Count",    1)
    slot(conn, f, 3, "length", "Length",         1)
    slot(conn, f, 4, "finish", "Finish",         1)

    options(conn, f, "model", [
        ("DH-26","DH-26 - Full Surface"),
        ("DH-35","DH-35 - Half Surface"),
        ("DH-40","DH-40 - Full Mortise"),
    ])

    options(conn, f, "wires", [
        ("4W","4 Wire"),("8W","8 Wire"),("12W","12 Wire"),
    ])

    options(conn, f, "length", [
        ("79","79\""),("83","83\""),("85","85\""),("95","95\""),
    ])

    options(conn, f, "finish", [
        ("CL","CL - Clear Anodized"),
        ("DU","DU - Dark Bronze Anodized"),
        ("BK","BK - Black Anodized"),
    ])
