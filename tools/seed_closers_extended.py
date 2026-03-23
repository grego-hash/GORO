"""Seed additional closers — Rixson, LCN 1460, Glynn-Johnson, Norton 1600."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_rixson(conn)
    _seed_glynn_johnson(conn)
    _seed_norton_1600(conn)
    print("  Rixson + Glynn-Johnson + Norton 1600 seeded.")


# ═════════════════════════════════════════════════════════════════════
# Rixson Floor Closers
# ═════════════════════════════════════════════════════════════════════

def _seed_rixson(conn):
    # ── Model 27/28 Floor Closer ──
    f = fid(conn, "Rixson", "27/28 Floor Closer",
            "Floor Closer",
            "{model} {spindle} {finish}",
            "Rixson {model} {spindle} {finish}")

    slot(conn, f, 1, "model",   "Model",          1)
    slot(conn, f, 2, "spindle", "Spindle Type",    1)
    slot(conn, f, 3, "cover",   "Cover Plate",     1)
    slot(conn, f, 4, "cement",  "Cement Case",     0)
    slot(conn, f, 5, "finish",  "Finish",          1)
    slot(conn, f, 6, "hold_open", "Hold-Open",     0)

    models = [
        ("27",   "27 - Center Hung, 105° Max"),
        ("28",   "28 - Center Hung, 180° Max"),
        ("27S",  "27S - Offset Hung"),
        ("28S",  "28S - Offset Hung, 180° Max"),
    ]
    options(conn, f, "model", models)

    spindles = [
        ("3/4SQ",  "3/4\" Square Spindle"),
        ("1SQ",    "1\" Square Spindle"),
        ("RND",    "Round Spindle"),
    ]
    options(conn, f, "spindle", spindles)

    covers = [
        ("CP",     "CP - Standard Cover Plate"),
        ("CP-F",   "CP-F - Flush Cover Plate"),
    ]
    options(conn, f, "cover", covers)

    options(conn, f, "cement", [("NONE","None"),("CC","CC - Cement Case")])

    finishes = [
        ("689",  "689 - Aluminum"),
        ("690",  "690 - Dark Bronze"),
        ("691",  "691 - Bright Chrome"),
        ("693",  "693 - Black"),
        ("695",  "695 - Satin Brass"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "hold_open", [("NONE","None"),("HO","HO - Hold-Open"),("SHO","SHO - Selective Hold-Open")])

    # ── Model 1 Overhead Concealed Closer ──
    f2 = fid(conn, "Rixson", "Model 1 Overhead Concealed Closer",
             "Concealed Closer",
             "1 {arm_type} {finish}",
             "Rixson Model 1 {arm_type} {finish}")

    slot(conn, f2, 1, "arm_type",  "Arm Type",         1)
    slot(conn, f2, 2, "size",      "Size / Spring",    1)
    slot(conn, f2, 3, "finish",    "Finish",           1)
    slot(conn, f2, 4, "hold_open", "Hold-Open",        0)

    arms = [
        ("T",   "T - Standard Track Arm"),
        ("TB",  "TB - Track Arm w/ Backcheck"),
        ("TS",  "TS - Track Arm w/ Delayed Action"),
    ]
    options(conn, f2, "arm_type", arms)

    options(conn, f2, "size", [
        ("3",  "Size 3"), ("4",  "Size 4"), ("5",  "Size 5"), ("6",  "Size 6"),
    ])
    options(conn, f2, "finish", finishes)
    options(conn, f2, "hold_open", [("NONE","None"),("HO","HO - Hold-Open")])


# ═════════════════════════════════════════════════════════════════════
# LCN 1460 Series
# ═════════════════════════════════════════════════════════════════════

def _seed_lcn_1460(conn):
    f = fid(conn, "LCN", "1460 Series Door Closer",
            "Door Closer",
            "1461 {arm_type} {finish}",
            "LCN 1461 {arm_type} {finish}")

    slot(conn, f, 1, "arm_type",  "Arm Type",        1)
    slot(conn, f, 2, "mounting",  "Mounting",         1)
    slot(conn, f, 3, "size",      "Spring Size",      1)
    slot(conn, f, 4, "finish",    "Finish",           1)
    slot(conn, f, 5, "cover",     "Cover",            0)
    slot(conn, f, 6, "hold_open", "Hold Open",        0)
    slot(conn, f, 7, "backcheck", "Backcheck",        0)
    slot(conn, f, 8, "delay",     "Delayed Action",   0)

    arms = [
        ("REG",   "REG - Regular Arm"),
        ("CUSH",  "CUSH - Cushion Arm"),
        ("HO",    "HO - Hold-Open Arm"),
        ("TBSRT", "TBSRT - Extra-Duty Arm, w/ Thru Bolt"),
        ("EDA",   "EDA - Extra-Duty Arm"),
        ("PA",    "PA - Parallel Arm"),
        ("SCUSH", "SCUSH - Spring Cush Arm"),
    ]
    options(conn, f, "arm_type", arms)

    options(conn, f, "mounting", [
        ("PULL",   "Pull Side (Regular)"),
        ("PUSH",   "Push Side (Top Jamb)"),
        ("PA",     "Parallel Arm"),
        ("CB",     "Corner Bracket"),
        ("SOFFIT", "Soffit Mount (Recessed)"),
    ])

    options(conn, f, "size", [("1","1"),("2","2"),("3","3"),("4","4"),("5","5"),("6","6")])

    finishes = [
        ("689",  "689 - Aluminum"),
        ("690",  "690 - Dark Statuary Bronze"),
        ("691",  "691 - Bright Chrome"),
        ("695",  "695 - Satin Brass"),
        ("693",  "693 - Black"),
        ("696",  "696 - Brass / Bronze Painted"),
        ("652",  "652 - Satin Aluminum"),
        ("716",  "716 - Sprayed Aluminum"),
        ("SP28", "SP28 - Satin Aluminum (Painted)"),
        ("US32D","US32D - Satin Stainless Steel"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "cover", [("NONE","None"),("COVER","Metal Cover"),("SLIM","Slim Cover"),("PLSTC","Plastic Cover")])

    options(conn, f, "hold_open", [
        ("NONE",   "No Hold Open"),
        ("FHO",    "Friction Hold Open (Arm-Based)"),
        ("MHO",    "Magnetic Hold Open"),
        ("EHO",    "Electronic Hold Open"),
    ])

    options(conn, f, "backcheck", [
        ("NONE", "No Backcheck"),
        ("BC",   "Backcheck (Spring Cushion)"),
    ])

    options(conn, f, "delay", [
        ("NONE", "No Delayed Action"),
        ("DA",   "DA - Delayed Action"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Glynn-Johnson Overhead Stops / Holders
# ═════════════════════════════════════════════════════════════════════

def _seed_glynn_johnson(conn):
    f = fid(conn, "Glynn-Johnson", "100+ Series Overhead Stop/Holder",
            "Overhead Stop/Holder",
            "{model} {finish}",
            "Glynn-Johnson {model} {finish}")

    slot(conn, f, 1, "model",     "Model",          1)
    slot(conn, f, 2, "finish",    "Finish",          1)

    models = [
        ("101S",   "101S - Overhead Stop, Standard"),
        ("102S",   "102S - Overhead Stop/Holder"),
        ("103S",   "103S - Overhead Stop/Holder, Heavy-Duty"),
        ("104S",   "104S - Overhead Stop/Holder, Extra-Heavy-Duty"),
        ("105S",   "105S - Overhead Stop/Holder, Surface Mount"),
    ]
    options(conn, f, "model", models)

    finishes = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless Steel"),
        ("US28", "US28 - Satin Aluminum"),
        ("US10B","US10B - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    # ── 900+ Series Heavy Duty Overhead ──
    f2 = fid(conn, "Glynn-Johnson", "900+ Series Heavy Duty Overhead Stop",
             "Overhead Stop/Holder",
             "{model} {finish}",
             "Glynn-Johnson {model} {finish}")

    slot(conn, f2, 1, "model",  "Model",   1)
    slot(conn, f2, 2, "finish", "Finish",  1)

    models_900 = [
        ("901S",  "901S - Heavy Duty Stop"),
        ("902S",  "902S - Heavy Duty Stop/Holder"),
        ("903S",  "903S - Extra-Heavy Duty Stop/Holder"),
        ("904S",  "904S - Extra-Heavy Duty Holder"),
    ]
    options(conn, f2, "model", models_900)
    options(conn, f2, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Norton 1600 Series
# ═════════════════════════════════════════════════════════════════════

def _seed_norton_1600(conn):
    f = fid(conn, "Norton", "1600 Series Door Closer",
            "Door Closer",
            "1600 {arm_type} {finish}",
            "Norton 1600 {arm_type} {finish}")

    slot(conn, f, 1, "arm_type", "Arm Type",        1)
    slot(conn, f, 2, "mounting", "Mounting",         1)
    slot(conn, f, 3, "size",     "Spring Size",      1)
    slot(conn, f, 4, "finish",   "Finish",           1)
    slot(conn, f, 5, "cover",    "Cover",            0)

    arms = [
        ("REG",    "REG - Regular Arm"),
        ("HO",     "HO - Hold-Open Arm"),
        ("CUSH",   "CUSH - Cushion Arm"),
        ("SN",     "SN - Snubber Arm"),
    ]
    options(conn, f, "arm_type", arms)

    options(conn, f, "mounting", [
        ("PULL",   "Pull Side (Regular)"),
        ("PUSH",   "Push Side (Top Jamb)"),
        ("PA",     "Parallel Arm"),
    ])

    options(conn, f, "size", [("1","1"),("2","2"),("3","3"),("4","4"),("5","5"),("6","6")])

    finishes = [
        ("689",  "689 - Aluminum"),
        ("690",  "690 - Dark Bronze"),
        ("691",  "691 - Bright Chrome"),
        ("695",  "695 - Satin Brass"),
        ("693",  "693 - Black"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "cover", [("NONE","None"),("COVER","Metal Cover")])
