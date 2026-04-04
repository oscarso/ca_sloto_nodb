import csv
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple, Dict


def order3next(csv_path: Path = None) -> Dict[int, int]:
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    rows: List[List[int]] = []
    p = Path(csv_path)

    with p.open("r", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if ";" in sample and "," not in sample else ","
        reader = csv.reader(f, delimiter=delimiter)
        for raw in reader:
            if not raw:
                continue
            if raw[0].strip().lower() == "draw_num":
                continue
            rows.append([int(x) for x in raw[:7]])

    # Build 3-row patterns and track the next value (4th row) for each pattern
    pattern_to_next: Counter = Counter()
    for col in range(1, 6):  # columns 2-6
        for i in range(len(rows) - 3):
            a, b, c = rows[i][col], rows[i+1][col], rows[i+2][col]
            nxt = rows[i+3][col]
            pattern_to_next[(a, b, c, nxt)] += 1

    # For each 3-value pattern, find the most common next value
    prediction: Dict[int, int] = {}
    for (a, b, c, nxt), cnt in pattern_to_next.items():
        key = (a, b, c)
        if key not in prediction or pattern_to_next[(a, b, c, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 3 rows to predict the next row (columns 2-6)
    if len(rows) < 3:
        print("Not enough data to predict.")
        return {}
    last_three = rows[-3:]
    next_pred = {}
    for col in range(1, 6):
        pattern = (last_three[0][col], last_three[1][col], last_three[2][col])
        next_pred[col] = prediction.get(pattern, None)

    print("Prediction for next draw (columns 2-6):")
    for col_idx, val in next_pred.items():
        print(f"Column {col_idx+1}: {val}")

    return next_pred


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    order3next(csv_path)
