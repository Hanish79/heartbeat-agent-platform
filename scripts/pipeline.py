#!/usr/bin/env python3
"""
Deterministic orchestration pipeline for the Heartbeat demo.

Stages:
1. validate documentation
2. validate plan approval when requested
3. build traceability matrix
4. validate release approval when requested
5. optionally publish

No AI calls are made.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class StageResult:
    name: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_stage(name: str, command: list[str], cwd: Path) -> StageResult:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return StageResult(
        name=name,
        command=tuple(command),
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Heartbeat demo pipeline.")
    parser.add_argument("--repo-root", help="Repository root.")
    parser.add_argument("--plan-approval", default="approvals/plan-approval.md")
    parser.add_argument("--release-approval", default="approvals/release-approval.md")
    parser.add_argument("--require-plan-approval", action="store_true")
    parser.add_argument("--require-release-approval", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--execute-publish", action="store_true")
    parser.add_argument("--drive-root")
    parser.add_argument("--git", action="store_true")
    parser.add_argument("--report", default="output/pipeline-report.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    scripts = repo_root / "scripts"
    python = sys.executable
    stages: list[StageResult] = []

    stages.append(run_stage(
        "validate_documents",
        [python, str(scripts / "validate_documents.py"), "--repo-root", str(repo_root)],
        repo_root,
    ))

    if stages[-1].returncode == 0 and args.require_plan_approval:
        stages.append(run_stage(
            "validate_plan_approval",
            [python, str(scripts / "approval_engine.py"), args.plan_approval, "--repo-root", str(repo_root)],
            repo_root,
        ))

    if all(stage.returncode == 0 for stage in stages):
        stages.append(run_stage(
            "traceability",
            [python, str(scripts / "traceability.py"), "--repo-root", str(repo_root)],
            repo_root,
        ))

    if all(stage.returncode == 0 for stage in stages) and args.require_release_approval:
        stages.append(run_stage(
            "validate_release_approval",
            [python, str(scripts / "approval_engine.py"), args.release_approval, "--repo-root", str(repo_root)],
            repo_root,
        ))

    if all(stage.returncode == 0 for stage in stages) and args.publish:
        command = [
            python,
            str(scripts / "publish.py"),
            "--repo-root",
            str(repo_root),
            "--approval",
            args.release_approval,
        ]
        if args.execute_publish:
            command.append("--execute")
        if args.drive_root:
            command.extend(["--drive-root", args.drive_root])
        if args.git:
            command.append("--git")

        stages.append(run_stage("publish", command, repo_root))

    passed = all(stage.returncode == 0 for stage in stages)
    payload = {
        "passed": passed,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stages": [asdict(stage) for stage in stages],
    }

    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "passed": passed,
        "stages": [
            {"name": stage.name, "returncode": stage.returncode}
            for stage in stages
        ],
        "report": str(report_path),
    }, indent=2))

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
