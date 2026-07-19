Read CLAUDE.md first.

Review:

- registers/source-register.csv
- registers/action-register.csv
- registers/decision-register.csv
- registers/risk-register.csv
- registers/artifact-register.csv

Validate:

1. Every action, decision and risk has a valid source_id.
2. Every artifact references at least one source.
3. IDs are unique.
4. Source references are sufficiently precise.
5. Unknown owners and deadlines are blank, not inferred.
6. Approved status is supported by explicit evidence.
7. Low-confidence findings are identified.

Run:

powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/powershell/Invoke-HeartbeatCI.ps1

Create:
documents/04-draft-working-area/traceability-validation-report.md

Do not modify source documents.
Do not promote artifacts.
Do not commit or push.