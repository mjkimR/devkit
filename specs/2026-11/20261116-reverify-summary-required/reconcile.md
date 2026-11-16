---
reconcile_id: REC-reverify-summary-required
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
  - file: docs/development/reference/workflow.md
    resolution: modified
---

# Reverify summary reconciliation

## Contracts changed

- `CAP-DLV-workflow-envelopes` section 2, the `--summary TEXT` row of the authoring flag table: `reverify` requires a
  nonempty summary when authoring and refuses a missing or whitespace-only one with `ENVELOPE_FLAG_INVALID`,
  `[TARGET] --summary` and a `[FIX]` naming `--summary`, before writing (AC-01). Source:
  `compose_envelope` in `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py`.
- `CAP-DLV-workflow-envelopes` section 5 item 3: an unauthored record's `ENVELOPE_COMMIT_INVALID` names each failing
  field and its `[FIX]` names the kind's writer command with `--summary`/`--stage`: an uncommitted file is rewritten
  and retried as the same file, a file already in HEAD is kept and a new envelope is written instead (AC-02, AC-03;
  the committed-record branch is the fix of review-01 finding 1). Source: `require_authored` in
  `services/envelope/commit.py`, called from `usecases/commit_envelope.py`.
- `CAP-DLV-cli-and-output`: the `envelope reverify` synopsis notes the required `--summary`; the
  `ENVELOPE_FLAG_INVALID` row lists the missing reverify summary; the `ENVELOPE_COMMIT_INVALID` row describes the
  field-naming refusal. Codes, exit codes and actions are unchanged.
- `docs/development/reference/workflow.md`: the `envelope reverify` example passes `--summary`.

Agent-facing bundle text (not Living Spec, changed under Task 3): the `spec-review` skill and the `spec` skill's
`references/planning.md` reverify invocations now pass `--summary`; `devkit sync` updated the tracked
`.devkit/installation.json` and the ignored managed copies.

## Unaffected layers

- Use cases: `UC-drive-development-to-integration` cites `ENVELOPE_COMMIT_INVALID` only as a code; its steps already
  pass `--summary` to reverify through the `spec-review` skill, so no step changes.
- Architecture: `KIND_COMMANDS` moved from `cli/envelope.py` to `models/envelope.py` inside the same feature so the
  service names the writer command without importing an adapter; no layer rule or feature edge changes
  (`.devkit/architecture.toml` untouched).
- Design, domain and operations: no `DESIGN-`, `DOMAIN-` or `OPS-` document owns envelope authoring or the explicit
  commit refusal text (`devkit docs search "envelope commit"` lists only the two capabilities above and
  `ADR-explicit-envelope-commits`, whose decision is unchanged).
- Decisions: the nonempty-summary rule of an explicit commit is `CAP-DLV-workflow-envelopes` section 5 item 3;
  this change enforces it earlier for `reverify` and names the failing field. The decision of
  `ADR-explicit-envelope-commits` (an explicit one-file commit command) is unchanged, so no ADR is needed.
- Fix hints: the review `--from` refusal and the review/challenger "close the round" fix in `authoring.py` now
  suggest `envelope reverify ... --summary "<judgment>"`, so following them is not refused (reconcile-check-01
  finding 1).

## Entrypoints

`devkit spec entrypoints derive` proposed the changed helpers, tests and skill sources for both capabilities. All
were rejected: the existing doorways (`cli/envelope.py`, `services/envelope/authoring.py`,
`usecases/commit_envelope.py`) already lead to every changed path, and helpers, models, tests and bundle text are not
CAP doorways. No `entrypoints` changed.

## Source feedback

- `FB-reverify-writes-envelope-commit-refuses`: resolved by `SPEC-reverify-summary-required`. The writer refuses a
  missing summary (AC-01) and the commit refusal names the empty field and `--summary` (AC-02); verified by the
  regression tests in `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py` and the code
  review of this range.
