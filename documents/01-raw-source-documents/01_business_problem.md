# Business problem: Shipment Validation Agent

## Current problem
Incoming shipment requests arrive through API, file and messaging channels. Invalid or incomplete requests create avoidable failures, manual rework and inconsistent customer responses.

## Desired outcome
Introduce an AI-assisted validation agent that:
- validates mandatory shipment fields;
- detects inconsistent values;
- classifies likely failure reasons;
- recommends corrections;
- never changes a shipment automatically without a defined rule;
- routes uncertain cases for human review.

## Scope
The demo covers JSON shipment requests only.

## Out of scope
- Production deployment
- Direct updates to InfoAXS
- Customer authentication
- Pricing calculation
- Dangerous goods regulatory approval
- Personally identifiable production data
