"""
hotcold_next.py — Hot/Cold Frequency Analysis Predictor

Core idea
---------
Numbers that appear more often than chance in *recent* draws are "Hot";
numbers that appear less often are "Cold".  The algorithm scores each
candidate across three time windows:

  • Recent  (default last 20 draws) — the "hot" signal
  • Medium  (default last 40 draws) — medium-term confirmation
  • All-time (entire history)        — long-term baseline

A fourth component captures numbers that are historically frequent but
have recently gone quiet ("due" factor).

Score formula (weights sum to 1.0):
  score = 0.45 × recent_norm
        + 0.25 × medium_norm
        + 0.20 × alltime_norm
        + 0.10 × due_norm

Each predicted number is labelled with its classification:
  Hot   — recent rate ≥ 2× expected
  Warm  — recent rate ≥ 1.2× expected
  Cool  — recent rate ≥ 0.5× expected
  Cold  — recent rate < 0.5× expected
  Ice   — did not appear in the recent window at all
"""

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, resolve_duplicates

# Valid number ranges
_MAIN_RANGE = range(1, 48)   # columns 1-5: 1-47
_MEGA_RANGE  = range(1, 28)  # column 6 (mega): 1-27


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify(recent_count: int, recent_window: int, col_size: int) -> str:
    """
    Label a number based on how often it appeared in the recent window
    relative to the uniform expectation (1 / col_size).
    """
    if recent_count == 0:
        return "Ice"
    ratio = (recent_count / recent_window) / (1.0 / col_size)
    if ratio >= 2.0:
        return "Hot"
    if ratio >= 1.2:
        return "Warm"
    if ratio >= 0.5:
        return "Cool"
    return "Cold"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _safe_norm(val: float, max_val: float) -> float:
    return val / max_val if max_val > 0 else 0.0


def hotcold_score(
    candidate: int,
    alltime: Counter,
    recent: Counter,
    medium: Counter,
    total_draws: int,
    recent_window: int,
    medium_window: int,
    col_size: int,
) -> Tuple[float, Dict[str, float]]:
    """
    Compute hot/cold composite score for *candidate*.

    Returns (total_score, component_dict).
    """
    # --- recent hotness (0-1) ---
    r_rate   = recent.get(candidate, 0) / recent_window
    r_max    = max(recent.values()) / recent_window if recent else 1.0
    r_norm   = _safe_norm(r_rate, r_max)
    r_comp   = 0.45 * r_norm

    # --- medium hotness (0-1) ---
    m_rate   = medium.get(candidate, 0) / medium_window
    m_max    = max(medium.values()) / medium_window if medium else 1.0
    m_norm   = _safe_norm(m_rate, m_max)
    m_comp   = 0.25 * m_norm

    # --- all-time frequency (0-1) ---
    a_rate   = alltime.get(candidate, 0) / total_draws
    a_max    = max(alltime.values()) / total_draws if alltime else 1.0
    a_norm   = _safe_norm(a_rate, a_max)
    a_comp   = 0.20 * a_norm

    # --- due factor: historically frequent but recently absent ---
    due_raw  = max(0.0, a_rate - r_rate)          # gap between historical and recent rate
    due_norm = min(due_raw / (a_max or 1.0), 1.0) # normalise by max all-time rate
    d_comp   = 0.10 * due_norm

    total = r_comp + m_comp + a_comp + d_comp
    return total, {
        "recent":  r_comp,
        "medium":  m_comp,
        "alltime": a_comp,
        "due":     d_comp,
    }


# ---------------------------------------------------------------------------
# Main prediction function
# ---------------------------------------------------------------------------

def hotcold_next(
    csv_path: Path = None,
    recent_window: int = 20,
    medium_window: int = 40,
    run_accuracy_test: bool = True,
) -> Dict[int, int]:
    """
    Predict the next draw using Hot/Cold frequency analysis.

    Args:
        csv_path:          path to the lottery CSV
        recent_window:     look-back window for "hot" classification (default 20)
        medium_window:     medium look-back window (default 40)
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
        print("Not enough data for hotcold analysis (need at least 10 draws).")
        return {}

    total_draws = len(rows)
    # Clamp windows to available data
    r_win = min(recent_window, total_draws)
    m_win = min(medium_window, total_draws)

    recent_rows = rows[-r_win:]
    medium_rows = rows[-m_win:]

    print("=" * 50)
    print("HOTCOLD NEXT - Hot/Cold Frequency Analysis")
    print("=" * 50)
    print(f"Total draws : {total_draws}")
    print(f"Recent window : last {r_win} draws")
    print(f"Medium window : last {m_win} draws")
    print(f"\nClassification scale:")
    print(f"  Hot  = recent rate ≥ 2.0× expected")
    print(f"  Warm = recent rate ≥ 1.2× expected")
    print(f"  Cool = recent rate ≥ 0.5× expected")
    print(f"  Cold = recent rate < 0.5× expected")
    print(f"  Ice  = zero appearances in recent window")

    predictions: Dict[int, int] = {}
    col_ranked:  Dict[int, List[int]] = {}
    source:      Dict[int, str] = {}

    # -------------------------------------------------------------------
    # Main numbers: columns 1-5
    # -------------------------------------------------------------------
    col_size_main = len(_MAIN_RANGE)

    for col in range(1, 6):
        print(f"\n[Column {col} Hot/Cold Analysis]")

        alltime = Counter(row[col] for row in rows)
        recent  = Counter(row[col] for row in recent_rows)
        medium  = Counter(row[col] for row in medium_rows)

        # Classify historically-seen numbers
        labels = {
            v: classify(recent.get(v, 0), r_win, col_size_main)
            for v in alltime
        }
        hot_list  = sorted(v for v, lbl in labels.items() if lbl == "Hot")
        cold_list = sorted(v for v, lbl in labels.items() if lbl in ("Cold", "Ice"))

        print(f"  Hot  numbers : {hot_list if hot_list else '(none)'}")
        print(f"  Cold/Ice     : {cold_list[:12]}{'…' if len(cold_list) > 12 else ''}")

        # Score every valid candidate
        scored: List[Tuple[int, float, Dict]] = []
        for candidate in _MAIN_RANGE:
            score, comps = hotcold_score(
                candidate, alltime, recent, medium,
                total_draws, r_win, m_win, col_size_main,
            )
            scored.append((candidate, score, comps))

        scored.sort(key=lambda x: x[1], reverse=True)

        best, best_score, best_comps = scored[0]
        best_label = labels.get(best, "New")   # "New" = never appeared historically

        predictions[col]  = best
        col_ranked[col]   = [c for c, _, _ in scored]
        dominant = max(best_comps.items(), key=lambda kv: kv[1])
        source[col] = (
            f"hotcold score={best_score:.3f} [{best_label}] "
            f"dominant={dominant[0]} ({dominant[1]:.3f}) | "
            f"recent={recent.get(best, 0)}/{r_win}, "
            f"alltime={alltime.get(best, 0)}/{total_draws}"
        )

        top5 = [(c, round(s, 3), labels.get(c, "New")) for c, s, _ in scored[:5]]
        print(f"  Top 5 candidates : {top5}")
        print(f"  -> PREDICTED: {best} [{best_label}] (score: {best_score:.3f})")
        print(f"     Components: recent={best_comps['recent']:.3f}  "
              f"medium={best_comps['medium']:.3f}  "
              f"alltime={best_comps['alltime']:.3f}  "
              f"due={best_comps['due']:.3f}")

    # -------------------------------------------------------------------
    # Mega number: column 6
    # -------------------------------------------------------------------
    col_size_mega = len(_MEGA_RANGE)

    print(f"\n[Mega Hot/Cold Analysis]")

    alltime_m = Counter(row[6] for row in rows)
    recent_m  = Counter(row[6] for row in recent_rows)
    medium_m  = Counter(row[6] for row in medium_rows)

    labels_m = {
        v: classify(recent_m.get(v, 0), r_win, col_size_mega)
        for v in alltime_m
    }
    hot_m  = sorted(v for v, lbl in labels_m.items() if lbl == "Hot")
    cold_m = sorted(v for v, lbl in labels_m.items() if lbl in ("Cold", "Ice"))

    print(f"  Hot  mega : {hot_m if hot_m else '(none)'}")
    print(f"  Cold/Ice  : {cold_m}")

    mega_scored: List[Tuple[int, float, Dict]] = []
    for candidate in _MEGA_RANGE:
        score, comps = hotcold_score(
            candidate, alltime_m, recent_m, medium_m,
            total_draws, r_win, m_win, col_size_mega,
        )
        mega_scored.append((candidate, score, comps))

    mega_scored.sort(key=lambda x: x[1], reverse=True)
    best_m, best_m_score, best_m_comps = mega_scored[0]
    best_m_label = labels_m.get(best_m, "New")

    predictions[6] = best_m
    col_ranked[6]  = [c for c, _, _ in mega_scored]
    dom_m = max(best_m_comps.items(), key=lambda kv: kv[1])
    source[6] = (
        f"hotcold score={best_m_score:.3f} [{best_m_label}] "
        f"dominant={dom_m[0]} ({dom_m[1]:.3f}) | "
        f"recent={recent_m.get(best_m, 0)}/{r_win}, "
        f"alltime={alltime_m.get(best_m, 0)}/{total_draws}"
    )

    top5_m = [(c, round(s, 3), labels_m.get(c, "New")) for c, s, _ in mega_scored[:5]]
    print(f"  Top 5 candidates : {top5_m}")
    print(f"  -> PREDICTED: {best_m} [{best_m_label}] (score: {best_m_score:.3f})")

    # -------------------------------------------------------------------
    # Duplicate resolution (columns 1-5 must be unique)
    # -------------------------------------------------------------------
    print("\n--- Duplicate Resolution ---")
    predictions = resolve_duplicates(predictions, col_ranked)

    # -------------------------------------------------------------------
    # Final summary
    # -------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("HOTCOLD_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}  <- {source[col]}")
    print(f"  Mega:     {predictions[6]}  <- {source[6]}")
    print("=" * 50)

    # -------------------------------------------------------------------
    # Optional accuracy test
    # -------------------------------------------------------------------
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("HOTCOLD_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from hotcold_next_minus_one import hotcold_next_minus_one
        hotcold_next_minus_one(csv_path, recent_window=r_win, medium_window=m_win)
        print("=" * 50)

    return predictions


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _csv    = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    _recent = int(sys.argv[2])  if len(sys.argv) > 2 else 20
    _medium = int(sys.argv[3])  if len(sys.argv) > 3 else 40

    print("\n" + "=" * 50)
    print("HOTCOLD_NEXT: Forward Prediction")
    print("=" * 50)
    hotcold_next(_csv, recent_window=_recent, medium_window=_medium)
