# Source summary: Business problem — Shipment Validation Agent

## Traceability
- Source documents used: 01_business_problem.md
- Source file name(s) / ID: documents\01-raw-source-documents\01_business_problem.md (SRC-0001)
- Generation date: 2026-07-16
- Artifact status: Draft — not reviewed
- Artifact owner: Not assigned (no owner stated in source)
- Related identifiers: DEC-0001, DEC-0002, DEC-0003, DEC-0004, RSK-0003, RSK-0004, RSK-0006

## Structured summary

### Current problem (confirmed fact, as stated)
Incoming shipment requests arrive through API, file and messaging channels. Invalid or
incomplete requests create avoidable failures, manual rework and inconsistent customer
responses.

### Desired outcome (confirmed fact, as stated)
Introduce an AI-assisted validation agent that:
- validates mandatory shipment fields
- detects inconsistent values
- classifies likely failure reasons
- recommends corrections
- never changes a shipment automatically without a defined rule
- routes uncertain cases for human review

### Scope (confirmed fact, as stated)
The demo covers JSON shipment requests only.

### Out of scope (confirmed fact, as stated)
- Production deployment
- Direct updates to InfoAXS
- Customer authentication
- Pricing calculation
- Dangerous goods regulatory approval
- Personally identifiable production data

## Decisions extracted
| ID | Decision | Basis |
|---|---|---|
| DEC-0001 | Demo scope is limited to JSON shipment requests only | Stated directly in "Scope" |
| DEC-0002 | Production deployment, direct InfoAXS updates, customer authentication, pricing calculation, dangerous goods regulatory approval, and PII production data are excluded from the demo | Stated directly in "Out of scope" |
| DEC-0003 | The agent must never change a shipment automatically without a defined rule | Stated directly in "Desired outcome" |
| DEC-0004 | Uncertain cases must be routed for human review | Stated directly in "Desired outcome" |

## Risks / gaps extracted
| ID | Risk / gap | Basis |
|---|---|---|
| RSK-0003 | The JSON shipment request schema (mandatory fields, validation rules) is not defined anywhere in this document | Absence noted during review |
| RSK-0004 | The method for classifying "likely failure reasons" and generating "recommended corrections" is not defined (no rule set or model referenced) | Absence noted during review |

## Actions extracted
None. No action items, assignees, or deadlines are stated in this document.

## Owners and deadlines
None stated. This document does not name any individual owner or date.

## Contradictions and outdated information
None found within this document in isolation. See cross-document contradiction check below.

## Cross-document check (against SRC-0002 — synthetic stakeholder notes)
- No contradictions identified. "Never changes a shipment automatically without a defined
  rule" (SRC-0001) is consistent with the Architecture note in SRC-0002 that deterministic
  rules must remain separate from probabilistic AI recommendations.
- No outdated/superseded status: this is the only version of this document in the repository
  (registers/source-register.csv shows a single entry, review_status = "Not reviewed").

## Missing approvals / unresolved dependencies
- registers/source-register.csv lists this source with `review_status = Not reviewed` and no
  `owner` — the document has not been formally reviewed or approved.
- No approval record for this document exists under any approval-gate location referenced by
  scripts/approval_engine.py (proposal / architecture / deployment gates).