"""Quick verification of Trimco seeding in hw_configurator.db."""
import sqlite3, pathlib

DB = pathlib.Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
conn = sqlite3.connect(str(DB))
c = conn.cursor()

# Total families and pricing rows
c.execute("SELECT COUNT(*) FROM hw_families WHERE manufacturer='Trimco'")
fam = c.fetchone()[0]
c.execute("""
    SELECT COUNT(*) FROM hw_pricing p
    JOIN hw_families f ON p.family_id=f.id
    WHERE f.manufacturer='Trimco'
""")
pr = c.fetchone()[0]
print(f"Trimco families: {fam}")
print(f"Trimco pricing rows: {pr}")

# Overall totals
c.execute("SELECT COUNT(*) FROM hw_families")
print(f"Total families: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM hw_pricing")
print(f"Total pricing rows: {c.fetchone()[0]}")

# List Trimco families
print("\nTrimco families:")
for r in c.execute("SELECT name, category FROM hw_families WHERE manufacturer='Trimco' ORDER BY name"):
    print(f"  {r[0]:50s} [{r[1]}]")

# Spot check: boxed item 1001-4x20 finish 605 = $79.30
print("\nSpot check boxed 1001-4x20 / 605:")
c.execute("""
    SELECT p.slot_value, p.amount
    FROM hw_pricing p
    JOIN hw_families f ON p.family_id=f.id
    WHERE f.manufacturer='Trimco' AND p.slot_value='1001-4x20:605'
""")
for r in c.fetchall():
    print(f"  {r[0]} = ${r[1]}")

# Spot check: AP411 12 inch 605/606 = $530.40
print('\nSpot check AP411 / 12" / 605/606:')
c.execute("""
    SELECT p.slot_value, p.amount
    FROM hw_pricing p
    JOIN hw_families f ON p.family_id=f.id
    WHERE f.manufacturer='Trimco' AND p.slot_value LIKE 'AP411:12%'
""")
for r in c.fetchall():
    print(f"  {r[0]} = ${r[1]}")

# Spot check: KE38-1 finish 605 = $711.70
print("\nSpot check KE38-1 / 605:")
c.execute("""
    SELECT p.slot_value, p.amount
    FROM hw_pricing p
    JOIN hw_families f ON p.family_id=f.id
    WHERE f.manufacturer='Trimco' AND p.slot_value='KE38-1:605'
""")
for r in c.fetchall():
    print(f"  {r[0]} = ${r[1]}")

conn.close()
