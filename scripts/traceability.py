#!/usr/bin/env python3
"""
Build and validate requirement traceability from Markdown artifacts.

Recognized identifiers:
- BR-### business requirement
- RULE-### business rule
- AC-### acceptance criterion
- TEST-### test scenario
- ADR-### architecture decision
- DEV-### development task

The tool scans Markdown files and creates a JSON matrix showing where each ID
is defined and referenced.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

ID_PATTERN = re.compile(r"\b(BR|RULE|AC|TEST|ADR|DEV)-\d{3,}\b")
HEADING_WITH_ID = re.compile(r"^#{1,6}\s+.*?\b((?:BR|RULE|AC|TEST|ADR|DEV)-\d{3,})\b", re.MULTILINE)

REQUIRED_REFERENCE_RULES = {
    "AC": {"BR", "RULE"},
    "TEST": {"AC", "BR", "RULE"},
    "DEV": {"BR", "AC", "ADR"},
}


@dataclass(frozen=True)
class TraceLocation:
    file: str
    line: int
    context: str
    defined: bool


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_file(path: Path, repo_root: Path) -> dict[str, list[TraceLocation]]:
    text = path.read_text(encoding="utf-8")
    defined_ids = {match.group(1) for match in HEADING_WITH_ID.finditer(text)}
    results: dict[str, list[TraceLocation]] = defaultdict(list)

    for match in ID_PATTERN.finditer(text):
        identifier = match.group(0)
        start = max(0, text.rfind("\n", 0, match.start()) + 1)
        end = text.find("\n", match.end())
        if end == -1:
            end = len(text)
        context = text[start:end].strip()
        results[identifier].append(
            TraceLocation(
                file=str(path.relative_to(repo_root)),
                line=line_number(text, match.start()),
                context=context[:300],
                defined=identifier in defined_ids,
            )
        )
    return results


def validate_links(matrix: dict[str, list[TraceLocation]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    for identifier, locations in sorted(matrix.items()):
        prefix = identifier.split("-", 1)[0]

        if not any(location.defined for location in locations):
            findings.append({
                "severity": "ERROR",
                "id": identifier,
                "message": "Identifier is referenced but never defined in a heading.",
            })

        required_prefixes = REQUIRED_REFERENCE_RULES.get(prefix)
        if not required_prefixes:
            continue

        combined_context = " ".join(location.context for location in locations)
        referenced_ids = set(ID_PATTERN.findall(combined_context))
        referenced_prefixes = {item for item in referenced_ids}

        if not (required_prefixes & referenced_prefixes):
            findings.append({
                "severity": "WARNING",
                "id": identifier,
                "message": f"{prefix} item has no visible reference to any of: {sorted(required_prefixes)}",
            })

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Build requirement traceability matrix.")
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--include", nargs="*", default=["docs", "input", "output", "approvals"])
    parser.add_argument("--report", default="output/traceability.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    matrix: dict[str, list[TraceLocation]] = defaultdict(list)

    for relative_root in args.include:
        root = repo_root / relative_root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            for identifier, locations in scan_file(path, repo_root).items():
                matrix[identifier].extend(locations)

    findings = validate_links(matrix)
    payload = {
        "valid": not any(item["severity"] == "ERROR" for item in findings),
        "identifier_count": len(matrix),
        "matrix": {
            identifier: [asdict(location) for location in locations]
            for identifier, locations in sorted(matrix.items())
        },
        "findings": findings,
    }

    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "valid": payload["valid"],
        "identifier_count": payload["identifier_count"],
        "finding_count": len(findings),
        "report": str(report_path),
    }, indent=2))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
