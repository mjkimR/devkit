---
id: PLAN-retire-stale-integration-clauses
spec: SPEC-retire-stale-integration-clauses
---

# Technical Plan: `SPEC-retire-stale-integration-clauses` Retire stale integration ADR clauses

## 1. Constitution & Invariant Review

The change replaces accepted decision clauses, so it needs a new ADR with `supersedes`. That ADR is the deliverable.
It changes no capability `MUST`: `CAP-INT-mcp-services` already states the current refusal points.

## 2. Architecture Overview & Impact

| Component | Change | Serves |
| --- | --- | --- |
| `docs/decisions/2026-11/20261102-retire-stale-integration-approval-clauses.md` | New partial-superseding ADR | AC-01, AC-02 |
| `ADR-local-and-pull-request-integration` | "Superseded in part by" line under the heading and at the `--auto`/`--admin` item | AC-01 |
| `ADR-configuration-language-and-rendering` | "Superseded in part by" lines under the heading and at the approval-form and local-text items | AC-01, AC-02 |
| The three source feedback files under `specs/2026-11/20261102-adr-normative-outcomes/feedback/` | Status and Disposition | AC-03 |

## 3. Verification & Test Plan

- `uv run devkit rules check` (decision supersession, references, feedback status).
- `just test-affected`.
