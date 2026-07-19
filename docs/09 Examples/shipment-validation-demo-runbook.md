# Heartbeat Shipment Validation ADLC Demo Runbook

## Demo objective

Demonstrate a controlled AI-assisted development lifecycle that converts a business request into requirements, architecture, code, tests, evidence, approval, and a versioned GitHub release.

## Demo duration

15 to 20 minutes.

## Demo scenario

A business request is received to validate shipment creation requests before forwarding them to InfoAXS.

The workflow demonstrates:

- Immutable source ingestion
- Requirements generation
- Human approval
- Architecture generation
- Human approval
- Code and test generation
- Automated validation
- Traceability
- Release approval
- GitHub version control

## Prerequisites

- Repository available under `C:\Heartbeat`
- Python virtual environment available
- Claude Code installed
- Git configured
- GitHub remote configured
- Required source documents copied locally
- Approval files reset to `pending`
- No uncommitted unrelated changes
- Local CI passes

## Pre-demo reset

Run:

```powershell
cd C:\Heartbeat
git status
git branch --show-current
.\scripts\powershell\Invoke-HeartbeatCI.ps1