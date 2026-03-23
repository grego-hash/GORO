import sqlite3
conn = sqlite3.connect("data/hw_configurator.db")
conn.row_factory = sqlite3.Row

print("=== Schlage families ===")
rows = conn.execute("SELECT id, name, category FROM hw_families WHERE manufacturer='Schlage'").fetchall()
for r in rows:
    print(dict(r))

print("\n=== Pricing row count per family ===")
rows = conn.execute("""
    SELECT f.name, COUNT(p.id) as price_count
    FROM hw_families f
    LEFT JOIN hw_pricing p ON p.family_id = f.id
    WHERE f.manufacturer = 'Schlage'
    GROUP BY f.id
""").fetchall()
for r in rows:
    print(dict(r))

print("\n=== ALL families (mfr, name) ===")
rows = conn.execute("SELECT manufacturer, name FROM hw_families ORDER BY manufacturer, name").fetchall()
for r in rows:
    print(f"  {r['manufacturer']} - {r['name']}")
