"""Dump page 79 word layout for KA plate analysis."""
import pdfplumber
from collections import defaultdict

PDF = r"C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\Trimco_List_Price_26_CAN.pdf"

with pdfplumber.open(PDF) as pdf:
    page = pdf.pages[78]  # page 79 (0-indexed)
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)

    # Group by y position
    rows = defaultdict(list)
    for w in words:
        y_key = round(w["top"] / 4) * 4
        rows[y_key].append(w)

    for y in sorted(rows.keys()):
        ws = sorted(rows[y], key=lambda w: w["x0"])
        parts = []
        for w in ws:
            parts.append("{:>12s}(@{:.0f})".format(w["text"], w["x0"]))
        line = "  ".join(parts)
        print("y={:5.0f}: {}".format(y, line))
