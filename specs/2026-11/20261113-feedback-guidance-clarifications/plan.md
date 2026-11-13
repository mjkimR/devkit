---
id: PLAN-feedback-guidance-clarifications
spec: SPEC-feedback-guidance-clarifications
---

# Technical Plan: `SPEC-feedback-guidance-clarifications`

## 1. Constitution & Invariant Review

None. Preserve `CAP-DLV-delivery-workflows` and `CAP-DLV-workflow-envelopes`: the existing new reconcile-check
route, PASS/FAIL/SKIP, task coverage, optional UX review and two independent rounds. No new dependency, feature
edge, runtime behavior or ADR is needed.

## 2. Architecture Overview & Impact

The spec bundle owns review evidence and stage sequencing (AC-01 through AC-04); the docs bundle owns the project
style-source fallback (AC-05). Keep shipped assets self-contained. Reflect procedure details in the two existing
delivery capabilities and relevant workflow reference passages; no new Living Spec document is planned.

## 3. Component & Interface Design

Use existing `envelope new --kind reconcile-check --stage living-spec-draft --findings-file -` with resolution and
waiver fields. Keep check provenance in SKIP detail with source envelope and full SHA. Link the optional Screens
procedure from specify completion, give its ordered combined-commit sequence, and name build-verify in the UX
closure command. For visual style, prefer project style/token ownership already present; create shared style
background only when the authorized change needs it and its write scope admits it.

## 6. Verification & Test Plan

- Add meaningful bundle instruction-contract checks beside existing spec and docs bundle tests, covering AC-01 to AC-05.
- Run relevant bundle integration suites, `just lint-check devkit-spec`, `just lint-check devkit-docs`,
  `just check devkit-spec`, `just check devkit-docs` and
  `just test-affected --base 021ad3c06c5ac0b3fffd8dad2fe931c2687db48e --tier all`.
- Run the five-scenario before/after probe described in `SPEC-feedback-guidance-clarifications`; no live host gate.
- Run sync, its final check, diff/envelope validation and cumulative
  `uv run devkit rules check --ci --base a6872bf5ef7d99a10e8bc3799f88b615c03fd47e`.
- Independent code review and independent reconcile verification are required at medium because agent-facing
  text changes in two packages. Preserve each role's exact source identity and verify no writes by tree snapshot.
- Reuse passing checks for subsequent record-only changes; rerun relevant checks for any source fix.
