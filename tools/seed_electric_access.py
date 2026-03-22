"""Seed electric strikes and maglocks — HES, Securitron, SDC, RCI."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_hes(conn)
    _seed_securitron(conn)
    _seed_sdc(conn)
    _seed_rci(conn)
    print("  HES + Securitron + SDC + RCI seeded.")


# ═════════════════════════════════════════════════════════════════════
# HES Electric Strikes
# ═════════════════════════════════════════════════════════════════════

def _seed_hes(conn):
    # ── 1006 Series ──
    f = fid(conn, "HES", "1006 Series Electric Strike",
            "Electric Strike",
            "1006-{faceplate} {voltage} {finish}",
            "HES 1006 {faceplate} {voltage} {finish}")

    slot(conn, f, 1, "faceplate",  "Faceplate / Latchbolt", 1)
    slot(conn, f, 2, "voltage",    "Voltage",               1)
    slot(conn, f, 3, "function",   "Function",              1)
    slot(conn, f, 4, "finish",     "Finish",                1)
    slot(conn, f, 5, "monitoring", "Monitoring",             0)

    faceplates = [
        ("CDB",    "CDB - Cylindrical / Deadbolt, Complete Pack"),
        ("CLB",    "CLB - Cylindrical Latchbolt Only"),
        ("F",      "F - Faceplate Only"),
    ]
    options(conn, f, "faceplate", faceplates)

    voltages = [
        ("12VDC",  "12VDC"),
        ("24VDC",  "24VDC"),
        ("12VAC",  "12VAC"),
        ("24VAC",  "24VAC"),
    ]
    options(conn, f, "voltage", voltages)

    functions = [
        ("FS",    "FS - Fail Safe (Locked on Power)"),
        ("FSE",   "FSE - Fail Safe Electric"),
        ("F",     "F - Fail Secure (Locked on No Power)"),
    ]
    options(conn, f, "function", functions)

    finishes = [
        ("630",  "630 - Satin Stainless"),
        ("612",  "612 - Satin Bronze"),
        ("DERA", "DERA - Dark Bronze"),
    ]
    options(conn, f, "finish", finishes)

    monitoring = [
        ("NONE", "None"),
        ("LBM",  "LBM - Latchbolt Monitor"),
    ]
    options(conn, f, "monitoring", monitoring)

    # ── 5000 Series ──
    f2 = fid(conn, "HES", "5000 Series Electric Strike",
             "Electric Strike",
             "5000-{faceplate} {voltage} {finish}",
             "HES 5000 {faceplate} {voltage} {finish}")

    slot(conn, f2, 1, "faceplate",  "Faceplate Configuration", 1)
    slot(conn, f2, 2, "voltage",    "Voltage",                 1)
    slot(conn, f2, 3, "function",   "Function",                1)
    slot(conn, f2, 4, "finish",     "Finish",                  1)
    slot(conn, f2, 5, "monitoring", "Monitoring",               0)

    fp_5000 = [
        ("501",    "501 - ANSI Square, 4-7/8\" x 1-1/4\""),
        ("502",    "502 - ANSI Round, 4-7/8\" x 1-1/4\""),
        ("504",    "504 - ANSI Square, Compact"),
    ]
    options(conn, f2, "faceplate", fp_5000)
    options(conn, f2, "voltage", voltages)
    options(conn, f2, "function", functions)
    options(conn, f2, "finish", finishes)
    options(conn, f2, "monitoring", monitoring)

    # ── 9600 Series ──
    f3 = fid(conn, "HES", "9600 Series Electric Strike",
             "Electric Strike",
             "9600-{faceplate} {voltage} {finish}",
             "HES 9600 {faceplate} {voltage} {finish}")

    slot(conn, f3, 1, "faceplate", "Faceplate Configuration", 1)
    slot(conn, f3, 2, "voltage",   "Voltage",                 1)
    slot(conn, f3, 3, "function",  "Function",                1)
    slot(conn, f3, 4, "finish",    "Finish",                  1)

    fp_9600 = [
        ("630",  "630 - Surface Mount"),
        ("612",  "612 - Surface Mount"),
    ]
    options(conn, f3, "faceplate", fp_9600)
    options(conn, f3, "voltage", voltages)

    func_9600 = [
        ("FS",  "FS - Fail Safe"),
        ("F",   "F - Fail Secure"),
    ]
    options(conn, f3, "function", func_9600)
    options(conn, f3, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Securitron Maglocks
# ═════════════════════════════════════════════════════════════════════

def _seed_securitron(conn):
    f = fid(conn, "Securitron", "Magnalock Series",
            "Electromagnetic Lock",
            "{model} {voltage} {options}",
            "Securitron {model} {voltage} {options}")

    slot(conn, f, 1, "model",     "Model",               1)
    slot(conn, f, 2, "voltage",   "Voltage",              1)
    slot(conn, f, 3, "finish",    "Finish",               1)
    slot(conn, f, 4, "sensor",    "Sensor / Monitoring",  0)

    models = [
        ("M32",   "M32 - Magnalock, 600 lb Holding Force"),
        ("M32D",  "M32D - Magnalock, 600 lb (Dual Voltage)"),
        ("M62",   "M62 - Magnalock, 1200 lb Holding Force"),
        ("M62D",  "M62D - Magnalock, 1200 lb (Dual Voltage)"),
        ("M82",   "M82 - Magnalock, 1800 lb Holding Force"),
        ("M82D",  "M82D - Magnalock, 1800 lb (Dual Voltage)"),
        ("M32DBN","M32DBN - Magnalock Bond Sensor, 600 lb"),
        ("M62DBN","M62DBN - Magnalock Bond Sensor, 1200 lb"),
    ]
    options(conn, f, "model", models)

    voltages = [
        ("12VDC", "12VDC"),
        ("24VDC", "24VDC"),
    ]
    options(conn, f, "voltage", voltages)

    finishes = [
        ("US28", "US28 - Satin Aluminum"),
        ("DK",   "DK - Dark Bronze"),
        ("BLK",  "BLK - Black"),
    ]
    options(conn, f, "finish", finishes)

    sensors = [
        ("NONE",  "None"),
        ("BM",    "BM - Bond Sensor (Door Status)"),
        ("DPS",   "DPS - Door Position Switch"),
    ]
    options(conn, f, "sensor", sensors)


# ═════════════════════════════════════════════════════════════════════
# SDC Electric Strikes & Maglocks
# ═════════════════════════════════════════════════════════════════════

def _seed_sdc(conn):
    # ── Electric Strikes ──
    f = fid(conn, "SDC", "Electric Strike Series",
            "Electric Strike",
            "{model} {voltage} {function}",
            "SDC {model} {voltage} {function}")

    slot(conn, f, 1, "model",    "Model",     1)
    slot(conn, f, 2, "voltage",  "Voltage",   1)
    slot(conn, f, 3, "function", "Function",  1)
    slot(conn, f, 4, "finish",   "Finish",    1)

    models = [
        ("45-4SU",   "45-4SU - Universal Strike, 4-7/8\" x 1-1/4\""),
        ("45-4SQ",   "45-4SQ - Square Corner Strike"),
        ("45-7U",    "45-7U - Universal Strike, 7\" x 1\""),
        ("55-4SU",   "55-4SU - Heavy-Duty Universal Strike"),
        ("55-4SQ",   "55-4SQ - Heavy-Duty Square Corner"),
    ]
    options(conn, f, "model", models)

    voltages = [
        ("12VDC",  "12VDC"),
        ("24VDC",  "24VDC"),
        ("12VAC",  "12VAC"),
        ("24VAC",  "24VAC"),
    ]
    options(conn, f, "voltage", voltages)

    functions = [
        ("FS",  "FS - Fail Safe"),
        ("F",   "F - Fail Secure"),
        ("FSE", "FSE - Fail Safe Electric"),
    ]
    options(conn, f, "function", functions)

    finishes = [
        ("630", "630 - Satin Stainless"),
        ("612", "612 - Satin Bronze"),
    ]
    options(conn, f, "finish", finishes)

    # ── Maglocks ──
    f2 = fid(conn, "SDC", "Maglock Series",
             "Electromagnetic Lock",
             "{model} {voltage}",
             "SDC {model} {voltage}")

    slot(conn, f2, 1, "model",   "Model",    1)
    slot(conn, f2, 2, "voltage", "Voltage",  1)
    slot(conn, f2, 3, "finish",  "Finish",   1)
    slot(conn, f2, 4, "sensor",  "Sensor",   0)

    mag_models = [
        ("1511",  "1511 - Single, 1200 lb"),
        ("1511S", "1511S - Single, 1200 lb w/ Status Sensor"),
        ("1561",  "1561 - Single, 600 lb"),
        ("1571",  "1571 - Double, 1200 lb (Pair)"),
        ("1581",  "1581 - Shear Lock, 2000 lb"),
    ]
    options(conn, f2, "model", mag_models)
    options(conn, f2, "voltage", [("12VDC","12VDC"),("24VDC","24VDC")])
    options(conn, f2, "finish", [("US28","US28 - Satin Aluminum"),("DK","DK - Dark Bronze")])
    options(conn, f2, "sensor", [("NONE","None"),("DPS","DPS - Door Position Switch"),("BM","BM - Bond Sensor")])


# ═════════════════════════════════════════════════════════════════════
# RCI Maglocks
# ═════════════════════════════════════════════════════════════════════

def _seed_rci(conn):
    f = fid(conn, "RCI", "Electromagnetic Lock",
            "Electromagnetic Lock",
            "{model} {voltage} {finish}",
            "RCI {model} {voltage} {finish}")

    slot(conn, f, 1, "model",   "Model",               1)
    slot(conn, f, 2, "voltage", "Voltage",              1)
    slot(conn, f, 3, "finish",  "Finish",               1)
    slot(conn, f, 4, "sensor",  "Sensor / Monitoring",  0)

    models = [
        ("8310",   "8310 - Single, 1200 lb Holding Force"),
        ("8310x28","8310x28 - Single, 1200 lb (Satin Aluminum)"),
        ("8320",   "8320 - Mini Single, 600 lb"),
        ("8371",   "8371 - Surface Mount, 750 lb"),
        ("8372",   "8372 - Shear Lock, 2000 lb"),
    ]
    options(conn, f, "model", models)

    options(conn, f, "voltage", [("12VDC","12VDC"),("24VDC","24VDC")])
    options(conn, f, "finish", [("US28","US28 - Satin Aluminum"),("US40","US40 - Dark Bronze"),("BLK","BLK - Black")])
    options(conn, f, "sensor", [("NONE","None"),("DPS","DPS - Door Position Switch"),("DSM","DSM - Door Status Monitor")])
