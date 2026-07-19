"""Tests for POST /validate-shipment.

Traceability: examples/shipment-validation/02-requirements/requirements.md
Each test maps to one acceptance criterion (AC-01..AC-09).
"""

ENDPOINT = "/validate-shipment"


def test_missing_customer_account_number(client, valid_payload):
    """AC-01 / BR-01."""
    payload = dict(valid_payload, customer_account_number="")
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "customer_account_number" in fields


def test_invalid_origin_country(client, valid_payload):
    """AC-02 / BR-02."""
    payload = dict(valid_payload, origin_country="ZZ")
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "origin_country" in fields


def test_invalid_destination_country(client, valid_payload):
    """AC-03 / BR-03."""
    payload = dict(valid_payload, destination_country="ZZ")
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "destination_country" in fields


def test_zero_shipment_weight(client, valid_payload):
    """AC-04 / BR-04."""
    payload = dict(valid_payload, shipment_weight=0)
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "shipment_weight" in fields


def test_negative_shipment_weight(client, valid_payload):
    """AC-05 / BR-04."""
    payload = dict(valid_payload, shipment_weight=-1.5)
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "shipment_weight" in fields


def test_unsupported_product_type(client, valid_payload):
    """AC-06 / BR-05."""
    payload = dict(valid_payload, product_type="Overnight")
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "product_type" in fields


def test_missing_consignee_name(client, valid_payload):
    """AC-07 / BR-06."""
    payload = dict(valid_payload, consignee_name="")
    resp = client.post(ENDPOINT, json=payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is False
    fields = {e["field"] for e in body["errors"]}
    assert "consignee_name" in fields


def test_valid_request(client, valid_payload):
    """AC-08."""
    resp = client.post(ENDPOINT, json=valid_payload)
    body = resp.json()

    assert resp.status_code == 200
    assert body["valid"] is True
    assert body["errors"] == []
    assert body["correlation_id"]


def test_correlation_id_generation(client, valid_payload):
    """AC-09 — correlation ID present on both valid and invalid responses,
    and matches the X-Correlation-Id response header."""
    valid_resp = client.post(ENDPOINT, json=valid_payload)
    valid_body = valid_resp.json()
    assert valid_body["correlation_id"]
    assert valid_resp.headers["X-Correlation-Id"] == valid_body["correlation_id"]

    invalid_payload = dict(valid_payload, consignee_name="")
    invalid_resp = client.post(ENDPOINT, json=invalid_payload)
    invalid_body = invalid_resp.json()
    assert invalid_body["correlation_id"]
    assert invalid_resp.headers["X-Correlation-Id"] == invalid_body["correlation_id"]

    # Two separate requests must not share a correlation ID.
    assert valid_body["correlation_id"] != invalid_body["correlation_id"]
