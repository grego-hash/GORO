"""Summarize each page of the Trimco pricebook text extraction."""
with open("data/trimco_pricebook_text.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith("--- PAGE"):
        context = []
        for j in range(i + 1, min(i + 15, len(lines))):
            stripped = lines[j].strip()
            if stripped and not stripped.startswith("(cid:"):
                context.append(stripped)
            if len(context) >= 4:
                break
        summary = " | ".join(context[:3])
        print(f"{line.strip()}  ->  {summary}")
