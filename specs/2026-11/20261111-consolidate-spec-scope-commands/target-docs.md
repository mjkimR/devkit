---
id: PROP-consolidate-spec-scope-commands-target
title: Target Living Spec Structure for PROP-consolidate-spec-scope-commands
status: draft
proposal: SPEC-consolidate-spec-scope-commands
created_at: 2026-11-11
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
  - file: docs/usecases/collaboration/UC-run-parallel-work-safely.md
  - file: docs/decisions/2026-11/20261102-worktrees-and-scope.md
---

# [Blueprint] PROP-consolidate-spec-scope-commands: Target Living Spec Structure

The Living Spec changes if the proposal is accepted, following the user's answers recorded in its §6 (journal
removed, `compare` retired, creation dirty paths kept, `--base` kept).

---

## 1. System Capabilities Plan (docs/capabilities/)

- **Modify `CAP-COLL-work-scope-registry`**:
  - Summary and §1-§2: In-Scope lists `collect`, `release` and `sweep`, creation registration and the cleanup; the
    journal and the retired commands leave the scope.
  - §3: rule 5 (optimistic concurrency of `update`) goes; rule 6 keeps only `release` idempotency; rule 8 (journal)
    goes; rule 2 now also covers invalid dirty paths at creation.
  - §4.1: creation registration records declarations, unresolved inputs, base anchors and the dirty paths at
    creation from collect's observation service; the committed-range rules stay as the registration cap collect
    applies to registered observations (§4.9); the `missing-base-ref`, `missing-base-revision` and
    `unknown-base-revision` rows, the paragraph on `update` re-detecting the base, and "changes ... at the register
    or update that recollects" are rewritten for creation-only records.
  - §4.3: record fields keep `last_request_id`, `last_added`, `last_removed` as tolerated legacy fields; operations
    lose `update`; the deadline drops the update retry; the journal paragraph goes (an existing file is left
    untouched); the read-access MUST is re-anchored from `query`, `query --spec` and `query --history` to collect and
    the registry reads of release, sweep and the cleanup.
  - §4.4-§4.5: the command table, output examples and JSON shapes keep `collect` (without `--mode`), `release` and
    `sweep`.
  - §4.6: the Host-responsibility paragraph loses `query`, history, `compare` and the hidden `update`.
  - §4.8: remove `SPEC_SCOPE_ACK_FAILED`, `SPEC_SCOPE_TOKEN_MISSING`, `SPEC_SCOPE_RECORD_MISSING`,
    `SPEC_SCOPE_JOURNAL_UNAVAILABLE` and `SPEC_SCOPE_JOURNAL_LINE_INVALID`; rewrite `SPEC_SCOPE_TIMEOUT`,
    `SPEC_SCOPE_RECORD_INVALID` and `SPEC_SCOPE_TOKEN_MISMATCH` without `update`/`query`; mark
    `SPEC_SCOPE_TOKEN_EXISTS`, `SPEC_SCOPE_TASK_EXISTS` and `SPEC_SCOPE_SHARED_WORKTREE` as verbose diagnostics of
    creation registration.
  - §4.9: no `--mode` table; `--base` stays as the explicit base override; collect always reads records, refs and accessible worktrees; snapshot evidence is the
    creation-time record; the failure, metadata-limit and partial fixes name no mode and no budget for
    `result-limit`.
- **Modify `CAP-HARN-command-mount`**: the §4.2 row becomes `devkit spec scope collect|release|sweep`; §4.6 examples
  stop naming `scope update`.
- **Modify `CAP-HARN-agent-guidance`**: the spec-orchestrate row and "Host scope observation" name `scope collect`
  without `--mode`; the hidden `update` sentence goes.
- **Modify `CAP-DLV-proposal-planning`**: `target-docs.md` targets are read by `scope collect` as `future` evidence
  once the proposal has a `plan-*` source; queued drafts are not observed.

## 2. Use Cases Plan (docs/usecases/)

- **Modify `UC-run-parallel-work-safely`**: step 1 and scenario 1 compare planned declarations through collect once a
  unit has a `plan-*` or `dev-*` source, and state that queued drafts are not observed; step 5, 5c and scenarios 3-4
  drop the mode and the snapshot/fetch conflict; the success guarantee keeps "no worker update or ACK duty".

## 3. Decisions

- Promote `ADR-collect-only-scope-observation`, superseding in part `ADR-worktrees-and-scope`; in that ADR add the
  "Superseded in part by" line and reword the `query`/history mentions of §4 "Registry storage and read access", §5
  and §6 to the remaining read surfaces, without changing its other decisions.

## 4. Code and assets (not Living Spec, listed for the plan)

- `packages/devkit-spec/src/devkit_spec/features/scope/`: CLI, use cases, registry update, ACK, `observe_git`,
  journal and history reader, `services/compare.py`, `own()`; `base/errors.py` codes and fix strings; the
  target-docs scaffold comment in `features/proposals/usecases/scaffold.py`; the `registered_dict` docstring; the
  `usecase_exceptions` entries for `query._record_warnings`/`query._spec_dir` in `.devkit/architecture.toml`.
- The spec bundle's spec-orchestrate skill source (`collect` without `--mode`).
- Tests listed in `docs/materials/2026-11/20261111-consolidate-spec-scope-commands/scope-command-callers.md`.
