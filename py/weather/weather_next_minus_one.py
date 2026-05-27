import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_csv, write_temp_csv

sys.path.insert(0, str(Path(__file__).parent))
from weather_next import weather_next


def weather_next_minus_one(csv_path: Path = None) -> None:
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )

    all_rows, header, delimiter = load_csv(Path(csv_path))

    if len(all_rows) < 2:
        print("Not enough data to compare.")
        return

    actual_last = all_rows[-1]

    temp_path = write_temp_csv(Path(csv_path), all_rows[:-1], header, delimiter, suffix="_weather_temp")

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    predicted = weather_next(temp_path, run_accuracy_test=False)
    sys.stdout = old_stdout

    temp_path.unlink()

    print(f"Actual last draw (Draw {actual_last[0]}):")
    for i in range(1, 6):
        print(f"  Column {i}: {actual_last[i]}")
    print(f"  Mega: {actual_last[6]}")

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
    print(f"\nMain numbers accuracy: {correct}/{total} correct ({accuracy:.1f}%)")

    if mega is not None and mega == actual_last[6]:
        print(f"Mega prediction: CORRECT ({mega})")
    elif mega is not None:
        print(f"Mega prediction: WRONG (predicted {mega}, actual {actual_last[6]})")
    else:
        print(f"Mega prediction: None (actual was {actual_last[6]})")


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    weather_next_minus_one(csv_path)
