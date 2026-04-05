# ca_sloto Pattern Analysis

Scripts to analyze vertical patterns in ca_sloto draw data and predict the next draw.

## Scripts

### order2.py
Analyzes 2‑row vertical patterns in columns 2–6 and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order2.py

# Show all patterns from a custom file
python3 py/order2.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order2.py 5

# Show top 10 patterns from a custom file
python3 py/order2.py path/to/file.csv 10
```

- **Output**: 2‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: 2–6 (skips draw_num and mega)
- **Window size**: 2 rows

### order3.py
Analyzes 3‑row vertical patterns in columns 2–6 and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order3.py

# Show all patterns from a custom file
python3 py/order3.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order3.py 5

# Show top 10 patterns from a custom file
python3 py/order3.py path/to/file.csv 10
```

- **Output**: 3‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: 2–6 (skips draw_num and mega)
- **Window size**: 3 rows

### order4.py
Analyzes 4‑row vertical patterns in columns 2–6 and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order4.py

# Show all patterns from a custom file
python3 py/order4.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order4.py 5

# Show top 10 patterns from a custom file
python3 py/order4.py path/to/file.csv 10
```

- **Output**: 4‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: 2–6 (skips draw_num and mega)
- **Window size**: 4 rows

### order5.py
Analyzes 5‑row vertical patterns in columns 2–6 and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order5.py

# Show all patterns from a custom file
python3 py/order5.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order5.py 5

# Show top 10 patterns from a custom file
python3 py/order5.py path/to/file.csv 10
```

- **Output**: 5‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: 2–6 (skips draw_num and mega)
- **Window size**: 5 rows

### order_m2.py
Analyzes 2‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order_m2.py

# Show all patterns from a custom file
python3 py/order_m2.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order_m2.py 5

# Show top 10 patterns from a custom file
python3 py/order_m2.py path/to/file.csv 10
```

- **Output**: 2‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 2 rows

### order_m3.py
Analyzes 3‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order_m3.py

# Show all patterns from a custom file
python3 py/order_m3.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order_m3.py 5

# Show top 10 patterns from a custom file
python3 py/order_m3.py path/to/file.csv 10
```

- **Output**: 3‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 3 rows

### order_m4.py
Analyzes 4‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order_m4.py

# Show all patterns from a custom file
python3 py/order_m4.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order_m4.py 5

# Show top 10 patterns from a custom file
python3 py/order_m4.py path/to/file.csv 10
```

- **Output**: 4‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 4 rows

### order_m5.py
Analyzes 5‑row vertical patterns in the mega column (column 7) and shows frequencies.

```bash
# Show all patterns (default file)
python3 py/order_m5.py

# Show all patterns from a custom file
python3 py/order_m5.py path/to/file.csv

# Show top 5 patterns (default file)
python3 py/order_m5.py 5

# Show top 10 patterns from a custom file
python3 py/order_m5.py path/to/file.csv 10
```

- **Output**: 5‑value tuples and their frequencies, sorted by descending frequency
- **Columns used**: Column 7 (mega number only)
- **Window size**: 5 rows

### order_next.py
Predicts the next draw using hierarchical fallback approaches for both main numbers and mega number.

```bash
# Use default file
python3 py/order_next.py

# Specify a custom file
python3 py/order_next.py path/to/file.csv
```

- **Main numbers priority**: order4 → order5 → order4 → order3 → order2 fallback hierarchy
- **Mega number priority**: order_m5 → order_m4 → order_m3 → order_m2 fallback hierarchy
- **Output**: Shows all prediction stages with clear fallback indicators for columns 2–6 and mega (column 7)
- **Target**: Predicts the draw immediately after the last row in the input file

### order_next_minus_one.py
Tests prediction accuracy by excluding the last draw and predicting it.

```bash
# Use default file
python3 py/order_next_minus_one.py

# Specify a custom file
python3 py/order_next_minus_one.py path/to/file.csv
```

- **Method**: Excludes last draw, predicts it, then compares with actual
- **Output**: Shows predicted vs actual values with accuracy percentage
- **Purpose**: Validates prediction model performance

### kimi_next.py
Ensemble prediction algorithm combining frequency analysis, gap analysis, Markov transitions, and positional bias.

```bash
# Use default file
python3 py/kimi_next.py

# Specify a custom file
python3 py/kimi_next.py path/to/file.csv
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
python3 py/kimi_next_minus_one.py
```

- **Method**: Excludes last draw, runs kimi_next, compares prediction with actual
- **Output**: Shows predicted vs actual with accuracy percentage

### weather_next.py
"Weather-like" prediction using trend, momentum, cycle, pressure, and drift analysis.

```bash
# Use default file
python3 py/weather_next.py

# Specify a custom file
python3 py/weather_next.py path/to/file.csv
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
python3 py/weather_next_minus_one.py
```

- **Method**: Excludes last draw, runs weather_next, compares prediction with actual
- **Output**: Shows predicted vs actual with accuracy percentage

### all_next.py
Runs all three prediction algorithms (order_next, kimi_next, weather_next) and displays their results side by side for comparison.

```bash
# Use default file
python3 py/all_next.py

# Specify a custom file
python3 py/all_next.py path/to/file.csv
```

- **Algorithms**: Combines order_next, kimi_next, and weather_next
- **Output**: Table showing all three predictions + individual accuracy tests
- **Purpose**: Compare different prediction approaches on the same data

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
- Column 7: Mega/extra number (used for mega prediction in order_next.py, ignored by order2–order5)

## ca_sloto

Scripts designed for ca_sloto draw data analysis and prediction.
