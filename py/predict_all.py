import sys
from pathlib import Path
from typing import Dict, List
import io
import shutil
import csv

# Import all three prediction modules
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "oso"))
sys.path.insert(0, str(Path(__file__).parent / "kimi"))
sys.path.insert(0, str(Path(__file__).parent / "weather"))
from oso_next import oso_next
from kimi_next import kimi_next
from weather_next import weather_next


def predict_all(csv_path: Path = None) -> None:
    """
    Run all three prediction algorithms (oso_next, kimi_next, weather_next)
    and display their results side by side.
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    
    print("\n" + "=" * 70)
    print("PREDICTION COMPARISON - All Algorithms")
    print("=" * 70)
    print(f"Data file: {csv_path}")
    print("=" * 70)
    
    # Run oso_next
    print("\n[1] Running oso_next...")
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    oso_result = oso_next(csv_path, run_accuracy_test=False)
    sys.stdout = old_stdout
    
    # Run kimi_next
    print("[2] Running kimi_next...")
    sys.stdout = io.StringIO()
    kimi_result = kimi_next(csv_path, run_accuracy_test=False)
    sys.stdout = old_stdout
    
    # Run weather_next
    print("[3] Running weather_next...")
    sys.stdout = io.StringIO()
    weather_result = weather_next(csv_path, run_accuracy_test=False)
    sys.stdout = old_stdout
    
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
    
    # Header row
    print(f"{'Column':<12} {'oso_next':<15} {'kimi_next':<15} {'weather_next':<15}")
    print("-" * 70)
    
    # Data rows for columns 1-5
    for col in range(1, 6):
        oso_val = oso_result.get(col, "N/A")
        kimi_val = kimi_result.get(col, "N/A")
        weather_val = weather_result.get(col, "N/A")
        print(f"{'Column ' + str(col):<12} {str(oso_val):<15} {str(kimi_val):<15} {str(weather_val):<15}")
    
    # Mega row
    print("-" * 70)
    oso_mega = oso_result.get(6, "N/A")
    kimi_mega = kimi_result.get(6, "N/A")
    weather_mega = weather_result.get(6, "N/A")
    print(f"{'Mega':<12} {str(oso_mega):<15} {str(kimi_mega):<15} {str(weather_mega):<15}")
    
    print("=" * 70)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("ALGORITHM CHARACTERISTICS")
    print("=" * 70)
    print("oso_next:     Pattern matching with hierarchical fallback")
    print("kimi_next:    Ensemble of frequency, gap, Markov, and positional analysis")
    print("weather_next: Trend, momentum, cycle, pressure, and drift analysis")
    print("=" * 70)
    
    # Run accuracy tests for all three
    print("\n" + "=" * 70)
    print("ACCURACY TESTS (minus_one)")
    print("=" * 70)
    
    # Import minus_one functions
    from oso_next_minus_one import oso_next_minus_one
    from kimi_next_minus_one import kimi_next_minus_one
    from weather_next_minus_one import weather_next_minus_one
    
    print("\n--- oso_next accuracy ---")
    oso_next_minus_one(csv_path)
    
    print("\n--- kimi_next accuracy ---")
    kimi_next_minus_one(csv_path)
    
    print("\n--- weather_next accuracy ---")
    weather_next_minus_one(csv_path)
    
    # Clean up temp files and folder
    tmp_dir = csv_path.parent / "tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        print(f"\n[Cleaned up temp folder: {tmp_dir}]")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    predict_all(csv_path)
