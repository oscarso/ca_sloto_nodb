import io
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_THIS = Path(__file__).resolve()
_PY_ROOT = _THIS.parents[1]

# Add sibling algorithm folders to path
for sub in ("oso", "kimi", "weather", "monte"):
    sys.path.insert(0, str(_PY_ROOT / sub))
sys.path.insert(0, str(_PY_ROOT))

from utils import load_rows, resolve_duplicates
from oso_next import oso_next
from kimi_next import kimi_next
from weather_next import weather_next
from monte_next import monte_next


def _silent_run(fn, *args, **kwargs) -> Dict[int, int]:
    """Run an algorithm while suppressing its stdout output."""
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        return fn(*args, **kwargs)
    finally:
        sys.stdout = old


def exclude_next(
    csv_path: Path = None,
    top_n: int = 3,
    simulations: int = 10000,
    run_accuracy_test: bool = True,
    precomputed_preds: Optional[Dict[str, Dict[int, int]]] = None,
) -> Dict[int, int]:
    """
    EXCLUDE_NEXT — Contrarian Deficit + Staleness algorithm.

    Scores each candidate by how under-represented (deficit) and how
    long ago it last appeared (staleness), then enforces that the chosen
    value for each column does NOT match any prediction from oso, kimi,
    weather, or monte.

    Args:
        csv_path:          path to the lottery CSV
        top_n:             passed through to oso_next
        simulations:       passed through to monte_next
        run_accuracy_test: whether to run the minus-one accuracy check
        precomputed_preds: optional dict with keys 'oso', 'kimi', 'weather',
                           'monte' containing already-computed predictions.
                           When provided the four sub-algorithms are NOT re-run,
                           eliminating the double-execution that occurs when
                           predict_all.py calls them first.
    """
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else _PY_ROOT.parent / "data" / "dresult_test.csv"
        )
    csv_path = Path(csv_path)

    print("=" * 50)
    print("EXCLUDE_NEXT - Contrarian Deficit+Staleness Algorithm")
    print("=" * 50)
    print(f"Data file: {csv_path}")

    rows = load_rows(csv_path)
    if not rows:
        print("No data to analyze.")
        return {}

    # Column number ranges
    col_ranges = {
        1: range(1, 48), 2: range(1, 48), 3: range(1, 48),
        4: range(1, 48), 5: range(1, 48),
        6: range(1, 28),  # Mega
    }

    # -----------------------------------------------------------------------
    # Obtain the other algorithms' predictions (for exclusion)
    # Use precomputed results when available to avoid double-running.
    # -----------------------------------------------------------------------
    if precomputed_preds is not None:
        oso_pred = precomputed_preds.get("oso", {})
        kimi_pred = precomputed_preds.get("kimi", {})
        weather_pred = precomputed_preds.get("weather", {})
        monte_pred = precomputed_preds.get("monte", {})
        print("Using precomputed predictions (skipping re-run of sub-algorithms).")
    else:
        print("Running oso_next / kimi_next / weather_next / monte_next (for exclusion set) ...")
        oso_pred = _silent_run(oso_next, csv_path, top_n=top_n, run_accuracy_test=False)
        kimi_pred = _silent_run(kimi_next, csv_path, run_accuracy_test=False)
        weather_pred = _silent_run(weather_next, csv_path, run_accuracy_test=False)
        monte_pred = _silent_run(monte_next, csv_path, simulations=simulations, run_accuracy_test=False)

    print("\n--- Other Algorithms' Predictions (to be EXCLUDED) ---")
    header = f"{'Col':<8} {'oso':<6} {'kimi':<6} {'weather':<9} {'monte':<6}"
    print(header)
    print("-" * len(header))
    for col in range(1, 7):
        label = "Mega" if col == 6 else f"Col {col}"
        print(
            f"{label:<8} "
            f"{str(oso_pred.get(col, '-')):<6} "
            f"{str(kimi_pred.get(col, '-')):<6} "
            f"{str(weather_pred.get(col, '-')):<9} "
            f"{str(monte_pred.get(col, '-')):<6}"
        )

    # Build exclusion sets
    main_excluded: set = set()
    mega_excluded: set = set()
    for pred in (oso_pred, kimi_pred, weather_pred, monte_pred):
        for c in range(1, 6):
            v = pred.get(c)
            if isinstance(v, int):
                main_excluded.add(v)
        mv = pred.get(6)
        if isinstance(mv, int):
            mega_excluded.add(mv)

    excluded: Dict[int, set] = {c: main_excluded for c in range(1, 6)}
    excluded[6] = mega_excluded

    print(f"\nMain-numbers exclusion set ({len(main_excluded)} values): {sorted(main_excluded)}")
    print(f"Mega exclusion set ({len(mega_excluded)} values): {sorted(mega_excluded)}")

    # -----------------------------------------------------------------------
    # Deficit + Staleness scoring
    # -----------------------------------------------------------------------
    n_draws = len(rows)
    final: Dict[int, int] = {}
    source: Dict[int, str] = {}
    col_ranked: Dict[int, List[Tuple[int, float, int, int]]] = {}

    print("\n--- Deficit + Staleness Analysis ---")
    for col in range(1, 7):
        values = list(col_ranges[col])
        counts = Counter(row[col] for row in rows)
        expected = n_draws / len(values)

        last_seen: Dict[int, int] = {}
        for idx, row in enumerate(rows):
            last_seen[row[col]] = idx

        max_deficit = max((expected - counts.get(v, 0)) for v in values) or 1

        scored: List[Tuple[int, float, int, int]] = []
        for v in values:
            cnt = counts.get(v, 0)
            deficit = max(0.0, expected - cnt)
            deficit_norm = deficit / max_deficit
            stale = (n_draws - 1 - last_seen[v]) if v in last_seen else n_draws
            stale_norm = stale / n_draws
            score = 0.6 * deficit_norm + 0.4 * stale_norm
            scored.append((v, score, cnt, stale))

        scored.sort(key=lambda x: x[1], reverse=True)
        col_ranked[col] = scored

        # Pick top candidate not in exclusion set
        chosen = None
        for rank, (v, score, cnt, stale) in enumerate(scored, start=1):
            if v not in excluded[col]:
                chosen = (v, score, cnt, stale, rank)
                break
        if chosen is None:
            v, score, cnt, stale = scored[0]
            chosen = (v, score, cnt, stale, 1)

        v, score, cnt, stale, rank = chosen
        final[col] = v
        source[col] = (
            f"deficit+staleness score={score:.3f} "
            f"(count={cnt}, stale={stale} draws, rank#{rank}, {len(excluded[col])} values excluded)"
        )

    # Duplicate resolution
    print("\n--- Duplicate Resolution ---")
    col_ranked_for_dedup = {
        col: [v for v, *_ in col_ranked[col] if v not in excluded[col]]
        for col in range(1, 6)
    }
    final = resolve_duplicates(final, col_ranked_for_dedup)

    print("\n" + "=" * 50)
    print("EXCLUDE_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {final[col]}  <- {source[col]}")
    print(f"  Mega:     {final[6]}  <- {source[6]}")
    print("=" * 50)

    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("EXCLUDE_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        sys.path.insert(0, str(_THIS.parent))
        from exclude_next_minus_one import exclude_next_minus_one
        exclude_next_minus_one(csv_path, top_n=top_n, simulations=simulations)
        print("=" * 50)

    return final


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    simulations = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    exclude_next(csv_path, top_n=top_n, simulations=simulations)
