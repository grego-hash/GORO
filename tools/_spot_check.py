import csv
with open("data/trimco_ap_items.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("AP411 12\":")
for r in rows:
    if r["family"] == "AP411" and r["size"] == '12"':
        print(f"  {r['finish']} = ${r['price']}")

print("\nAP412 12\":")
for r in rows:
    if r["family"] == "AP412" and r["size"] == '12"':
        print(f"  {r['finish']} = ${r['price']}")

print("\nAP413 36\":")
for r in rows:
    if r["family"] == "AP413" and r["size"] == '36"':
        print(f"  {r['finish']} = ${r['price']}")

# Count families
families = sorted(set(r["family"] for r in rows))
print(f"\n{len(families)} families: {families}")
