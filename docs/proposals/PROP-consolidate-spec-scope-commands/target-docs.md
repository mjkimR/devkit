---
id: PROP-consolidate-spec-scope-commands-target
title: Target Living Spec Structure for PROP-consolidate-spec-scope-commands
status: draft
proposal: PROP-consolidate-spec-scope-commands
created_at: 2026-11-11
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
  - file: docs/usecases/collaboration/UC-run-parallel-work-safely.md
---

# [Blueprint] PROP-consolidate-spec-scope-commands: Target Living Spec Structure

The Living Spec changes if the proposal is accepted with its recommended answers. Items marked "(per answer)"
follow the open questions on `compare` and the journal reader.

---

## 1. System Capabilities Plan (docs/capabilities/)

- **Modify `CAP-COLL-work-scope-registry`**:
  - §2 In-Scope lists `collect`, `release` and `sweep` (plus the journal reader, per answer).
  - §3 drops rules 5 and 6's `update` clauses (optimistic concurrency and `request_id` replay); `release`
    idempotency stays.
  - §4.1: creation registration stores declarations, unresolved inputs and base anchors, no observed paths; the
    committed-range rules stay as the registration cap collect applies to registered observations (§4.9).
  - §4.3: the record schema keeps `last_request_id`, `last_added` and `last_removed` only as tolerated legacy
    fields; operations lose `update`; the deadline drops the update retry; journal events lose `update` (existing
    lines stay readable).
  - §4.4-§4.5: the command table, output examples and JSON shapes keep `collect`, `release`, `sweep` (and the
    journal reader, per answer).
  - §4.6: the Host-responsibility paragraph loses the retained hidden `update`.
  - §4.8: remove `SPEC_SCOPE_ACK_FAILED` and `SPEC_SCOPE_TOKEN_MISSING`; rewrite the `SPEC_SCOPE_TIMEOUT`,
    `SPEC_SCOPE_RECORD_MISSING` and `SPEC_SCOPE_RECORD_INVALID` conditions without `update`/`query`;
    `SPEC_SCOPE_JOURNAL_LINE_INVALID` per answer.
  - §4.9: no `--mode` table or `--base` step; collect always reads records, refs and accessible worktrees;
    snapshot evidence is creation-time declarations; the failure and result-limit fixes name no mode.
- **Modify `CAP-HARN-command-mount`**: the §4.2 row becomes `devkit spec scope collect|release|sweep` (plus the
  reader, per answer); §4.6 examples stop naming `scope update`.
- **Modify `CAP-HARN-agent-guidance`**: the spec-orchestrate row and "Host scope observation" name `scope collect`
  without `--mode`; the hidden `update` sentence goes.
- **Modify `CAP-DLV-proposal-planning`**: `target-docs.md` targets are read by `scope collect` (future horizon on
  `plan-*` sources) instead of `scope compare` (per answer).

## 2. Use Cases Plan (docs/usecases/)

- **Modify `UC-run-parallel-work-safely`**: step 1 and scenario 1 compare planned declarations through collect's
  `future` horizon (per answer on `compare`); step 5, 5c and scenarios 3-4 drop the mode and the snapshot/fetch
  conflict; the success guarantee keeps "no worker update or ACK duty".

## 3. Decisions

- Promote `PADR-collect-only-scope-observation`, superseding in part `ADR-worktrees-and-scope`; add the
  "Superseded in part by" line to that ADR without changing its other decisions.

## 4. Code and assets (not Living Spec, listed for the plan)

- `packages/devkit-spec/src/devkit_spec/features/scope/`: CLI, use cases, registry update, ACK, `observe_git`,
  history reader (per answer), `services/compare.py`; `base/errors.py` codes and fix strings; the target-docs
  scaffold comment in `features/proposals/usecases/scaffold.py`; the `usecase_exceptions` entries for
  `query._record_warnings`/`query._spec_dir` in `.devkit/architecture.toml`.
- The spec bundle's spec-orchestrate skill source (`collect` without `--mode`).
- Tests listed in `materials/scope-command-callers.md`.
