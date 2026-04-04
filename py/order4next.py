import csv
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple, Dict


def order4next(csv_path: Path = None) -> Dict[int, int]:
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

    # Build 4-row patterns and track the next value (5th row) for each pattern
    pattern_to_next: Counter = Counter()
    for col in range(1, 6):  # columns 2-6
        for i in range(len(rows) - 4):
            a, b, c, d = rows[i][col], rows[i+1][col], rows[i+2][col], rows[i+3][col]
            nxt = rows[i+4][col]
            pattern_to_next[(a, b, c, d, nxt)] += 1

    # For each 4-value pattern, find the most common next value
    prediction: Dict[Tuple[int, int, int, int], int] = {}
    for (a, b, c, d, nxt), cnt in pattern_to_next.items():
        key = (a, b, c, d)
        if key not in prediction or pattern_to_next[(a, b, c, d, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 4 rows to predict the next row (columns 2-6)
    if len(rows) < 4:
        print("Not enough data to predict.")
        return {}
    last_four = rows[-4:]
    next_pred = {}
    for col in range(1, 6):
        pattern = (last_four[0][col], last_four[1][col], last_four[2][col], last_four[3][col])
        next_pred[col] = prediction.get(pattern, None)

    print("Prediction for next draw (columns 2-6):")
    for col_idx, val in next_pred.items():
        print(f"Column {col_idx+1}: {val}")

    return next_pred


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    order4next(csv_path)
