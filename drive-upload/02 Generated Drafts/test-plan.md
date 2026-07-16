# Shipment Validation API Test Plan

Status: TEST_PLAN_ONLY

## TEST-001 Missing Mandatory Field

Requirement: BR-001, BR-004, BR-005  
Acceptance Criterion: AC-001  
Expected Result: INVALID response with field-level error and original correlation ID.

## TEST-002 Zero Weight

Requirement: BR-002, BR-004, BR-006  
Acceptance Criterion: AC-002  
Expected Result: INVALID response with INVALID_WEIGHT and no downstream processing.

## TEST-003 Invalid Origin Country

Requirement: BR-003, BR-004  
Acceptance Criterion: AC-003  
Expected Result: INVALID response identifying originCountry.

## TEST-004 Valid Shipment

Requirement: BR-001, BR-002, BR-003, BR-005  
Acceptance Criterion: AC-004  
Expected Result: VALID response with original correlation ID.
