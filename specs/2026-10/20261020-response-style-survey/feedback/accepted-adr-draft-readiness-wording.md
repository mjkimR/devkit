---
id: FB-accepted-adr-draft-readiness-wording
title: Accepted response-style ADR retains draft-readiness wording
scope: repo
kind: friction
category: docs-mismatch
target: docs/decisions/2026-10/20261020-response-style-adaptive-replies.md
skill: spec-specify
agent: codex
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-accepted-adr-draft-readiness-wording] Accepted response-style ADR retains draft-readiness wording

## 1. Friction / Question

- **Context**: Development checked the accepted proposal's premises after handoff.
- **Expectation**: Promoted ADR text makes its accepted decision distinguishable from historical proposal preparation.
- **Actual**: The ADR has `status: accepted` but retains a statement that the draft is a direction for user review
  and formal adoption follows the workflow. Reading this without the handoff evidence can make acceptance unclear.
- **Interpretation Chosen**: Use accepted frontmatter and the recorded handoff authority; preserve the accepted ADR.
- **Suggestion**: During Planning acceptance preparation, review present-tense readiness statements before PADR
  promotion. Do not make the handoff engine rewrite arbitrary narrative automatically.

## Diagnostic Details

- **Reproduction**: Read the promoted adaptive-replies ADR and the carried Development skeleton.
- **Expected / Actual**: A settled decision was expected; accepted metadata coexists with draft-readiness prose.
- **Versions**: Observed on handoff base `1c238be1df936aa86d466a53e9abc5f6322a7aef`.
- **Conditions**: Proposal-to-spec handoff, Codex Development worker, accepted ADR edits excluded.
- **Workarounds Attempted**: Used explicit handoff authority and drafted measurable Development criteria; succeeded.
- **Related Assets**: `ADR-response-style`, `SPEC-response-style-survey`, proposal acceptance preparation.

## Evidence

```text
status: accepted
The draft is a direction for user review, not a plan-accept decision or deployed instruction.
```

The readiness sentence does not invalidate acceptance, but costs a separate authority check. This is wording
friction in the preserved decision, not evidence that the accepted behavior should change.

## Disposition

The session corrected the readiness prose in `ADR-response-style`: the draft-review
statement now describes Planning history, and the outcome explicitly records the accepted direction.
The user authorized this one-off wording correction to the accepted ADR; its decision, constraints and
qualification about unobserved runtime quality remain unchanged. No new decision or handoff-engine change
was introduced.

Verification: low-effort self-review compared the before/after decision and confirmed only readiness wording
changed; `just lint-check spec`, `just check spec` and `just test-affected --base main` passed (1,111 tests).
