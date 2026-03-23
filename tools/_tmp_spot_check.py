"""Spot check all new Von Duprin option slots."""
import sqlite3

conn = sqlite3.connect("../data/hw_configurator.db")

# Check how many slots per family
rows = conn.execute("""
    SELECT f.name, COUNT(s.id) as slot_count
    FROM hw_families f
    JOIN hw_slots s ON s.family_id = f.id
    WHERE f.manufacturer = 'Von Duprin'
    GROUP BY f.id
    ORDER BY f.name
""").fetchall()
print("=== Slots per family ===")
for name, cnt in rows:
    print(f"  {cnt:2d} slots | {name}")

# Check slots for 98/99 specifically
print()
print("=== 98/99 Series Slots ===")
rows = conn.execute("""
    SELECT s.slot_order, s.slot_key, s.display_name, s.required
    FROM hw_slots s
    JOIN hw_families f ON f.id = s.family_id
    WHERE f.name = '98/99 Series Exit Device'
    ORDER BY s.slot_order
""").fetchall()
for order, key, name, req in rows:
    print(f"  {order:2d}. {key:20s} {name:35s} req={req}")

# Check pricing for some options
print()
print("=== Sample option prices (98/99) ===")
rows = conn.execute("""
    SELECT p.slot_key, p.option_key, p.amount
    FROM hw_pricing p
    JOIN hw_families f ON f.id = p.family_id
    WHERE f.name = '98/99 Series Exit Device'
    AND p.slot_key IN ('dogging','switch','qel','electric','alarm','outdoor',
                       'weep','antimicrobial','accessible','dbl_cylinder',
                       'fer','quiet_mech','delay','chexit')
    ORDER BY p.slot_key, p.option_key
""").fetchall()
for sk, ok, amt in rows:
    print(f"  {sk:20s} {ok:15s} = ${amt:,.0f}")

# Check a simple family - 75 Rim
print()
print("=== 75 Series Rim Exit Device Slots ===")
rows = conn.execute("""
    SELECT s.slot_order, s.slot_key, s.display_name, s.required
    FROM hw_slots s
    JOIN hw_families f ON f.id = s.family_id
    WHERE f.name = '75 Series Rim Exit Device'
    ORDER BY s.slot_order
""").fetchall()
for order, key, name, req in rows:
    print(f"  {order:2d}. {key:20s} {name:35s} req={req}")

# Check 22 Series options
print()
print("=== 22 Series Rim Slots ===")
rows = conn.execute("""
    SELECT s.slot_order, s.slot_key, s.display_name, s.required
    FROM hw_slots s
    JOIN hw_families f ON f.id = s.family_id
    WHERE f.name = '22 Series Rim Exit Device'
    ORDER BY s.slot_order
""").fetchall()
for order, key, name, req in rows:
    print(f"  {order:2d}. {key:20s} {name:35s} req={req}")

# Check 94/95 CVR47 options
print()
print("=== 94/95 CVR47 Slots ===")
rows = conn.execute("""
    SELECT s.slot_order, s.slot_key, s.display_name, s.required
    FROM hw_slots s
    JOIN hw_families f ON f.id = s.family_id
    WHERE f.name = '94/95 Series Concealed Vertical Rod (CVR47)'
    ORDER BY s.slot_order
""").fetchall()
for order, key, name, req in rows:
    print(f"  {order:2d}. {key:20s} {name:35s} req={req}")

# Verify specific prices match catalog
print()
print("=== Price Verification ===")
checks = [
    ("98/99 Series Exit Device", "dogging", "CD", 158),
    ("98/99 Series Exit Device", "dogging", "CDSI", 521),
    ("98/99 Series Exit Device", "dogging", "SD", 667),
    ("98/99 Series Exit Device", "switch", "RX", 419),
    ("98/99 Series Exit Device", "switch", "SS", 861),
    ("98/99 Series Exit Device", "qel", "QEL", 1446),
    ("98/99 Series Exit Device", "qel", "SD-QEL", 2113),
    ("98/99 Series Exit Device", "qel", "PN", 2348),
    ("98/99 Series Exit Device", "electric", "E", 1045),
    ("98/99 Series Exit Device", "alarm", "ALK", 1042),
    ("98/99 Series Exit Device", "outdoor", "OUT", 657),
    ("98/99 Series Exit Device", "weep", "WH", 147),
    ("98/99 Series Exit Device", "antimicrobial", "AM", 111),
    ("98/99 Series Exit Device", "accessible", "AX", 102),
    ("98/99 Series Exit Device", "dbl_cylinder", "-2", 544),
    ("98/99 Series Exit Device", "dbl_cylinder", "-2SI", 910),
    ("98/99 Series Exit Device", "fer", "FER", 602),
    ("98/99 Series Exit Device", "quiet_mech", "QM", 303),
    ("98/99 Series Exit Device", "chexit", "CXA", 3066),
    ("98/99 Series Exit Device", "delay", "0-DELAY", 223),
    ("98/99 Series Exit Device", "delay", "OTHER", 302),
    ("22 Series Rim Exit Device", "alarm", "ALK", 925),
    ("22 Series Rim Exit Device", "accessible", "AX", 38),
    ("75 Series Rim Exit Device", "dogging", "CD", 158),
    ("75 Series Rim Exit Device", "switch", "RX", 419),
]

passed = 0
failed = 0
for family, slot_key, opt_key, expected in checks:
    row = conn.execute("""
        SELECT p.amount FROM hw_pricing p
        JOIN hw_families f ON f.id = p.family_id
        WHERE f.name = ? AND p.slot_key = ? AND p.option_key = ?
    """, (family, slot_key, opt_key)).fetchone()
    actual = row[0] if row else None
    if actual == expected:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {family} / {slot_key}={opt_key}: expected ${expected}, got {actual}")

print(f"  {passed}/{passed+failed} price checks PASSED")

conn.close()
