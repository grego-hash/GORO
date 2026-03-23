"""Seed LCN 8310 Series Actuators & Accessories pricing.

Source: LCN Price Book 16, effective February 27, 2026 (pp 116-128).
Families: Touchless Actuator, Push Actuator, Actuator Kit,
          Transmitter & Receiver, Safety Sensor, Accessory
"""

from seed_helpers import fid, slot, options, price, price_bulk


def seed(conn):
    _seed_touchless(conn)
    _seed_push(conn)
    _seed_kit(conn)
    _seed_tx_rx(conn)
    _seed_safety(conn)
    _seed_accessory(conn)
    print("  LCN 8310 Actuators & Accessories (6 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 8310 Touchless Actuators — standalone units
# Heavy Duty (stainless), Standard Duty, Battery powered
# ═══════════════════════════════════════════════════════════════
def _seed_touchless(conn):
    f = fid(conn, "LCN", "8310 Touchless Actuator", "Actuator",
            "8310-{config}",
            "LCN 8310-{config} Touchless Actuator")
    slot(conn, f, 1, "config", "Model", 1)
    options(conn, f, "config", [
        ("810D",   "Double Gang, HD, Stainless Steel"),
        ("810S",   "Single Gang, HD, Stainless Steel"),
        ("810R",   "Round, HD, Stainless Steel"),
        ("813",    "Single/Double Gang, SD, Black"),
        ("813WH",  "Single/Double Gang, SD, White"),
        ("813R",   "Round, SD, Black"),
        ("813J",   "Jamb, SD, Black"),
        ("813JWH", "Jamb, SD, White"),
        ("815",    "Surface Mount Box, HD, Stainless Steel"),
        ("2310",   "Single Gang, Battery, SS"),
        ("2320",   "Double Gang, Battery, SS"),
        ("2330",   "Narrow, Battery, SS"),
        ("2340",   "Round, Battery, SS"),
    ])
    price_bulk(conn, f, "config", [
        ("810D", 1131.00),  ("810S", 1042.00),  ("810R", 1131.00),
        ("813", 765.00),    ("813WH", 812.00),  ("813R", 765.00),
        ("813J", 765.00),   ("813JWH", 812.00), ("815", 999.00),
        ("2310", 588.00),   ("2320", 593.00),   ("2330", 588.00),
        ("2340", 593.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 8310 Push / Wall Actuators — standalone push units
# ═══════════════════════════════════════════════════════════════
def _seed_push(conn):
    f = fid(conn, "LCN", "8310 Push Actuator", "Actuator",
            "8310-{config}",
            "LCN 8310-{config} Push Actuator")
    slot(conn, f, 1, "config", "Model", 1)
    options(conn, f, "config", [
        ("818",  "Jamb Mount, 1.5\" x 4.75\""),
        ("856",  "Wall Mount, 4.5\" Round"),
        ("853",  "Wall Mount, 4.75\" Square"),
        ("855",  "Wall Mount, 4.75\" Sq. Dual Vestibule"),
        ("852",  "Wall Mount, 6\" Round"),
        ("836T", "Wall Mount, 36\" x 6\" Full Length"),
    ])
    price_bulk(conn, f, "config", [
        ("818", 302.00),  ("856", 351.00),  ("853", 438.00),
        ("855", 692.00),  ("852", 457.00),  ("836T", 1653.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 8310 Actuator Kits & Packages
# Touchless kits, wireless kits, pair packages, restroom kits
# ═══════════════════════════════════════════════════════════════
def _seed_kit(conn):
    f = fid(conn, "LCN", "8310 Actuator Kit", "Actuator",
            "8310-{config}",
            "LCN 8310-{config} Actuator Kit")
    slot(conn, f, 1, "config", "Kit", 1)
    options(conn, f, "config", [
        # Touchless kits (actuator pair + receiver + transmitters)
        ("3810DW",  "(2) HD Double Gang + Rcvr + (2) TX"),
        ("3810RW",  "(2) HD Round + Rcvr + (2) TX"),
        ("3813W",   "(2) SD Black + Rcvr + (2) TX"),
        ("3813RW",  "(2) SD Round + Rcvr + (2) TX"),
        ("3813JW",  "(2) SD Jamb + Rcvr + (2) TX"),
        ("2210",    "(2) Battery SG + Wireless Rcvr"),
        # Wireless kits (actuator + transmitter + box)
        ("3818W",   "Jamb Wireless Kit"),
        ("3856W",   "4.5\" Round Wireless Kit"),
        ("853WP",   "4.75\" Sq. Wireless Surface Kit"),
        ("3853W",   "4.75\" Sq. Wireless Kit"),
        ("3855W",   "Dual Vestibule Wireless Kit"),
        ("852WP",   "6\" Round Wireless Surface Kit"),
        ("3852W",   "6\" Round Wireless Kit"),
        ("836TW",   "Full Length Wireless"),
        # Pair packages
        ("3822T",   "(2) Jamb Actuator Pack"),
        ("3822TW",  "(2) Jamb Wireless Pack"),
        ("3860T",   "(2) 4.5\" Round Pack"),
        ("3860TW",  "(2) 4.5\" Round Wireless Pack"),
        ("3857T",   "(2) 4.75\" Square Pack"),
        ("3857TW",  "(2) 4.75\" Square Wireless Pack"),
        # Restroom kits
        ("2410",    "Touchless Restroom Kit"),
        ("2420",    "Push Plate Restroom Kit"),
    ])
    price_bulk(conn, f, "config", [
        ("3810DW", 3007.00),  ("3810RW", 3007.00),
        ("3813W", 2274.00),   ("3813RW", 2274.00),  ("3813JW", 2274.00),
        ("2210", 1497.00),
        ("3818W", 668.00),    ("3856W", 930.00),
        ("853WP", 1179.00),   ("3853W", 1059.00),
        ("3855W", 1621.00),
        ("852WP", 1179.00),   ("3852W", 1059.00),
        ("836TW", 1914.00),
        ("3822T", 692.00),    ("3822TW", 1344.00),
        ("3860T", 1141.00),   ("3860TW", 2198.00),
        ("3857T", 1375.00),   ("3857TW", 2435.00),
        ("2410", 3552.00),    ("2420", 2763.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 8310 Transmitters & Receivers
# ═══════════════════════════════════════════════════════════════
def _seed_tx_rx(conn):
    f = fid(conn, "LCN", "8310 Transmitter & Receiver", "Actuator",
            "8310-{config}",
            "LCN 8310-{config}")
    slot(conn, f, 1, "config", "Model", 1)
    options(conn, f, "config", [
        ("880",  "900 MHz Receiver"),
        ("865",  "433 MHz Receiver, 1-ch Sequencing"),
        ("881",  "900MHz Handheld, 1-button"),
        ("882",  "900MHz Handheld, 2-button"),
        ("883",  "900MHz Handheld, 3-button"),
        ("884",  "900MHz Handheld, 4-button"),
        ("885",  "900MHz Handheld, Retrofit"),
        ("886",  "900MHz Hardwired"),
        ("844",  "433MHz Wall Transmitter, 9v"),
        ("844J", "433MHz Jamb Transmitter, 3v"),
    ])
    price_bulk(conn, f, "config", [
        ("880", 238.00),  ("865", 359.00),
        ("881", 244.00),  ("882", 290.00),  ("883", 301.00),
        ("884", 308.00),  ("885", 252.00),  ("886", 244.00),
        ("844", 342.00),  ("844J", 342.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 8310 Safety Sensors & Sensor Kits
# ═══════════════════════════════════════════════════════════════
def _seed_safety(conn):
    f = fid(conn, "LCN", "8310 Safety Sensor", "Actuator",
            "8310-{config}",
            "LCN 8310-{config} Safety Sensor")
    slot(conn, f, 1, "config", "Model", 1)
    options(conn, f, "config", [
        ("804-1", "Door Mount Safety, 1 Element"),
        ("804-2", "Door Mount Safety, 2 Elements"),
        ("875",   "Header Mount Activation, K-band"),
        ("877",   "Header Mount Safety, Infrared"),
        ("878",   "Monitored Safety Kit, Single Door"),
        ("879",   "Monitored Safety Kit, Double Door"),
        ("3881",  "Activation + Safety Package, Single Door"),
        ("3882",  "Activation + Safety Package, Double Door"),
        ("3883",  "Low Energy Safety Package, Single Door"),
        ("3891",  "Safety Package, Simultaneous Pair"),
        ("3892",  "Safety Package, Independent Pair"),
    ])
    price_bulk(conn, f, "config", [
        ("804-1", 2118.00),  ("804-2", 2891.00),
        ("875", 1344.00),    ("877", 2563.00),
        ("878", 7326.00),    ("879", 13071.00),
        ("3881", 10014.00),  ("3882", 13750.00),
        ("3883", 2891.00),
        ("3891", 12889.00),  ("3892", 13750.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 8310 Accessories
# DPS, transformer, boxes, weather rings, escutcheons, switches,
# bollards, wireless conversion kits, relay module
# ═══════════════════════════════════════════════════════════════
def _seed_accessory(conn):
    f = fid(conn, "LCN", "8310 Accessory", "Actuator",
            "8310-{config}",
            "LCN 8310-{config}")
    slot(conn, f, 1, "config", "Item", 1)
    options(conn, f, "config", [
        ("805",  "Door Position Switch"),
        ("824",  "Transformer, 24v Hardwired"),
        ("800",  "Weather Ring, 4.5\" Round"),
        ("801",  "Weather Ring, 4.75\" Square"),
        ("802",  "Weather Ring, 6\" Round"),
        ("819",  "Jamb Box (Flush or Surface)"),
        ("867",  "Box, 4.75\" Square"),
        ("868",  "Box, 4.5\" Round"),
        ("869",  "Box, 6\" Round"),
        ("874",  "Escutcheon, 4.5\" Round"),
        ("876",  "Escutcheon, 6\" Round"),
        ("806K", "Key Switch (On/Off/Hold)"),
        ("806R", "Rocker Switch (On/Off/Hold)"),
        ("845",  "Programmable Relay Module"),
        ("866",  "Bollard Post, 42\" x 4\" x 6\""),
        ("3803", "Wireless Conversion Kit, Jamb"),
        ("3809", "Wireless Conversion Kit, Wall"),
        ("3889", "Pneumatic Safety Module Kit"),
    ])
    price_bulk(conn, f, "config", [
        ("805", 95.00),    ("824", 139.00),
        ("800", 41.00),    ("801", 41.00),    ("802", 41.00),
        ("819", 66.00),    ("867", 285.00),   ("868", 253.00),
        ("869", 278.00),
        ("874", 626.00),   ("876", 626.00),
        ("806K", 359.00),  ("806R", 359.00),
        ("845", 554.00),   ("866", 1547.00),
        ("3803", 984.00),  ("3809", 984.00),  ("3889", 881.00),
    ])
