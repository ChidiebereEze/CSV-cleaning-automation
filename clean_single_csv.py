"""Clean and optionally consolidate CSV/XLSX files.

Examples:
  python clean_single_csv.py input/orders.csv
  python clean_single_csv.py input/*.csv --combine
  python clean_single_csv.py input/orders.xlsx --date-columns order_date
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd


SUPPORTED = {".csv", ".xlsx"}


def normalize_columns(columns):
    normalized = []
    for column in columns:
        name = str(column).strip().lower()
        name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
        normalized.append(name or "unnamed_column")
    duplicates = pd.Index(normalized)[pd.Index(normalized).duplicated()].unique().tolist()
    if duplicates:
        raise ValueError(
            "Column names collide after standardization: "
            + ", ".join(duplicates)
        )
    return normalized


def read_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".xlsx":
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path.name}. Use CSV or XLSX.")


def clean_dataframe(frame: pd.DataFrame, date_columns: list[str]):
    original_rows = len(frame)
    original_columns = list(frame.columns)
    frame = frame.copy()
    frame.columns = normalize_columns(frame.columns)

    # Trim whitespace in text cells and treat whitespace-only cells as missing.
    for column in frame.select_dtypes(include=["object", "string"]).columns:
        frame[column] = frame[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        frame[column] = frame[column].replace("", pd.NA)

    missing = {
        str(column): int(count)
        for column, count in frame.isna().sum().items()
        if count
    }

    duplicate_count = int(frame.duplicated().sum())
    frame = frame.drop_duplicates().reset_index(drop=True)

    date_checks = {}
    for requested in date_columns:
        column = re.sub(r"[^a-z0-9]+", "_", requested.strip().lower()).strip("_")
        if column not in frame.columns:
            date_checks[column] = {"error": "Column not found"}
            continue
        values = frame[column]
        non_empty = values.notna()
        parsed = pd.to_datetime(values[non_empty], errors="coerce")
        date_checks[column] = {
            "non_empty_values": int(non_empty.sum()),
            "invalid_values": int(parsed.isna().sum()),
        }

    report = {
        "rows_before": original_rows,
        "rows_after": len(frame),
        "duplicate_rows_removed": duplicate_count,
        "columns_before": [str(value) for value in original_columns],
        "columns_after": list(frame.columns),
        "missing_values_by_column": missing,
        "date_validation": date_checks,
    }
    return frame, report


def output_path_for(source: Path, output_dir: Path) -> Path:
    return output_dir / f"{source.stem}_cleaned{source.suffix.lower()}"


def save_frame(frame: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    else:
        frame.to_excel(path, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Clean CSV/XLSX files and optionally consolidate them."
    )
    parser.add_argument("files", nargs="+", help="Input CSV or XLSX file paths")
    parser.add_argument("--output-dir", default="output", help="Output folder (default: output)")
    parser.add_argument(
        "--date-columns", nargs="*", default=[],
        help="Optional date columns to validate, e.g. --date-columns order_date invoice_date",
    )
    parser.add_argument(
        "--combine", action="store_true",
        help="Combine all supplied files into one CSV after standardizing their columns",
    )
    args = parser.parse_args()

    paths = [Path(value) for value in args.files]
    for path in paths:
        if not path.is_file():
            parser.error(f"Input file does not exist: {path}")
        if path.suffix.lower() not in SUPPORTED:
            parser.error(f"Unsupported file type: {path}. Use .csv or .xlsx")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    cleaned_frames = []

    try:
        for path in paths:
            original = read_file(path)
            cleaned, report = clean_dataframe(original, args.date_columns)
            destination = output_path_for(path, output_dir)
            save_frame(cleaned, destination)
            report.update({"input_file": str(path), "output_file": str(destination)})
            reports.append(report)
            cleaned_frames.append(cleaned)
            print(f"Cleaned {path.name}: {report['rows_before']} -> {report['rows_after']} rows")

        if args.combine:
            combined = pd.concat(cleaned_frames, ignore_index=True, sort=False)
            before_deduplication = len(combined)
            combined = combined.drop_duplicates().reset_index(drop=True)
            combined_path = output_dir / "combined_cleaned.csv"
            combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
            print(
                f"Combined {len(paths)} files: {before_deduplication} -> "
                f"{len(combined)} rows; saved to {combined_path}"
            )

        report_path = output_dir / "cleaning_report.json"
        report_path.write_text(
            json.dumps({"files": reports}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Cleaning report saved to {report_path}")

    except (OSError, ValueError, pd.errors.ParserError, ImportError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
