"""
range_oso_next.py — Range-Constrained OSO Predictor (consolidated)

Consolidates range_oso3_next / range_oso4_next / range_oso5_next into a
single algorithm, mirroring how oso_next.py consolidates oso_order2 through
oso_order5: instead of three separate top-level predictions (one per fixed
window size), one algorithm hierarchically tries each window size and uses
whichever one actually produces a signal — exactly the same
"order5 -> order4 -> order3 -> order2" priority oso_next uses for its main
columns.

Two-stage prediction:

  1. RANGE STAGE — identical to range_oso3/4/5 (see range_common.py):
     order5 -> order4 -> order3 -> order2 -> mode cascade on the min-sequence
     and max-sequence (mega excluded). No arithmetic anywhere — these are
     lottery draw numbers, not a time series to smooth.

  2. OSO STAGE — for each main column, hierarchical fallback:
     try the order5 pattern match first; if it exists AND falls inside the
     predicted range, use it. Otherwise try order4, then order3, then
     order2. If none of the four window sizes produces an in-range match,
     fall back to a merged ranked-candidate list — tail-match frequency
     summed across all four orders, then overall historical column
     frequency as a tie-break — restricted to in-range values.

  3. RANGE CONSTRAINT — the final pick for each column, and any
     duplicate-resolution substitute, must fall inside the predicted
     [range_min, range_max].

The mega number (column 6) is NOT range-constrained (the range definition
explicitly excludes it) — it uses the same order5 -> order4 -> order3 ->
order2 hierarchical fallback, then falls back to overall column-7
frequency.

The individual range_oso3_next / range_oso4_next / range_oso5_next scripts
still exist and still run standalone (same relationship oso_order2.py..
oso_order5.py have to oso_next.py) — they're just no longer each a separate
entry in predict_all.py now that this consolidated version covers all of
them at once.
"""

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, pattern_fallback, resolve_duplicates

sys.path.insert(0, str(Path(__file__).parent))
from range_common import predict_range

_MAIN_RANGE = range(1, 48)   # columns 1-5: 1-47
_MEGA_RANGE = range(1, 28)   # column 6 (mega): 1-27
_ORDERS = (5, 4, 3, 2)


# ---------------------------------------------------------------------------
# Hierarchical order5 -> order4 -> order3 -> order2 helpers
# ---------------------------------------------------------------------------

def _tail_frequencies(rows: List[List[int]], col: int, order: int) -> Dict[int, int]:
    """
    For a given column and window size, find every value that historically
    followed the CURRENT last-order-row window, with frequency counts.
    """
    if len(rows) < order + 1:
        return {}
    tail = tuple(rows[-order:][j][col] for j in range(order))
    freqs: Counter = Counter()
    for i in range(len(rows) - order):
        key = tuple(rows[i + j][col] for j in range(order))
        if key == tail:
            freqs[rows[i + order][col]] += 1
    return dict(freqs)


def _merged_ranked_candidates(
    rows: List[List[int]],
    col: int,
    value_domain: range,
) -> List[int]:
    """
    Full ranked candidate list over value_domain for a column, ordered by:
      1. tail-match frequency summed across order5, order4, order3, order2
      2. overall historical column frequency (desc)
      3. numeric value (asc) as final tie-break

    Covers the entire domain (not just historically-seen values) so a
    range-filtered slice always has enough candidates for duplicate
    resolution.
    """
    merged: Counter = Counter()
    for order in _ORDERS:
        for val, cnt in _tail_frequencies(rows, col, order).items():
            merged[val] += cnt
    overall_freq = Counter(row[col] for row in rows)

    return sorted(
        value_domain,
        key=lambda v: (-merged.get(v, 0), -overall_freq.get(v, 0), v),
    )


def _hierarchical_column_pick(
    rows: List[List[int]],
    col: int,
    range_min: int,
    range_max: int,
    verbose: bool = False,
) -> Tuple[Optional[int], Optional[str]]:
    """
    Try order5, then order4, order3, order2 pattern match for this column;
    use the first one that both matches historically AND falls inside the
    predicted range. Returns (value, source) or (None, None) if nothing
    in the cascade qualifies.
    """
    for order in _ORDERS:
        candidate = pattern_fallback(rows, order, col_range=[col]).get(col)
        if verbose:
            if candidate is None:
                print(f"    order{order}: no historical match")
            else:
                tag = "in range" if range_min <= candidate <= range_max else "OUT of range"
                print(f"    order{order}: {candidate} ({tag})")
        if candidate is not None and range_min <= candidate <= range_max:
            return candidate, f"order{order} pattern ({order}-row match), in range [{range_min}-{range_max}]"
    return None, None


def _hierarchical_mega_pick(
    rows: List[List[int]],
    verbose: bool = False,
) -> Tuple[Optional[int], str]:
    """Same order5 -> order4 -> order3 -> order2 cascade for the mega column, not range-constrained."""
    for order in _ORDERS:
        candidate = pattern_fallback(rows, order, col_range=[6]).get(6)
        if verbose:
            tag = str(candidate) if candidate is not None else "no historical match"
            print(f"    order{order}: {tag}")
        if candidate is not None:
            return candidate, f"order{order} pattern ({order}-row mega match)"

    mega_freq = Counter(row[6] for row in rows)
    if mega_freq:
        val, cnt = mega_freq.most_common(1)[0]
        return val, f"fallback: most frequent historical mega value ({cnt}/{len(rows)} draws)"
    return None, "no data"


# ---------------------------------------------------------------------------
# Main prediction function
# ---------------------------------------------------------------------------

def range_oso_next(
    csv_path: Path = None,
    run_accuracy_test: bool = True,
) -> Dict[int, int]:
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    csv_path = Path(csv_path)
    rows: List[List[int]] = load_rows(csv_path)

    if len(rows) < 6:
        print("Not enough data for range+oso analysis (need at least 6 draws).")
        return {}

    print("=" * 50)
    print("RANGE + OSO (consolidated order5->4->3->2) - Range-Constrained Prediction")
    print("=" * 50)

    # ---------------------------------------------------------------
    # Stage 1: predict the next draw's main-number range
    # ---------------------------------------------------------------
    print(f"\n[Range Prediction — order5 -> order4 -> order3 -> order2 -> mode cascade]")
    range_min, range_max, src_min, src_max = predict_range(rows, verbose=True)
    print(f"  Predicted min: {range_min}  <- {src_min}")
    print(f"  Predicted max: {range_max}  <- {src_max}")
    print(f"  Predicted range for next draw: {range_min}-{range_max}")

    # ---------------------------------------------------------------
    # Stage 2: hierarchical order5->4->3->2 candidates per column,
    # constrained to range
    # ---------------------------------------------------------------
    predictions: Dict[int, int] = {}
    col_candidates_in_range: Dict[int, List[int]] = {}
    source: Dict[int, str] = {}

    for col in range(1, 6):
        print(f"\n[Column {col} hierarchical order5->4->3->2 analysis]")
        raw_pred, raw_source = _hierarchical_column_pick(rows, col, range_min, range_max, verbose=True)
        ranked_all = _merged_ranked_candidates(rows, col, _MAIN_RANGE)
        in_range_ranked = [v for v in ranked_all if range_min <= v <= range_max]
        col_candidates_in_range[col] = in_range_ranked if in_range_ranked else ranked_all

        print(f"  Top in-range candidates: {in_range_ranked[:8]}")

        if raw_pred is not None:
            final = raw_pred
            source[col] = raw_source
        elif in_range_ranked:
            final = in_range_ranked[0]
            source[col] = (
                f"range-constrained fallback -> next-best in-range candidate "
                f"[{range_min}-{range_max}] (multi-order/frequency ranked)"
            )
        else:
            # Should not happen (range always spans at least one integer),
            # but guard against a degenerate empty range just in case.
            final = range_min
            source[col] = f"clipped to range boundary [{range_min}-{range_max}]"

        predictions[col] = final
        print(f"  -> PICK: {final}  <- {source[col]}")

    # ---------------------------------------------------------------
    # Duplicate resolution (columns 1-5 must be unique, stays in-range)
    # ---------------------------------------------------------------
    print("\n--- Duplicate Resolution (range-constrained) ---")
    predictions = resolve_duplicates(predictions, col_candidates_in_range)

    # ---------------------------------------------------------------
    # Mega number (column 6) — NOT range-constrained
    # ---------------------------------------------------------------
    print(f"\n[Mega hierarchical order5->4->3->2 analysis]")
    mega_pred, mega_source = _hierarchical_mega_pick(rows, verbose=True)
    predictions[6] = mega_pred
    source[6] = mega_source
    print(f"  -> PICK: {mega_pred}  <- {source[6]}")

    # ---------------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------------
    print("\n" + "=" * 50)
    print("RANGE_OSO_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    print(f"  Predicted range: {range_min}-{range_max}")
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}  <- {source[col]}")
    print(f"  Mega:     {predictions[6]}  <- {source[6]}")
    print("=" * 50)

    predictions["_range"] = (range_min, range_max)

    # ---------------------------------------------------------------
    # Optional accuracy test
    # ---------------------------------------------------------------
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("RANGE_OSO_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from range_oso_next_minus_one import range_oso_next_minus_one
        range_oso_next_minus_one(csv_path)
        print("=" * 50)

    return predictions


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _csv = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print("\n" + "=" * 50)
    print("RANGE_OSO_NEXT: Forward Prediction")
    print("=" * 50)
    range_oso_next(_csv)
