---
id: PLAN-formal-docs-feedback-handoff
spec: SPEC-formal-docs-feedback-handoff
---

# Technical Plan: `SPEC-formal-docs-feedback-handoff` Feedback lifecycle domain and proposal handoff design documents

## 1. Constitution & Invariant Review

None. Both documents are of delivered kinds at their area-scoped paths (`ADR-area-scoped-design-bundles`) with
problem-first openings (`ADR-problem-first-formal-document-openings`). Ownership follows
`CAP-DOCS-documentation-ownership` §3.1 and §3.3: one reader question each, normative statements cited, never moved.
No ADR is needed.

## 2. Architecture Overview & Impact

Target area: `docs/` only.

| Task | Document | Kind instruction | Sources to verify (AC-05) |
| --- | --- | --- | --- |
| 1.1 | `docs/domain/delivery/DOMAIN-feedback-lifecycle.md` | `domain-writing` | `CAP-DOCS-document-model` Feedback lifecycle, `CAP-DLV-proposal-planning` §3.1, `CAP-DLV-delivery-workflows` Source feedback at completion, `CAP-HARN-agent-guidance` Feedback capture policy and §4.5, `ADR-feedback-lifecycle-ledger`, spec bundle `spec-feedback/SKILL.md`, `playbooks/feedback-hygiene/SKILL.md`, `skills/spec/references/source-feedback.md`, `features/proposals/usecases/feedback.py`, docs `kinds.py` terminal statuses |
| 1.2 | `docs/designs/delivery/DESIGN-proposal-handoff/design.md` | `design-writing` | `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`, `.../proposals/usecases/feedback.py`, `.../proposals/services/{body,rewrite,history}.py`, `.../delivery/usecases/{handoff,native_handoff}.py`, `.../scope/usecases/flow.py`, `CAP-DLV-proposal-lifecycle` §4.1-4.3 and Host-authorized proposal lifecycle CLI, commit `93e72152c` |

Implementation choices: the domain entry goes to `docs/domain/delivery/` (spec Assumptions). The design follows
the source order of `handoff_proposal`, which differs from the payload's listing in one place: the projected
dependency graph check (`_check_dependency_projection`) is the last preflight, after the body is carried, because it
validates the generated `spec.md` text. The composed worktree creation runs before all of it.

Design, domain and operations impact: one design and one domain entry are added. `DOMAIN-delivery-relationships` and
`DESIGN-workflow-stage-evaluation` are unaffected: the new documents link to them as related entries and restate
none of their statements. No operations document routes feedback or handoff symptoms.

## 3. Error Handling & Edge Cases

- A claim the current source contradicts is corrected in the new document; a gap or over-detail in an owner becomes
  feedback in this unit.
- The worked example is a historical commit: where the current code behaves differently (own-path boundary
  omission), the design says so.

## 4. Verification & Test Plan

- `uv run devkit rules check --ci --base cdbcdf224` (AC-01, AC-06, reference resolution).
- `uv run devkit docs resolve DOMAIN-feedback-lifecycle` and `DESIGN-proposal-handoff` (AC-01).
- `just lint-check` and `git diff --check` (AC-06).
- `just test-affected --base cdbcdf224` (docs-only; the full-mode fallback is kept).
- Manual read against the cited source and the example commit, recorded in review (AC-02 to AC-05).
- `uv run devkit workflow envelope check --unit specs/2026-11/20261116-formal-docs-feedback-handoff`.
