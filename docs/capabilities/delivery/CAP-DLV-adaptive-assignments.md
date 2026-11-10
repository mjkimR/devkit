---
id: CAP-DLV-adaptive-assignments
title: Adaptive assignment ledger and return verification
summary: "Commands record delegated assignments in a shared Git ledger and verify returned work against literal scope, commit authority and reported checks, without dispatching agents or running checks."
status: active
area: delivery
usecases: [UC-advance-an-idea]
entrypoints:
  - packages/devkit-adaptive/src/devkit_adaptive/features/assignment/cli/commands.py
---

# [CAP-DLV-adaptive-assignments] Adaptive assignments

## 1. Purpose

The delegating agent records assignment authority before dispatch and verifies each return against repository facts.
`ADR-adaptive-assignment-commands`, `ADR-adaptive-assignment-ledger-storage` and
`ADR-adaptive-requires-document-system` record the command, storage and dependency decisions.

## 2. Scope

In scope: recording, returning, verifying, closing, listing and showing assignments, and resolving governing documents.
**Scope Excluded**: starting agents, running declared checks, creating worktrees, blocking sessions, pruning,
MCP, glob scopes and migrations; the Host owns dispatch, integration and judgment of product correctness.

## 3. Business Rules

1. **Shared ledger**: Every mutation MUST append one schema-1 event under the shared Git directory while holding the exclusive 10-second lock. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
2. **Fragment recovery**: IF a ledger ends without a newline, THEN readers MUST ignore the fragment with `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` and the next writer MUST truncate it under lock before appending. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
3. **Literal scope**: The feature MUST compare normalized literal path prefixes, with `.` covering the worktree and each other entry covering itself and its subtree. Test: `packages/devkit-adaptive/tests/unit/features/assignment/test_values.py`.
4. **Overlap**: IF a new write scope overlaps another assignment that is not closed, THEN `new` MUST refuse with `ADAPTIVE_SCOPE_OVERLAP`, except for its parent or explicitly named dependencies. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
5. **Narrowed children**: WHEN recording a child, the feature MUST require scope and commit authority inside its parent's and at most Host → lead → child depth. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
6. **Governing constraints**: WHEN recording an assignment, the feature MUST resolve governing IDs in its worktree and refuse all unresolved values together with `ADAPTIVE_GOVERNING_UNRESOLVED`. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_governing.py`.
7. **Returned work**: `verify` MUST recompute the seven checks of the interface contract and record verified only when none fail or remain not-run. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
8. **Changed paths**: Verification MUST include committed paths without rename detection and uncommitted/untracked status paths minus dirty-at-assignment paths. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
9. **Closing**: WHEN integrated closing lacks a passed verification, the command MUST require a reason and return `ADAPTIVE_CLOSED_UNVERIFIED`; outstanding children prevent closing. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
10. **Resume observations**: `list` MUST report repository facts and no agent liveness claim, including missing worktrees, commit counts and attention fields. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
11. **Repository preservation**: Assignment commands MUST leave tracked files and every worktree's Git status unchanged. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
12. **Approach independence**: Commands MUST require neither an approach value, bundle selection nor a `.devkit/` directory. Test: `packages/devkit-adaptive/tests/integration/features/assignment/test_commands.py`.
13. **Independent installation**: The distribution MUST install the command and document system without devkit-spec. Test: `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`.

## 4. Interfaces and Limits

### Commands

The group is `devkit adaptive assignment`, mounted by the entry point `adaptive = "devkit_adaptive.cli:cli"` in the
`devkit.commands` group of `devkit-adaptive` (`ARCH-05-3-command-plugins`). Every command:

- takes `--format text|json` and the standard `-q`, `-v`, `--strict` and `--workspace-root` options from
  `devkit_dist.adapters.cli`, and resolves the workspace root with its `resolve_root`;
- resolves the repository as the Git work tree containing that root and works from any worktree of it; a root that
  is in no work tree, the bare directory of a repository included, is `ADAPTIVE_REPOSITORY_UNSUPPORTED`;
- performs no approach check and needs no bundle selection and no `.devkit/` directory.

IDs match `^[a-z0-9][a-z0-9-]{0,39}$`. Revisions are stored as full commit IDs, resolved with
`git rev-parse --verify --quiet <rev>^{commit}`. Timestamps are UTC, ISO 8601 with seconds and a `Z` suffix. Paths
are compared after symlink resolution.

**`new`** records an assignment with status `open`.

```text
devkit adaptive assignment new --owner <text> --goal <text>
    [--id <id>] [--role <text>] [--worktree <path>] [--base <rev>]
    [--write <path>]... [--commit] [--check <name>[=<command>]]...
    [--governing <id-or-path>]... [--depends-on <id>]... [--parent <id>]
    [--evidence <text>] [--handoff <text>] [--stop <text>]
```

- `--id` defaults to `a<N>`, the first unused `N` counting from the number of recorded assignments plus one.
- `--worktree` defaults to the worktree containing the workspace root. It must be a worktree of the same repository
  whose directory exists: a path that `git worktree list --porcelain -z` does not list, lists as `bare` or lists
  with `prunable` is `ADAPTIVE_WORKTREE_UNAVAILABLE`.
- `--base` defaults to the HEAD of that worktree and must resolve to a commit; a repository without a commit gives
  `ADAPTIVE_REVISION_UNRESOLVED`. The base is the commit the assignee starts from, so record an assignment when it
  is dispatched: a dependent assignment after its dependency's result is in its worktree.
- `--write` is repeatable and takes a path relative to the worktree root, or an absolute path under it. No `--write`
  records a read-only assignment.
- `--commit` records that the assignee may commit. Without it the assignee must leave HEAD at the base.
- `--check` declares a check by name; the optional command text is recorded and never run.
- `--governing` is repeatable and names a document the assignee treats as a constraint. Each value is validated in
  the assignment's worktree before anything is appended:
  - The single value `none` records an empty list. `none` beside another value is `ARGUMENT_INVALID`. Omitting the
    option records an empty list as well.
  - A value that matches the document ID grammar (`is_id` of `devkit_docs`) is resolved through the document index
    of the worktree (`DocumentIndex.load(<worktree root>).resolve(<value>)`). The document's own ID is recorded,
    also when the value was an alias.
  - Any other value is a path. A relative path is relative to the worktree root and must exist inside it; an
    absolute path must exist. A path under the worktree root is recorded relative and normalized, any other path
    absolute.
  - Every value that fails is collected into one `ADAPTIVE_GOVERNING_UNRESOLVED` with a `[DETAIL]` per value and its
    reason: `unknown-id`, `duplicate-id` or `missing-path`. Its `[FIX]` names the three routes: correct the value,
    bring the document into the assignment's worktree, or pass the absolute path of a copy the assignee can read.
  - The index is loaded once per command and only when a value is an ID.
- `--evidence`, `--handoff` and `--stop` are recorded text for resume and are not verified.
- `new` also records `dirty_at_assign`: the uncommitted and untracked paths of the worktree at that moment.
- Refusals, each exit `2`: an existing ID, an unknown `--parent` or `--depends-on` ID, a closed parent, a parent that
  itself has a parent, authority not inside the parent's, a write scope that overlaps another assignment (the recorded assignment schema) and
  an unresolved governing document.

**`return`** records what the assignee returned and sets status `returned`.

```text
devkit adaptive assignment return <id> --status completed|needs_input|failed
    [--final <rev>] [--check <name>=<outcome>]... [--unverified <text>]... [--summary <text>]
```

- `--final` defaults to the HEAD of the assignment's worktree; a given value must resolve to a commit.
- `<outcome>` is `pass`, `fail`, `skipped` or `unavailable`. An outcome for an undeclared name is recorded and never
  fails verification.
- A later `return` on an assignment that is not `closed` replaces the current return; the earlier one stays in the
  event history.

**`verify`** compares the current return with the repository (the verification contract), records the result and sets status `verified`
or `rejected`. Exit `0` on `pass`, `1` on `fail`. It may be repeated; each run recomputes from the repository.

```text
devkit adaptive assignment verify <id>
```

**`close`** ends an assignment with status `closed`.

```text
devkit adaptive assignment close <id> --outcome integrated|abandoned [--reason <text>]
```

- `--reason` is required for `abandoned`, and for `integrated` when the status is not `verified`.
- `integrated` on a status other than `verified` succeeds with the `ADAPTIVE_CLOSED_UNVERIFIED` warning.
- A parent with a child that is not `closed` is refused (`ADAPTIVE_CHILDREN_OUTSTANDING`, exit `2`).

**`list`** prints the assignments that are not `closed`; `--all` adds the closed ones. For each one that is not
`closed` it observes the worktree and reports:

- `worktree_state`: `present`, or `missing` when the directory does not exist, the path is no longer a worktree of
  the repository, or its record carries `prunable`;
- `head`: the worktree HEAD; `commits`: the number of commits in `<base>..HEAD`; `dirty`: the number of uncommitted
  and untracked paths not in `dirty_at_assign`;
- `waiting_on`: the `depends_on` assignments that are not `closed`;
- `attention`: zero or more of `worktree-missing`, `base-not-ancestor` (HEAD does not descend from the base),
  `head-moved` (a return exists and HEAD is not its final commit) and `no-changes` (status `open`, HEAD is the base
  and `dirty` is `0`).

With a missing worktree, `head`, `commits` and `dirty` are null (`-` in text) and `attention` is
`worktree-missing` alone. A closed assignment has `"observed": null` in JSON and `-` for the observed fields in
text. `list` reads worktrees with the same Git commands as `verify` (the verification contract) and exits `0` whatever it lists.

**`show <id>`** prints one assignment with every recorded field, its current return and its event history. It is
the read a new context uses to dispatch an assignment again.

Text output, one sentinel per line, values rendered with `field_value`:

| Command | Lines |
| --- | --- |
| `new`, `return`, `close` | `[ASSIGNMENT: <id> status=<status> owner=<owner> role=<role> parent=<id> worktree=<path> base=<sha> final=<sha> outcome=<outcome>]`; `final` and `outcome` are `-` until set |
| `verify` | one `[CHECK: <name> status=pass\|fail\|not-run\|not-applicable]` per check in the order of the verification contract, one `[OUT_OF_SCOPE: <path> change=committed\|uncommitted]` per offending path, then `[VERIFICATION: <id> result=pass\|fail final=<sha> changed=<n> out_of_scope=<n>]` |
| `list` | one `[ASSIGNMENT: <id> status=<status> owner=<owner> role=<role> parent=<id> worktree=<path> worktree_state=<state> head=<sha> commits=<n> dirty=<n> waiting_on=<ids> attention=<values> assigned_at=<timestamp>]` per assignment, lists comma-separated, then `[SUMMARY: open=<n> returned=<n> verified=<n> rejected=<n> closed=<n>]` |
| `show` | the `[ASSIGNMENT: ...]` line; `[GRANT: commit=yes\|no]`; one `[FIELD: <name> value=<text>]` for each of `goal`, `evidence`, `handoff`, `stop`, `return_summary` and `close_reason` that is set; one `[WRITE: <path>]` per scope entry; one `[GOVERNING: <id-or-path>]`, `[DEPENDS_ON: <id>]` and `[UNVERIFIED: <text>]` per entry; one `[DECLARED_CHECK: <name> command=<text> outcome=<outcome>]` per declared check; one `[EVENT: <type> at=<timestamp>]` per event |

JSON output is one compact object (`ARCH-08-1-agent-output` §4):

| Command | Object |
| --- | --- |
| `new`, `return`, `close`, `show` | `{"assignment": <assignment>, "notices": [...]}`; `show` adds `"events": [...]` |
| `verify` | `{"id", "result", "final", "checks": {...}, "changed_paths": {"committed": [...], "uncommitted": [...], "preexisting_dirty": [...]}, "errors": [...], "notices": [...]}`; `errors` holds one advisory per code that applies |
| `list` | `{"assignments": [<assignment> plus "observed": {"worktree_state", "head", "commits", "dirty", "waiting_on", "attention"}], "summary": {"open", "returned", "verified", "rejected", "closed"}, "notices": [...]}` |

The `checks` object of `verify` has exactly these keys and members:

| Key | Members |
| --- | --- |
| `return` | `status`, `returned` (the return status) |
| `base` | `status`, `base`, `final` |
| `head` | `status`, `head`, `final` |
| `commit` | `status` |
| `scope` | `status`, `outside`: list of `{"path", "change"}` with `change` `committed` or `uncommitted` |
| `checks` | `status`, `missing`: list of names, `not_passed`: list of `{"name", "outcome"}` |
| `children` | `status`, `outstanding`: list of IDs |

### Records

An `<assignment>` object:

| Field | Type | Meaning |
| --- | --- | --- |
| `id`, `status` | string | `status` is `open`, `returned`, `verified`, `rejected` or `closed` |
| `owner`, `role`, `goal` | string | `role` may be null |
| `worktree`, `base` | string | Absolute worktree path; full commit ID |
| `write` | list of strings | Normalized POSIX paths relative to the worktree root; empty for read-only |
| `commit` | boolean | Whether the assignee may commit |
| `checks` | list of `{"name", "command"}` | `command` may be null |
| `governing` | list of strings | Document IDs, and paths relative to the worktree root or absolute (the command interfaces); empty for none |
| `depends_on` | list of strings | Assignment IDs |
| `parent`, `evidence`, `handoff`, `stop` | string or null | |
| `assigned_at` | timestamp | |
| `dirty_at_assign` | list of strings | |
| `return` | null or `{"status", "final", "checks": [{"name", "outcome"}], "unverified": [...], "summary", "returned_at"}` | The current return |
| `verification` | null or `{"result", "final", "checks": {<name>: <status>}, "verified_at"}` | Result of the latest `verify` of the current return; null after a later `return` |
| `close` | null or `{"outcome", "reason", "closed_at"}` | |

Status transitions: `new` gives `open`; `return` gives `returned` from any status but `closed`; `verify` gives
`verified` or `rejected` from `returned`, `verified` or `rejected`; `close` gives `closed` from any other status.
Every other command on a `closed` assignment is refused (`ADAPTIVE_ASSIGNMENT_CLOSED`).

Write-scope rules:

- An entry covers a path when the path equals the entry or starts with the entry followed by `/`; `.` covers every
  path.
- Two entries overlap when one covers the other.
- `new` refuses a scope with an entry that overlaps an entry of another assignment that is not `closed`
  (`ADAPTIVE_SCOPE_OVERLAP`), whatever their worktrees. Two assignments are exempt: the parent, and each assignment
  named in `--depends-on`, because a dependent assignment is sequenced after it. The advisory names the other
  assignment and both entries, and its `[FIX]` lists the three routes: narrow the scope, close the other
  assignment when its work is finished, or name it in `--depends-on` when this work is sequenced after it.
- With `--parent`, each write entry must be covered by an entry of the parent, and `--commit` requires the parent's
  commit grant (`ADAPTIVE_AUTHORITY_NOT_NARROWED`). The parent must have no parent (`ADAPTIVE_NESTING_DEPTH`), which
  keeps the depth at Host, lead, child.

### Verification

`verify` evaluates these checks in order. The result is `pass` when no check is `fail` or `not-run`.

| Check | Passes when | Code on failure |
| --- | --- | --- |
| `return` | The return status is `completed` | `ADAPTIVE_RETURN_NOT_COMPLETED` |
| `base` | The base is an ancestor of the final commit (`git merge-base --is-ancestor`) | `ADAPTIVE_BASE_NOT_ANCESTOR` |
| `head` | The worktree HEAD is the final commit | `ADAPTIVE_HEAD_MOVED` |
| `commit` | The final commit is the base; `not-applicable` when the assignment grants commits | `ADAPTIVE_COMMIT_NOT_GRANTED` |
| `scope` | A write entry covers every changed path; `not-run` when `base` failed | `ADAPTIVE_SCOPE_VIOLATION` |
| `checks` | Every declared check has the outcome `pass`; `not-applicable` without declared checks | `ADAPTIVE_CHECK_OUTCOME_MISSING` for a declared check without an outcome, `ADAPTIVE_CHECK_NOT_PASSED` for `fail`, `skipped` or `unavailable` |
| `children` | Every assignment naming this one as parent is `closed`; `not-applicable` without children | `ADAPTIVE_CHILDREN_OUTSTANDING` |

Changed paths are the union of:

- committed: `git diff --no-renames --name-only -z <base> <final> --`, so a rename counts under both names;
- uncommitted: `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` in the worktree, minus the
  paths in `dirty_at_assign`. `--no-optional-locks` keeps the command from writing the index of a worktree where an
  assignee is working.

Reading the status output (observed with Git 2.49.0, `docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §9):

- A record is `XY <path>`, terminated by NUL. When `X` or `Y` is `R` or `C`, the next NUL-terminated record is the
  original path without a status prefix. Both names count as changed.
- An untracked nested repository is one record with a trailing `/`. The parser strips the trailing `/`, so a write
  entry covers the nested repository by its directory name.

Stated limits, which the capability and the reference page repeat:

- Ignored files and writes outside the worktree are not observed.
- A path in `dirty_at_assign` is excluded even when the assignee changed it again; `verify` lists such paths under
  `preexisting_dirty` with the `ADAPTIVE_PREEXISTING_DIRTY` notice.
- Paths brought in by merging another branch into the assignment's branch count as changed.
- In a checkout that the Host or another agent edits at the same time, changed paths cannot be attributed; the Host
  judges that result and records its reason at `close`.
- A recorded outcome repeats the assignee's report; no check is run.
- Governing documents are validated when the assignment is recorded and not again.
- The commands read the repository that `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` name when these are set.
- The content of a submodule is not observed; a changed submodule appears as its one path.

In-scope uncommitted paths do not fail `scope`. When the assignment grants commits, `verify` reports them with the
`ADAPTIVE_UNCOMMITTED_CHANGES` warning, because the final commit does not contain them. Without the grant they are
the expected result and no warning is raised.

### Codes and exit codes

Exit `0`: success, warnings and notices included. Exit `1`: `verify` with a failed check, or a warning under
`--strict`. Exit `2`: the command could not run or refused. `CAP-HARN-command-mount` §4.7 describes `devkit spec` and
`devkit docs` only and does not change.

Every code is one `AdvisoryError` subclass of a package base error, prefixed `ADAPTIVE_`
(`RULE-advisory-unique-code`). The mode is the derived `[ACTION]` mode of `CAP-ADV-agent-advisory-protocol` §5; each
class sets the fields that derive it (`input_error = True` for `INPUT_ERROR`, `actor = Actor.USER` for
`INTERACTION`) and a `fix`. `packages/devkit-spec/src/devkit_spec/base/errors.py` is the model for the module.

| Code | Level, exit, mode | Raised when |
| --- | --- | --- |
| `ADAPTIVE_REPOSITORY_UNSUPPORTED` | error, `2`, `INPUT_ERROR` | The workspace root is not inside a Git work tree |
| `ADAPTIVE_LEDGER_UNREADABLE` | error, `2`, `INTERACTION` | A newline-terminated line cannot be parsed, or an event has an unknown schema number; the report asks whether to move the damaged ledger aside |
| `ADAPTIVE_LEDGER_UNWRITABLE` | error, `2`, `INTERACTION` | The ledger directory, lock or file cannot be created or written; the report says the assignments stay unrecorded |
| `ADAPTIVE_ASSIGNMENT_UNKNOWN` | error, `2`, `INPUT_ERROR` | An ID, `--parent` or `--depends-on` names no assignment |
| `ADAPTIVE_ASSIGNMENT_EXISTS` | error, `2`, `INPUT_ERROR` | `new --id` names a recorded assignment |
| `ADAPTIVE_ASSIGNMENT_CLOSED` | error, `2`, `INPUT_ERROR` | `return`, `verify` or `close` on a closed assignment, or `new --parent` naming one |
| `ADAPTIVE_ASSIGNMENT_NOT_RETURNED` | error, `2`, `INPUT_ERROR` | `verify` on an assignment without a return |
| `ADAPTIVE_WORKTREE_UNAVAILABLE` | error, `2`, `INPUT_ERROR` | `new`, a `return` without `--final`, or `verify` cannot read the assignment's worktree, or `--worktree` is not a present worktree of this repository |
| `ADAPTIVE_REVISION_UNRESOLVED` | error, `2`, `INPUT_ERROR` | `--base` or `--final`, given or defaulted, does not resolve to a commit |
| `ADAPTIVE_GOVERNING_UNRESOLVED` | error, `2`, `INPUT_ERROR` | `new`: a `--governing` ID resolves to no document or to several, or a path does not exist (the command interfaces) |
| `ADAPTIVE_SCOPE_OVERLAP` | error, `2`, `INPUT_ERROR` | `new`: a write entry overlaps another open assignment (the recorded assignment schema) |
| `ADAPTIVE_AUTHORITY_NOT_NARROWED` | error, `2`, `INPUT_ERROR` | `new --parent`: a write entry or the commit grant exceeds the parent's |
| `ADAPTIVE_NESTING_DEPTH` | error, `2`, `INPUT_ERROR` | `new --parent`: the parent has a parent |
| `ADAPTIVE_CHILDREN_OUTSTANDING` | error, `1` from `verify`, `2` from `close`, `INPUT_ERROR` | A child is not closed |
| `ADAPTIVE_RETURN_NOT_COMPLETED`, `ADAPTIVE_BASE_NOT_ANCESTOR`, `ADAPTIVE_HEAD_MOVED`, `ADAPTIVE_COMMIT_NOT_GRANTED`, `ADAPTIVE_SCOPE_VIOLATION`, `ADAPTIVE_CHECK_OUTCOME_MISSING`, `ADAPTIVE_CHECK_NOT_PASSED` | error, `1`, `INPUT_ERROR`, collected by `verify` | The check of the verification contract failed; `ADAPTIVE_SCOPE_VIOLATION` names at most 20 paths and the count of the rest |
| `ADAPTIVE_UNCOMMITTED_CHANGES` | warning | `verify`: the assignment grants commits and in-scope uncommitted paths exist |
| `ADAPTIVE_CLOSED_UNVERIFIED` | warning | `close --outcome integrated` on a status other than `verified` |
| `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` | warning | A reader skipped an unterminated final fragment |
| `ADAPTIVE_PREEXISTING_DIRTY` | notice | `verify`: paths in `dirty_at_assign` are still dirty |

A verification failure is `INPUT_ERROR` because the Host corrects the returned work and verifies again
(`CAP-ADV-agent-advisory-protocol` §6, the note under `BLOCKED`). No code derives `MAINTENANCE`.

Codes of other packages pass through unchanged: `ARGUMENT_INVALID` (a malformed ID, a write entry with `*`, `?` or
`[` or outside the worktree, a malformed `--check`, an unknown outcome, a missing required `--reason`, `none` beside
another `--governing` value, a `--workspace-root` that is a subdirectory of a work tree), `LOCK_HELD`, `GIT_FAILED`,
`DEVKIT_ROOT_NESTED` and `YAML_BINDING_UNAVAILABLE` (the document index without LibYAML). The document index's
`DOCS_ID_UNRESOLVED` and `DOCS_ID_DUPLICATE` are caught and reported as `ADAPTIVE_GOVERNING_UNRESOLVED`. With the
distribution absent, `devkit adaptive` is click's usage error, exit `2`, without a code.

### Ledger

`ADR-adaptive-assignment-ledger-storage` decides location and format. The details Development implements:

- Directory `<git common dir>/devkit/adaptive/`, created on the first write; files `ledger.jsonl` and `lock`. The
  common directory is the output of `git rev-parse --path-format=absolute --git-common-dir`. For a linked worktree
  of a bare repository it is the bare directory.
- One event per line: `{"schema": 1, "at": <timestamp>, "event": "assigned"|"returned"|"verified"|"closed", "id":
  <id>, "data": {...}}`. `data` holds the fields that event sets (the recorded assignment schema).
- A write takes the exclusive lock (`devkit_core.core.file_lock`, 10 second bound), reads and folds the ledger,
  validates, then appends one newline-terminated line and flushes it to disk.
- Bytes after the last newline are a fragment of an interrupted append, not an event. A reader skips the fragment
  with the `ADAPTIVE_LEDGER_FRAGMENT_IGNORED` warning. A writer, holding the lock, truncates the file back to the
  last newline before it appends, so a fragment never becomes an earlier line.
- `list` and `show` read without the lock.
- The file format is private. `devkit adaptive assignment list --format json` and the list use case are the read
  interface for other code, `PROP-adaptive-lifecycle-hooks` included; the list use case module is declared in
  `public_modules`.
- No command deletes or rewrites an event, and no pruning command is added.


