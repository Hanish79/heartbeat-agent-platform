@'
# Shipment Validation API Business Request

## Business objective

Validate shipment creation requests before they are submitted to the legacy
InfoAXS shipment service.

## Problem

Invalid or incomplete shipment requests currently generate downstream failures,
manual correction effort and inconsistent customer responses.

## Required capabilities

1. Accept a shipment validation request through a REST API.
2. Validate mandatory shipment fields.
3. Apply region-specific validation rules.
4. Return a consistent validation response.
5. Record correlation and audit identifiers.
6. Reject invalid requests without calling InfoAXS.
7. Forward valid requests to the downstream shipment creation service in a
   later implementation phase.

## Mandatory fields

- Customer account number
- Origin country
- Destination country
- Shipper name
- Consignee name
- Shipment weight
- Product type

## Initial business rules

- Customer account number must not be empty.
- Origin and destination must use ISO two-letter country codes.
- Shipment weight must be greater than zero.
- Product type must be one of:
  - Express
  - Standard
  - Economy
- Consignee name is mandatory.
- Each request must receive a correlation ID.

## Out of scope

- Customer authentication
- Pricing
- Address resolution
- Shipment creation in InfoAXS
- Production deployment
- Performance testing

## Success criteria

- All mandatory fields are validated.
- Invalid requests return clear errors.
- Valid requests return a successful validation result.
- Automated tests cover all defined business rules.
- Traceability exists from business requirement to test evidence.
'@ | Set-Content `
  .\examples\shipment-validation\01-business-input\business-request.md `
  -Encoding UTF8