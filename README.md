# ca_sloto Pattern Analysis

Scripts to analyze vertical patterns in ca_sloto draw data and predict the next draw.

## Folder Structure

```
py/
├── utils.py          # Shared utilities (load_rows, pattern_fallback, resolve_duplicates, …)
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
├── hotcold/          # Hot/Cold frequency analysis
│   ├── hotcold_next.py
│   └── hotcold_next_minus_one.py
└── predict_all.py    # Compare all six algorithms
```

## Shared Utilities (py/utils.py)

Central module imported by every prediction script. Eliminates the repeated boilerplate that previously existed across 12+ files.

| Function | Description |
|---|---|
| `load_csv(path)` | Reads CSV, auto-detects `,` or `;` delimiter, skips header row. Returns `(rows, header, delimiter)` |
| `load_rows(path)` | Convenience wrapper — returns `rows` only |
| `write_temp_csv(path, rows, header, delimiter, suffix)` | Writes a temp CSV to `path.parent/tmp/` for minus-one tests |
| `pattern_fallback(rows, order, col_range)` | Generic N-row look-back predictor. Replaces the 8 hand-written `*_fallback()` functions that were previously in `oso_next.py` |
| `resolve_duplicates(prediction, ranked_candidates)` | Ensures columns 1–5 have unique values by substituting next-best candidates |

---

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

- **Main numbers priority**: 3-row heuristic → order5 → order4 → order3 → order2 (all via `pattern_fallback()` from utils)
- **Mega number priority**: order_m5 → order_m4 → order_m3 → order_m2 (same generic function, `col_range=[6]`)
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

- **`seed` parameter** (new): Pass an integer seed for reproducible results across runs. Useful for debugging or comparing runs. Call from Python as `monte_next(csv_path, simulations=10000, seed=42)`.
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
- **`precomputed_preds` parameter** (new): When called from `predict_all.py`, the other algorithms' results are passed in directly (as `{'oso': ..., 'kimi': ..., 'weather': ..., 'monte': ...}`), so those four algorithms are not run a second time. When called standalone (without this argument), it runs them internally as before.
- **Source tracking**: Each number is annotated with `deficit+staleness score=X.XXX (count=N, stale=N draws, rank#N, excluded=[...])`
- **Duplicate resolution**: Columns 1-5 guaranteed unique while still respecting the exclusion set
- **Includes**: Automatically runs `exclude_next_minus_one` for accuracy test

### exclude_next_minus_one.py
Tests exclude_next prediction accuracy by excluding the last draw.

```bash
python3 py/exclude/exclude_next_minus_one.py
```

## HOTCOLD Frequency Analysis (py/hotcold/)

### hotcold_next.py
Predicts the next draw by classifying each number as **Hot**, **Warm**, **Cool**, **Cold**, or **Ice** based on recent frequency relative to statistical expectation, then ranking all candidates with a multi-window composite score.

```bash
# Use default file (recent_window=20, medium_window=40)
python3 py/hotcold/hotcold_next.py

# Specify custom file
python3 py/hotcold/hotcold_next.py path/to/file.csv

# Custom file + recent window
python3 py/hotcold/hotcold_next.py path/to/file.csv 15

# Custom file + both windows
python3 py/hotcold/hotcold_next.py path/to/file.csv 15 30
```

**Classification labels** (based on recent frequency vs uniform expectation `1 / col_size`):

| Label | Condition |
|---|---|
| **Hot** | recent rate ≥ 2.0× expected — on a streak |
| **Warm** | recent rate ≥ 1.2× expected — above average |
| **Cool** | recent rate ≥ 0.5× expected — below average |
| **Cold** | recent rate < 0.5× expected — going quiet |
| **Ice** | zero appearances in the recent window |

**Score formula** (weights sum to 1.0):
```
score = 0.45 × recent_norm
      + 0.25 × medium_norm
      + 0.20 × alltime_norm
      + 0.10 × due_norm
```

- **recent_norm** (weight 0.45): frequency in last `recent_window` draws, relative to the hottest number in that window
- **medium_norm** (weight 0.25): same but over `medium_window` draws — confirms the trend
- **alltime_norm** (weight 0.20): all-time historical frequency — long-term baseline
- **due_norm** (weight 0.10): gap between historical rate and recent rate — rewards numbers that *should* appear often but have recently gone quiet

**Parameters:**
- `recent_window` (default 20): how many recent draws define "hot" classification
- `medium_window` (default 40): medium look-back for the second frequency component

**Source tracking**: Each predicted number is annotated with its classification label, dominant component, and raw counts:
```
Column 1: 7  <- hotcold score=0.412 [Hot] dominant=recent (0.369) | recent=4/20, alltime=47/300
```

**Duplicate resolution**: Columns 1-5 guaranteed unique; falls to next-best scored candidate.
**Includes**: Automatically runs `hotcold_next_minus_one` for accuracy test.

### hotcold_next_minus_one.py
Tests hotcold_next accuracy by excluding the last draw.

```bash
python3 py/hotcold/hotcold_next_minus_one.py
python3 py/hotcold/hotcold_next_minus_one.py path/to/file.csv 20 40
```

- **Method**: Excludes last draw, runs hotcold_next, compares prediction with actual
- **Output**: Shows predicted vs actual with ` <--` markers on correct values and accuracy percentage

---

## Comparison Script

### predict_all.py
Runs all six prediction algorithms (oso_next, kimi_next, weather_next, monte_next, exclude_next, hotcold_next) and displays results side by side. Detailed outputs are printed inline; all FINAL PREDICTION blocks are aggregated at the end.

```bash
# Use default file (top_n=3, simulations=10000, recent=20, medium=40)
python3 py/predict_all.py

# Specify custom file
python3 py/predict_all.py path/to/file.csv

# Custom file + top_n
python3 py/predict_all.py path/to/file.csv 5

# Custom file + top_n + simulations
python3 py/predict_all.py path/to/file.csv 5 50000

# All parameters
python3 py/predict_all.py path/to/file.csv 5 50000 15 30
```

- **Algorithms**: oso_next, kimi_next, weather_next, monte_next, exclude_next, hotcold_next
- **Parameters**:
  - `top_n`: Controls oso_next pattern group filtering (default: 3)
  - `simulations`: Controls monte_next simulation count (default: 10000)
  - `recent_window`: Controls hotcold_next recent window (default: 20)
  - `medium_window`: Controls hotcold_next medium window (default: 40)
- **No double-running**: oso, kimi, weather, and monte results are computed once and passed directly into `exclude_next` via `precomputed_preds`. Previously these four algorithms were run a second time inside `exclude_next`.
- **Output flow**:
  1. Detailed output from each algorithm (FINAL PREDICTION extracted from inline output)
  2. `# ALL FINAL PREDICTIONS` — all FINAL PREDICTION blocks grouped together, each with per-column source/reason
  3. Side-by-side comparison table for the next draw
  4. Algorithm characteristics summary
  5. Individual `minus_one` accuracy tests
- **Weak-signal handling**: If `oso_next` is flagged weak (≥3/5 columns from order2 fallback):
  - `oso_next` is suppressed from the FINAL PREDICTIONS section, comparison table, and accuracy test
  - `exclude_next` automatically drops `oso` from its exclusion set
- **Accuracy tests**: Runs all six `*_minus_one` checks at the end
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

## Changelog

Changes are listed newest-first.

---

### hotcold_next — new 6th algorithm

Added `py/hotcold/hotcold_next.py` and `py/hotcold/hotcold_next_minus_one.py`.

Each number per column is classified as **Hot / Warm / Cool / Cold / Ice** based on its recent appearance rate vs the uniform expectation. The composite score combines three time windows and a due factor:

```
score = 0.45 × recent_norm + 0.25 × medium_norm + 0.20 × alltime_norm + 0.10 × due_norm
```

The classification label appears next to every prediction:
```
Column 3: 18  <- hotcold score=0.412 [Hot] dominant=recent (0.369) | recent=4/20, alltime=47/300
```

`predict_all.py` was updated to run hotcold as algorithm `[6]` and include it in the comparison table. Two new optional CLI arguments: `recent_window` (default 20) and `medium_window` (default 40).

---

### Shared utilities — py/utils.py

Introduced `py/utils.py` to replace repeated boilerplate across 19 files:

| Function | What it replaced |
|---|---|
| `load_rows(path)` | CSV loading block copy-pasted 12+ times |
| `load_csv(path)` | Same, but also returns header and delimiter (used by minus-one scripts) |
| `write_temp_csv(...)` | Temp-file creation in every minus-one script |
| `pattern_fallback(rows, order, col_range)` | 8 nearly-identical `*_fallback()` functions in `oso_next.py` |
| `resolve_duplicates(pred, ranked)` | Duplicate-resolution loop copy-pasted into all 5 algorithm files |

---

### Fixed: exclude_next double-ran all four sub-algorithms

`predict_all.py` ran oso → kimi → weather → monte, then `exclude_next` silently re-ran all four to build its exclusion set — each algorithm ran **twice**.

`exclude_next` now accepts `precomputed_preds`. `predict_all.py` passes results directly:
```python
exclude_next(csv_path, precomputed_preds={"oso": oso_result, "kimi": kimi_result, ...})
```
When called standalone the parameter is omitted and the sub-algorithms run as before.

---

### New: seed parameter in monte_next

`monte_next()` accepts an optional `seed` for reproducible runs:
```python
monte_next(csv_path, simulations=10000, seed=42)
```

---

### Source tracking for every prediction

All algorithms annotate each predicted number with *how* it was chosen:
```
OSO_NEXT    Column 1: 1   <- order5 fallback (5-row pattern)
KIMI_NEXT   Column 1: 1   <- ensemble score=0.613, dominant=frequency (0.300)
WEATHER     Column 1: 3   <- weather score=0.445, dominant=trend (0.181)
MONTE       Column 1: 1   <- Monte Carlo (10,000 sims, confidence=8.3%, hits=830)
HOTCOLD     Column 1: 7   <- hotcold score=0.412 [Hot] dominant=recent (0.369)
```

---

### Duplicate resolution across all algorithms

All algorithms guarantee columns 1–5 have unique values. Each uses its own scoring method's ranked list to pick the next-best replacement:

| Algorithm | Tie-break when duplicate |
|---|---|
| `oso_next` | Historical column frequency |
| `kimi_next` | Next-best ensemble score |
| `weather_next` | Next-best weather score |
| `monte_next` | Next-best simulation frequency |
| `exclude_next` | Next-best deficit+staleness score (respects exclusion set) |
| `hotcold_next` | Next-best hotcold composite score |

---

### Weak-signal detection in oso_next

`oso_next` flags its prediction as **weak** when ≥3/5 columns fall back to `order2`. When weak, `predict_all.py` suppresses it from the comparison table and `exclude_next` drops it from its exclusion set.

---

### Correct-prediction markers in minus_one tests

All 6 `*_minus_one.py` scripts append ` <--` to any value matching the actual draw:
```
Predicted draw:
  Column 1: 7
  Column 2: 3 <--
  Column 3: 8
  Column 4: 20
  Column 5: 46
  Mega: 6
```

---

### Grouped FINAL PREDICTION output

`predict_all.py` prints each algorithm's detailed analysis first, then groups all FINAL PREDICTION blocks under `# ALL FINAL PREDICTIONS` for easy side-by-side comparison.
