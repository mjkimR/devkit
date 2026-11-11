---
id: CAP-COLL-work-scope-registry
title: Work Scope Comparison and Shared Registry
summary: "Scope observation through devkit spec scope collect compares creation snapshots with bounded host observation of branch and worktree evidence; release, sweep and the post-finish cleanup remove registry records. Partial coverage remains visible without worker publication or write authority."
area: collaboration
status: active
created_at: 2026-10-13
usecases:
  - UC-run-parallel-work-safely
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/scope/
  - packages/devkit-spec/src/devkit_spec/features/scope/cli/commands.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/cleanup.py
---

# [CAP-COLL-work-scope-registry] Work Scope Comparison and Shared Registry

## 1. Summary

`devkit spec scope collect` reports, for each pair of planned or running tasks, how many documents and code paths
they both touch and how much of their scope is still unknown. Creation keeps each task's initial scope in a registry
that every worktree of the repository shares without configuration; `release`, `sweep` and the post-finish cleanup
remove its records. The purpose is detection before parallel work runs: the overlap evidence is an input to the
orchestrator's decision of what runs in parallel and in which order work is integrated. It never grants or blocks a
write, and it is not exclusive ownership. Rationale: `ADR-collect-only-scope-observation`.

## 2. Scope & Boundary

- **In-Scope**: building scope sets from proposals, spec bundles and Git; pairwise comparison inside `collect`; the
  local file registry (records, owner tokens, locking, deadlines, sweep); the `collect`, `release` and hidden `sweep`
  commands; the creation registration of `devkit spec proposal handoff` and `devkit spec new`; the dual-mode
  `devkit.post_finish` extension (`devkit_spec.features.delivery.usecases.cleanup.after_finish`, classic callable and
  `ScopedCleanup`).
- **Out-of-Scope**:
  - The entrypoint path contract and `_Boundary` parsing: `CAP-TRACE-code-entrypoints`.
  - `[tool.spec.scope]` validation: `CAP-DLV-project-policy`. Document namespaces: `CAP-DOCS-namespaces` (independent
    of the registry namespace).
  - Creating and removing task worktrees: devkit's `devkit worktree`.
- **Non-Goals** (Scope Excluded): exclusive claims and write blocking; heartbeats, automatic expiry and distributed
  recovery; refreshing a record after creation; a registry event history; remote adapters; Windows locking; network file systems
  (where `flock` and rename are not reliable); attributing changes to more than one task in a worktree; semantic
  conflict detection; weighting or ranking pairs. Overlap evidence is a join of declarations and Git observations: it
  proves neither a merge conflict nor independence.

## 3. Business Rules & Policies

1. **Detection, never blocking**: no scope result MAY grant or refuse a write; `overlaps=` above 0 informs
   scheduling and integration order only.
2. **Unknown is not "no overlap"**: an input that cannot become a path, including a dirty path outside the path
   contract at creation, MUST be counted as unresolved with its reason, never dropped silently.
3. **Declarations are not merged**: when a bundle has both `reconcile.md` and `target-docs.md`, a path only one of
   them names is reported as a `DIFF`; the two lists are never merged.
4. **One token per worktree**: registration returns an opaque owner token once and stores only its SHA-256; a second
   registration from the same worktree MUST be refused (`SPEC_SCOPE_TOKEN_EXISTS`) so the first record is never
   orphaned. The token file is created exclusively: of two registrations racing in one worktree, the one that saves
   its token second is refused the same way, and its record is removed again. A record whose token cannot be saved
   is always removed again; when that removal fails, the original error is reported with the failure as a detail.
5. **Idempotent release**: `release` repeated, or run where nothing is registered, MUST succeed and change nothing.
6. **Atomic publication**: operations on an existing namespace hold its lock while reading, comparing or writing;
   shared readers exclude exclusive writers and never see a partial record. An absent namespace observation is empty
   and may precede a concurrent first registration.
7. **Cleanup after finish**: devkit-spec's `devkit.post_finish` extension (`devkit_spec.features.delivery.usecases.cleanup.after_finish`) implements both the classic callable contract for `devkit worktree finish` and `devkit_agt.features.integration.ScopedCleanup` (`integration_local_only = True`, `integration_plan`, `integration_validate`, `integration_run`) for `IntegrationService`. It runs in the
   base after the worktree finish succeeds and removes the records whose worktree is the finished one, at the
   revision it read (`sweep --apply` restricted to those tasks; or `release` for a `--no-worktree` base checkout task); other stale records stay for an explicit sweep. On the `ScopedCleanup` path, `integration_plan` binds each scope record as `CleanupTarget(kind="scope-record", identity=<task_id>, revision="<mode>:<namespace>:<revision>")` (`mode` in `worktree|base`) and `CleanupTarget(kind="proposal-prune", identity="docs/proposals/PROP-<slug>", revision=<source_sha>)`, `integration_validate` rejects any revision, namespace or mode drift (`INTEGRATION_REQUEST_STALE`) while permitting already-removed records once the Git part is done: the base HEAD contains the integration's result commit (`context.result_sha`; the source under `[worktree] merge = "ff-only"` or for a cleanup-only request, so later commits on the base are allowed) and the worktree is gone (`SPEC-integration-follow-ups`), and `integration_run` emits `SPEC_POST_FINISH_CLEANUP` notices (`CleanupResult(done=..., notices=...)`).
   Neither of its cleanups stops the other. A proposal prune that fails (a directory that cannot be listed or
   removed) is a `SPEC_PROPOSAL_CLEANUP_FAILED` warning whose fix is `devkit spec proposal prune <slug>`, and the
   record removal still runs. When the record removal fails (a malformed `[tool.spec]`, a registry timeout), its
   error (`SPEC_CONFIG_INVALID`, `SPEC_SCOPE_TIMEOUT`, ...) is returned beside the prune notices, devkit reports it as
   a warning with its own code, and its fix ends with `devkit spec scope sweep --apply` (or `devkit worktree finish <branch>` after a verified local landing). Nothing is released before
   the finish, so a refused finish leaves the task registered. Rationale: `ADR-worktrees-and-scope`, `SPEC-hook-driven-integration-cleanup`.
8. **Absolute shared path**: a configured `shared_path` MUST be absolute (a relative path would resolve to a
   different directory in each worktree).

## 4. Interfaces & Data Contracts

### 4.1 Scope Inputs

A scope set has a document side, a code side, observed paths and unresolved inputs. Both filesystem and pinned-tree declaration readers use the same target/boundary/entrypoint parser.
Every path is a literal workspace-relative path under the entrypoint path contract of `CAP-TRACE-code-entrypoints` (no glob, no absolute
path, no `..`, case-sensitive, `./` and a trailing `/` normalized), with its granularity in the working tree (`file`,
`dir`, or `unknown` when it does not exist), its source and its stage.

| Input | Side | Source | Stage |
| --- | --- | --- | --- |
| Proposal: `targets` of `docs/proposals/PROP-<slug>/target-docs.md` | document | `declared-doc` | `prop` |
| Spec bundle: `targets` of `reconcile.md` (not `waived`); without `reconcile.md`, those of `target-docs.md` | document | `declared-doc` | `spec` (`prop` for `target-docs.md`) |
| `entrypoints` of each capability or use case target (also under `docs/packages/<name>/`), while the bundle declares no code (below) | code | `candidate` | as its target |
| `tasks.md` `_Boundary` entries, including the exact path of another spec bundle's feedback file (below) | code | `declared-code` | `spec` |
| Git: the committed range (below, collect only), staged, unstaged, untracked | code | `observed` | `build` |

Candidates estimate a task's code before it declares any. When at least one `_Boundary` entry of a spec bundle's
`tasks.md` is a code path (`declared-code`), the bundle's code side is its declared code and it contributes no
`candidate` path, however broad its targets' `entrypoints` are. A proposal, and a spec bundle whose `tasks.md` is
missing, still the handoff skeleton, or names no code path (only `N/A`, placeholders, invalid paths, or paths under
`docs/` or `specs/`), keeps its targets' `entrypoints` as candidates. A capability or use case target without
`entrypoints` is unresolved (`no-entrypoints`) in both cases. A stored record keeps the rule that applied at creation;
collect reads live declarations with the rule that applies now.

A `_Boundary` entry under `specs/` is `excluded-tree`, except the exact path of a feedback file of another spec bundle
(`specs/**/feedback/<name>.md`, outside the declaring bundle's directory and not a directory of the working tree): it
is collected as `declared-code` of granularity `file` (`unknown` while planned), so two units that resolve the same
feedback file overlap on it. Such a path does not count as declared code for the rule above: it never replaces the
candidates. Globs stay `invalid-path`, and directories, other files of another bundle and the declaring bundle's own
feedback stay `excluded-tree`. Entrypoint derivation still skips every `specs/` path (`CAP-TRACE-code-entrypoints`).

`targets` is the same list in both files: `- file: <workspace-relative path>` with an optional `resolution`
(`devkit spec proposal new --with-target-docs` scaffolds `targets: []`). Document IDs are not accepted. Observed paths
are relative to the workspace root and limited to it; a changed path outside the path contract (a glob character or
a colon in its name) is unresolved (`invalid-path`, source `observed`). Renames are not detected: a moved file is
observed at its old and its new path, so a task that moves a file overlaps a task editing it at its old path.

Creation registration stores the bundle's declarations, its unresolved inputs, the base anchors and the worktree's
staged, unstaged and untracked paths at creation (the uncommitted handoff output and any other dirty file), read
through collect's observation service (`devkit_spec.features.scope.services.observation`) under the
`[tool.spec.scope] timeout`. Its committed range is empty by construction, since it starts at the registration HEAD,
so creation reads none; a record keeps this creation-time scope until it is removed.

Collect computes a source's committed range from the fork point, the unique `git merge-base <base> <tip>`: what a
task merges or rebases in from its base branch is not observed, while its own changes, including conflict
resolutions, are. For a registered observation the record caps the range: its base ref is the branch the base checkout
was on when the task registered (devkit records no branch a worktree forked from, so it is a guess, and the base
checkout may be on another branch than the one the worktree was created from), and its base revision is HEAD at
creation. The range is therefore never wider than `<base revision>..<tip>`, so another branch's commits are never
observed:

- the base revision is the fork point or its ancestor: the range is `<fork point>..<tip>`;
- the fork point is an ancestor of the base revision (it predates the base revision): the range is
  `<base revision>..<tip>`;
- neither is the other's ancestor (the task registered after committing, so its base revision is a commit of its own,
  and later merged its base branch in): the committed paths are those changed in both `<fork point>..<tip>` and
  `<base revision>..<tip>`, so the paths merged in from the base branch drop out.

In the base checkout itself, on the base branch, or when the base checkout is detached, the record has no base ref.
A base without a unique fork point (it does not resolve, shares no history with the tip, or a shallow clone does not
reach it) leaves the committed layer unresolved (`unknown-base`, 4.9) until the base is fixed or the clone deepened
(`git fetch --unshallow`).

| Unresolved reason | Input |
| --- | --- |
| `planned-doc` | A document target that does not exist yet (it still counts as a document, so two tasks planning the same file overlap). |
| `no-entrypoints` | A capability or use case target without `entrypoints`. |
| `not-a-path`, `invalid-path`, `excluded-tree` | A `_Boundary` entry that is `N/A`/`none`, not a literal path, or under `docs/` or `specs/` (except another bundle's feedback file, 4.1). |
| `invalid-path` | A document target that is not a literal path, or a changed path outside the path contract (source `observed`). |
| `waived` | A `reconcile.md` target with `resolution: waived`. |
| `no-targets` | A `target-docs.md` without a `targets` key. |
| `missing-target-docs`, `missing-reconcile`, `missing-tasks` | The input file does not exist. |
| `unknown-base` | Collect found no unique fork point between the selected base and the source's tip (4.9). |
| `missing-base-revision`, `unknown-base-revision`, `missing-base-ref` | Only on records written before creation stopped reading a committed range; collect reads them like any other unresolved input. |

### 4.2 Comparison

Collect compares each pair of observations (4.9). Two sets overlap on a **document** when both declare the same document path, and on **code** when a declared,
candidate or observed path of one equals or contains (by whole segments) one of the other's. A spec bundle that
declares code is compared by its declared and observed code only (4.1), so a path that only its targets'
`entrypoints` name is no overlap. A pair reports both counts, each overlapping path with its granularity and the
sources of both sides, and the unresolved count of both sides. Ranking and weighting are the consumer's.

### 4.3 Registry

- **Location**: the default shared path is `devkit-spec-scope/` in the Git common directory
  (`git rev-parse --git-common-dir`), and the default namespace is the first 16 hex digits of the SHA-256 of that
  directory's absolute path: every worktree of one repository shares them, and cleaning caches never touches them.
  `[tool.spec.scope]` overrides both; to share a registry between clones or hosts, give each the same absolute
  `shared_path` and the same `namespace`. Package documents contribute their workspace-relative targets and
  entrypoints like any other.
- **Record**: `<shared>/<namespace>/<task-id>.json` (the task ID mapped to a file-name-safe form), schema version 1:
  `namespace`, `task_id`, `token_hash`, `revision` (1 at creation), `base_revision` (HEAD at creation), `base_ref`
  (the base checkout's branch at creation, `refs/heads/<name>`; empty when there is none, 4.1), `worktree` (the
  absolute workspace root), `hostname`, `shared_worktree`, `spec` (workspace-relative), `scopes` (`path`, `kind`,
  `source`, `stage`, `first_seen`), `unresolved`, `updated_at`, and the legacy keys `last_request_id`, `last_added`
  and `last_removed`: creation writes them empty and zero, a record written by the retired update may carry other
  values (and a `revision` above 1), and every reader accepts and ignores them.
- **Token**: saved in the worktree's own Git directory as `devkit-spec-scope-token` (mode 0600), never in the working
  tree or the registry, and always created exclusively. It is written to a temporary file
  (`.devkit-spec-scope-token-<random>`) and hard-linked into place, so it is never read half-written; on a file
  system without hard links the token file is created exclusively and written in place, and a file that does not end
  with the token's newline (a save in progress or interrupted) counts as no token: `release` removes it. A temporary
  file a crash left behind is removed by the next mutating token load/save once it is older than a minute.
  Collection never reads a token.
- **Atomicity**: mutations hold exclusive `flock` on `<shared>/<namespace>/.lock` (devkit's `file_lock`; the lock file is created
  with mode 0600, so the processes sharing a namespace run as one user, and a symbolic link or anything but a
  regular file there is `SPEC_SCOPE_SHARED_PATH_UNAVAILABLE`);
  a record (mode 0644) is published with devkit's `atomic_write_text`: a `.<record>.devkit-*.tmp` file in the same
  directory, synced and renamed over the record. Temp files an interrupted publish left behind are removed at the
  next mutating lock acquisition, and the OS releases the lock of a process that died.
  Registry reads open the existing regular, non-symlink lock read-only and hold shared `flock` across all record
  enumeration and reads. Opening a nonregular lock, including a FIFO, never blocks before rejection. Never unlink or
  replace the lock while the namespace is in use.
- **Read access**: the registry reads of `collect` (4.9) and of `release`, `sweep` and the post-finish cleanup before
  they write MUST NOT create directories or locks, open files for writing, or clean record/token temporary files.
  Only actual namespace ENOENT returns empty without creation. An existing namespace without its lock is
  `SPEC_SCOPE_SHARED_PATH_UNAVAILABLE`; permission, unsafe-path and other namespace IO failures are errors, never
  evidence of empty state. Per-record invalid-data warnings remain visible. Neither empty nor partially readable
  results certify that active work has no overlap.
- **Initialization and repair**: authorized registration from a worktree without a token can initialize a missing
  lock. Release and sweep may query first and are not missing-lock recovery. Otherwise an operator repairs a missing
  lock after writers are quiescent, without deleting records/tokens or replacing an existing lock.
- **Permissions**: readable initialized state can be read without write access when the host permits read-open
  flock. Mutations still need namespace writes (lock, records, temporaries) and, when applicable, worktree
  Git-directory token writes and cleanup. Hosts grant required access explicitly; refusal stops that operation.
  Successful reads grant no mutation authority. Storage, configured absolute shared paths, namespaces and token
  locations remain unchanged; there is no relocation or transport fallback. The access separation follows
  `ADR-worktrees-and-scope`.
- **Operations** (`devkit_spec.features.scope.Registry`; the local file adapter `LocalRegistry` is the only implementation):
  - `register` (creation registration only): creates the record at revision 1; an existing task ID in the namespace
    is `SPEC_SCOPE_TASK_EXISTS`. A second record for the same worktree and host marks both `shared_worktree` (a
    `SPEC_SCOPE_SHARED_WORKTREE` notice).
  - `query`: every readable record, for `release`, `sweep` and the post-finish cleanup; unreadable files are
    reported, never read as records. `record_file` names the file of a task's record and `may_hold` tells whether an
    unreadable file may be a token's record (it may unless its bytes can be read and lack the token's hash), so
    commands refuse only for the unreadable files that may be the record they look for.
  - `release`: deletes the record when the token owns it; a missing record is a no-op. A record left alone in the
    worktree the released one shared loses its `shared_worktree` flag, unless an unreadable record file may name that
    worktree too.
  - `sweep`: classifies each record: `active`; `stale` (`worktree-missing`: same host, and the worktree path is gone
    or no longer a Git work tree); `unverifiable` (`other-host`); `error` (`parse`, `permission`). With `--apply` a
    stale record is removed (`removed`, `worktree-missing`) only if its revision still equals the one read before,
    else `error` with `stale-revision`.
- **Deadline**: creation registration, `release` and `sweep` run under `[tool.spec.scope] timeout` (default 10
  seconds), one devkit `Deadline` whose expiry raises `SPEC_SCOPE_TIMEOUT`: the shared/exclusive lock wait and every
  Git subprocess take the time left, and a Git process that outlives it is killed. Collect has its own budgets (4.9).
- **No event history**: the registry appends no event log. A `journal.jsonl` an earlier version left in a namespace is
  neither read, written nor removed.

### 4.4 Commands

Every command takes `-w/--workspace-root`, `--format text|json`, `-q`, `-v` and `--strict`; text output is one
sentinel per line, warnings follow on stderr, and JSON is one object with the same data and its `notices`.

| Command | Does |
| --- | --- |
| `devkit spec scope collect [--base <ref>] [--fetch <remote>]... [--timeout <seconds>] [--source-timeout <seconds>]` | Observes registry snapshots, `plan-*`/`dev-*` refs and accessible worktrees and compares them pairwise; repeat `--fetch` for configured remotes. See 4.9. |
| `devkit spec scope release [--task-id <id>]` | Removes this worktree's record and token. Without a token it succeeds and changes nothing, with or without `--task-id`; with `--task-id`, the token must own that record. A token whose record is already gone is removed, unless an unreadable record file may hold that record. |
| `devkit spec scope sweep [--apply] [--expect <task>=<rev>]...` (hidden) | Reports stale, unverifiable and unreadable records; `--apply` removes stale ones whose revision is unchanged (without `--expect`, the revisions this command read first). |

The scope group has no `register`, `query`, `compare` or `update` subcommand and `collect` has no `--mode` option:
Click refuses each as a usage error (exit 2; `ADR-collect-only-scope-observation`).

Argument errors (`ARGUMENT_INVALID`): `--expect` without `--apply`, an `--expect` that is not
`<task-id>=<revision>`, and the `collect` budgets and remotes of 4.9.

### 4.5 Output

```text
[SCOPE: SPEC-a namespace=3f2a... revision=1 scopes=6 unresolved=2 shared_path=.git/devkit-spec-scope token=...]  # creation
[SCOPE_RELEASE: SPEC-a released=yes registered=yes already=no revision=1]                # release
[SWEEP: SPEC-b verdict=stale reason=worktree-missing revision=1]                         # sweep
[SUMMARY: namespace=3f2a... active=1 stale=1 unverifiable=0 error=0 removed=0]           # sweep
```

- `collect` renders the lines of 4.9; its `[PAIR]` lines are followed by their `[EVIDENCE: <path> ...]` lines (the
  path positional).
- Paths are relative to the workspace root: `shared_path=` and the `[TARGET]` of registry advisories.
- `[SCOPE: <task> ...]` is only a creation registration (`devkit spec proposal handoff`, `devkit spec new`); `release`
  prints `[SCOPE_RELEASE: ...]` and `spec worker inspect` `[SCOPE_ENTRY: <path> ...]`.
- Successful creation registration may print the owner token once; collection never exposes an owner token or its
  hash.
- `sweep` verdicts are `active`, `stale`, `unverifiable`, `error` and `removed`. `sweep --apply` that kept a record
  because its revision moved prints its verdicts, then `SPEC_SCOPE_STALE_REVISION`.

JSON shapes: creation's `scope` object `{task, namespace, revision, spec, scopes, unresolved, shared_path, token}` (no
record internals or timestamps); `release` `{task, released, registered, already, revision, notices}`; `sweep`
`{results, summary, notices[, errors]}`; `collect` as in 4.9.

### 4.6 Creation and Host responsibilities

`devkit spec proposal handoff` (both forms) and `devkit spec new` register initial scope after successful creation
in an eligible linked worktree. Base and standalone checkouts register nothing automatically. Skeleton declarations
remain unresolved. Automatic registration is best effort: failures and registration notices produce no default advisory,
error/notice/status field or worker recovery task, and preserve primary output, exit code and `--strict` behavior.
Primary-operation errors/notices remain unchanged. Verbose-only INFO diagnostics identify automatic collection
failures (`SPEC_SCOPE_TOKEN_EXISTS`, `SPEC_SCOPE_TASK_EXISTS`, `SPEC_SCOPE_SHARED_WORKTREE` and any other cause),
and logging failures cannot fail creation. Cancellation/termination propagate normally. No retry, storage fallback
or permission escalation is performed.

Workers have no scope registration, update or ACK duty, and nothing refreshes a record after creation. Explicit and
internal `workflow next`, readiness and worker inspection do not collect or publish scope. The Host requests explicit
observation with `collect` when evidence is needed for scheduling. Post-finish cleanup retains rule 7. Queued Backlog
drafts and drafts accepted with `--direct` on the base have no observation until they have a `plan-*` or `dev-*`
source.

Rationale: `ADR-worktrees-and-scope`, `ADR-collect-only-scope-observation`.

### 4.7 Configuration

```toml
[tool.spec.scope]
shared_path = "/srv/devkit-scope"   # absolute, or starting with ~; default: devkit-spec-scope/ in the Git common dir
namespace = "team"                  # letters, digits, '.', '_', '-', not starting with '.'; default: the common-dir hash
timeout = 10                        # whole seconds per command, 1 to 300
```

A malformed table is `SPEC_CONFIG_INVALID` (`CAP-DLV-project-policy`).

### 4.8 Codes

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `SPEC_SCOPE_NOT_A_WORKTREE` | `ERROR` (`INPUT_ERROR`) | `ScopeNotAWorktreeError` | The workspace is not inside a Git work tree. |
| `SPEC_SCOPE_SPEC_NOT_FOUND` | `ERROR` (`INPUT_ERROR`) | `ScopeSpecNotFoundError` | The bundle a creation registration names is not a directory (verbose diagnostic of creation registration). |
| `SPEC_SCOPE_INPUT_INVALID` | `ERROR` (`INPUT_ERROR`) | `ScopeInputInvalidError` | `tasks.md`, `reconcile.md` or `target-docs.md` cannot be read, or its `targets` is not a list of mappings with a string `file`. |
| `SPEC_SCOPE_TOKEN_EXISTS` | `ERROR` (`INPUT_ERROR`) | `ScopeTokenExistsError` | This worktree already registered a task, or a concurrent registration in it saved its token first (verbose diagnostic of creation registration). |
| `SPEC_SCOPE_TASK_EXISTS` | `ERROR` (`INPUT_ERROR`) | `ScopeTaskExistsError` | Another record has the task ID (verbose diagnostic of creation registration). |
| `SPEC_SCOPE_TOKEN_MISMATCH` | `ERROR` (`BLOCKED`) | `ScopeTokenMismatchError` | `release --task-id` names a record this worktree's token does not own. |
| `SPEC_SCOPE_STALE_REVISION` | `ERROR` (`AUTO`) | `ScopeStaleRevisionError` | `sweep --apply` kept a stale record whose revision changed since it was read; nothing was removed for it. |
| `SPEC_SCOPE_TIMEOUT` | `ERROR` (`DEFER`) | `ScopeTimeoutError` | The lock or Git outlasted `timeout` (creation registration, `release`, `sweep`). |
| `SPEC_SCOPE_LOCK_UNSUPPORTED` | `ERROR` (`BLOCKED`) | `ScopeLockUnsupportedError` | No `fcntl.flock` on this platform. |
| `SPEC_SCOPE_NAMESPACE_INVALID` | `ERROR` (`INPUT_ERROR`) | `ScopeNamespaceError` | An adapter call names an empty, dotted or nested namespace. |
| `SPEC_SCOPE_SHARED_PATH_UNAVAILABLE` | `ERROR` (`INTERACTION`) | `ScopeSharedPathError` | The registry directory (or the token file) cannot be created, read or written, or its `.lock` is not a regular file. |
| `SPEC_SCOPE_RECORD_INVALID` | `WARNING` | `ScopeRecordInvalidWarning` | A record file cannot be read and was left out. An `ERROR` (`INTERACTION`, the token kept until the files are repaired or removed) only when the record a command needs may be unreadable: `release` without `--task-id` (and the post-finish cleanup of a base checkout task) when this worktree's record is not readable and an unreadable file may hold its token's hash; `release --task-id <id>` when that task's own record file cannot be read. |
| `SPEC_SCOPE_SHARED_WORKTREE` | `WARNING` | `ScopeSharedWorktreeWarning` | Another task registered the same worktree (verbose diagnostic of creation registration). |
| `SPEC_SCOPE_COLLECTION_PARTIAL` | `WARNING` | `ScopeCollectionPartialWarning` | Some requested source, input or comparison coverage is missing. |
| `SPEC_SCOPE_COLLECTION_FAILED` | `ERROR` (`INPUT_ERROR`; `MAINTENANCE` for the report limit) | `ScopeCollectionFailedError` | Neither the ref nor the worktree inventory can be read (`[TARGET]` names the failed sources, `[DETAIL]` each reason), or report metadata cannot fit the bounded result. |
| `SPEC_POST_FINISH_CLEANUP` | `NOTICE` | `PostFinishCleanupNotice` | `ScopedCleanup.integration_run` removed an empty proposal directory or a finished worktree's scope record during approval-bound local integration. |

devkit's own errors pass through: `ARGUMENT_INVALID` (4.4), `GIT_FAILED`, `SPEC_CONFIG_INVALID`.


### 4.9 Explicit Host observation

`devkit spec scope collect` returns invocation-local evidence and does not read owner tokens or mutate records,
revisions or temporary files. It inventories existing registry records with shared read locking.
Missing registry storage is empty evidence; unreadable storage is a coverage gap while available Git evidence
remains usable. This is independent of registry participation and creates no persistent observation cache.

Every run observes the same sources: the existing creation records (snapshots), every local and configured
remote-tracking `plan-*`/`dev-*` ref at its pinned commit, and every accessible main or linked worktree's
declarations and committed, staged, unstaged and untracked paths. No option selects fewer. Network refresh is
separate: repeatable `--fetch <remote>` accepts only configured remotes and updates only their remote-tracking branch
namespace, without tags, pruning, submodules, interactive prompts, pushes or automatic deepening. Without fetch, refs
are locally cached evidence. Successful fetch times are in `coverage.layers.fetch`; previous cache freshness is
unknown. No observation reads another PC's private/unpushed changes. Separate clones do not share registry snapshots
by default. PRs with pushed declarations/changes are recommended for frequent multi-PC work. A cloud-backed registry
repository for initial snapshot sharing is a future direction under ADR-host-owned-scope-observation, not a deployed
backend or distributed watcher.

Each candidate exposes `activity=active-candidate|inactive|unknown`, identity evidence and a reason. Physical worktree
access and lifecycle evidence are distinct. Terminal clean units are excluded from comparison; terminal dirty
worktrees and ambiguous bindings remain visible. Clean non-activity checkouts without a task binding are excluded
as `clean-unbound`. An accessible worktree must belong to this repository's worktree inventory and common directory;
another-host record path is never opened merely because the same path exists here.

Declarations, targets, entrypoints and path kinds come from one filesystem or pinned tree source. Valid local unit
markers take precedence over exact activity-slug discovery; stale/mismatched markers stay unresolved. Task keys
combine namespace, anchor ID and unit path. Registry `task_id` is a separate registration alias; snapshot-only
observations have unknown canonical identity until a unique live anchor confirms the namespace/unit binding.
The registration alias remains in provenance, and a confirmed custom alias retains its historical range cap.
Duplicate anchor IDs at distinct unit paths have unknown attribution.
Worktree HEAD/status and fingerprints for declaration files read are checked before/after observation; detected
changes produce partial coverage without retries. This cannot detect every change-and-revert or provide a single
atomic snapshot across worktrees.

Base selection uses explicit `--base` (the override for candidates without a base marker, such as remote-tracking
refs when `<remote>/HEAD` and the main checkout branch differ), a validated local `devkitBase`, a confirmed record
base, then a uniquely resolvable integration hint. Hints use remote symbolic HEAD or the non-activity main checkout branch and expose
ambiguity. A selected base whose commit equals the tip is still a base: its committed range is empty (or the
registration cap's, 4.1) and the layer is observed. The base is discarded, and the layer stays `unknown-base`, only
when `git rev-parse --symbolic-full-name <base>` (in the source's checkout, so `HEAD` names its branch) resolves to
the candidate's own full ref or to a tracking peer of the same task (`refs/heads/<branch>` or
`refs/remotes/<remote>/<branch>` for a configured remote, where `<branch>` is the candidate's inventoried branch
name: the whole name under `refs/heads/` for a worktree, the last segment for a ref, since `plan-*`/`dev-*` names hold
no slash); a base that resolves to no ref is kept as a commit. A tracking peer of the same task is therefore never its integration base.
Confirmed registered observations retain the registration-HEAD cap/intersection from 4.1; unregistered observations
use a unique merge-base-to-tip diff, labelled `branch-relative` because stacked parent work can be included. Missing history/base evidence leaves that
layer unresolved. Available declaration/dirty evidence remains usable.

Each observation has its own ID, task key, scope, aliases, provenance and observed/missing layers. Commit, selected
base, historical cap, range method and effective declaration evidence must agree before deduplication. Divergent
or ancestor refs retain separate observations and provenance relations. Dirty worktrees remain distinct. Unreadable
live declarations can fall back to pinned declarations, explicitly marked as fallback. Historical snapshots remain
separate; a successful current observation or verified terminal-clean lifecycle disables their obsolete evidence
for comparison unless dirty/unknown live evidence contradicts that lifecycle. Pairs name observation
IDs and skip only confirmed same-task observations. Counts are observation-pair counts, never a proof of independence.

Every path of an observation has a horizon. A Planning activity is an observation whose `provenance.unit` is a
proposal unit and whose source is a `plan-*` ref or worktree (the last segment of `provenance.ref`); its `observed`
paths (committed, staged, unstaged, untracked) are `current` and its `declared-doc`, `declared-code` and `candidate`
paths are `future`. Every path of any other observation is `current`: a proposal on a `dev-*` source (a handoff
before its first commit), a spec unit, a snapshot and an observation without a unit. The unit kind comes from
`provenance.unit`, never from `task_key`. An evidence entry is `current` when both sides are `current`, otherwise
`future`. Code evidence keeps one entry per path pair, taking a `current` source when a side holds the path as both,
so a current overlap is never hidden behind a future one. Each evidence entry carries `horizon`, each pair `current`
and `future` entry counts (`current + future = len(docs) + len(code)`), and `summary.current_overlapping` counts
the pairs with at least one `current` entry. The horizon only labels evidence: every overlap stays listed and counted
in `docs`, `code` and `overlapping` (4.2), and neither horizon grants or refuses a write. The Host reads it for
scheduling (`CAP-HARN-agent-guidance`): `current` overlap serializes running activities, `future`-only overlap does
not serialize Planning runs but orders handoff and integration, and partial coverage never proves independence.

JSON is one object with `started_at`, `finished_at`, `coverage`, `inventory`, `observations`, `pairs`, `summary`
and `notices`. Coverage carries source/fetch outcomes, bounded problem examples and total count, discovered/retained
source counts, `comparisons_complete`, total/completed pair counts and the last completed pair key. Each problem
is `{source_id, reason, inputs}`: `inputs` lists the sorted distinct reasons of the source's unresolved inputs
(4.1), whatever the problem's own reason (`unresolved-input` or `unknown-base`), and is empty for a gap with no
unresolved input; a repeated source and reason merges its inputs into one problem. Lifecycle-normal inputs
(`missing-target-docs`, `missing-reconcile`) still count as gaps. Complete means
requested observable layers for discovered candidates, not global/private visibility. Missing inputs, unknown bases,
ambiguous identity, inaccessible/unstable sources and exhausted budgets produce `SPEC_SCOPE_COLLECTION_PARTIAL`.
Usable results exit 0, warning-bearing results exit 1 only under `--strict`, and inability to read both the ref and
the worktree inventory raises `SPEC_SCOPE_COLLECTION_FAILED` with exit 2. Invalid budgets and an unconfigured
`--fetch` remote are `ARGUMENT_INVALID`.

Text renders `[SCOPE_CANDIDATE: source= activity= reason=]`, `[SCOPE_OBSERVATION: id= task=<id>|- unit=<dir>|-
source= sha= missing=]`, `[PAIR: ... unresolved= current= future=]`, `[EVIDENCE: <path> ... horizon=current|future]`
and a `[SUMMARY: ... overlapping= current_overlapping= coverage=complete|partial comparisons_complete=yes|no]`. A worktree source is named `worktree:<path relative to the
workspace>` (`worktree:.` is this checkout). The base checkout (the main worktree off any activity branch) is an
inactive `base-checkout` candidate, never a coverage gap, dirty or not. `SPEC_SCOPE_COLLECTION_PARTIAL` lists each
source and reason once in `[DETAIL]`, with its inputs in parentheses when it has any
(`refs/heads/dev-x: unresolved-input (excluded-tree, missing-reconcile)`), the sources in `[TARGET]`. It emits no worker ACK. The CLI uses the existing advisory
boundary for errors, notices and strict behavior.

Total `--timeout` defaults to 30 seconds and `--source-timeout` to 5 seconds, each an integer 1–300. A source receives
at most the total computation time remaining; fetch shares that budget. Computation reserves finalization time,
checks comparison loops and bounds Git output while reading. Slow stdout consumers are outside computation timing.
Limits are 1 MiB per declaration, 16 MiB total declaration bytes, 256 retained source candidates, 10,000 complete
pairs, 10,000 evidence entries and an 8 MiB encoded report including framing/notices. Retention conservatively covers JSON and text, including
repeated observation IDs on evidence lines. Limits preserve complete
entries and bounded coverage/summary diagnostics; `input-limit` and `result-limit` report omitted work. Timeouts use
`source-timeout`; other reasons include `unknown-base`, `identity-ambiguous`, `fetch-failed`, `source-unreadable`,
`unresolved-input` and `observation-changed`. Uncomputed pairs never count as zero overlap. The
`SPEC_SCOPE_COLLECTION_PARTIAL` fix offers larger budgets for `source-timeout` only; a `result-limit` is reported.

Checks: `packages/devkit-spec/tests/integration/features/scope/test_collection.py`,
`packages/devkit-spec/tests/integration/features/scope/test_collection_horizon.py`,
`packages/devkit-spec/tests/integration/features/scope/test_observation.py` (the committed-range cases of 4.1),
`packages/devkit-spec/tests/integration/features/scope/test_flow.py` and creation tests under
`packages/devkit-spec/tests/integration/features/delivery/`; the 4.8 table is checked against the defined codes in
both directions by `packages/devkit-spec/tests/integration/package/test_documented_codes.py`.
