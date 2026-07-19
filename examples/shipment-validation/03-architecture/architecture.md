# Shipment Validation API — Architecture

## Traceability

| Field | Value |
|---|---|
| Source requirements | examples/shipment-validation/02-requirements/requirements.md |
| Requirements approval | approvals/requirements.json — approved by Hani Shtayyeh, 2026-07-14T10:00:00+03:00 |
| Source documents | SRC-0003 (primary), SRC-0001, SRC-0002 (supporting context) |
| Generation date | 2026-07-19 |
| Artifact status | Draft — pending approval |
| Artifact owner | Not assigned |
| Related requirement, decision, risk, or action identifiers | FR-01–FR-07, NFR-01–NFR-04, BR-01–BR-08, AC-01–AC-09 |

## Context

The Shipment Validation API is a synchronous REST service that sits in front of the legacy InfoAXS shipment creation service. It receives a shipment creation request, validates it against mandatory-field and business-rule checks, and returns a validation result. Per FR-06/FR-07, invalid requests are rejected without calling InfoAXS, and forwarding of valid requests to InfoAXS is explicitly deferred to a later implementation phase — this demo does not integrate with InfoAXS at all.

```
Client ──▶ Shipment Validation API ──▶ (validation result only)

           InfoAXS forwarding = out of scope (later phase, per FR-07)
```

## Components

| Component | Responsibility | Traceability |
|---|---|---|
| API layer (FastAPI app) | Exposes the REST endpoint, parses the request body, returns the HTTP response. | FR-01 |
| Request model (Pydantic) | Declares the shape of an inbound shipment validation request and its field types. | FR-02, BR-08 |
| Response model (Pydantic) | Declares the shape of the validation response (status, errors, correlation ID). | FR-04, BR-07 |
| Validation service | Applies mandatory-field presence checks and business rules (BR-01–BR-08); produces a list of field-level errors. | FR-02, FR-03, FR-06, BR-01–BR-08 |
| Country code reference | Fixed ISO two-letter country code list used by the validation service for origin/destination checks. | BR-02, BR-03 |
| Correlation/audit handler | Generates a correlation ID for every request (valid or invalid) and attaches it to the response. | FR-05, BR-07, AC-09 |

This demo has no persistence layer and no external service calls, consistent with NFR-01 (stateless).

## Request and response flow

1. Client sends `POST /validate-shipment` with a JSON body.
2. FastAPI parses the body against the Pydantic request model. Type-level parsing failures (e.g. wrong JSON shape) are returned as HTTP 422 by FastAPI's built-in handling.
3. A correlation ID is generated for the request before validation logic runs, so that it is present on every response, including early failures (FR-05, AC-09).
4. The validation service runs all business rule checks (BR-01–BR-08) and collects every failing field into a list, rather than stopping at the first failure — so a caller can see all problems in a single response.
5. If the error list is empty, the response returns a successful validation result (AC-08). If not, the response returns a failure result listing every failed field and reason (FR-04, AC-01–AC-07).
6. InfoAXS is never called by this service (FR-06). No downstream call exists in this phase (FR-07).

```
POST /validate-shipment
   │
   ▼
[Correlation ID generated]
   │
   ▼
[Pydantic parses request body] ──(parse error)──▶ HTTP 422
   │
   ▼
[Validation service runs BR-01..BR-08]
   │
   ├─ errors found ──▶ HTTP 200, { valid: false, errors: [...], correlation_id }
   │
   └─ no errors ─────▶ HTTP 200, { valid: true, errors: [], correlation_id }
```

**Architecture decision — HTTP status code for business-rule failures:** business-rule validation failures (BR-01–BR-08) return HTTP 200 with `valid: false` and an error list, not HTTP 4xx. Rationale: these are well-formed requests that are semantically invalid per business rules, not malformed HTTP requests. This mirrors the distinction requested in FR-04 ("a consistent validation response") for both valid and invalid outcomes. Only structurally malformed JSON (missing required JSON keys/wrong types) results in HTTP 422 via Pydantic. This is a design decision made in the absence of an explicit source statement on status codes; flagged for approval.

## Validation service responsibilities

The validation service is the single place where BR-01–BR-08 are enforced:

- BR-01: customer account number non-empty
- BR-02: origin country is a valid ISO two-letter code (against the fixed reference list)
- BR-03: destination country is a valid ISO two-letter code (against the fixed reference list)
- BR-04: shipment weight > 0
- BR-05: product type in {Express, Standard, Economy}
- BR-06: consignee name non-empty
- BR-07: correlation ID present on every response (enforced by the correlation handler, not the validation service itself)
- BR-08: shipper name non-empty (per the Gap identified in requirements.md — shipper name is listed as mandatory but has no explicit rule stated in SRC-0003; treated as non-empty by inference, flagged as assumption)

The validation service is a pure function: given a parsed request, it returns a list of zero or more field errors. It has no side effects, no state, and no external dependencies (NFR-01).

## Error model

Each error entry contains:

| Field | Description |
|---|---|
| `field` | The name of the field that failed validation. |
| `code` | A short machine-readable rule code (e.g. `FIELD_REQUIRED`, `INVALID_COUNTRY_CODE`, `INVALID_WEIGHT`, `INVALID_PRODUCT_TYPE`). |
| `message` | A human-readable explanation of the failure, to support operations staff explaining rejections (NFR-02). |

The response envelope is:

```json
{
  "valid": false,
  "errors": [
    { "field": "customer_account_number", "code": "FIELD_REQUIRED", "message": "Customer account number must not be empty." }
  ],
  "correlation_id": "..."
}
```

All business rules produce exactly one error code each, enumerated in the validation service. Multiple failing fields all appear in the same `errors` list (no fail-fast short-circuiting), so a single API call surfaces every problem with the request.

## Audit and correlation handling

- A correlation ID (UUID v4) is generated per request by the correlation/audit handler, independent of validation outcome, satisfying FR-05 and AC-09.
- The correlation ID is returned in the response body and also set on a response header (`X-Correlation-Id`) so it can be captured by upstream logging/tracing infrastructure without parsing the body.
- Per the requirements assumption, a distinct "audit identifier" is not implemented separately from the correlation ID in this demo; the correlation ID is treated as satisfying both purposes unless a reviewer specifies a distinct audit ID format. This assumption is carried forward from requirements.md and requires confirmation.
- No request or response payloads are persisted or logged to disk in this demo (no persistence layer exists at all); any logging is limited to process-standard-output request/response summaries for local demonstration purposes.

## Security assumptions

- NFR-03 (no real customer or shipment data) is enforced procedurally, not technically: this demo must only ever be exercised with synthetic data. The application itself performs no PII detection, since that capability is out of scope for both SRC-0003 and this build.
- Customer authentication is explicitly out of scope (SRC-0003 Out of scope). This demo implements no authentication or authorization layer. It is not suitable for exposure outside a controlled demo/test environment.
- No secrets, credentials, or tokens are required by this service, since it has no external dependencies in this phase.
- Input validation (BR-01–BR-08) also serves as basic defense against malformed input reaching any future downstream InfoAXS integration, but no InfoAXS integration exists yet to protect.

## Deployment assumptions

- Production deployment is explicitly out of scope (SRC-0003 Out of scope). This architecture assumes local/demo execution only (e.g. `uvicorn` run locally), not a hosted environment.
- Performance testing is explicitly out of scope (SRC-0003 Out of scope); no throughput, latency, or scaling design is included.
- The service is stateless (NFR-01), so if a future phase requires deployment, it can scale horizontally without session affinity — noted for future reference only, not designed here.

## Architecture decisions

| ID | Decision | Rationale |
|---|---|---|
| AD-01 | Use FastAPI + Pydantic for the API layer and request/response models. | Directive per build instructions (Stage 3); also gives free request-shape validation and OpenAPI docs generation. |
| AD-02 | Business-rule failures return HTTP 200 with `valid: false`, not HTTP 4xx. | See flagged decision under Request and response flow. Distinguishes "malformed request" from "well-formed but business-invalid request." |
| AD-03 | Validation collects all field errors rather than failing fast on the first error. | Matches FR-04's requirement for a consistent, complete validation response; better supports NFR-02 (clear explanation of failure). |
| AD-04 | Country code list is a fixed, hardcoded reference list within the application (not an external service call). | No source document specifies a country code data source; keeps the service stateless and dependency-free (NFR-01), consistent with demo/out-of-scope constraints (no production deployment). |
| AD-05 | Correlation ID doubles as the audit identifier in this demo. | No distinct audit ID format is specified in any source document; avoids inventing an unconfirmed data element. Flagged assumption, carried from requirements.md. |

## Risks

| ID | Risk | Impact | Mitigation / note |
|---|---|---|---|
| R-01 | AD-02 (HTTP 200 for business failures) may not match caller expectations if a future consumer expects HTTP 4xx for invalid requests. | Medium — could require a breaking API change later. | Flagged for explicit approval at this architecture gate; documented as AD-02. |
| R-02 | Shipper name validation rule (BR-08) is an inferred rule, not an explicit source rule. | Low — demo scope only. | Carried from requirements.md; needs confirmation before being treated as a confirmed business rule. |
| R-03 | Audit identifier is not distinct from correlation ID. | Low in demo; potential rework if a real audit trail format is later mandated. | Documented as AD-05; revisit if this demo is extended toward production. |
| R-04 | Country code reference list is hardcoded; unclear if it is complete/authoritative. | Low in demo; would need a maintained source in a later phase. | Documented as AD-04; out of scope for production readiness in this demo. |
| R-05 | No authentication layer exists. | Low in demo (explicitly out of scope); high if ever exposed beyond a controlled environment. | Documented under Security assumptions; do not deploy this demo outside a controlled environment. |

## Traceability to requirements

| Architecture element | Requirements covered |
|---|---|
| API layer | FR-01 |
| Request/response models | FR-02, FR-04, BR-08 |
| Validation service | FR-02, FR-03, FR-06, BR-01–BR-06, BR-08 |
| Correlation/audit handler | FR-05, BR-07, NFR-04 (AC-09 coverage) |
| Error model | FR-04, NFR-02 |
| Security assumptions | NFR-03, out-of-scope: customer authentication |
| Deployment assumptions | Out-of-scope: production deployment, performance testing |
| No InfoAXS integration | FR-06, FR-07, out-of-scope: shipment creation in InfoAXS |
