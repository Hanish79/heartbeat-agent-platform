Read CLAUDE.md first.

Build the Shipment Validation API demo using:

- examples/shipment-validation/01-business-input/business-request.md
- registers/source-register.csv

Complete the following stages.

## Stage 1: Requirements

Create:

examples/shipment-validation/02-requirements/requirements.md

Include:

- Business objective
- Functional requirements
- Non-functional requirements
- Business rules
- Acceptance criteria in Given/When/Then format
- Assumptions
- Dependencies
- Out-of-scope items
- Traceability to the correct source_id

Do not continue to architecture unless:

approvals/requirements.json

has status "approved".

## Stage 2: Architecture

After requirements approval, create:

examples/shipment-validation/03-architecture/architecture.md

Include:

- Context
- Components
- Request and response flow
- Validation service responsibilities
- Error model
- Audit and correlation handling
- Security assumptions
- Deployment assumptions
- Architecture decisions
- Risks
- Traceability to requirements

Do not continue to development unless:

approvals/architecture.json

has status "approved".

## Stage 3: Development

After architecture approval, create a small Python FastAPI implementation under:

examples/shipment-validation/04-development

Include:

- Application code
- Pydantic request and response models
- Validation logic
- Error handling
- Correlation ID handling
- requirements.txt
- README.md

## Stage 4: Testing

Create tests under:

examples/shipment-validation/05-testing

Cover:

- Missing customer account
- Invalid origin country
- Invalid destination country
- Zero shipment weight
- Negative shipment weight
- Unsupported product type
- Missing consignee name
- Valid request
- Correlation ID generation

## Stage 5: Evidence

Create:

- examples/shipment-validation/06-evidence/test-results.md
- examples/shipment-validation/06-evidence/traceability.csv
- examples/shipment-validation/06-evidence/build.json
- examples/shipment-validation/06-evidence/security.json

Do not approve artifacts.
Do not alter source documents.
Do not commit or push.
Do not bypass approval files.