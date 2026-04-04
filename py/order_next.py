import csv
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple, Dict


def order3_fallback(csv_path: Path) -> Dict[int, int]:
    """Get order3 predictions as fallback for None values"""
    rows: List[List[int]] = []
    with csv_path.open("r", newline="") as f:
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
    prediction: Dict[Tuple[int, int, int], int] = {}
    for (a, b, c, nxt), cnt in pattern_to_next.items():
        key = (a, b, c)
        if key not in prediction or pattern_to_next[(a, b, c, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 3 rows to predict the next row
    if len(rows) < 3:
        return {}
    last_three = rows[-3:]
    fallback = {}
    for col in range(1, 6):
        pattern = (last_three[0][col], last_three[1][col], last_three[2][col])
        fallback[col] = prediction.get(pattern, None)
    
    return fallback


def order_next(csv_path: Path = None) -> Dict[int, int]:
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

    # Use the last 4 rows to predict the next row, then "disappear" the 4th row
    if len(rows) < 4:
        print("Not enough data to predict.")
        return {}
    last_four = rows[-4:]

    # First predict using the full 4-row pattern
    pred_full = {}
    for col in range(1, 6):
        pattern = (last_four[0][col], last_four[1][col], last_four[2][col], last_four[3][col])
        pred_full[col] = prediction.get(pattern, None)

    # Now "disappear" the 4th row and predict using only first 3 rows
    # by looking for 3-row patterns that led to the 4th row's value
    pred_disappear = {}
    for col in range(1, 6):
        # Look for 3-row patterns that were followed by the 4th row's value
        three_to_four: Counter = Counter()
        for i in range(len(rows) - 3):
            a, b, c = rows[i][col], rows[i+1][col], rows[i+2][col]
            fourth = rows[i+3][col]
            three_to_four[(a, b, c, fourth)] += 1

        # Find the most common fourth value for the current 3-row pattern
        cur_three = (last_four[-3][col], last_four[-2][col], last_four[-1][col])
        candidates = [(a, b, c, fourth) for (a, b, c, fourth) in three_to_four if (a, b, c) == cur_three]
        if candidates:
            # Choose the most common fourth value
            most_common = max(candidates, key=lambda x: three_to_four[x])
            pred_disappear[col] = most_common[3]
        else:
            pred_disappear[col] = None

    print("Prediction using full 4-row pattern:")
    for col_idx, val in pred_full.items():
        print(f"Column {col_idx+1}: {val}")

    print("\nPrediction after 'disappearing' 4th row (using 3-row -> 4th mapping):")
    for col_idx, val in pred_disappear.items():
        print(f"Column {col_idx+1}: {val}")

    # Fill None values with order3 fallback predictions
    fallback = order3_fallback(p)
    final_prediction = {}
    print("\nFinal prediction (with order3 fallback for None values):")
    for col_idx, val in pred_disappear.items():
        if val is None and fallback.get(col_idx) is not None:
            final_prediction[col_idx] = fallback[col_idx]
            print(f"Column {col_idx+1}: {final_prediction[col_idx]} (from order3 fallback)")
        else:
            final_prediction[col_idx] = val
            print(f"Column {col_idx+1}: {val}")

    return final_prediction


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    order_next(csv_path)
