import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, resolve_duplicates


def monte_next(
    csv_path: Path = None,
    simulations: int = 10000,
    seed: int = None,
    run_accuracy_test: bool = True,
) -> Dict[int, int]:
    """
    Monte Carlo simulation-based prediction.

    Uses three interleaved strategies per simulation:
      1. Pure weighted-random sampling from historical distribution
      2. Markov-style transition sampling (from last draw)
      3. Correlation-aware sequential column sampling

    Args:
        csv_path:    path to the CSV data file
        simulations: number of simulations to run (default 10 000)
        seed:        optional random seed for reproducibility
        run_accuracy_test: whether to run the minus-one accuracy check
    """
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )
    if simulations is None:
        simulations = int(sys.argv[2]) if len(sys.argv) > 2 else 10000

    if seed is not None:
        random.seed(seed)

    rows: List[List[int]] = load_rows(csv_path)

    if len(rows) < 5:
        print("Not enough data for Monte Carlo simulation (need at least 5 rows)")
        return {}

    print("\n" + "=" * 50)
    print("MONTE CARLO SIMULATION PREDICTION")
    print("=" * 50)
    print(f"Running {simulations:,} simulations based on historical distributions...")
    print(f"Data rows: {len(rows)}" + (f"  |  seed={seed}" if seed is not None else ""))

    # Historical distributions per column
    col_distributions: Dict[int, Counter] = {
        col: Counter(row[col] for row in rows)
        for col in range(1, 7)
    }

    # Markov-style transition lists
    transitions: Dict[int, Dict[int, List[int]]] = {col: {} for col in range(1, 7)}
    for col in range(1, 7):
        for i in range(len(rows) - 1):
            cur, nxt = rows[i][col], rows[i + 1][col]
            transitions[col].setdefault(cur, []).append(nxt)

    # Column-pair correlations (for correlation-aware sampling)
    correlations: Dict[Tuple[int, int], Counter] = {}
    for c1 in range(1, 6):
        for c2 in range(c1 + 1, 6):
            correlations[(c1, c2)] = Counter()
            for row in rows:
                correlations[(c1, c2)][(row[c1], row[c2])] += 1

    print("\n--- Historical Statistics ---")
    for col in range(1, 6):
        print(f"Column {col}: Top values = {col_distributions[col].most_common(3)}")
    print(f"Mega: Top values = {col_distributions[6].most_common(3)}")

    print(f"\n--- Running {simulations:,} Simulations ---")

    simulation_results: Dict[int, Counter] = {i: Counter() for i in range(1, 7)}
    last_row = rows[-1]

    for sim in range(simulations):
        method = sim % 3

        if method == 0:
            # Method 1: pure weighted random
            for col in range(1, 7):
                vals = list(col_distributions[col].keys())
                wts = list(col_distributions[col].values())
                simulation_results[col][random.choices(vals, weights=wts, k=1)[0]] += 1

        elif method == 1:
            # Method 2: transition-based
            for col in range(1, 7):
                cur = last_row[col]
                if cur in transitions[col] and transitions[col][cur]:
                    chosen = random.choice(transitions[col][cur])
                else:
                    vals = list(col_distributions[col].keys())
                    wts = list(col_distributions[col].values())
                    chosen = random.choices(vals, weights=wts, k=1)[0]
                simulation_results[col][chosen] += 1

        else:
            # Method 3: correlation-aware sequential
            temp: Dict[int, int] = {}
            for col in range(1, 6):
                if col == 1:
                    vals = list(col_distributions[col].keys())
                    wts = list(col_distributions[col].values())
                    chosen = random.choices(vals, weights=wts, k=1)[0]
                else:
                    prev_val = temp[col - 1]
                    correlated = [
                        v2 for (v1, v2), cnt in correlations.get((col - 1, col), Counter()).items()
                        if v1 == prev_val
                        for _ in range(cnt)
                    ]
                    if correlated and random.random() < 0.7:
                        chosen = random.choice(correlated)
                    else:
                        vals = list(col_distributions[col].keys())
                        wts = list(col_distributions[col].values())
                        chosen = random.choices(vals, weights=wts, k=1)[0]
                temp[col] = chosen
                simulation_results[col][chosen] += 1

            # Mega: independent
            vals = list(col_distributions[6].keys())
            wts = list(col_distributions[6].values())
            simulation_results[6][random.choices(vals, weights=wts, k=1)[0]] += 1

    # Extract predictions
    prediction: Dict[int, int] = {}
    source: Dict[int, str] = {}

    print("\n--- Simulation Results ---")
    for col in range(1, 6):
        val, hits = simulation_results[col].most_common(1)[0]
        prediction[col] = val
        conf = hits / simulations * 100
        source[col] = f"Monte Carlo ({simulations:,} sims, confidence={conf:.1f}%, hits={hits})"
        print(f"  Column {col}: {val} (confidence: {conf:.1f}%)")

    mega_val, mega_hits = simulation_results[6].most_common(1)[0]
    prediction[6] = mega_val
    mega_conf = mega_hits / simulations * 100
    source[6] = f"Monte Carlo ({simulations:,} sims, confidence={mega_conf:.1f}%, hits={mega_hits})"
    print(f"  Mega: {mega_val} (confidence: {mega_conf:.1f}%)")

    print("\n--- Top 3 Alternatives per Column ---")
    for col in range(1, 7):
        top3 = simulation_results[col].most_common(3)
        label = f"Column {col}" if col < 6 else "Mega"
        alts = [f"{v} ({cnt / simulations * 100:.1f}%)" for v, cnt in top3]
        print(f"  {label}: {', '.join(alts)}")

    # Duplicate resolution
    print("\n--- Duplicate Resolution ---")
    col_ranked_candidates = {
        col: [v for v, _ in simulation_results[col].most_common()]
        for col in range(1, 6)
    }
    prediction = resolve_duplicates(prediction, col_ranked_candidates)

    print("\n" + "=" * 50)
    print("MONTE_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {prediction[col]}  <- {source[col]}")
    print(f"  Mega:     {prediction[6]}  <- {source[6]}")
    print("=" * 50)

    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("MONTE_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from monte_next_minus_one import monte_next_minus_one
        monte_next_minus_one(csv_path)
        print("=" * 50)

    return prediction


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    simulations = int(sys.argv[2]) if len(sys.argv) > 2 else None
    monte_next(csv_path, simulations)
