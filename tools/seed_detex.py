"""Seed Detex — exit alarms, alarmed exit devices."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_eax(conn)
    _seed_ecl(conn)
    _seed_v40(conn)
    print("  Detex exit alarms + devices seeded.")


# ═════════════════════════════════════════════════════════════════════
# Detex EAX-500 / EAX-2500 Exit Alarm
# ═════════════════════════════════════════════════════════════════════

def _seed_eax(conn):
    f = fid(conn, "Detex", "EAX-500 Exit Alarm",
            "Exit Alarm",
            "EAX-{model} {power} {finish}",
            "Detex EAX-{model} {power} {finish}")

    slot(conn, f, 1, "model",   "Model",         1)
    slot(conn, f, 2, "power",   "Power Source",   1)
    slot(conn, f, 3, "finish",  "Finish",         1)
    slot(conn, f, 4, "options", "Options",        0)

    models = [
        ("500",   "EAX-500 - Surface Mount Exit Alarm"),
        ("500SK", "EAX-500SK - Exit Alarm w/ Shunt Key"),
        ("2500",  "EAX-2500 - Multi-Point Exit Alarm"),
        ("2500S", "EAX-2500S - Multi-Point w/ Shunt"),
        ("300",   "EAX-300 - Door Prop Alarm"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "power", [
        ("BAT",  "Battery Powered (9V)"),
        ("HW",   "Hardwired (12/24VDC)"),
    ])

    finishes = [
        ("BK",  "Black"),
        ("GR",  "Grey"),
        ("W",   "White"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "options", [
        ("NONE",  "None"),
        ("DS",    "DS - Door Status Switch"),
        ("RA",    "RA - Remote Annunciation"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Detex ECL-230D Alarmed Exit Device
# ═════════════════════════════════════════════════════════════════════

def _seed_ecl(conn):
    f = fid(conn, "Detex", "ECL-230D Alarmed Exit Device",
            "Exit Device",
            "ECL-230D {size} {finish}",
            "Detex ECL-230D {size} {finish}")

    slot(conn, f, 1, "model",   "Model",        1)
    slot(conn, f, 2, "size",    "Door Width",    1)
    slot(conn, f, 3, "finish",  "Finish",        1)
    slot(conn, f, 4, "power",   "Power Source",  1)
    slot(conn, f, 5, "handing", "Handing",       1)

    models = [
        ("ECL-230D",  "ECL-230D - Panic Hardware w/ Alarm"),
        ("ECL-230X",  "ECL-230X - Panic Hardware Exit Only"),
        ("ECL-600",   "ECL-600 - Fire Rated Alarmed Exit Device"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "size", [("36","36\""),("48","48\"")])
    options(conn, f, "finish", [
        ("US28","US28 - Satin Aluminum"),
        ("BLK", "BLK - Black"),
    ])
    options(conn, f, "power", [
        ("BAT","Battery Powered"),
        ("HW", "Hardwired (12/24VDC)"),
    ])
    options(conn, f, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])


# ═════════════════════════════════════════════════════════════════════
# Detex V-40 Value Series Exit Device
# ═════════════════════════════════════════════════════════════════════

def _seed_v40(conn):
    f = fid(conn, "Detex", "V-40 Value Series Exit Device",
            "Exit Device",
            "V-40 {trim} {finish}",
            "Detex V-40 {trim} {finish}")

    slot(conn, f, 1, "model",   "Device Type",    1)
    slot(conn, f, 2, "trim",    "Trim Type",       1)
    slot(conn, f, 3, "finish",  "Finish",          1)
    slot(conn, f, 4, "size",    "Door Width",      1)
    slot(conn, f, 5, "handing", "Handing",         1)

    options(conn, f, "model", [
        ("V-40xEB", "V-40xEB - Rim Exit, Economy Bar"),
        ("V-40xCD", "V-40xCD - Rim Exit, Crossbar"),
        ("V-40xET", "V-40xET - Rim Exit, Touchbar"),
    ])

    options(conn, f, "trim", [
        ("EB",  "Exit Bar Only (No Trim)"),
        ("LTR", "Lever Trim"),
        ("PTR", "Pull Trim"),
    ])

    options(conn, f, "finish", [
        ("628","628 - Satin Aluminum"),
        ("BLK","BLK - Black"),
    ])

    options(conn, f, "size", [("36","36\""),("48","48\"")])
    options(conn, f, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])
