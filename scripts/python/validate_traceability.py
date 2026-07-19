from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTERS_DIR = PROJECT_ROOT / "registers"

SOURCE_REGISTER = REGISTERS_DIR / "source-register.csv"

TRACEABILITY_REGISTERS = {
    "action-register.csv": "action_id",
    "decision-register.csv": "decision_id",
    "risk-register.csv": "risk_id",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file and return its rows as dictionaries."""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_source_ids(raw_value: str) -> list[str]:
    """
    Parse one or more source IDs.

    Supported formats:
    - SRC-0001
    - SRC-0001,SRC-0002
    - SRC-0001;SRC-0002
    """
    normalized_value = raw_value.replace(",", ";")

    return [
        source_id.strip()
        for source_id in normalized_value.split(";")
        if source_id.strip()
    ]


def main() -> int:
    errors: list[str] = []

    source_rows = read_csv(SOURCE_REGISTER)

    if not source_rows:
        print("Traceability validation failed:")
        print("- Source register is missing or empty.")
        return 1

    valid_source_ids = {
        row.get("source_id", "").strip()
        for row in source_rows
        if row.get("source_id", "").strip()
    }

    for register_name, record_id_column in TRACEABILITY_REGISTERS.items():
        register_path = REGISTERS_DIR / register_name

        if not register_path.exists():
            errors.append(f"Missing register: {register_name}")
            continue

        rows = read_csv(register_path)
        seen_ids: set[str] = set()

        for row_number, row in enumerate(rows, start=2):
            record_id = row.get(record_id_column, "").strip()
            description = (
                row.get("description", "").strip()
                or row.get("decision", "").strip()
            )

            source_ids_raw = row.get("source_id", "").strip()
            source_ids = parse_source_ids(source_ids_raw)

            if not record_id:
                errors.append(
                    f"{register_name} row {row_number}: "
                    f"missing {record_id_column}"
                )
            elif record_id in seen_ids:
                errors.append(
                    f"{register_name} row {row_number}: "
                    f"duplicate ID {record_id}"
                )
            else:
                seen_ids.add(record_id)

            if not description:
                errors.append(
                    f"{register_name} row {row_number}: "
                    "missing description or decision"
                )

            if not source_ids:
                errors.append(
                    f"{register_name} row {row_number}: "
                    "missing source_id"
                )
                continue

            for source_id in source_ids:
                if source_id not in valid_source_ids:
                    errors.append(
                        f"{register_name} row {row_number}: "
                        f"unknown source_id {source_id}"
                    )

    if errors:
        print("Traceability validation failed:")

        for error in errors:
            print(f"- {error}")

        return 1

    print("Traceability validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())