"""
hotcold_next_minus_one.py — Accuracy test for hotcold_next.

Excludes the last draw from the dataset, predicts it, then compares
the prediction against the actual result.
"""

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_csv, write_temp_csv

sys.path.insert(0, str(Path(__file__).parent))
from hotcold_next import hotcold_next


def hotcold_next_minus_one(
    csv_path: Path = None,
    recent_window: int = 20,
    medium_window: int = 40,
) -> None:
    """
    Test hotcold_next accuracy by predicting the last known draw.

    Writes a temporary CSV without the last row, runs hotcold_next on it,
    then compares the prediction to the withheld actual draw.
    """
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    if len(sys.argv) > 2:
        recent_window = int(sys.argv[2])
    if len(sys.argv) > 3:
        medium_window = int(sys.argv[3])

    csv_path = Path(csv_path)
    all_rows, header, delimiter = load_csv(csv_path)

    if len(all_rows) < 2:
        print("Not enough data to compare.")
        return

    actual_last = all_rows[-1]

    # Write temp CSV without the last row
    temp_path = write_temp_csv(
        csv_path, all_rows[:-1], header, delimiter, suffix="_hotcold_temp"
    )

    # Silently predict on the reduced dataset
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    predicted = hotcold_next(
        temp_path,
        recent_window=recent_window,
        medium_window=medium_window,
        run_accuracy_test=False,
    )
    sys.stdout = old_stdout

    temp_path.unlink()

    # Report results
    print(f"Actual last draw (Draw {actual_last[0]}):")
    for i in range(1, 6):
        print(f"  Column {i}: {actual_last[i]}")
    print(f"  Mega: {actual_last[6]}")

    print(f"\nPredicted draw:")
    for col in range(1, 6):
        val  = predicted.get(col)
        mark = " <--" if val == actual_last[col] else ""
        print(f"  Column {col}: {val}{mark}")
    mega = predicted.get(6)
    print(f"  Mega: {mega}{' <--' if mega == actual_last[6] else ''}")

    correct = sum(1 for col in range(1, 6) if predicted.get(col) == actual_last[col])
    total   = sum(1 for col in range(1, 6) if predicted.get(col) is not None)
    accuracy = correct / total * 100 if total > 0 else 0
    print(f"\nMain numbers accuracy: {correct}/{total} correct ({accuracy:.1f}%)")

    if mega is not None and mega == actual_last[6]:
        print(f"Mega prediction: CORRECT ({mega})")
    elif mega is not None:
        print(f"Mega prediction: WRONG (predicted {mega}, actual {actual_last[6]})")
    else:
        print(f"Mega prediction: None (actual was {actual_last[6]})")


if __name__ == "__main__":
    _csv    = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    _recent = int(sys.argv[2])  if len(sys.argv) > 2 else 20
    _medium = int(sys.argv[3])  if len(sys.argv) > 3 else 40
    hotcold_next_minus_one(_csv, recent_window=_recent, medium_window=_medium)
