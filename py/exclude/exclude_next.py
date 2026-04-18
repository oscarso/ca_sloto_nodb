import csv
import sys
import io
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

# Add sibling algorithm folders to path
_THIS = Path(__file__).resolve()
_PY_ROOT = _THIS.parents[1]
for sub in ("oso", "kimi", "weather", "monte"):
    sys.path.insert(0, str(_PY_ROOT / sub))

from oso_next import oso_next
from kimi_next import kimi_next
from weather_next import weather_next
from monte_next import monte_next


def _silent_run(fn, *args, **kwargs) -> Dict[int, int]:
    """Run an algorithm but suppress its stdout output."""
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        return fn(*args, **kwargs)
    finally:
        sys.stdout = old


def _load_rows(csv_path: Path) -> List[List[int]]:
    rows: List[List[int]] = []
    with csv_path.open("r", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if ";" in sample and "," not in sample else ","
        reader = csv.reader(f, delimiter=delimiter)
        for raw in reader:
            if not raw or raw[0].strip().lower() == "draw_num":
                continue
            rows.append([int(x) for x in raw[:7]])
    return rows


def exclude_next(
    csv_path: Path = None,
    top_n: int = 3,
    simulations: int = 10000,
    run_accuracy_test: bool = True,
) -> Dict[int, int]:
    """
    EXCLUDE_NEXT - Novel 'contrarian' algorithm.
    
    Uses a completely different approach from oso/kimi/weather/monte:
      - 'Deficit': under-represented numbers (expected - actual count)
      - 'Staleness': how many draws since the number was last seen
      - Combined score = deficit_norm + staleness_norm
    
    Then enforces that the picked value for each column MUST NOT match
    the prediction from oso_next, kimi_next, weather_next, or monte_next.
    If it collides, falls to next-best ranked candidate.
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _PY_ROOT.parent / "data" / "dresult_test.csv"
    csv_path = Path(csv_path)

    print("=" * 50)
    print("EXCLUDE_NEXT - Contrarian Deficit+Staleness Algorithm")
    print("=" * 50)
    print(f"Data file: {csv_path}")

    rows = _load_rows(csv_path)
    if not rows:
        print("No data to analyze.")
        return {}

    # Column ranges (based on data observed)
    col_ranges = {
        1: range(1, 48),
        2: range(1, 48),
        3: range(1, 48),
        4: range(1, 48),
        5: range(1, 48),
        6: range(1, 28),  # Mega
    }

    # Run the other 4 algorithms only to get their predictions (for exclusion)
    print(f"Running oso_next / kimi_next / weather_next / monte_next (for exclusion set) ...")
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
        print(f"{label:<8} "
              f"{str(oso_pred.get(col, '-')):<6} "
              f"{str(kimi_pred.get(col, '-')):<6} "
              f"{str(weather_pred.get(col, '-')):<9} "
              f"{str(monte_pred.get(col, '-')):<6}")

    # Build exclusion set per column (values predicted by other algos)
    excluded: Dict[int, set] = {}
    for col in range(1, 7):
        s = set()
        for pred in (oso_pred, kimi_pred, weather_pred, monte_pred):
            v = pred.get(col)
            if isinstance(v, int):
                s.add(v)
        excluded[col] = s

    n_draws = len(rows)
    final: Dict[int, int] = {}
    source: Dict[int, str] = {}
    col_ranked: Dict[int, List[Tuple[int, float, int, int]]] = {}

    print("\n--- Deficit + Staleness Analysis ---")
    for col in range(1, 7):
        values = list(col_ranges[col])
        # Count occurrences
        counts = Counter(row[col] for row in rows)
        expected = n_draws / len(values)  # uniform expectation

        # Staleness: draws since last appearance (bigger = more stale)
        last_seen: Dict[int, int] = {}
        for idx, row in enumerate(rows):
            last_seen[row[col]] = idx
        max_stale = n_draws  # never-seen => max stale

        # Score each candidate
        scored: List[Tuple[int, float, int, int]] = []
        max_deficit = max((expected - counts.get(v, 0)) for v in values) or 1
        for v in values:
            cnt = counts.get(v, 0)
            deficit = max(0.0, expected - cnt)  # only under-represented
            deficit_norm = deficit / max_deficit if max_deficit > 0 else 0
            stale = (n_draws - 1 - last_seen[v]) if v in last_seen else max_stale
            stale_norm = stale / max_stale if max_stale > 0 else 0
            score = 0.6 * deficit_norm + 0.4 * stale_norm
            scored.append((v, score, cnt, stale))

        scored.sort(key=lambda x: x[1], reverse=True)
        col_ranked[col] = scored

        # Pick top candidate NOT in exclusion set
        chosen = None
        rank = 0
        for v, score, cnt, stale in scored:
            rank += 1
            if v not in excluded[col]:
                chosen = (v, score, cnt, stale, rank)
                break
        if chosen is None:
            # Fallback: take best even if it collides (shouldn't happen in practice)
            v, score, cnt, stale = scored[0]
            chosen = (v, score, cnt, stale, 1)

        v, score, cnt, stale, rank = chosen
        final[col] = v
        source[col] = (
            f"deficit+staleness score={score:.3f} "
            f"(count={cnt}, stale={stale} draws, rank#{rank}, excluded={sorted(excluded[col])})"
        )

    # Resolve duplicates among columns 1-5
    print("\n--- Duplicate Resolution ---")
    for _ in range(20):
        seen: Dict[int, int] = {}
        duplicates = []
        for col in range(1, 6):
            v = final[col]
            if v in seen:
                duplicates.append(col)
            else:
                seen[v] = col
        if not duplicates:
            break
        for col in duplicates:
            used = {final[c] for c in range(1, 6) if c != col}
            for v, score, cnt, stale in col_ranked[col]:
                if v in excluded[col]:
                    continue
                if v in used or v == final[col]:
                    continue
                old = final[col]
                final[col] = v
                source[col] = (
                    f"duplicate resolution, deficit+staleness score={score:.3f} "
                    f"(count={cnt}, stale={stale} draws)"
                )
                print(f"Column {col}: {old} -> {v} (duplicate resolution)")
                break

    # Final summary
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
