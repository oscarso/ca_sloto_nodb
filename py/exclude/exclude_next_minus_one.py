import csv
import io
import sys
from pathlib import Path
from typing import List

_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent))


def exclude_next_minus_one(csv_path: Path = None, top_n: int = 3, simulations: int = 10000) -> None:
    """
    Tests exclude_next prediction accuracy by excluding the last draw.
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _THIS.parents[2] / "data" / "dresult_test.csv"
    csv_path = Path(csv_path)

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

    actual_last = all_rows[-1]

    tmp_dir = csv_path.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    temp_path = tmp_dir / f"{csv_path.stem}_exclude_temp.csv"
    with temp_path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        if header:
            writer.writerow(header)
        for row in all_rows[:-1]:
            writer.writerow(row)

    # Suppress output while predicting
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    from exclude_next import exclude_next
    predicted = exclude_next(
        temp_path, top_n=top_n, simulations=simulations, run_accuracy_test=False
    )
    sys.stdout = old_stdout

    temp_path.unlink()

    print(f"Actual last draw (Draw {actual_last[0]}):")
    for i in range(1, 6):
        print(f"  Column {i}: {actual_last[i]}")
    print(f"  Mega: {actual_last[6]}")

    print(f"\nPredicted draw:")
    for col_idx in range(1, 6):
        print(f"  Column {col_idx}: {predicted.get(col_idx)}")
    mega = predicted.get(6)
    print(f"  Mega: {mega}")

    correct = 0
    total = 0
    for col_idx in range(1, 6):
        if predicted.get(col_idx) is not None:
            total += 1
            if predicted[col_idx] == actual_last[col_idx]:
                correct += 1

    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\nMain numbers accuracy: {correct}/{total} correct ({accuracy:.1f}%)")

    if mega is not None and mega == actual_last[6]:
        print(f"Mega prediction: CORRECT ({mega})")
    elif mega is not None:
        print(f"Mega prediction: WRONG (predicted {mega}, actual {actual_last[6]})")
    else:
        print(f"Mega prediction: None (actual was {actual_last[6]})")


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    simulations = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    exclude_next_minus_one(csv_path, top_n=top_n, simulations=simulations)
