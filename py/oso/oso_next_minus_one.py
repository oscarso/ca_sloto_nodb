import csv
import sys
from pathlib import Path
from typing import List, Dict

# Import oso_next function from oso_next module
from oso_next import oso_next


def oso_next_minus_one(csv_path: Path = None, top_n: int = None) -> None:
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Read all rows
    all_rows: List[List[int]] = []
    header = None
    delimiter = ","
    
    with csv_path.open("r", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if ";" in sample and "," not in sample else ","
        reader = csv.reader(f, delimiter=delimiter)
        for raw in reader:
            if not raw:
                continue
            if raw[0].strip().lower() == "draw_num":
                header = raw
                continue
            all_rows.append([int(x) for x in raw[:7]])

    if len(all_rows) < 2:
        print("Not enough data to compare.")
        return

    # Get the actual last draw (for comparison)
    actual_last = all_rows[-1]
    
    # Create temporary file without the last row (in data/tmp folder)
    tmp_dir = csv_path.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    temp_path = tmp_dir / f"{csv_path.stem}_temp.csv"
    with temp_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        # Write header if it existed
        if header:
            writer.writerow(header)
        # Write all rows except the last one
        for row in all_rows[:-1]:
            writer.writerow(row)

    # Predict using order_next on data without the last row
    # Suppress output by redirecting stdout temporarily
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    predicted = oso_next(temp_path, top_n=top_n, run_accuracy_test=False)
    
    # Restore stdout
    sys.stdout = old_stdout
    
    # Clean up temp file
    temp_path.unlink()

    # Compare prediction with actual last draw
    print(f"Actual last draw (Draw {actual_last[0]}):")
    for i in range(1, 6):
        print(f"  Column {i}: {actual_last[i]}")
    print(f"  Mega: {actual_last[6]}")
    
    print(f"\nPredicted draw:")
    for col_idx in range(1, 6):
        val = predicted.get(col_idx)
        mark = " <--" if val == actual_last[col_idx] else ""
        print(f"  Column {col_idx}: {val}{mark}")
    mega = predicted.get(6)
    mega_mark = " <--" if mega == actual_last[6] else ""
    print(f"  Mega: {mega}{mega_mark}")

    # Calculate accuracy for main numbers
    correct = 0
    total = 0
    for col_idx in range(1, 6):
        if predicted.get(col_idx) is not None:
            total += 1
            if predicted[col_idx] == actual_last[col_idx]:
                correct += 1
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\nMain numbers accuracy: {correct}/{total} correct ({accuracy:.1f}%)")
    
    # Check mega accuracy separately
    if mega is not None and mega == actual_last[6]:
        print(f"Mega prediction: CORRECT ({mega})")
    elif mega is not None:
        print(f"Mega prediction: WRONG (predicted {mega}, actual {actual_last[6]})")
    else:
        print(f"Mega prediction: None (actual was {actual_last[6]})")


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    oso_next_minus_one(csv_path, top_n)
