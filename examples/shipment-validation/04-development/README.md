# Shipment Validation API — Development

## Traceability

| Field | Value |
|---|---|
| Requirements | examples/shipment-validation/02-requirements/requirements.md (approved — approvals/requirements.json) |
| Architecture | examples/shipment-validation/03-architecture/architecture.md (approved — approvals/architecture.json) |
| Source documents | business-request.md (unregistered — see requirements.md Gap identified); SRC-0001, SRC-0002 (supporting context) |
| Generation date | 2026-07-19 |
| Artifact status | Draft — implementation for demo purposes only |
| Artifact owner | Not assigned |

## What this is

A small FastAPI service implementing the Shipment Validation API described in
architecture.md. It validates a shipment creation request against business
rules BR-01–BR-08 and returns a consistent validation response with a
correlation ID. It does **not** call InfoAXS or any external service
(FR-06/FR-07 — forwarding to InfoAXS is a later phase, out of scope here).

## Structure

```
04-development/
  app/
    __init__.py
    models.py       Pydantic request/response models
    validation.py   Business rule validation logic (BR-01..BR-08)
    main.py         FastAPI app and POST /validate-shipment endpoint
  requirements.txt
  README.md
```

## Running locally

```
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir examples/shipment-validation/04-development
```

Or, from inside `examples/shipment-validation/04-development`:

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoint

`POST /validate-shipment`

Request body:

```json
{
  "customer_account_number": "CUST-001",
  "origin_country": "AE",
  "destination_country": "SA",
  "shipper_name": "Aramex Depot",
  "consignee_name": "Jane Doe",
  "shipment_weight": 2.5,
  "product_type": "Express"
}
```

Successful response (HTTP 200):

```json
{
  "valid": true,
  "errors": [],
  "correlation_id": "..."
}
```

Business-rule failure response (HTTP 200 — see architecture.md AD-02 for
rationale):

```json
{
  "valid": false,
  "errors": [
    { "field": "shipment_weight", "code": "INVALID_WEIGHT", "message": "Shipment weight must be greater than zero." }
  ],
  "correlation_id": "..."
}
```

The correlation ID is present on every response, valid or invalid, and is
also returned on the `X-Correlation-Id` response header.

## Known assumptions and gaps carried from requirements/architecture

- `business-request.md`, the primary source for this demo, has no entry in
  `registers/source-register.csv` — see requirements.md "Gap identified"
  and architecture.md risk R-06. Treated as the demo's primary input per
  the explicit build instructions, but not yet a governed/registered
  source.
- Shipper name is validated as mandatory/non-empty by inference (no explicit
  source rule) — see requirements.md "Second gap identified".
- Country codes are checked against a small fixed demo reference list in
  `app/validation.py`, not a complete ISO 3166 list or external service
  (AD-04).
- The correlation ID doubles as the audit identifier in this demo (AD-05).

## Out of scope (per business request and architecture)

Customer authentication, pricing, address resolution, InfoAXS shipment
creation, production deployment, performance testing.
