"""Seed Schlage ND Series cylindrical lock data.

Schlage ND Series — Grade 1 cylindrical (bored) lockset.
Part number: ND{function} {lever}{rose} {finish}
"""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all, price, price_bulk


# ── Standard BHMA finishes shared across Schlage ──
SCHLAGE_FINISHES = [
    ("605",  "605 - Bright Brass"),
    ("606",  "606 - Satin Brass"),
    ("612",  "612 - Satin Bronze"),
    ("613",  "613 - Oil Rubbed Bronze"),
    ("619",  "619 - Satin Nickel"),
    ("622",  "622 - Flat Black"),
    ("625",  "625 - Bright Chrome"),
    ("626",  "626 - Satin Chrome"),
    ("626AM","626AM - Antimicrobial Satin Chrome"),
    ("629",  "629 - Bright Stainless"),
    ("630",  "630 - Satin Stainless (HSLR)"),
    ("643e", "643e - Aged Bronze"),
]


def seed(conn):
    _seed_nd_cylindrical(conn)
    print("  Schlage ND Series seeded.")


def _seed_nd_cylindrical(conn):
    f = fid(conn,
            "Schlage",
            "ND Series Cylindrical Lock",
            "Cylindrical Lockset",
            "{function} {lever}{rose} {finish}",
            "Schlage ND Series {function} {lever}{rose} {finish}")

    # ── Slots ──
    slot(conn, f, 1, "function",      "Function",      1)
    slot(conn, f, 2, "cylinder_type", "Cylinder Type",  0)  # optional, hidden for non-keyed
    slot(conn, f, 3, "lever",         "Lever Design",   1)
    slot(conn, f, 4, "rose",          "Rose / Escutcheon", 1)
    slot(conn, f, 5, "finish",        "Finish",         1)

    # ── Functions ──
    functions = [
        # Non-keyed
        ("ND10S",    "ND10S - Passage"),
        ("ND12S",    "ND12S - Exit Lock (lever × lever)"),
        ("ND12EL",   "ND12EL - Exit Lock, Electrically Locked"),
        ("ND12EU",   "ND12EU - Exit Lock, Electrically Unlocked"),
        ("ND25D",    "ND25D - Exit Lock (blank × lever)"),
        ("ND30S",    "ND30S - Patio Lock"),
        ("ND40S",    "ND40S - Privacy / Bath"),
        ("ND44S",    "ND44S - Hospital Privacy"),
        ("ND170",    "ND170 - Single Dummy Trim"),
        ("ND172",    "ND172 - Double Dummy Trim"),
        # Keyed single cylinder
        ("ND25x70",  "ND25x70 - Classroom Exit Lock"),
        ("ND25x80",  "ND25x80 - Storeroom Exit Lock"),
        ("ND50PD",   "ND50PD - Entry / Office"),
        ("ND53PD",   "ND53PD - Entrance"),
        ("ND60PD",   "ND60PD - Vestibule / Apartment"),
        ("ND70PD",   "ND70PD - Classroom"),
        ("ND73PD",   "ND73PD - Corridor"),
        ("ND75PD",   "ND75PD - Classroom Security (360° Key)"),
        ("ND78PD",   "ND78PD - Classroom Security (180° Key)"),
        ("ND80PD",   "ND80PD - Storeroom"),
        ("ND80EL",   "ND80EL - Storeroom, Electrically Locked"),
        ("ND80EU",   "ND80EU - Storeroom, Electrically Unlocked"),
        ("ND81PD",   "ND81PD - Accessible Storeroom"),
        ("ND82PD",   "ND82PD - Institution"),
        ("ND85PD",   "ND85PD - Faculty Restroom"),
        # Vandlgard
        ("ND91PD",   "ND91PD - Entry / Office (Vandlgard)"),
        ("ND92PD",   "ND92PD - Entrance (Vandlgard)"),
        ("ND94PD",   "ND94PD - Classroom (Vandlgard)"),
        ("ND95PD",   "ND95PD - Classroom Security (Vandlgard)"),
        ("ND96PD",   "ND96PD - Storeroom (Vandlgard)"),
        ("ND96EL",   "ND96EL - Storeroom, Electrically Locked (VG)"),
        ("ND96EU",   "ND96EU - Storeroom, Electrically Unlocked (VG)"),
        ("ND97PD",   "ND97PD - Corridor (Vandlgard)"),
        ("ND98PD",   "ND98PD - Classroom Security 180° (Vandlgard)"),
        # Keyed double cylinder
        ("ND60PD2",  "ND60PD (Dbl Cyl) - Vestibule Lock"),
        ("ND66PD",   "ND66PD - Store Lock"),
        ("ND70x80",  "ND70x80 - Classroom × Storeroom"),
        ("ND72PD",   "ND72PD - Communicating Lock"),
        ("ND72VG",   "ND72VG - Communicating (Vandlgard)"),
        ("ND93PD",   "ND93PD - Vestibule (Vandlgard)"),
    ]
    options(conn, f, "function", functions)

    # ── Cylinder Type ──
    cylinder_types = [
        ("C",   "C - Conventional 6-Pin (C Keyway)"),
        ("CE",  "CE - Conventional Everest"),
        ("CP",  "CP - Conventional Primus"),
        ("CEP", "CEP - Conventional Everest Primus"),
        ("J",   "J - Less FSIC"),
        ("R",   "R - FSIC Construction Core"),
        ("F",   "F - FSIC 6-Pin"),
        ("FE",  "FE - FSIC Everest"),
        ("FP",  "FP - FSIC Primus"),
        ("FEP", "FEP - FSIC Everest Primus"),
        ("G",   "G - SFIC 7-Pin"),
        ("H",   "H - SFIC Construction Core"),
        ("BD",  "BD - SFIC Best-Type D Core"),
        ("B",   "B - Less SFIC"),
        ("L",   "L - Less Cylinder"),
    ]
    options(conn, f, "cylinder_type", cylinder_types)

    # Non-keyed functions → hide cylinder
    non_keyed = {"ND10S", "ND12S", "ND12EL", "ND12EU", "ND25D",
                 "ND30S", "ND40S", "ND44S", "ND170", "ND172"}
    for func_val in non_keyed:
        for ct in cylinder_types:
            rule(conn, f, "conflict", "function", func_val, "cylinder_type", ct[0],
                 "No cylinder for non-keyed function")

    # ── Lever Designs ──
    levers = [
        ("ATH", "ATH - Athens"),
        ("SPA", "SPA - Sparta"),
        ("RHO", "RHO - Rhodes"),
        ("TLR", "TLR - Tubular Return"),
        ("BRW", "BRW - Broadway"),
        ("LON", "LON - Longitude"),
        ("LAT", "LAT - Latitude"),
        ("ACC", "ACC - Accent"),
        ("MER", "MER - Merano"),
        ("OME", "OME - Omega"),
        ("GRW", "GRW - Greenwich"),
        ("JUP", "JUP - Jupiter (Healthcare)"),
        ("SAT", "SAT - Saturn (Healthcare)"),
        ("NEP", "NEP - Neptune (Healthcare)"),
    ]
    options(conn, f, "lever", levers)

    # ── Rose / Escutcheon ──
    roses = [
        ("RLD", "RLD - Standard Round Rose"),
        ("SPA", "SPA - Sectional Rose"),
        ("ECS", "ECS - Escutcheon Plate"),
        ("BVD", "BVD - Beveled Edge Rose"),
        ("VAN", "VAN - Vandlgard Rose"),
    ]
    options(conn, f, "rose", roses)

    # ── Finishes ──
    options(conn, f, "finish", SCHLAGE_FINISHES)

    # ── Finish restrictions for select lever designs ──
    # Longitude/Latitude/Merano/Accent → limited finishes
    limited_finish_levers = ["LON", "LAT", "MER", "ACC"]
    limited_finishes = ["605", "606", "612", "613", "619", "625", "626"]
    for lev in limited_finish_levers:
        restrict(conn, f, "lever", lev, "finish", limited_finishes,
                 "Limited finishes for designer lever")

    # Healthcare levers (JUP/SAT/NEP) → 626 and 630 typically
    healthcare_finishes = ["619", "625", "626"]
    for lev in ["JUP", "SAT", "NEP"]:
        restrict(conn, f, "lever", lev, "finish", healthcare_finishes,
                 "Healthcare lever finish restriction")

    # 630 (HSLR) only available with HSLR lever (TLR-like / RHO etc)
    # Per price book, 630 is available on all standard levers but at much
    # higher price — no restriction needed, just a price adder.

    # ==============================================================
    # PRICING — 2026 Schlage ND Series Price Book (effective 2/27/26)
    # ==============================================================
    # Base prices per function (at 626 finish, P6 cylinder for keyed)
    _function_base_prices = [
        # Non-keyed
        ("ND10S",    719.00),
        ("ND12S",    734.00),
        ("ND12EL",  1164.00),
        ("ND12EU",  1164.00),
        ("ND25D",    661.00),
        ("ND30S",   2327.00),
        ("ND40S",    829.00),
        ("ND44S",    829.00),
        ("ND170",    201.00),
        ("ND172",    313.00),
        # Keyed single cylinder
        ("ND25x70", 1625.00),
        ("ND25x80", 1625.00),
        ("ND50PD",   981.00),
        ("ND53PD",   981.00),
        ("ND60PD",  1793.00),
        ("ND70PD",   981.00),
        ("ND73PD",   981.00),
        ("ND75PD",  1167.00),
        ("ND78PD",  1167.00),
        ("ND80PD",   981.00),
        ("ND80EL",  1351.00),
        ("ND80EU",  1351.00),
        ("ND81PD",   981.00),
        ("ND82PD",  1167.00),
        ("ND85PD",  1173.00),
        # Vandlgard
        ("ND91PD",  1073.00),
        ("ND92PD",  1073.00),
        ("ND94PD",  1073.00),
        ("ND95PD",  1257.00),
        ("ND96PD",  1073.00),
        ("ND96EL",  1484.00),
        ("ND96EU",  1484.00),
        ("ND97PD",  1073.00),
        ("ND98PD",  1257.00),
        # Double cylinder
        ("ND60PD2", 1167.00),
        ("ND66PD",  1167.00),
        ("ND70x80", 1812.00),
        ("ND72PD",  1940.00),
        ("ND72VG",  2032.00),
        ("ND93PD",  1257.00),
    ]
    price_bulk(conn, f, "function", _function_base_prices, price_type="base")

    # Finish adders (relative to 626 base)
    _finish_adders = [
        ("626",    0.00),
        ("605",   12.00),
        ("606",   12.00),
        ("612",   12.00),
        ("619",   12.00),
        ("622",   12.00),
        ("625",   12.00),
        ("629",   12.00),
        ("643e",  12.00),
        ("613",   30.00),
        ("626AM", 30.00),
        ("630", 1915.00),
    ]
    price_bulk(conn, f, "finish", _finish_adders, price_type="adder")

    # Cylinder type adders (open keyway, single cylinder)
    _cyl_adders = [
        ("C",    0.00),    # P6 conventional included in base
        ("CE",   0.00),    # conventional Everest same price
        ("CP",   0.00),    # Primus — order separately
        ("CEP",  0.00),
        ("L",  -103.00),   # Less conventional cylinder
        ("J",   -66.00),   # Less FSIC
        ("R",    50.00),   # FSIC construction core
        ("F",    50.00),   # FSIC 6-pin
        ("FE",   84.00),   # FSIC Everest 7-pin
        ("FP",   84.00),   # FSIC Primus
        ("FEP",  84.00),
        ("G",    69.00),   # SFIC 7-pin
        ("H",    33.00),   # Refundable construction SFIC
        ("BD",  -66.00),   # Disposable construction SFIC
        ("B",   -66.00),   # Less SFIC
    ]
    price_bulk(conn, f, "cylinder_type", _cyl_adders, price_type="adder")
