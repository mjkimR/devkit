# Review-refactor sweep: `devkit playbook` CLI group (manual evidence)

`SPEC-review-refactor` AC-07. Manual evidence, not test coverage: one real, bounded, read-only batch of the
`review-refactor` playbook (read from its bundle source, since this repository does not select `maintenance`). It
stops at its decision round with nothing applied, as an unattended run does; a real decision round is a separate
invocation after delivery.

## 1. Intake

| Field | Value |
| --- | --- |
| Run ID | rr-20261026-sweep-01 |
| Repository | devkit (this repository), worktree of branch `dev-review-refactor` |
| HEAD | `573b675bc4598c959f0ed8cfea6cefaf79b50f44`; `packages/devkit-dist` unchanged since the Unit base `08f91ca7` (`git diff --stat 08f91ca7 HEAD -- packages/devkit-dist` empty) |
| Dirty paths | none (`git status --short` empty) |
| Prior reports | none |
| Destination | this file |
| Surfaces | `cli` (one batch) |
| Roots | the `devkit playbook` command group: `packages/devkit-dist/src/devkit_dist/features/distribution/cli/playbooks.py`, its help output, and the shared options it imports from `cli/output.py` |
| Selection | the Host's task scope stands in for the user's selection (spec §5 assumption); no scope addition |

## 2. Coverage

Read: `cli/playbooks.py` (99 lines, whole), `cli/output.py` lines 20-40, `adapters/cli.py` lines 45-112
(`WORKSPACE_HELP`, `workspace_option`, `resolve_root`), `features/project/repositories/project.py` lines 102-150
(`find_project_root`, `require_devkit_root`), `usecases/playbook_get.py` (whole); `uv run devkit playbook --help`,
`get --help`, `search --help`. No subagent was used for this small batch; the review ran in the playbook's agent.

Inventory: group `playbook` with `get PLAYBOOK_ID` (`-w`) and `search QUERY` (`-w`, `--limit`, `--min-score`,
`--min-similarity`, `--mode`, `--max-bytes`). No overlap: `get` is exact retrieval, `search` ranks headers.

Excluded: other distribution command groups (outside the roots); code and guidance surfaces (not selected).
Coverage gaps: none for the roots; no clone or dead-code tool was run (CLI surface, inventory by reading).

## 3. Findings

### RR-1: `-w/--workspace-root` help misstates the resolution order

- **Question**: CLI help: does the help describe actual behavior? Also grouping and naming: one concept, two wordings.
- **Location**: `packages/devkit-dist/src/devkit_dist/features/distribution/cli/output.py:26-28` (`WORKSPACE`, used
  by `playbook get` and `playbook search` and every distribution group module); canonical default
  `packages/devkit-dist/src/devkit_dist/adapters/cli.py:81` (`WORKSPACE_HELP`, used by 20 other commands).
- **Observed**: the help says "the nearest directory with .devkit/, else the Git top level, else the current one".
  `find_project_root` (`project.py:102-138`) returns the Git top level first inside a work tree (and raises
  `DEVKIT_ROOT_NESTED` for a nested `.devkit/`), and walks to the nearest `.devkit/` only outside Git; an explicit
  `-w` must itself be a devkit root (`require_devkit_root`).
- **Cost**: an agent that reads the help predicts the nearest `.devkit/` wins inside a repository and passes a nested
  directory, then meets `DEVKIT_ROOT_NESTED` or `ARGUMENT_INVALID`; the same option keeps two help texts accurate
  for one behavior (`rg -n "workspace_option\(" packages`: 1 custom wording in distribution, 1 in gate, 1 in
  worktree, 20+ default).
- **Evidence class**: semantic assessment of help text against code; the resolution code is deterministic.
- **Proposed disposition**: consolidate, behavior preserved: drop the distribution-specific wording and use the
  shared default, or correct the default so it states the Git-top-level-first order. Route: single-module test
  passes only if the edit stays in `cli/output.py` (one package-level module of one feature directory); a corrected
  shared default in `adapters/cli.py` is a second module, so the work item routes as an overall refactor. Edited
  paths: `cli/output.py` (and `adapters/cli.py` for the corrected default), plus the help assertions in
  `packages/devkit-dist/tests/` as following edits.
- **Decision**: pending (decision round not held).

## 4. Dropped and kept candidates

| Candidate | Outcome | Reason |
| --- | --- | --- |
| `playbook get` validates the ID in the adapter and again in `GetPlaybook.execute` | Dropped | No maintenance cost: the adapter call makes the argument error win over a workspace error before `resolve_root`; the use case call guards non-CLI callers (docstring `playbook_get.py:30`). |
| `get --help` names no way to find an ID | Dropped | No named cost: the group help states search and retrieval, and `SelectionError` names `devkit list`. |
| `--min-score`, `--min-similarity`, `--mode`, `--max-bytes` unneeded | Dropped | Each has a `[playbooks]` configuration twin and tests (`tests/integration/features/distribution/test_playbooks.py:77,291,400`); removing one is a contract change with no evidenced cost. |
| `_json_command` underscore name imported by six modules | Dropped | Code surface (not selected) and a rename without behavioral motivation (cosmetic churn). |
| Command function names `playbook_get` and `search` differ in style | Dropped | Cosmetic; no cost. |

## 5. Decision round (pending)

One finding is presented for the `cli` batch: RR-1 with disposition "consolidate, behavior preserved", the route
statement above and its edited paths. The run stops here with nothing applied; RR-1 is recorded as the follow-up
`FB-workspace-root-help-resolution-order` in this Unit's `feedback/`.

## 6. Report

- Outcome: `stopped at decision round`.
- Counts: found 1, applied 0, contract work items 0, deferred 0, kept 0, pending 1, dropped 5.
- Completion: the batch is not complete (one pending decision); no claim covers anything beyond the `devkit
  playbook` group.
- HEAD and dirty paths rechecked at the end: unchanged.
