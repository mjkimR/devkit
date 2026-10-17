---
id: PLAN-hygiene-reliability
spec: SPEC-hygiene-reliability
---

# Technical Plan: Hygiene reliability

## 1. Constitution & Invariant Review

None. Changes stay within gate and workflow, using core Git helpers; devkit.advisory is unchanged.
The updated contracts are `CAP-GATE-commit-gates` and `CAP-DLV-workflow-envelopes`.

## 2. Architecture Overview & Impact

- Gate hook installation gains an automatic-only fallback-preservation option, validated within the clone lock.
- Workflow CLI resolves supplied scope revisions with core run_git in Git workspaces before writing an envelope.
- Finding parsing and serialization retain optional descriptive severity strings, including reverify carry-forward.
- Move the rules library section to rules-library.md and update inbound links.
- No new dependencies, migrations or schema versions.

## 3. Failure Modes and Boundaries

Invalid retained interpreters fall back to the validated installation interpreter. Explicit installation still honors
its python argument. Unknown revisions, trees, blobs and option-like refs are refused before writing a file.
Outside Git, lexical checks remain available. Severity is metadata and cannot change gate outcomes.

## 4. Verification

Write regression tests before implementing hook and revision changes. Cover linked-worktree removal, per-stage
fallback repair, explicit replacement, known/unknown/non-commit revisions, outside-Git behavior, severity round-trip
and invalid types. Run relevant tests, devkit lint and type checks, layering, hygiene and cumulative CI rules.
Independent medium code review and separate reconciliation verification compare the actual diff to all six criteria.
