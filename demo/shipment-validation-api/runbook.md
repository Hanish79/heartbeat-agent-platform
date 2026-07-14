# Shipment Validation API Demo Runbook

## Demo Goal

Show one complete, governed delivery path for the Shipment Validation API.

Do not introduce another example during the presentation.

## Preparation

From the repository root:

```bash
python --version
docker --version
act --version
```

Confirm these files exist:

```text
docs/
.claude/agents/
scripts/
.github/workflows/local-ci.yml
demo/shipment-validation-api/
```

## Step 1: Show the Single Source of Truth

Open:

```text
docs/README.md
docs/00 Vision/README.md
docs/02 ADLC/README.md
docs/05 Human Approval/README.md
```

Explain:

> Documentation defines the process before any agent or automation is allowed to act.

## Step 2: Show the Only Business Input

Open:

```text
demo/shipment-validation-api/input/shipment-validation-requirement.md
```

Highlight:

- BR-001 through BR-006
- AC-001 through AC-004
- Shipment Validation API is the only use case

## Step 3: Show the Claude Roles

Open:

```text
.claude/agents/business.md
.claude/agents/architect.md
.claude/agents/developer.md
.claude/agents/security.md
.claude/agents/qa.md
.claude/agents/reviewer.md
```

Explain:

> Each role is bounded. No role may approve itself, publish autonomously, or change governance.

## Step 4: Show the Expected Planning Outputs

Open:

```text
demo/shipment-validation-api/expected/requirement-summary.md
demo/shipment-validation-api/expected/architecture-overview.md
demo/shipment-validation-api/expected/test-plan.md
demo/shipment-validation-api/expected/security-review.md
```

Explain:

> These files demonstrate the expected shape of controlled outputs before coding.

## Step 5: Show Human Approval

Open:

```text
approvals/proposal.json
```

Explain:

> The workflow cannot continue while status is PENDING.

For the live demo, copy this approval record into:

```text
approvals/plan-approval.md
```

Then complete:

```text
Status: APPROVED
Reviewer: <name>
Date: YYYY-MM-DD
```

Check all checklist items.

## Step 6: Run Deterministic Validation

```bash
python scripts/pipeline.py --repo-root .
```

Expected result:

```text
validate_documents: PASS
traceability: PASS
pipeline: PASS
```

## Step 7: Run Local CI with act

List jobs:

```bash
act -l
```

Run:

```bash
act push \
  -W .github/workflows/local-ci.yml \
  -e demo/shipment-validation-api/act/push-event.json \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

Expected result:

```text
Deterministic validation: PASS
```

## Step 8: Show Input Payloads

Open:

```text
demo/shipment-validation-api/requests/valid-request.json
demo/shipment-validation-api/requests/invalid-request.json
```

Explain the expected behavior:

- valid request returns VALID
- invalid request returns structured errors
- both responses preserve correlationId
- invalid request never proceeds downstream

## Step 9: Show Release Approval

Open:

```text
approvals/deployment.json
```

Explain:

> Release approval remains PENDING until local CI, security, QA, and independent review evidence are complete.

## Step 10: Close the Demo

Use this statement:

> The purpose of this demo is not autonomous coding. It is controlled acceleration. One approved requirement enters the process, every artifact remains traceable, deterministic checks enforce quality, and humans retain decision authority at every critical gate.
