# Shipment Validation Requirement

## Objective

Create an API that validates shipment requests before they are accepted for downstream processing.

## Mandatory Fields

- customerAccount
- originCountry
- destinationCountry
- weight
- productType
- correlationId

## Business Rules

1. Weight must be greater than zero.
2. Origin and destination must be two-letter ISO country codes.
3. Missing mandatory fields must return clear validation errors.
4. Every response must return the original correlation ID.
5. Invalid requests must not proceed to downstream processing.

## Acceptance Criteria

- valid requests return `VALID`
- invalid requests return `INVALID`
- each validation error identifies field, code, and message
- automated tests cover valid and invalid paths
