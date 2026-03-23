import sqlite3

conn = sqlite3.connect('data/hw_configurator.db')
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Check for Hager families
for t in tables:
    if 'famil' in t.lower():
        cur.execute(f"SELECT * FROM {t} WHERE manufacturer='Hager' LIMIT 5")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        print(f"\nTable {t}, cols: {cols}")
        print(f"Hager rows: {len(rows)}")
        for r in rows:
            print(f"  {r}")
        # Count all Hager
        cur.execute(f"SELECT COUNT(*) FROM {t} WHERE manufacturer='Hager'")
        print(f"Total Hager: {cur.fetchone()[0]}")

conn.close()
