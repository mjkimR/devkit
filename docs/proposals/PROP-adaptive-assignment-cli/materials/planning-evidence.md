# Planning evidence for the assignment commands

Evidence and comparisons behind the settled design in `PROP-adaptive-assignment-cli`. The two `scout` envelopes
(`envelopes/scout-01.yaml`, `envelopes/scout-02.yaml`) hold the findings; this file keeps the comparisons.

## 1. Evidence boundary

- Every claim below is a read of this worktree at `67750e0596f0`. Nothing was installed or built.
- No Git experiment ran. The one probe command of this turn, a throwaway repository under the proposal's ignored
  `.probe/` path, was denied by the host permission system and was not retried in another form. The Git plumbing
  below is therefore taken from code that already runs in this repository, not from a new measurement.
- `uv run devkit adaptive` in this worktree exits `2` with click's `No such command 'adaptive'` usage text and no
  advisory code (scout-02).

## 2. Git plumbing already used in the repository

| Need | Command in existing code | Location |
| --- | --- | --- |
| Committed changed paths | `git diff --no-renames --name-only -z <base> <head> --` | `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inspect.py:178-184` |
| Uncommitted and untracked paths | `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all`, reading the second record of a rename or copy entry | `inspect.py:125-142` |
| Ancestry | `git merge-base --is-ancestor <base> <head>`; exit `1` is "not an ancestor" | `packages/devkit-core/src/devkit_core/core/git.py:184-197` |
| Shared Git directory | `git rev-parse --path-format=absolute --git-common-dir` | `packages/devkit/src/devkit_agt/features/isolated_execution/repositories/runs.py:39`, `packages/devkit-dist/src/devkit_dist/features/project/repositories/invocation.py:34` |
| Worktree list | `git worktree list --porcelain -z` | `packages/devkit-spec/src/devkit_spec/features/scope/services/inventory.py:35-58` |

`--no-renames` makes a rename appear as one deleted and one added path, so both names are compared with the write
scope. `--untracked-files=all` lists each untracked file instead of its directory. Ignored files appear in neither
command.

The existing helpers differ on the base: `inspect.py` compares the two trees `<base> <head>`, the scope collector
compares from the merge base. With the ancestry check passing, both give the same paths, so the commands use the
two-tree form and run the ancestry check first.

## 3. Reuse by owning package

| Piece | Owner | Reachable without `devkit_agt` or `devkit_spec` |
| --- | --- | --- |
| `run_git`, `run_git_text`, `is_ancestor` | `devkit_core.core` | Yes |
| `file_lock` (`fcntl.flock`, bounded wait, `LOCK_HELD`) | `devkit_core.core` | Yes |
| `atomic_write_text`, `normalize_relpath`, `resolve_within` | `devkit_core.core` | Yes |
| Toplevel and common-directory lookup | `devkit_dist.features.project` public modules | Yes |
| `boundary`, `FORMAT_OPTION`, `echo_json`, `echo_notices`, `exit_on_warnings`, `field_value` | `devkit_dist.adapters.cli` | Yes |
| Changed-path collection, scope containment, head and ancestry checks of a worker | `devkit_spec.features.worker` | No: importing `devkit_spec` is excluded |
| Worktree list parser | private in `devkit_agt.features.worktree`, private in `devkit_spec.features.scope` | No public function in any package |
| Segment-aware `**` glob matcher `match_path` | `devkit_agt.features.rules.models.settings` (public) | Only with `devkit_agt` |
| Worktree lifecycle and isolated execution use cases | `devkit_agt.features.worktree`, `devkit_agt.features.isolated_execution` | Only with `devkit_agt`; the commands create no worktree and run no process |

What the commands need from Git is about five subprocess calls. Each is available through `devkit_core.core.run_git`.

## 4. Ledger location

| Option | Seen from every linked worktree | Tracked or shown by `git status` | Survives `git clean -fdx` | Host sandbox | Precedent |
| --- | --- | --- | --- | --- | --- |
| Tracked project file | No: each branch has its own copy until merged | Yes: every write dirties the Host checkout and enters the verification's own changed paths | Yes | Writable in the checkout | None for runtime state |
| `.devkit/transient/` of one checkout | No: the directory is per checkout and ignored; a lead in another worktree would need the main worktree resolved for it | No | No | Writable in that checkout only | Checkout-local state only (`CAP-DIST-workspace-ownership` §1, §2.8) |
| `<git common dir>/devkit/adaptive/` | Yes | No | Yes | Codex `workspace-write` treats shared Git as outside sandbox access and asks approval (`.devkit/managed/spec/subagents/planning-worker.md` step 5) | `devkit exec` runs (`<common>/devkit/executions`), the spec scope registry (`<common>/devkit-spec-scope`), the integration lock |

A tracked file also turns the ledger into a per-change record in history, which adaptive development excludes.

## 5. Ledger format

| Option | Partial write | History of transitions | Concurrency | Precedent |
| --- | --- | --- | --- | --- |
| One JSON document | Atomic replace of the whole board | Lost unless embedded | One lock; every write rewrites all assignments | None |
| One JSON file per assignment | Atomic replace per file | Lost unless embedded | Per-file writes, a lock for ID allocation and overlap checks | `devkit exec` run files |
| Append-only JSON Lines events | Only the last line can be torn; earlier events are never rewritten | Kept in order with timestamps | One lock around read, validate, append | The spec scope registry's `journal.jsonl` |

The overlap, narrowing and nesting checks read every open assignment before a write, so one lock around the whole
ledger is needed in each option. The event log adds the transition history that resume and a later hook consumer
read, at the cost of folding events into state on each read.

## 6. Write-scope semantics

| Option | Containment | Overlap of two scopes | Child within parent | Precedent |
| --- | --- | --- | --- | --- |
| Literal path prefix (a file, or a directory with its subtree) | Exact: equal, or under the entry plus `/` | Exact: one entry covers the other | Exact: a parent entry covers each child entry | `inspect.py:196-199`, `devkit_docs/utils/paths.py:28-39`; both reject glob characters |
| Globs with `*` and `**` | Exact with a segment-aware matcher | Needs a pattern-intersection decision, or a conservative literal-prefix comparison with false refusals | Same problem | `match_path`, owned by `devkit_agt` |

The bundle guidance names ownership as paths ("exclusive absolute ownership", "assigned product and test paths") and
uses no pattern. Literal prefixes keep the three decisions exact; adding globs later keeps every literal entry valid.

## 7. Base dependency of `devkit-adaptive`

| Answer | Allows | Forbids or costs |
| --- | --- | --- |
| `devkit-dist` only | Installing the bundle and the commands without the harness; the commands on `devkit_core` and `devkit_dist` helpers; guidance that names `devkit worktree` only as the project's documented procedure when a harness is installed | Importing `devkit_agt` worktree, workflow or rules modules; a small worktree-list parser and a prefix matcher are written in the feature |
| `devkit-agt` | Importing public `devkit_agt` modules (`match_path`, the hex-validating `is_ancestor`) and declaring edges to `devkit_agt.features.worktree` | Installing the harness wheel with every adaptive installation; the orchestration reference's "without assuming a harness is installed" no longer describes the package; the adaptive test suite depends on `devkit-agt` |

Neither answer needs `devkit_spec`, and `devkit-docs` already depends on `devkit_agt`, so both keep
`CAP-DLV-adaptive-development` rule 2. The commands use no worktree lifecycle, no isolated execution and no rule
engine, so nothing in this unit needs the second answer.

## 8. Contract statements that the commands touch

- `ADR-adaptive-development-and-research`: "No new runtime, CLI or distribution mechanism." and "Identifiers and
  commands use `adaptive-dev`."
- `CAP-DLV-adaptive-development` §2 Scope Excluded: "a runtime scheduler, agent bus, new wheel"; §4: "No
  adaptive-development runtime or CLI is added."; the final section: "No implicit Unit or verification ledger is
  created."; rule 18: "identifiers and commands MUST use `adaptive-dev`".
- `CAP-HARN-command-mount` §4.7: no `devkit spec` or `devkit docs` command reports a negative result. The statement
  names those two groups only; `ARCH-08-1-agent-output` §7 defines exit `1` for every command.
