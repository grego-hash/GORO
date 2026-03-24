"""Quick verification of Schlage cylinder seeding."""
import sqlite3, os

db = os.path.join(os.path.dirname(__file__), "..", "data", "hw_configurator.db")
conn = sqlite3.connect(db)

print("=== Schlage Cylinder Families ===")
for r in conn.execute(
    "SELECT id, name FROM hw_families WHERE manufacturer='Schlage' AND category='Cylinder' ORDER BY id"
):
    print(f"  [{r[0]}] {r[1]}")

# FSIC Cores (20-740)
fid = conn.execute("SELECT id FROM hw_families WHERE name='FSIC Cores'").fetchone()[0]
print(f"\n=== FSIC Cores (20-740) — family_id={fid} ===")
for r in conn.execute(
    "SELECT slot_value, amount FROM hw_pricing WHERE family_id=? AND slot_name='application:mechanism' ORDER BY slot_value",
    (fid,),
):
    print(f"  {r[0]} = ${r[1]:.2f}")

# FSIC Rim (20-757)
fid2 = conn.execute("SELECT id FROM hw_families WHERE name='FSIC Rim Cylinders'").fetchone()[0]
print(f"\n=== FSIC Rim Cylinders (20-757) — family_id={fid2} ===")
for r in conn.execute(
    "SELECT slot_value, amount FROM hw_pricing WHERE family_id=? AND slot_name='application:mechanism' ORDER BY slot_value",
    (fid2,),
):
    print(f"  {r[0]} = ${r[1]:.2f}")

# Totals
tf = conn.execute("SELECT COUNT(*) FROM hw_families").fetchone()[0]
tp = conn.execute("SELECT COUNT(*) FROM hw_pricing").fetchone()[0]
print(f"\nDatabase total: {tf} families, {tp} pricing rows")
conn.close()
