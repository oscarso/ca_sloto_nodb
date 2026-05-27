"""
utils.py — shared utilities for all prediction modules.

Exports:
    load_csv(csv_path)            → (rows, header, delimiter)
    load_rows(csv_path)           → rows
    pattern_fallback(rows, order) → {col: value | None}
    resolve_duplicates(...)       → updated prediction dict
    write_temp_csv(...)           → Path to temp file
"""

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def load_csv(csv_path: Path) -> Tuple[List[List[int]], Optional[List[str]], str]:
    """
    Load a lottery results CSV file.

    Handles both comma- and semicolon-delimited files, and skips the optional
    header row (draw_num, ...).

    Returns:
        rows      – list of [draw_num, c1, c2, c3, c4, c5, mega]
        header    – the raw header row if present, else None
        delimiter – ',' or ';'
    """
    rows: List[List[int]] = []
    header: Optional[List[str]] = None

    with Path(csv_path).open("r", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if ";" in sample and "," not in sample else ","
        reader = csv.reader(f, delimiter=delimiter)
        for raw in reader:
            if not raw:
                continue
            if raw[0].strip().lower() == "draw_num":
                header = raw
                continue
            rows.append([int(x) for x in raw[:7]])

    return rows, header, delimiter


def load_rows(csv_path: Path) -> List[List[int]]:
    """Load CSV and return only the data rows (no header / delimiter)."""
    rows, _, _ = load_csv(csv_path)
    return rows


def write_temp_csv(
    csv_path: Path,
    rows: List[List[int]],
    header: Optional[List[str]],
    delimiter: str,
    suffix: str = "_temp",
) -> Path:
    """
    Write *rows* to a temporary file inside csv_path.parent/tmp/.

    The tmp/ directory is created if it doesn't exist.
    Returns the path to the newly created temp file.
    """
    tmp_dir = Path(csv_path).parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    temp_path = tmp_dir / f"{Path(csv_path).stem}{suffix}.csv"
    with temp_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        if header:
            writer.writerow(header)
        for row in rows:
            writer.writerow(row)
    return temp_path


# ---------------------------------------------------------------------------
# Pattern prediction
# ---------------------------------------------------------------------------

def pattern_fallback(
    rows: List[List[int]],
    order: int,
    col_range: Iterable[int] = None,
) -> Dict[int, Optional[int]]:
    """
    Generic N-row look-back pattern predictor.

    Scans all windows of `order` consecutive rows for each column in
    `col_range`, records what value followed each window, then predicts
    the most-common follower for the current (most-recent) window.

    This single function replaces the 8 hand-written *_fallback functions
    that previously existed in oso_next.py (order2_fallback … order5_fallback
    and order_m2_fallback … order_m5_fallback).

    Args:
        rows:      historical draw rows (each: [draw_num, c1, c2, c3, c4, c5, mega])
        order:     look-back window size (2, 3, 4, or 5)
        col_range: column indices to predict (default: range(1, 6) — main numbers)
                   Use [6] for the mega number only.

    Returns:
        {col_index: predicted_value}  — value is None if no pattern matched.
    """
    if col_range is None:
        col_range = range(1, 6)
    cols = list(col_range)

    if len(rows) < order:
        return {col: None for col in cols}

    # Count (window_key + next_value) tuples across all requested columns.
    # Patterns from different columns with identical value sequences are merged,
    # which is the same behaviour as the original per-column fallback functions.
    pattern_counts: Counter = Counter()
    for col in cols:
        for i in range(len(rows) - order):
            key = tuple(rows[i + j][col] for j in range(order))
            nxt = rows[i + order][col]
            pattern_counts[key + (nxt,)] += 1

    # For each window key, keep the most-frequently-following value.
    best: Dict[Tuple, int] = {}
    for entry, cnt in pattern_counts.items():
        key, nxt = entry[:-1], entry[-1]
        if key not in best or pattern_counts[key + (best[key],)] < cnt:
            best[key] = nxt

    # Apply to the tail of the data (the most recent `order` rows).
    tail = rows[-order:]
    return {
        col: best.get(tuple(tail[j][col] for j in range(order)))
        for col in cols
    }


# ---------------------------------------------------------------------------
# Duplicate resolution
# ---------------------------------------------------------------------------

def resolve_duplicates(
    prediction: Dict[int, int],
    col_ranked_candidates: Dict[int, List[int]],
    col_range: Iterable[int] = None,
    max_iterations: int = 20,
) -> Dict[int, int]:
    """
    Ensure no two columns in col_range share the same predicted value.

    When a duplicate is detected, the later column is replaced with its
    next-best candidate (from col_ranked_candidates) that isn't already used.

    The input dict is NOT mutated; a new dict is returned.
    """
    if col_range is None:
        col_range = range(1, 6)
    cols = list(col_range)

    pred = dict(prediction)

    for _ in range(max_iterations):
        seen: Dict[int, int] = {}
        dupes: List[int] = []
        for col in cols:
            val = pred[col]
            if val in seen:
                dupes.append(col)
            else:
                seen[val] = col

        if not dupes:
            break

        for col in dupes:
            old_val = pred[col]
            used = {pred[c] for c in cols if c != col}
            for candidate in col_ranked_candidates[col]:
                if candidate not in used and candidate != old_val:
                    print(f"Column {col}: {old_val} -> {candidate} (duplicate resolution)")
                    pred[col] = candidate
                    break

    return pred
