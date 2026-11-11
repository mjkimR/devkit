---
id: PLAN-consolidate-spec-scope-commands
spec: SPEC-consolidate-spec-scope-commands
---

# Technical Plan: `SPEC-consolidate-spec-scope-commands` Consolidate the spec scope commands around collect

## 1. Constitution & Invariant Review

- `ADR-collect-only-scope-observation` (accepted at handoff) supersedes in part `ADR-worktrees-and-scope`: the collect
  modes, the directly callable maintenance `update` with its ACK and the maintenance ACK regression tests. No other
  ADR or architecture document states a retired command, option or code (searched `docs/decisions`,
  `docs/architecture`, `docs/development/reference` and `guides/`).
- `ADR-worktrees-and-scope` body: only its "Superseded in part" line is in the write scope (`SPEC-consolidate-spec-scope-commands`
  assumption A1); the line re-anchors its `query`/history wording to the remaining read surfaces.
- Capability contracts rewritten: `CAP-COLL-work-scope-registry` (§1-§4.9), `CAP-HARN-command-mount` §4.2 and §4.6,
  `CAP-HARN-agent-guidance` (spec-orchestrate row and "Host scope observation"), `CAP-DLV-proposal-planning`
  (`target-docs.md` reader), `UC-run-parallel-work-safely`.
- `ARCH-05-2-components`: no new feature edge. `.devkit/architecture.toml` loses the two `usecase_exceptions` for
  `query._record_warnings` and `query._spec_dir` (the module goes); the `open_session` exception stays for `release`,
  `sweep`.

## 2. Architecture Overview & Impact

| Component (`packages/devkit-spec/src/devkit_spec/`) | Change |
| --- | --- |
| `features/scope/cli/commands.py` | Only `collect`, `release`, hidden `sweep`; `compare`, `register`, `query` (and history rendering), `update`, `_echo_pairs` go; `collect` loses `--mode` |
| `features/scope/usecases/flow.py` | Keeps `Session`, `open_session`, `RegisterScopeUseCase`, `auto_register`, `own`, `ReleaseScopeUseCase`; drops the journal helpers, `Ack`, `AckStatus`, `UpdateScopeUseCase`, `_current_base_ref`, `_diff_scopes`, `_register_guidance`, `SOURCE_HANDOFF` and the `source` parameters. Creation scope = declarations + dirty paths from `services/observation.py` |
| `features/scope/usecases/inputs.py` | `observe_git`, `_fork_point`, `_is_ancestor` go; the declaration entry points stay |
| `features/scope/usecases/{query,history}.py`, `models/history.py`, `services/compare.py`, `repositories/git.py` | Deleted (no remaining caller) |
| `features/scope/usecases/sweep.py` | No journal append |
| `features/scope/models/model.py` | `Event`, `EventKind`, `AckCounts`, `JOURNAL_FILE`, `PairResult`, `Evidence` and `Problem.line` go; `Record` keeps the `last_*` fields as tolerated legacy keys |
| `features/scope/models/registry.py` | `Registry.update` and `new_request_id` go |
| `features/scope/models/deadline.py` | `JOURNAL_SECONDS` goes |
| `features/scope/repositories/localfs.py` | `update`, `append`, `history`, `journal_path` go |
| `features/scope/models/observation.py`, `services/collection.py`, `usecases/collection.py` | `CollectionOptions.mode`, mode branching, the JSON `mode` key and the mode fix strings go |
| `features/scope/cli/output.py` | `registered_dict` docstring no longer points at `query` |
| `features/scope/__init__.py` | Exports follow the removals |
| `features/delivery/usecases/{cleanup,handoff,specs}.py` | Cleanup: no journal, `own()` returning `None`; creation calls lose `source=` |
| `features/proposals/usecases/scaffold.py` | The `target-docs.md` scaffold comment names `scope collect` |
| `base/errors.py` | Five classes removed; fixes of `TOKEN_EXISTS`, `TASK_EXISTS`, `TOKEN_MISMATCH`, `TIMEOUT`, `COLLECTION_PARTIAL`, `COLLECTION_FAILED` rewritten |
| `bundles/spec/bundle/skills/spec-orchestrate/SKILL.md.jinja` | `scope collect` without `--mode worktrees`; `devkit sync` outputs committed |

## 3. Component & Interface Design

```text
devkit spec scope collect [--base REF] [--fetch REMOTE]... [--timeout 1..300] [--source-timeout 1..300] [-w DIR] [--format text|json]
devkit spec scope release [--task-id ID] [-w DIR] [--format text|json]
devkit spec scope sweep [--apply] [--expect TASK=REV]... [-w DIR] [--format text|json]   (hidden)
```

```python
def own(session: Session, *, cleanup: bool = True) -> Own | None: ...   # None: no token, or its record is gone

class RegisterScopeUseCase(BaseUseCase):
    def execute(self, session: Session, spec_dir: str, task_id: str | None = None) -> Registered: ...

def auto_register(root: Path, spec_dir: str) -> Registered | None: ...
```

Creation scope: `from_spec(root, spec_dir)`, then `observation.add_paths(scope, observation.dirty(root, deadline),
FilesystemReader(root, deadline, ReadBudget()), deadline)` with the command's `Deadline`; invalid names become
`Unresolved(<raw>, "invalid-path", observed)`.

## 4. Storage & State Management

Records stay schema version 1 with every key; `register` keeps writing `last_request_id: ""`, `last_added: 0`,
`last_removed: 0` (assumption A2). No journal is written or read; an existing `journal.jsonl` is left as it is.

## 5. Error Handling & Edge Cases

- `own()` without a token or record returns `None`; an unreadable record that may be this token's still raises
  `SPEC_SCOPE_RECORD_INVALID` at `ERROR`. The cleanup's base-checkout path treats `None` as nothing to release.
- Creation registration: a dirty-path timeout raises `SPEC_SCOPE_TIMEOUT`, which `auto_register` swallows as a verbose
  diagnostic (A3).
- `collect --mode x`: Click `No such option`, exit 2.

## 6. Verification & Test Plan

- AC-01: `tests/integration/features/scope/test_cli.py` (help lists, removed commands exit 2, release/sweep kept),
  `tests/integration/package/test_help_and_notices.py`.
- AC-02: `tests/integration/features/scope/test_flow.py` (creation record contents, invalid dirty path,
  no Git-side reasons), `tests/integration/features/delivery/test_handoff.py` and `test_spec_initialization.py`.
- AC-03, AC-04: `tests/integration/features/scope/test_collection.py`, `test_collection_horizon.py` (no `--mode`,
  no `mode` key, `--mode` refused, budgets/remote validation).
- AC-05: `tests/integration/features/scope/test_localfs.py` and `test_read_access.py` (legacy record read, journal
  untouched), `tests/integration/features/delivery/test_cleanup.py`, `tests/e2e/features/delivery/test_integration.py`.
- AC-06: `tests/integration/package/test_documented_codes.py` (both directions against CAP-COLL §4.8, fix scan).
- Commands: `just lint`, `just check devkit-spec` (Pyright, per `docs/development/setup.md`), `just test-affected` (with its
  `mode=full` fallback), `uv run devkit sync --check`, `uv run devkit rules check --ci --base main`.
- `observe_git` range cases are compared with collect's range tests before removal; a case collect does not cover
  moves to `test_collection.py`.
