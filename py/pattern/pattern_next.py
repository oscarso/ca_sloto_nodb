"""
pattern_next.py — Structural Pattern Predictor

Core idea
---------
This lottery's results are not random noise across all positions: the draw is
reported as five *sorted-ascending* main numbers plus a mega number, and that
ordering imprints a strong, repeatable structure on each column.  Analysis of
the full history (data/2026-0530_dresult.csv, 2,708 draws) shows:

  • Each column lives in its own band:
        col1 ≈ 1-10  (mean  7.8)   col2 ≈ 11-20 (mean 15.6)
        col3 ≈ 21-30 (mean 23.5)   col4 ≈ 31-40 (mean 31.8)
        col5 ≈ 41-47 (mean 40.1)
  • The sum of the five main numbers is tightly clustered (mean ≈ 119,
    modal band 110-129) — extreme low/high totals are rare.
  • Within each column the value distribution has clear "decade-band" peaks.

`pattern_next` predicts the next draw by exploiting that structure rather than
by sequence-matching (oso) or raw frequency (hotcold).  For every column it
scores each candidate value on three structural signals:

  score = 0.55 × positional   (how typical the value is for THIS column)
        + 0.30 × recent        (positional frequency in the recent window)
        + 0.15 × band          (conformance to the column's modal decade band)

After the five column winners are chosen, a **sum-band correction** nudges the
selection toward the historical modal total, and the five mains are re-sorted
ascending so the prediction respects the lottery's structural shape.

The mega number (column 6, range 1-27) is predicted from positional +
recent frequency only — it has no sort constraint.
"""

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, resolve_duplicates

# Valid number ranges
_MAIN_RANGE = range(1, 48)   # columns 1-5: 1-47
_MEGA_RANGE = range(1, 28)   # column 6 (mega): 1-27


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _safe_norm(val: float, max_val: float) -> float:
    return val / max_val if max_val > 0 else 0.0


def pattern_score(
    candidate: int,
    positional: Counter,
    recent: Counter,
    band_dist: Counter,
    band_size: int,
) -> Tuple[float, Dict[str, float]]:
    """
    Composite structural score for *candidate* in a single column.

    positional  – all-time value frequency for this column position
    recent      – value frequency for this column in the recent window
    band_dist   – distribution of decade-bands for this column position
    band_size   – width of a decade band (10)

    Returns (total_score, component_dict).
    """
    p_max = max(positional.values()) if positional else 1.0
    p_norm = _safe_norm(positional.get(candidate, 0), p_max)
    p_comp = 0.55 * p_norm

    r_max = max(recent.values()) if recent else 1.0
    r_norm = _safe_norm(recent.get(candidate, 0), r_max)
    r_comp = 0.30 * r_norm

    band = (candidate - 1) // band_size
    b_max = max(band_dist.values()) if band_dist else 1.0
    b_norm = _safe_norm(band_dist.get(band, 0), b_max)
    b_comp = 0.15 * b_norm

    total = p_comp + r_comp + b_comp
    return total, {"positional": p_comp, "recent": r_comp, "band": b_comp}


def _sum_band_correction(
    predictions: Dict[int, int],
    col_ranked: Dict[int, List[int]],
    target_sum: int,
    tolerance: int,
) -> Dict[int, int]:
    """
    Nudge the five main-number picks so their total lands inside
    [target_sum - tolerance, target_sum + tolerance].

    For each correction step it finds the single column swap (to that column's
    next-best candidate) that moves the running total closest to target_sum,
    without colliding with the other columns.  Stops when inside the band or
    when no improving swap exists.
    """
    pred = dict(predictions)
    cols = list(range(1, 6))

    for _ in range(12):
        cur_sum = sum(pred[c] for c in cols)
        if abs(cur_sum - target_sum) <= tolerance:
            break

        best_swap = None          # (col, new_val, new_distance)
        cur_dist = abs(cur_sum - target_sum)

        for col in cols:
            used = {pred[c] for c in cols if c != col}
            # consider the column's top alternatives (already score-ranked)
            for cand in col_ranked[col][:25]:
                if cand in used or cand == pred[col]:
                    continue
                new_sum = cur_sum - pred[col] + cand
                new_dist = abs(new_sum - target_sum)
                if new_dist < cur_dist and (best_swap is None or new_dist < best_swap[2]):
                    best_swap = (col, cand, new_dist)

        if best_swap is None:
            break
        col, new_val, _ = best_swap
        pred[col] = new_val

    return pred


# ---------------------------------------------------------------------------
# Main prediction function
# ---------------------------------------------------------------------------

def pattern_next(
    csv_path: Path = None,
    recent_window: int = 50,
    run_accuracy_test: bool = True,
) -> Dict[int, int]:
    """
    Predict the next draw using structural-pattern analysis.

    Args:
        csv_path:          path to the lottery CSV
        recent_window:     look-back window for the recent-frequency signal
        run_accuracy_test: whether to run the minus-one accuracy check
    """
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    csv_path = Path(csv_path)

    rows = load_rows(csv_path)

    if len(rows) < 10:
        print("Not enough data for pattern analysis (need at least 10 draws).")
        return {}

    total_draws = len(rows)
    r_win = min(recent_window, total_draws)
    recent_rows = rows[-r_win:]
    band_size = 10

    # Historical modal total of the five main numbers (structural sum band)
    main_sums = [sum(r[1:6]) for r in rows]
    target_sum = round(sum(main_sums) / len(main_sums))
    # tolerance ≈ half a decade band keeps us inside the dominant cluster
    tolerance = 9

    print("=" * 50)
    print("PATTERN NEXT - Structural Pattern Analysis")
    print("=" * 50)
    print(f"Total draws       : {total_draws}")
    print(f"Recent window     : last {r_win} draws")
    print(f"Modal main-sum    : ~{target_sum} (target band ±{tolerance})")
    print(f"\nScore = 0.55*positional + 0.30*recent + 0.15*band")
    print(f"  positional : how typical a value is for that column")
    print(f"  recent     : value frequency in the recent window")
    print(f"  band       : conformance to the column's modal decade band")

    predictions: Dict[int, int] = {}
    col_ranked: Dict[int, List[int]] = {}
    source: Dict[int, str] = {}

    # -------------------------------------------------------------------
    # Main numbers: columns 1-5
    # -------------------------------------------------------------------
    for col in range(1, 6):
        print(f"\n[Column {col} Structural Analysis]")

        positional = Counter(row[col] for row in rows)
        recent = Counter(row[col] for row in recent_rows)
        band_dist = Counter((row[col] - 1) // band_size for row in rows)

        modal_band = band_dist.most_common(1)[0][0]
        band_lo, band_hi = modal_band * band_size + 1, (modal_band + 1) * band_size
        print(f"  Modal band  : {band_lo}-{band_hi} "
              f"({band_dist[modal_band]}/{total_draws} draws)")

        scored: List[Tuple[int, float, Dict]] = []
        for candidate in _MAIN_RANGE:
            score, comps = pattern_score(
                candidate, positional, recent, band_dist, band_size
            )
            scored.append((candidate, score, comps))

        scored.sort(key=lambda x: x[1], reverse=True)
        best, best_score, best_comps = scored[0]

        predictions[col] = best
        col_ranked[col] = [c for c, _, _ in scored]
        dominant = max(best_comps.items(), key=lambda kv: kv[1])
        source[col] = (
            f"pattern score={best_score:.3f} dominant={dominant[0]} "
            f"({dominant[1]:.3f}) | positional={positional.get(best, 0)}/{total_draws}, "
            f"recent={recent.get(best, 0)}/{r_win}, band={band_lo}-{band_hi}"
        )

        top5 = [(c, round(s, 3)) for c, s, _ in scored[:5]]
        print(f"  Top 5 candidates : {top5}")
        print(f"  -> PRE-SUM PICK: {best} (score: {best_score:.3f})")
        print(f"     Components: positional={best_comps['positional']:.3f}  "
              f"recent={best_comps['recent']:.3f}  band={best_comps['band']:.3f}")

    # -------------------------------------------------------------------
    # Sum-band correction (structural total constraint)
    # -------------------------------------------------------------------
    pre_sum = sum(predictions[c] for c in range(1, 6))
    print(f"\n--- Sum-Band Correction ---")
    print(f"  Pre-correction picks : "
          f"{[predictions[c] for c in range(1, 6)]} (sum={pre_sum})")
    predictions = _sum_band_correction(predictions, col_ranked, target_sum, tolerance)
    post_sum = sum(predictions[c] for c in range(1, 6))
    print(f"  Post-correction picks: "
          f"{[predictions[c] for c in range(1, 6)]} (sum={post_sum}, "
          f"target ~{target_sum})")

    # -------------------------------------------------------------------
    # Duplicate resolution, then re-sort ascending (structural shape)
    # -------------------------------------------------------------------
    print("\n--- Duplicate Resolution ---")
    predictions = resolve_duplicates(predictions, col_ranked)

    mains_sorted = sorted(predictions[c] for c in range(1, 6))
    for i, col in enumerate(range(1, 6)):
        predictions[col] = mains_sorted[i]
    print(f"  Sorted-ascending mains: {mains_sorted}")

    # -------------------------------------------------------------------
    # Mega number: column 6 (positional + recent only)
    # -------------------------------------------------------------------
    print(f"\n[Mega Structural Analysis]")
    positional_m = Counter(row[6] for row in rows)
    recent_m = Counter(row[6] for row in recent_rows)

    mega_scored: List[Tuple[int, float]] = []
    for candidate in _MEGA_RANGE:
        p_max = max(positional_m.values()) if positional_m else 1.0
        r_max = max(recent_m.values()) if recent_m else 1.0
        score = (0.65 * _safe_norm(positional_m.get(candidate, 0), p_max)
                 + 0.35 * _safe_norm(recent_m.get(candidate, 0), r_max))
        mega_scored.append((candidate, score))

    mega_scored.sort(key=lambda x: x[1], reverse=True)
    best_m, best_m_score = mega_scored[0]
    predictions[6] = best_m
    source[6] = (
        f"pattern score={best_m_score:.3f} | "
        f"positional={positional_m.get(best_m, 0)}/{total_draws}, "
        f"recent={recent_m.get(best_m, 0)}/{r_win}"
    )
    print(f"  Top 5 candidates : {[(c, round(s, 3)) for c, s in mega_scored[:5]]}")
    print(f"  -> PREDICTED: {best_m} (score: {best_m_score:.3f})")

    # -------------------------------------------------------------------
    # Final summary
    # -------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("PATTERN_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}  <- {source.get(col, '(re-sorted)')}")
    print(f"  Mega:     {predictions[6]}  <- {source[6]}")
    print("=" * 50)

    # -------------------------------------------------------------------
    # Optional accuracy test
    # -------------------------------------------------------------------
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("PATTERN_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from pattern_next_minus_one import pattern_next_minus_one
        pattern_next_minus_one(csv_path, recent_window=r_win)
        print("=" * 50)

    return predictions


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _csv = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    _recent = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    print("\n" + "=" * 50)
    print("PATTERN_NEXT: Forward Prediction")
    print("=" * 50)
    pattern_next(_csv, recent_window=_recent)
