# Shipment Validation API — Requirements

## Traceability

| Field | Value |
|---|---|
| Source documents used | examples/shipment-validation/01-business-input/business-request.md (primary input per build instructions); documents/01-raw-source-documents/01_business_problem.md; documents/01-raw-source-documents/02_stakeholder_notes.md |
| Source file names / source_id | business-request.md — **no source_id assigned** (see Gap below); SRC-0001 (01_business_problem.md); SRC-0002 (02_stakeholder_notes.md) |
| Generation date | 2026-07-19 |
| Artifact status | Draft — pending approval |
| Artifact owner | Not assigned |
| Related requirement, decision, risk, or action identifiers | None assigned yet |

## Gap identified — source registration

`registers/source-register.csv` currently lists only two entries:

- SRC-0001 → `01_business_problem.md`
- SRC-0002 → `02_stakeholder_notes.md`

There is **no register entry** for `shipment-validation-business-request.md`
or for `examples/shipment-validation/01-business-input/business-request.md`,
even though both files exist on disk
(`documents/01-raw-source-documents/shipment-validation-business-request.md`,
1820 bytes) and the build instructions explicitly name
`business-request.md` as the primary input for this demo.

Per CLAUDE.md ("Do not invent owners, dates, decisions, approvals, or
status"), this document does **not** fabricate a source_id (e.g. "SRC-0003")
for an unregistered file. Below, requirements sourced from
`business-request.md` are labelled **[business-request.md — unregistered]**
rather than attributed to a source_id. Requirements sourced from the two
registered documents are labelled with their real source_id (SRC-0001,
SRC-0002). This gap should be resolved by adding the missing file to
`registers/source-register.csv` before this requirements document is
approved.

## Business objective

Validate shipment creation requests before they are submitted to the legacy InfoAXS shipment service, so that invalid or incomplete requests are rejected early instead of generating downstream failures, manual correction effort, and inconsistent customer responses. **[business-request.md — unregistered]**

This is consistent with the broader business problem in SRC-0001 (reduce avoidable failures and rework from invalid/incomplete shipment requests) and the business-owner goal in SRC-0002 (reduce avoidable shipment rejection, improve first-time-right submission).

## Functional requirements

| ID | Requirement | Source |
|---|---|---|
| FR-01 | The system must accept a shipment validation request through a REST API. | business-request.md — unregistered |
| FR-02 | The system must validate the presence of all mandatory shipment fields. | business-request.md — unregistered |
| FR-03 | The system must apply region-specific validation rules (ISO two-letter country code checks for origin and destination). | business-request.md — unregistered |
| FR-04 | The system must return a consistent validation response structure for both valid and invalid requests. | business-request.md — unregistered |
| FR-05 | The system must record a correlation identifier and audit identifier for every request. | business-request.md — unregistered |
| FR-06 | The system must reject invalid requests without calling InfoAXS. | business-request.md — unregistered |
| FR-07 | Forwarding of valid requests to the downstream shipment creation service (InfoAXS) is planned for a later implementation phase and is not built in this demo. | business-request.md — unregistered |

## Non-functional requirements

| ID | Requirement | Source |
|---|---|---|
| NFR-01 | The validation service must be stateless (no persisted request state between calls). | SRC-0002 (Architecture note) |
| NFR-02 | Error responses must clearly identify which field(s) failed and why, to support operations staff explaining rejections. | SRC-0002 (Operations note) |
| NFR-03 | No real customer or shipment data may be used in the demo; only synthetic data is permitted. | SRC-0002 (Security note) |
| NFR-04 | Automated tests must cover all defined business rules. | business-request.md — unregistered |

## Business rules

| ID | Rule | Source |
|---|---|---|
| BR-01 | Customer account number must not be empty. | business-request.md — unregistered |
| BR-02 | Origin country must be a valid ISO two-letter country code. | business-request.md — unregistered |
| BR-03 | Destination country must be a valid ISO two-letter country code. | business-request.md — unregistered |
| BR-04 | Shipment weight must be greater than zero. | business-request.md — unregistered |
| BR-05 | Product type must be one of: Express, Standard, Economy. | business-request.md — unregistered |
| BR-06 | Consignee name is mandatory and must not be empty. | business-request.md — unregistered |
| BR-07 | Every request must receive a correlation ID. | business-request.md — unregistered |
| BR-08 | Mandatory fields are: customer account number, origin country, destination country, shipper name, consignee name, shipment weight, product type. | business-request.md — unregistered |

**Second gap identified:** `business-request.md` lists "Shipper name" as a mandatory field (Mandatory fields section) but states no explicit validation rule for it under "Initial business rules" (e.g. a non-empty check). This demo treats shipper name as mandatory/non-empty for consistency with the mandatory fields list, but this is an assumption, not an explicitly stated rule. Flagged for confirmation.

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

- `business-request.md` is treated as the primary source for this demo's functional requirements and business rules because the build instructions explicitly name it as an input, even though it currently has no source_id in `registers/source-register.csv`. This is an assumption made to proceed with the explicitly requested build; it should not be read as confirmation that the file is a reviewed/approved source.
- SRC-0001 and SRC-0002 describe a broader AI-assisted "Shipment Validation Agent" concept (classification of failure reasons, correction recommendations, human review routing). This demo builds only the deterministic validation API scope defined in `business-request.md`; the AI-assisted capabilities in SRC-0001/SRC-0002 are not in scope for this build.
- Shipper name is treated as mandatory/non-empty by inference from the mandatory fields list in `business-request.md`, since no explicit business rule for it is stated. (See Second gap identified above.)
- "Region-specific validation rules" (`business-request.md`, Required capabilities #3) is interpreted as the ISO two-letter country code checks on origin and destination, since no other region-specific rules are defined in the source.
- Audit identifier (`business-request.md`, Required capabilities #5) is assumed to be satisfied by the correlation ID unless a separate audit ID format is confirmed by a human reviewer.
- No owner, approver, or target date is stated in any source document; these fields are left unassigned rather than invented, per CLAUDE.md quality controls.

## Dependencies

- Downstream InfoAXS shipment creation service (forwarding of valid requests) — explicitly deferred to a later implementation phase per `business-request.md` and therefore not built here.
- ISO two-letter country code reference list — required for BR-02/BR-03 validation; not provided in source documents. Assumed to be implemented as a fixed reference list within the demo application (documented in the architecture stage).
- Resolution of the source-registration gap (see above) before this document can be considered fully traceable.

## Out of scope

The following are explicitly out of scope per `business-request.md`:

- Customer authentication
- Pricing
- Address resolution
- Shipment creation in InfoAXS
- Production deployment
- Performance testing

## Contradictions and quality notes

- No direct contradictions were found between SRC-0001, SRC-0002, and `business-request.md` on the core validation rules. SRC-0001/SRC-0002 describe a superset (AI-assisted agent) of the scope defined in `business-request.md` (deterministic REST API); this requirements document scopes strictly to `business-request.md` per the demo build instructions, and flags the broader material as context only.
- **Primary quality issue**: `business-request.md` — the document explicitly named as this demo's input — is not present in `registers/source-register.csv`. All requirements sourced from it are traceable to a file path but not to a governed source_id. This is flagged prominently in the Gap identified section above and should be resolved (by registering the file) before approval.
- SRC-0001 and SRC-0002 both show `review_status = Not reviewed` in the register. This requirements document should be treated as provisional pending source document review.
