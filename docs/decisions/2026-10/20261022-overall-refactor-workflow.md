---
id: ADR-overall-refactor-workflow
title: An Overall Refactor Task Kind With a Direct-Only Workflow
summary: "For project-level restructuring that the unit workflows slow down, we add the overall-refactor task kind with one direct-only workflow without a unit, to let the Host and the user restructure freely with subagents, accepting that only the final report and commits record the work."
status: accepted
created_at: 2026-10-22
---

# [ADR-overall-refactor-workflow] An Overall Refactor Task Kind With a Direct-Only Workflow

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `capabilities/delivery/`, `architecture/`

---

## 1. Context & Problem Statement

Work is classified on `task-kind` (`feature`, `bugfix`) and `planning-depth` (`session`, `spec`, `proposal`). A
structural change across the project (package boundaries, conventions, document systems, ledgers) fits none of the
depths: `session` cannot change the Living Spec, `spec` demands `spec.md`, `plan.md` and `tasks.md` with fixed task
boundaries before code, and `proposal` adds Planning and usually workers. Such work is broad and its direction settles
while it proceeds, so the unit documents and worker boundaries hold it back.

---

## 2. Decision Drivers

- Project-level restructuring proceeds in the conversation, with the user deciding as the shape emerges.
- No document overhead that does not change the result: no Unit, no envelopes, no reconcile record.
- A refactor inside one feature keeps its existing path; the new kind must not attract it.
- Gates, CI and integration authority stay as they are.

---

## 3. Considered Options

### Option 1: A `overall-refactor` task kind with one workflow without depth (Selected)
- **Overview**: `sdd-overall-refactor`, `direct` only, no Unit, gates `plan-intent` and `dev-integration`.
- **Pros**: one new concept; the qualified name keeps small refactors on the feature path.

### Option 2: A `refactor` task kind
- **Cons**: every small refactor would be routed to the unconstrained path.

### Option 3: A new planning depth combined with every task kind
- **Cons**: two more workflows and a fourth depth whose meaning is scope, not what must be settled first.

---

## 4. Decision Outcome

We adopt **Option 1**. This adds a value to the task-kind axis of `ADR-delivery-classification`.

- **Applies to**: a change that adds no behavior and restructures several areas of the project at once, whose
  direction settles while the work proceeds. A refactor inside one feature or module is `feature` work.
- **Workflow**: `overall-refactor` has no planning depth and runs `sdd-overall-refactor`: `intent-refactor`
  (`plan-intent`), `restructure`, `report-refactor`, `commit-refactor` (exit `lint-ci-clean`), `approval-refactor`
  (`dev-integration`), `merge`. It never creates a proposal or spec bundle.
- **Mode**: `direct` only. The predefined `planning-worker` and `development-worker` are not used; general subagents are
  used freely for drafting, edits and research, while the Host splits the work, checks results, talks with the user and
  commits.
- **Records**: the Living Spec changes with the code; a lasting policy is an ADR. The final response and the commit
  body report what changed and why, the breaking changes and the verification (full test suite, lint, types,
  `devkit rules check`). No other record is written.
- **Integration**: on the base checkout, or on `dev-<slug>` through the session integration path with
  `task_kind: overall-refactor` in its claims.

---

## 5. Consequences

- **Positive**: project-level restructuring runs without unit overhead and with parallel subagents.
- **Negative / Risks**: no per-task boundary check; the review of the final diff and the full test suite carry the
  verification.
- **Follow-ups**: none.

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_workflows.py` (the `sdd-overall-refactor` definition).
- `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py` (session claims with `overall-refactor`).
