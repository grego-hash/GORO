"""Seed Lockey digital/mechanical keypad locks."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_lockey_digital(conn)
    _seed_lockey_mechanical(conn)
    print("  Lockey keypad locks seeded.")


# ═════════════════════════════════════════════════════════════════════
# Lockey Digital Keypad Lever Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_lockey_digital(conn):
    f = fid(conn, "Lockey", "Digital Keypad Lock",
            "Electronic Lock",
            "{model} {function} {finish}",
            "Lockey {model} Digital Keypad {function} {finish}")

    slot(conn, f, 1, "model",    "Model",    1)
    slot(conn, f, 2, "function", "Function", 1)
    slot(conn, f, 3, "finish",   "Finish",   1)

    options(conn, f, "model", [
        ("E930",  "E930 - Electronic Lever (Motorized)"),
        ("E985",  "E985 - Electronic w/ Audit Trail"),
        ("E995",  "E995 - Electronic Deadbolt"),
        ("2835DC","2835DC - Digital Lever w/ Passage"),
    ])

    options(conn, f, "function", [
        ("Passage",  "Passage / Free Egress"),
        ("Storeroom","Storeroom (always locked)"),
        ("Entry",    "Entry (toggle)"),
    ])

    options(conn, f, "finish", [
        ("SN","SN - Satin Nickel"),
        ("BK","BK - Jet Black"),
        ("AB","AB - Antique Brass"),
        ("SC","SC - Satin Chrome"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Lockey Mechanical Push-Button Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_lockey_mechanical(conn):
    f = fid(conn, "Lockey", "Mechanical Push-Button Lock",
            "Keypad Lock",
            "{model} {function} {finish}",
            "Lockey {model} Mechanical Keyless {function} {finish}")

    slot(conn, f, 1, "model",    "Model",    1)
    slot(conn, f, 2, "function", "Function", 1)
    slot(conn, f, 3, "finish",   "Finish",   1)

    options(conn, f, "model", [
        ("2835","2835 - Push-Button Lever"),
        ("2900","2900 - Narrow-Stile Hookbolt"),
        ("2950","2950 - Narrow-Stile Deadlatch"),
        ("1600","1600 - Push-Button Knob"),
        ("3210","3210 - Deadbolt Keyless"),
    ])

    options(conn, f, "function", [
        ("Passage",  "Passage"),
        ("Storeroom","Storeroom"),
        ("Entry",    "Entry"),
    ])

    options(conn, f, "finish", [
        ("SN","SN - Satin Nickel"),
        ("BK","BK - Jet Black"),
        ("AB","AB - Antique Brass"),
        ("SC","SC - Satin Chrome"),
        ("WH","WH - White"),
    ])
