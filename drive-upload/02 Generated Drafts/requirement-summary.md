# Shipment Validation API Requirement Summary

Status: DRAFT_FOR_REVIEW

## Objective

Validate shipment requests before downstream processing.

## Requirements

| ID | Requirement |
|---|---|
| BR-001 | Validate mandatory fields |
| BR-002 | Reject weight less than or equal to zero |
| BR-003 | Validate two-letter country codes |
| BR-004 | Return structured validation errors |
| BR-005 | Preserve correlation ID |
| BR-006 | Block invalid downstream processing |

## Acceptance Criteria

| ID | Covers |
|---|---|
| AC-001 | BR-001, BR-004, BR-005 |
| AC-002 | BR-002, BR-004, BR-006 |
| AC-003 | BR-003, BR-004 |
| AC-004 | BR-001, BR-002, BR-003, BR-005 |
