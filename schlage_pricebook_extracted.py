"""
Schlage Pricebook 16 - Extracted Pricing Data
Effective February 27, 2026
Source: schlage_all_text.txt

IMPORTANT: The source file only contained data for:
  ALX, B250, B500, B600, CL, CS210, HL Series
  S Series (cylinder-only pricing, NOT complete locks)

NOT FOUND in file (no PDF sections present):
  PC Series, PM Series, PT Series, LM9200 Series
  These must come from separate pricebook PDFs.
"""

# =============================================================================
# ALX SERIES (Cylindrical)
# =============================================================================

ALX_SERIES = {
    "series": "ALX",
    "type": "cylindrical",
    "grade": 2,
    "default_cylinder": "P6",
    "default_keyway": "S123 (open)",

    # Finish groupings for 6-column pricing
    # Columns: [Tier1-Std, Tier2-Std, Tier3-Std, Tier1-Prem, Tier2-Prem, Tier3-Prem]
    # ALX has 6 price columns:
    #   Cols 1-3 = Standard levers (ATH, BRW, BRK, LAT, SAT, RHO, SPA, TLR)
    #   Cols 4-6 = Premium levers (LON, OME) - higher prices
    "finish_tiers": {
        "standard_lever": {  # ATH, BRW, BRK, LAT, SAT, RHO, SPA, TLR
            "tier_1": ["605", "606", "612", "619", "622", "625", "643e"],  # note: 606, 612, 625, 643e = extended lead time
            "tier_2": ["626"],
            "tier_3": ["613", "626AM"],  # 626AM = extended lead time
        },
        "premium_lever": {  # LON, OME
            "tier_1": ["605", "606", "612", "619", "622", "625", "643e"],
            "tier_2": ["626"],
            "tier_3": ["613", "626AM"],
        },
    },

    # Functions: {code: (description, [tier1_std, tier2_std, tier3_std, tier1_prem, tier2_prem, tier3_prem])}
    "functions": {
        # NON-KEYED
        "ALX10":   ("Passage latch",                          [295.00, 307.00, 325.00, 317.00, 329.00, 347.00]),
        "ALX40":   ("Bath/bedroom privacy lock",              [334.00, 346.00, 364.00, 356.00, 368.00, 386.00]),
        "ALXV40":  ("Vandlgard bath/bedroom privacy lock",    [334.00, 346.00, 364.00, 356.00, 368.00, 386.00]),
        "ALX44":   ("Hospital privacy lock",                  [334.00, 346.00, 364.00, 356.00, 368.00, 386.00]),
        "ALXV44":  ("Vandlgard hospital privacy lock",        [334.00, 346.00, 364.00, 356.00, 368.00, 386.00]),
        "ALX170":  ("Single dummy trim",                      [184.00, 190.00, 199.00, 195.00, 201.00, 210.00]),
        "ALX172":  ("Double dummy trim",                      [276.00, 288.00, 306.00, 298.00, 310.00, 328.00]),
        # KEYED (P6 cylinder included)
        "ALX25":   ("P6 Exit lock with exterior blank plate", [257.00, 263.00, 287.00, 268.00, 274.00, 287.00]),
        "ALX50":   ("P6 Entrance/office lock",                [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALXV50":  ("P6 Vandlgard entrance/office lock",      [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALX53":   ("P6 Entrance lock",                       [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALXV53":  ("P6 Vandlgard entrance lock",             [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALX70":   ("P6 Classroom lock",                      [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALXV70":  ("P6 Vandlgard classroom lock",            [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALX80":   ("P6 Storeroom lock",                      [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
        "ALXV80":  ("P6 Vandlgard storeroom lock",            [416.00, 428.00, 446.00, 438.00, 450.00, 468.00]),
    },

    "cylinder_adjustments": {
        # code: (description, open_adj, restricted_adj)
        # For ALX, single cylinder only
        "P6":    ("Conventional 6-pin cylinder",              0.00,    34.00),
        "P":     ("Conventional 6-pin cylinder, keyed 5",     0.00,    34.00),
        "Z":     ("Everest SL Conventional Cylinder, 7-pin",  None,    34.00),   # N/A for open
        "L":     ("Less conventional cylinder",               -103.00, None),     # single price
        "R":     ("FSIC (Full size interchangeable core)",    50.00,   84.00),
        "T":     ("FSIC - Construction Core",                 50.00,   None),     # N/A for restricted
        "M":     ("Everest SL - FSIC, 7-pin",                None,    84.00),
        "J":     ("Less FSIC",                                -66.00,  None),     # single price
        "G":     ("SFIC 7-pin",                               None,    69.00),
        "H":     ("Refundable Construction SFIC",             33.00,   None),
        "BDC":   ("Disposable Construction SFIC",             -66.00,  None),
        "B":     ("Less SFIC",                                -66.00,  None),     # single price
        "B-SAXC": ("Less SFIC for Sargent XC",               0.00,    None),
        "J-CO6": ("Less FSIC (LFIC) for Corbin Russwin 6-pin", 0.00, None),     # extended lead time
        "J-CO7": ("Less FSIC (LFIC) for Corbin Russwin 7-pin", 0.00, None),     # extended lead time
        "J-SA":  ("Less FSIC (LFIC) for Sargent 6-pin",      0.00,   None),     # extended lead time
        "J-SAXC": ("Less FSIC for Sargent XC",               0.00,   None),     # extended lead time
        "L-CO":  ("Less Conventional for Corbin Russwin",     0.00,   None),     # extended lead time
        "L-SA":  ("Less Conventional for Sargent",            0.00,   None),     # extended lead time
    },

    "lever_styles": {
        "standard": ["ATH", "BRW", "BRK", "LAT", "SAT", "RHO", "SPA", "TLR"],  # cols 1-3
        "premium": ["LON", "OME"],  # cols 4-6, higher prices
    },

    "tactile_options": {
        # code: (description, price_per_lever)
        "8AT": ("Athens tactile lever (Milled)",       77.00),
        "8BK": ("Boardwalk tactile lever (Knurled)",   77.00),
        "8BY": ("Broadway tactile lever (Knurled)",    77.00),
        "8LT": ("Latitude tactile lever (Milled)",    77.00),
        "8LN": ("Longitude tactile lever (Milled)",   77.00),
        "8RO": ("Rhodes tactile lever (Milled)",       77.00),
        "8SP": ("Sparta tactile lever (Milled)",       77.00),
        "8TR": ("Tubular tactile lever (Knurled)",     77.00),
    },

    "options": {
        "TORX":    ("Tamper resistant Torx screws for latch and strike", 36.00),
        "BAA":     ("Buy America Act Compliant",                         25.00),
        "PCL":     ("Pack cylinders loose in box",                       0.00),
        "SCRSTD":  ("Standard screws",                                   0.00),
    },

    "less_components": {
        "LLL_lever":       ("Less each knob or lever",  -20.70),
        "LLL_rose":        ("Less each rose or turn",   -15.20),
        "LLL_springlatch": ("Less spring latch",        -92.50),
        "LLL_deadlatch":   ("Less deadlatch",           -92.50),
        "LLL_strike":      ("Less strike",              -25.10),
    },
}


# =============================================================================
# B250 SERIES (Deadlatch / Night Latch)
# =============================================================================

B250_SERIES = {
    "series": "B250",
    "type": "deadlatch",

    "finish_tiers": {
        # 3 columns
        "tier_1": ["605", "606", "626", "622", "625"],  # 606, 622, 625 = extended lead time
        "tier_2": ["609"],  # extended lead time
        "tier_3": ["613"],
    },

    "functions": {
        # code: (description, [tier1, tier2, tier3])
        # SINGLE CYLINDER
        "B250":  ("P6 Single cylinder deadlatch (night latch)", [449.00, 455.00, 465.00]),
        # DOUBLE CYLINDER
        "B252":  ("P6 Double cylinder deadlatch",               [502.00, 508.00, 518.00]),
    },

    "cylinder_adjustments": {
        # code: (description, single_open, single_restricted, double_open, double_restricted)
        "P6":  ("Conventional 6-pin cylinder",          0.00,    34.00,   0.00,    68.00),
        "P5":  ("Conventional 5-pin cylinder",          0.00,    34.00,   0.00,    68.00),
        "Z":   ("Everest SL Conv Cylinder, 7-pin",     None,    34.00,   None,    68.00),
        "R":   ("FSIC",                                 71.00,   105.00,  142.00,  210.00),
        "T":   ("FSIC - Construction Core",             71.00,   None,    142.00,  None),
        "M":   ("Everest SL - FSIC, 7-pin",            None,    105.00,  None,    210.00),
        "J":   ("Less FSIC",                            -45.00,  None,    -90.00,  None),
    },

    "options": {
        "TORX":       ("Tamper resistant Torx screws for latch and strike",  36.00),
        "BAA":        ("Buy America Act Compliant",                          12.00),
        "XB03-330":   ("B250 for doors over 2-3/4\" - 5-9/16\"",           480.00),  # ext lead time
        "XB03-427":   ("B252 for doors over 2-3/4\" - 5-9/16\"",           534.00),  # ext lead time
        "XB09-062":   ("Less holdback function (B400 turn sub)",             88.00),
        "K510-066":   ("Plastic dust box for ANSI strike",                   0.00),
    },

    "less_components": {
        "LLL_deadlatch": ("Less deadlatch", -34.50),
        "LLL_strike":    ("Less strike",    -10.40),
    },
}


# =============================================================================
# B500 SERIES (Deadbolt - Grade 2)
# =============================================================================

B500_SERIES = {
    "series": "B500",
    "type": "deadbolt",
    "grade": 2,

    # 4 finish columns
    "finish_tiers": {
        "tier_1": ["605", "606", "609", "612", "619", "622", "625", "643e"],
        "tier_2": ["626"],
        "tier_3": ["613"],
        "tier_4": ["626AM"],  # extended lead time
    },

    # Base functions WITHOUT indicators
    "functions": {
        # KEYLESS
        "B572":   ("Door bolt with coin turn",                     [125.00, 131.00, 141.00, 181.00]),
        "B572F":  ("UL listed door bolt with coin turn",           [136.00, 142.00, 152.00, 192.00]),
        "B580":   ("Door bolt",                                    [106.00, 112.00, 122.00, 162.00]),
        "B580F":  ("UL listed door bolt",                          [117.00, 123.00, 133.00, 173.00]),
        "B581":   ("Door bolt with trim",                          [106.00, 112.00, 122.00, 162.00]),
        "B581F":  ("UL listed door bolt with trim",                [117.00, 123.00, 133.00, 173.00]),
        # SINGLE CYLINDER
        "B560":   ("P6 Single cylinder deadbolt",                  [136.00, 142.00, 152.00, 192.00]),
        "B560F":  ("P6 UL listed single cylinder deadbolt",        [147.00, 153.00, 163.00, 203.00]),
        "B561":   ("P6 Cylinder x blank plate deadbolt",           [136.00, 142.00, 152.00, 192.00]),
        "B561F":  ("P6 UL listed cyl x blank plate deadbolt",     [147.00, 153.00, 163.00, 203.00]),
        "B563":   ("P6 Classroom deadbolt",                        [145.00, 151.00, 161.00, 201.00]),
        "B563F":  ("P6 UL listed classroom deadbolt",              [156.00, 162.00, 172.00, 212.00]),
        # DOUBLE CYLINDER
        "B562":   ("P6 Double cylinder deadbolt",                  [184.00, 190.00, 200.00, 240.00]),
    },

    # Functions WITH indicators
    # (single_t1, dual_t1, single_t2, dual_t2, single_t3, dual_t3, single_t4, dual_t4)
    "functions_with_indicators": {
        # KEYLESS
        "B572":   ("Door bolt with coin turn",
                   {"SINGLE": [218.00, 224.00, 234.00, 274.00],
                    "DUAL":   [311.00, 317.00, 327.00, 367.00]}),
        "B572F":  ("UL listed door bolt with coin turn",
                   {"SINGLE": [229.00, 235.00, 245.00, 285.00],
                    "DUAL":   [322.00, 328.00, 338.00, 378.00]}),
        "B581":   ("Door bolt with trim (Inside indication only)",
                   {"SINGLE": [199.00, 205.00, 215.00, 255.00],
                    "DUAL":   None}),  # N/A
        "B581F":  ("UL listed door bolt with trim (Inside indication only)",
                   {"SINGLE": [210.00, 216.00, 226.00, 266.00],
                    "DUAL":   None}),  # N/A
        # SINGLE CYLINDER
        "B560":   ("P6 Single cylinder deadbolt",
                   {"SINGLE": [229.00, 235.00, 245.00, 285.00],
                    "DUAL":   [322.00, 328.00, 338.00, 378.00]}),
        "B560F":  ("P6 UL listed single cylinder deadbolt",
                   {"SINGLE": [240.00, 246.00, 256.00, 296.00],
                    "DUAL":   [333.00, 339.00, 349.00, 389.00]}),
        "B561":   ("P6 Cylinder x blank plate deadbolt",
                   {"SINGLE": [229.00, 235.00, 245.00, 285.00],
                    "DUAL":   None}),  # N/A
        "B561F":  ("P6 UL listed cylinder x blank plate deadbolt",
                   {"SINGLE": [240.00, 246.00, 256.00, 296.00],
                    "DUAL":   None}),  # N/A
        "B563":   ("P6 Classroom deadbolt",
                   {"SINGLE": [238.00, 244.00, 254.00, 294.00],
                    "DUAL":   None}),  # N/A
        "B563F":  ("P6 UL listed classroom deadbolt",
                   {"SINGLE": [249.00, 255.00, 265.00, 305.00],
                    "DUAL":   None}),  # N/A
        # DOUBLE CYLINDER
        "B562":   ("P6 Double cylinder deadbolt",
                   {"SINGLE": [277.00, 283.00, 293.00, 333.00],
                    "DUAL":   [370.00, 376.00, 386.00, 426.00]}),
    },

    "indicator_messages": {
        "IS-LOC": "Inside trim LOCKED/UNLOCKED",
        "OS-LOC": "Outside trim LOCKED/UNLOCKED",
        "IS-OCC": "Inside trim OCCUPIED/VACANT",
        "OS-OCC": "Outside trim OCCUPIED/VACANT",
        "IS-LOCFR": "Inside trim LOCKED/UNLOCKED (Française)",
        "OS-LOCFR": "Outside trim LOCKED/UNLOCKED (Française)",
    },

    "cylinder_adjustments": {
        # code: (description, single_open, single_restricted, double_open, double_restricted)
        "P6":  ("Conventional 6-pin cylinder",          0.00,    34.00,   0.00,    68.00),
        "P":   ("Conventional 6-pin, keyed 5",          0.00,    34.00,   0.00,    68.00),
        "Z":   ("Everest SL Conv Cylinder, 7-pin",      None,    34.00,   None,    68.00),
        "L":   ("Less conventional cylinder",            -23.00,  None,    -46.00,  None),
        "R":   ("FSIC",                                  190.00,  224.00,  380.00,  448.00),
        "T":   ("FSIC - Construction Core",              190.00,  None,    380.00,  None),
        "M":   ("Everest SL - FSIC, 7-pin",             None,    224.00,  None,    448.00),
        "J":   ("Less FSIC",                             57.00,   None,    114.00,  None),
        "G":   ("SFIC 7-pin",                            None,    146.00,  None,    292.00),
        "H":   ("Refundable Construction SFIC",          182.00,  None,    364.00,  None),
        "BDC": ("Disposable Construction SFIC",          57.00,   None,    114.00,  None),
        "B":   ("Less SFIC",                             57.00,   None,    114.00,  None),
    },

    "options": {
        "BAA":      ("Buy America Act Compliant",      12.00),
        "37-016":   ("Strike reinforcer",               0.00),
        "J250-028": ("2\" strike reinforcement screws", 0.00),
    },

    "less_components": {
        "LLL_deadbolt": ("Less deadbolt", -21.50),
        "LLL_strike":   ("Less strike",   -9.20),
    },
}


# =============================================================================
# B600 SERIES (Deadbolt - Grade 1)
# =============================================================================

B600_SERIES = {
    "series": "B600",
    "type": "deadbolt",
    "grade": 1,

    # 4 finish columns (same structure as B500)
    "finish_tiers": {
        "tier_1": ["605", "606", "609", "612", "619", "622", "625", "643e"],
        "tier_2": ["626"],
        "tier_3": ["613"],
        "tier_4": ["626AM"],  # extended lead time
    },

    # Base functions WITHOUT indicators
    "functions": {
        "B660":   ("P6 Single cylinder deadbolt",       [330.00, 336.00, 346.00, 378.00]),
        "B661":   ("P6 Cylinder x blank plate deadbolt", [330.00, 336.00, 346.00, 378.00]),
        "B662":   ("P6 Double cylinder deadbolt",        [423.00, 429.00, 439.00, 471.00]),
        "B663":   ("P6 Classroom deadbolt",              [343.00, 349.00, 359.00, 391.00]),
        "B664":   ("P6 Cylinder only deadbolt",          [330.00, 333.00, 338.00, 378.00]),
        "B672":   ("Door bolt with coin turn",           [319.00, 322.00, 327.00, 367.00]),
        "B680":   ("Door bolt",                          [257.00, 260.00, 265.00, 281.00]),
    },

    # Functions WITH indicators
    "functions_with_indicators": {
        # KEYLESS
        "B672":  ("UL listed door bolt with coin turn",
                  {"SINGLE": [412.00, 415.00, 420.00, 460.00],
                   "DUAL":   [505.00, 508.00, 513.00, 553.00]}),
        # SINGLE CYLINDER
        "B660":  ("P6 UL listed single cylinder deadbolt",
                  {"SINGLE": [423.00, 429.00, 439.00, 471.00],
                   "DUAL":   [516.00, 522.00, 532.00, 564.00]}),
        "B661":  ("P6 UL listed cyl x blank plate deadbolt (outside indication only)",
                  {"SINGLE": [423.00, 429.00, 439.00, 471.00],
                   "DUAL":   None}),  # N/A
        "B663":  ("P6 UL listed classroom deadbolt (outside indication only)",
                  {"SINGLE": [436.00, 442.00, 452.00, 484.00],
                   "DUAL":   None}),  # N/A
        # DOUBLE CYLINDER
        "B662":  ("P6 UL listed double cylinder deadbolt",
                  {"SINGLE": [516.00, 522.00, 532.00, 564.00],
                   "DUAL":   [609.00, 615.00, 625.00, 657.00]}),
    },

    "cylinder_adjustments": {
        # code: (description, single_open, single_restricted, double_open, double_restricted)
        "P6":  ("Conventional 6-pin cylinder",           0.00,    34.00,   0.00,    68.00),
        "P":   ("Conventional 6-pin, keyed 5",           0.00,    34.00,   0.00,    68.00),
        "Z":   ("Everest SL Conv Cylinder, 7-pin",       None,    34.00,   None,    68.00),
        "L":   ("Less conventional cylinder",             -80.00,  None,    -160.00, None),
        "R":   ("FSIC (not compatible with B664)",        47.00,   81.00,   94.00,   162.00),
        "T":   ("FSIC - Construction Core (not B664)",    47.00,   None,    94.00,   None),
        "M":   ("Everest SL - FSIC, 7-pin (not B664)",   None,    81.00,   None,    162.00),
        "J":   ("Less FSIC (not B664)",                   -69.00,  None,    -138.00, None),
        "G":   ("SFIC 7-pin (not B664)",                  None,    135.00,  None,    270.00),
        "H":   ("Refundable Construction SFIC (not B664)", 70.00,  None,    140.00,  None),
        "BDC": ("Disposable Construction SFIC (not B664)", 0.00,   None,    0.00,    None),
        "B":   ("Less SFIC",                               0.00,   None,    0.00,    None),
    },

    "options": {
        "TORX":     ("Tamper resistant Torx screws",    36.00),
        "BAA":      ("Buy America Act Compliant",        12.00),
        "SCRSTD":   ("Standard screws",                  0.00),
        "37-016":   ("Strike reinforcer",                0.00),
        "J250-028": ("2\" strike reinforcement screws",  0.00),
    },

    "less_components": {
        "LLL_deadbolt": ("Less deadbolt", -30.20),
        "LLL_strike":   ("Less strike",   -10.60),
    },
}


# =============================================================================
# CL SERIES (Cabinet Lock)
# =============================================================================

CL_SERIES = {
    "series": "CL",
    "type": "cabinet_lock",

    "finish_tiers": {
        "tier_1": ["605", "626"],  # Only 2 finishes for most CL products
    },

    "functions_conventional": {
        # code: (description, open_price, restricted_price)
        "CL100PB":  ("Door cabinet lock, 6-pin cylinder, 1\" bolt throw",   237.00, 271.00),
        "CL200PB":  ("Drawer cabinet lock, 6-pin cylinder, 3/4\" bolt throw", 237.00, 271.00),
    },

    "functions_primus_controlled": {
        # code: (description, price)  -- Primus/Primus XP restricted only
        "CL174PB":     ("Door cabinet lock, 6-pin, 1\" bolt throw (Primus)",     359.00),
        "CL174PB-XP":  ("Door cabinet lock, 6-pin, 1\" bolt throw (Primus XP)",  359.00),
        "CL274PB":     ("Drawer cabinet lock, 6-pin, 3/4\" bolt throw (Primus)",  359.00),
        "CL274PB-XP":  ("Drawer cabinet lock, 6-pin, 3/4\" bolt throw (Primus XP)", 359.00),
    },

    "functions_primus_ul437": {
        # code: (description, price) -- Primus/Primus XP High Security UL 437
        "CL154PB":     ("Door cabinet lock, 6-pin, 1\" bolt throw (Primus UL437)",    428.00),
        "CL154PB-XP":  ("Door cabinet lock, 6-pin, 1\" bolt throw (Primus XP UL437)", 428.00),
        "CL254PB":     ("Drawer cabinet lock, 6-pin, 3/4\" bolt throw (Primus UL437)", 428.00),
        "CL254PB-XP":  ("Drawer cabinet lock, 6-pin, 3/4\" bolt throw (Primus XP UL437)", 428.00),
    },

    "functions_fsic": {
        # code: (description, open_price, restricted_price)
        "CL777R":  ("Door cabinet lock, FSIC, 1\" bolt throw",      275.00, 309.00),
        "CL888R":  ("Drawer cabinet lock, FSIC, 3/4\" bolt throw",  275.00, 309.00),
        "CL920R":  ("FSIC Cam Lock",                                224.00, 258.00),
    },

    "functions_fsic_primus": {
        # code: (description, price) - Primus/Primus XP
        "CL774R":     ("Door cabinet lock, FSIC, 1\" bolt throw (Primus)",      397.00),
        "CL774R-XP":  ("Door cabinet lock, FSIC, 1\" bolt throw (Primus XP)",   397.00),
        "CL874R":     ("Drawer cabinet lock, FSIC, 3/4\" bolt throw (Primus)",  397.00),
        "CL874R-XP":  ("Drawer cabinet lock, FSIC, 3/4\" bolt throw (Primus XP)", 397.00),
        "CL974R":     ("FSIC Cam Lock (Primus)",                                 346.00),
        "CL974R-XP":  ("FSIC Cam Lock (Primus XP)",                              346.00),
    },

    "functions_fsic_ratchet": {
        # code: (description, open_price, restricted_price)
        "CL929R":  ("Ratchet Lock, FSIC", 290.00, 324.00),
    },

    "fsic_options": {
        "T_suffix": ("Full Size Construction Core", 0.00),
        "J_suffix": ("Less Full Size Core",         -33.00),
    },

    "functions_sfic": {
        # Finishes: 626 only
        # code: (description, open_price)
        "CL721G":  ("Door cabinet lock, SFIC, 1\" bolt throw",           248.00),
        "CL771G":  ("Drawer cabinet lock, SFIC, 3/4\" bolt throw",       248.00),
        "CL725G":  ("Everest Patented SFIC Rim Latch Lock",              248.00),
        "CL775G":  ("Everest Patented SFIC Rim Deadbolt Lock",           248.00),
        "CL720G":  ("Everest Patented SFIC Cam Lock",                    231.00),
        "CL728G":  ("Everest Patented SFIC Mail Box Lock",               184.00),
        "CL729G":  ("Everest Patented SFIC Ratchet Lock",                297.00),
    },

    "options": {
        "1-3/8_door": ("Lock for 1-3/8\" door", 5.10),
    },

    "special_locks": {
        "XB03-232":  ("Cabinet Lock for doors 1/8\" to 3/4\" thick",          969.00),
        "XB03-232P": ("Primus Cabinet Lock for doors 1/8\" to 3/4\" thick",   969.00),
        "XB06-530":  ("Cabinet Lock for doors over 7/8\" to 2\" thick",       1166.00),
        "XB06-530P": ("Primus Cabinet Lock for doors over 7/8\" to 2\" thick", 1166.00),
    },
}


# =============================================================================
# CS210 SERIES (Interconnect)
# =============================================================================

CS210_SERIES = {
    "series": "CS210",
    "type": "interconnect",

    "finish_tiers": {
        # 2 columns
        "tier_1": ["626"],
        "tier_2": ["605", "609", "619", "622", "625", "643e"],  # most extended lead time
    },

    "lever_styles": [
        "ACC", "AVA", "BRK", "BRW", "CHP", "CLT",
        "ELA", "FLA", "JAZ", "JUP", "LAT", "LON",
        "MER", "MNH", "NEP", "SAT", "STA", "VLA",
    ],

    "functions": {
        # code: (description, [tier1, tier2])
        "CS210-B60":  ("Entrance, single locking, with residential spin ring", [672.00, 685.00]),
        "CS210-B500": ("Entrance, single locking, with commercial spin ring",  [672.00, 685.00]),
    },

    "cylinder_adjustments": {
        # code: (description, single_open, single_restricted)
        "P6":  ("Conventional 6-pin cylinder",          0.00,    34.00),
        "P":   ("Conventional 6-pin, keyed 5",          0.00,    34.00),
        "Z":   ("Everest SL Conv Cylinder, 7-pin",      None,    34.00),
        "L":   ("Less conventional cylinder",            -103.00, None),
        "R":   ("FSIC",                                  50.00,   84.00),
        "T":   ("FSIC - Construction Core",              50.00,   None),
        "M":   ("Everest SL - FSIC, 7-pin",             None,    84.00),
        "J":   ("Less FSIC",                             -66.00,  None),
        "G":   ("SFIC 7-pin",                            None,    135.00),
        "H":   ("Refundable Construction SFIC",          70.00,   None),
        "BDC": ("Disposable Construction SFIC",          0.00,    None),
        "B":   ("Less SFIC",                             0.00,    None),
    },

    "options": {
        "BAA":      ("Buy America Act Compliant",         25.00),
        "PCL":      ("Pack cylinders loose in box",        0.00),
        "K510-066": ("Plastic dust box for ANSI strike",   0.00),
    },

    "less_components": {
        "LLL_deadbolt_strike":  ("Less deadbolt strike",   0.00),
        "LLL_deadlatch_strike": ("Less deadlatch strike",  0.00),
        "LLL_both_levers":      ("Less both levers",       -9.90),
    },
}


# =============================================================================
# HL SERIES (Hospital Latch)
# =============================================================================

HL_SERIES = {
    "series": "HL",
    "type": "hospital_latch",

    # TUBULAR (BORED) HOSPITAL LATCH
    "tubular_finish_tiers": {
        "tier_1": ["626"],
        "tier_2": ["605", "606", "612", "625"],
        "tier_3": ["613", "629", "630"],
    },

    "tubular_functions": {
        # HL6 PUSH/PULL LATCH
        "HL6-2":   ("Push/pull latch - 2-3/4\" backset",      [573.00, 585.00, 603.00]),
        "HL6-3":   ("Push/pull latch - 3-3/4\" backset",      [573.00, 585.00, 603.00]),
        "HL6-5":   ("Push/pull latch - 5\" backset",          [573.00, 585.00, 603.00]),
        "HL6-7":   ("Push/pull latch - 7\" backset",          [654.00, 666.00, 684.00]),
        # PL7 PRIVACY (Push side thumbturn)
        "PL7-2":   ("Push side thumbturn - 2-3/4\" backset",  [747.00, 759.00, 777.00]),
        "PL7-3":   ("Push side thumbturn - 3-3/4\" backset",  [747.00, 759.00, 777.00]),
        "PL7-5":   ("Push side thumbturn - 5\" backset",      [747.00, 759.00, 777.00]),
        "PL7-7":   ("Push side thumbturn - 7\" backset",      [832.00, 844.00, 862.00]),
        # PL8 PRIVACY (Pull side thumbturn)
        "PL8-2":   ("Pull side thumbturn - 2-3/4\" backset",  [747.00, 759.00, 777.00]),
        "PL8-3":   ("Pull side thumbturn - 3-3/4\" backset",  [747.00, 759.00, 777.00]),
        "PL8-5":   ("Pull side thumbturn - 5\" backset",      [747.00, 759.00, 777.00]),
        "PL8-7":   ("Pull side thumbturn - 7\" backset",      [832.00, 844.00, 862.00]),
    },

    # MORTISE HOSPITAL LATCH (HL6 + L Series mortise lock)
    "mortise_finish_tiers": {
        "tier_1": ["626"],
        "tier_2": ["605", "606", "612", "625"],
        "tier_3": ["613", "630"],
    },

    "mortise_functions": {
        # code: (description, [tier1, tier2, tier3])
        "HL6-9010":     ("Passage function",                                    [1564.00, 1576.00, 1594.00]),
        "HL6-9040":     ("Privacy function (thumbturn)",                         [1636.00, 1648.00, 1666.00]),
        "HL6-9050":     ("Office/inner entry function (thumbturn)",              [1636.00, 1648.00, 1666.00]),
        "HL6-9060":     ("Apartment entrance function",                          [1564.00, 1576.00, 1594.00]),
        "HL6-9070":     ("Classroom function",                                   [1564.00, 1576.00, 1594.00]),
        "HL6-9080":     ("Storeroom function",                                   [1564.00, 1576.00, 1594.00]),
        "HL6-9082":     ("Institution function",                                 [1564.00, 1576.00, 1594.00]),
        "HL6-9092EL/EU": ("Storeroom function with electric locking/unlocking",  [2723.00, 2735.00, 2753.00]),
        "HL6-9095EL/EU": ("Institution function with electric locking/unlocking", [2723.00, 2735.00, 2753.00]),
        "HL6-9453":     ("Entrance function (thumbturn)",                        [1636.00, 1648.00, 1666.00]),
        "HL6-9456":     ("Dormitory exit function (thumbturn)",                  [1636.00, 1648.00, 1666.00]),
        "HL6-9465":     ("Closet/storeroom function",                            [1636.00, 1648.00, 1666.00]),
        "HL6-9466":     ("Store/utility function",                               [1636.00, 1648.00, 1666.00]),
        "HL6-9473":     ("Dorm bedroom function (thumbturn)",                    [1636.00, 1648.00, 1666.00]),
        "HL6-9485":     ("Faculty restroom/hotel lock (thumbturn)",              [1636.00, 1648.00, 1666.00]),
        "HL6-9486":     ("Faculty restroom/hotel lock (thumbturn)",              [1636.00, 1648.00, 1666.00]),
        # PADDLES ONLY / LESS MORTISE LOCK
        "HL6-9000RK":   ("Mortise paddles only / less mortise lock",             [673.00, 685.00, 703.00]),
        "HL6-9000RK-95": ("Mortise paddles only / less mortise lock (L9095)",    [673.00, 685.00, 703.00]),
        # VON DUPRIN PULL LATCH
        "HL6Q-7500":    ("Pull latch for Von Duprin Exit Device",                [437.00, 449.00, 467.00]),
    },

    # NOTE: Cylinders are NOT included with mortise push-pull latches. Order separately.
    # See L Series mortise cylinders in Cylinders section.

    "options": {
        # code: (description, tubular_adj, mortise_adj)
        "A":    ("ASA strike, ANSI 115.1",                   0.00,     None),     # tubular only
        "AS":   ("Both standard and ASA strikes",            49.40,    None),     # tubular only
        "B":    ("Brass base material on 626",               91.50,    91.50),
        "BT":   ("Bent Tab for Mortise Lock Strike",         None,     106.40),   # mortise only
        "E1-E6": ("Engraved push and pull",                  91.50,    91.50),
        "EN":   ("Pull only latch",                          -113.00,  -258.00),
        "EO":   ("Push only latch",                          -113.00,  -258.00),
        "LL":   ("Lead lining",                              171.00,   834.00),
        "RX":   ("Request to Exit for HL6-9092 or 9095",     None,     273.00),   # mortise only
        "SOC":  ("Pin-in-socket security screws",            49.90,    49.90),
        "AM":   ("Antimicrobial finish (626AM or 630AM)",    83.80,    83.80),
    },
}


# =============================================================================
# S SERIES - Cylinder-Only Pricing (no complete lock data in file)
# =============================================================================

S_SERIES_CYLINDERS = {
    "series": "S",
    "type": "cylindrical",
    "note": "Only cylinder-only pricing found in file. Complete lock pricing not in schlage_all_text.txt.",

    "conventional_cylinders": {
        # Keyed Levers
        "standard": {
            "part": "21-059",
            "open": 103.00,
            "restricted": 137.00,
        },
        "primus": {
            "part_standard": "20-752",
            "part_xp": "20-752-XP",
            "part_rp": "20-752-RP",
            "price": 225.00,
        },
        "primus_ul437": {
            "part_standard": "20-552",
            "part_xp": "20-552-XP",
            "part_rp": "20-552-RP",
            "price": 294.00,
        },
        "sl": {
            "part": "91-007",
            "price": 137.00,
        },
        "sl_primus": {
            "part": "91-722-XP",
            "price": 225.00,
        },
    },
}


# =============================================================================
# SERIES NOT FOUND IN FILE
# =============================================================================

MISSING_SERIES = {
    "PC":     "PC Series - NOT FOUND in schlage_all_text.txt (no PDF section present)",
    "PM":     "PM Series - NOT FOUND in schlage_all_text.txt (no PDF section present)",
    "PT":     "PT Series - NOT FOUND in schlage_all_text.txt (no PDF section present)",
    "LM9200": "LM9200 Series - NOT FOUND in schlage_all_text.txt (only referenced in L Series cylinder section)",
}


# =============================================================================
# ALL SERIES DICT (for iteration)
# =============================================================================

ALL_EXTRACTED_SERIES = {
    "ALX": ALX_SERIES,
    "B250": B250_SERIES,
    "B500": B500_SERIES,
    "B600": B600_SERIES,
    "CL": CL_SERIES,
    "CS210": CS210_SERIES,
    "HL": HL_SERIES,
    "S_CYLINDERS": S_SERIES_CYLINDERS,
}
