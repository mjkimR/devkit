# Scope command callers and pipelines (Planning evidence)

Evidence gathered by the Planning `scout` at head `835863a3` (base `ba3bcce4`). Paths are relative to the
repository root; the scope feature is `packages/devkit-spec/src/devkit_spec/features/scope/`.

## Callers per command

| Command | CLI callers outside the feature, its tests and CAP-COLL | Internal Python use that survives retirement |
| --- | --- | --- |
| `register` | none; named only in fix strings (`usecases/flow.py` `_register_guidance`, `own()` errors) | `RegisterScopeUseCase` through `auto_register` from `devkit spec proposal handoff` and `devkit spec new` (best effort, every failure swallowed) |
| `query` | none | `Registry.query` stays for `release`, `sweep`, post-finish cleanup and collect's registry inventory; `QueryScopesUseCase` has no other user |
| `query --history` | none; its `[NEXT_CMD]` names itself | `LocalRegistry.history` and `QueryScopeHistoryUseCase` have no other user; the journal writers are independent |
| `compare` | no guidance invocation; text references in the target-docs scaffold comment (`features/proposals/usecases/scaffold.py`), `CAP-DLV-proposal-planning` and UC-run-parallel-work-safely scenario 1 | `services/compare.py` survives only through `query` and `update`; dead after both go |
| hidden `update` | none; `CAP-HARN-agent-guidance` says an operator may call it directly, not as a worker step | `UpdateScopeUseCase` and `Registry.update` have no other caller |
| `release` | spec `worktree` reference; `CAP-HARN-command-mount` | post-finish cleanup (base-checkout task, scoped run), registration rollback |
| hidden `sweep` | spec `worktree` reference, spec-integrate (`CAP-HARN-agent-guidance`) and several fix strings | post-finish cleanup calls `Registry.sweep` directly |
| `collect` | spec-orchestrate (`--mode worktrees`, the default) and `CAP-HARN-agent-guidance` | none |

devkit-agt reaches the cleanup only through the `devkit.post_finish` entry point (`ScopedCleanup` methods), never the
CLI. devkit-viewer, devkit-mcp and devkit-adaptive read neither the registry nor the journal.

## The update write path

Only the hidden `update` uses: `request_id` replay, the `Ack` model and `[SCOPE_ACK]`, `ScopeAckFailedError`,
the record fields `last_request_id`, `last_added`, `last_removed` (registration writes zeros) and the journal `update`
events (read only by `query --history`). Existing records carry these fields, so record parsing must keep accepting
them.

## Codes

- Used only by retired paths: `SPEC_SCOPE_ACK_FAILED`; `SPEC_SCOPE_TOKEN_MISSING` (raised by `own()`, whose remaining
  cleanup caller checks the token first).
- Still raised by a kept path: `SPEC_SCOPE_RECORD_MISSING` (cleanup's base-checkout path), `SPEC_SCOPE_STALE_REVISION`
  (sweep), `SPEC_SCOPE_TOKEN_MISMATCH` (`release --task-id`), `SPEC_SCOPE_RECORD_INVALID`, `SPEC_SCOPE_TIMEOUT` (its
  fix names the update retry: rewrite), the creation and collection codes.
- Depends on the journal-reader decision: `SPEC_SCOPE_JOURNAL_LINE_INVALID`. Becomes internal only:
  `SPEC_SCOPE_SPEC_NOT_FOUND` (creation registration swallows it).
- `tests/integration/package/test_documented_codes.py` checks only that each source code is documented; a stale
  CAP-COLL §4.8 row for a removed code is not caught.

## The two paths-changed pipelines (SP-1)

| Aspect | Registry (`usecases/inputs.py` `observe_git`) | Collection (`services/observation.py`, `services/collection.py`) |
| --- | --- | --- |
| Callers | register and update; after retirement only creation registration | collect |
| Base | the record's base revision (registration HEAD) and base ref | `--base`, `devkitBase`, record base ref, then remote-HEAD or main-checkout hint |
| Fork | best merge-base | exactly one merge-base, else `unknown-base` |
| Range | registration cap with the §4.1 intersection rule | the same cap for registered observations; branch-relative merge-base to tip otherwise |
| Dirty paths | `diff --cached`, `diff`, `ls-files --others --exclude-standard` | same argument lists |
| Invalid paths | dropped silently | reported unresolved (`invalid-path`) |
| Runner | `run_git` under the `[tool.spec.scope] timeout` deadline; timeout fails the command | own Popen runner (process-group kill, output cap, sanitized env); timeout is partial coverage |
| Change detection | none | HEAD and status fingerprints before and after (`observation-changed`) |

## Collect options

Guidance passes only `--mode worktrees` (the default). No guidance passes `--base`, `--fetch`, `--timeout` or
`--source-timeout`. Fix strings name `--timeout 120 --source-timeout 30` (`SPEC_SCOPE_COLLECTION_PARTIAL`),
"select a readable source with --mode" and `--mode snapshot` (`SPEC_SCOPE_COLLECTION_FAILED`). Snapshot candidates
are added in every mode, so the default already includes snapshot and ref sources. Tests use `--mode snapshot|refs`
in about 15 functions, `--base` in about 27, `--fetch` in about 4.

## Documents naming the commands

CAP-COLL-work-scope-registry §2, §3 rules 5-6, §4.3 operations and deadline, §4.4-§4.6, §4.8, §4.9;
CAP-HARN-command-mount §4.2 row and §4.6 examples (`scope update`); CAP-HARN-agent-guidance (spec-orchestrate row,
"Host scope observation", the hidden `update` sentence); UC-run-parallel-work-safely steps 1, 5, 5c, the success
guarantee and scenarios 1, 3, 4; CAP-DLV-proposal-planning (target-docs read by `scope compare`);
ADR-worktrees-and-scope §4 "Host-owned scope observation" (collect modes, retained hidden `update` and ACK) and §6;
the spec-orchestrate skill source. `docs/development/reference/` names none.

## Test impact (approximate)

About 20 test functions (27 cases) exercise only retired CLI paths; about 8 test `observe_git` semantics and move to
the unified implementation; about 40 use retired commands as fixtures or vary collect options and need rewriting
(`test_cli.py`, `test_flow.py`, `test_collection.py`, `test_collection_horizon.py`, `test_inputs.py`,
`test_localfs.py` with `tests/support/spec_support/scope_contract.py`, `delivery/test_cleanup.py`,
`e2e/features/delivery/test_integration.py`, `package/test_help_and_notices.py`).
