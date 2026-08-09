"""
range_oso4_next.py — Range-Constrained OSO Order-4 Predictor

Core idea
---------
Two-stage prediction:

  1. RANGE STAGE — predict the [min, max] span of the next draw's five main
     numbers (mega excluded). For every historical draw, derive
     min_val = min(col1..col5) and max_val = max(col1..col5), building two
     single-value sequences (the min-sequence and the max-sequence).

     Each sequence gets its own hierarchical order-N pattern match — the
     exact same order5 -> order4 -> order3 -> order2 cascade oso_next uses
     for the five main columns, just applied to the min-sequence for the
     predicted min and independently to the max-sequence for the predicted
     max: try a 5-row window match first (has this exact 5-in-a-row window
     been seen before, and if so what followed it?), then 4-row, then
     3-row, then 2-row. (This range-stage cascade is shared verbatim with
     range_oso3_next / range_oso5_next — see range_common.py.)

     No averaging or other arithmetic is used anywhere in this stage — these
     are lottery draw numbers, not a time series to smooth. If none of
     order5..order2 has a historical match, the final fallback is the
     single historically most-frequent value (the mode) for that sequence —
     still a pure lookup, not a computation.

  2. OSO_ORDER4 STAGE — for each main column, predict candidates the same
     way oso_next's "order4 fallback" stage does (pattern_fallback(rows, 4)):
     what value followed the current 4-row window for that column,
     historically. Candidates are then ranked (4-row match frequency first,
     then overall historical column frequency, then ascending value as a
     final tie-break) across the FULL 1-47 domain.

  3. RANGE CONSTRAINT — the final pick for each column must fall inside the
     predicted [range_min, range_max]. If the raw order4 pick is in range,
     it's kept. Otherwise the ranked candidate list is walked (restricted to
     in-range values) until an in-range candidate is found. Duplicate
     resolution (columns 1-5 must be unique) also draws only from the
     in-range ranked list, so the final prediction never leaves the
     predicted range.

The mega number (column 6) is NOT range-constrained (the range definition
explicitly excludes the mega number) — it's predicted the same way
oso_next predicts mega: order4-style pattern match on column 7, falling
back to overall column-7 frequency.
"""

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, pattern_fallback, resolve_duplicates

sys.path.insert(0, str(Path(__file__).parent))
from range_common import predict_range

_MAIN_RANGE = range(1, 48)   # columns 1-5: 1-47
_MEGA_RANGE = range(1, 28)   # column 6 (mega): 1-27
_ORDER = 4


# ---------------------------------------------------------------------------
# OSO order4-stage helpers
# ---------------------------------------------------------------------------

def _order4_tail_frequencies(rows: List[List[int]], col: int) -> Dict[int, int]:
    """
    For a given column, find every value that historically followed the
    CURRENT last-4-row window, with frequency counts (not just the single
    best pick — used to build a ranked candidate list).
    """
    if len(rows) < _ORDER + 1:
        return {}
    tail = tuple(rows[-_ORDER:][j][col] for j in range(_ORDER))
    freqs: Counter = Counter()
    for i in range(len(rows) - _ORDER):
        key = tuple(rows[i + j][col] for j in range(_ORDER))
        if key == tail:
            freqs[rows[i + _ORDER][col]] += 1
    return dict(freqs)


def _ranked_candidates(
    rows: List[List[int]],
    col: int,
    value_domain: range,
) -> List[int]:
    """
    Full ranked candidate list over value_domain for a column, ordered by:
      1. order4 tail-match frequency (desc)
      2. overall historical column frequency (desc)
      3. numeric value (asc) as final tie-break

    Covers the entire domain (not just historically-seen values) so a
    range-filtered slice always has enough candidates for duplicate
    resolution.
    """
    tail_freq = _order4_tail_frequencies(rows, col)
    overall_freq = Counter(row[col] for row in rows)

    return sorted(
        value_domain,
        key=lambda v: (-tail_freq.get(v, 0), -overall_freq.get(v, 0), v),
    )


# ---------------------------------------------------------------------------
# Main prediction function
# ---------------------------------------------------------------------------

def range_oso4_next(
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

    if len(rows) < 5:
        print("Not enough data for range+oso_order4 analysis (need at least 5 draws).")
        return {}

    print("=" * 50)
    print("RANGE + OSO_ORDER4 - Range-Constrained Prediction")
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
    # Stage 2: oso_order4 candidates per column, constrained to range
    # ---------------------------------------------------------------
    predictions: Dict[int, int] = {}
    col_candidates_in_range: Dict[int, List[int]] = {}
    source: Dict[int, str] = {}

    for col in range(1, 6):
        print(f"\n[Column {col} order4 analysis]")
        raw_pred = pattern_fallback(rows, _ORDER, col_range=[col]).get(col)
        ranked_all = _ranked_candidates(rows, col, _MAIN_RANGE)
        in_range_ranked = [v for v in ranked_all if range_min <= v <= range_max]
        col_candidates_in_range[col] = in_range_ranked if in_range_ranked else ranked_all

        print(f"  order4 raw pick: {raw_pred}")
        print(f"  Top in-range candidates: {in_range_ranked[:8]}")

        if raw_pred is not None and range_min <= raw_pred <= range_max:
            final = raw_pred
            source[col] = f"order4 pattern (4-row match), in range [{range_min}-{range_max}]"
        elif in_range_ranked:
            final = in_range_ranked[0]
            source[col] = (
                f"range-constrained fallback -> next-best in-range candidate "
                f"[{range_min}-{range_max}] (order4/frequency ranked)"
            )
        else:
            # Should not happen (range always spans at least one integer),
            # but guard against a degenerate empty range just in case.
            final = range_min if raw_pred is None else min(max(raw_pred, range_min), range_max)
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
    print(f"\n[Mega order4 analysis]")
    mega_pred = pattern_fallback(rows, _ORDER, col_range=[6]).get(6)
    if mega_pred is not None:
        source[6] = "order4 pattern (4-row mega match)"
    else:
        mega_freq = Counter(row[6] for row in rows)
        mega_pred = mega_freq.most_common(1)[0][0] if mega_freq else None
        source[6] = "fallback: most frequent historical mega value"
    predictions[6] = mega_pred
    print(f"  -> PICK: {mega_pred}  <- {source[6]}")

    # ---------------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------------
    print("\n" + "=" * 50)
    print("RANGE_OSO4_NEXT - FINAL PREDICTION (with source)")
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
        print("RANGE_OSO4_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from range_oso4_next_minus_one import range_oso4_next_minus_one
        range_oso4_next_minus_one(csv_path)
        print("=" * 50)

    return predictions


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _csv = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print("\n" + "=" * 50)
    print("RANGE_OSO4_NEXT: Forward Prediction")
    print("=" * 50)
    range_oso4_next(_csv)
