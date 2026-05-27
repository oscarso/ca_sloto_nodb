import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, resolve_duplicates


def frequency_analysis(rows: List[List[int]], column: int, top_n: int = 10) -> List[Tuple[int, int]]:
    """Frequency of numbers in a specific column. Returns (number, count) sorted by freq."""
    counter: Counter = Counter(row[column] for row in rows)
    return counter.most_common(top_n)


def gap_analysis(rows: List[List[int]], column: int) -> Dict[int, int]:
    """How many draws since each number last appeared."""
    last_seen: Dict[int, int] = {}
    gap_since: Dict[int, int] = {}

    for idx, row in enumerate(rows):
        num = row[column]
        if num in last_seen:
            gap_since[num] = idx - last_seen[num]
        last_seen[num] = idx

    total_rows = len(rows)
    for num, last_idx in last_seen.items():
        if num not in gap_since:
            gap_since[num] = total_rows - last_idx

    return gap_since


def markov_transitions(rows: List[List[int]], column: int) -> Dict[int, Counter]:
    """Markov chain: given number X, what's likely to come next?"""
    transitions: Dict[int, Counter] = defaultdict(Counter)
    for i in range(len(rows) - 1):
        transitions[rows[i][column]][rows[i + 1][column]] += 1
    return transitions


def positional_bias(rows: List[List[int]], column: int) -> Dict[int, float]:
    """Normalized position bias scores (0-1 scale)."""
    counter: Counter = Counter(row[column] for row in rows)
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
    bias_data: Dict[int, float],
) -> Tuple[float, Dict[str, float]]:
    """Combined ensemble score for a candidate number."""
    freq_dict = {num: count for num, count in freq_data}
    max_freq = max(freq_dict.values()) if freq_dict else 1
    freq_comp = 0.3 * (freq_dict.get(candidate, 0) / max_freq)

    gap = gap_data.get(candidate, len(rows))
    avg_gap = sum(gap_data.values()) / len(gap_data) if gap_data else len(rows)
    gap_comp = 0.25 * (1.0 - min(abs(gap - avg_gap) / (avg_gap * 2), 1.0))

    markov_comp = 0.0
    if last_value in transition_data and candidate in transition_data[last_value]:
        total_transitions = sum(transition_data[last_value].values())
        markov_comp = 0.3 * (transition_data[last_value][candidate] / total_transitions)

    bias_comp = 0.15 * bias_data.get(candidate, 0)

    total = freq_comp + gap_comp + markov_comp + bias_comp
    return total, {
        "frequency": freq_comp,
        "gap": gap_comp,
        "markov": markov_comp,
        "bias": bias_comp,
    }


def kimi_next(csv_path: Path = None, run_accuracy_test: bool = True) -> Dict[int, int]:
    """Predict next draw using ensemble of frequency, gap, Markov, and positional analysis."""
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )

    rows = load_rows(csv_path)

    if len(rows) < 5:
        print("Not enough data to analyze.")
        return {}

    predictions: Dict[int, int] = {}
    col_ranked_candidates: Dict[int, List[int]] = {}
    source: Dict[int, str] = {}
    col_components: Dict[int, Dict] = {}

    print("=" * 50)
    print("KIMI NEXT - Ensemble Prediction Algorithm")
    print("=" * 50)

    # Main numbers (columns 1-5)
    for col in range(1, 6):
        print(f"\n[Column {col} Analysis]")

        last_value = rows[-1][col]
        freq_data = frequency_analysis(rows, col, top_n=20)
        gap_data = gap_analysis(rows, col)
        transition_data = markov_transitions(rows, col)
        bias_data = positional_bias(rows, col)

        print(f"  Last value: {last_value}")
        print(f"  Top frequencies: {freq_data[:5]}")

        candidates = list(range(1, 48))
        scores = []
        candidate_components: Dict[int, Dict] = {}

        for candidate in candidates:
            score, components = ensemble_score(
                rows, col, candidate, last_value,
                gap_data, transition_data, freq_data, bias_data,
            )
            scores.append((candidate, score))
            candidate_components[candidate] = components

        scores.sort(key=lambda x: x[1], reverse=True)
        best_candidate, best_score = scores[0]

        predictions[col] = best_candidate
        col_ranked_candidates[col] = [c for c, _ in scores]
        col_components[col] = candidate_components

        best_comps = candidate_components[best_candidate]
        dominant = max(best_comps.items(), key=lambda kv: kv[1])
        source[col] = f"ensemble score={best_score:.3f}, dominant={dominant[0]} ({dominant[1]:.3f})"

        print(f"  Top 5 candidates: {[(c, round(s, 3)) for c, s in scores[:5]]}")
        print(f"  -> PREDICTED: {best_candidate} (score: {best_score:.3f}, components: {best_comps})")

    # Mega number (column 6, index 6)
    print(f"\n[Mega Number Analysis]")

    last_mega = rows[-1][6]
    freq_data_mega = frequency_analysis(rows, 6, top_n=10)
    gap_data_mega = gap_analysis(rows, 6)
    transition_data_mega = markov_transitions(rows, 6)
    bias_data_mega = positional_bias(rows, 6)

    print(f"  Last mega: {last_mega}")
    print(f"  Top frequencies: {freq_data_mega[:5]}")

    mega_candidates = list(range(1, 28))
    mega_scores = []
    mega_candidate_components: Dict[int, Dict] = {}

    for candidate in mega_candidates:
        score, components = ensemble_score(
            rows, 6, candidate, last_mega,
            gap_data_mega, transition_data_mega, freq_data_mega, bias_data_mega,
        )
        mega_scores.append((candidate, score))
        mega_candidate_components[candidate] = components

    mega_scores.sort(key=lambda x: x[1], reverse=True)
    best_mega, best_mega_score = mega_scores[0]
    best_mega_comps = mega_candidate_components[best_mega]
    dominant_mega = max(best_mega_comps.items(), key=lambda kv: kv[1])
    source[6] = f"ensemble score={best_mega_score:.3f}, dominant={dominant_mega[0]} ({dominant_mega[1]:.3f})"
    predictions[6] = best_mega

    print(f"  Top 5 candidates: {mega_scores[:5]}")
    print(f"  -> PREDICTED: {best_mega} (score: {best_mega_score:.3f})")

    # Duplicate resolution
    print("\n--- Duplicate Resolution ---")
    predictions = resolve_duplicates(predictions, col_ranked_candidates)

    # Update source for any resolved columns
    for col in range(1, 6):
        val = predictions[col]
        best_comps = col_components[col].get(val, {})
        if best_comps:
            dom = max(best_comps.items(), key=lambda kv: kv[1])
            if "duplicate resolution" not in source.get(col, ""):
                pass  # source was set before resolution; leave it unless changed

    print("\n" + "=" * 50)
    print("KIMI_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}  <- {source[col]}")
    print(f"  Mega:     {predictions[6]}  <- {source[6]}")
    print("=" * 50)

    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("KIMI_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from kimi_next_minus_one import kimi_next_minus_one
        kimi_next_minus_one(csv_path)
        print("=" * 50)

    return predictions


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print("\n" + "=" * 50)
    print("KIMI_NEXT: Forward Prediction")
    print("=" * 50)
    kimi_next(csv_path, run_accuracy_test=False)
