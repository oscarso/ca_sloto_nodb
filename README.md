# Lottery Pattern Analysis

Scripts to analyze vertical patterns in lottery draw data and predict the next draw.

## Scripts

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

### order3next.py
Predicts the next draw using 3‑row pattern frequencies.

```bash
# Use default file
python3 py/order3next.py

# Specify a custom file
python3 py/order3next.py path/to/file.csv
```

- **How it works**: Learns which 4th value most commonly follows each 3‑value vertical pattern, then applies this to the last 3 rows
- **Output**: Predicted next value for each column 2–6
- **Target**: Predicts the draw immediately after the last row in the input file

### order4next.py
Predicts the next draw using 4‑row pattern frequencies.

```bash
# Use default file
python3 py/order4next.py

# Specify a custom file
python3 py/order4next.py path/to/file.csv
```

- **How it works**: Learns which 5th value most commonly follows each 4‑value vertical pattern, then applies this to the last 4 rows
- **Output**: Predicted next value for each column 2–6
- **Target**: Predicts the draw immediately after the last row in the input file

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
- Column 7: Mega/extra number (ignored for pattern analysis)
