"""Hager expanded product lines — stops, kick plates, pulls, closers,
flush bolts, coordinators, overhead stops, thresholds, and protection plates.

Run via:  python tools/seed_all.py
"""

from seed_helpers import fid, slot, options, restrict, rule

# =====================================================================
# Shared finish palettes
# =====================================================================
HAGER_ARCH_FINISHES = [
    ("US26D", "US26D - Satin Chrome"),
    ("US32D", "US32D - Satin Stainless"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US3",   "US3 - Polished Brass"),
    ("US26",  "US26 - Polished Chrome"),
    ("US4",   "US4 - Satin Brass"),
    ("US15",  "US15 - Satin Nickel"),
    ("USP",   "USP - Primed"),
]

HAGER_SS_FINISHES = [
    ("US32D", "US32D - Satin Stainless"),
    ("US26D", "US26D - Satin Chrome"),
    ("US3",   "US3 - Polished Brass"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US4",   "US4 - Satin Brass"),
]

HAGER_CLOSER_FINISHES = [
    ("ALM", "Aluminum"),
    ("DKB", "Dark Bronze"),
    ("BLK", "Black"),
    ("SPC", "Sprayed Coat"),
    ("689", "689 - Aluminum"),
    ("690", "690 - Dark Bronze"),
]

HAGER_PLATE_FINISHES = [
    ("US32D", "US32D - Satin Stainless"),
    ("US26D", "US26D - Satin Chrome"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US3",   "US3 - Polished Brass"),
    ("US4",   "US4 - Satin Brass"),
    ("BRS",   "Brass"),
    ("CSP",   "CSP - Clear Anodized"),
]


def seed(conn):
    _seed_floor_stops(conn)
    _seed_wall_stops(conn)
    _seed_overhead_stops(conn)
    _seed_kick_plates(conn)
    _seed_mop_plates(conn)
    _seed_armor_plates(conn)
    _seed_push_plates(conn)
    _seed_pull_plates(conn)
    _seed_door_pulls(conn)
    _seed_flush_bolts(conn)
    _seed_coordinators(conn)
    _seed_closers_5100(conn)
    _seed_closers_5300(conn)
    _seed_thresholds(conn)
    _seed_dust_proof_strike(conn)
    _seed_silencers(conn)


# =================================================================
# 1.  Floor Stops
# =================================================================
def _seed_floor_stops(conn):
    f = fid(conn, "Hager", "Floor Stop", "Door Stop",
            "{model}-{finish}", "Hager {model} Floor Stop, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "finish", "Finish", True)

    options(conn, f, "model", [
        ("232W",  "232W - Wall Bumper / Floor Stop"),
        ("241F",  "241F - Heavy Duty Floor Stop"),
        ("241W",  "241W - Heavy Duty Wall Stop"),
        ("242F",  "242F - Universal Floor Stop"),
        ("244F",  "244F - Dome Floor Stop"),
        ("244S",  "244S - Dome Floor Stop (Screw Mount)"),
        ("246F",  "246F - Convex Floor Stop"),
        ("248F",  "248F - Plunger Floor Stop"),
        ("252W",  "252W - Angle Wall Stop"),
        ("258S",  "258S - Heavy Duty Floor Stop"),
        ("340F",  "340F - Floor Mount Stop"),
    ])
    options(conn, f, "finish", HAGER_SS_FINISHES)


# =================================================================
# 2.  Wall Stops
# =================================================================
def _seed_wall_stops(conn):
    f = fid(conn, "Hager", "Wall Stop", "Door Stop",
            "{model}-{finish}", "Hager {model} Wall Stop, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "finish", "Finish", True)
    slot(conn, f, 3, "projection", "Projection", False)

    options(conn, f, "model", [
        ("232W",  "232W - Concave Wall Stop"),
        ("236W",  "236W - Wall Stop w/ Heavy Rubber"),
        ("241W",  "241W - Heavy Duty Wall Stop"),
        ("252W",  "252W - Angle Wall Stop"),
        ("256W",  "256W - Rigid Wall Stop"),
    ])
    options(conn, f, "finish", HAGER_SS_FINISHES)
    options(conn, f, "projection", [
        ("STD", "Standard"),
        ("EXT", "Extended"),
    ])


# =================================================================
# 3.  Overhead Stops / Holders
# =================================================================
def _seed_overhead_stops(conn):
    f = fid(conn, "Hager", "Overhead Stop / Holder", "Overhead Stop",
            "{model}-{hold}-{finish}",
            "Hager {model} Overhead Stop, {hold}, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "hold", "Hold Open", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "model", [
        ("5911",  "5911 - Surface Overhead Stop"),
        ("5913",  "5913 - Heavy Duty Surface OH Stop"),
        ("5914",  "5914 - Concealed Overhead Stop"),
        ("5916",  "5916 - Heavy Duty Concealed OH Stop"),
        ("5921",  "5921 - Overhead Stop & Holder"),
        ("5923",  "5923 - Heavy Duty OH Stop & Holder"),
        ("5924",  "5924 - Concealed OH Stop & Holder"),
        ("5926",  "5926 - HD Concealed OH Stop & Holder"),
    ])
    options(conn, f, "hold", [
        ("S",  "Stop Only (no hold open)"),
        ("SH", "Stop & Hold Open"),
    ])
    options(conn, f, "finish", HAGER_CLOSER_FINISHES)

    # Models 5911/5913 are stop-only — no hold open
    for m in ("5911", "5913", "5914", "5916"):
        restrict(conn, f, "model", m, "hold", ["S"],
                 f"Model {m} is stop-only")


# =================================================================
# 4.  Kick Plates
# =================================================================
def _seed_kick_plates(conn):
    f = fid(conn, "Hager", "Kick Plate", "Protection Plate",
            "{material}-{height}x{width}-{finish}",
            "Hager {material} Kick Plate {height}\"x{width}\", {finish}")

    slot(conn, f, 1, "material", "Material", True)
    slot(conn, f, 2, "height", "Height", True)
    slot(conn, f, 3, "width", "Width", True)
    slot(conn, f, 4, "corners", "Corners", True)
    slot(conn, f, 5, "finish", "Finish", True)
    slot(conn, f, 6, "fastener", "Fastener Type", False)

    options(conn, f, "material", [
        ("SS",   "Stainless Steel"),
        ("BRS",  "Brass"),
        ("BRZ",  "Bronze"),
        ("ALM",  "Aluminum"),
    ])
    options(conn, f, "height", [
        ("6",  "6\""),
        ("8",  "8\""),
        ("10", "10\""),
        ("12", "12\""),
    ])
    options(conn, f, "width", [
        ("28", "28\""),
        ("30", "30\""),
        ("32", "32\""),
        ("34", "34\""),
        ("36", "36\""),
        ("42", "42\""),
    ])
    options(conn, f, "corners", [
        ("SQ", "Square Corners"),
        ("RC", "Rounded Corners"),
        ("BV", "Beveled Edges"),
    ])
    options(conn, f, "finish", HAGER_PLATE_FINISHES)
    options(conn, f, "fastener", [
        ("CS", "Countersunk Screws"),
        ("AH", "Adhesive"),
        ("MG", "Magnetic Mount"),
    ])


# =================================================================
# 5.  Mop / Base Plates
# =================================================================
def _seed_mop_plates(conn):
    f = fid(conn, "Hager", "Mop Plate", "Protection Plate",
            "{material}-{height}x{width}-{finish}",
            "Hager {material} Mop Plate {height}\"x{width}\", {finish}")

    slot(conn, f, 1, "material", "Material", True)
    slot(conn, f, 2, "height", "Height", True)
    slot(conn, f, 3, "width", "Width", True)
    slot(conn, f, 4, "corners", "Corners", True)
    slot(conn, f, 5, "finish", "Finish", True)

    options(conn, f, "material", [
        ("SS",   "Stainless Steel"),
        ("BRS",  "Brass"),
        ("ALM",  "Aluminum"),
    ])
    options(conn, f, "height", [
        ("4",  "4\""),
        ("6",  "6\""),
    ])
    options(conn, f, "width", [
        ("28", "28\""),
        ("30", "30\""),
        ("32", "32\""),
        ("34", "34\""),
        ("36", "36\""),
        ("42", "42\""),
    ])
    options(conn, f, "corners", [
        ("SQ", "Square Corners"),
        ("RC", "Rounded Corners"),
        ("BV", "Beveled Edges"),
    ])
    options(conn, f, "finish", HAGER_PLATE_FINISHES)


# =================================================================
# 6.  Armor Plates
# =================================================================
def _seed_armor_plates(conn):
    f = fid(conn, "Hager", "Armor Plate", "Protection Plate",
            "{material}-{height}x{width}-{finish}",
            "Hager {material} Armor Plate {height}\"x{width}\", {finish}")

    slot(conn, f, 1, "material", "Material", True)
    slot(conn, f, 2, "height", "Height", True)
    slot(conn, f, 3, "width", "Width", True)
    slot(conn, f, 4, "finish", "Finish", True)

    options(conn, f, "material", [
        ("SS",   "Stainless Steel"),
        ("BRS",  "Brass"),
        ("ALM",  "Aluminum"),
    ])
    options(conn, f, "height", [
        ("34", "34\""),
        ("36", "36\""),
        ("40", "40\""),
    ])
    options(conn, f, "width", [
        ("28", "28\""),
        ("30", "30\""),
        ("32", "32\""),
        ("34", "34\""),
        ("36", "36\""),
        ("42", "42\""),
    ])
    options(conn, f, "finish", HAGER_PLATE_FINISHES)


# =================================================================
# 7.  Push Plates
# =================================================================
def _seed_push_plates(conn):
    f = fid(conn, "Hager", "Push Plate", "Push / Pull",
            "{model}-{size}-{finish}",
            "Hager {model} Push Plate {size}, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "size", "Size", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "model", [
        ("30S",  "30S - Square Corner Push Plate"),
        ("30R",  "30R - Round Corner Push Plate"),
        ("31S",  "31S - Engraved Push Plate"),
        ("32S",  "32S - Hospital Push Plate (wide)"),
        ("33A",  "33A - Antimicrobial Push Plate"),
    ])
    options(conn, f, "size", [
        ("3.5x15", "3-1/2\" x 15\""),
        ("4x16",   "4\" x 16\""),
        ("6x16",   "6\" x 16\""),
        ("8x16",   "8\" x 16\""),
    ])
    options(conn, f, "finish", HAGER_PLATE_FINISHES)


# =================================================================
# 8.  Pull Plates
# =================================================================
def _seed_pull_plates(conn):
    f = fid(conn, "Hager", "Pull Plate", "Push / Pull",
            "{model}-{size}-{finish}",
            "Hager {model} Pull Plate {size}, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "size", "Size", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "model", [
        ("45S",  "45S - Square Corner Pull Plate"),
        ("45R",  "45R - Round Corner Pull Plate"),
        ("46S",  "46S - Engraved Pull Plate"),
        ("47S",  "47S - Hospital Pull Plate (wide)"),
    ])
    options(conn, f, "size", [
        ("3.5x15", "3-1/2\" x 15\""),
        ("4x16",   "4\" x 16\""),
        ("6x16",   "6\" x 16\""),
    ])
    options(conn, f, "finish", HAGER_PLATE_FINISHES)


# =================================================================
# 9.  Door Pulls (Back-to-Back & Single)
# =================================================================
def _seed_door_pulls(conn):
    f = fid(conn, "Hager", "Door Pull", "Push / Pull",
            "{model}-{length}-{finish}",
            "Hager {model} Door Pull, {length}, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "length", "Length", True)
    slot(conn, f, 3, "mounting", "Mounting", True)
    slot(conn, f, 4, "finish", "Finish", True)

    options(conn, f, "model", [
        ("4424",  "4424 - Round Pull"),
        ("4425",  "4425 - Flat Pull"),
        ("4426",  "4426 - Offset Pull"),
        ("4427",  "4427 - Cranked Pull"),
        ("4428",  "4428 - Square Pull"),
        ("4430",  "4430 - Tubular Pull"),
        ("4432",  "4432 - ADA Pull"),
        ("4435",  "4435 - Barn Door Pull"),
    ])
    options(conn, f, "length", [
        ("6",   "6\""),
        ("8",   "8\""),
        ("10",  "10\""),
        ("12",  "12\""),
        ("18",  "18\""),
        ("24",  "24\""),
    ])
    options(conn, f, "mounting", [
        ("BTB",  "Back-to-Back"),
        ("SGL",  "Single Side"),
        ("TM",   "Thru-Mount"),
    ])
    options(conn, f, "finish", HAGER_SS_FINISHES)


# =================================================================
# 10.  Flush Bolts
# =================================================================
def _seed_flush_bolts(conn):
    f = fid(conn, "Hager", "Flush Bolt", "Flush Bolt",
            "{model}-{finish}",
            "Hager {model} Flush Bolt, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "length", "Rod Length", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "model", [
        ("282D", "282D - Dust Proof Flush Bolt"),
        ("283D", "283D - Heavy Duty Flush Bolt"),
        ("284D", "284D - Automatic Flush Bolt"),
        ("285D", "285D - Constant Latching Flush Bolt"),
        ("286D", "286D - Manual Flush Bolt"),
        ("287D", "287D - Extension Flush Bolt"),
        ("290A", "290A - Lever Extension Flush Bolt"),
        ("292D", "292D - Surface Flush Bolt"),
        ("294D", "294D - Fire Rated Flush Bolt"),
    ])
    options(conn, f, "length", [
        ("12",  "12\" Rod"),
        ("18",  "18\" Rod"),
        ("24",  "24\" Rod"),
        ("36",  "36\" Rod"),
        ("48",  "48\" Rod"),
    ])
    options(conn, f, "finish", HAGER_SS_FINISHES)

    # Fire rated only available in 12" & 18" rods
    restrict(conn, f, "model", "294D", "length", ["12", "18"],
             "294D fire rated limited to short rods")


# =================================================================
# 11.  Door Coordinators
# =================================================================
def _seed_coordinators(conn):
    f = fid(conn, "Hager", "Door Coordinator", "Coordinator",
            "{model}-{width}",
            "Hager {model} Door Coordinator for {width} opening")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "width", "Opening Width", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "model", [
        ("5906",  "5906 - Standard Coordinator"),
        ("5908",  "5908 - Heavy Duty Coordinator"),
        ("5909",  "5909 - Roller Coordinator"),
    ])
    options(conn, f, "width", [
        ("4-0", "4'-0\" Opening"),
        ("5-0", "5'-0\" Opening"),
        ("6-0", "6'-0\" Opening"),
        ("7-0", "7'-0\" Opening"),
        ("8-0", "8'-0\" Opening"),
    ])
    options(conn, f, "finish", HAGER_CLOSER_FINISHES)


# =================================================================
# 12.  5100 Series Surface Closers
# =================================================================
def _seed_closers_5100(conn):
    f = fid(conn, "Hager", "5100 Series Closer", "Closer",
            "5100-{body}-{arm}-{finish}",
            "Hager 5100 Series Closer, Size {body}, {arm} Arm, {finish}")

    slot(conn, f, 1, "body", "Closer Size", True)
    slot(conn, f, 2, "arm", "Arm Type", True)
    slot(conn, f, 3, "cover", "Cover", False)
    slot(conn, f, 4, "hold_open", "Hold Open", False)
    slot(conn, f, 5, "finish", "Finish", True)

    options(conn, f, "body", [
        ("1",  "Size 1 (light door)"),
        ("2",  "Size 2"),
        ("3",  "Size 3"),
        ("4",  "Size 4 (standard)"),
        ("5",  "Size 5 (heavy)"),
        ("6",  "Size 6 (extra heavy)"),
        ("1-4", "Adjustable 1-4"),
        ("1-6", "Adjustable 1-6"),
    ])
    options(conn, f, "arm", [
        ("REG", "Regular Arm"),
        ("PA",  "Parallel Arm"),
        ("TJ",  "Top Jamb"),
        ("DA",  "Double Acting Arm"),
    ])
    options(conn, f, "cover", [
        ("STD", "Standard Cover"),
        ("SLM", "Slim Cover"),
        ("NCV", "No Cover"),
    ])
    options(conn, f, "hold_open", [
        ("HO",  "Hold Open"),
        ("NHO", "Non-Hold-Open"),
    ])
    options(conn, f, "finish", HAGER_CLOSER_FINISHES)


# =================================================================
# 13.  5300 Series Concealed Closers
# =================================================================
def _seed_closers_5300(conn):
    f = fid(conn, "Hager", "5300 Series Concealed Closer", "Closer",
            "5300-{body}-{arm}-{finish}",
            "Hager 5300 Series Concealed Closer, Size {body}, {arm} Arm, {finish}")

    slot(conn, f, 1, "body", "Closer Size", True)
    slot(conn, f, 2, "arm", "Arm Type", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "body", [
        ("2",  "Size 2"),
        ("3",  "Size 3"),
        ("4",  "Size 4"),
        ("5",  "Size 5"),
        ("2-5", "Adjustable 2-5"),
    ])
    options(conn, f, "arm", [
        ("REG", "Regular Arm"),
        ("PA",  "Parallel Arm"),
        ("TJ",  "Top Jamb"),
    ])
    options(conn, f, "finish", HAGER_CLOSER_FINISHES)


# =================================================================
# 14.  Thresholds
# =================================================================
def _seed_thresholds(conn):
    f = fid(conn, "Hager", "Threshold", "Threshold",
            "{model}-{width}-{finish}",
            "Hager {model} Threshold, {width}, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "width", "Door Width", True)
    slot(conn, f, 3, "finish", "Finish", True)

    options(conn, f, "model", [
        ("409S",  "409S - Saddle Threshold"),
        ("416S",  "416S - ADA Saddle Threshold"),
        ("420S",  "420S - ADA Offset Threshold"),
        ("430A",  "430A - Heavy Duty Threshold"),
        ("440A",  "440A - Panic Threshold"),
        ("450S",  "450S - Thermal Break Threshold"),
    ])
    options(conn, f, "width", [
        ("28", "28\" (2'-4\")"),
        ("30", "30\" (2'-6\")"),
        ("32", "32\" (2'-8\")"),
        ("34", "34\" (2'-10\")"),
        ("36", "36\" (3'-0\")"),
        ("42", "42\" (3'-6\")"),
        ("48", "48\" (4'-0\")"),
    ])
    options(conn, f, "finish", [
        ("ALM", "Aluminum Mill"),
        ("DBA", "Dark Bronze Anodized"),
        ("CSA", "Clear Satin Anodized"),
    ])


# =================================================================
# 15.  Dust Proof Strike
# =================================================================
def _seed_dust_proof_strike(conn):
    f = fid(conn, "Hager", "Dust Proof Strike", "Strike",
            "{model}-{finish}",
            "Hager {model} Dust Proof Strike, {finish}")

    slot(conn, f, 1, "model", "Model", True)
    slot(conn, f, 2, "finish", "Finish", True)

    options(conn, f, "model", [
        ("340D", "340D - Standard Dust Proof Strike"),
        ("340DA", "340DA - Adjustable Dust Proof Strike"),
        ("341D", "341D - Heavy Duty Dust Proof Strike"),
    ])
    options(conn, f, "finish", HAGER_SS_FINISHES)


# =================================================================
# 16.  Door Silencers
# =================================================================
def _seed_silencers(conn):
    f = fid(conn, "Hager", "Door Silencer", "Accessory",
            "{model}",
            "Hager {model} Door Silencer")

    slot(conn, f, 1, "model", "Model", True)

    options(conn, f, "model", [
        ("260W", "260W - Rubber Silencer (wood frame)"),
        ("261W", "261W - Peel & Stick Silencer (wood frame)"),
        ("262M", "262M - Rubber Silencer (metal frame)"),
        ("263M", "263M - Peel & Stick Silencer (metal frame)"),
    ])
