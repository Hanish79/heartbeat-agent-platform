#!/usr/bin/env python3
"""
Validate the Phase 1 documentation structure and Markdown hygiene.

The validator is deterministic and checks:
- required documentation sections
- required README files
- broken relative Markdown links
- forbidden placeholder tokens
- duplicate top-level headings inside a file
- approval status vocabulary
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote

REQUIRED_SECTIONS = (
    "00 Vision",
    "01 Architecture",
    "02 ADLC",
    "03 Repository",
    "04 Governance",
    "05 Human Approval",
    "06 Development",
    "07 Operations",
    "08 Security",
    "09 Examples",
)

ALLOWED_APPROVAL_STATUSES = {
    "PENDING",
    "APPROVED",
    "APPROVED_WITH_COMMENTS",
    "REJECTED",
    "EXPIRED",
}

FORBIDDEN_PLACEHOLDERS = (
    "TBD",
    "TO BE COMPLETED",
    "INSERT HERE",
    "LOREM IPSUM",
)

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
STATUS_LINE = re.compile(r"^\s*Status:\s*([A-Z_]+)\s*$", re.MULTILINE)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Finding:
    severity: str
    file: str
    message: str


def validate_required_structure(docs_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not docs_root.exists():
        return [Finding("ERROR", str(docs_root), "Documentation root does not exist.")]

    root_readme = docs_root / "README.md"
    if not root_readme.exists():
        findings.append(Finding("ERROR", str(root_readme), "Missing root documentation README."))

    for section in REQUIRED_SECTIONS:
        section_path = docs_root / section
        if not section_path.is_dir():
            findings.append(Finding("ERROR", str(section_path), "Missing required documentation section."))
            continue
        readme = section_path / "README.md"
        if not readme.exists():
            findings.append(Finding("ERROR", str(readme), "Missing section README."))
    return findings


def relative_link_target(markdown_file: Path, raw_target: str) -> Path | None:
    target = raw_target.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    return (markdown_file.parent / unquote(target)).resolve()


def validate_markdown_file(path: Path, repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")

    for placeholder in FORBIDDEN_PLACEHOLDERS:
        if placeholder.lower() in text.lower():
            findings.append(Finding("WARNING", str(path.relative_to(repo_root)), f"Contains placeholder: {placeholder}"))

    statuses = STATUS_LINE.findall(text)
    for status in statuses:
        if status not in ALLOWED_APPROVAL_STATUSES and status not in {
            "DRAFT_FOR_REVIEW",
            "PLAN_ONLY",
            "TEST_PLAN_ONLY",
            "SECURITY_REVIEW_COMPLETE",
            "INDEPENDENT_REVIEW_COMPLETE",
            "Proposed",
        }:
            findings.append(Finding("ERROR", str(path.relative_to(repo_root)), f"Unknown status value: {status}"))

    seen_h1: set[str] = set()
    for hashes, title in HEADING.findall(text):
        if len(hashes) != 1:
            continue
        normalized = title.strip().lower()
        if normalized in seen_h1:
            findings.append(Finding("WARNING", str(path.relative_to(repo_root)), f"Duplicate H1 heading: {title}"))
        seen_h1.add(normalized)

    for raw_target in MARKDOWN_LINK.findall(text):
        target = relative_link_target(path, raw_target)
        if target is None:
            continue
        if not target.exists():
            findings.append(Finding("ERROR", str(path.relative_to(repo_root)), f"Broken relative link: {raw_target}"))

    if "\t" in text:
        findings.append(Finding("WARNING", str(path.relative_to(repo_root)), "Contains tab characters."))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Heartbeat demo documentation.")
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--report", default="output/document-validation.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    docs_root = repo_root / "docs"

    findings = validate_required_structure(docs_root)
    for path in sorted(docs_root.rglob("*.md")) if docs_root.exists() else []:
        findings.extend(validate_markdown_file(path, repo_root))

    report = {
        "valid": not any(item.severity == "ERROR" for item in findings),
        "error_count": sum(item.severity == "ERROR" for item in findings),
        "warning_count": sum(item.severity == "WARNING" for item in findings),
        "findings": [asdict(item) for item in findings],
    }

    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
