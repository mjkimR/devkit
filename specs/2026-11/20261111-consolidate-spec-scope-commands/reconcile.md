---
reconcile_id: REC-consolidate-spec-scope-commands
status: pending
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/usecases/collaboration/UC-run-parallel-work-safely.md
    resolution: modified
  - file: docs/capabilities/collaboration/CAP-COLL-shared-artifacts.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-worktrees-and-scope.md
    resolution: waived
    rationale: The handoff already added its Superseded in part line, which RULE-decision-supersession fixes to the superseder's statement; rewording the query and history mentions of its body is outside the Development write scope and is left for the Host.
---

# Reconciliation: `SPEC-consolidate-spec-scope-commands`

`ADR-collect-only-scope-observation` (promoted at handoff, unchanged here: its origin wording names the spec and the
proposal's materials correctly) records the decision. Each target below states the delivered contract.

- `CAP-COLL-work-scope-registry`: summary, §1 and §2 name `collect`, `release`, hidden `sweep`, creation registration
  and the cleanup; the journal and the retired commands leave the scope (Non-Goals add record refresh and an event
  history). §3 drops the update concurrency rule and the journal rule, keeps release idempotency (now rule 5), rule 2
  covers invalid dirty paths, and the cleanup and shared-path rules become 7 and 8. §4.1 states creation's
  declarations plus dirty paths through the observation service, collect's committed-range cap and intersection
  rule, and the `unknown-base` reason; the Git-side reasons stay only for older records. §4.3 keeps the `last_*` keys
  as tolerated legacy fields, drops `update` and the journal, and re-anchors the read-access MUST to `collect` and the
  registry reads of `release`, `sweep` and the cleanup. §4.4-§4.6 list only the remaining commands, outputs and JSON
  shapes, state that the retired commands and `collect --mode` are Click usage errors, and drop `query`, history,
  `compare` and the hidden `update` from the Host paragraph. §4.8 removes the five retired codes and rewrites
  `SPEC_SCOPE_TIMEOUT`, `SPEC_SCOPE_RECORD_INVALID`, `SPEC_SCOPE_TOKEN_MISMATCH`, `SPEC_SCOPE_STALE_REVISION` and
  `SPEC_SCOPE_SPEC_NOT_FOUND`, marking the creation-only codes as verbose diagnostics (AC-06 checks the table against
  the defined codes in both directions). §4.9 replaces the mode table with one source set, keeps `--base`, `--fetch`
  and the budgets, drops `mode` from the JSON and names the `result-limit` fix.
- `CAP-HARN-command-mount`: the §4.2 row is `devkit spec scope collect|release|sweep`; §4.6 no longer names
  `scope update`.
- `CAP-HARN-agent-guidance`: the spec-orchestrate row and "Host scope observation" name `scope collect` without a
  mode; the hidden `update` sentence goes.
- `CAP-DLV-proposal-planning`: `target-docs.md` targets are read by `scope collect` as `future` evidence once the
  proposal has a `plan-*` source; queued drafts are not observed.
- `UC-run-parallel-work-safely`: step 1 and scenario 1 compare declarations through collection for units with a
  `plan-*` or `dev-*` source; step 5, extension 5c and scenarios 2-4 drop the mode, the snapshot/fetch conflict and
  the journal.
- `ADR-worktrees-and-scope` (waived, spec assumption A1): unchanged. Its "Superseded in part" line, added at handoff,
  must repeat the superseder's statement verbatim (`RULE-decision-supersession`); the body rewording of the
  `query`/history mentions in §4, §5 and §6 that the statement announces is outside the Development write scope and
  remains for the Host.

- `CAP-COLL-shared-artifacts`: the store-boundary sentence names "any scope journal an earlier version left" instead
  of journals the registry keeps (review-01 P3).

## Outside the write scope (for the Host)

- `CAP-WT-task-worktrees` (`docs/capabilities/worktree/`, line 212) still says the post-finish extension covers "the
  scope registry, its journal and the proposal-directory cleanup"; the journal no longer exists. The file is outside
  this Development write scope, so the wording is left for the Host (review-01 P3).
- `ADR-worktrees-and-scope` body rewording (assumption A1, above).

## Entrypoints

`devkit spec entrypoints derive` proposed broad helper and test paths for every target; none was applied: the
targets already name the scope feature, its CLI, `usecases/collection.py` and the cleanup as doorways.

## Non-Living-Spec changes

- Spec bundle guidance: `spec-orchestrate/SKILL.md.jinja` names `devkit spec scope collect` without
  `--mode worktrees`; `devkit sync` rewrote `.devkit/installation.json` (the only tracked sync output).
- The `target-docs.md` scaffold comment names `scope collect`; `.devkit/architecture.toml` loses the two
  `usecase_exceptions` of the deleted `usecases/query.py`.

## No-impact checks

- `docs/architecture/`, `docs/development/reference/`, `guides/` and `docs/steering/` name none of the retired
  commands, options or codes.
- No domain term was introduced or renamed.

## Deferred work and source feedback

None: no deferred item, and the spec carries no source feedback ID.
