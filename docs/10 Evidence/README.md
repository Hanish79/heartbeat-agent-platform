# 10 Evidence

Every deterministic pipeline run produces an executive evidence package:

```text
evidence/
├── tests.xml
├── traceability.csv
├── build.json
├── security.json
└── deployment.json
```

| File | Executive question |
|---|---|
| `tests.xml` | What checks ran and which failed? |
| `traceability.csv` | Can requirements be traced to delivery artifacts? |
| `build.json` | Did the governed pipeline pass? |
| `security.json` | What is the security recommendation and what remains open? |
| `deployment.json` | Was deployment approved and was anything published? |

Evidence is generated even when the pipeline fails. It is deterministic and is not produced or amended by an AI agent.
