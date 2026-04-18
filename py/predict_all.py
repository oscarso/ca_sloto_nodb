import sys
from pathlib import Path
from typing import Dict, List
import io
import shutil
import csv

# Import all four prediction modules
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "oso"))
sys.path.insert(0, str(Path(__file__).parent / "kimi"))
sys.path.insert(0, str(Path(__file__).parent / "weather"))
sys.path.insert(0, str(Path(__file__).parent / "monte"))
sys.path.insert(0, str(Path(__file__).parent / "exclude"))
from oso_next import oso_next
from kimi_next import kimi_next
from weather_next import weather_next
from monte_next import monte_next
from exclude_next import exclude_next


def predict_all(csv_path: Path = None, top_n: int = None, simulations: int = None) -> None:
    """
    Run all four prediction algorithms (oso_next, kimi_next, weather_next, monte_next)
    and display their results side by side.
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3  # Default to 3
    if simulations is None:
        simulations = int(sys.argv[3]) if len(sys.argv) > 3 else 10000  # Default to 10000
    
    print("\n" + "=" * 70)
    print("PREDICTION COMPARISON - All Algorithms")
    print("=" * 70)
    print(f"Data file: {csv_path}")
    print("=" * 70)
    
    def run_capture(fn, *args, **kwargs):
        """Run algorithm, capture stdout, split detailed output from FINAL PREDICTION block."""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        result = fn(*args, **kwargs)
        captured = sys.stdout.getvalue()
        sys.stdout = old_stdout
        # Split on FINAL PREDICTION marker
        marker = "FINAL PREDICTION (with source)"
        if marker in captured:
            idx = captured.rfind(marker)
            # Find the "====" line before marker (top header bar)
            header_start = captured.rfind("=" * 10, 0, idx)
            # Skip the second "====" (bottom of header) right after marker
            second_bar = captured.find("=" * 10, idx)
            # Advance past the entire second bar line (newline after it)
            after_second_bar = captured.find("\n", second_bar) + 1 if second_bar != -1 else -1
            # Find the closing "====" line (after the prediction content)
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
    
    # Run all four algorithms, capturing output
    print("\n" + "=" * 70)
    print("[1] Running oso_next (detailed output below)")
    print("=" * 70)
    oso_result, oso_detail, oso_final = run_capture(oso_next, csv_path, top_n=top_n, run_accuracy_test=False)
    print(oso_detail)
    
    print("\n" + "=" * 70)
    print("[2] Running kimi_next (detailed output below)")
    print("=" * 70)
    kimi_result, kimi_detail, kimi_final = run_capture(kimi_next, csv_path, run_accuracy_test=False)
    print(kimi_detail)
    
    print("\n" + "=" * 70)
    print("[3] Running weather_next (detailed output below)")
    print("=" * 70)
    weather_result, weather_detail, weather_final = run_capture(weather_next, csv_path, run_accuracy_test=False)
    print(weather_detail)
    
    print("\n" + "=" * 70)
    print("[4] Running monte_next (detailed output below)")
    print("=" * 70)
    monte_result, monte_detail, monte_final = run_capture(monte_next, csv_path, simulations=simulations, run_accuracy_test=False)
    print(monte_detail)
    
    print("\n" + "=" * 70)
    print("[5] Running exclude_next (ensemble of all algorithms)")
    print("=" * 70)
    exclude_result, exclude_detail, exclude_final = run_capture(
        exclude_next, csv_path, top_n=top_n, simulations=simulations, run_accuracy_test=False
    )
    print(exclude_detail)
    
    oso_weak = bool(oso_result.get("_weak"))
    
    # Show all FINAL PREDICTIONs grouped together
    print("\n" + "#" * 70)
    print("# ALL FINAL PREDICTIONS")
    print("#" * 70)
    blocks = []
    if not oso_weak:
        blocks.append(oso_final)
    else:
        print("\n[oso_next suppressed: weak signal (mostly order2 fallback)]")
    blocks.extend([kimi_final, weather_final, monte_final, exclude_final])
    for block in blocks:
        if block:
            print(block)
    
    # Read the last draw number from CSV
    last_draw_num = None
    with csv_path.open("r", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if ";" in sample and "," not in sample else ","
        reader = csv.reader(f, delimiter=delimiter)
        for raw in reader:
            if not raw or raw[0].strip().lower() == "draw_num":
                continue
            last_draw_num = int(raw[0])
    
    predicted_draw_num = last_draw_num + 1 if last_draw_num else "Unknown"
    
    # Display results in table format
    print("\n" + "=" * 70)
    print(f"PREDICTION RESULTS (for Draw #{predicted_draw_num})")
    print("=" * 70)
    
    # Header row (suppress oso if weak)
    if oso_weak:
        print(f"{'Column':<12} {'kimi_next':<12} {'weather_next':<12} {'monte_next':<12} {'exclude':<12}")
    else:
        print(f"{'Column':<12} {'oso_next':<12} {'kimi_next':<12} {'weather_next':<12} {'monte_next':<12} {'exclude':<12}")
    print("-" * 84)
    
    # Data rows for columns 1-5
    for col in range(1, 6):
        oso_val = oso_result.get(col, "N/A")
        kimi_val = kimi_result.get(col, "N/A")
        weather_val = weather_result.get(col, "N/A")
        monte_val = monte_result.get(col, "N/A")
        exclude_val = exclude_result.get(col, "N/A")
        label = f"Column {col}"
        if oso_weak:
            print(f"{label:<12} {str(kimi_val):<12} {str(weather_val):<12} {str(monte_val):<12} {str(exclude_val):<12}")
        else:
            print(f"{label:<12} {str(oso_val):<12} {str(kimi_val):<12} {str(weather_val):<12} {str(monte_val):<12} {str(exclude_val):<12}")
    
    # Mega row
    print("-" * 84)
    oso_mega = oso_result.get(6, "N/A")
    kimi_mega = kimi_result.get(6, "N/A")
    weather_mega = weather_result.get(6, "N/A")
    monte_mega = monte_result.get(6, "N/A")
    exclude_mega = exclude_result.get(6, "N/A")
    if oso_weak:
        print(f"{'Mega':<12} {str(kimi_mega):<12} {str(weather_mega):<12} {str(monte_mega):<12} {str(exclude_mega):<12}")
    else:
        print(f"{'Mega':<12} {str(oso_mega):<12} {str(kimi_mega):<12} {str(weather_mega):<12} {str(monte_mega):<12} {str(exclude_mega):<12}")
    
    print("=" * 70)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("ALGORITHM CHARACTERISTICS")
    print("=" * 70)
    print("oso_next:     Pattern matching with hierarchical fallback")
    print("kimi_next:    Ensemble of frequency, gap, Markov, and positional analysis")
    print("weather_next: Trend, momentum, cycle, pressure, and drift analysis")
    print("monte_next:   Monte Carlo simulation with statistical sampling")
    print("exclude_next: Voting ensemble combining all above (oso excluded if weak)")
    print("=" * 70)
    
    # Run accuracy tests for all three
    print("\n" + "=" * 70)
    print("ACCURACY TESTS (minus_one)")
    print("=" * 70)
    
    # Import minus_one functions
    from oso_next_minus_one import oso_next_minus_one
    from kimi_next_minus_one import kimi_next_minus_one
    from weather_next_minus_one import weather_next_minus_one
    from monte_next_minus_one import monte_next_minus_one
    from exclude_next_minus_one import exclude_next_minus_one
    
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
    
    # Clean up temp files and folder
    tmp_dir = csv_path.parent / "tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        print(f"\n[Cleaned up temp folder: {tmp_dir}]")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    simulations = int(sys.argv[3]) if len(sys.argv) > 3 else None
    predict_all(csv_path, top_n, simulations)
