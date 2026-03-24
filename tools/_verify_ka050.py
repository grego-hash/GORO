"""Verify KA050 is in the database."""
import sqlite3

conn = sqlite3.connect("data/hw_configurator.db")
conn.row_factory = sqlite3.Row

# Find Armor Plate family
rows = conn.execute("""
    SELECT f.id, f.name, f.category, f.assembly_pattern, f.description_template
    FROM hw_families f
    WHERE f.manufacturer = 'Trimco' AND f.name LIKE '%Armor%'
""").fetchall()
for r in rows:
    print("Family: {} (id={}, cat={})".format(r["name"], r["id"], r["category"]))
    print("  Assembly: {}".format(r["assembly_pattern"]))
    print("  Desc: {}".format(r["description_template"]))

# Find KA050 pricing
rows = conn.execute("""
    SELECT p.slot_name, p.slot_value, p.price_type, p.amount
    FROM hw_pricing p
    JOIN hw_families f ON p.family_id = f.id
    WHERE f.manufacturer = 'Trimco' AND f.name LIKE '%Armor%'
    ORDER BY p.slot_value
""").fetchall()
print("\nArmor Plate pricing: {} rows".format(len(rows)))
for r in rows:
    print("  {} = {} -> ${:.2f}".format(r["slot_name"], r["slot_value"], r["amount"]))

# Show model options
rows = conn.execute("""
    SELECT o.value, o.display_name
    FROM hw_options o
    JOIN hw_families f ON o.family_id = f.id
    WHERE f.manufacturer = 'Trimco' AND f.name LIKE '%Armor%' AND o.slot_name = 'model'
    ORDER BY o.value
""").fetchall()
print("\nModel options:")
for r in rows:
    print("  {} -> {}".format(r["value"], r["display_name"]))

# Show all protection plate families
rows = conn.execute("""
    SELECT f.name, f.category
    FROM hw_families f
    WHERE f.manufacturer = 'Trimco' AND f.category = 'Door Protection Plate'
    ORDER BY f.name
""").fetchall()
print("\nAll protection plate families:")
for r in rows:
    print("  {} ({})".format(r["name"], r["category"]))

# Total counts
row = conn.execute("SELECT COUNT(*) FROM hw_families").fetchone()
print("\nTotal families: {}".format(row[0]))
row = conn.execute("SELECT COUNT(*) FROM hw_pricing").fetchone()
print("Total pricing rows: {}".format(row[0]))

conn.close()
