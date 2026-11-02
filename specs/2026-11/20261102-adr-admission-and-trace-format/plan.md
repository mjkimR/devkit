---
id: PLAN-adr-admission-and-trace-format
spec: SPEC-adr-admission-and-trace-format
---

# Technical Plan: `SPEC-adr-admission-and-trace-format` ADR admission criteria and restatement trace format

## 1. Constitution & Invariant Review

None. The change refines authoring guidance from `SPEC-adr-normative-outcomes` and reformats existing clauses. No
decision changes, so it needs no new ADR. The ADR edits are format edits, which `ADR-immutable-decisions-editable-records`
allows in place.

## 2. Architecture Overview & Impact

| Component | Change | Serves |
| --- | --- | --- |
| docs bundle `instructions/decision-writing.md` | New "When to Write" section with the admission criteria for ADRs and PADRs. "Decision Outcome Clauses" switches to declarative clauses with a trailing `→ <ID> <location> (<KEYWORD>)` trace. | AC-01, AC-03 |
| docs bundle `templates/decision.md` | Example clause in the trace format | AC-03 |
| spec bundle `skills/spec/references/planning.md` | The New PADR step applies the admission criteria first | AC-02 |
| `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py` | Assertions for the criteria and the trace format | AC-01 to AC-03 |
| `CAP-HARN-agent-guidance` | The `decision-writing` row mentions the admission criteria and the trace | AC-01, AC-03 |
| The 13 marked ADRs | Format-only rewrite of each marked clause | AC-04 |

## 3. Verification & Test Plan

- `just test devkit-spec tests/integration/bundles/spec/test_writing_guidance.py`
- `uv run devkit rules check`, and `uv run devkit rules check --phase hygiene` on the edited bundle assets
- `just test-affected`
- `rg -n -U '\b(MUST|SHOULD|MAY)\b[^\n]*\n?[^\n]*→ ' docs/decisions` returns no inline keyword on a marked clause
