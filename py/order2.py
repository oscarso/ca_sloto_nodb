import csv
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple


def order2(csv_path: Path = None, top_n: int = None) -> Counter:
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

    # Build 2-row patterns vertically: for each column 2-6, take the values from 2 consecutive rows
    patterns: List[Tuple[int, int]] = []
    for col in range(1, 6):  # columns 2-6 (indices 1-5)
        for i in range(len(rows) - 1):
            a = rows[i][col]
            b = rows[i+1][col]
            patterns.append((a, b))

    freq = Counter(patterns)

    # Determine how many results to show
    if top_n is None:
        # Try to read top_n from command line args
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None

    # Print patterns sorted by descending frequency
    sorted_items = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    if top_n is not None:
        sorted_items = sorted_items[:top_n]
    for pat, count in sorted_items:
        print(f"{pat}={count}")

    return freq


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    order2(csv_path, top_n)
