#!/usr/bin/env python3
"""
Machine-enforced JSON approval engine for Heartbeat governance gates.

Supported gates:
- proposal
- architecture
- deployment

The engine fails closed when an approval file is:
- missing
- malformed
- pending
- rejected
- expired
- missing approver details
- missing approval timestamp
- missing required evidence
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_STATUSES = {
    "PENDING",
    "APPROVED",
    "APPROVED_WITH_CONDITIONS",
    "REJECTED",
    "EXPIRED",
}
PASSING_STATUSES = {"APPROVED", "APPROVED_WITH_CONDITIONS"}
EXPECTED_GATES = {"proposal", "architecture", "deployment"}


@dataclass(frozen=True)
class ApprovalResult:
    file: str
    valid: bool
    gate: str | None
    status: str | None
    approver_name: str | None
    approver_role: str | None
    approved_at: str | None
    expires_at: str | None
    unverified_evidence: tuple[str, ...]
    errors: tuple[str, ...]


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "Approval file does not exist."
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON: {exc}"


def evaluate_approval(path: Path, expected_gate: str | None = None) -> ApprovalResult:
    payload, load_error = load_json(path)
    if payload is None:
        return ApprovalResult(
            file=str(path),
            valid=False,
            gate=None,
            status=None,
            approver_name=None,
            approver_role=None,
            approved_at=None,
            expires_at=None,
            unverified_evidence=(),
            errors=(load_error or "Unknown approval read error.",),
        )

    errors: list[str] = []
    gate = payload.get("gate")
    status = payload.get("status")
    approver = payload.get("approver") or {}
    approver_name = (approver.get("name") or "").strip() or None
    approver_role = (approver.get("role") or "").strip() or None
    approved_at = payload.get("approved_at")
    expires_at = payload.get("expires_at")
    evidence = payload.get("evidence")

    if gate not in EXPECTED_GATES:
        errors.append(f"Invalid gate: {gate!r}.")
    if expected_gate and gate != expected_gate:
        errors.append(f"Expected gate {expected_gate!r}, found {gate!r}.")

    if status not in VALID_STATUSES:
        errors.append(f"Invalid status: {status!r}.")
    elif status not in PASSING_STATUSES:
        errors.append(f"Gate is not approved: {status}.")

    if not approver_name:
        errors.append("Approver name is missing.")
    if not approver_role:
        errors.append("Approver role is missing.")

    approved_dt = parse_datetime(approved_at)
    if approved_dt is None:
        errors.append("approved_at is missing or invalid ISO-8601.")

    expires_dt = parse_datetime(expires_at) if expires_at else None
    if expires_at and expires_dt is None:
        errors.append("expires_at is invalid ISO-8601.")
    if expires_dt and expires_dt <= datetime.now(timezone.utc):
        errors.append("Approval has expired.")

    if not isinstance(evidence, list):
        errors.append("Evidence must be a list.")
        evidence = []

    unverified = tuple(
        str(item.get("name", item.get("id", "unnamed evidence")))
        for item in evidence
        if item.get("required", False) and not item.get("verified", False)
    )
    if unverified:
        errors.append(f"{len(unverified)} required evidence item(s) are not verified.")

    if status == "APPROVED_WITH_CONDITIONS":
        conditions = payload.get("conditions")
        if not isinstance(conditions, list) or not conditions:
            errors.append("Conditional approval requires at least one condition.")

    return ApprovalResult(
        file=str(path),
        valid=not errors,
        gate=gate,
        status=status,
        approver_name=approver_name,
        approver_role=approver_role,
        approved_at=approved_at,
        expires_at=expires_at,
        unverified_evidence=unverified,
        errors=tuple(errors),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Heartbeat JSON approval gate.")
    parser.add_argument("approval_file")
    parser.add_argument("--expected-gate", choices=sorted(EXPECTED_GATES))
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    approval_path = Path(args.approval_file)
    if not approval_path.is_absolute():
        approval_path = repo_root / approval_path

    result = evaluate_approval(approval_path, args.expected_gate)
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
