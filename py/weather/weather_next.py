import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_rows, resolve_duplicates


def calculate_trend(rows: List[List[int]], column: int, window: int = 5) -> float:
    """Linear regression slope, normalised to [-1, 1]."""
    if len(rows) < window:
        return 0.0
    recent = [row[column] for row in rows[-window:]]
    n = len(recent)
    x_mean = (n - 1) / 2
    y_mean = sum(recent) / n
    numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    if denominator == 0:
        return 0.0
    return max(-1.0, min(1.0, numerator / denominator / 10))


def calculate_momentum(rows: List[List[int]], column: int, window: int = 3) -> float:
    """Average absolute change over recent draws, normalised to [0, 1]."""
    if len(rows) < window + 1:
        return 0.0
    recent = [row[column] for row in rows[-(window + 1):]]
    changes = [abs(recent[i] - recent[i - 1]) for i in range(1, len(recent))]
    return min(1.0, sum(changes) / len(changes) / 20)


def detect_cycle(rows: List[List[int]], column: int, max_cycle: int = 10) -> Tuple[int, float]:
    """Detect repeating pattern. Returns (cycle_length, confidence 0-1)."""
    if len(rows) < max_cycle * 2:
        return (0, 0.0)
    values = [row[column] for row in rows]
    best_cycle, best_score = 0, 0.0
    for cycle_len in range(2, min(max_cycle, len(values) // 2)):
        score = sum(
            1 - min(abs(values[i] - values[i - cycle_len]) / 5, 1.0)
            for i in range(cycle_len, len(values))
            if abs(values[i] - values[i - cycle_len]) <= 5
        )
        avg = score / (len(values) - cycle_len)
        if avg > best_score:
            best_score, best_cycle = avg, cycle_len
    return (best_cycle, best_score)


def calculate_pressure(rows: List[List[int]], column: int, window: int = 10) -> Dict[int, float]:
    """Gaussian pressure map centred on recent mean."""
    if len(rows) < window:
        return {}
    recent = [row[column] for row in rows[-window:]]
    mean_val = sum(recent) / len(recent)
    std_val = math.sqrt(sum((x - mean_val) ** 2 for x in recent) / len(recent)) if len(recent) > 1 else 1
    return {
        num: math.exp(-(abs(num - mean_val) ** 2) / (2 * (std_val + 5) ** 2))
        for num in range(1, 48)
    }


def calculate_drift(rows: List[List[int]], column: int, short_window: int = 3, long_window: int = 10) -> float:
    """Short-term vs long-term average divergence, normalised to [-1, 1]."""
    if len(rows) < long_window:
        return 0.0
    short_avg = sum(row[column] for row in rows[-short_window:]) / short_window
    long_avg = sum(row[column] for row in rows[-long_window:]) / long_window
    return max(-1.0, min(1.0, (short_avg - long_avg) / 20))


def ensemble_weather_score(
    candidate: int,
    last_value: int,
    trend: float,
    momentum: float,
    cycle_len: int,
    cycle_conf: float,
    pressure: Dict[int, float],
    drift: float,
) -> Tuple[float, Dict[str, float]]:
    """Weighted combination of weather-inspired signals."""
    distance = candidate - last_value

    trend_comp = 0.25 * max(0.0, 1 - abs(distance / 20 - trend))
    momentum_comp = 0.20 * (1 - min(abs(abs(distance) - momentum * 15) / 20, 1.0))
    cycle_comp = 0.25 * pressure.get(candidate, 0.0)
    pressure_comp = 0.20 * pressure.get(candidate, 0.0)
    drift_comp = 0.10 * max(0.0, 1 - abs((candidate - last_value) / 20 - drift))

    total = trend_comp + momentum_comp + cycle_comp + pressure_comp + drift_comp
    return total, {
        "trend": trend_comp,
        "momentum": momentum_comp,
        "cycle": cycle_comp,
        "pressure": pressure_comp,
        "drift": drift_comp,
    }


def weather_next(csv_path: Path = None, run_accuracy_test: bool = True) -> Dict[int, int]:
    """Predict next draw using weather-like pattern analysis."""
    if csv_path is None:
        csv_path = (
            Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[1] / "data" / "dresult_test.csv"
        )

    rows = load_rows(csv_path)

    if len(rows) < 10:
        print("Not enough data for weather analysis (need at least 10 draws).")
        return {}

    predictions: Dict[int, int] = {}
    col_ranked_candidates: Dict[int, List[int]] = {}
    source: Dict[int, str] = {}
    col_components: Dict[int, Dict] = {}

    print("=" * 50)
    print("WEATHER NEXT - Atmospheric Pattern Prediction")
    print("=" * 50)

    for col in range(1, 6):
        print(f"\n[Column {col} Weather Analysis]")

        last_value = rows[-1][col]
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

        candidates = list(range(1, 48))
        scores = []
        candidate_components: Dict[int, Dict] = {}

        for candidate in candidates:
            score, components = ensemble_weather_score(
                candidate, last_value, trend, momentum,
                cycle_len, cycle_conf, pressure, drift,
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
        source[col] = f"weather score={best_score:.3f}, dominant={dominant[0]} ({dominant[1]:.3f})"

        print(f"  Top 5 candidates: {[(c, round(s, 3)) for c, s in scores[:5]]}")
        print(f"  -> PREDICTED: {best_candidate} (score: {best_score:.3f}, components: {best_comps})")

    # Mega number
    print(f"\n[Mega Number Weather Analysis]")

    last_mega = rows[-1][6]
    trend_m = calculate_trend(rows, 6, window=5)
    momentum_m = calculate_momentum(rows, 6, window=3)
    cycle_len_m, cycle_conf_m = detect_cycle(rows, 6, max_cycle=10)
    pressure_m = calculate_pressure(rows, 6, window=10)
    drift_m = calculate_drift(rows, 6, short_window=3, long_window=10)

    print(f"  Last mega: {last_mega}")
    print(f"  Trend: {trend_m:+.2f}  Momentum: {momentum_m:.2f}  Drift: {drift_m:+.2f}")
    print(f"  Cycle: length={cycle_len_m}, confidence={cycle_conf_m:.2f}")

    mega_scores = []
    mega_candidate_components: Dict[int, Dict] = {}
    for candidate in range(1, 28):
        score, components = ensemble_weather_score(
            candidate, last_mega, trend_m, momentum_m,
            cycle_len_m, cycle_conf_m, pressure_m, drift_m,
        )
        mega_scores.append((candidate, score))
        mega_candidate_components[candidate] = components

    mega_scores.sort(key=lambda x: x[1], reverse=True)
    best_mega, best_mega_score = mega_scores[0]
    best_mega_comps = mega_candidate_components[best_mega]
    dominant_mega = max(best_mega_comps.items(), key=lambda kv: kv[1])
    source[6] = f"weather score={best_mega_score:.3f}, dominant={dominant_mega[0]} ({dominant_mega[1]:.3f})"
    predictions[6] = best_mega

    print(f"  Top 5 candidates: {mega_scores[:5]}")
    print(f"  -> PREDICTED: {best_mega} (score: {best_mega_score:.3f})")

    # Duplicate resolution
    print("\n--- Duplicate Resolution ---")
    predictions = resolve_duplicates(predictions, col_ranked_candidates)

    print("\n" + "=" * 50)
    print("WEATHER_NEXT - FINAL PREDICTION (with source)")
    print("=" * 50)
    for col in range(1, 6):
        print(f"  Column {col}: {predictions[col]}  <- {source[col]}")
    print(f"  Mega:     {predictions[6]}  <- {source[6]}")
    print("=" * 50)

    if run_accuracy_test:
        print("\n" + "=" * 50)
        print("WEATHER_NEXT_MINUS_ONE: Accuracy Test")
        print("=" * 50)
        from weather_next_minus_one import weather_next_minus_one
        weather_next_minus_one(csv_path)
        print("=" * 50)

    return predictions


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print("\n" + "=" * 50)
    print("WEATHER_NEXT: Forward Prediction")
    print("=" * 50)
    weather_next(csv_path, run_accuracy_test=False)
