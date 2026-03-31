"""Email utilities for GORO 1.0 - handles vendor quote emails via default mail client."""

import os
import re
import webbrowser
from pathlib import Path
from typing import Optional, List
import csv
from urllib.parse import quote

try:
    import win32com.client as _win32com_client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False


def load_vendor_contacts(vendors_contacts_csv: Path) -> dict:
    """Load vendor contacts from CSV. Returns dict: {vendor_name: email}
    Prioritizes contacts marked as Default=True, falls back to any available contact."""
    vendor_emails = {}
    vendor_defaults = {}  # Track which vendors have a default contact
    
    # Ensure we have a Path object
    if isinstance(vendors_contacts_csv, str):
        vendors_contacts_csv = Path(vendors_contacts_csv)
    
    if not vendors_contacts_csv.exists():
        return vendor_emails
    
    try:
        with open(vendors_contacts_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return vendor_emails
                
            for row in reader:
                vendor = row.get('Vendor Name', '').strip()
                email = row.get('Email', '').strip()
                is_default = row.get('Default', '').strip().lower() == 'true'
                
                if vendor and email:
                    # If this is marked as default, use it
                    if is_default:
                        vendor_emails[vendor] = email
                        vendor_defaults[vendor] = True
                    # If no default set yet for this vendor, use this email
                    elif vendor not in vendor_emails:
                        vendor_emails[vendor] = email
    except Exception:
        pass
    
    return vendor_emails


def launch_outlook_with_pdf(
    recipient_email: str,
    subject: str,
    body: str,
    pdf_path: Path,
    cc: str = "",
    bcc: str = ""
) -> bool:
    """
    Launch Outlook with a pre-filled draft and the PDF attached.

    Tries Outlook COM automation first (attaches the file automatically).
    Falls back to a mailto URL (no attachment) if COM is unavailable.
    """
    if HAS_WIN32COM:
        try:
            return _launch_outlook_com(
                recipient_email, subject, body, pdf_path, cc, bcc
            )
        except Exception:
            pass  # fall through to mailto

    return _launch_mailto(
        recipient_email, subject, body, pdf_path, cc, bcc
    )


def _launch_outlook_com(
    recipient_email: str,
    subject: str,
    body: str,
    pdf_path: Path,
    cc: str = "",
    bcc: str = "",
) -> bool:
    """Create an Outlook MailItem via COM with the PDF attached."""
    outlook = _win32com_client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # olMailItem
    mail.To = recipient_email or ""
    mail.Subject = subject or ""
    mail.Body = body or ""
    if cc:
        mail.CC = cc
    if bcc:
        mail.BCC = bcc

    abs_path = os.path.abspath(str(pdf_path))
    if os.path.isfile(abs_path):
        mail.Attachments.Add(abs_path)

    mail.Display(False)  # show in Outlook without modal block
    return True


def _launch_mailto(
    recipient_email: str,
    subject: str,
    body: str,
    pdf_path: Path,
    cc: str = "",
    bcc: str = ""
) -> bool:
    """Fallback: open a mailto URL (cannot attach files)."""
    try:
        mailto_url = f"mailto:{quote(recipient_email or '')}?subject={quote(subject or '')}"

        if cc:
            mailto_url += f"&cc={quote(cc)}"
        if bcc:
            mailto_url += f"&bcc={quote(bcc)}"

        mailto_url += f"&body={quote(body or '')}"

        webbrowser.open(mailto_url)

        return True
    except Exception as e:
        print(f"Error launching email: {e}")
        return False


def get_vendor_list_from_table(table_data: List[dict], vendor_column: str = "Vendor") -> List[str]:
    """
    Extract unique vendor names from table data.
    
    Args:
        table_data: List of row dictionaries from the table
        vendor_column: Name of the vendor column
    
    Returns:
        Sorted list of unique vendor names
    """
    vendors = set()
    for row in table_data:
        vendor_raw = str(row.get(vendor_column, '')).strip()
        if not vendor_raw:
            continue

        # Support comma/semicolon/newline separated vendor names in one cell.
        parts = [p.strip() for p in re.split(r"[,;\n]+", vendor_raw) if p.strip()]
        if not parts:
            parts = [vendor_raw]
        for vendor in parts:
            vendors.add(vendor)
    return sorted(list(vendors))


def filter_table_by_vendor(table_data: List[dict], vendor: str, vendor_column: str = "Vendor") -> List[dict]:
    """
    Filter table rows to only include those matching the specified vendor.
    
    Args:
        table_data: List of row dictionaries
        vendor: Vendor name to filter by
        vendor_column: Name of the vendor column
    
    Returns:
        Filtered list of rows
    """
    vendor_norm = vendor.strip().casefold()
    filtered: List[dict] = []

    for row in table_data:
        vendor_raw = str(row.get(vendor_column, '')).strip()
        if not vendor_raw:
            continue

        # Keep compatibility with previous exact-match behavior.
        if vendor_raw.casefold() == vendor_norm:
            filtered.append(row)
            continue

        # Also match when multiple vendors are listed in one cell.
        parts = [p.strip().casefold() for p in re.split(r"[,;\n]+", vendor_raw) if p.strip()]
        if vendor_norm in parts:
            filtered.append(row)

    return filtered

