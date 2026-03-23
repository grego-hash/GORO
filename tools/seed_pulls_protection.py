"""Seed pulls, protection, and trim — Rockwood, Trimco, Don-Jo."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_rockwood(conn)
    _seed_trimco(conn)
    _seed_donjo(conn)
    print("  Rockwood + Trimco + Don-Jo seeded.")


# ═════════════════════════════════════════════════════════════════════
# Rockwood
# ═════════════════════════════════════════════════════════════════════

def _seed_rockwood(conn):
    # ── Shared Rockwood Finishes ──
    RW_FINISHES = [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless Steel"),
        ("US28", "US28 - Satin Aluminum"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US4",  "US4 - Satin Brass"),
        ("US15", "US15 - Satin Nickel"),
        ("US26", "US26 - Polished Chrome"),
        ("USP",  "USP - Primed for Paint"),
    ]

    RW_PLATE_FINISHES = [
        ("US32D","US32D - Satin Stainless Steel"),
        ("US28", "US28 - Satin Aluminum"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US4",  "US4 - Satin Brass"),
        ("US26D","US26D - Satin Chrome"),
        ("US15", "US15 - Satin Nickel"),
    ]

    # ══════════════════════════════════════════════════════════════
    # Pull Handles
    # ══════════════════════════════════════════════════════════════
    f = fid(conn, "Rockwood", "Pull Handle",
            "Pull / Push",
            "RM{model} {size} {finish}",
            "Rockwood RM{model} {size} {finish}")

    slot(conn, f, 1, "model",  "Model",       1)
    slot(conn, f, 2, "size",   "Length",       1)
    slot(conn, f, 3, "finish", "Finish",       1)
    slot(conn, f, 4, "mount",  "Mounting",     1)

    models = [
        ("BF100", "BF100 - Straight Pull"),
        ("BF102", "BF102 - Offset Pull"),
        ("BF107", "BF107 - Round Pull"),
        ("BF110", "BF110 - Straight Pull, Cast"),
        ("BF157", "BF157 - Hospital Pull"),
        ("BF140", "BF140 - D-Shape Pull"),
        ("BF159", "BF159 - Barrier-Free Pull"),
        ("BF161", "BF161 - Contoured Pull"),
        ("BF180", "BF180 - Oval Shape Pull"),
        ("BF131", "BF131 - Triangular Pull"),
        ("BF106", "BF106 - Round Tube Pull"),
        ("BF120", "BF120 - Flat Bar Pull"),
    ]
    options(conn, f, "model", models)

    sizes = [
        ("6",   "6\" CTC"),
        ("8",   "8\" CTC"),
        ("10",  "10\" CTC"),
        ("12",  "12\" CTC"),
        ("18",  "18\" CTC"),
        ("24",  "24\" CTC"),
        ("36",  "36\" CTC"),
    ]
    options(conn, f, "size", sizes)
    options(conn, f, "finish", RW_FINISHES)

    options(conn, f, "mount", [
        ("TM", "TM - Thru-Mount (Back-to-Back)"),
        ("SM", "SM - Surface Mount"),
        ("SK", "SK - Snap-On Cover Mount"),
    ])

    # ══════════════════════════════════════════════════════════════
    # Push Plates
    # ══════════════════════════════════════════════════════════════
    f2 = fid(conn, "Rockwood", "Push Plate",
             "Push / Pull Plate",
             "{model} {size} {finish}",
             "Rockwood {model} {size} {finish}")

    slot(conn, f2, 1, "model",  "Model",    1)
    slot(conn, f2, 2, "size",   "Size",     1)
    slot(conn, f2, 3, "finish", "Finish",   1)

    pp_models = [
        ("70A",   "70A - Push Plate, Square Corner"),
        ("70B",   "70B - Push Plate, Round Corner"),
        ("70C",   "70C - Push Plate, Beveled Edge"),
        ("70D",   "70D - Push Plate, Radiused Edge"),
        ("76",    "76 - Hospital Push Plate"),
        ("73",    "73 - Push Plate, Offset"),
        ("70E",   "70E - Push Plate, Engraved"),
    ]
    options(conn, f2, "model", pp_models)

    pp_sizes = [
        ("3.5x15",  "3-1/2\" x 15\""),
        ("4x16",    "4\" x 16\""),
        ("6x16",    "6\" x 16\""),
        ("8x16",    "8\" x 16\""),
        ("4x12",    "4\" x 12\""),
        ("6x12",    "6\" x 12\""),
        ("8x20",    "8\" x 20\""),
        ("10x16",   "10\" x 16\""),
        ("12x20",   "12\" x 20\""),
    ]
    options(conn, f2, "size", pp_sizes)
    options(conn, f2, "finish", RW_PLATE_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Push / Pull Bars
    # ══════════════════════════════════════════════════════════════
    f_ppb = fid(conn, "Rockwood", "Push / Pull Bar",
                "Pull / Push",
                "{model} {size} {finish}",
                "Rockwood {model} Push/Pull Bar {size} {finish}")

    slot(conn, f_ppb, 1, "model",  "Model",    1)
    slot(conn, f_ppb, 2, "size",   "Length",   1)
    slot(conn, f_ppb, 3, "finish", "Finish",   1)
    slot(conn, f_ppb, 4, "mount",  "Mounting", 1)

    options(conn, f_ppb, "model", [
        ("T100",  "T100 - Round Tube, Straight"),
        ("T102",  "T102 - Round Tube, Offset"),
        ("T105",  "T105 - Round Tube, Cranked"),
        ("T110",  "T110 - Flat Bar, Straight"),
        ("T112",  "T112 - Flat Bar, Offset"),
        ("T120",  "T120 - Round Bar, Mitred Return"),
    ])
    options(conn, f_ppb, "size", [
        ("8",  "8\""),
        ("10", "10\""),
        ("12", "12\""),
        ("18", "18\""),
        ("24", "24\""),
        ("36", "36\""),
    ])
    options(conn, f_ppb, "finish", RW_FINISHES)
    options(conn, f_ppb, "mount", [
        ("TM","TM - Thru-Mount (Back-to-Back)"),
        ("SM","SM - Surface Mount"),
    ])

    # ══════════════════════════════════════════════════════════════
    # Kick Plates (expanded)
    # ══════════════════════════════════════════════════════════════
    f3 = fid(conn, "Rockwood", "Kick Plate",
             "Protection Plate",
             "{model} {height}x{width} {finish}",
             "Rockwood {model} {height} x {width} {finish}")

    slot(conn, f3, 1, "model",  "Model",     1)
    slot(conn, f3, 2, "height", "Height",    1)
    slot(conn, f3, 3, "width",  "Width",     1)
    slot(conn, f3, 4, "finish", "Finish",    1)
    slot(conn, f3, 5, "corner", "Corners",   1)

    options(conn, f3, "model", [
        ("K1050", "K1050 - Kick Plate, Stainless Steel"),
        ("K1000", "K1000 - Kick Plate, Aluminum"),
        ("K1100", "K1100 - Kick Plate, Brass / Bronze"),
    ])
    options(conn, f3, "height", [
        ("4", "4\""),  ("6", "6\""),  ("8", "8\""),
        ("10","10\""), ("12","12\""), ("16","16\""),
        ("18","18\""), ("20","20\""), ("24","24\""),
    ])
    options(conn, f3, "width", [
        ("20","20\""),  ("24","24\""),  ("28","28\""),
        ("30","30\""),  ("32","32\""),  ("34","34\""),
        ("36","36\""),  ("42","42\""),
    ])
    options(conn, f3, "finish", RW_PLATE_FINISHES)
    options(conn, f3, "corner", [("SQ","Square"),("RD","Rounded"),("BV","Beveled")])

    # ══════════════════════════════════════════════════════════════
    # Mop / Armor Plates (full range)
    # ══════════════════════════════════════════════════════════════
    f4 = fid(conn, "Rockwood", "Mop/Armor Plate",
             "Protection Plate",
             "{model} {height}x{width} {finish}",
             "Rockwood Mop/Armor Plate {model} {height} x {width} {finish}")

    slot(conn, f4, 1, "model",  "Model",    1)
    slot(conn, f4, 2, "height", "Height",   1)
    slot(conn, f4, 3, "width",  "Width",    1)
    slot(conn, f4, 4, "finish", "Finish",   1)

    options(conn, f4, "model", [
        ("K1050M","K1050M - Mop Plate, Stainless Steel"),
        ("K1000M","K1000M - Mop Plate, Aluminum"),
        ("K1050A","K1050A - Armor Plate, Stainless Steel"),
    ])
    options(conn, f4, "height", [
        ("4", "4\""),   ("6", "6\""),   ("8", "8\""),
        ("10","10\""),  ("12","12\""),  ("16","16\""),
        ("18","18\""),  ("20","20\""),  ("24","24\""),
        ("28","28\""),  ("34","34\""),  ("42","42\""),
    ])
    options(conn, f4, "width", [
        ("20","20\""),  ("24","24\""),  ("28","28\""),
        ("30","30\""),  ("32","32\""),  ("34","34\""),
        ("36","36\""),  ("42","42\""),
    ])
    options(conn, f4, "finish", RW_PLATE_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Flush Bolts
    # ══════════════════════════════════════════════════════════════
    f5 = fid(conn, "Rockwood", "Flush Bolt",
             "Door Accessory",
             "{model} {finish}",
             "Rockwood {model} Flush Bolt {finish}")

    slot(conn, f5, 1, "model",    "Model",      1)
    slot(conn, f5, 2, "length",   "Rod Length",  1)
    slot(conn, f5, 3, "finish",   "Finish",      1)

    options(conn, f5, "model", [
        ("555",   "555 - Flush Bolt, Standard"),
        ("557",   "557 - Flush Bolt, Heavy Duty"),
        ("560",   "560 - Flush Bolt, Automatic (Top)"),
        ("570",   "570 - Flush Bolt, Automatic (Bottom)"),
        ("580",   "580 - Flush Bolt, Self-Latching"),
        ("556",   "556 - Flush Bolt, Dust-Proof Strike"),
        ("550",   "550 - Surface Bolt"),
    ])
    options(conn, f5, "length", [
        ("12", "12\""), ("18", "18\""), ("24", "24\""),
    ])
    options(conn, f5, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Edge Pulls
    # ══════════════════════════════════════════════════════════════
    f6 = fid(conn, "Rockwood", "Edge Pull",
             "Pull / Push",
             "{model} {finish}",
             "Rockwood {model} Edge Pull {finish}")

    slot(conn, f6, 1, "model",   "Model",   1)
    slot(conn, f6, 2, "finish",  "Finish",  1)

    options(conn, f6, "model", [
        ("EP1",   "EP1 - Edge Pull, 1\" x 3-1/4\""),
        ("EP2",   "EP2 - Edge Pull, 2\" x 7\""),
        ("EP2HD", "EP2HD - Edge Pull, Heavy Duty, 2\" x 7\""),
        ("EP3",   "EP3 - Edge Pull, 1\" x 4\""),
        ("EP4",   "EP4 - Edge Pull, 1-1/4\" x 5\""),
    ])
    options(conn, f6, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Flush Pulls / Recessed Pulls
    # ══════════════════════════════════════════════════════════════
    f_fp = fid(conn, "Rockwood", "Flush Pull",
               "Pull / Push",
               "{model} {finish}",
               "Rockwood {model} Flush Pull {finish}")

    slot(conn, f_fp, 1, "model",  "Model",   1)
    slot(conn, f_fp, 2, "finish", "Finish",  1)

    options(conn, f_fp, "model", [
        ("870",   "870 - Flush Cup Pull, 1\" x 3-1/4\""),
        ("871",   "871 - Flush Cup Pull, 2\" x 7\""),
        ("872",   "872 - Flush Cup Pull, Round 3\" Dia"),
        ("875",   "875 - Flush Cup Pull, Oval 2\" x 4\""),
        ("876",   "876 - Flush Cup Pull, ADA Recessed, 4\" x 16\""),
    ])
    options(conn, f_fp, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Door Stops (Wall, Floor, Overhead)
    # ══════════════════════════════════════════════════════════════
    f7 = fid(conn, "Rockwood", "Door Stop",
             "Door Accessory",
             "{model} {finish}",
             "Rockwood {model} Door Stop {finish}")

    slot(conn, f7, 1, "model",  "Model",   1)
    slot(conn, f7, 2, "finish", "Finish",  1)

    options(conn, f7, "model", [
        ("403",   "403 - Wall Stop, Concave, Rubber Bumper"),
        ("409",   "409 - Wall Stop, Dome"),
        ("410",   "410 - Wall Stop, Dome, Heavy Duty"),
        ("085",   "085 - Wall Stop, Flat Tip"),
        ("470",   "470 - Floor Stop, Dome"),
        ("471",   "471 - Floor Stop, Dome, Heavy Duty"),
        ("441",   "441 - Floor Stop, Low Profile"),
        ("446",   "446 - Floor Stop, with Holder"),
        ("485",   "485 - Overhead Stop"),
        ("486",   "486 - Overhead Stop, Heavy Duty"),
        ("460",   "460 - Wall Stop & Holder, Magnetic"),
        ("461",   "461 - Wall Stop & Holder, Rigid"),
    ])
    options(conn, f7, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Door Guards / Bumpers / Corner Guards
    # ══════════════════════════════════════════════════════════════
    f8 = fid(conn, "Rockwood", "Door Guard / Corner Guard",
             "Door Protection",
             "{model} {size} {finish}",
             "Rockwood {model} Door Guard {size} {finish}")

    slot(conn, f8, 1, "model",  "Model",   1)
    slot(conn, f8, 2, "size",   "Size",    1)
    slot(conn, f8, 3, "finish", "Finish",  1)

    options(conn, f8, "model", [
        ("DG1",   "DG1 - Door Edge Guard, Standard"),
        ("DG2",   "DG2 - Door Edge Guard, Heavy Duty"),
        ("DG3",   "DG3 - Door Edge Guard, Full-Length"),
        ("CG10",  "CG10 - Corner Guard, Surface Mount"),
        ("CG20",  "CG20 - Corner Guard, Recessed"),
        ("CG30",  "CG30 - Corner Guard, Snap-On"),
    ])
    options(conn, f8, "size", [
        ("36","36\""),  ("42","42\""),  ("48","48\""),
        ("84","84\" (7'-0\")"),  ("96","96\" (8'-0\")"),
    ])
    options(conn, f8, "finish", RW_PLATE_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Closet / Shelf Hardware
    # ══════════════════════════════════════════════════════════════
    f_cl = fid(conn, "Rockwood", "Closet / Shelf Hardware",
               "Closet Hardware",
               "{model} {finish}",
               "Rockwood {model} {finish}")

    slot(conn, f_cl, 1, "model",  "Model",   1)
    slot(conn, f_cl, 2, "finish", "Finish",  1)

    options(conn, f_cl, "model", [
        ("CS10",  "CS10 - Closet Rod Support, Standard"),
        ("CS10HD","CS10HD - Closet Rod Support, Heavy Duty"),
        ("CS12",  "CS12 - Closet Rod Flange, Round"),
        ("CS15",  "CS15 - Closet Rod Bracket, Adjustable"),
        ("CS20",  "CS20 - Shelf Bracket, Fixed"),
        ("CS25",  "CS25 - Shelf Bracket, Adjustable"),
        ("CS30",  "CS30 - Rod & Shelf Bracket Combo"),
        ("HC10",  "HC10 - Hook, Coat, Single"),
        ("HC20",  "HC20 - Hook, Coat, Double"),
        ("HC30",  "HC30 - Hook, Coat, Heavy Duty"),
    ])
    options(conn, f_cl, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Barrier-Free / ADA Pulls
    # ══════════════════════════════════════════════════════════════
    f_bf = fid(conn, "Rockwood", "Barrier-Free / ADA Pull",
               "Pull / Push",
               "{model} {size} {finish}",
               "Rockwood {model} ADA Pull {size} {finish}")

    slot(conn, f_bf, 1, "model",  "Model",    1)
    slot(conn, f_bf, 2, "size",   "Size",     1)
    slot(conn, f_bf, 3, "finish", "Finish",   1)

    options(conn, f_bf, "model", [
        ("BF159",  "BF159 - ADA Straight Pull"),
        ("BF160",  "BF160 - ADA Offset Pull"),
        ("BF162",  "BF162 - ADA Offset Pull, Round"),
        ("BF165",  "BF165 - ADA D-Shape Pull"),
        ("BF170",  "BF170 - ADA Cranked Pull"),
        ("RM876",  "RM876 - ADA Recessed Pull (Flush)"),
    ])
    options(conn, f_bf, "size", [
        ("10", "10\" CTC"),
        ("12", "12\" CTC"),
        ("18", "18\" CTC"),
        ("24", "24\" CTC"),
    ])
    options(conn, f_bf, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Cabinet / Drawer Pulls
    # ══════════════════════════════════════════════════════════════
    f_cab = fid(conn, "Rockwood", "Cabinet / Drawer Pull",
                "Cabinet Hardware",
                "{model} {size} {finish}",
                "Rockwood {model} Cabinet Pull {size} {finish}")

    slot(conn, f_cab, 1, "model",  "Model",   1)
    slot(conn, f_cab, 2, "size",   "Size",    1)
    slot(conn, f_cab, 3, "finish", "Finish",  1)

    options(conn, f_cab, "model", [
        ("CP10",   "CP10 - Wire Pull, Round"),
        ("CP12",   "CP12 - Wire Pull, Flat"),
        ("CP15",   "CP15 - Cup Pull, Recessed"),
        ("CP20",   "CP20 - Bar Pull, Round"),
        ("CP22",   "CP22 - Bar Pull, Square"),
        ("CP25",   "CP25 - Knob, Round"),
        ("CP26",   "CP26 - Knob, Square"),
        ("CP30",   "CP30 - Appliance Pull, Long"),
        ("CP35",   "CP35 - Ring Pull"),
    ])
    options(conn, f_cab, "size", [
        ("3",     "3\" CTC"),
        ("3.75",  "3-3/4\" CTC"),
        ("5",     "5\" CTC"),
        ("6.25",  "6-5/16\" CTC"),
        ("8",     "8\" CTC"),
        ("12",    "12\" CTC"),
        ("18",    "18\" CTC"),
    ])
    options(conn, f_cab, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Handrail Brackets
    # ══════════════════════════════════════════════════════════════
    f_hr = fid(conn, "Rockwood", "Handrail Bracket",
               "Handrail / Railing",
               "{model} {finish}",
               "Rockwood {model} Handrail Bracket {finish}")

    slot(conn, f_hr, 1, "model",  "Model",     1)
    slot(conn, f_hr, 2, "finish", "Finish",    1)

    options(conn, f_hr, "model", [
        ("HB100",  "HB100 - Handrail Bracket, Standard Wall"),
        ("HB110",  "HB110 - Handrail Bracket, Heavy Duty"),
        ("HB200",  "HB200 - Handrail Bracket, ADA Compliant"),
        ("HB210",  "HB210 - Handrail Bracket, Adjustable"),
        ("HB300",  "HB300 - Handrail Bracket, Flat Base"),
        ("HB310",  "HB310 - Handrail Bracket, Round Base"),
    ])
    options(conn, f_hr, "finish", RW_FINISHES)

    # ══════════════════════════════════════════════════════════════
    # Coat / Hat Hooks
    # ══════════════════════════════════════════════════════════════
    f_hk = fid(conn, "Rockwood", "Coat / Hat Hook",
               "Door Accessory",
               "{model} {finish}",
               "Rockwood {model} Hook {finish}")

    slot(conn, f_hk, 1, "model",  "Model",   1)
    slot(conn, f_hk, 2, "finish", "Finish",  1)

    options(conn, f_hk, "model", [
        ("CH100",  "CH100 - Single Prong Coat Hook"),
        ("CH110",  "CH110 - Double Prong Coat Hook"),
        ("CH115",  "CH115 - Triple Prong Coat Hook, Institutional"),
        ("CH120",  "CH120 - Hat & Coat Hook, Heavy Duty"),
        ("CH130",  "CH130 - Robe Hook, Single"),
        ("CH140",  "CH140 - Robe Hook, ADA-Compliant"),
    ])
    options(conn, f_hk, "finish", RW_FINISHES)


# ═════════════════════════════════════════════════════════════════════
# Trimco
# ═════════════════════════════════════════════════════════════════════

def _seed_trimco(conn):
    # ── Hospital Push/Pull ──
    f = fid(conn, "Trimco", "1001A Hospital Push/Pull",
            "Pull / Push",
            "1001A {size} {finish}",
            "Trimco 1001A {size} {finish}")

    slot(conn, f, 1, "size",   "Size (CTC)",  1)
    slot(conn, f, 2, "finish", "Finish",       1)

    options(conn, f, "size", [
        ("8",  "8\" CTC"),
        ("10", "10\" CTC"),
        ("12", "12\" CTC"),
    ])

    finishes = [
        ("630", "630 - Satin Stainless"),
        ("626", "626 - Satin Chrome"),
        ("628", "628 - Satin Aluminum"),
        ("613", "613 - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    # ── Flush Pulls / Edge Pulls ──
    f2 = fid(conn, "Trimco", "Flush Pull / Edge Pull",
             "Pull / Push",
             "{model} {finish}",
             "Trimco {model} {finish}")

    slot(conn, f2, 1, "model",  "Model",   1)
    slot(conn, f2, 2, "finish", "Finish",  1)

    models = [
        ("1064",   "1064 - Flush Pull, 1\" x 3-1/4\""),
        ("1069",   "1069 - Flush Pull, 2\" x 7\""),
        ("1064-2", "1064-2 - Flush Pull, 1\" x 4\""),
        ("5002",   "5002 - Edge Pull"),
        ("5003",   "5003 - Edge Pull, Heavy Duty"),
    ]
    options(conn, f2, "model", models)
    options(conn, f2, "finish", finishes)

    # ── Push Plates ──
    f3 = fid(conn, "Trimco", "Push Plate",
             "Push / Pull Plate",
             "{model} {size} {finish}",
             "Trimco {model} {size} {finish}")

    slot(conn, f3, 1, "model",  "Model",   1)
    slot(conn, f3, 2, "size",   "Size",    1)
    slot(conn, f3, 3, "finish", "Finish",  1)

    options(conn, f3, "model", [
        ("1001",  "1001 - Round Corner"),
        ("1001B", "1001B - Beveled Edge"),
        ("1003",  "1003 - Square Corner"),
    ])
    options(conn, f3, "size", [
        ("3.5x15", "3-1/2\" x 15\""),
        ("4x16",   "4\" x 16\""),
        ("6x16",   "6\" x 16\""),
    ])
    options(conn, f3, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Don-Jo
# ═════════════════════════════════════════════════════════════════════

def _seed_donjo(conn):
    # ── Door Wraps ──
    f = fid(conn, "Don-Jo", "Door Wrap",
            "Door Wrap / Reinforcer",
            "{model} {finish}",
            "Don-Jo {model} {finish}")

    slot(conn, f, 1, "model",   "Model",           1)
    slot(conn, f, 2, "finish",  "Finish",           1)
    slot(conn, f, 3, "handing", "Handing",          0)

    models = [
        ("504-CW", "504-CW - Full Mortise Wrap-Around, 4-1/4\" x 9\""),
        ("514-CW", "514-CW - Full Mortise Wrap-Around, 4-3/4\" x 9\""),
        ("80-CW",  "80-CW - Cylindrical Lock Wrap-Around, 4-1/4\" x 9\""),
        ("81-CW",  "81-CW - Cylindrical Lock Wrap-Around, 4-3/4\" x 12\""),
        ("4-CW",   "4-CW - Deadbolt Wrap-Around"),
        ("13-CW",  "13-CW - Latch/Lock Combo Wrap-Around"),
    ]
    options(conn, f, "model", models)

    finishes = [
        ("630",  "630 - Satin Stainless"),
        ("628",  "628 - Satin Aluminum"),
        ("612",  "612 - Satin Bronze"),
        ("605",  "605 - Polished Brass"),
        ("613",  "613 - Oil Rubbed Bronze"),
    ]
    options(conn, f, "finish", finishes)

    options(conn, f, "handing", [("LH","Left Hand"),("RH","Right Hand")])

    # ── Latch Guards ──
    f2 = fid(conn, "Don-Jo", "Latch Guard / Protector",
             "Latch Guard",
             "{model} {finish}",
             "Don-Jo {model} {finish}")

    slot(conn, f2, 1, "model",  "Model",    1)
    slot(conn, f2, 2, "finish", "Finish",   1)

    guards = [
        ("LP-107",  "LP-107 - Latch Protector, 7\" Outswing"),
        ("LP-110",  "LP-110 - Latch Protector, 10\" Outswing"),
        ("LP-207",  "LP-207 - Latch Protector, 7\" Inswing"),
        ("LP-210",  "LP-210 - Latch Protector, 10\" Inswing"),
        ("PLP-111", "PLP-111 - Pin Latch Protector"),
    ]
    options(conn, f2, "model", guards)
    options(conn, f2, "finish", finishes)

    # ── Kick / Protection Plates ──
    f3 = fid(conn, "Don-Jo", "Protection Plate",
             "Protection Plate",
             "K-{height}x{width} {finish}",
             "Don-Jo Kick Plate {height} x {width} {finish}")

    slot(conn, f3, 1, "height", "Height",   1)
    slot(conn, f3, 2, "width",  "Width",    1)
    slot(conn, f3, 3, "finish", "Finish",   1)
    slot(conn, f3, 4, "corner", "Corners",  1)

    options(conn, f3, "height", [("6","6\""),("8","8\""),("10","10\""),("12","12\"")])
    options(conn, f3, "width", [
        ("28","28\""),("30","30\""),("32","32\""),
        ("34","34\""),("36","36\""),("42","42\""),
    ])
    options(conn, f3, "finish", finishes)
    options(conn, f3, "corner", [("SQ","Square"),("RD","Rounded"),("BV","Beveled")])
