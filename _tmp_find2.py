from pdfminer.high_level import extract_text

PDF = r'C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\hager.pdf'
for p in range(32, 76):
    text = extract_text(PDF, page_numbers=[p])
    lines = [l.strip() for l in text.split('\n') if l.strip()][:4]
    header = " | ".join(l[:60] for l in lines)
    print(f"p{p+1}: {header}")
