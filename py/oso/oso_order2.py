import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows


def order2(csv_path: Path = None, top_n: int = None):
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    p = Path(csv_path)
    rows: List[List[int]] = load_rows(p)

    # Vertical 2-row patterns (same column)
    patterns: List[Tuple[int, int]] = []
    for col in range(1, 6):
        for i in range(len(rows) - 1):
            patterns.append((rows[i][col], rows[i + 1][col]))

    # Cross-column patterns (all column combinations across 2 consecutive rows)
    cross_patterns: List[Tuple[int, int]] = []
    for i in range(len(rows) - 1):
        for col_a in range(1, 6):
            for col_b in range(1, 6):
                cross_patterns.append((rows[i][col_a], rows[i + 1][col_b]))

    freq = Counter(patterns)
    cross_freq = Counter(cross_patterns)

    combined: Dict[Tuple, int] = {}
    for pat, count in freq.items():
        combined[pat] = combined.get(pat, 0) + count
    for pat, count in cross_freq.items():
        combined[pat] = combined.get(pat, 0) + count

    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print("=== PATTERNS (merged vertical + cross-column) ===")
    sorted_items = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)
    if top_n is not None:
        unique_freqs = sorted(set(combined.values()), reverse=True)
        thresholds = set(unique_freqs[:top_n])
        sorted_items = [(p, c) for p, c in sorted_items if c in thresholds]
    for pat, count in sorted_items:
        print(f"{pat}={count}")

    return freq, cross_freq


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    order2(csv_path, top_n)
