# PDF Import Feature Guide

## Installation

### ✅ Poppler (Built-in)

**Good news!** Poppler is now bundled with GORO and installed automatically. You don't need to install it separately.

### 1. Install Python Dependencies

```bash
pip install -r requirements_pdf.txt
```

Or install packages individually:

```bash
pip install pdfplumber pdf2image pytesseract Pillow
```

### 2. Tesseract OCR (Installed by GORO Setup)

GORO now packages the official Tesseract installer inside the Windows installer and installs it automatically into the GORO app folder during setup.

If the user installs GORO using the normal GORO setup EXE, no separate Tesseract install is required.

**Development only:** if you're running from source instead of the installed app, the build script downloads the Tesseract installer, but OCR is only provisioned automatically when you install GORO through the generated installer EXE.

**Note:** Tesseract is only used for scanned PDFs. Text-based PDFs work automatically with the bundled Poppler.

## How to Use

### Basic Workflow

1. **Open a Schedule**
   - Navigate to Bids or Projects
   - Click "View Schedule" for any workbook

2. **Click "Import from PDF"**
   - Button appears at the top of the schedule dialog
   - Only visible if PDF libraries are installed

3. **Select Your PDF**
   - Choose the PDF file containing the table you want to import

4. **Automatic Text Extraction (For Text-Based PDFs)**
   - If the PDF contains selectable text, pdfplumber will extract it automatically
   - You'll be asked to select the page (if multiple pages)
   - Then select which table (if multiple tables on the page)

5. **Manual OCR Selection (For Scanned PDFs)**
   - If text extraction fails, the OCR mode activates
   - An image of the PDF page will appear
   - **Draw a rectangle** around the table you want to import
   - Click "OK" to process

6. **Map Columns**
   - A dialog shows the detected columns from your PDF
   - Map each PDF column to a CSV column using the dropdowns
   - Auto-matching attempts to match column names automatically
   - Select "Skip" for columns you don't want to import
   - Click "OK" to import

7. **Review Imported Data**
   - The data will be appended to the end of your current schedule tab
   - Review and edit as needed
   - Save changes when done

## Tips

### For Best Results

- **Text-based PDFs**: These work best with pdfplumber (fast and accurate)
- **Scanned PDFs**: Use OCR mode, ensure text is clear and high contrast
- **Table Selection**: When drawing the OCR rectangle, include the entire table but minimize extra whitespace
- **Column Mapping**: Review the auto-matching suggestions before importing
- **Data Cleanup**: After import, review the data as OCR may have some errors with numbers/special characters

### Common Issues

**"Import from PDF" button not visible:**
- Install the required libraries (`pip install -r requirements_pdf.txt`)
- Restart the application after installation

**OCR produces garbled text:**
- Make sure the PDF image quality is good
- Try selecting a smaller, more focused region
- Check that Tesseract is properly installed

**Tesseract not found:**
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Make sure it's added to your PATH
- Or specify the path in the code: `pytesseract.pytesseract.tesseract_cmd`

**Columns don't match:**
- Use the column mapping dialog to manually map each column
- You can skip columns that aren't needed
- Column names are matched based on similarity

## Supported PDF Types

### ✅ Works Best With:
- PDFs with selectable text (created digitally)
- Tables with clear structure
- Scanned documents with high-quality images
- Black text on white background

### ⚠️ May Have Issues With:
- Handwritten tables
- Complex multi-level headers
- Tables with merged cells
- Very low resolution scans
- Colored backgrounds or watermarks

## Technical Details

The import feature uses a **hybrid approach**:

1. **Try pdfplumber first** (fast text extraction)
   - Detects tables automatically
   - Preserves structure and formatting
   - Works only with text-based PDFs

2. **Fall back to OCR** (image-based extraction)
   - Converts PDF page to image
   - User selects region manually
   - Uses Tesseract OCR engine
   - Works with scanned documents

This gives you the best of both worlds - speed for text PDFs and flexibility for scanned documents.
