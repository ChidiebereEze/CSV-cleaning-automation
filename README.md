# CSV & Excel Data Cleaning

A small Python tool for cleaning CSV/XLSX files and preparing consistent datasets for analysis or reporting.

## Features

- Accepts CSV and XLSX input files.
- Standardizes column names (lowercase, trimmed, spaces/punctuation changed to underscores).
- Trims whitespace from text cells and converts blank cells to missing values.
- Removes exact duplicate rows and reports how many were removed.
- Reports missing values by column.
- Optionally validates specified date columns without silently changing their values.
- Can combine multiple cleaned files, aligning columns by name and removing exact duplicates from the combined result.
- Writes a JSON cleaning report alongside the output files.

## Requirements

Python 3.9+, pandas, and openpyxl (for Excel files).

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Clean one CSV:

```bash
python clean_single_csv.py input/orders.csv
```

Clean an Excel workbook:

```bash
python clean_single_csv.py input/orders.xlsx
```

Clean and combine multiple CSV files:

```bash
python clean_single_csv.py input/january.csv input/february.csv --combine
```

Validate date columns:

```bash
python clean_single_csv.py input/orders.csv --date-columns order_date delivery_date
```

Choose a different output folder:

```bash
python clean_single_csv.py input/orders.csv --output-dir results
```

## Output

The default output folder is `output/`.

- `*_cleaned.csv` or `*_cleaned.xlsx`: cleaned version of each input file.
- `combined_cleaned.csv`: created when `--combine` is used.
- `cleaning_report.json`: row counts, removed duplicates, standardized columns, missing-value counts, and requested date-validation results.

## Important notes

- Original input files are never overwritten.
- Duplicate removal means exact duplicate rows only. Similar-looking records are not automatically merged.
- Date validation is a check, not an automatic correction. Review invalid values before using the data.
- Combining files aligns columns by their standardized names. Review the combined output when source files use different meanings for similarly named columns.
- PDF extraction, fuzzy duplicate matching, and automatic correction of missing values are not included.

## Example workflow

1. Keep a copy of the original customer files.
2. Run the cleaner on a small sample first.
3. Review the cleaned output and `cleaning_report.json`.
4. Confirm duplicate and date-handling rules with the customer before processing the full dataset.
