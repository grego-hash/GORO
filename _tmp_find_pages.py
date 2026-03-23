from pdfminer.high_level import extract_text

PDF = r'C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\hager.pdf'

# Find 5100 closer section
for p in range(130, 158):
    text = extract_text(PDF, page_numbers=[p])
    lines = [l.strip() for l in text.split('\n') if l.strip()][:5]
    header = ' | '.join(lines)
    print(f"p{p+1}: {header[:120]}")
