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

    # Build cross-column permutation patterns: all combinations between row N and row N+1
    cross_patterns: List[Tuple[int, int]] = []
    for i in range(len(rows) - 1):
        for col_a in range(1, 6):  # all values in row i (columns 2-6)
            for col_b in range(1, 6):  # all values in row i+1 (columns 2-6)
                a = rows[i][col_a]
                b = rows[i+1][col_b]
                cross_patterns.append((a, b))

    freq = Counter(patterns)
    cross_freq = Counter(cross_patterns)

    # Combine both pattern types (no prefix distinction)
    combined: Dict[Tuple, int] = {}
    for pat, count in freq.items():
        combined[pat] = combined.get(pat, 0) + count
    for pat, count in cross_freq.items():
        combined[pat] = combined.get(pat, 0) + count

    # Determine how many results to show
    if top_n is None:
        # Try to read top_n from command line args
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None

    # Print combined patterns sorted by descending frequency
    print("=== PATTERNS (merged vertical + cross-column) ===")
    sorted_items = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)
    
    # Filter to top N frequency groups if requested
    if top_n is not None:
        # Get unique frequency values, sorted descending
        unique_freqs = sorted(set(combined.values()), reverse=True)
        # Take top N frequency thresholds
        freq_thresholds = unique_freqs[:top_n]
        # Filter items whose count is in the top N frequencies
        sorted_items = [(pat, cnt) for pat, cnt in sorted_items if cnt in freq_thresholds]
    
    for pat, count in sorted_items:
        print(f"{pat}={count}")

    return freq, cross_freq


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    order2(csv_path, top_n)
