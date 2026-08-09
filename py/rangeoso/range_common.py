"""
range_common.py — Shared range-stage logic for range_oso3 / range_oso4 / range_oso5.

The RANGE STAGE (predict the next draw's min/max span from its five main
numbers, mega excluded) is identical across all range_osoN algorithms —
only the column-pick stage (oso_orderN) differs between them. This module
holds that shared logic so it isn't triplicated.

Range prediction uses a hierarchical order5 -> order4 -> order3 -> order2
pattern cascade — the same fallback mechanism oso_next uses for its main
columns — applied independently to the min-sequence (predicted min) and the
max-sequence (predicted max). No averaging or other arithmetic is used
anywhere: these are lottery draw numbers, not a time series to smooth. If
none of order5..order2 has a historical match, the final fallback is the
single historically most-frequent value (the mode) for that sequence.
"""

import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import pattern_fallback


def _order_sequence_predict(seq: List[int], order: int) -> Optional[int]:
    """
    N-row look-back pattern match on a single-value sequence.

    Reuses the exact same window/best-follower logic as
    utils.pattern_fallback(), applied to a synthetic single-column series
    (the per-draw min or max value) instead of a CSV column.
    """
    if len(seq) < order:
        return None
    pseudo_rows = [[0, v] for v in seq]
    return pattern_fallback(pseudo_rows, order=order, col_range=[1]).get(1)


def _predict_sequence_value(
    seq: List[int],
    label: str = "",
    verbose: bool = False,
) -> Tuple[Optional[int], str]:
    """
    Predict the next value of a single-value sequence (the per-draw min or
    max) using pattern-matching only — no arithmetic, no averaging.

    Fallback chain (all lookup/frequency based, nothing computed) — the
    same hierarchical cascade oso_next uses for main columns:
      1. order5 pattern match — exact 5-row window seen before?
      2. order4 pattern match — exact 4-row window seen before?
      3. order3 pattern match — exact 3-row window seen before?
      4. order2 pattern match — exact 2-row window seen before?
      5. mode — the single most-frequent value in the sequence's history.
    """
    for order in (5, 4, 3, 2):
        val = _order_sequence_predict(seq, order)
        if verbose:
            tag = f"MATCH -> {val}" if val is not None else "no historical match"
            print(f"  order{order} attempt on {label}-sequence: {tag}")
        if val is not None:
            return val, f"order{order} pattern match ({order}-row window seen before)"

    if seq:
        mode_val, mode_count = Counter(seq).most_common(1)[0]
        if verbose:
            print(f"  order5..order2 all missed on {label}-sequence -> falling back to mode")
        return mode_val, f"fallback: most frequent historical value (mode, {mode_count}/{len(seq)} draws)"

    return None, "no data"


def predict_range(
    rows: List[List[int]],
    verbose: bool = False,
) -> Tuple[int, int, str, str]:
    """
    Predict (range_min, range_max) for the next draw's five main numbers.

    Purely pattern/frequency based — no averaging or other arithmetic.
    Returns (range_min, range_max, source_min, source_max).
    """
    mins = [min(r[1:6]) for r in rows]
    maxs = [max(r[1:6]) for r in rows]

    if verbose:
        print("  -- min-sequence cascade --")
    pred_min, source_min = _predict_sequence_value(mins, label="min", verbose=verbose)
    if verbose:
        print("  -- max-sequence cascade --")
    pred_max, source_max = _predict_sequence_value(maxs, label="max", verbose=verbose)

    # Safety: clip to valid domain and guarantee min <= max
    pred_min = max(1, min(47, pred_min)) if pred_min is not None else 1
    pred_max = max(1, min(47, pred_max)) if pred_max is not None else 47
    if pred_min > pred_max:
        pred_min, pred_max = pred_max, pred_min
        source_min += " (swapped: min > max)"
        source_max += " (swapped: min > max)"

    return pred_min, pred_max, source_min, source_max
