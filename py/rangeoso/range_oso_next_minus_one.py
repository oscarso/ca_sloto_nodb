"""
range_oso_next_minus_one.py — Accuracy test for range_oso_next (consolidated).

Excludes the last draw from the dataset, predicts it (including the
predicted range), then compares the prediction against the actual result.
"""

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_csv, write_temp_csv

sys.path.insert(0, str(Path(__file__).parent))
from range_oso_next import range_oso_next


def range_oso_next_minus_one(csv_path: Path = None) -> None:
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )

    csv_path = Path(csv_path)
    all_rows, header, delimiter = load_csv(csv_path)

    if len(all_rows) < 2:
        print("Not enough data to compare.")
        return

    actual_last = all_rows[-1]
    actual_min = min(actual_last[1:6])
    actual_max = max(actual_last[1:6])

    # Write temp CSV without the last row
    temp_path = write_temp_csv(
        csv_path, all_rows[:-1], header, delimiter, suffix="_range_oso_temp"
    )

    # Silently predict on the reduced dataset
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    predicted = range_oso_next(
        temp_path,
        run_accuracy_test=False,
    )
    sys.stdout = old_stdout

    temp_path.unlink()

    range_min, range_max = predicted.get("_range", (None, None))

    # Report results
    print(f"Actual last draw (Draw {actual_last[0]}):")
    for i in range(1, 6):
        print(f"  Column {i}: {actual_last[i]}")
    print(f"  Mega: {actual_last[6]}")
    print(f"  Actual range: {actual_min}-{actual_max}")

    print(f"\nPredicted range: {range_min}-{range_max}")
    range_hit = (
        range_min is not None
        and range_max is not None
        and range_min <= actual_min
        and actual_max <= range_max
    )
    print(f"Range containment: {'HIT (actual draw fully within predicted range)' if range_hit else 'MISS'}")

    print(f"\nPredicted draw:")
    for col in range(1, 6):
        val = predicted.get(col)
        mark = " <--" if val == actual_last[col] else ""
        print(f"  Column {col}: {val}{mark}")
    mega = predicted.get(6)
    print(f"  Mega: {mega}{' <--' if mega == actual_last[6] else ''}")

    correct = sum(1 for col in range(1, 6) if predicted.get(col) == actual_last[col])
    total = sum(1 for col in range(1, 6) if predicted.get(col) is not None)
    accuracy = correct / total * 100 if total > 0 else 0
    print(f"\n[range_oso_next] Main numbers accuracy: {correct}/{total} correct ({accuracy:.1f}%)")

    # Structural "hit" count: predicted mains that appear anywhere in the
    # actual draw (order-independent) — a fairer measure for a sorted draw.
    actual_set = {actual_last[i] for i in range(1, 6)}
    pred_set = {predicted.get(col) for col in range(1, 6)}
    set_hits = len(actual_set & pred_set)
    print(f"Set overlap (order-independent): {set_hits}/5 main numbers matched")

    if mega is not None and mega == actual_last[6]:
        print(f"Mega prediction: CORRECT ({mega})")
    elif mega is not None:
        print(f"Mega prediction: WRONG (predicted {mega}, actual {actual_last[6]})")
    else:
        print(f"Mega prediction: None (actual was {actual_last[6]})")

    return correct, total


if __name__ == "__main__":
    _csv = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    range_oso_next_minus_one(_csv)
