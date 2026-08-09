import csv
import io
import shutil
import sys
from pathlib import Path
from typing import Dict, List

# Add py/ root so utils and sub-modules are importable
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "oso"))
sys.path.insert(0, str(Path(__file__).parent / "kimi"))
sys.path.insert(0, str(Path(__file__).parent / "weather"))
sys.path.insert(0, str(Path(__file__).parent / "monte"))
sys.path.insert(0, str(Path(__file__).parent / "exclude"))
sys.path.insert(0, str(Path(__file__).parent / "hotcold"))
sys.path.insert(0, str(Path(__file__).parent / "pattern"))
sys.path.insert(0, str(Path(__file__).parent / "rangeoso"))

from oso_next import oso_next
from kimi_next import kimi_next
from weather_next import weather_next
from monte_next import monte_next
from exclude_next import exclude_next
from hotcold_next import hotcold_next
from pattern_next import pattern_next
from range_oso_next import range_oso_next


def predict_all(
    csv_path: Path = None,
    top_n: int = None,
    simulations: int = None,
    recent_window: int = None,
    medium_window: int = None,
) -> None:
    """
    Run all eight prediction algorithms and display results side by side.

    oso, kimi, weather, and monte are run first and their results are passed
    directly into exclude_next — avoiding the redundant re-run that previously
    occurred when exclude_next called them internally.
    """
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parent.parent / "data" / "dresult_test.csv"
        )
    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if simulations is None:
        simulations = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    if recent_window is None:
        recent_window = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    if medium_window is None:
        medium_window = int(sys.argv[5]) if len(sys.argv) > 5 else 40

    print("\n" + "=" * 70)
    print("PREDICTION COMPARISON - All Algorithms")
    print("=" * 70)
    print(f"Data file:      {csv_path}")
    print(f"top_n:          {top_n}  |  simulations: {simulations:,}")
    print(f"hotcold recent: {recent_window} draws  |  medium: {medium_window} draws")
    print("=" * 70)

    def run_capture(fn, *args, **kwargs):
        """Run algorithm, capture stdout, split detailed output from FINAL PREDICTION block."""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        result = fn(*args, **kwargs)
        captured = sys.stdout.getvalue()
        sys.stdout = old_stdout

        marker = "FINAL PREDICTION (with source)"
        if marker in captured:
            idx = captured.rfind(marker)
            header_start = captured.rfind("=" * 10, 0, idx)
            second_bar = captured.find("=" * 10, idx)
            after_second_bar = captured.find("\n", second_bar) + 1 if second_bar != -1 else -1
            closing_bar = captured.find("=" * 10, after_second_bar) if after_second_bar > 0 else -1
            if closing_bar != -1:
                close_end = captured.find("\n", closing_bar) + 1
            else:
                close_end = len(captured)
            detailed = captured[:header_start] + captured[close_end:]
            final_block = captured[header_start:close_end]
        else:
            detailed = captured
            final_block = ""
        return result, detailed, final_block

    # ------------------------------------------------------------------
    # Run the four base algorithms
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[1] Running oso_next (detailed output below)")
    print("=" * 70)
    oso_result, oso_detail, oso_final = run_capture(
        oso_next, csv_path, top_n=top_n, run_accuracy_test=False
    )
    print(oso_detail)

    print("\n" + "=" * 70)
    print("[2] Running kimi_next (detailed output below)")
    print("=" * 70)
    kimi_result, kimi_detail, kimi_final = run_capture(
        kimi_next, csv_path, run_accuracy_test=False
    )
    print(kimi_detail)

    print("\n" + "=" * 70)
    print("[3] Running weather_next (detailed output below)")
    print("=" * 70)
    weather_result, weather_detail, weather_final = run_capture(
        weather_next, csv_path, run_accuracy_test=False
    )
    print(weather_detail)

    print("\n" + "=" * 70)
    print("[4] Running monte_next (detailed output below)")
    print("=" * 70)
    monte_result, monte_detail, monte_final = run_capture(
        monte_next, csv_path, simulations=simulations, run_accuracy_test=False
    )
    print(monte_detail)

    # ------------------------------------------------------------------
    # Run exclude_next with precomputed results — no double-run
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[5] Running exclude_next (ensemble of all algorithms)")
    print("=" * 70)
    exclude_result, exclude_detail, exclude_final = run_capture(
        exclude_next,
        csv_path,
        top_n=top_n,
        simulations=simulations,
        run_accuracy_test=False,
        precomputed_preds={
            "oso": oso_result,
            "kimi": kimi_result,
            "weather": weather_result,
            "monte": monte_result,
        },
    )
    print(exclude_detail)

    print("\n" + "=" * 70)
    print("[6] Running hotcold_next (detailed output below)")
    print("=" * 70)
    hotcold_result, hotcold_detail, hotcold_final = run_capture(
        hotcold_next,
        csv_path,
        recent_window=recent_window,
        medium_window=medium_window,
        run_accuracy_test=False,
    )
    print(hotcold_detail)

    print("\n" + "=" * 70)
    print("[7] Running pattern_next (detailed output below)")
    print("=" * 70)
    pattern_result, pattern_detail, pattern_final = run_capture(
        pattern_next,
        csv_path,
        run_accuracy_test=False,
    )
    print(pattern_detail)

    print("\n" + "=" * 70)
    print("[8] Running range_oso_next (detailed output below)")
    print("=" * 70)
    range_oso_result, range_oso_detail, range_oso_final = run_capture(
        range_oso_next,
        csv_path,
        run_accuracy_test=False,
    )
    print(range_oso_detail)

    oso_weak = bool(oso_result.get("_weak"))

    # ------------------------------------------------------------------
    # Show all FINAL PREDICTIONs grouped together
    # ------------------------------------------------------------------
    print("\n" + "#" * 70)
    print("# ALL FINAL PREDICTIONS")
    print("#" * 70)
    if oso_weak:
        print("\n[oso_next suppressed: weak signal (mostly order2 fallback)]")
    blocks = []
    if not oso_weak:
        blocks.append(oso_final)
    blocks.extend([
        kimi_final, weather_final, monte_final, exclude_final, hotcold_final,
        pattern_final, range_oso_final,
    ])
    for block in blocks:
        if block:
            print(block)

    # Read the last draw number from CSV
    last_draw_num = None
    with Path(csv_path).open("r", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if ";" in sample and "," not in sample else ","
        reader = csv.reader(f, delimiter=delimiter)
        for raw in reader:
            if not raw or raw[0].strip().lower() == "draw_num":
                continue
            last_draw_num = int(raw[0])

    predicted_draw_num = last_draw_num + 1 if last_draw_num else "Unknown"

    # ------------------------------------------------------------------
    # Summary table
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"PREDICTION RESULTS (for Draw #{predicted_draw_num})")
    print("=" * 70)

    if oso_weak:
        print(f"{'Column':<12} {'kimi':<8} {'weather':<10} {'monte':<8} {'exclude':<10} {'hotcold':<8} {'pattern':<8} {'range_oso':<10}")
    else:
        print(f"{'Column':<12} {'oso':<8} {'kimi':<8} {'weather':<10} {'monte':<8} {'exclude':<10} {'hotcold':<8} {'pattern':<8} {'range_oso':<10}")
    print("-" * 116)

    for col in range(1, 6):
        label = f"Column {col}"
        k  = str(kimi_result.get(col, 'N/A'))
        w  = str(weather_result.get(col, 'N/A'))
        mo = str(monte_result.get(col, 'N/A'))
        ex = str(exclude_result.get(col, 'N/A'))
        hc = str(hotcold_result.get(col, 'N/A'))
        pa = str(pattern_result.get(col, 'N/A'))
        ro = str(range_oso_result.get(col, 'N/A'))
        if oso_weak:
            print(f"{label:<12} {k:<8} {w:<10} {mo:<8} {ex:<10} {hc:<8} {pa:<8} {ro:<10}")
        else:
            o = str(oso_result.get(col, 'N/A'))
            print(f"{label:<12} {o:<8} {k:<8} {w:<10} {mo:<8} {ex:<10} {hc:<8} {pa:<8} {ro:<10}")

    print("-" * 116)
    k  = str(kimi_result.get(6, 'N/A'))
    w  = str(weather_result.get(6, 'N/A'))
    mo = str(monte_result.get(6, 'N/A'))
    ex = str(exclude_result.get(6, 'N/A'))
    hc = str(hotcold_result.get(6, 'N/A'))
    pa = str(pattern_result.get(6, 'N/A'))
    ro = str(range_oso_result.get(6, 'N/A'))
    if oso_weak:
        print(f"{'Mega':<12} {k:<8} {w:<10} {mo:<8} {ex:<10} {hc:<8} {pa:<8} {ro:<10}")
    else:
        o = str(oso_result.get(6, 'N/A'))
        print(f"{'Mega':<12} {o:<8} {k:<8} {w:<10} {mo:<8} {ex:<10} {hc:<8} {pa:<8} {ro:<10}")
    print("=" * 70)

    ro_range = range_oso_result.get("_range")
    if ro_range:
        print(f"range_oso predicted range: {ro_range[0]}-{ro_range[1]}")

    print("\n" + "=" * 70)
    print("ALGORITHM CHARACTERISTICS")
    print("=" * 70)
    print("oso_next:     Pattern matching with hierarchical fallback")
    print("kimi_next:    Ensemble of frequency, gap, Markov, and positional analysis")
    print("weather_next: Trend, momentum, cycle, pressure, and drift analysis")
    print("monte_next:   Monte Carlo simulation with statistical sampling")
    print("exclude_next: Contrarian deficit+staleness (oso excluded if weak)")
    print("hotcold_next: Hot/Cold frequency analysis across multiple time windows")
    print("pattern_next: Structural patterns - positional bands, decade bands, sum constraint")
    print("range_oso:    Predicts next-draw min/max range (order5->4->3->2->mode cascade), then")
    print("              picks each column via the same order5->4->3->2 hierarchical fallback")
    print("              (whichever window size first has a historical match), constrained")
    print("              to only pick within that range")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Accuracy tests (minus_one)
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ACCURACY TESTS (minus_one)")
    print("=" * 70)

    from oso_next_minus_one import oso_next_minus_one
    from kimi_next_minus_one import kimi_next_minus_one
    from weather_next_minus_one import weather_next_minus_one
    from monte_next_minus_one import monte_next_minus_one
    from exclude_next_minus_one import exclude_next_minus_one
    from hotcold_next_minus_one import hotcold_next_minus_one
    from pattern_next_minus_one import pattern_next_minus_one
    from range_oso_next_minus_one import range_oso_next_minus_one

    if not oso_weak:
        print("\n--- oso_next accuracy ---")
        oso_next_minus_one(csv_path, top_n=top_n)
    else:
        print("\n--- oso_next accuracy (skipped: weak signal) ---")

    print("\n--- kimi_next accuracy ---")
    kimi_next_minus_one(csv_path)

    print("\n--- weather_next accuracy ---")
    weather_next_minus_one(csv_path)

    print("\n--- monte_next accuracy ---")
    monte_next_minus_one(csv_path, simulations)

    print("\n--- exclude_next accuracy ---")
    exclude_next_minus_one(csv_path, top_n=top_n, simulations=simulations)

    print("\n--- hotcold_next accuracy ---")
    hotcold_next_minus_one(csv_path, recent_window=recent_window, medium_window=medium_window)

    print("\n--- pattern_next accuracy ---")
    pattern_next_minus_one(csv_path)

    print("\n--- range_oso_next accuracy ---")
    range_oso_next_minus_one(csv_path)

    # Clean up temp files
    tmp_dir = Path(csv_path).parent / "tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        print(f"\n[Cleaned up temp folder: {tmp_dir}]")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    csv_path      = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n         = int(sys.argv[2])  if len(sys.argv) > 2 else None
    simulations   = int(sys.argv[3])  if len(sys.argv) > 3 else None
    recent_window = int(sys.argv[4])  if len(sys.argv) > 4 else None
    medium_window = int(sys.argv[5])  if len(sys.argv) > 5 else None
    predict_all(csv_path, top_n, simulations, recent_window, medium_window)
