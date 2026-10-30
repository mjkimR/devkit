---
reconcile_id: REC-worker-audit-known-host-advance
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-orchestration-workers.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-drop-the-base-checkout-equality-from-worker-validation.md
    resolution: waived
    rationale: "Promoted at handoff and unchanged here: it already records the dropped equality, the own-envelope condition, the accepted partial committed escape and both superseded clauses of ADR-orchestration-workers."
---

# Reconciliation: `SPEC-worker-audit-known-host-advance`

## Living Spec reflection

- `CAP-DLV-delivery-workflows` §4.6.2 One-shot activity workers: the Host-validation paragraph now states that the
  Host records and compares no base-checkout state, that base advances by the Host, another session or an unknown
  author never block the range, and that a partial committed escape is the accepted residual
  (`ADR-drop-the-base-checkout-equality-from-worker-validation`). The acceptance requirements name the turn's own
  `worker` envelope (absent at the last accepted head) instead of an unchanged base (AC-02).
- `CAP-DLV-delivery-workflows`, worker inspection inputs: the base checkout's HEAD and dirty paths are information,
  not checks; the sentence no longer names a Host comparison with a saved state (AC-02). The inspection contract
  itself (inputs, checks, exit codes, `base_checkout` field) is unchanged, matching the unchanged code.
- `ADR-orchestration-workers`: one pointer line under "Committed results and their validation" names the promoted ADR
  and the two superseded clauses (that subsection's "and the base checkout unchanged" and the Decision Outcome's Range
  inspection comparison); its decision text and frontmatter are unchanged (AC-02).

## No-impact review

- `devkit docs refs ADR-orchestration-workers --direction in` and a repository search for the pre-spawn record and
  the unchanged-base wording found no other current contract restating the equality: `docs/usecases/`,
  `docs/architecture/`, `docs/development/`, `guides/` and the other bundle sources have none.
  `CAP-DLV-proposal-planning` keeps `SPEC_HANDOFF_BASE_DIRTY` and integration keeps `WORKTREE_BASE_DIRTY`, both
  unchanged by design.
- Completed specs and earlier materials (`MAT-codex-native-worker-evidence`, `MAT-base-observation-options`) that
  restate the equality stay as history (spec Non-Goal 7).
- No domain term is introduced or renamed; the glossary is unchanged.

## Deferred work

- None filed. The follow-up for a partial committed escape (a commit-gate check refusing a base-checkout commit that
  touches a path an active task worktree's unit owns) is conditional on an observed escape; the user decided to file
  no draft before that (`ADR-drop-the-base-checkout-equality-from-worker-validation`, Consequences).

## Entrypoints

`devkit spec entrypoints derive` offered `.devkit/installation.json`, the `spec-delegate/references` directory and the
two test files for `CAP-DLV-delivery-workflows`; all are rejected: tests and the receipt are no doorways, and the
reference directory was touched only for wording. The capability's existing entrypoints (the workflows directory and
the worker CLI) stay.
