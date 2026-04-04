import csv
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple
import math


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


def calculate_trend(rows: List[List[int]], column: int, window: int = 5) -> float:
    """
    Calculate the trend direction and strength for a column.
    Returns a value between -1 (strong decreasing) and 1 (strong increasing).
    """
    if len(rows) < window:
        return 0.0
    
    recent = [row[column] for row in rows[-window:]]
    # Simple linear regression slope
    n = len(recent)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(recent) / n
    
    numerator = sum((x[i] - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.0
    
    slope = numerator / denominator
    # Normalize to -1 to 1 range (assuming max slope of ~10 per draw)
    return max(-1, min(1, slope / 10))


def calculate_momentum(rows: List[List[int]], column: int, window: int = 3) -> float:
    """
    Calculate momentum - how fast the number is changing.
    High momentum = large recent changes, Low momentum = stable.
    """
    if len(rows) < window + 1:
        return 0.0
    
    recent = [row[column] for row in rows[-(window+1):]]
    changes = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]
    
    avg_change = sum(changes) / len(changes)
    # Normalize (assuming max meaningful change is ~20)
    return min(1, avg_change / 20)


def detect_cycle(rows: List[List[int]], column: int, max_cycle: int = 10) -> Tuple[int, float]:
    """
    Detect if there's a cyclical pattern in the column.
    Returns (cycle_length, confidence) where confidence is 0-1.
    """
    if len(rows) < max_cycle * 2:
        return (0, 0.0)
    
    values = [row[column] for row in rows]
    best_cycle = 0
    best_score = 0.0
    
    for cycle_len in range(2, min(max_cycle, len(values) // 2)):
        score = 0
        matches = 0
        for i in range(cycle_len, len(values)):
            # Compare current value with value one cycle ago
            diff = abs(values[i] - values[i - cycle_len])
            if diff <= 5:  # Within 5 numbers is considered a match
                score += 1 - (diff / 5)
                matches += 1
        
        if matches > 0:
            avg_score = score / (len(values) - cycle_len)
            if avg_score > best_score:
                best_score = avg_score
                best_cycle = cycle_len
    
    return (best_cycle, best_score)


def calculate_pressure(rows: List[List[int]], column: int, window: int = 10) -> Dict[int, float]:
    """
    Calculate 'pressure' - which numbers are being pushed toward based on recent clustering.
    """
    if len(rows) < window:
        return {}
    
    recent = [row[column] for row in rows[-window:]]
    mean_val = sum(recent) / len(recent)
    std_val = math.sqrt(sum((x - mean_val) ** 2 for x in recent) / len(recent)) if len(recent) > 1 else 1
    
    # Create pressure map - numbers closer to mean have higher pressure
    pressure = {}
    for num in range(1, 48):
        distance = abs(num - mean_val)
        # Gaussian-like pressure centered on mean
        pressure[num] = math.exp(-(distance ** 2) / (2 * (std_val + 5) ** 2))
    
    return pressure


def calculate_drift(rows: List[List[int]], column: int, short_window: int = 3, long_window: int = 10) -> float:
    """
    Calculate drift - difference between short-term and long-term trends.
    Positive drift = short term is higher than long term (upward momentum).
    """
    if len(rows) < long_window:
        return 0.0
    
    short_avg = sum(row[column] for row in rows[-short_window:]) / short_window
    long_avg = sum(row[column] for row in rows[-long_window:]) / long_window
    
    # Normalize to -1 to 1
    drift = (short_avg - long_avg) / 20
    return max(-1, min(1, drift))


def ensemble_weather_score(
    candidate: int,
    last_value: int,
    trend: float,
    momentum: float,
    cycle_len: int,
    cycle_conf: float,
    pressure: Dict[int, float],
    drift: float
) -> float:
    """
    Calculate ensemble weather score for a candidate number.
    """
    score = 0.0
    
    # 1. Trend component (weight: 0.25)
    # If trend is positive, favor higher numbers, negative favors lower
    distance_from_last = candidate - last_value
    trend_alignment = 1 - abs(distance_from_last / 20 - trend)
    score += 0.25 * max(0, trend_alignment)
    
    # 2. Momentum component (weight: 0.20)
    # High momentum means larger jumps are more likely
    expected_jump = momentum * 15  # Max jump based on momentum
    jump_diff = abs(abs(distance_from_last) - expected_jump)
    momentum_score = 1 - min(jump_diff / 20, 1)
    score += 0.20 * momentum_score
    
    # 3. Cycle component (weight: 0.25)
    # If we detected a cycle, predict the value from one cycle ago
    cycle_score = pressure.get(candidate, 0)
    score += 0.25 * cycle_score
    
    # 4. Pressure component (weight: 0.20)
    pressure_score = pressure.get(candidate, 0)
    score += 0.20 * pressure_score
    
    # 5. Drift component (weight: 0.10)
    # Drift indicates acceleration/deceleration
    drift_score = 1 - abs((candidate - last_value) / 20 - drift)
    score += 0.10 * max(0, drift_score)
    
    return score


def weather_next(csv_path: Path = None, run_accuracy_test: bool = True) -> Dict[int, int]:
    """
    Predict next draw using weather-like pattern analysis:
    - Trend (direction of movement)
    - Momentum (speed of change)
    - Cycles (repeating patterns)
    - Pressure (clustering tendency)
    - Drift (short vs long term divergence)
    """
    if csv_path is None:
        csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
    
    rows, _ = load_data(csv_path)
    
    if len(rows) < 10:
        print("Not enough data for weather analysis (need at least 10 draws).")
        return {}
    
    predictions = {}
    
    print("=" * 50)
    print("WEATHER NEXT - Atmospheric Pattern Prediction")
    print("=" * 50)
    
    # Analyze main numbers (columns 1-5, indices 1-5)
    for col in range(1, 6):
        print(f"\n[Column {col} Weather Analysis]")
        
        last_value = rows[-1][col]
        
        # Calculate all weather metrics
        trend = calculate_trend(rows, col, window=5)
        momentum = calculate_momentum(rows, col, window=3)
        cycle_len, cycle_conf = detect_cycle(rows, col, max_cycle=10)
        pressure = calculate_pressure(rows, col, window=10)
        drift = calculate_drift(rows, col, short_window=3, long_window=10)
        
        print(f"  Last value: {last_value}")
        print(f"  Trend: {trend:+.2f} ({'rising' if trend > 0.1 else 'falling' if trend < -0.1 else 'stable'})")
        print(f"  Momentum: {momentum:.2f} ({'high' if momentum > 0.5 else 'low'} volatility)")
        print(f"  Cycle: length={cycle_len}, confidence={cycle_conf:.2f}")
        print(f"  Drift: {drift:+.2f} ({'accelerating' if drift > 0.1 else 'decelerating' if drift < -0.1 else 'steady'})")
        
        # Score all candidates
        candidates = list(range(1, 48))
        scores = []
        
        for candidate in candidates:
            score = ensemble_weather_score(
                candidate, last_value, trend, momentum,
                cycle_len, cycle_conf, pressure, drift
            )
            scores.append((candidate, score))
        
        # Sort and pick best
        scores.sort(key=lambda x: x[1], reverse=True)
        best_candidate = scores[0][0]
        best_score = scores[0][1]
        
        predictions[col] = best_candidate
        
        print(f"  Top 5 candidates: {scores[:5]}")
        print(f"  -> PREDICTED: {best_candidate} (score: {best_score:.3f})")
    
    # Analyze mega number (column 7, index 6)
    print(f"\n[Mega Number Weather Analysis]")
    
    last_mega = rows[-1][6]
    
    trend_mega = calculate_trend(rows, 6, window=5)
    momentum_mega = calculate_momentum(rows, 6, window=3)
    cycle_len_mega, cycle_conf_mega = detect_cycle(rows, 6, max_cycle=10)
    pressure_mega = calculate_pressure(rows, 6, window=10)
    drift_mega = calculate_drift(rows, 6, short_window=3, long_window=10)
    
    print(f"  Last mega: {last_mega}")
    print(f"  Trend: {trend_mega:+.2f}")
    print(f"  Momentum: {momentum_mega:.2f}")
    print(f"  Cycle: length={cycle_len_mega}, confidence={cycle_conf_mega:.2f}")
    print(f"  Drift: {drift_mega:+.2f}")
    
    # Mega numbers typically 1-27
    mega_candidates = list(range(1, 28))
    mega_scores = []
    
    for candidate in mega_candidates:
        score = ensemble_weather_score(
            candidate, last_mega, trend_mega, momentum_mega,
            cycle_len_mega, cycle_conf_mega, pressure_mega, drift_mega
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
    print("FINAL WEATHER PREDICTION")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}")
    print(f"  Mega: {predictions[6]}")
    print("=" * 50)
    
    # Run accuracy test (minus_one) only if not called from minus_one
    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("WEATHER_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        # Import here to avoid circular import issues
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from weather_next_minus_one import weather_next_minus_one
        weather_next_minus_one(csv_path)
        print("=" * 50)
    
    return predictions


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    
    # Run main prediction
    print("\n" + "=" * 50)
    print("WEATHER_NEXT: Forward Prediction")
    print("=" * 50)
    weather_next(csv_path, run_accuracy_test=False)
