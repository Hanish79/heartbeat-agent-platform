# Shipment Validation API — Requirements

## Traceability

| Field | Value |
|---|---|
| Source documents used | shipment-validation-business-request.md |
| Source file names / source_id | SRC-0003 |
| Generation date | 2026-07-19 |
| Artifact status | Draft — pending approval |
| Artifact owner | Not assigned |
| Related requirement, decision, risk, or action identifiers | None assigned yet |

## Business objective

Validate shipment creation requests before they are submitted to the legacy InfoAXS shipment service, so that invalid or incomplete requests are rejected early instead of generating downstream failures, manual correction effort, and inconsistent customer responses. [SRC-0003]

## Functional requirements

| ID | Requirement | Source |
|---|---|---|
| FR-01 | The system must accept a shipment validation request through a REST API. | SRC-0003 |
| FR-02 | The system must validate the presence of all mandatory shipment fields. | SRC-0003 |
| FR-03 | The system must apply region-specific validation rules (ISO two-letter country code checks for origin and destination). | SRC-0003 |
| FR-04 | The system must return a consistent validation response structure for both valid and invalid requests. | SRC-0003 |
| FR-05 | The system must record a correlation identifier and audit identifier for every request. | SRC-0003 |
| FR-06 | The system must reject invalid requests without calling InfoAXS. | SRC-0003 |
| FR-07 | Forwarding of valid requests to the downstream shipment creation service (InfoAXS) is planned for a later implementation phase and is not built in this demo. | SRC-0003 |

## Non-functional requirements

| ID | Requirement | Source |
|---|---|---|
| NFR-01 | The validation service must be stateless (no persisted request state between calls). | SRC-0002 (Architecture note) — supporting context, not SRC-0003 |
| NFR-02 | Error responses must clearly identify which field(s) failed and why, to support operations staff explaining rejections. | SRC-0002 (Operations note) — supporting context, not SRC-0003 |
| NFR-03 | No real customer or shipment data may be used in the demo; only synthetic data is permitted. | SRC-0002 (Security note) — supporting context, not SRC-0003 |
| NFR-04 | Automated tests must cover all defined business rules. | SRC-0003 |

**Assumption flag:** NFR-01 through NFR-03 are derived from SRC-0002 (synthetic stakeholder notes), which describes a broader AI-assisted shipment validation agent. This demo implements only the deterministic REST API validation scope defined in SRC-0003. These NFRs are included because they are consistent with and do not contradict SRC-0003, but they are not themselves sourced from the primary business request. See Assumptions below.

## Business rules

| ID | Rule | Source |
|---|---|---|
| BR-01 | Customer account number must not be empty. | SRC-0003 |
| BR-02 | Origin country must be a valid ISO two-letter country code. | SRC-0003 |
| BR-03 | Destination country must be a valid ISO two-letter country code. | SRC-0003 |
| BR-04 | Shipment weight must be greater than zero. | SRC-0003 |
| BR-05 | Product type must be one of: Express, Standard, Economy. | SRC-0003 |
| BR-06 | Consignee name is mandatory and must not be empty. | SRC-0003 |
| BR-07 | Every request must receive a correlation ID. | SRC-0003 |
| BR-08 | Mandatory fields are: customer account number, origin country, destination country, shipper name, consignee name, shipment weight, product type. | SRC-0003 |

**Gap identified:** SRC-0003 lists "Shipper name" as a mandatory field (see Mandatory fields section) but does not state an explicit validation rule for it under "Initial business rules" (e.g., non-empty check). This demo treats shipper name as mandatory/non-empty for consistency with the mandatory fields list, but this is an assumption, not an explicit stated rule. Flagged for confirmation.

## Acceptance criteria (Given/When/Then)

**AC-01 — Missing customer account number** (BR-01, FR-02)
- Given a shipment validation request with an empty or missing customer account number
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the customer account number field, and InfoAXS is not called

**AC-02 — Invalid origin country code** (BR-02, FR-03)
- Given a shipment validation request with an origin country that is not a valid ISO two-letter code
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the origin country field

**AC-03 — Invalid destination country code** (BR-03, FR-03)
- Given a shipment validation request with a destination country that is not a valid ISO two-letter code
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the destination country field

**AC-04 — Zero shipment weight** (BR-04)
- Given a shipment validation request with a shipment weight equal to zero
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the shipment weight field

**AC-05 — Negative shipment weight** (BR-04)
- Given a shipment validation request with a negative shipment weight
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the shipment weight field

**AC-06 — Unsupported product type** (BR-05)
- Given a shipment validation request with a product type other than Express, Standard, or Economy
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the product type field

**AC-07 — Missing consignee name** (BR-06)
- Given a shipment validation request with an empty or missing consignee name
- When the request is submitted to the validation API
- Then the API returns a validation failure identifying the consignee name field

**AC-08 — Valid request** (FR-04, FR-06)
- Given a shipment validation request that satisfies all mandatory fields and business rules
- When the request is submitted to the validation API
- Then the API returns a successful validation result and does not call InfoAXS (InfoAXS forwarding is out of scope for this phase)

**AC-09 — Correlation ID generation** (BR-07, FR-05)
- Given any shipment validation request, valid or invalid
- When the request is submitted to the validation API
- Then the response includes a correlation ID

## Assumptions

- SRC-0001 and SRC-0002 describe a broader AI-assisted "Shipment Validation Agent" concept (classification of failure reasons, correction recommendations, human review routing). This demo builds only the deterministic validation API scope defined in SRC-0003; the AI-assisted capabilities in SRC-0001/SRC-0002 are not in scope for this build. This is an assumption made to reconcile overlapping source documents, not a confirmed decision.
- Shipper name is treated as mandatory/non-empty by inference from the mandatory fields list in SRC-0003, since no explicit business rule for it is stated. (See Gap identified above.)
- "Region-specific validation rules" (SRC-0003, Required capabilities #3) is interpreted as the ISO two-letter country code checks on origin and destination, since no other region-specific rules are defined in the source.
- Audit identifier (SRC-0003, Required capabilities #5) is assumed to be satisfied by the correlation ID unless a separate audit ID format is confirmed by a human reviewer.
- No owner, approver, or target date is stated in the source documents; these fields are left unassigned rather than invented, per CLAUDE.md quality controls.

## Dependencies

- Downstream InfoAXS shipment creation service (forwarding of valid requests) — explicitly deferred to a later implementation phase per SRC-0003 and therefore not built here.
- ISO two-letter country code reference list — required for BR-02/BR-03 validation; not provided in source documents. Assumed to be implemented as a fixed reference list within the demo application (documented in the architecture stage).

## Out of scope

The following are explicitly out of scope per SRC-0003:

- Customer authentication
- Pricing
- Address resolution
- Shipment creation in InfoAXS
- Production deployment
- Performance testing

## Contradictions and quality notes

- No direct contradictions were found between SRC-0001, SRC-0002, and SRC-0003 on the core validation rules. SRC-0001/SRC-0002 describe a superset (AI-assisted agent) of the scope defined in SRC-0003 (deterministic REST API); this requirements document scopes strictly to SRC-0003 per the demo build instructions, and flags the broader material as context only.
- All three source documents in the register show `review_status = Not reviewed`. This requirements document should be treated as provisional pending source document review.
