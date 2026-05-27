import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows


def order5(csv_path: Path = None, top_n: int = None):
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    p = Path(csv_path)
    rows: List[List[int]] = load_rows(p)

    # Vertical 5-row patterns
    patterns: List[Tuple[int, int, int, int, int]] = []
    for col in range(1, 6):
        for i in range(len(rows) - 4):
            patterns.append((
                rows[i][col], rows[i + 1][col], rows[i + 2][col],
                rows[i + 3][col], rows[i + 4][col],
            ))

    # Cross-column patterns
    cross_patterns: List[Tuple] = []
    for i in range(len(rows) - 4):
        for col_a in range(1, 6):
            for col_b in range(1, 6):
                for col_c in range(1, 6):
                    for col_d in range(1, 6):
                        for col_e in range(1, 6):
                            cross_patterns.append((
                                rows[i][col_a], rows[i + 1][col_b], rows[i + 2][col_c],
                                rows[i + 3][col_d], rows[i + 4][col_e],
                            ))

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
    order5(csv_path, top_n)
