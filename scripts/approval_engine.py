#!/usr/bin/env python3
"""
Parse and enforce Markdown approval records.

An approval is valid only when:
- the file exists
- Status is APPROVED or APPROVED_WITH_COMMENTS
- Reviewer is populated
- Date is populated and ISO formatted
- all checklist items are checked
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

VALID_STATUSES = {
    "PENDING",
    "APPROVED",
    "APPROVED_WITH_COMMENTS",
    "REJECTED",
    "EXPIRED",
}
PASSING_STATUSES = {"APPROVED", "APPROVED_WITH_COMMENTS"}

FIELD_PATTERNS = {
    "status": re.compile(r"^\s*Status:\s*(.+?)\s*$", re.MULTILINE),
    "reviewer": re.compile(r"^\s*Reviewer:\s*(.+?)\s*$", re.MULTILINE),
    "date": re.compile(r"^\s*Date:\s*(.+?)\s*$", re.MULTILINE),
}

UNCHECKED_ITEM = re.compile(r"^\s*-\s*\[\s\]\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ApprovalResult:
    file: str
    valid: bool
    status: str | None
    reviewer: str | None
    date: str | None
    unchecked_items: tuple[str, ...]
    errors: tuple[str, ...]


def extract_field(text: str, name: str) -> str | None:
    match = FIELD_PATTERNS[name].search(text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def validate_iso_date(value: str | None) -> bool:
    if not value:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def evaluate_approval(path: Path) -> ApprovalResult:
    errors: list[str] = []

    if not path.exists():
        return ApprovalResult(
            file=str(path),
            valid=False,
            status=None,
            reviewer=None,
            date=None,
            unchecked_items=(),
            errors=("Approval file does not exist.",),
        )

    text = path.read_text(encoding="utf-8")
    status = extract_field(text, "status")
    reviewer = extract_field(text, "reviewer")
    approval_date = extract_field(text, "date")
    unchecked_items = tuple(UNCHECKED_ITEM.findall(text))

    if status not in VALID_STATUSES:
        errors.append(f"Invalid or missing status: {status!r}")
    elif status not in PASSING_STATUSES:
        errors.append(f"Approval status does not authorize progression: {status}")

    if not reviewer:
        errors.append("Reviewer is missing.")

    if not validate_iso_date(approval_date):
        errors.append("Date is missing or is not ISO format YYYY-MM-DD.")

    if unchecked_items:
        errors.append(f"{len(unchecked_items)} checklist item(s) remain unchecked.")

    return ApprovalResult(
        file=str(path),
        valid=not errors,
        status=status,
        reviewer=reviewer,
        date=approval_date,
        unchecked_items=unchecked_items,
        errors=tuple(errors),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Markdown approval record.")
    parser.add_argument("approval_file")
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    approval_path = Path(args.approval_file)
    if not approval_path.is_absolute():
        approval_path = repo_root / approval_path

    result = evaluate_approval(approval_path)
    payload = asdict(result)

    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = repo_root / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
