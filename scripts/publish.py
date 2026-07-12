#!/usr/bin/env python3
"""
Publish approved demo artifacts.

Default behavior is safe and deterministic:
- validates release approval
- verifies repository cleanliness rules
- copies approved outputs to a local approved/ directory
- optionally pushes to a mounted Drive folder
- optionally commits and pushes to Git only when explicitly requested

Nothing is published unless --execute is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from approval_engine import evaluate_approval


@dataclass(frozen=True)
class PublishedFile:
    source: str
    destination: str
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_tree(source_root: Path, destination_root: Path, execute: bool) -> list[PublishedFile]:
    records: list[PublishedFile] = []
    if not source_root.exists():
        return records

    for source in sorted(source_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root)
        destination = destination_root / relative
        if execute:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        records.append(PublishedFile(str(source), str(destination), sha256_file(source)))
    return records


def run_git(repo_root: Path, command: list[str], execute: bool) -> dict[str, object]:
    full = ["git", *command]
    if not execute:
        return {"command": full, "executed": False, "returncode": None, "stdout": "", "stderr": ""}

    result = subprocess.run(full, cwd=repo_root, capture_output=True, text=True)
    return {
        "command": full,
        "executed": True,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish approved demo outputs.")
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--approval", default="approvals/release-approval.md")
    parser.add_argument("--source", default="output")
    parser.add_argument("--approved-dir", default="approved")
    parser.add_argument("--drive-root", help="Mounted Drive root. Approved files go to 04 Approved Outputs.")
    parser.add_argument("--git", action="store_true", help="Commit and push when execution is enabled.")
    parser.add_argument("--message", default="chore: publish approved demo artifacts")
    parser.add_argument("--execute", action="store_true", help="Perform changes. Without this flag, dry-run only.")
    parser.add_argument("--report", default="output/publish-report.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    approval_path = repo_root / args.approval
    approval = evaluate_approval(approval_path)

    if not approval.valid:
        print(json.dumps({"published": False, "approval": asdict(approval)}, indent=2))
        return 1

    source_root = repo_root / args.source
    if not source_root.exists():
        print(f"ERROR: Source directory does not exist: {source_root}", file=sys.stderr)
        return 2

    local_destination = repo_root / args.approved_dir
    published = copy_tree(source_root, local_destination, args.execute)

    drive_records: list[PublishedFile] = []
    if args.drive_root:
        drive_destination = Path(args.drive_root).expanduser().resolve() / "04 Approved Outputs"
        drive_records = copy_tree(source_root, drive_destination, args.execute)

    git_results: list[dict[str, object]] = []
    if args.git:
        git_results.append(run_git(repo_root, ["add", "."], args.execute))
        git_results.append(run_git(repo_root, ["commit", "-m", args.message], args.execute))
        git_results.append(run_git(repo_root, ["push"], args.execute))

    payload = {
        "published": args.execute,
        "dry_run": not args.execute,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "approval": asdict(approval),
        "local_files": [asdict(item) for item in published],
        "drive_files": [asdict(item) for item in drive_records],
        "git": git_results,
    }

    report_path = repo_root / args.report
    if args.execute:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))

    failed_git = any(item.get("executed") and item.get("returncode") not in (0, None) for item in git_results)
    return 1 if failed_git else 0


if __name__ == "__main__":
    raise SystemExit(main())
