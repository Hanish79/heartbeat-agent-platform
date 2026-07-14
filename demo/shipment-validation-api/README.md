# Shipment Validation API Demo

This directory contains the only demo scenario for the Heartbeat Agentic Delivery repository.

## Objective

Demonstrate how one approved business requirement moves through:

```text
Documentation
    ↓
Claude role prompts
    ↓
Deterministic automation
    ↓
Human approvals
    ↓
Local CI using act
    ↓
Approved demo evidence
```

## Scenario

The Shipment Validation API validates shipment data before downstream processing.

It must:

- validate required fields
- reject weight less than or equal to zero
- validate two-letter ISO country codes
- return structured errors
- preserve correlation ID
- prevent invalid requests from continuing downstream

## What This Demo Proves

- one source requirement
- one traceable lifecycle
- one plan approval gate
- one release approval gate
- one deterministic pipeline
- one local CI workflow
- one controlled output package

## What This Demo Does Not Prove

- production deployment
- live customer integration
- Google Drive API automation
- autonomous AI publishing
- multiple use cases
- production data processing

## Starting Point

Read:

```text
demo/shipment-validation-api/runbook.md
```
