"""Milestone management system for GORO 1.0.

Allows users to save workbook snapshots as read-only milestones with options to:
- View milestone information
- Revert a workbook to a previous milestone
- Copy a milestone to a new editable workbook
- Compare current workbook with a milestone to see changes
"""

import json
import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Milestone:
    """Represents a saved workbook milestone."""
    name: str
    created: str  # ISO format timestamp
    description: str
    milestone_path: Path


def get_milestones_dir(workbook_path: Path) -> Path:
    """Get the milestones directory for a workbook."""
    milestones_dir = workbook_path / ".milestones"
    milestones_dir.mkdir(parents=True, exist_ok=True)
    return milestones_dir


def _set_tree_readonly(folder: Path) -> None:
    """Mark every file under *folder* as read-only."""
    for f in folder.rglob('*'):
        if f.is_file():
            try:
                f.chmod(f.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
            except Exception:
                pass


def _set_tree_writable(folder: Path) -> None:
    """Remove the read-only flag from every file under *folder*."""
    for f in folder.rglob('*'):
        if f.is_file():
            try:
                f.chmod(f.stat().st_mode | stat.S_IWUSR)
            except Exception:
                pass


def list_milestones(workbook_path: Path) -> List[Milestone]:
    """List all milestones for a workbook, sorted by creation date (newest first)."""
    milestones_dir = get_milestones_dir(workbook_path)
    milestones = []
    
    try:
        for milestone_folder in sorted(milestones_dir.iterdir(), reverse=True):
            if not milestone_folder.is_dir() or milestone_folder.name.startswith('.'):
                continue
            
            meta_file = milestone_folder / "milestone.json"
            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    milestone = Milestone(
                        name=meta.get('name', milestone_folder.name),
                        created=meta.get('created', ''),
                        description=meta.get('description', ''),
                        milestone_path=milestone_folder
                    )
                    milestones.append(milestone)
                except Exception:
                    pass
    except Exception:
        pass
    
    return milestones


def create_milestone(workbook_path: Path, name: str, description: str = "") -> bool:
    """
    Create a new milestone (snapshot) of the current workbook.
    
    Args:
        workbook_path: Path to the workbook directory
        name: Name for the milestone
        description: Optional description
    
    Returns:
        True if successful, False otherwise
    """
    if not workbook_path.exists():
        return False
    
    try:
        # Create milestone directory with timestamp
        milestones_dir = get_milestones_dir(workbook_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        milestone_folder = milestones_dir / f"{timestamp}_{name.replace(' ', '_')}"
        milestone_folder.mkdir(parents=True, exist_ok=True)
        
        # Copy all workbook contents to milestone (excluding .milestones folder)
        for item in workbook_path.iterdir():
            if item.name == '.milestones':
                continue
            
            if item.is_file():
                shutil.copy2(item, milestone_folder / item.name)
            elif item.is_dir():
                shutil.copytree(item, milestone_folder / item.name, dirs_exist_ok=True)
        
        # Create milestone metadata
        meta = {
            'name': name,
            'description': description,
            'created': datetime.utcnow().isoformat() + 'Z',
        }
        
        with open(milestone_folder / "milestone.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        # Lock the snapshot so milestone files cannot be accidentally modified.
        _set_tree_readonly(milestone_folder)
        
        return True
    
    except Exception as e:
        print(f"Error creating milestone: {e}")
        return False


def delete_milestone(milestone: Milestone) -> bool:
    """Delete a milestone."""
    try:
        if milestone.milestone_path and milestone.milestone_path.exists():
            # Remove read-only flags so shutil.rmtree can delete the files.
            _set_tree_writable(milestone.milestone_path)
            shutil.rmtree(milestone.milestone_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting milestone: {e}")
        import traceback
        traceback.print_exc()
    return False


def revert_to_milestone(workbook_path: Path, milestone: Milestone) -> bool:
    """
    Revert a workbook to a previous milestone.
    
    This replaces all current workbook contents with the milestone contents.
    
    Args:
        workbook_path: Path to the workbook directory
        milestone: The milestone to revert to
    
    Returns:
        True if successful, False otherwise
    """
    if not workbook_path.exists() or not milestone.milestone_path.exists():
        return False
    
    try:
        # Remove all current contents except .milestones folder
        for item in list(workbook_path.iterdir()):
            if item.name == '.milestones':
                continue
            
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        
        # Copy milestone contents back (independent copies, milestone stays untouched)
        for item in milestone.milestone_path.iterdir():
            if item.name == 'milestone.json':
                continue
            
            dest = workbook_path / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
        
        # Ensure the restored workbook files are writable (milestone copies
        # inherit the read-only flag, but the live workbook must be editable).
        for child in workbook_path.iterdir():
            if child.name == '.milestones':
                continue
            if child.is_file():
                try:
                    child.chmod(child.stat().st_mode | stat.S_IWUSR)
                except Exception:
                    pass
            elif child.is_dir():
                _set_tree_writable(child)
        
        return True
    
    except Exception as e:
        print(f"Error reverting to milestone: {e}")
        return False


def copy_milestone_to_new_workbook(milestone: Milestone, new_workbook_path: Path) -> bool:
    """
    Copy a milestone to a new editable workbook.
    
    Args:
        milestone: The milestone to copy
        new_workbook_path: Path for the new workbook
    
    Returns:
        True if successful, False otherwise
    """
    if not milestone.milestone_path.exists():
        return False
    
    try:
        # Create the new workbook directory
        new_workbook_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all milestone contents
        for item in milestone.milestone_path.iterdir():
            if item.name == 'milestone.json':
                continue
            
            if item.is_file():
                shutil.copy2(item, new_workbook_path / item.name)
            elif item.is_dir():
                shutil.copytree(item, new_workbook_path / item.name, dirs_exist_ok=True)
        
        # New workbook must be editable (milestone copies inherit read-only).
        _set_tree_writable(new_workbook_path)
        
        return True
    
    except Exception as e:
        print(f"Error copying milestone: {e}")
        return False


def compare_workbooks(workbook_path: Path, milestone: Milestone) -> Dict:
    """
    Compare current workbook with a milestone.
    
    Returns a dict with detailed file changes including CSV row-level details.
    
    Args:
        workbook_path: Path to the current workbook
        milestone: The milestone to compare against
    
    Returns:
        Dictionary with change information
    """
    changes = {
        'modified': [],
        'added': [],
        'removed': [],
        'csv_details': {}  # Per-file CSV changes
    }
    
    if not workbook_path.exists() or not milestone.milestone_path.exists():
        return changes
    
    try:
        # Get all files from both workbook and milestone
        def get_files(path: Path, is_milestone: bool = False) -> Dict[str, Path]:
            """Get a dict of relative paths to files."""
            files = {}
            for item in path.rglob('*'):
                # Skip milestone.json metadata file
                if item.name == 'milestone.json':
                    continue
                
                # For regular workbook scanning, skip .milestones folders
                # For milestone scanning, include everything
                if not is_milestone and '.milestones' in item.parts:
                    continue
                
                if item.is_file():
                    rel_path = item.relative_to(path)
                    files[str(rel_path)] = item
            return files
        
        current_files = get_files(workbook_path, is_milestone=False)
        milestone_files = get_files(milestone.milestone_path, is_milestone=True)
        
        # Check for modifications and additions
        for rel_path, current_file in current_files.items():
            if rel_path in milestone_files:
                # File exists in both - check if different
                milestone_file = milestone_files[rel_path]
                try:
                    if current_file.read_bytes() != milestone_file.read_bytes():
                        changes['modified'].append(rel_path)
                        
                        # If it's a CSV, get detailed changes
                        if current_file.suffix.lower() == '.csv':
                            csv_changes = get_csv_detailed_changes(current_file, milestone_file, current_file.name)
                            if csv_changes:
                                changes['csv_details'][rel_path] = csv_changes
                except Exception:
                    changes['modified'].append(rel_path)
            else:
                # File only in current workbook
                changes['added'].append(rel_path)
                
                # If it's a CSV, get its contents as "added" data
                if current_file.suffix.lower() == '.csv':
                    csv_data = get_csv_file_as_added(current_file, current_file.name)
                    if csv_data:
                        changes['csv_details'][rel_path] = csv_data
        
        # Check for removals
        for rel_path in milestone_files:
            if rel_path not in current_files:
                changes['removed'].append(rel_path)
                
                # If it's a CSV, get its contents as "removed" data
                milestone_file = milestone_files[rel_path]
                if milestone_file.suffix.lower() == '.csv':
                    csv_data = get_csv_file_as_removed(milestone_file, milestone_file.name)
                    if csv_data:
                        changes['csv_details'][rel_path] = csv_data
    
    except Exception as e:
        print(f"Error comparing workbooks: {e}")
    
    return changes


def get_identifier_column(file_name: str, headers: List[str]) -> Optional[int]:
    """
    Determine which column to use as the row identifier based on file type.
    
    Returns column index or None if no suitable identifier found.
    """
    file_lower = file_name.lower()
    
    # For Schedule.csv - use Opening column
    if 'schedule' in file_lower:
        for idx, header in enumerate(headers):
            if header.lower() in ['opening', 'opening #', 'opening number', 'opng']:
                return idx
    
    # For door files - use Door Type or Description
    elif 'door' in file_lower:
        for idx, header in enumerate(headers):
            if header.lower() in ['door type', 'type', 'description', 'door description']:
                return idx
    
    # For frame files - use Frame Type or Description
    elif 'frame' in file_lower:
        for idx, header in enumerate(headers):
            if header.lower() in ['frame type', 'type', 'description', 'frame description']:
                return idx
    
    # For hardware files - use Description or Group
    elif 'hardware' in file_lower:
        for idx, header in enumerate(headers):
            if header.lower() in ['description', 'hardware description', 'group', 'hardware group', 'part description']:
                return idx
    
    # Default: try to find any Description or Type column
    for idx, header in enumerate(headers):
        if header.lower() in ['description', 'type', 'name']:
            return idx
    
    return None


def is_row_empty(row: list) -> bool:
    """Check if a row contains only empty/whitespace values."""
    if not row:
        return True
    return all(not str(cell).strip() for cell in row)


def normalize_value_for_comparison(value: str) -> str:
    """
    Normalize a CSV cell value for comparison.
    Handles numeric values with different decimal representations.
    """
    if not value or not isinstance(value, str):
        return str(value).strip()
    
    value = value.strip()
    
    # Try to parse as number and normalize
    try:
        # Remove common formatting
        clean_val = value.replace('$', '').replace(',', '').strip()
        
        # Try to parse as float
        num_val = float(clean_val)
        
        # Check if it's effectively an integer
        if num_val == int(num_val):
            return str(int(num_val))
        else:
            # Normalize to remove trailing zeros: 1.50 -> 1.5
            normalized = f"{num_val:.10f}".rstrip('0').rstrip('.')
            return normalized
    except (ValueError, AttributeError):
        # Not a number, return as-is (stripped)
        return value


def get_csv_detailed_changes(current_csv: Path, milestone_csv: Path, file_name: str = "") -> Dict:
    """
    Compare two CSV files and return detailed row and cell changes.
    
    Returns:
        Dict with detailed change information
    """
    import csv
    
    result = {
        'modified_rows': [],  # List of dicts with row index and changed fields
        'added_rows': [],     # List of row indices or identifiers
        'removed_rows': [],   # List of row indices or identifiers
        'headers': [],
        'file_name': file_name
    }
    
    try:
        # Read both CSVs
        def read_csv(path: Path) -> List[List[str]]:
            if not path.exists():
                return []
            try:
                with open(path, 'r', newline='', encoding='utf-8-sig') as f:
                    return list(csv.reader(f))
            except Exception:
                return []
        
        current_rows = read_csv(current_csv)
        milestone_rows = read_csv(milestone_csv)
        
        if not current_rows and not milestone_rows:
            return result
        
        # Extract headers
        headers = current_rows[0] if current_rows else (milestone_rows[0] if milestone_rows else [])
        result['headers'] = headers
        
        # Determine identifier column
        identifier_col = get_identifier_column(file_name or current_csv.name, headers)
        
        # Skip header row for comparison
        current_data = current_rows[1:] if len(current_rows) > 1 else []
        milestone_data = milestone_rows[1:] if len(milestone_rows) > 1 else []
        
        # Filter out empty rows from both datasets
        current_data = [row for row in current_data if not is_row_empty(row)]
        milestone_data = [row for row in milestone_data if not is_row_empty(row)]
        
        # Check for modifications
        max_len = max(len(current_data), len(milestone_data))
        for idx in range(max_len):
            if idx < len(current_data) and idx < len(milestone_data):
                current_row = current_data[idx]
                milestone_row = milestone_data[idx]
                
                # Normalize both rows for comparison
                normalized_current = [normalize_value_for_comparison(val) for val in current_row]
                normalized_milestone = [normalize_value_for_comparison(val) for val in milestone_row]
                
                if normalized_current != normalized_milestone:
                    # Find which fields changed
                    changed_fields = []
                    max_cols = max(len(current_row), len(milestone_row))
                    for col_idx in range(max_cols):
                        current_val = current_row[col_idx] if col_idx < len(current_row) else ''
                        milestone_val = milestone_row[col_idx] if col_idx < len(milestone_row) else ''
                        
                        # Compare normalized values
                        if normalize_value_for_comparison(current_val) != normalize_value_for_comparison(milestone_val):
                            field_name = headers[col_idx] if col_idx < len(headers) else f"Column {col_idx}"
                            changed_fields.append({
                                'field': field_name,
                                'old_value': milestone_val,
                                'new_value': current_val
                            })
                    
                    if changed_fields:
                        # Get row identifier if available
                        row_id = None
                        if identifier_col is not None and identifier_col < len(current_row):
                            row_id = current_row[identifier_col].strip()
                        
                        result['modified_rows'].append({
                            'row_index': idx + 2,  # +2 for header and 1-based indexing
                            'row_identifier': row_id,
                            'changes': changed_fields
                        })
            elif idx < len(current_data):
                # Row exists in current but not milestone (added)
                # Skip if row is empty
                if not is_row_empty(current_data[idx]):
                    row_id = None
                    if identifier_col is not None and identifier_col < len(current_data[idx]):
                        row_id = current_data[idx][identifier_col].strip()
                    result['added_rows'].append({'index': idx + 2, 'identifier': row_id})
            else:
                # Row exists in milestone but not current (removed)
                # Skip if row is empty
                if not is_row_empty(milestone_data[idx]):
                    row_id = None
                    if identifier_col is not None and identifier_col < len(milestone_data[idx]):
                        row_id = milestone_data[idx][identifier_col].strip()
                    result['removed_rows'].append({'index': idx + 2, 'identifier': row_id})
    
    except Exception as e:
        print(f"Error comparing CSVs: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def get_csv_file_as_added(csv_path: Path, file_name: str = "") -> Dict:
    """Read a CSV file and return all rows as 'added' data."""
    import csv
    
    result = {
        'modified_rows': [],
        'added_rows': [],
        'removed_rows': [],
        'headers': [],
        'file_name': file_name
    }
    
    try:
        if not csv_path.exists():
            return result
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            rows = list(csv.reader(f))
        
        if not rows:
            return result
        
        headers = rows[0] if rows else []
        result['headers'] = headers
        
        # Determine identifier column
        identifier_col = get_identifier_column(file_name or csv_path.name, headers)
        
        # All data rows are "added"
        data = rows[1:] if len(rows) > 1 else []
        for idx, row in enumerate(data):
            row_id = None
            if identifier_col is not None and identifier_col < len(row):
                row_id = row[identifier_col].strip()
            result['added_rows'].append({'index': idx + 2, 'identifier': row_id})
    
    except Exception as e:
        print(f"Error reading CSV as added: {e}")
    
    return result


def get_csv_file_as_removed(csv_path: Path, file_name: str = "") -> Dict:
    """Read a CSV file and return all rows as 'removed' data."""
    import csv
    
    result = {
        'modified_rows': [],
        'added_rows': [],
        'removed_rows': [],
        'headers': [],
        'file_name': file_name
    }
    
    try:
        if not csv_path.exists():
            return result
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            rows = list(csv.reader(f))
        
        if not rows:
            return result
        
        headers = rows[0] if rows else []
        result['headers'] = headers
        
        # Determine identifier column
        identifier_col = get_identifier_column(file_name or csv_path.name, headers)
        
        # All data rows are "removed"
        data = rows[1:] if len(rows) > 1 else []
        for idx, row in enumerate(data):
            row_id = None
            if identifier_col is not None and identifier_col < len(row):
                row_id = row[identifier_col].strip()
            result['removed_rows'].append({'index': idx + 2, 'identifier': row_id})
    
    except Exception as e:
        print(f"Error reading CSV as removed: {e}")
    
    return result

