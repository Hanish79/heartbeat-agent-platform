from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "python"
    / "validate_traceability.py"
)


def load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "validate_traceability",
        VALIDATOR_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load validator: {VALIDATOR_PATH}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_single_source_id() -> None:
    validator = load_validator_module()

    assert validator.parse_source_ids("SRC-0001") == [
        "SRC-0001"
    ]


def test_parse_comma_separated_source_ids() -> None:
    validator = load_validator_module()

    assert validator.parse_source_ids(
        "SRC-0001, SRC-0002"
    ) == [
        "SRC-0001",
        "SRC-0002",
    ]


def test_parse_semicolon_separated_source_ids() -> None:
    validator = load_validator_module()

    assert validator.parse_source_ids(
        "SRC-0001;SRC-0002"
    ) == [
        "SRC-0001",
        "SRC-0002",
    ]


def test_parse_empty_source_ids() -> None:
    validator = load_validator_module()

    assert validator.parse_source_ids("") == []