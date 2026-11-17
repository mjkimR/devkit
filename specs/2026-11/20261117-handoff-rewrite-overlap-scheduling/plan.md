---
id: PLAN-handoff-rewrite-overlap-scheduling
spec: SPEC-handoff-rewrite-overlap-scheduling
---

# Technical Plan: `SPEC-handoff-rewrite-overlap-scheduling` Handoff rewrites as integration evidence in scope scheduling

## 1. Constitution & Invariant Review

No ADR: the change refines how the Host reads the existing `current` horizon under `ADR-worktrees-and-scope`
and changes no collection contract (`CAP-COLL-work-scope-registry`).

## 2. Architecture Overview & Impact

Wording only, in the scheduling statement and its Living Spec mirror:

- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/SKILL.md.jinja`, the scheduling
  bullet: add one directive. A `current` overlap whose evidence is `observed` only for both units, on a path each
  unit's handoff commit changed and `git diff --name-only <handoff commit>..<unit head>` does not list, does not
  serialize Development; it stays integration-conflict evidence and no payload names it as a write target.
- `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, "Host scope observation": the same rule in the mirrored
  sentence.
- `specs/2026-11/feedback/20261116-handoff-reference-overlap-serializes-workers.md`: resolved with a disposition.

Design, domain and operations: unaffected; no component, term or command changes (Planning, "Design, domain and
operations impact").

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`
- `docs/capabilities/harness/CAP-HARN-agent-guidance.md`
- `specs/2026-11/feedback/20261116-handoff-reference-overlap-serializes-workers.md`

### Excluded Boundaries:
- `packages/devkit-spec/src/devkit_spec/features/scope/`
- `packages/devkit-docs/`
- `packages/devkit/`

## 3. Verification & Test Plan

- AC-01, AC-02: review of the amended bullet against the spec; `uv run devkit rules check --phase hygiene` on the
  skill source reports no `RULE-agent-asset-wording` warning, and the self-containment `rg` finds no new document ID.
- AC-03: `uv run devkit sync` then `uv run devkit generated check`, `just lint-check`,
  `uv run devkit rules check --ci --base main`, `just test-affected --base main`, `git diff --check`.
