import sys
from collections import Counter
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows


def order_m3(csv_path: Path = None, top_n: int = None):
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    rows: List[List[int]] = load_rows(Path(csv_path))

    col = 6  # mega column
    patterns: List[Tuple[int, int, int]] = [
        (rows[i][col], rows[i + 1][col], rows[i + 2][col])
        for i in range(len(rows) - 2)
    ]
    freq = Counter(patterns)

    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None

    sorted_items = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    if top_n is not None:
        sorted_items = sorted_items[:top_n]
    for pat, count in sorted_items:
        print(f"{pat}={count}")

    return freq


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    order_m3(csv_path, top_n)
