import sqlite3

conn = sqlite3.connect('data/hw_configurator.db')
cur = conn.cursor()

cur.execute("SELECT id, name, category FROM hw_families WHERE manufacturer='Hager' ORDER BY name")
for r in cur.fetchall():
    print(f"  ID={r[0]:3d} [{r[2]}] {r[1]}")

cur.execute("SELECT COUNT(*) FROM hw_pricing p JOIN hw_families f ON f.id=p.family_id WHERE f.manufacturer='Hager'")
print(f"\nTotal Hager pricing rows: {cur.fetchone()[0]}")

# Check which ones have pricing
cur.execute("""
    SELECT f.id, f.name, COUNT(p.id) as cnt
    FROM hw_families f
    LEFT JOIN hw_pricing p ON p.family_id = f.id
    WHERE f.manufacturer='Hager'
    GROUP BY f.id ORDER BY f.name
""")
for r in cur.fetchall():
    print(f"  ID={r[0]:3d} prices={r[2]:3d} {r[1]}")

conn.close()
