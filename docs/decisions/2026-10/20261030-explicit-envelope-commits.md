---
id: ADR-explicit-envelope-commits
title: Explicit commits for individual workflow envelopes
summary: "For record-only workflow steps, we commit one named envelope through a separate explicit command with a deterministic subject, to simplify retry and preserve authoring compatibility, accepting one extra command and manual combined commits."
proposal: SPEC-workflow-record-auto-commit
status: accepted
created_at: 2026-10-30
---

# [ADR-explicit-envelope-commits] Explicit commits for individual workflow envelopes

- **Status**: Accepted
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

CAP-DLV-delivery-workflows requires stage-boundary commits. CAP-DLV-workflow-envelopes authoring writes files and
allocates sequences without committing. Re-running authoring after a Git failure would create a different record.
A stage may also produce source or document changes that must remain in a combined commit.

## 2. Decision Drivers

- Remove routine commit-message composition for record-only stages.
- Retry an existing record without allocating another sequence.
- Keep normal authoring and library use outside Git compatible.
- Preserve normal Git hooks and signing with a proportionate implementation.

## 3. Considered Options

- **A — Separate single-record commit command (selected):** Commits an explicitly named existing envelope. One
  extra invocation gives writing and committing separate observable failure boundaries and reuses the same retry.
- **B — Authoring --commit plus a recovery command:** Saves one happy-path invocation, but needs both authoring
  and existing-record commit interfaces and a contract for file-written/commit-failed partial results.
- **C — Commit every record write or workflow next:** Removes explicit invocation but changes existing write-only
  or read-only behavior and can split records from related changes. Rejected.
- **D — Keep manual Git with message guidance:** Adds no runtime behavior, but leaves exact staging and message
  generation repeated at every eligible step. It remains the fallback for combined changes and repository policies.

## 4. Decision Outcome

Select option A: workflow envelope commit takes --unit and one --file. The file is an existing new envelope under
that Unit. Existing authoring commands remain write-only. Use the normal index and Git commit; refuse other dirty
paths, partial staging, modified historical envelopes and unsupported repository state. A failed attempt may leave
only the selected file staged, which the same command accepts when bytes match. A clean exact record already in
HEAD returns already_committed without creating a commit.

Generate chore(workflow): record <slug> <kind>-<NN> from the tracked SPEC/PROP anchor ID and envelope identity.
Put workflow, segment and stage in the body. Preserve evidence SHAs and report actual HEAD after hooks, including
metadata-rewriting hooks. Unexpected postconditions retain state and require inspection. Custom Unit identities
and rejecting message policies use the existing manual commit route. Require one active writer per worktree;
local precondition/postcondition checks address accidental mistakes without adding a global transaction service.

Opt in at record-only final-report and review/reverify call sites. Keep combined commits for source fixes, document
reflection, multiple envelopes, feedback with files, and worker/problem records requiring accompanying work.
No approval, integration or publication authority changes. This adds an optional operation and does not supersede
an accepted decision. `SPEC-workflow-record-auto-commit` specifies result/error behavior and acceptance scenarios.

## 5. Consequences

- Routine message generation and exact staging become deterministic for eligible single records.
- Retry uses an existing record path; no immutable-envelope schema change is needed.
- One extra command remains after authoring, and combined stage changes still require a manual commit.
- The command cannot mechanically establish whether an envelope belongs with already committed semantic changes;
  executor guidance and review enforce that boundary.
- Message-hook incompatibility remains visible rather than gaining a custom message-policy discovery framework.
- Integration preparation must follow the record commit because its source identity includes HEAD.

## 6. Confirmation

Development adds integration coverage under packages/devkit/tests/integration/features/workflow/ for exact changed
paths, dirty-state refusal, rejected hooks, staged-file retry, idempotent repeat, metadata-rewriting hooks and
uncertain outcomes. Unit coverage tests deterministic identity and result/error fields. Bundle integration checks
under packages/devkit-spec/tests/integration/bundles/spec/ cover eligible and combined-commit guidance in feature
and bugfix flows. AC-01 through AC-05 in `SPEC-workflow-record-auto-commit` define acceptance. Review checks the semantic
co-commit boundaries; no runtime check can infer them from envelope YAML alone.
