# Shipment Validation API — Test Results

## Traceability

| Field | Value |
|---|---|
| Test suite | examples/shipment-validation/05-testing/test_validate_shipment.py |
| Requirements | examples/shipment-validation/02-requirements/requirements.md (approved — approvals/requirements.json) |
| Architecture | examples/shipment-validation/03-architecture/architecture.md (approved — approvals/architecture.json) |
| Source documents | business-request.md (unregistered — see requirements.md Gap identified); SRC-0001, SRC-0002 (supporting context) |
| Generation date | 2026-07-19 |
| Artifact status | Draft — evidence for demo purposes only, not yet approved |
| Artifact owner | Not assigned |

## Execution environment

- Python 3.14.6
- Project virtual environment: `C:\Heartbeat\.venv`
- pytest 9.1.1
- fastapi 0.139.2, pydantic 2.13.4, starlette 1.3.1, httpx 0.28.1, uvicorn 0.51.0
- These are the versions actually installed in the project `.venv` and are
  what `requirements.txt` now specifies.

## Command

```
pytest examples/shipment-validation/05-testing/ -v
```

## Result summary

**9 passed, 0 failed, 1 warning, in 0.50s.**

The warning (`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated`) is an informational deprecation notice from the test client library, not a test failure.

## Test-by-test results

| Test | Scenario | Acceptance criterion | Business rule | Result |
|---|---|---|---|---|
| test_missing_customer_account_number | Missing customer account | AC-01 | BR-01 | PASSED |
| test_invalid_origin_country | Invalid origin country | AC-02 | BR-02 | PASSED |
| test_invalid_destination_country | Invalid destination country | AC-03 | BR-03 | PASSED |
| test_zero_shipment_weight | Zero shipment weight | AC-04 | BR-04 | PASSED |
| test_negative_shipment_weight | Negative shipment weight | AC-05 | BR-04 | PASSED |
| test_unsupported_product_type | Unsupported product type | AC-06 | BR-05 | PASSED |
| test_missing_consignee_name | Missing consignee name | AC-07 | BR-06 | PASSED |
| test_valid_request | Valid request | AC-08 | — | PASSED |
| test_correlation_id_generation | Correlation ID generation | AC-09 | BR-07 | PASSED |

All 9 scenarios required by the build instructions are covered, and all passed on this run.

## Coverage notes

- Every business rule (BR-01–BR-08) has at least one covering test, except BR-08 (shipper name mandatory), which is exercised indirectly through the shared `valid_payload` fixture (a non-empty shipper name is required for other tests to reach `valid: true`) but has no dedicated failure-path test. This was not one of the 9 scenarios explicitly listed in the build instructions, so no dedicated test was added; flagged as a coverage gap for reviewer consideration.
- Architecture decision AD-02 (business-rule failures return HTTP 200, not 4xx) is implicitly verified by every failing-scenario test asserting `resp.status_code == 200`.

## Outstanding gaps carried into this evidence

- `business-request.md`, the primary source for these requirements and tests, is still not present in `registers/source-register.csv` (see requirements.md Gap identified, architecture.md risk R-06). This does not affect whether the tests pass, but it does affect whether this test evidence is fully traceable to a governed source_id.
