"""Deduplicate, validate, normalize, and enrich business data."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from automation_common import write_output


def cleanup_csv(input_file: Path) -> dict:
    with input_file.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    seen = set()
    cleaned = []
    duplicates = 0
    invalid_emails = []
    for row in rows:
        normalized = {key.strip().lower().replace(" ", "_"): (value or "").strip() for key, value in row.items()}
        key = tuple(sorted(normalized.items()))
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        email = normalized.get("email", "")
        if email and not re.match(r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$", email):
            invalid_emails.append(email)
        cleaned.append(normalized)
    return {
        "tool": "Data Cleanup",
        "input_file": input_file.name,
        "input_rows": len(rows),
        "clean_rows": len(cleaned),
        "duplicates_removed": duplicates,
        "invalid_emails": invalid_emails,
        "cleaned_preview": cleaned[:25],
        "enrichment_suggestions": ["Company domain lookup", "Phone country normalization", "Address/state standardization"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Advanced data cleanup for CSV files.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data_cleanup_report.json"))
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()
    print(write_output(cleanup_csv(args.input), args.output, args.format))


if __name__ == "__main__":
    main()

