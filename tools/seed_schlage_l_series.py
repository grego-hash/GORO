"""Seed Schlage L-Series data extracted from catalog pages 14, 56-66.

Run:  python tools/seed_schlage_l_series.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.hw_configurator_db import get_connection, init_db


def seed_families(conn):
    """Seed all Schlage L-Series families into an already-open connection."""
    _seed_l_series_lock(conn)
    _seed_conventional_cylinders(conn)
    _seed_fsic_cylinders(conn)
    _seed_sfic_cylinders(conn)
    _seed_armored_fronts(conn)
    _seed_strikes(conn)
    _seed_thumbturn_cylinders(conn)
    _seed_blocking_rings(conn)
    _seed_le_wireless(conn)
    print("  Schlage L-Series seeded.")


def seed():
    # Delete existing DB so stale data never accumulates
    db_path = Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
    if db_path.exists():
        db_path.unlink()
    init_db()
    conn = get_connection()
    try:
        seed_families(conn)
        conn.commit()
        print("Schlage L-Series seed data loaded successfully.")
    finally:
        conn.close()


# =====================================================================
# 1. L Series Mortise Lock (main lockset configurator)
# =====================================================================

def _seed_l_series_lock(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series Mortise Lock',
            'Mortise Lockset',
            '{function} {cylinder_type} {lever} {rose} {finish} {handing}',
            'Schlage L Series {function} {cylinder_type} {lever}{rose} {finish} {handing} {thumbturn} {indicator}'
        )
    """)
    fid = _fid(conn, "L Series Mortise Lock")

    # ---- Slots (ordering per pg 62 How-to-Order) ----
    # Pos 2: Function, Pos 3: Cylinder Type, Pos 4A: Lever, Pos 4B: Rose,
    # Pos 4C: Finish, Pos 6: Handing (optional)
    _slot(conn, fid, 1, "function",      "Function", 1)
    _slot(conn, fid, 2, "cylinder_type", "Cylinder Type", 0)  # hidden for non-keyed
    _slot(conn, fid, 3, "lever",         "Lever Design", 1)
    _slot(conn, fid, 4, "rose",          "Rose / Trim", 1)
    _slot(conn, fid, 5, "finish",        "Finish", 1)
    _slot(conn, fid, 6, "handing",       "Handing", 0)  # optional
    _slot(conn, fid, 7, "thumbturn",     "Thumbturn Cylinder", 0)   # optional
    _slot(conn, fid, 8, "indicator",     "Indicator", 0)            # optional
    _slot(conn, fid, 9, "armored_front", "Armored Front", 0)        # optional
    _slot(conn, fid, 10, "strike",       "Strike", 0)               # optional
    _slot(conn, fid, 11, "door_thickness","Door Thickness", 0)      # optional
    _slot(conn, fid, 12, "voltage",      "Voltage", 0)              # optional (electrified)
    _slot(conn, fid, 13, "monitoring",   "Monitoring Option", 0)    # optional (electrified)

    # ---- Options: Function (common L-Series codes) ----
    # Mechanical functions
    functions = [
        ("L9010", "L9010 - Passage"),
        ("L9040", "L9040 - Privacy / Bath"),
        ("L9050", "L9050 - Office / Entry"),
        ("L9060", "L9060 - Apartment / Vestibule"),
        ("L9070", "L9070 - Classroom"),
        ("L9080", "L9080 - Storeroom"),
        ("L9453", "L9453 - Entrance"),
        ("L9456", "L9456 - Corridor"),
        ("L9480", "L9480 - Vandlgard Storeroom"),
        ("L9485", "L9485 - Faculty Restroom"),
        ("L9486", "L9486 - Faculty Restroom (Vacant/Occupied)"),
        ("L9473", "L9473 - Dormitory / Bedroom"),
        ("L9082", "L9082 - Institute"),
        # ---- Wired Electrified: Non-Keyed (pg 35) ----
        ("L9090EL", "L9090EL - Elec. Lock, Outside Lever, No Cylinder"),
        ("L9090EU", "L9090EU - Elec. Unlock, Outside Lever, No Cylinder"),
        ("L9091EL", "L9091EL - Elec. Lock, Both Levers, No Cylinder"),
        ("L9091EU", "L9091EU - Elec. Unlock, Both Levers, No Cylinder"),
        # ---- Wired Electrified: Keyed Non-Deadbolt (pg 35) ----
        ("L9092EL", "L9092EL - Elec. Lock, Outside Lever, Outside Cyl."),
        ("L9092EU", "L9092EU - Elec. Unlock, Outside Lever, Outside Cyl."),
        ("L9093EL", "L9093EL - Elec. Lock, Both Levers, Outside Cyl."),
        ("L9093EU", "L9093EU - Elec. Unlock, Both Levers, Outside Cyl."),
        ("L9095EL", "L9095EL - Elec. Lock, Both Levers, Double Cyl."),
        ("L9095EU", "L9095EU - Elec. Unlock, Both Levers, Double Cyl."),
        # ---- Wired Electrified: Keyed Deadbolt (pg 36) ----
        ("L9420EL", "L9420EL - Elec. Lock, Outside Lever, Thumbturn w/ Deadbolt"),
        ("L9420EU", "L9420EU - Elec. Unlock, Outside Lever, Thumbturn w/ Deadbolt"),
        ("L9453EL", "L9453EL - Elec. Lock, Both Levers, Thumbturn w/ Deadbolt"),
        ("L9453EU", "L9453EU - Elec. Unlock, Both Levers, Thumbturn w/ Deadbolt"),
        ("L9444EL", "L9444EL - Elec. Lock, Outside Lever, Double Cyl. w/ Deadbolt"),
        ("L9444EU", "L9444EU - Elec. Unlock, Outside Lever, Double Cyl. w/ Deadbolt"),
        ("L9445EL", "L9445EL - Elec. Lock, Both Levers, Double Cyl. w/ Deadbolt"),
        ("L9445EU", "L9445EU - Elec. Unlock, Both Levers, Double Cyl. w/ Deadbolt"),
        # ---- Motorized Latch Retraction (pg 37, 24VDC only) ----
        ("L9510",   "L9510 - Passage w/ Motorized Latch Retraction"),
        ("L9580",   "L9580 - Storeroom w/ Motorized Latch Retraction"),
        ("L9582",   "L9582 - Institution w/ Motorized Latch Retraction"),
        # ---- Motorized w/ Lever Control (pg 37, 24VDC only) ----
        ("L9592EL", "L9592EL - Elec. Lock, Outside Lever, MLR"),
        ("L9592EU", "L9592EU - Elec. Unlock, Outside Lever, MLR"),
        ("L9593EL", "L9593EL - Elec. Lock, Both Levers, Double Cyl., MLR"),
        ("L9593EU", "L9593EU - Elec. Unlock, Both Levers, Double Cyl., MLR"),
        ("L9596EL", "L9596EL - Elec. Lock/Unlock Inside Lever, Double Cyl., MLR"),
        ("L9596EU", "L9596EU - Elec. Lock/Unlock Inside Lever, Double Cyl., MLR"),
    ]
    _options(conn, fid, "function", functions)

    # ---- Options: Cylinder Type (pg 62 position 3) ----
    cylinder_types = [
        # Conventional
        ("P6",  "P6 - 6-Pin Conventional (default)"),
        ("P",   "P - 6-Pin Conventional, keyed 11"),
        ("Z",   "Z - Everest SI Cylinder, 7-pin"),
        ("L",   "L - Less Cylinder"),
        ("C",   "C - Concealed Mortise 6-pin"),
        ("CI",  "CI - Concealed Mortise IC"),
        ("W",   "W - Less Concealed Mortise Cylinder"),
        # Full-size IC (FSIC)
        ("R",   "R - FSIC Construction Core"),
        ("M",   "M - Everest SI FSIC, 7-pin"),
        ("J",   "J - Less FSIC"),
        ("F",   "F - FSIC 6-pin (less Schlage logo)"),
        ("T",   "T - Refurbishable Construction FSIC"),
        # Small-format IC (SFIC)
        ("G",   "G - SFIC 7-pin"),
        ("H",   "H - Refurbishable Construction SFIC"),
        ("BDC", "BDC - Disposable Construction SFIC"),
        ("SPR", "SPR - SFIC SPR"),
        ("B",   "B - Less SFIC"),
    ]
    _options(conn, fid, "cylinder_type", cylinder_types)

    # Non-keyed functions: hide the cylinder slot entirely
    no_cylinder_funcs = {"L9010", "L9040", "L9090EL", "L9090EU", "L9091EL", "L9091EU", "L9510"}
    for func_val in no_cylinder_funcs:
        for ct in cylinder_types:
            _rule(conn, fid, "conflict", "function", func_val, "cylinder_type", ct[0],
                  "No cylinder for this function")

    # ---- Options: Handing (pg 62 position 6, optional) ----
    handing = [
        ("LH",  "LH - Left Hand"),
        ("RH",  "RH - Right Hand"),
    ]
    _options(conn, fid, "handing", handing)

    # Handing required only for specific lever designs (pg 62 note 6)
    # All other levers get conflict rules to hide the handing slot.
    handed_levers = {"12", "Accent", "Avt", "Merano", "M62", "M53", "M85"}

    # ---- Options: Lever Designs (from pg 14 matrix + pg 64 health care) ----
    # Standard Collection
    levers = [
        ("01", "01"),
        ("02", "02"),
        ("03", "03 (Tubular)"),
        ("06", "06 (Rhodes)"),
        ("07", "07 (Athens)"),
        ("12", "12"),
        ("17", "17 (Sparta/Neptune)"),
        ("18", "18"),
        ("D",  "D"),
        ("Accent",    "Accent"),
        ("Merano",    "Merano"),
        ("Latitude",  "Latitude"),
        ("Longitude", "Longitude"),
        ("Carnegie",  "Carnegie"),
        # M Collection
        ("M12", "M12"),
        ("M15", "M15"),
        ("M51", "M51"),
        ("M52", "M52"),
        ("M53", "M53"),
        ("M56", "M56"),
        ("M61", "M61"),
        ("M66", "M66"),
        ("M81", "M81"),
        ("M82", "M82"),
        ("M83", "M83"),
        ("M84", "M84"),
        ("M85", "M85"),
        # Health-care / ligature resistant (pg 64)
        ("SL1",  "SL1 - Ligature Resistant Lever"),
        ("SM1",  "SM1 - Ligature Resistant Knob"),
        ("HSLR", "HSLR - High Security Ligature Resistant"),
    ]
    _options(conn, fid, "lever", levers)

    # Handing: non-handed levers → conflict both LH/RH so slot hides
    all_lever_codes = [lv[0] for lv in levers]
    for lev in all_lever_codes:
        if lev not in handed_levers:
            for hand in ["LH", "RH"]:
                _rule(conn, fid, "conflict", "lever", lev, "handing", hand,
                      "Handing not applicable for this lever")

    # ---- Options: Rose / Trim (from pg 14 matrix, Trim section) ----
    roses = [
        ("A",   "A Rose"),
        ("B",   "B Rose"),
        ("C",   "C Rose"),
        ("N",   "N Escutcheon"),
        ("L",   "L Escutcheon"),
    ]
    _options(conn, fid, "rose", roses)

    # ---- Options: Finishes (14 available per pg 64 specs) ----
    finishes = [
        ("605",   "605 - Bright Brass"),
        ("606",   "606 - Satin Brass"),
        ("609",   "609 - Antique Brass"),
        ("612",   "612 - Satin Bronze"),
        ("613",   "613 - Oil Rubbed Bronze"),
        ("618",   "618 - Bright Nickel"),
        ("619",   "619 - Satin Nickel"),
        ("622",   "622 - Flat Black"),
        ("625",   "625 - Bright Chrome"),
        ("626",   "626 - Satin Chrome"),
        ("626AM", "626AM - Antimicrobial Satin Chrome"),
        ("631",   "631 - Stainless Steel"),
        ("643AM", "643AM - Antimicrobial Aged Bronze"),
        ("643e",  "643e - Aged Bronze"),
    ]
    _options(conn, fid, "finish", finishes)

    # ---- Rules: finish restrictions from pg 14 footnotes ----
    # Footnote 2: Available in 605,606,609,612,613,619,625,626 only
    fn2 = ["605", "606", "609", "612", "613", "619", "625", "626"]
    # Footnote 3: Available in 626, 619 and 605/606 only
    fn3 = ["605", "606", "619", "626"]
    # Footnote 5: Available in 613, 618, 622, 625, 626, and 643e only
    fn5 = ["613", "618", "622", "625", "626", "643e"]
    # Footnote 7: Available in 613 and 618 only
    fn7 = ["613", "618"]

    # M Collection levers → footnote 2 finishes
    m_levers = [
        "M12", "M15", "M51", "M52", "M53", "M56",
        "M61", "M66", "M81", "M82", "M83", "M84", "M85",
    ]
    for lev in m_levers:
        _restrict(conn, fid, "lever", lev, "finish", fn2,
                  "M Collection finish restriction (footnote 2)")

    # Carnegie → footnote 5 finishes
    _restrict(conn, fid, "lever", "Carnegie", "finish", fn5,
              "Carnegie finish restriction (footnote 5)")

    # Accent/Merano with AVA rose options may have footnote restrictions
    # Latitude/Longitude → footnote 2 finishes (per catalog dot marks)
    _restrict(conn, fid, "lever", "Latitude", "finish", fn2,
              "Latitude finish restriction (footnote 2)")
    _restrict(conn, fid, "lever", "Longitude", "finish", fn2,
              "Longitude finish restriction (footnote 2)")

    # C Rose → restricted to fewer finishes (footnote 3 from matrix)
    _restrict(conn, fid, "rose", "C", "finish", fn3,
              "C Rose finish restriction (footnote 3)")

    # ---- Options: Thumbturn Cylinder (pg 60 — accessory for functions w/ inside thumbturn) ----
    thumbturn_options = [
        ("09-900", "09-900 - Thumbturn, No Collar"),
        ("09-904", "09-904 - Thumbturn w/ Compression Ring & Spring"),
        ("09-905", "09-905 - Thumbturn w/ Compression Ring, Spring & Blocking Ring"),
    ]
    _options(conn, fid, "thumbturn", thumbturn_options)

    # Functions that require a thumbturn on the inside
    thumbturn_functions = {
        # Mechanical
        "L9040", "L9050", "L9060", "L9453", "L9456", "L9473", "L9485", "L9486",
        # Electrified deadbolt w/ thumbturn (pg 36)
        "L9420EL", "L9420EU", "L9453EL", "L9453EU",
    }
    # Functions that do NOT get a thumbturn → conflict all thumbturn options to auto-hide slot
    no_thumbturn = [f[0] for f in functions if f[0] not in thumbturn_functions]
    for func_val in no_thumbturn:
        for tt in thumbturn_options:
            _rule(conn, fid, "conflict", "function", func_val, "thumbturn", tt[0],
                  "Thumbturn not applicable for this function")

    # ---- Options: Indicator (functions with visual Vacant/Occupied indicator) ----
    indicator_options = [
        ("STD", "Standard Visual Indicator (Vacant / Occupied)"),
    ]
    _options(conn, fid, "indicator", indicator_options)

    # Functions that include an indicator
    indicator_functions = {"L9456", "L9485", "L9486"}
    # Functions without indicator → conflict to auto-hide slot
    no_indicator = [f[0] for f in functions if f[0] not in indicator_functions]
    for func_val in no_indicator:
        for ind in indicator_options:
            _rule(conn, fid, "conflict", "function", func_val, "indicator", ind[0],
                  "Indicator not applicable for this function")

    # ---- Options: Armored Front (pg 61 — configuration driven by function) ----
    # Each function determines what cutouts the mortise case needs.
    armored_front_options = [
        ("LATCH_ONLY",         "09-562 - Latch Only"),
        ("LATCH_AUX",          "09-563 - Latch x Auxiliary Latch"),
        ("LATCH_DEADBOLT",     "09-564 - Latch x Deadbolt"),
        ("LATCH_AUX_DEADBOLT", "09-566 - Latch x Auxiliary Latch x Deadbolt"),
    ]
    _options(conn, fid, "armored_front", armored_front_options)
    af_all_vals = [a[0] for a in armored_front_options]

    # Map each function → which armored front configuration(s) are valid
    func_to_af = {
        # Mechanical
        "L9010": ["LATCH_ONLY"],                        # Passage: latch only
        "L9040": ["LATCH_AUX"],                         # Privacy: latch + aux latch
        "L9050": ["LATCH_AUX"],                         # Office/Entry: latch + aux
        "L9060": ["LATCH_DEADBOLT"],                    # Apartment: latch + deadbolt
        "L9070": ["LATCH_ONLY"],                        # Classroom: latch only
        "L9080": ["LATCH_ONLY"],                        # Storeroom: latch only
        "L9453": ["LATCH_AUX_DEADBOLT"],                # Entrance: latch + aux + deadbolt
        "L9456": ["LATCH_AUX_DEADBOLT"],                # Corridor w/ indicator
        "L9473": ["LATCH_AUX"],                         # Dormitory: latch + aux
        "L9480": ["LATCH_ONLY"],                        # Vandlgard: latch only
        "L9485": ["LATCH_AUX_DEADBOLT"],                # Faculty restroom
        "L9486": ["LATCH_AUX_DEADBOLT"],                # Faculty restroom V/O
        "L9082": ["LATCH_ONLY"],                        # Institute: latch only
        # Electrified non-keyed (pg 35): latch + aux
        "L9090EL": ["LATCH_AUX"], "L9090EU": ["LATCH_AUX"],
        "L9091EL": ["LATCH_AUX"], "L9091EU": ["LATCH_AUX"],
        # Electrified keyed non-deadbolt (pg 35): latch + aux
        "L9092EL": ["LATCH_AUX"], "L9092EU": ["LATCH_AUX"],
        "L9093EL": ["LATCH_AUX"], "L9093EU": ["LATCH_AUX"],
        "L9095EL": ["LATCH_AUX"], "L9095EU": ["LATCH_AUX"],
        # Electrified keyed deadbolt (pg 36): latch + aux + deadbolt
        "L9420EL": ["LATCH_AUX_DEADBOLT"], "L9420EU": ["LATCH_AUX_DEADBOLT"],
        "L9453EL": ["LATCH_AUX_DEADBOLT"], "L9453EU": ["LATCH_AUX_DEADBOLT"],
        "L9444EL": ["LATCH_AUX_DEADBOLT"], "L9444EU": ["LATCH_AUX_DEADBOLT"],
        "L9445EL": ["LATCH_AUX_DEADBOLT"], "L9445EU": ["LATCH_AUX_DEADBOLT"],
        # Motorized (pg 37): latch only
        "L9510": ["LATCH_ONLY"], "L9580": ["LATCH_ONLY"], "L9582": ["LATCH_ONLY"],
        # Motorized w/ lever control (pg 37): latch + aux
        "L9592EL": ["LATCH_AUX"], "L9592EU": ["LATCH_AUX"],
        "L9593EL": ["LATCH_AUX"], "L9593EU": ["LATCH_AUX"],
        "L9596EL": ["LATCH_AUX"], "L9596EU": ["LATCH_AUX"],
    }
    for func_val, allowed_afs in func_to_af.items():
        _restrict(conn, fid, "function", func_val, "armored_front", allowed_afs,
                  f"Armored front for {func_val}")

    # ---- Options: Strike (pg 61 — type driven by function) ----
    strike_options = [
        ("10-072", "10-072 - Standard (1-1/4\" lip, multiple lengths)"),
        ("10-073", "10-073 - Deadbolt Strike (L9453 series deadlocks)"),
        ("10-075", "10-075 - 1/2\" Rabbeted (use with 1-1/16\" armor)"),
    ]
    _options(conn, fid, "strike", strike_options)
    strike_all_vals = [s[0] for s in strike_options]

    # Most functions use 10-072 standard; deadbolt functions also allow 10-073.
    std_strike_funcs = {
        "L9010", "L9040", "L9050", "L9070", "L9080",
        "L9473", "L9480", "L9082",
        # Electrified non-deadbolt
        "L9090EL", "L9090EU", "L9091EL", "L9091EU",
        "L9092EL", "L9092EU", "L9093EL", "L9093EU",
        "L9095EL", "L9095EU",
        # Motorized
        "L9510", "L9580", "L9582",
        "L9592EL", "L9592EU", "L9593EL", "L9593EU",
        "L9596EL", "L9596EU",
    }
    db_strike_funcs = {
        "L9060", "L9453", "L9456", "L9485", "L9486",
        # Electrified deadbolt
        "L9420EL", "L9420EU", "L9453EL", "L9453EU",
        "L9444EL", "L9444EU", "L9445EL", "L9445EU",
    }
    for func_val in std_strike_funcs:
        _restrict(conn, fid, "function", func_val, "strike",
                  ["10-072", "10-075"],
                  f"Standard strike for {func_val}")
    for func_val in db_strike_funcs:
        _restrict(conn, fid, "function", func_val, "strike",
                  ["10-072", "10-073", "10-075"],
                  f"Standard or deadbolt strike for {func_val}")

    # ---- Options: Door Thickness (standard range + extended) ----
    door_thickness_options = [
        ("1-3/4",  "1-3/4\" (Standard)"),
        ("1-3/8",  "1-3/8\""),
        ("2",      "2\""),
        ("2-1/4",  "2-1/4\""),
        ("2-1/2",  "2-1/2\" (requires extended parts)"),
        ("2-3/4",  "2-3/4\" (requires extended parts)"),
    ]
    _options(conn, fid, "door_thickness", door_thickness_options)
    # Door thickness is always available (all functions), so no conflict rules needed.
    # SFIC cylinders limited to 2" max — create restrictions when cylinder_type is G/H/BDC/SPR/B
    sfic_cyl_types = ["G", "H", "BDC", "SPR", "B"]
    thick_doors = ["2-1/4", "2-1/2", "2-3/4"]
    for cyl in sfic_cyl_types:
        for thick in thick_doors:
            _rule(conn, fid, "conflict", "cylinder_type", cyl, "door_thickness", thick,
                  "SFIC cylinders limited to 2\" max door thickness")

    # ---- Options: Voltage (pg 35-37 — electrified / motorized functions) ----
    voltage_options = [
        ("12_24VDC", "12/24VDC Auto-Detect"),
        ("24VDC",    "24VDC Only"),
    ]
    _options(conn, fid, "voltage", voltage_options)

    # Group electrified functions by voltage
    # EL/EU (non-motorized): 12/24VDC auto-detect
    auto_voltage_funcs = {
        "L9090EL", "L9090EU", "L9091EL", "L9091EU",
        "L9092EL", "L9092EU", "L9093EL", "L9093EU",
        "L9095EL", "L9095EU",
        "L9420EL", "L9420EU", "L9453EL", "L9453EU",
        "L9444EL", "L9444EU", "L9445EL", "L9445EU",
    }
    # Motorized: 24VDC only
    dc24_only_funcs = {
        "L9510", "L9580", "L9582",
        "L9592EL", "L9592EU", "L9593EL", "L9593EU",
        "L9596EL", "L9596EU",
    }
    all_electrified = auto_voltage_funcs | dc24_only_funcs

    # Mechanical functions: conflict all voltage options to hide slot
    for func_val in [f[0] for f in functions if f[0] not in all_electrified]:
        for v in voltage_options:
            _rule(conn, fid, "conflict", "function", func_val, "voltage", v[0],
                  "Voltage not applicable for mechanical function")

    # Auto-detect EL/EU: restrict to 12/24VDC only
    for func_val in auto_voltage_funcs:
        _restrict(conn, fid, "function", func_val, "voltage", ["12_24VDC"],
                  "Non-motorized electrified: 12/24VDC auto-detect")
    # Motorized: restrict to 24VDC only
    for func_val in dc24_only_funcs:
        _restrict(conn, fid, "function", func_val, "voltage", ["24VDC"],
                  "Motorized function: 24VDC only")

    # ---- Options: Monitoring (pg 35-37 — RX / LX available on electrified functions) ----
    monitoring_options = [
        ("NONE", "None"),
        ("RX",   "RX - Request to Exit Switch"),
        ("LX",   "LX - Latchbolt Monitor"),
    ]
    _options(conn, fid, "monitoring", monitoring_options)

    # All wired electrified (EL/EU) functions support RX + LX (pg 35-37)
    rx_lx_funcs = {
        # Non-keyed (pg 35)
        "L9090EL", "L9090EU", "L9091EL", "L9091EU",
        # Keyed non-deadbolt (pg 35)
        "L9092EL", "L9092EU", "L9093EL", "L9093EU",
        "L9095EL", "L9095EU",
        # Keyed deadbolt (pg 36)
        "L9420EL", "L9420EU", "L9453EL", "L9453EU",
        "L9444EL", "L9444EU", "L9445EL", "L9445EU",
        # Motorized (pg 37)
        "L9510", "L9580",
        "L9592EL", "L9592EU", "L9593EL", "L9593EU",
    }
    # Functions that support LX only (no RX) — institution motorized
    lx_only_funcs = {
        "L9582", "L9596EL", "L9596EU",
    }
    monitoring_funcs = rx_lx_funcs | lx_only_funcs

    # Non-monitoring functions: conflict all monitoring options to hide slot
    for func_val in [f[0] for f in functions if f[0] not in monitoring_funcs]:
        for m in monitoring_options:
            _rule(conn, fid, "conflict", "function", func_val, "monitoring", m[0],
                  "Monitoring not available for this function")

    # RX+LX functions: allow all 3 options (None, RX, LX) - no restrictions needed
    # LX-only functions: restrict to None and LX
    for func_val in lx_only_funcs:
        _restrict(conn, fid, "function", func_val, "monitoring",
                  ["NONE", "LX"],
                  "Only latchbolt monitor available for this function")

    print(f"  L Series Mortise Lock  (id={fid})")


# =====================================================================
# 5. Armored Fronts (pg 61)
# =====================================================================

def _seed_armored_fronts(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series Armored Front',
            'Armored Front',
            '{part_number}',
            'Schlage L Series Armored Front {part_number} - {configuration}'
        )
    """)
    fid = _fid(conn, "L Series Armored Front")

    _slot(conn, fid, 1, "configuration", "Configuration", 1)
    _slot(conn, fid, 2, "part_number",   "Part Number (auto)", 1)

    _options(conn, fid, "configuration", [
        ("LATCH_ONLY",        "Latch Only"),
        ("LATCH_AUX",         "Latch x Auxiliary Latch"),
        ("LATCH_DEADBOLT",    "Latch x Deadbolt"),
        ("LATCH_AUX_DEADBOLT","Latch x Auxiliary Latch x Deadbolt"),
        ("DEADBOLT_ONLY",     "Deadbolt Only"),
        ("BLANK",             "Blank (no holes)"),
        ("LATCH_AUX_NONUL",   "Latch x Aux Latch, Non-UL (Holdback)"),
        ("DEADBOLT_SM",       "Deadbolt Only, Small Mortise Case"),
    ])

    # Part numbers: 1-1/4" width | 1-1/8" width
    _options(conn, fid, "part_number", [
        ("09-562", "09-562 (1-1/4\") / 09-668 (1-1/8\") - Latch Only"),
        ("09-563", "09-563 (1-1/4\") / 09-669 (1-1/8\") - Latch x Aux Latch"),
        ("09-564", "09-564 (1-1/4\") / 09-670 (1-1/8\") - Latch x Deadbolt"),
        ("09-565", "09-565 (1-1/4\") / 09-671 (1-1/8\") - Deadbolt Only"),
        ("09-566", "09-566 (1-1/4\") / 09-672 (1-1/8\") - Latch x Aux x Deadbolt"),
        ("09-601", "09-601 (1-1/4\") / 09-667 (1-1/8\") - Blank"),
        ("09-713", "09-713 - Latch x Aux, Non-UL Holdback"),
        ("09-717", "09-717 - Deadbolt Only, Small Mortise Case"),
    ])

    # Map configuration → part number
    config_parts = [
        ("LATCH_ONLY",         "09-562"),
        ("LATCH_AUX",          "09-563"),
        ("LATCH_DEADBOLT",     "09-564"),
        ("LATCH_AUX_DEADBOLT", "09-566"),
        ("DEADBOLT_ONLY",      "09-565"),
        ("BLANK",              "09-601"),
        ("LATCH_AUX_NONUL",    "09-713"),
        ("DEADBOLT_SM",        "09-717"),
    ]
    for cfg, pn in config_parts:
        _rule(conn, fid, "require", "configuration", cfg, "part_number", pn,
              f"Configuration maps to part {pn}")

    print(f"  L Series Armored Front  (id={fid})")


# =====================================================================
# 6. Strikes (pg 61)
# =====================================================================

def _seed_strikes(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series Strike',
            'Strike',
            '{part_number}',
            'Schlage L Series Strike {part_number} - {strike_type}'
        )
    """)
    fid = _fid(conn, "L Series Strike")

    _slot(conn, fid, 1, "strike_type",  "Strike Type", 1)
    _slot(conn, fid, 2, "part_number",  "Part Number (auto)", 1)

    _options(conn, fid, "strike_type", [
        ("STD_L9000",  "10-072 - Standard for L9000 (multiple lip lengths)"),
        ("L9453_DB",   "10-073 - L9453 Series Deadlocks, Deadbolt Strike Standard"),
        ("RABBETED",   "10-075 - 1/2\" Rabbeted (use with 1-1/16\" armor)"),
        ("L400_OPT",   "10-078 - 1-1/4\" x 9-1/2\" with Box (L400 Optional)"),
        ("L400_STD",   "10-079 - 1-3/8\" x 9-1/2\" with Box (L400 Standard)"),
        ("ARM_FRONT",  "10-097 - Armored Front Strike, No Box"),
    ])

    _options(conn, fid, "part_number", [
        ("10-072", "10-072"),
        ("10-073", "10-073"),
        ("10-075", "10-075"),
        ("10-078", "10-078"),
        ("10-079", "10-079"),
        ("10-097", "10-097"),
    ])

    for st, pn in [
        ("STD_L9000", "10-072"), ("L9453_DB", "10-073"),
        ("RABBETED", "10-075"), ("L400_OPT", "10-078"),
        ("L400_STD", "10-079"), ("ARM_FRONT", "10-097"),
    ]:
        _rule(conn, fid, "require", "strike_type", st, "part_number", pn,
              f"Strike type maps to part {pn}")

    print(f"  L Series Strike  (id={fid})")


# =====================================================================
# 7. Classroom Thumbturn Cylinders (pg 60)
# =====================================================================

def _seed_thumbturn_cylinders(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series Thumbturn Cylinder',
            'Thumbturn Cylinder',
            '{part_number}',
            'Schlage Classroom Thumbturn Cylinder {part_number} - {collar}'
        )
    """)
    fid = _fid(conn, "L Series Thumbturn Cylinder")

    _slot(conn, fid, 1, "collar",       "Collar Type", 1)
    _slot(conn, fid, 2, "part_number",  "Part Number (auto)", 1)

    _options(conn, fid, "collar", [
        ("NONE",        "09-900 - None (standard)"),
        ("COMP_SPRING", "09-904 - Compression Ring & Spring"),
        ("COMP_BLOCK",  "09-905 - Compression Ring, Spring & 1/8\" Blocking Ring"),
    ])

    _options(conn, fid, "part_number", [
        ("09-900", "09-900"),
        ("09-904", "09-904"),
        ("09-905", "09-905"),
    ])

    for collar, pn in [("NONE", "09-900"), ("COMP_SPRING", "09-904"), ("COMP_BLOCK", "09-905")]:
        _rule(conn, fid, "require", "collar", collar, "part_number", pn,
              f"Collar maps to {pn}")

    print(f"  L Series Thumbturn Cylinder  (id={fid})")


# =====================================================================
# 8. Blocking & Compression Rings (pg 59)
# =====================================================================

def _seed_blocking_rings(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series Blocking / Compression Ring',
            'Blocking Ring',
            '{part_number}',
            'Schlage {ring_type} - {part_number}'
        )
    """)
    fid = _fid(conn, "L Series Blocking / Compression Ring")

    _slot(conn, fid, 1, "ring_type",    "Ring Type", 1)
    _slot(conn, fid, 2, "part_number",  "Part Number (auto)", 1)

    _options(conn, fid, "ring_type", [
        ("BLOCK_079",  "26-079 - Blocking Ring"),
        ("BLOCK_082",  "26-082 - Blocking Ring (larger)"),
        ("COMP_083",   "26-083 - Compression Ring & Spring (specify finish & dimension)"),
        ("COMP_L839",  "L839-199 - Compression Spring only"),
    ])

    _options(conn, fid, "part_number", [
        ("26-079",   "26-079"),
        ("26-082",   "26-082"),
        ("26-083",   "26-083"),
        ("L839-199", "L839-199"),
    ])

    for rt, pn in [
        ("BLOCK_079", "26-079"), ("BLOCK_082", "26-082"),
        ("COMP_083", "26-083"), ("COMP_L839", "L839-199"),
    ]:
        _rule(conn, fid, "require", "ring_type", rt, "part_number", pn,
              f"Ring type maps to {pn}")

    print(f"  L Series Blocking / Compression Ring  (id={fid})")


# =====================================================================
# 2. Conventional Cylinders (pg 56)
# =====================================================================

def _seed_conventional_cylinders(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series Conventional Cylinder',
            'Cylinder',
            '{part_number}',
            'Schlage {design} Conventional Cylinder - {mechanism}'
        )
    """)
    fid = _fid(conn, "L Series Conventional Cylinder")

    _slot(conn, fid, 1, "design",    "Design / Trim", 1)
    _slot(conn, fid, 2, "function",  "Function Group", 1)
    _slot(conn, fid, 3, "mechanism", "Cylinder Mechanism", 1)

    _options(conn, fid, "design", [
        ("LN_ESC",      "L & N Escutcheons (cylinder only)"),
        ("L_ESC",       "L Escutcheon (concealed body cylinder)"),
        ("SEC_TRIM",    "Sectional Trim (compression ring & spring)"),
    ])

    _options(conn, fid, "function", [
        ("STD",         "All except L9060P / L9485 / L9486"),
        ("L9060P",      "L9060P Outside"),
        ("L9485_86",    "L9485 / L9486 Faculty Restroom"),
        ("LM9280",      "LM9280 / M9280 Storeroom"),
    ])

    _options(conn, fid, "mechanism", [
        ("STD_PT",      "Standard Pin & Tumbler"),
        ("SI",          "SI Cylinder"),
        ("LEGACY_P",    "Legacy Primus / Primus RP / Primus XP"),
        ("PXP_SI",      "Primus XP SI Cylinder"),
        ("UL437",       "UL 437 (Legacy / Primus / Primus XP)"),
        ("PXP_LOCK",    "Primus XP Lockout"),
        ("PXP_UL437",   "Primus XP UL 437 Lockout"),
    ])

    # --- Part number lookup rules ---
    # These map (design, function, mechanism) → part_number
    # Modeled as restrict rules where selecting design+function restricts
    # the available mechanisms and we store part numbers in description.
    #
    # L & N Escutcheons
    _cyl_part(conn, fid, "LN_ESC", "STD",      "STD_PT",    "30-021")
    _cyl_part(conn, fid, "LN_ESC", "STD",      "SI",        "91-053")
    _cyl_part(conn, fid, "LN_ESC", "STD",      "LEGACY_P",  "20-703 / 20-703-XP / 20-703-RP")
    _cyl_part(conn, fid, "LN_ESC", "STD",      "PXP_SI",    "91-700-XP")
    _cyl_part(conn, fid, "LN_ESC", "STD",      "UL437",     "20-593 / 20-593-XP")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "STD_PT",    "28-021")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "SI",        "91-059")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "LEGACY_P",  "20-701 / 20-701-RP / 20-701-XP")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "PXP_SI",    "91-754-XP")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "UL437",     "20-501 / 20-501-XP")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "PXP_LOCK",  "20-715-XP")
    _cyl_part(conn, fid, "LN_ESC", "L9060P",   "PXP_UL437", "20-515-XP")
    _cyl_part(conn, fid, "LN_ESC", "L9485_86", "STD_PT",    "30-022")
    _cyl_part(conn, fid, "LN_ESC", "LM9280",   "STD_PT",    "30-019")
    _cyl_part(conn, fid, "LN_ESC", "LM9280",   "SI",        "91-130")
    # L Escutcheon
    _cyl_part(conn, fid, "L_ESC",  "STD",      "STD_PT",    "30-004")
    _cyl_part(conn, fid, "L_ESC",  "STD",      "LEGACY_P",  "20-789 / 20-789-XP")
    _cyl_part(conn, fid, "L_ESC",  "STD",      "UL437",     "20-599 / 20-599-XP")
    _cyl_part(conn, fid, "L_ESC",  "L9060P",   "STD_PT",    "28-023")
    _cyl_part(conn, fid, "L_ESC",  "L9060P",   "LEGACY_P",  "24-167 / 24-767-RP / 24-167-XP")
    _cyl_part(conn, fid, "L_ESC",  "L9060P",   "UL437",     "24-567 / 24-567-XP")
    _cyl_part(conn, fid, "L_ESC",  "L9485_86", "STD_PT",    "30-005")
    # Sectional Trim
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "STD_PT",    "30-001")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "SI",        "91-083")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "LEGACY_P",  "20-787 / 20-787-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "PXP_SI",    "91-757-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "UL437",     "20-587 / 20-587-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "PXP_LOCK",  "30-715-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "PXP_UL437", "20-515-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "STD_PT",    "20-001")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "SI",        "91-051")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "LEGACY_P",  "20-700 / 20-700-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "PXP_SI",    "91-751-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "UL437",     "20-500 / 20-500-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "PXP_LOCK",  "20-715-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060P",   "PXP_UL437", "20-515-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9485_86", "STD_PT",    "30-002")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280",   "STD_PT",    "30-000")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280",   "SI",        "91-129")

    # Conflict rules: L Escutcheon has N/A for SI, PXP_SI, PXP_LOCK, PXP_UL437
    for mech in ["SI", "PXP_SI", "PXP_LOCK", "PXP_UL437"]:
        _rule(conn, fid, "conflict", "design", "L_ESC", "mechanism", mech,
              "L Escutcheon does not support this mechanism")

    # L9485/86 only supports STD_PT
    for mech in ["SI", "LEGACY_P", "PXP_SI", "UL437", "PXP_LOCK", "PXP_UL437"]:
        _rule(conn, fid, "conflict", "function", "L9485_86", "mechanism", mech,
              "Faculty restroom only available with standard pin & tumbler")

    # LM9280 only supports STD_PT and SI
    for mech in ["LEGACY_P", "PXP_SI", "UL437", "PXP_LOCK", "PXP_UL437"]:
        _rule(conn, fid, "conflict", "function", "LM9280", "mechanism", mech,
              "LM9280 storeroom only available with STD P&T or SI")

    print(f"  L Series Conventional Cylinder  (id={fid})")


# =====================================================================
# 3. FSIC Cylinders (pg 57)
# =====================================================================

def _seed_fsic_cylinders(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series FSIC Cylinder',
            'Cylinder',
            '{part_number}',
            'Schlage {design} FSIC Cylinder - {mechanism}'
        )
    """)
    fid = _fid(conn, "L Series FSIC Cylinder")

    _slot(conn, fid, 1, "design",    "Design / Trim", 1)
    _slot(conn, fid, 2, "function",  "Function Group", 1)
    _slot(conn, fid, 3, "mechanism", "Core Mechanism", 1)

    _options(conn, fid, "design", [
        ("LN_COMP", "L & N Escutcheons (w/ compression ring)"),
        ("SEC_TRIM", "Sectional Trim (w/ compression ring, spring & blocking ring)"),
    ])

    _options(conn, fid, "function", [
        ("STD",      "All except L9060 / L9485 / L9486"),
        ("L9060",    "L9060 Outside"),
        ("L9485_86", "L9485 / L9486 Faculty Restroom"),
        ("LM9280",   "LM9280 / LV9080 / M9280 Storeroom"),
    ])

    _options(conn, fid, "mechanism", [
        ("STD_PT",   "Standard Pin & Tumbler"),
        ("SI",       "SI Cylinder"),
        ("LEGACY_P", "Legacy Primus / Primus XP"),
        ("PXP_SI",   "Primus XP SI Cylinder"),
        ("HOUSING",  "Housing Less Core"),
    ])

    # Part numbers from pg 57 table
    # L & N Escutcheons
    _cyl_part(conn, fid, "LN_COMP", "STD",      "STD_PT",   "30-008")
    _cyl_part(conn, fid, "LN_COMP", "STD",      "SI",       "91-163")
    _cyl_part(conn, fid, "LN_COMP", "STD",      "LEGACY_P", "20-788 / 20-788-XP")
    _cyl_part(conn, fid, "LN_COMP", "STD",      "PXP_SI",   "91-063-XP")
    _cyl_part(conn, fid, "LN_COMP", "STD",      "HOUSING",  "30-007")
    _cyl_part(conn, fid, "LN_COMP", "L9060",    "STD_PT",   "30-031")
    _cyl_part(conn, fid, "LN_COMP", "L9060",    "SI",       "91-165")
    _cyl_part(conn, fid, "LN_COMP", "L9060",    "LEGACY_P", "20-781 / 20-782-XP")
    _cyl_part(conn, fid, "LN_COMP", "L9060",    "PXP_SI",   "91-065-XP")
    _cyl_part(conn, fid, "LN_COMP", "L9060",    "HOUSING",  "30-022 + 36-083")
    _cyl_part(conn, fid, "LN_COMP", "L9485_86", "STD_PT",   "30-001")
    _cyl_part(conn, fid, "LN_COMP", "LM9280",   "STD_PT",   "25-101")
    _cyl_part(conn, fid, "LN_COMP", "LM9280",   "HOUSING",  "25-102")
    # Sectional Trim
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "STD_PT",   "30-110")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "SI",       "91-169")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "LEGACY_P", "20-775 / 20-775-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "PXP_SI",   "91-059-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",      "HOUSING",  "30-137")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",    "STD_PT",   "30-033 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",    "SI",       "91-165 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",    "LEGACY_P", "20-783 / 20-783-XP")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",    "PXP_SI",   "91-065-XP + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",    "HOUSING",  "30-022 + 36-083 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9485_86", "STD_PT",   "30-140")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280",   "STD_PT",   "25-101 + 36-082-037")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280",   "HOUSING",  "26-102 + 36-082-037")

    # Conflict rules
    for mech in ["SI", "LEGACY_P", "PXP_SI", "HOUSING"]:
        _rule(conn, fid, "conflict", "function", "L9485_86", "mechanism", mech,
              "Faculty restroom: standard pin & tumbler only")
    for mech in ["SI", "LEGACY_P", "PXP_SI"]:
        _rule(conn, fid, "conflict", "function", "LM9280", "mechanism", mech,
              "Storeroom: STD P&T or Housing only")

    print(f"  L Series FSIC Cylinder  (id={fid})")


# =====================================================================
# 4. SFIC Cylinders (pg 58)
# =====================================================================

def _seed_sfic_cylinders(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'L Series SFIC Cylinder',
            'Cylinder',
            '{part_number}',
            'Schlage {design} SFIC Cylinder - {mechanism}'
        )
    """)
    fid = _fid(conn, "L Series SFIC Cylinder")

    _slot(conn, fid, 1, "design",    "Design / Trim", 1)
    _slot(conn, fid, 2, "function",  "Function Group", 1)
    _slot(conn, fid, 3, "mechanism", "Core Mechanism", 1)

    _options(conn, fid, "design", [
        ("LN_COMP",  "L & N Escutcheons (w/ compression ring & spring)"),
        ("SEC_TRIM", "Sectional Trim (w/ compression ring, spring & blocking ring)"),
    ])

    _options(conn, fid, "function", [
        ("STD",    "All except L9060"),
        ("L9060",  "L9060 Outside"),
        ("LM9280", "LM9280 / LV9080 / M9280"),
    ])

    _options(conn, fid, "mechanism", [
        ("EV29R",    "Everest 29R Restricted (01 suffix)"),
        ("KEYED",    "Keyed Construction (A suffix)"),
        ("DISP",     "Disposable Construction (BDC suffix)"),
        ("HOUSING",  "Housing Less Core (B suffix)"),
    ])

    # Part numbers from pg 58 table
    # L & N Escutcheons
    _cyl_part(conn, fid, "LN_COMP", "STD",    "EV29R",   "80-108")
    _cyl_part(conn, fid, "LN_COMP", "STD",    "KEYED",   "80-136")
    _cyl_part(conn, fid, "LN_COMP", "STD",    "DISP",    "80-15")
    _cyl_part(conn, fid, "LN_COMP", "STD",    "HOUSING", "80-108")
    _cyl_part(conn, fid, "LN_COMP", "L9060",  "EV29R",   "80-304")
    _cyl_part(conn, fid, "LN_COMP", "L9060",  "KEYED",   "80-134")
    _cyl_part(conn, fid, "LN_COMP", "L9060",  "DISP",    "80-112")
    _cyl_part(conn, fid, "LN_COMP", "L9060",  "HOUSING", "80-104")
    _cyl_part(conn, fid, "LN_COMP", "LM9280", "EV29R",   "26-108")
    _cyl_part(conn, fid, "LN_COMP", "LM9280", "KEYED",   "26-107")
    _cyl_part(conn, fid, "LN_COMP", "LM9280", "DISP",    "27-105")
    _cyl_part(conn, fid, "LN_COMP", "LM9280", "HOUSING", "26-104")
    # Sectional Trim
    _cyl_part(conn, fid, "SEC_TRIM", "STD",    "EV29R",   "80-301")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",    "KEYED",   "80-131")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",    "DISP",    "80-109")
    _cyl_part(conn, fid, "SEC_TRIM", "STD",    "HOUSING", "80-101")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",  "EV29R",   "80-304 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",  "KEYED",   "80-134 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",  "DISP",    "80-112 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "L9060",  "HOUSING", "80-104 + 36-082-050")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280", "EV29R",   "26-104 + 36-082-025")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280", "KEYED",   "26-107 + 36-082-025")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280", "DISP",    "27-105 + 36-082-025")
    _cyl_part(conn, fid, "SEC_TRIM", "LM9280", "HOUSING", "26-104 + 36-082-025")

    print(f"  L Series SFIC Cylinder  (id={fid})")


# =====================================================================
# 9. LE Wireless Electronic Lock (pg 63, 66)
# =====================================================================

def _seed_le_wireless(conn):
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (
            'Schlage',
            'LE Wireless Electronic Lock',
            'Wireless Electronic Lockset',
            '{series} {chassis} {style} {cylinder_type} {finish} {lever} {rose} {handing}',
            'Schlage LE {series} {chassis} {style} {cylinder_type} {lever}{rose} {finish} {handing}'
        )
    """)
    fid = _fid(conn, "LE Wireless Electronic Lock")

    # ---- Slots (per pg 63 ordering diagram) ----
    _slot(conn, fid, 1, "series",        "Series", 1)
    _slot(conn, fid, 2, "chassis",       "Chassis", 1)
    _slot(conn, fid, 3, "style",         "Style (Escutcheon)", 1)
    _slot(conn, fid, 4, "cylinder_type", "Cylinder Type", 1)
    _slot(conn, fid, 5, "lever",         "Outside Lever Style", 1)
    _slot(conn, fid, 6, "finish",        "Outside Finish", 1)
    _slot(conn, fid, 7, "rose",          "Outside Rose", 1)
    _slot(conn, fid, 8, "handing",       "Handing", 0)

    # ---- Series (pg 63 detail 1) ----
    _options(conn, fid, "series", [
        ("LEB",  "LEB - Mobile Enabled Wireless Lock"),
        ("LEBM", "LEBM - Mobile Enabled + HID Credential Support"),
    ])

    # ---- Chassis (pg 63 detail 2) ----
    _options(conn, fid, "chassis", [
        ("MS", "MS - Mortise w/ LED Indicator"),
        ("MB", "MB - Mortise w/ Interior Push Button & LED"),
        ("ME", "ME - Mortise Deadbolt w/ LED"),
    ])

    # ---- Style (pg 63 detail 3) ----
    _options(conn, fid, "style", [
        ("GRW", "GRW - Greenwich Sectional"),
        ("ADD", "ADD - Addison Escutcheon"),
    ])

    # ---- Cylinder Type (pg 63 detail 4) ----
    _options(conn, fid, "cylinder_type", [
        # Conventional
        ("P6",  "P6 - 6-Pin Conventional (default)"),
        ("Z",   "Z - Everest SI Cylinder, 7-pin"),
        ("L",   "L - Less Cylinder"),
        # FSIC
        ("R",   "R - FSIC 6-pin"),
        ("J",   "J - Less FSIC"),
        ("M",   "M - Everest SI FSIC, 7-pin"),
        ("T",   "T - FSIC Construction Core"),
        # SFIC
        ("G",   "G - SFIC 7-pin"),
        ("B",   "B - Less SFIC"),
        ("H",   "H - Refurbishable Construction SFIC"),
        ("BDC", "BDC - Disposable Construction SFIC"),
    ])

    # ---- Lever Designs (pg 66: 31 lever designs) ----
    # Tactile warning on outside lever available on same subset as mechanical
    le_levers = [
        ("01", "01"), ("02", "02"), ("03", "03"), ("06", "06"),
        ("07", "07"), ("12", "12"), ("17", "17"), ("18", "18"),
        ("D",  "D"),
        ("Accent", "Accent"), ("Merano", "Merano"),
        ("Latitude", "Latitude"), ("Longitude", "Longitude"),
        # M Collection (pg 66 confirms M51 M52 MR1 M61 M12 M82)
        ("M51", "M51"), ("M52", "M52"), ("M81", "M81"),
        ("M61", "M61"), ("M12", "M12"), ("M82", "M82"),
        ("MR1", "MR1"), ("MR2", "MR2"),
    ]
    _options(conn, fid, "lever", le_levers)

    # ---- Finish (pg 66: 9 available) ----
    le_finishes = [
        ("605",   "605 - Bright Brass"),
        ("606",   "606 - Satin Brass"),
        ("612",   "612 - Satin Bronze"),
        ("618",   "618 - Bright Nickel"),
        ("622",   "622 - Flat Black"),
        ("625",   "625 - Bright Chrome"),
        ("626",   "626 - Satin Chrome"),
        ("626AM", "626AM - Antimicrobial Satin Chrome"),
        ("643e",  "643e - Aged Bronze"),
    ]
    _options(conn, fid, "finish", le_finishes)

    # ---- Rose (pg 66: A, B, C wrought brass/SS; AVA, MER forged brass) ----
    _options(conn, fid, "rose", [
        ("A",   "A Rose"),
        ("B",   "B Rose"),
        ("C",   "C Rose"),
        ("AVA", "AVA Rose"),
        ("MER", "MER Rose"),
    ])

    # ---- Handing (pg 63 detail 11 / pg 66: handed to order) ----
    _options(conn, fid, "handing", [
        ("LH", "LH - Left Hand"),
        ("RH", "RH - Right Hand"),
    ])

    # ---- Functions by chassis (pg 66) ----
    # MS chassis → LEBMS Storeroom only
    # MB chassis → selectable Office, Privacy, Apartment
    # ME chassis → selectable Privacy, Apartment
    _rule(conn, fid, "restrict", "chassis", "MS", "series", "LEB",
          "MS chassis available with LEB")
    _rule(conn, fid, "restrict", "chassis", "MS", "series", "LEBM",
          "MS chassis available with LEBM")
    _rule(conn, fid, "restrict", "chassis", "MB", "series", "LEB",
          "MB chassis available with LEB")
    _rule(conn, fid, "restrict", "chassis", "MB", "series", "LEBM",
          "MB chassis available with LEBM")
    _rule(conn, fid, "restrict", "chassis", "ME", "series", "LEB",
          "ME chassis available with LEB")
    _rule(conn, fid, "restrict", "chassis", "ME", "series", "LEBM",
          "ME chassis available with LEBM")

    # GRW style → rose codes A, B, C, AVA, MER
    # ADD style → escutcheon (no separate rose needed, but for now allow all)

    # AVA/MER roses only with GRW style
    _rule(conn, fid, "conflict", "style", "ADD", "rose", "AVA",
          "AVA rose not available with Addison escutcheon")
    _rule(conn, fid, "conflict", "style", "ADD", "rose", "MER",
          "MER rose not available with Addison escutcheon")

    # SFIC limited to 2" max door thickness (noted on pg 66; info only)

    print(f"  LE Wireless Electronic Lock  (id={fid})")


# =====================================================================
# Helpers
# =====================================================================

def _fid(conn, name):
    return conn.execute(
        "SELECT id FROM hw_families WHERE manufacturer='Schlage' AND name=?",
        (name,),
    ).fetchone()["id"]


def _slot(conn, fid, order, name, label, required):
    conn.execute("""
        INSERT OR IGNORE INTO hw_slots (family_id, slot_order, slot_name, slot_label, required)
        VALUES (?, ?, ?, ?, ?)
    """, (fid, order, name, label, required))


def _options(conn, fid, slot, pairs):
    for i, (val, display) in enumerate(pairs):
        conn.execute("""
            INSERT OR IGNORE INTO hw_options (family_id, slot_name, value, display_name, sort_order)
            VALUES (?, ?, ?, ?, ?)
        """, (fid, slot, val, display, i))


def _restrict(conn, fid, trigger_slot, trigger_val, target_slot, allowed, desc):
    for val in allowed:
        _rule(conn, fid, "restrict", trigger_slot, trigger_val, target_slot, val, desc)


def _rule(conn, fid, rtype, tslot, tval, target_slot, target_val, desc):
    conn.execute("""
        INSERT OR IGNORE INTO hw_rules
            (family_id, rule_type, trigger_slot, trigger_value, target_slot, target_value, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fid, rtype, tslot, tval, target_slot, target_val, desc))


def _cyl_part(conn, fid, design, func, mech, part_num):
    """Store a cylinder part number lookup as a description-tagged rule."""
    conn.execute("""
        INSERT OR IGNORE INTO hw_rules
            (family_id, rule_type, trigger_slot, trigger_value, target_slot, target_value, description)
        VALUES (?, 'restrict', 'design', ?, 'mechanism', ?, ?)
    """, (fid, design, mech, f"PART:{part_num} | func={func}"))


if __name__ == "__main__":
    seed()
