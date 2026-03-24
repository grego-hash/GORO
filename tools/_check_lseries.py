import sqlite3, pathlib
db = pathlib.Path("data/hw_configurator.db")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
c = conn.cursor()
fid = c.execute("SELECT id FROM hw_families WHERE manufacturer='Schlage' AND name='L Series Mortise Lock'").fetchone()[0]
print("Family ID:", fid)
rows = c.execute("SELECT slot_name, COUNT(*) as cnt FROM hw_pricing WHERE family_id=? GROUP BY slot_name", (fid,)).fetchall()
print("Pricing slot_names:")
for r in rows:
    print(f"  {r['slot_name']}: {r['cnt']} rows")
# Show a few compound rows
print("\nSample compound rows:")
for r in c.execute("SELECT slot_name, slot_value, amount FROM hw_pricing WHERE family_id=? AND slot_name LIKE '%:%' LIMIT 10", (fid,)).fetchall():
    print(f"  {r['slot_name']} = {r['slot_value']} -> ${r['amount']}")
# Show non-compound function rows
print("\nNon-compound function rows:")
for r in c.execute("SELECT slot_name, slot_value, amount FROM hw_pricing WHERE family_id=? AND slot_name='function' LIMIT 10", (fid,)).fetchall():
    print(f"  {r['slot_name']} = {r['slot_value']} -> ${r['amount']}")
conn.close()
