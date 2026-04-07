# ca_sloto Pattern Analysis

Scripts to analyze vertical patterns in ca_sloto draw data and predict the next draw.

## Folder Structure

```
py/
├── oso/              # Pattern analysis scripts (order-based)
│   ├── oso_order2.py
│   ├── oso_order3.py
│   ├── oso_order4.py
│   ├── oso_order5.py
│   ├── oso_order_m2.py
│   ├── oso_order_m3.py
│   ├── oso_order_m4.py
│   ├── oso_order_m5.py
│   ├── oso_next.py           # Main OSO prediction
│   └── oso_next_minus_one.py # Accuracy test
├── kimi/             # Ensemble prediction algorithm
│   ├── kimi_next.py
│   └── kimi_next_minus_one.py
├── weather/          # Weather-like trend prediction
│   ├── weather_next.py
│   └── weather_next_minus_one.py
├── monte/            # Monte Carlo simulation
│   ├── monte_next.py
│   └── monte_next_minus_one.py
└── predict_all.py    # Compare all four algorithms
```

## OSO Pattern Analysis (py/oso/)

### oso_order2.py
Analyzes 2‑row patterns in columns 2–6. Counts both vertical (same-column) and cross-column permutation patterns between consecutive rows. Outputs merged sorted list.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order2.py

# Show all patterns from a custom file
python3 py/oso/oso_order2.py path/to/file.csv

# Show top 3 frequency groups (default file)
python3 py/oso/oso_order2.py 3

# Show top 5 frequency groups from custom file
python3 py/oso/oso_order2.py path/to/file.csv 5
```

- **Output**: Merged vertical + cross-column patterns, sorted by frequency
- **top_n**: Shows patterns in top N frequency groups (e.g., all patterns with count 18, 15, 14 if top_n=3)
- **Columns used**: 2–6 (skips draw_num and mega)
- **Window size**: 2 rows
- **Cross combinations**: 5×5 = 25 per row pair

### oso_order3.py
Analyzes 3‑row patterns in columns 2–6. Counts both vertical and cross-column permutation patterns. Outputs merged sorted list.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order3.py

# Show top 3 frequency groups
python3 py/oso/oso_order3.py 3
```

- **Output**: Merged vertical + cross-column patterns, sorted by frequency
- **top_n**: Shows patterns in top N frequency groups
- **Columns used**: 2–6
- **Window size**: 3 rows
- **Cross combinations**: 5×5×5 = 125 per row triple

### oso_order4.py
Analyzes 4‑row patterns in columns 2–6. Counts both vertical and cross-column permutation patterns. Outputs merged sorted list.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order4.py

# Show top 3 frequency groups
python3 py/oso/oso_order4.py 3
```

- **Output**: Merged vertical + cross-column patterns, sorted by frequency
- **top_n**: Shows patterns in top N frequency groups
- **Columns used**: 2–6
- **Window size**: 4 rows
- **Cross combinations**: 5×5×5×5 = 625 per row quadruple

### oso_order5.py
Analyzes 5‑row patterns in columns 2–6. Counts both vertical and cross-column permutation patterns. Outputs merged sorted list.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order5.py

# Show top 3 frequency groups
python3 py/oso/oso_order5.py 3
```

- **Output**: Merged vertical + cross-column patterns, sorted by frequency
- **top_n**: Shows patterns in top N frequency groups
- **Columns used**: 2–6
- **Window size**: 5 rows
- **Cross combinations**: 5×5×5×5×5 = 3,125 per row quintuple

### oso_order_m2.py
Analyzes 2‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order_m2.py

# Show all patterns from a custom file
python3 py/oso/oso_order_m2.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/oso/oso_order_m2.py 5

# Show top 10 patterns from a custom file
python3 py/oso/oso_order_m2.py path/to/file.csv 10
```

- **Output**: 2‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 2 rows

### oso_order_m3.py
Analyzes 3‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order_m3.py

# Show all patterns from a custom file
python3 py/oso/oso_order_m3.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/oso/oso_order_m3.py 5

# Show top 10 patterns from a custom file
python3 py/oso/oso_order_m3.py path/to/file.csv 10
```

- **Output**: 3‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 3 rows

### oso_order_m4.py
Analyzes 4‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order_m4.py

# Show all patterns from a custom file
python3 py/oso/oso_order_m4.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/oso/oso_order_m4.py 5

# Show top 10 patterns from a custom file
python3 py/oso/oso_order_m4.py path/to/file.csv 10
```

- **Output**: 4‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 4 rows

### oso_order_m5.py
Analyzes 5‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/oso/oso_order_m5.py

# Show all patterns from a custom file
python3 py/oso/oso_order_m5.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/oso/oso_order_m5.py 5

# Show top 10 patterns from a custom file
python3 py/oso/oso_order_m5.py path/to/file.csv 10
```

- **Output**: 5‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 5 rows

### oso_next.py
Predicts the next draw using hierarchical fallback approaches. Accepts optional `top_n` parameter to show prediction based on top pattern frequency groups.

```bash
# Use default file (top_n defaults to showing all patterns)
python3 py/oso/oso_next.py

# Specify custom file
python3 py/oso/oso_next.py path/to/file.csv

# Specify file and top_n (shows prediction based on top 3 frequency groups)
python3 py/oso/oso_next.py path/to/file.csv 3

# Higher top_n for more pattern groups
python3 py/oso/oso_next.py path/to/file.csv 5
```

- **Main numbers priority**: oso_order4 → oso_order5 → oso_order3 → oso_order2 fallback hierarchy
- **Mega number priority**: oso_order_m5 → oso_order_m4 → oso_order_m3 → oso_order_m2 fallback hierarchy
- **top_n parameter**: When specified, shows additional "PREDICTION BASED ON TOP N PATTERN GROUPS" section with patterns used for each column
- **Output**: Shows all prediction stages + final prediction + optional top-N pattern analysis
- **Target**: Predicts the draw immediately after the last row in the input file
- **Includes**: Automatically runs `oso_next_minus_one` for accuracy test

### oso_next_minus_one.py
Tests prediction accuracy by excluding the last draw and predicting it. Accepts optional `top_n` parameter.

```bash
# Use default file
python3 py/oso/oso_next_minus_one.py

# Specify custom file
python3 py/oso/oso_next_minus_one.py path/to/file.csv

# Specify file and top_n
python3 py/oso/oso_next_minus_one.py path/to/file.csv 3
```

- **Method**: Excludes last draw, predicts it, then compares with actual
- **top_n parameter**: Passed to oso_next for pattern group filtering
- **Output**: Shows predicted vs actual values with accuracy percentage
- **Purpose**: Validates prediction model performance

## KIMI Ensemble Prediction (py/kimi/)

### kimi_next.py
Ensemble prediction algorithm combining frequency analysis, gap analysis, Markov transitions, and positional bias.

```bash
# Use default file
python3 py/kimi/kimi_next.py

# Specify a custom file
python3 py/kimi/kimi_next.py path/to/file.csv
```

- **Components**:
  - **Frequency**: Most common numbers per column
  - **Gap analysis**: Time since last appearance
  - **Markov chains**: Transition probabilities from recent values
  - **Positional bias**: Column-specific distributions
- **Output**: Shows analysis per column with confidence scores
- **Includes**: Automatically runs `kimi_next_minus_one` for accuracy test

### kimi_next_minus_one.py
Tests kimi_next prediction accuracy by excluding the last draw.

```bash
python3 py/kimi/kimi_next_minus_one.py
```

- **Method**: Excludes last draw, runs kimi_next, compares prediction with actual
- **Output**: Shows predicted vs actual with accuracy percentage

## WEATHER Prediction (py/weather/)

### weather_next.py
"Weather-like" prediction using trend, momentum, cycle, pressure, and drift analysis.

```bash
# Use default file
python3 py/weather/weather_next.py

# Specify a custom file
python3 py/weather/weather_next.py path/to/file.csv
```

- **Metrics**:
  - **Trend**: Direction of movement (rising/falling/stable)
  - **Momentum**: Volatility/speed of change
  - **Cycles**: Repeating patterns every N draws
  - **Pressure**: Clustering tendency around recent average
  - **Drift**: Short-term vs long-term divergence
- **Output**: Shows weather analysis per column with prediction scores
- **Includes**: Automatically runs `weather_next_minus_one` for accuracy test

### weather_next_minus_one.py
Tests weather_next prediction accuracy by excluding the last draw.

```bash
python3 py/weather/weather_next_minus_one.py
```

- **Method**: Excludes last draw, runs weather_next, compares prediction with actual
- **Output**: Shows predicted vs actual with accuracy percentage

## MONTE CARLO Simulation (py/monte/)

### monte_next.py
Monte Carlo simulation-based prediction using statistical sampling and probability distributions. Completely different from pattern/trend approaches.

```bash
# Use default file (10,000 simulations)
python3 py/monte/monte_next.py

# Specify custom file
python3 py/monte/monte_next.py path/to/file.csv

# Custom file with 50,000 simulations
python3 py/monte/monte_next.py path/to/file.csv 50000
```

- **Approach**: 
  - **Distribution sampling**: Weighted random selection from historical frequencies
  - **Transition chains**: Sampling from Markov-style state transitions
  - **Correlation modeling**: Column-to-column dependency simulation
- **Simulations**: Default 10,000 runs (configurable)
- **Output**: Shows simulation statistics, confidence levels, and top alternatives per column
- **Includes**: Automatically runs `monte_next_minus_one` for accuracy test

### monte_next_minus_one.py
Tests monte_next prediction accuracy by excluding the last draw.

```bash
python3 py/monte/monte_next_minus_one.py
```

- **Method**: Excludes last draw, runs monte_next, compares prediction with actual
- **Output**: Shows predicted vs actual with accuracy percentage

## Comparison Script

### predict_all.py
Runs all four prediction algorithms (oso_next, kimi_next, weather_next, monte_next) and displays results side by side. All algorithms show detailed output.

```bash
# Use default file (top_n=3, simulations=10000)
python3 py/predict_all.py

# Specify custom file
python3 py/predict_all.py path/to/file.csv

# Custom file + top_n
python3 py/predict_all.py path/to/file.csv 5

# Custom file + top_n + simulations
python3 py/predict_all.py path/to/file.csv 5 50000
```

- **Algorithms**: Combines oso_next, kimi_next, weather_next, and monte_next
- **Parameters**:
  - `top_n`: Controls oso_next pattern group filtering (default: 3)
  - `simulations`: Controls monte_next simulation count (default: 10000)
- **Output**: All four detailed outputs → comparison table → individual accuracy tests
- **Cleanup**: Removes temp files in `data/tmp/` after completion

## CSV Format

Expected CSV format (semicolon or comma delimited):
```
draw_num;d1;d2;d3;d4;mega
1379;1;7;9;14;16;26
1380;2;5;10;15;17;27
...
```

- Column 1: Draw Number (ignored for pattern analysis)
- Columns 2–6: Main numbers (used for pattern analysis)
- Column 7: Mega/extra number (used for mega prediction in oso_next.py, ignored by oso_order2–oso_order5)

## ca_sloto

Scripts designed for ca_sloto draw data analysis and prediction.
