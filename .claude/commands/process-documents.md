Read CLAUDE.md first.

Process all registered source documents that have not yet been reviewed.

Inputs:
- documents/01-raw-source-documents
- registers/source-register.csv

For each source document:

1. Create a structured summary.
2. Extract decisions, actions, risks, dependencies, owners and deadlines.
3. Identify contradictions and missing information.
4. State document currency and whether it may be superseded.
5. Link extracted items to the source_id.
6. Save summaries under documents/02-source-summaries.

Update:
- registers/action-register.csv
- registers/decision-register.csv
- registers/risk-register.csv
- registers/artifact-register.csv

Generate:
- logs/pipeline-execution-report.md

Controls:
- Do not modify source documents.
- Do not promote drafts to approved outputs.
- Do not invent facts, dates, ownership, approval or status.
- Do not commit or push.
- Clearly separate confirmed facts from assumptions.