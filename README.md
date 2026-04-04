# ca_sloto Pattern Analysis

Scripts to analyze vertical patterns in ca_sloto draw data and predict the next draw.

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

### order_next.py
Predicts the next draw using 4‑row pattern frequencies with a two‑step approach.

```bash
# Use default file
python3 py/order_next.py

# Specify a custom file
python3 py/order_next.py path/to/file.csv
```

- **Step 1**: Uses 4‑row patterns to predict the next value
- **Step 2**: "Disappears" the 4th row and uses historical 3‑row → 4th‑row mappings to predict
- **Output**: Shows both predictions for comparison
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

## ca_sloto

Scripts designed for ca_sloto draw data analysis and prediction.
