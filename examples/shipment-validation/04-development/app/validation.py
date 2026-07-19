"""Validation service.

Traceability: architecture.md (Validation service responsibilities).
Implements business rules BR-01..BR-08 from requirements.md.
Pure function: no state, no external calls (NFR-01).
"""

from __future__ import annotations

from typing import List

from .models import ShipmentValidationRequest, ValidationErrorItem

# AD-04: fixed reference list, not an external service call.
ISO_COUNTRY_CODES = {
    "AE", "SA", "JO", "EG", "US", "GB", "DE", "FR", "IN", "CN",
    "AU", "CA", "BR", "ZA", "KE", "QA", "KW", "BH", "OM", "LB",
}

PRODUCT_TYPES = {"Express", "Standard", "Economy"}


def validate_shipment(request: ShipmentValidationRequest) -> List[ValidationErrorItem]:
    errors: List[ValidationErrorItem] = []

    # BR-01: customer account number must not be empty.
    if not request.customer_account_number.strip():
        errors.append(
            ValidationErrorItem(
                field="customer_account_number",
                code="FIELD_REQUIRED",
                message="Customer account number must not be empty.",
            )
        )

    # BR-08 (inferred, flagged assumption in requirements.md): shipper name mandatory.
    if not request.shipper_name.strip():
        errors.append(
            ValidationErrorItem(
                field="shipper_name",
                code="FIELD_REQUIRED",
                message="Shipper name must not be empty.",
            )
        )

    # BR-06: consignee name is mandatory.
    if not request.consignee_name.strip():
        errors.append(
            ValidationErrorItem(
                field="consignee_name",
                code="FIELD_REQUIRED",
                message="Consignee name must not be empty.",
            )
        )

    # BR-02: origin country must be a valid ISO two-letter code.
    if request.origin_country not in ISO_COUNTRY_CODES:
        errors.append(
            ValidationErrorItem(
                field="origin_country",
                code="INVALID_COUNTRY_CODE",
                message="Origin country must be a valid ISO two-letter country code.",
            )
        )

    # BR-03: destination country must be a valid ISO two-letter code.
    if request.destination_country not in ISO_COUNTRY_CODES:
        errors.append(
            ValidationErrorItem(
                field="destination_country",
                code="INVALID_COUNTRY_CODE",
                message="Destination country must be a valid ISO two-letter country code.",
            )
        )

    # BR-04: shipment weight must be greater than zero.
    if request.shipment_weight <= 0:
        errors.append(
            ValidationErrorItem(
                field="shipment_weight",
                code="INVALID_WEIGHT",
                message="Shipment weight must be greater than zero.",
            )
        )

    # BR-05: product type must be one of Express, Standard, Economy.
    if request.product_type not in PRODUCT_TYPES:
        errors.append(
            ValidationErrorItem(
                field="product_type",
                code="INVALID_PRODUCT_TYPE",
                message="Product type must be one of: Express, Standard, Economy.",
            )
        )

    return errors
