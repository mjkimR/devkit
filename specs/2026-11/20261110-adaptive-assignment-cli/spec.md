---
id: SPEC-adaptive-assignment-cli
title: Assignment ledger and return verification commands for adaptive delegation
summary: Add commands that record delegated assignments and verify a return against its assignment, and make devkit-adaptive require the document system, so a Host resumes from recorded state and checks scope, source identity, declared checks and governing documents deterministically.
status: in-progress
created: 2026-11-10
depends_on:
  - SPEC-adaptive-package-extraction
related_capabilities: [CAP-DLV-adaptive-development]
related_usecases: [UC-advance-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-adaptive-assignment-cli] Adaptive assignment commands

## 1. Goal

Record delegated assignments in the shared Git directory and verify returns against recorded authority, repository facts and declared check outcomes. Add the document-system requirement and align guidance with the command contract.

## 2. User Stories

- A Host records and resumes outstanding assignments from any worktree.
- A delegating agent verifies returned work against its granted scope and checks.
- A consumer installs adaptive development with its document system but without SDD.

## 3. Behavioral Contract

### 3.2 Commands

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
  itself has a parent, authority not inside the parent's, a write scope that overlaps another assignment (§3.3) and
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

**`verify`** compares the current return with the repository (§3.4), records the result and sets status `verified`
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
text. `list` reads worktrees with the same Git commands as `verify` (§3.4) and exits `0` whatever it lists.

**`show <id>`** prints one assignment with every recorded field, its current return and its event history. It is
the read a new context uses to dispatch an assignment again.

Text output, one sentinel per line, values rendered with `field_value`:

| Command | Lines |
| --- | --- |
| `new`, `return`, `close` | `[ASSIGNMENT: <id> status=<status> owner=<owner> role=<role> parent=<id> worktree=<path> base=<sha> final=<sha> outcome=<outcome>]`; `final` and `outcome` are `-` until set |
| `verify` | one `[CHECK: <name> status=pass\|fail\|not-run\|not-applicable]` per check in the order of §3.4, one `[OUT_OF_SCOPE: <path> change=committed\|uncommitted]` per offending path, then `[VERIFICATION: <id> result=pass\|fail final=<sha> changed=<n> out_of_scope=<n>]` |
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

### 3.3 Records

An `<assignment>` object:

| Field | Type | Meaning |
| --- | --- | --- |
| `id`, `status` | string | `status` is `open`, `returned`, `verified`, `rejected` or `closed` |
| `owner`, `role`, `goal` | string | `role` may be null |
| `worktree`, `base` | string | Absolute worktree path; full commit ID |
| `write` | list of strings | Normalized POSIX paths relative to the worktree root; empty for read-only |
| `commit` | boolean | Whether the assignee may commit |
| `checks` | list of `{"name", "command"}` | `command` may be null |
| `governing` | list of strings | Document IDs, and paths relative to the worktree root or absolute (§3.2); empty for none |
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

### 3.4 Verification

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

### 3.5 Codes and exit codes

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
| `ADAPTIVE_GOVERNING_UNRESOLVED` | error, `2`, `INPUT_ERROR` | `new`: a `--governing` ID resolves to no document or to several, or a path does not exist (§3.2) |
| `ADAPTIVE_SCOPE_OVERLAP` | error, `2`, `INPUT_ERROR` | `new`: a write entry overlaps another open assignment (§3.3) |
| `ADAPTIVE_AUTHORITY_NOT_NARROWED` | error, `2`, `INPUT_ERROR` | `new --parent`: a write entry or the commit grant exceeds the parent's |
| `ADAPTIVE_NESTING_DEPTH` | error, `2`, `INPUT_ERROR` | `new --parent`: the parent has a parent |
| `ADAPTIVE_CHILDREN_OUTSTANDING` | error, `1` from `verify`, `2` from `close`, `INPUT_ERROR` | A child is not closed |
| `ADAPTIVE_RETURN_NOT_COMPLETED`, `ADAPTIVE_BASE_NOT_ANCESTOR`, `ADAPTIVE_HEAD_MOVED`, `ADAPTIVE_COMMIT_NOT_GRANTED`, `ADAPTIVE_SCOPE_VIOLATION`, `ADAPTIVE_CHECK_OUTCOME_MISSING`, `ADAPTIVE_CHECK_NOT_PASSED` | error, `1`, `INPUT_ERROR`, collected by `verify` | The check of §3.4 failed; `ADAPTIVE_SCOPE_VIOLATION` names at most 20 paths and the count of the rest |
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

### 3.6 Ledger

`ADR-adaptive-assignment-ledger-storage` decides location and format. The details Development implements:

- Directory `<git common dir>/devkit/adaptive/`, created on the first write; files `ledger.jsonl` and `lock`. The
  common directory is the output of `git rev-parse --path-format=absolute --git-common-dir`. For a linked worktree
  of a bare repository it is the bare directory.
- One event per line: `{"schema": 1, "at": <timestamp>, "event": "assigned"|"returned"|"verified"|"closed", "id":
  <id>, "data": {...}}`. `data` holds the fields that event sets (§3.3).
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


## 4. Acceptance Criteria

### [AC-01] Shared ledger from linked worktrees

- **Given** a repository with a linked worktree
- **When** `new` runs in the main worktree with `--worktree`,
  `--write src/a` and `--check tests`
- **Then** the assignment is `open` with the worktree HEAD as base, and `list` run
  from the linked worktree prints it.

### [AC-02] No tracked or status changes

- **Given** any command of the group has run
- **Then** `git status --porcelain` of every worktree is unchanged
  and no tracked file changed.
- **When** the specified public command or check runs.

### [AC-03] Literal overlap and sequencing

- **Given** an open assignment with `--write src/a`
- **When** `new` records `--write src/a/x.py` or `--write .`
  for another assignment
- **Then** it exits `2` with `ADAPTIVE_SCOPE_OVERLAP` and appends nothing; with
  `--depends-on <the first ID>` it succeeds; `--write src/ab` succeeds.

### [AC-04] Passing return

- **Given** a returned assignment whose commits changed only paths under its write scope and whose declared
  checks all have `pass`
- **When** `verify` runs
- **Then** it exits `0`, prints `result=pass` and the status is `verified`.

### [AC-05] Committed and uncommitted scope violations

- **Given** a return whose commit renamed a file from inside the scope to outside it, or left an untracked
  file outside the scope
- **When** `verify` runs
- **Then** it exits `1` with `ADAPTIVE_SCOPE_VIOLATION`, lists each
  offending path with `change=committed` or `change=uncommitted`, and the status is `rejected`. Given an uncommitted
  rename from inside the scope to outside it, then the new name is listed. Given an untracked nested repository
  `vendor/x` and the write entry `vendor`, then `scope` passes.

### [AC-06] Ancestry and moved HEAD

- **Given** a return whose final commit does not descend from the base
- **Then** `verify` exits `1` with
  `ADAPTIVE_BASE_NOT_ANCESTOR` and `scope` is `not-run`. Given the worktree HEAD moved after `return`, then `verify`
  exits `1` with `ADAPTIVE_HEAD_MOVED`.
- **When** the specified public command or check runs.

### [AC-07] Declared check outcomes

- **Given** declared checks `tests` and `lint` and a return with `tests=pass` only
- **Then** `verify` exits `1`
  with `ADAPTIVE_CHECK_OUTCOME_MISSING`; with `lint=skipped` it exits `1` with `ADAPTIVE_CHECK_NOT_PASSED`.
- **When** the specified public command or check runs.

### [AC-08] Commit authority and strict warnings

- **Given** an assignment without `--commit` and a return whose final commit is not the base
- **Then** `verify`
  exits `1` with `ADAPTIVE_COMMIT_NOT_GRANTED`. Given the same assignment with only uncommitted in-scope paths and
  HEAD at the base, then `verify --strict` exits `0` with `result=pass` and no warning; with `--commit` granted the
  same state reports `ADAPTIVE_UNCOMMITTED_CHANGES` and `verify --strict` exits `1` with `result=pass`.
- **When** the specified public command or check runs.

### [AC-09] Child scope, depth and completion

- **Given** a parent with `--write src` and `--commit`
- **When** a child is recorded with `--write docs`, then
  `new` exits `2` with `ADAPTIVE_AUTHORITY_NOT_NARROWED`; a child of a child exits `2` with `ADAPTIVE_NESTING_DEPTH`;
  while a child is not closed, `verify` of the parent exits `1` and `close` of the parent exits `2`, both with
  `ADAPTIVE_CHILDREN_OUTSTANDING`.
- **Then** the specified outcomes and codes hold.

### [AC-10] Repair and repeated returns

- **Given** a `rejected` assignment
- **When** the worktree is repaired, `return` is recorded again and `verify`
  passes
- **Then** the status is `verified` and `show` lists both returns in its events.

### [AC-11] Reasoned unverified closing

- **Given** a `rejected` assignment
- **When** `close --outcome integrated` runs without `--reason`
- **Then** it exits
  `2` with `ARGUMENT_INVALID`; with `--reason` it exits `0` with the `ADAPTIVE_CLOSED_UNVERIFIED` warning, and `1`
  under `--strict`.

### [AC-12] Resume observations and complete show

- **Given** three open assignments, one whose worktree directory was moved away without `git worktree
  prune`, one with a commit and one untouched
- **When** `list` runs in a fresh process
- **Then** it reports
  `attention=worktree-missing`, `commits=1` and `attention=no-changes` respectively and exits `0`; closed
  assignments appear only with `--all`. In the same process `show <id>` prints the goal, the stop condition, the
  commit grant, the write scope, the governing documents and the declared checks that `new` recorded, in text and
  in JSON.

### [AC-13] Concurrent append and fragment recovery

- **Given** two processes that run `new` at the same time
- **Then** both assignments are recorded with distinct
  IDs and every ledger line parses. Given a ledger that ends with an unterminated fragment, then `list` succeeds with
  `ADAPTIVE_LEDGER_FRAGMENT_IGNORED`; after a following `new`, `list` exits `0` without the warning and every line
  of the file parses. A newline-terminated line that does not parse gives `ADAPTIVE_LEDGER_UNREADABLE`, exit `2`.
- **When** the specified public command or check runs.

### [AC-14] Repository and ledger errors

- **Given** a directory outside a Git work tree
- **Then** every command exits `2` with
  `ADAPTIVE_REPOSITORY_UNSUPPORTED`. Given a repository without a commit, then `list` exits `0` with an empty list
  and `new` exits `2` with `ADAPTIVE_REVISION_UNRESOLVED`. Given a ledger directory that cannot be written, then
  `new` exits `2` with `ADAPTIVE_LEDGER_UNWRITABLE`. Given a linked worktree of a bare repository, then `new` and
  `list` succeed there and the ledger lies under the bare directory.
- **When** the specified public command or check runs.

### [AC-15] Compact JSON and sentinel text

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** For every command, `--format json` prints exactly one compact object with the keys of §3.2, a failure
  prints `{"error": ..., "notices": ...}`, and text mode prints only the sentinels of §3.2 on stdout.

### [AC-16] Documented codes and architecture

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** Every `ADAPTIVE_` code declared in the package appears in a document under `docs/` (documented-codes
  test), and `devkit rules check` reports no `RULE-architecture`, `RULE-usecase-boundaries` or
  `RULE-advisory-unique-code` finding for the package.

### [AC-17] Delegation and document guidance

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** The bundle content tests find, without an installation condition: the recording, verification and
  closing steps and the fallback in `delegation.md`; the resume rule in `current-context.md`; the unconditional
  step 1, the new step 2 and the `devkit rules check` step in `documents.md`; and no "without assuming a harness is
  installed" in `orchestration.md`. They find no command name in the product-support role contracts, the
  `adaptive-import` skill or the conversion playbook. The three archetypes state no prerequisite.

### [AC-18] Installed adaptive distribution without SDD

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** The installed-consumer test builds the `devkit-adaptive` wheel and its sibling wheels, installs them
  into a fresh environment and shows:
  - the installed metadata of `devkit-adaptive` requires `devkit-docs` at exactly the built version and names no
    `devkit-spec`;
  - `devkit-spec` is not an installed distribution (the sibling wheels are named by file, so their presence shows
    nothing; the metadata check above carries the requirement);
  - after `devkit sync` in a consumer repository with one commit, the receipt's `selection.presets` holds
    `docs == ["core"]` and `harness == ["core"]`, and `.devkit/managed/adaptive-dev` does not exist until
    `devkit add adaptive-dev`;
  - `devkit adaptive assignment list --format json` exits `0` with an empty `assignments` list;
  - `devkit adaptive assignment new --owner o --goal g --governing CAP-NOPE-missing` exits `2` with
    `ADAPTIVE_GOVERNING_UNRESOLVED`, which shows the document index imports in the installed environment.

### [AC-19] Fresh module imports without SDD

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** A test starts a fresh interpreter that imports every module of the package
  (`pkgutil.walk_packages`), the CLI module included, and prints the loaded module names; the test finds no
  `devkit_spec` module among them.

### [AC-20] Governing IDs, aliases, paths and none

- **Given** a worktree that holds a document with a valid ID (written `<ID>` here) and the file
  `docs/notes.md`
- **When** `new` records `--governing <ID> --governing docs/notes.md`
- **Then** `show` lists both and the
  JSON `governing` is `["<ID>", "docs/notes.md"]`. An alias of the document records `<ID>`. `--governing none` and
  no `--governing` both record `[]`. `--governing none --governing <ID>` exits `2` with `ARGUMENT_INVALID`.

### [AC-21] Unresolved governing values and worktree locality

- **Given** `--governing <an ID no document declares> --governing docs/absent.md`
- **Then** `new` exits `2` with one
  `ADAPTIVE_GOVERNING_UNRESOLVED` that names both values and appends nothing. Given a document that exists
  uncommitted in the main worktree and not in the linked worktree of the assignment, then `--governing <its ID>`
  exits `2` with `ADAPTIVE_GOVERNING_UNRESOLVED`, and `--governing <absolute path of the main worktree's copy>`
  succeeds and records the absolute path. Given two documents that declare the same ID, then that ID is refused with
  the reason `duplicate-id`.
- **When** the specified public command or check runs.

### [AC-22] Pins, lockstep and snapshot refusal

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** The package metadata test passes (§3.8), `packages/devkit/tests/integration/package/test_lockstep.py`
  passes, `uv lock --check` passes, and the snapshot refusal test shows `BUNDLE_SNAPSHOT_UNSUPPORTED`.

### [AC-23] Living Spec and installation consistency

- **Given** the implemented distribution and its documented command contract.
- **When** the named test or review runs.
- **Then** Each statement of `target-docs.md` §1 to §4 is present in its document (checked in the reconcile
  review, one document at a time). As a search aid, `rg -nU "devkit-docs\s+(plus|and)\s+devkit-(catalog|adaptive)"
  docs/capabilities docs/architecture guides README.md` then prints only statements about installing
  `deep-research`, and `rg -n "docs/catalog" docs/capabilities docs/architecture guides` prints no statement about
  adaptive development.
## 5. Non-Goals

- **Scope Excluded**: hooks, scheduling, process running, MCP, glob scopes, ledger pruning, migrations, SDD records in the adaptive product, public shared Git helpers and edits to other runtime packages.

## 6. Assumptions and Source

The prerequisite is landed with the approved package names and paths. Current metadata is version 0.1.6. The source capability for guidance is `CAP-DLV-adaptive-development`; `PROP-adaptive-assignment-cli-target` specifies the retained document changes. Three promoted ADRs settle the command, storage and requirement choices. Source runtime changes are confined to devkit-adaptive.
