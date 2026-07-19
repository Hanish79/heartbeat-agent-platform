"""Test configuration.

Adds the Stage 3 development directory to sys.path so tests can import the
`app` package without packaging/installing it, and provides a shared
TestClient fixture and a baseline valid request payload.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DEVELOPMENT_DIR = Path(__file__).resolve().parents[1] / "04-development"
sys.path.insert(0, str(DEVELOPMENT_DIR))

from app.main import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def valid_payload() -> dict:
    # AC-08 baseline valid request. Traceability: requirements.md AC-08.
    return {
        "customer_account_number": "CUST-001",
        "origin_country": "AE",
        "destination_country": "SA",
        "shipper_name": "Aramex Depot",
        "consignee_name": "Jane Doe",
        "shipment_weight": 2.5,
        "product_type": "Express",
    }
