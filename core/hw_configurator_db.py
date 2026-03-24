"""Hardware Configurator database layer using SQLite."""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


DB_NAME = "hw_configurator.db"


def get_db_path() -> Path:
    """Return the path to the configurator database."""
    return Path(__file__).resolve().parent.parent / "data" / DB_NAME


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS hw_families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                assembly_pattern TEXT NOT NULL DEFAULT '',
                description_template TEXT NOT NULL DEFAULT '',
                UNIQUE(manufacturer, name)
            );

            CREATE TABLE IF NOT EXISTS hw_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                slot_order INTEGER NOT NULL DEFAULT 0,
                slot_name TEXT NOT NULL,
                slot_label TEXT NOT NULL,
                required INTEGER NOT NULL DEFAULT 1,
                UNIQUE(family_id, slot_name)
            );

            CREATE TABLE IF NOT EXISTS hw_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                slot_name TEXT NOT NULL,
                value TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0,
                UNIQUE(family_id, slot_name, value)
            );

            CREATE TABLE IF NOT EXISTS hw_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                rule_type TEXT NOT NULL CHECK(rule_type IN ('require','conflict','restrict')),
                trigger_slot TEXT NOT NULL,
                trigger_value TEXT NOT NULL,
                target_slot TEXT NOT NULL,
                target_value TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_slots_family
                ON hw_slots(family_id);
            CREATE INDEX IF NOT EXISTS idx_options_family_slot
                ON hw_options(family_id, slot_name);
            CREATE INDEX IF NOT EXISTS idx_rules_family
                ON hw_rules(family_id);
            CREATE INDEX IF NOT EXISTS idx_rules_trigger
                ON hw_rules(family_id, trigger_slot, trigger_value);

            CREATE TABLE IF NOT EXISTS hw_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                label TEXT NOT NULL,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                selections_json TEXT NOT NULL DEFAULT '{}',
                part_number TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                manufacturer TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '',
                finish TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_favorites_user
                ON hw_favorites(username);

            CREATE TABLE IF NOT EXISTS hw_pricing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                slot_name TEXT NOT NULL,
                slot_value TEXT NOT NULL,
                price_type TEXT NOT NULL DEFAULT 'base'
                    CHECK(price_type IN ('base','adder')),
                amount REAL NOT NULL DEFAULT 0.0,
                UNIQUE(family_id, slot_name, slot_value)
            );
            CREATE INDEX IF NOT EXISTS idx_pricing_family
                ON hw_pricing(family_id, slot_name);
        """)
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Read helpers
# ------------------------------------------------------------------

def get_manufacturers() -> List[str]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT manufacturer FROM hw_families ORDER BY manufacturer"
        ).fetchall()
        return [r["manufacturer"] for r in rows]
    finally:
        conn.close()


def get_families(manufacturer: str) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, category, assembly_pattern, description_template "
            "FROM hw_families WHERE manufacturer = ? ORDER BY name",
            (manufacturer,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_family(family_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, manufacturer, name, category, assembly_pattern, "
            "description_template FROM hw_families WHERE id = ?",
            (family_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_slots(family_id: int) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, slot_name, slot_label, slot_order, required "
            "FROM hw_slots WHERE family_id = ? ORDER BY slot_order",
            (family_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_options(family_id: int, slot_name: str) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT value, display_name FROM hw_options "
            "WHERE family_id = ? AND slot_name = ? ORDER BY sort_order, display_name",
            (family_id, slot_name),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_valid_options(
    family_id: int, slot_name: str, selections: Dict[str, str]
) -> List[dict]:
    """Return valid options for *slot_name* given the current *selections*.

    Rule logic:
      - restrict : whitelist — only listed target values are allowed.
      - conflict : blacklist — listed target values are removed.
      - require  : force — only the required value(s) remain.
    """
    all_opts = get_all_options(family_id, slot_name)
    if not all_opts:
        return all_opts

    conn = get_connection()
    try:
        rules = conn.execute(
            "SELECT rule_type, trigger_slot, trigger_value, target_value "
            "FROM hw_rules WHERE family_id = ? AND target_slot = ?",
            (family_id, slot_name),
        ).fetchall()

        restricted_values: set = set()
        has_restrict = False
        conflicted_values: set = set()
        required_values: set = set()
        has_require = False

        for rule in rules:
            trigger_slot = rule["trigger_slot"]
            trigger_value = rule["trigger_value"]

            if trigger_slot not in selections:
                continue
            if selections[trigger_slot] != trigger_value:
                continue

            rt = rule["rule_type"]
            tv = rule["target_value"]

            if rt == "restrict":
                has_restrict = True
                restricted_values.add(tv)
            elif rt == "conflict":
                conflicted_values.add(tv)
            elif rt == "require":
                has_require = True
                required_values.add(tv)

        valid = all_opts

        if has_require:
            valid = [o for o in valid if o["value"] in required_values]
        elif has_restrict:
            valid = [o for o in valid if o["value"] in restricted_values]

        if conflicted_values:
            valid = [o for o in valid if o["value"] not in conflicted_values]

        # ── Pricing-aware filtering for compound keys ──────────────
        # When pricing uses compound keys (e.g. "model:size:finish"),
        # filter this slot's options to only those that appear in at
        # least one pricing row compatible with the current selections.
        pricing_rows = conn.execute(
            "SELECT slot_name, slot_value FROM hw_pricing WHERE family_id = ?",
            (family_id,),
        ).fetchall()

        compound_rows = [r for r in pricing_rows if ":" in r["slot_name"]]
        if compound_rows:
            # Find compound keys that include this slot
            relevant = [
                r for r in compound_rows
                if slot_name in r["slot_name"].split(":")
            ]
            if relevant:
                compatible_values: set = set()
                for r in relevant:
                    parts = r["slot_name"].split(":")
                    vals = r["slot_value"].split(":")
                    if len(parts) != len(vals):
                        continue
                    kv = dict(zip(parts, vals))

                    # Check that all OTHER selected slots match
                    match = True
                    for p, v in kv.items():
                        if p == slot_name:
                            continue
                        sel = selections.get(p)
                        if sel is not None and sel != v:
                            match = False
                            break

                    if match:
                        compatible_values.add(kv[slot_name])

                # Also include values that have simple (non-compound)
                # pricing — compound rows are adders, not the full set.
                simple_values = {
                    r["slot_value"]
                    for r in pricing_rows
                    if r["slot_name"] == slot_name
                }
                compatible_values |= simple_values

                if compatible_values:
                    valid = [o for o in valid if o["value"] in compatible_values]

        return valid
    finally:
        conn.close()


# ------------------------------------------------------------------
# Assembly helpers
# ------------------------------------------------------------------

def assemble_part_number(family_id: int, selections: Dict[str, str]) -> str:
    family = get_family(family_id)
    if not family:
        return ""
    pattern = family["assembly_pattern"]
    if not pattern:
        slots = get_slots(family_id)
        parts = [selections.get(s["slot_name"], "") for s in slots]
        return "".join(p for p in parts if p)
    # Track which keys have placeholders in the pattern
    import re as _re
    in_pattern = set(_re.findall(r"\{(\w+)\}", pattern))
    result = pattern
    for key, val in selections.items():
        result = result.replace("{" + key + "}", val)
    # Remove unfilled placeholders and collapse extra whitespace
    result = _re.sub(r"\{[^}]+\}", "", result)
    result = " ".join(result.split())
    # Append selected optional values not covered by the pattern
    extras = []
    for key, val in selections.items():
        if key not in in_pattern and val:
            extras.append(val)
    if extras:
        result = result + " " + " ".join(extras)
    return result


def assemble_description(family_id: int, selections: Dict[str, str]) -> str:
    family = get_family(family_id)
    if not family:
        return ""
    template = family["description_template"]
    if not template:
        return assemble_part_number(family_id, selections)
    # Track which keys have placeholders in the template
    import re as _re
    in_template = set(_re.findall(r"\{(\w+)\}", template))
    result = template
    for key, val in selections.items():
        result = result.replace("{" + key + "}", val)
    result = _re.sub(r"\{[^}]+\}", "", result)
    result = " ".join(result.split())
    # Append selected optional values not covered by the template
    extras = []
    for key, val in selections.items():
        if key not in in_template and val:
            extras.append(val)
    if extras:
        result = result + " " + " ".join(extras)
    return result


# ------------------------------------------------------------------
# Favorites helpers
# ------------------------------------------------------------------

def get_favorites(username: str) -> List[dict]:
    """Return all favorites for a given user, sorted by label."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, label, family_id, selections_json, part_number, "
            "description, manufacturer, category, finish "
            "FROM hw_favorites WHERE username = ? ORDER BY label",
            (username,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def save_favorite(username: str, label: str, family_id: int,
                  selections: Dict[str, str], part_number: str,
                  description: str, manufacturer: str,
                  category: str, finish: str) -> int:
    """Save a new favorite and return its id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO hw_favorites "
            "(username, label, family_id, selections_json, part_number, "
            " description, manufacturer, category, finish) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (username, label, family_id, json.dumps(selections),
             part_number, description, manufacturer, category, finish),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_favorite(fav_id: int):
    """Delete a favorite by id."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM hw_favorites WHERE id = ?", (fav_id,))
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Pricing helpers
# ------------------------------------------------------------------

def get_list_price(family_id: int, selections: Dict[str, str]) -> Optional[float]:
    """Compute the list price for a configuration.

    The total is the sum of a single 'base' row (matched by the first
    selected slot that has a base entry) plus all 'adder' rows that
    match the current selections.  Returns *None* when no base price
    is found (i.e. no pricing data exists for this family).

    Compound keys are supported: a slot_name like ``"rose:finish"`` with
    slot_value ``"N:605"`` matches only when *both* selections match.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT slot_name, slot_value, price_type, amount "
            "FROM hw_pricing WHERE family_id = ?",
            (family_id,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return None

    base = None
    adder_total = 0.0

    for r in rows:
        sn = r["slot_name"]
        sv = r["slot_value"]
        if ":" in sn:
            # Compound key — all sub-slots must match
            parts = sn.split(":")
            vals = sv.split(":")
            if len(parts) != len(vals):
                continue
            if not all(selections.get(p) == v for p, v in zip(parts, vals)):
                continue
        else:
            sel_val = selections.get(sn)
            if sel_val is None or sel_val != sv:
                continue

        if r["price_type"] == "base":
            base = r["amount"]
        else:
            adder_total += r["amount"]

    if base is None:
        return None
    return base + adder_total


# ------------------------------------------------------------------
# Part-string reverse matching
# ------------------------------------------------------------------

def _build_option_index(conn, family_id: int) -> Dict[str, List[str]]:
    """Return {slot_name: [value, ...]} for all options in a family."""
    rows = conn.execute(
        "SELECT slot_name, value FROM hw_options WHERE family_id = ? "
        "ORDER BY slot_name, sort_order",
        (family_id,),
    ).fetchall()
    index: Dict[str, List[str]] = {}
    for r in rows:
        index.setdefault(r["slot_name"], []).append(r["value"])
    return index


def _tokenize_pattern(pattern: str) -> list:
    """Split assembly_pattern into a list of (type, value) tokens.

    Types: 'slot' for {name} placeholders, 'lit' for literal text between them.
    Adjacent slots with no separator are grouped as ('adjacent', [name1, name2, ...]).
    """
    tokens = []
    pos = 0
    while pos < len(pattern):
        brace = pattern.find("{", pos)
        if brace == -1:
            tail = pattern[pos:]
            if tail:
                tokens.append(("lit", tail))
            break
        if brace > pos:
            tokens.append(("lit", pattern[pos:brace]))
        end = pattern.index("}", brace)
        slot_name = pattern[brace + 1 : end]
        tokens.append(("slot", slot_name))
        pos = end + 1

    # Merge consecutive 'slot' tokens into 'adjacent' groups
    merged: list = []
    for tok in tokens:
        if tok[0] == "slot":
            if merged and merged[-1][0] == "adjacent":
                merged[-1] = ("adjacent", merged[-1][1] + [tok[1]])
            elif merged and merged[-1][0] == "slot":
                merged[-1] = ("adjacent", [merged[-1][1], tok[1]])
            else:
                merged.append(tok)
        else:
            merged.append(tok)
    return merged


def _try_match_family(
    text: str,
    pattern: str,
    option_index: Dict[str, List[str]],
    slot_names: List[str],
    required_slots: set,
    manufacturer: str = "",
) -> tuple[Dict[str, str], float]:
    """Attempt to match *text* against a single family.

    Returns (selections, score).  Score is 0.0 if nothing matched.
    The algorithm:
      1. Check if literal prefixes from the assembly pattern appear in the text.
      2. For each slot, check which of its known option values appear in the text.
      3. For adjacent slots (no separator), try all value combinations.
      4. Score = (matched_required * 3 + matched_optional) / (total_required * 3 + total_optional)
    """
    text_upper = text.upper().strip()

    # Strip manufacturer name from the front if present (users often paste
    # "Schlage L9080P 06A 626" but the pattern has no manufacturer prefix).
    if manufacturer:
        mfr_upper = manufacturer.upper()
        if text_upper.startswith(mfr_upper):
            text_upper = text_upper[len(mfr_upper):].strip()

    selections: Dict[str, str] = {}

    tokens = _tokenize_pattern(pattern)

    # Quick-reject: check that literal fragments of the pattern appear in the text
    for tok_type, tok_val in tokens:
        if tok_type == "lit":
            lit_upper = tok_val.strip().upper()
            if lit_upper and lit_upper not in text_upper:
                # Allow single-char separators (like "-") to be missing
                if len(lit_upper) > 1:
                    return {}, 0.0

    # Build a "remaining" string that we consume as we match tokens
    remaining = text_upper

    # Strip known literal prefixes from the text for cleaner matching
    for tok_type, tok_val in tokens:
        if tok_type == "lit":
            lit_upper = tok_val.strip().upper()
            if lit_upper:
                remaining = remaining.replace(lit_upper, " ", 1)

    # Split remaining into tokens for matching
    parts = remaining.split()

    # --- Strategy 1: positional token matching using pattern structure ---
    # Walk through the pattern tokens and try to greedily consume from `parts`
    part_idx = 0
    for tok in tokens:
        if tok[0] == "lit":
            # Literals were already stripped; skip
            continue
        elif tok[0] == "slot":
            slot_name = tok[1]
            opts = option_index.get(slot_name, [])
            opts_upper = {v.upper(): v for v in opts}
            matched = False
            # Try at current position, then skip up to 2 unknown tokens
            for skip in range(min(3, len(parts) - part_idx + 1)):
                try_idx = part_idx + skip
                if try_idx >= len(parts):
                    break
                # Try multi-word matches first (e.g. "1-1/8")
                for lookahead in range(min(3, len(parts) - try_idx), 0, -1):
                    candidate = " ".join(parts[try_idx : try_idx + lookahead])
                    if candidate in opts_upper:
                        selections[slot_name] = opts_upper[candidate]
                        part_idx = try_idx + lookahead
                        matched = True
                        break
                if matched:
                    break
                # Try substring match within current part
                current = parts[try_idx]
                for ov_upper, ov_orig in sorted(
                    opts_upper.items(), key=lambda x: len(x[0]), reverse=True
                ):
                    if current == ov_upper:
                        selections[slot_name] = ov_orig
                        part_idx = try_idx + 1
                        matched = True
                        break
                    if len(ov_upper) >= 2 and (current.startswith(ov_upper) or current.endswith(ov_upper)):
                        selections[slot_name] = ov_orig
                        leftover = current.replace(ov_upper, "", 1).strip()
                        if leftover:
                            parts[try_idx] = leftover
                            part_idx = try_idx
                        else:
                            part_idx = try_idx + 1
                        matched = True
                        break
                if matched:
                    break
        elif tok[0] == "adjacent":
            adj_slots = tok[1]
            # For adjacent slots, try at current position and skip up to 2
            for skip in range(min(3, len(parts) - part_idx + 1)):
                try_idx = part_idx + skip
                if try_idx >= len(parts):
                    break
                _match_adjacent(adj_slots, parts, try_idx, option_index, selections)
                if any(sn in selections for sn in adj_slots):
                    part_idx = try_idx + 1
                    break

    # --- Strategy 2: fallback scan — find option values anywhere in text ---
    for slot_name in slot_names:
        if slot_name in selections:
            continue
        opts = option_index.get(slot_name, [])
        # Sort longest first to prefer more specific matches
        for opt_val in sorted(opts, key=len, reverse=True):
            opt_upper = opt_val.upper()
            # Check if this value appears as a whole word in the original text
            if re.search(r"(?:^|[\s\-/])(" + re.escape(opt_upper) + r")(?:[\s\-/]|$)", text_upper):
                selections[slot_name] = opt_val
                break
            # Also try matching as a prefix/suffix within any token
            # (handles concatenated values like "L9080P" containing "L9080")
            if len(opt_upper) >= 3:
                for part in text_upper.split():
                    if len(part) > len(opt_upper) and (part.startswith(opt_upper) or part.endswith(opt_upper)):
                        selections[slot_name] = opt_val
                        break
                if slot_name in selections:
                    break

    # --- Score ---
    if not selections:
        return {}, 0.0

    total_required = len(required_slots) or 1
    total_optional = max(len(slot_names) - len(required_slots), 1)
    matched_req = sum(1 for s in required_slots if s in selections)
    matched_opt = sum(1 for s in selections if s not in required_slots)

    score = (matched_req * 3.0 + matched_opt) / (total_required * 3.0 + total_optional)
    return selections, score


def _match_adjacent(
    slot_names: List[str],
    parts: list,
    start_idx: int,
    option_index: Dict[str, List[str]],
    selections: Dict[str, str],
) -> None:
    """Try to match adjacent slots that have no separator in the pattern.

    For example, pattern ``{lever}{escutcheon}`` with text token ``06A``
    should split into lever=06, escutcheon=A.
    """
    if start_idx >= len(parts):
        return

    # Combine the parts that might belong to these adjacent slots
    combined = parts[start_idx] if start_idx < len(parts) else ""
    combined_upper = combined.upper()

    if len(slot_names) == 2:
        s1, s2 = slot_names
        opts1 = {v.upper(): v for v in option_index.get(s1, [])}
        opts2 = {v.upper(): v for v in option_index.get(s2, [])}

        # Try every split point
        for i in range(1, len(combined_upper)):
            head = combined_upper[:i]
            tail = combined_upper[i:]
            if head in opts1 and tail in opts2:
                selections[s1] = opts1[head]
                selections[s2] = opts2[tail]
                return

    # General case: recursive matching for 3+ adjacent slots
    _match_adjacent_recursive(slot_names, 0, combined_upper, option_index, selections)


def _match_adjacent_recursive(
    slot_names: List[str],
    idx: int,
    remaining: str,
    option_index: Dict[str, List[str]],
    selections: Dict[str, str],
) -> bool:
    if idx == len(slot_names):
        return remaining == ""
    sn = slot_names[idx]
    opts = {v.upper(): v for v in option_index.get(sn, [])}
    for length in range(len(remaining), 0, -1):
        head = remaining[:length]
        if head in opts:
            selections[sn] = opts[head]
            if _match_adjacent_recursive(slot_names, idx + 1, remaining[length:], option_index, selections):
                return True
            del selections[sn]
    return False


def match_part_string(text: str) -> List[dict]:
    """Attempt to match a free-text part string to configurator families.

    Returns a list of candidate matches sorted by score (best first).
    Each entry::

        {
            "family_id": int,
            "manufacturer": str,
            "name": str,
            "selections": dict[str, str],
            "score": float,   # 0.0 – 1.0
        }
    """
    if not text or not text.strip():
        return []

    conn = get_connection()
    try:
        families = conn.execute(
            "SELECT id, manufacturer, name, assembly_pattern "
            "FROM hw_families"
        ).fetchall()

        candidates: List[dict] = []

        for fam in families:
            family_id = fam["id"]
            pattern = fam["assembly_pattern"]
            if not pattern:
                continue

            option_index = _build_option_index(conn, family_id)

            slot_rows = conn.execute(
                "SELECT slot_name, required FROM hw_slots "
                "WHERE family_id = ? ORDER BY slot_order",
                (family_id,),
            ).fetchall()
            slot_names = [r["slot_name"] for r in slot_rows]
            required_slots = {r["slot_name"] for r in slot_rows if r["required"]}

            selections, score = _try_match_family(
                text, pattern, option_index, slot_names, required_slots,
                manufacturer=fam["manufacturer"],
            )
            if score > 0.0 and selections:
                candidates.append({
                    "family_id": family_id,
                    "manufacturer": fam["manufacturer"],
                    "name": fam["name"],
                    "selections": selections,
                    "score": score,
                })

        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates
    finally:
        conn.close()
