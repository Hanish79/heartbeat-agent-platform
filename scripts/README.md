# Phase 3 Deterministic Automation

No script in this directory calls an AI service.

## Scripts

| Script | Purpose |
|---|---|
| `sync_drive.py` | Synchronize repository folders with a mounted or mirrored Google Drive folder |
| `validate_documents.py` | Validate documentation structure, links, statuses, and placeholders |
| `approval_engine.py` | Parse and enforce Markdown approval records |
| `traceability.py` | Build a requirement-to-artifact traceability matrix |
| `pipeline.py` | Orchestrate deterministic validation and publishing stages |
| `publish.py` | Publish only approved outputs, with dry-run as the default |

## Safe Defaults

- publishing is dry-run unless `--execute` is supplied
- Git operations require both `--git` and `--execute`
- Google Drive must be mounted or mirrored locally
- missing approval blocks progression
- any validation error returns a non-zero exit code

## Example

```bash
python scripts/pipeline.py
python scripts/pipeline.py --require-plan-approval
python scripts/pipeline.py --require-release-approval
python scripts/pipeline.py --require-release-approval --publish
python scripts/pipeline.py --require-release-approval --publish --execute-publish
```
