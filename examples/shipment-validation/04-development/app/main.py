"""Shipment Validation API.

Traceability: examples/shipment-validation/03-architecture/architecture.md
Endpoint: POST /validate-shipment

AD-02: business-rule failures return HTTP 200 with valid=false, not HTTP 4xx.
Only structurally malformed request bodies (handled by Pydantic/FastAPI)
return HTTP 422. InfoAXS is never called by this service (FR-06/FR-07).
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Response

from .models import ShipmentValidationRequest, ShipmentValidationResponse
from .validation import validate_shipment

app = FastAPI(title="Shipment Validation API")


@app.post("/validate-shipment", response_model=ShipmentValidationResponse)
def validate_shipment_endpoint(
    request: ShipmentValidationRequest, response: Response
) -> ShipmentValidationResponse:
    # FR-05 / BR-07 / AC-09: correlation ID generated for every request,
    # regardless of validation outcome.
    correlation_id = str(uuid.uuid4())
    response.headers["X-Correlation-Id"] = correlation_id

    errors = validate_shipment(request)

    return ShipmentValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        correlation_id=correlation_id,
    )
