#!/usr/bin/env python3
"""
Deterministic folder synchronization for the Heartbeat demo.

This script does not call Google APIs. It synchronizes files between the
repository and a locally mounted or mirrored Google Drive folder.

Typical use:
    python scripts/sync_drive.py pull --drive-root "/path/to/Heartbeat Agent Demo"
    python scripts/sync_drive.py push --drive-root "/path/to/Heartbeat Agent Demo"

Expected Drive structure:
    01 Input Documents/
    02 Generated Drafts/
    03 Waiting for Approval/
    04 Approved Outputs/
    05 Rejected Outputs/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_MAPPING = {
    "01 Input Documents": "input",
    "02 Generated Drafts": "output",
    "03 Waiting for Approval": "approvals",
    "04 Approved Outputs": "approved",
    "05 Rejected Outputs": "rejected",
}

IGNORED_NAMES = {".DS_Store", "Thumbs.db"}
IGNORED_SUFFIXES = {".tmp", ".part"}


@dataclass(frozen=True)
class SyncRecord:
    source: str
    destination: str
    action: str
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IGNORED_NAMES or path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        yield path


def copy_if_changed(source: Path, destination: Path, dry_run: bool) -> SyncRecord | None:
    source_hash = sha256_file(source)
    if destination.exists() and destination.is_file():
        if sha256_file(destination) == source_hash:
            return None
        action = "updated"
    else:
        action = "created"

    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    return SyncRecord(
        source=str(source),
        destination=str(destination),
        action=action,
        sha256=source_hash,
    )


def sync_tree(source_root: Path, destination_root: Path, dry_run: bool) -> list[SyncRecord]:
    if not source_root.exists():
        return []

    records: list[SyncRecord] = []
    for source in iter_files(source_root):
        relative = source.relative_to(source_root)
        destination = destination_root / relative
        record = copy_if_changed(source, destination, dry_run)
        if record:
            records.append(record)
    return records


def resolve_repo_root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize demo files with a mounted Drive folder.")
    parser.add_argument("direction", choices=("pull", "push"))
    parser.add_argument("--drive-root", required=True, help="Mounted or mirrored Google Drive root folder.")
    parser.add_argument("--repo-root", help="Repository root. Defaults to parent of scripts/.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.repo_root)
    drive_root = Path(args.drive_root).expanduser().resolve()

    if not drive_root.exists():
        print(f"ERROR: Drive root does not exist: {drive_root}", file=sys.stderr)
        return 2

    records: list[SyncRecord] = []

    for drive_folder, repo_folder in DEFAULT_MAPPING.items():
        drive_path = drive_root / drive_folder
        repo_path = repo_root / repo_folder

        if args.direction == "pull":
            records.extend(sync_tree(drive_path, repo_path, args.dry_run))
        else:
            records.extend(sync_tree(repo_path, drive_path, args.dry_run))

    report = {
        "direction": args.direction,
        "dry_run": args.dry_run,
        "repo_root": str(repo_root),
        "drive_root": str(drive_root),
        "changes": [asdict(record) for record in records],
        "change_count": len(records),
    }

    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = repo_root / report_path
        if not args.dry_run:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
