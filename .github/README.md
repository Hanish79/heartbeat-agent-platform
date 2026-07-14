# CI Configuration

`workflows/local-ci.yml` runs deterministic repository checks only.

It does not:
- call Claude or any other AI service
- publish approved outputs
- push commits
- access Google Drive
- use production credentials

It validates:
- Python syntax
- documentation structure
- traceability
- deterministic pipeline behavior
- approval records when already approved
- publish dry-run behavior
