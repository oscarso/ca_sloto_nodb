import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import random
from collections import Counter


def monte_next(csv_path: Path = None, simulations: int = 10000, run_accuracy_test: bool = True) -> Dict[int, int]:
    """
    Monte Carlo simulation-based prediction.
    
    Completely different approach from oso/kimi/weather:
    - Uses statistical sampling rather than pattern matching
    - Runs thousands of random simulations based on historical distributions
    - Accounts for column correlations through joint probability sampling
    - Predicts based on most frequent outcomes across all simulations
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    if simulations is None:
        simulations = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    
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
    
    if len(rows) < 5:
        print("Not enough data for Monte Carlo simulation (need at least 5 rows)")
        return {}
    
    print("\n" + "=" * 50)
    print("MONTE CARLO SIMULATION PREDICTION")
    print("=" * 50)
    print(f"Running {simulations:,} simulations based on historical distributions...")
    print(f"Data rows: {len(rows)}")
    
    # Analyze historical distributions per column
    col_distributions: Dict[int, Counter] = {}
    for col in range(1, 7):  # Columns 1-6 (main + mega)
        values = [row[col] for row in rows]
        col_distributions[col] = Counter(values)
    
    # Calculate transition probabilities (Markov-like but Monte Carlo style)
    transitions: Dict[int, Dict[int, List[int]]] = {}
    for col in range(1, 7):
        transitions[col] = {}
        for i in range(len(rows) - 1):
            current = rows[i][col]
            next_val = rows[i+1][col]
            if current not in transitions[col]:
                transitions[col][current] = []
            transitions[col][current].append(next_val)
    
    # Column correlations (joint occurrences)
    correlations: Dict[Tuple[int, int, int], Counter] = {}
    for c1 in range(1, 6):
        for c2 in range(c1+1, 6):
            correlations[(c1, c2, 0)] = Counter()  # 0 = any, track pairs
            for row in rows:
                pair = (row[c1], row[c2])
                correlations[(c1, c2, 0)][pair] += 1
    
    print("\n--- Historical Statistics ---")
    for col in range(1, 6):
        dist = col_distributions[col]
        most_common = dist.most_common(3)
        print(f"Column {col}: Top values = {most_common}")
    
    mega_dist = col_distributions[6]
    print(f"Mega: Top values = {mega_dist.most_common(3)}")
    
    # Run Monte Carlo simulations
    print(f"\n--- Running {simulations:,} Simulations ---")
    
    simulation_results: Dict[int, Counter] = {i: Counter() for i in range(1, 7)}
    
    # Get last row as starting point for transitions
    last_row = rows[-1]
    
    for sim in range(simulations):
        # Method 1: Pure random sampling from distribution
        if sim % 3 == 0:
            for col in range(1, 7):
                # Weighted random choice based on historical frequency
                values = list(col_distributions[col].keys())
                weights = list(col_distributions[col].values())
                chosen = random.choices(values, weights=weights, k=1)[0]
                simulation_results[col][chosen] += 1
        
        # Method 2: Transition-based sampling
        elif sim % 3 == 1:
            for col in range(1, 7):
                current = last_row[col]
                if current in transitions[col] and transitions[col][current]:
                    # Sample from historical transitions
                    next_candidates = transitions[col][current]
                    chosen = random.choice(next_candidates)
                else:
                    # Fallback to distribution
                    values = list(col_distributions[col].keys())
                    weights = list(col_distributions[col].values())
                    chosen = random.choices(values, weights=weights, k=1)[0]
                simulation_results[col][chosen] += 1
        
        # Method 3: Constrained random walk with correlation
        else:
            # Sample columns sequentially with correlation awareness
            temp_prediction = {}
            for col in range(1, 6):
                if col == 1:
                    # First column: pure distribution
                    values = list(col_distributions[col].keys())
                    weights = list(col_distributions[col].values())
                    chosen = random.choices(values, weights=weights, k=1)[0]
                else:
                    # Subsequent columns: consider previous column correlation
                    prev_col = col - 1
                    prev_val = temp_prediction[prev_col]
                    # Find correlated values
                    correlated = []
                    for (v1, v2), cnt in correlations.get((prev_col, col, 0), Counter()).items():
                        if v1 == prev_val:
                            correlated.extend([v2] * cnt)
                    
                    if correlated and random.random() < 0.7:  # 70% use correlation
                        chosen = random.choice(correlated)
                    else:
                        # Fallback to distribution
                        values = list(col_distributions[col].keys())
                        weights = list(col_distributions[col].values())
                        chosen = random.choices(values, weights=weights, k=1)[0]
                
                temp_prediction[col] = chosen
                simulation_results[col][chosen] += 1
            
            # Mega column independent
            values = list(col_distributions[6].keys())
            weights = list(col_distributions[6].values())
            chosen = random.choices(values, weights=weights, k=1)[0]
            simulation_results[6][chosen] += 1
    
    # Extract predictions (most frequent in simulations)
    prediction = {}
    confidence = {}
    
    print("\n--- Simulation Results ---")
    print("Column predictions based on frequency across all simulations:")
    
    for col in range(1, 6):
        most_common = simulation_results[col].most_common(1)[0]
        prediction[col] = most_common[0]
        confidence[col] = most_common[1] / simulations * 100
        print(f"  Column {col}: {prediction[col]} (confidence: {confidence[col]:.1f}%)")
    
    mega_common = simulation_results[6].most_common(1)[0]
    prediction[6] = mega_common[0]
    confidence[6] = mega_common[1] / simulations * 100
    print(f"  Mega: {prediction[6]} (confidence: {confidence[6]:.1f}%)")
    
    # Show top 3 alternatives for each column
    print("\n--- Top 3 Alternatives per Column ---")
    for col in range(1, 7):
        top3 = simulation_results[col].most_common(3)
        col_name = f"Column {col}" if col < 6 else "Mega"
        alts = [f"{val} ({cnt/simulations*100:.1f}%)" for val, cnt in top3]
        print(f"  {col_name}: {', '.join(alts)}")
    
    print("\n" + "=" * 50)
    print("MONTE CARLO FINAL PREDICTION")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {prediction[col]}")
    print(f"  Mega: {prediction[6]}")
    print("=" * 50)
    
    # Run accuracy test
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("MONTE_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        sys.path.insert(0, str(Path(__file__).parent))
        from monte_next_minus_one import monte_next_minus_one
        monte_next_minus_one(csv_path)
        print("=" * 50)
    
    return prediction


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    simulations = int(sys.argv[2]) if len(sys.argv) > 2 else None
    monte_next(csv_path, simulations)
