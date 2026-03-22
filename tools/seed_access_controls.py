"""Seed access control peripherals — Alarm Lock/Trilogy, Camden, Alarm Controls."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_alarm_lock(conn)
    _seed_camden(conn)
    _seed_alarm_controls(conn)
    print("  Alarm Lock + Camden + Alarm Controls seeded.")


# ═════════════════════════════════════════════════════════════════════
# Alarm Lock / Trilogy
# ═════════════════════════════════════════════════════════════════════

def _seed_alarm_lock(conn):
    # ── DL2700 / DL3000 Standalone Keypad ──
    f = fid(conn, "Alarm Lock", "Trilogy DL2700/DL3000 Keypad Lock",
            "Electronic Lock",
            "{model} {function} {lever} {finish}",
            "Alarm Lock Trilogy {model} {function} {lever} {finish}")

    slot(conn, f, 1, "model",    "Model",          1)
    slot(conn, f, 2, "function", "Function",       1)
    slot(conn, f, 3, "lever",    "Lever / Knob",   1)
    slot(conn, f, 4, "finish",   "Finish",         1)

    models = [
        ("DL2700",   "DL2700 - Standalone Keypad, Standard"),
        ("DL2700WP", "DL2700WP - Standalone Keypad, Weatherproof"),
        ("DL3000",   "DL3000 - Networked Keypad"),
        ("DL3000WP", "DL3000WP - Networked Keypad, Weatherproof"),
        ("DL2800",   "DL2800 - Standalone Mortise Keypad"),
        ("DL3200",   "DL3200 - Networked Mortise Keypad"),
    ]
    options(conn, f, "model", models)

    functions = [
        ("ENT", "Entry / Office"),
        ("STR", "Storeroom"),
        ("CLS", "Classroom"),
    ]
    options(conn, f, "function", functions)

    levers = [
        ("K",   "Standard Knob"),
        ("L",   "Standard Lever"),
        ("LL",  "Long Lever"),
        ("IL",  "Institutional Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
    ]
    options(conn, f, "finish", finishes)

    # ── DL1200 / DL1300 Deadbolt Keypads ──
    f2 = fid(conn, "Alarm Lock", "Trilogy DL1200/DL1300 Deadbolt Keypad",
             "Electronic Lock",
             "{model} {finish}",
             "Alarm Lock Trilogy {model} {finish}")

    slot(conn, f2, 1, "model",  "Model",    1)
    slot(conn, f2, 2, "finish", "Finish",   1)

    options(conn, f2, "model", [
        ("DL1200",  "DL1200 - Standalone Deadbolt Keypad"),
        ("DL1300",  "DL1300 - Networked Deadbolt Keypad"),
    ])
    options(conn, f2, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Camden
# ═════════════════════════════════════════════════════════════════════

def _seed_camden(conn):
    # ── Wave-to-Open Switches ──
    f = fid(conn, "Camden", "Touchless / Wave-to-Open Switch",
            "Access Switch",
            "CM-{model} {finish}",
            "Camden CM-{model} {finish}")

    slot(conn, f, 1, "model",    "Model",          1)
    slot(conn, f, 2, "finish",   "Finish / Color", 1)
    slot(conn, f, 3, "graphics", "Faceplate",      0)

    models = [
        ("330",   "CM-330 - SureWave, Battery Powered"),
        ("331",   "CM-331 - SureWave, Hardwired"),
        ("333",   "CM-333 - Lazerpoint, Recessed"),
        ("332",   "CM-332 - SureWave, Narrow Frame"),
        ("325",   "CM-325 - Wrist Watch, Surface Mount"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "finish", [
        ("SS",  "Stainless Steel"),
        ("BLK", "Black"),
        ("WH",  "White"),
    ])

    options(conn, f, "graphics", [
        ("NONE",  "None / Plain"),
        ("LOGO",  "Logo Engraving"),
        ("HAND",  "Hand Symbol"),
    ])

    # ── Push Plates / Request-to-Exit ──
    f2 = fid(conn, "Camden", "Push Plate / Request to Exit",
             "Access Switch",
             "CM-{model}",
             "Camden CM-{model}")

    slot(conn, f2, 1, "model",    "Model",       1)
    slot(conn, f2, 2, "graphics", "Graphics",    0)

    pp_models = [
        ("1000",  "CM-1000 - Mushroom Push Button, Green"),
        ("1100",  "CM-1100 - Mushroom Push Button, Red"),
        ("2000",  "CM-2000 - Flush Mount Push Plate"),
        ("2200",  "CM-2200 - Flush Mount Push Plate, Illuminated"),
        ("500",   "CM-500 - Vandal Resistant Push Plate"),
    ]
    options(conn, f2, "model", pp_models)

    options(conn, f2, "graphics", [
        ("NONE",  "None / Blank"),
        ("PTE",   "PUSH TO EXIT"),
        ("LOGO",  "Custom Logo"),
    ])

    # ── Keypads ──
    f3 = fid(conn, "Camden", "Keypad / Digital Entry",
             "Access Switch",
             "CM-{model}",
             "Camden CM-{model}")

    slot(conn, f3, 1, "model",  "Model",          1)
    slot(conn, f3, 2, "mount",  "Mounting",       1)

    options(conn, f3, "model", [
        ("120",   "CM-120 - Wired Keypad, Stainless"),
        ("130",   "CM-130 - Wired Keypad, Surface Mount"),
        ("160",   "CM-160 - Wired Keypad, Illuminated"),
    ])

    options(conn, f3, "mount", [
        ("SURF", "Surface Mount"),
        ("FL",   "Flush Mount"),
        ("WP",   "Weatherproof Box"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Alarm Controls
# ═════════════════════════════════════════════════════════════════════

def _seed_alarm_controls(conn):
    # ── Request-to-Exit Buttons ──
    f = fid(conn, "Alarm Controls", "Request-to-Exit Button",
            "Access Switch",
            "{model}",
            "Alarm Controls {model}")

    slot(conn, f, 1, "model",  "Model",    1)
    slot(conn, f, 2, "color",  "Color",    0)

    models = [
        ("TS-2",   "TS-2 - Request-to-Exit Button, 3/4\" Mushroom"),
        ("TS-2T",  "TS-2T - TS-2 w/ Timer"),
        ("TS-14",  "TS-14 - Narrow Push Plate Button"),
        ("TS-32",  "TS-32 - Dual Button (In/Out)"),
    ]
    options(conn, f, "model", models)
    options(conn, f, "color", [("SS","Stainless Steel"),("WH","White"),("BLK","Black")])

    # ── Power Supplies ──
    f2 = fid(conn, "Alarm Controls", "Power Supply / Transformer",
             "Power Supply",
             "{model}",
             "Alarm Controls {model}")

    slot(conn, f2, 1, "model",  "Model",    1)

    options(conn, f2, "model", [
        ("EFLOW-4N",  "EFLOW-4N - 12/24VDC, 4A, w/ Fire Alarm Reset"),
        ("EFLOW-6N",  "EFLOW-6N - 12/24VDC, 6A, w/ Fire Alarm Reset"),
        ("EFLOW-2N",  "EFLOW-2N - 12/24VDC, 2A, w/ Fire Alarm Reset"),
        ("SMP-5",     "SMP-5 - Switching Power Supply, 12/24VDC, 5A"),
        ("SMP-3",     "SMP-3 - Switching Power Supply, 12/24VDC, 3A"),
    ])
