import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set


def load_data(csv_path: Path) -> Tuple[List[List[int]], str]:
    """Load CSV data and return rows with delimiter"""
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
    return rows, delimiter


def frequency_analysis(rows: List[List[int]], column: int, top_n: int = 10) -> List[Tuple[int, int]]:
    """
    Analyze frequency of numbers in a specific column.
    Returns list of (number, count) tuples sorted by frequency.
    """
    counter = Counter()
    for row in rows:
        counter[row[column]] += 1
    return counter.most_common(top_n)


def gap_analysis(rows: List[List[int]], column: int) -> Dict[int, int]:
    """
    Analyze how many draws since each number last appeared.
    Returns dict of {number: draws_since_last_seen}
    """
    last_seen: Dict[int, int] = {}
    gap_since: Dict[int, int] = {}
    
    for idx, row in enumerate(rows):
        num = row[column]
        if num in last_seen:
            gap_since[num] = idx - last_seen[num]
        last_seen[num] = idx
    
    # For numbers not in gap_since, calculate from their last appearance to end
    total_rows = len(rows)
    for num, last_idx in last_seen.items():
        if num not in gap_since:
            gap_since[num] = total_rows - last_idx
    
    return gap_since


def markov_transitions(rows: List[List[int]], column: int) -> Dict[int, Counter]:
    """
    Build Markov chain transitions: given number X, what's likely to come next?
    Returns dict of {number: Counter of next_numbers}
    """
    transitions: Dict[int, Counter] = defaultdict(Counter)
    
    for i in range(len(rows) - 1):
        current = rows[i][column]
        next_num = rows[i + 1][column]
        transitions[current][next_num] += 1
    
    return transitions


def positional_bias(rows: List[List[int]], column: int) -> Dict[int, float]:
    """
    Calculate position bias - numbers that appear more frequently in this column.
    Returns normalized scores (0-1 scale)
    """
    counter = Counter()
    for row in rows:
        counter[row[column]] += 1
    
    max_count = max(counter.values()) if counter else 1
    return {num: count / max_count for num, count in counter.items()}


def ensemble_score(
    rows: List[List[int]],
    column: int,
    candidate: int,
    last_value: int,
    gap_data: Dict[int, int],
    transition_data: Dict[int, Counter],
    freq_data: List[Tuple[int, int]],
    bias_data: Dict[int, float]
) -> float:
    """
    Calculate ensemble score for a candidate number.
    Combines multiple weak signals into a single score.
    """
    score = 0.0
    
    # 1. Frequency component (weight: 0.3)
    freq_dict = {num: count for num, count in freq_data}
    max_freq = max(freq_dict.values()) if freq_dict else 1
    freq_score = freq_dict.get(candidate, 0) / max_freq
    score += 0.3 * freq_score
    
    # 2. Gap analysis component (weight: 0.25)
    # Numbers with moderate gaps are more interesting than very recent or very old
    gap = gap_data.get(candidate, len(rows))
    avg_gap = sum(gap_data.values()) / len(gap_data) if gap_data else len(rows)
    # Prefer numbers that are "due" but not too overdue
    gap_score = 1.0 - min(abs(gap - avg_gap) / (avg_gap * 2), 1.0)
    score += 0.25 * gap_score
    
    # 3. Markov transition component (weight: 0.3)
    if last_value in transition_data and candidate in transition_data[last_value]:
        total_transitions = sum(transition_data[last_value].values())
        trans_score = transition_data[last_value][candidate] / total_transitions
        score += 0.3 * trans_score
    
    # 4. Positional bias component (weight: 0.15)
    score += 0.15 * bias_data.get(candidate, 0)
    
    return score


def kimi_next(csv_path: Path = None, run_accuracy_test: bool = True) -> Dict[int, int]:
    """
    Predict next draw using ensemble of frequency, gap, Markov, and positional analysis.
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    
    rows, _ = load_data(csv_path)
    
    if len(rows) < 5:
        print("Not enough data to analyze.")
        return {}
    
    predictions = {}
    
    print("=" * 50)
    print("KIMI NEXT - Ensemble Prediction Algorithm")
    print("=" * 50)
    
    # Analyze main numbers (columns 1-5, indices 1-5)
    for col in range(1, 6):
        print(f"\n[Column {col} Analysis]")
        
        # Gather all historical numbers for this column
        all_numbers = set(row[col] for row in rows)
        last_value = rows[-1][col]
        
        # Build analysis data
        freq_data = frequency_analysis(rows, col, top_n=20)
        gap_data = gap_analysis(rows, col)
        transition_data = markov_transitions(rows, col)
        bias_data = positional_bias(rows, col)
        
        print(f"  Last value: {last_value}")
        print(f"  Top frequencies: {freq_data[:5]}")
        
        # Score all possible candidates
        candidates = list(range(1, 48))  # Assuming ca_sloto numbers 1-47
        scores = []
        
        for candidate in candidates:
            score = ensemble_score(
                rows, col, candidate, last_value,
                gap_data, transition_data, freq_data, bias_data
            )
            scores.append((candidate, score))
        
        # Sort by score and pick top
        scores.sort(key=lambda x: x[1], reverse=True)
        best_candidate = scores[0][0]
        best_score = scores[0][1]
        
        predictions[col] = best_candidate
        
        print(f"  Top 5 candidates: {scores[:5]}")
        print(f"  -> PREDICTED: {best_candidate} (score: {best_score:.3f})")
    
    # Analyze mega number (column 7, index 6)
    print(f"\n[Mega Number Analysis]")
    
    all_mega = set(row[6] for row in rows)
    last_mega = rows[-1][6]
    
    freq_data_mega = frequency_analysis(rows, 6, top_n=10)
    gap_data_mega = gap_analysis(rows, 6)
    transition_data_mega = markov_transitions(rows, 6)
    bias_data_mega = positional_bias(rows, 6)
    
    print(f"  Last mega: {last_mega}")
    print(f"  Top frequencies: {freq_data_mega[:5]}")
    
    # Mega numbers might have different range (e.g., 1-27)
    mega_candidates = list(range(1, 28))  # Adjust if needed
    mega_scores = []
    
    for candidate in mega_candidates:
        score = ensemble_score(
            rows, 6, candidate, last_mega,
            gap_data_mega, transition_data_mega, freq_data_mega, bias_data_mega
        )
        mega_scores.append((candidate, score))
    
    mega_scores.sort(key=lambda x: x[1], reverse=True)
    best_mega = mega_scores[0][0]
    best_mega_score = mega_scores[0][1]
    
    predictions[6] = best_mega
    
    print(f"  Top 5 candidates: {mega_scores[:5]}")
    print(f"  -> PREDICTED: {best_mega} (score: {best_mega_score:.3f})")
    
    # Final summary
    print("\n" + "=" * 50)
    print("FINAL PREDICTION")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}")
    print(f"  Mega: {predictions[6]}")
    print("=" * 50)
    
    # Run accuracy test (minus_one) only if not called from minus_one
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("KIMI_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        # Import here to avoid circular import issues
        sys.path.insert(0, str(Path(__file__).parent))
        from kimi_next_minus_one import kimi_next_minus_one
        kimi_next_minus_one(csv_path)
        print("=" * 50)
    
    return predictions


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    
    # Run main prediction (will also trigger accuracy test)
    print("\n" + "=" * 50)
    print("KIMI_NEXT: Forward Prediction")
    print("=" * 50)
    kimi_next(csv_path, run_accuracy_test=False)
