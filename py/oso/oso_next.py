import csv
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple, Dict

# Import order scripts
sys.path.insert(0, str(Path(__file__).parent))
from oso_order2 import order2
from oso_order3 import order3
from oso_order4 import order4
from oso_order5 import order5
from oso_order_m2 import order_m2
from oso_order_m3 import order_m3
from oso_order_m4 import order_m4
from oso_order_m5 import order_m5


def order_m5_fallback(csv_path: Path) -> int:
    """Get order_m5 prediction for mega number (column 7) as primary"""
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

    # Build 5-row patterns for mega column (index 6) and track the next value (6th row)
    pattern_to_next: Counter = Counter()
    col = 6  # mega column
    for i in range(len(rows) - 5):
        a, b, c, d, e = rows[i][col], rows[i+1][col], rows[i+2][col], rows[i+3][col], rows[i+4][col]
        nxt = rows[i+5][col]
        pattern_to_next[(a, b, c, d, e, nxt)] += 1

    # For each 5-value pattern, find the most common next value
    prediction: Dict[Tuple[int, int, int, int, int], int] = {}
    for (a, b, c, d, e, nxt), cnt in pattern_to_next.items():
        key = (a, b, c, d, e)
        if key not in prediction or pattern_to_next[(a, b, c, d, e, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 5 rows to predict the next mega
    if len(rows) < 5:
        return None
    last_five = rows[-5:]
    pattern = (last_five[0][col], last_five[1][col], last_five[2][col], last_five[3][col], last_five[4][col])
    return prediction.get(pattern, None)


def order_m4_fallback(csv_path: Path) -> int:
    """Get order_m4 prediction for mega number (column 7)"""
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

    # Build 4-row patterns for mega column (index 6) and track the next value (5th row)
    pattern_to_next: Counter = Counter()
    col = 6  # mega column
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

    # Use the last 4 rows to predict the next mega
    if len(rows) < 4:
        return None
    last_four = rows[-4:]
    pattern = (last_four[0][col], last_four[1][col], last_four[2][col], last_four[3][col])
    return prediction.get(pattern, None)


def order_m3_fallback(csv_path: Path) -> int:
    """Get order_m3 prediction for mega number (column 7) as fallback"""
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

    # Build 3-row patterns for mega column (index 6) and track the next value (4th row)
    pattern_to_next: Counter = Counter()
    col = 6  # mega column
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

    # Use the last 3 rows to predict the next mega
    if len(rows) < 3:
        return None
    last_three = rows[-3:]
    pattern = (last_three[0][col], last_three[1][col], last_three[2][col])
    return prediction.get(pattern, None)


def order_m2_fallback(csv_path: Path) -> int:
    """Get order_m2 prediction for mega number (column 7) as final fallback"""
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

    # Build 2-row patterns for mega column (index 6) and track the next value (3rd row)
    pattern_to_next: Counter = Counter()
    col = 6  # mega column
    for i in range(len(rows) - 2):
        a, b = rows[i][col], rows[i+1][col]
        nxt = rows[i+2][col]
        pattern_to_next[(a, b, nxt)] += 1

    # For each 2-value pattern, find the most common next value
    prediction: Dict[Tuple[int, int], int] = {}
    for (a, b, nxt), cnt in pattern_to_next.items():
        key = (a, b)
        if key not in prediction or pattern_to_next[(a, b, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 2 rows to predict the next mega
    if len(rows) < 2:
        return None
    last_two = rows[-2:]
    pattern = (last_two[0][col], last_two[1][col])
    return prediction.get(pattern, None)


def order2_fallback(csv_path: Path) -> Dict[int, int]:
    """Get order2 predictions as final fallback for None values"""
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

    # Build 2-row patterns and track the next value (3rd row) for each pattern
    pattern_to_next: Counter = Counter()
    for col in range(1, 6):  # columns 2-6
        for i in range(len(rows) - 2):
            a, b = rows[i][col], rows[i+1][col]
            nxt = rows[i+2][col]
            pattern_to_next[(a, b, nxt)] += 1

    # For each 2-value pattern, find the most common next value
    prediction: Dict[Tuple[int, int], int] = {}
    for (a, b, nxt), cnt in pattern_to_next.items():
        key = (a, b)
        if key not in prediction or pattern_to_next[(a, b, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 2 rows to predict the next row
    if len(rows) < 2:
        return {}
    last_two = rows[-2:]
    fallback = {}
    for col in range(1, 6):
        pattern = (last_two[0][col], last_two[1][col])
        fallback[col] = prediction.get(pattern, None)
    
    return fallback


def order5_fallback(csv_path: Path) -> Dict[int, int]:
    """Get order5 predictions as primary fallback for None values"""
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

    # Build 5-row patterns and track the next value (6th row) for each pattern
    pattern_to_next: Counter = Counter()
    for col in range(1, 6):  # columns 2-6
        for i in range(len(rows) - 5):
            a, b, c, d, e = rows[i][col], rows[i+1][col], rows[i+2][col], rows[i+3][col], rows[i+4][col]
            nxt = rows[i+5][col]
            pattern_to_next[(a, b, c, d, e, nxt)] += 1

    # For each 5-value pattern, find the most common next value
    prediction: Dict[Tuple[int, int, int, int, int], int] = {}
    for (a, b, c, d, e, nxt), cnt in pattern_to_next.items():
        key = (a, b, c, d, e)
        if key not in prediction or pattern_to_next[(a, b, c, d, e, prediction[key])] < cnt:
            prediction[key] = nxt

    # Use the last 5 rows to predict the next row
    if len(rows) < 5:
        return {}
    last_five = rows[-5:]
    fallback = {}
    for col in range(1, 6):
        pattern = (last_five[0][col], last_five[1][col], last_five[2][col], last_five[3][col], last_five[4][col])
        fallback[col] = prediction.get(pattern, None)
    
    return fallback


def order4_fallback(csv_path: Path) -> Dict[int, int]:
    """Get order4 predictions as secondary fallback for None values"""
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

    # Use the last 4 rows to predict the next row
    if len(rows) < 4:
        return {}
    last_four = rows[-4:]
    fallback = {}
    for col in range(1, 6):
        pattern = (last_four[0][col], last_four[1][col], last_four[2][col], last_four[3][col])
        fallback[col] = prediction.get(pattern, None)
    
    return fallback


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


def oso_next(csv_path: Path = None, top_n: int = None, run_accuracy_test: bool = True) -> Dict[int, int]:
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    if top_n is None:
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
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

    # Fill None values with order5 fallback predictions
    print("\n--- order5 fallback ---")
    freq5, _ = order5(p, top_n)
    fallback5 = order5_fallback(p)
    stage1_prediction = {}
    print("\nStage 1 prediction (with order5 fallback for None values):")
    for col_idx, val in pred_disappear.items():
        if val is None and fallback5.get(col_idx) is not None:
            stage1_prediction[col_idx] = fallback5[col_idx]
            print(f"Column {col_idx+1}: {stage1_prediction[col_idx]} (from order5 fallback)")
        else:
            stage1_prediction[col_idx] = val
            print(f"Column {col_idx+1}: {val}")

    # Fill remaining None values with order4 fallback predictions
    print("\n--- order4 fallback ---")
    freq4, _ = order4(p, top_n)
    fallback4 = order4_fallback(p)
    stage2_prediction = {}
    print("\nStage 2 prediction (with order4 fallback for remaining None values):")
    for col_idx, val in stage1_prediction.items():
        if val is None and fallback4.get(col_idx) is not None:
            stage2_prediction[col_idx] = fallback4[col_idx]
            print(f"Column {col_idx+1}: {stage2_prediction[col_idx]} (from order4 fallback)")
        else:
            stage2_prediction[col_idx] = val
            print(f"Column {col_idx+1}: {val}")

    # Fill remaining None values with order3 fallback predictions
    print("\n--- order3 fallback ---")
    freq3, _ = order3(p, top_n)
    fallback3 = order3_fallback(p)
    stage3_prediction = {}
    print("\nStage 3 prediction (with order3 fallback for remaining None values):")
    for col_idx, val in stage2_prediction.items():
        if val is None and fallback3.get(col_idx) is not None:
            stage3_prediction[col_idx] = fallback3[col_idx]
            print(f"Column {col_idx+1}: {stage3_prediction[col_idx]} (from order3 fallback)")
        else:
            stage3_prediction[col_idx] = val
            print(f"Column {col_idx+1}: {val}")

    # Fill remaining None values with order2 fallback predictions
    print("\n--- order2 fallback ---")
    freq2, _ = order2(p, top_n)
    fallback2 = order2_fallback(p)
    final_prediction = {}
    print("\nFinal prediction (with order2 fallback for remaining None values):")
    for col_idx, val in stage3_prediction.items():
        if val is None and fallback2.get(col_idx) is not None:
            final_prediction[col_idx] = fallback2[col_idx]
            print(f"Column {col_idx+1}: {final_prediction[col_idx]} (from order2 fallback)")
        else:
            final_prediction[col_idx] = val
            print(f"Column {col_idx+1}: {val}")

    # Predict mega number using order_m5 -> order_m4 -> order_m3 -> order_m2 fallback chain
    print("\n--- order_m5 fallback ---")
    freq_m5 = order_m5(p, top_n)
    mega_pred = order_m5_fallback(p)
    if mega_pred is not None:
        print(f"\nMega (Column 7): {mega_pred} (from order_m5)")
    else:
        print("\n--- order_m4 fallback ---")
        freq_m4 = order_m4(p, top_n)
        mega_pred = order_m4_fallback(p)
        if mega_pred is not None:
            print(f"\nMega (Column 7): {mega_pred} (from order_m4 fallback)")
        else:
            print("\n--- order_m3 fallback ---")
            freq_m3 = order_m3(p, top_n)
            mega_pred = order_m3_fallback(p)
            if mega_pred is not None:
                print(f"\nMega (Column 7): {mega_pred} (from order_m3 fallback)")
            else:
                print("\n--- order_m2 fallback ---")
                freq_m2 = order_m2(p, top_n)
                mega_pred = order_m2_fallback(p)
                print(f"\nMega (Column 7): {mega_pred} (from order_m2 fallback)")
    final_prediction[6] = mega_pred

    print("\n" + "=" * 50)
    print("FINAL PREDICTION")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {final_prediction[col]}")
    print(f"  Mega: {final_prediction[6]}")
    print("=" * 50)

    # If top_n was specified, show prediction based on top patterns
    if top_n is not None:
        print("\n" + "=" * 50)
        print(f"PREDICTION BASED ON TOP {top_n} PATTERN GROUPS")
        print("=" * 50)
        
        # Show top patterns used for each column's prediction
        for col in range(1, 6):
            col_patterns = []
            # Check order5 patterns for this column
            for (a, b, c, d, e), cnt in freq5.items():
                if cnt >= min(sorted(set(freq5.values()), reverse=True)[:top_n] if freq5 else [0]):
                    # Pattern from top groups - check if it ends with predicted value
                    if final_prediction.get(col) is not None:
                        col_patterns.append(f"order5:{(a,b,c,d,e)}={cnt}")
            
            # Check order4 patterns
            for (a, b, c, d), cnt in freq4.items():
                if cnt >= min(sorted(set(freq4.values()), reverse=True)[:top_n] if freq4 else [0]):
                    if final_prediction.get(col) is not None:
                        col_patterns.append(f"order4:{(a,b,c,d)}={cnt}")
            
            # Check order3 patterns  
            for (a, b, c), cnt in freq3.items():
                if cnt >= min(sorted(set(freq3.values()), reverse=True)[:top_n] if freq3 else [0]):
                    if final_prediction.get(col) is not None:
                        col_patterns.append(f"order3:{(a,b,c)}={cnt}")
            
            # Check order2 patterns
            for (a, b), cnt in freq2.items():
                if cnt >= min(sorted(set(freq2.values()), reverse=True)[:top_n] if freq2 else [0]):
                    if final_prediction.get(col) is not None:
                        col_patterns.append(f"order2:{(a,b)}={cnt}")
            
            pred_val = final_prediction.get(col, "N/A")
            print(f"  Column {col}: {pred_val}")
            if col_patterns[:3]:  # Show up to 3 relevant patterns
                print(f"    Top patterns: {', '.join(col_patterns[:3])}")
        
        print(f"  Mega: {final_prediction[6]}")
        print("=" * 50)

    # Run accuracy test (minus_one) only if not called from minus_one
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("OSO_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        # Import here to avoid circular import issues
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from oso_next_minus_one import oso_next_minus_one
        oso_next_minus_one(csv_path)
        print("=" * 50)

    return final_prediction


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Run main prediction
    print("\n" + "=" * 50)
    print("OSO_NEXT: Forward Prediction")
    print("=" * 50)
    oso_next(csv_path, top_n)
    
    # Run accuracy test (minus_one)
    print("\n" + "=" * 50)
    print("OSO_NEXT_MINUS_ONE: Accuracy Test")
    print("=" * 50)
    # Import here to avoid circular import issues
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from oso_next_minus_one import oso_next_minus_one
    oso_next_minus_one(csv_path)
    print("=" * 50)
