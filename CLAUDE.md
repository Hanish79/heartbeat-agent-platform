# Heartbeat Project Instructions

## Objective

Support the Aramex Heartbeat modernization program by processing project
documents, generating controlled outputs, maintaining traceability, and
supporting repeatable delivery workflows.

## Source document rules

- Treat documents/01-raw-source-documents as immutable.
- Never edit, rename, move, or delete source files.
- Store document summaries under documents/02-source-summaries.
- Store working outputs under documents/04-draft-working-area.
- Promote files to documents/03-approved-outputs only after explicit human approval.
- Move superseded approved artifacts to documents/05-archive-superseded.

## Traceability

Every generated artifact must identify:

- Source documents used
- Source file names
- Generation date
- Artifact status
- Artifact owner
- Related requirement, decision, risk, or action identifiers

## Quality controls

Before presenting an output:

- Check for contradictions across source documents
- Identify missing information
- Separate confirmed facts from assumptions
- Flag outdated or superseded documents
- Preserve business and technical terminology
- Do not invent owners, dates, decisions, approvals, or status

## Git controls

- Do not commit directly to main
- Create a feature branch for each change
- Use conventional commit messages
- Do not commit credentials, tokens, secrets, or temporary files
- Do not push unless explicitly instructed

## Naming convention

Use:

YYYYMMDD_<artifact-type>_<subject>_vX.Y.<extension>

Example:

20260716_architecture-review_shipping-api_v0.1.md