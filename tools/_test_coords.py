"""Dump AP series page 26-27 data rows."""
import pdfplumber
from collections import defaultdict

PDF = r"C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\Trimco_List_Price_26_CAN.pdf"

pdf = pdfplumber.open(PDF)

for pi in [25, 26]:  # pages 26, 27
    page = pdf.pages[pi]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    
    rows_by_y = defaultdict(list)
    for w in words:
        y_key = round(w["top"] / 8) * 8
        rows_by_y[y_key].append(w)
    
    print(f"=== PAGE {pi+1} ===")
    for y in sorted(rows_by_y.keys()):
        row_words = sorted(rows_by_y[y], key=lambda w: w["x0"])
        parts = ", ".join(f"{w['text']}@{w['x0']:.0f}" for w in row_words)
        print(f"  y={y}: {parts}")
    print()

pdf.close()
