"""Seed narrow-stile / storefront hardware — Adams Rite, Jackson, Precision."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_adams_rite(conn)
    _seed_jackson(conn)
    _seed_precision(conn)
    print("  Adams Rite + Jackson + Precision seeded.")


# ═════════════════════════════════════════════════════════════════════
# Adams Rite
# ═════════════════════════════════════════════════════════════════════

def _seed_adams_rite(conn):
    # ── 4510/4710 Deadlatch ──
    f = fid(conn, "Adams Rite", "4510/4710 Deadlatch",
            "Narrow Stile Deadlatch",
            "{model}-{backset} {faceplate} {finish}",
            "Adams Rite {model}-{backset} {faceplate} {finish}")

    slot(conn, f, 1, "model",     "Model",               1)
    slot(conn, f, 2, "backset",   "Backset",              1)
    slot(conn, f, 3, "faceplate", "Faceplate",            1)
    slot(conn, f, 4, "finish",    "Finish",               1)
    slot(conn, f, 5, "handing",   "Handing",              1)

    models = [
        ("4510",  "4510 - Deadlatch, Standard"),
        ("4511",  "4511 - Deadlatch w/ Auxiliary Latch"),
        ("4710",  "4710 - Deadlatch, Round-End Faceplate"),
        ("4711",  "4711 - Deadlatch w/ Auxiliary, Round-End"),
    ]
    options(conn, f, "model", models)

    backsets = [
        ("31/32", "31/32\""),
        ("1-1/8", "1-1/8\""),
        ("1-1/2", "1-1/2\""),
    ]
    options(conn, f, "backset", backsets)

    faceplates = [
        ("FLAT",  "Flat Faceplate"),
        ("RAD",   "Radius Faceplate"),
    ]
    options(conn, f, "faceplate", faceplates)

    finishes = [
        ("628",  "628 - Satin Aluminum"),
        ("335",  "335 - Black Anodized"),
        ("313",  "313 - Dark Bronze Anodized"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "handing", [("LH","Left Hand"),("RH","Right Hand")])

    # ── 4300/4500/4900 Exits ──
    f2 = fid(conn, "Adams Rite", "8600 Narrow Stile Exit Device",
             "Narrow Stile Exit Device",
             "8600-{device} {voltage} {finish}",
             "Adams Rite 8600 {device} {voltage} {finish}")

    slot(conn, f2, 1, "device",   "Device Type",   1)
    slot(conn, f2, 2, "voltage",  "Voltage",        0)
    slot(conn, f2, 3, "finish",   "Finish",         1)
    slot(conn, f2, 4, "size",     "Door Width",     1)
    slot(conn, f2, 5, "handing",  "Handing",        1)

    devices = [
        ("8610",   "8610 - Rim, Narrow Stile"),
        ("8611",   "8611 - Rim, Motorized"),
        ("8620",   "8620 - CVR, Narrow Stile"),
        ("8630",   "8630 - Mortise, Narrow Stile"),
        ("8651",   "8651 - Rim, Electric Latch Retraction"),
    ]
    options(conn, f2, "device", devices)

    options(conn, f2, "voltage", [
        ("NONE","None (Mechanical)"),
        ("12VDC","12VDC"),("24VDC","24VDC"),
    ])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "size", [("36","36\""),("42","42\""),("48","48\"")])
    options(conn, f2, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    # Mechanical devices → no voltage
    for d in ["8610", "8620", "8630"]:
        restrict(conn, f2, "device", d, "voltage", ["NONE"],
                 f"Mech device {d} → no voltage")

    # ELR device requires voltage
    for d in ["8611", "8651"]:
        restrict(conn, f2, "device", d, "voltage", ["12VDC", "24VDC"],
                 f"Electrified {d} → requires voltage")

    # ── 4590 / 4790 Hookbolt ──
    f3 = fid(conn, "Adams Rite", "4590/4790 Hookbolt",
             "Narrow Stile Hookbolt",
             "{model}-{backset} {finish}",
             "Adams Rite {model}-{backset} {finish}")

    slot(conn, f3, 1, "model",   "Model",    1)
    slot(conn, f3, 2, "backset", "Backset",   1)
    slot(conn, f3, 3, "finish",  "Finish",    1)
    slot(conn, f3, 4, "handing", "Handing",   1)

    options(conn, f3, "model", [
        ("4590","4590 - Hookbolt, Flat Faceplate"),
        ("4790","4790 - Hookbolt, Round-End Faceplate"),
    ])
    options(conn, f3, "backset", backsets)
    options(conn, f3, "finish", finishes)
    options(conn, f3, "handing", [("LH","Left Hand"),("RH","Right Hand")])


# ═════════════════════════════════════════════════════════════════════
# Jackson
# ═════════════════════════════════════════════════════════════════════

def _seed_jackson(conn):
    f = fid(conn, "Jackson", "1200 Series Panic Exit",
            "Exit Device",
            "{model} {trim_type} {finish}",
            "Jackson {model} {trim_type} {finish}")

    slot(conn, f, 1, "model",     "Model",          1)
    slot(conn, f, 2, "trim_type", "Trim Type",       1)
    slot(conn, f, 3, "lever",     "Lever Design",    0)
    slot(conn, f, 4, "finish",    "Finish",          1)
    slot(conn, f, 5, "size",      "Door Width",      1)
    slot(conn, f, 6, "handing",   "Handing",         1)

    models = [
        ("1285",  "1285 - Rim Device, Aluminum"),
        ("1295",  "1295 - Rim Device, Aluminum w/ Thumbpiece"),
        ("1285V", "1285V - Vertical Rod, Concealed"),
        ("1295V", "1295V - Vertical Rod, Concealed w/ Thumbpiece"),
    ]
    options(conn, f, "model", models)

    trim_types = [
        ("PT",   "PT - Push Bar / Touchbar"),
        ("PT-L", "PT-L - Push Bar w/ Lever Trim"),
        ("PT-T", "PT-T - Push Bar w/ Thumbpiece"),
    ]
    options(conn, f, "trim_type", trim_types)

    levers = [
        ("01",  "01 - Standard Lever"),
        ("06",  "06 - Round Lever"),
        ("10",  "10 - Flat Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("628", "628 - Satin Aluminum"),
        ("335", "335 - Black Anodized"),
        ("313", "313 - Dark Bronze Anodized"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "size", [("36","36\""),("48","48\"")])
    options(conn, f, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    # Hide lever when no lever trim
    for t in ["PT", "PT-T"]:
        conflict_all(conn, f, "trim_type", [t], "lever",
                     [l[0] for l in levers], f"Trim {t} hides lever")


# ═════════════════════════════════════════════════════════════════════
# Precision
# ═════════════════════════════════════════════════════════════════════

def _seed_precision(conn):
    # ── Apex 2000 Series ──
    f = fid(conn, "Precision", "Apex 2000 Series Exit Device",
            "Exit Device",
            "2{device_type} {trim_type} {finish}",
            "Precision Apex 2{device_type} {trim_type} {finish}")

    slot(conn, f, 1, "device_type", "Device Type",    1)
    slot(conn, f, 2, "trim_type",   "Trim Type",      1)
    slot(conn, f, 3, "lever",       "Lever Design",   0)
    slot(conn, f, 4, "finish",      "Finish",         1)
    slot(conn, f, 5, "size",        "Door Width",     1)
    slot(conn, f, 6, "handing",     "Handing",        1)

    devices = [
        ("108",  "2108 - Rim Exit"),
        ("208",  "2208 - Mortise Exit"),
        ("308",  "2308 - SVR Exit (Surface Vertical Rod)"),
        ("608",  "2608 - CVR Exit (Concealed Vertical Rod)"),
    ]
    options(conn, f, "device_type", devices)

    trim_types = [
        ("PB",    "PB - Push Bar Only"),
        ("PB-L",  "PB-L - Push Bar w/ Lever Trim"),
        ("PB-TP", "PB-TP - Push Bar w/ Thumbpiece"),
        ("PB-PT", "PB-PT - Push Bar w/ Pull Trim"),
    ]
    options(conn, f, "trim_type", trim_types)

    levers = [
        ("02",  "02 - Standard Lever"),
        ("03",  "03 - Decorative Lever"),
        ("12",  "12 - Round Lever"),
        ("17",  "17 - Institutional Lever"),
    ]
    options(conn, f, "lever", levers)

    finishes = [
        ("US26D", "US26D - Satin Chrome"),
        ("US32D", "US32D - Satin Stainless"),
        ("US28",  "US28 - Satin Aluminum"),
        ("US10B", "US10B - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "size", [("36","36\""),("42","42\""),("48","48\"")])
    options(conn, f, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    # Hide lever unless lever-trim selected
    for t in ["PB", "PB-TP", "PB-PT"]:
        conflict_all(conn, f, "trim_type", [t], "lever",
                     [l[0] for l in levers], f"Trim {t} hides lever")

    # ── Apex 4000 Series (Wide Stile) ──
    f2 = fid(conn, "Precision", "Apex 4000 Series Exit Device",
             "Exit Device",
             "4{device_type} {trim_type} {finish}",
             "Precision Apex 4{device_type} {trim_type} {finish}")

    slot(conn, f2, 1, "device_type", "Device Type",    1)
    slot(conn, f2, 2, "trim_type",   "Trim Type",      1)
    slot(conn, f2, 3, "lever",       "Lever Design",   0)
    slot(conn, f2, 4, "finish",      "Finish",         1)
    slot(conn, f2, 5, "size",        "Door Width",     1)
    slot(conn, f2, 6, "handing",     "Handing",        1)

    devices_4k = [
        ("108",  "4108 - Rim Exit"),
        ("208",  "4208 - Mortise Exit"),
        ("308",  "4308 - SVR Exit"),
        ("608",  "4608 - CVR Exit"),
    ]
    options(conn, f2, "device_type", devices_4k)
    options(conn, f2, "trim_type", trim_types)
    options(conn, f2, "lever", levers)
    options(conn, f2, "finish", finishes)
    options(conn, f2, "size", [("36","36\""),("42","42\""),("48","48\"")])
    options(conn, f2, "handing", [("LHR","Left Hand Reverse"),("RHR","Right Hand Reverse")])

    for t in ["PB", "PB-TP", "PB-PT"]:
        conflict_all(conn, f2, "trim_type", [t], "lever",
                     [l[0] for l in levers], f"Trim {t} hides lever")
