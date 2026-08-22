"""
total_last_ten.py — aggregate hold-out backtest across all algorithms, run
over the last N draws (default 10).

For each of the last N draws in the data file (most recent first), this
pretends that draw AND every draw after it hasn't happened yet, re-predicts
it from the earlier history only (no data leakage), pools every algorithm's
predicted main numbers (mega excluded) into one flat list, and reports what
percentage of that pool matched the actual draw.

(Formerly total_next_minus_one.py, which did the same pooled comparison but
for only the single most recent draw.)

Usage:
    python3 total_last_ten.py [csv_path] [n] [top_n] [simulations] [recent_window] [medium_window]
"""

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "oso"))
sys.path.insert(0, str(Path(__file__).parent / "kimi"))
sys.path.insert(0, str(Path(__file__).parent / "weather"))
sys.path.insert(0, str(Path(__file__).parent / "monte"))
sys.path.insert(0, str(Path(__file__).parent / "exclude"))
sys.path.insert(0, str(Path(__file__).parent / "hotcold"))
sys.path.insert(0, str(Path(__file__).parent / "pattern"))
sys.path.insert(0, str(Path(__file__).parent / "rangeoso"))

from utils import load_csv, write_temp_csv
from oso_next import oso_next
from kimi_next import kimi_next
from weather_next import weather_next
from monte_next import monte_next
from exclude_next import exclude_next
from hotcold_next import hotcold_next
from pattern_next import pattern_next
from range_oso_next import range_oso_next


def _run_silent(fn, *args, **kwargs):
    """Run fn with stdout suppressed and return just its result."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        result = fn(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    return result


def _predict_pool(history_rows, header, delimiter, csv_path, top_n, simulations, recent_window, medium_window):
    """
    Run all 8 algorithms against `history_rows` and return:
        (pool, per_algo, oso_weak)
    pool      – flat list of every predicted main number (mega excluded)
    per_algo  – {algo_name: [5 predicted numbers]}
    oso_weak  – True if oso was suppressed for a weak signal
    """
    temp_path = write_temp_csv(csv_path, history_rows, header, delimiter, suffix="_total_temp")

    try:
        oso_result = _run_silent(oso_next, temp_path, top_n=top_n, run_accuracy_test=False)
        kimi_result = _run_silent(kimi_next, temp_path, run_accuracy_test=False)
        weather_result = _run_silent(weather_next, temp_path, run_accuracy_test=False)
        monte_result = _run_silent(monte_next, temp_path, simulations=simulations, run_accuracy_test=False)
        exclude_result = _run_silent(
            exclude_next, temp_path, top_n=top_n, simulations=simulations,
            run_accuracy_test=False,
            precomputed_preds={
                "oso": oso_result, "kimi": kimi_result,
                "weather": weather_result, "monte": monte_result,
            },
        )
        hotcold_result = _run_silent(
            hotcold_next, temp_path, recent_window=recent_window,
            medium_window=medium_window, run_accuracy_test=False,
        )
        pattern_result = _run_silent(pattern_next, temp_path, run_accuracy_test=False)
        range_oso_result = _run_silent(range_oso_next, temp_path, run_accuracy_test=False)
    finally:
        # Best-effort cleanup: some sandboxes disallow deleting files in
        # mounted folders, so don't let that fail the whole run.
        try:
            temp_path.unlink(missing_ok=True)
            tmp_dir = csv_path.parent / "tmp"
            if tmp_dir.exists() and not any(tmp_dir.iterdir()):
                tmp_dir.rmdir()
        except OSError:
            pass

    oso_weak = bool(oso_result.get("_weak"))

    algos = []
    if not oso_weak:
        algos.append(("oso", oso_result))
    algos.extend([
        ("kimi", kimi_result),
        ("weather", weather_result),
        ("monte", monte_result),
        ("exclude", exclude_result),
        ("hotcold", hotcold_result),
        ("pattern", pattern_result),
        ("range_oso", range_oso_result),
    ])

    pool = []
    per_algo = {}
    for name, result in algos:
        predicted = [result.get(c) for c in range(1, 6) if result.get(c) is not None]
        pool.extend(predicted)
        per_algo[name] = predicted

    return pool, per_algo, oso_weak


def total_last_ten(
    csv_path: Path = None,
    num_draws: int = None,
    top_n: int = None,
    simulations: int = None,
    recent_window: int = None,
    medium_window: int = None,
    skip: int = 0,
):
    """
    skip: how many of the most-recent draws to skip before starting the
    window (0 = start at the very last draw). Lets a long run be split into
    smaller batches, e.g. skip=0,num_draws=5 then skip=5,num_draws=5 covers
    the same 10 draws as one skip=0,num_draws=10 call.
    """
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parent.parent / "data" / "dresult_test.csv"
        )
    csv_path = Path(csv_path)
    if num_draws is None:
        num_draws = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    if top_n is None:
        top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    if simulations is None:
        simulations = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
    if recent_window is None:
        recent_window = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    if medium_window is None:
        medium_window = int(sys.argv[6]) if len(sys.argv) > 6 else 40

    all_rows, header, delimiter = load_csv(csv_path)
    if len(all_rows) <= num_draws + skip:
        print(f"Not enough data for a {num_draws}-draw hold-out test at skip={skip}.")
        return

    last_idx = len(all_rows) - 1 - skip       # index of the most recent draw in this window
    start_idx = last_idx - num_draws + 1      # index of the OLDEST draw in this window

    print("\n" + "=" * 78)
    print(f"TOTAL_LAST_{num_draws} — pooled hold-out test, Draw #{all_rows[last_idx][0]} down to Draw #{all_rows[start_idx][0]}")
    print("=" * 78)
    print(f"Data file: {csv_path}")
    print("-" * 78)
    print(f"{'Draw':<10} {'Matches':<14} {'Pool size':<12} {'% matched':<10}")
    print("-" * 78)

    per_draw = []
    total_matches_all = 0
    total_pool_all = 0

    for idx in range(last_idx, start_idx - 1, -1):
        actual_row = all_rows[idx]
        history = all_rows[:idx]  # everything strictly before this draw — no leakage
        actual_main = set(actual_row[1:6])

        pool, per_algo, oso_weak = _predict_pool(
            history, header, delimiter, csv_path, top_n, simulations, recent_window, medium_window
        )
        matches = sum(pool.count(num) for num in actual_main)
        pct = (matches / len(pool) * 100) if pool else 0.0

        per_draw.append({
            "draw": actual_row[0],
            "actual_main": sorted(actual_main),
            "matches": matches,
            "pool_size": len(pool),
            "pct": pct,
            "oso_weak": oso_weak,
        })
        total_matches_all += matches
        total_pool_all += len(pool)

        weak_tag = "  [oso weak]" if oso_weak else ""
        print(f"#{actual_row[0]:<9} {matches}/{len(pool):<12} {len(pool):<12} {pct:>6.1f}%{weak_tag}")

    overall_pct = (total_matches_all / total_pool_all * 100) if total_pool_all else 0.0
    print("-" * 78)
    print(f"OVERALL across last {num_draws} draws: {total_matches_all}/{total_pool_all} = {overall_pct:.1f}%")
    print("=" * 78)

    return {
        "per_draw": per_draw,
        "total_matches": total_matches_all,
        "total_pool": total_pool_all,
        "overall_pct": overall_pct,
    }


if __name__ == "__main__":
    csv_path      = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    num_draws     = int(sys.argv[2])  if len(sys.argv) > 2 else None
    top_n         = int(sys.argv[3])  if len(sys.argv) > 3 else None
    simulations   = int(sys.argv[4])  if len(sys.argv) > 4 else None
    recent_window = int(sys.argv[5])  if len(sys.argv) > 5 else None
    medium_window = int(sys.argv[6])  if len(sys.argv) > 6 else None
    skip          = int(sys.argv[7])  if len(sys.argv) > 7 else 0
    total_last_ten(csv_path, num_draws, top_n, simulations, recent_window, medium_window, skip=skip)
