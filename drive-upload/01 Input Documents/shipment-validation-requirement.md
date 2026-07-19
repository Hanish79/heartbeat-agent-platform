# Shipment Validation API Requirement

Status: APPROVED_INPUT

## Business Objective

Prevent invalid shipment requests from reaching downstream shipment-processing services.

## BR-001 Validate Mandatory Fields

The API must validate that the following fields are present and non-empty:

- customerAccount
- originCountry
- destinationCountry
- productType
- correlationId

## BR-002 Validate Shipment Weight

The API must reject a shipment request when weight is less than or equal to zero.

## BR-003 Validate Country Codes

The API must validate that originCountry and destinationCountry use two-letter ISO country codes.

## BR-004 Return Structured Errors

When a request is invalid, the API must return a structured list of validation errors.

Each error must include:

- field
- code
- message

## BR-005 Preserve Correlation ID

Every response must return the correlationId supplied in the request.

## BR-006 Block Invalid Downstream Processing

Invalid requests must not proceed to downstream shipment-processing services.

## Acceptance Criteria

### AC-001 Mandatory Field Failure

Given a request with a missing mandatory field  
When the request is validated  
Then the response status is INVALID  
And the response identifies the missing field  
And the original correlationId is returned

### AC-002 Invalid Weight Failure

Given a request with weight equal to zero  
When the request is validated  
Then the response status is INVALID  
And the response contains an INVALID_WEIGHT error  
And the request is not passed downstream

### AC-003 Invalid Country Code Failure

Given a request with a country code that is not exactly two letters  
When the request is validated  
Then the response status is INVALID  
And the response identifies the affected country field

### AC-004 Valid Request

Given a request containing all mandatory fields  
And weight is greater than zero  
And both country codes contain exactly two letters  
When the request is validated  
Then the response status is VALID  
And the original correlationId is returned
