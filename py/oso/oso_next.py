import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

# Add py/ root to path so utils is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, pattern_fallback, resolve_duplicates

# Import order scripts (for frequency display only)
sys.path.insert(0, str(Path(__file__).parent))
from oso_order2 import order2
from oso_order3 import order3
from oso_order4 import order4
from oso_order5 import order5
from oso_order_m2 import order_m2
from oso_order_m3 import order_m3
from oso_order_m4 import order_m4
from oso_order_m5 import order_m5


def oso_next(csv_path: Path = None, top_n: int = None, run_accuracy_test: bool = True) -> Dict[int, int]:
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None

    p = Path(csv_path)
    rows: List[List[int]] = load_rows(p)

    # ------------------------------------------------------------------
    # Build 4-row patterns → predict via the "disappear" heuristic
    # ------------------------------------------------------------------
    pattern_to_next: Counter = Counter()
    for col in range(1, 6):
        for i in range(len(rows) - 4):
            a, b, c, d = rows[i][col], rows[i+1][col], rows[i+2][col], rows[i+3][col]
            nxt = rows[i+4][col]
            pattern_to_next[(a, b, c, d, nxt)] += 1

    prediction_4: Dict[Tuple, int] = {}
    for (a, b, c, d, nxt), cnt in pattern_to_next.items():
        key = (a, b, c, d)
        if key not in prediction_4 or pattern_to_next[(a, b, c, d, prediction_4[key])] < cnt:
            prediction_4[key] = nxt

    if len(rows) < 4:
        print("Not enough data to predict.")
        return {}

    last_four = rows[-4:]

    # Track source of each prediction
    source = {col: None for col in range(1, 7)}

    # Full 4-row pattern prediction
    pred_full = {}
    for col in range(1, 6):
        pattern = (last_four[0][col], last_four[1][col], last_four[2][col], last_four[3][col])
        pred_full[col] = prediction_4.get(pattern)

    # "Disappear" the 4th row: use 3-row pattern → 4th-row mapping
    pred_disappear = {}
    for col in range(1, 6):
        three_to_four: Counter = Counter()
        for i in range(len(rows) - 3):
            a, b, c = rows[i][col], rows[i+1][col], rows[i+2][col]
            fourth = rows[i+3][col]
            three_to_four[(a, b, c, fourth)] += 1

        cur_three = (last_four[-3][col], last_four[-2][col], last_four[-1][col])
        candidates = [(a, b, c, fourth) for (a, b, c, fourth) in three_to_four if (a, b, c) == cur_three]
        if candidates:
            most_common = max(candidates, key=lambda x: three_to_four[x])
            pred_disappear[col] = most_common[3]
            source[col] = f"3-row pattern {cur_three} (freq={three_to_four[most_common]})"
        else:
            pred_disappear[col] = None

    print("Prediction using full 4-row pattern:")
    for col_idx, val in pred_full.items():
        print(f"  Column {col_idx+1}: {val}")

    print("\nPrediction after 'disappearing' 4th row (using 3-row -> 4th mapping):")
    for col_idx, val in pred_disappear.items():
        print(f"  Column {col_idx+1}: {val}")

    # ------------------------------------------------------------------
    # Fallback chain: order5 → order4 → order3 → order2
    # All 8 original *_fallback() functions replaced by pattern_fallback()
    # ------------------------------------------------------------------
    print("\n--- order5 fallback ---")
    freq5, _ = order5(p, top_n)
    fallback5 = pattern_fallback(rows, 5)

    stage1 = {}
    print("\nStage 1 (order5 fallback for None values):")
    for col, val in pred_disappear.items():
        if val is None and fallback5.get(col) is not None:
            stage1[col] = fallback5[col]
            source[col] = "order5 fallback (5-row pattern)"
            print(f"  Column {col+1}: {stage1[col]} (from order5 fallback)")
        else:
            stage1[col] = val
            print(f"  Column {col+1}: {val}")

    print("\n--- order4 fallback ---")
    freq4, _ = order4(p, top_n)
    fallback4 = pattern_fallback(rows, 4)

    stage2 = {}
    print("\nStage 2 (order4 fallback for remaining None values):")
    for col, val in stage1.items():
        if val is None and fallback4.get(col) is not None:
            stage2[col] = fallback4[col]
            source[col] = "order4 fallback (4-row pattern)"
            print(f"  Column {col+1}: {stage2[col]} (from order4 fallback)")
        else:
            stage2[col] = val
            print(f"  Column {col+1}: {val}")

    print("\n--- order3 fallback ---")
    freq3, _ = order3(p, top_n)
    fallback3 = pattern_fallback(rows, 3)

    stage3 = {}
    print("\nStage 3 (order3 fallback for remaining None values):")
    for col, val in stage2.items():
        if val is None and fallback3.get(col) is not None:
            stage3[col] = fallback3[col]
            source[col] = "order3 fallback (3-row pattern)"
            print(f"  Column {col+1}: {stage3[col]} (from order3 fallback)")
        else:
            stage3[col] = val
            print(f"  Column {col+1}: {val}")

    print("\n--- order2 fallback ---")
    freq2, _ = order2(p, top_n)
    fallback2 = pattern_fallback(rows, 2)

    final_prediction = {}
    print("\nFinal prediction (order2 fallback for remaining None values):")
    for col, val in stage3.items():
        if val is None and fallback2.get(col) is not None:
            final_prediction[col] = fallback2[col]
            source[col] = "order2 fallback (2-row pattern)"
            print(f"  Column {col+1}: {final_prediction[col]} (from order2 fallback)")
        else:
            final_prediction[col] = val
            print(f"  Column {col+1}: {val}")

    # ------------------------------------------------------------------
    # Mega number fallback chain: order_m5 → order_m4 → order_m3 → order_m2
    # ------------------------------------------------------------------
    print("\n--- order_m5 fallback ---")
    freq_m5 = order_m5(p, top_n)
    mega_pred = pattern_fallback(rows, 5, col_range=[6]).get(6)
    if mega_pred is not None:
        source[6] = "order_m5 (5-row mega pattern)"
        print(f"\nMega (Column 7): {mega_pred} (from order_m5)")
    else:
        print("\n--- order_m4 fallback ---")
        freq_m4 = order_m4(p, top_n)
        mega_pred = pattern_fallback(rows, 4, col_range=[6]).get(6)
        if mega_pred is not None:
            source[6] = "order_m4 fallback (4-row mega pattern)"
            print(f"\nMega (Column 7): {mega_pred} (from order_m4 fallback)")
        else:
            print("\n--- order_m3 fallback ---")
            freq_m3 = order_m3(p, top_n)
            mega_pred = pattern_fallback(rows, 3, col_range=[6]).get(6)
            if mega_pred is not None:
                source[6] = "order_m3 fallback (3-row mega pattern)"
                print(f"\nMega (Column 7): {mega_pred} (from order_m3 fallback)")
            else:
                print("\n--- order_m2 fallback ---")
                freq_m2 = order_m2(p, top_n)
                mega_pred = pattern_fallback(rows, 2, col_range=[6]).get(6)
                source[6] = "order_m2 fallback (2-row mega pattern)"
                print(f"\nMega (Column 7): {mega_pred} (from order_m2 fallback)")

    final_prediction[6] = mega_pred

    # ------------------------------------------------------------------
    # Duplicate resolution (columns 1-5 must be unique)
    # ------------------------------------------------------------------
    print("\n--- Duplicate Resolution ---")
    col_candidates: Dict[int, List[int]] = {}
    for col in range(1, 6):
        col_freq: Counter = Counter(row[col] for row in rows)
        col_candidates[col] = [val for val, _ in col_freq.most_common()]

    final_prediction = resolve_duplicates(final_prediction, col_candidates)

    # Fill source for columns that came from the full 4-row path
    for col in range(1, 6):
        if source[col] is None and final_prediction.get(col) is not None:
            source[col] = "4-row pattern (via disappear-3-row heuristic)"

    # ------------------------------------------------------------------
    # Weak-signal detection
    # ------------------------------------------------------------------
    order2_count = sum(1 for col in range(1, 6) if source[col] and "order2" in source[col])
    is_weak = order2_count >= 3
    final_prediction["_source"] = dict(source)
    final_prediction["_weak"] = is_weak

    print("\n" + "=" * 50)
    print("OSO_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {final_prediction[col]}  <- {source[col]}")
    print(f"  Mega:     {final_prediction[6]}  <- {source[6]}")
    if is_weak:
        print(f"\n  [!] WEAK SIGNAL: {order2_count}/5 columns from order2 fallback")
        print(f"      (oso_next will be suppressed from the comparison table)")
    print("=" * 50)

    # Optional top-N pattern display
    if top_n is not None:
        print("\n" + "=" * 50)
        print(f"PREDICTION BASED ON TOP {top_n} PATTERN GROUPS")
        print("=" * 50)
        for col in range(1, 6):
            pred_val = final_prediction.get(col, "N/A")
            print(f"  Column {col}: {pred_val}")
        print(f"  Mega: {final_prediction[6]}")
        print("=" * 50)

    # Optional accuracy test
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("OSO_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from oso_next_minus_one import oso_next_minus_one
        oso_next_minus_one(csv_path)
        print("=" * 50)

    return final_prediction


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print("\n" + "=" * 50)
    print("OSO_NEXT: Forward Prediction")
    print("=" * 50)
    oso_next(csv_path, top_n)

    print("\n" + "=" * 50)
    print("OSO_NEXT_MINUS_ONE: Accuracy Test")
    print("=" * 50)
    from oso_next_minus_one import oso_next_minus_one
    oso_next_minus_one(csv_path)
    print("=" * 50)
