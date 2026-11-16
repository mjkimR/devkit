---
id: PLAN-proposal-precedence-edges
spec: SPEC-proposal-precedence-edges
---

# Technical Plan: `SPEC-proposal-precedence-edges` Ordering claims between proposals checked when made

## 1. Constitution & Invariant Review

No `MUST` changes. The change is guidance text inside the existing Backlog and Planning procedures. It keeps
`ADR-proposal-acceptance` (an accepted proposal is never edited) and the successor-declared `depends_on` edge of
`ADR-roadmap-and-milestones-ledger`; Planning recorded no PADR because the steps restate no lasting policy beyond
those ADRs. No feature edge is added.

## 2. Architecture Overview & Impact

- Target Area: harness guidance (the spec bundle's `spec` skill references) and its capability statement.
- Design: unaffected; no component, interface or structure changes (guidance text only).
- Domain: `DOMAIN-delivery-relationships` unaffected; prerequisite, membership and provenance semantics are unchanged
  and no edge is added.
- Operations: unaffected; no runbook or operational procedure reads proposal ordering.
- Capability: `CAP-HARN-agent-guidance` "Repository Backlog and next work" gains one paragraph owning the two checks
  (statement owner); the bundle references carry the procedure.

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/`
- `packages/devkit-spec/tests/integration/bundles/spec/`
- `docs/capabilities/harness/CAP-HARN-agent-guidance.md`

### Excluded Boundaries:
- `packages/devkit-spec/src/devkit_spec/features/`
- `packages/devkit-spec/src/devkit_spec/base/`
- `packages/devkit-docs/`
- `packages/devkit/`
- `docs/decisions/`

## 3. Component & Interface Design

- `references/backlog.md.jinja`, Requests and decomposition: two list items after the editability check. The first
  names the trigger (a draft claiming to precede another proposal's handoff, or whose cost depends on another
  proposal's or spec's state) and the check (base `status`, `git branch -a --list 'dev-<slug>' '*/dev-<slug>'`,
  fetch only within existing network authorization). The second names the outcomes: handed off (a `dev-<slug>`
  branch or a `SPEC-<slug>`) rewrites the premise; a still-accepted proposal with no branch is sequenced by the user
  before the commit and the decision is stated in the draft's body.
- `references/planning.md`, Steps: the head-pinned recheck bullet runs on the first turn as well as after a refresh,
  and adds the same branch check for each proposal the draft names as following it, with the one-clause reason (a
  base or HEAD read shows a handed-off proposal as `accepted` until its Development integrates).
- The branch command is written once per reference with its exact patterns, so both places run the same check.
- `devkit sync` reprojects the changed references; its outputs are recorded as `(sync output)`.

## 4. Verification & Test Plan

- New `packages/devkit-spec/tests/integration/bundles/spec/test_ordering_claim_guidance.py`:
  - AC-01, AC-02: `assert_rule` over the rendered backlog and planning references, local and cloud.
  - AC-03: a Git fixture (base with an accepted proposal, a local `dev-<slug>`, a clone with only the fetched
    branch, and a `dev-<slug>-extra` decoy) runs the documented command and asserts its output.
- `test_bundle_budgets.py` keeps both references within 12288 bytes.
- AC-04: `uv run devkit rules check --ci --base main`.
- AC-05: `git diff --stat d889ae40f..HEAD -- packages/devkit-spec/src/devkit_spec/features/ packages/devkit-docs/`
  lists nothing.
- Checks: `just lint-check`, `just check`, `just test-affected --base d889ae40f` (fallback `mode=full` kept),
  `uv run devkit workflow envelope check --unit specs/2026-11/20261116-proposal-precedence-edges`.
- Before/after: the new guidance test fails on the handoff head (the clauses are absent) and passes after the edit;
  the head with the edit disabled is the baseline.
