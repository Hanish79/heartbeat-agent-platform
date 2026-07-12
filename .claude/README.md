# Claude Configuration

This directory contains the role prompts used in Phase 2 of the Heartbeat Agentic Delivery Demo.

## Agents

| Agent | Purpose |
|---|---|
| `business.md` | Business analysis and requirements traceability |
| `architect.md` | Architecture and interface planning |
| `developer.md` | Implementation planning only |
| `security.md` | Security review and threat modeling |
| `qa.md` | Test strategy and quality planning |
| `reviewer.md` | Independent cross-artifact review |

## Phase 2 Constraint

No agent may create application code, test code, deployment code, or publishing automation during this phase.

## Recommended Sequence

```text
business
   ↓
human review
   ↓
architect
   ↓
human review
   ↓
developer planning
   ↓
security
   ↓
qa
   ↓
reviewer
   ↓
human approval
```
