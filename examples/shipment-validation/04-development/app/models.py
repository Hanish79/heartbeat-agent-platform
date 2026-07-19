"""Pydantic request and response models for the Shipment Validation API.

Traceability: examples/shipment-validation/03-architecture/architecture.md
(Components, Error model). Fields map to requirements.md BR-01..BR-08.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ShipmentValidationRequest(BaseModel):
    customer_account_number: str = Field(default="")
    origin_country: str = Field(default="")
    destination_country: str = Field(default="")
    shipper_name: str = Field(default="")
    consignee_name: str = Field(default="")
    shipment_weight: float
    product_type: str = Field(default="")


class ValidationErrorItem(BaseModel):
    field: str
    code: str
    message: str


class ShipmentValidationResponse(BaseModel):
    valid: bool
    errors: List[ValidationErrorItem]
    correlation_id: str
