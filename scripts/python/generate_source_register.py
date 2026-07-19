from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "documents" / "01-raw-source-documents"
REGISTER_PATH = PROJECT_ROOT / "registers" / "source-register.csv"

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".xml",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    REGISTER_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str | int]] = []

    for path in sorted(SOURCE_DIR.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        stat = path.stat()

        rows.append(
            {
                "source_id": f"SRC-{len(rows) + 1:04d}",
                "file_name": path.name,
                "relative_path": str(path.relative_to(PROJECT_ROOT)),
                "file_type": path.suffix.lower().lstrip("."),
                "size_bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(
                    stat.st_mtime,
                    tz=timezone.utc,
                ).isoformat(),
                "sha256": sha256_file(path),
                "status": "Source",
                "review_status": "Not reviewed",
                "owner": "",
                "notes": "",
            }
        )

    fieldnames = [
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
    ]

    with REGISTER_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {REGISTER_PATH} with {len(rows)} source files.")


if __name__ == "__main__":
    main()