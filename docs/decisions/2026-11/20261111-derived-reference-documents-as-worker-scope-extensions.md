---
id: ADR-derived-reference-documents-as-worker-scope-extensions
title: Derived reference documents as worker scope extensions
summary: "For quick references, guides and package READMEs that restate changed behavior, we admit them as recorded Tier B extensions with a named reason, to keep references in step without Host recovery, accepting more extension collisions."
supersedes:
  - ADR-recorded-adjacent-path-extensions-for-development-workers
status: accepted
created_at: 2026-11-11
---

# [ADR-derived-reference-documents-as-worker-scope-extensions] Derived reference documents as worker scope extensions

## 1. Context & Problem Statement

A Development worker's declared write scope estimates the files a unit touches and protects files it must not
change; it is not a collision barrier, and collisions from later extensions are accepted. Tier B admits an exact
adjacent file inside the same documented feature root or test mirror, or an existing Living Spec document whose
reason names the restated contract ID. Quick references, user guides and package READMEs must stay in step with the
Living Spec and packages, yet are neither. Workers therefore admit them in one unit by naming a contract ID and
refuse them in another, and the Host repairs the missed document in a separate commit.

## 2. Decision Drivers

- Keep derived references in step within the unit that changes the behavior they restate.
- Give workers and reviewers one class to judge, with no contract ID required where none exists.
- Keep agent instruction files, agent assets and protected classes outside self-admission.

## 3. Considered Options

1. Keep the current classes: the Host keeps repairing missed references, and judgment stays inconsistent.
2. Require planners to name every derived reference up front: predicting them is the estimate that already misses.
3. Admit an exact existing derived reference document as a recorded Tier B class: bounded autonomy with the
   existing annotation, record and review.
4. Admit any documentation file: includes agent instructions and release documents that need Host authority.

## 4. Decision Outcome

Option 3 is selected because it keeps references in step and gives reviewers one rule, while the protected
classes stay out.

- A Development worker may record as a Tier B extension an exact existing quick-reference document, user guide or
  the README of a package that owns a source the unit changes, when its edited passages restate a public name,
  command or behavior the task changes. → `CAP-DLV-delivery-roles` worker write boundaries (MAY).
- The extension's reason names the changed symbol, command or contract ID; the edit adds no document or section
  and changes only the restating passages. → `CAP-DLV-delivery-roles` worker write boundaries (MUST).
- Agent instruction files, bundle and agent assets and release documents stay outside Tier B.
  → `CAP-DLV-delivery-roles` worker write boundaries (MUST NOT).
- The annotation, typed record, review severity, Tier C and inspection decisions are unchanged.

Supersedes in part `ADR-recorded-adjacent-path-extensions-for-development-workers`: the list of documents that qualify as Tier B extensions, which gains derived reference documents. Its annotation, record, review, denial and inspection decisions remain in force.

## 5. Consequences

Units land with references in step, and parallel units that both extend into one reference document may conflict at
merge, which the conflict-tolerant integration absorbs. Reviewers judge whether each edited passage restates the
changed behavior. Inspection checks only structural evidence; agent instruction files remain a recognizable
protected class. If extensions into references start carrying unrelated cleanup, narrow the class.

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_scope_extension_guidance.py` checks the class in the
  local and cloud worker and review guidance.
- `packages/devkit-spec/tests/integration/features/worker/test_scope_extensions.py` checks that recorded reference,
  guide and README extensions pass and agent instruction files fail.
- Whether an edited passage restates the changed behavior: Review only.
