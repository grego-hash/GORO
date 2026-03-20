"""Email utilities for GORO 1.0 - handles vendor quote emails via Outlook."""

import subprocess
import tempfile
import re
from pathlib import Path
from typing import Optional, List
import csv


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
    Launch Outlook with PDF attachment using Windows COM.
    
    Args:
        recipient_email: Email address of recipient
        subject: Email subject line
        body: Email body text
        pdf_path: Path to PDF file to attach
        cc: Optional CC email addresses
        bcc: Optional BCC email addresses
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import win32com.client
        
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 = MailItem
        
        mail.To = recipient_email
        mail.Subject = subject
        mail.Body = body
        
        if cc:
            mail.CC = cc
        if bcc:
            mail.BCC = bcc
        
        # Add attachment
        if pdf_path.exists():
            mail.Attachments.Add(str(pdf_path.absolute()))
        
        mail.Display(False)  # Show the email composition window
        return True
        
    except ImportError:
        # pywin32 not installed, fallback to command line
        return launch_outlook_via_shell(
            recipient_email, subject, body, pdf_path, cc, bcc
        )
    except Exception as e:
        print(f"Error launching Outlook: {e}")
        return False


def launch_outlook_via_shell(
    recipient_email: str,
    subject: str,
    body: str,
    pdf_path: Path,
    cc: str = "",
    bcc: str = ""
) -> bool:
    """
    Fallback: Launch Outlook via command line with file attachment.
    Note: This method may have limitations with PDF attachment but still opens Outlook.
    """
    try:
        # Build Outlook URL - note: attachments via mailto: have limited support
        # This will open Outlook with email pre-filled, user can manually attach PDF
        mailto_url = f"mailto:{recipient_email}?subject={subject}"
        
        if cc:
            mailto_url += f"&cc={cc}"
        if bcc:
            mailto_url += f"&bcc={bcc}"
        
        # URL encode the body text (basic encoding)
        body_encoded = body.replace('\n', '%0D%0A').replace(' ', '%20')
        mailto_url += f"&body={body_encoded}"
        
        # Try to open with Outlook
        import webbrowser
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

