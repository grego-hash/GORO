"""Find KA050 page and examine word layout."""
import pdfplumber, pathlib

pdf_path = pathlib.Path(r"C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\Trimco_List_Price_26_CAN.pdf")
pdf = pdfplumber.open(str(pdf_path))
for i, page in enumerate(pdf.pages):
    text = page.extract_text() or ""
    if "KA050" in text:
        print(f"Page {i+1}: found KA050")
        words = page.extract_words()
        ka_words = [w for w in words if "KA" in w["text"]]
        for w in ka_words:
            print(f"  x={w['x0']:.0f} y={w['top']:.0f} text={w['text']}")
        # Show all words on this page
        print(f"\nAll words on page {i+1}:")
        for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
            print(f"  x={w['x0']:.1f} y={w['top']:.1f} text={w['text']}")
        break
pdf.close()
