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
├── exclude/          # Contrarian algorithm (differs from all 4)
│   ├── exclude_next.py
│   └── exclude_next_minus_one.py
└── predict_all.py    # Compare all five algorithms
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

- **Main numbers priority**: 3-row heuristic → oso_order5 → oso_order4 → oso_order3 → oso_order2 fallback hierarchy
- **Mega number priority**: oso_order_m5 → oso_order_m4 → oso_order_m3 → oso_order_m2 fallback hierarchy
- **top_n parameter**: When specified, shows additional "PREDICTION BASED ON TOP N PATTERN GROUPS" section with patterns used for each column
- **Source tracking**: Each predicted number is annotated with its source (e.g., `order5 fallback`, `3-row pattern`, `order2 fallback`)
- **Duplicate resolution**: Columns 1-5 are guaranteed to have unique numbers; duplicates are replaced using historical column frequency
- **Weak-signal detection**: If ≥3/5 columns fall back to `order2`, the prediction is marked **weak** and will be suppressed in `predict_all.py` output and `exclude_next`'s input set
- **Output**: Shows all prediction stages + final prediction (with source) + optional top-N pattern analysis
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

- **Components** (weighted ensemble score, max = 1.0):
  - **Frequency** (weight 0.30): Most common numbers per column
  - **Gap analysis** (weight 0.25): How "due" a number is (proximity to average gap)
  - **Markov transitions** (weight 0.30): Transition probabilities from the last value
  - **Positional bias** (weight 0.15): Column-specific distributions
- **Source tracking**: Each predicted number is annotated with `ensemble score=X.XXX, dominant=<component> (X.XXX)` indicating which signal contributed most
- **Duplicate resolution**: Columns 1-5 are guaranteed unique; duplicates fall to next-best ranked candidate by ensemble score
- **Output**: Shows analysis per column + final prediction with source + component breakdown
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

- **Metrics** (weighted score, max = 1.0):
  - **Trend** (weight 0.25): Direction of movement (rising/falling/stable)
  - **Momentum** (weight 0.20): Volatility/speed of change
  - **Cycle** (weight 0.25): Repeating patterns every N draws
  - **Pressure** (weight 0.20): Clustering tendency around recent average
  - **Drift** (weight 0.10): Short-term vs long-term divergence
- **Source tracking**: Each predicted number is annotated with `weather score=X.XXX, dominant=<component> (X.XXX)`
- **Duplicate resolution**: Columns 1-5 are guaranteed unique; duplicates fall to next-best ranked candidate by weather score
- **Output**: Shows weather analysis per column + final prediction with source + component breakdown
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

- **Approach** (3 rotating sampling methods):
  - **Distribution sampling**: Weighted random selection from historical frequencies
  - **Transition chains**: Sampling from Markov-style state transitions
  - **Correlation modeling**: Column-to-column dependency simulation
- **Simulations**: Default 10,000 runs (configurable)
- **Source tracking**: Each predicted number is annotated with `Monte Carlo (N sims, confidence=X.X%, hits=N)`
- **Duplicate resolution**: Columns 1-5 are guaranteed unique; duplicates fall to next-best by simulation frequency
- **Output**: Shows simulation statistics, confidence levels, top alternatives per column, and final prediction with source
- **Includes**: Automatically runs `monte_next_minus_one` for accuracy test

### monte_next_minus_one.py
Tests monte_next prediction accuracy by excluding the last draw.

```bash
python3 py/monte/monte_next_minus_one.py
```

- **Method**: Excludes last draw, runs monte_next, compares prediction with actual
- **Output**: Shows predicted vs actual with accuracy percentage

## EXCLUDE Contrarian Prediction (py/exclude/)

### exclude_next.py
A **novel, independent** algorithm that does NOT reuse oso/kimi/weather/monte scoring. Its predictions are also forced to **differ** from every other algorithm's prediction for each column.

```bash
# Use default file
python3 py/exclude/exclude_next.py

# Specify a custom file
python3 py/exclude/exclude_next.py path/to/file.csv

# Custom file + top_n + simulations (used to query the other algorithms)
python3 py/exclude/exclude_next.py path/to/file.csv 3 10000
```

- **Method**: Contrarian Deficit + Staleness scoring
  - **Deficit** (weight 0.60): `expected_count - actual_count` — favors under-represented numbers
  - **Staleness** (weight 0.40): Draws since last appearance — favors overdue numbers
  - `score = 0.6 × deficit_norm + 0.4 × staleness_norm`
- **Exclusion constraint**: The chosen value for each column is guaranteed to differ from the top prediction of `oso_next`, `kimi_next`, `weather_next`, and `monte_next`. If the top-ranked candidate collides, it falls through to the next-best.
- **Source tracking**: Each number is annotated with `deficit+staleness score=X.XXX (count=N, stale=N draws, rank#N, excluded=[...])`
- **Duplicate resolution**: Columns 1-5 guaranteed unique while still respecting the exclusion set
- **Includes**: Automatically runs `exclude_next_minus_one` for accuracy test

### exclude_next_minus_one.py
Tests exclude_next prediction accuracy by excluding the last draw.

```bash
python3 py/exclude/exclude_next_minus_one.py
```

## Comparison Script

### predict_all.py
Runs all five prediction algorithms (oso_next, kimi_next, weather_next, monte_next, exclude_next) and displays results side by side. Detailed outputs are printed inline; all FINAL PREDICTION blocks are aggregated at the end.

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

- **Algorithms**: oso_next, kimi_next, weather_next, monte_next, exclude_next
- **Parameters**:
  - `top_n`: Controls oso_next pattern group filtering (default: 3)
  - `simulations`: Controls monte_next simulation count (default: 10000)
- **Output flow**:
  1. Detailed output from each algorithm (FINAL PREDICTION extracted from inline output)
  2. `# ALL FINAL PREDICTIONS` — all FINAL PREDICTION blocks grouped together, each with per-column source/reason
  3. Side-by-side comparison table for the next draw
  4. Algorithm characteristics summary
  5. Individual `minus_one` accuracy tests
- **Weak-signal handling**: If `oso_next` is flagged weak (≥3/5 columns from order2 fallback):
  - `oso_next` is suppressed from the FINAL PREDICTIONS section, comparison table, and accuracy test
  - `exclude_next` automatically drops `oso` from its exclusion set
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

## Recent Changes

### Source tracking for every prediction
All 4 core algorithms (`oso`, `kimi`, `weather`, `monte`) now display **how** each predicted number was computed in their FINAL PREDICTION output, e.g.:

```
OSO_NEXT - FINAL PREDICTION (with source)
  Column 1: 1   <- order5 fallback (5-row pattern)
  Column 5: 39  <- 3-row pattern (38, 39, 45) (freq=1)
  Mega:     15  <- order_m5 (5-row mega pattern)

KIMI_NEXT - FINAL PREDICTION (with source)
  Column 1: 1   <- ensemble score=0.613, dominant=frequency (0.300)

WEATHER_NEXT - FINAL PREDICTION (with source)
  Column 1: 3   <- weather score=0.445, dominant=trend (0.181)

MONTE_NEXT - FINAL PREDICTION (with source)
  Column 1: 1   <- Monte Carlo (10,000 sims, confidence=8.3%, hits=830)
```

### Duplicate resolution across all algorithms
All algorithms now guarantee **columns 1-5 have unique numbers** (matching lottery rules). Each uses its own scoring method's ranked candidates to pick the next-best replacement when duplicates are detected:

| Algorithm | Tie-break when duplicate |
|-----------|--------------------------|
| `oso_next` | Column's historical frequency |
| `kimi_next` | Next-best ensemble score |
| `weather_next` | Next-best weather score |
| `monte_next` | Next-best simulation frequency |
| `exclude_next` | Next-best deficit+staleness score (with exclusion constraint) |

### Weak-signal detection in oso_next
`oso_next` now flags its prediction as **weak** when ≥3/5 columns fall back all the way to `order2` (which almost always matches and carries the least signal). When weak:
- `predict_all.py` suppresses `oso_next` from the comparison table, FINAL PREDICTIONS group, and accuracy test
- `exclude_next` automatically drops it from its exclusion set

### New algorithm: exclude_next
Added a **5th, independent** algorithm (`py/exclude/exclude_next.py`) that uses a contrarian Deficit+Staleness scoring method and forces its predictions to differ from all 4 other algorithms' predictions per column. See the EXCLUDE section above.

### Grouped FINAL PREDICTION output
`predict_all.py` now prints each algorithm's detailed analysis first, then groups **all FINAL PREDICTION blocks together** under a `# ALL FINAL PREDICTIONS` section for easy comparison, then shows the comparison table and accuracy tests.
