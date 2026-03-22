"""Seed Dormakaba 8600 premium mortise lock line."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_8600(conn)
    _seed_7000(conn)
    print("  Dormakaba 8600 + 7000 seeded.")


# ═════════════════════════════════════════════════════════════════════
# Dormakaba 8600 Series Mortise Lock  (Grade 1, BHMA)
# ═════════════════════════════════════════════════════════════════════

def _seed_8600(conn):
    f = fid(conn, "Dormakaba", "8600 Mortise Lock",
            "Mortise Lock",
            "8600 {function} {cylinder} {lever} {rose} {finish}",
            "Dormakaba 8600 {function} {cylinder} {lever} {rose} {finish}")

    slot(conn, f, 1, "function", "Function",      1)
    slot(conn, f, 2, "cylinder", "Cylinder Type", 1)
    slot(conn, f, 3, "lever",    "Lever Design",  1)
    slot(conn, f, 4, "rose",     "Rose",          1)
    slot(conn, f, 5, "finish",   "Finish",        1)

    options(conn, f, "function", [
        ("8605","8605 - Entrance/Office"),
        ("8608","8608 - Classroom"),
        ("8609","8609 - Classroom Security"),
        ("8613","8613 - Institutional"),
        ("8615","8615 - Dormitory/Exit"),
        ("8620","8620 - Privacy"),
        ("8625","8625 - Storeroom"),
        ("8640","8640 - Apartment Entrance"),
        ("8670","8670 - Passage/Closet"),
    ])

    options(conn, f, "cylinder", [
        ("SFIC","SFIC - Small Format IC"),
        ("LFIC","LFIC - Large Format IC"),
        ("Conv","Conventional Cylinder"),
        ("T-Turn","Thumbturn (Privacy/Passage)"),
    ])

    options(conn, f, "lever", [
        ("W",   "W - Curved Return Lever"),
        ("L",   "L - Angular Lever"),
        ("J",   "J - Rounded Lever"),
        ("E",   "E - Egg Knob"),
    ])

    options(conn, f, "rose", [
        ("RD","RD - Round Rose"),
        ("SQ","SQ - Square Rose"),
        ("ESC","ESC - Escutcheon Plate"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("630","630 - Satin Stainless"),
        ("613","613 - Oil Rubbed Bronze"),
        ("605","605 - Bright Brass"),
        ("625","625 - Bright Chrome"),
    ])

    # Privacy / Passage → Thumbturn only
    restrict(conn, f, "function", "8620", "cylinder", ["T-Turn"],
             "Privacy uses thumbturn")
    restrict(conn, f, "function", "8670", "cylinder", ["T-Turn"],
             "Passage uses thumbturn")


# ═════════════════════════════════════════════════════════════════════
# Dormakaba 7000 Series Cylindrical Lock
# ═════════════════════════════════════════════════════════════════════

def _seed_7000(conn):
    f = fid(conn, "Dormakaba", "7000 Cylindrical Lock",
            "Cylindrical Lock",
            "7000 {function} {cylinder} {lever} {finish}",
            "Dormakaba 7000 {function} {cylinder} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",      1)
    slot(conn, f, 2, "cylinder", "Cylinder Type", 1)
    slot(conn, f, 3, "lever",    "Lever Design",  1)
    slot(conn, f, 4, "finish",   "Finish",        1)

    options(conn, f, "function", [
        ("7005","7005 - Entrance/Office"),
        ("7008","7008 - Classroom"),
        ("7010","7010 - Passage"),
        ("7020","7020 - Privacy"),
        ("7025","7025 - Storeroom"),
        ("7040","7040 - Apartment"),
    ])

    options(conn, f, "cylinder", [
        ("SFIC","SFIC - Small Format IC"),
        ("Conv","Conventional Cylinder"),
        ("N/A", "N/A (Passage / Privacy)"),
    ])

    options(conn, f, "lever", [
        ("W","W - Curved Return Lever"),
        ("L","L - Angular Lever"),
        ("J","J - Rounded Lever"),
    ])

    options(conn, f, "finish", [
        ("626","626 - Satin Chrome"),
        ("630","630 - Satin Stainless"),
        ("613","613 - Oil Rubbed Bronze"),
    ])

    for fn in ("7010", "7020"):
        restrict(conn, f, "function", fn, "cylinder", ["N/A"],
                 f"7000 {fn} has no cylinder")
