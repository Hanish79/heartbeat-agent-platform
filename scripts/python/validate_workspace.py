from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRECTORIES = [
    PROJECT_ROOT / "documents" / "01-raw-source-documents",
    PROJECT_ROOT / "documents" / "02-source-summaries",
    PROJECT_ROOT / "documents" / "03-approved-outputs",
    PROJECT_ROOT / "documents" / "04-draft-working-area",
    PROJECT_ROOT / "registers",
    PROJECT_ROOT / "logs",
]

REQUIRED_FILES = [
    PROJECT_ROOT / "CLAUDE.md",
    PROJECT_ROOT / "registers" / "source-register.csv",
]

REQUIRED_SOURCE_COLUMNS = {
    "source_id",
    "file_name",
    "relative_path",
    "file_type",
    "size_bytes",
    "modified_utc",
    "sha256",
    "status",
    "review_status",
    "owner",
    "notes",
}


def validate_directories(errors: list[str]) -> None:
    for directory in REQUIRED_DIRECTORIES:
        if not directory.exists():
            errors.append(f"Missing directory: {directory}")


def validate_files(errors: list[str]) -> None:
    for file_path in REQUIRED_FILES:
        if not file_path.exists():
            errors.append(f"Missing file: {file_path}")


def validate_source_register(errors: list[str]) -> None:
    register = PROJECT_ROOT / "registers" / "source-register.csv"

    if not register.exists():
        return

    with register.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)

        actual_columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_SOURCE_COLUMNS - actual_columns

        if missing_columns:
            errors.append(
                "Source register is missing columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

        if not rows:
            errors.append("Source register contains no source documents.")

        source_ids = [row.get("source_id", "") for row in rows]

        if len(source_ids) != len(set(source_ids)):
            errors.append("Duplicate source IDs found in source-register.csv.")


def main() -> int:
    errors: list[str] = []

    validate_directories(errors)
    validate_files(errors)
    validate_source_register(errors)

    if errors:
        print("Workspace validation failed:")

        for error in errors:
            print(f"- {error}")

        return 1

    print("Workspace validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())